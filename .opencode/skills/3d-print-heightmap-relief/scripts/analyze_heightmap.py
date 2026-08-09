#!/usr/bin/env python3
"""Analyze a height map against physical size, printer limits, and mesh cost."""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

import numpy as np
from scipy import ndimage

from heightmap_common import image_stats, load_image_float, seam_metrics, write_json


def memory_estimate(width_mm: float, height_mm: float, pitch_mm: float) -> dict:
    nu = max(2, int(math.ceil(width_mm / pitch_mm)) + 1)
    nv = max(2, int(math.ceil(height_mm / pitch_mm)) + 1)
    vertices = 2 * nu * nv
    faces = 4 * (nu - 1) * (nv - 1) + 4 * ((nu - 1) + (nv - 1))
    raw = vertices * 3 * 8 + faces * 3 * 8 + nu * nv * 4
    return {
        "grid_u": nu,
        "grid_v": nv,
        "closed_patch_vertices": vertices,
        "closed_patch_triangles": faces,
        "raw_array_bytes": raw,
        "raw_array_mib": raw / 2**20,
        "practical_working_set_mib_low": raw * 3 / 2**20,
        "practical_working_set_mib_high": raw * 10 / 2**20,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("--physical-width-mm", type=float, required=True)
    p.add_argument("--physical-height-mm", type=float, required=True)
    p.add_argument("--mesh-pitch-mm", type=float)
    p.add_argument("--nozzle-mm", type=float, default=0.4)
    p.add_argument("--line-width-mm", type=float)
    p.add_argument("--layer-height-mm", type=float, default=0.2)
    p.add_argument("--relief-depth-mm", type=float, default=0.6)
    p.add_argument("--repeat-x", action="store_true")
    p.add_argument("--repeat-y", action="store_true")
    p.add_argument("--report", type=Path)
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.physical_width_mm <= 0 or args.physical_height_mm <= 0:
        raise ValueError("Physical dimensions must be positive")
    if args.nozzle_mm <= 0 or args.layer_height_mm <= 0 or args.relief_depth_mm <= 0:
        raise ValueError("Printer and relief dimensions must be positive")

    values, source = load_image_float(args.image)
    h, w = values.shape
    px_x = args.physical_width_mm / w
    px_y = args.physical_height_mm / h
    line_width = args.line_width_mm or args.nozzle_mm * 1.10
    # Conservative planning values. These are not hard physical limits.
    recommended_xy = max(line_width * 0.50, args.nozzle_mm * 0.45)
    reliable_feature = max(line_width, args.nozzle_mm)
    useful_z_steps = args.relief_depth_mm / args.layer_height_mm

    pitch = args.mesh_pitch_mm or min(px_x, px_y)
    estimate = memory_estimate(args.physical_width_mm, args.physical_height_mm, pitch)
    seams = seam_metrics(values)

    gx = np.gradient(values, axis=1) / max(px_x, 1e-12)
    gy = np.gradient(values, axis=0) / max(px_y, 1e-12)
    slope = args.relief_depth_mm * np.sqrt(gx * gx + gy * gy)
    threshold = max(0.03, float(values.std()) * 0.20)
    mask = values > threshold
    components, count = ndimage.label(mask)
    sizes = np.bincount(components.ravel())[1:] if count else np.array([], dtype=int)
    physical_component_areas = sizes * px_x * px_y
    small_area_limit = reliable_feature**2
    small_components = int(np.sum(physical_component_areas < small_area_limit))

    warnings: list[str] = []
    recommendations: list[str] = []

    if px_x > reliable_feature or px_y > reliable_feature:
        warnings.append(
            "The source raster is coarser than one nominal extrusion width at final size; "
            "the image may look blocky before printer limits are reached."
        )
    if px_x < recommended_xy / 4 or px_y < recommended_xy / 4:
        recommendations.append(
            "The image is strongly oversampled for a typical FDM surface. Keep the source, "
            "but generate the mesh at a coarser pitch to avoid unnecessary memory use."
        )
    if useful_z_steps < 2:
        warnings.append("Relief depth is below two layer heights; tonal separation will be weak.")
    elif useful_z_steps < 4:
        recommendations.append("Use at least four Z steps for smoother tonal relief where geometry permits.")
    if estimate["practical_working_set_mib_high"] > 4096:
        warnings.append("The pessimistic mesh working-set estimate exceeds 4 GiB.")
    elif estimate["practical_working_set_mib_high"] > 1024:
        recommendations.append("Boolean operations may need over 1 GiB; generate or process relief in patches.")

    def seam_bad(axis: str) -> bool:
        if axis == "x":
            return (
                seams["left_right_rms"] > 0.03
                and (
                    seams["left_right_to_adjacent_ratio"] > 2.0
                    or seams["left_right_excess_rms"] > 0.03
                )
            )
        return (
            seams["top_bottom_rms"] > 0.03
            and (
                seams["top_bottom_to_adjacent_ratio"] > 2.0
                or seams["top_bottom_excess_rms"] > 0.03
            )
        )

    if args.repeat_x and seam_bad("x"):
        warnings.append("Left/right seam is unusually stronger than ordinary neighboring-pixel variation.")
    if args.repeat_y and seam_bad("y"):
        warnings.append("Top/bottom seam is unusually stronger than ordinary neighboring-pixel variation.")
    if count and small_components / count > 0.25:
        recommendations.append(
            "More than one quarter of thresholded islands are smaller than roughly one extrusion-width square; "
            "blur, simplify, enlarge, or remove them."
        )
    if float(np.percentile(slope, 99)) > 1.5:
        recommendations.append(
            "The 99th-percentile local relief slope is steep (>1.5 mm/mm); preview in the slicer "
            "and consider blur, lower depth, or a larger physical image."
        )

    report = {
        "image": source,
        "image_stats": image_stats(values),
        "seams": seams,
        "physical_mapping": {
            "width_mm": args.physical_width_mm,
            "height_mm": args.physical_height_mm,
            "pixels": [w, h],
            "source_pitch_x_mm_per_px": px_x,
            "source_pitch_y_mm_per_px": px_y,
        },
        "printer_assumptions": {
            "nozzle_mm": args.nozzle_mm,
            "line_width_mm": line_width,
            "layer_height_mm": args.layer_height_mm,
            "relief_depth_mm": args.relief_depth_mm,
            "relief_depth_in_layers": useful_z_steps,
            "planning_xy_sample_pitch_mm": recommended_xy,
            "planning_reliable_feature_mm": reliable_feature,
            "note": (
                "Source-image resolution, mesh sampling resolution, and printable XY/Z resolution are separate. "
                "These planning values are conservative heuristics, not printer guarantees."
            ),
        },
        "mesh_estimate": estimate,
        "feature_diagnostics": {
            "threshold": threshold,
            "connected_components": int(count),
            "components_below_nominal_feature_area": small_components,
            "slope_mm_per_mm_p50": float(np.percentile(slope, 50)),
            "slope_mm_per_mm_p95": float(np.percentile(slope, 95)),
            "slope_mm_per_mm_p99": float(np.percentile(slope, 99)),
            "slope_mm_per_mm_max": float(np.max(slope)),
        },
        "warnings": warnings,
        "recommendations": recommendations,
    }

    if args.report:
        write_json(report, args.report)
    else:
        import json
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
