#!/usr/bin/env python
"""Refine GroundingDINO boxes with SAM and write `sam_box` fields.

Input is the GeoShield GroundingDINO JSON format. Output keeps every detection
and adds a tighter `sam_box` inferred from the SAM mask bounding rectangle.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", type=Path, required=True)
    parser.add_argument("--groundingdino-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--sam-checkpoint", type=Path, required=True)
    parser.add_argument("--sam-model-type", default="vit_h")
    parser.add_argument("--device", default="cuda")
    return parser.parse_args()


def mask_box(mask: np.ndarray) -> list[int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def main() -> None:
    args = parse_args()
    try:
        from segment_anything import SamPredictor, sam_model_registry
    except ImportError as exc:
        raise SystemExit("Install segment-anything to run SAM refinement.") from exc

    model = sam_model_registry[args.sam_model_type](checkpoint=str(args.sam_checkpoint))
    model.to(args.device)
    predictor = SamPredictor(model)

    data = json.loads(args.groundingdino_json.read_text(encoding="utf-8"))
    for image_name, item in data.items():
        image_path = args.images_dir / image_name
        image = np.array(Image.open(image_path).convert("RGB"))
        predictor.set_image(image)
        for detection in item.get("detections", []):
            box = np.array(detection["box"], dtype=np.float32)
            masks, scores, _ = predictor.predict(box=box, multimask_output=True)
            best = int(np.argmax(scores))
            refined = mask_box(masks[best])
            if refined is not None:
                detection["sam_box"] = refined
                detection["sam_score"] = float(scores[best])
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote SAM-refined boxes to {args.output_json}")


if __name__ == "__main__":
    main()
