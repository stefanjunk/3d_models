#!/usr/bin/env python3
"""Prepare a periodic uint16 sample tile from the approved 16-bit height map."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "model_parameters.json"
META = ROOT / "assets" / "carbon_twill_height_samples.json"
RAW = ROOT / "assets" / "carbon_twill_height_samples_u16.raw"


def main() -> None:
    params = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    relief = params["carbon_relief"]
    source = ROOT / relief["source"]
    tile_w, tile_h = map(float, relief["tile_size"])
    pitch = float(relief["geometry_sample_pitch"])
    width = max(2, round(tile_w / pitch))
    height = max(2, round(tile_h / pitch))

    with Image.open(source) as image:
        if image.mode not in {"I;16", "I;16L", "I;16B", "I"}:
            raise ValueError(f"Expected a 16-bit grayscale height map, got {image.mode}")
        source_array = np.asarray(image, dtype=np.float32)

    source_min = float(source_array.min())
    source_max = float(source_array.max())
    if not source_max > source_min:
        raise ValueError("Height map has no usable dynamic range")

    # BOX resampling removes sub-printer noise.  The tile is periodic, so no
    # duplicate endpoint is stored; the CAD sampler wraps bilinearly.
    prepared_image = Image.fromarray(source_array.astype(np.uint16)).resize(
        (width, height), Image.Resampling.BOX
    )
    prepared = np.asarray(prepared_image, dtype=np.float32)
    prepared = np.clip((prepared - source_min) / (source_max - source_min), 0.0, 1.0)
    samples = np.rint(prepared * 65535.0).astype("<u2")

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_bytes(samples.tobytes(order="C"))
    report = {
        "source": str(source.relative_to(ROOT)),
        "source_bit_depth": 16,
        "source_pixels": [int(source_array.shape[1]), int(source_array.shape[0])],
        "source_range_u16": [source_min, source_max],
        "prepared_file": str(RAW.relative_to(ROOT)),
        "prepared_pixels": [width, height],
        "prepared_bit_depth": 16,
        "tile_size_mm": [tile_w, tile_h],
        "sample_pitch_mm": [tile_w / width, tile_h / height],
        "periodic_u": True,
        "periodic_v": True,
        "normalization": "source minimum to 0; source maximum to 65535",
    }
    META.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
