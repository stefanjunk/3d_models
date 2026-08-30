#!/usr/bin/env python3
"""Generate the R7-DRAFT-2 moving-Wiper purge catcher and test coupons.

The model is an original clean-room CadQuery construction from the approved
R7 requirements, the user's four physical measurements, and the owned R6
functional envelope.  No third-party mesh, STEP, profile, or dimensions are
loaded by this script.

All geometry uses millimetres.  The assembly origin is the lower Wiper screw
centre on the screw seating plane.  +X points through the catcher toward the
impact wall, +Y points toward the printer front/removal direction, and +Z is
up.  Outputs are DRAFT artifacts and remain coupon- and full-motion-gated.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
import platform
from pathlib import Path
import sys
from typing import Iterable, Sequence
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARAMS = ROOT / "params/r7-z-rider-draft2.json"
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Shape:
    if not (x1 > x0 and y1 > y0 and z1 > z0):
        raise ValueError(f"invalid box bounds: {(x0, x1, y0, y1, z0, z1)}")
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def polygon_face(points: Sequence[Sequence[float]]) -> cq.Face:
    vectors = [cq.Vector(*map(float, point)) for point in points]
    wire = cq.Wire.makePolygon(vectors, close=True)
    return cq.Face.makeFromWires(wire)


def prism_x(points_yz: Sequence[Sequence[float]], x0: float, x1: float) -> cq.Shape:
    face = polygon_face([(x0, y, z) for y, z in points_yz])
    return cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), cq.Vector(x1 - x0, 0.0, 0.0))


def prism_y(points_xz: Sequence[Sequence[float]], y0: float, y1: float) -> cq.Shape:
    face = polygon_face([(x, y0, z) for x, z in points_xz])
    return cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), cq.Vector(0.0, y1 - y0, 0.0))


def prism_z(points_xy: Sequence[Sequence[float]], z0: float, z1: float) -> cq.Shape:
    face = polygon_face([(x, y, z0) for x, y in points_xy])
    return cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), cq.Vector(0.0, 0.0, z1 - z0))


def cylinder_x(radius: float, x0: float, x1: float, y: float, z: float) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1.0, 0.0, 0.0))


def cylinder_y(radius: float, y0: float, y1: float, x: float, z: float) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0.0, 1.0, 0.0))


def cylinder_z(radius: float, z0: float, z1: float, x: float, y: float) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0.0, 0.0, 1.0))


def fuse_all(shapes: Iterable[cq.Shape]) -> cq.Shape:
    parts = list(shapes)
    if not parts:
        raise ValueError("cannot fuse an empty shape list")
    result = parts[0]
    for part in parts[1:]:
        result = result.fuse(part)
    return result.clean()


def slot_cutter_x(
    width: float,
    total_length: float,
    x0: float,
    x1: float,
    y: float,
    center_z: float,
) -> cq.Shape:
    radius = width / 2.0
    straight = max(0.0, total_length - width)
    low_z = center_z - straight / 2.0
    high_z = center_z + straight / 2.0
    parts = [
        cylinder_x(radius, x0, x1, y, low_z),
        cylinder_x(radius, x0, x1, y, high_z),
    ]
    if straight > 0.0:
        parts.append(box(x0, x1, y - radius, y + radius, low_z, high_z))
    return fuse_all(parts)


def slot_cutter_y(
    width: float,
    total_length: float,
    y0: float,
    y1: float,
    x: float,
    center_z: float,
) -> cq.Shape:
    radius = width / 2.0
    straight = max(0.0, total_length - width)
    low_z = center_z - straight / 2.0
    high_z = center_z + straight / 2.0
    parts = [
        cylinder_y(radius, y0, y1, x, low_z),
        cylinder_y(radius, y0, y1, x, high_z),
    ]
    if straight > 0.0:
        parts.append(box(x - radius, x + radius, y0, y1, low_z, high_z))
    return fuse_all(parts)


def catcher_bounds(params: dict) -> tuple[float, float, float, float, float, float]:
    """Derive the catcher envelope directly from the approved physical datums."""
    catcher = params["catcher"]
    capture_x = float(params["measured_datums"]["screw_datum_to_purge_throw_plane_x_mm"])
    half_width = float(catcher["width_x_mm"]) / 2.0
    x0, x1 = capture_x - half_width, capture_x + half_width
    y0 = float(catcher["rear_face_y_mm"])
    y1 = y0 + float(catcher["depth_y_mm"])
    z0 = float(catcher["bottom_z_mm"])
    z1 = z0 + float(catcher["height_z_mm"])
    return x0, x1, y0, y1, z0, z1


def hexagon_points(center_u: float, center_v: float, radius: float) -> list[tuple[float, float]]:
    return [
        (
            center_u + radius * math.cos(math.radians(angle)),
            center_v + radius * math.sin(math.radians(angle)),
        )
        for angle in (0, 60, 120, 180, 240, 300)
    ]


def honeycomb_centers(
    u0: float,
    u1: float,
    v0: float,
    v1: float,
    cell_radius: float,
    opening_radius: float,
    frame: float,
) -> list[tuple[float, float]]:
    step_u = 1.5 * cell_radius
    step_v = math.sqrt(3.0) * cell_radius
    opening_v = math.sqrt(3.0) * opening_radius / 2.0
    centers: list[tuple[float, float]] = []
    column = 0
    center_u = u0 + frame + opening_radius
    while center_u + opening_radius <= u1 - frame + 1.0e-7:
        offset_v = 0.5 * step_v if column % 2 else 0.0
        center_v = v0 + frame + opening_v + offset_v
        while center_v + opening_v <= v1 - frame + 1.0e-7:
            centers.append((center_u, center_v))
            center_v += step_v
        column += 1
        center_u += step_u
    return centers


def overlaps_keepout(
    center_u: float,
    center_v: float,
    opening_radius: float,
    keepouts: Sequence[Sequence[float]],
) -> bool:
    half_v = math.sqrt(3.0) * opening_radius / 2.0
    for ku0, ku1, kv0, kv1 in keepouts:
        if (
            center_u + opening_radius >= ku0
            and center_u - opening_radius <= ku1
            and center_v + half_v >= kv0
            and center_v - half_v <= kv1
        ):
            return True
    return False


def perforated_panel_x(
    x0: float,
    x1: float,
    u0: float,
    u1: float,
    z0: float,
    z1: float,
    cell_radius: float,
    rib_width: float,
    frame: float,
    keepouts: Sequence[Sequence[float]] = (),
) -> tuple[cq.Shape, int]:
    panel = box(x0, x1, u0, u1, z0, z1)
    opening_radius = cell_radius - rib_width / 2.0
    centers = honeycomb_centers(u0, u1, z0, z1, cell_radius, opening_radius, frame)
    cut_count = 0
    for center_u, center_z in centers:
        if overlaps_keepout(center_u, center_z, opening_radius, keepouts):
            continue
        cutter = prism_x(hexagon_points(center_u, center_z, opening_radius), x0 - 0.5, x1 + 0.5)
        panel = panel.cut(cutter)
        cut_count += 1
    return panel.clean(), cut_count


def perforated_panel_y(
    y0: float,
    y1: float,
    u0: float,
    u1: float,
    z0: float,
    z1: float,
    cell_radius: float,
    rib_width: float,
    frame: float,
) -> tuple[cq.Shape, int]:
    panel = box(u0, u1, y0, y1, z0, z1)
    opening_radius = cell_radius - rib_width / 2.0
    centers = honeycomb_centers(u0, u1, z0, z1, cell_radius, opening_radius, frame)
    cut_count = 0
    for center_u, center_z in centers:
        cutter = prism_y(hexagon_points(center_u, center_z, opening_radius), y0 - 0.5, y1 + 0.5)
        panel = panel.cut(cutter)
        cut_count += 1
    return panel.clean(), cut_count


def rail_profile(params: dict, center_z: float, clearance: float = 0.0) -> list[tuple[float, float]]:
    guide = params["lateral_guides"]
    base_x = float(guide["rail_base_x_mm"]) - clearance
    tip_x = float(guide["rail_tip_x_mm"]) + clearance
    base_half = float(guide["rail_base_half_height_z_mm"]) + clearance
    tip_half = float(guide["rail_tip_half_height_z_mm"]) + clearance
    return [
        (base_x, center_z - base_half),
        (tip_x, center_z - tip_half),
        (tip_x, center_z + tip_half),
        (base_x, center_z + base_half),
    ]


def build_datum_plate(params: dict) -> tuple[cq.Shape, dict[str, cq.Shape], dict]:
    plate_p = params["datum_plate"]
    guide = params["lateral_guides"]
    pitch = float(params["measured_datums"]["screw_pitch_z_mm"])
    thickness = float(plate_p["thickness_y_mm"])
    half_width = float(plate_p["width_x_mm"]) / 2.0
    z0, z1 = float(plate_p["z_min_mm"]), float(plate_p["z_max_mm"])
    plate = box(-half_width, half_width, 0.0, thickness, z0, z1)
    lower = cylinder_y(
        float(plate_p["lower_hole_diameter_mm"]) / 2.0,
        -0.5,
        thickness + 0.5,
        0.0,
        0.0,
    )
    upper = slot_cutter_y(
        float(plate_p["upper_slot_width_mm"]),
        float(plate_p["upper_slot_total_length_z_mm"]),
        -0.5,
        thickness + 0.5,
        0.0,
        pitch,
    )
    plate = plate.cut(lower).cut(upper).clean()
    rails = [
        prism_y(
            rail_profile(params, float(center_z)),
            float(guide["rail_y_min_mm"]),
            float(guide["rail_y_max_mm"]),
        )
        for center_z in guide["rail_center_z_mm"]
    ]
    latch = params["latch"]
    upper_center = max(map(float, guide["rail_center_z_mm"]))
    beam_root_z = upper_center - float(guide["receiver_pad_half_height_z_mm"])
    beam_top_z = beam_root_z + float(latch["beam_length_z_mm"])
    catch_y0 = float(guide["receiver_y_max_mm"]) - 1.1
    catch = box(
        float(guide["receiver_x_min_mm"]) - 0.7,
        float(guide["receiver_x_min_mm"]) + 0.1,
        catch_y0,
        catch_y0 + 1.3,
        beam_top_z - 3.0,
        beam_top_z + 0.5,
    )
    catch_spine_vertical = box(
        float(guide["receiver_x_min_mm"]) - 0.7,
        float(guide["receiver_x_min_mm"]) - 0.01,
        float(guide["rail_y_max_mm"]) - 0.2,
        catch_y0 + 1.3,
        upper_center + float(guide["receiver_pad_half_height_z_mm"]),
        beam_top_z + 0.5,
    )
    catch_spine_rail_link = box(
        float(guide["receiver_x_min_mm"]) - 0.7,
        float(guide["receiver_x_min_mm"]) - 0.01,
        float(guide["rail_y_max_mm"]) - 0.2,
        float(guide["rail_y_max_mm"]) + 0.2,
        upper_center - float(guide["rail_tip_half_height_z_mm"]),
        upper_center + float(guide["receiver_pad_half_height_z_mm"]) + 0.2,
    )
    latch_catch = fuse_all([catch, catch_spine_vertical, catch_spine_rail_link])
    result = fuse_all([plate, *rails, latch_catch])
    feature_shapes = {"plate": plate, "rails": fuse_all(rails), "latch_catch": latch_catch}
    head_keepout = float(plate_p["assumed_screw_head_keepout_diameter_mm"]) / 2.0
    nearest_rail_edge_gap = min(
        abs(float(center) - screw_z) - float(guide["rail_tip_half_height_z_mm"]) - head_keepout
        for center in guide["rail_center_z_mm"]
        for screw_z in (0.0, pitch)
    )
    return result, feature_shapes, {
        "screw_pitch_z_mm": pitch,
        "lower_hole_diameter_mm": float(plate_p["lower_hole_diameter_mm"]),
        "upper_slot_width_mm": float(plate_p["upper_slot_width_mm"]),
        "upper_slot_total_length_z_mm": float(plate_p["upper_slot_total_length_z_mm"]),
        "screw_axis_direction": "+Y normal to seating plane",
        "screw_seating_plane_y_mm": 0.0,
        "assumed_head_keepout_radius_mm": head_keepout,
        "minimum_assumed_head_keepout_to_rail_gap_mm": nearest_rail_edge_gap,
        "rail_center_z_mm": list(map(float, guide["rail_center_z_mm"])),
        "rail_length_y_mm": float(guide["rail_y_max_mm"]) - float(guide["rail_y_min_mm"]),
        "latch_catch_z_range_mm": [beam_top_z - 3.0, beam_top_z + 0.5],
    }


def build_bottom_ring(params: dict) -> cq.Shape:
    catcher = params["catcher"]
    mount_x, impact_x, y0, y1, z0, _ = catcher_bounds(params)
    z1 = z0 + float(catcher["bottom_frame_height_mm"])
    frame = 2.5
    outer = box(mount_x, impact_x, y0, y1, z0, z1)
    inner = box(mount_x + frame, impact_x - frame, y0 + frame, y1 - frame, z0 - 0.5, z1 + 0.5)
    return outer.cut(inner).clean()


def build_hood(params: dict, solid_wall: float) -> tuple[cq.Shape, float]:
    catcher = params["catcher"]
    _, impact_x, y0, y1, _, _ = catcher_bounds(params)
    start_z = float(catcher["hood_start_z_mm"])
    top_z = float(catcher["impact_top_z_mm"])
    hood_depth = float(catcher["hood_depth_x_mm"])
    samples = int(catcher["hood_profile_samples"])
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for index in range(samples):
        t = index / (samples - 1)
        smooth = t * t * (3.0 - 2.0 * t)
        z = start_z + (top_z - start_z) * t
        x = impact_x - hood_depth * smooth
        outer.append((x, z))
        inner.append((x - solid_wall, z))
    profile = outer + list(reversed(inner))
    hood = prism_y(profile, y0, y1)
    max_slope = 1.5 * hood_depth / (top_z - start_z)
    return hood.clean(), math.degrees(math.atan(max_slope))


def receiver_channel_cutter(params: dict, center_z: float, clearance: float) -> cq.Shape:
    guide = params["lateral_guides"]
    profile = rail_profile(params, center_z, clearance)
    profile[0] = (float(guide["receiver_x_min_mm"]) - 0.6, profile[0][1])
    profile[-1] = (float(guide["receiver_x_min_mm"]) - 0.6, profile[-1][1])
    return prism_y(
        profile,
        float(guide["receiver_y_min_mm"]) - 0.6,
        float(guide["receiver_y_max_mm"]) - float(guide["receiver_front_stop_mm"]),
    )


def build_catcher(
    params: dict,
    clearance: float,
    lattice_wall: float | None = None,
    solid_wall: float | None = None,
) -> tuple[cq.Shape, dict]:
    catcher = params["catcher"]
    guide = params["lateral_guides"]
    latch = params["latch"]
    lattice_wall = float(catcher["lattice_wall_mm"] if lattice_wall is None else lattice_wall)
    solid_wall = float(catcher["solid_wall_mm"] if solid_wall is None else solid_wall)
    mount_x, impact_x, y0, y1, bottom_z, top_z = catcher_bounds(params)
    band_z = float(catcher["capture_zone_lower_z_mm"])
    hood_z = float(catcher["hood_start_z_mm"])
    cheek_z0 = float(catcher["cheek_start_z_mm"])
    cheek_z1 = float(catcher["cheek_top_z_mm"])
    top_frame_z = float(catcher["front_rear_top_frame_z_mm"])
    cell_radius = float(catcher["honeycomb_cell_radius_mm"])
    frame = float(catcher["edge_frame_mm"])
    mount_keepout = [
        (
            float(guide["receiver_y_min_mm"]) - 1.0,
            float(guide["receiver_y_max_mm"]) + 1.0,
            min(map(float, guide["rail_center_z_mm"])) - float(guide["receiver_pad_half_height_z_mm"]) - 1.0,
            0.0,
        )
    ]
    impact_lower, impact_cells = perforated_panel_x(
        impact_x - lattice_wall,
        impact_x,
        y0,
        y1,
        bottom_z,
        band_z,
        cell_radius,
        float(catcher["lattice_wall_mm"]),
        frame,
    )
    mount_lower, mount_cells = perforated_panel_x(
        mount_x,
        mount_x + lattice_wall,
        y0,
        y1,
        bottom_z,
        band_z,
        cell_radius,
        float(catcher["lattice_wall_mm"]),
        frame,
        mount_keepout,
    )
    front_lower, front_cells = perforated_panel_y(
        y1 - lattice_wall,
        y1,
        mount_x,
        impact_x,
        bottom_z,
        band_z,
        cell_radius,
        float(catcher["lattice_wall_mm"]),
        frame,
    )
    rear_lower, rear_cells = perforated_panel_y(
        y0,
        y0 + lattice_wall,
        mount_x,
        impact_x,
        bottom_z,
        band_z,
        cell_radius,
        float(catcher["lattice_wall_mm"]),
        frame,
    )
    hood, hood_angle = build_hood(params, solid_wall)
    parts: list[cq.Shape] = [
        build_bottom_ring(params),
        impact_lower,
        mount_lower,
        front_lower,
        rear_lower,
        box(impact_x - solid_wall, impact_x, y0, y1, band_z, hood_z),
        hood,
        box(mount_x, impact_x, y1 - solid_wall, y1, cheek_z0, cheek_z1),
        box(mount_x, impact_x, y0, y0 + solid_wall, cheek_z0, cheek_z1),
        box(mount_x, impact_x, y1 - solid_wall, y1, cheek_z1, top_frame_z),
        box(mount_x, impact_x, y0, y0 + solid_wall, cheek_z1, top_frame_z),
    ]
    receiver_blocks: list[cq.Shape] = []
    for center_z in map(float, guide["rail_center_z_mm"]):
        receiver_blocks.append(
            box(
                float(guide["receiver_x_min_mm"]),
                float(guide["receiver_x_max_mm"]),
                float(guide["receiver_y_min_mm"]),
                float(guide["receiver_y_max_mm"]),
                center_z - float(guide["receiver_pad_half_height_z_mm"]),
                center_z + float(guide["receiver_pad_half_height_z_mm"]),
            )
        )
    parts.extend(receiver_blocks)
    upper_center = max(map(float, guide["rail_center_z_mm"]))
    beam_root_z = upper_center - float(guide["receiver_pad_half_height_z_mm"])
    beam_top_z = beam_root_z + float(latch["beam_length_z_mm"])
    beam_outer_x = float(guide["receiver_x_min_mm"]) + 2.4
    beam_inner_root = beam_outer_x - float(latch["root_thickness_x_mm"])
    beam_inner_tip = beam_outer_x - float(latch["beam_thickness_x_mm"])
    beam_half_y = float(latch["beam_width_y_mm"]) / 2.0
    beam_center_y = float(guide["receiver_y_max_mm"]) - beam_half_y
    beam = prism_y(
        [
            (beam_inner_root, beam_root_z),
            (beam_outer_x, beam_root_z),
            (beam_outer_x, beam_top_z),
            (beam_inner_tip, beam_top_z),
        ],
        beam_center_y - beam_half_y,
        beam_center_y + beam_half_y,
    )
    hook = prism_z(
        [
            (beam_inner_tip, beam_center_y + beam_half_y - 1.1),
            (beam_inner_tip, beam_center_y + beam_half_y),
            (beam_inner_tip - float(latch["hook_overlap_x_mm"]), beam_center_y + beam_half_y),
        ],
        beam_top_z - 3.0,
        beam_top_z,
    )
    hard_stop_x0 = beam_outer_x + float(latch["hard_stop_gap_x_mm"])
    hard_stop = box(
        hard_stop_x0,
        hard_stop_x0 + 0.8,
        beam_center_y - beam_half_y,
        beam_center_y + beam_half_y,
        beam_top_z - 6.0,
        beam_top_z + 0.5,
    )
    hard_stop_spine = box(
        hard_stop_x0,
        hard_stop_x0 + 0.8,
        float(guide["receiver_y_max_mm"]) - 1.5,
        float(guide["receiver_y_max_mm"]),
        upper_center - float(guide["receiver_pad_half_height_z_mm"]),
        beam_top_z + 0.5,
    )
    parts.extend([beam, hook, hard_stop, hard_stop_spine])
    result = fuse_all(parts)
    channel_cutters = [receiver_channel_cutter(params, float(z), clearance) for z in guide["rail_center_z_mm"]]
    for cutter in channel_cutters:
        result = result.cut(cutter)
    result = result.clean()
    drop_frame = 2.5
    return result, {
        "outer_bounds_nominal_mm": {
            "x": [mount_x, impact_x],
            "y": [y0, y1],
            "z": [bottom_z, top_z],
        },
        "measurement_binding": {
            "capture_center_x_mm": (mount_x + impact_x) / 2.0,
            "purge_deposition_z_mm": -float(params["measured_datums"]["lower_screw_to_purge_deposition_plane_mm"]),
            "closed_capture_zone_z_mm": [band_z, hood_z],
            "front_of_screw_plane_y_mm": y0,
            "measured_rear_wiper_extent_y_mm": float(params["machine_keepout"]["rear_wiper_extent_y_mm"]),
        },
        "drop_opening_clear_mm": [
            float(catcher["width_x_mm"]) - 2.0 * drop_frame,
            float(catcher["depth_y_mm"]) - 2.0 * drop_frame,
        ],
        "honeycomb_openings": impact_cells + mount_cells + front_cells + rear_cells,
        "honeycomb_openings_by_face": {
            "impact": impact_cells,
            "mount": mount_cells,
            "front": front_cells,
            "rear": rear_cells,
        },
        "lattice_wall_mm": lattice_wall,
        "solid_wall_mm": solid_wall,
        "hood_max_overhang_from_vertical_deg": hood_angle,
        "receiver_clearance_each_surface_mm": clearance,
        "receiver_front_stop_mm": float(guide["receiver_front_stop_mm"]),
        "service_stroke_mm": (
            float(guide["rail_y_max_mm"])
            - float(guide["rail_y_min_mm"])
            + 2.0 * clearance
        ),
        "latch_beam_root_z_mm": beam_root_z,
        "latch_beam_top_z_mm": beam_top_z,
        "latch_hard_stop_gap_x_mm": float(latch["hard_stop_gap_x_mm"]),
        "open_bottom_by_construction": True,
        "horizontal_purge_storage_pocket": False,
    }


def build_mount_pattern_gauge(params: dict) -> cq.Shape:
    pitch = float(params["measured_datums"]["screw_pitch_z_mm"])
    plate = params["datum_plate"]
    thickness = 1.2
    gauge = box(-7.0, 7.0, 0.0, thickness, -5.0, pitch + 5.0)
    lower = cylinder_y(float(plate["lower_hole_diameter_mm"]) / 2.0, -0.5, thickness + 0.5, 0.0, 0.0)
    upper = slot_cutter_y(
        float(plate["upper_slot_width_mm"]),
        float(plate["upper_slot_total_length_z_mm"]),
        -0.5,
        thickness + 0.5,
        0.0,
        pitch,
    )
    return gauge.cut(lower).cut(upper).clean()


def build_slide_coupon_male(params: dict) -> cq.Shape:
    guide = params["lateral_guides"]
    rail = prism_y(rail_profile(params, 0.0), 0.0, 12.0)
    base = box(0.0, float(guide["rail_base_x_mm"]) + 0.3, 0.0, 12.0, -5.5, 5.5)
    return base.fuse(rail).clean()


def build_slide_coupon_female(params: dict, clearance: float) -> cq.Shape:
    guide = params["lateral_guides"]
    block = box(
        float(guide["receiver_x_min_mm"]),
        float(guide["receiver_x_max_mm"]),
        0.0,
        15.0,
        -3.5,
        3.5,
    )
    cutter = prism_y(rail_profile(params, 0.0, clearance), -0.5, 12.8)
    return block.cut(cutter).clean()


def build_latch_coupon(params: dict) -> tuple[cq.Shape, cq.Shape]:
    guide = params["lateral_guides"]
    latch = params["latch"]
    beam_length = float(latch["beam_length_z_mm"])
    beam_outer_x = 4.5
    beam_inner_root = beam_outer_x - float(latch["root_thickness_x_mm"])
    beam_inner_tip = beam_outer_x - float(latch["beam_thickness_x_mm"])
    half_y = float(latch["beam_width_y_mm"]) / 2.0
    flex_base = box(0.0, 5.5, -half_y, half_y, 0.0, 4.0)
    beam = prism_y(
        [
            (beam_inner_root, 3.0),
            (beam_outer_x, 3.0),
            (beam_outer_x, 3.0 + beam_length),
            (beam_inner_tip, 3.0 + beam_length),
        ],
        -half_y,
        half_y,
    )
    hook = prism_z(
        [
            (beam_inner_tip + 0.15, 0.0),
            (beam_inner_tip + 0.15, 1.1),
            (beam_inner_tip - float(latch["hook_overlap_x_mm"]), 1.1),
        ],
        beam_length,
        beam_length + 3.0,
    ).translate(cq.Vector(0.0, half_y - 1.1, 0.0))
    stop_x = beam_outer_x + float(latch["hard_stop_gap_x_mm"])
    stop = box(stop_x, stop_x + 0.8, -half_y, half_y, beam_length - 3.0, beam_length + 3.5)
    stop_spine = box(stop_x, stop_x + 0.8, -half_y, -half_y + 1.5, 0.0, beam_length + 3.5)
    flex = fuse_all([flex_base, beam, hook, stop, stop_spine])
    fixed_base = box(0.0, 4.0, -half_y, half_y, 0.0, 4.0)
    catch = box(2.2, 3.2, half_y - 1.1, half_y, beam_length, beam_length + 3.5)
    catch_spine = box(2.2, 3.2, half_y - 1.1, half_y, 0.0, beam_length + 3.5)
    fixed = fuse_all([fixed_base, catch, catch_spine])
    return flex, fixed


def build_measurement_reference(params: dict) -> cq.Shape:
    """Non-manufacturing STEP reference for the four user-measured datums."""
    measured = params["measured_datums"]
    pitch = float(measured["screw_pitch_z_mm"])
    purge_z = -float(measured["lower_screw_to_purge_deposition_plane_mm"])
    purge_x = float(measured["screw_datum_to_purge_throw_plane_x_mm"])
    rear_y = -float(measured["screw_plane_to_rear_wiper_extent_mm"])
    radius = 0.45
    return cq.Compound.makeCompound(
        [
            cylinder_z(radius, 0.0, pitch, 0.0, 0.0),
            cylinder_z(radius, purge_z, 0.0, 0.0, 0.0),
            cylinder_x(radius, 0.0, purge_x, 0.0, purge_z),
            cylinder_y(radius, rear_y, 0.0, 0.0, 0.0),
            cq.Solid.makeSphere(1.2, cq.Vector(0.0, 0.0, 0.0)),
            cq.Solid.makeSphere(1.2, cq.Vector(0.0, 0.0, pitch)),
            cq.Solid.makeSphere(1.2, cq.Vector(purge_x, 0.0, purge_z)),
            cq.Solid.makeSphere(1.2, cq.Vector(0.0, rear_y, 0.0)),
        ]
    )


def orient_on_bed(
    shape: cq.Shape,
    rotation_x_deg: float = 0.0,
    rotation_y_deg: float = 0.0,
    rotation_z_deg: float = 0.0,
) -> cq.Shape:
    result = shape
    if abs(rotation_x_deg) > 1.0e-9:
        result = result.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), rotation_x_deg)
    if abs(rotation_y_deg) > 1.0e-9:
        result = result.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), rotation_y_deg)
    if abs(rotation_z_deg) > 1.0e-9:
        result = result.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), rotation_z_deg)
    bounds = result.BoundingBox()
    return result.translate(cq.Vector(0.0, 0.0, -bounds.zmin))


def export_shape(
    shape: cq.Shape,
    step_path: Path,
    stl_path: Path,
    tolerance: float,
    angular_tolerance: float,
    print_rotation_xyz_deg: Sequence[float] = (0.0, 0.0, 0.0),
) -> None:
    step_path.parent.mkdir(parents=True, exist_ok=True)
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(step_path))
    print_shape = orient_on_bed(shape, *map(float, print_rotation_xyz_deg))
    cq.exporters.export(
        print_shape,
        str(stl_path),
        tolerance=tolerance,
        angularTolerance=angular_tolerance,
    )


def mesh_audit(path: Path) -> dict:
    loaded = trimesh.load(path, force="mesh", process=True)
    if isinstance(loaded, trimesh.Scene):
        mesh = loaded.to_geometry()
    else:
        mesh = loaded
    components = mesh.split(only_watertight=False)
    checks = {
        "nonempty": bool(len(mesh.vertices) and len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "positive_volume": bool(abs(float(mesh.volume)) > 0.0),
        "single_component": len(components) == 1,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": {
            "vertices": int(len(mesh.vertices)),
            "triangles": int(len(mesh.faces)),
            "components": int(len(components)),
            "bounds_min_mm": mesh.bounds[0].tolist(),
            "bounds_max_mm": mesh.bounds[1].tolist(),
            "volume_mm3": abs(float(mesh.volume)),
            "surface_area_mm2": float(mesh.area),
            "file_bytes": path.stat().st_size,
            "audit_loading": "trimesh process=True merges exactly coincident STL vertices; no repaired mesh is exported",
        },
    }


def xml_number(value: float) -> str:
    return (f"{float(value):.6f}").rstrip("0").rstrip(".") or "0"


def write_core_3mf(path: Path, object_name: str, meshes: Sequence[trimesh.Trimesh]) -> None:
    """Write a deterministic minimal Core 3MF without slicer-specific metadata."""
    ET.register_namespace("", CORE_NS)
    model = ET.Element(f"{{{CORE_NS}}}model", {"unit": "millimeter", f"{{{XML_NS}}}lang": "de-DE"})
    resources = ET.SubElement(model, f"{{{CORE_NS}}}resources")
    base = ET.SubElement(resources, f"{{{CORE_NS}}}basematerials", {"id": "1"})
    ET.SubElement(base, f"{{{CORE_NS}}}base", {"name": "PETG draft", "displaycolor": "#08777DFF"})
    obj = ET.SubElement(resources, f"{{{CORE_NS}}}object", {"id": "2", "type": "model", "name": object_name})
    mesh_node = ET.SubElement(obj, f"{{{CORE_NS}}}mesh")
    vertices_node = ET.SubElement(mesh_node, f"{{{CORE_NS}}}vertices")
    triangles_node = ET.SubElement(mesh_node, f"{{{CORE_NS}}}triangles")
    offset = 0
    for mesh in meshes:
        # STL repeats triangle corners.  Index coincident vertices before writing
        # the Core 3MF so topology validators see the same closed shell as the
        # processed source mesh instead of an edge-disconnected triangle soup.
        indexed_mesh = mesh.copy()
        indexed_mesh.merge_vertices()
        for x, y, z in np.asarray(indexed_mesh.vertices, dtype=float):
            ET.SubElement(
                vertices_node,
                f"{{{CORE_NS}}}vertex",
                {"x": xml_number(x), "y": xml_number(y), "z": xml_number(z)},
            )
        for a, b, c in np.asarray(indexed_mesh.faces, dtype=np.int64):
            ET.SubElement(
                triangles_node,
                f"{{{CORE_NS}}}triangle",
                {
                    "v1": str(int(a) + offset),
                    "v2": str(int(b) + offset),
                    "v3": str(int(c) + offset),
                    "pid": "1",
                    "p1": "0",
                    "p2": "0",
                    "p3": "0",
                },
            )
        offset += len(indexed_mesh.vertices)
    build_node = ET.SubElement(model, f"{{{CORE_NS}}}build")
    ET.SubElement(build_node, f"{{{CORE_NS}}}item", {"objectid": "2"})
    model_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(model, encoding="utf-8")
    content = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="{CONTENT_NS}">' 
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>'
    ).encode()
    rels = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="{REL_NS}">' 
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>'
    ).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for member_name, data in (
            ("[Content_Types].xml", content),
            ("_rels/.rels", rels),
            ("3D/3dmodel.model", model_bytes),
        ):
            info = zipfile.ZipInfo(member_name, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)


def load_print_mesh(path: Path, translation: Sequence[float] = (0.0, 0.0, 0.0)) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="mesh", process=False)
    if isinstance(loaded, trimesh.Scene):
        loaded = loaded.to_geometry()
    mesh = loaded.copy()
    mesh.apply_translation(np.asarray(translation, dtype=float))
    return mesh


def solid_report(shape: cq.Shape) -> dict:
    bounds = shape.BoundingBox()
    checks = {
        "valid_brep": bool(shape.isValid()),
        "positive_volume": shape.Volume() > 0.0,
        "single_solid": len(shape.Solids()) == 1,
    }
    center = shape.Center()
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": {
            "solids": len(shape.Solids()),
            "volume_mm3": shape.Volume(),
            "center_of_mass_mm": [center.x, center.y, center.z],
            "bounds_min_mm": [bounds.xmin, bounds.ymin, bounds.zmin],
            "bounds_max_mm": [bounds.xmax, bounds.ymax, bounds.zmax],
        },
    }


def latch_calculation(params: dict) -> dict:
    latch = params["latch"]
    length = float(latch["beam_length_z_mm"])
    thickness = float(latch["beam_thickness_x_mm"])
    width = float(latch["beam_width_y_mm"])
    deflection = float(latch["nominal_deflection_x_mm"])
    strain = 1.5 * thickness * deflection / (length * length)
    forces = []
    for modulus in map(float, latch["petg_modulus_range_mpa"]):
        force = modulus * width * thickness**3 * deflection / (4.0 * length**3)
        forces.append(force)
    return {
        "model": "simple rectangular cantilever screening bound; tapered root and printed anisotropy not represented",
        "beam_length_mm": length,
        "beam_thickness_mm": thickness,
        "beam_width_mm": width,
        "nominal_tip_deflection_mm": deflection,
        "estimated_outer_fibre_strain_percent": strain * 100.0,
        "estimated_force_range_n": [min(forces), max(forces)],
        "hard_stop_gap_mm": float(latch["hard_stop_gap_x_mm"]),
        "status": "COUPON_REQUIRED",
    }


def shape_triangles(shape: cq.Shape, tolerance: float, angular_tolerance: float) -> tuple[np.ndarray, np.ndarray]:
    vertices, triangles = shape.tessellate(tolerance, angular_tolerance)
    points = np.asarray([[v.x, v.y, v.z] for v in vertices], dtype=float)
    faces = np.asarray(triangles, dtype=np.int64)
    return points, faces


def add_shape_to_axes(
    ax,
    shape: cq.Shape,
    color: str,
    tolerance: float,
    angular_tolerance: float,
    alpha: float = 1.0,
    max_faces: int = 16000,
) -> None:
    vertices, faces = shape_triangles(shape, tolerance, angular_tolerance)
    if len(faces) > max_faces:
        step = math.ceil(len(faces) / max_faces)
        faces = faces[::step]
    collection = Poly3DCollection(vertices[faces], facecolor=color, edgecolor="none", alpha=alpha)
    ax.add_collection3d(collection)


def set_axes_equal(ax, shapes: Sequence[cq.Shape]) -> None:
    mins = np.asarray(
        [[s.BoundingBox().xmin, s.BoundingBox().ymin, s.BoundingBox().zmin] for s in shapes],
        dtype=float,
    ).min(axis=0)
    maxs = np.asarray(
        [[s.BoundingBox().xmax, s.BoundingBox().ymax, s.BoundingBox().zmax] for s in shapes],
        dtype=float,
    ).max(axis=0)
    center = (mins + maxs) / 2.0
    radius = max(maxs - mins) / 2.0 * 1.12
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)
    ax.set_box_aspect((1, 1, 1))


def save_preview(
    path: Path,
    plate: cq.Shape,
    catcher: cq.Shape,
    measurement_reference: cq.Shape,
    params: dict,
    tolerance: float,
    angular_tolerance: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(13, 6.5), facecolor="#F4F1EB")
    for index, exploded in enumerate((False, True), start=1):
        ax = figure.add_subplot(1, 2, index, projection="3d", facecolor="#F4F1EB")
        shown_catcher = catcher.translate(cq.Vector(0.0, 13.0 if exploded else 0.0, 0.0))
        add_shape_to_axes(ax, plate, "#08777D", tolerance, angular_tolerance)
        add_shape_to_axes(ax, shown_catcher, "#C9CDCB", tolerance, angular_tolerance, alpha=0.94)
        add_shape_to_axes(ax, measurement_reference, "#E5722A", tolerance, angular_tolerance, alpha=0.72)
        set_axes_equal(ax, [plate, shown_catcher, measurement_reference])
        ax.view_init(elev=20, azim=138)
        ax.set_xlabel("+X purge/impact")
        ax.set_ylabel("+Y front/service; rear keep-out is -Y")
        ax.set_zlabel("+Z")
        ax.set_title("assembled datum" if not exploded else "13 mm service preview (limit is 15 mm)")
    figure.suptitle("R7-DRAFT-2 Z-Rider — measured datums bound to CAD, not physical proof", fontsize=14)
    figure.tight_layout()
    figure.savefig(path, dpi=170)
    plt.close(figure)


def save_measurement_diagram(path: Path, params: dict) -> None:
    """Create an orthographic proof that every user measurement drives a named feature."""
    from matplotlib.patches import Rectangle

    measured = params["measured_datums"]
    catcher = params["catcher"]
    x0, x1, y0, y1, z0, z1 = catcher_bounds(params)
    purge_x = float(measured["screw_datum_to_purge_throw_plane_x_mm"])
    purge_z = -float(measured["lower_screw_to_purge_deposition_plane_mm"])
    pitch = float(measured["screw_pitch_z_mm"])
    rear_y = -float(measured["screw_plane_to_rear_wiper_extent_mm"])
    capture_z0 = float(catcher["capture_zone_lower_z_mm"])
    capture_z1 = float(catcher["hood_start_z_mm"])
    figure, axes = plt.subplots(1, 2, figsize=(13, 6.5), facecolor="#F4F1EB")

    front = axes[0]
    front.set_title("Frontansicht X/Z — Fangzone und Schraubendatum")
    front.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor="#D8DCDA", edgecolor="#596260", lw=2))
    front.add_patch(Rectangle((x0, capture_z0), x1 - x0, capture_z1 - capture_z0, facecolor="#7FD5D3", alpha=0.45, edgecolor="none"))
    front.scatter([0.0, 0.0], [0.0, pitch], s=75, c="#08777D", zorder=5)
    front.axvline(purge_x, color="#E5722A", ls="--", lw=2)
    front.axhline(purge_z, color="#E5722A", ls="--", lw=2)
    front.annotate("17 mm", xy=(-12, pitch), xytext=(-12, 0), arrowprops={"arrowstyle": "<->", "color": "#A04418"}, ha="center", va="center", color="#A04418")
    front.annotate("10 mm", xy=(-20, 0), xytext=(-20, purge_z), arrowprops={"arrowstyle": "<->", "color": "#A04418"}, ha="center", va="center", color="#A04418")
    front.annotate("37 mm", xy=(purge_x, -28), xytext=(0, -28), arrowprops={"arrowstyle": "<->", "color": "#A04418"}, ha="center", va="center", color="#A04418")
    front.text(purge_x + 1.5, purge_z + 1.0, "Purge-Datum", color="#A04418")
    front.text(x0 + 2.0, capture_z0 + 2.0, "geschlossene Fangzone", color="#08777D")
    front.set_xlabel("X [mm] — vom Schraubendatum zur Wurfbahn")
    front.set_ylabel("Z [mm]")
    front.set_aspect("equal", adjustable="box")
    front.set_xlim(-24, 74)
    front.set_ylim(-40, 32)
    front.grid(True, alpha=0.25)

    top = axes[1]
    top.set_title("Draufsicht X/Y — rückwärtiger Maschinen-Keep-out")
    top.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="#D8DCDA", edgecolor="#596260", lw=2, label="Fangkopf"))
    top.add_patch(Rectangle((-10, rear_y), 80, -rear_y, facecolor="#E5722A", alpha=0.18, edgecolor="#A04418", hatch="//", label="40-mm-Wiper-Keep-out"))
    top.axhline(0.0, color="#08777D", lw=2, label="Schraubenauflage Y=0")
    top.scatter([0.0], [0.0], s=75, c="#08777D", zorder=5)
    top.annotate("40 mm", xy=(-5, 0), xytext=(-5, rear_y), arrowprops={"arrowstyle": "<->", "color": "#A04418"}, ha="center", va="center", color="#A04418")
    top.text(x0 + 2.0, y0 + 2.0, "gesamte neue Geometrie vor Y=0", color="#08777D")
    top.set_xlabel("X [mm]")
    top.set_ylabel("Y [mm] — +Y nach vorn")
    top.set_aspect("equal", adjustable="box")
    top.set_xlim(-12, 74)
    top.set_ylim(-44, 50)
    top.grid(True, alpha=0.25)
    top.legend(loc="lower right")

    figure.suptitle("R7-DRAFT-2 — verbindliche Maße als CAD-Zwangsbedingungen", fontsize=15)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180)
    plt.close(figure)


def assert_parameters(params: dict) -> None:
    plate = params["datum_plate"]
    guide = params["lateral_guides"]
    catcher = params["catcher"]
    manufacturing = params["manufacturing"]
    measured = params["measured_datums"]
    pitch = float(measured["screw_pitch_z_mm"])
    assert abs(pitch - 17.0) < 1.0e-9
    assert abs(float(measured["lower_screw_to_purge_deposition_plane_mm"]) - 10.0) < 1.0e-9
    assert abs(float(measured["screw_datum_to_purge_throw_plane_x_mm"]) - 37.0) < 1.0e-9
    assert abs(float(measured["screw_plane_to_rear_wiper_extent_mm"]) - 40.0) < 1.0e-9
    assert float(plate["lower_hole_diameter_mm"]) > 0.0
    assert float(plate["upper_slot_total_length_z_mm"]) >= float(plate["upper_slot_width_mm"])
    assert len(guide["rail_center_z_mm"]) == 2
    assert float(guide["rail_y_max_mm"]) > float(guide["rail_y_min_mm"])
    assert 0.0 < float(guide["default_clearance_mm"]) <= 0.6
    assert float(catcher["width_x_mm"]) == 62.0
    assert float(catcher["depth_y_mm"]) == 44.0
    assert float(catcher["height_z_mm"]) == 62.0
    x0, x1, y0, _, _, _ = catcher_bounds(params)
    assert abs((x0 + x1) / 2.0 - float(measured["screw_datum_to_purge_throw_plane_x_mm"])) < 1.0e-9
    assert y0 >= float(params["machine_keepout"]["screw_seating_plane_y_mm"])
    purge_z = -float(measured["lower_screw_to_purge_deposition_plane_mm"])
    assert float(catcher["capture_zone_lower_z_mm"]) <= purge_z <= float(catcher["hood_start_z_mm"])
    assert float(catcher["solid_wall_mm"]) >= 3.0 * float(manufacturing["line_width_mm"])
    service_stroke = (
        float(guide["rail_y_max_mm"])
        - float(guide["rail_y_min_mm"])
        + 2.0 * float(guide["default_clearance_mm"])
    )
    assert service_stroke <= float(guide["maximum_service_stroke_mm"])


def build(output_dir: Path, params_path: Path) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    params = json.loads(params_path.read_text(encoding="utf-8"))
    assert_parameters(params)
    manufacturing = params["manufacturing"]
    tolerance = float(manufacturing["stl_linear_tolerance_mm"])
    angular_tolerance = float(manufacturing["stl_angular_tolerance_rad"])
    density = float(manufacturing["density_g_cm3"])

    datum_plate, datum_features, datum_metrics = build_datum_plate(params)
    clearance = float(params["lateral_guides"]["default_clearance_mm"])
    catcher, catcher_metrics = build_catcher(params, clearance)
    mount_gauge = build_mount_pattern_gauge(params)
    slide_male = build_slide_coupon_male(params)
    latch_flex, latch_fixed = build_latch_coupon(params)
    measurement_reference = build_measurement_reference(params)

    parts: dict[str, tuple[cq.Shape, tuple[float, float, float]]] = {
        "datum-plate-draft": (datum_plate, (90.0, 0.0, 0.0)),
        "moving-catcher-balanced-draft": (catcher, (0.0, 0.0, 0.0)),
        "mount-pattern-gauge": (mount_gauge, (90.0, 0.0, 0.0)),
        "lateral-slide-male": (slide_male, (0.0, -90.0, 0.0)),
        "latch-cycle-flex": (latch_flex, (0.0, 0.0, 0.0)),
        "latch-cycle-fixed": (latch_fixed, (0.0, 0.0, 0.0)),
    }
    coupon_shapes: dict[str, cq.Shape] = {}
    for variant in map(float, params["lateral_guides"]["clearance_coupon_variants_mm"]):
        key = f"lateral-slide-female-c{int(round(variant * 100)):03d}"
        coupon_shapes[key] = build_slide_coupon_female(params, variant)
        parts[key] = (coupon_shapes[key], (0.0, -90.0, 0.0))

    brep_reports: dict[str, dict] = {}
    mesh_reports: dict[str, dict] = {}
    artifact_paths: list[Path] = []
    for name, (shape, rotation) in parts.items():
        step_path = output_dir / "models/step" / f"{name}.step"
        stl_path = output_dir / "models/stl" / f"{name}.stl"
        export_shape(shape, step_path, stl_path, tolerance, angular_tolerance, rotation)
        artifact_paths.extend([step_path, stl_path])
        brep_reports[name] = solid_report(shape)
        mesh_reports[name] = mesh_audit(stl_path)

    reference_path = output_dir / "models/reference/measured-datums-reference.step"
    reference_path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(measurement_reference, str(reference_path))
    artifact_paths.append(reference_path)

    stl_dir = output_dir / "models/stl"
    three_mf_exports = {
        "DRAFT-R7-purge-catcher-body.3mf": (
            "R7-DRAFT-2 measured purge catcher body",
            [load_print_mesh(stl_dir / "moving-catcher-balanced-draft.stl")],
        ),
        "DRAFT-R7-wiper-datum-plate.3mf": (
            "R7-DRAFT-2 measured Wiper datum plate",
            [load_print_mesh(stl_dir / "datum-plate-draft.stl")],
        ),
        "DRAFT-R7-mount-pattern-gauge.3mf": (
            "R7-DRAFT-2 17 mm mount pattern gauge",
            [load_print_mesh(stl_dir / "mount-pattern-gauge.stl")],
        ),
        "DRAFT-R7-slide-clearance-coupon.3mf": (
            "R7-DRAFT-2 0.30 mm slide clearance coupon",
            [
                load_print_mesh(stl_dir / "lateral-slide-male.stl"),
                load_print_mesh(stl_dir / "lateral-slide-female-c030.stl", (18.0, 0.0, 0.0)),
            ],
        ),
        "DRAFT-R7-latch-cycle-coupon.3mf": (
            "R7-DRAFT-2 latch cycle coupon",
            [
                load_print_mesh(stl_dir / "latch-cycle-flex.stl"),
                load_print_mesh(stl_dir / "latch-cycle-fixed.stl", (14.0, 0.0, 0.0)),
            ],
        ),
    }
    for filename, (object_name, meshes) in three_mf_exports.items():
        path = output_dir / "models/3mf" / filename
        write_core_3mf(path, object_name, meshes)
        artifact_paths.append(path)

    assembly = cq.Compound.makeCompound([datum_plate, catcher])
    assembly_path = output_dir / "models/step/r7-z-rider-balanced-assembly-draft.step"
    assembly_path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(assembly, str(assembly_path))
    artifact_paths.append(assembly_path)

    variants = {
        "conservative": {"lattice_wall_mm": 1.70, "solid_wall_mm": 2.10},
        "balanced": {
            "lattice_wall_mm": float(params["catcher"]["lattice_wall_mm"]),
            "solid_wall_mm": float(params["catcher"]["solid_wall_mm"]),
        },
        "aggressive": {"lattice_wall_mm": 1.00, "solid_wall_mm": 1.35},
    }
    variant_reports: dict[str, dict] = {}
    for name, values in variants.items():
        if name == "balanced":
            variant_shape = catcher
            variant_geometry = catcher_metrics
        else:
            variant_shape, variant_geometry = build_catcher(
                params,
                clearance,
                lattice_wall=float(values["lattice_wall_mm"]),
                solid_wall=float(values["solid_wall_mm"]),
            )
        stl_path = output_dir / "models/optimization" / f"moving-catcher-{name}.stl"
        stl_path.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(
            orient_on_bed(variant_shape),
            str(stl_path),
            tolerance=tolerance,
            angularTolerance=angular_tolerance,
        )
        artifact_paths.append(stl_path)
        audit = mesh_audit(stl_path)
        mass = variant_shape.Volume() / 1000.0 * density
        variant_reports[name] = {
            "geometry": values,
            "brep": solid_report(variant_shape),
            "mesh": audit,
            "catcher_mass_g": mass,
            "moving_mass_with_common_plate_g": mass + datum_plate.Volume() / 1000.0 * density,
            "service_stroke_mm": variant_geometry["service_stroke_mm"],
            "slicer_metrics": "NOT_RUN",
            "physical_evidence": "NOT_RUN",
        }

    preview_path = output_dir / "previews/r7-z-rider-balanced-draft.png"
    save_preview(preview_path, datum_plate, catcher, measurement_reference, params, tolerance, angular_tolerance)
    artifact_paths.append(preview_path)
    measurement_preview_path = output_dir / "previews/r7-measured-datums.png"
    save_measurement_diagram(measurement_preview_path, params)
    artifact_paths.append(measurement_preview_path)

    plate_mass = datum_plate.Volume() / 1000.0 * density
    catcher_mass = catcher.Volume() / 1000.0 * density
    moving_mass = plate_mass + catcher_mass
    collision_volume = datum_plate.intersect(catcher).Volume()
    mount_x, impact_x, y0, y1, body_bottom, _ = catcher_bounds(params)
    drop_probe = box(
        mount_x + 2.6,
        impact_x - 2.6,
        y0 + 2.6,
        y1 - 2.6,
        body_bottom - 0.2,
        body_bottom + 0.8,
    )
    drop_probe_intersection = catcher.intersect(drop_probe).Volume()
    measured = params["measured_datums"]
    purge_z = -float(measured["lower_screw_to_purge_deposition_plane_mm"])
    measured_binding = {
        "M-R7-001-screw-pitch-z": {
            "expected_mm": 17.0,
            "actual_mm": datum_metrics["screw_pitch_z_mm"],
            "deviation_mm": datum_metrics["screw_pitch_z_mm"] - 17.0,
            "bound_feature": "lower round hole center to upper slot center",
        },
        "M-R7-002-lower-screw-to-purge-z": {
            "expected_mm": 10.0,
            "actual_mm": abs(purge_z),
            "deviation_mm": abs(purge_z) - 10.0,
            "bound_feature": "purge deposition datum inside closed capture zone",
        },
        "M-R7-003-screw-to-throw-x": {
            "expected_mm": 37.0,
            "actual_mm": (mount_x + impact_x) / 2.0,
            "deviation_mm": (mount_x + impact_x) / 2.0 - 37.0,
            "bound_feature": "catcher capture center plane",
        },
        "M-R7-004-rear-wiper-keepout-y": {
            "expected_mm": 40.0,
            "actual_mm": abs(float(params["machine_keepout"]["rear_wiper_extent_y_mm"])),
            "deviation_mm": abs(float(params["machine_keepout"]["rear_wiper_extent_y_mm"])) - 40.0,
            "bound_feature": "reference-only rear keep-out; added geometry stays at y >= 0",
        },
    }
    measurement_checks = {
        "screw_pitch_bound_to_hole_centers": abs(measured_binding["M-R7-001-screw-pitch-z"]["deviation_mm"]) <= 1.0e-9,
        "purge_z_bound_inside_closed_capture_zone": (
            abs(measured_binding["M-R7-002-lower-screw-to-purge-z"]["deviation_mm"]) <= 1.0e-9
            and float(params["catcher"]["capture_zone_lower_z_mm"]) <= purge_z <= float(params["catcher"]["hood_start_z_mm"])
        ),
        "throw_x_bound_to_capture_center": abs(measured_binding["M-R7-003-screw-to-throw-x"]["deviation_mm"]) <= 1.0e-9,
        "rear_keepout_bound_and_respected": (
            abs(measured_binding["M-R7-004-rear-wiper-keepout-y"]["deviation_mm"]) <= 1.0e-9
            and float(brep_reports["datum-plate-draft"]["metrics"]["bounds_min_mm"][1]) >= -1.0e-6
            and float(brep_reports["moving-catcher-balanced-draft"]["metrics"]["bounds_min_mm"][1]) >= -1.0e-6
        ),
    }
    geometry_checks = {
        "datum_plate_valid_single_solid": brep_reports["datum-plate-draft"]["status"] == "PASS",
        "catcher_valid_single_solid": brep_reports["moving-catcher-balanced-draft"]["status"] == "PASS",
        "datum_and_catcher_no_hard_collision": collision_volume <= 1.0e-6,
        "drop_opening_probe_clear": drop_probe_intersection <= 1.0e-6,
        **measurement_checks,
        "two_spatially_separated_guides": len(datum_metrics["rail_center_z_mm"]) == 2,
        "service_stroke_within_15_mm": catcher_metrics["service_stroke_mm"] <= 15.0,
        "hood_overhang_at_most_45_deg": catcher_metrics["hood_max_overhang_from_vertical_deg"] <= 45.0,
        "open_bottom_declared": catcher_metrics["open_bottom_by_construction"],
        "no_horizontal_storage_pocket": not catcher_metrics["horizontal_purge_storage_pocket"],
        "moving_mass_at_most_25_g": moving_mass <= float(manufacturing["moving_mass_target_g"]),
        "all_print_meshes_pass": all(report["status"] == "PASS" for report in mesh_reports.values()),
    }
    geometry_validation = {
        "schema_version": "1.0",
        "project_id": params["project_id"],
        "geometry_revision": params["geometry_revision"],
        "status": "PASS_DIGITAL_DRAFT" if all(geometry_checks.values()) else "FAIL",
        "checks": geometry_checks,
        "metrics": {
            "measured_datum_bindings": measured_binding,
            "datum_plate": datum_metrics,
            "catcher": catcher_metrics,
            "datum_catcher_collision_volume_mm3": collision_volume,
            "drop_probe_intersection_volume_mm3": drop_probe_intersection,
            "datum_plate_mass_g": plate_mass,
            "catcher_mass_g": catcher_mass,
            "moving_mass_g": moving_mass,
            "moving_mass_target_g": float(manufacturing["moving_mass_target_g"]),
            "baseline_r6_moving_mass_g": 31.98899958276287,
            "mass_reduction_vs_r6_percent": (1.0 - moving_mass / 31.98899958276287) * 100.0,
        },
        "brep_reports": brep_reports,
        "mesh_reports": mesh_reports,
        "physical_gates": params["physical_gates"],
        "release_state": "DRAFT_NOT_PRINT_QUALIFIED",
    }
    validation_path = output_dir / "reports/geometry-validation.json"
    write_json(validation_path, geometry_validation)
    artifact_paths.append(validation_path)

    engineering_report = {
        "schema_version": "1.0",
        "geometry_revision": params["geometry_revision"],
        "latch_screening_calculation": latch_calculation(params),
        "moving_mass": geometry_validation["metrics"],
        "interpretation": [
            "The latch calculation is only a screening bound; printed PETG orientation, creep and fatigue require the supplied 100-cycle coupon.",
            "The 25 g value is a project target, not an approved machine payload.",
            "Screw identity, remaining engagement and full machine keep-outs remain unmeasured.",
        ],
    }
    engineering_path = output_dir / "reports/mass-and-latch-calculation.json"
    write_json(engineering_path, engineering_report)
    artifact_paths.append(engineering_path)

    optimization_report = {
        "schema_version": "1.0",
        "geometry_revision": params["geometry_revision"],
        "baseline": {
            "id": "R6-owned-digital-baseline",
            "moving_mass_g": 31.98899958276287,
            "exact_slicer_metrics": "NOT_RUN_IN_R7_PHASE_YET",
        },
        "protected_regions": [
            "screw seating face, lower round datum and upper compensating slot",
            "two guide profiles, receiver channels and front stops",
            "latch beam/root/hook/catch/hard stop",
            "impact band, hood, cheeks and 57 x 39 mm open drop frame",
            "future measured machine keep-outs and watermark host surface",
        ],
        "variants": variant_reports,
        "provisional_selection": "balanced only if exact slicing passes; physical coupons remain mandatory",
        "pareto_status": "PENDING_EXACT_SLICER_AND_PHYSICAL_CONSTRAINTS",
    }
    optimization_path = output_dir / "reports/optimization-variants.json"
    write_json(optimization_path, optimization_report)
    artifact_paths.append(optimization_path)

    autonomy_ledger = {
        "schema_version": "1.0",
        "policy_source": "autonomy-policy.json; human gates remain authoritative in design-spec.yaml",
        "geometry_revision": params["geometry_revision"],
        "agent_stages": [
            {"stage": "decomposition", "status": "AUTO_APPROVED", "evidence": "R7-DESIGN-DECOMPOSITION.md"},
            {
                "stage": "parametric-source",
                "status": "AUTO_APPROVED" if all(report["status"] == "PASS" for report in brep_reports.values()) else "BLOCKED",
                "evidence": "reports/geometry-validation.json",
            },
            {
                "stage": "mesh-generation",
                "status": "AUTO_APPROVED" if all(report["status"] == "PASS" for report in mesh_reports.values()) else "BLOCKED",
                "evidence": "reports/geometry-validation.json",
            },
            {"stage": "interface-validation", "status": "BLOCKED", "reason": "required physical coupons and full-motion test are NOT_RUN"},
            {"stage": "slicer-preflight", "status": "BLOCKED", "reason": "exact Anycubic run is not part of source generation"},
            {"stage": "print-candidate", "status": "BLOCKED", "reason": "physical and slicer gates remain open"},
        ],
    }
    ledger_path = output_dir / "reports/agent-approval-ledger.json"
    write_json(ledger_path, autonomy_ledger)
    artifact_paths.append(ledger_path)

    source_path = Path(__file__).resolve()
    inputs = {
        "source": {"path": str(source_path.relative_to(ROOT)), "sha256": sha256_file(source_path)},
        "parameters": {"path": str(params_path.relative_to(ROOT)), "sha256": sha256_file(params_path)},
    }
    artifact_records = []
    for path in sorted(artifact_paths):
        artifact_records.append(
            {
                "path": str(path.relative_to(output_dir)),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    build_report = {
        "schema_version": "1.0",
        "project_id": params["project_id"],
        "spec_revision": params["spec_revision"],
        "geometry_revision": params["geometry_revision"],
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": geometry_validation["status"],
        "environment": {
            "python": platform.python_version(),
            "cadquery": getattr(cq, "__version__", "unknown"),
            "trimesh": getattr(trimesh, "__version__", "unknown"),
            "platform": platform.platform(),
        },
        "inputs": inputs,
        "artifacts": artifact_records,
        "third_party_geometry_loaded": False,
        "printer_upload_or_start": False,
    }
    build_report_path = output_dir / "reports/source-build-report.json"
    write_json(build_report_path, build_report)

    return {
        "status": geometry_validation["status"],
        "output_dir": str(output_dir),
        "moving_mass_g": moving_mass,
        "artifacts": len(artifact_records) + 1,
        "physical_gates": params["physical_gates"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--params", type=Path, default=DEFAULT_PARAMS)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.output_dir.resolve(), args.params.resolve())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        raise
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
