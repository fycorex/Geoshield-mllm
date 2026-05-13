from geoshield_mllm.victims import normalize_response
import unittest


class NormalizeTests(unittest.TestCase):
    def test_normalize_strict_json(self) -> None:
        raw = '{"predicted_location_text":"Shanghai, China","latitude":31.23,"longitude":121.47,"confidence":0.8,"evidence":["sign"],"refusal":false}'
        parsed = normalize_response("techutopia", "gpt-5-mini", "geolocation_infer_v1", raw)
        self.assertEqual(parsed.provider, "techutopia")
        self.assertEqual(parsed.latitude, 31.23)
        self.assertFalse(parsed.refusal)
        self.assertIsNone(parsed.parse_error)

    def test_normalize_parse_error_preserved(self) -> None:
        parsed = normalize_response("techutopia", "gpt-4o", "geolocation_infer_v1", "not json")
        self.assertTrue(parsed.parse_error)
        self.assertEqual(parsed.raw_text, "not json")


def test_normalize_strict_json() -> None:
    raw = '{"predicted_location_text":"Shanghai, China","latitude":31.23,"longitude":121.47,"confidence":0.8,"evidence":["sign"],"refusal":false}'
    parsed = normalize_response("techutopia", "gpt-5-mini", "geolocation_infer_v1", raw)
    assert parsed.provider == "techutopia"
    assert parsed.latitude == 31.23
    assert parsed.refusal is False
    assert parsed.parse_error is None


def test_normalize_parse_error_preserved() -> None:
    parsed = normalize_response("techutopia", "gpt-4o", "geolocation_infer_v1", "not json")
    assert parsed.parse_error
    assert parsed.raw_text == "not json"
