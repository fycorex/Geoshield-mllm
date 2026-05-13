# Storage

## Drive Root

All large artifacts are stored under `GeoShield-MLLM-Probe/`.

## Hierarchy

```text
GeoShield-MLLM-Probe/
  datasets/
    gsv_100_pilot/
      clean/
      metadata/
    im2gps3k_100_pilot/
      clean/
      metadata/
    gsv_500_stratified/
      clean/
      metadata/
    im2gps3k_500_stratified/
      clean/
      metadata/
  runs/
    <run_id>/
      clean/
      adv/
      delta/
      raw_api/
      normalized/
      metrics/
      reports/
  shared/
    schemas/
    prompt_versions/
```

## Upload Policy

Use resumable upload for large files. Each uploaded artifact should have a JSON sidecar with project, run id, dataset name, item id, variant, local SHA-256, creation time, and git commit hash. Use Drive `appProperties` only for short searchable metadata; keep full metadata in sidecars.

## Local Cache

The local cache stores downloaded artifacts and folder id mappings. Cached files are valid only when their SHA-256 matches the expected checksum.

## Backend Interface

Storage backends implement `upload_file`, `download_file`, `exists`, `list_run_artifacts`, `resolve_drive_path`, and `ensure_folder_path`.

## Naming Rules

Use deterministic paths, stable item ids, and explicit variants such as `clean`, `adv`, `delta`, `raw_api`, `normalized`, and `metrics`.

## Git Boundary

Do not commit image batches, adversarial outputs, deltas, raw API dumps, normalized prediction bundles, or metrics bundles. Commit only lightweight manifests, schemas, docs, and summary reports.

