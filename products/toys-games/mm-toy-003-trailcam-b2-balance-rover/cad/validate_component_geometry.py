"""Deterministic V0/V1 checks for MM-TOY-003 0.1.0-parametric.3."""

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
import component_parameters as P
from build_component_rover import cots_parts, orient_mesh_for_print, printed_parts

OUT = ROOT / "validation" / f"v{P.CANDIDATE}" / "geometry-validation.json"


def file_record(path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }


def check(
    check_id: str,
    condition: bool,
    message: str,
    metrics: dict[str, object],
    required: bool = True,
) -> dict[str, object]:
    return {
        "id": check_id,
        "required": required,
        "status": "PASS" if condition else "FAIL",
        "message": message,
        "metrics": metrics,
    }


def review(check_id: str, message: str, metrics: dict[str, object]) -> dict[str, object]:
    return {
        "id": check_id,
        "required": False,
        "status": "REVIEW_REQUIRED",
        "message": message,
        "metrics": metrics,
    }


def union_bounds(shapes: list[cq.Shape]) -> tuple[float, float, float, float, float, float]:
    bounds = [shape.BoundingBox() for shape in shapes]
    return (
        min(bb.xmin for bb in bounds),
        max(bb.xmax for bb in bounds),
        min(bb.ymin for bb in bounds),
        max(bb.ymax for bb in bounds),
        min(bb.zmin for bb in bounds),
        max(bb.zmax for bb in bounds),
    )


def mass_properties(printed: dict, include_ballast: bool = True) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for part in printed.values():
        mass = part.shape.Volume() * P.PETG_DENSITY_G_PER_MM3
        centre = cq.Shape.centerOfMass(part.shape)
        entries.append(
            {
                "name": part.name,
                "group": part.group,
                "mass_g": mass,
                "x_mm": centre.x,
                "y_mm": centre.y,
                "z_mm": centre.z,
                "basis": "conservative solid-density PETG B-Rep",
            }
        )
    for name, (mass, x, y, z) in P.COTS_MASS_POSITION.items():
        if name == "upper_trim_ballast" and not include_ballast:
            continue
        entries.append(
            {
                "name": name,
                "group": "BOM_0.1.0-bom.1",
                "mass_g": mass,
                "x_mm": x,
                "y_mm": y,
                "z_mm": z,
                "basis": "BOM installed-mass estimate at component registration proxy",
            }
        )
    total = sum(float(row["mass_g"]) for row in entries)
    com = [
        sum(float(row["mass_g"]) * float(row[key]) for row in entries) / total
        for key in ("x_mm", "y_mm", "z_mm")
    ]
    printed_mass = sum(
        float(row["mass_g"])
        for row in entries
        if row["basis"] == "conservative solid-density PETG B-Rep"
    )
    return {
        "entries": entries,
        "total_mass_g": total,
        "printed_solid_density_mass_g": printed_mass,
        "center_of_mass_mm": com,
        "ballast_included_g": P.BALLAST_INSTALLED_ESTIMATE_G if include_ballast else 0.0,
    }


def main() -> int:
    printed = printed_parts()
    cots = cots_parts()
    checks: list[dict[str, object]] = []

    invalid = [
        name
        for name, part in printed.items()
        if part.shape.isNull()
        or not part.shape.isValid()
        or part.shape.Volume() <= 0
        or len(part.shape.Solids()) != 1
    ]
    checks.append(
        check(
            "printed-brep-solids",
            not invalid and len(printed) == 19,
            "All 19 printed parts must be one valid positive-volume solid",
            {"count": len(printed), "invalid_or_multisolid": invalid},
        )
    )

    left = printed["side-frame-left"].shape
    right_mirrored = printed["side-frame-right"].shape.mirror("XZ")
    checks.append(
        check(
            "side-frame-symmetry",
            abs(left.Volume() - right_mirrored.Volume()) < 1e-3,
            "Left and right frame volumes must be mirrored equivalents",
            {"volume_delta_mm3": abs(left.Volume() - right_mirrored.Volume())},
        )
    )

    all_shapes = [part.shape for part in [*printed.values(), *cots.values()]]
    xmin, xmax, ymin, ymax, zmin, zmax = union_bounds(all_shapes)
    envelope = {
        "length_x_mm": xmax - xmin,
        "width_y_mm": ymax - ymin,
        "height_ground_to_top_mm": zmax - P.GROUND_Z_MM,
        "min_mm": [xmin, ymin, min(zmin, P.GROUND_Z_MM)],
        "max_mm": [xmax, ymax, zmax],
    }
    envelope_ok = (
        envelope["length_x_mm"] <= P.OVERALL_LENGTH_MAX_MM + 1e-5
        and envelope["width_y_mm"] <= P.OVERALL_WIDTH_MAX_MM + 1e-5
        and envelope["height_ground_to_top_mm"] <= P.UPRIGHT_HEIGHT_MAX_MM + 1e-5
    )
    checks.append(
        check(
            "assembly-envelope",
            envelope_ok,
            "Registered assembly must remain within 190 x 260 x 250 mm",
            envelope,
        )
    )

    oversized: dict[str, list[float]] = {}
    for name, part in printed.items():
        bb = orient_mesh_for_print(part).BoundingBox()
        dims = (bb.xlen, bb.ylen, bb.zlen)
        if any(value > limit + 1e-5 for value, limit in zip(dims, P.PRINT_BED_MM)):
            oversized[name] = list(dims)
    checks.append(
        check(
            "individual-print-bed-fit",
            not oversized,
            "Every documented print orientation must fit 220 x 220 x 250 mm",
            {"oversized": oversized, "bed_mm": P.PRINT_BED_MM},
        )
    )

    wheels = [part for part in cots.values() if part.group == "WHEEL"]
    wheel_centres = [cq.Shape.centerOfMass(part.shape) for part in wheels]
    one_axis = (
        len(wheels) == 2
        and all(abs(c.x) < 1e-6 and abs(c.z) < 1e-6 for c in wheel_centres)
        and abs(abs(wheel_centres[0].y - wheel_centres[1].y) - P.WHEEL_TRACK_MM) < 1e-6
    )
    checks.append(
        check(
            "two-wheels-one-axis",
            one_axis,
            "Exactly two wheel envelopes share one common geometric axis",
            {
                "wheel_count": len(wheels),
                "centres_mm": [[c.x, c.y, c.z] for c in wheel_centres],
                "track_mm": P.WHEEL_TRACK_MM,
            },
        )
    )

    printed_compound = cq.Compound.makeCompound([part.shape for part in printed.values()])
    wheel_clearances = {
        name: part.shape.distance(printed_compound)
        for name, part in cots.items()
        if part.group == "WHEEL"
    }
    checks.append(
        check(
            "wheel-to-printed-clearance",
            min(wheel_clearances.values()) >= 5.0 - 1e-5,
            "The conservative 120 x 42 mm tire envelopes retain at least 5 mm to printed parts",
            {"clearance_mm": wheel_clearances, "required_mm": 5.0},
        )
    )

    motor_overlap = cots["motor-left-proxy"].shape.intersect(cots["motor-right-proxy"].shape).Volume()
    checks.append(
        check(
            "motor-body-central-gap",
            motor_overlap < 1e-6 and P.MOTOR_BODY_INNER_Y_MM_PROVISIONAL >= 10.0,
            "The two 73 mm motor proxies must not overlap at the centre plane",
            {
                "overlap_mm3": motor_overlap,
                "each_inner_end_from_centre_mm": P.MOTOR_BODY_INNER_Y_MM_PROVISIONAL,
            },
        )
    )

    battery_gap = {
        "x_each_side_mm": (P.BATTERY_INNER_MM[0] - P.BATTERY_SIZE_MM_PROVISIONAL[0]) / 2.0,
        "y_each_side_mm": (P.BATTERY_INNER_MM[1] - P.BATTERY_SIZE_MM_PROVISIONAL[1]) / 2.0,
        "floor_gap_mm": P.BATTERY_CLEARANCE_PER_SIDE_MM,
    }
    battery_intersection = cots["battery-proxy"].shape.intersect(printed["battery-cradle"].shape).Volume()
    checks.append(
        check(
            "battery-cradle-envelope",
            min(battery_gap.values()) >= 1.0 - 1e-6 and battery_intersection < 1e-5,
            "The 153 x 44 x 25 mm battery proxy must retain 1 mm nominal cradle clearance",
            {**battery_gap, "unexpected_intersection_mm3": battery_intersection},
        )
    )

    trim_each_side = (P.BATTERY_MOUNT_SLOT_LENGTH_MM - P.M3_CLEARANCE_MM) / 2.0
    checks.append(
        check(
            "battery-longitudinal-trim",
            trim_each_side >= P.BATTERY_TRIM_MM,
            "Cradle slots retain at least +/-12 mm longitudinal adjustment",
            {
                "available_each_side_mm": trim_each_side,
                "required_each_side_mm": P.BATTERY_TRIM_MM,
            },
        )
    )

    camera_intersection = cots["camera-proxy"].shape.intersect(printed["camera-guard"].shape).Volume()
    camera_distance = cots["camera-proxy"].shape.distance(printed["camera-guard"].shape)
    checks.append(
        check(
            "camera-guard-clearance",
            camera_intersection < 1e-5 and camera_distance >= 0.8,
            "RunCam body/lens proxy must remain clear of the protective guard",
            {"intersection_mm3": camera_intersection, "minimum_distance_mm": camera_distance},
        )
    )

    checks.append(
        check(
            "electronics-footprint-contract",
            abs(P.TX800_HOLE_PITCH_MM - 20.0) < 1e-9
            and abs(P.DRIVER_HOLE_DELTA_MM[0] - 7.62) < 1e-9
            and abs(P.DRIVER_HOLE_DELTA_MM[1] - 43.18) < 1e-9,
            "Protected VTX and motor-driver mounting relations match manufacturer declarations",
            {
                "tx800_hole_pitch_mm": P.TX800_HOLE_PITCH_MM,
                "driver_hole_delta_mm": P.DRIVER_HOLE_DELTA_MM,
                "driver_slots_allow_x_registration_mm": 4.0,
            },
        )
    )

    contact = P.LANDING_CONTACT_ANGLE_DEG
    angle = math.radians(P.NORMAL_PITCH_LIMIT_DEG)
    normal_clearance = (
        P.LANDING_BOTTOM_Z_MM * math.cos(angle)
        - P.LANDING_TIP_X_MM * math.sin(angle)
        - P.GROUND_Z_MM
    )
    checks.append(
        check(
            "landing-contact-angle",
            contact >= P.LANDING_CONTACT_TILT_MIN_DEG and normal_clearance > 0,
            "Landing geometry stays clear through normal pitch and contacts no earlier than 22 degrees",
            {
                "first_contact_deg": contact,
                "clearance_at_12deg_mm": normal_clearance,
            },
        )
    )

    mass = mass_properties(printed, include_ballast=True)
    mass_without_trim = mass_properties(printed, include_ballast=False)
    com = mass["center_of_mass_mm"]
    mass_ok = (
        mass["total_mass_g"] <= 2200.0
        and 70.0 <= com[2] <= 110.0
        and abs(com[1]) <= 3.0
        and abs(com[0]) <= P.BATTERY_TRIM_MM
    )
    checks.append(
        check(
            "bom-mass-properties",
            mass_ok,
            "Conservative solid-PETG plus BOM ledger must satisfy the complete-rover mass/COM gate",
            {
                "total_mass_g": mass["total_mass_g"],
                "center_of_mass_mm": com,
                "printed_solid_density_mass_g": mass["printed_solid_density_mass_g"],
                "calculation_ballast_g": P.BALLAST_INSTALLED_ESTIMATE_G,
                "limits": {
                    "mass_max_g": 2200.0,
                    "com_z_mm": [70.0, 110.0],
                    "abs_com_y_max_mm": 3.0,
                    "abs_com_x_max_mm": P.BATTERY_TRIM_MM,
                },
            },
        )
    )

    checks.append(
        review(
            "delivered-part-intake",
            "Manufacturer-derived fits remain DRAFT until exact samples and process coupons pass",
            {
                "required_samples": [
                    "Pololu 4755 + 1995 + 2686 motor stack",
                    "INJORA CRAW18003 + CRAW20161023 assembled wheel",
                    "Gens ace GEA503S60X6GT battery including leads",
                    "Pololu 2507 board and installed terminals",
                    "Adafruit 4502 carrier revision",
                    "AMASS XT60E-M and Littelfuse 178.6152.0001",
                    "RunCam Phoenix 2 SE V2 and SpeedyBee TX800",
                ],
                "mass_without_trim": mass_without_trim,
                "cassette_capacity_g": P.BALLAST_CASSETTE_DESIGN_CAPACITY_G,
            },
        )
    )

    source_paths = [HERE / "component_parameters.py", HERE / "build_component_rover.py", HERE / "validate_component_geometry.py"]
    required = [item for item in checks if item["required"]]
    report = {
        "schema_version": "1.0",
        "tool": "MM-TOY-003 component geometry validator",
        "tool_version": "0.1.0",
        "project_id": P.PROJECT_ID,
        "candidate": P.CANDIDATE,
        "status": "PASS" if all(item["status"] == "PASS" for item in required) else "FAIL",
        "inputs": [file_record(path) for path in source_paths],
        "checks": checks,
        "mass_properties": mass,
        "mass_properties_without_trim": mass_without_trim,
        "limitations": [
            "Digital B-Rep and proxy checks do not qualify printed strength, component fit, electrical safety, dynamic balance or service life.",
            "Solid-density PETG is conservative for CAD mass comparison and is not an exact slicer/material prediction.",
            "The 100 g ballast value is a calculation point, not an instruction; the complete rover must be weighed and its COM measured before loading the cassette.",
            "The 260 mm width is consumed by the declared 218 mm track plus two 42 mm tire widths and therefore has no unmeasured envelope margin.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "checks": {item["id"]: item["status"] for item in checks},
                "mass_g": mass["total_mass_g"],
                "com_mm": mass["center_of_mass_mm"],
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
