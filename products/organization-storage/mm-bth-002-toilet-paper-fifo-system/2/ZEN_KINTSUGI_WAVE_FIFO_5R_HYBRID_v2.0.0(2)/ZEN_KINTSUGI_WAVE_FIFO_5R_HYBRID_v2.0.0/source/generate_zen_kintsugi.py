#!/usr/bin/env python3
"""Generate the parametric ZEN KINTSUGI WAVE toilet-roll FIFO tower.

The script writes manufacturing STLs, a colored 3MF assembly, validation data,
and a preview image. Units are millimetres. Geometry is constructed with
Shapely profiles, Trimesh, and the Manifold boolean backend.

Change the DEFAULTS block or pass CLI options to adapt roll size/count.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import struct
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence
from xml.etree import ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union


# ----------------------------- DEFAULTS -----------------------------------

DEFAULT_ROLL_DIAMETER = 120.0
DEFAULT_ROLL_WIDTH = 105.0
DEFAULT_ROLL_COUNT = 5
DEFAULT_RADIAL_CLEARANCE = 4.0

NOZZLE = 0.60
LINE_WIDTH = 0.68
LAYER_HEIGHT = 0.30

STONE_DENSITY_G_CM3 = 1.27  # PETG nominal, for CAD-only mass estimates
GOLD_DENSITY_G_CM3 = 1.24   # PLA nominal
WOOD_DENSITY_G_CM3 = 1.20   # wood-filled PLA nominal


@dataclass(frozen=True)
class Params:
    roll_diameter: float = DEFAULT_ROLL_DIAMETER
    roll_width: float = DEFAULT_ROLL_WIDTH
    roll_count: int = DEFAULT_ROLL_COUNT
    radial_clearance: float = DEFAULT_RADIAL_CLEARANCE
    module_pitch: float = 124.0
    crown_height: float = 44.0
    side_thickness: float = 6.0
    back_thickness: float = 3.4
    front_thickness: float = 5.5
    connector_hole_diameter: float = 5.2
    connector_pin_diameter: float = 4.8
    connector_depth: float = 7.2
    groove_depth: float = 0.85
    groove_width: float = 3.0
    inlay_width: float = 2.2
    inlay_thickness: float = 0.65
    tray_assembly_z_offset: float = 2.2
    output_rail_height: float = 12.0

    @property
    def inner_half_width(self) -> float:
        return self.roll_diameter / 2.0 + self.radial_clearance

    @property
    def outer_half_width(self) -> float:
        return self.inner_half_width + self.side_thickness

    @property
    def test_roll_width(self) -> float:
        return self.roll_width + 2.0

    @property
    def rear_clearance(self) -> float:
        return 3.1

    @property
    def front_clearance(self) -> float:
        return 2.0

    @property
    def roll_center_y(self) -> float:
        return self.back_thickness + self.rear_clearance + self.test_roll_width / 2.0

    @property
    def front_y(self) -> float:
        return (
            self.back_thickness
            + self.rear_clearance
            + self.test_roll_width
            + self.front_clearance
        )

    @property
    def total_depth(self) -> float:
        return self.front_y + self.front_thickness

    @property
    def tower_height(self) -> float:
        return self.roll_count * self.module_pitch + self.crown_height


def clean(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    mesh = mesh.copy()
    mesh.remove_unreferenced_vertices()
    mesh.merge_vertices()
    trimesh.repair.fix_normals(mesh, multibody=True)
    return mesh


def union_meshes(meshes: Iterable[trimesh.Trimesh]) -> trimesh.Trimesh:
    items = [m for m in meshes if m is not None and len(m.faces)]
    if not items:
        raise ValueError("No meshes to union")
    if len(items) == 1:
        return clean(items[0])
    return clean(trimesh.boolean.union(items, engine="manifold", check_volume=False))


def difference_mesh(base: trimesh.Trimesh, cutters: Iterable[trimesh.Trimesh]) -> trimesh.Trimesh:
    items = [base] + [c for c in cutters if c is not None and len(c.faces)]
    if len(items) == 1:
        return clean(base)
    return clean(trimesh.boolean.difference(items, engine="manifold", check_volume=False))


def rounded_rect(x0: float, y0: float, x1: float, y1: float, radius: float) -> Polygon:
    return box(x0 + radius, y0 + radius, x1 - radius, y1 - radius).buffer(radius, resolution=12)


def _extrude_parts(geom, height: float) -> list[trimesh.Trimesh]:
    if geom.is_empty:
        return []
    geoms = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    out = []
    for polygon in geoms:
        if polygon.area < 1e-5:
            continue
        out.append(trimesh.creation.extrude_polygon(polygon, height=height, engine="earcut"))
    return out


def extrude_xy(geom, height: float, z0: float = 0.0, merge: bool = True) -> trimesh.Trimesh:
    meshes = _extrude_parts(geom, height)
    for mesh in meshes:
        mesh.apply_translation([0.0, 0.0, z0])
    return union_meshes(meshes) if merge else clean(trimesh.util.concatenate(meshes))


def extrude_yz(geom, thickness: float, x0: float) -> trimesh.Trimesh:
    """Extrude a profile whose 2-D axes are (y,z) in +x."""
    meshes = _extrude_parts(geom, thickness)
    transformed = []
    for mesh in meshes:
        old = mesh.vertices.copy()
        mesh.vertices = np.column_stack([x0 + old[:, 2], old[:, 0], old[:, 1]])
        transformed.append(mesh)
    return union_meshes(transformed)


def extrude_xz(geom, thickness: float, y0: float, merge: bool = True) -> trimesh.Trimesh:
    """Extrude a profile whose 2-D axes are (x,z) in +y."""
    meshes = _extrude_parts(geom, thickness)
    transformed = []
    for mesh in meshes:
        old = mesh.vertices.copy()
        mesh.vertices = np.column_stack([old[:, 0], y0 + old[:, 2], old[:, 1]])
        transformed.append(mesh)
    return union_meshes(transformed) if merge else clean(trimesh.util.concatenate(transformed))


def cylinder_between_axis(radius: float, height: float, axis: str, sections: int = 48) -> trimesh.Trimesh:
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    if axis == "z":
        return mesh
    if axis == "y":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
        return mesh
    if axis == "x":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
        return mesh
    raise ValueError(axis)


def side_profile(p: Params, h: float, style: str, phase: float) -> Polygon:
    outer = box(0.0, 0.0, p.total_depth, h)
    if style == "solid":
        return outer
    # Open the window through the top: a solid top strip would become a
    # >100 mm bridge when a module is printed upright.
    window = unary_union(
        [
            rounded_rect(10.0, 7.0, p.front_y - 3.5, h + 8.0, 7.0),
            box(10.0, h - 9.0, p.front_y - 3.5, h + 1.0),
        ]
    )
    frame = outer.difference(window)
    if h >= 80.0:
        # Pointed waves keep every long lower edge steeper than ~45 degrees.
        wave1 = LineString(
            [(8.0, 14.0), (34.0, h * 0.46), (61.0, 15.0), (88.0, h * 0.48), (p.front_y - 2.0, 20.0)]
        ).buffer(3.2, cap_style=1, join_style=1)
        wave2 = LineString(
            [(8.0, h - 14.0), (34.0, h * 0.55), (61.0, h - 15.0), (88.0, h * 0.52), (p.front_y - 2.0, h - 24.0)]
        ).buffer(3.2, cap_style=1, join_style=1)
        ribs = [wave1, wave2]
    else:
        # The short crown cannot span the whole depth at 45 degrees; use
        # vertical reed-like ribs instead.
        ribs = [
            LineString([(40.0, 0.0), (40.0, h)]).buffer(3.2, cap_style=1),
            LineString([(79.0, 0.0), (79.0, h)]).buffer(3.2, cap_style=1),
        ]
    return unary_union([frame, *ribs]).intersection(outer)


def back_profile(p: Params, h: float, style: str, phase: float) -> Polygon:
    outer = box(-p.outer_half_width, 0.0, p.outer_half_width, h)
    if style == "solid":
        profile = outer
    else:
        window = unary_union(
            [
                rounded_rect(
                    -p.inner_half_width + 6.0,
                    7.0,
                    p.inner_half_width - 6.0,
                    h + 8.0,
                    7.0,
                ),
                box(-p.inner_half_width + 6.0, h - 9.0, p.inner_half_width - 6.0, h + 1.0),
            ]
        )
        frame = outer.difference(window)
        pads = [Point(-38.0, h * 0.55).buffer(9.0), Point(38.0, h * 0.55).buffer(9.0)]
        verticals = [
            LineString([(-38.0, 0.0), (-38.0, h)]).buffer(3.0, cap_style=1),
            LineString([(38.0, 0.0), (38.0, h)]).buffer(3.0, cap_style=1),
        ]
        if h >= 80.0:
            xmin = -p.inner_half_width + 6.0
            xmax = p.inner_half_width - 6.0
            brace1 = LineString(
                [(xmin, 12.0), (-25.0, h * 0.49), (8.0, 15.0), (41.0, h * 0.49), (xmax, 35.0)]
            ).buffer(3.0, cap_style=1, join_style=1)
            brace2 = LineString(
                [(xmin, h - 12.0), (-25.0, h * 0.52), (8.0, h - 15.0), (41.0, h * 0.52), (xmax, h - 35.0)]
            ).buffer(3.0, cap_style=1, join_style=1)
            braces = [brace1, brace2]
        else:
            braces = [LineString([(0.0, 0.0), (0.0, h)]).buffer(3.0, cap_style=1)]
        profile = unary_union([frame, *braces, *verticals, *pads]).intersection(outer)
    return profile


def rail_polygon(p: Params, h: float, side: int, phase: float, z0: float, z1: float) -> Polygon:
    zs = np.linspace(z0, z1, max(8, int((z1 - z0) / 3.0)))
    inner = side * (p.inner_half_width - 9.0 + 1.6 * np.sin(2 * np.pi * zs / p.module_pitch + phase))
    outer_x = side * p.outer_half_width
    if side < 0:
        pts = [(outer_x, z0), (outer_x, z1)] + list(zip(inner[::-1], zs[::-1]))
    else:
        pts = [(outer_x, z0)] + list(zip(inner, zs)) + [(outer_x, z1)]
    return Polygon(pts).buffer(0)


def front_profile(p: Params, h: float, kind: str, phase: float) -> Polygon:
    if kind == "output":
        upper_start = min(h - 16.0, p.roll_diameter * 0.82)
        left_upper = rail_polygon(p, h, -1, phase, upper_start, h).intersection(
            Polygon(
                [
                    (-p.outer_half_width, upper_start),
                    (-p.inner_half_width, upper_start),
                    (-p.inner_half_width + 9.0, upper_start + 10.0),
                    (-p.inner_half_width + 9.0, h),
                    (-p.outer_half_width, h),
                ]
            )
        )
        right_upper = rail_polygon(p, h, 1, phase + 0.4, upper_start, h).intersection(
            Polygon(
                [
                    (p.outer_half_width, upper_start),
                    (p.inner_half_width, upper_start),
                    (p.inner_half_width - 9.0, upper_start + 10.0),
                    (p.inner_half_width - 9.0, h),
                    (p.outer_half_width, h),
                ]
            )
        )
        left = unary_union(
            [
                left_upper,
                box(-p.outer_half_width, 0.0, -p.inner_half_width + 6.0, 18.0),
            ]
        )
        right = unary_union(
            [
                right_upper,
                box(p.inner_half_width - 6.0, 0.0, p.outer_half_width, 18.0),
            ]
        )
        return unary_union([left, right])
    left = rail_polygon(p, h, -1, phase, 0.0, h)
    right = rail_polygon(p, h, 1, phase + 0.4, 0.0, h)
    return unary_union([left, right])


def crack_lines(p: Params, h: float, pattern: str, kind: str) -> list[LineString]:
    if pattern == "A":
        left = [(-63, 4), (-66, h * 0.19), (-60, h * 0.39), (-68, h * 0.61), (-61, h * 0.82), (-65, h - 4)]
        right = [(64, 4), (60, h * 0.25), (67, h * 0.48), (61, h * 0.70), (66, h - 4)]
        branches = [LineString([(-60, h * 0.39), (-56, h * 0.49)]), LineString([(67, h * 0.48), (70, h * 0.58)])]
    else:
        left = [(-65, 4), (-60, h * 0.22), (-67, h * 0.43), (-61, h * 0.65), (-66, h * 0.86), (-63, h - 4)]
        right = [(62, 4), (67, h * 0.18), (61, h * 0.40), (68, h * 0.64), (62, h * 0.83), (65, h - 4)]
        branches = [LineString([(-67, h * 0.43), (-70, h * 0.52)]), LineString([(61, h * 0.40), (56, h * 0.50)])]
    lines = [LineString(left), LineString(right), *branches]
    if kind == "output":
        min_z = min(h - 16.0, p.roll_diameter * 0.82)
        clip = box(-p.outer_half_width, min_z, p.outer_half_width, h)
        lines = [line.intersection(clip) for line in lines]
    return [line for line in lines if not line.is_empty]


def crack_polygon(p: Params, h: float, pattern: str, kind: str, width: float):
    rail = front_profile(p, h, kind, 0.15 if pattern == "A" else 1.05)
    ribbons = [line.buffer(width / 2.0, cap_style=1, join_style=1) for line in crack_lines(p, h, pattern, kind)]
    return unary_union(ribbons).intersection(rail).buffer(0)


def connector_cutters(p: Params, h: float, top: bool, bottom: bool) -> list[trimesh.Trimesh]:
    out = []
    positions = [
        (-p.outer_half_width + p.side_thickness / 2.0, 8.0),
        (p.outer_half_width - p.side_thickness / 2.0, 8.0),
        (-p.outer_half_width + p.side_thickness / 2.0, p.front_y - 3.5),
        (p.outer_half_width - p.side_thickness / 2.0, p.front_y - 3.5),
    ]
    for x, y in positions:
        if bottom:
            c = cylinder_between_axis(p.connector_hole_diameter / 2.0, p.connector_depth + 0.2, "z")
            c.apply_translation([x, y, (p.connector_depth + 0.2) / 2.0 - 0.1])
            out.append(c)
        if top:
            c = cylinder_between_axis(p.connector_hole_diameter / 2.0, p.connector_depth + 0.2, "z")
            c.apply_translation([x, y, h - (p.connector_depth + 0.2) / 2.0 + 0.1])
            out.append(c)
    return out


def wall_mount_cutters(p: Params, h: float) -> list[trimesh.Trimesh]:
    cutters = []
    for x in (-38.0, 38.0):
        through = cylinder_between_axis(2.3, p.back_thickness + 1.0, "y", sections=40)
        through.apply_translation([x, p.back_thickness / 2.0, h * 0.55])
        counter = cylinder_between_axis(4.9, 2.3, "y", sections=48)
        counter.apply_translation([x, p.back_thickness - 0.9, h * 0.55])
        cutters.extend([through, counter])
    return cutters


def crown_dovetail(p: Params) -> tuple[Polygon, trimesh.Trimesh]:
    ymid = p.roll_center_y
    male = Polygon(
        [
            (p.outer_half_width - 0.2, ymid - 5.0),
            (p.outer_half_width - 0.2, ymid + 5.0),
            (p.outer_half_width + 5.0, ymid + 8.0),
            (p.outer_half_width + 5.0, ymid - 8.0),
        ]
    )
    return male, extrude_xy(male, 30.0, z0=8.0)


def make_body(
    p: Params,
    kind: str,
    pattern: str = "A",
    style: str = "wave",
) -> tuple[trimesh.Trimesh, trimesh.Trimesh, object]:
    h = p.crown_height if kind == "crown" else p.module_pitch
    phase = 0.15 if pattern == "A" else 1.05
    parts = [
        extrude_yz(side_profile(p, h, style, phase), p.side_thickness, -p.outer_half_width),
        extrude_yz(side_profile(p, h, style, phase + math.pi), p.side_thickness, p.inner_half_width),
        extrude_xz(back_profile(p, h, style, phase), p.back_thickness, 0.0),
        extrude_xz(front_profile(p, h, kind, phase), p.front_thickness, p.front_y),
    ]

    if kind == "output":
        rail_length = p.front_y - p.back_thickness + 1.0
        for x in (-34.0, 34.0):
            rail = trimesh.creation.box(extents=[11.0, rail_length, p.output_rail_height])
            rail.apply_translation(
                [x, p.back_thickness + rail_length / 2.0 - 0.5, p.output_rail_height / 2.0]
            )
            parts.append(rail)
    if kind == "crown":
        _, male_mesh = crown_dovetail(p)
        tray_pad = trimesh.creation.box(extents=[p.side_thickness, 22.0, 40.0])
        tray_pad.apply_translation(
            [p.inner_half_width + p.side_thickness / 2.0, p.roll_center_y, 20.0]
        )
        parts.extend([tray_pad, male_mesh])

    body = union_meshes(parts)
    top = kind != "crown"
    bottom = kind != "output"
    cutters = connector_cutters(p, h, top=top, bottom=bottom)
    if kind != "crown":
        cutters.extend(wall_mount_cutters(p, h))

    groove_geom = crack_polygon(p, h, pattern, kind, p.groove_width)
    groove_mesh = extrude_xz(
        groove_geom,
        p.groove_depth + 0.1,
        p.total_depth - p.groove_depth,
        merge=False,
    )
    cutters.append(groove_mesh)
    body = difference_mesh(body, cutters)

    insert_geom = crack_polygon(p, h, pattern, kind, p.inlay_width)
    insert_functional = extrude_xz(
        insert_geom,
        p.inlay_thickness,
        p.total_depth - p.inlay_thickness + 0.03,
        merge=False,
    )
    return body, insert_functional, insert_geom


def make_connector_pin(p: Params) -> trimesh.Trimesh:
    r = p.connector_pin_diameter / 2.0
    total = 2 * p.connector_depth - 1.0
    profile = np.array(
        [
            [0.0, 0.0],
            [r - 0.3, 0.0],
            [r, 1.0],
            [r, total - 1.0],
            [r - 0.3, total],
            [0.0, total],
        ]
    )
    return clean(trimesh.creation.revolve(profile, sections=48))


def make_scent_tray(p: Params) -> trimesh.Trimesh:
    center = np.array([p.outer_half_width + 30.0, p.roll_center_y, 0.0])
    outer = trimesh.creation.cylinder(radius=26.0, height=9.0, sections=96)
    outer.apply_translation([center[0], center[1], 4.5])
    inner = trimesh.creation.cylinder(radius=21.5, height=7.0, sections=96)
    inner.apply_translation([center[0], center[1], 7.0])
    bowl = difference_mesh(outer, [inner])

    bracket = trimesh.creation.box(extents=[12.0, 30.0, 40.0])
    bracket.apply_translation([p.outer_half_width + 6.0, p.roll_center_y, 20.0])
    combined = union_meshes([bowl, bracket])
    male, _ = crown_dovetail(p)
    female = male.buffer(0.38, join_style=2)
    slot = extrude_xy(female, 36.0, z0=-0.1)
    return difference_mesh(combined, [slot])


def make_fit_coupon(p: Params) -> tuple[trimesh.Trimesh, trimesh.Trimesh]:
    block = trimesh.creation.box(extents=[64.0, 28.0, 5.0])
    block.apply_translation([32.0, 14.0, 2.5])
    cutters = []
    for y, width in [(8.0, 2.8), (14.0, 3.0)]:
        groove = trimesh.creation.box(extents=[42.0, width, p.groove_depth + 0.1])
        groove.apply_translation([25.0, y, 5.0 - (p.groove_depth + 0.1) / 2.0])
        cutters.append(groove)
    for x, diameter in [(53.0, 5.1), (59.0, 5.3)]:
        hole = cylinder_between_axis(diameter / 2.0, 5.4, "z")
        hole.apply_translation([x, 21.0, 2.5])
        cutters.append(hole)
    body = difference_mesh(block, cutters)
    strips = []
    for y, width in [(8.0, 2.2), (14.0, 2.4)]:
        strip = trimesh.creation.box(extents=[42.0, width, p.inlay_thickness])
        strip.apply_translation([25.0, y, p.inlay_thickness / 2.0])
        strips.append(strip)
    return body, clean(trimesh.util.concatenate(strips))


def make_test_roll(p: Params, diameter: float | None = None, width: float | None = None) -> trimesh.Trimesh:
    d = diameter or (p.roll_diameter + 2.0)
    w = width or (p.roll_width + 2.0)
    roll = cylinder_between_axis(d / 2.0, w, "y", sections=96)
    roll.apply_translation([0.0, p.roll_center_y, 0.0])
    return roll


def transform_copy(mesh: trimesh.Trimesh, translation: Sequence[float]) -> trimesh.Trimesh:
    m = mesh.copy()
    m.apply_translation(translation)
    return m


def export_stl(mesh: trimesh.Trimesh, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path, file_type="stl")


def mesh_metrics(mesh: trimesh.Trimesh) -> dict:
    components = mesh.split(only_watertight=False)
    return {
        "triangles": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "watertight": bool(mesh.is_watertight),
        "is_volume": bool(mesh.is_volume),
        "components": int(len(components)),
        "volume_mm3": float(abs(mesh.volume)),
        "bounds_mm": np.round(mesh.bounds, 3).tolist(),
    }


def collision_check(
    p: Params,
    output: trimesh.Trimesh,
    middle_a: trimesh.Trimesh,
    middle_b: trimesh.Trimesh,
    crown: trimesh.Trimesh,
) -> dict:
    modules = [(0.0, output)]
    for i in range(1, p.roll_count):
        modules.append((i * p.module_pitch, middle_a if i % 2 else middle_b))
    modules.append((p.roll_count * p.module_pitch, crown))
    # Begin above the intentional output-rail stop; the rails must collide at
    # the resting position, while the free shaft above must remain clear.
    samples = np.linspace(
        (p.roll_diameter + 2.0) / 2.0 + 6.0,
        p.roll_count * p.module_pitch - p.roll_diameter / 2.0,
        98,
    )
    test_roll = make_test_roll(p)
    collisions = []
    max_volume = 0.0
    for zc in samples:
        roll = transform_copy(test_roll, [0.0, 0.0, zc])
        for z0, module in modules:
            if zc + (p.roll_diameter + 2.0) / 2.0 < z0 - 0.1:
                continue
            local_h = p.crown_height if module is crown else p.module_pitch
            if zc - (p.roll_diameter + 2.0) / 2.0 > z0 + local_h + 0.1:
                continue
            moved = transform_copy(module, [0.0, 0.0, z0])
            inter = trimesh.boolean.intersection([moved, roll], engine="manifold", check_volume=False)
            vol = 0.0 if inter is None or len(inter.faces) == 0 else abs(float(inter.volume))
            max_volume = max(max_volume, vol)
            if vol > 0.05:
                collisions.append({"roll_center_z": float(zc), "module_z": float(z0), "volume_mm3": vol})
    test_radius = (p.roll_diameter + 2.0) / 2.0
    rail_inner_x = 34.0 - 11.0 / 2.0
    theoretical_stop_center = p.output_rail_height + math.sqrt(test_radius**2 - rail_inner_x**2)
    stop_roll = transform_copy(test_roll, [0.0, 0.0, theoretical_stop_center - 0.5])
    stop_intersection = trimesh.boolean.intersection(
        [output, stop_roll], engine="manifold", check_volume=False
    )
    stop_volume = (
        0.0
        if stop_intersection is None or len(stop_intersection.faces) == 0
        else abs(float(stop_intersection.volume))
    )
    return {
        "test_roll_mm": [p.roll_diameter + 2.0, p.roll_width + 2.0],
        "positions_tested": int(len(samples)),
        "collision_count": len(collisions),
        "max_intersection_volume_mm3": max_volume,
        "theoretical_output_stop_center_z_mm": theoretical_stop_center,
        "output_stop_intersection_at_0p5mm_overtravel_mm3": stop_volume,
        "collisions": collisions[:20],
    }


def add_3mf_object(resources, object_id: int, mesh: trimesh.Trimesh, material_index: int, name: str):
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    obj = ET.SubElement(
        resources,
        f"{{{ns}}}object",
        {"id": str(object_id), "type": "model", "pid": "1", "pindex": str(material_index), "name": name},
    )
    mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
    verts = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
    for v in mesh.vertices:
        ET.SubElement(verts, f"{{{ns}}}vertex", {"x": f"{v[0]:.6f}", "y": f"{v[1]:.6f}", "z": f"{v[2]:.6f}"})
    tris = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
    for f in mesh.faces:
        ET.SubElement(tris, f"{{{ns}}}triangle", {"v1": str(int(f[0])), "v2": str(int(f[1])), "v3": str(int(f[2]))})


def write_3mf(
    path: Path,
    objects: list[tuple[str, trimesh.Trimesh, int]],
    build_items: list[tuple[int, Sequence[float]]],
) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "de-DE"})
    meta = ET.SubElement(model, f"{{{ns}}}metadata", {"name": "Title"})
    meta.text = "ZEN KINTSUGI WAVE – 5-Rollen FIFO-Säule"
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    mats = ET.SubElement(resources, f"{{{ns}}}basematerials", {"id": "1"})
    for name, color in [
        ("Stein-PETG", "#A9A79FFF"),
        ("Gold-Silk", "#C9A227FF"),
        ("Holz-Duftschale", "#8B5A2BFF"),
        ("Verbinder", "#666666FF"),
    ]:
        ET.SubElement(mats, f"{{{ns}}}base", {"name": name, "displaycolor": color})
    for idx, (name, mesh, mat) in enumerate(objects, start=2):
        add_3mf_object(resources, idx, mesh, mat, name)
    build = ET.SubElement(model, f"{{{ns}}}build")
    for object_index, t in build_items:
        attrs = {"objectid": str(object_index + 2)}
        if any(abs(float(v)) > 1e-9 for v in t):
            attrs["transform"] = f"1 0 0 0 1 0 0 0 1 {t[0]:.6f} {t[1]:.6f} {t[2]:.6f}"
        ET.SubElement(build, f"{{{ns}}}item", attrs)

    model_bytes = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    content_types = b'''<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'''
    rels = b'''<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("3D/3dmodel.model", model_bytes)


def render_preview(
    path: Path,
    meshes: list[tuple[trimesh.Trimesh, str]],
    p: Params,
) -> None:
    # Near-frontal product view: the roll faces and FIFO opening stay legible,
    # while a small angle still reveals the sculpted side lattice and tray.
    az = math.radians(10.0)
    el = math.radians(78.0)
    rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(el), -math.sin(el)], [0, math.sin(el), math.cos(el)]])
    rot = rx @ rz
    all_polys = []
    all_depths = []
    all_colors = []
    light = np.array([-0.35, -0.55, 0.76])
    light /= np.linalg.norm(light)
    color_map = {
        "stone": np.array([0.63, 0.62, 0.58]),
        "gold": np.array([0.82, 0.59, 0.10]),
        "wood": np.array([0.48, 0.26, 0.11]),
        "roll": np.array([0.96, 0.94, 0.86]),
        "pin": np.array([0.34, 0.34, 0.34]),
    }
    for mesh, material in meshes:
        verts = mesh.vertices @ rot.T
        faces = mesh.faces
        normals = mesh.face_normals @ rot.T
        projected = verts[:, :2].copy()
        projected[:, 1] *= -1.0
        polys = projected[faces]
        depths = verts[faces][:, :, 2].mean(axis=1)
        shade = np.clip(0.35 + 0.65 * np.maximum(0.0, normals @ light), 0.25, 1.0)
        base = color_map[material]
        colors = np.clip(base[None, :] * shade[:, None] + 0.06, 0, 1)
        all_polys.extend(polys)
        all_depths.extend(depths)
        all_colors.extend(colors)
    order = np.argsort(all_depths)
    polys = [all_polys[i] for i in order]
    colors = [all_colors[i] for i in order]
    fig, ax = plt.subplots(figsize=(6.5, 13), dpi=180)
    fig.patch.set_facecolor("#eeeae2")
    ax.set_facecolor("#eeeae2")
    fig.subplots_adjust(left=0.035, right=0.965, bottom=0.025, top=0.88)
    collection = PolyCollection(polys, facecolors=colors, edgecolors="none", linewidths=0)
    ax.add_collection(collection)
    points = np.concatenate(polys, axis=0)
    xmin, ymin = points.min(axis=0)
    xmax, ymax = points.max(axis=0)
    margin_x = (xmax - xmin) * 0.08
    margin_y = (ymax - ymin) * 0.05
    ax.set_xlim(xmin - margin_x, xmax + margin_x)
    ax.set_ylim(ymin - margin_y, ymax + margin_y)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(
        0.045,
        0.968,
        "ZEN KINTSUGI WAVE",
        ha="left",
        va="top",
        fontsize=17,
        weight="bold",
        color="#312d28",
    )
    fig.text(
        0.045,
        0.935,
        f"parametrische FIFO-Säule · {p.roll_count} Rollen",
        ha="left",
        va="top",
        fontsize=9,
        color="#5c554c",
    )
    fig.savefig(path)
    plt.close(fig)


def write_csv(path: Path, rows: list[dict]) -> None:
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def build(p: Params, out_root: Path) -> None:
    release = out_root / "release"
    stl_dir = release / "STL"
    baseline_dir = release / "baseline_reference"
    for d in (release, stl_dir, baseline_dir):
        d.mkdir(parents=True, exist_ok=True)

    output, gold_output_fn, gold_output_geom = make_body(p, "output", "A", "wave")
    middle_a, gold_a_fn, gold_a_geom = make_body(p, "middle", "A", "wave")
    middle_b, gold_b_fn, gold_b_geom = make_body(p, "middle", "B", "wave")
    crown, gold_crown_fn, gold_crown_geom = make_body(p, "crown", "B", "wave")
    tray = make_scent_tray(p)
    pin = make_connector_pin(p)
    coupon, coupon_inlays = make_fit_coupon(p)

    flat_gold = {
        "gold_inlay_output_flat.stl": extrude_xy(gold_output_geom, p.inlay_thickness, merge=False),
        "gold_inlay_middle_A_flat.stl": extrude_xy(gold_a_geom, p.inlay_thickness, merge=False),
        "gold_inlay_middle_B_flat.stl": extrude_xy(gold_b_geom, p.inlay_thickness, merge=False),
        "gold_inlay_crown_flat.stl": extrude_xy(gold_crown_geom, p.inlay_thickness, merge=False),
    }

    manufacturing = {
        "body_output.stl": output,
        "body_middle_A.stl": middle_a,
        "body_middle_B.stl": middle_b,
        "body_crown_with_tray_rail.stl": crown,
        **flat_gold,
        "scent_stone_tray.stl": tray,
        "connector_pin_4p8mm.stl": pin,
        "fit_coupon_body.stl": coupon,
        "fit_coupon_gold_strips.stl": coupon_inlays,
    }
    for name, mesh in manufacturing.items():
        export_stl(mesh, stl_dir / name)

    baseline_output, _, _ = make_body(p, "output", "A", "solid")
    baseline_middle, _, _ = make_body(p, "middle", "A", "solid")
    baseline_crown, _, _ = make_body(p, "crown", "B", "solid")
    export_stl(baseline_output, baseline_dir / "baseline_solid_output.stl")
    export_stl(baseline_middle, baseline_dir / "baseline_solid_middle.stl")
    export_stl(baseline_crown, baseline_dir / "baseline_solid_crown.stl")

    objects = [
        ("Ausgabe", output, 0),
        ("Mittel_A", middle_a, 0),
        ("Mittel_B", middle_b, 0),
        ("Krone", crown, 0),
        ("Gold_Ausgabe", gold_output_fn, 1),
        ("Gold_Mittel_A", gold_a_fn, 1),
        ("Gold_Mittel_B", gold_b_fn, 1),
        ("Gold_Krone", gold_crown_fn, 1),
        ("Duftstein_Schale", tray, 2),
        ("Verbinder", pin, 3),
    ]
    build_items: list[tuple[int, Sequence[float]]] = [(0, (0, 0, 0)), (4, (0, 0, 0))]
    for i in range(1, p.roll_count):
        if i % 2:
            build_items.extend([(1, (0, 0, i * p.module_pitch)), (5, (0, 0, i * p.module_pitch))])
        else:
            build_items.extend([(2, (0, 0, i * p.module_pitch)), (6, (0, 0, i * p.module_pitch))])
    crown_z = p.roll_count * p.module_pitch
    build_items.extend(
        [
            (3, (0, 0, crown_z)),
            (7, (0, 0, crown_z)),
            (8, (0, 0, crown_z + p.tray_assembly_z_offset)),
        ]
    )
    connector_positions = [
        (-p.outer_half_width + p.side_thickness / 2.0, 8.0),
        (p.outer_half_width - p.side_thickness / 2.0, 8.0),
        (-p.outer_half_width + p.side_thickness / 2.0, p.front_y - 3.5),
        (p.outer_half_width - p.side_thickness / 2.0, p.front_y - 3.5),
    ]
    pin_h = 2 * p.connector_depth - 1.0
    for interface in range(1, p.roll_count + 1):
        z = interface * p.module_pitch - pin_h / 2.0
        for x, y in connector_positions:
            build_items.append((9, (x, y, z)))
    write_3mf(release / "ZEN_KINTSUGI_WAVE_5R_assembly.3mf", objects, build_items)

    fifo = collision_check(p, output, middle_a, middle_b, crown)
    validation = {"parameters": asdict(p), "fifo": fifo, "files": {}}
    for name in manufacturing:
        reloaded = trimesh.load_mesh(stl_dir / name, process=True)
        validation["files"][name] = mesh_metrics(reloaded)
    validation["baseline_files"] = {}
    for path in sorted(baseline_dir.glob("*.stl")):
        validation["baseline_files"][path.name] = mesh_metrics(trimesh.load_mesh(path, process=True))
    with (release / "validation_report.json").open("w", encoding="utf-8") as f:
        json.dump(validation, f, ensure_ascii=False, indent=2)

    baseline_body_volume = (
        abs(baseline_output.volume)
        + (p.roll_count - 1) * abs(baseline_middle.volume)
        + abs(baseline_crown.volume)
    )
    selected_body_volume = (
        abs(output.volume)
        + math.ceil((p.roll_count - 1) / 2) * abs(middle_a.volume)
        + math.floor((p.roll_count - 1) / 2) * abs(middle_b.volume)
        + abs(crown.volume)
    )
    rows = [
        {
            "candidate": "Baseline_solid_0p4",
            "geometry": "solid side/back panels",
            "nozzle_mm": 0.4,
            "layer_mm": 0.2,
            "body_volume_cm3": round(baseline_body_volume / 1000.0, 1),
            "solid_equivalent_mass_g": round(baseline_body_volume / 1000.0 * STONE_DENSITY_G_CM3, 1),
            "exact_slicer_time": "not measured",
            "status": "reference",
        },
        {
            "candidate": "A_process_only_0p6",
            "geometry": "solid side/back panels",
            "nozzle_mm": NOZZLE,
            "layer_mm": LAYER_HEIGHT,
            "body_volume_cm3": round(baseline_body_volume / 1000.0, 1),
            "solid_equivalent_mass_g": round(baseline_body_volume / 1000.0 * STONE_DENSITY_G_CM3, 1),
            "exact_slicer_time": "not measured",
            "status": "not selected: retains bulk",
        },
        {
            "candidate": "B_geometry_only_0p4",
            "geometry": "large wave windows + continuous ribs",
            "nozzle_mm": 0.4,
            "layer_mm": 0.2,
            "body_volume_cm3": round(selected_body_volume / 1000.0, 1),
            "solid_equivalent_mass_g": round(selected_body_volume / 1000.0 * STONE_DENSITY_G_CM3, 1),
            "exact_slicer_time": "not measured",
            "status": "feasible, slower detail profile",
        },
        {
            "candidate": "C_selected_0p6",
            "geometry": "large wave windows + continuous ribs",
            "nozzle_mm": NOZZLE,
            "layer_mm": LAYER_HEIGHT,
            "body_volume_cm3": round(selected_body_volume / 1000.0, 1),
            "solid_equivalent_mass_g": round(selected_body_volume / 1000.0 * STONE_DENSITY_G_CM3, 1),
            "exact_slicer_time": "not measured",
            "status": "selected; verify in user's slicer",
        },
    ]
    write_csv(release / "candidate_comparison.csv", rows)

    spacing = LINE_WIDTH - LAYER_HEIGHT * (1.0 - math.pi / 4.0)
    path_plan = {
        "process_starting_point": {
            "nozzle_mm": NOZZLE,
            "line_width_mm": LINE_WIDTH,
            "layer_height_mm": LAYER_HEIGHT,
            "speed_reference_mm_s": 45.0,
            "requested_flow_at_reference_mm3_s": LINE_WIDTH * LAYER_HEIGHT * 45.0,
        },
        "constant_width_estimate": {
            "path_spacing_mm": spacing,
            "three_path_section_mm": LINE_WIDTH + 2.0 * spacing,
            "four_path_section_mm": LINE_WIDTH + 3.0 * spacing,
            "six_mm_rib_remaining_core_with_three_walls_each_side_mm": 6.0
            - 2.0 * (LINE_WIDTH + 2.0 * spacing),
            "three_point_four_mm_back_remaining_core_with_two_walls_each_side_mm": 3.4
            - 2.0 * (LINE_WIDTH + spacing),
        },
        "support_strategy": {
            "orientation": "all body modules upright on z=0",
            "long_lattice_segments_minimum_slope": ">=45 degrees from horizontal",
            "top_spanning_strips": "removed",
            "local_bridges": "mount counterbores and tray dovetail roof only; inspect in slicer",
        },
        "note": "Constant-width planning only. Arachne/variable-width paths and exact time/material must be checked in the target slicer.",
    }
    with (release / "path_assumptions.json").open("w", encoding="utf-8") as f:
        json.dump(path_plan, f, ensure_ascii=False, indent=2)

    preview_meshes: list[tuple[trimesh.Trimesh, str]] = []
    preview_meshes.extend([(output, "stone"), (gold_output_fn, "gold")])
    for i in range(1, p.roll_count):
        body = middle_a if i % 2 else middle_b
        gold = gold_a_fn if i % 2 else gold_b_fn
        preview_meshes.extend(
            [
                (transform_copy(body, [0, 0, i * p.module_pitch]), "stone"),
                (transform_copy(gold, [0, 0, i * p.module_pitch]), "gold"),
            ]
        )
    preview_meshes.extend(
        [
            (transform_copy(crown, [0, 0, crown_z]), "stone"),
            (transform_copy(gold_crown_fn, [0, 0, crown_z]), "gold"),
            (transform_copy(tray, [0, 0, crown_z + p.tray_assembly_z_offset]), "wood"),
        ]
    )
    nominal_roll = make_test_roll(p, p.roll_diameter, p.roll_width)
    rail_inner_x = 34.0 - 11.0 / 2.0
    rest_center = p.output_rail_height + math.sqrt((p.roll_diameter / 2.0) ** 2 - rail_inner_x**2)
    for i in range(p.roll_count):
        preview_meshes.append(
            (transform_copy(nominal_roll, [0, 0, rest_center + i * p.roll_diameter]), "roll")
        )
    render_preview(release / "preview_ZEN_KINTSUGI_WAVE.png", preview_meshes, p)

    source_copy = release / "source"
    source_copy.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), source_copy / Path(__file__).name)
    (source_copy / "requirements.txt").write_text(
        "numpy>=2.0\ntrimesh>=5.0\nmanifold3d>=3.0\nshapely>=2.0\nmapbox_earcut>=2.0\nmatplotlib>=3.8\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--roll-diameter", type=float, default=DEFAULT_ROLL_DIAMETER)
    parser.add_argument("--roll-width", type=float, default=DEFAULT_ROLL_WIDTH)
    parser.add_argument("--roll-count", type=int, default=DEFAULT_ROLL_COUNT)
    parser.add_argument("--clearance", type=float, default=DEFAULT_RADIAL_CLEARANCE)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.roll_count < 1:
        raise SystemExit("roll-count must be >= 1")
    pitch = args.roll_diameter + 4.0
    params = Params(
        roll_diameter=args.roll_diameter,
        roll_width=args.roll_width,
        roll_count=args.roll_count,
        radial_clearance=args.clearance,
        module_pitch=pitch,
    )
    build(params, args.output)
