#!/usr/bin/env python3
"""Convert calibrated overhead-photo points into palette dimensions."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def distance(a: list[float], b: list[float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def capture_dimensions(data: dict, maximum_skew_percent: float = 3.0) -> dict:
    reference = data["reference"]
    palette = data["palette"]
    reference_pixels = distance(reference["edge_a_px"], reference["edge_b_px"])
    if reference_pixels <= 0 or reference["length_mm"] <= 0:
        raise ValueError("reference edge and physical length must be positive")
    corners = palette["corners_px"]
    if len(corners) != 4:
        raise ValueError("palette.corners_px must contain TL, TR, BR, BL")
    top = distance(corners[0], corners[1])
    right = distance(corners[1], corners[2])
    bottom = distance(corners[3], corners[2])
    left = distance(corners[0], corners[3])
    if min(top, right, bottom, left) <= 0:
        raise ValueError("palette edges must be positive")
    scale = reference["length_mm"] / reference_pixels
    width_pixels = (top + bottom) / 2.0
    height_pixels = (left + right) / 2.0
    width_skew = abs(top - bottom) / width_pixels * 100.0
    height_skew = abs(left - right) / height_pixels * 100.0
    skew = max(width_skew, height_skew)
    thickness = float(palette["closed_thickness_mm"])
    if thickness <= 0:
        raise ValueError("closed_thickness_mm must be a positive caliper measurement")
    passed = skew <= maximum_skew_percent
    result = {
        "schema_version": "1.0",
        "status": "PASS" if passed else "FAIL",
        "method": "overhead_photo_with_in_plane_reference_plus_caliper_thickness",
        "scale_mm_per_px": round(scale, 8),
        "closed_face_width_mm": round(width_pixels * scale, 2),
        "closed_face_height_mm": round(height_pixels * scale, 2),
        "closed_thickness_mm": round(thickness, 2),
        "perspective_skew_percent": round(skew, 3),
        "maximum_perspective_skew_percent": maximum_skew_percent,
        "recommended_minimum_compartment_clear_mm": round(thickness + 1.0, 2),
        "limitations": [
            "A single overhead photo measures only the closed face plane.",
            "Thickness must be measured with calipers; hinge protrusions require the maximum closed thickness.",
            "FAIL means the camera was not square enough for the declared tolerance.",
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--maximum-skew-percent", type=float, default=3.0)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    result = capture_dimensions(data, args.maximum_skew_percent)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
