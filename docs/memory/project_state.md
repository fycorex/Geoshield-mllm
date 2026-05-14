# Project State

Last updated: 2026-05-14

Repository status: bootstrap pushed to `fycorex/Geoshield-mllm` on `main`; current working tree has uncommitted paper-plan and smoke-runner updates.

Implemented:
- Repository structure for configs, docs, manifests, scripts, package code, and tests.
- Documentation for architecture, protocol, storage, setup, reports, and agent behavior.
- Starter configs for dataset subsets, attacks, eval queues, prompts, and Google Drive storage.
- Python package foundations for manifests, sampling, attacks, providers, geocoding, storage, metrics, reports, retry, hashing, and CLI.
- Provider config corrected so GPT-4o and GPT-5 mini are treated as TechUtopia OpenAI-compatible models at `https://copilot.techutopia.cn/v1`.
- `setup.py` compatibility shim added so editable installs work in environments whose build backend path lacks PEP 660 support.
- Dataset preparation command added for coordinate-bearing CSV/JSONL metadata and local image directories.
- TechUtopia smoke eval runner added with explicit dry-run records and live OpenAI-compatible call path.
- Google Drive smoke command added for dry-run, OAuth, and service account validation.
- Downloaded ignored local Hugging Face data under `data/raw/geoshield_pilot_100`: 100 coordinate-bearing GSV-like rows and 50 coordinate-bearing IM2GPS3K rows.
- Downloaded official IM2GPS3K images from the `lugiavn/revisiting-im2gps` MediaFire link and GPS metadata from `im2gps3k_places365.csv`; froze `im2gps3k_100_pilot`.
- Added paper-aligned smoke runner that records GeoShield baseline settings without claiming real attack execution.
- Drive OAuth smoke succeeded and wrote `docs/drive_smoke_latest.json`.

Incomplete:
- Real GeoShield attack integration is not implemented; current attack layer supports dry-run metadata.
- Live provider calls require working TechUtopia/API credentials.
- `gsv_100_pilot` is GSV-like proxy data, not verified as the GeoShield paper's 1,602-image Street View benchmark.

Current blockers:
- Expired `gh` token. Plain `git push` succeeded, but `gh` operations still require `gh auth login -h github.com`.
- Cloud API credentials are not available to this shell except where the user runs commands manually.
- `TECHUTOPIA_API_KEY` is not currently exported in this shell, so only dry-run eval can run here.
- Service-account Drive smoke returned Google Drive 403 `storageQuotaExceeded`; OAuth smoke succeeds, so service-account mode needs shared-drive/delegation if used.

Active assumptions:
- Python 3.11+ is available.
- Local validation should use the dedicated `geoshield-mllm` conda env.
- `conda` may not be on PATH; use `/home/ubuntu/miniconda3/bin/conda` or export `$HOME/miniconda3/bin` into PATH.
- Main experiments stay at or below 1000 images.
- Google Drive is the canonical large-artifact store.
- Current GPT-4o and GPT-5 mini access is through TechUtopia, not direct OpenAI.
- API adapters must preserve raw responses and normalized parse failures.

Next recommended steps:
1. Add real GeoShield attack integration.
2. Upload/cache pilot artifacts in Drive using the working OAuth path.
3. Run a small live TechUtopia eval once endpoint access is confirmed.
4. Acquire or reconstruct the GeoShield paper's Street View benchmark before making paper-aligned GSV claims.
