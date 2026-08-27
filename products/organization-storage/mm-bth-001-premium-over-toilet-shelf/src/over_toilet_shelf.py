"""Parametric printable geometry for a premium over-toilet shelf.

All dimensions use millimetres. Assembly coordinates are right handed:
+X points right, +Y points from the wall toward the user, and +Z points up.
The origin lies on the finished floor at the centre of the rear frame plane.
The wall plane is at Y = -installation.wall_gap. The toilet and cistern are
site keep-outs only and never carry shelf load.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any

import cadquery as cq


IDENTITY = [
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0,
]


@dataclass
class PartRecord:
    name: str
    solid: cq.Workplane
    quantity: int
    material: str
    orientation: str
    category: str


@dataclass
class AssemblyRecord:
    name: str
    solid: cq.Workplane
    color: tuple[float, float, float]


@dataclass
class BuildResult:
    config: dict[str, Any]
    print_parts: list[PartRecord]
    assembly_parts: list[AssemblyRecord]
    derived: dict[str, Any]


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def centred_box(
    x_size: float,
    y_size: float,
    z_size: float,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
) -> cq.Workplane:
    return cq.Workplane("XY").box(x_size, y_size, z_size).translate((x, y, z))


def box_from_corner(
    x_size: float,
    y_size: float,
    z_size: float,
    x0: float = 0.0,
    y0: float = 0.0,
    z0: float = 0.0,
) -> cq.Workplane:
    return centred_box(
        x_size,
        y_size,
        z_size,
        x=x0 + x_size / 2.0,
        y=y0 + y_size / 2.0,
        z=z0 + z_size / 2.0,
    )


def cylinder_x(diameter: float, length: float, x0: float, y: float, z: float) -> cq.Workplane:
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(diameter / 2.0).extrude(length)


def cylinder_z(diameter: float, length: float, x: float, y: float, z0: float) -> cq.Workplane:
    return cq.Workplane("XY", origin=(x, y, z0)).circle(diameter / 2.0).extrude(length)


def cylinder_y(diameter: float, length: float, x: float, y0: float, z: float) -> cq.Workplane:
    # XZ workplanes extrude along -Y. Start at the positive end so the solid
    # spans [y0, y0 + length].
    return (
        cq.Workplane("XZ", origin=(x, y0 + length, z))
        .circle(diameter / 2.0)
        .extrude(length)
    )


def place_on_bed(part: cq.Workplane) -> cq.Workplane:
    bounds = part.val().BoundingBox()
    return part.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def orient_side_on_bed(part: cq.Workplane) -> cq.Workplane:
    return place_on_bed(part.rotate((0, 0, 0), (0, 1, 0), 90))


def orient_fascia_on_bed(part: cq.Workplane) -> cq.Workplane:
    return place_on_bed(part.rotate((0, 0, 0), (1, 0, 0), 90))


def safe_fillet(part: cq.Workplane, selector: str, radius: float) -> cq.Workplane:
    if radius <= 0:
        return part
    try:
        return part.edges(selector).fillet(radius)
    except Exception as error:
        raise RuntimeError(f"Required fillet failed for selector {selector!r}") from error


def beam_yz(
    y0: float,
    z0: float,
    y1: float,
    z1: float,
    width: float,
    thickness_x: float,
) -> cq.Workplane:
    dy = y1 - y0
    dz = z1 - z0
    length = math.hypot(dy, dz)
    ny = -dz / length * width / 2.0
    nz = dy / length * width / 2.0
    profile = [
        (y0 + ny, z0 + nz),
        (y1 + ny, z1 + nz),
        (y1 - ny, z1 - nz),
        (y0 - ny, z0 - nz),
    ]
    return (
        cq.Workplane("YZ", origin=(-thickness_x / 2.0, 0.0, 0.0))
        .polyline(profile)
        .close()
        .extrude(thickness_x)
    )


def text_solid(
    text: str,
    width: float,
    height: float,
    depth: float,
    y0: float,
    z_center: float,
    font: str,
) -> cq.Workplane | None:
    if not text.strip() or depth <= 0:
        return None
    size = min(height * 0.62, max(5.0, width / max(2.0, len(text) * 0.72)))
    try:
        shape = (
            cq.Workplane("XY")
            .text(text, size, depth, font=font, halign="center", valign="center")
            .rotate((0, 0, 0), (1, 0, 0), -90)
            .translate((0.0, y0, z_center))
        )
    except Exception as error:
        raise RuntimeError(f"Text generation failed for {text!r} using font {font!r}") from error
    return shape


def apply_front_finish(
    panel: cq.Workplane,
    width: float,
    height: float,
    thickness: float,
    finish: str,
    relief: float = 0.8,
) -> cq.Workplane:
    """Apply compact procedural relief while keeping the rear datum untouched."""
    front_y = thickness / 2.0
    margin = 3.0
    if finish == "smooth":
        return panel
    if finish == "fluted":
        pitch = 8.0
        count = max(1, int((width - 2.0 * margin) // pitch))
        x_start = -(count - 1) * pitch / 2.0
        for index in range(count):
            x = x_start + index * pitch
            groove = cylinder_z(
                diameter=3.2,
                length=height - 2.0 * margin,
                x=x,
                y=front_y + 0.9,
                z0=-height / 2.0 + margin,
            )
            panel = panel.cut(groove)
        return panel
    if finish == "ribs":
        pitch = 10.0
        count = max(1, int((width - 2.0 * margin) // pitch))
        x_start = -(count - 1) * pitch / 2.0
        for index in range(count):
            x = x_start + index * pitch
            rib = centred_box(2.2, relief, height - 2.0 * margin, x=x, y=front_y + relief / 2.0)
            panel = panel.union(rib)
        return panel
    if finish == "diamond":
        cutter_depth = relief + 0.4
        line_width = 1.5
        diagonal_length = math.hypot(width, height) + 20.0
        for angle in (-35.0, 35.0):
            for offset in range(-int(width), int(width) + 1, 14):
                groove = centred_box(
                    diagonal_length,
                    cutter_depth,
                    line_width,
                    y=front_y + 0.3,
                    z=offset * 0.35,
                ).rotate((0, 0, 0), (0, 1, 0), angle)
                panel = panel.cut(groove)
        return panel
    raise ValueError(f"Unsupported finish: {finish}")


def decorate_front(
    panel: cq.Workplane,
    width: float,
    height: float,
    thickness: float,
    finish: str,
    text: str,
    text_mode: str,
    text_depth: float,
    font: str,
) -> cq.Workplane:
    panel = apply_front_finish(panel, width, height, thickness, finish)
    front_y = thickness / 2.0
    if not text.strip():
        return panel
    if text_mode == "engrave":
        cutter = text_solid(
            text,
            width - 10.0,
            height - 8.0,
            text_depth + 0.25,
            front_y - text_depth,
            0.0,
            font,
        )
        return panel if cutter is None else panel.cut(cutter)
    if text_mode == "emboss":
        addition = text_solid(
            text,
            width - 10.0,
            height - 8.0,
            text_depth,
            front_y - 0.05,
            0.0,
            font,
        )
        return panel if addition is None else panel.union(addition)
    raise ValueError(f"Unsupported text mode: {text_mode}")


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    printer = config["printer"]
    installation = config["installation"]
    frame = config["frame"]
    shelf = config["shelf"]
    grid = config["module_grid"]
    levels = config["levels"]

    if config.get("project", {}).get("revision") != "0.2.0":
        raise ValueError("Only revision 0.2.0 configuration may drive the current production model")
    if installation.get("mode") != "floor_standing_with_wall_restraint":
        raise ValueError("Revision 0.2.0 requires floor-standing installation with wall restraint")

    overall_width = float(installation["overall_width"])
    overall_depth = float(installation["overall_depth"])
    overall_height = float(installation["overall_height"])
    clear_width = float(installation["shelf_clear_width"])
    thickness = float(frame["side_thickness"])
    frame_outer_width = clear_width + 2.0 * thickness
    side_depth = float(frame["side_depth"])
    foot_width = float(frame["foot_width"])
    foot_depth = float(frame["foot_depth"])
    wall_gap = float(installation["wall_gap"])
    build_volume = [float(value) for value in printer["build_volume"]]
    if not 580.0 <= overall_width <= 850.0:
        raise ValueError("Overall width is outside the approved 580-850 mm range")
    if not 220.0 <= overall_depth <= 350.0:
        raise ValueError("Overall depth is outside the approved 220-350 mm range")
    if not 1400.0 <= overall_height <= 1900.0:
        raise ValueError("Overall height is outside the approved 1400-1900 mm range")
    if not 480.0 <= float(installation["toilet_clear_width"]) <= 700.0:
        raise ValueError("Toilet clear width is outside the approved range")
    if not 850.0 <= float(installation["toilet_clear_height"]) <= 1150.0:
        raise ValueError("Toilet clear height is outside the approved range")
    if clear_width < float(installation["toilet_clear_width"]):
        raise ValueError("Shelf clear width must not reduce the configured toilet clearance")
    if frame_outer_width + foot_width - thickness > overall_width + 1e-6:
        raise ValueError("Four-foot footprint exceeds the configured overall width")
    if float(installation["clear_wall_width"]) < overall_width:
        raise ValueError("Configured shelf exceeds the measured clear wall width")
    if side_depth > overall_depth or float(shelf["depth"]) > overall_depth:
        raise ValueError("Frame or shelf depth exceeds the configured overall depth")
    if abs(float(shelf["depth"]) - float(installation["shelf_depth"])) > 1e-6:
        raise ValueError("Shelf depth differs between installation and shelf configuration")
    if foot_depth > overall_depth:
        raise ValueError("Foot depth exceeds the configured overall depth")
    if not 0.0 <= wall_gap <= 80.0:
        raise ValueError("Wall gap is outside the approved 0-80 mm range")
    if float(shelf["depth"]) > build_volume[1]:
        raise ValueError("Shelf depth exceeds configured print-bed Y dimension")
    if shelf["top_skin"] < 4.0 * printer["layer_height"]:
        raise ValueError("Shelf top skin is thinner than four print layers")
    if shelf["edge_beam_thickness"] < 10.0 or shelf["total_height"] < 22.0:
        raise ValueError("Shelf beam section is below the validated starting section")
    if float(shelf["nominal_load_kg_evenly_distributed"]) > 4.0:
        raise ValueError("Configured shelf load exceeds the unvalidated 4 kg design target")
    if grid["columns"] < 1:
        raise ValueError("Module grid requires at least one column")
    seam = grid["wide_module_seam"]
    if float(seam["plate_thickness"]) <= 0.0:
        raise ValueError("Wide-module seam plate thickness must be positive")
    if float(seam["plate_length"]) <= 2.0 * float(seam["m3_axis_offset"]):
        raise ValueError("Wide-module seam plate must extend beyond both M3 axes")
    if float(seam["plate_width"]) >= 2.0 * float(seam["station_edge_offset"]):
        raise ValueError("Wide-module seam stations require edge clearance")
    if float(seam["boss_diameter"]) - float(seam["provisional_insert_hole_diameter"]) < 3.6:
        raise ValueError("Wide-module seam boss has less than 1.8 mm radial wall")
    if abs(float(seam["plate_boss_contact_gap"])) > 1.0e-6:
        raise ValueError("Wide-module seam plates must contact their boss tops without a gap")

    pad_t = float(frame["tpu_pad_thickness"])
    side_base_z = pad_t + float(frame["foot_height"]) - float(frame["foot_slot_depth"])
    frame_height = overall_height - side_base_z
    if frame_height <= 0:
        raise ValueError("Frame height above the foot receivers must be positive")
    segment_count = math.ceil(frame_height / float(frame["side_segment_max_height"]))
    segment_body_height = frame_height / segment_count
    segment_print_height = segment_body_height + float(frame["connector_pin_height"])
    if segment_print_height > build_volume[0] + 1e-6 or side_depth > build_volume[1] + 1e-6:
        raise ValueError("Side segment does not fit the configured print bed in its intended orientation")

    shelf_z_values: list[float] = []
    for level in levels:
        shelf_z = float(level["shelf_top_z"])
        if shelf_z < float(installation["toilet_clear_height"]) + 50.0:
            raise ValueError(f"Shelf level {level['name']} enters the toilet/service keep-out")
        if shelf_z > overall_height - 100.0:
            raise ValueError(f"Shelf level {level['name']} is too close to the frame top")
        upper_grid_hole = shelf_z - 20.0
        grid_start = float(frame["grid_start_from_floor"])
        grid_pitch = float(frame["grid_pitch"])
        grid_error = abs((upper_grid_hole - grid_start) / grid_pitch - round((upper_grid_hole - grid_start) / grid_pitch))
        if grid_error > 1e-6:
            raise ValueError(f"Shelf level {level['name']} is not aligned to the frame grid")
        if any(abs(shelf_z - other) < 80.0 for other in shelf_z_values):
            raise ValueError("Shelf levels require at least 80 mm vertical separation")
        shelf_z_values.append(shelf_z)
        used = sum(int(module["span"]) for module in level.get("modules", []))
        if used > grid["columns"]:
            raise ValueError(f"Modules on level {level['name']} exceed the grid")
    sorted_levels = sorted(
        zip(shelf_z_values, levels, strict=True), key=lambda item: item[0]
    )
    for (lower_z, lower), (upper_z, _) in zip(sorted_levels, sorted_levels[1:]):
        module_height = max(
            [float(module.get("height", 0.0)) for module in lower.get("modules", [])]
            or [0.0]
        )
        if lower_z + module_height + 8.0 > upper_z - float(shelf["total_height"]):
            raise ValueError(f"Modules on level {lower['name']} collide with the next shelf")
    tile_count = math.ceil(clear_width / float(shelf["max_tile_width"]))
    tile_width = clear_width / tile_count
    columns = int(grid["columns"])
    gap = float(grid["gap"])
    margin = float(grid["side_margin"])
    column_width = (clear_width - 2.0 * margin - (columns - 1) * gap) / columns
    if column_width <= 0:
        raise ValueError("Module grid has no positive column width")
    split_component_count = 0
    max_monolithic_width = float(grid["max_monolithic_print_width"])
    for level in levels:
        for module in level.get("modules", []):
            span = int(module["span"])
            module_width = span * column_width + (span - 1) * gap
            if module["type"] != "open" and module_width > max_monolithic_width:
                split_component_count += 2 if module["type"] == "drawer" else 1

    restraint_min = float(frame["wall_restraint_hole_min_z"])
    restraint_max = float(frame["wall_restraint_hole_max_z"])
    restraint_pitch = float(frame["wall_restraint_hole_spacing"])
    restraint_hole_z_values: list[float] = []
    hole_z = restraint_min
    while hole_z <= restraint_max + 1e-6:
        restraint_hole_z_values.append(hole_z)
        hole_z += restraint_pitch
    nominal_lower = float(frame["wall_restraint_nominal_lower_hole_z"])
    if nominal_lower not in restraint_hole_z_values or nominal_lower + restraint_pitch not in restraint_hole_z_values:
        raise ValueError("Nominal wall-restraint hole pair is outside the adjustable range")

    return {
        "clear_width": clear_width,
        "shelf_z_values": shelf_z_values,
        "tile_count": tile_count,
        "tile_width": tile_width,
        "column_width": column_width,
        "frame_outer_width": frame_outer_width,
        "side_x": clear_width / 2.0 + thickness / 2.0,
        "side_base_z": side_base_z,
        "frame_height": frame_height,
        "side_segment_count": segment_count,
        "side_segment_body_height": segment_body_height,
        "side_segment_print_height": segment_print_height,
        "floor_contact_count": 4,
        "wall_restraint_count": 2,
        "wall_restraint_hole_z_values": restraint_hole_z_values,
        "split_module_component_count": split_component_count,
        "module_seam_joiner_quantity": split_component_count * 2,
        "module_seam_plate_boss_contact_gap_mm": float(
            seam["plate_boss_contact_gap"]
        ),
        "overall_envelope_mm": [overall_width, overall_depth, overall_height],
    }


def make_side_segment(
    config: dict[str, Any],
    segment_index: int,
    segment_count: int,
) -> tuple[cq.Workplane, float]:
    frame = config["frame"]
    pad_t = float(frame["tpu_pad_thickness"])
    side_base_z = pad_t + float(frame["foot_height"]) - float(frame["foot_slot_depth"])
    total_h = float(config["installation"]["overall_height"]) - side_base_z
    depth = float(frame["side_depth"])
    thickness = float(frame["side_thickness"])
    rail = float(frame["side_rail_width"])
    segment_h = total_h / segment_count
    z_global0 = side_base_z + segment_index * segment_h
    z_global1 = z_global0 + segment_h

    part = centred_box(thickness, rail, segment_h, y=rail / 2.0, z=segment_h / 2.0)
    part = part.union(
        centred_box(thickness, rail, segment_h, y=depth - rail / 2.0, z=segment_h / 2.0)
    )
    part = part.union(centred_box(thickness, depth, rail, y=depth / 2.0, z=rail / 2.0))
    part = part.union(
        centred_box(thickness, depth, rail, y=depth / 2.0, z=segment_h - rail / 2.0)
    )
    part = part.union(
        beam_yz(
            rail,
            rail,
            depth - rail,
            segment_h - rail,
            width=rail * 0.70,
            thickness_x=thickness,
        )
    )

    grid_z = float(frame["grid_start_from_floor"])
    pitch = float(frame["grid_pitch"])
    hole_d = float(frame["grid_hole_diameter"])
    y_rows = (rail / 2.0, depth - rail / 2.0)
    while grid_z <= float(config["installation"]["overall_height"]) - rail / 2.0 + 1e-6:
        if z_global0 + rail / 2.0 <= grid_z <= z_global1 - rail / 2.0:
            local_z = grid_z - z_global0
            for y in y_rows:
                part = part.cut(cylinder_x(hole_d, thickness + 2.0, -thickness / 2.0 - 1.0, y, local_z))
        grid_z += pitch

    pin_x = 8.0
    pin_y = 14.0
    pin_h = float(frame["connector_pin_height"])
    connector_y = (38.0, depth - 38.0)
    clearance = float(frame["connector_clearance"])
    if segment_index < segment_count - 1:
        for y in connector_y:
            pin = centred_box(pin_x, pin_y, pin_h, y=y, z=segment_h + pin_h / 2.0)
            pin = safe_fillet(pin, "|Z", 1.2)
            part = part.union(pin)
            part = part.cut(
                cylinder_x(4.4, thickness + 2.0, -thickness / 2.0 - 1.0, y, segment_h + pin_h / 2.0)
            )
    if segment_index > 0:
        for y in connector_y:
            socket = centred_box(
                pin_x + 2.0 * clearance,
                pin_y + 2.0 * clearance,
                pin_h + clearance,
                y=y,
                z=(pin_h + clearance) / 2.0 - 0.05,
            )
            part = part.cut(socket)
            part = part.cut(
                cylinder_x(4.4, thickness + 2.0, -thickness / 2.0 - 1.0, y, pin_h / 2.0)
            )
    wall_hole_global_z = float(frame["wall_restraint_hole_min_z"])
    wall_hole_max_z = float(frame["wall_restraint_hole_max_z"])
    wall_hole_pitch = float(frame["wall_restraint_hole_spacing"])
    while wall_hole_global_z <= wall_hole_max_z + 1e-6:
        if z_global0 + 8.0 <= wall_hole_global_z <= z_global1 - 8.0:
            part = part.cut(
                cylinder_y(
                    6.2,
                    rail + 2.0,
                    0.0,
                    -1.0,
                    wall_hole_global_z - z_global0,
                )
            )
        wall_hole_global_z += wall_hole_pitch
    if segment_index == 0:
        foot_lock_local_z = float(frame["foot_slot_depth"]) / 2.0
        for y in (rail / 2.0, depth - rail / 2.0):
            part = part.cut(
                cylinder_x(
                    4.5,
                    thickness + 2.0,
                    -thickness / 2.0 - 1.0,
                    y,
                    foot_lock_local_z,
                )
            )
    return part, segment_h


def make_floor_foot(
    config: dict[str, Any], position: str
) -> tuple[cq.Workplane, cq.Workplane, float, float]:
    frame = config["frame"]
    width = float(frame["foot_width"])
    depth = float(frame["foot_depth"])
    height = float(frame["foot_height"])
    pad_t = float(frame["tpu_pad_thickness"])
    slot_depth = float(frame["foot_slot_depth"])
    side_t = float(frame["side_thickness"])
    clearance = float(frame["connector_clearance"])
    rail = float(frame["side_rail_width"])
    if position == "rear":
        slot_y = rail / 2.0
        assembly_y = 0.0
    elif position == "front":
        slot_y = float(frame["side_depth"]) - rail / 2.0 - (float(config["installation"]["overall_depth"]) - depth)
        assembly_y = float(config["installation"]["overall_depth"]) - depth
    else:
        raise ValueError(f"Unsupported foot position: {position}")
    if not rail / 2.0 <= slot_y <= depth - rail / 2.0:
        raise ValueError(f"{position.title()} foot cannot capture the configured frame rail")
    body = centred_box(width, depth, height, y=depth / 2.0, z=pad_t + height / 2.0)
    body = safe_fillet(body, "|Z", 3.0)
    slot = centred_box(
        side_t + 2.0 * clearance,
        rail + 2.0 * clearance,
        slot_depth + 0.2,
        y=slot_y,
        z=pad_t + height - slot_depth / 2.0 + 0.1,
    )
    body = body.cut(slot)
    foot_lock_z = pad_t + height - slot_depth / 2.0
    body = body.cut(
        cylinder_x(4.5, width + 2.0, -width / 2.0 - 1.0, slot_y, foot_lock_z)
    )
    pad = centred_box(width - 4.0, depth - 4.0, pad_t, y=depth / 2.0, z=pad_t / 2.0)
    nub_x = width / 2.0 - 8.0
    nub_y = (20.0, depth - 20.0)
    for x in (-nub_x, nub_x):
        for y in nub_y:
            body = body.cut(cylinder_z(4.4, 3.2, x, y, pad_t - 0.1))
            pad = pad.union(cylinder_z(4.0, 3.0, x, y, pad_t))
    base_z = pad_t + height - slot_depth
    return body, pad, base_z, assembly_y


def make_shelf_bracket(config: dict[str, Any], hand: str) -> cq.Workplane:
    frame = config["frame"]
    shelf = config["shelf"]
    depth = float(shelf["depth"])
    panel_depth = float(frame["side_depth"])
    plate_t = 12.0
    drop = float(frame["grid_pitch"]) + 40.0
    ledge = 36.0
    sign = 1.0 if hand == "left" else -1.0
    profile = [
        (0.0, 0.0),
        (panel_depth, 0.0),
        (panel_depth - 12.0, -18.0),
        (52.0, -drop),
        (0.0, -drop),
    ]
    plate = (
        cq.Workplane("YZ", origin=(-plate_t / 2.0, 0.0, 0.0))
        .polyline(profile)
        .close()
        .extrude(plate_t)
    )
    shelf_total_height = float(shelf["total_height"])
    ledge_box = centred_box(
        ledge,
        depth,
        8.0,
        x=sign * (plate_t / 2.0 + ledge / 2.0),
        y=depth / 2.0,
        z=-shelf_total_height - 4.0,
    )
    part = plate.union(ledge_box)
    for y in (frame["side_rail_width"] / 2.0, panel_depth - frame["side_rail_width"] / 2.0):
        for z in (-20.0, -20.0 - float(frame["grid_pitch"])):
            part = part.cut(cylinder_x(5.6, plate_t + 2.0, -plate_t / 2.0 - 1.0, y, z))
    x_bolt = sign * (plate_t / 2.0 + 6.0)
    edge_axis_y = float(shelf["edge_beam_thickness"]) / 2.0
    for y in (edge_axis_y, depth - edge_axis_y):
        part = part.cut(
            cylinder_z(4.5, 10.0, x_bolt, y, -shelf_total_height - 9.0)
        )
    return part


def shelf_tile_bounds(clear_width: float, tile_count: int, index: int) -> tuple[float, float, float]:
    tile_width = clear_width / tile_count
    x0 = -clear_width / 2.0 + index * tile_width
    return x0, x0 + tile_width, tile_width


def make_shelf_tile(
    config: dict[str, Any],
    clear_width: float,
    tile_count: int,
    tile_index: int,
    include_header_sockets: bool,
) -> cq.Workplane:
    shelf = config["shelf"]
    top = float(shelf["total_height"])
    skin = float(shelf["top_skin"])
    depth = float(shelf["depth"])
    edge = float(shelf["edge_beam_thickness"])
    rib_t = float(shelf["rib_thickness"])
    clearance = float(shelf["fit_clearance"])
    _, _, width = shelf_tile_bounds(clear_width, tile_count, tile_index)
    local_x0 = -width / 2.0

    part = box_from_corner(width, depth, skin, local_x0, 0.0, top - skin)
    part = part.union(box_from_corner(width, edge, top, local_x0, 0.0, 0.0))
    part = part.union(box_from_corner(width, edge, top, local_x0, depth - edge, 0.0))
    for y in (depth / 3.0, 2.0 * depth / 3.0):
        part = part.union(
            centred_box(width, rib_t, top - 3.0, y=y, z=(top - 3.0) / 2.0)
        )
    cross_count = max(0, int(width // float(shelf["cross_rib_spacing"])))
    for index in range(1, cross_count + 1):
        x = local_x0 + index * width / (cross_count + 1)
        part = part.union(centred_box(rib_t, depth, 11.0, x=x, y=depth / 2.0, z=5.5))
    rear_lip_h = float(shelf["rear_lip_height"])
    part = part.union(
        centred_box(width, 3.0, rear_lip_h, y=1.5, z=top + rear_lip_h / 2.0)
    )
    module_front_y = 10.0 + float(config["module_grid"]["default_depth"])
    module_stop_y = module_front_y + 6.0
    if module_stop_y + 1.5 >= depth:
        raise ValueError("Module front stop does not fit on the configured shelf depth")
    part = part.union(
        centred_box(width, 3.0, 6.0, y=module_stop_y, z=top + 3.0)
    )

    tongue_x = 8.0
    tongue_y = 24.0
    tongue_z = 6.0
    tongue_overlap = 0.6
    tongue_centers_y = (edge / 2.0, depth - edge / 2.0)
    if tile_index < tile_count - 1:
        for y in tongue_centers_y:
            part = part.union(
                centred_box(
                    tongue_x + tongue_overlap,
                    tongue_y,
                    tongue_z,
                    x=width / 2.0 + (tongue_x - tongue_overlap) / 2.0,
                    y=y,
                    z=top - 10.0,
                )
            )
    if tile_index > 0:
        for y in tongue_centers_y:
            part = part.cut(
                centred_box(
                    tongue_x + 2.0 * clearance,
                    tongue_y + 2.0 * clearance,
                    tongue_z + 2.0 * clearance,
                    x=-width / 2.0 + tongue_x / 2.0 - 0.1,
                    y=y,
                    z=top - 10.0,
                )
            )

    joiner_holes_x: list[float] = []
    if tile_index > 0:
        joiner_holes_x.append(-width / 2.0 + 30.0)
    if tile_index < tile_count - 1:
        joiner_holes_x.append(width / 2.0 - 30.0)
    for x in joiner_holes_x:
        for y in (edge / 2.0, depth - edge / 2.0):
            part = part.cut(cylinder_z(5.4, 8.2, x, y, -0.1))

    if tile_index in (0, tile_count - 1):
        x_insert = -width / 2.0 + 18.0 if tile_index == 0 else width / 2.0 - 18.0
        for y in (edge / 2.0, depth - edge / 2.0):
            part = part.cut(cylinder_z(5.4, 8.2, x_insert, y, -0.1))

    fascia_h = top - 6.0
    panel_t = 2.0
    rail_lip = 2.2
    part = part.union(
        centred_box(width, rail_lip, 2.0, y=depth + rail_lip / 2.0, z=3.0)
    )
    part = part.union(
        centred_box(width, rail_lip, 2.0, y=depth + rail_lip / 2.0, z=top - 3.0)
    )
    panel_clearance = panel_t + 0.35
    part = part.cut(
        centred_box(
            width + 0.4,
            panel_clearance,
            fascia_h,
            y=depth + panel_clearance / 2.0 - 0.1,
            z=top / 2.0,
        )
    )

    if include_header_sockets:
        header = config["personalization"]["header"]
        for x_global in (-70.0, 70.0):
            tile_global_x0, tile_global_x1, _ = shelf_tile_bounds(clear_width, tile_count, tile_index)
            if tile_global_x0 + 8.0 < x_global < tile_global_x1 - 8.0:
                local_x = x_global - (tile_global_x0 + tile_global_x1) / 2.0
                part = part.union(
                    centred_box(14.0, 12.0, 12.6, x=local_x, y=6.0, z=top + 5.7)
                )
                part = part.cut(
                    centred_box(8.5, 6.5, 13.2, x=local_x, y=6.0, z=top + 6.5)
                )
    return part


def make_shelf_joiner(config: dict[str, Any]) -> cq.Workplane:
    shelf = config["shelf"]
    length = float(shelf["joiner_length"])
    width = float(shelf["joiner_width"])
    height = float(shelf["joiner_height"])
    part = centred_box(length, width, height, z=height / 2.0)
    part = safe_fillet(part, "|Z", 2.0)
    for x in (-30.0, 30.0):
        part = part.cut(cylinder_z(4.5, height + 2.0, x, 0.0, -1.0))
    return part


def make_fascia(
    config: dict[str, Any],
    width: float,
    finish: str,
    label: str,
) -> cq.Workplane:
    shelf = config["shelf"]
    personalization = config["personalization"]
    height = float(shelf["total_height"]) - 6.6
    thickness = 2.0
    panel = centred_box(width - 0.8, thickness, height)
    panel = decorate_front(
        panel,
        width - 0.8,
        height,
        thickness,
        finish,
        label,
        personalization["text_mode"],
        float(personalization["text_depth"]),
        personalization["text_font"],
    )
    return panel


def hollow_open_box(
    width: float,
    depth: float,
    height: float,
    wall: float,
    bottom: float,
) -> cq.Workplane:
    outer = centred_box(width, depth, height, y=depth / 2.0, z=height / 2.0)
    inner = centred_box(
        width - 2.0 * wall,
        depth - 2.0 * wall,
        height - bottom + 1.0,
        y=depth / 2.0,
        z=bottom + (height - bottom + 1.0) / 2.0,
    )
    return outer.cut(inner)


def add_module_label(
    part: cq.Workplane,
    width: float,
    depth: float,
    height: float,
    label: str,
    finish: str,
    config: dict[str, Any],
) -> cq.Workplane:
    if not label and finish == "smooth":
        return part
    panel_t = 1.8
    panel_h = min(height - 8.0, 44.0)
    panel = centred_box(width - 8.0, panel_t, panel_h)
    panel = decorate_front(
        panel,
        width - 8.0,
        panel_h,
        panel_t,
        finish,
        label,
        config["personalization"]["text_mode"],
        float(config["personalization"]["text_depth"]),
        config["personalization"]["text_font"],
    )
    panel = panel.translate((0.0, depth + panel_t / 2.0 - 0.1, height / 2.0))
    return part.union(panel)


def make_bin_module(
    config: dict[str, Any],
    width: float,
    height: float,
    label: str,
    finish: str,
) -> cq.Workplane:
    grid = config["module_grid"]
    depth = float(grid["default_depth"])
    wall = float(grid["wall"])
    bottom = float(grid["bottom"])
    part = hollow_open_box(width, depth, height, wall, bottom)
    scoop = centred_box(min(72.0, width * 0.44), wall + 2.0, 28.0, y=depth - wall / 2.0, z=height - 10.0)
    scoop = safe_fillet(scoop, "|Y", 8.0)
    part = part.cut(scoop)
    return add_module_label(part, width, depth, height, label, finish, config)


def make_tray_module(
    config: dict[str, Any],
    width: float,
    height: float,
    label: str,
    finish: str,
) -> cq.Workplane:
    grid = config["module_grid"]
    return add_module_label(
        hollow_open_box(
            width,
            float(grid["default_depth"]),
            max(26.0, height),
            float(grid["wall"]),
            float(grid["bottom"]),
        ),
        width,
        float(grid["default_depth"]),
        max(26.0, height),
        label,
        finish,
        config,
    )


def make_drawer_module(
    config: dict[str, Any],
    width: float,
    height: float,
    label: str,
    finish: str,
) -> tuple[cq.Workplane, cq.Workplane]:
    grid = config["module_grid"]
    depth = float(grid["default_depth"])
    wall = float(grid["wall"])
    side_c = float(grid["drawer_clearance_each_side"])
    vertical_c = float(grid["drawer_clearance_vertical"])
    rear_c = float(grid["drawer_rear_clearance"])

    housing = centred_box(width, depth, height, y=depth / 2.0, z=height / 2.0)
    cavity = centred_box(
        width - 2.0 * wall,
        depth - wall + 1.0,
        height - 2.0 * wall,
        y=wall + (depth - wall + 1.0) / 2.0,
        z=height / 2.0,
    )
    housing = housing.cut(cavity)
    drawer_w = width - 2.0 * wall - 2.0 * side_c
    drawer_d = depth - wall - rear_c
    drawer_h = height - 2.0 * wall - vertical_c
    drawer = hollow_open_box(
        drawer_w,
        drawer_d,
        drawer_h,
        max(2.2, wall - 0.3),
        max(2.2, grid["bottom"] - 0.3),
    )
    front_t = 3.0
    front = centred_box(width - 1.0, front_t, height - 1.0)
    front = decorate_front(
        front,
        width - 1.0,
        height - 1.0,
        front_t,
        finish,
        label,
        config["personalization"]["text_mode"],
        float(config["personalization"]["text_depth"]),
        config["personalization"]["text_font"],
    )
    front_z = height / 2.0 - (wall + vertical_c / 2.0)
    front = front.translate((0.0, drawer_d + front_t / 2.0, front_z))
    neck = centred_box(
        drawer_w - 8.0,
        0.8,
        drawer_h - 8.0,
        y=drawer_d - 0.2,
        z=drawer_h / 2.0,
    )
    drawer = drawer.union(neck).union(front)
    finger = centred_box(
        min(62.0, width * 0.40),
        front_t + 2.0,
        12.0,
        y=drawer_d + front_t / 2.0,
        z=drawer_h - 6.0,
    )
    finger = safe_fillet(finger, "|Y", 4.0)
    drawer = drawer.cut(finger)
    return housing, drawer


def make_divider_module(config: dict[str, Any], width: float, height: float) -> cq.Workplane:
    depth = float(config["module_grid"]["default_depth"])
    base = centred_box(width, depth, 3.0, y=depth / 2.0, z=1.5)
    divider = centred_box(3.0, depth, height, y=depth / 2.0, z=height / 2.0)
    return base.union(divider)


def make_hanger(config: dict[str, Any]) -> cq.Workplane:
    shelf = config["shelf"]
    beam_t = float(shelf["edge_beam_thickness"])
    top_h = float(shelf["total_height"])
    clearance = float(shelf["fit_clearance"])
    width = 18.0
    profile = [
        (0.0, 0.0),
        (beam_t + clearance + 5.0, 0.0),
        (beam_t + clearance + 5.0, -top_h - 42.0),
        (beam_t + clearance - 5.0, -top_h - 52.0),
        (beam_t + clearance - 12.0, -top_h - 42.0),
        (beam_t + clearance - 6.0, -top_h - 32.0),
        (beam_t + clearance - 2.6, -top_h - 36.0),
        (beam_t + clearance - 2.6, -5.0),
        (4.0, -5.0),
        (4.0, -top_h + 2.0),
        (0.0, -top_h + 2.0),
    ]
    return cq.Workplane("YZ", origin=(-width / 2.0, 0.0, 0.0)).polyline(profile).close().extrude(width)


def make_header_backer(config: dict[str, Any]) -> tuple[cq.Workplane, cq.Workplane]:
    header = config["personalization"]["header"]
    personalization = config["personalization"]
    outer_w = float(header["outer_width"])
    outer_h = float(header["outer_height"])
    backer_t = float(header["backer_thickness"])
    insert_w = float(header["insert_width"])
    insert_h = float(header["insert_height"])
    insert_t = float(header["insert_base_thickness"])
    backer = centred_box(outer_w, backer_t, outer_h)
    recess = centred_box(
        insert_w + 0.5,
        insert_t + 0.5,
        insert_h + 0.5,
        y=backer_t / 2.0 + 0.1,
    )
    backer = backer.cut(recess)
    foot_h = 8.4
    for x in (-70.0, 70.0):
        backer = backer.union(
            centred_box(
                8.0,
                6.0,
                foot_h,
                x=x,
                y=-backer_t / 2.0 + 3.0,
                z=-outer_h / 2.0 - foot_h / 2.0 + 0.2,
            )
        )
    insert = centred_box(insert_w, insert_t, insert_h)
    insert = decorate_front(
        insert,
        insert_w,
        insert_h,
        insert_t,
        header["finish"],
        header["text"],
        header["text_mode"],
        float(personalization["text_depth"]),
        personalization["text_font"],
    )
    return backer, insert


def make_anti_tip_bracket(config: dict[str, Any]) -> cq.Workplane:
    frame = config["frame"]
    width = float(frame["wall_restraint_bracket_width"])
    height = float(frame["wall_restraint_bracket_height"])
    depth = float(config["installation"]["wall_gap"])
    if depth <= 0.0:
        raise ValueError("The current printable wall-restraint spacer requires a positive wall gap")
    part = centred_box(width, depth, height, y=depth / 2.0, z=height / 2.0)
    hole_spacing = float(frame["wall_restraint_hole_spacing"])
    lower_hole = (height - hole_spacing) / 2.0
    for z in (lower_hole, lower_hole + hole_spacing):
        part = part.cut(
            cylinder_y(6.2, depth + 2.0, 0.0, -1.0, z)
        )
    return part


def make_fit_coupon(config: dict[str, Any]) -> cq.Workplane:
    clearances = (0.20, 0.30, 0.40, 0.50)
    base = centred_box(112.0, 42.0, 3.0, z=1.5)
    pin_x = 8.0
    pin_y = 14.0
    for index, clearance in enumerate(clearances):
        x = -42.0 + index * 28.0
        socket_block = centred_box(20.0, 24.0, 14.0, x=x, z=10.0)
        socket = centred_box(
            pin_x + 2.0 * clearance,
            pin_y + 2.0 * clearance,
            12.2,
            x=x,
            z=10.0,
        )
        base = base.union(socket_block.cut(socket))
        pin = centred_box(pin_x, pin_y, 12.0, x=x, y=-32.0, z=9.0)
        base = base.union(pin)
    return base


def make_module_seam_joiner(config: dict[str, Any]) -> cq.Workplane:
    """Create the removable M3 bridge used by center-split wide modules."""
    seam = config["module_grid"]["wide_module_seam"]
    length = float(seam["plate_length"])
    width = float(seam["plate_width"])
    height = float(seam["plate_thickness"])
    axis_offset = float(seam["m3_axis_offset"])
    hole_diameter = float(seam["plate_hole_diameter"])
    part = centred_box(length, width, height, z=height / 2.0)
    part = safe_fillet(part, "|Z", 2.0)
    for x in (-axis_offset, axis_offset):
        part = part.cut(cylinder_z(hole_diameter, height + 2.0, x, 0.0, -1.0))
    return part


def make_module_seam_coupon(config: dict[str, Any]) -> cq.Workplane:
    """Small three-body coupon for the provisional M3 wide-module seam."""
    seam = config["module_grid"]["wide_module_seam"]
    half_width = 40.0
    depth = 40.0
    height = 8.0
    assembly_gap = 0.30
    axis_offset = float(seam["m3_axis_offset"])
    insert_diameter = float(seam["provisional_insert_hole_diameter"])
    left = centred_box(
        half_width,
        depth,
        height,
        x=-(half_width + assembly_gap) / 2.0,
        z=height / 2.0,
    )
    right = centred_box(
        half_width,
        depth,
        height,
        x=(half_width + assembly_gap) / 2.0,
        z=height / 2.0,
    )
    for x in (-axis_offset, axis_offset):
        if x < 0:
            left = left.cut(cylinder_z(insert_diameter, height + 2.0, x, 0.0, -1.0))
        else:
            right = right.cut(cylinder_z(insert_diameter, height + 2.0, x, 0.0, -1.0))
    joiner = make_module_seam_joiner(config).translate((0.0, -34.0, 0.0))
    return left.union(right).union(joiner)


def make_floor_interface_coupon(config: dict[str, Any]) -> cq.Workplane:
    """Representative foot receiver, TPU retention and lower-rail lock coupon."""
    foot, pad, _, _ = make_floor_foot(config, "rear")
    frame = config["frame"]
    side_t = float(frame["side_thickness"])
    rail = float(frame["side_rail_width"])
    rail_stub = centred_box(side_t, rail, 40.0, y=rail / 2.0, z=20.0)
    rail_stub = rail_stub.cut(
        cylinder_x(
            4.5,
            side_t + 2.0,
            -side_t / 2.0 - 1.0,
            rail / 2.0,
            float(frame["foot_slot_depth"]) / 2.0,
        )
    )
    foot_print = place_on_bed(foot)
    pad_print = place_on_bed(pad).translate((50.0, 0.0, 0.0))
    rail_print = orient_side_on_bed(rail_stub).translate((100.0, 0.0, 0.0))
    return foot_print.union(pad_print).union(rail_print)


def split_wide_module_for_print(
    config: dict[str, Any],
    part: cq.Workplane,
    width: float,
    depth: float,
    height: float,
    joiner_side: str,
) -> tuple[cq.Workplane, cq.Workplane, cq.Workplane, list[tuple[float, float, float]]]:
    """Add two serviceable seam stations, then return left/right print bodies.

    The joining bars sit inside open modules/drawers and above drawer housings.
    Their final M3 insert or captive-nut detail remains coupon-controlled.
    """
    seam = config["module_grid"]["wide_module_seam"]
    boss_height = float(seam["boss_height"])
    boss_diameter = float(seam["boss_diameter"])
    insert_diameter = float(seam["provisional_insert_hole_diameter"])
    station_edge_offset = float(seam["station_edge_offset"])
    contact_gap = float(seam["plate_boss_contact_gap"])
    station_y = (station_edge_offset, depth - station_edge_offset)
    if joiner_side == "bottom-inside":
        boss_z0 = 0.0
        joiner_z = boss_height + contact_gap
        hole_z0 = 0.8
    elif joiner_side == "top-outside":
        boss_z0 = height
        joiner_z = height + boss_height + contact_gap
        hole_z0 = height + 0.8
    else:
        raise ValueError(f"Unsupported wide-module joiner side: {joiner_side}")

    prepared = part
    for y in station_y:
        for x in (-float(seam["m3_axis_offset"]), float(seam["m3_axis_offset"])):
            boss = cylinder_z(boss_diameter, boss_height, x, y, boss_z0)
            prepared = prepared.union(boss)
            prepared = prepared.cut(
                cylinder_z(insert_diameter, boss_height + 0.3, x, y, hole_z0)
            )

    margin = 20.0
    split_height = height + 2.0 * margin + 12.0
    split_depth = depth + 2.0 * margin + 12.0
    left_cutter = box_from_corner(
        width / 2.0 + margin,
        split_depth,
        split_height,
        -width / 2.0 - margin,
        -margin,
        -margin,
    )
    right_cutter = box_from_corner(
        width / 2.0 + margin,
        split_depth,
        split_height,
        0.0,
        -margin,
        -margin,
    )
    left = prepared.intersect(left_cutter)
    right = prepared.intersect(right_cutter)
    placements = [(0.0, y, joiner_z) for y in station_y]
    return prepared, left, right, placements


def build_model(config: dict[str, Any]) -> BuildResult:
    derived = validate_config(config)
    frame = config["frame"]
    shelf = config["shelf"]
    grid = config["module_grid"]
    personalization = config["personalization"]
    clear_width = float(derived["clear_width"])
    tile_count = int(derived["tile_count"])
    segment_count = int(derived["side_segment_count"])
    frame_outer_width = float(derived["frame_outer_width"])
    side_t = float(frame["side_thickness"])
    shelf_depth = float(shelf["depth"])
    tile_width = clear_width / tile_count
    side_x = float(derived["side_x"])
    side_base_z = float(derived["side_base_z"])

    print_parts: list[PartRecord] = []
    assembly_parts: list[AssemblyRecord] = []

    rear_foot, rear_pad, rear_base_z, rear_foot_y = make_floor_foot(config, "rear")
    front_foot, front_pad, front_base_z, front_foot_y = make_floor_foot(config, "front")
    if abs(rear_base_z - front_base_z) > 1e-9 or abs(side_base_z - rear_base_z) > 1e-9:
        raise ValueError("Front and rear foot receivers must establish one frame floor datum")
    print_parts.extend(
        [
            PartRecord("rear_floor_foot_print_2x", place_on_bed(rear_foot), 2, "PETG", "bottom down", "frame"),
            PartRecord("front_floor_foot_print_2x", place_on_bed(front_foot), 2, "PETG", "bottom down", "frame"),
            PartRecord("rear_tpu_foot_pad_print_2x", place_on_bed(rear_pad), 2, "TPU 95A", "flat", "frame"),
            PartRecord("front_tpu_foot_pad_print_2x", place_on_bed(front_pad), 2, "TPU 95A", "flat", "frame"),
        ]
    )
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        for position, foot, pad, assembly_y in (
            ("rear", rear_foot, rear_pad, rear_foot_y),
            ("front", front_foot, front_pad, front_foot_y),
        ):
            assembly_parts.append(
                AssemblyRecord(
                    f"{label}_{position}_floor_foot",
                    foot.translate((sign * side_x, assembly_y, 0.0)),
                    (0.18, 0.24, 0.22),
                )
            )
            assembly_parts.append(
                AssemblyRecord(
                    f"{label}_{position}_tpu_pad",
                    pad.translate((sign * side_x, assembly_y, 0.0)),
                    (0.08, 0.10, 0.10),
                )
            )

    side_segment_h = float(derived["side_segment_body_height"])
    for index in range(segment_count):
        segment, _ = make_side_segment(config, index, segment_count)
        print_parts.append(
            PartRecord(
                f"side_segment_{index + 1:02d}_print_2x",
                orient_side_on_bed(segment),
                2,
                "PETG",
                "large YZ face on bed",
                "frame",
            )
        )
        for sign, label in ((-1.0, "left"), (1.0, "right")):
            assembly_parts.append(
                AssemblyRecord(
                    f"{label}_side_segment_{index + 1}",
                    segment.translate((sign * side_x, 0.0, side_base_z + index * side_segment_h)),
                    (0.22, 0.32, 0.29),
                )
            )

    left_bracket = make_shelf_bracket(config, "left")
    right_bracket = make_shelf_bracket(config, "right")
    print_parts.extend(
        [
            PartRecord("shelf_bracket_left_print", orient_side_on_bed(left_bracket), len(config["levels"]), "PETG", "large face on bed", "bracket"),
            PartRecord("shelf_bracket_right_print", orient_side_on_bed(right_bracket), len(config["levels"]), "PETG", "large face on bed", "bracket"),
        ]
    )

    module_seam_joiner = make_module_seam_joiner(config)
    module_seam_joiner_quantity = int(derived["module_seam_joiner_quantity"])
    if module_seam_joiner_quantity:
        print_parts.append(
            PartRecord(
                "wide_module_m3_seam_joiner_print",
                place_on_bed(module_seam_joiner),
                module_seam_joiner_quantity,
                "PETG",
                "flat",
                "module",
            )
        )

    joiner = make_shelf_joiner(config)
    joiner_quantity = max(0, tile_count - 1) * 2 * len(config["levels"])
    print_parts.append(
        PartRecord("shelf_seam_joiner_print", place_on_bed(joiner), joiner_quantity, "PETG", "flat", "shelf")
    )

    module_color = (0.72, 0.56, 0.38)
    accent_color = (0.56, 0.23, 0.15)
    for level_index, level in enumerate(config["levels"]):
        shelf_top_z = float(derived["shelf_z_values"][level_index])
        bracket_plate_t = 12.0
        left_bracket_x = -frame_outer_width / 2.0 + side_t + bracket_plate_t / 2.0
        right_bracket_x = frame_outer_width / 2.0 - side_t - bracket_plate_t / 2.0
        assembly_parts.extend(
            [
                AssemblyRecord(
                    f"level_{level_index + 1}_left_bracket",
                    left_bracket.translate((left_bracket_x, 0.0, shelf_top_z)),
                    (0.16, 0.20, 0.19),
                ),
                AssemblyRecord(
                    f"level_{level_index + 1}_right_bracket",
                    right_bracket.translate((right_bracket_x, 0.0, shelf_top_z)),
                    (0.16, 0.20, 0.19),
                ),
            ]
        )
        include_header_sockets = bool(
            personalization["header"]["enabled"]
            and int(personalization["header"]["mount_level"]) == level_index
        )
        for tile_index in range(tile_count):
            tile = make_shelf_tile(
                config,
                clear_width,
                tile_count,
                tile_index,
                include_header_sockets,
            )
            print_parts.append(
                PartRecord(
                    f"level_{level_index + 1:02d}_shelf_tile_{tile_index + 1:02d}_print",
                    place_on_bed(tile.rotate((0, 0, 0), (1, 0, 0), 180)),
                    1,
                    "PETG",
                    "top face on bed",
                    "shelf",
                )
            )
            x0, x1, _ = shelf_tile_bounds(clear_width, tile_count, tile_index)
            x_center = (x0 + x1) / 2.0
            assembly_parts.append(
                AssemblyRecord(
                    f"level_{level_index + 1}_tile_{tile_index + 1}",
                    tile.translate((x_center, 0.0, shelf_top_z - shelf["total_height"])),
                    (0.42, 0.48, 0.43),
                )
            )
            label = level["fascia_label"] if tile_index == tile_count // 2 else ""
            fascia = make_fascia(config, tile_width, level["fascia_finish"], label)
            print_parts.append(
                PartRecord(
                    f"level_{level_index + 1:02d}_fascia_{tile_index + 1:02d}_{level['fascia_finish']}_print",
                    orient_fascia_on_bed(fascia),
                    1,
                    "PLA/PETG decorative",
                    "front face selected by finish",
                    "decor",
                )
            )
            fascia_assembly = fascia.translate(
                (
                    x_center,
                    shelf_depth + 1.0,
                    shelf_top_z - shelf["total_height"] / 2.0,
                )
            )
            assembly_parts.append(
                AssemblyRecord(
                    f"level_{level_index + 1}_fascia_{tile_index + 1}",
                    fascia_assembly,
                    accent_color,
                )
            )

        for seam_index in range(tile_count - 1):
            seam_x = -clear_width / 2.0 + (seam_index + 1) * tile_width
            for y in (shelf["edge_beam_thickness"] / 2.0, shelf_depth - shelf["edge_beam_thickness"] / 2.0):
                assembly_parts.append(
                    AssemblyRecord(
                        f"level_{level_index + 1}_joiner_{seam_index + 1}_{int(y)}",
                        joiner.translate((seam_x, y, shelf_top_z - shelf["total_height"] - shelf["joiner_height"])),
                        (0.13, 0.16, 0.15),
                    )
                )

        columns = int(grid["columns"])
        gap = float(grid["gap"])
        margin = float(grid["side_margin"])
        column_w = (clear_width - 2.0 * margin - (columns - 1) * gap) / columns
        cursor = 0
        for module_index, module in enumerate(level.get("modules", [])):
            span = int(module["span"])
            module_w = span * column_w + (span - 1) * gap
            module_x0 = -clear_width / 2.0 + margin + cursor * (column_w + gap)
            module_x = module_x0 + module_w / 2.0
            module_type = module["type"]
            module_h = float(module.get("height", 80.0))
            label = module.get("label", "")
            finish = module.get("finish", "smooth")
            if module_type == "bin":
                body = make_bin_module(config, module_w, module_h, label, finish)
                if module_w > float(grid["max_monolithic_print_width"]):
                    body, left_body, right_body, joiner_placements = split_wide_module_for_print(
                        config, body, module_w, float(grid["default_depth"]), module_h, "bottom-inside"
                    )
                    body = cq.Workplane(
                        obj=cq.Compound.makeCompound([left_body.val(), right_body.val()])
                    )
                    print_parts.extend(
                        [
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_bin_left_print",
                                place_on_bed(left_body),
                                1,
                                "PETG",
                                "bottom down",
                                "module",
                            ),
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_bin_right_print",
                                place_on_bed(right_body),
                                1,
                                "PETG",
                                "bottom down",
                                "module",
                            ),
                        ]
                    )
                    for joiner_index, (_, joiner_y, joiner_z) in enumerate(joiner_placements, start=1):
                        assembly_parts.append(
                            AssemblyRecord(
                                f"level_{level_index + 1}_bin_{module_index + 1}_seam_joiner_{joiner_index}",
                                module_seam_joiner.translate(
                                    (module_x, 10.0 + joiner_y, shelf_top_z + joiner_z)
                                ),
                                (0.13, 0.16, 0.15),
                            )
                        )
                else:
                    print_parts.append(
                        PartRecord(
                            f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_bin_print",
                            place_on_bed(body),
                            1,
                            "PETG",
                            "bottom down",
                            "module",
                        )
                    )
                assembly_parts.append(
                    AssemblyRecord(
                        f"level_{level_index + 1}_bin_{module_index + 1}",
                        body.translate((module_x, 10.0, shelf_top_z)),
                        module_color,
                    )
                )
            elif module_type == "tray":
                body = make_tray_module(config, module_w, module_h, label, finish)
                if module_w > float(grid["max_monolithic_print_width"]):
                    body, left_body, right_body, joiner_placements = split_wide_module_for_print(
                        config, body, module_w, float(grid["default_depth"]), max(26.0, module_h), "bottom-inside"
                    )
                    body = cq.Workplane(
                        obj=cq.Compound.makeCompound([left_body.val(), right_body.val()])
                    )
                    print_parts.extend(
                        [
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_tray_left_print",
                                place_on_bed(left_body), 1, "PETG", "bottom down", "module"
                            ),
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_tray_right_print",
                                place_on_bed(right_body), 1, "PETG", "bottom down", "module"
                            ),
                        ]
                    )
                    for joiner_index, (_, joiner_y, joiner_z) in enumerate(joiner_placements, start=1):
                        assembly_parts.append(
                            AssemblyRecord(
                                f"level_{level_index + 1}_tray_{module_index + 1}_seam_joiner_{joiner_index}",
                                module_seam_joiner.translate(
                                    (module_x, 10.0 + joiner_y, shelf_top_z + joiner_z)
                                ),
                                (0.13, 0.16, 0.15),
                            )
                        )
                else:
                    print_parts.append(
                        PartRecord(
                            f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_tray_print",
                            place_on_bed(body),
                            1,
                            "PETG",
                            "bottom down",
                            "module",
                        )
                    )
                assembly_parts.append(
                    AssemblyRecord(
                        f"level_{level_index + 1}_tray_{module_index + 1}",
                        body.translate((module_x, 10.0, shelf_top_z)),
                        module_color,
                    )
                )
            elif module_type == "drawer":
                housing, drawer = make_drawer_module(config, module_w, module_h, label, finish)
                drawer_translation = (
                    module_x,
                    10.0 + grid["wall"] + grid["drawer_rear_clearance"],
                    shelf_top_z + grid["wall"] + grid["drawer_clearance_vertical"] / 2.0,
                )
                if module_w > float(grid["max_monolithic_print_width"]):
                    housing, housing_left, housing_right, housing_joiners = split_wide_module_for_print(
                        config, housing, module_w, float(grid["default_depth"]), module_h, "top-outside"
                    )
                    drawer_height = (
                        module_h
                        - 2.0 * float(grid["wall"])
                        - float(grid["drawer_clearance_vertical"])
                    )
                    drawer_depth = (
                        float(grid["default_depth"])
                        - float(grid["wall"])
                        - float(grid["drawer_rear_clearance"])
                    )
                    drawer, drawer_left, drawer_right, drawer_joiners = split_wide_module_for_print(
                        config, drawer, module_w, drawer_depth, drawer_height, "bottom-inside"
                    )
                    housing = cq.Workplane(
                        obj=cq.Compound.makeCompound([housing_left.val(), housing_right.val()])
                    )
                    drawer = cq.Workplane(
                        obj=cq.Compound.makeCompound([drawer_left.val(), drawer_right.val()])
                    )
                    print_parts.extend(
                        [
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_drawer_housing_left_print",
                                place_on_bed(housing_left.rotate((0, 0, 0), (1, 0, 0), 90)),
                                1,
                                "PETG",
                                "rear wall on bed; front opening up",
                                "module",
                            ),
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_drawer_housing_right_print",
                                place_on_bed(housing_right.rotate((0, 0, 0), (1, 0, 0), 90)),
                                1,
                                "PETG",
                                "rear wall on bed; front opening up",
                                "module",
                            ),
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_drawer_left_print",
                                place_on_bed(drawer_left),
                                1,
                                "PETG",
                                "bottom down",
                                "module",
                            ),
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_drawer_right_print",
                                place_on_bed(drawer_right),
                                1,
                                "PETG",
                                "bottom down",
                                "module",
                            ),
                        ]
                    )
                    for joiner_index, (_, joiner_y, joiner_z) in enumerate(housing_joiners, start=1):
                        assembly_parts.append(
                            AssemblyRecord(
                                f"level_{level_index + 1}_drawer_housing_{module_index + 1}_seam_joiner_{joiner_index}",
                                module_seam_joiner.translate(
                                    (module_x, 10.0 + joiner_y, shelf_top_z + joiner_z)
                                ),
                                (0.13, 0.16, 0.15),
                            )
                        )
                    for joiner_index, (_, joiner_y, joiner_z) in enumerate(drawer_joiners, start=1):
                        assembly_parts.append(
                            AssemblyRecord(
                                f"level_{level_index + 1}_drawer_{module_index + 1}_seam_joiner_{joiner_index}",
                                module_seam_joiner.translate(
                                    (
                                        drawer_translation[0],
                                        drawer_translation[1] + joiner_y,
                                        drawer_translation[2] + joiner_z,
                                    )
                                ),
                                (0.13, 0.16, 0.15),
                            )
                        )
                else:
                    print_parts.extend(
                        [
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_drawer_housing_print",
                                place_on_bed(housing.rotate((0, 0, 0), (1, 0, 0), 90)),
                                1,
                                "PETG",
                                "rear wall on bed; front opening up",
                                "module",
                            ),
                            PartRecord(
                                f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_drawer_print",
                                place_on_bed(drawer),
                                1,
                                "PETG",
                                "bottom down",
                                "module",
                            ),
                        ]
                    )
                assembly_parts.extend(
                    [
                        AssemblyRecord(
                            f"level_{level_index + 1}_drawer_housing_{module_index + 1}",
                            housing.translate((module_x, 10.0, shelf_top_z)),
                            (0.39, 0.45, 0.41),
                        ),
                        AssemblyRecord(
                            f"level_{level_index + 1}_drawer_{module_index + 1}",
                            drawer.translate(drawer_translation),
                            module_color,
                        ),
                    ]
                )
            elif module_type == "divider":
                body = make_divider_module(config, module_w, module_h)
                print_parts.append(
                    PartRecord(
                        f"level_{level_index + 1:02d}_module_{module_index + 1:02d}_divider_print",
                        place_on_bed(body),
                        1,
                        "PETG",
                        "base down",
                        "module",
                    )
                )
                assembly_parts.append(
                    AssemblyRecord(
                        f"level_{level_index + 1}_divider_{module_index + 1}",
                        body.translate((module_x, 10.0, shelf_top_z)),
                        module_color,
                    )
                )
            elif module_type != "open":
                raise ValueError(f"Unsupported module type: {module_type}")
            cursor += span

        hanger_count = int(level.get("hangers", 0))
        if hanger_count:
            hanger = make_hanger(config)
            print_parts.append(
                PartRecord(
                    f"level_{level_index + 1:02d}_hanger_print",
                    orient_side_on_bed(hanger),
                    hanger_count,
                    "PETG",
                    "large face on bed",
                    "module",
                )
            )
            for hanger_index in range(hanger_count):
                x = (hanger_index - (hanger_count - 1) / 2.0) * 70.0
                placed = hanger.rotate((0, 0, 0), (0, 0, 1), 180).translate(
                    (x, shelf_depth + shelf["edge_beam_thickness"], shelf_top_z)
                )
                assembly_parts.append(
                    AssemblyRecord(
                        f"level_{level_index + 1}_hanger_{hanger_index + 1}",
                        placed,
                        accent_color,
                    )
                )

    if personalization["header"]["enabled"]:
        backer, insert = make_header_backer(config)
        print_parts.append(
            PartRecord(
                "personalized_header_backer_print",
                orient_fascia_on_bed(backer),
                1,
                "PETG",
                "rear face on bed",
                "decor",
            )
        )
        mount_level = int(personalization["header"]["mount_level"])
        shelf_top_z = float(derived["shelf_z_values"][mount_level])
        outer_h = float(personalization["header"]["outer_height"])
        backer_t = float(personalization["header"]["backer_thickness"])
        backer_y = 5.5
        backer_placed = backer.translate((0.0, backer_y, shelf_top_z + outer_h / 2.0 + 8.0))
        insert_placed = insert.translate(
            (
                0.0,
                backer_y + backer_t / 2.0,
                shelf_top_z + outer_h / 2.0 + 8.0,
            )
        )
        assembly_parts.append(
            AssemblyRecord("header_backer", backer_placed, (0.34, 0.39, 0.36))
        )
        image_relief_enabled = bool(personalization["image_relief"]["enabled"])
        if not image_relief_enabled:
            print_parts.append(
                PartRecord(
                    "personalized_header_insert_print",
                    orient_fascia_on_bed(insert),
                    1,
                    "decorative PLA/PETG",
                    "rear face on bed",
                    "decor",
                )
            )
            assembly_parts.append(
                AssemblyRecord("header_insert", insert_placed, accent_color)
            )
        derived["header_insert_assembly_translation"] = [
            0.0,
            backer_y + 1.40,
            shelf_top_z + outer_h / 2.0 + 8.0,
        ]

    anti_tip = make_anti_tip_bracket(config)
    print_parts.append(
        PartRecord(
            "height_adjustable_wall_restraint_spacer_print_2x",
            orient_fascia_on_bed(anti_tip),
            2,
            "PETG",
            "largest face on bed",
            "mounting",
        )
    )
    restraint_hole_spacing = float(frame["wall_restraint_hole_spacing"])
    restraint_lower_hole_local = (
        float(frame["wall_restraint_bracket_height"]) - restraint_hole_spacing
    ) / 2.0
    anti_tip_z = float(frame["wall_restraint_nominal_lower_hole_z"]) - restraint_lower_hole_local
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        assembly_parts.append(
            AssemblyRecord(
                f"{label}_wall_restraint_spacer",
                anti_tip.translate((sign * side_x, -float(config["installation"]["wall_gap"]), anti_tip_z)),
                (0.16, 0.18, 0.17),
            )
        )

    coupon = make_fit_coupon(config)
    print_parts.append(
        PartRecord("fit_coupon_020_030_040_050_print", place_on_bed(coupon), 1, "same material as frame", "flat", "coupon")
    )
    module_seam_coupon = make_module_seam_coupon(config)
    print_parts.append(
        PartRecord(
            "wide_module_m3_seam_coupon_print",
            place_on_bed(module_seam_coupon),
            1,
            "same PETG and M3 hardware process as wide modules",
            "flat",
            "coupon",
        )
    )
    floor_interface_coupon = make_floor_interface_coupon(config)
    print_parts.append(
        PartRecord(
            "floor_foot_tpu_lock_coupon_print",
            place_on_bed(floor_interface_coupon),
            1,
            "production PETG, TPU and M4 foot-lock hardware",
            "use exported multi-body orientation",
            "coupon",
        )
    )

    derived.update(
        {
            "tile_width": tile_width,
            "shelf_depth": shelf_depth,
            "frame_outer_width": frame_outer_width,
            "frame_total_height_from_floor": float(config["installation"]["overall_height"]),
            "toilet_clear_width": float(config["installation"]["toilet_clear_width"]),
            "toilet_clear_height": float(config["installation"]["toilet_clear_height"]),
            "wall_restraint_nominal_lower_hole_z": float(frame["wall_restraint_nominal_lower_hole_z"]),
            "print_part_file_count": len(print_parts),
            "assembly_body_count": len(assembly_parts),
        }
    )
    return BuildResult(config, print_parts, assembly_parts, derived)


def make_assembly_compound(parts: list[AssemblyRecord]) -> cq.Workplane:
    compound = cq.Compound.makeCompound([part.solid.val() for part in parts])
    return cq.Workplane(obj=compound)
