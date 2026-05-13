from __future__ import annotations

from pathlib import Path

import typer

from geoshield_mllm.attacks import AttackConfig, build_attack
from geoshield_mllm.datasets import load_manifest, prepare_dataset_from_config
from geoshield_mllm.storage import GoogleDriveBackend
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
def dry_run_attack(manifest: Path, attack_config: Path, output: Path = Path("runs/dry_run_attack.json")) -> None:
    items = load_manifest(manifest)
    cfg = AttackConfig(**read_yaml(attack_config))
    attack = build_attack(cfg)
    results = [attack.run_item(item, output.parent, dry_run=True).__dict__ for item in items]
    write_json(output, results)
    typer.echo(f"wrote {len(results)} dry-run attack records to {output}")


if __name__ == "__main__":
    app()
