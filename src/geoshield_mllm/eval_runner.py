from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from geoshield_mllm.datasets import load_manifest
from geoshield_mllm.metrics import haversine_km, threshold_hits
from geoshield_mllm.utils.io import write_json
from geoshield_mllm.utils.time import utc_now_iso
from geoshield_mllm.victims import build_provider, normalize_response
from geoshield_mllm.victims.base import RawVictimResponse, VictimRequest


@dataclass(frozen=True)
class EvalRunSummary:
    run_id: str
    manifest: str
    provider: str
    models: list[str]
    limit: int
    dry_run: bool
    output_dir: str
    num_records: int


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _dry_raw_response(provider: str, model: str) -> RawVictimResponse:
    payload = {
        "dry_run": True,
        "raw_text": "",
        "error": "dry_run_no_api_call",
        "created_at": utc_now_iso(),
    }
    return RawVictimResponse(provider=provider, model=model, content=payload, raw_text="")


def _error_raw_response(provider: str, model: str, exc: Exception) -> RawVictimResponse:
    status_code = getattr(exc, "status_code", None)
    response = getattr(exc, "response", None)
    response_text = None
    if response is not None:
        try:
            response_text = response.text
        except Exception:  # noqa: BLE001
            response_text = None
    payload = {
        "error": True,
        "error_type": type(exc).__name__,
        "message": str(exc),
        "status_code": status_code,
        "response_text": response_text,
        "created_at": utc_now_iso(),
    }
    return RawVictimResponse(provider=provider, model=model, content=payload, raw_text="")


def run_eval(
    *,
    manifest_path: Path,
    prompt_path: Path,
    run_id: str,
    provider_name: str = "techutopia",
    models: list[str] | None = None,
    limit: int = 5,
    dry_run: bool = True,
    output_root: Path = Path("runs"),
) -> EvalRunSummary:
    load_dotenv()
    models = models or ["gpt-4o", "gpt-5-mini"]
    prompt = prompt_path.read_text(encoding="utf-8")
    items = load_manifest(manifest_path)[:limit]
    out_dir = output_root / run_id
    raw_dir = out_dir / "raw_api"
    normalized_dir = out_dir / "normalized"
    metrics_dir = out_dir / "metrics"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    provider = None if dry_run else build_provider(provider_name)
    records: list[dict] = []

    for item in items:
        if not item.image_path:
            raise ValueError(f"Manifest item {item.item_id} has no image_path")
        for model in models:
            request = VictimRequest(
                image_path=Path(item.image_path),
                prompt=prompt,
                prompt_version=prompt_path.stem,
                model=model,
            )
            provider_error = None
            if dry_run:
                raw = _dry_raw_response(provider_name, model)
            else:
                try:
                    raw = provider.infer_geolocation(request)  # type: ignore[union-attr]
                except Exception as exc:  # noqa: BLE001 - errors are preserved as run artifacts.
                    provider_error = type(exc).__name__
                    raw = _error_raw_response(provider_name, model, exc)
            raw_path = raw_dir / f"{item.item_id}_{provider_name}_{model}.json"
            write_json(raw_path, raw.content)
            normalized = normalize_response(provider_name, model, prompt_path.stem, raw.raw_text, str(raw_path))
            if dry_run:
                normalized.parse_error = "dry_run_no_api_call"
            elif provider_error:
                normalized.parse_error = f"provider_error:{provider_error}"
            distance_km = None
            if normalized.latitude is not None and normalized.longitude is not None:
                distance_km = haversine_km(item.latitude, item.longitude, normalized.latitude, normalized.longitude)
            record = {
                "run_id": run_id,
                "item_id": item.item_id,
                "dataset_name": item.dataset_name,
                "subset_name": item.subset_name,
                "ground_truth_latitude": item.latitude,
                "ground_truth_longitude": item.longitude,
                "distance_km": distance_km,
                "dry_run": dry_run,
                "provider_error": provider_error,
                **normalized.to_dict(),
                **threshold_hits(distance_km),
            }
            records.append(record)

    predictions_path = normalized_dir / "predictions.jsonl"
    with predictions_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    summary = EvalRunSummary(
        run_id=run_id,
        manifest=str(manifest_path),
        provider=provider_name,
        models=models,
        limit=limit,
        dry_run=dry_run,
        output_dir=str(out_dir),
        num_records=len(records),
    )
    write_json(metrics_dir / "summary.json", summary.__dict__)
    return summary
