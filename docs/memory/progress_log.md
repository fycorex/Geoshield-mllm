# Progress Log

## 2026-05-13T00:00:00Z

Summary: Began repository bootstrap for Geoshield-mllm. Confirmed local repo has no commits and `origin` points to `https://github.com/fycorex/Geoshield-mllm`. `gh` authentication is present but invalid.

Files changed: initial docs, configs, package scaffold, tests, and repo metadata.

Tests run: pending during bootstrap.

## 2026-05-13T00:20:00Z

Summary: Switched local validation guidance to the existing conda environment at `/home/ubuntu/miniconda3/envs/geoshield`. Network package installation is restricted, so tests were made runnable with standard `unittest` while remaining pytest-compatible.

Files changed: `docs/setup.md`, `README.md`, tests, memory docs.

Tests run: `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests.

## 2026-05-13T00:30:00Z

Summary: Created and pushed the initial bootstrap commit to `origin/main`. `gh auth status` remains invalid, but plain git push to `https://github.com/fycorex/Geoshield-mllm` succeeded.

Files changed: repository scaffold committed as `95ae9ec feat: bootstrap geoshield mllm scaffold`.

Tests run: `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests before commit.

## 2026-05-13T00:40:00Z

Summary: Fixed environment setup guidance after user reported `conda` was not on PATH and editable install failed due to missing PEP 660 backend support. Added `setup.py` shim and updated docs to use absolute conda path/PATH export plus `conda run`.

Files changed: `setup.py`, `README.md`, `docs/setup.md`, memory docs.

Tests run: pending for this follow-up patch.

## 2026-05-13T00:45:00Z

Summary: Fixed pytest compatibility for `tests/test_manifest.py` after the Python 3.11 conda env exposed a missing `path` assignment in the pytest-style manifest roundtrip test.

Files changed: `tests/test_manifest.py`, `docs/memory/progress_log.md`.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 24 tests; `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests.

## 2026-05-13T00:55:00Z

Summary: Implemented dataset preparation from coordinate-bearing CSV/JSONL metadata and local image directories. Inspected available local GeoShield repro data and found only 30 source images with no lat/lon, so pilot manifests were not frozen from that source. Anchored large-artifact ignore rules so `configs/datasets/` and package dataset modules are tracked.

Files changed: dataset preparation module, CLI, dataset configs, manifests docs, memory docs, dataset availability report, tests.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 26 tests; `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests.

## 2026-05-13T01:05:00Z

Summary: Found coordinate-bearing IM2GPS3K rows in the non-strict GeoShield repro output and added `im2gps3k_15_smoke` as a local plumbing-validation subset.

Files changed: smoke dataset config, frozen smoke manifest, README, experiment protocol, TODO, memory docs.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 27 tests; `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests.

## 2026-05-13T01:15:00Z

Summary: Added TechUtopia smoke eval runner with dry-run output and live OpenAI-compatible chat-completions image request support. The current shell has no `TECHUTOPIA_API_KEY`, so live eval was not run.

Files changed: TechUtopia provider, eval runner, CLI, tests, README, memory docs.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 27 tests; `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests. Dry-run smoke eval wrote 4 explicit non-result records under ignored `runs/smoke_techutopia_dryrun/`.

## 2026-05-13T01:25:00Z

Summary: User ran live TechUtopia smoke eval and the endpoint returned `PermissionDeniedError: Your request was blocked.` Updated eval runner to preserve provider errors as raw artifacts and normalized records instead of crashing the whole run.

Files changed: eval runner, eval tests, memory docs.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 28 tests; `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests.

## 2026-05-13T01:35:00Z

Summary: Declined browser impersonation as a way to bypass TechUtopia blocking. Added legitimate configurable request metadata instead: research-client `User-Agent`, `TECHUTOPIA_EXTRA_HEADERS_JSON`, and `TECHUTOPIA_IMAGE_MODE=none` for text-only diagnostics.

Files changed: TechUtopia provider, `.env.example`, README, setup docs, memory docs.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 31 tests; `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests.

## 2026-05-13T00:05:00Z

Summary: Corrected provider assumptions after user clarification. GPT-4o and GPT-5 mini are now configured under TechUtopia OpenAI-compatible access at `https://copilot.techutopia.cn/v1`; first-party OpenAI remains optional.

Files changed: `.env.example`, eval configs, README, experiment protocol, TODO, memory docs.

Tests run: pending during bootstrap.
