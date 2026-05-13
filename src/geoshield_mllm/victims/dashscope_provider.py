from __future__ import annotations

from geoshield_mllm.victims.base import RawVictimResponse, VictimProvider, VictimRequest


class DashScopeProvider(VictimProvider):
    provider_name = "dashscope"

    def infer_geolocation(self, request: VictimRequest) -> RawVictimResponse:
        raise NotImplementedError("DashScope live calls require credentials and budget controls.")

