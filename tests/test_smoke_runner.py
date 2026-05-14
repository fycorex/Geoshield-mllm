import json
from pathlib import Path

from geoshield_mllm.datasets import ManifestItem, save_manifest
from geoshield_mllm.smoke_runner import run_paper_aligned_smoke


def test_paper_aligned_smoke_records_geoshield_settings(tmp_path: Path) -> None:
    image = tmp_path / "a.jpg"
    image.write_bytes(b"fake-image")
    manifest = tmp_path / "manifest.csv"
    save_manifest(
        manifest,
        [
            ManifestItem(
                item_id="item1",
                dataset_name="im2gps3k",
                subset_name="im2gps3k_100_pilot",
                image_path=str(image),
                latitude=1.0,
                longitude=2.0,
            )
        ],
    )
    attack_config = tmp_path / "attack.yaml"
    attack_config.write_text(
        "\n".join(
            [
                "attack_name: geoshield_like",
                "attack_variant: paper_aligned_baseline",
                "resize: 640",
                "epsilon: 8/255",
                "step_size: 1/255",
                "steps: 200",
                "output_root: runs/{run_id}/adv",
                "seed: 1337",
            ]
        ),
        encoding="utf-8",
    )
    eval_config = tmp_path / "eval.yaml"
    eval_config.write_text(
        "\n".join(
            [
                "run_goal: smoke",
                "victim_providers: [techutopia]",
                "victim_models:",
                "  techutopia: [gpt-4o]",
                "prompt_version: geolocation_infer_v1",
                "geocoder_backend: google_geocode",
                "storage_backend: google_drive",
            ]
        ),
        encoding="utf-8",
    )
    prompt = tmp_path / "prompt.md"
    prompt.write_text("Return JSON", encoding="utf-8")

    summary = run_paper_aligned_smoke(
        manifest_path=manifest,
        attack_config_path=attack_config,
        eval_config_path=eval_config,
        prompt_path=prompt,
        run_id="smoke",
        limit=1,
        dry_run=True,
        output_root=tmp_path / "runs",
    )

    assert summary.attack_records == 1
    assert summary.eval_records == 1
    run_card = json.loads((tmp_path / "runs/smoke/run_card.json").read_text(encoding="utf-8"))
    assert run_card["paper_alignment"]["resize"] == 640
    assert run_card["paper_alignment"]["epsilon"] == "8/255"
    assert run_card["paper_alignment"]["steps"] == 200
