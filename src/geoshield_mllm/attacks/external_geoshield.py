from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from geoshield_mllm.attacks.base import AttackConfig
from geoshield_mllm.datasets import ManifestItem, load_manifest
from geoshield_mllm.run_context import current_git_commit
from geoshield_mllm.utils.hashing import sha256_file
from geoshield_mllm.utils.io import write_json
from geoshield_mllm.utils.time import utc_now_iso
from geoshield_mllm.victims import build_provider
from geoshield_mllm.victims.base import VictimRequest


NON_GEO_PROMPT = (
    "Describe the visible scene, objects, materials, layout, weather, and activities. "
    "Do not identify or guess the country, city, street, landmark name, language, or exact location."
)


@dataclass(frozen=True)
class ExternalGeoShieldRunSummary:
    run_id: str
    output_dir: str
    num_items: int
    adv_records: int
    command: list[str]
    strict_geoee: bool
    descriptions_provider: str
    finished_at: str


def _parse_fraction(value: str | float | int) -> float:
    if isinstance(value, (float, int)):
        return float(value)
    text = str(value).strip()
    if "/" in text:
        num, den = text.split("/", 1)
        return float(num) / float(den)
    return float(text)


def _epsilon_to_geoshield_units(value: str | float | int) -> int:
    parsed = _parse_fraction(value)
    if parsed <= 1.0:
        return int(round(parsed * 255.0))
    return int(round(parsed))


def _alpha_to_geoshield_units(value: str | float | int) -> float:
    parsed = _parse_fraction(value)
    if parsed < 1.0:
        return parsed * 255.0
    return parsed


def _safe_name(item: ManifestItem) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in item.item_id)


def _resize_square(src: Path, dst: Path, size: int) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as image:
        image = image.convert("RGB")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (size, size), (0, 0, 0))
        canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
        canvas.save(dst, "PNG")


def _extract_raw_text(content: dict) -> str:
    if "raw_text" in content and isinstance(content["raw_text"], str):
        return content["raw_text"]
    try:
        return content["choices"][0]["message"]["content"]
    except Exception:  # noqa: BLE001
        return ""


def _write_descriptions(
    *,
    items: list[ManifestItem],
    clean_paths: dict[str, Path],
    output_path: Path,
    provider_name: str,
    model: str,
    allow_fallback: bool,
) -> str:
    descriptions: dict[str, dict[str, str]] = {}
    used_provider = provider_name
    provider = None
    if provider_name != "fallback":
        try:
            provider = build_provider(provider_name)
        except Exception:
            if not allow_fallback:
                raise
            used_provider = "fallback"
    for item in items:
        clean_path = clean_paths[item.item_id]
        text = ""
        if provider is not None:
            request = VictimRequest(
                image_path=clean_path,
                prompt=NON_GEO_PROMPT,
                prompt_version="describe_non_geo_v1",
                model=model,
            )
            try:
                raw = provider.describe_non_geo(request)
                text = _extract_raw_text(raw.content).strip()
            except Exception:
                if not allow_fallback:
                    raise
        if not text:
            text = "A photograph with visible objects, scene layout, and environmental context."
        descriptions[clean_path.name] = {
            "description": text,
            "provider": used_provider,
            "model": model if used_provider != "fallback" else "fallback",
            "prompt": NON_GEO_PROMPT,
        }
    write_json(output_path, descriptions)
    return used_provider


def _collect_adv_images(raw_output: Path, adv_dir: Path, items: list[ManifestItem], clean_paths: dict[str, Path]) -> list[dict]:
    records = []
    for item in items:
        clean_name = clean_paths[item.item_id].name
        matches = sorted((raw_output / "img").rglob(clean_name))
        if not matches:
            raise RuntimeError(f"Missing GeoShield output for {item.item_id} ({clean_name}) under {raw_output / 'img'}")
        adv_path = adv_dir / f"{_safe_name(item)}.png"
        adv_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(matches[-1], adv_path)
        records.append(
            {
                "item_id": item.item_id,
                "clean_path": str(clean_paths[item.item_id]),
                "adv_path": str(adv_path),
                "adv_sha256": sha256_file(adv_path),
                "source_geoshield_output": str(matches[-1]),
            }
        )
    return records


def run_external_geoshield(
    *,
    manifest_path: Path,
    attack_config: AttackConfig,
    run_id: str,
    limit: int,
    output_root: Path = Path("runs"),
    external_root: Path = Path("external/geoshield"),
    python: str = "/home/ubuntu/miniconda3/envs/geoshield/bin/python",
    device: str = "cpu",
    backbones: list[str] | None = None,
    strict_geoee: bool = False,
    groundingdino_device: str = "cpu",
    descriptions_provider: str = "fallback",
    descriptions_model: str = "gpt-4o",
    allow_description_fallback: bool = True,
    steps_override: int | None = None,
    resize_override: int | None = None,
) -> ExternalGeoShieldRunSummary:
    items = load_manifest(manifest_path)[:limit]
    if not items:
        raise ValueError(f"No items loaded from {manifest_path}")
    output_dir = output_root / run_id
    clean_dir = output_dir / "clean"
    target_dir = output_dir / "target"
    raw_output = output_dir / "geoshield_raw"
    metadata_dir = output_dir / "metadata"
    adv_dir = output_dir / "adv"
    log_dir = output_dir / "logs"
    for path in (clean_dir, target_dir, raw_output, metadata_dir, adv_dir, log_dir):
        path.mkdir(parents=True, exist_ok=True)

    resize = resize_override or attack_config.resize
    clean_paths: dict[str, Path] = {}
    for item in items:
        if not item.image_path:
            raise ValueError(f"Manifest item {item.item_id} has no image_path")
        src = Path(item.image_path)
        clean_name = f"{_safe_name(item)}.png"
        clean_path = clean_dir / clean_name
        target_path = target_dir / clean_name
        _resize_square(src, clean_path, resize)
        shutil.copy2(clean_path, target_path)
        clean_paths[item.item_id] = clean_path

    description_path = metadata_dir / "descriptions.json"
    used_description_provider = _write_descriptions(
        items=items,
        clean_paths=clean_paths,
        output_path=description_path,
        provider_name=descriptions_provider,
        model=descriptions_model,
        allow_fallback=allow_description_fallback,
    )

    bbox_path = metadata_dir / "groundingdino_bboxes.json"
    if strict_geoee:
        bbox_cmd = [
            python,
            "scripts/repro30/generate_groundingdino_bboxes.py",
            f"--output-dir={output_dir.resolve()}",
            f"--device={groundingdino_device}",
        ]
        result = subprocess.run(bbox_cmd, cwd=external_root, text=True, capture_output=True, check=False)
        (log_dir / "groundingdino.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode != 0:
            raise RuntimeError(f"GroundingDINO failed with exit code {result.returncode}; see {log_dir / 'groundingdino.log'}")

    backbones = backbones or ["B16", "B32"]
    steps = steps_override or attack_config.steps
    cmd = [
        python,
        "geoshield.py",
        f"data.cle_data_path={clean_dir.resolve()}",
        f"data.tgt_data_path={target_dir.resolve()}",
        f"data.output={raw_output.resolve()}",
        f"data.num_samples={len(items)}",
        "data.batch_size=1",
        f"data.description_json_path={description_path.resolve()}",
        f"optim.epsilon={_epsilon_to_geoshield_units(attack_config.epsilon)}",
        f"optim.alpha={_alpha_to_geoshield_units(attack_config.step_size)}",
        f"optim.steps={steps}",
        f"model.input_res={resize}",
        f"model.device={device}",
        "model.ensemble=true",
        "model.backbone=[" + ",".join(backbones) + "]",
    ]
    if strict_geoee:
        cmd.append(f"data.bbox_json_path={bbox_path.resolve()}")

    env = os.environ.copy()
    env["WANDB_MODE"] = "disabled"
    started_at = utc_now_iso()
    result = subprocess.run(cmd, cwd=external_root, env=env, text=True, capture_output=True, check=False)
    (log_dir / "geoshield.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"GeoShield failed with exit code {result.returncode}; see {log_dir / 'geoshield.log'}")

    adv_records = _collect_adv_images(raw_output, adv_dir, items, clean_paths)
    write_json(metadata_dir / "adv_records.json", adv_records)
    run_card = {
        "run_id": run_id,
        "attack_name": attack_config.attack_name,
        "attack_variant": attack_config.attack_variant,
        "manifest": str(manifest_path),
        "num_items": len(items),
        "resize": resize,
        "epsilon": attack_config.epsilon,
        "step_size": attack_config.step_size,
        "steps": steps,
        "device": device,
        "backbones": backbones,
        "strict_geoee": strict_geoee,
        "groundingdino_bbox_path": str(bbox_path) if strict_geoee else None,
        "description_path": str(description_path),
        "description_provider": used_description_provider,
        "git_commit_hash": current_git_commit(),
        "started_at": started_at,
        "finished_at": utc_now_iso(),
        "command": cmd,
        "notes": "Real GeoShield optimization run. If strict_geoee is false, GeoShield falls back to full-image region selection.",
    }
    write_json(output_dir / "run_card.json", run_card)
    summary = ExternalGeoShieldRunSummary(
        run_id=run_id,
        output_dir=str(output_dir),
        num_items=len(items),
        adv_records=len(adv_records),
        command=cmd,
        strict_geoee=strict_geoee,
        descriptions_provider=used_description_provider,
        finished_at=run_card["finished_at"],
    )
    write_json(output_dir / "metrics" / "attack_summary.json", summary.__dict__)
    return summary
