from __future__ import annotations

import os

from geoshield_mllm.victims.base import RawVictimResponse, VictimProvider, VictimRequest


class TechUtopiaProvider(VictimProvider):
    provider_name = "techutopia"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or os.getenv("TECHUTOPIA_API_KEY")
        self.base_url = (base_url or os.getenv("TECHUTOPIA_BASE_URL") or "https://copilot.techutopia.cn/v1").rstrip("/")

    def infer_geolocation(self, request: VictimRequest) -> RawVictimResponse:
        raise NotImplementedError(
            "TechUtopia live calls require explicit credential-backed implementation and budget controls. "
            f"Configured OpenAI-compatible base URL: {self.base_url}"
        )

