# Project State

Last updated: 2026-05-13

Repository status: initial bootstrap pushed to `fycorex/Geoshield-mllm` on `main`.

Implemented:
- Repository structure for configs, docs, manifests, scripts, package code, and tests.
- Documentation for architecture, protocol, storage, setup, reports, and agent behavior.
- Starter configs for dataset subsets, attacks, eval queues, prompts, and Google Drive storage.
- Python package foundations for manifests, sampling, attacks, providers, geocoding, storage, metrics, reports, retry, hashing, and CLI.
- Provider config corrected so GPT-4o and GPT-5 mini are treated as TechUtopia OpenAI-compatible models at `https://copilot.techutopia.cn/v1`.
- `setup.py` compatibility shim added so editable installs work in environments whose build backend path lacks PEP 660 support.
- Dataset preparation command added for coordinate-bearing CSV/JSONL metadata and local image directories.
- `im2gps3k_15_smoke` frozen from locally available coordinate-bearing GeoShield repro metadata.
- TechUtopia smoke eval runner added with explicit dry-run records and live OpenAI-compatible call path.
- Google Drive smoke command added for dry-run, OAuth, and service account validation.
- Downloaded ignored local Hugging Face data under `data/raw/geoshield_pilot_100`: 100 coordinate-bearing GSV-like rows and 50 coordinate-bearing IM2GPS3K rows.
- Downloaded official IM2GPS3K images from the `lugiavn/revisiting-im2gps` MediaFire link and GPS metadata from `im2gps3k_places365.csv`; froze `im2gps3k_100_pilot`.

Incomplete:
- Real GeoShield attack integration is not implemented; current attack layer supports dry-run metadata.
- Live provider calls and Drive uploads require credentials.
- GitHub push is blocked until `gh` is reauthenticated.

Current blockers:
- Expired `gh` token. Plain `git push` succeeded, but `gh` operations still require `gh auth login -h github.com`.
- Cloud API credentials are not available to this shell except where the user runs commands manually.
- Need to upload/local-cache large dataset artifacts through Drive once Drive auth is settled.
- `TECHUTOPIA_API_KEY` is not currently exported in this shell, so only dry-run eval can run here.
- Drive dry-run smoke passed. A later service-account smoke attempt returned Google Drive 403 `storageQuotaExceeded`: service accounts do not have storage quota unless using shared drives or domain-wide delegation/OAuth delegation.

Active assumptions:
- Python 3.11+ is available.
- Local validation should use the dedicated `geoshield-mllm` conda env.
- `conda` may not be on PATH; use `/home/ubuntu/miniconda3/bin/conda` or export `$HOME/miniconda3/bin` into PATH.
- Main experiments stay at or below 1000 images.
- Google Drive is the canonical large-artifact store.
- Current GPT-4o and GPT-5 mini access is through TechUtopia, not direct OpenAI.
- API adapters must preserve raw responses and normalized parse failures.

Next recommended steps:
1. Reauthenticate `gh`.
2. Configure Drive OAuth or shared-drive service-account storage and rerun live Drive smoke.
3. Run a small live TechUtopia eval once endpoint access is confirmed.
4. Add real GeoShield attack integration.
