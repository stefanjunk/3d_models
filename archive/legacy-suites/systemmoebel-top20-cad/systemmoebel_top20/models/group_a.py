"""Products 01-05."""

from __future__ import annotations

from typing import Any

import cadquery as cq

from ..common import (
    ModelSpec,
    config_number,
    cylinder,
    open_tray,
    plate,
    ring,
    rounded_prism,
)


PROVISIONAL_INTERFACE = (
    "PROVISIONAL — concept geometry only; measure the exact furniture/board "
    "revision and print a fit coupon before relying on the interface."
)


def _number(config: dict[str, Any], section: str, key: str) -> float:
    """Read one millimetre dimension while retaining common.py validation."""
    values = config.get(section)
    if not isinstance(values, dict):
        raise KeyError(f"Missing configuration section {section!r}")
    return config_number(values, key)


def _union(base: cq.Workplane, *parts: cq.Workplane) -> cq.Workplane:
    """Fuse overlapping functional regions into one cleaned body."""
    result = base
    for part in parts:
        result = result.union(part)
    return result.clean()


def _rounded_at(
    width: float,
    depth: float,
    height: float,
    center: tuple[float, float],
    z0: float,
    radius: float,
) -> cq.Workplane:
    return rounded_prism(width, depth, height, radius, z0).translate(
        (center[0], center[1], 0.0)
    )


def _alex_inventory_tray(config: dict[str, Any]) -> ModelSpec:
    section = "01_alex_workstation_tray"
    width = _number(config, section, "width")
    depth = _number(config, section, "depth")
    height = _number(config, section, "height")
    wall = max(2.4, _number(config, section, "wall"))
    floor = max(2.4, _number(config, section, "floor"))

    body = open_tray(width, depth, height, wall, floor, radius=7.0)
    divider = max(3.0, wall)
    divider_z = floor - 0.25
    divider_top = height - 4.0
    divider_height = divider_top - divider_z
    x_min = -width / 2.0 + wall
    x_max = width / 2.0 - wall
    y_min = -depth / 2.0 + wall
    y_max = depth / 2.0 - wall
    spine_x = -38.0

    spine = plate(
        divider,
        y_max - y_min + 0.4,
        divider_height,
        center=(spine_x, 0.0),
        z0=divider_z,
    )
    left_branch = plate(
        spine_x - x_min + divider,
        divider,
        divider_height,
        center=((x_min + spine_x) / 2.0, 21.0),
        z0=divider_z,
    )
    right_branch = plate(
        x_max - spine_x + divider,
        divider,
        divider_height,
        center=((spine_x + x_max) / 2.0, -27.0),
        z0=divider_z,
    )
    short_branch = plate(
        divider,
        y_max + 27.0 + divider,
        divider_height,
        center=(35.0, (y_max - 27.0) / 2.0),
        z0=divider_z,
    )
    round_tool_zone = ring(
        34.0,
        27.0,
        17.0,
        center=(72.0, 38.0),
        z0=floor - 0.2,
    )
    body = _union(
        body,
        spine,
        left_branch,
        right_branch,
        short_branch,
        round_tool_zone,
    )

    return ModelSpec(
        index=1,
        slug="alex_inventory_workplace_tray",
        title="ALEX inventory workplace tray — provisional concept",
        solid=body,
        material="PETG or PLA prototype; process selection pending",
        print_orientation="continuous tray floor on the build plate",
        support_required=False,
        minimum_wall_mm=min(wall, floor),
        interface_note=PROVISIONAL_INTERFACE,
        protected_features=(
            "provisional furniture fit envelope",
            "continuous floor and perimeter load path",
            "all asymmetric divider roots and branch junctions",
            "round tool-zone root at the tray floor",
        ),
    )


def _bror_shadow_tray(config: dict[str, Any]) -> ModelSpec:
    section = "02_bror_tool_tray"
    width = _number(config, section, "width")
    depth = _number(config, section, "depth")
    height = _number(config, section, "height")
    wall = max(2.4, _number(config, section, "wall"))
    floor = max(2.4, _number(config, section, "floor"))

    pocket_depth = 5.5
    shadow_deck = floor + pocket_depth
    body = open_tray(width, depth, height, wall, shadow_deck, radius=8.0)
    cutter_z = floor
    cutter_height = pocket_depth + 1.0

    # Hammer: a broad head and rooted handle form an immediately legible T-shape.
    hammer = _union(
        _rounded_at(15.0, 80.0, cutter_height, (-67.0, -18.0), cutter_z, 5.0),
        _rounded_at(62.0, 24.0, cutter_height, (-67.0, 29.0), cutter_z, 6.0),
    )

    # Screwdriver: a rounded grip, narrow shaft and wider terminal tip.
    screwdriver = _union(
        _rounded_at(56.0, 24.0, cutter_height, (23.0, 42.0), cutter_z, 8.0),
        _rounded_at(58.0, 10.0, cutter_height, (74.0, 42.0), cutter_z, 4.0),
        _rounded_at(10.0, 16.0, cutter_height, (100.0, 42.0), cutter_z, 3.0),
    )

    # Open-ended wrench silhouette.  The offset circular and rectangular voids
    # leave two robust jaw prongs in the cutter rather than a generic capsule.
    wrench = _union(
        _rounded_at(75.0, 14.0, cutter_height, (35.0, -23.0), cutter_z, 6.0),
        cylinder(36.0, cutter_height, center=(-9.0, -23.0), z0=cutter_z),
    )
    wrench_mouth = _union(
        cylinder(18.0, cutter_height + 0.5, center=(-13.0, -23.0), z0=cutter_z),
        plate(
            24.0,
            12.0,
            cutter_height + 0.5,
            center=(-27.0, -23.0),
            z0=cutter_z,
        ),
    )
    wrench = wrench.cut(wrench_mouth).clean()

    socket_cutters = (
        cylinder(18.0, cutter_height, center=(24.0, -61.0), z0=cutter_z),
        cylinder(24.0, cutter_height, center=(55.0, -60.0), z0=cutter_z),
        cylinder(30.0, cutter_height, center=(91.0, -58.0), z0=cutter_z),
    )
    for cutter in (hammer, screwdriver, wrench, *socket_cutters):
        body = body.cut(cutter)
    body = body.clean()

    return ModelSpec(
        index=2,
        slug="bror_tool_shadow_tray",
        title="BROR tool shadow tray — provisional concept",
        solid=body,
        material="PETG or PLA prototype; process selection pending",
        print_orientation="continuous recessed floor on the build plate",
        support_required=False,
        minimum_wall_mm=min(wall, floor),
        interface_note=PROVISIONAL_INTERFACE,
        protected_features=(
            "provisional furniture fit envelope",
            "continuous shadow-deck floor and perimeter load path",
            "minimum floor ligament below every recessed tool pocket",
            "material bridges between hammer, wrench, screwdriver and socket zones",
        ),
    )


def _pax_accessory_grid(config: dict[str, Any]) -> ModelSpec:
    section = "03_pax_accessory_grid"
    width = _number(config, section, "width")
    depth = _number(config, section, "depth")
    height = _number(config, section, "height")
    wall = max(2.4, _number(config, section, "wall"))
    floor = max(2.4, _number(config, section, "floor"))

    body = open_tray(width, depth, height, wall, floor, radius=7.0)
    divider = max(3.0, wall)
    divider_z = floor - 0.25
    divider_top = height - 4.0
    divider_height = divider_top - divider_z
    x_min = -width / 2.0 + wall
    x_max = width / 2.0 - wall
    y_min = -depth / 2.0 + wall
    y_max = depth / 2.0 - wall
    spine_x = -25.0

    spine = plate(
        divider,
        y_max - y_min + 0.4,
        divider_height,
        center=(spine_x, 0.0),
        z0=divider_z,
    )
    upper_left = plate(
        spine_x - x_min + divider,
        divider,
        divider_height,
        center=((x_min + spine_x) / 2.0, 22.0),
        z0=divider_z,
    )
    center_branch = plate(
        45.0 - spine_x + divider,
        divider,
        divider_height,
        center=((spine_x + 45.0) / 2.0, -18.0),
        z0=divider_z,
    )
    upper_right = plate(
        divider,
        y_max + 18.0 + divider,
        divider_height,
        center=(45.0, (y_max - 18.0) / 2.0),
        z0=divider_z,
    )
    lower_center = plate(
        divider,
        -18.0 - y_min + divider,
        divider_height,
        center=(18.0, (y_min - 18.0) / 2.0),
        z0=divider_z,
    )
    large_round_cell = ring(
        44.0,
        36.0,
        23.0,
        center=(79.0, 45.0),
        z0=floor - 0.2,
    )
    small_round_cell = ring(
        36.0,
        29.0,
        19.0,
        center=(80.0, -50.0),
        z0=floor - 0.2,
    )
    body = _union(
        body,
        spine,
        upper_left,
        center_branch,
        upper_right,
        lower_center,
        large_round_cell,
        small_round_cell,
    )

    return ModelSpec(
        index=3,
        slug="pax_asymmetric_accessory_grid",
        title="PAX accessory grid — provisional concept",
        solid=body,
        material="PETG or PLA prototype; process selection pending",
        print_orientation="continuous compartment floor on the build plate",
        support_required=False,
        minimum_wall_mm=wall,
        interface_note=PROVISIONAL_INTERFACE,
        protected_features=(
            "provisional furniture fit envelope",
            "continuous floor and perimeter load path",
            "asymmetric divider roots and intersections",
            "large and small round-cell roots at the floor",
        ),
    )


def _billy_collection_riser(config: dict[str, Any]) -> ModelSpec:
    section = "04_billy_collection_riser"
    width = _number(config, section, "width")
    depth = _number(config, section, "depth")
    height = _number(config, section, "height")
    wall = max(2.4, _number(config, section, "wall"))
    structural = max(3.0, wall)

    base = plate(width, depth, structural, z0=0.0)
    segment_depth = depth / 3.0
    tread_heights = (height * 0.27, height * 0.54, height * 0.80)
    body = base

    # Full-depth divider plates also act as primary vertical support webs.
    divider_x = (-45.0, 55.0)
    dividers = tuple(
        plate(structural, depth, height, center=(x, 0.0), z0=0.0)
        for x in divider_x
    )
    body = _union(body, *dividers)

    # Closely spaced vertical webs keep horizontal tread bridges below 30 mm
    # for the default 0.6 mm-nozzle concept profile.  Every tread has a direct
    # floor-to-load-surface path; there are no horizontal roofs over deep voids.
    web_x = (-108.0, -88.0, -68.0, -22.0, 3.0, 29.0, 80.0, 103.0, 108.0)
    for index, tread_height in enumerate(tread_heights):
        y_center = -depth / 2.0 + segment_depth * (index + 0.5)
        tread = plate(
            width,
            segment_depth,
            structural,
            center=(0.0, y_center),
            z0=tread_height - structural,
        )
        web_height = tread_height - structural + 0.25
        webs = tuple(
            plate(
                structural,
                segment_depth,
                web_height,
                center=(x, y_center),
                z0=structural - 0.25,
            )
            for x in web_x
        )
        body = _union(body, tread, *webs)

    return ModelSpec(
        index=4,
        slug="billy_collection_riser",
        title="BILLY stepped collection riser — provisional concept",
        solid=body,
        material="PETG or PLA prototype; load testing required",
        print_orientation="full base plate on bed; stepped treads bridge between integral webs",
        support_required=False,
        minimum_wall_mm=structural,
        interface_note=PROVISIONAL_INTERFACE,
        protected_features=(
            "provisional furniture fit envelope",
            "continuous base, vertical webs and floor-to-tread load paths",
            "full-depth divider roots and tread intersections",
            "closely spaced vertical support webs beneath every tread",
        ),
    )


def _bror_shadow_cluster(config: dict[str, Any]) -> ModelSpec:
    section = "05_bror_shadow_cluster"
    width = _number(config, section, "width")
    board_height = _number(config, section, "height")
    backplate = max(2.4, _number(config, section, "backplate"))
    slot_width = _number(config, section, "slot_width")
    slot_length = _number(config, section, "slot_length")
    pitch_x = _number(config, section, "slot_pitch_x")
    pitch_z = _number(config, section, "slot_pitch_z")

    tab_projection = max(12.0, 2.0 * slot_width)
    core_width = width - 2.0 * tab_projection
    core_height = board_height - 2.0 * tab_projection
    body = plate(core_width, core_height, backplate, z0=0.0)
    tab_overlap = 0.6
    tab_depth = tab_projection + tab_overlap

    # Tabs remain in the board plane.  Their dimensions deliberately use the
    # provisional slot length/pitches but do not claim compatibility.
    top_tabs = tuple(
        plate(
            slot_length,
            tab_depth,
            backplate,
            center=(x, core_height / 2.0 + (tab_projection - tab_overlap) / 2.0),
            z0=0.0,
        )
        for x in (-pitch_x, 0.0, pitch_x)
    )
    bottom_tabs = tuple(
        plate(
            slot_length,
            tab_depth,
            backplate,
            center=(x, -core_height / 2.0 - (tab_projection - tab_overlap) / 2.0),
            z0=0.0,
        )
        for x in (-pitch_x / 2.0, pitch_x / 2.0)
    )
    side_tabs = tuple(
        plate(
            tab_depth,
            slot_length,
            backplate,
            center=(side * (core_width / 2.0 + (tab_projection - tab_overlap) / 2.0), y),
            z0=0.0,
        )
        for side in (-1.0, 1.0)
        for y in (-pitch_z / 2.0, pitch_z / 2.0)
    )
    body = _union(body, *top_tabs, *bottom_tabs, *side_tabs)

    # Two paired through-slot interfaces provide a real path for purchased
    # reusable straps without inventing an unverified furniture-side hook.
    for x in (-55.0, 55.0):
        for y in (12.0, 28.0):
            strap_slot = rounded_prism(
                18.0,
                5.5,
                backplate + 2.0,
                radius=2.75,
                z0=-1.0,
            ).translate((x, y, 0.0))
            body = body.cut(strap_slot)

    attachment_z = backplate - 0.5
    tool_ring_large = ring(
        42.0,
        34.0,
        24.0,
        center=(-4.0, -21.0),
        z0=attachment_z,
    )
    tool_ring_small = ring(
        32.0,
        25.0,
        20.0,
        center=(56.0, -22.0),
        z0=attachment_z,
    )
    cup_outer = cylinder(46.0, 31.0, center=(-68.0, -15.0), z0=attachment_z)
    cup_inner = cylinder(
        38.0,
        28.5,
        center=(-68.0, -15.0),
        z0=attachment_z + 3.5,
    )
    tool_cup = cup_outer.cut(cup_inner).clean()
    body = _union(body, tool_ring_large, tool_ring_small, tool_cup)

    return ModelSpec(
        index=5,
        slug="bror_shadow_board_workflow_cluster",
        title="BROR shadow-board workflow cluster — provisional concept",
        solid=body,
        material="PETG prototype; interface and load testing required",
        print_orientation="flat rear face of the backplate on the build plate",
        support_required=False,
        minimum_wall_mm=min(backplate, 3.5),
        interface_note=(
            PROVISIONAL_INTERFACE
            + " Retention concept: two paired 18 × 5.5 mm through-slot interfaces for "
            "purchased reusable straps; straps and furniture-side routing are not included."
        ),
        protected_features=(
            "provisional board fit envelope",
            "continuous backplate and perimeter load path",
            "all in-plane interface-tab roots",
            "two paired purchased-strap through-slot interfaces",
            "integrated tool-ring and blind-cup roots at the backplate",
        ),
    )


def build(config: dict[str, Any]) -> list[ModelSpec]:
    project = config.get("project")
    if not isinstance(project, dict) or project.get("units") != "mm":
        raise ValueError("Products 01-05 require millimetre configuration")
    return [
        _alex_inventory_tray(config),
        _bror_shadow_tray(config),
        _pax_accessory_grid(config),
        _billy_collection_riser(config),
        _bror_shadow_cluster(config),
    ]
