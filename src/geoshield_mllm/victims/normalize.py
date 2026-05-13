from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class NormalizedPrediction:
    provider: str
    model: str
    prompt_version: str
    raw_text: str
    predicted_location_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    confidence: float | None = None
    evidence: list[str] = field(default_factory=list)
    refusal: bool = False
    parse_error: str | None = None
    geocode_fallback_used: bool = False
    raw_response_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _extract_json(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


def normalize_response(provider: str, model: str, prompt_version: str, raw_text: str, raw_response_path: str | None = None) -> NormalizedPrediction:
    prediction = NormalizedPrediction(
        provider=provider,
        model=model,
        prompt_version=prompt_version,
        raw_text=raw_text,
        raw_response_path=raw_response_path,
    )
    try:
        data = _extract_json(raw_text)
    except Exception as exc:  # noqa: BLE001
        prediction.parse_error = str(exc)
        return prediction

    prediction.predicted_location_text = data.get("predicted_location_text")
    prediction.latitude = data.get("latitude")
    prediction.longitude = data.get("longitude")
    prediction.confidence = data.get("confidence")
    prediction.evidence = list(data.get("evidence") or [])
    prediction.refusal = bool(data.get("refusal", False))
    return prediction

