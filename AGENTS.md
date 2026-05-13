# Repository Instructions

Project: Geoshield-mllm.

This repository builds a reproducible probing stack for GeoShield-style geolocation privacy defense under cloud multimodal model evaluation. The immediate goal is failure-mode analysis on small, frozen subsets, not a claim of a new defense.

Core references:
- GeoShield defense paper, AAAI 2026 PDF: https://ojs.aaai.org/index.php/AAAI/article/download/40877/44838
- GeoShield arXiv: https://arxiv.org/abs/2508.03209
- Official GeoShield repo: https://github.com/thinwayliu/Geoshield
- Working GeoShield fork: https://github.com/fycorex/geoshield
- Related attack paper only, arXiv: https://arxiv.org/abs/2505.01050
- Related attack repo: https://github.com/fycorex/attack-vllm

Do not confuse the GeoShield defense paper with the black-box VLM attack reference. They are different papers with different goals.

Hard constraints:
- Pilot first, then main.
- Main runs must stay at or below 1000 images.
- Code, configs, manifests, schemas, reports, and lightweight metadata belong in git.
- Image artifacts, perturbations, raw API dumps, normalized prediction bundles, metrics bundles, and run bundles belong in Google Drive or local ignored artifact directories.
- Do not fabricate experiment results, credentials, Drive IDs, API success, or push success.

Git rules:
- Canonical repository: https://github.com/fycorex/Geoshield-mllm
- Git identity: `fycorex <zfysjtu24@sjtu.edu.cn>`.
- Prefer `gh` for GitHub operations when possible.
- Branch naming: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`, `exp/<topic>`.
- Commit style: `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, `test: ...`, `chore: ...`.
- Never commit secrets, image batches, raw API dumps, or large generated artifacts.
- Do not rewrite history or force push unless explicitly requested.

Coding standards:
- Python 3.11+.
- Package-first code under `src/geoshield_mllm/`.
- Use `pathlib`, typed data models, explicit config, and structured JSON/Markdown outputs.
- Keep provider adapters behind common interfaces with dry-run behavior where credentials are absent.
- Treat current GPT-4o and GPT-5 mini access as TechUtopia OpenAI-compatible access at `https://copilot.techutopia.cn/v1`; first-party OpenAI is optional and separate.
- Prefer the existing conda environment at `/home/ubuntu/miniconda3/envs/geoshield` for local validation in this workspace.
- Use web search when current API/package behavior is uncertain.

Experiment record requirements:
- Every run records run id, goal, paper alignment, dataset/subset, image count, seed, resize, epsilon, step size, steps, attack, auxiliary model, victim provider/model, prompt version, geocoder backend, git commit, timestamps, Drive paths/IDs, and notes.
- Negative results are first-class results and must be reported without burying parse/refusal/error rates.

Storage rules:
- Google Drive root: `GeoShield-MLLM-Probe/`.
- Use sidecar JSON metadata for uploaded artifacts.
- Cache and reuse folder IDs.
- Validate local cache entries with SHA-256.
- Keep Drive and git roles separate.

Source-of-truth docs:
- `docs/memory/project_state.md`
- `docs/memory/decisions.md`
- `docs/memory/progress_log.md`
- `TODO.md`
- `docs/architecture.md`
- `docs/experiment_protocol.md`
- `docs/storage.md`

Project memory rules:
- After each major change, update project state, progress log, and TODO.
- Record architecture decisions chronologically in `docs/memory/decisions.md`.
- If architecture, storage, or experiment protocol changes, update the matching docs in the same commit.
