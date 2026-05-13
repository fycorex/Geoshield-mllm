from __future__ import annotations

from geoshield_mllm.victims.base import VictimProvider
from geoshield_mllm.victims.techutopia_provider import TechUtopiaProvider


def build_provider(provider: str) -> VictimProvider:
    if provider == "techutopia":
        return TechUtopiaProvider()
    raise KeyError(f"Provider is not wired for live eval yet: {provider}")

