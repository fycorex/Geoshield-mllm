from __future__ import annotations

from pathlib import Path

import typer

from geoshield_mllm.attacks import AttackConfig, build_attack
from geoshield_mllm.attacks.external_geoshield import run_external_geoshield
from geoshield_mllm.datasets import load_manifest, prepare_dataset_from_config
from geoshield_mllm.eval_runner import run_eval
from geoshield_mllm.smoke_runner import run_paper_aligned_smoke
from geoshield_mllm.storage import GoogleDriveBackend
from geoshield_mllm.storage.drive_smoke import run_drive_smoke
from geoshield_mllm.utils.io import read_yaml, write_json

app = typer.Typer(help="GeoShield MLLM probing CLI.")


@app.command()
def validate_manifest(path: Path) -> None:
    items = load_manifest(path)
    typer.echo(f"valid manifest: {path} ({len(items)} items)")


@app.command()
def prepare_dataset(config: Path, availability_report: Path = Path("docs/dataset_availability.md")) -> None:
    report = prepare_dataset_from_config(config, write_availability_report=availability_report)
    if report.written_rows:
        typer.echo(f"wrote {report.written_rows} rows to {report.output_manifest}")
    else:
        typer.echo(report.skipped_reason or "no rows written")


@app.command()
def drive_resolve(*parts: str) -> None:
    backend = GoogleDriveBackend()
    typer.echo(backend.resolve_drive_path(*parts))


@app.command()
def drive_smoke_test(
    auth_mode: str = typer.Option("dry-run", "--auth-mode", help="dry-run, oauth, or service-account"),
    report: Path = Path("docs/drive_smoke_latest.json"),
    root: str = "GeoShield-MLLM-Probe",
    oauth_client_secrets: Path = Path("credentials.json"),
    oauth_token: Path = Path(".cache/geoshield_mllm/drive/oauth_token.json"),
    service_account_path: Path | None = None,
) -> None:
    smoke = run_drive_smoke(
        auth_mode=auth_mode,  # type: ignore[arg-type]
        root=root,
        report_path=report,
        oauth_client_secrets=oauth_client_secrets,
        oauth_token=oauth_token,
        service_account_path=service_account_path,
    )
    status = "ok" if smoke.ok else "failed"
    typer.echo(f"drive smoke {status}: {report}")


@app.command()
def dry_run_attack(manifest: Path, attack_config: Path, output: Path = Path("runs/dry_run_attack.json")) -> None:
    items = load_manifest(manifest)
    cfg = AttackConfig(**read_yaml(attack_config))
    attack = build_attack(cfg)
    results = [attack.run_item(item, output.parent, dry_run=True).__dict__ for item in items]
    write_json(output, results)
    typer.echo(f"wrote {len(results)} dry-run attack records to {output}")


@app.command()
def eval_techutopia_smoke(
    manifest: Path = Path("manifests/im2gps3k_100_pilot.csv"),
    prompt: Path = Path("configs/prompts/geolocation_infer_v1.md"),
    run_id: str = "smoke_techutopia",
    limit: int = 5,
    model: list[str] = typer.Option(["gpt-4o", "gpt-5-mini"], "--model"),
    dry_run: bool = True,
) -> None:
    summary = run_eval(
        manifest_path=manifest,
        prompt_path=prompt,
        run_id=run_id,
        provider_name="techutopia",
        models=model,
        limit=limit,
        dry_run=dry_run,
    )
    typer.echo(f"wrote {summary.num_records} eval records to {summary.output_dir}")


@app.command()
def paper_aligned_smoke(
    manifest: Path = Path("manifests/im2gps3k_100_pilot.csv"),
    attack_config: Path = Path("configs/attacks/geoshield_baseline.yaml"),
    eval_config: Path = Path("configs/evals/pilot_openai.yaml"),
    prompt: Path = Path("configs/prompts/geolocation_infer_v1.md"),
    run_id: str = "smoke_paper_aligned_geoshieldbase",
    limit: int = 2,
    dry_run: bool = True,
) -> None:
    summary = run_paper_aligned_smoke(
        manifest_path=manifest,
        attack_config_path=attack_config,
        eval_config_path=eval_config,
        prompt_path=prompt,
        run_id=run_id,
        limit=limit,
        dry_run=dry_run,
    )
    typer.echo(f"paper-aligned smoke wrote {summary.eval_records} eval records to {summary.output_dir}")


@app.command()
def run_geoshield_attack(
    manifest: Path = Path("manifests/im2gps3k_100_pilot.csv"),
    attack_config: Path = Path("configs/attacks/geoshield_baseline.yaml"),
    run_id: str = "geoshield_real_attack_smoke",
    limit: int = 1,
    external_root: Path = Path("external/geoshield"),
    python: str = "/home/ubuntu/miniconda3/envs/geoshield/bin/python",
    device: str = "cpu",
    backbone: list[str] = typer.Option(["B16", "B32"], "--backbone"),
    strict_geoee: bool = typer.Option(False, "--strict-geoee/--no-strict-geoee"),
    groundingdino_device: str = "cpu",
    descriptions_provider: str = "fallback",
    descriptions_model: str = "gpt-4o",
    allow_description_fallback: bool = True,
    steps: int | None = None,
    resize: int | None = None,
) -> None:
    cfg = AttackConfig(**read_yaml(attack_config))
    summary = run_external_geoshield(
        manifest_path=manifest,
        attack_config=cfg,
        run_id=run_id,
        limit=limit,
        external_root=external_root,
        python=python,
        device=device,
        backbones=backbone,
        strict_geoee=strict_geoee,
        groundingdino_device=groundingdino_device,
        descriptions_provider=descriptions_provider,
        descriptions_model=descriptions_model,
        allow_description_fallback=allow_description_fallback,
        steps_override=steps,
        resize_override=resize,
    )
    typer.echo(f"GeoShield generated {summary.adv_records} protected images in {summary.output_dir}")


if __name__ == "__main__":
    app()
