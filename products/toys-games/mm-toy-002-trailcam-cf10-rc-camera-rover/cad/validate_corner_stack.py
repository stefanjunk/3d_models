#!/usr/bin/env python3
"""Deterministic integration audit for the rejected MM-TOY-002 corner stack.

The script is intentionally read-only with respect to CAD inputs.  It measures
the version-0.4.0 chassis/suspension STEP baseline, checks the approved
decomposition against the experimental suspension source, and evaluates the
documented trailing-arm kinematic proposal.  It does not import the CAD source
modules because those modules export files as an import side effect.

The output path must not exist.  This preserves every exact audit run instead
of silently overwriting prior evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import date
from pathlib import Path
from typing import Any

import cadquery as cq


SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
CAD = PROJECT / "cad"
EXPORTS = CAD / "exports"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(PROJECT)),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def load_step(path: Path) -> cq.Shape:
    shape = cq.importers.importStep(str(path)).val()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"expected one valid solid: {path}")
    return shape


def common_volume_mm3(a: cq.Shape, b: cq.Shape) -> float:
    common = a.intersect(b)
    return float(sum(solid.Volume() for solid in common.Solids()))


def component(plan: dict[str, Any], component_id: str) -> dict[str, Any]:
    return next(item for item in plan["components"] if item["id"] == component_id)


def interface(plan: dict[str, Any], interface_id: str) -> dict[str, Any]:
    return next(item for item in plan["interfaces"] if item["id"] == interface_id)


def trailing_arm_pose(delta_z_mm: float) -> dict[str, float]:
    """Rejected v2 proposal: pivot (86, 8), wheel (126, 5), lower eye (126, 14)."""
    pivot_x, pivot_z = 86.0, 8.0
    wheel_dx, wheel_dz = 40.0, -3.0
    radius = math.hypot(wheel_dx, wheel_dz)
    alpha_static = math.atan2(wheel_dz, wheel_dx)
    theta = math.asin((wheel_dz + delta_z_mm) / radius) - alpha_static

    wheel_x = pivot_x + radius * math.cos(alpha_static + theta)
    wheel_z = 5.0 + delta_z_mm
    lower_eye_x = pivot_x + 40.0 * math.cos(theta) - 6.0 * math.sin(theta)
    lower_eye_z = pivot_z + 40.0 * math.sin(theta) + 6.0 * math.cos(theta)
    shock_length = math.sqrt(
        (lower_eye_x - 126.0) ** 2 + (78.0 - 51.0) ** 2 + (lower_eye_z - 45.0) ** 2
    )
    return {
        "wheel_delta_z_mm": delta_z_mm,
        "rotation_deg": math.degrees(theta),
        "wheel_x_mm": wheel_x,
        "wheel_z_mm": wheel_z,
        "lower_shock_eye_x_mm": lower_eye_x,
        "lower_shock_eye_y_mm": 78.0,
        "lower_shock_eye_z_mm": lower_eye_z,
        "shock_eye_distance_mm": shock_length,
        "nominal_tire_ground_clearance_mm": wheel_z - 45.0 - (-40.0),
        "max_tire_envelope_ground_clearance_mm": wheel_z - 57.5 - (-40.0),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error(f"refusing to overwrite existing evidence: {output}")

    paths = {
        "validator": SCRIPT,
        "design_spec": PROJECT / "design-spec.yaml",
        "decomposition": PROJECT / "architecture" / "hybrid-design-plan-v0.4.0.json",
        "parameters": CAD / "parameters.py",
        "chassis_source": CAD / "chassis.py",
        "suspension_source": CAD / "suspension.py",
        "chassis_step": EXPORTS / "DRAFT-chassis-printed.step",
        "chassis_stl": EXPORTS / "DRAFT-chassis-printed.stl",
        "arm_left_step": EXPORTS / "DRAFT-suspension-arm-left.step",
        "arm_left_stl": EXPORTS / "DRAFT-suspension-arm-left.stl",
        "arm_right_step": EXPORTS / "DRAFT-suspension-arm-right.step",
        "arm_right_stl": EXPORTS / "DRAFT-suspension-arm-right.stl",
        "carrier_left_step": EXPORTS / "DRAFT-axle-carrier-left-front.step",
        "carrier_left_stl": EXPORTS / "DRAFT-axle-carrier-left-front.stl",
        "carrier_right_step": EXPORTS / "DRAFT-axle-carrier-right-front.step",
        "carrier_right_stl": EXPORTS / "DRAFT-axle-carrier-right-front.stl",
        "carrier_left_rear_step": EXPORTS / "DRAFT-axle-carrier-left-rear.step",
        "carrier_left_rear_stl": EXPORTS / "DRAFT-axle-carrier-left-rear.stl",
        "carrier_right_rear_step": EXPORTS / "DRAFT-axle-carrier-right-rear.step",
        "carrier_right_rear_stl": EXPORTS / "DRAFT-axle-carrier-right-rear.stl",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing audit inputs: " + ", ".join(missing))

    plan = json.loads(paths["decomposition"].read_text(encoding="utf-8"))
    suspension_text = paths["suspension_source"].read_text(encoding="utf-8")

    chassis = load_step(paths["chassis_step"])
    collision_inputs = {
        "arm_left": load_step(paths["arm_left_step"]),
        "arm_right": load_step(paths["arm_right_step"]),
        "carrier_left_front": load_step(paths["carrier_left_step"]),
        "carrier_right_front": load_step(paths["carrier_right_step"]),
    }
    collisions = {
        name: common_volume_mm3(chassis, shape)
        for name, shape in collision_inputs.items()
    }

    # Conservative purchased-part proxies.  They are collision keep-outs only,
    # not supplier-authoritative component geometry.
    motor_proxy = cq.Solid.makeCylinder(
        18.4, 80.0, pnt=(126.0, 76.0, 5.0), dir=(0.0, -1.0, 0.0)
    )
    motor_proxy_common = common_volume_mm3(chassis, motor_proxy)

    # The rejected v2 pivot plate (x=76..96, y=38..75, z=0..4) reaches into
    # the conservative full-cylinder wheel envelope.  Real rim hollows remain
    # unknown and may only replace this proxy after measurement.
    pivot_plate = cq.Solid.makeBox(20.0, 37.0, 4.0, pnt=(76.0, 38.0, 0.0))
    tire_proxy_common: dict[str, float] = {}
    for diameter in (90.0, 115.0):
        tire = cq.Solid.makeCylinder(
            diameter / 2.0, 33.0, pnt=(126.0, 66.0, 5.0), dir=(0.0, 1.0, 0.0)
        )
        tire_proxy_common[f"diameter_{diameter:.0f}_mm"] = common_volume_mm3(
            pivot_plate, tire
        )

    arms = component(plan, "SUSPENSION_ARMS")
    shocks = component(plan, "SHOCK_SET")
    carrier_interface = interface(plan, "IF-SUSP-CARRIERS")
    approved_contract = {
        "suspension_name": arms["name"],
        "suspension_functions": arms["functions"],
        "shock_functions": shocks["functions"],
        "carrier_interface_type": carrier_interface["nominal_geometry"]["type"],
    }
    experimental_source_flags = {
        "shock_used_as_upper_link": "upper coil-over shock acting as the upper link"
        in suspension_text,
        "carrier_contains_motor_clamp": "motor clamp bore" in suspension_text,
        "carrier_has_chassis_anti_rotation_tabs": "anti-rotation tabs" in suspension_text,
        "two_vertical_arm_carrier_holes": "two outer M3 holes, vertical axis"
        in suspension_text,
    }

    tang_gap_mm = 4.0
    tang_thickness_mm = 3.6
    tang_clearance_per_side_mm = (tang_gap_mm - tang_thickness_mm) / 2.0
    flange_clearance_per_side_mm = min(4.2 - 4.0, 8.4 - 8.2)
    required_clearance_per_side_mm = 0.25
    pivot_bore_diameter_mm = 3.2
    required_ligament_mm = 5.0
    required_local_section_diameter_mm = (
        pivot_bore_diameter_mm + 2.0 * required_ligament_mm
    )
    pivot_center_min_above_base_mm = (
        4.0
        + required_clearance_per_side_mm
        + pivot_bore_diameter_mm / 2.0
        + required_ligament_mm
    )

    poses = [trailing_arm_pose(delta) for delta in (-15.0, -10.0, 0.0, 10.0, 15.0)]

    checks = [
        {
            "id": "approved-architecture-match",
            "status": "FAIL" if any(experimental_source_flags.values()) else "PASS",
            "message": "Experimental lower-arm/shock/carrier source contradicts the approved double-wishbone and ball-joint contract.",
        },
        {
            "id": "neutral-assembly-collision",
            "status": "FAIL" if any(value > 1e-6 for value in collisions.values()) else "PASS",
            "message": "Every measured v1 suspension part has non-zero Boolean common with the chassis.",
        },
        {
            "id": "printed-interface-clearance",
            "status": "FAIL"
            if min(tang_clearance_per_side_mm, flange_clearance_per_side_mm)
            < required_clearance_per_side_mm
            else "PASS",
            "message": "Rejected v2 tang/flange proposals provide 0.20 mm/side, below the approved 0.25 mm/side contract.",
        },
        {
            "id": "pivot-ligament",
            "status": "FAIL" if 8.0 < pivot_center_min_above_base_mm else "PASS",
            "message": "A 3.2 mm bore with 5.0 mm ligament above the base requires pivot z >= 10.85 mm; the rejected proposal uses z=8.0 mm.",
        },
        {
            "id": "purchased-component-authority",
            "status": "REVIEW_REQUIRED",
            "message": "Exact motor, wheel, bearing/shaft, ball-joint, CVD and shock identities or measurements are absent.",
        },
    ]

    result = {
        "schema_version": "1.0",
        "tool": "validate_corner_stack.py",
        "tool_version": "1.0.0",
        "project_id": "MM-TOY-002",
        "project_revision": "0.4.0",
        "profile": "draft-integration-review",
        "run_date": date.today().isoformat(),
        "status": "FAIL",
        "decision": "BLOCKED",
        "checks": checks,
        "metrics": {
            "baseline_collision_common_volume_mm3": collisions,
            "provisional_motor_proxy_chassis_common_volume_mm3": motor_proxy_common,
            "rejected_pivot_plate_tire_proxy_common_volume_mm3": tire_proxy_common,
            "interface_clearance_mm_per_side": {
                "required": required_clearance_per_side_mm,
                "tang": tang_clearance_per_side_mm,
                "arm_plate_between_carrier_flanges": flange_clearance_per_side_mm,
            },
            "pivot_ligament": {
                "bore_diameter_mm": pivot_bore_diameter_mm,
                "required_ligament_mm": required_ligament_mm,
                "required_local_section_diameter_mm": required_local_section_diameter_mm,
                "rejected_pivot_z_mm": 8.0,
                "minimum_pivot_z_above_base_mm": pivot_center_min_above_base_mm,
            },
            "rejected_trailing_arm_kinematics": poses,
        },
        "approved_contract": approved_contract,
        "experimental_source_flags": experimental_source_flags,
        "inputs": [input_record(path) for path in paths.values()],
        "limitations": [
            "The audit rejects an experimental architecture; it does not validate a replacement design.",
            "Wheel and motor solids are conservative envelopes, not supplier-authoritative geometry.",
            "No exact steering, suspension, driveshaft, shock, fastener-tool or diagonal-articulation sweep exists.",
            "No exact machine/process/filament profiles or slicer run exist.",
            "No physical strength, fatigue, fit, control or safety evidence exists.",
        ],
        "recommended_next_contract": {
            "suspension": "approved upper and lower wishbones with purchased ball joints/kingpin; shock is damping/spring element only",
            "drivetrain": "one chassis-fixed motor module per axle with locked output/spool and two purchased articulated half-shafts",
            "manufacturing_boundary": "keep every purchased interface provisional until exact selected parts are measured",
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": result["decision"], "output": str(output)}, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
