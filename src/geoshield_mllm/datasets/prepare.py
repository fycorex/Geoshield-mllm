from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from geoshield_mllm.datasets.manifest import ManifestItem, save_manifest
from geoshield_mllm.datasets.sampler import deterministic_sample
from geoshield_mllm.utils.hashing import sha256_file
from geoshield_mllm.utils.io import read_yaml

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


@dataclass(frozen=True)
class PrepareReport:
    dataset_name: str
    subset_name: str
    source_root: str
    output_manifest: str
    requested_sample_size: int
    discovered_rows: int
    rows_with_coordinates: int
    written_rows: int
    skipped_reason: str | None = None

    def to_markdown(self) -> str:
        lines = [
            f"# Dataset Availability: {self.subset_name}",
            "",
            f"- dataset: `{self.dataset_name}`",
            f"- source root: `{self.source_root}`",
            f"- output manifest: `{self.output_manifest}`",
            f"- requested sample size: `{self.requested_sample_size}`",
            f"- discovered rows: `{self.discovered_rows}`",
            f"- rows with coordinates: `{self.rows_with_coordinates}`",
            f"- written rows: `{self.written_rows}`",
        ]
        if self.skipped_reason:
            lines.append(f"- skipped reason: {self.skipped_reason}")
        lines.append("")
        return "\n".join(lines)


def _first_present(row: dict[str, Any], names: list[str]) -> str | None:
    lowered = {str(key).lower(): value for key, value in row.items()}
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            return str(value)
        value = lowered.get(name.lower())
        if value not in (None, ""):
            return str(value)
    return None


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _discover_image_rows(source_root: Path, dataset_name: str) -> list[dict[str, Any]]:
    return [
        {"source_path": str(path), "dataset": dataset_name, "source_id": path.name}
        for path in sorted(source_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def load_source_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    metadata_manifest = config.get("metadata_manifest")
    source_root = Path(str(config["source_root"])).expanduser()
    if metadata_manifest:
        path = Path(str(metadata_manifest)).expanduser()
        if path.suffix.lower() == ".csv":
            return _read_csv(path)
        if path.suffix.lower() in {".jsonl", ".ndjson"}:
            return _read_jsonl(path)
        raise ValueError(f"Unsupported metadata manifest format: {path}")
    if source_root.is_file():
        if source_root.suffix.lower() == ".csv":
            return _read_csv(source_root)
        if source_root.suffix.lower() in {".jsonl", ".ndjson"}:
            return _read_jsonl(source_root)
        raise ValueError(f"Unsupported source file format: {source_root}")
    if source_root.is_dir():
        return _discover_image_rows(source_root, str(config["dataset_name"]))
    raise FileNotFoundError(source_root)


def row_to_manifest_item(row: dict[str, Any], config: dict[str, Any], index: int) -> ManifestItem | None:
    lat = _first_present(row, ["latitude", "lat", "true_lat", "LAT"])
    lon = _first_present(row, ["longitude", "lon", "lng", "true_lon", "LON"])
    if lat is None or lon is None:
        return None
    image_path = _first_present(row, ["image_path", "source_path", "path", "file", "filename", "img_id", "IMG_ID"])
    drive_path = _first_present(row, ["drive_path"])
    if image_path:
        image = Path(image_path).expanduser()
        if not image.is_absolute():
            image = Path(str(config["source_root"])).expanduser() / image
        image_path = str(image)
    source_id = _first_present(row, ["source_id", "id", "img_id", "IMG_ID", "filename"]) or f"{config['dataset_name']}_{index:06d}"
    tags = row.get("tags") or []
    if isinstance(tags, str) and "," in tags and "|" not in tags:
        tags = "|".join(part.strip() for part in tags.split(",") if part.strip())
    sha256 = None
    if image_path and Path(image_path).is_file():
        sha256 = sha256_file(Path(image_path))
    return ManifestItem(
        item_id=f"{config['subset_name']}_{index:06d}",
        dataset_name=str(config["dataset_name"]),
        subset_name=str(config["subset_name"]),
        split_name=str(config.get("split_name", "unspecified")),
        image_path=image_path,
        drive_path=drive_path,
        latitude=float(lat),
        longitude=float(lon),
        tags=tags,
        city=_first_present(row, ["city", "city_name", "true_city"]),
        region=_first_present(row, ["region", "state"]),
        country=_first_present(row, ["country", "true_country"]),
        source_id=source_id,
        license=_first_present(row, ["license"]),
        sha256=sha256 or _first_present(row, ["sha256"]),
        notes=_first_present(row, ["notes"]),
    )


def prepare_dataset_from_config(config_path: Path, *, write_availability_report: Path | None = None) -> PrepareReport:
    config = read_yaml(config_path)
    rows = [
        row
        for row in load_source_rows(config)
        if str(row.get("dataset", config["dataset_name"])) == str(config["dataset_name"])
    ]
    items = [
        item
        for idx, row in enumerate(rows, start=1)
        if (item := row_to_manifest_item(row, config, idx)) is not None
    ]
    requested = int(config["sample_size"])
    report = PrepareReport(
        dataset_name=str(config["dataset_name"]),
        subset_name=str(config["subset_name"]),
        source_root=str(config["source_root"]),
        output_manifest=str(config["output_manifest"]),
        requested_sample_size=requested,
        discovered_rows=len(rows),
        rows_with_coordinates=len(items),
        written_rows=0,
    )
    if len(items) < requested:
        report = PrepareReport(
            **{**report.__dict__, "skipped_reason": f"Need {requested} coordinate-bearing rows, found {len(items)}."}
        )
    else:
        selected = deterministic_sample(items, requested, int(config["seed"]))
        save_manifest(Path(str(config["output_manifest"])), selected)
        report = PrepareReport(**{**report.__dict__, "written_rows": len(selected)})
    if write_availability_report:
        write_availability_report.parent.mkdir(parents=True, exist_ok=True)
        existing = write_availability_report.read_text(encoding="utf-8") if write_availability_report.exists() else ""
        write_availability_report.write_text((existing.rstrip() + "\n\n" + report.to_markdown()).strip() + "\n", encoding="utf-8")
    return report
