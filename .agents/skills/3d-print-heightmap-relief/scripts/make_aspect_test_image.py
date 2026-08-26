#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import math

from PIL import Image, ImageDraw
from _relief_utils import write_json


def pair(text: str) -> tuple[float, float]:
    a, b = text.lower().replace(",", "x").split("x", 1)
    return float(a), float(b)


def main() -> int:
    p = argparse.ArgumentParser(description="Create a square-pixel physical aspect diagnostic with known-size square and circle.")
    p.add_argument("output")
    p.add_argument("--size-mm", type=pair, default=(80.0, 40.0))
    p.add_argument("--ppi", type=float, default=200.0)
    p.add_argument("--marker-mm", type=float, default=20.0)
    p.add_argument("--metadata")
    args = p.parse_args()

    w_mm, h_mm = args.size_mm
    pitch = 25.4 / args.ppi
    w_px = max(1, int(round(w_mm / pitch)))
    h_px = max(1, int(round(h_mm / pitch)))
    marker_px = max(4, int(round(args.marker_mm / pitch)))
    if marker_px * 2.4 > w_px or marker_px * 1.4 > h_px:
        raise SystemExit("marker is too large for requested canvas; increase --size-mm or reduce --marker-mm")

    im = Image.new("I;16", (w_px, h_px), 0)
    d = ImageDraw.Draw(im)
    stroke = max(2, marker_px // 50)
    margin_y = (h_px - marker_px) // 2
    gap = max(stroke * 4, int(round(5.0 / pitch)))
    total = marker_px * 2 + gap
    x0 = (w_px - total) // 2
    sq = (x0, margin_y, x0 + marker_px, margin_y + marker_px)
    cir_x = x0 + marker_px + gap
    cir = (cir_x, margin_y, cir_x + marker_px, margin_y + marker_px)
    d.rectangle(sq, fill=32768, outline=65535, width=stroke)
    d.ellipse(cir, fill=32768, outline=65535, width=stroke)
    # Crosshair and border give obvious X/Y orientation without changing known marker dimensions.
    d.line((w_px // 2, 0, w_px // 2, h_px - 1), fill=12000, width=max(1, stroke // 2))
    d.line((0, h_px // 2, w_px - 1, h_px // 2), fill=12000, width=max(1, stroke // 2))
    im.save(args.output, dpi=(args.ppi, args.ppi))

    meta = {
        "schema": "heightmap-aspect-diagnostic-v2.2",
        "physical": {"width_mm": w_mm, "height_mm": h_mm, "aspect": w_mm / h_mm},
        "authoring": {"ppi": args.ppi, "pitch_mm": pitch, "pixel_width": w_px, "pixel_height": h_px},
        "markers": {
            "square_nominal_mm": [args.marker_mm, args.marker_mm],
            "circle_nominal_diameter_mm": args.marker_mm,
        },
        "validation_instruction": (
            f"After mapping through the production pipeline, measure the square and circle on the final 3D surface. "
            f"The square must remain {args.marker_mm:g} x {args.marker_mm:g} mm and the circle must not become an ellipse."
        ),
    }
    meta_path = Path(args.metadata) if args.metadata else Path(args.output).with_suffix(Path(args.output).suffix + ".json")
    write_json(meta_path, meta)
    print(f"Wrote aspect diagnostic {args.output}: {w_mm:g}x{h_mm:g} mm, {w_px}x{h_px} px @ {args.ppi:g} PPI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
