from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class GeocodeResult:
    latitude: float | None
    longitude: float | None
    formatted_address: str | None
    raw: dict


class GoogleGeocoder:
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    def geocode(self, text: str) -> GeocodeResult:
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY is required for live geocoding.")
        response = requests.get(self.endpoint, params={"address": text, "key": self.api_key}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results") or []
        if not results:
            return GeocodeResult(None, None, None, payload)
        first = results[0]
        location = first["geometry"]["location"]
        return GeocodeResult(location["lat"], location["lng"], first.get("formatted_address"), payload)

