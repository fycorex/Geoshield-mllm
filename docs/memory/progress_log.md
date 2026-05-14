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

## 2026-05-13T01:45:00Z

Summary: Added Google Drive smoke test command with dry-run, OAuth, and service-account modes. The smoke writes a tiny file, uploads/downloads it through the backend, validates SHA-256, and writes `docs/drive_smoke_latest.json`.

Files changed: Drive smoke module, CLI, tests, storage/setup docs, memory docs.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 32 tests; `PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests` passed 12 tests. `drive-smoke-test --auth-mode dry-run` passed and wrote `docs/drive_smoke_latest.json`; no OAuth or service-account credentials were present for live Drive smoke.

## 2026-05-13T02:00:00Z

Summary: Downloaded coordinate-bearing Hugging Face data into ignored local storage. The first 100+100 attempt used a VLM-GeoPrivacyBench image mirror and failed for IM2GPS3K because that mirror is not the official IM2GPS3K dataset and yielded only 50 IM2GPS3K-labelled rows. This was kept out of git and not used as `im2gps3k_100_pilot`.

Files changed: dataset configs, frozen manifests, dataset availability docs, memory docs; ignored image data downloaded under `data/raw/`.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 32 tests.

## 2026-05-13T02:05:00Z

Summary: Froze `manifests/gsv_100_pilot.csv` with 100 coordinate-bearing GSV-like rows. Observed user-side/service-account Drive smoke report with Google Drive 403 `storageQuotaExceeded`, which means the service account needs a shared drive, OAuth/delegation, or other quota-owning target.

Files changed: frozen GSV manifest, configs, dataset availability docs, Drive smoke report, memory docs.

Tests run: `conda run -n geoshield-mllm python -m pytest` passed 32 tests.

## 2026-05-13T02:15:00Z

Summary: Corrected IM2GPS3K acquisition after user pointed out that official IM2GPS3K contains about 3000 images with ground-truth GPS. Downloaded official image ZIP from the `lugiavn/revisiting-im2gps` MediaFire link, extracted 3000 images, downloaded `im2gps3k_places365.csv` GPS metadata, and froze `manifests/im2gps3k_100_pilot.csv`.

Files changed: IM2GPS3K config, frozen IM2GPS3K pilot manifest, dataset availability docs, memory docs.

Tests run: `conda run -n geoshield-mllm python -m geoshield_mllm.cli validate-manifest manifests/gsv_100_pilot.csv` passed; `conda run -n geoshield-mllm python -m geoshield_mllm.cli validate-manifest manifests/im2gps3k_100_pilot.csv` passed; `conda run -n geoshield-mllm python -m pytest` passed 33 tests.

## 2026-05-14T02:20:00Z

Summary: Re-read the current Markdown notes for GeoShield and the transferable black-box VLLM attack paper. Revised the plan to keep GeoShield as the primary defense paper, treat arXiv:2505.01050 as later stress-test context only, and label the current GSV pilot as GSV-like proxy data rather than a verified paper benchmark.

Files changed: research notes, revised research plan, experiment protocol, dataset availability docs, README, TODO, memory docs.

Tests run: pending.

## 2026-05-14T02:25:00Z

Summary: Added a config-driven `paper-aligned-smoke` command. Ran it on `im2gps3k_100_pilot` and `gsv_100_pilot` with GeoShield baseline settings: resize 640, epsilon 8/255, step size 1/255, and 200 steps. Both smoke runs wrote ignored artifacts under `runs/`; they are dry-run/non-result checks because real GeoShield attack integration is not wired yet.

Files changed: CLI, smoke runner, smoke-runner test, README, memory docs.

Tests run: GSV manifest integrity check found 100 rows, 0 missing images, 0 SHA-256 mismatches, latitude range `[-45.5513762, 65.9787027]`, and longitude range `[-123.0291068, 175.9786412]`; `conda run -n geoshield-mllm python -m geoshield_mllm.cli paper-aligned-smoke --manifest manifests/im2gps3k_100_pilot.csv --attack-config configs/attacks/geoshield_baseline.yaml --eval-config configs/evals/pilot_openai.yaml --run-id smoke_paper_aligned_im2gps3k --limit 2` passed; `conda run -n geoshield-mllm python -m geoshield_mllm.cli paper-aligned-smoke --manifest manifests/gsv_100_pilot.csv --attack-config configs/attacks/geoshield_baseline.yaml --eval-config configs/evals/pilot_openai.yaml --run-id smoke_paper_aligned_gsvproxy --limit 2` passed; `conda run -n geoshield-mllm python -m pytest` passed 34 tests.

## 2026-05-14T02:40:00Z

Summary: Added a real external GeoShield runner path and an Attack-VLLM-informed adaptive GeoShield config/plan. The intended adaptive branch keeps GNFD/Geo-EE/PSAE, expands the surrogate ensemble, and adds Attack-VLLM-style augmentation/loss work as the next optimizer patch.

Files changed: adaptive config, adaptive plan docs, README, TODO, memory docs, external GeoShield runner, CLI.

Tests run: A one-image, one-step real GeoShield smoke generated a protected image under ignored `runs/real_geoshield_smoke_1step/`. Full test suite not rerun in this change because the user asked for commands rather than more local execution.

## 2026-05-14T02:55:00Z

Summary: Corrected GSV/GSC policy after user clarified exact data is required. Removed the tracked proxy `gsv_100_pilot.csv`, pointed `gsv_100_pilot.yaml` at the exact Location-Inference GSV benchmark, and added a download helper for the published Google Drive folder id.

Files changed: GSV dataset config, dataset availability docs, setup docs, adaptive plan, README, TODO, memory docs, requirements, exact-GSV download script.

Tests run: not run; documentation/config correction only.

## 2026-05-14T03:20:00Z

Summary: Patched the external GeoShield optimizer for the adaptive Attack-VLLM branch. The loop now supports DINOv2 and open-VLLM surrogate adapters, Gaussian noise, crop-pad-resize, DiffJPEG-like compression, PatchDrop, perturbation averaging, visual contrastive loss, relative proxy loss, and SAM-refined bounding boxes. Because `external/geoshield` is ignored, the modified source is preserved as a tracked overlay with an apply script.

Files changed: adaptive attack config, attack config dataclass, external runner overrides, SAM refinement script, adaptive overlay files, overlay apply script, adaptive plan, TODO, memory docs.

Tests run: `conda run -n geoshield-mllm python -m py_compile` passed for the overlay and helper scripts. `conda run -n geoshield-mllm python -m pytest` passed 36 tests.

## 2026-05-14T03:35:00Z

Summary: Re-checked the exact Location-Inference GSV/GSC source after the user clarified that Google Drive should be used for output/result artifacts, not dataset download. The upstream `njspyx/location-inference` README lists only a `gdown` Google Drive folder release for the dataset. The GitHub repo contains notebooks, Inspect code, and model-result CSVs, but no image files or alternate non-Drive release.

Files changed: dataset availability docs, setup docs, memory docs.

Tests run: not run; source verification and documentation update only.

## 2026-05-14T03:50:00Z

Summary: Downloaded the official Location-Inference GSV/GSC release after the user explicitly permitted Google Drive for the correct dataset source. Updated the downloader for current `gdown` CLI syntax, extracted `imgs_final.zip`, verified `1602` images, and froze `manifests/gsv_100_pilot.csv` with 100 deterministic rows.

Files changed: GSV dataset config, GSV manifest, downloader script, dataset preparation mapper, dataset availability docs, setup docs, memory docs.

Tests run: `conda run -n geoshield-mllm python -m geoshield_mllm.cli validate-manifest manifests/gsv_100_pilot.csv` passed. Manual manifest check found 100 rows, 0 missing images, 100 unique cities, and 35 countries. `conda run -n geoshield-mllm python -m pytest` passed 36 tests.

## 2026-05-13T00:05:00Z

Summary: Corrected provider assumptions after user clarification. GPT-4o and GPT-5 mini are now configured under TechUtopia OpenAI-compatible access at `https://copilot.techutopia.cn/v1`; first-party OpenAI remains optional.

Files changed: `.env.example`, eval configs, README, experiment protocol, TODO, memory docs.

Tests run: pending during bootstrap.
