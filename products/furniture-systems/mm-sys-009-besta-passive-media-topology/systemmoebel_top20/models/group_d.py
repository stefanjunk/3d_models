"""Products 16-20."""

from __future__ import annotations

from typing import Any

import cadquery as cq

from ..common import (
    ModelSpec,
    config_number,
    cylinder,
    open_tray,
    plate,
    rectangular_c_clip,
    rounded_prism,
)


MIN_WALL_MM = 2.4


def _section(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config[key]
    if not isinstance(value, dict):
        raise TypeError(f"Expected config section {key}, got {value!r}")
    return value


def _wall(section: dict[str, Any], key: str = "wall") -> float:
    value = config_number(section, key)
    if value < MIN_WALL_MM:
        raise ValueError(f"{key} must be at least {MIN_WALL_MM} mm, got {value}")
    return value


def _union(parts: list[cq.Workplane]) -> cq.Workplane:
    if not parts:
        raise ValueError("At least one solid is required")
    result = parts[0]
    for part in parts[1:]:
        result = result.union(part)
    return result.clean()


def _malm_dividers(config: dict[str, Any]) -> ModelSpec:
    section = _section(config, "16_malm_drawer_dividers")
    width = config_number(section, "width")
    depth = config_number(section, "depth")
    height = config_number(section, "height")
    wall = _wall(section)
    nominal_floor = config_number(section, "floor")

    # The legacy floor setting defines a widened divider root, not a floor:
    # the grid intentionally remains open-bottomed.
    root_height = max(2.0 * nominal_floor, 2.0 * wall)
    root_width = wall + 1.6
    overlap = 0.8
    x_dividers = (-0.24 * width, 0.14 * width)
    y_dividers = (-0.18 * depth, 0.26 * depth)

    parts = [
        plate(wall, depth, height, center=(-(width - wall) / 2.0, 0.0)),
        plate(wall, depth, height, center=((width - wall) / 2.0, 0.0)),
        plate(width, wall, height, center=(0.0, -(depth - wall) / 2.0)),
        plate(width, wall, height, center=(0.0, (depth - wall) / 2.0)),
    ]
    for x_pos in x_dividers:
        parts.extend(
            [
                plate(wall, depth - 2.0 * wall + overlap, height, center=(x_pos, 0.0)),
                plate(
                    root_width,
                    depth - 2.0 * wall + overlap,
                    root_height,
                    center=(x_pos, 0.0),
                ),
            ]
        )
    for y_pos in y_dividers:
        parts.extend(
            [
                plate(width - 2.0 * wall + overlap, wall, height, center=(0.0, y_pos)),
                plate(
                    width - 2.0 * wall + overlap,
                    root_width,
                    root_height,
                    center=(0.0, y_pos),
                ),
            ]
        )

    return ModelSpec(
        index=16,
        slug="malm_fold_size_dividers",
        title="MALM fold-size drawer dividers",
        solid=_union(parts),
        material="PLA Pro or PETG",
        print_orientation="Open grid on its continuous divider and perimeter roots at Z=0",
        support_required=False,
        minimum_wall_mm=wall,
        interface_note=(
            "PROVISIONAL drawer envelope and fold-size layout; a process-matched physical "
            "fit coupon and low-load drawer-cycle test are required before use."
        ),
        protected_features=(
            "continuous open-bottom perimeter",
            "unequal fold-size cells",
            "widened connected divider roots",
            "drawer stop and closing-path clearance",
        ),
    )


def _ivar_side_rail(config: dict[str, Any]) -> ModelSpec:
    section = _section(config, "17_ivar_side_rail")
    length = config_number(section, "length")
    post_width = config_number(section, "post_width")
    post_depth = config_number(section, "post_depth")
    clip_wall = _wall(section, "clip_wall")
    clip_height = config_number(section, "clip_height")
    if clip_height < MIN_WALL_MM:
        raise ValueError("clip_height is too small")

    outer_width = post_width + 2.0 * clip_wall
    opening = post_width - 2.0 * clip_wall
    clip_offset = (length - outer_width) / 2.0
    clips = [
        rectangular_c_clip(
            post_width,
            post_depth,
            clip_height,
            clip_wall,
            opening,
        ).translate((x_pos, 0.0, 0.0))
        for x_pos in (-clip_offset, clip_offset)
    ]

    overlap = 0.6
    clip_back = -(post_depth / 2.0 + clip_wall)
    rail_depth = 3.0 * clip_wall
    rail_center_y = clip_back - rail_depth / 2.0 + overlap
    rail_back = rail_center_y - rail_depth / 2.0
    parts = clips + [plate(length, rail_depth, clip_height, center=(0.0, rail_center_y))]

    # Local backing pads spread load where each clip root meets the rail.
    for x_pos in (-clip_offset, clip_offset):
        parts.append(
            rounded_prism(
                outer_width + 8.0,
                rail_depth + 5.0,
                clip_height,
                radius=2.5,
            ).translate((x_pos, rail_center_y - 2.5, 0.0))
        )

    # Three shallow T-hooks and two closed low-load docks are all planar
    # extrusions so the complete rail prints flat without generated support.
    hook_depth = 16.0
    hook_width = 8.0
    for x_pos in (-55.0, 0.0, 55.0):
        stem_center_y = rail_back - hook_depth / 2.0 + overlap
        parts.append(
            plate(hook_width, hook_depth, clip_height, center=(x_pos, stem_center_y))
        )
        parts.append(
            plate(
                22.0,
                5.0,
                clip_height,
                center=(x_pos, stem_center_y - hook_depth / 2.0 + 2.5),
            )
        )

    dock_depth = 18.0
    dock_center_y = rail_back - dock_depth / 2.0 + overlap
    for x_pos in (-clip_offset, clip_offset):
        outer = rounded_prism(24.0, dock_depth, clip_height, radius=3.0).translate(
            (x_pos, dock_center_y, 0.0)
        )
        inner = rounded_prism(
            12.0,
            8.0,
            clip_height + 2.0,
            radius=1.5,
            z0=-1.0,
        ).translate((x_pos, dock_center_y, 0.0))
        parts.append(outer.cut(inner).clean())

    return ModelSpec(
        index=17,
        slug="ivar_no_drill_side_inventory_rail",
        title="IVAR no-drill side inventory rail",
        solid=_union(parts),
        material="PETG or ASA; optional non-marking contact pads",
        print_orientation="Flat as modeled on all continuous Z=0 faces; rotate only for installation",
        support_required=False,
        minimum_wall_mm=clip_wall,
        interface_note=(
            "PROVISIONAL post section, opening, and clip preload; a process-matched physical "
            "fit coupon, finish-marking check, and low-load test are required before use."
        ),
        protected_features=(
            "two broad rectangular C-clips",
            "reinforced clip-to-rail roots",
            "continuous long rail",
            "low-load planar hooks and docks",
            "wall-anchor access and clearance",
        ),
    )


def _support_rail(
    width: float,
    center_y: float,
    top_z: float,
    wall: float,
    cap_depth: float,
) -> cq.Workplane:
    """Full-width display rail with self-supporting 56-degree cap shoulders."""
    # 56-degree shoulder gives margin beyond a nominal 45-degree overhang.
    shoulder_height = (cap_depth - wall) * 0.75
    stem_top = top_z - wall - shoulder_height
    if stem_top < wall:
        raise ValueError("Display level is too low for its support-free rail shoulder")
    profile = [
        (-wall / 2.0, 0.0),
        (wall / 2.0, 0.0),
        (wall / 2.0, stem_top),
        (cap_depth / 2.0, top_z - wall),
        (cap_depth / 2.0, top_z),
        (-cap_depth / 2.0, top_z),
        (-cap_depth / 2.0, top_z - wall),
        (-wall / 2.0, stem_top),
    ]
    return (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(width / 2.0, both=True)
        .translate((0.0, center_y, 0.0))
    )


def _billy_display_matrix(config: dict[str, Any]) -> ModelSpec:
    section = _section(config, "18_billy_display_matrix")
    width = config_number(section, "width")
    depth = config_number(section, "depth")
    height = config_number(section, "height")
    wall = _wall(section)

    cap_depth = 5.0 * wall
    level_heights = (14.0, 42.0, height)
    level_rail_positions = ((-75.0, -40.0), (-18.0, 18.0), (40.0, 75.0))
    parts: list[cq.Workplane] = []
    for top_z, y_positions in zip(level_heights, level_rail_positions):
        for y_pos in y_positions:
            parts.append(_support_rail(width, y_pos, top_z, wall, cap_depth))

    # Three bed-level runners connect every vertical web while leaving most of
    # the footprint open instead of filling it with a large stepped block.
    runner_width = 8.0
    for x_pos in (-(width - runner_width) / 2.0, 0.0, (width - runner_width) / 2.0):
        parts.append(plate(runner_width, depth, wall, center=(x_pos, 0.0)))

    return ModelSpec(
        index=18,
        slug="billy_collection_display_matrix",
        title="BILLY collection display matrix",
        solid=_union(parts),
        material="PLA Pro or PETG",
        print_orientation="Upright on the three base runners and support-web roots at Z=0",
        support_required=False,
        minimum_wall_mm=wall,
        interface_note=(
            "PROVISIONAL shelf envelope, object spacing, and sight lines; a physical fit "
            "coupon and low-load stability test with non-fragile proxies are required."
        ),
        protected_features=(
            "three stepped display levels",
            "paired narrow object-support rails per level",
            "open-frame vertical webs",
            "56-degree support-intent rail shoulders",
            "no fall, impact, or fragile-object retention claim",
        ),
    )


def _desk_cable_rail(config: dict[str, Any]) -> ModelSpec:
    section = _section(config, "19_desk_cable_rail")
    project = _section(config, "project")
    length = config_number(section, "length")
    desk_thickness = config_number(section, "desk_thickness")
    clamp_depth = config_number(section, "clamp_depth")
    wall = _wall(section)
    clearance = config_number(project, "nominal_xy_clearance_per_side_mm")
    raw_diameters = section["cable_diameters"]
    if not isinstance(raw_diameters, list) or not raw_diameters:
        raise TypeError("cable_diameters must be a non-empty list")
    cable_diameters = [float(value) for value in raw_diameters]
    if any(value <= 0.0 for value in cable_diameters):
        raise ValueError("cable diameters must be positive")

    pad_thickness = 1.0
    pad_overlap = 0.2
    pad_protrusion = pad_thickness - pad_overlap
    channel_opening = desk_thickness + 2.0 * (clearance + pad_protrusion)
    outer_height = channel_opening + 2.0 * wall
    jaw_center = channel_opening / 2.0 + wall / 2.0

    spine = plate(length, outer_height, wall)
    lower_jaw = plate(length, wall, clamp_depth, center=(0.0, -jaw_center))
    upper_jaw = plate(length, wall, clamp_depth, center=(0.0, jaw_center))

    flange_depth = 24.0
    overlap = 0.6
    flange_min_y = outer_height / 2.0 - overlap
    flange_max_y = flange_min_y + flange_depth
    flange = plate(
        length,
        flange_depth,
        wall,
        center=(0.0, (flange_min_y + flange_max_y) / 2.0),
    )
    parts = [spine, lower_jaw, upper_jaw, flange]

    # Three broad, shallow pad lands per jaw preserve a distributed contact
    # path. Their effective opening retains the configured per-side clearance.
    pad_length = 44.0
    pad_depth = min(24.0, clamp_depth)
    pad_positions = (-0.35 * length, 0.0, 0.35 * length)
    lower_pad_y = -channel_opening / 2.0 + pad_thickness / 2.0 - pad_overlap
    upper_pad_y = channel_opening / 2.0 - pad_thickness / 2.0 + pad_overlap
    for x_pos in pad_positions:
        parts.append(
            plate(pad_length, pad_thickness, pad_depth, center=(x_pos, lower_pad_y))
        )
        parts.append(
            plate(pad_length, pad_thickness, pad_depth, center=(x_pos, upper_pad_y))
        )

    solid = _union(parts)
    slot_length = 15.0
    slot_inner_y = flange_max_y - slot_length
    spacing = length / (len(cable_diameters) + 1.0)
    for index, diameter in enumerate(cable_diameters, start=1):
        x_pos = -length / 2.0 + index * spacing
        slot_width = diameter + 2.0 * clearance
        slot = plate(
            slot_width,
            slot_length + 2.0,
            wall + 2.0,
            center=(x_pos, flange_max_y - slot_length / 2.0 + 1.0),
            z0=-1.0,
        ).union(
            cylinder(
                slot_width,
                wall + 2.0,
                center=(x_pos, slot_inner_y),
                z0=-1.0,
            )
        )
        solid = solid.cut(slot)

    return ModelSpec(
        index=19,
        slug="lagkapten_alex_reversible_cable_rail",
        title="LAGKAPTEN/ALEX reversible cable parking rail",
        solid=solid.clean(),
        material="PETG with optional broad TPU contact pads",
        print_orientation="As modeled: broad channel spine and slotted flange flat at Z=0",
        support_required=False,
        minimum_wall_mm=wall,
        interface_note=(
            "PROVISIONAL desk thickness, pad compression, and cable diameters; a process-matched "
            "physical fit coupon, surface-marking check, and low-load test are required."
        ),
        protected_features=(
            "support-free rectangular C-channel",
            "broad distributed furniture-pad lands",
            "configured open-edge cable slots",
            "left-right reversible symmetric rail",
            "no high-clamp-force or heavy-device claim",
        ),
    )


def _triangular_gusset(
    center_x: float,
    front_y: float,
    depth: float,
    height: float,
    floor: float,
    thickness: float,
) -> cq.Workplane:
    profile = [
        (front_y, floor - 0.4),
        (front_y, height),
        (front_y - depth, floor - 0.4),
    ]
    return (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(thickness / 2.0, both=True)
        .translate((center_x, 0.0, 0.0))
    )


def _lack_leg_dock(config: dict[str, Any]) -> ModelSpec:
    section = _section(config, "20_lack_leg_mini_dock")
    leg_width = config_number(section, "leg_width")
    leg_depth = config_number(section, "leg_depth")
    clip_height = config_number(section, "clip_height")
    wall = _wall(section)
    dock_width = config_number(section, "dock_width")
    dock_depth = config_number(section, "dock_depth")
    dock_height = config_number(section, "dock_height")
    floor = MIN_WALL_MM

    clip_opening = leg_width - 2.0 * wall
    clip = rectangular_c_clip(
        leg_width,
        leg_depth,
        clip_height,
        wall,
        clip_opening,
    )
    clip_back = -(leg_depth / 2.0 + wall)
    dock_front = clip_back + 0.8
    dock_center_y = dock_front - dock_depth / 2.0
    dock = open_tray(
        dock_width,
        dock_depth,
        dock_height,
        wall=wall,
        floor=floor,
        radius=6.0,
    ).translate((0.0, dock_center_y, 0.0))

    # Unequal pockets allocate a narrow remote bay and a wider notepad bay.
    divider_x = -12.0
    divider = plate(
        wall,
        dock_depth - 2.0 * wall + 0.8,
        dock_height - floor + 0.4,
        center=(divider_x, dock_center_y),
        z0=floor - 0.4,
    )

    root_pad_depth = 10.0
    root_pad_center_y = -(leg_depth / 2.0) - root_pad_depth / 2.0 - 0.2
    root_pad = rounded_prism(
        leg_width + 2.0 * wall + 12.0,
        root_pad_depth,
        clip_height,
        radius=2.5,
    ).translate((0.0, root_pad_center_y, 0.0))

    inner_front_y = dock_front - wall
    gusset_depth = min(38.0, dock_depth / 2.0)
    gusset_height = min(38.0, clip_height + 14.0)
    gusset_thickness = 5.0
    gussets = [
        _triangular_gusset(
            center_x,
            inner_front_y,
            gusset_depth,
            gusset_height,
            floor,
            gusset_thickness,
        )
        for center_x in (-36.0, 22.0)
    ]

    return ModelSpec(
        index=20,
        slug="lack_leg_two_pocket_mini_dock",
        title="LACK leg two-pocket mini dock",
        solid=_union([clip, dock, divider, root_pad, *gussets]),
        material="PETG with optional non-marking contact pads",
        print_orientation="Upright as modeled on the pocket floor, clip roots, and gussets at Z=0",
        support_required=False,
        minimum_wall_mm=floor,
        interface_note=(
            "PROVISIONAL leg section, clip preload, remote, and notepad envelopes; a "
            "process-matched physical fit coupon, table-tip check, and very-low-load test "
            "are required before use."
        ),
        protected_features=(
            "rectangular leg C-clip",
            "reinforced clip root pad",
            "connected unequal remote and notepad pockets",
            "two gusseted floor-to-clip load paths",
            "very-low-load-only use",
        ),
    )


def build(config: dict[str, Any]) -> list[ModelSpec]:
    return [
        _malm_dividers(config),
        _ivar_side_rail(config),
        _billy_display_matrix(config),
        _desk_cable_rail(config),
        _lack_leg_dock(config),
    ]
