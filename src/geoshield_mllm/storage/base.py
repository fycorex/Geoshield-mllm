from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredArtifact:
    drive_path: str
    file_id: str | None
    sha256: str | None = None
    metadata_path: str | None = None


class StorageBackend(ABC):
    @abstractmethod
    def upload_file(self, local_path: Path, drive_path: str, metadata: dict | None = None) -> StoredArtifact:
        raise NotImplementedError

    @abstractmethod
    def download_file(self, drive_path: str, local_path: Path, expected_sha256: str | None = None) -> Path:
        raise NotImplementedError

    @abstractmethod
    def exists(self, drive_path: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_run_artifacts(self, run_id: str) -> list[StoredArtifact]:
        raise NotImplementedError

    @abstractmethod
    def resolve_drive_path(self, *parts: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def ensure_folder_path(self, drive_path: str) -> str | None:
        raise NotImplementedError

