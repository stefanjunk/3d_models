#!/usr/bin/env python3
"""Fail-closed validation for the MM-TOY-002 v2 pivot-host coupons."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import cadquery as cq
import double_wishbone_v2_kinematics as kin
import double_wishbone_v2_pivot_host_coupon as coupon
import parameters as p
import trimesh

SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
EXPORT_DIR = SCRIPT.parent / "exports" / "v0.4.0-draft.3-pivot-host-coupon"
TOLERANCE_MM3 = 1e-5
TOLERANCE_MM = 1e-5


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


def resolve_manifest_path(raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else PROJECT / path


def common_volume(first: cq.Shape, second: cq.Shape) -> float:
    return float(first.intersect(second).Volume())


def shape_bounds(shape: cq.Shape) -> dict[str, list[float]]:
    bounds = shape.BoundingBox()
    return {
        "minimum_mm": [bounds.xmin, bounds.ymin, bounds.zmin],
        "maximum_mm": [bounds.xmax, bounds.ymax, bounds.zmax],
        "size_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
    }


def maximum_vector_delta(first: list[float], second: list[float]) -> float:
    return max(abs(a - b) for a, b in zip(first, second, strict=True))


def cylinder_between(
    start: kin.Vec3,
    end: kin.Vec3,
    radius: float,
    *,
    start_trim: float = 0.0,
) -> cq.Shape:
    direction = kin.v_sub(end, start)
    length = kin.v_length(direction)
    if length <= start_trim + 1e-9:
        raise ValueError("trim removes complete proxy segment")
    unit = kin.v_scale(direction, 1.0 / length)
    trimmed_start = kin.v_add(start, kin.v_scale(unit, start_trim))
    return cq.Solid.makeCylinder(
        radius,
        length - start_trim,
        pnt=trimmed_start,
        dir=unit,
    )


def tire_envelope(pose: kin.CornerPose, radius: float) -> cq.Shape:
    half_width = p.TIRE_WIDTH_MM / 2.0
    start = kin.v_add(
        pose.wheel_center,
        kin.v_scale(pose.wheel_axis, -half_width),
    )
    return cq.Solid.makeCylinder(
        radius,
        p.TIRE_WIDTH_MM,
        pnt=start,
        dir=pose.wheel_axis,
    )


def check_manifest(manifest_path: Path, export_dir: Path) -> tuple[bool, list[str]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for group in ("inputs", "outputs"):
        for item in manifest[group]:
            path = resolve_manifest_path(item["path"])
            if not path.is_file():
                errors.append(f"missing {group[:-1]} {item['path']}")
                continue
            if path.stat().st_size != item["size_bytes"]:
                errors.append(f"size mismatch {item['path']}")
            if sha256(path) != item["sha256"]:
                errors.append(f"hash mismatch {item['path']}")
    if manifest.get("candidate") != "0.4.0-draft.3":
        errors.append("unexpected manifest candidate")
    if manifest.get("vehicle_part_claim") is not False:
        errors.append("manifest must deny a vehicle-part claim")
    if manifest.get("slicer") != "NOT_RUN_NO_COMPLETE_PROFILE_SET":
        errors.append("manifest must preserve the fail-closed slicer disposition")
    expected_names = {
        "DRAFT-dwv2-front-pivot-host-coupon.step",
        "DRAFT-dwv2-front-pivot-host-coupon.stl",
        "DRAFT-dwv2-rear-pivot-host-coupon.step",
        "DRAFT-dwv2-rear-pivot-host-coupon.stl",
        "DRAFT-dwv2-pivot-host-coupons-preview.png",
        "manifest.json",
    }
    actual_names = {path.name for path in export_dir.iterdir() if path.is_file()}
    if actual_names != expected_names:
        errors.append(
            f"artifact set mismatch: expected={sorted(expected_names)}, "
            f"actual={sorted(actual_names)}"
        )
    return not errors, errors


def mesh_record(
    path: Path, source_shape: cq.Shape, step_shape: cq.Shape
) -> dict[str, Any]:
    loaded = trimesh.load_mesh(path, process=True)
    if not isinstance(loaded, trimesh.Trimesh):
        raise TypeError(f"expected one Trimesh in {path}")
    mesh_bounds = {
        "minimum_mm": loaded.bounds[0].tolist(),
        "maximum_mm": loaded.bounds[1].tolist(),
        "size_mm": (loaded.bounds[1] - loaded.bounds[0]).tolist(),
    }
    source_record = shape_bounds(source_shape)
    step_record = shape_bounds(step_shape)
    bodies = loaded.split(only_watertight=False)
    source_volume = float(source_shape.Volume())
    step_volume = float(step_shape.Volume())
    mesh_volume = float(abs(loaded.volume))
    try:
        recorded_path = path.relative_to(PROJECT)
    except ValueError:
        recorded_path = path
    return {
        "path": str(recorded_path),
        "watertight": bool(loaded.is_watertight),
        "winding_consistent": bool(loaded.is_winding_consistent),
        "body_count": len(bodies),
        "vertex_count": len(loaded.vertices),
        "face_count": len(loaded.faces),
        "source_brep_valid": source_shape.isValid(),
        "source_brep_solid_count": len(source_shape.Solids()),
        "step_brep_valid": step_shape.isValid(),
        "step_brep_solid_count": len(step_shape.Solids()),
        "source_volume_mm3": source_volume,
        "step_volume_mm3": step_volume,
        "mesh_volume_mm3": mesh_volume,
        "step_source_relative_volume_error": abs(step_volume - source_volume)
        / source_volume,
        "mesh_source_relative_volume_error": abs(mesh_volume - source_volume)
        / source_volume,
        "source_bounds": source_record,
        "step_bounds": step_record,
        "mesh_bounds": mesh_bounds,
        "step_source_maximum_bound_delta_mm": max(
            maximum_vector_delta(
                step_record[key],
                source_record[key],
            )
            for key in ("minimum_mm", "maximum_mm", "size_mm")
        ),
        "mesh_source_maximum_bound_delta_mm": max(
            maximum_vector_delta(
                mesh_bounds[key],
                source_record[key],
            )
            for key in ("minimum_mm", "maximum_mm", "size_mm")
        ),
    }


def eye_clearance_record(variant: coupon.Variant, host: cq.Shape) -> dict[str, Any]:
    lower_y = p.DWV2_LOWER_INBOARD_Y_MM - p.FRAME_RAIL_Y_MM
    upper_y = p.DWV2_UPPER_INBOARD_Y_MM - p.FRAME_RAIL_Y_MM
    locations = [
        *(
            ("lower", x, lower_y, p.DWV2_LOWER_INBOARD_Z_MM)
            for x in coupon.lower_eye_centers_x()
        ),
        *(
            ("upper", x, upper_y, p.DWV2_UPPER_INBOARD_Z_MM)
            for x in coupon.variant_upper_eye_centers_x(variant)
        ),
    ]
    details: list[dict[str, Any]] = []
    for level, center_x, axis_y, axis_z in locations:
        proxy = coupon.cylinder_x(
            center_x - p.DWV2_HOST_ARM_EYE_WIDTH_MM / 2.0,
            p.DWV2_HOST_ARM_EYE_WIDTH_MM,
            axis_y,
            axis_z,
            p.DWV2_HOST_ARM_EYE_DIAMETER_MM / 2.0,
        )
        details.append(
            {
                "level": level,
                "center_x_mm": center_x,
                "intersection_mm3": common_volume(host, proxy),
            }
        )
    unrelieved_rail = coupon.hollow_rail()
    unrelieved_lower = []
    for center_x in coupon.lower_eye_centers_x():
        proxy = coupon.cylinder_x(
            center_x - p.DWV2_HOST_ARM_EYE_WIDTH_MM / 2.0,
            p.DWV2_HOST_ARM_EYE_WIDTH_MM,
            lower_y,
            p.DWV2_LOWER_INBOARD_Z_MM,
            p.DWV2_HOST_ARM_EYE_DIAMETER_MM / 2.0,
        )
        unrelieved_lower.append(common_volume(unrelieved_rail, proxy))
    return {
        "final_eye_intersections": details,
        "maximum_final_eye_intersection_mm3": max(
            item["intersection_mm3"] for item in details
        ),
        "unrelieved_lower_eye_intersections_mm3": unrelieved_lower,
        "minimum_unrelieved_lower_eye_intersection_mm3": min(unrelieved_lower),
    }


def attachment_record(variant: coupon.Variant) -> dict[str, Any]:
    rail = coupon.hollow_rail()
    lower_y = p.DWV2_LOWER_INBOARD_Y_MM - p.FRAME_RAIL_Y_MM
    lower_intersections: list[float] = []
    for center_x in coupon.lower_eye_centers_x():
        for x_start, x_end in coupon.clevis_intervals(
            center_x,
            p.DWV2_HOST_CLEVIS_GAP_MM,
            p.DWV2_HOST_LUG_THICKNESS_MM,
        ):
            boss = coupon.cylinder_x(
                x_start,
                x_end - x_start,
                lower_y,
                p.DWV2_LOWER_INBOARD_Z_MM,
                p.DWV2_HOST_PIVOT_BOSS_DIAMETER_MM / 2.0,
            )
            lower_intersections.append(common_volume(rail, boss))

    upper_intersections: list[float] = []
    for center_x in coupon.variant_upper_eye_centers_x(variant):
        for x_start, x_end in coupon.clevis_intervals(
            center_x,
            p.DWV2_HOST_CLEVIS_GAP_MM,
            p.DWV2_HOST_LUG_THICKNESS_MM,
        ):
            web = coupon.yz_prism(
                x_start,
                x_end - x_start,
                coupon.upper_tower_points(),
            )
            upper_intersections.append(common_volume(rail, web))
    return {
        "lower_boss_to_rail_intersections_mm3": lower_intersections,
        "minimum_lower_boss_to_rail_intersection_mm3": min(lower_intersections),
        "upper_web_to_rail_intersections_mm3": upper_intersections,
        "minimum_upper_web_to_rail_intersection_mm3": min(upper_intersections),
    }


def tire_sweep_record(variant: coupon.Variant, host: cq.Shape) -> dict[str, Any]:
    global_host = host.translate((kin.axle_x(variant), p.FRAME_RAIL_Y_MM, 0.0))
    travel_values = kin.axis_range(
        p.DWV2_TRAVEL_MIN_MM,
        p.DWV2_TRAVEL_MAX_MM,
        p.DWV2_TRAVEL_STEP_MM,
    )
    steer_values = (
        kin.axis_range(
            p.DWV2_STEER_MIN_DEG,
            p.DWV2_STEER_MAX_DEG,
            p.DWV2_STEER_STEP_DEG,
        )
        if variant == "front"
        else [0.0]
    )
    radius_records: dict[str, Any] = {}
    total_samples = 0
    for radius in (p.TIRE_DIAMETER_MM / 2.0, p.TIRE_DIAMETER_MAX_MM / 2.0):
        maximum = 0.0
        worst_pose: dict[str, float] | None = None
        for travel in travel_values:
            for steer in steer_values:
                pose = kin.corner_pose(variant, 1, travel, steer)
                overlap = common_volume(global_host, tire_envelope(pose, radius))
                total_samples += 1
                if overlap > maximum:
                    maximum = overlap
                    worst_pose = {"travel_mm": travel, "steer_deg": steer}
        radius_records[f"radius_{radius:g}_mm"] = {
            "maximum_intersection_mm3": maximum,
            "worst_pose": worst_pose,
            "sample_count": len(travel_values) * len(steer_values),
        }
    return {"sample_count": total_samples, "radii": radius_records}


def arm_neck_record(variant: coupon.Variant, host: cq.Shape) -> dict[str, Any]:
    global_host = host.translate((kin.axle_x(variant), p.FRAME_RAIL_Y_MM, 0.0))
    travel_values = kin.axis_range(
        p.DWV2_TRAVEL_MIN_MM,
        p.DWV2_TRAVEL_MAX_MM,
        p.DWV2_TRAVEL_STEP_MM,
    )
    records: dict[str, dict[str, Any]] = {}
    for level in ("lower", "upper"):
        maximum = 0.0
        worst: dict[str, float] | None = None
        sample_count = 0
        for travel in travel_values:
            pose = kin.corner_pose(variant, 1, travel, 0.0)
            if level == "lower":
                inboards = (pose.lower_inboard_a, pose.lower_inboard_b)
                outer = pose.lower_outer
            else:
                inboards = (pose.upper_inboard_a, pose.upper_inboard_b)
                outer = pose.upper_outer
            for inboard in inboards:
                proxy = cylinder_between(
                    inboard,
                    outer,
                    p.DWV2_HOST_ARM_BEAM_PROXY_RADIUS_MM,
                    start_trim=p.DWV2_HOST_ARM_EYE_DIAMETER_MM / 2.0,
                )
                overlap = common_volume(global_host, proxy)
                sample_count += 1
                if overlap > maximum:
                    maximum = overlap
                    worst = {
                        "travel_mm": travel,
                        "inboard_x_mm": inboard[0],
                    }
        records[level] = {
            "maximum_intersection_mm3": maximum,
            "worst_case": worst,
            "sample_count": sample_count,
        }
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--export-dir", type=Path, default=EXPORT_DIR)
    args = parser.parse_args()
    output = args.output.resolve()
    export_dir = args.export_dir.resolve()
    if output.exists():
        parser.error(f"refusing to overwrite existing evidence: {output}")

    paths: dict[str, Path] = {
        "validator": SCRIPT,
        "coupon_source": SCRIPT.parent / "double_wishbone_v2_pivot_host_coupon.py",
        "kinematic_source": SCRIPT.parent / "double_wishbone_v2_kinematics.py",
        "parameters": SCRIPT.parent / "parameters.py",
        "design_spec": PROJECT / "design-spec.yaml",
        "interface_contract": PROJECT
        / "architecture"
        / "double-wishbone-v2-interface-contract-v0.4.0.json",
        "kinematic_validation": PROJECT
        / "validation"
        / "double-wishbone-v2-kinematics-2026-08-30.json",
        "front_step": export_dir / "DRAFT-dwv2-front-pivot-host-coupon.step",
        "front_stl": export_dir / "DRAFT-dwv2-front-pivot-host-coupon.stl",
        "rear_step": export_dir / "DRAFT-dwv2-rear-pivot-host-coupon.step",
        "rear_stl": export_dir / "DRAFT-dwv2-rear-pivot-host-coupon.stl",
        "preview": export_dir / "DRAFT-dwv2-pivot-host-coupons-preview.png",
        "manifest": export_dir / "manifest.json",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing validation inputs: " + ", ".join(missing))

    manifest_ok, manifest_errors = check_manifest(paths["manifest"], export_dir)
    variants: dict[coupon.Variant, dict[str, Any]] = {}
    for variant in ("front", "rear"):
        source_shape = coupon.build_pivot_host(variant)
        step_shape = cq.importers.importStep(str(paths[f"{variant}_step"])).val()
        mesh = mesh_record(paths[f"{variant}_stl"], source_shape, step_shape)
        variants[variant] = {
            "geometry": mesh,
            "eye_clearance": eye_clearance_record(variant, source_shape),
            "attachments": attachment_record(variant),
            "tire_sweep": tire_sweep_record(variant, source_shape),
            "straight_arm_neck_proxy": arm_neck_record(variant, source_shape),
        }

    nominal = {
        "m3_radial_clearance_mm": (p.DWV2_HOST_PIVOT_BORE_MM - p.PIVOT_PIN_MM) / 2.0,
        "boss_radial_ligament_mm": (
            p.DWV2_HOST_PIVOT_BOSS_DIAMETER_MM - p.DWV2_HOST_PIVOT_BORE_MM
        )
        / 2.0,
        "eye_axial_clearance_per_side_mm": (
            p.DWV2_HOST_CLEVIS_GAP_MM - p.DWV2_HOST_ARM_EYE_WIDTH_MM
        )
        / 2.0,
        "eye_radial_pocket_clearance_mm": (
            p.DWV2_HOST_EYE_POCKET_DIAMETER_MM - p.DWV2_HOST_ARM_EYE_DIAMETER_MM
        )
        / 2.0,
        "rail_wall_mm": p.DWV2_HOST_RAIL_WALL_MM,
        "lug_thickness_mm": p.DWV2_HOST_LUG_THICKNESS_MM,
    }

    geometry_pass = all(
        data["geometry"]["watertight"]
        and data["geometry"]["winding_consistent"]
        and data["geometry"]["body_count"] == 1
        and data["geometry"]["source_brep_valid"]
        and data["geometry"]["source_brep_solid_count"] == 1
        and data["geometry"]["step_brep_valid"]
        and data["geometry"]["step_brep_solid_count"] == 1
        and data["geometry"]["step_source_relative_volume_error"] <= 1e-9
        and data["geometry"]["mesh_source_relative_volume_error"] <= 1e-3
        and data["geometry"]["step_source_maximum_bound_delta_mm"] <= TOLERANCE_MM
        and data["geometry"]["mesh_source_maximum_bound_delta_mm"] <= 0.06
        for data in variants.values()
    )
    eye_pass = all(
        data["eye_clearance"]["maximum_final_eye_intersection_mm3"] <= TOLERANCE_MM3
        and data["eye_clearance"]["minimum_unrelieved_lower_eye_intersection_mm3"]
        > TOLERANCE_MM3
        for data in variants.values()
    )
    attachments_pass = all(
        data["attachments"]["minimum_lower_boss_to_rail_intersection_mm3"]
        > TOLERANCE_MM3
        and data["attachments"]["minimum_upper_web_to_rail_intersection_mm3"]
        > TOLERANCE_MM3
        for data in variants.values()
    )
    tire_pass = all(
        radius["maximum_intersection_mm3"] <= TOLERANCE_MM3
        for data in variants.values()
        for radius in data["tire_sweep"]["radii"].values()
    )
    nominal_pass = (
        nominal["m3_radial_clearance_mm"] >= p.CLEARANCE_FASTENER_MM
        and nominal["boss_radial_ligament_mm"] >= 5.0
        and nominal["eye_axial_clearance_per_side_mm"] >= p.CLEARANCE_FASTENER_MM
        and nominal["eye_radial_pocket_clearance_mm"] >= p.CLEARANCE_FASTENER_MM
        and nominal["rail_wall_mm"] >= p.WALL_MIN_MM
        and nominal["lug_thickness_mm"] >= p.FATIGUE_MIN_MM
    )
    straight_arm_max = max(
        level["maximum_intersection_mm3"]
        for data in variants.values()
        for level in data["straight_arm_neck_proxy"].values()
    )

    checks = [
        {
            "id": "artifact-integrity",
            "status": "PASS" if manifest_ok else "FAIL",
            "message": "All manifest input/output hashes and the exact artifact set match."
            if manifest_ok
            else f"manifest_errors={manifest_errors}",
        },
        {
            "id": "brep-step-stl-topology",
            "status": "PASS" if geometry_pass else "FAIL",
            "message": "Front and rear source/STEP are one valid solid; both STL files are one watertight, consistently wound body with bounded tessellation error.",
        },
        {
            "id": "nominal-clevis-process-geometry",
            "status": "PASS" if nominal_pass else "FAIL",
            "message": "M3 radial clearance, boss ligament, eye clearances, rail wall and lug thickness meet the current numeric contract.",
        },
        {
            "id": "rail-pocket-and-eye-clearance",
            "status": "PASS" if eye_pass else "FAIL",
            "message": "The unrelieved rail would intersect both lower eyes, while the final four eye pockets per coupon have zero B-Rep overlap.",
        },
        {
            "id": "boss-and-upper-web-attachment",
            "status": "PASS" if attachments_pass else "FAIL",
            "message": "Every lower boss and upper tower web has positive volumetric overlap with the rail; each completed coupon remains one solid.",
        },
        {
            "id": "tire-full-sweep-clearance",
            "status": "PASS" if tire_pass else "FAIL",
            "message": "Full solid tire envelopes at 90 mm nominal and 115 mm maximum diameter have zero overlap across the declared front steering/travel and rear travel sweeps.",
        },
        {
            "id": "straight-arm-neck-routing",
            "status": "PASS"
            if straight_arm_max <= TOLERANCE_MM3
            else "REVIEW_REQUIRED",
            "message": f"Trimmed 6 mm diameter straight arm-neck proxies reach a maximum host overlap of {straight_arm_max:.6f} mm3; final dog-leg/neck geometry is outside this coupon scope.",
        },
        {
            "id": "horizontal-pivot-hole-process",
            "status": "REVIEW_REQUIRED",
            "message": "The x-axis 3.5 mm circular holes are intentional ream-after-print process candidates; bridge quality and final M3 fit require a physical coupon before freezing circular versus teardrop pilot geometry.",
        },
        {
            "id": "shock-host-and-purchased-interfaces",
            "status": "REVIEW_REQUIRED",
            "message": "Shock host, ball joints, CVD plunge/articulation, hub/bearing and wheel backspacing remain excluded pending measured samples and arm-path resolution.",
        },
        {
            "id": "anycubic-exact-slicer",
            "status": "NOT_RUN",
            "message": "The repository has no complete approved machine/process/filament JSON profile set for this coupon; exact Anycubic slicing remains fail-closed.",
        },
        {
            "id": "physical-fit-load-fatigue",
            "status": "NOT_RUN",
            "message": "No printed coupon, reamed bore measurement, proof load, impact or fatigue evidence exists.",
        },
        {
            "id": "watermark",
            "status": "NOT_RUN",
            "message": "No watermark is added to an interface/process coupon; watermark remains the last solid change for a stable product candidate.",
        },
    ]
    scope_failures = [item["id"] for item in checks if item["status"] == "FAIL"]
    result = {
        "schema_version": "1.0",
        "tool": SCRIPT.name,
        "tool_version": "1.0.0",
        "project_id": "MM-TOY-002",
        "project_revision": "0.4.0",
        "candidate": "0.4.0-draft.3",
        "profile": "chassis-pivot-host-interface-process-coupon",
        "run_date": datetime.now(tz=UTC).date().isoformat(),
        "status": "FAIL" if scope_failures else "REVIEW_REQUIRED",
        "decision": "BLOCKED" if scope_failures else "DRAFT_COUPON_ONLY",
        "coupon_scope_status": "FAIL" if scope_failures else "PASS",
        "passed_scope": "front/rear chassis-side longitudinal clevis topology, nominal clearances, artifact topology and tire-envelope clearance",
        "excluded_scope": "wishbone necks, shock mounts, uprights, drivetrain, full chassis integration, slicing and physical qualification",
        "scope_failures": scope_failures,
        "checks": checks,
        "metrics": {
            "nominal_contract": nominal,
            "variants": variants,
            "tire_boolean_sample_count": sum(
                data["tire_sweep"]["sample_count"] for data in variants.values()
            ),
            "arm_neck_boolean_sample_count": sum(
                level["sample_count"]
                for data in variants.values()
                for level in data["straight_arm_neck_proxy"].values()
            ),
            "straight_arm_neck_maximum_intersection_mm3": straight_arm_max,
        },
        "inputs": [input_record(path) for path in paths.values()],
        "limitations": [
            "A collision-free interface coupon does not prove a collision-free arm or complete vehicle.",
            "The solid-cylinder tire test is a conservative keep-out, not a rim-cavity or backspacing model.",
            "No strength, fatigue, layer-adhesion, wear or driving-safety claim is made.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "decision": result["decision"],
                "coupon_scope_status": result["coupon_scope_status"],
                "scope_failures": scope_failures,
                "straight_arm_neck_maximum_intersection_mm3": straight_arm_max,
                "output": str(output),
            },
            indent=2,
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
