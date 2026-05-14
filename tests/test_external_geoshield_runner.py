from pathlib import Path

from geoshield_mllm.attacks.external_geoshield import _alpha_to_geoshield_units, _epsilon_to_geoshield_units


def test_geoshield_unit_conversion() -> None:
    assert _epsilon_to_geoshield_units("8/255") == 8
    assert _epsilon_to_geoshield_units(8) == 8
    assert _alpha_to_geoshield_units("1/255") == 1.0
    assert _alpha_to_geoshield_units(1.0) == 1.0
