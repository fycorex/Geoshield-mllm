# External GeoShield Adaptive Overlay

This directory contains a tracked overlay for `external/geoshield`. The external
GeoShield checkout is intentionally ignored by the parent repository, so these
files preserve the adaptive optimizer changes needed for reproducible runs.

Apply the overlay after cloning or updating the external checkout:

```bash
conda run -n geoshield-mllm python scripts/apply_geoshield_adaptive_overlay.py \
  --external-root external/geoshield
```

The overlay adds:

- DINOv2 surrogate support.
- Open VLLM surrogate adapters for Qwen2-VL and LLaVA-NeXT-style models.
- Gaussian noise, crop-pad-resize, DiffJPEG-like tensor compression, PatchDrop,
  and perturbation averaging inside the optimization loop.
- Visual contrastive and relative proxy objectives.
- SAM-refined bounding box preference through `sam_box` or `refined_box` fields
  in the GroundingDINO JSON.

Keep this overlay small and source-only. Do not place checkpoints, datasets, run
outputs, raw API responses, or generated image artifacts here.
