#!/usr/bin/env python
"""Download the exact Location-Inference Google Street View benchmark.

The GeoShield paper's Google Street View benchmark matches the dataset from
Jay et al., "Evaluating Precise Geolocation Inference Capabilities of Vision
Language Models": 1,602 images from 1,563 cities across 88 countries.

This script downloads into root /data/, which is git-ignored.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


FOLDER_ID = "1FodVI-dir7zIpGRVpjnRBgvyTILAOFCX"
DEFAULT_OUTPUT = Path("data/raw/location_inference_gsv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder-id", default=FOLDER_ID)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gdown", default="gdown")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        args.gdown,
        "--folder",
        args.folder_id,
        "--output",
        str(args.output_dir),
    ]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Downloaded exact GSV benchmark candidate to {args.output_dir}")


if __name__ == "__main__":
    main()
