from pathlib import Path

from geoshield_mllm.attacks.base import AttackConfig
from geoshield_mllm.attacks.external_geoshield import _alpha_to_geoshield_units, _epsilon_to_geoshield_units
from geoshield_mllm.utils.io import read_yaml


def test_geoshield_unit_conversion() -> None:
    assert _epsilon_to_geoshield_units("8/255") == 8
    assert _epsilon_to_geoshield_units(8) == 8
    assert _alpha_to_geoshield_units("1/255") == 1.0
    assert _alpha_to_geoshield_units(1.0) == 1.0


def test_adaptive_attack_config_parses() -> None:
    cfg = AttackConfig(**read_yaml(Path("configs/attacks/geoshield_attack_vllm_adaptive.yaml")))
    assert cfg.attack_vllm_transfer["enabled"] is True
    assert cfg.attack_vllm_transfer["losses"]["visual_contrastive_loss"] is True
    assert "DINOv2" in cfg.surrogate["primary_backbones"]
    assert "Qwen2VL" in cfg.surrogate["open_vllm_backbones"]
