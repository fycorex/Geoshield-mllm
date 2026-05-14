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
- `im2gps3k_100_pilot` from official IM2GPS3K images and GPS metadata
- `gsv_100_pilot` from the exact Location-Inference Google Street View benchmark; do not use GSV-like proxy data
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
export PATH="$HOME/miniconda3/bin:$PATH"
conda create -n geoshield-mllm python=3.11
conda run -n geoshield-mllm python -m pip install -U pip setuptools wheel
conda run -n geoshield-mllm python -m pip install -e ".[dev,providers]"
conda run -n geoshield-mllm python -m pytest
```

Fallback command if a minimal environment lacks pytest:

```bash
PYTHONPATH=src /home/ubuntu/miniconda3/envs/geoshield-mllm/bin/python -m unittest discover -s tests
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
6. `adaptive_transfer_stress_test` as a later explicitly labeled stress test

The Attack-VLLM-informed GeoShield branch is documented in `docs/adaptive_geoshield_plan.md` and configured by `configs/attacks/geoshield_attack_vllm_adaptive.yaml`. GSV/GSC experiments require the exact Location-Inference benchmark, not proxy Street View data.

## Smoke Eval

Paper-aligned dry-run smoke with GeoShield baseline settings:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli paper-aligned-smoke \
  --manifest manifests/im2gps3k_100_pilot.csv \
  --attack-config configs/attacks/geoshield_baseline.yaml \
  --eval-config configs/evals/pilot_openai.yaml \
  --run-id smoke_paper_aligned_im2gps3k \
  --limit 2
```

Dry-run TechUtopia smoke eval:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli eval-techutopia-smoke \
  --manifest manifests/im2gps3k_100_pilot.csv \
  --run-id smoke_techutopia_dryrun \
  --limit 2
```

Live smoke eval after setting `TECHUTOPIA_API_KEY`:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli eval-techutopia-smoke \
  --manifest manifests/im2gps3k_100_pilot.csv \
  --run-id smoke_techutopia_live_v1 \
  --limit 2 \
  --no-dry-run
```

If the endpoint returns `PermissionDeniedError: Your request was blocked`, first verify the key is real and not a placeholder. The adapter sends an explicit research-client `User-Agent`; if TechUtopia documents required headers, set them as JSON:

```bash
export TECHUTOPIA_EXTRA_HEADERS_JSON='{"X-Example-Header":"value"}'
```

To diagnose whether the endpoint blocks base64 image payloads specifically, run a text-only request:

```bash
export TECHUTOPIA_IMAGE_MODE=none
conda run -n geoshield-mllm python -m geoshield_mllm.cli eval-techutopia-smoke \
  --manifest manifests/im2gps3k_100_pilot.csv \
  --run-id smoke_techutopia_textonly_probe \
  --limit 1 \
  --no-dry-run
```

## Reporting Expectations

Every run should produce `run_card.json`, `run_card.md`, `summary.json`, and a Markdown result page under `docs/results/<run_id>/`. Reports must include exact configs, dataset summary, model summary, parse/refusal/geocode fallback rates, subgroup metrics, failure cases, Drive paths, and interpretation notes.
