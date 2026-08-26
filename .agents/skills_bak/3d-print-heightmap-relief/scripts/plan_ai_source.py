#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path
from _relief_utils import write_json


def pair(text: str) -> tuple[float, float]:
    a, b = text.lower().replace(",", "x").split("x", 1)
    return float(a), float(b)


def main() -> int:
    p = argparse.ArgumentParser(description="Plan an AI-generated source master at a declared physical size and square-pixel authoring PPI.")
    p.add_argument("--size-mm", required=True, type=pair)
    p.add_argument("--authoring-ppi", type=float, default=300.0)
    p.add_argument("--image-class", default="texture")
    p.add_argument("--description", required=True)
    p.add_argument("--seamless-x", action="store_true")
    p.add_argument("--seamless-y", action="store_true")
    p.add_argument("--output-json")
    p.add_argument("--output-prompt")
    args = p.parse_args()

    w_mm, h_mm = args.size_mm
    w_px = max(1, int(math.ceil(w_mm / 25.4 * args.authoring_ppi)))
    h_px = max(1, int(math.ceil(h_mm / 25.4 * args.authoring_ppi)))
    physical_aspect = w_mm / h_mm
    requested_raster_aspect = w_px / h_px
    aspect_error_pct = abs(requested_raster_aspect / physical_aspect - 1.0) * 100.0
    seamless = []
    if args.seamless_x:
        seamless.append("left and right borders")
    if args.seamless_y:
        seamless.append("top and bottom borders")
    seamless_text = "; seamless across " + " and ".join(seamless) if seamless else ""

    prompt = (
        f"Create a grayscale relief source image for 3D-print engraving/embossing: {args.description}. "
        f"The source represents exactly {w_mm:g} x {h_mm:g} mm at {args.authoring_ppi:g} PPI with square pixels. "
        f"Requested native raster: at least {w_px} x {h_px} pixels; preserve the physical aspect ratio {physical_aspect:.8f}:1{seamless_text}. "
        "Use continuous tonal gradients where appropriate. Do not threshold, posterize, dither, palette-reduce, or intentionally reduce the image to a few gray/height steps. "
        "Keep important recognizable subjects undistorted and away from crop-critical borders unless explicitly requested."
    )
    spec = {
        "schema": "heightmap-relief-source-spec-v2.2",
        "image_class": args.image_class,
        "physical": {"width_mm": w_mm, "height_mm": h_mm, "aspect": physical_aspect},
        "authoring": {"ppi": args.authoring_ppi, "square_pixels": True, "requested_width_px": w_px, "requested_height_px": h_px},
        "requested_raster_aspect": requested_raster_aspect,
        "requested_aspect_error_pct": aspect_error_pct,
        "seamless_x": args.seamless_x,
        "seamless_y": args.seamless_y,
        "description": args.description,
        "generation_prompt": prompt,
    }
    if args.output_json:
        write_json(args.output_json, spec)
    if args.output_prompt:
        Path(args.output_prompt).write_text(prompt + "\n", encoding="utf-8")
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
