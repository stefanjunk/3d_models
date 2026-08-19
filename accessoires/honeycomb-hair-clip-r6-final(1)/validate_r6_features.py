#!/usr/bin/env python3
"""Revision-6 parametric, hinge, honeycomb, and export acceptance checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_PRESETS = {
    "small": (68.0, 8.0),
    "medium": (76.0, 10.0),
    "large": (85.0, 12.0),
    "extra_large": (96.0, 15.0),
}


def close(actual: float, expected: float, tolerance: float = 1e-5) -> bool:
    return abs(actual - expected) <= tolerance


def load_audits(directory: Path) -> dict[str, dict]:
    audits: dict[str, dict] = {}
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        audits[path.stem] = data
    return audits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--boundary-min", type=Path, required=True)
    parser.add_argument("--boundary-max", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-release-state", choices=("DRAFT", "FINAL"), default="FINAL")
    args = parser.parse_args()

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    presets = summary["results"]
    audits = load_audits(args.audit_dir)
    boundary_min = json.loads(args.boundary_min.read_text(encoding="utf-8"))["result"]
    boundary_max = json.loads(args.boundary_max.read_text(encoding="utf-8"))["result"]

    checks: dict[str, bool] = {
        "revision_is_6": summary.get("revision") == 6,
        "release_state_matches_expected": summary.get("releaseState") == args.expected_release_state,
        "all_named_presets_present": set(presets) == set(EXPECTED_PRESETS),
        "all_export_audits_pass": bool(audits) and all(item.get("overall_pass") is True for item in audits.values()),
    }

    for name, (expected_length, expected_rise) in EXPECTED_PRESETS.items():
        item = presets[name]
        params = item["parameters"]
        hinge = item["hinge"]
        armor = item["armor"]
        assembly = item["assembly"]
        watermark = item["watermark"]
        prefix = f"{name}_"
        checks.update({
            prefix + "requested_length_parameter": close(params["clipLengthMm"], expected_length),
            prefix + "requested_arch_rise_parameter": close(params["archRiseMm"], expected_rise),
            prefix + "overall_length_within_half_mm": abs(assembly["dimensionsMm"][0] - expected_length) <= 0.5,
            prefix + "two_moving_mesh_components": assembly["connectedBodies"] == 2,
            prefix + "each_source_body_connected": item["upperBody"]["connectedBodies"] == 1 and item["lowerBody"]["connectedBodies"] == 1,
            prefix + "assembly_kernel_clean": assembly["manifoldStatus"] == "NoError",
            prefix + "mass_below_30_g": 0 < assembly["petgMassG"] < 30,
            prefix + "bed_datum_is_zero": close(assembly["bounds"][0][2], 0.0),
            prefix + "hinge_pin_is_4_mm": close(hinge["pinDiameterMm"], 4.0),
            prefix + "radial_clearance_is_0_35_mm": close(hinge["radialClearanceMm"], 0.35),
            prefix + "axial_clearance_is_0_40_mm": close(hinge["axialClearanceEachSideMm"], 0.40),
            prefix + "hinge_travel_at_least_28_deg": hinge["usefulTravelDeg"] >= 28.0,
            prefix + "kinematic_core_collision_free": hinge["kinematicCoreCollisionFree"] is True,
            prefix + "terminal_closed_pose_nonintersecting": hinge["terminalClosedIntersectionVolumeMm3"] <= 0.05,
            prefix + "hard_stop_contacts_only_at_full_open": 0 < hinge["hardStopContactVolumeAtFullOpenMm3"] < 1.0,
            prefix + "latch_screening_strain_below_one_percent": hinge["latchEstimatedOuterFiberStrain"] < 0.01,
            prefix + "exactly_three_transverse_rows": armor["rowCount"] == 3 and len(armor["cellsPerRow"]) == 3,
            prefix + "center_row_is_staggered": armor["cellsPerRow"][0] == armor["cellsPerRow"][2] and armor["cellsPerRow"][1] == armor["cellsPerRow"][0] - 1,
            prefix + "large_derived_hexagons": close(armor["acrossFlatsMm"], 18.533333333333335),
            prefix + "groove_at_least_0_8_mm": armor["nominalGrooveMm"] >= 0.8,
            prefix + "one_hex_orientation_only": armor["uniformOrientation"] is True and armor["dedicatedRotatedSideRow"] is False,
            prefix + "no_standalone_end_blocks": armor["standaloneEndBlocks"] is False,
            prefix + "bed_row_only_is_clipped": armor["buildSideHalfCellCount"] == armor["cellsPerRow"][0],
            prefix + "non_bed_row_cells_whole": armor["nonBedSideWholeCellCount"] == armor["cellsPerRow"][2],
            prefix + "watermark_is_included": watermark["included"] is True,
            prefix + "watermark_asset_is_exact_release": watermark["assetId"] == "JSI-WM-001-R1" and watermark["profile"] == "compact",
            prefix + "watermark_recess_is_0_4_mm": close(watermark["depthMm"], 0.40),
            prefix + "watermark_does_not_cross_cell_grooves": watermark["edgeClearanceMm"] >= 2.0,
            prefix + "watermark_residual_wall_is_safe": watermark["residualHostWallMm"] >= 1.2,
        })

    for label, item, expected_length, expected_rise in (
        ("boundary_min", boundary_min, 65.0, 7.0),
        ("boundary_max", boundary_max, 105.0, 18.0),
    ):
        checks.update({
            label + "_generates": item["assembly"]["manifoldStatus"] == "NoError",
            label + "_length_parameter": close(item["parameters"]["clipLengthMm"], expected_length),
            label + "_rise_parameter": close(item["parameters"]["archRiseMm"], expected_rise),
            label + "_two_components": item["assembly"]["connectedBodies"] == 2,
            label + "_terminal_pose_clear": item["hinge"]["terminalClosedIntersectionVolumeMm3"] <= 0.05,
            label + "_three_rows": item["armor"]["rowCount"] == 3,
        })

    result = {
        "revision": 6,
        "checks": checks,
        "check_count": len(checks),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "passed": all(checks.values()),
        "note": "Digital geometry, parameter, mesh, and kinematic checks do not replace the PETG print-in-place release, latch, wear, or comfort tests.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()
