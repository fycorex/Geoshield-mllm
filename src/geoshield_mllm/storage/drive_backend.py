from __future__ import annotations

import json
import io
import mimetypes
from pathlib import Path
from typing import Any

from geoshield_mllm.storage.base import StorageBackend, StoredArtifact
from geoshield_mllm.storage.local_cache import LocalCache
from geoshield_mllm.utils.hashing import sha256_file
from geoshield_mllm.utils.io import write_json
from geoshield_mllm.utils.time import utc_now_iso


class GoogleDriveBackend(StorageBackend):
    """Google Drive backend with deterministic path logic and dry-run friendly service injection."""

    def __init__(self, root: str = "GeoShield-MLLM-Probe", cache_dir: Path | str = ".cache/geoshield_mllm/drive", service: Any | None = None) -> None:
        self.root = root.strip("/")
        self.cache = LocalCache(Path(cache_dir))
        self.service = service
        self.folder_ids_path = self.cache.root / "folder_ids.json"
        self.folder_ids = self._load_folder_ids()

    def _load_folder_ids(self) -> dict[str, str]:
        if self.folder_ids_path.exists():
            return json.loads(self.folder_ids_path.read_text(encoding="utf-8"))
        return {}

    def _save_folder_ids(self) -> None:
        write_json(self.folder_ids_path, self.folder_ids)

    @staticmethod
    def _quote(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def resolve_drive_path(self, *parts: str) -> str:
        cleaned = [self.root]
        for part in parts:
            for segment in str(part).split("/"):
                segment = segment.strip()
                if segment:
                    cleaned.append(segment)
        return "/".join(cleaned)

    def ensure_folder_path(self, drive_path: str) -> str | None:
        normalized = self.resolve_drive_path(drive_path.removeprefix(self.root).strip("/")) if not drive_path.startswith(self.root) else drive_path.strip("/")
        if normalized in self.folder_ids:
            return self.folder_ids[normalized]
        if self.service is None:
            self.folder_ids[normalized] = f"dryrun:{normalized}"
            self._save_folder_ids()
            return self.folder_ids[normalized]

        parent_id = None
        built_path: list[str] = []
        for segment in normalized.split("/"):
            built_path.append(segment)
            current = "/".join(built_path)
            if current in self.folder_ids:
                parent_id = self.folder_ids[current]
                continue
            query = (
                "mimeType='application/vnd.google-apps.folder' and trashed=false "
                f"and name='{self._quote(segment)}'"
            )
            if parent_id:
                query += f" and '{parent_id}' in parents"
            result = self.service.files().list(q=query, fields="files(id, name)", pageSize=10).execute()
            files = result.get("files", [])
            if files:
                folder_id = files[0]["id"]
            else:
                body: dict[str, Any] = {"name": segment, "mimeType": "application/vnd.google-apps.folder"}
                if parent_id:
                    body["parents"] = [parent_id]
                folder_id = self.service.files().create(body=body, fields="id").execute()["id"]
            self.folder_ids[current] = folder_id
            parent_id = folder_id
        self._save_folder_ids()
        return parent_id

    def upload_file(self, local_path: Path, drive_path: str, metadata: dict | None = None) -> StoredArtifact:
        local_path = Path(local_path)
        digest = sha256_file(local_path)
        full_path = self.resolve_drive_path(drive_path)
        sidecar = {
            "project": "Geoshield-mllm",
            "drive_path": full_path,
            "local_sha256": digest,
            "created_at": utc_now_iso(),
            **(metadata or {}),
        }
        sidecar_key = f"{full_path}.metadata.json"
        cached_sidecar = self.cache.path_for(sidecar_key)
        write_json(cached_sidecar, sidecar)
        if self.service is None:
            self.cache.put(local_path, full_path)
            return StoredArtifact(drive_path=full_path, file_id=f"dryrun:{full_path}", sha256=digest, metadata_path=str(cached_sidecar))
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc:
            raise RuntimeError("google-api-python-client is required for live Drive uploads.") from exc

        parent_path, name = full_path.rsplit("/", 1)
        parent_id = self.ensure_folder_path(parent_path)
        mime_type = mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
        media = MediaFileUpload(str(local_path), mimetype=mime_type, resumable=True)
        body = {
            "name": name,
            "parents": [parent_id],
            "appProperties": {
                "project": "Geoshield-mllm",
                "local_sha256": digest,
                "drive_path": full_path,
            },
        }
        created = self.service.files().create(body=body, media_body=media, fields="id").execute()
        return StoredArtifact(drive_path=full_path, file_id=created["id"], sha256=digest, metadata_path=str(cached_sidecar))

    def download_file(self, drive_path: str, local_path: Path, expected_sha256: str | None = None) -> Path:
        full_path = self.resolve_drive_path(drive_path)
        cached = self.cache.path_for(full_path)
        if not cached.exists():
            if self.service is None:
                raise FileNotFoundError(f"No cached dry-run artifact for {full_path}")
            file_id = self._find_file_id(full_path)
            if not file_id:
                raise FileNotFoundError(f"No Drive artifact found for {full_path}")
            try:
                from googleapiclient.http import MediaIoBaseDownload
            except ImportError as exc:
                raise RuntimeError("google-api-python-client is required for live Drive downloads.") from exc
            request = self.service.files().get_media(fileId=file_id)
            cached.parent.mkdir(parents=True, exist_ok=True)
            with cached.open("wb") as raw:
                downloader = MediaIoBaseDownload(raw, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
        if expected_sha256 and not self.cache.validate(cached, expected_sha256):
            raise ValueError(f"Checksum mismatch for cached artifact {full_path}")
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(cached.read_bytes())
        return local_path

    def exists(self, drive_path: str) -> bool:
        full_path = self.resolve_drive_path(drive_path)
        if self.cache.path_for(full_path).exists():
            return True
        return False if self.service is None else self._find_file_id(full_path) is not None

    def list_run_artifacts(self, run_id: str) -> list[StoredArtifact]:
        prefix = self.resolve_drive_path("runs", run_id).replace("/", "__")
        return [
            StoredArtifact(drive_path=path.name.replace("__", "/"), file_id=f"dryrun:{path.name}")
            for path in self.cache.root.glob(f"{prefix}*")
            if not path.name.endswith(".metadata.json")
        ]

    def _find_file_id(self, full_path: str) -> str | None:
        if self.service is None:
            return None
        if "/" not in full_path:
            return self.ensure_folder_path(full_path)
        parent_path, name = full_path.rsplit("/", 1)
        parent_id = self.ensure_folder_path(parent_path)
        query = f"name='{self._quote(name)}' and trashed=false and '{parent_id}' in parents"
        result = self.service.files().list(q=query, fields="files(id, name)", pageSize=10).execute()
        files = result.get("files", [])
        return files[0]["id"] if files else None
