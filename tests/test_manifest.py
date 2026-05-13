from pathlib import Path

import tempfile
import unittest

from geoshield_mllm.datasets import ManifestItem, deterministic_sample, load_manifest, save_manifest


class ManifestTests(unittest.TestCase):
    def test_manifest_roundtrip(self) -> None:
        tmp_path = Path(tempfile.mkdtemp())
        path = tmp_path / "manifest.csv"
        item = ManifestItem(
            item_id="a",
            dataset_name="gsv",
            subset_name="gsv_100_pilot",
            image_path="clean/a.jpg",
            latitude=31.2304,
            longitude=121.4737,
            tags=["street_view_like", "strong_text_cue"],
        )
        save_manifest(path, [item])
        loaded = load_manifest(path)
        self.assertEqual(loaded[0].item_id, "a")
        self.assertEqual(loaded[0].tags, ["street_view_like", "strong_text_cue"])

    def test_manifest_requires_path(self) -> None:
        with self.assertRaises(ValueError):
            ManifestItem(item_id="a", dataset_name="gsv", subset_name="s", latitude=0, longitude=0)

    def test_deterministic_sample_is_stable(self) -> None:
        items = list(range(20))
        self.assertEqual(deterministic_sample(items, 5, seed=7), deterministic_sample(items, 5, seed=7))


def test_manifest_roundtrip(tmp_path: Path) -> None:
    item = ManifestItem(
        item_id="a",
        dataset_name="gsv",
        subset_name="gsv_100_pilot",
        image_path="clean/a.jpg",
        latitude=31.2304,
        longitude=121.4737,
        tags=["street_view_like", "strong_text_cue"],
    )
    save_manifest(path, [item])
    loaded = load_manifest(path)
    assert loaded[0].item_id == "a"
    assert loaded[0].tags == ["street_view_like", "strong_text_cue"]


def test_manifest_requires_path() -> None:
    try:
        ManifestItem(item_id="a", dataset_name="gsv", subset_name="s", latitude=0, longitude=0)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_deterministic_sample_is_stable() -> None:
    items = list(range(20))
    assert deterministic_sample(items, 5, seed=7) == deterministic_sample(items, 5, seed=7)
