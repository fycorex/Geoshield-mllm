# Experiment Protocol

## Paper Identity

The primary paper is GeoShield, a geolocation privacy defense paper. The black-box VLM attack paper at arXiv:2505.01050 is related background only and must not be treated as the GeoShield paper.

## Research Questions

1. Under what settings does GeoShield-style defense underperform?
2. Which image or prompt characteristics explain underperformance?
3. Which measured failures motivate later MLLM-aware defenses?

## Dataset Policy

Use paper-aligned or similar datasets, but freeze small deterministic subsets before evaluation. Store ground-truth latitude/longitude and preserve city, region, and country fields when available. Supported tags are `iconic_landmark`, `strong_text_cue`, `street_view_like`, `natural_scene`, `indoor`, and `low_geo_signal`.

Current dataset status:
- `im2gps3k_100_pilot` uses official IM2GPS3K images and GPS metadata.
- `gsv_100_pilot` must use the exact Location-Inference Google Street View benchmark: 1,602 images from 1,563 unique cities across 88 countries.
- The previous public random Street View Hugging Face proxy is rejected and must not be reported as GSV/GSC.

## Pilot/Main Strategy

Pilot subsets contain 100 images each. Main subsets contain 500 images each. Total main evaluation size must stay at or below 1000 images.

Additional smaller subsets may be used only for plumbing validation or interim analysis. Smoke runs should prefer `im2gps3k_100_pilot` or `gsv_100_pilot` with `--limit 2` rather than maintaining separate tiny manifests.

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

The baseline GeoShield branch should keep paper-style CLIP surrogate settings. The adaptive branch may add DINOv2, Qwen2VL, and LLaVA-NeXT surrogates, plus Attack-VLLM-style augmentation and proxy losses, but reports must label those runs as adaptive GeoShield and not as official baseline GeoShield.

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
6. `adaptive_transfer_stress_test` as a later, explicitly labeled stress test using ideas from arXiv:2505.01050.

The adaptive branch is now implemented as a source overlay for the external GeoShield optimizer. Before adaptive runs, apply `patches/external_geoshield_adaptive/` to `external/geoshield`; before strict Geo-EE runs with SAM, generate a GroundingDINO JSON and refine it with `scripts/generate_sam_refined_boxes.py`.

## Negative Results

Negative or ambiguous findings are valid outputs. Reports must disclose parse failures, refusals, geocoding fallbacks, API errors, and small-sample uncertainty.

## Future Method Development

Do not introduce a claimed defense until baseline and mismatch failure modes have been measured. New defenses should reuse the same manifests and evaluation stack.
