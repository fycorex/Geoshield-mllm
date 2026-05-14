# Research Notes: GeoShield and Related VLLM Attack Paper

## 1. GeoShield (AAAI 2026, arXiv:2508.03209)

Role in this repository: primary defense paper.

Core methodology: geoprivacy protection via adversarial perturbations. GeoShield aims to reduce VLM geolocation accuracy while preserving non-geographic semantics and visual quality.

- **GNFD:** Separates geographical and non-geographical features.
- **Geo-EE:** Uses an auxiliary MLLM, GroundingDINO, and SAM to find geographical exposure elements.
- **PSAE:** Multi-scale optimization over global crops and local patches to improve robustness against resizing.
- **Parameters:** `epsilon=8/255`, `steps=200`, `step_size=1/255`, `resize=640`.
- **Datasets:** Google Street View and Im2GPS3k with GPS coordinates. The GeoShield markdown states that the Street View benchmark has 1,602 images from 1,563 unique cities across 88 countries and that Im2GPS3k has approximately 3,000 Flickr-sourced geotagged images.

## 2. Transferable Adversarial Attacks on Black-Box Vision-Language Models (arXiv:2505.01050)

Role in this repository: related attack reference only. It should inform future adaptive stress tests after the GeoShield-style baseline is reproduced and measured. It is not the GeoShield paper and should not define baseline defense claims.

Core methodology: transferable targeted attacks against black-box VLLMs.

- **Surrogates:** CLIP-family models, open-source VLLMs, DINOv2-style visual models, and adversarially trained models.
- **Loss:** Visual Contrastive Loss using positive and negative visual examples to represent target semantics.
- **Augmentations:** Random Gaussian noise, crop/pad/resize, DropPath/PatchDrop, perturbation averaging, and DiffJPEG-style compression.

## 3. Repository Implications

- The immediate plan remains failure-mode probing of GeoShield-style protection, not claiming a merged or improved defense.
- Attack-VLLM techniques belong in later adaptive evaluation phases once baseline GeoShield integration and clean/adv evaluation are stable.
- Any future improved defense must be motivated by measured failures, not assumed from combining paper ideas.
- Current `gsv_100_pilot` is a GSV-like public Street View proxy, not a verified match to the GeoShield 1,602-image Street View benchmark.
