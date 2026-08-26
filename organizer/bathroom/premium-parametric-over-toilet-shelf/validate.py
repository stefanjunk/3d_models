#!/usr/bin/env python3
"""Validate exported meshes, bed fit, manifests, and optional image relief."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
import cadquery as cq

from src.over_toilet_shelf import build_model


ROOT = Path(__file__).resolve().parent


def load_mesh(path: Path) -> trimesh.Trimesh:
    # STL repeats vertex coordinates per triangle. Processing merges coincident
    # vertices so topology checks operate on the represented surface, not the
    # serialization layout.
    loaded = trimesh.load(path, force="mesh", process=True)
    if isinstance(loaded, trimesh.Scene):
        loaded = loaded.to_geometry()
    if not isinstance(loaded, trimesh.Trimesh):
        raise TypeError(f"Unsupported mesh type for {path}: {type(loaded)}")
    return loaded


def intersection_volume(a, b) -> float:
    common = a.intersect(b)
    return sum(abs(float(shape.Volume())) for shape in common.vals())


def point_inside(part, point: tuple[float, float, float]) -> bool:
    return bool(part.val().isInside(cq.Vector(*point), 1.0e-5))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_integration(config: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    measurements: dict[str, Any] = {}

    project = config.get("project", {})
    installation = config.get("installation", {})
    revision = project.get("revision")
    spec_revision = project.get("spec_revision")
    installation_mode = installation.get("mode")
    measurements["configuration_identity"] = {
        "revision": revision,
        "spec_revision": spec_revision,
        "geometry_revision": project.get("geometry_revision"),
        "installation_mode": installation_mode,
        "release_status": project.get("release_status", "DRAFT"),
    }
    if revision != "0.2.0" or spec_revision != "0.2.0":
        failures.append(
            "Configuration project revision and spec revision must both be 0.2.0"
        )
    if installation_mode != "floor_standing_with_wall_restraint":
        failures.append(
            "Configuration installation mode must be floor_standing_with_wall_restraint"
        )
    if failures:
        return {"status": "FAIL", "failures": failures, "measurements": measurements}

    try:
        result = build_model(config)
    except Exception as error:
        failures.append(f"Revision 0.2.0 build_model validation rejected the configuration: {error}")
        return {"status": "FAIL", "failures": failures, "measurements": measurements}

    bodies = {record.name: record.solid for record in result.assembly_parts}
    print_parts = {record.name: record for record in result.print_parts}
    derived = result.derived
    frame = config["frame"]
    shelf = config["shelf"]
    grid = config["module_grid"]
    seam = grid["wide_module_seam"]
    tile_count = int(derived["tile_count"])
    segment_count = int(derived["side_segment_count"])
    clear_width = float(derived["clear_width"])
    frame_outer_width = float(derived["frame_outer_width"])
    side_t = float(frame["side_thickness"])
    side_x = float(derived["side_x"])
    wall_gap = float(installation["wall_gap"])
    shelf_top_values = [float(value) for value in derived["shelf_z_values"]]
    tolerance = 1.0e-6

    def check_scalar(name: str, actual: float, expected: float) -> None:
        measurements[name] = actual
        if abs(actual - expected) > tolerance:
            failures.append(f"{name} is {actual:.3f} mm; required {expected:.3f} mm")

    def bounds(part: cq.Workplane) -> dict[str, float]:
        box = part.val().BoundingBox()
        return {
            "xmin": float(box.xmin),
            "xmax": float(box.xmax),
            "ymin": float(box.ymin),
            "ymax": float(box.ymax),
            "zmin": float(box.zmin),
            "zmax": float(box.zmax),
            "xlen": float(box.xlen),
            "ylen": float(box.ylen),
            "zlen": float(box.zlen),
        }

    def solid_count(part: cq.Workplane) -> int:
        return len(part.val().Solids())

    def validation_compound(parts: list[cq.Workplane]) -> cq.Workplane:
        solids = [solid for part in parts for solid in part.val().Solids()]
        return cq.Workplane(obj=cq.Compound.makeCompound(solids))

    hardware = config.get("hardware", {})
    bom_rows: dict[str, dict[str, str]] = {}
    try:
        with (ROOT / "BOM.csv").open(newline="", encoding="utf-8") as handle:
            bom_rows = {row["item"]: row for row in csv.DictReader(handle)}
    except (OSError, KeyError) as error:
        failures.append(f"BOM hardware callouts could not be read: {error}")

    washer_t = 1.0
    locking_nut_h = 5.0
    hardware_stack_specs = {
        "shelf_bracket_m5": {
            "required_callout": "M5 x 45",
            "config_key": "shelf_bracket_bolt",
            "bom_item": "M5_bolts",
            "nominal_length_mm": 45.0,
            "modeled_stack_mm": {
                "frame": float(frame["side_thickness"]),
                "bracket": 12.0,
                "washers": 2.0 * washer_t,
                "locking_nut": locking_nut_h,
            },
            "minimum_remaining_mm": 5.0,
        },
        "shelf_to_bracket_m4": {
            "required_callout": "M4 x 20",
            "config_key": "shelf_to_bracket_screw",
            "bom_item": "M4_shelf_screws",
            "nominal_length_mm": 20.0,
            "modeled_stack_mm": {"bracket_ledge": 8.0, "washer": washer_t},
            "minimum_engagement_mm": 8.0,
        },
        "shelf_joiner_m4": {
            "required_callout": "M4 x 16",
            "config_key": "shelf_joiner_screw",
            "bom_item": "M4_joiner_screws",
            "nominal_length_mm": 16.0,
            "modeled_stack_mm": {
                "joiner_plate": float(shelf["joiner_height"]),
                "washer": washer_t,
            },
            "minimum_engagement_mm": 8.0,
        },
        "floor_foot_lock_m4": {
            "required_callout": "M4 x 50",
            "config_key": "foot_lock",
            "bom_item": "M4_foot_bolts",
            "nominal_length_mm": 50.0,
            "modeled_stack_mm": {
                "foot_receiver": float(frame["foot_width"]),
                "washers": 2.0 * washer_t,
                "locking_nut": locking_nut_h,
            },
        },
    }
    hardware_stack_checks: dict[str, Any] = {}
    for stack_name, stack in hardware_stack_specs.items():
        config_callout = str(hardware.get(stack["config_key"], ""))
        bom_callout = bom_rows.get(stack["bom_item"], {}).get(
            "material_or_specification", ""
        )
        required_callout = str(stack["required_callout"])
        callouts_present = (
            required_callout in config_callout and required_callout in bom_callout
        )
        used_length = sum(float(value) for value in stack["modeled_stack_mm"].values())
        remaining = float(stack["nominal_length_mm"]) - used_length
        check = {
            "required_callout": required_callout,
            "configuration_callout": config_callout,
            "bom_callout": bom_callout,
            "callouts_present": callouts_present,
            "planning_washer_thickness_each_mm": washer_t,
            "planning_locking_nut_height_mm": locking_nut_h,
            "modeled_stack_mm": stack["modeled_stack_mm"],
            "remaining_length_or_insert_engagement_mm": remaining,
            "exact_purchased_dimensions_status": "PENDING",
            "process_matched_coupon_status": "PENDING",
        }
        hardware_stack_checks[stack_name] = check
        if not callouts_present:
            failures.append(
                f"Required {required_callout} callout is missing from parameters.json or BOM.csv"
            )
        minimum = stack.get("minimum_remaining_mm", stack.get("minimum_engagement_mm"))
        if minimum is not None and remaining + tolerance < float(minimum):
            failures.append(
                f"{stack_name} remaining length/engagement is {remaining:.3f} mm; "
                f"minimum is {float(minimum):.3f} mm"
            )
        if "minimum_remaining_mm" in stack:
            check["minimum_remaining_length_mm"] = float(stack["minimum_remaining_mm"])
        if "minimum_engagement_mm" in stack:
            check["minimum_insert_engagement_mm"] = float(stack["minimum_engagement_mm"])
    measurements["hardware_stack_checks"] = hardware_stack_checks
    measurements["hardware_stack_qualification"] = (
        "DRAFT planning stack only; exact purchased dimensions and process-matched coupons pending"
    )

    expected_envelope = [680.0, 300.0, 1650.0]
    actual_envelope = [float(value) for value in derived["overall_envelope_mm"]]
    measurements["overall_envelope_mm"] = actual_envelope
    if any(abs(actual - expected) > tolerance for actual, expected in zip(actual_envelope, expected_envelope, strict=True)):
        failures.append(
            f"Overall envelope is {actual_envelope}; required {expected_envelope} mm"
        )
    check_scalar("shelf_clear_width_mm", clear_width, 620.0)
    measurements["shelf_top_datums_mm"] = shelf_top_values
    if shelf_top_values != [1050.0, 1400.0]:
        failures.append(
            f"Shelf top datums are {shelf_top_values}; required [1050.0, 1400.0] mm"
        )
    check_scalar("frame_outer_width_mm", frame_outer_width, 660.0)
    measurements["side_segment_count_per_side"] = segment_count
    if segment_count != 7:
        failures.append(f"Side segment count is {segment_count}; required seven per side")

    expected_side_assembly_names = {
        f"{label}_side_segment_{index}"
        for label in ("left", "right")
        for index in range(1, 8)
    }
    missing_side_names = sorted(expected_side_assembly_names - bodies.keys())
    measurements["side_segment_assembly_names_present"] = not missing_side_names
    if missing_side_names:
        failures.append(f"Missing side-segment assembly bodies: {missing_side_names}")

    build_volume = [float(value) for value in config["printer"]["build_volume"]]
    side_segment_extents: dict[str, Any] = {}
    for index in range(1, 8):
        name = f"side_segment_{index:02d}_print_2x"
        record = print_parts.get(name)
        if record is None:
            failures.append(f"Missing side-segment print body: {name}")
            continue
        part_bounds = bounds(record.solid)
        extents = [part_bounds["xlen"], part_bounds["ylen"], part_bounds["zlen"]]
        fits = all(
            extent <= limit + tolerance
            for extent, limit in zip(extents, build_volume, strict=True)
        )
        side_segment_extents[name] = {
            "extents_mm": extents,
            "configured_bed_mm": build_volume,
            "quantity": int(record.quantity),
            "fits": fits,
        }
        if record.quantity != 2:
            failures.append(f"{name} must have quantity two")
        if not fits:
            failures.append(f"Side-segment print extent exceeds configured bed: {name} {extents}")
    measurements["side_segment_print_extents"] = side_segment_extents

    floor_units = [
        (-1.0, "left", "rear", "left_rear_floor_foot", "left_rear_tpu_pad"),
        (-1.0, "left", "front", "left_front_floor_foot", "left_front_tpu_pad"),
        (1.0, "right", "rear", "right_rear_floor_foot", "right_rear_tpu_pad"),
        (1.0, "right", "front", "right_front_floor_foot", "right_front_tpu_pad"),
    ]
    floor_contacts: list[dict[str, Any]] = []
    contact_locations: list[tuple[float, float]] = []
    pad_t = float(frame["tpu_pad_thickness"])
    foot_width = float(frame["foot_width"])
    foot_depth = float(frame["foot_depth"])
    side_depth = float(frame["side_depth"])
    rail_width = float(frame["side_rail_width"])
    foot_lock_z = float(derived["side_base_z"]) + float(frame["foot_slot_depth"]) / 2.0
    for sign, label, position, foot_name, pad_name in floor_units:
        if foot_name not in bodies or pad_name not in bodies:
            failures.append(f"Missing named floor-contact pair: {foot_name} / {pad_name}")
            continue
        foot = bodies[foot_name]
        pad = bodies[pad_name]
        foot_bounds = bounds(foot)
        pad_bounds = bounds(pad)
        location = (
            (pad_bounds["xmin"] + pad_bounds["xmax"]) / 2.0,
            (pad_bounds["ymin"] + pad_bounds["ymax"]) / 2.0,
        )
        contact_locations.append(location)
        pad_on_floor = abs(pad_bounds["zmin"]) <= tolerance
        pad_base_interface_z = pad_bounds["zmin"] + pad_t
        foot_on_pad = abs(foot_bounds["zmin"] - pad_base_interface_z) <= tolerance
        nubs_extend_into_foot = pad_bounds["zmax"] > pad_base_interface_z + tolerance
        centres_aligned = (
            abs((foot_bounds["xmin"] + foot_bounds["xmax"]) / 2.0 - location[0]) <= tolerance
            and abs((foot_bounds["ymin"] + foot_bounds["ymax"]) / 2.0 - location[1]) <= tolerance
        )
        footprint_within_envelope = (
            min(foot_bounds["xmin"], pad_bounds["xmin"]) >= -expected_envelope[0] / 2.0 - tolerance
            and max(foot_bounds["xmax"], pad_bounds["xmax"]) <= expected_envelope[0] / 2.0 + tolerance
            and min(foot_bounds["ymin"], pad_bounds["ymin"]) >= -tolerance
            and max(foot_bounds["ymax"], pad_bounds["ymax"]) <= expected_envelope[1] + tolerance
        )
        nub_interior_z = pad_base_interface_z + (
            pad_bounds["zmax"] - pad_base_interface_z
        ) / 2.0
        nub_x_offset = foot_width / 2.0 - 8.0
        expected_nub_locations = [
            (location[0] + x_offset, foot_bounds["ymin"] + y_offset, nub_interior_z)
            for x_offset in (-nub_x_offset, nub_x_offset)
            for y_offset in (20.0, foot_depth - 20.0)
        ]
        nub_checks = []
        for nub_index, point in enumerate(expected_nub_locations, start=1):
            pad_material = point_inside(pad, point)
            foot_hole = not point_inside(foot, point)
            nub_checks.append(
                {
                    "index": nub_index,
                    "xyz_mm": list(point),
                    "tpu_material_present": pad_material,
                    "petg_receiver_hole_open": foot_hole,
                }
            )
            if not pad_material or not foot_hole:
                failures.append(
                    f"TPU nub/PETG receiver mismatch at {pad_name} nub {nub_index}"
                )

        rail_axis_y = rail_width / 2.0 if position == "rear" else side_depth - rail_width / 2.0
        wing_width = (foot_width - side_t) / 2.0
        foot_center_x = (foot_bounds["xmin"] + foot_bounds["xmax"]) / 2.0
        wing_offset = side_t / 2.0 + wing_width / 2.0
        foot_wing_axis_points = [
            (foot_center_x + offset, rail_axis_y, foot_lock_z)
            for offset in (-wing_offset, wing_offset)
        ]
        foot_wings_open = wing_width > 0.0 and all(
            not point_inside(foot, point) for point in foot_wing_axis_points
        )
        segment_name = f"{label}_side_segment_1"
        segment = bodies.get(segment_name)
        if segment is None:
            segment_axis_points: list[tuple[float, float, float]] = []
            lower_segment_open = False
        else:
            segment_bounds = bounds(segment)
            segment_axis_points = [
                (
                    segment_bounds["xmin"]
                    + fraction * (segment_bounds["xmax"] - segment_bounds["xmin"]),
                    rail_axis_y,
                    foot_lock_z,
                )
                for fraction in (0.15, 0.50, 0.85)
            ]
            lower_segment_open = all(
                not point_inside(segment, point) for point in segment_axis_points
            )
        foot_lock_open = foot_wings_open and lower_segment_open
        if not foot_lock_open:
            failures.append(
                f"M4 foot-lock axis is not open through both foot wings and {segment_name} "
                f"at Y={rail_axis_y:.3f}, Z={foot_lock_z:.3f} mm"
            )
        floor_contacts.append(
            {
                "foot": foot_name,
                "pad": pad_name,
                "location_xy_mm": [location[0], location[1]],
                "pad_floor_z_mm": pad_bounds["zmin"],
                "pad_base_top_z_mm": pad_base_interface_z,
                "foot_underside_z_mm": foot_bounds["zmin"],
                "pad_on_floor": pad_on_floor,
                "foot_on_pad": foot_on_pad,
                "nubs_extend_into_foot": nubs_extend_into_foot,
                "nub_checks": nub_checks,
                "centres_aligned": centres_aligned,
                "within_overall_width_depth": footprint_within_envelope,
                "m4_foot_lock": {
                    "axis_y_mm": rail_axis_y,
                    "source_derived_axis_z_mm": foot_lock_z,
                    "foot_wing_axis_points_mm": [list(point) for point in foot_wing_axis_points],
                    "both_foot_wings_open": foot_wings_open,
                    "lower_side_segment": segment_name,
                    "segment_axis_points_mm": [list(point) for point in segment_axis_points],
                    "lower_side_segment_open": lower_segment_open,
                    "aligned_and_open": foot_lock_open,
                },
            }
        )
        if not pad_on_floor or not foot_on_pad or not nubs_extend_into_foot or not centres_aligned:
            failures.append(f"Floor-contact stack is not continuous at {foot_name} / {pad_name}")
        if not footprint_within_envelope:
            failures.append(f"Floor-contact footprint exceeds the overall envelope: {foot_name}")
    unique_locations = {
        (round(location[0], 6), round(location[1], 6)) for location in contact_locations
    }
    measurements["floor_contacts"] = floor_contacts
    measurements["floor_contact_location_count"] = len(unique_locations)
    measurements["derived_floor_contact_count"] = int(derived["floor_contact_count"])
    if len(contact_locations) != 4 or len(unique_locations) != 4:
        failures.append("The four floor-contact locations must be present and unique")
    if int(derived["floor_contact_count"]) != 4:
        failures.append("Derived floor-contact count must be four")
    measurements["floor_interface_qualification"] = (
        "Digital pad-base, four-nub receiver, and M4 foot-lock checks only; "
        "production PETG/TPU/M4 coupon and floor evidence pending"
    )

    legacy_support_keys = {
        "cistern_top_width",
        "cistern_top_depth",
        "height_above_cistern",
        "cistern_pad_thickness",
        "support_on_cistern",
        "support_on_toilet",
    }
    legacy_support_paths = sorted(
        f"{section_name}.{key}"
        for section_name in ("installation", "frame")
        for key in config.get(section_name, {})
        if key in legacy_support_keys
    )
    support_body_names = sorted(
        name for name in bodies if "cistern_support" in name or "toilet_support" in name
    )
    measurements["floor_standing_load_path"] = {
        "mode": installation_mode,
        "legacy_support_keys_present": legacy_support_paths,
        "toilet_or_cistern_support_bodies": support_body_names,
        "toilet_and_cistern_are_planning_keepouts_only": True,
    }
    if legacy_support_paths or support_body_names:
        failures.append("Legacy toilet/cistern support logic is present in the active build")

    restraint_names = ["left_wall_restraint_spacer", "right_wall_restraint_spacer"]
    measurements["wall_restraint_spacer_names"] = restraint_names
    measurements["derived_wall_restraint_count"] = int(derived["wall_restraint_count"])
    missing_restraints = [name for name in restraint_names if name not in bodies]
    if missing_restraints or int(derived["wall_restraint_count"]) != 2:
        failures.append(
            f"Two named wall-restraint spacers are required; missing {missing_restraints}"
        )
    restraint_print = print_parts.get("height_adjustable_wall_restraint_spacer_print_2x")
    if restraint_print is None or restraint_print.quantity != 2:
        failures.append("Wall-restraint spacer print body must exist with quantity two")

    rear_rail_width = float(frame["side_rail_width"])

    def segment_at_z(label: str, z_value: float) -> tuple[str, cq.Workplane] | None:
        for index in range(1, segment_count + 1):
            name = f"{label}_side_segment_{index}"
            part = bodies.get(name)
            if part is None:
                continue
            part_bounds = bounds(part)
            if part_bounds["zmin"] + tolerance < z_value < part_bounds["zmax"] - tolerance:
                return name, part
        return None

    restraint_min = float(frame["wall_restraint_hole_min_z"])
    restraint_max = float(frame["wall_restraint_hole_max_z"])
    restraint_pitch = float(frame["wall_restraint_hole_spacing"])
    expected_restraint_series: list[float] = []
    value = restraint_min
    while value <= restraint_max + tolerance:
        expected_restraint_series.append(value)
        value += restraint_pitch
    actual_restraint_series = [
        float(value) for value in derived["wall_restraint_hole_z_values"]
    ]
    measurements["wall_restraint_adjustable_hole_series_mm"] = actual_restraint_series
    if actual_restraint_series != expected_restraint_series:
        failures.append(
            "Derived wall-restraint hole series does not match configured minimum, maximum, and pitch"
        )

    adjustable_hole_checks: dict[str, dict[str, bool]] = {}
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        label_checks: dict[str, bool] = {}
        for z_value in actual_restraint_series:
            segment_record = segment_at_z(label, z_value)
            if segment_record is None:
                failures.append(f"No {label} side segment contains wall-restraint Z={z_value:.0f} mm")
                label_checks[f"{z_value:.0f}"] = False
                continue
            _, segment = segment_record
            through_rear_rail = all(
                not point_inside(segment, (sign * side_x, y_value, z_value))
                for y_value in (rear_rail_width * 0.15, rear_rail_width * 0.50, rear_rail_width * 0.85)
            )
            label_checks[f"{z_value:.0f}"] = through_rear_rail
            if not through_rear_rail:
                failures.append(
                    f"Missing adjustable through-hole on {label} rear rail at Z={z_value:.0f} mm"
                )
        adjustable_hole_checks[label] = label_checks
    measurements["wall_restraint_rear_rail_through_holes"] = adjustable_hole_checks

    nominal_lower = float(frame["wall_restraint_nominal_lower_hole_z"])
    nominal_pair = [nominal_lower, nominal_lower + restraint_pitch]
    measurements["wall_restraint_nominal_hole_pair_mm"] = nominal_pair
    if nominal_pair != [1480.0, 1530.0]:
        failures.append(
            f"Nominal wall-restraint hole pair is {nominal_pair}; required [1480.0, 1530.0] mm"
        )
    nominal_hole_checks: dict[str, dict[str, bool]] = {}
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        spacer_name = f"{label}_wall_restraint_spacer"
        spacer = bodies.get(spacer_name)
        label_checks: dict[str, bool] = {}
        if spacer is None:
            continue
        for z_value in nominal_pair:
            spacer_through = all(
                not point_inside(spacer, (sign * side_x, y_value, z_value))
                for y_value in (-wall_gap * 0.85, -wall_gap * 0.50, -wall_gap * 0.15)
            )
            segment_record = segment_at_z(label, z_value)
            rail_through = bool(
                segment_record
                and all(
                    not point_inside(segment_record[1], (sign * side_x, y_value, z_value))
                    for y_value in (
                        rear_rail_width * 0.15,
                        rear_rail_width * 0.50,
                        rear_rail_width * 0.85,
                    )
                )
            )
            label_checks[f"{z_value:.0f}"] = spacer_through and rail_through
            if not spacer_through or not rail_through:
                failures.append(
                    f"Nominal wall-restraint through-hole is missing at {label} Z={z_value:.0f} mm"
                )
        nominal_hole_checks[label] = label_checks
    measurements["wall_restraint_nominal_through_holes"] = nominal_hole_checks

    # Shelf/bracket bearing overlap is intentional; validate its fastener axes
    # below rather than treating the support contact as a collision.
    seam_joiner_assembly_names = sorted(
        name for name in bodies if "_seam_joiner_" in name
    )
    joiners_by_module: dict[str, list[str]] = {}
    for joiner_name in seam_joiner_assembly_names:
        module_name = joiner_name.rsplit("_seam_joiner_", 1)[0]
        joiners_by_module.setdefault(module_name, []).append(joiner_name)
    complete_split_modules: dict[str, cq.Workplane] = {}
    for module_name, joiner_names in joiners_by_module.items():
        if module_name in bodies and len(joiner_names) == 2:
            complete_split_modules[module_name] = validation_compound(
                [bodies[module_name], *(bodies[name] for name in sorted(joiner_names))]
            )

    pair_checks: list[tuple[str, str]] = [
        ("left_wall_restraint_spacer", f"left_side_segment_{segment_count}"),
        ("right_wall_restraint_spacer", f"right_side_segment_{segment_count}"),
    ]
    drawer_pairs: list[tuple[str, str]] = []
    for level_index, level in enumerate(config["levels"], start=1):
        for module_index, module in enumerate(level.get("modules", []), start=1):
            if module["type"] == "drawer":
                pair = (
                    f"level_{level_index}_drawer_housing_{module_index}",
                    f"level_{level_index}_drawer_{module_index}",
                )
                pair_checks.append(pair)
                drawer_pairs.append(pair)
    if "header_insert" in bodies:
        pair_checks.append(("header_backer", "header_insert"))
    for name_a, name_b in pair_checks:
        if name_a not in bodies or name_b not in bodies:
            failures.append(f"Missing assembly body for intersection check: {name_a} / {name_b}")
            continue
        part_a = complete_split_modules.get(name_a, bodies[name_a])
        part_b = complete_split_modules.get(name_b, bodies[name_b])
        volume = intersection_volume(part_a, part_b)
        measurements[f"intersection_{name_a}__{name_b}_mm3"] = volume
        if volume > 0.05:
            failures.append(
                f"Unintended assembly intersection {name_a} / {name_b}: {volume:.3f} mm3"
            )

    edge_axis_y_values = (
        float(shelf["edge_beam_thickness"]) / 2.0,
        float(shelf["depth"]) - float(shelf["edge_beam_thickness"]) / 2.0,
    )
    shelf_total_height = float(shelf["total_height"])
    m4_axis_checks: list[dict[str, Any]] = []
    max_m4_axis_error = 0.0
    for level_index, shelf_top_z in enumerate(shelf_top_values, start=1):
        for sign, label, tile_number in (
            (-1.0, "left", 1),
            (1.0, "right", tile_count),
        ):
            # These offsets are source-owned by make_shelf_bracket/make_shelf_tile.
            bracket_center_x = sign * (frame_outer_width / 2.0 - side_t - 6.0)
            bracket_axis_x = bracket_center_x - sign * 12.0
            tile_axis_x = sign * (clear_width / 2.0 - 18.0)
            axis_error = abs(bracket_axis_x - tile_axis_x)
            max_m4_axis_error = max(max_m4_axis_error, axis_error)
            bracket_name = f"level_{level_index}_{label}_bracket"
            tile_name = f"level_{level_index}_tile_{tile_number}"
            bracket = bodies.get(bracket_name)
            tile = bodies.get(tile_name)
            for y_value in edge_axis_y_values:
                bracket_open = bool(
                    bracket
                    and not point_inside(
                        bracket,
                        (
                            bracket_axis_x,
                            y_value,
                            shelf_top_z - shelf_total_height - 4.0,
                        ),
                    )
                )
                tile_open = bool(
                    tile
                    and not point_inside(
                        tile,
                        (
                            tile_axis_x,
                            y_value,
                            shelf_top_z - shelf_total_height + 4.0,
                        ),
                    )
                )
                m4_axis_checks.append(
                    {
                        "level": level_index,
                        "side": label,
                        "y_mm": y_value,
                        "bracket_axis_x_mm": bracket_axis_x,
                        "insert_axis_x_mm": tile_axis_x,
                        "axis_error_mm": axis_error,
                        "bracket_hole_open": bracket_open,
                        "shelf_insert_open": tile_open,
                    }
                )
                if not bracket_open or not tile_open:
                    failures.append(
                        f"Missing M4 bracket/shelf insert hole on level {level_index} {label} at Y={y_value:.1f} mm"
                    )
    measurements["shelf_bracket_m4_axis_checks"] = m4_axis_checks
    measurements["shelf_bracket_m4_max_axis_error_mm"] = max_m4_axis_error
    if max_m4_axis_error > 0.20 + tolerance:
        failures.append(
            f"Shelf bracket M4 axis error is {max_m4_axis_error:.3f} mm; limit is 0.20 mm"
        )

    grid_start = float(frame["grid_start_from_floor"])
    grid_pitch = float(frame["grid_pitch"])
    m5_grid_checks: list[dict[str, Any]] = []
    max_m5_grid_error = 0.0
    for level_index, shelf_top_z in enumerate(shelf_top_values, start=1):
        for sign, label in ((-1.0, "left"), (1.0, "right")):
            bracket_name = f"level_{level_index}_{label}_bracket"
            bracket = bodies.get(bracket_name)
            bracket_center_x = sign * (frame_outer_width / 2.0 - side_t - 6.0)
            for z_value in (shelf_top_z - 20.0, shelf_top_z - 70.0):
                nearest_grid_z = grid_start + round((z_value - grid_start) / grid_pitch) * grid_pitch
                grid_error = abs(z_value - nearest_grid_z)
                max_m5_grid_error = max(max_m5_grid_error, grid_error)
                segment_record = segment_at_z(label, z_value)
                for y_value in (
                    rear_rail_width / 2.0,
                    float(frame["side_depth"]) - rear_rail_width / 2.0,
                ):
                    bracket_open = bool(
                        bracket
                        and not point_inside(bracket, (bracket_center_x, y_value, z_value))
                    )
                    frame_open = bool(
                        segment_record
                        and not point_inside(
                            segment_record[1], (sign * side_x, y_value, z_value)
                        )
                    )
                    m5_grid_checks.append(
                        {
                            "level": level_index,
                            "side": label,
                            "y_mm": y_value,
                            "axis_z_mm": z_value,
                            "nearest_50mm_grid_z_mm": nearest_grid_z,
                            "grid_error_mm": grid_error,
                            "bracket_hole_open": bracket_open,
                            "frame_hole_open": frame_open,
                        }
                    )
                    if not bracket_open or not frame_open:
                        failures.append(
                            f"Missing aligned M5 bracket/frame hole on level {level_index} {label} at Y={y_value:.1f}, Z={z_value:.1f} mm"
                        )
    measurements["shelf_bracket_m5_grid_checks"] = m5_grid_checks
    measurements["shelf_bracket_m5_max_grid_error_mm"] = max_m5_grid_error
    if abs(grid_pitch - 50.0) > tolerance or max_m5_grid_error > tolerance:
        failures.append("M5 shelf bracket axes are not aligned to the 50 mm frame grid")

    drawer_sweep: dict[str, list[dict[str, float]]] = {}
    drawer_travel = float(grid["default_depth"])
    travel_samples = [drawer_travel * fraction for fraction in (0.0, 0.25, 0.50, 0.75, 1.0)]
    for housing_name, drawer_name in drawer_pairs:
        if housing_name not in bodies or drawer_name not in bodies:
            continue
        samples = []
        for travel in travel_samples:
            housing = complete_split_modules.get(housing_name, bodies[housing_name])
            drawer = complete_split_modules.get(drawer_name, bodies[drawer_name])
            volume = intersection_volume(housing, drawer.translate((0.0, travel, 0.0)))
            samples.append({"travel_mm": travel, "intersection_mm3": volume})
            if volume > 0.05:
                failures.append(
                    f"Drawer sweep collision {housing_name}/{drawer_name} at {travel:.1f} mm: {volume:.3f} mm3"
                )
        drawer_sweep[f"{housing_name}__{drawer_name}"] = samples
    measurements["drawer_swept_travel"] = {
        "sample_policy": "validation-only complete housing/drawer compounds, including both seam joiners, sampled closed through full configured module depth at 0/25/50/75/100 percent",
        "configured_travel_mm": drawer_travel,
        "pairs": drawer_sweep,
    }
    if not drawer_pairs:
        failures.append("Default build must contain a drawer/housing pair")

    drawer_side_clearance = float(grid["drawer_clearance_each_side"])
    drawer_vertical_clearance = float(grid["drawer_clearance_vertical"])
    drawer_rear_clearance = float(grid["drawer_rear_clearance"])
    measurements["drawer_clearances_mm"] = {
        "each_side": drawer_side_clearance,
        "vertical": drawer_vertical_clearance,
        "rear": drawer_rear_clearance,
    }
    if min(drawer_side_clearance, drawer_vertical_clearance, drawer_rear_clearance) <= 0:
        failures.append("Drawer clearance must remain positive on every constrained axis")

    split_descriptors: list[dict[str, Any]] = []
    columns = int(grid["columns"])
    module_gap = float(grid["gap"])
    module_margin = float(grid["side_margin"])
    module_column_width = (
        clear_width - 2.0 * module_margin - (columns - 1) * module_gap
    ) / columns
    for level_index, level in enumerate(config["levels"], start=1):
        shelf_top_z = float(derived["shelf_z_values"][level_index - 1])
        for module_index, module in enumerate(level.get("modules", []), start=1):
            span = int(module["span"])
            module_width = span * module_column_width + (span - 1) * module_gap
            module_type = module["type"]
            if module_type == "open" or module_width <= float(grid["max_monolithic_print_width"]):
                continue
            print_prefix = f"level_{level_index:02d}_module_{module_index:02d}"
            if module_type == "drawer":
                split_descriptors.extend(
                    [
                        {
                            "assembly_name": f"level_{level_index}_drawer_housing_{module_index}",
                            "print_prefix": f"{print_prefix}_drawer_housing",
                            "joiner_side": "top-outside",
                            "station_depth_mm": float(grid["default_depth"]),
                            "boss_z0_mm": shelf_top_z + float(module["height"]),
                        },
                        {
                            "assembly_name": f"level_{level_index}_drawer_{module_index}",
                            "print_prefix": f"{print_prefix}_drawer",
                            "joiner_side": "bottom-inside",
                            "station_depth_mm": (
                                float(grid["default_depth"])
                                - float(grid["wall"])
                                - float(grid["drawer_rear_clearance"])
                            ),
                            "boss_z0_mm": (
                                shelf_top_z
                                + float(grid["wall"])
                                + float(grid["drawer_clearance_vertical"]) / 2.0
                            ),
                        },
                    ]
                )
            else:
                split_descriptors.append(
                    {
                        "assembly_name": f"level_{level_index}_{module_type}_{module_index}",
                        "print_prefix": f"{print_prefix}_{module_type}",
                        "joiner_side": "bottom-inside",
                        "station_depth_mm": float(grid["default_depth"]),
                        "boss_z0_mm": shelf_top_z,
                    }
                )

    expected_split_print_bodies = {
        f"{descriptor['print_prefix']}_{hand}_print"
        for descriptor in split_descriptors
        for hand in ("left", "right")
    }
    actual_split_print_bodies = {
        name
        for name in print_parts
        if "_module_" in name and (name.endswith("_left_print") or name.endswith("_right_print"))
    }
    measurements["default_split_module_print_bodies"] = sorted(actual_split_print_bodies)
    if actual_split_print_bodies != expected_split_print_bodies:
        failures.append(
            "Default build must provide the expected left/right drawer, housing, and bin print bodies"
        )

    split_module_checks: dict[str, Any] = {}
    boss_height = float(seam["boss_height"])
    station_edge_offset = float(seam["station_edge_offset"])
    m3_axis_offset = float(seam["m3_axis_offset"])
    configured_contact_gap = float(seam["plate_boss_contact_gap"])
    for descriptor in split_descriptors:
        module_name = descriptor["assembly_name"]
        module = bodies.get(module_name)
        joiner_names = sorted(joiners_by_module.get(module_name, []))
        print_names = [
            f"{descriptor['print_prefix']}_{hand}_print" for hand in ("left", "right")
        ]
        check: dict[str, Any] = {
            "joiner_side": descriptor["joiner_side"],
            "print_half_names": print_names,
            "joiner_names": joiner_names,
            "physical_seam_qualification_status": "PENDING",
        }
        split_module_checks[module_name] = check
        if module is None:
            failures.append(f"Missing split-module assembly body: {module_name}")
            continue
        half_solids = list(module.val().Solids())
        check["assembly_printable_half_solid_count"] = len(half_solids)
        if len(half_solids) != 2:
            failures.append(
                f"{module_name} must contain exactly two printable-half solids; found {len(half_solids)}"
            )
            continue
        print_half_solid_counts = {
            name: solid_count(print_parts[name].solid) if name in print_parts else 0
            for name in print_names
        }
        check["print_half_solid_counts"] = print_half_solid_counts
        if any(count != 1 for count in print_half_solid_counts.values()):
            failures.append(
                f"{module_name} must have exactly two single-solid printable half records"
            )

        half_bounds = sorted(
            (
                {
                    "xmin": float(solid.BoundingBox().xmin),
                    "xmax": float(solid.BoundingBox().xmax),
                    "zmin": float(solid.BoundingBox().zmin),
                    "zmax": float(solid.BoundingBox().zmax),
                }
                for solid in half_solids
            ),
            key=lambda item: item["xmin"],
        )
        module_bounds = bounds(module)
        seam_gap = half_bounds[1]["xmin"] - half_bounds[0]["xmax"]
        seam_x = (half_bounds[0]["xmax"] + half_bounds[1]["xmin"]) / 2.0
        module_center_x = (module_bounds["xmin"] + module_bounds["xmax"]) / 2.0
        seam_center_error = abs(seam_x - module_center_x)
        vertical_step = max(
            abs(half_bounds[0]["zmin"] - half_bounds[1]["zmin"]),
            abs(half_bounds[0]["zmax"] - half_bounds[1]["zmax"]),
        )
        halves_meet = abs(seam_gap) <= 0.05 + tolerance and seam_center_error <= 0.05 + tolerance
        check["center_seam"] = {
            "gap_or_overlap_mm": seam_gap,
            "center_error_mm": seam_center_error,
            "meet_tolerance_mm": 0.05,
            "halves_meet": halves_meet,
            "vertical_step_proxy_mm": vertical_step,
            "vertical_step_limit_mm": 0.5,
        }
        if not halves_meet:
            failures.append(f"{module_name} printable halves do not meet at the center seam within 0.05 mm")
        if vertical_step > 0.5 + tolerance:
            failures.append(
                f"{module_name} vertical seam-step proxy is {vertical_step:.3f} mm; limit is 0.5 mm"
            )

        if len(joiner_names) != 2 or module_name not in complete_split_modules:
            failures.append(f"{module_name} requires exactly two named validation-compound seam joiners")
            check["complete_compound_solid_count"] = 0
            continue
        check["complete_compound_solid_count"] = solid_count(
            complete_split_modules[module_name]
        )
        expected_station_y = [
            module_bounds["ymin"] + station_edge_offset,
            module_bounds["ymin"]
            + float(descriptor["station_depth_mm"])
            - station_edge_offset,
        ]
        joiner_checks: list[dict[str, Any]] = []
        for joiner_index, (joiner_name, expected_y) in enumerate(
            zip(joiner_names, expected_station_y, strict=True), start=1
        ):
            joiner = bodies[joiner_name]
            joiner_bounds = bounds(joiner)
            joiner_center_x = (joiner_bounds["xmin"] + joiner_bounds["xmax"]) / 2.0
            joiner_center_y = (joiner_bounds["ymin"] + joiner_bounds["ymax"]) / 2.0
            boss_z0 = float(descriptor["boss_z0_mm"])
            boss_top_z = boss_z0 + boss_height
            actual_contact_gap = joiner_bounds["zmin"] - boss_top_z
            expected_joiner_zmin = boss_top_z + configured_contact_gap
            seating_errors = {
                "seam_x_mm": abs(joiner_center_x - seam_x),
                "station_y_mm": abs(joiner_center_y - expected_y),
                "source_datum_z_mm": abs(joiner_bounds["zmin"] - expected_joiner_zmin),
            }
            seated = max(seating_errors.values()) <= 0.05 + tolerance
            axes = []
            for axis_x in (seam_x - m3_axis_offset, seam_x + m3_axis_offset):
                plate_samples = [
                    (
                        axis_x,
                        expected_y,
                        joiner_bounds["zmin"] + fraction * joiner_bounds["zlen"],
                    )
                    for fraction in (0.20, 0.50, 0.80)
                ]
                boss_samples = [
                    (axis_x, expected_y, boss_z0 + boss_height * fraction)
                    for fraction in (0.25, 0.50, 0.75)
                ]
                plate_open = all(
                    not point_inside(joiner, point) for point in plate_samples
                )
                boss_open = all(
                    not point_inside(module, point) for point in boss_samples
                )
                axes.append(
                    {
                        "x_mm": axis_x,
                        "y_mm": expected_y,
                        "joiner_plate_open": plate_open,
                        "module_boss_open": boss_open,
                    }
                )
            joiner_check = {
                "index": joiner_index,
                "name": joiner_name,
                "source_boss_datum": descriptor["joiner_side"],
                "boss_top_z_mm": boss_top_z,
                "plate_zmin_mm": joiner_bounds["zmin"],
                "plate_boss_contact_gap_mm": actual_contact_gap,
                "required_contact_gap_mm": configured_contact_gap,
                "seating_errors_mm": seating_errors,
                "seated_on_boss_top": seated,
                "m3_axes": axes,
            }
            joiner_checks.append(joiner_check)
            if not seated:
                failures.append(f"{joiner_name} is not seated on its source-defined boss top")
            if any(
                not axis["joiner_plate_open"] or not axis["module_boss_open"]
                for axis in axes
            ):
                failures.append(f"{joiner_name} does not have two open M3 plate/boss axes")
        check["joiner_checks"] = joiner_checks

    seam_joiner_record = print_parts.get("wide_module_m3_seam_joiner_print")
    measurements["default_module_seam_joiners"] = {
        "derived_quantity": int(derived["module_seam_joiner_quantity"]),
        "print_quantity": int(seam_joiner_record.quantity) if seam_joiner_record else 0,
        "assembly_names": seam_joiner_assembly_names,
    }
    if (
        int(derived["split_module_component_count"]) != 3
        or int(derived["module_seam_joiner_quantity"]) != 6
        or seam_joiner_record is None
        or seam_joiner_record.quantity != 6
        or len(seam_joiner_assembly_names) != 6
    ):
        failures.append("Default split modules require exactly six M3 seam joiners")
    measurements["split_module_checks"] = split_module_checks
    measurements["split_module_qualification"] = (
        "Validation-only complete compounds include both printable halves and both named joiners; "
        "exact M3 hardware, process coupon, seam load, and assembly-cycle qualification pending"
    )

    module_stop_y = 10.0 + float(grid["default_depth"]) + 6.0
    stop_rail_height = 6.0
    stop_rail_depth = 3.0
    stop_rail_checks: list[dict[str, Any]] = []
    module_retention_checks: list[dict[str, Any]] = []
    for level_index, (level, shelf_top_z) in enumerate(
        zip(config["levels"], shelf_top_values, strict=True), start=1
    ):
        expected_stop_rail = (
            cq.Workplane("XY")
            .box(clear_width, stop_rail_depth, stop_rail_height)
            .translate((0.0, module_stop_y, shelf_top_z + stop_rail_height / 2.0))
        )
        for tile_index in range(tile_count):
            tile_name = f"level_{level_index}_tile_{tile_index + 1}"
            tile = bodies.get(tile_name)
            x0 = -clear_width / 2.0 + tile_index * clear_width / tile_count
            x1 = x0 + clear_width / tile_count
            sample_points = [
                (x0 + fraction * (x1 - x0), module_stop_y, shelf_top_z + z_offset)
                for fraction in (0.10, 0.50, 0.90)
                for z_offset in (0.25, stop_rail_height - 0.25)
            ]
            rail_material_present = bool(
                tile and all(point_inside(tile, point) for point in sample_points)
            )
            above_rail_open = bool(
                tile
                and not point_inside(
                    tile,
                    (
                        (x0 + x1) / 2.0,
                        module_stop_y,
                        shelf_top_z + stop_rail_height + 0.20,
                    ),
                )
            )
            stop_rail_checks.append(
                {
                    "tile": tile_name,
                    "source_defined_y_mm": module_stop_y,
                    "required_height_mm": stop_rail_height,
                    "material_samples_present": rail_material_present,
                    "above_rail_open": above_rail_open,
                }
            )
            if not rail_material_present or not above_rail_open:
                failures.append(
                    f"{tile_name} does not contain the source-positioned 6 mm stop rail"
                )

        cursor = 0
        for module_index, module_config in enumerate(level.get("modules", []), start=1):
            module_type = module_config["type"]
            span = int(module_config["span"])
            if module_type == "open":
                cursor += span
                continue
            if module_type == "drawer":
                module_name = f"level_{level_index}_drawer_housing_{module_index}"
            else:
                module_name = f"level_{level_index}_{module_type}_{module_index}"
            module_part = complete_split_modules.get(module_name, bodies.get(module_name))
            if module_part is None:
                failures.append(f"Missing default module for front-stop check: {module_name}")
                cursor += span
                continue
            module_bounds = bounds(module_part)
            rail_bounds = bounds(expected_stop_rail)
            clearance = rail_bounds["ymin"] - module_bounds["ymax"]
            stop_intersection = intersection_volume(module_part, expected_stop_rail)
            starts_behind_without_intersection = (
                clearance >= -tolerance and stop_intersection <= 0.05
            )
            module_retention_checks.append(
                {
                    "module": module_name,
                    "validation_body": (
                        "complete_split_compound"
                        if module_name in complete_split_modules
                        else "assembly_body"
                    ),
                    "front_clearance_to_stop_mm": clearance,
                    "stop_intersection_mm3": stop_intersection,
                    "starts_behind_stop_without_intersection": starts_behind_without_intersection,
                }
            )
            if not starts_behind_without_intersection:
                failures.append(f"Default module intersects or starts ahead of its stop rail: {module_name}")
            cursor += span
    measurements["shelf_tile_stop_rails"] = stop_rail_checks
    measurements["default_module_stop_clearance"] = module_retention_checks
    measurements["module_retention_physical_criterion"] = {
        "horizontal_force_n": 10.0,
        "maximum_travel_mm": 5.0,
        "status": "PENDING — planned physical criterion, not passed by digital validation",
    }

    header = config["personalization"]["header"]
    if not header.get("enabled"):
        failures.append("Default revision 0.2.0 integration requires the removable header")
    else:
        backer_t = float(header["backer_thickness"])
        insert_t = float(header["insert_base_thickness"])
        recess_width = float(header["insert_width"]) + 0.5
        recess_height = float(header["insert_height"]) + 0.5
        recess_depth_size = insert_t + 0.5
        recess_center_y = backer_t / 2.0 + 0.1
        recess_inner_y = recess_center_y - recess_depth_size / 2.0
        recess_depth = backer_t / 2.0 - recess_inner_y
        insert_back_y = backer_t / 2.0 - insert_t / 2.0
        insert_engagement = backer_t / 2.0 - insert_back_y
        removable_gap = insert_back_y - recess_inner_y
        header_checks = {
            "recess_width_clearance_total_mm": recess_width - float(header["insert_width"]),
            "recess_height_clearance_total_mm": recess_height - float(header["insert_height"]),
            "recess_depth_mm": recess_depth,
            "insert_engagement_depth_mm": insert_engagement,
            "removable_tape_gap_mm": removable_gap,
            "backer_present": "header_backer" in bodies,
            "insert_present_or_relief_selected": (
                "header_insert" in bodies
                or bool(config["personalization"]["image_relief"]["enabled"])
            ),
        }
        measurements["header_recess"] = header_checks
        if (
            header_checks["recess_width_clearance_total_mm"] <= 0
            or header_checks["recess_height_clearance_total_mm"] <= 0
            or recess_depth < insert_engagement - tolerance
            or removable_gap < -tolerance
            or not header_checks["backer_present"]
            or not header_checks["insert_present_or_relief_selected"]
        ):
            failures.append("Header recess clearance, depth, or body inventory check failed")

    measurements["planning_keepouts"] = {
        "verification_status": "SITE VERIFICATION PENDING",
        "baseboard": {
            "depth_mm": float(installation["baseboard_keepout_depth"]),
            "height_mm": float(installation["baseboard_keepout_height"]),
        },
        "toilet_and_service": {
            "clear_width_mm": float(installation["toilet_clear_width"]),
            "clear_height_mm": float(installation["toilet_clear_height"]),
            "planning_depth_mm": float(installation["overall_depth"]),
        },
        "wall": {
            "gap_mm": wall_gap,
            "clear_width_mm": float(installation["clear_wall_width"]),
        },
        "scope": "Planning values reported only; measured toilet, cistern/lid service path, pipes, flush controls, baseboard, wall, and floor remain pending",
    }
    measurements["shelf_tile_width_mm"] = float(derived["tile_width"])
    measurements["shelf_load_target_kg_udl"] = float(
        shelf["nominal_load_kg_evenly_distributed"]
    )
    measurements["validation_scope"] = (
        "DRAFT digital integration checks only, including planning hardware stacks, floor interfaces, "
        "validation-only complete split-module compounds, and module stop rails; exact purchased hardware, "
        "coupons, physical retention, hanger, manufacturing, load, anti-tip, and release acceptance remain pending"
    )
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "measurements": measurements,
    }


def validate_output(output: Path) -> dict[str, Any]:
    manifest_path = output / "reports" / "build_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config_path = Path(manifest.get("config_absolute", manifest["config"]))
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    config = json.loads(config_path.read_text(encoding="utf-8"))
    build_volume = np.asarray(config["printer"]["build_volume"], dtype=float)
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    warnings: list[str] = []
    manufacturing_blockers: list[str] = []
    expected_coupon_component_counts = {
        "fit_coupon_020_030_040_050_print": 9,
        "wide_module_m3_seam_coupon_print": 3,
        "floor_foot_tpu_lock_coupon_print": 3,
    }

    exact_3mf_files = sorted(
        str(path.relative_to(output))
        for path in (output / "3mf").rglob("*.3mf")
        if path.is_file()
    )
    if not exact_3mf_files:
        missing_3mf = (
            "DRAFT manufacturing blocker: no revision-bound exact target-profile 3MF is present"
        )
        manufacturing_blockers.append(missing_3mf)
        warnings.append(missing_3mf)

    for reference, expected_hash in manifest.get("source_hashes_sha256", {}).items():
        path = Path(reference)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            failures.append(f"Tracked source missing: {reference}")
        elif sha256(path) != expected_hash:
            failures.append(f"Tracked source hash mismatch: {reference}")
    for reference, expected_hash in manifest.get("artifact_hashes_sha256", {}).items():
        path = output / reference
        if not path.exists():
            failures.append(f"Tracked artifact missing: {reference}")
        elif sha256(path) != expected_hash:
            failures.append(f"Tracked artifact hash mismatch: {reference}")

    for record in manifest["parts"]:
        path = output / record["stl"]
        if not path.exists():
            failures.append(f"Missing STL: {record['stl']}")
            continue
        mesh = load_mesh(path)
        extents = np.asarray(mesh.extents, dtype=float)
        components = mesh.split(only_watertight=False)
        expected_component_count = (
            expected_coupon_component_counts.get(record["name"], 1)
            if record["category"] == "coupon"
            else 1
        )
        watertight = bool(mesh.is_watertight)
        winding = bool(mesh.is_winding_consistent)
        is_volume = bool(mesh.is_volume)
        volume = abs(float(mesh.volume))
        bed_fit = bool(np.all(extents <= build_volume + 0.25))
        component_count_matches = len(components) == expected_component_count
        if not watertight:
            failures.append(f"Not watertight: {record['name']}")
        if not winding:
            failures.append(f"Inconsistent winding: {record['name']}")
        if not is_volume:
            failures.append(f"Not a closed positive volume: {record['name']}")
        if volume <= 0.01:
            failures.append(f"Non-positive volume: {record['name']}")
        if not bed_fit:
            failures.append(
                f"Exceeds build volume: {record['name']} {extents.tolist()} > {build_volume.tolist()}"
            )
        if not component_count_matches:
            failures.append(
                f"Unexpected component count: {record['name']} has {len(components)}; "
                f"required {expected_component_count}"
            )
        step_value = record.get("step")
        if step_value and not (output / step_value).exists():
            failures.append(f"Missing STEP: {step_value}")
        results.append(
            {
                "name": record["name"],
                "quantity": record["quantity"],
                "triangles": int(len(mesh.faces)),
                "vertices": int(len(mesh.vertices)),
                "file_size_bytes": path.stat().st_size,
                "extents_mm": extents.tolist(),
                "volume_mm3": volume,
                "watertight": watertight,
                "winding_consistent": winding,
                "is_volume": is_volume,
                "component_count": len(components),
                "expected_component_count": expected_component_count,
                "component_count_matches": component_count_matches,
                "bed_fit": bed_fit,
            }
        )

    assembly_stl = output / "preview" / "premium_over_toilet_shelf_assembly.stl"
    assembly_step = output / "preview" / "premium_over_toilet_shelf_assembly.step"
    if not assembly_stl.exists() or not assembly_step.exists():
        failures.append("Assembly preview STL or STEP is missing")
        assembly_metrics: dict[str, Any] = {}
    else:
        assembly = load_mesh(assembly_stl)
        assembly_metrics = {
            "triangles": int(len(assembly.faces)),
            "vertices": int(len(assembly.vertices)),
            "named_body_count": len(manifest["assembly_body_names"]),
            "serialized_surface_component_count": len(
                assembly.split(only_watertight=False)
            ),
            "extents_mm": assembly.extents.tolist(),
            "file_size_bytes": assembly_stl.stat().st_size,
        }

    image_report_path = output / "reports" / "image_relief_report.json"
    image_relief = None
    if image_report_path.exists():
        image_relief = json.loads(image_report_path.read_text(encoding="utf-8"))
        if image_relief["aspect_error_pct"] > 0.75:
            failures.append(
                f"Image-relief physical aspect error is {image_relief['aspect_error_pct']:.3f}%"
            )
        if not image_relief["watertight"]:
            failures.append("Image-relief insert is not watertight")
        if image_relief["triangles"] > 1_000_000:
            failures.append("Image-relief insert exceeds one-million-triangle workflow target")
        if image_relief["triangles"] > 250_000:
            warnings.append("Image-relief triangle count requires exact-slicer timing review")
        if image_relief.get("resource_budget_status") == "FAIL":
            failures.append("Image-relief resource budget failed")
        local_bounds = np.asarray(image_relief["assembly_local_bounds_mm"], dtype=float)
        local_extents = local_bounds[1] - local_bounds[0]
        header = config["personalization"]["header"]
        width_clearance = float(header["insert_width"]) + 0.5 - local_extents[0]
        height_clearance = float(header["insert_height"]) + 0.5 - local_extents[2]
        image_relief["backer_width_clearance_total_mm"] = width_clearance
        image_relief["backer_height_clearance_total_mm"] = height_clearance
        if width_clearance < -1e-6 or height_clearance < -1e-6:
            failures.append("Image-relief insert exceeds the modeled header recess")

    derived = manifest["derived"]
    if derived["tile_count"] < 1 or derived["side_segment_count"] < 1:
        failures.append("Derived segmentation count is invalid")
    if len(derived["shelf_z_values"]) != len(config["levels"]):
        failures.append("Shelf-level count differs between configuration and build")

    component_failures = list(failures)
    integration = validate_integration(config)
    failures.extend(integration["failures"])

    report = {
        "schema_version": 1,
        "output": str(output),
        "status": "PASS" if not failures else "FAIL",
        "release_status": "DRAFT — physical, manufacturing, and release acceptance not claimed",
        "component_mesh_status": "PASS" if not component_failures else "FAIL",
        "integration_status": integration["status"],
        "manufacturing_status": "BLOCKED" if manufacturing_blockers else "DRAFT",
        "manifest_configuration": {
            "path": str(config_path),
            "revision": config.get("project", {}).get("revision"),
            "spec_revision": config.get("project", {}).get("spec_revision"),
            "geometry_revision": config.get("project", {}).get("geometry_revision"),
            "installation_mode": config.get("installation", {}).get("mode"),
        },
        "exact_3mf": {
            "status": "PRESENT_UNREVIEWED" if exact_3mf_files else "ABSENT",
            "files": exact_3mf_files,
            "component_mesh_geometry_failure": False,
        },
        "build_volume_mm": build_volume.tolist(),
        "checked_print_files": len(results),
        "parts": results,
        "assembly": assembly_metrics,
        "integration": integration,
        "image_relief": image_relief,
        "failures": failures,
        "warnings": warnings,
        "manufacturing_blockers": manufacturing_blockers,
        "remaining_gates": [
            "exact target slicer review from a revision-bound 3MF, including preview, toolpaths, supports, thin walls, seams, and time/material estimate",
            "exact purchased M5 x 45, M4 x 20, M4 x 16, and M4 x 50 dimensions plus process-matched stack/insert coupons; planning washer and locking-nut dimensions are not purchase acceptance",
            "production PETG/TPU/M4 floor-foot lock coupon covering pad-base contact, four-nub retention, rail alignment, service cycles, shear, and pull-off",
            "complete split-module seam qualification with both printable halves, both joiners, exact M3 hardware, seam-load proof, tool access, and assembly cycles",
            "remaining process-matched interfaces, including frame seams, shelf seams, drawer/header fits, and M4/M5 bosses/inserts",
            "measured site verification for toilet/cistern and lid service path, flush controls, pipes, baseboard, wall gap/substrate, clear width, and four floor contacts",
            "shelf physical evidence: 4 kg service/24-hour creep, 8 kg one-hour proof load, residual set, and 1000 load cycles",
            "drawer physical evidence: 5000 full-travel cycles",
            "module and hanger physical retention: 10 N/5 mm module criterion, loaded module behavior, 500 hanger cycles, and hanger proof load",
            "substrate-specific guarded 100 N anti-tip test with the selected purchased anchors",
            "print-time/material optimization decision and manufacturing-mesh policy with protected regions and independent slicer-resolution evidence",
            "JuSt Innovation watermark integration on current geometry and explicit final release approval",
        ],
    }
    reports = output / "reports"
    (reports / "validation_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# DRAFT validation report",
        "",
        f"**DRAFT digital validation status: {report['status']}**",
        "",
        "No physical, manufacturing, load, anti-tip, or release acceptance is claimed.",
        "",
        f"- Checked printable files: {len(results)}",
        f"- Build volume: {build_volume.tolist()} mm",
        f"- Named assembly bodies: {assembly_metrics.get('named_body_count', 'n/a')}",
        f"- Integration status: {integration['status']}",
        f"- Component-mesh status: {report['component_mesh_status']}",
        f"- Manufacturing status: {report['manufacturing_status']}",
        "",
        "## Failures",
        "",
    ]
    lines.extend([f"- {failure}" for failure in failures] or ["- None"])
    lines.extend(["", "## Manufacturing warnings and blockers", ""])
    lines.extend([f"- {item}" for item in manufacturing_blockers] or ["- None recorded"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Remaining gates", ""])
    lines.extend([f"- {item}" for item in report["remaining_gates"]])
    (reports / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "default")
    args = parser.parse_args()
    report = validate_output(args.output.resolve())
    print(json.dumps({"status": report["status"], "failures": report["failures"]}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
