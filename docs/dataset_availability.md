# Dataset Availability

## GSV 100 Pilot

- dataset: `gsv`
- source root: `/home/ubuntu/Geoshield-mllm/data/raw/location_inference_gsv/images`
- metadata: `/home/ubuntu/Geoshield-mllm/data/raw/location_inference_gsv/metadata.csv`
- output manifest: `manifests/gsv_100_pilot.csv`
- requested sample size: `100`
- discovered rows: `pending`
- rows with coordinates: `pending`
- written rows: `0`
- exact source: `https://github.com/njspyx/location-inference`
- source paper: `https://arxiv.org/abs/2502.14412`
- upstream release method: the official `njspyx/location-inference` README lists `gdown --id '1FodVI-dir7zIpGRVpjnRBgvyTILAOFCX' --folder`; user explicitly permitted this official Drive-hosted dataset source on 2026-05-14.
- expected full benchmark: `1602` Google Street View images from `1563` unique cities across `88` countries.
- status: downloaded to ignored local storage and frozen as `manifests/gsv_100_pilot.csv`.
- full release files: `full_benchmark.csv`, `img_coordinates_final_v1_with_country.csv`, `imgs_final.zip`, extracted `imgs_final_v1/` with `1602` images.
- frozen pilot: `100` rows, `0` missing images, `100` unique cities, `35` countries.

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
- exact GSV download target: `data/raw/location_inference_gsv/`
- rejected GSV-like proxy download: `data/raw/geoshield_pilot_100/`
- git policy: all raw images, ZIPs, and downloaded metadata under root `/data/` are ignored.

## Rejected Mirror Attempt

A VLM-GeoPrivacyBench image-mirror scan yielded only 50 usable IM2GPS3K-labelled rows. That mirror is not treated as official IM2GPS3K and is not used for `im2gps3k_100_pilot`.

## Rejected GSV Proxy

The previous `gsv_100_pilot.csv` was generated from `stochastic/random_streetview_images_pano_v0.0.2`. That source is not the exact GeoShield/Location-Inference GSV benchmark and must not be used for GSV/GSC experiments.

# Dataset Availability: gsv_100_pilot

- dataset: `gsv`
- source root: `/home/ubuntu/Geoshield-mllm/data/raw/location_inference_gsv`
- output manifest: `manifests/gsv_100_pilot.csv`
- requested sample size: `100`
- discovered rows: `1602`
- rows with coordinates: `1602`
- written rows: `100`

# Dataset Availability: gsv_100_pilot

- dataset: `gsv`
- source root: `/home/ubuntu/Geoshield-mllm/data/raw/location_inference_gsv`
- output manifest: `manifests/gsv_100_pilot.csv`
- requested sample size: `100`
- discovered rows: `1602`
- rows with coordinates: `1602`
- written rows: `100`
