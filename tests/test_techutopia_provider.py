from unittest.mock import patch

from geoshield_mllm.victims.techutopia_provider import TechUtopiaProvider


def test_techutopia_default_headers() -> None:
    with patch.dict("os.environ", {}, clear=True):
        provider = TechUtopiaProvider(api_key="test")
    assert provider.default_headers["User-Agent"] == "Geoshield-mllm/0.1 research-client"


def test_techutopia_extra_headers() -> None:
    with patch.dict("os.environ", {"TECHUTOPIA_EXTRA_HEADERS_JSON": '{"X-Project":"Geoshield-mllm"}'}, clear=True):
        provider = TechUtopiaProvider(api_key="test")
    assert provider.default_headers["X-Project"] == "Geoshield-mllm"


def test_techutopia_image_mode_env() -> None:
    with patch.dict("os.environ", {"TECHUTOPIA_IMAGE_MODE": "none"}, clear=True):
        provider = TechUtopiaProvider(api_key="test")
    assert provider.image_mode == "none"
