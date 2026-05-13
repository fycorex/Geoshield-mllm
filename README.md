# Geoshield-mllm

Geoshield-mllm is a config-driven research scaffold for probing failure modes of GeoShield-style geolocation privacy defense on small image subsets with cloud multimodal APIs. It is designed for reproducibility, traceability, and conservative claims.

The immediate objective is to answer where and why GeoShield-style defense underperforms under controlled settings. The project does not claim a new defense until failure modes are measured and understood.

## Core References

- GeoShield defense paper, AAAI 2026 PDF: https://ojs.aaai.org/index.php/AAAI/article/download/40877/44838
- GeoShield arXiv: https://arxiv.org/abs/2508.03209
- Official GeoShield repo: https://github.com/thinwayliu/Geoshield
- Working fork: https://github.com/fycorex/geoshield
- Related attack reference only: https://arxiv.org/abs/2505.01050
- Related attack repo: https://github.com/fycorex/attack-vllm

## Scope

This repository stores code, configs, schemas, manifests, Markdown reports, and lightweight metadata. Large artifacts stay out of git and are stored through the Google Drive backend.

Current GPT-4o and GPT-5 mini access is configured through the TechUtopia OpenAI-compatible endpoint at `https://copilot.techutopia.cn/v1`. First-party OpenAI support remains scaffolded as a separate optional provider.

Dataset plan:
- `gsv_100_pilot`
- `im2gps3k_100_pilot`
- `gsv_500_stratified`
- `im2gps3k_500_stratified`

Baseline alignment:
- resize: `640`
- epsilon: `8/255`
- step size: `1/255`
- steps: `200`

Exploratory sweeps vary epsilon in `{2/255, 4/255, 8/255}` and steps in `{50, 100, 200}`.

## Storage Policy

GitHub stores source, configs, frozen manifests, schemas, and reports. Google Drive stores clean/protected images, deltas, raw API responses, normalized predictions, metrics bundles, and run bundles under `GeoShield-MLLM-Probe/`.

## Layout

- `configs/`: datasets, attacks, evals, prompts, and storage config.
- `manifests/`: frozen manifest docs and schemas.
- `src/geoshield_mllm/`: package code.
- `scripts/`: command wrappers.
- `docs/`: architecture, protocol, storage, setup, reports, memory, and results.
- `tests/`: dry-run and pure-unit tests.

## Quickstart

```bash
gh auth login
git config user.name "fycorex"
git config user.email "zfysjtu24@sjtu.edu.cn"
conda activate geoshield
pip install -e ".[dev,providers]"
pytest
```

In the current workspace, where pytest is not installed and network package installation is restricted, use:

```bash
PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield/bin/python -m unittest discover -s tests
```

If this repo is not yet on GitHub:

```bash
gh repo create fycorex/Geoshield-mllm --public --source=. --remote=origin --push
```

If the remote already exists:

```bash
git remote add origin https://github.com/fycorex/Geoshield-mllm
git push -u origin main
```

## Initial Experiment Queue

1. `pilot_baseline_techutopia`
2. `pilot_cross_provider`
3. `main_budget_sweep`
4. `main_failure_tags`
5. `aux_victim_mismatch`

## Reporting Expectations

Every run should produce `run_card.json`, `run_card.md`, `summary.json`, and a Markdown result page under `docs/results/<run_id>/`. Reports must include exact configs, dataset summary, model summary, parse/refusal/geocode fallback rates, subgroup metrics, failure cases, Drive paths, and interpretation notes.
