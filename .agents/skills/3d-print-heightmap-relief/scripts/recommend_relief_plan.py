#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from _relief_utils import default_aspect_tolerance_pct, minimum_remaining_wall, recommend_pitch, recommended_depth_range


def pair(text: str) -> tuple[float, float]:
    a, b = text.lower().replace(",", "x").split("x", 1)
    return float(a), float(b)


def main() -> int:
    p = argparse.ArgumentParser(description="Recommend resolution, aspect policy, fit, and relief depth.")
    p.add_argument("--size-mm", required=True, type=pair)
    p.add_argument("--process", default="fdm")
    p.add_argument("--nozzle-mm", type=float, default=0.4)
    p.add_argument("--layer-height-mm", type=float, default=0.2)
    p.add_argument("--resin-xy-mm", type=float, default=0.05)
    p.add_argument("--axis-mode", default="xy-z")
    p.add_argument("--surface-type", default="plane")
    p.add_argument("--image-class", default="subject")
    p.add_argument("--mode", default="engrave", choices=["engrave", "emboss"])
    p.add_argument("--repeating", action="store_true")
    p.add_argument("--wall-thickness-mm", type=float, default=2.0)
    args = p.parse_args()

    w, h = args.size_mm
    rec = recommend_pitch(w, h, args.process, args.nozzle_mm, args.layer_height_mm, args.resin_xy_mm, args.axis_mode)
    d, dnote = recommended_depth_range(args.image_class, args.mode)
    reserve = minimum_remaining_wall(args.nozzle_mm)
    safe = max(0.0, args.wall_thickness_mm - reserve)
    texture = args.image_class.lower() in {"texture", "pattern", "wood", "carbon", "fabric", "stone"}
    fit = "repeat" if args.repeating or texture else "contain"
    notes = [
        "Preserve PHYSICAL aspect ratio in millimetres through every stage.",
        "Raw processed raster aspect may differ from physical aspect when pitch_x_mm != pitch_y_mm.",
        "Use the square-pixel preview for human inspection; never feed that preview back into geometry.",
    ]
    if args.surface_type.lower() in {"cylinder", "cylinder_side"}:
        notes.append("Cylinder horizontal placement distance must be arc length R*theta, not degrees or raw UV width.")
    if args.surface_type.lower() in {"sphere", "ball", "ellipsoid", "sphere_patch", "ellipsoid_patch"} and not texture:
        notes.append("Use a bounded metric-aware patch for recognizable subjects; avoid poles and high-stretch UV regions.")
    result = {
        "size_mm": [w, h],
        "resolution": rec.to_dict(),
        "aspect": {
            "policy": "preserve",
            "tolerance_pct": default_aspect_tolerance_pct(args.image_class),
            "allow_aspect_distortion": False,
        },
        "recommended_fit": fit,
        "master_bit_depth": 16,
        "depth_range_mm": {"min": d[0], "max": d[1], "note": dnote},
        "wall": {"wall_thickness_mm": args.wall_thickness_mm, "minimum_remaining_wall_mm": reserve, "max_safe_engrave_depth_mm": safe},
        "notes": notes,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
