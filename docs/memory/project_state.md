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

Incomplete:
- Real dataset manifests are not frozen yet.
- Requested 100-image pilot manifests are not frozen yet.
- Current local GeoShield repro data has 15 coordinate-bearing IM2GPS3K rows and no coordinate-bearing GSV rows, so it is not sufficient to freeze the requested 100-image pilot manifests.
- Real GeoShield attack integration is not implemented; current attack layer supports dry-run metadata.
- Live provider calls and Drive uploads require credentials.
- GitHub push is blocked until `gh` is reauthenticated.

Current blockers:
- Expired `gh` token. Plain `git push` succeeded, but `gh` operations still require `gh auth login -h github.com`.
- No dataset source paths or cloud API credentials in the workspace.
- Need more coordinate-bearing GSV/IM2GPS3K metadata before freezing `gsv_100_pilot.csv` or `im2gps3k_100_pilot.csv`.
- `TECHUTOPIA_API_KEY` is not currently exported in this shell, so only dry-run eval can run here.
- No Drive OAuth/service account credentials in the workspace.
- `pytest` is not installed in the current conda env, and network package installation is restricted; unit tests are runnable with `unittest`.

Active assumptions:
- Python 3.11+ is available.
- Local validation should use `/home/ubuntu/miniconda3/envs/geoshield` unless a newer dedicated conda env is created.
- `conda` may not be on PATH; use `/home/ubuntu/miniconda3/bin/conda` or export `$HOME/miniconda3/bin` into PATH.
- Main experiments stay at or below 1000 images.
- Google Drive is the canonical large-artifact store.
- Current GPT-4o and GPT-5 mini access is through TechUtopia, not direct OpenAI.
- API adapters must preserve raw responses and normalized parse failures.

Next recommended steps:
1. Reauthenticate `gh`.
2. Install dev dependencies in a conda env with network access using `conda run -n <env> python -m pip ...`, then run `python -m pytest`.
3. Add dataset source roots and generate pilot manifests.
4. Configure Drive credentials and run a small storage smoke test.
