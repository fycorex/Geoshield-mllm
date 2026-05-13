from geoshield_mllm.metrics import haversine_km, threshold_hits
import unittest


class HaversineTests(unittest.TestCase):
    def test_haversine_zero(self) -> None:
        self.assertEqual(haversine_km(0, 0, 0, 0), 0)

    def test_haversine_known_degree_at_equator(self) -> None:
        self.assertTrue(111 <= haversine_km(0, 0, 0, 1) <= 112)

    def test_threshold_hits(self) -> None:
        hits = threshold_hits(100)
        self.assertFalse(hits["acc_25km"])
        self.assertTrue(hits["acc_200km"])


def test_haversine_zero() -> None:
    assert haversine_km(0, 0, 0, 0) == 0


def test_haversine_known_degree_at_equator() -> None:
    assert 111 <= haversine_km(0, 0, 0, 1) <= 112


def test_threshold_hits() -> None:
    hits = threshold_hits(100)
    assert hits["acc_25km"] is False
    assert hits["acc_200km"] is True
