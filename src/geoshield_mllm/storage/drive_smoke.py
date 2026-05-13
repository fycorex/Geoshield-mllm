from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from geoshield_mllm.storage.drive_auth import build_drive_service_oauth, build_drive_service_service_account
from geoshield_mllm.storage.drive_backend import GoogleDriveBackend
from geoshield_mllm.utils.hashing import sha256_file
from geoshield_mllm.utils.io import write_json
from geoshield_mllm.utils.time import utc_now_iso

AuthMode = Literal["dry-run", "oauth", "service-account"]


@dataclass(frozen=True)
class DriveSmokeReport:
    ok: bool
    auth_mode: AuthMode
    root: str
    drive_path: str
    file_id: str | None
    uploaded_sha256: str
    downloaded_sha256: str | None
    downloaded_matches: bool
    local_source: str
    local_download: str
    metadata_path: str | None
    started_at: str
    finished_at: str
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _build_service(auth_mode: AuthMode, oauth_client_secrets: Path, oauth_token: Path, service_account_path: Path | None):
    if auth_mode == "dry-run":
        return None
    if auth_mode == "oauth":
        return build_drive_service_oauth(oauth_client_secrets, oauth_token)
    if auth_mode == "service-account":
        path = service_account_path or Path(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""))
        if not str(path):
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS or --service-account-path is required.")
        return build_drive_service_service_account(path)
    raise ValueError(f"Unsupported auth mode: {auth_mode}")


def run_drive_smoke(
    *,
    auth_mode: AuthMode = "dry-run",
    root: str = "GeoShield-MLLM-Probe",
    cache_dir: Path = Path(".cache/geoshield_mllm/drive"),
    local_dir: Path = Path(".cache/geoshield_mllm/drive_smoke"),
    report_path: Path = Path("docs/drive_smoke_latest.json"),
    oauth_client_secrets: Path = Path("credentials.json"),
    oauth_token: Path = Path(".cache/geoshield_mllm/drive/oauth_token.json"),
    service_account_path: Path | None = None,
) -> DriveSmokeReport:
    started = utc_now_iso()
    local_dir.mkdir(parents=True, exist_ok=True)
    source = local_dir / "smoke_source.txt"
    download = local_dir / "smoke_download.txt"
    source.write_text(f"Geoshield-mllm Drive smoke test\nstarted_at={started}\n", encoding="utf-8")
    uploaded_sha = sha256_file(source)
    drive_rel_path = "shared/smoke/drive_smoke.txt"
    try:
        service = _build_service(auth_mode, oauth_client_secrets, oauth_token, service_account_path)
        backend = GoogleDriveBackend(root=root, cache_dir=cache_dir, service=service)
        stored = backend.upload_file(
            source,
            drive_rel_path,
            {
                "variant": "drive_smoke",
                "auth_mode": auth_mode,
                "git_commit_hash": os.popen("git rev-parse HEAD").read().strip(),
            },
        )
        backend.download_file(drive_rel_path, download, expected_sha256=uploaded_sha)
        downloaded_sha = sha256_file(download)
        report = DriveSmokeReport(
            ok=downloaded_sha == uploaded_sha,
            auth_mode=auth_mode,
            root=root,
            drive_path=stored.drive_path,
            file_id=stored.file_id,
            uploaded_sha256=uploaded_sha,
            downloaded_sha256=downloaded_sha,
            downloaded_matches=downloaded_sha == uploaded_sha,
            local_source=str(source),
            local_download=str(download),
            metadata_path=stored.metadata_path,
            started_at=started,
            finished_at=utc_now_iso(),
        )
    except Exception as exc:  # noqa: BLE001 - report smoke failure as data.
        report = DriveSmokeReport(
            ok=False,
            auth_mode=auth_mode,
            root=root,
            drive_path=f"{root}/{drive_rel_path}",
            file_id=None,
            uploaded_sha256=uploaded_sha,
            downloaded_sha256=None,
            downloaded_matches=False,
            local_source=str(source),
            local_download=str(download),
            metadata_path=None,
            started_at=started,
            finished_at=utc_now_iso(),
            error=f"{type(exc).__name__}: {exc}",
        )
    write_json(report_path, report.to_dict())
    return report

