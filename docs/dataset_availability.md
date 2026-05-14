# Dataset Availability

## GSV 100 Pilot

- dataset: `gsv`
- source root: `/home/ubuntu/Geoshield-mllm/data/raw/geoshield_pilot_100/source_images/gsv`
- metadata: `/home/ubuntu/Geoshield-mllm/data/raw/geoshield_pilot_100/metadata/source_manifest.csv`
- output manifest: `manifests/gsv_100_pilot.csv`
- requested sample size: `100`
- discovered rows: `100`
- rows with coordinates: `100`
- written rows: `100`
- source: `https://huggingface.co/datasets/stochastic/random_streetview_images_pano_v0.0.2`
- source note: public Street View-like Hugging Face source `stochastic/random_streetview_images_pano_v0.0.2`.
- paper-alignment note: GeoShield reports a Google Street View benchmark with 1,602 images from 1,563 cities across 88 countries. This pilot is usable as GSV-like proxy data, but it is not verified as that benchmark.

## IM2GPS3K 100 Pilot

- dataset: `im2gps3k`
- source root: `/home/ubuntu/Geoshield-mllm/data/raw/im2gps3k_official/images/im2gps3ktest`
- metadata: `/home/ubuntu/Geoshield-mllm/data/external/im2gps3k_official/im2gps3k_places365.csv`
- output manifest: `manifests/im2gps3k_100_pilot.csv`
- requested sample size: `100`
- metadata rows: `2997`
- extracted image files: `3000`
- rows with coordinates: `2997`
- written rows: `100`
- image source: `https://github.com/lugiavn/revisiting-im2gps`, which links `http://www.mediafire.com/file/7ht7sn78q27o9we/im2gps3ktest.zip`
- metadata source: `https://huggingface.co/datasets/Wendy-Fly/AAAI-2026/blob/main/im2gps3k_places365.csv`
- source note: official IM2GPS3K image ZIP linked from `lugiavn/revisiting-im2gps`; GPS metadata from `im2gps3k_places365.csv` mirror.

## Ignored Local Data

- official IM2GPS3K ZIP: `data/raw/im2gps3k_official/im2gps3ktest.zip`
- official IM2GPS3K extracted images: `data/raw/im2gps3k_official/images/im2gps3ktest/`
- official IM2GPS3K metadata mirror: `data/external/im2gps3k_official/im2gps3k_places365.csv`
- GSV-like pilot download: `data/raw/geoshield_pilot_100/`
- git policy: all raw images, ZIPs, and downloaded metadata under root `/data/` are ignored.

## Rejected Mirror Attempt

A VLM-GeoPrivacyBench image-mirror scan yielded only 50 usable IM2GPS3K-labelled rows. That mirror is not treated as official IM2GPS3K and is not used for `im2gps3k_100_pilot`.
