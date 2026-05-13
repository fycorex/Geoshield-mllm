from __future__ import annotations

from pathlib import Path


def update_latest(results_dir: Path, run_id: str) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "latest.md").write_text(f"# Latest Result\n\nLatest run: `{run_id}`\n", encoding="utf-8")


def append_index(results_dir: Path, run_id: str, summary: str) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    index_path = results_dir / "index.md"
    existing = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Results Index\n\n"
    if run_id not in existing:
        existing = existing.rstrip() + f"\n\n- `{run_id}`: {summary}\n"
    index_path.write_text(existing, encoding="utf-8")

