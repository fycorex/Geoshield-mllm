"""Apply the tracked adaptive GeoShield overlay to an external GeoShield checkout."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


OVERLAY_ROOT = Path(__file__).resolve().parents[1] / "patches" / "external_geoshield_adaptive"


def iter_overlay_files() -> list[Path]:
    return sorted(
        path
        for path in OVERLAY_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


def apply_overlay(external_root: Path) -> list[Path]:
    if not OVERLAY_ROOT.exists():
        raise FileNotFoundError(f"Overlay directory not found: {OVERLAY_ROOT}")
    if not (external_root / "geoshield.py").exists():
        raise FileNotFoundError(f"GeoShield checkout not found at {external_root}")

    copied: list[Path] = []
    for source in iter_overlay_files():
        relative = source.relative_to(OVERLAY_ROOT)
        target = external_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--external-root",
        type=Path,
        default=Path("external/geoshield"),
        help="Path to the external GeoShield checkout.",
    )
    args = parser.parse_args()

    copied = apply_overlay(args.external_root.resolve())
    for path in copied:
        print(path)


if __name__ == "__main__":
    main()
