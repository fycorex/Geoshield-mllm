from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from geoshield_mllm.metrics.thresholds import THRESHOLDS_KM


def rate(values: Iterable[bool]) -> float:
    values = list(values)
    return sum(1 for value in values if value) / len(values) if values else 0.0


def summarize_predictions(rows: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = [row.get("parse_error") in (None, "") for row in rows]
    refusals = [bool(row.get("refusal")) for row in rows]
    fallbacks = [bool(row.get("geocode_fallback_used")) for row in rows]
    summary: dict[str, Any] = {
        "num_predictions": len(rows),
        "parse_success_rate": rate(parsed),
        "refusal_rate": rate(refusals),
        "geocode_fallback_rate": rate(fallbacks),
    }
    for threshold in THRESHOLDS_KM:
        key = f"acc_{threshold}km"
        valid = [row[key] for row in rows if row.get(key) is not None]
        summary[key] = rate(valid)
    return summary


def breakdown_by(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key, "unknown"))].append(row)
    return {group: summarize_predictions(group_rows) for group, group_rows in sorted(groups.items())}

