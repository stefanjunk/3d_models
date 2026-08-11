#!/usr/bin/env python3
"""Revision-3 acceptance checks for the generated hair-clip package."""

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
        "revision_is_3": metrics["revision"] == 3,
        "complete_regular_hexagons": armor["cellShape"] == "complete-regular-hexagon",
        "top_cell_count_is_23": armor["topCellCount"] == 23,
        "non_bed_side_cell_count_is_8": armor["nonBedSideCellCount"] == 8,
        "across_flats_is_8_mm": close(armor["acrossFlatsMm"], 8.0),
        "groove_is_at_least_0_8_mm": armor["nominalGrooveMm"] >= 0.8,
        "structural_shell_width_is_22_mm": close(armor["structuralShellWidthMm"], 22.0),
        "complete_hex_envelope_is_25_6_mm": close(armor["completeCellEnvelopeWidthMm"], 25.6),
        "lower_rail_center_is_12_5_mm": close(rail["centralWidthMm"], 12.5),
        "lower_rail_ends_are_22_mm": close(rail["fullEndWidthMm"], 22.0),
        "length_in_approved_range": 50.0 <= dimensions[0] <= 65.0,
        "print_orientation_starts_at_z_zero": close(clip["bounds"][0][2], 0.0),
        "one_connected_kernel_body": clip["manifoldStatus"] == "NoError" and clip["connectedBodies"] == 1,
        "mass_below_20_g": 0.0 < clip["petgMassG"] < 20.0,
        "independent_mesh_audit_passed": mesh_audit.get("overall_pass") is True,
    }
    result = {
        "revision": 3,
        "checks": checks,
        "passed": all(checks.values()),
        "note": "Parameter and mesh gates are digital checks; real PETG fatigue and latch behavior require the coupon test.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()
