from __future__ import annotations

from geoshield_mllm.attacks.base import Attack, AttackConfig
from geoshield_mllm.attacks.geoshield_like import GeoShieldLikeAttack


def build_attack(config: AttackConfig) -> Attack:
    if config.attack_name == "geoshield_like":
        return GeoShieldLikeAttack(config)
    raise KeyError(f"Unknown attack: {config.attack_name}")

