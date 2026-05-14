# Decisions

## 2026-05-13: Use Package-First Scaffold

Decision: Put implementation under `src/geoshield_mllm/` with thin scripts in `scripts/`.

Why: This keeps tests importable, encourages reusable modules, and avoids notebook-only logic.

Alternatives considered: script-only repository. Rejected because provider, storage, metrics, and report code need stable interfaces.

Impact: CLI and scripts call the package API.

## 2026-05-13: Treat Google Drive as Artifact Backend, Not Git Remote

Decision: Store large/generated artifacts in Drive through a backend interface and keep git lightweight.

Why: Images, deltas, raw API dumps, and metrics bundles are too large and mutable for git.

Alternatives considered: Git LFS. Deferred because the requested design names Google Drive as the main artifact store.

Impact: `.gitignore` excludes artifact classes and storage docs define Drive hierarchy.

## 2026-05-13: Dry-Run First External Integrations

Decision: Provider, attack, and storage layers expose interfaces and dry-run behavior before credentials are available.

Why: The repository must be testable without secrets and must not fabricate successful API calls or attacks.

Alternatives considered: stub outputs that look like real results. Rejected because it risks contaminating reports.

Impact: Tests focus on schema, metrics, path resolution, retry, and normalization.

## 2026-05-13: Route GPT-4o and GPT-5 Mini Through TechUtopia

Decision: Treat `gpt-4o` and `gpt-5-mini` as TechUtopia OpenAI-compatible models using `https://copilot.techutopia.cn/v1`.

Why: The user clarified that available access for those models is through `copilot.techutopia.cn`.

Alternatives considered: keeping them under the first-party OpenAI provider. Rejected because it would mismatch the available API surface and credentials.

Impact: Eval configs use `techutopia` for pilot and main runs; first-party OpenAI remains a separate optional provider.

## 2026-05-13: Use Existing Conda Env for Local Validation

Decision: Use `/home/ubuntu/miniconda3/envs/geoshield` for local validation in this workspace.

Why: The system `python` command is unavailable, system Python lacks pytest, and network package installation is restricted.

Alternatives considered: installing pytest into user Python or the conda env. Deferred because network install attempts failed or were interrupted.

Impact: Tests are written to run under `unittest` with `PYTHONPATH=src`, while dev requirements still include pytest for normal development.

## 2026-05-13: Add setup.py Editable Install Compatibility

Decision: Add a minimal `setup.py` shim alongside `pyproject.toml`.

Why: The user encountered an editable install failure where the build backend did not expose `build_editable`, and pip noted there was no `setup.py` or `setup.cfg` fallback.

Alternatives considered: requiring a newer pip/setuptools only. Rejected because the repo should be easy to bootstrap in mixed server environments.

Impact: `pip install -e .` has a legacy-compatible path while project metadata remains in `pyproject.toml`.

## 2026-05-13: Refuse to Freeze Manifests Without Coordinates

Decision: `prepare-dataset` requires coordinate-bearing rows and will not write undersized pilot manifests when latitude/longitude are missing.

Why: The project goal requires geolocation metrics, and fabricating or silently omitting ground truth would make later evaluation invalid.

Alternatives considered: creating image-only manifests from the local 30-image GeoShield repro output. Rejected because they would violate the manifest schema and experiment protocol.

Impact: A dataset availability report is generated when local sources are insufficient; real manifests can be frozen once coordinate-bearing metadata is supplied.

## 2026-05-13: Anchor Dataset Artifact Ignore Rules

Decision: Change `.gitignore` large-artifact patterns from broad `datasets/` style entries to root-anchored `/datasets/`, `/data/`, and `/runs/`.

Why: Broad directory ignore rules accidentally hide source and config paths such as `src/geoshield_mllm/datasets/` and `configs/datasets/`.

Alternatives considered: force-adding ignored files. Rejected because future dataset source/config work should not require special git flags.

Impact: Root-level artifact directories remain ignored, while code and config dataset directories are tracked normally.

## 2026-05-13: Add IM2GPS3K 15-Image Smoke Subset

Decision: Freeze `im2gps3k_15_smoke` from the coordinate-bearing rows already available in `/home/ubuntu/Geoshield/outputs/geoshield_repro30_paper_e8_s200_640`.

Why: The requested 100-image pilots remain blocked, but a small real-coordinate subset is enough to validate manifest, provider, metrics, and reporting plumbing.

Alternatives considered: waiting for the full pilot metadata before any eval plumbing. Rejected because it would stall useful integration work.

Impact: Smoke results must be labeled as plumbing validation only and not treated as paper-scale evidence.

## 2026-05-13: Make Dry-Run Eval Records Explicit Non-Results

Decision: Dry-run eval writes raw and normalized records with `dry_run=true` and `parse_error=dry_run_no_api_call`.

Why: This validates file layout and parsing/report plumbing without creating outputs that could be mistaken for model predictions.

Alternatives considered: emitting plausible JSON predictions. Rejected because it could contaminate later reports.

Impact: Any metric summary can filter or flag dry-run records unambiguously.

## 2026-05-13: Do Not Browser-Impersonate TechUtopia

Decision: Add legitimate configurable request metadata for TechUtopia (`User-Agent`, optional provider-approved extra headers, and image-mode diagnostics), but do not imitate a browser to bypass blocked requests.

Why: `PermissionDeniedError: Your request was blocked` may reflect invalid credentials, endpoint policy, unsupported image payloads, or provider-side access controls. Bypassing those controls would make runs non-reproducible and operationally fragile.

Alternatives considered: hard-coding browser-like headers. Rejected because it is an evasion tactic rather than a documented API integration.

Impact: Live failures are preserved as artifacts, and users can configure documented headers or run a text-only diagnostic probe.

## 2026-05-13: Validate Drive With a Tiny Artifact Smoke

Decision: Add `drive-smoke-test` to validate Drive auth and backend behavior before any dataset or run bundle upload.

Why: Drive ownership, quota, and folder permissions can fail late if not tested independently with a tiny artifact.

Alternatives considered: waiting until first real run upload. Rejected because it would mix storage failures with model/dataset failures.

Impact: Drive setup can now be validated without committing artifacts or running an experiment.

## 2026-05-13: Use Official IM2GPS3K, Not the Privacy-Benchmark Mirror

Decision: Use the official IM2GPS3K image ZIP linked by `lugiavn/revisiting-im2gps` and `im2gps3k_places365.csv` GPS metadata for `im2gps3k_100_pilot`.

Why: IM2GPS3K is a roughly 3000-image benchmark with ground-truth GPS. A VLM-GeoPrivacyBench image mirror only yielded 50 IM2GPS3K-labelled rows and is not a substitute.

Alternatives considered: freezing a 50-row mirror subset. Rejected because it would confuse official IM2GPS3K with a related privacy benchmark mirror.

Impact: `im2gps3k_100_pilot` now uses official-source images/metadata; the rejected mirror attempt remains documented only as an acquisition mistake.

## 2026-05-13: Service Account Drive Quota Requires Shared Drive or Delegation

Decision: Treat service-account 403 `storageQuotaExceeded` as a Drive configuration blocker, not a code failure.

Why: Google Drive reports that service accounts do not have storage quota for normal My Drive uploads. The storage target must be a shared drive or use OAuth/delegation with a quota-owning user.

Alternatives considered: retrying uploads. Rejected because repeated retries will not fix quota ownership.

Impact: Use OAuth desktop auth first, or configure a shared drive/service-account access path before large artifact uploads.

## 2026-05-14: Reject Proxy GSV and Require Exact Location-Inference GSV

Decision: Delete the tracked proxy `gsv_100_pilot` manifest and require the exact Location-Inference Google Street View benchmark for GSV/GSC experiments.

Why: The GeoShield paper notes a Google Street View benchmark with 1,602 images from 1,563 cities across 88 countries. The matching Location-Inference repo publishes a Google Drive folder id for that dataset. The prior local 100-image GSV subset was only Street View-like and must not be used.

Alternatives considered: keeping the proxy with warnings. Rejected because the user requires exact GSV/GSC and proxy data could leak into reports.

Impact: `manifests/gsv_100_pilot.csv` is absent until exact data is downloaded and frozen. GSV/GSC runs are blocked until then.

## 2026-05-14: Add Paper-Aligned Smoke Before Real Attack Integration

Decision: Add `paper-aligned-smoke` to validate manifests, configs, attack metadata, eval artifacts, and run cards using GeoShield baseline settings.

Why: The real GeoShield fork integration is still incomplete, but the pipeline should already prove that paper-aligned settings are recorded and reproducible.

Alternatives considered: waiting for full attack integration before any smoke. Rejected because config/reporting mistakes should be caught earlier.

Impact: Smoke success is explicitly non-result dry-run evidence; it does not claim protected-image generation or model performance.

## 2026-05-14: Add Attack-VLLM-Informed Adaptive GeoShield Branch

Decision: Keep `geoshield_baseline` as the clean GeoShield reproduction branch and add `geoshield_attack_vllm_adaptive` as a separate adaptive branch.

Why: The user wants GeoShield optimized with Attack-VLLM ideas such as more surrogates, preprocessing robustness, and contrastive losses. Keeping this separate avoids confusing official GeoShield baseline claims with new adaptive modifications.

Alternatives considered: silently changing the baseline config. Rejected because it would make paper-aligned comparisons invalid.

Impact: Commands and configs now distinguish baseline GeoShield from the adaptive Attack-VLLM-enhanced branch.

## 2026-05-14: Persist External GeoShield Changes As a Tracked Overlay

Decision: Keep `external/geoshield` ignored, but track a source overlay under `patches/external_geoshield_adaptive/` plus an apply script.

Why: The external GeoShield checkout is a separate source tree and should not be committed wholesale. The adaptive optimization loop changes must still be reproducible from this repository.

Alternatives considered: committing the whole external checkout, or leaving only local untracked edits. Committing the full checkout would blur ownership and add unrelated files. Leaving local edits untracked would make the adaptive branch non-reproducible.

Impact: A fresh clone can apply the adaptive optimizer changes with `scripts/apply_geoshield_adaptive_overlay.py`, while the baseline GeoShield branch remains separable.
