#!/usr/bin/env python3
"""Shared parametric interface geometry for MM-ART-010 and MM-ART-011.

The source owns the concealed seam connector, its derived rear-open pockets,
the local rear slide/snap socket, and the isolated 18 mm hanger/standoff parts.
All coordinates are millimetres. Product panel rear datum is Z=0 and the
visible face points toward +Z.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

import cadquery as cq


HERE = Path(__file__).resolve().parent
PARAMS: Dict = json.loads((HERE / "interface-parameters.json").read_text())


def _box_xyz(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=(True, True, True))
        .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    )


def _prism(points: Iterable[Tuple[float, float]], z0: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").polyline(list(points)).close().extrude(height).translate((0, 0, z0))


def seam_connector() -> cq.Workplane:
    """Double-ended fork connector, printed flat with all flexures in XY."""
    p = PARAMS["connector"]
    arm_t = p["arm_thickness_in_plane"]
    gap = p["inner_gap"]
    half_bridge = p["central_bridge_length"] / 2
    half_length = p["overall_length"] / 2
    zt = p["z_thickness"]
    y_inner = gap / 2
    y_outer = y_inner + arm_t

    solid = _box_xyz(-half_bridge, half_bridge, -y_outer, y_outer, 0, zt)
    for sign_x in (-1, 1):
        xa, xb = (half_bridge, half_length) if sign_x > 0 else (-half_length, -half_bridge)
        for sign_y in (-1, 1):
            ya, yb = (y_inner, y_outer) if sign_y > 0 else (-y_outer, -y_inner)
            solid = solid.union(_box_xyz(xa, xb, ya, yb, 0, zt))

    # The barb has a near-vertical retaining face and a long insertion ramp.
    upper_right = [(9.0, y_outer), (9.0, y_outer + 0.6), (13.2, y_outer)]
    upper_left = [(-9.0, y_outer), (-9.0, y_outer + 0.6), (-13.2, y_outer)]
    for pts in (upper_right, upper_left):
        barb = _prism(pts, 0, zt)
        solid = solid.union(barb).union(barb.mirror("XZ"))
    return solid.clean()


def connector_pocket(side: str, clearance: float) -> cq.Workplane:
    """Rear-open pocket cutter for one panel half in seam-local coordinates."""
    p = PARAMS["connector"]
    gap = PARAMS["panel"]["nominal_center_seam_gap"]
    depth = p["z_thickness"] + clearance
    throat_half = p["body_outer_width"] / 2 + clearance
    well_half = p["barb_outer_width"] / 2 + clearance
    seam_edge = gap / 2
    throat_end = 9.0
    pocket_end = p["overall_length"] / 2 + clearance
    if side == "right":
        throat = _box_xyz(seam_edge, throat_end, -throat_half, throat_half, 0, depth)
        well = _box_xyz(throat_end, pocket_end, -well_half, well_half, 0, depth)
    elif side == "left":
        throat = _box_xyz(-throat_end, -seam_edge, -throat_half, throat_half, 0, depth)
        well = _box_xyz(-pocket_end, -throat_end, -well_half, well_half, 0, depth)
    else:
        raise ValueError("side must be 'left' or 'right'")
    return throat.union(well).clean()


def connector_receiver(side: str, clearance: float) -> cq.Workplane:
    """Small panel proxy with production-depth rear-open pocket."""
    gap = PARAMS["panel"]["nominal_center_seam_gap"]
    seam_edge = gap / 2
    if side == "right":
        block = _box_xyz(seam_edge, 20.0, -7.0, 7.0, 0, 3.0)
    elif side == "left":
        block = _box_xyz(-20.0, -seam_edge, -7.0, 7.0, 0, 3.0)
    else:
        raise ValueError("side must be 'left' or 'right'")
    return block.cut(connector_pocket(side, clearance)).clean()


def socket_cutter(clearance: float) -> cq.Workplane:
    """Rear-open insertion port, locking rail and local detent relief."""
    p = PARAMS["socket_anchor"]
    depth = p["head_z_thickness"] + clearance
    entry = _box_xyz(-8.0 - clearance, 0.0, -5.0 - clearance, 5.0 + clearance, 0, depth)
    rail = _box_xyz(0.0, 14.0 + clearance, -3.0 - clearance, 3.0 + clearance, 0, depth)
    detent = _box_xyz(10.5, 13.5, 3.0, 3.65 + clearance, 0, depth)
    return entry.union(rail).union(detent).clean()


def anchor_head() -> cq.Workplane:
    """Insertion key with under-ledge tail and in-plane locking detent."""
    p = PARAMS["socket_anchor"]
    zt = p["head_z_thickness"]
    shaft = _box_xyz(-6.0, 8.0, -2.5, 2.5, 0, zt)
    tail = _box_xyz(-6.0, -2.0, -4.5, 4.5, 0, zt)
    arm = _box_xyz(-3.0, 6.0, 2.4, 3.4, 0, zt)
    bump = _prism([(4.8, 3.4), (5.4, 3.65), (6.0, 3.4)], 0, zt)
    return shaft.union(tail).union(arm).union(bump).clean()


def socket_receiver(clearance: float) -> cq.Workplane:
    block = _box_xyz(-10.0, 17.0, -8.0, 8.0, 0, 3.0)
    return block.cut(socket_cutter(clearance)).clean()


def _installed_anchor_with_stem() -> cq.Workplane:
    slide = PARAMS["socket_anchor"]["lock_slide"]
    head = anchor_head().translate((slide, 0, 0))
    stem = _box_xyz(slide - 2.5, slide + 2.5, -4.0, 4.0, -14.0, 0.02)
    return head.union(stem).clean()


def lower_standoff() -> cq.Workplane:
    """Local snap/slide anchor with a wall-contact pad at Z=-18 mm."""
    slide = PARAMS["socket_anchor"]["lock_slide"]
    pad = _box_xyz(slide - 11.0, slide + 11.0, -11.0, 11.0, -18.0, -14.0)
    return _installed_anchor_with_stem().union(pad).clean()


def upper_hanger() -> cq.Workplane:
    """Local anchor with an installer-selected screw-head reference keyhole."""
    slide = PARAMS["socket_anchor"]["lock_slide"]
    pad = _box_xyz(slide - 14.0, slide + 14.0, -16.0, 16.0, -18.0, -14.0)
    hole = (
        cq.Workplane("XY")
        .center(slide, -5.0)
        .circle(6.5)
        .extrude(5.0)
        .translate((0, 0, -18.5))
    )
    slot = _box_xyz(slide - 3.25, slide + 3.25, -5.0, 16.5, -18.5, -13.5)
    pad = pad.cut(hole.union(slot))
    head = anchor_head().translate((slide, 0, 0))
    # Twin load paths remain outside the open wall-fastener corridor. Each
    # overlaps the head and wall pad, so the exported hanger is one solid.
    left_stem = _box_xyz(slide - 6.0, slide - 3.5, -4.0, 4.0, -14.05, 0.02)
    right_stem = _box_xyz(slide + 3.5, slide + 6.0, -4.0, 4.0, -14.05, 0.02)
    return head.union(left_stem).union(right_stem).union(pad).clean()


def product_panel_pocket_cutters(side: str, panel_x_offset: float = 300.0) -> cq.Compound:
    """Three seam pocket cutters positioned in one panel's global frame."""
    clearance = PARAMS["connector"]["selected_provisional_clearance_per_side"]
    cutters = []
    for y in PARAMS["panel"]["connector_y_positions"]:
        local = connector_pocket(side, clearance).translate((panel_x_offset, y, 0))
        cutters.extend(local.vals())
    return cq.Compound.makeCompound(cutters)


def product_socket_cutters() -> cq.Compound:
    clearance = PARAMS["socket_anchor"]["selected_provisional_clearance_per_side"]
    cutters = []
    for x, y, _kind in PARAMS["panel"]["socket_centers_global"]:
        cutters.extend(socket_cutter(clearance).translate((x, y, 0)).vals())
    return cq.Compound.makeCompound(cutters)


def geometric_strain_percent(thickness: float, deflection: float, length: float) -> float:
    return 100.0 * 1.5 * thickness * deflection / (length * length)
