# Architecture

## Goal

Geoshield-mllm provides a reproducible pipeline for measuring when GeoShield-style geolocation privacy defense is weaker than expected under cloud multimodal model evaluation.

## Design Principles

- Configs define experiments; code executes them.
- Manifests are frozen before evaluation.
- Artifacts are content-addressed or checksum-validated where practical.
- Provider-specific raw responses are preserved while normalized schemas enable common metrics.
- Dry-run paths must be useful without credentials.

## Dataflow

1. Dataset config selects a source and deterministic subset.
2. `prepare_dataset` writes a frozen manifest with ground-truth latitude/longitude and optional tags.
3. `run_attack` creates clean/protected artifact records. The dry-run path records metadata only; the external GeoShield runner can call a local GeoShield checkout to generate protected images.
4. `run_eval` sends clean and protected images to configured victim providers, stores raw responses, and normalizes predictions.
5. Geocoding fills missing coordinates from model text when configured and records fallback usage.
6. `aggregate_metrics` computes distances, threshold accuracies, parse/refusal/fallback rates, and subgroup breakdowns.
7. `generate_report` writes run cards, summaries, and Markdown reports.
8. Google Drive stores large artifacts; git stores configs, manifests, reports, and metadata.

## Module Responsibilities

- `datasets`: manifest schema, deterministic sampling, tag validation.
- `attacks`: attack interfaces, dry-run baseline wrapper, and external GeoShield runner. The adaptive branch can pass optimizer overrides for DINOv2/open-VLLM surrogates, Attack-VLLM augmentations, visual contrastive loss, and relative proxy loss.
- `victims`: provider interfaces, API adapters, raw response preservation, normalization.
- `geocode`: Google geocoding fallback adapter.
- `storage`: local cache and Google Drive backend.
- `metrics`: haversine distance, threshold accuracy, subgroup summaries.
- `reports`: run cards, Markdown reports, result index updates.
- `utils`: hashing, I/O, retry, logging, time helpers.

## Manifest Schema

A manifest row identifies one image and stores immutable evaluation metadata: `item_id`, `dataset_name`, `subset_name`, `split_name`, `image_path`, `drive_path`, `latitude`, `longitude`, optional administrative metadata, tags, checksum, and notes.

## Normalized Prediction Schema

Normalized predictions keep provider, model, prompt version, raw text, parsed location text, optional latitude/longitude, confidence, refusal flag, parse error, geocode fallback flag, raw response path, and timing/error metadata.

## Run Card Schema

Run cards record run identity, objective, paper alignment, dataset/subset, attack settings, victim settings, prompt/geocoder/storage versions, git commit, timestamps, artifact paths/IDs, and notes.

## Git vs Drive Boundary

Git stores code, docs, configs, manifests, schemas, and Markdown reports. Drive stores image artifacts, deltas, raw API outputs, normalized dumps, metrics bundles, and run bundles.

## Extension Points

Future MLLM-aware defenses should implement the attack interface, emit comparable metadata, and reuse manifests, provider normalization, metrics, and reports. New providers should subclass the base victim adapter and preserve raw responses before normalization.

## External GeoShield Overlay

The external GeoShield checkout remains ignored by git. Adaptive optimizer edits are stored as a tracked overlay under `patches/external_geoshield_adaptive/` and applied with `scripts/apply_geoshield_adaptive_overlay.py`. This preserves reproducibility without committing checkpoints, datasets, generated images, or the whole external repository.
