from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from geoshield_mllm.attacks import AttackConfig, build_attack
from geoshield_mllm.datasets import load_manifest
from geoshield_mllm.eval_runner import EvalRunSummary, run_eval
from geoshield_mllm.run_context import current_git_commit
from geoshield_mllm.utils.io import read_yaml, write_json
from geoshield_mllm.utils.time import utc_now_iso


@dataclass(frozen=True)
class PaperAlignedSmokeSummary:
    run_id: str
    manifest: str
    attack_config: str
    eval_config: str
    prompt_path: str
    limit: int
    dry_run: bool
    output_dir: str
    attack_records: int
    eval_records: int


def _first_provider(eval_config: dict[str, Any]) -> str:
    providers = eval_config.get("victim_providers") or ["techutopia"]
    if not isinstance(providers, list) or not providers:
        raise ValueError("eval config must define a non-empty victim_providers list")
    return str(providers[0])


def _models_for_provider(eval_config: dict[str, Any], provider: str) -> list[str]:
    by_provider = eval_config.get("victim_models") or {}
    models = by_provider.get(provider) if isinstance(by_provider, dict) else None
    if not models:
        return ["gpt-4o", "gpt-5-mini"]
    return [str(model) for model in models]


def run_paper_aligned_smoke(
    *,
    manifest_path: Path,
    attack_config_path: Path,
    eval_config_path: Path,
    prompt_path: Path,
    run_id: str,
    limit: int = 2,
    dry_run: bool = True,
    output_root: Path = Path("runs"),
) -> PaperAlignedSmokeSummary:
    attack_config = AttackConfig(**read_yaml(attack_config_path))
    eval_config = read_yaml(eval_config_path)
    provider = _first_provider(eval_config)
    models = _models_for_provider(eval_config, provider)
    items = load_manifest(manifest_path)[:limit]
    output_dir = output_root / run_id
    attack_dir = output_dir / "attack_metadata"
    attack_dir.mkdir(parents=True, exist_ok=True)

    attack = build_attack(attack_config)
    attack_records = [attack.run_item(item, attack_dir, dry_run=True).__dict__ for item in items]
    with (attack_dir / "records.jsonl").open("w", encoding="utf-8") as handle:
        for record in attack_records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    eval_summary: EvalRunSummary = run_eval(
        manifest_path=manifest_path,
        prompt_path=prompt_path,
        run_id=run_id,
        provider_name=provider,
        models=models,
        limit=limit,
        dry_run=dry_run,
        output_root=output_root,
    )
    run_card = {
        "run_id": run_id,
        "goal": eval_config.get("run_goal", "paper-aligned smoke"),
        "paper_alignment": {
            "primary_paper": "GeoShield AAAI 2026 / arXiv:2508.03209",
            "related_attack_reference": "arXiv:2505.01050 only; not the GeoShield paper",
            "resize": attack_config.resize,
            "epsilon": attack_config.epsilon,
            "step_size": attack_config.step_size,
            "steps": attack_config.steps,
            "attack_name": attack_config.attack_name,
            "attack_variant": attack_config.attack_variant,
            "attack_execution": "dry-run metadata only until real GeoShield integration is wired",
        },
        "manifest": str(manifest_path),
        "num_images": len(items),
        "victim_provider": provider,
        "victim_models": models,
        "prompt_version": prompt_path.stem,
        "geocoder_backend": eval_config.get("geocoder_backend"),
        "storage_backend": eval_config.get("storage_backend"),
        "dry_run": dry_run,
        "git_commit_hash": current_git_commit(),
        "started_at": utc_now_iso(),
        "finished_at": utc_now_iso(),
        "output_dir": str(output_dir),
        "notes": "Smoke success means config wiring/artifact writing succeeded; it is not an experimental result.",
    }
    write_json(output_dir / "run_card.json", run_card)
    summary = PaperAlignedSmokeSummary(
        run_id=run_id,
        manifest=str(manifest_path),
        attack_config=str(attack_config_path),
        eval_config=str(eval_config_path),
        prompt_path=str(prompt_path),
        limit=limit,
        dry_run=dry_run,
        output_dir=str(output_dir),
        attack_records=len(attack_records),
        eval_records=eval_summary.num_records,
    )
    write_json(output_dir / "metrics" / "paper_aligned_smoke_summary.json", summary.__dict__)
    return summary
