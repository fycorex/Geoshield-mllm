from __future__ import annotations

THRESHOLDS_KM = (1, 25, 200, 750, 2500)


def threshold_hits(distance_km: float | None, thresholds: tuple[int, ...] = THRESHOLDS_KM) -> dict[str, bool | None]:
    return {f"acc_{threshold}km": None if distance_km is None else distance_km <= threshold for threshold in thresholds}

