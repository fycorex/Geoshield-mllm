# Adaptive GeoShield Plan

This project should first reproduce a real GeoShield protected-image path, then add Attack-VLLM techniques as an adaptive stress/improvement branch.

## Baseline To Preserve

GeoShield remains the primary defense paper. The baseline must use:

- resize: `640`
- epsilon: `8/255`
- step size: `1/255`
- steps: `200`
- GNFD non-geographic descriptions
- Geo-EE geography-revealing region detection
- PSAE global and local perturbation optimization

## Attack-VLLM Ideas To Add

Use arXiv:2505.01050 as engineering input, not as the baseline paper:

- diverse surrogate ensemble: CLIP B/16, CLIP B/32, CLIP L/14-336, LAION CLIP, then DINOv2 and open VLLMs when available
- model regularization: DropPath/PatchDrop and perturbation averaging
- data robustness: Gaussian noise, random crop/pad/resize, and DiffJPEG-style compression
- loss upgrade: visual contrastive loss and relative proxy loss

## Experiment Branches

1. `geoshield_baseline`: official-style GeoShield settings, no Attack-VLLM additions.
2. `geoshield_full_surrogate`: same GeoShield loss, larger CLIP ensemble.
3. `geoshield_geoee_mllm`: strict GNFD + Geo-EE using MLLM descriptions and GroundingDINO/SAM.
4. `geoshield_attack_vllm_aug`: GeoShield plus Attack-VLLM preprocessing augmentations.
5. `geoshield_attack_vllm_loss`: add visual contrastive loss once positive/negative geo/non-geo exemplars are defined.

## Command Templates

Fast real protected-image smoke:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli run-geoshield-attack \
  --manifest manifests/im2gps3k_100_pilot.csv \
  --attack-config configs/attacks/geoshield_baseline.yaml \
  --run-id real_geoshield_smoke_1step \
  --limit 1 \
  --device cpu \
  --backbone B16 \
  --backbone B32 \
  --steps 1 \
  --resize 224
```

Paper-budget GeoShield baseline:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli run-geoshield-attack \
  --manifest manifests/im2gps3k_100_pilot.csv \
  --attack-config configs/attacks/geoshield_baseline.yaml \
  --run-id geoshield_baseline_im2gps3k_100 \
  --limit 100 \
  --device cuda:0 \
  --backbone B16 \
  --backbone B32 \
  --backbone Laion
```

Adaptive full-surrogate GeoShield branch:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli run-geoshield-attack \
  --manifest manifests/im2gps3k_100_pilot.csv \
  --attack-config configs/attacks/geoshield_attack_vllm_adaptive.yaml \
  --run-id geoshield_attackvllm_adaptive_im2gps3k_100 \
  --limit 100 \
  --device cuda:0 \
  --backbone B16 \
  --backbone B32 \
  --backbone L336 \
  --backbone Laion \
  --strict-geoee \
  --groundingdino-device cuda \
  --descriptions-provider techutopia \
  --descriptions-model gpt-4o
```

Exact GSV branch after downloading the Location-Inference benchmark:

```bash
conda run -n geoshield-mllm python -m geoshield_mllm.cli run-geoshield-attack \
  --manifest manifests/gsv_100_pilot.csv \
  --attack-config configs/attacks/geoshield_attack_vllm_adaptive.yaml \
  --run-id geoshield_attackvllm_adaptive_exactgsv_100 \
  --limit 100 \
  --device cuda:0 \
  --backbone B16 \
  --backbone B32 \
  --backbone L336 \
  --backbone Laion \
  --strict-geoee \
  --groundingdino-device cuda \
  --descriptions-provider techutopia \
  --descriptions-model gpt-4o
```

Do not run GSV experiments against the prior Hugging Face Street View proxy. Exact GSV/GSC means the 1,602-image Location-Inference Google Street View benchmark used by GeoShield.

## Current Implementation Gap

The repo can call the real external GeoShield optimizer and generate protected images. The next code work is to patch the optimizer itself so Attack-VLLM augmentations and visual contrastive loss are part of the gradient loop, not only config intent.
