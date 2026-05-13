from __future__ import annotations

from geoshield_mllm.victims.base import RawVictimResponse, VictimProvider, VictimRequest


class OpenAIProvider(VictimProvider):
    provider_name = "openai"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def infer_geolocation(self, request: VictimRequest) -> RawVictimResponse:
        raise NotImplementedError("First-party OpenAI live calls are intentionally not enabled without credentials and budget controls.")

