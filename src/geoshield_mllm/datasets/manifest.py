from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_TAGS = {
    "iconic_landmark",
    "strong_text_cue",
    "street_view_like",
    "natural_scene",
    "indoor",
    "low_geo_signal",
}


class ManifestItem(BaseModel):
    item_id: str
    dataset_name: str
    subset_name: str
    split_name: str = "unspecified"
    image_path: str | None = None
    drive_path: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    tags: list[str] = Field(default_factory=list)
    city: str | None = None
    region: str | None = None
    country: str | None = None
    source_id: str | None = None
    license: str | None = None
    sha256: str | None = None
    width: int | None = None
    height: int | None = None
    notes: str | None = None

    csv_fields: ClassVar[list[str]] = [
        "item_id", "dataset_name", "subset_name", "split_name", "image_path", "drive_path",
        "latitude", "longitude", "tags", "city", "region", "country", "source_id", "license",
        "sha256", "width", "height", "notes",
    ]

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value: object) -> list[str]:
        if value in (None, ""):
            return []
        if isinstance(value, str):
            if value.startswith("["):
                parsed = json.loads(value)
                return [str(tag) for tag in parsed]
            return [tag for tag in value.split("|") if tag]
        if isinstance(value, list):
            return [str(tag) for tag in value]
        raise TypeError("tags must be a list, JSON list, or pipe-separated string")

    @field_validator("width", "height", mode="before")
    @classmethod
    def parse_optional_int(cls, value: object) -> int | None:
        if value in (None, ""):
            return None
        return int(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        unknown = sorted(set(value) - ALLOWED_TAGS)
        if unknown:
            raise ValueError(f"unknown tags: {unknown}")
        return value

    @model_validator(mode="after")
    def validate_paths(self) -> "ManifestItem":
        if not self.image_path and not self.drive_path:
            raise ValueError("at least one of image_path or drive_path is required")
        return self

    def to_csv_row(self) -> dict[str, object]:
        row = self.model_dump()
        row["tags"] = "|".join(self.tags)
        return {field: row.get(field) for field in self.csv_fields}


def load_manifest(path: Path) -> list[ManifestItem]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return [ManifestItem.model_validate(row) for row in csv.DictReader(handle)]


def save_manifest(path: Path, items: list[ManifestItem]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ManifestItem.csv_fields)
        writer.writeheader()
        for item in items:
            writer.writerow(item.to_csv_row())
