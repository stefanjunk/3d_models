"""Deterministic V0/V1 validation for MM-TOY-003 parametric.1 geometry."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import parameters as P
from build_rover import cots_parts, printed_parts

OUT = ROOT / "validation" / f"v{P.CANDIDATE}" / "geometry-validation.json"


def file_record(path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }


def bounds_union(shapes: list[cq.Shape]) -> tuple[float, float, float, float, float, float]:
    boxes = [shape.BoundingBox() for shape in shapes]
    return (
        min(bb.xmin for bb in boxes), max(bb.xmax for bb in boxes),
        min(bb.ymin for bb in boxes), max(bb.ymax for bb in boxes),
        min(bb.zmin for bb in boxes), max(bb.zmax for bb in boxes),
    )


def mass_properties() -> dict[str, object]:
    printed = printed_parts()
    entries: list[dict[str, float | str]] = []
    for part in printed.values():
        mass = part.shape.Volume() * P.PETG_DENSITY_G_PER_MM3
        centre = cq.Shape.centerOfMass(part.shape)
        entries.append({"name": part.name, "group": part.group, "mass_g": mass, "x_mm": centre.x, "y_mm": centre.y, "z_mm": centre.z, "basis": "solid PETG B-Rep proxy"})

    proxy_positions = {
        "motor_left": (0.0, 47.5, 0.0), "motor_right": (0.0, -47.5, 0.0),
        "brackets_pair": (0.0, 0.0, -10.0),
        "wheel_hub_left": (0.0, P.WHEEL_CENTER_Y_MM, 0.0), "wheel_hub_right": (0.0, -P.WHEEL_CENTER_Y_MM, 0.0),
        "battery_power_set": P.BATTERY_CENTER_MM,
        "control_stack": (0.0, 0.0, 140.0),
        "camera_vtx_rx": (45.0, 0.0, 140.0),
        "antennas": (0.0, 0.0, 186.0),
        "hardware": (0.0, 0.0, 70.0),
    }
    for name, mass in P.COTS_MASS_G.items():
        x, y, z = proxy_positions[name]
        entries.append({"name": name, "group": "COTS_PROXY", "mass_g": mass, "x_mm": x, "y_mm": y, "z_mm": z, "basis": "provisional purchased-part mass ledger"})

    total = sum(float(row["mass_g"]) for row in entries)
    com = [sum(float(row["mass_g"]) * float(row[axis]) for row in entries) / total for axis in ("x_mm", "y_mm", "z_mm")]
    axle_fixed_names = {"motor_left", "motor_right", "brackets_pair", "wheel_hub_left", "wheel_hub_right"}
    balance_body = [row for row in entries if row["name"] not in axle_fixed_names]
    body_total = sum(float(row["mass_g"]) for row in balance_body)
    body_com = [sum(float(row["mass_g"]) * float(row[axis]) for row in balance_body) / body_total for axis in ("x_mm", "y_mm", "z_mm")]
    return {
        "entries": entries,
        "total_mass_g": total,
        "center_of_mass_mm": com,
        "balance_body_excludes": sorted(axle_fixed_names),
        "balance_body_mass_g": body_total,
        "balance_body_center_of_mass_mm": body_com,
    }


def check(check_id: str, condition: bool, message: str, metrics: dict[str, object]) -> dict[str, object]:
    return {"id": check_id, "required": True, "status": "PASS" if condition else "FAIL", "message": message, "metrics": metrics}


def main() -> int:
    printed = printed_parts()
    cots = cots_parts()
    checks: list[dict[str, object]] = []

    invalid = [name for name, part in printed.items() if part.shape.isNull() or not part.shape.isValid() or part.shape.Volume() <= 0]
    checks.append(check("printed-solids", not invalid, "All printed B-Reps must be valid with positive volume", {"invalid": invalid, "count": len(printed)}))

    expected_chassis = [part for part in printed.values() if part.group == "CHASSIS_SET"]
    checks.append(check("chassis-part-count", len(expected_chassis) == 5, "Approved chassis set contains two side frames and three crossmembers", {"count": len(expected_chassis)}))

    wheels = [part for part in cots.values() if part.group == "HUB_WHEEL_SET"]
    wheel_centres = [
        (cq.Shape.centerOfMass(part.shape).x, cq.Shape.centerOfMass(part.shape).z)
        for part in wheels
    ]
    checks.append(check("two-wheels-one-axis", len(wheels) == 2 and all(abs(x) < 1e-6 and abs(z) < 1e-6 for x, z in wheel_centres), "Exactly two wheel proxies share the project Y axis", {"wheel_count": len(wheels), "xz_centres_mm": wheel_centres}))

    all_shapes = [part.shape for part in [*printed.values(), *cots.values()]]
    xmin, xmax, ymin, ymax, zmin, zmax = bounds_union(all_shapes)
    envelope = {"length_x_mm": xmax - xmin, "width_y_mm": ymax - ymin, "height_ground_to_top_mm": zmax - P.GROUND_Z_MM, "min_mm": [xmin, ymin, min(zmin, P.GROUND_Z_MM)], "max_mm": [xmax, ymax, zmax]}
    envelope_ok = envelope["length_x_mm"] <= P.OVERALL_LENGTH_MAX_MM + 1e-6 and envelope["width_y_mm"] <= P.OVERALL_WIDTH_MAX_MM + 1e-6 and envelope["height_ground_to_top_mm"] <= P.UPRIGHT_HEIGHT_MAX_MM + 1e-6
    checks.append(check("master-envelope", envelope_ok, "Assembly proxy remains inside the approved upright envelope", envelope))

    oversized = {}
    for name, part in printed.items():
        bb = part.shape.BoundingBox()
        dims = sorted((bb.xlen, bb.ylen, bb.zlen))
        if any(dim > limit + 1e-6 for dim, limit in zip(dims, sorted((220.0, 220.0, 250.0)))):
            oversized[name] = dims
    checks.append(check("individual-bed-fit", not oversized, "Every printed part can be oriented inside 220 x 220 x 250 mm", {"oversized": oversized}))

    checks.append(check("wheel-body-gap", P.WHEEL_BODY_GAP_MM >= 5.0, "Nominal wheel-to-side-frame axial gap is at least 5 mm", {"gap_mm": P.WHEEL_BODY_GAP_MM}))

    contact = P.LANDING_CONTACT_ANGLE_DEG
    normal_clearance_z = P.LANDING_BOTTOM_Z_MM * math.cos(math.radians(P.NORMAL_PITCH_LIMIT_DEG)) - P.LANDING_TIP_X_MM * math.sin(math.radians(P.NORMAL_PITCH_LIMIT_DEG)) - P.GROUND_Z_MM
    checks.append(check("landing-contact-angle", contact >= P.LANDING_CONTACT_TILT_MIN_DEG and normal_clearance_z > 0, "Landing corner remains clear through normal pitch and contacts no earlier than 22 degrees", {"first_contact_deg": contact, "clearance_at_12deg_mm": normal_clearance_z}))

    mass = mass_properties()
    com = mass["center_of_mass_mm"]
    mass_ok = mass["total_mass_g"] <= 2200.0 and 70.0 <= com[2] <= 110.0 and abs(com[1]) <= 3.0 and abs(com[0]) <= P.BATTERY_TRIM_MM
    checks.append(check("proxy-mass-properties", mass_ok, "Provisional mass ledger must meet approved mass and COM limits before exact-part intake", {"total_mass_g": mass["total_mass_g"], "center_of_mass_mm": com, "limits": {"mass_max_g": 2200, "com_z_mm": [70, 110], "abs_com_y_max_mm": 3, "abs_com_x_max_mm": P.BATTERY_TRIM_MM}}))

    body_com = mass["balance_body_center_of_mass_mm"]
    body_com_ok = 70.0 <= body_com[2] <= 110.0 and abs(body_com[1]) <= 3.0 and abs(body_com[0]) <= P.BATTERY_TRIM_MM
    checks.append({"id": "balance-body-com-diagnostic", "required": False, "status": "PASS" if body_com_ok else "FAIL", "message": "Diagnostic inverted-pendulum body COM excluding axle-fixed wheels, hubs, motors and brackets", "metrics": {"body_mass_g": mass["balance_body_mass_g"], "center_of_mass_mm": body_com, "excluded": mass["balance_body_excludes"]}})

    left = printed["side-frame-left"].shape
    right = printed["side-frame-right"].shape.mirror("XZ")
    volume_delta = abs(left.Volume() - right.Volume())
    checks.append(check("side-frame-symmetry", volume_delta < 1e-3, "Left/right side-frame solids are mirrored volume equivalents", {"volume_delta_mm3": volume_delta}))

    source_paths = [HERE / "parameters.py", HERE / "build_rover.py", HERE / "validate_geometry.py"]
    report = {
        "schema_version": "1.0",
        "tool": "MM-TOY-003 geometry validator",
        "tool_version": "0.1.0",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "inputs": [file_record(path) for path in source_paths],
        "checks": checks,
        "mass_properties": mass,
        "limitations": [
            "COTS dimensions and masses are provisional proxies.",
            "B-Rep validity and envelope checks do not qualify printed strength, fit, control safety or service life.",
            "Landing contact uses the declared planar controlling corner; physical tire compression and floor compliance remain unmodeled."
        ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": {row["id"]: row["status"] for row in checks}}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
