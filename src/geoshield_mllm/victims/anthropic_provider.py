from __future__ import annotations

from geoshield_mllm.victims.base import RawVictimResponse, VictimProvider, VictimRequest


class AnthropicProvider(VictimProvider):
    provider_name = "anthropic"

    def infer_geolocation(self, request: VictimRequest) -> RawVictimResponse:
        raise NotImplementedError("Anthropic live calls require credentials and budget controls.")

