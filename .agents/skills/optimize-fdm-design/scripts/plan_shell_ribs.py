#!/usr/bin/env python3
"""Plan nominal FDM shell, rib, sealed-wall, floor, and flow dimensions."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def positive_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a finite number greater than zero")
    return parsed


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be an integer greater than zero")
    return parsed


def section_thickness(paths: int, line_width: float, spacing: float) -> float:
    return line_width + (paths - 1) * spacing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nozzle-mm", required=True, type=positive_float)
    parser.add_argument("--line-width-mm", type=positive_float, help="Defaults to 112.5%% of nozzle")
    parser.add_argument("--layer-height-mm", required=True, type=positive_float)
    parser.add_argument("--shell-lines", type=positive_int, default=3)
    parser.add_argument("--rib-lines", type=positive_int, default=2)
    parser.add_argument("--sealed-lines", type=positive_int, default=4)
    parser.add_argument("--floor-layers", type=positive_int, default=4)
    parser.add_argument("--plate-thickness-mm", type=positive_float, help="Optional thin CAD plate to check for an infill core")
    parser.add_argument("--wall-lines-per-side", type=positive_int, help="Defaults to --shell-lines for the opposing-wall check")
    parser.add_argument("--speed-mm-s", type=positive_float)
    parser.add_argument("--max-flow-mm3-s", type=positive_float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    nozzle = args.nozzle_mm
    width = args.line_width_mm or 1.125 * nozzle
    layer = args.layer_height_mm
    if layer >= width:
        parser.error("layer height must be smaller than line width for this spacing model")

    spacing = width - layer * (1.0 - math.pi / 4.0)
    sections = {
        "functional_shell": {
            "paths": args.shell_lines,
            "nominal_thickness_mm": section_thickness(args.shell_lines, width, spacing),
        },
        "rib_or_web": {
            "paths": args.rib_lines,
            "nominal_thickness_mm": section_thickness(args.rib_lines, width, spacing),
        },
        "sealed_wall_starting_point": {
            "paths": args.sealed_lines,
            "nominal_thickness_mm": section_thickness(args.sealed_lines, width, spacing),
        },
        "floor_or_skin": {
            "layers": args.floor_layers,
            "nominal_thickness_mm": args.floor_layers * layer,
        },
        "rib_root_radius_starting_point_mm": width,
    }

    opposing_wall_core_check = None
    if args.plate_thickness_mm is not None:
        wall_lines_per_side = args.wall_lines_per_side or args.shell_lines
        per_side_depth = section_thickness(wall_lines_per_side, width, spacing)
        combined_depth = 2.0 * per_side_depth
        remaining_core = args.plate_thickness_mm - combined_depth
        if remaining_core <= 0:
            core_status = "NO_INFILL_CORE"
        elif remaining_core < width:
            core_status = "SUB_LINE_WIDTH_CORE"
        else:
            core_status = "INFILL_CORE_PRESENT"
        opposing_wall_core_check = {
            "plate_thickness_mm": args.plate_thickness_mm,
            "wall_lines_per_side": wall_lines_per_side,
            "estimated_wall_depth_per_side_mm": per_side_depth,
            "estimated_combined_wall_depth_mm": combined_depth,
            "estimated_remaining_infill_core_mm": remaining_core,
            "status": core_status,
            "infill_percentage_can_change_bulk": core_status == "INFILL_CORE_PRESENT",
            "interpretation": "NO_INFILL_CORE means opposing wall stacks consume the plate; SUB_LINE_WIDTH_CORE is likely gap-fill/variable-width territory. Verify exact paths in the target slicer.",
        }

    warnings: list[str] = []
    ratio = layer / nozzle
    if ratio > 0.75:
        warnings.append("Layer height exceeds 75% of nozzle diameter; validate flow and layer bonding before release.")
    width_ratio = width / nozzle
    if width_ratio < 1.05 or width_ratio > 1.20:
        warnings.append("Line width is outside the common 105-120% nozzle starting range; use a tested slicer profile.")
    if args.rib_lines == 1:
        warnings.append("A single-path rib is process-sensitive and should not carry meaningful load without a coupon.")
    if opposing_wall_core_check and opposing_wall_core_check["status"] != "INFILL_CORE_PRESENT":
        warnings.append("The thin-plate estimate leaves no reliable infill core; changing infill percentage may not change material or strength.")

    requested_flow = None
    flow_limited_speed = None
    if args.speed_mm_s is not None:
        requested_flow = width * layer * args.speed_mm_s
        if args.max_flow_mm3_s is not None and requested_flow > args.max_flow_mm3_s:
            warnings.append("Requested speed exceeds the supplied volumetric-flow limit.")
    if args.max_flow_mm3_s is not None:
        flow_limited_speed = args.max_flow_mm3_s / (width * layer)

    result = {
        "process": {
            "nozzle_mm": nozzle,
            "line_width_mm": width,
            "layer_height_mm": layer,
            "constant_width_path_spacing_mm": spacing,
            "layer_to_nozzle_ratio": ratio,
            "line_width_to_nozzle_ratio": width_ratio,
            "speed_mm_s": args.speed_mm_s,
            "requested_flow_mm3_s": requested_flow,
            "max_flow_mm3_s": args.max_flow_mm3_s,
            "flow_limited_speed_mm_s": flow_limited_speed,
        },
        "sections": sections,
        "opposing_wall_core_check": opposing_wall_core_check,
        "warnings": warnings,
        "verification": [
            "Inspect exact wall paths in the target slicer; variable-width generators may differ from this constant-width estimate.",
            "For thin plates, confirm whether the two opposing wall stacks meet before treating infill as an optimization lever.",
            "Validate rib spacing, root, floor span, interface pads, and sealed walls for the actual load/process.",
            "Leak-test wetted walls and coupon any process-sensitive thin feature.",
        ],
    }

    encoded = json.dumps(result, indent=2, sort_keys=True)
    print(encoded)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
