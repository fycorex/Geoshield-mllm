# Experiment Protocol

## Paper Identity

The primary paper is GeoShield, a geolocation privacy defense paper. The black-box VLM attack paper at arXiv:2505.01050 is related background only and must not be treated as the GeoShield paper.

## Research Questions

1. Under what settings does GeoShield-style defense underperform?
2. Which image or prompt characteristics explain underperformance?
3. Which measured failures motivate later MLLM-aware defenses?

## Dataset Policy

Use paper-aligned or similar datasets, but freeze small deterministic subsets before evaluation. Store ground-truth latitude/longitude and preserve city, region, and country fields when available. Supported tags are `iconic_landmark`, `strong_text_cue`, `street_view_like`, `natural_scene`, `indoor`, and `low_geo_signal`.

## Pilot/Main Strategy

Pilot subsets contain 100 images each. Main subsets contain 500 images each. Total main evaluation size must stay at or below 1000 images.

Additional smaller subsets may be used only for plumbing validation or interim analysis. `im2gps3k_15_smoke` validates the stack quickly. It is not a replacement for the official IM2GPS3K pilot.

## Baseline-Aligned Settings

- resize: `640`
- epsilon: `8/255`
- step size: `1/255`
- steps: `200`

Exploratory sweeps use epsilon `{2/255, 4/255, 8/255}` and steps `{50, 100, 200}`.

## Victim Model Policy

Supported provider families are TechUtopia OpenAI-compatible endpoints, first-party OpenAI, Gemini, Anthropic, and Qwen/DashScope. In this project, current GPT-4o and GPT-5 mini access is expected through TechUtopia at `https://copilot.techutopia.cn/v1`, not through a first-party OpenAI key. Provider support must keep raw responses and normalized outputs.

## Auxiliary vs Victim Mismatch

Auxiliary/surrogate model choices and victim model choices are separate run-card fields. Mismatch experiments should change one axis at a time where budget allows.

## Prompt Policy

Prompts are versioned under `configs/prompts/`. Geolocation prompts require strict JSON output. Non-geographic description prompts must avoid asking for location.

## Metrics

Report haversine distance, threshold accuracy at 1 km, 25 km, 200 km, 750 km, and 2500 km, parse success rate, refusal rate, geocode fallback rate, per-tag breakdowns, per-dataset breakdowns, and clean-vs-adv comparisons.

## Run Naming

Use `<date>_<datasetbundle>_<attack>_<victimgroup>_<shorttag>`, for example `2026-05-13_pilot200_geoshieldbase_techutopia_baseline`.

## Queue

1. `pilot_baseline_techutopia`
2. `pilot_cross_provider`
3. `main_budget_sweep`
4. `main_failure_tags`
5. `aux_victim_mismatch`

## Negative Results

Negative or ambiguous findings are valid outputs. Reports must disclose parse failures, refusals, geocoding fallbacks, API errors, and small-sample uncertainty.

## Future Method Development

Do not introduce a claimed defense until baseline and mismatch failure modes have been measured. New defenses should reuse the same manifests and evaluation stack.
