#!/usr/bin/env python3
"""Fail-closed validation for the MM-TOY-002 v2 kinematic skeleton."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import cadquery as cq
import double_wishbone_v2_kinematics as kin
import parameters as p

SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
EXPORT_DIR = SCRIPT.parent / "exports" / "v0.4.0-draft.2-double-wishbone"
TOLERANCE_MM = 1e-6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_record(path: Path) -> dict[str, Any]:
    try:
        recorded_path = path.relative_to(PROJECT)
    except ValueError:
        recorded_path = path
    return {
        "path": str(recorded_path),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def range_record(values: Iterable[float]) -> dict[str, float]:
    materialized = list(values)
    return {"minimum": min(materialized), "maximum": max(materialized)}


def tire_y_bounds(pose: kin.CornerPose, radius: float) -> tuple[float, float]:
    axis = kin.v_unit(pose.wheel_axis)
    helper = (1.0, 0.0, 0.0) if abs(axis[0]) < 0.9 else (0.0, 0.0, 1.0)
    radial_a = kin.v_unit(kin.v_cross(axis, helper))
    radial_b = kin.v_unit(kin.v_cross(axis, radial_a))
    values: list[float] = []
    for axial in (-p.TIRE_WIDTH_MM / 2.0, p.TIRE_WIDTH_MM / 2.0):
        for degree in range(0, 360, 5):
            angle = math.radians(degree)
            radial = kin.v_add(
                kin.v_scale(radial_a, radius * math.cos(angle)),
                kin.v_scale(radial_b, radius * math.sin(angle)),
            )
            point = kin.v_add(
                kin.v_add(pose.wheel_center, kin.v_scale(axis, axial)), radial
            )
            values.append(point[1])
    return min(values), max(values)


def check_manifest(manifest_path: Path) -> tuple[bool, list[str]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for item in manifest["outputs"]:
        path = PROJECT / item["path"]
        if not path.is_file():
            errors.append(f"missing output {item['path']}")
            continue
        if path.stat().st_size != item["size_bytes"]:
            errors.append(f"size mismatch {item['path']}")
        if sha256(path) != item["sha256"]:
            errors.append(f"hash mismatch {item['path']}")
    if manifest["stl_export"] != "INTENTIONALLY_NOT_GENERATED":
        errors.append("manifest does not explicitly prohibit STL in skeleton phase")
    return not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--export-dir", type=Path, default=EXPORT_DIR)
    args = parser.parse_args()
    output = args.output.resolve()
    export_dir = args.export_dir.resolve()
    if output.exists():
        parser.error(f"refusing to overwrite existing evidence: {output}")

    paths = {
        "validator": SCRIPT,
        "kinematic_source": SCRIPT.parent / "double_wishbone_v2_kinematics.py",
        "parameters": SCRIPT.parent / "parameters.py",
        "design_spec": PROJECT / "design-spec.yaml",
        "approved_decomposition": PROJECT
        / "architecture"
        / "hybrid-design-plan-v0.4.0.json",
        "interface_contract": PROJECT
        / "architecture"
        / "double-wishbone-v2-interface-contract-v0.4.0.json",
        "cots_study": PROJECT / "reports" / "cots-drivetrain-study-v0.4.0.md",
        "chassis_source": SCRIPT.parent / "chassis.py",
        "reference_chassis_step": SCRIPT.parent
        / "exports"
        / "DRAFT-chassis-printed.step",
        "skeleton_step": export_dir
        / "DRAFT-double-wishbone-v2-kinematic-skeleton.step",
        "preview_png": export_dir / "DRAFT-double-wishbone-v2-neutral-preview.png",
        "manifest": export_dir / "manifest.json",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing validation inputs: " + ", ".join(missing))

    contract = json.loads(paths["interface_contract"].read_text(encoding="utf-8"))
    chassis_source = paths["chassis_source"].read_text(encoding="utf-8")
    travel_values = kin.axis_range(
        p.DWV2_TRAVEL_MIN_MM,
        p.DWV2_TRAVEL_MAX_MM,
        p.DWV2_TRAVEL_STEP_MM,
    )
    steer_values = kin.axis_range(
        p.DWV2_STEER_MIN_DEG,
        p.DWV2_STEER_MAX_DEG,
        p.DWV2_STEER_STEP_DEG,
    )
    front_poses = [
        kin.corner_pose("front", side, travel, steer)
        for side in (-1, 1)
        for travel in travel_values
        for steer in steer_values
    ]
    rear_poses = [
        kin.corner_pose("rear", side, travel, 0.0)
        for side in (-1, 1)
        for travel in travel_values
    ]
    all_poses = front_poses + rear_poses

    lower_nominal_radius = math.hypot(
        p.DWV2_LOWER_OUTER_Y_MM - p.DWV2_LOWER_INBOARD_Y_MM,
        p.DWV2_LOWER_OUTER_Z_MM - p.DWV2_LOWER_INBOARD_Z_MM,
    )
    upper_nominal_radius = math.hypot(
        p.DWV2_UPPER_OUTER_Y_MM - p.DWV2_UPPER_INBOARD_Y_MM,
        p.DWV2_UPPER_OUTER_Z_MM - p.DWV2_UPPER_INBOARD_Z_MM,
    )
    radius_errors: list[float] = []
    upright_errors: list[float] = []
    front_tie_errors: list[float] = []
    rear_toe_errors: list[float] = []
    branch_steps: list[float] = []
    for axle in ("front", "rear"):
        for side in (-1, 1):
            nominal = kin.corner_pose(axle, side, 0.0, 0.0)
            upright_length = kin.distance(nominal.lower_outer, nominal.upper_outer)
            tie_length = kin.distance(nominal.tie_inner, nominal.tie_outer)
            previous_lower: kin.Vec3 | None = None
            previous_upper: kin.Vec3 | None = None
            for travel in travel_values:
                pose = kin.corner_pose(axle, side, travel, 0.0)
                lower_center = (
                    kin.axle_x(axle),
                    float(side) * p.DWV2_LOWER_INBOARD_Y_MM,
                    p.DWV2_LOWER_INBOARD_Z_MM,
                )
                upper_center = (
                    kin.upper_outer_x(axle),
                    float(side) * p.DWV2_UPPER_INBOARD_Y_MM,
                    p.DWV2_UPPER_INBOARD_Z_MM,
                )
                radius_errors.extend(
                    [
                        abs(
                            kin.distance(lower_center, pose.lower_outer)
                            - lower_nominal_radius
                        ),
                        abs(
                            kin.distance(upper_center, pose.upper_outer)
                            - upper_nominal_radius
                        ),
                    ]
                )
                upright_errors.append(
                    abs(
                        kin.distance(pose.lower_outer, pose.upper_outer)
                        - upright_length
                    )
                )
                if axle == "front":
                    for steer in steer_values:
                        steered = kin.corner_pose(axle, side, travel, steer)
                        front_tie_errors.append(
                            abs(
                                kin.distance(steered.tie_inner, steered.tie_outer)
                                - tie_length
                            )
                        )
                else:
                    rear_toe_errors.append(
                        abs(kin.distance(pose.tie_inner, pose.tie_outer) - tie_length)
                    )
                if previous_lower is not None and previous_upper is not None:
                    branch_steps.extend(
                        [
                            kin.distance(previous_lower, pose.lower_outer),
                            kin.distance(previous_upper, pose.upper_outer),
                        ]
                    )
                previous_lower, previous_upper = pose.lower_outer, pose.upper_outer

    diagonal_states = [
        {
            "axle": axle,
            "left_travel_mm": left,
            "right_travel_mm": right,
            "left_wheel_center": kin.corner_pose(axle, 1, left, 0.0).wheel_center,
            "right_wheel_center": kin.corner_pose(axle, -1, right, 0.0).wheel_center,
        }
        for axle in ("front", "rear")
        for left, right in ((10.0, -10.0), (-10.0, 10.0))
    ]

    dynamic_width: dict[str, dict[str, float]] = {}
    neutral_width: dict[str, float] = {}
    for radius in contract["sweep_contract"]["tire_radii_mm"]:
        y_values: list[float] = []
        for pose in front_poses:
            minimum_y, maximum_y = tire_y_bounds(pose, radius)
            y_values.extend([minimum_y, maximum_y])
        dynamic_width[f"radius_{radius:g}_mm"] = {
            "minimum_y_mm": min(y_values),
            "maximum_y_mm": max(y_values),
            "total_swept_width_mm": max(y_values) - min(y_values),
        }
        neutral_left = tire_y_bounds(kin.corner_pose("front", 1, 0.0, 0.0), radius)
        neutral_right = tire_y_bounds(kin.corner_pose("front", -1, 0.0, 0.0), radius)
        neutral_width[f"radius_{radius:g}_mm"] = neutral_left[1] - neutral_right[0]

    manifest_ok, manifest_errors = check_manifest(paths["manifest"])
    skeleton = cq.importers.importStep(str(paths["skeleton_step"])).val()
    skeleton_valid = skeleton.isValid() and len(skeleton.Solids()) > 1
    unexpected_stl = sorted(str(path) for path in export_dir.glob("*.stl"))

    current_chassis_axis_mismatch = (
        "y-axis 3.2 mm bores" in chassis_source
        and "Shock towers" in chassis_source
        and "DWV2_" not in chassis_source
    )
    shock_lengths = [pose.shock_length_mm for pose in all_poses]
    shaft_lengths = [pose.halfshaft_length_mm for pose in all_poses]
    shaft_angles = [pose.halfshaft_angle_deg for pose in all_poses]
    rear_toes = [pose.rear_toe_deg for pose in rear_poses]
    rack_y = [abs(pose.tie_inner[1]) for pose in front_poses]
    wheel_x = [pose.wheel_center[0] for pose in front_poses]
    wheel_y = [abs(pose.wheel_center[1]) for pose in front_poses]
    wheel_z = [pose.wheel_center[2] for pose in front_poses]
    max_link_error = max(
        radius_errors + upright_errors + front_tie_errors + rear_toe_errors
    )
    shaft_cots_min, shaft_cots_max = p.RC4WD_VVV_S0183_LENGTH_RANGE_MM
    shaft_proxy_inside_published_range = (
        min(shaft_lengths) >= shaft_cots_min and max(shaft_lengths) <= shaft_cots_max
    )

    checks = [
        {
            "id": "four-bar-link-closure",
            "status": "PASS" if max_link_error <= TOLERANCE_MM else "FAIL",
            "message": f"Maximum rigid-link closure error is {max_link_error:.3e} mm.",
        },
        {
            "id": "continuous-nonsingular-branch",
            "status": "PASS" if max(branch_steps) < 2.0 else "FAIL",
            "message": f"Maximum outer-joint movement between adjacent 1 mm travel samples is {max(branch_steps):.6f} mm.",
        },
        {
            "id": "front-suspension-steering-sweep",
            "status": "PASS" if len(front_poses) == 2 * 21 * 21 else "FAIL",
            "message": f"Solved {len(front_poses)} mirrored front poses (441 per side) across the full declared matrix.",
        },
        {
            "id": "rear-toe-link-closure",
            "status": "PASS"
            if max(abs(value) for value in rear_toes) <= 1.0
            else "FAIL",
            "message": f"Rear toe closure remains {min(rear_toes):.6f} to {max(rear_toes):.6f} degrees within the provisional planning bound.",
        },
        {
            "id": "shock-is-not-locating-link",
            "status": "PASS"
            if max(shock_lengths) - min(shock_lengths) > 5.0
            else "FAIL",
            "message": f"Shock eye distance varies from {min(shock_lengths):.6f} to {max(shock_lengths):.6f} mm and is not used in four-bar closure.",
        },
        {
            "id": "skeleton-artifact-integrity",
            "status": "PASS"
            if skeleton_valid and manifest_ok and not unexpected_stl
            else "FAIL",
            "message": "STEP is a valid multi-solid proxy compound; manifest hashes match; no STL was generated."
            if skeleton_valid and manifest_ok and not unexpected_stl
            else f"manifest_errors={manifest_errors}; unexpected_stl={unexpected_stl}",
        },
        {
            "id": "current-chassis-v1-interface",
            "status": "FAIL" if current_chassis_axis_mismatch else "REVIEW_REQUIRED",
            "message": "Current chassis source explicitly uses y-axis lower pivot bores, has no upper wishbone pivots and consumes no v2 x-axis datums.",
        },
        {
            "id": "halfshaft-cots-compatibility",
            "status": "PASS"
            if shaft_proxy_inside_published_range
            else "REVIEW_REQUIRED",
            "message": f"Skeleton proxy spans {min(shaft_lengths):.6f} to {max(shaft_lengths):.6f} mm versus the published candidate range {shaft_cots_min:.1f} to {shaft_cots_max:.1f} mm; actual joint centers and angular/plunge limits are unmeasured.",
        },
        {
            "id": "wheel-rim-cavity-and-dynamic-envelope",
            "status": "REVIEW_REQUIRED",
            "message": "Full tire cylinders overlap the joint region by construction; rim cavity, wheel backspacing and the acceptable dynamic width definition require measured hardware.",
        },
        {
            "id": "manufacturing-geometry",
            "status": "NOT_RUN",
            "message": "This phase intentionally contains no printable arm, upright or chassis-v2 solid.",
        },
        {
            "id": "anycubic-exact-slicer",
            "status": "NOT_RUN",
            "message": "No manufacturing STL/3MF exists and complete explicit machine/process/filament JSON profiles are absent.",
        },
        {
            "id": "watermark",
            "status": "NOT_RUN",
            "message": "Watermark remains deferred until a stable physical candidate; applying it to a skeleton would be premature.",
        },
    ]

    result = {
        "schema_version": "1.0",
        "tool": "validate_double_wishbone_v2.py",
        "tool_version": "1.0.0",
        "project_id": "MM-TOY-002",
        "project_revision": "0.4.0",
        "candidate": "0.4.0-draft.2",
        "profile": "non-manufacturing-kinematic-skeleton",
        "run_date": datetime.now(tz=UTC).date().isoformat(),
        "status": "FAIL",
        "decision": "BLOCKED",
        "passed_scope": "point/axis double-wishbone topology and deterministic motion closure",
        "blocking_scope": "current chassis integration, measured purchased interfaces and all manufacturing evidence",
        "checks": checks,
        "metrics": {
            "pose_counts": {
                "front_per_side": len(front_poses) // 2,
                "front_total": len(front_poses),
                "rear_per_side": len(rear_poses) // 2,
                "rear_total": len(rear_poses),
                "tire_radii_checked": len(contract["sweep_contract"]["tire_radii_mm"]),
            },
            "link_closure_max_error_mm": max_link_error,
            "adjacent_branch_step_max_mm": max(branch_steps),
            "front_wheel_center_sweep_mm": {
                "x": range_record(wheel_x),
                "absolute_y": range_record(wheel_y),
                "z": range_record(wheel_z),
            },
            "front_rack_inner_absolute_y_corridor_mm": range_record(rack_y),
            "shock_eye_distance_mm": range_record(shock_lengths),
            "rear_toe_deg": range_record(rear_toes),
            "halfshaft_proxy": {
                "length_mm": range_record(shaft_lengths),
                "length_change_mm": max(shaft_lengths) - min(shaft_lengths),
                "angle_deg": range_record(shaft_angles),
                "published_candidate_length_range_mm": [shaft_cots_min, shaft_cots_max],
                "inside_published_length_range": shaft_proxy_inside_published_range,
                "compatibility_claim": False,
            },
            "tire_envelopes": {
                "neutral_total_width_mm": neutral_width,
                "front_dynamic_swept_width_mm": dynamic_width,
                "project_nominal_width_limit_mm": p.OVERALL_WIDTH_MAX_MM,
                "interpretation": "dynamic sweep is a keep-out metric; whether the nominal width limit applies at steering lock remains a requirement review item",
            },
            "diagonal_states": diagonal_states,
        },
        "inputs": [input_record(path) for path in paths.values()],
        "limitations": [
            "No arm/upright section, bearing seat, fastener geometry or structural load model exists in this phase.",
            "Proxy collision cannot prove rim, CVD, shock or chassis clearance without measured hardware.",
            "Analytic closure does not certify material strength, fatigue life, safety or driving behavior.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "decision": result["decision"],
                "output": str(output),
            },
            indent=2,
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
