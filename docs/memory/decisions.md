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
