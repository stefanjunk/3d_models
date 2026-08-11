#!/usr/bin/env python3
"""Select a process-safe JuSt Innovation underside-watermark profile and scale."""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Profile:
    name: str
    width_mm: float
    height_mm: float
    max_reference_scale: float
    dxf: str
    svg: str


PROFILES = {
    "standard": Profile(
        "standard",
        32.0,
        10.0,
        60.0 / 32.0,
        "assets/just-innovation-watermark/exports/dxf/just-innovation-standard.dxf",
        "assets/just-innovation-watermark/exports/svg/just-innovation-standard.svg",
    ),
    "compact": Profile(
        "compact",
        11.4232449531,
        10.0,
        1.6,
        "assets/just-innovation-watermark/exports/dxf/just-innovation-compact.dxf",
        "assets/just-innovation-watermark/exports/svg/just-innovation-compact.svg",
    ),
}


def positive(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def best_orientation(profile: Profile, safe_width: float, safe_height: float) -> tuple[int, float]:
    choices: list[tuple[int, float]] = []
    for rotation, width, height in (
        (0, profile.width_mm, profile.height_mm),
        (90, profile.height_mm, profile.width_mm),
    ):
        choices.append((rotation, min(safe_width / width, safe_height / height)))
    return max(choices, key=lambda item: (item[1], -item[0]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface-width", type=positive, required=True)
    parser.add_argument("--surface-height", type=positive, required=True)
    parser.add_argument("--host-wall", type=positive, required=True)
    parser.add_argument("--nozzle", type=positive, default=0.4)
    parser.add_argument("--layer-height", type=positive, default=0.2)
    parser.add_argument("--depth", type=positive, default=0.4)
    parser.add_argument("--edge-clearance", type=positive)
    parser.add_argument("--prefer", choices=["auto", "standard", "compact"], default="auto")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    edge_clearance = round(args.edge_clearance or max(2.0, 2.0 * args.nozzle), 6)
    feature_clearance = round(max(3.0, 4.0 * args.nozzle), 6)
    safe_width = args.surface_width - 2.0 * edge_clearance
    safe_height = args.surface_height - 2.0 * edge_clearance
    process_scale = round(max(1.0, args.nozzle / 0.4), 6)
    minimum_host_wall = round(max(1.2, args.depth + 2.0 * args.nozzle), 6)

    if not 0.2 <= args.depth <= 0.8:
        errors.append("recess depth must remain between 0.20 and 0.80 mm")
    if args.depth < args.layer_height:
        errors.append("recess depth is smaller than one layer and may disappear in slicing")
    elif args.depth < 2.0 * args.layer_height:
        warnings.append("recess spans fewer than two nominal layers; inspect the exact slicer paths")
    layer_count = args.depth / args.layer_height
    if not math.isclose(layer_count, round(layer_count), rel_tol=0.0, abs_tol=1e-6):
        warnings.append("recess depth is not an integer multiple of layer height")
    if args.host_wall < minimum_host_wall:
        errors.append(
            f"host wall {args.host_wall:.3f} mm is below the required {minimum_host_wall:.3f} mm"
        )
    if safe_width <= 0 or safe_height <= 0:
        errors.append("edge clearance consumes the candidate surface")

    fit: dict[str, tuple[int, float]] = {}
    if safe_width > 0 and safe_height > 0:
        fit = {
            name: best_orientation(profile, safe_width, safe_height)
            for name, profile in PROFILES.items()
        }

    selected_name: str | None = None
    surface_long = max(args.surface_width, args.surface_height)
    if args.prefer != "auto":
        candidate = args.prefer
        if fit.get(candidate, (0, 0.0))[1] >= process_scale:
            selected_name = candidate
        else:
            errors.append(f"requested {candidate} profile does not fit at process-safe scale")
    else:
        standard_fits = fit.get("standard", (0, 0.0))[1] >= process_scale
        compact_fits = fit.get("compact", (0, 0.0))[1] >= process_scale
        standard_min_long = PROFILES["standard"].width_mm * process_scale
        if standard_fits and standard_min_long <= 0.45 * surface_long:
            selected_name = "standard"
        elif compact_fits:
            selected_name = "compact"
        elif standard_fits:
            selected_name = "standard"
        else:
            errors.append(
                "no approved profile fits; use a larger safe region, alternate surface/orientation, or finer validated nozzle"
            )

    selection: dict[str, object] | None = None
    if selected_name:
        profile = PROFILES[selected_name]
        rotation, maximum_fit_scale = fit[selected_name]
        if selected_name == "standard":
            aesthetic_scale = 0.25 * surface_long / profile.width_mm
        else:
            aesthetic_scale = 0.20 * surface_long / 10.0
        desired_scale = max(
            process_scale,
            min(max(process_scale, profile.max_reference_scale), aesthetic_scale),
        )
        scale = min(maximum_fit_scale, desired_scale)
        width = profile.width_mm * scale
        height = profile.height_mm * scale
        if rotation == 90:
            width, height = height, width
        selection = {
            "variant": selected_name,
            "uniform_scale": round(scale, 6),
            "rotation_deg": rotation,
            "actual_envelope_mm": [round(width, 4), round(height, 4)],
            "nominal_profile_envelope_mm": [profile.width_mm, profile.height_mm],
            "compact_across_flats_mm": round(10.0 * scale, 4) if selected_name == "compact" else None,
            "depth_mm": args.depth,
            "dxf": profile.dxf,
            "svg": profile.svg,
        }

    result = {
        "status": "PASS" if not errors and selection else "BLOCK",
        "asset_id": "JSI-WM-001-R1",
        "brand": "JuSt Innovation",
        "operation": "recessed",
        "preferred_surface": "print-bed-facing-underside",
        "candidate_surface_mm": [args.surface_width, args.surface_height],
        "safe_rectangle_mm": [round(max(0.0, safe_width), 4), round(max(0.0, safe_height), 4)],
        "edge_clearance_mm": edge_clearance,
        "recommended_feature_clearance_mm": feature_clearance,
        "minimum_host_wall_mm": minimum_host_wall,
        "residual_host_wall_mm": round(args.host_wall - args.depth, 4),
        "process_scale_floor": process_scale,
        "selection": selection,
        "orientation_check": "verify readable from the exported finished underside; mirror only if that direct view is mirrored",
        "errors": errors,
        "warnings": warnings,
    }
    output = json.dumps(result, indent=2)
    if args.json_out:
        target = Path(args.json_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
