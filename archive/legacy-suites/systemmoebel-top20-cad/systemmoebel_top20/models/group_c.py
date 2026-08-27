"""Products 11-15: support-free, one-piece concept models."""

from __future__ import annotations

from typing import Any, Iterable

import cadquery as cq

from ..common import (
    ModelSpec,
    config_number,
    open_tray,
    plate,
    ring,
    rounded_prism,
)


def _union_all(parts: Iterable[cq.Workplane]) -> cq.Workplane:
    iterator = iter(parts)
    result = next(iterator)
    for part in iterator:
        result = result.union(part)
    return result.clean()


def _elliptical_ring(
    radius_x: float,
    radius_y: float,
    wall: float,
    height: float,
    center: tuple[float, float],
    z0: float,
) -> cq.Workplane:
    outer = (
        cq.Workplane("XY")
        .ellipse(radius_x, radius_y)
        .extrude(height)
        .translate((center[0], center[1], z0))
    )
    inner = (
        cq.Workplane("XY")
        .ellipse(radius_x - wall, radius_y - wall)
        .extrude(height + 1.0)
        .translate((center[0], center[1], z0 - 0.5))
    )
    return outer.cut(inner).clean()


def _rounded_rect_ring(
    width: float,
    depth: float,
    wall: float,
    height: float,
    center: tuple[float, float],
    z0: float,
) -> cq.Workplane:
    outer = rounded_prism(width, depth, height, radius=4.0, z0=z0).translate(
        (center[0], center[1], 0.0)
    )
    inner = rounded_prism(
        width - 2.0 * wall,
        depth - 2.0 * wall,
        height + 1.0,
        radius=1.5,
        z0=z0 - 0.5,
    ).translate((center[0], center[1], 0.0))
    return outer.cut(inner).clean()


def _slotted_vertical_panel(
    x: float,
    depth: float,
    top_z: float,
    thickness: float,
    z0: float,
    sill_top_z: float,
    slots: tuple[tuple[float, float], ...],
) -> cq.Workplane:
    """Vertical comb panel: every window is open at the top for support-free printing."""
    panel = plate(thickness, depth, top_z - z0, center=(x, 0.0), z0=z0)
    for center_y, slot_depth in slots:
        cutter = plate(
            thickness + 2.0,
            slot_depth,
            top_z - sill_top_z + 2.0,
            center=(x, center_y),
            z0=sill_top_z,
        )
        panel = panel.cut(cutter)
    return panel.clean()


def _provisional_interface_note(config: dict[str, Any], interface: str) -> str:
    project = config["project"]
    status = str(project["fit_status"])
    clearance = config_number(project, "nominal_xy_clearance_per_side_mm")
    return (
        f"{status}: {interface}; nominal XY allowance {clearance:.2f} mm/side is "
        "only a starting point. Release is gated by a process-matched fit coupon."
    )


def _build_11(config: dict[str, Any]) -> ModelSpec:
    values = config["11_boaxel_cleaning_dock"]
    width = config_number(values, "width")
    rail_height = config_number(values, "rail_height")
    rail_depth = config_number(values, "rail_depth")
    tab_span = config_number(values, "interface_thickness")

    base_thickness = 3.0
    dock_height = max(14.0, rail_depth - base_thickness + 0.2)
    backplate = rounded_prism(width, rail_height, base_thickness, radius=4.0)

    parts: list[cq.Workplane] = [backplate]
    dock_y = 1.0
    for x, outer_diameter, inner_diameter in (
        (-76.0, 18.0, 12.0),
        (-32.0, 24.0, 17.0),
        (16.0, 30.0, 23.0),
    ):
        dock = ring(
            outer_diameter,
            inner_diameter,
            dock_height,
            center=(x, dock_y),
            z0=base_thickness - 0.2,
        )
        opening_width = inner_diameter * 0.62
        opening_depth = outer_diameter / 2.0 + 4.0
        opening = plate(
            opening_width,
            opening_depth,
            dock_height + 2.0,
            center=(x, dock_y - outer_diameter / 4.0 - 2.0),
            z0=base_thickness - 1.0,
        )
        parts.append(dock.cut(opening).clean())

    open_dock_center = (75.0, 1.0)
    open_dock = _rounded_rect_ring(
        34.0,
        24.0,
        3.0,
        dock_height,
        open_dock_center,
        base_thickness - 0.2,
    )
    open_dock_cut = plate(
        28.0,
        16.0,
        dock_height + 2.0,
        center=(open_dock_center[0], open_dock_center[1] - 8.0),
        z0=base_thickness - 1.0,
    )
    parts.append(open_dock.cut(open_dock_cut).clean())

    # Flat, deliberately simple concept tabs: their furniture fit is not asserted.
    tab_depth = 14.0
    tab_width = max(24.0, 2.0 * tab_span)
    tab_y = rail_height / 2.0 + tab_depth / 2.0 - 1.0
    for x in (-78.0, 78.0):
        parts.append(plate(tab_width, tab_depth, base_thickness, center=(x, tab_y)))

    solid = _union_all(parts)
    for x in (-78.0, 78.0):
        for offset_x in (-6.0, 6.0):
            strap_slot = rounded_prism(
                5.5,
                4.0,
                base_thickness + 2.0,
                radius=2.0,
                z0=-1.0,
            ).translate((x + offset_x, tab_y, 0.0))
            solid = solid.cut(strap_slot)

    return ModelSpec(
        index=11,
        slug="boaxel_light_cleaning_docking_rail",
        title="BOAXEL Light Cleaning Accessory Docking Rail",
        solid=solid.clean(),
        material="PETG",
        print_orientation="Flat backplate and provisional tabs on the bed; docks upward",
        support_required=False,
        minimum_wall_mm=3.0,
        interface_note=_provisional_interface_note(
            config,
            "BOAXEL spacing is provisional; two dual-slot flanges demonstrate retention "
            "with purchased reusable straps, which are not included or load-rated",
        ),
        protected_features=(
            "continuous flat backplate load path",
            "two dual-slot purchased-strap retention flanges",
            "distinct open docks for light cleaning accessories only",
            "excludes chemical containers and heavy tools",
        ),
    )


def _build_12(config: dict[str, Any]) -> ModelSpec:
    values = config["12_besta_controller_tray"]
    width = config_number(values, "width")
    depth = config_number(values, "depth")
    height = config_number(values, "height")
    wall = config_number(values, "wall")
    floor = config_number(values, "floor")

    tray = open_tray(width, depth, height, wall=wall, floor=floor, radius=8.0)
    feature_z = floor - 0.2
    parts: list[cq.Workplane] = [tray]

    for center_x in (-52.0, 52.0):
        parts.append(
            _elliptical_ring(
                40.0,
                47.0,
                wall,
                6.0,
                center=(center_x, 10.0),
                z0=feature_z,
            )
        )

    parts.append(
        _rounded_rect_ring(
            92.0,
            25.0,
            wall,
            8.0,
            center=(-42.0, -63.0),
            z0=feature_z,
        )
    )
    parts.append(
        ring(32.0, 24.0, 7.0, center=(60.0, -63.0), z0=feature_z)
    )

    return ModelSpec(
        index=12,
        slug="besta_controller_media_drawer_tray",
        title="BESTA Controller and Media Drawer Tray",
        solid=_union_all(parts),
        material="PETG",
        print_orientation="Continuous tray floor on the bed; all pockets upward",
        support_required=False,
        minimum_wall_mm=min(wall, floor),
        interface_note=_provisional_interface_note(
            config, "BESTA drawer envelope and running clearance are provisional"
        ),
        protected_features=(
            "two shallow elliptical controller nests",
            "separate remote and passive cable zones",
            "no charger, powered feature, or heat-producing component",
        ),
    )


def _build_13(config: dict[str, Any]) -> ModelSpec:
    values = config["13_trofast_workshop_insert"]
    width = config_number(values, "width")
    depth = config_number(values, "depth")
    height = config_number(values, "height")
    wall = config_number(values, "wall")
    floor = config_number(values, "floor")

    tray = open_tray(width, depth, height, wall=wall, floor=floor, radius=7.0)
    divider_z = floor - 0.2
    divider_height = 32.0
    inner_x = width / 2.0 - wall
    inner_y = depth / 2.0 - wall

    parts: list[cq.Workplane] = [tray]
    parts.append(
        plate(
            2.0 * inner_x + 1.0,
            wall,
            divider_height,
            center=(0.0, -20.0),
            z0=divider_z,
        )
    )

    lower_depth = inner_y - 20.0 + 0.5
    parts.append(
        plate(
            wall,
            lower_depth,
            divider_height,
            center=(-30.0, -20.0 - lower_depth / 2.0 + 0.25),
            z0=divider_z,
        )
    )

    upper_depth = inner_y + 20.0 + 0.5
    parts.append(
        plate(
            wall,
            upper_depth,
            divider_height,
            center=(35.0, -20.0 + upper_depth / 2.0 - 0.25),
            z0=divider_z,
        )
    )

    upper_left_width = inner_x + 35.0 + 0.5
    parts.append(
        plate(
            upper_left_width,
            wall,
            divider_height,
            center=(-inner_x + upper_left_width / 2.0 - 0.25, 32.0),
            z0=divider_z,
        )
    )

    # Integrated retaining wells add captive organization without loose inserts.
    parts.extend(
        (
            ring(24.0, 18.0, 7.0, center=(-67.0, -50.0), z0=divider_z),
            ring(18.0, 12.0, 7.0, center=(70.0, 53.0), z0=divider_z),
        )
    )

    return ModelSpec(
        index=13,
        slug="trofast_adult_workshop_insert",
        title="TROFAST Adult Workshop Organization Insert",
        solid=_union_all(parts),
        material="PETG",
        print_orientation="Tray floor on the bed; open compartments upward",
        support_required=False,
        minimum_wall_mm=min(wall, floor),
        interface_note=_provisional_interface_note(
            config, "TROFAST bin envelope and insertion clearance are provisional"
        ),
        protected_features=(
            "adult workshop organization use",
            "unequal connected compartment grid",
            "integrated captive small-parts wells with no loose pieces",
        ),
    )


def _build_14(config: dict[str, Any]) -> ModelSpec:
    values = config["14_kallax_material_cassette"]
    width = config_number(values, "width")
    depth = config_number(values, "depth")
    height = config_number(values, "height")
    wall = config_number(values, "wall")
    floor = config_number(values, "floor")

    edge_beam = 12.0
    rib_width = 7.0
    parts: list[cq.Workplane] = [
        plate(width, edge_beam, floor, center=(0.0, -depth / 2.0 + edge_beam / 2.0)),
        plate(width, edge_beam, floor, center=(0.0, depth / 2.0 - edge_beam / 2.0)),
        plate(edge_beam, depth - 2.0 * edge_beam, floor, center=(-width / 2.0 + edge_beam / 2.0, 0.0)),
        plate(edge_beam, depth - 2.0 * edge_beam, floor, center=(width / 2.0 - edge_beam / 2.0, 0.0)),
    ]

    for y in (-70.0, -35.0, 0.0, 35.0, 70.0):
        parts.append(plate(width - 20.0, rib_width, floor, center=(0.0, y)))

    divider_positions = (-55.0, 0.0, 55.0)
    for x in divider_positions:
        parts.append(plate(rib_width, depth - 20.0, floor, center=(x, 0.0)))

    panel_z0 = floor - 0.2
    side_slots = ((-82.5, 45.0), (-27.5, 45.0), (27.5, 45.0), (82.5, 45.0))
    for x in (-width / 2.0 + wall / 2.0, width / 2.0 - wall / 2.0):
        parts.append(
            _slotted_vertical_panel(
                x,
                depth,
                height,
                wall,
                panel_z0,
                32.0,
                side_slots,
            )
        )

    divider_slots = ((-75.0, 40.0), (-25.0, 40.0), (25.0, 40.0), (75.0, 40.0))
    for x in divider_positions:
        parts.append(
            _slotted_vertical_panel(
                x,
                depth - 20.0,
                height,
                wall,
                panel_z0,
                32.0,
                divider_slots,
            )
        )

    rear_y = depth / 2.0 - wall / 2.0
    parts.append(plate(width, wall, height - panel_z0, center=(0.0, rear_y), z0=panel_z0))
    front_y = -depth / 2.0 + wall / 2.0
    parts.append(plate(width, wall, 32.0, center=(0.0, front_y), z0=panel_z0))

    return ModelSpec(
        index=14,
        slug="kallax_creative_material_cassette",
        title="KALLAX Creative-Material Cassette",
        solid=_union_all(parts),
        material="PETG",
        print_orientation="Open ribbed base on the bed; vertical comb panels upward",
        support_required=False,
        minimum_wall_mm=min(wall, floor),
        interface_note=_provisional_interface_note(
            config, "KALLAX cubby envelope and removal clearance are provisional"
        ),
        protected_features=(
            "one-piece open ribbed base with perimeter load path",
            "rear frame and tall side/divider comb panels",
            "top-open panel windows avoid unsupported roofs and excessive solid slabs",
        ),
    )


def _build_15(config: dict[str, Any]) -> ModelSpec:
    values = config["15_boaxel_basket_sorter"]
    width = config_number(values, "width")
    depth = config_number(values, "depth")
    height = config_number(values, "height")
    wall = config_number(values, "wall")

    inner_width = width - 2.0 * wall
    inner_depth = depth - 2.0 * wall
    parts: list[cq.Workplane] = [
        plate(width, wall, height, center=(0.0, -depth / 2.0 + wall / 2.0)),
        plate(width, wall, height, center=(0.0, depth / 2.0 - wall / 2.0)),
        plate(wall, inner_depth, height, center=(-width / 2.0 + wall / 2.0, 0.0)),
        plate(wall, inner_depth, height, center=(width / 2.0 - wall / 2.0, 0.0)),
    ]

    grid_height = 58.0
    parts.extend(
        (
            plate(inner_width + 1.0, wall, grid_height, center=(0.0, -22.0)),
            plate(wall, inner_depth + 1.0, grid_height, center=(-35.0, 0.0)),
            plate(wall, depth / 2.0 + 22.0, grid_height, center=(45.0, 26.5)),
            plate(width / 2.0 + 35.0, wall, grid_height, center=(37.5, 30.0)),
        )
    )

    # Open-sided C tabs provide a printable placeholder for a basket-wire coupon.
    clip_width = 18.0
    clip_depth = 11.0
    clip_height = 16.0
    clip_center_y = depth / 2.0 + clip_depth / 2.0 - 1.0
    for x in (-72.0, 72.0):
        clip = plate(
            clip_width,
            clip_depth,
            clip_height,
            center=(x, clip_center_y),
        )
        slot = plate(
            5.0,
            8.0,
            clip_height + 2.0,
            center=(x, depth / 2.0 + 7.0),
            z0=-1.0,
        )
        parts.append(clip.cut(slot).clean())

    return ModelSpec(
        index=15,
        slug="boaxel_basket_microsorter",
        title="BOAXEL Basket Microsorter",
        solid=_union_all(parts),
        material="PETG",
        print_orientation="Open-bottom perimeter and grid edges directly on the bed",
        support_required=False,
        minimum_wall_mm=wall,
        interface_note=_provisional_interface_note(
            config, "BOAXEL basket-wire clip profile and spacing are provisional"
        ),
        protected_features=(
            "one-piece open-bottom perimeter and unequal-cell grid",
            "broad continuous perimeter/grid bed contact",
            "provisional open clip tabs retained for coupon testing",
        ),
    )


def build(config: dict[str, Any]) -> list[ModelSpec]:
    """Build products 11-15 from the supplied default-compatible dimensions."""
    return [
        _build_11(config),
        _build_12(config),
        _build_13(config),
        _build_14(config),
        _build_15(config),
    ]
