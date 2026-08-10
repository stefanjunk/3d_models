#!/usr/bin/env python3
"""Plan printer-aware image/height-map sampling and mesh memory.

The output is an estimate. It deliberately separates a measured effective
feature size from printer marketing resolution and labels fallback values as
planning placeholders.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def positive(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate geometry-map resolution, triangle count, and memory."
    )
    parser.add_argument("--width-mm", type=positive, required=True)
    parser.add_argument("--height-mm", type=positive, required=True)
    parser.add_argument(
        "--process", choices=("fdm", "resin", "custom"), default="custom"
    )
    parser.add_argument("--nozzle-mm", type=positive, default=0.4)
    parser.add_argument("--xy-pixel-mm", type=positive)
    parser.add_argument("--effective-feature-mm", type=positive)
    parser.add_argument("--samples-per-feature", type=positive, default=3.0)
    parser.add_argument("--memory-gb", type=positive, default=8.0)
    parser.add_argument(
        "--memory-fraction",
        type=positive,
        default=0.5,
        help="Fraction of RAM allowed for the simple mesh estimate (default: 0.5).",
    )
    parser.add_argument("--max-triangles", type=int)
    parser.add_argument("--source-width-px", type=int)
    parser.add_argument("--source-height-px", type=int)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def derive_feature(args: argparse.Namespace) -> tuple[float, str, list[str]]:
    warnings: list[str] = []
    if args.effective_feature_mm:
        return (
            args.effective_feature_mm,
            "user-supplied measured/project effective feature",
            warnings,
        )

    if args.process == "fdm":
        feature = max(1.5 * args.nozzle_mm, 0.5)
        warnings.append(
            "No measured effective feature was supplied. The FDM value is a "
            "conservative planning placeholder derived from nozzle diameter; "
            "replace it with a coupon measurement."
        )
        return feature, "FDM planning placeholder", warnings

    if args.process == "resin":
        if args.xy_pixel_mm:
            feature = max(3.0 * args.xy_pixel_mm, 0.1)
            source = "resin planning placeholder derived from XY pixel pitch"
        else:
            feature = 0.15
            source = "generic resin planning placeholder"
        warnings.append(
            "No measured effective feature was supplied. Optical pixel pitch and "
            "layer height do not fully determine printable feature size; replace "
            "this placeholder with printer/material/orientation test data."
        )
        return feature, source, warnings

    raise SystemExit(
        "--effective-feature-mm is required for --process custom. "
        "Use a measured printer/material/orientation value."
    )


def grid_for_pitch(width_mm: float, height_mm: float, pitch_mm: float) -> dict[str, Any]:
    # Subtract a tiny relative epsilon so exact decimal ratios such as 80/0.2
    # do not gain a cell from binary floating-point noise.
    width_cells = math.ceil(width_mm / pitch_mm - 1e-12)
    height_cells = math.ceil(height_mm / pitch_mm - 1e-12)
    width_px = width_cells + 1
    height_px = height_cells + 1
    triangles = 2 * (width_px - 1) * (height_px - 1)
    return {
        "width_px": width_px,
        "height_px": height_px,
        "triangles": triangles,
        "actual_pitch_x_mm": width_mm / max(width_px - 1, 1),
        "actual_pitch_y_mm": height_mm / max(height_px - 1, 1),
    }


def byte_summary(triangles: int) -> dict[str, Any]:
    binary_stl = 84 + 50 * triangles
    return {
        "binary_stl_bytes": binary_stl,
        "binary_stl_mib": binary_stl / (1024**2),
        "working_mesh_estimate_mib": {
            "low_80_bytes_per_triangle": triangles * 80 / (1024**2),
            "typical_160_bytes_per_triangle": triangles * 160 / (1024**2),
            "high_240_bytes_per_triangle": triangles * 240 / (1024**2),
        },
    }


def pitch_for_triangle_cap(
    width_mm: float,
    height_mm: float,
    nominal_pitch_mm: float,
    triangle_cap: int,
) -> tuple[float, dict[str, Any]]:
    """Find the finest uniform pitch whose ceil-rounded grid stays under cap."""
    low = nominal_pitch_mm
    high = nominal_pitch_mm
    while grid_for_pitch(width_mm, height_mm, high)["triangles"] > triangle_cap:
        high *= 2.0
    for _ in range(80):
        midpoint = (low + high) / 2.0
        if grid_for_pitch(width_mm, height_mm, midpoint)["triangles"] > triangle_cap:
            low = midpoint
        else:
            high = midpoint
    return high, grid_for_pitch(width_mm, height_mm, high)


def main() -> int:
    args = parse_args()
    if args.memory_fraction > 1:
        raise SystemExit("--memory-fraction must be no greater than 1")
    if args.max_triangles is not None and args.max_triangles <= 0:
        raise SystemExit("--max-triangles must be greater than zero")
    for name in ("source_width_px", "source_height_px"):
        value = getattr(args, name)
        if value is not None and value <= 0:
            raise SystemExit(f"--{name.replace('_', '-')} must be greater than zero")

    feature_mm, feature_source, warnings = derive_feature(args)
    pitch_mm = feature_mm / args.samples_per_feature
    nominal = grid_for_pitch(args.width_mm, args.height_mm, pitch_mm)

    memory_bytes = args.memory_gb * (1024**3) * args.memory_fraction
    memory_cap_triangles = max(1, math.floor(memory_bytes / 160.0))
    cap_triangles = memory_cap_triangles
    cap_sources = ["typical 160 bytes/triangle working estimate"]
    if args.max_triangles is not None:
        cap_triangles = min(cap_triangles, args.max_triangles)
        cap_sources.append("explicit --max-triangles")
    if cap_triangles < 2:
        raise SystemExit("The selected memory/triangle cap cannot hold even one grid cell")

    adjusted = None
    if nominal["triangles"] > cap_triangles:
        adjusted_pitch, adjusted = pitch_for_triangle_cap(
            args.width_mm, args.height_mm, pitch_mm, cap_triangles
        )
        adjusted["requested_pitch_mm"] = adjusted_pitch
        adjusted["reason"] = "nominal grid exceeded the planning triangle cap"
        warnings.append(
            "The nominal grid exceeds the selected working-memory/triangle cap. "
            "Use the adjusted uniform pitch, region-of-interest refinement, or a "
            "non-mesh representation until final export."
        )

    source_comparison = None
    if args.source_width_px and args.source_height_px:
        source_comparison = {
            "source_width_px": args.source_width_px,
            "source_height_px": args.source_height_px,
            "source_pitch_x_mm_if_full_coverage": args.width_mm
            / max(args.source_width_px - 1, 1),
            "source_pitch_y_mm_if_full_coverage": args.height_mm
            / max(args.source_height_px - 1, 1),
            "source_has_nominal_sample_count": (
                args.source_width_px >= nominal["width_px"]
                and args.source_height_px >= nominal["height_px"]
            ),
        }

    report: dict[str, Any] = {
        "physical_target_mm": {"width": args.width_mm, "height": args.height_mm},
        "process": args.process,
        "effective_feature_mm": feature_mm,
        "effective_feature_source": feature_source,
        "samples_per_feature": args.samples_per_feature,
        "nominal_pitch_mm": pitch_mm,
        "nominal_grid": nominal,
        "nominal_size_estimates": byte_summary(nominal["triangles"]),
        "planning_cap": {
            "memory_gb": args.memory_gb,
            "memory_fraction": args.memory_fraction,
            "triangle_cap": cap_triangles,
            "sources": cap_sources,
        },
        "adjusted_grid_if_needed": adjusted,
        "adjusted_size_estimates": (
            byte_summary(adjusted["triangles"]) if adjusted else None
        ),
        "source_comparison": source_comparison,
        "warnings": warnings,
        "notes": [
            "Triangle estimate assumes two triangles per regular height-map cell.",
            "Binary STL size is deterministic; working-memory figures are rough.",
            "Keep texture resolution independent from geometry-map resolution.",
            "Validate the chosen pitch and relief amplitude with a physical coupon.",
        ],
    }

    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
