from __future__ import annotations

from .manifest import ALLOWED_TAGS


def validate_tags(tags: list[str]) -> list[str]:
    unknown = sorted(set(tags) - ALLOWED_TAGS)
    if unknown:
        raise ValueError(f"unknown tags: {unknown}")
    return tags

