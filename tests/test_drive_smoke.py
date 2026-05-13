from pathlib import Path

from geoshield_mllm.storage.drive_smoke import run_drive_smoke


def test_drive_smoke_dry_run(tmp_path: Path) -> None:
    report = run_drive_smoke(
        auth_mode="dry-run",
        cache_dir=tmp_path / "drive_cache",
        local_dir=tmp_path / "local",
        report_path=tmp_path / "report.json",
    )
    assert report.ok is True
    assert report.downloaded_matches is True
    assert report.file_id and report.file_id.startswith("dryrun:")
    assert (tmp_path / "report.json").exists()

