#!/usr/bin/env python3
"""Revision-5 acceptance checks for the mirrored honeycomb end contour."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def close(actual: float, expected: float, tolerance: float = 1e-5) -> bool:
    return abs(actual - expected) <= tolerance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--mesh-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    mesh_audit = json.loads(args.mesh_audit.read_text(encoding="utf-8"))
    armor = metrics["armor"]
    rail = metrics["lowerRail"]
    clip = metrics["clip"]
    dimensions = clip["dimensionsMm"]

    checks = {
        "revision_is_5": metrics["revision"] == 5,
        "uniform_pointy_hexagons": armor["cellShape"] == "uniform-pointy-near-regular-hexagon",
        "true_staggered_honeycomb": armor["layout"] == "true-staggered-honeycomb-lattice",
        "five_rows_with_mirrored_end_cells": armor["rowCount"] == 5 and armor["cellsPerRow"] == [3, 4, 3, 4, 3],
        "seventeen_total_cells": armor["totalCellCount"] == 17,
        "only_three_build_side_half_cells": armor["buildSideHalfCellCount"] == 3,
        "fourteen_cells_remain_whole": armor["fullCellCount"] == 14,
        "non_bed_boundary_has_three_whole_cells": armor["nonBedSideWholeCellCount"] == 3,
        "across_flats_is_10_mm": close(armor["acrossFlatsMm"], 10.0),
        "groove_is_at_least_0_8_mm": armor["nominalGrooveMm"] >= 0.8,
        "longitudinal_fit_scale_is_controlled": 0.95 <= armor["longitudinalScale"] <= 1.0,
        "end_contour_is_declared_mirrored": armor["mirroredEndContour"] is True,
        "hinge_and_latch_overhang_match": close(armor["hingeOverhangPastShellMm"], armor["latchOverhangPastShellMm"]),
        "both_end_overhangs_exceed_6_mm": armor["hingeOverhangPastShellMm"] > 6.0 and armor["latchOverhangPastShellMm"] > 6.0,
        "one_orientation_only": armor["uniformOrientation"] is True,
        "rotated_side_row_removed": armor["dedicatedRotatedSideRow"] is False,
        "standalone_end_blocks_removed": armor["standaloneEndBlocks"] is False,
        "whole_cell_non_bed_envelope_is_26_6_mm": close(armor["nonBedCellEnvelopeMaxZMm"], 26.6),
        "structural_shell_width_is_22_mm": close(armor["structuralShellWidthMm"], 22.0),
        "lower_rail_center_is_12_5_mm": close(rail["centralWidthMm"], 12.5),
        "lower_rail_ends_are_22_mm": close(rail["fullEndWidthMm"], 22.0),
        "length_in_approved_range": 50.0 <= dimensions[0] <= 65.0,
        "print_orientation_starts_at_z_zero": close(clip["bounds"][0][2], 0.0),
        "one_connected_kernel_body": clip["manifoldStatus"] == "NoError" and clip["connectedBodies"] == 1,
        "mass_below_20_g": 0.0 < clip["petgMassG"] < 20.0,
        "independent_mesh_audit_passed": mesh_audit.get("overall_pass") is True,
    }
    result = {
        "revision": 5,
        "checks": checks,
        "passed": all(checks.values()),
        "note": "Digital mirrored-end lattice and mesh gates passed only if every value is true; PETG fatigue and latch behavior still require the coupon test.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()
