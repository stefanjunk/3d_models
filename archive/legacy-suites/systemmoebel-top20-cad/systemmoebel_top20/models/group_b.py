"""Products 06-10."""

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


INTERFACE_NOTE = "PROVISIONAL interface; fit coupon required before use."


def _fuse(parts: list[cq.Workplane]) -> cq.Workplane:
    """Fuse touching features into one cleaned solid."""
    if not parts:
        raise ValueError("At least one solid is required")
    result = parts[0]
    for part in parts[1:]:
        result = result.union(part)
    return result.clean()


def _grid_panel(
    width: float,
    depth: float,
    thickness: float,
    edge: float,
    rib_width: float,
    x_ribs: tuple[float, ...],
    y_ribs: tuple[float, ...],
) -> cq.Workplane:
    """Support-free bed frame whose ribs fully bound every ventilation opening."""
    parts = [
        plate(width, edge, thickness, center=(0.0, -(depth - edge) / 2.0)),
        plate(width, edge, thickness, center=(0.0, (depth - edge) / 2.0)),
        plate(edge, depth - 2.0 * edge, thickness, center=(-(width - edge) / 2.0, 0.0)),
        plate(edge, depth - 2.0 * edge, thickness, center=((width - edge) / 2.0, 0.0)),
    ]
    parts.extend(
        plate(rib_width, depth - 2.0 * edge, thickness, center=(x, 0.0))
        for x in x_ribs
    )
    parts.extend(
        plate(width - 2.0 * edge, rib_width, thickness, center=(0.0, y))
        for y in y_ribs
    )
    return _fuse(parts)


def _obround_cut(
    width: float,
    length: float,
    height: float,
    center: tuple[float, float],
    z0: float,
) -> cq.Workplane:
    """Vertical capsule cutter used only for provisional interface slots."""
    straight = max(0.0, length - width)
    parts = [plate(width, straight, height, center=center, z0=z0)]
    for y_offset in (-straight / 2.0, straight / 2.0):
        parts.append(cylinder(width, height, (center[0], center[1] + y_offset), z0))
    return _fuse(parts)


def _open_cable_guide(
    center: tuple[float, float],
    outer_diameter: float,
    inner_diameter: float,
    height: float,
) -> cq.Workplane:
    """Upright C guide with a front opening and no printed roof."""
    guide = ring(outer_diameter, inner_diameter, height, center=center)
    opening_depth = outer_diameter / 2.0 + 2.0
    opening = plate(
        inner_diameter,
        opening_depth,
        height + 2.0,
        center=(center[0], center[1] - opening_depth / 2.0),
        z0=-1.0,
    )
    return guide.cut(opening).clean()


def _wire_jaws(
    center: tuple[float, float],
    length: float,
    gap: float,
    wall: float,
    height: float,
    catch: float,
) -> list[cq.Workplane]:
    """Two open-top, 45-degree-friendly jaws for a horizontal shelf wire."""
    left_profile = [
        (-gap / 2.0 - wall, 0.0),
        (-gap / 2.0, 0.0),
        (-gap / 2.0, height * 0.60),
        (-gap / 2.0 + catch, height * 0.76),
        (-gap / 2.0, height),
        (-gap / 2.0 - wall, height),
    ]
    right_profile = [
        (gap / 2.0, 0.0),
        (gap / 2.0 + wall, 0.0),
        (gap / 2.0 + wall, height),
        (gap / 2.0, height),
        (gap / 2.0 - catch, height * 0.76),
        (gap / 2.0, height * 0.60),
    ]
    jaws = []
    for profile in (left_profile, right_profile):
        jaw = cq.Workplane("YZ").polyline(profile).close().extrude(length / 2.0, both=True)
        jaws.append(jaw.translate((center[0], center[1], 0.0)))
    return jaws


def _kallax_boardgame_matrix(config: dict[str, Any]) -> ModelSpec:
    width = config_number(config, "width")
    depth = config_number(config, "depth")
    height = config_number(config, "height")
    wall = config_number(config, "wall")
    floor = config_number(config, "floor")

    edge = max(10.0, 4.0 * wall)
    rib_width = max(6.0, 2.0 * wall)
    divider_x = (-width / 4.0, 0.0, width / 4.0)
    base = _grid_panel(width, depth, floor, edge, rib_width, divider_x, (0.0,))

    parts = [base]
    parts.extend(
        plate(wall, depth - 2.0 * wall, height, center=(x, 0.0)) for x in divider_x
    )
    rear_depth = max(6.0, 2.0 * wall)
    parts.append(
        plate(
            width,
            rear_depth,
            height,
            center=(0.0, (depth - rear_depth) / 2.0),
        )
    )

    return ModelSpec(
        index=6,
        slug="kallax_boardgame_matrix",
        title="KALLAX Board-Game Library Matrix",
        solid=_fuse(parts),
        material="PETG prototype",
        print_orientation="perforated base frame flat on the bed; divider fins upward",
        support_required=False,
        minimum_wall_mm=min(wall, floor),
        interface_note=INTERFACE_NOTE,
        protected_features=(
            "continuous perimeter and rib frame around all base openings",
            "full-depth vertical divider fins",
            "rear edge spine",
        ),
    )


def _platsa_collection_cells(config: dict[str, Any]) -> ModelSpec:
    width = config_number(config, "width")
    depth = config_number(config, "depth")
    height = config_number(config, "height")
    wall = config_number(config, "wall")
    floor = config_number(config, "floor")

    parts = [rounded_prism(width, depth, floor, radius=5.0)]
    rear_depth = max(6.0, 2.0 * wall)
    parts.append(plate(width, rear_depth, height, center=(0.0, (depth - rear_depth) / 2.0)))

    divider_data = (
        (-0.34 * width, 0.78 * depth, 0.72 * height),
        (-0.08 * width, 0.92 * depth, height),
        (0.20 * width, 0.66 * depth, 0.58 * height),
    )
    for x, divider_depth, divider_height in divider_data:
        y = depth / 2.0 - wall - divider_depth / 2.0
        parts.append(plate(wall, divider_depth, divider_height, center=(x, y)))

    edge_height = max(18.0, height * 0.14)
    parts.extend(
        (
            plate(wall, depth, edge_height, center=(-(width - wall) / 2.0, 0.0)),
            plate(wall, depth, edge_height, center=((width - wall) / 2.0, 0.0)),
        )
    )

    return ModelSpec(
        index=7,
        slug="platsa_collection_cells",
        title="PLATSA Asymmetric Collection Cells",
        solid=_fuse(parts),
        material="PETG prototype",
        print_orientation="continuous base flat on the bed; asymmetric cell walls upward",
        support_required=False,
        minimum_wall_mm=min(wall, floor),
        interface_note=INTERFACE_NOTE,
        protected_features=(
            "unequal vertical cell widths and depths",
            "rear spine and low side-edge bracing",
            "support-free open cell tops with no elevated shelf",
        ),
    )


def _skadis_workflow_cluster(config: dict[str, Any]) -> ModelSpec:
    width = config_number(config, "width")
    height = config_number(config, "height")
    backplate = config_number(config, "backplate")
    slot_width = config_number(config, "slot_width")
    slot_length = config_number(config, "slot_length")
    pitch_x = config_number(config, "slot_pitch_x")
    pitch_y = config_number(config, "slot_pitch_z")

    holder_wall = max(2.4, slot_width * 0.45)
    tab_width = max(18.0, 3.0 * backplate)
    tab_overlap = max(6.0, backplate)
    tab_extension = 12.0
    plate_width = width - 2.0 * tab_extension
    tab_center_x = plate_width / 2.0 + tab_width / 2.0 - tab_overlap
    tab_depth = slot_length + 2.0 * holder_wall

    cluster = rounded_prism(plate_width, height, backplate, radius=6.0)
    for x in (-tab_center_x, tab_center_x):
        cluster = cluster.union(
            rounded_prism(tab_width, tab_depth, backplate, radius=4.0).translate((x, 0.0, 0.0))
        )
        cluster = cluster.cut(
            _obround_cut(slot_width, slot_length, backplate + 2.0, (x, 0.0), -1.0)
        )

    holder_z = backplate - 0.2
    holder_y = pitch_y / 2.0
    holder_height = max(22.0, slot_length * 0.8)
    holder_diameters = (18.0, 22.0, 26.0)
    for x, outer_diameter in zip((-pitch_x, 0.0, pitch_x), holder_diameters):
        cluster = cluster.union(
            ring(
                outer_diameter,
                outer_diameter - 2.0 * holder_wall,
                holder_height,
                center=(x, holder_y),
                z0=holder_z,
            )
        )

    cup = open_tray(
        min(112.0, plate_width - 2.0 * backplate),
        30.0,
        holder_height,
        wall=holder_wall,
        floor=2.4,
        radius=4.0,
    ).translate((0.0, -height / 2.0 + 20.0, holder_z))
    cluster = cluster.union(cup).clean()

    return ModelSpec(
        index=8,
        slug="skadis_workflow_cluster",
        title="SKADIS Precision-Tool Workflow Cluster",
        solid=cluster,
        material="PETG prototype",
        print_orientation="flat backplate on the bed; open holders and cup upward",
        support_required=False,
        minimum_wall_mm=min(backplate, holder_wall, 2.4),
        interface_note=(
            INTERFACE_NOTE
            + " Retention concept uses the two slotted flanges with purchased reusable straps "
            "or bolts/washers; hardware and furniture-side routing are not included."
        ),
        protected_features=(
            "compact continuous backplate",
            "two provisional in-plane slotted interface tabs",
            "explicit purchased-strap or bolt retention path through both flange slots",
            "three precision-tool sleeves and one open-front tool cup",
        ),
    )


def _besta_media_topology(config: dict[str, Any]) -> ModelSpec:
    width = config_number(config, "width")
    depth = config_number(config, "depth")
    height = config_number(config, "height")
    wall = config_number(config, "wall")

    edge = max(10.0, 4.0 * wall)
    rib_width = max(6.0, 2.0 * wall)
    rail_x = (-0.27 * width, 0.27 * width)
    base = _grid_panel(
        width,
        depth,
        wall,
        edge,
        rib_width,
        rail_x,
        (-depth / 4.0, 0.0, depth / 4.0),
    )
    parts = [base]

    rail_height = max(7.2, 3.0 * wall)
    pad_height = max(9.6, 4.0 * wall)
    pad_y = depth / 2.0 - edge - 12.0
    for x in rail_x:
        parts.append(plate(rib_width, depth - 2.0 * edge, rail_height, center=(x, 0.0)))
        for y in (-pad_y, pad_y):
            parts.append(rounded_prism(20.0, 24.0, pad_height, radius=3.0).translate((x, y, 0.0)))

    guide_outer = 18.0
    guide_inner = 10.0
    guide_y = depth / 2.0 - edge
    for x in (-0.38 * width, 0.38 * width):
        parts.append(_open_cable_guide((x, guide_y), guide_outer, guide_inner, height))

    return ModelSpec(
        index=9,
        slug="besta_media_topology",
        title="BESTA Passive Media Topology Platform",
        solid=_fuse(parts),
        material="PETG prototype",
        print_orientation="ventilated frame flat on the bed; rails and open cable guides upward",
        support_required=False,
        minimum_wall_mm=wall,
        interface_note=INTERFACE_NOTE,
        protected_features=(
            "continuous framed ventilation cells",
            "raised longitudinal device rails and local pads",
            "two open cable guides without an electronics enclosure",
        ),
    )


def _omar_shelf_deck(config: dict[str, Any], project: dict[str, Any]) -> ModelSpec:
    width = config_number(config, "width")
    depth = config_number(config, "depth")
    height = config_number(config, "height")
    wall = config_number(config, "wall")
    wire_diameter = config_number(config, "wire_diameter")
    wire_pitch = config_number(config, "wire_pitch")
    clearance = config_number(project, "nominal_xy_clearance_per_side_mm")

    deck = rounded_prism(width, depth, wall, radius=5.0)
    # A continuous deck is required to retain small items. Drain/vent slots are
    # capped at 6 mm in their narrow direction instead of leaving a coarse grid.
    slot_width = 6.0
    slot_depth = 18.0
    for x in (-75.0, -50.0, -25.0, 0.0, 25.0, 50.0, 75.0):
        for y in (-60.0, -30.0, 0.0, 30.0, 60.0):
            vent = rounded_prism(
                slot_width,
                slot_depth,
                wall + 2.0,
                radius=slot_width / 2.0,
                z0=-1.0,
            ).translate((x, y, 0.0))
            deck = deck.cut(vent)
    parts = [deck]

    front_y = -(depth - wall) / 2.0
    parts.append(plate(width, wall, height, center=(0.0, front_y)))

    jaw_gap = wire_diameter + 2.0 * clearance
    jaw_length = max(12.0, 0.4 * wire_pitch)
    catch = min(0.6, clearance + 0.25)
    for x in (-2.0 * wire_pitch, 2.0 * wire_pitch):
        for y in (-wire_pitch, wire_pitch):
            parts.extend(_wire_jaws((x, y), jaw_length, jaw_gap, wall, height, catch))

    return ModelSpec(
        index=10,
        slug="omar_shelf_deck",
        title="OMAR Snap-In Ventilated Shelf Deck",
        solid=_fuse(parts),
        material="PETG prototype",
        print_orientation=(
            "perforated deck frame on the bed with lip and jaws upward; "
            "installation may flip the printed body"
        ),
        support_required=False,
        minimum_wall_mm=wall,
        interface_note=INTERFACE_NOTE,
        protected_features=(
            "continuous deck with maximum 6 mm narrow vent openings",
            "full-width front anti-roll lip",
            "four open-top provisional wire-jaw pairs",
        ),
    )


def build(config: dict[str, Any]) -> list[ModelSpec]:
    project = config["project"]
    if project.get("units") != "mm":
        raise ValueError("Products 06-10 require millimetre configuration values")

    return [
        _kallax_boardgame_matrix(config["06_kallax_boardgame_matrix"]),
        _platsa_collection_cells(config["07_platsa_collection_cells"]),
        _skadis_workflow_cluster(config["08_skadis_workflow_cluster"]),
        _besta_media_topology(config["09_besta_media_topology"]),
        _omar_shelf_deck(config["10_omar_shelf_deck"], project),
    ]
