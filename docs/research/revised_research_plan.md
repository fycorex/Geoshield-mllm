# Revised Research Plan: GeoShield Failure-Mode Probing

## 1. Context and Objective

The core objective of `Geoshield-mllm` is to evaluate failure modes of GeoShield-style geolocation privacy protection against multimodal large language models under controlled, reproducible settings.

The primary paper is GeoShield (AAAI 2026, arXiv:2508.03209). The transferable black-box VLLM attack paper (arXiv:2505.01050) is a related stress-test reference only. The two papers must remain separated in code, reports, and claims.

## 2. Updated Research Questions

1. **Baseline Vulnerability:** Under which image types, prompts, model families, and preprocessing settings does GeoShield-style protection underperform?
2. **Reason for Failure:** Are failures driven by landmarks, text cues, scene priors, indoor/outdoor ambiguity, model refusals, geocoder fallbacks, or attack/victim mismatch?
3. **Component Sensitivity:** Which GeoShield components and paper-aligned settings matter most once the real fork integration is wired?
4. **Adaptive Robustness:** After baseline measurement, do transfer-attack ideas such as Visual Contrastive Loss, diverse surrogates, and DiffJPEG-style augmentation expose additional weaknesses?

## 3. Revised Experiment Queue

1. `paper_aligned_smoke`: Prove config, manifest, attack metadata, eval artifact, and report wiring with resize 640, epsilon 8/255, step size 1/255, and 200 steps. This is a dry-run/code-path check unless live credentials and real GeoShield integration are enabled.
2. `pilot_baseline_techutopia`: Establish clean and protected baseline behavior on `im2gps3k_100_pilot` and `gsv_100_pilot` with TechUtopia GPT-4o/GPT-5 mini access.
3. `pilot_cross_provider`: Compare configured providers after TechUtopia succeeds.
4. `main_budget_sweep`: Vary `epsilon in {2/255, 4/255, 8/255}` and `steps in {50, 100, 200}`. Keep 16/255 out of the main GeoShield-aligned sweep unless explicitly labeled as an adaptive stress test because GeoShield emphasizes lower perturbation budgets.
5. `main_failure_tags`: Analyze per-tag behavior for `iconic_landmark`, `strong_text_cue`, `street_view_like`, `natural_scene`, `indoor`, and `low_geo_signal`.
6. `aux_victim_mismatch`: Measure transfer gaps between auxiliary/surrogate models and victim APIs.
7. `adaptive_transfer_stress_test`: Later phase only. Use arXiv:2505.01050 ideas to stress GeoShield-protected images after baseline claims are established.

## 4. Dataset Status

- `im2gps3k_100_pilot` uses official IM2GPS3K images and GPS metadata, so it is appropriate for pilot experiments.
- `gsv_100_pilot` must use the exact 1,602-image Location-Inference Google Street View benchmark referenced by GeoShield. The prior Hugging Face Street View proxy is rejected and must not be used.
- Reports must not include GSV/GSC results until `manifests/gsv_100_pilot.csv` is regenerated from the exact benchmark source.

## 5. Future Method Development

Do not claim a new defense during the probing phase. A future MLLM-aware defense can be proposed only after measured failures identify a concrete gap. Attack-VLLM techniques may then become design inputs, but they are not part of the initial GeoShield baseline claim.

## 6. Next Immediate Steps

1. Run `paper_aligned_smoke` on `im2gps3k_100_pilot` and `gsv_100_pilot` in dry-run mode.
2. Configure Drive OAuth or shared-drive service-account storage and rerun live Drive smoke.
3. Resolve TechUtopia live endpoint blocking with valid provider-supported access.
4. Add real GeoShield fork integration into `src/geoshield_mllm/attacks/`.
5. Download the exact Location-Inference GSV benchmark and regenerate `manifests/gsv_100_pilot.csv`.
