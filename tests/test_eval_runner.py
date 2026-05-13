import json
from pathlib import Path
from unittest.mock import patch

from geoshield_mllm.datasets import ManifestItem, save_manifest
from geoshield_mllm.eval_runner import run_eval
from geoshield_mllm.victims.base import VictimProvider, VictimRequest


def test_run_eval_dry_run_writes_explicit_non_result_records(tmp_path: Path) -> None:
    image = tmp_path / "a.jpg"
    image.write_bytes(b"fake-image")
    manifest = tmp_path / "manifest.csv"
    save_manifest(
        manifest,
        [
            ManifestItem(
                item_id="item1",
                dataset_name="im2gps3k",
                subset_name="smoke",
                image_path=str(image),
                latitude=1.0,
                longitude=2.0,
            )
        ],
    )
    prompt = tmp_path / "prompt.md"
    prompt.write_text("Return JSON", encoding="utf-8")
    summary = run_eval(
        manifest_path=manifest,
        prompt_path=prompt,
        run_id="test_run",
        provider_name="techutopia",
        models=["gpt-4o"],
        limit=1,
        dry_run=True,
        output_root=tmp_path / "runs",
    )
    assert summary.num_records == 1
    predictions = tmp_path / "runs/test_run/normalized/predictions.jsonl"
    record = json.loads(predictions.read_text(encoding="utf-8").strip())
    assert record["dry_run"] is True
    assert record["parse_error"] == "dry_run_no_api_call"
    assert record["distance_km"] is None


def test_run_eval_preserves_provider_errors(tmp_path: Path) -> None:
    image = tmp_path / "a.jpg"
    image.write_bytes(b"fake-image")
    manifest = tmp_path / "manifest.csv"
    save_manifest(
        manifest,
        [
            ManifestItem(
                item_id="item1",
                dataset_name="im2gps3k",
                subset_name="smoke",
                image_path=str(image),
                latitude=1.0,
                longitude=2.0,
            )
        ],
    )
    prompt = tmp_path / "prompt.md"
    prompt.write_text("Return JSON", encoding="utf-8")

    class BrokenProvider(VictimProvider):
        provider_name = "techutopia"

        def infer_geolocation(self, request: VictimRequest):  # type: ignore[no-untyped-def]
            raise PermissionError("Your request was blocked.")

    with patch("geoshield_mllm.eval_runner.build_provider", lambda _: BrokenProvider()):
        summary = run_eval(
            manifest_path=manifest,
            prompt_path=prompt,
            run_id="blocked_run",
            provider_name="techutopia",
            models=["gpt-4o"],
            limit=1,
            dry_run=False,
            output_root=tmp_path / "runs",
        )
    assert summary.num_records == 1
    record = json.loads((tmp_path / "runs/blocked_run/normalized/predictions.jsonl").read_text(encoding="utf-8").strip())
    assert record["provider_error"] == "PermissionError"
    assert record["parse_error"] == "provider_error:PermissionError"
    raw = json.loads((tmp_path / "runs/blocked_run/raw_api/item1_techutopia_gpt-4o.json").read_text(encoding="utf-8"))
    assert raw["error"] is True
    assert raw["message"] == "Your request was blocked."
