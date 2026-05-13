from __future__ import annotations

from geoshield_mllm.victims.base import RawVictimResponse, VictimProvider, VictimRequest


class GeminiProvider(VictimProvider):
    provider_name = "gemini"

    def infer_geolocation(self, request: VictimRequest) -> RawVictimResponse:
        raise NotImplementedError("Gemini live calls require credentials and budget controls.")

