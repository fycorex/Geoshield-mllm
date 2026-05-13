from pathlib import Path
import tempfile
import unittest

from geoshield_mllm.storage import GoogleDriveBackend


class StoragePathTests(unittest.TestCase):
    def test_drive_path_resolution(self) -> None:
        tmp_path = Path(tempfile.mkdtemp())
        backend = GoogleDriveBackend(cache_dir=tmp_path)
        self.assertEqual(backend.resolve_drive_path("runs", "abc", "/raw_api/"), "GeoShield-MLLM-Probe/runs/abc/raw_api")

    def test_dryrun_upload_download_with_checksum(self) -> None:
        tmp_path = Path(tempfile.mkdtemp())
        local = tmp_path / "a.txt"
        local.write_text("artifact", encoding="utf-8")
        backend = GoogleDriveBackend(cache_dir=tmp_path / "cache")
        stored = backend.upload_file(local, "runs/run1/raw_api/a.txt", {"run_id": "run1"})
        self.assertTrue(stored.sha256)
        self.assertTrue(backend.exists("runs/run1/raw_api/a.txt"))
        out = tmp_path / "out.txt"
        backend.download_file("runs/run1/raw_api/a.txt", out, expected_sha256=stored.sha256)
        self.assertEqual(out.read_text(encoding="utf-8"), "artifact")


def test_drive_path_resolution(tmp_path: Path) -> None:
    backend = GoogleDriveBackend(cache_dir=tmp_path)
    assert backend.resolve_drive_path("runs", "abc", "/raw_api/") == "GeoShield-MLLM-Probe/runs/abc/raw_api"


def test_dryrun_upload_download_with_checksum(tmp_path: Path) -> None:
    local = tmp_path / "a.txt"
    local.write_text("artifact", encoding="utf-8")
    backend = GoogleDriveBackend(cache_dir=tmp_path / "cache")
    stored = backend.upload_file(local, "runs/run1/raw_api/a.txt", {"run_id": "run1"})
    assert stored.sha256
    assert backend.exists("runs/run1/raw_api/a.txt")
    out = tmp_path / "out.txt"
    backend.download_file("runs/run1/raw_api/a.txt", out, expected_sha256=stored.sha256)
    assert out.read_text(encoding="utf-8") == "artifact"
