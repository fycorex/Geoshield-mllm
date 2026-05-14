# Project State

Last updated: 2026-05-14

Repository status: bootstrap pushed to `fycorex/Geoshield-mllm` on `main`; current working tree has uncommitted exact-GSV dataset updates.

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
- Downloaded the official Location-Inference GSV/GSC release from the upstream-published folder after explicit user approval; extracted 1,602 images and froze `gsv_100_pilot`.
- Added paper-aligned smoke runner that records GeoShield baseline settings without claiming real attack execution.
- Drive OAuth smoke succeeded and wrote `docs/drive_smoke_latest.json`.
- Added real external GeoShield runner capable of generating protected images through the local `external/geoshield` optimizer.
- Added Attack-VLLM-informed adaptive GeoShield config and command plan.
- Patched the local external GeoShield optimizer with an adaptive overlay that adds DINOv2, open-VLLM surrogate adapters, Attack-VLLM augmentations, visual contrastive loss, relative proxy loss, and SAM-refined box preference.
- Added `scripts/apply_geoshield_adaptive_overlay.py` so the ignored external checkout can be made reproducible from tracked overlay files.
- Added `scripts/generate_sam_refined_boxes.py` for GroundingDINO-to-SAM box refinement.
- Removed the proxy `manifests/gsv_100_pilot.csv`; exact GSV/GSC must come from the Location-Inference benchmark.

Incomplete:
- The adaptive GeoShield optimizer patch is source-applied and py-compile checked, but not yet validated end-to-end with DINOv2/open-VLLM checkpoints on GPU.
- SAM refinement requires a local SAM checkpoint and `segment-anything`.
- Live provider calls require working TechUtopia/API credentials.
- `gsv_500_stratified` is not currently frozen.

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
1. Apply the tracked adaptive overlay to any fresh `external/geoshield` checkout before adaptive runs.
2. Validate a one-image GPU adaptive run with CLIP+DINOv2; then add Qwen2VL/LLaVANeXT only if memory permits.
3. Run a one-image adaptive GPU smoke with the exact GSV and IM2GPS3K manifests before launching 100+100.
4. Upload/cache pilot artifacts in Drive using the working OAuth path.
5. Run a small live TechUtopia eval once endpoint access is confirmed.
