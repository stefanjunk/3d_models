#!/usr/bin/env python3
"""Generate the DRAFT ZEN KINTSUGI WAVE v2.1 printable release candidate.

Coordinate system (millimetres): +X right in the front view, +Y away from
the wall, +Z upward.  The functional shaft is authoritative; freeform shells,
ornament and colour bodies are derived around protected keep-outs.

The generator intentionally keeps the previous organic GLBs as immutable style
references only.  It rebuilds all production geometry from compact procedural
curves and surfaces so the result remains parameterised, repairable and
dimensionally testable.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence
from xml.etree import ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection
from shapely.geometry import Point, Polygon, box


VERSION = "2.1.0-DRAFT"
PRODUCT = "ZEN_KINTSUGI_WAVE_FIFO_5R"
SOURCE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SOURCE_DIR.parent
WATERMARK_DXF = SOURCE_DIR / "just-innovation-watermark" / "exports" / "dxf" / "just-innovation-compact.dxf"

IVORY = 0
GOLD = 1
BRONZE = 2
SAND = 3
PALETTE = [
    ("Stone Ivory PETG", "#D7D0C1FF"),
    ("Antique Gold PETG", "#B68A3AFF"),
    ("Walnut Bronze PETG", "#5A3827FF"),
    ("Warm Sand PETG", "#B8A489FF"),
]


@dataclass(frozen=True)
class Params:
    roll_diameter: float = 120.0
    roll_width: float = 105.0
    roll_count: int = 5
    radial_clearance: float = 4.0
    axial_clearance: float = 4.0
    module_pitch: float = 124.0
    crown_height: float = 46.0
    shell_inner_half_width: float = 65.0
    shell_nominal: float = 1.80
    shell_macro_relief: float = 2.25
    shell_micro_relief: float = 0.22
    rear_spine_width: float = 20.0
    rear_spine_thickness: float = 5.2
    rear_structure_max_y: float = 8.2
    front_ribbon_y: float = 119.35
    front_ribbon_depth_radius: float = 1.55
    front_ribbon_width_radius: float = 4.60
    connector_pin_diameter: float = 4.80
    connector_hole_diameter: float = 5.20
    connector_depth: float = 5.6
    tray_module_index: int = 2

    @property
    def proxy_diameter(self) -> float:
        return self.roll_diameter + 2.0

    @property
    def proxy_width(self) -> float:
        return self.roll_width + 2.0

    @property
    def roll_center_y(self) -> float:
        return self.rear_structure_max_y + 0.8 + self.proxy_width / 2.0

    @property
    def tower_height(self) -> float:
        return self.roll_count * self.module_pitch + self.crown_height

    @property
    def body_width_max(self) -> float:
        shell_width = 2.0 * (
            self.shell_inner_half_width
            + self.shell_nominal
            + self.shell_macro_relief
            + self.shell_micro_relief
        )
        ribbon_width = 2.0 * (66.2 + self.front_ribbon_width_radius)
        return max(shell_width, ribbon_width)


def clean(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    result = mesh.copy()
    result.remove_unreferenced_vertices()
    result.merge_vertices()
    trimesh.repair.fix_normals(result, multibody=True)
    return result


def union_meshes(meshes: Iterable[trimesh.Trimesh]) -> trimesh.Trimesh:
    items = [clean(m) for m in meshes if m is not None and len(m.faces)]
    if not items:
        raise ValueError("No meshes to union")
    if len(items) == 1:
        return items[0]
    return clean(trimesh.boolean.union(items, engine="manifold", check_volume=False))


def concat_meshes(meshes: Iterable[trimesh.Trimesh]) -> trimesh.Trimesh:
    items = [clean(m) for m in meshes if m is not None and len(m.faces)]
    if not items:
        raise ValueError("No meshes to concatenate")
    return clean(trimesh.util.concatenate(items))


def difference_mesh(base: trimesh.Trimesh, cutters: Iterable[trimesh.Trimesh]) -> trimesh.Trimesh:
    items = [clean(base)] + [clean(m) for m in cutters if m is not None and len(m.faces)]
    if len(items) == 1:
        return items[0]
    return clean(trimesh.boolean.difference(items, engine="manifold", check_volume=False))


def keep_largest_component(mesh: trimesh.Trimesh, discarded_volume_limit_mm3: float = 0.01) -> trimesh.Trimesh:
    """Remove only negligible closed Boolean slivers from a one-body authority."""
    components = list(mesh.split(only_watertight=False))
    if len(components) <= 1:
        return clean(mesh)
    components.sort(key=lambda item: abs(float(item.volume)), reverse=True)
    discarded = sum(abs(float(item.volume)) for item in components[1:])
    if discarded > discarded_volume_limit_mm3:
        raise ValueError(f"Unexpected disconnected production volume: {discarded:.6f} mm3")
    return clean(components[0])


def transform_copy(mesh: trimesh.Trimesh, xyz: Sequence[float]) -> trimesh.Trimesh:
    result = mesh.copy()
    result.apply_translation(np.asarray(xyz, dtype=float))
    return result


def cylinder_axis(radius: float, height: float, axis: str, sections: int = 48) -> trimesh.Trimesh:
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    if axis == "z":
        return mesh
    if axis == "y":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2.0, [1, 0, 0]))
        return mesh
    if axis == "x":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0]))
        return mesh
    raise ValueError(axis)


def cylinder_between(a: Sequence[float], b: Sequence[float], radius: float, sections: int = 32) -> trimesh.Trimesh:
    a3 = np.asarray(a, dtype=float)
    b3 = np.asarray(b, dtype=float)
    vec = b3 - a3
    length = float(np.linalg.norm(vec))
    if length <= 1e-8:
        raise ValueError("Cylinder endpoints coincide")
    mesh = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    mesh.apply_transform(trimesh.geometry.align_vectors([0.0, 0.0, 1.0], vec / length))
    mesh.apply_translation((a3 + b3) / 2.0)
    return clean(mesh)


def rounded_box(extents: Sequence[float], center: Sequence[float], radius: float = 0.0) -> trimesh.Trimesh:
    ex, ey, ez = [float(v) for v in extents]
    if radius <= 0.0:
        mesh = trimesh.creation.box(extents=[ex, ey, ez])
        mesh.apply_translation(center)
        return clean(mesh)
    # Compact rounded approximation: central boxes plus corner cylinders.
    r = min(radius, ex / 2.0, ey / 2.0)
    parts = []
    if ex - 2 * r > 0:
        parts.append(rounded_box([ex - 2 * r, ey, ez], center, 0.0))
    if ey - 2 * r > 0:
        parts.append(rounded_box([ex, ey - 2 * r, ez], center, 0.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = cylinder_axis(r, ez, "z", 32)
            c.apply_translation([
                center[0] + sx * (ex / 2.0 - r),
                center[1] + sy * (ey / 2.0 - r),
                center[2],
            ])
            parts.append(c)
    return union_meshes(parts)


def tube_sweep(
    points: Sequence[Sequence[float]],
    radius_normal: float,
    radius_binormal: float | None = None,
    sections: int = 14,
    closed: bool = False,
    preferred_normal: Sequence[float] | None = None,
) -> trimesh.Trimesh:
    """Watertight elliptical tube along a sampled curve using transported frames."""
    pts = np.asarray(points, dtype=float)
    if len(pts) < 3:
        raise ValueError("Sweep needs at least three points")
    radius_binormal = radius_normal if radius_binormal is None else radius_binormal
    tangents = np.empty_like(pts)
    for i in range(len(pts)):
        if closed:
            tangents[i] = pts[(i + 1) % len(pts)] - pts[(i - 1) % len(pts)]
        elif i == 0:
            tangents[i] = pts[1] - pts[0]
        elif i == len(pts) - 1:
            tangents[i] = pts[-1] - pts[-2]
        else:
            tangents[i] = pts[i + 1] - pts[i - 1]
    tangents /= np.linalg.norm(tangents, axis=1)[:, None]

    if preferred_normal is None:
        normal0 = np.array([0.0, 1.0, 0.0])
    else:
        normal0 = np.asarray(preferred_normal, dtype=float)
    normal0 -= tangents[0] * np.dot(normal0, tangents[0])
    if np.linalg.norm(normal0) < 1e-6:
        normal0 = np.array([1.0, 0.0, 0.0])
        normal0 -= tangents[0] * np.dot(normal0, tangents[0])
    normal0 /= np.linalg.norm(normal0)
    normals = np.empty_like(pts)
    binormals = np.empty_like(pts)
    normals[0] = normal0
    binormals[0] = np.cross(tangents[0], normals[0])
    binormals[0] /= np.linalg.norm(binormals[0])
    for i in range(1, len(pts)):
        prev = normals[i - 1]
        candidate = prev - tangents[i] * np.dot(prev, tangents[i])
        if np.linalg.norm(candidate) < 1e-6:
            candidate = binormals[i - 1] - tangents[i] * np.dot(binormals[i - 1], tangents[i])
        candidate /= np.linalg.norm(candidate)
        if np.dot(candidate, prev) < 0:
            candidate *= -1.0
        normals[i] = candidate
        binormals[i] = np.cross(tangents[i], normals[i])
        binormals[i] /= np.linalg.norm(binormals[i])

    theta = np.linspace(0.0, 2.0 * math.pi, sections, endpoint=False)
    rings = []
    for i in range(len(pts)):
        ring = (
            pts[i]
            + np.cos(theta)[:, None] * radius_normal * normals[i]
            + np.sin(theta)[:, None] * radius_binormal * binormals[i]
        )
        rings.append(ring)
    vertices = np.vstack(rings)
    faces: list[list[int]] = []
    spans = len(pts) if closed else len(pts) - 1
    for i in range(spans):
        j = (i + 1) % len(pts)
        for k in range(sections):
            n = (k + 1) % sections
            a, b = i * sections + k, i * sections + n
            c, d = j * sections + n, j * sections + k
            faces.extend([[a, b, c], [a, c, d]])
    if not closed:
        start_center = len(vertices)
        end_center = start_center + 1
        vertices = np.vstack([vertices, pts[0], pts[-1]])
        for k in range(sections):
            n = (k + 1) % sections
            faces.append([start_center, n, k])
            a = (len(pts) - 1) * sections + k
            b = (len(pts) - 1) * sections + n
            faces.append([end_center, a, b])
    return clean(trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=False))


def side_outer_abs_x(p: Params, y: np.ndarray | float, z: np.ndarray | float, pattern: int) -> np.ndarray:
    yv = np.asarray(y, dtype=float)
    zv = np.asarray(z, dtype=float)
    global_z = zv + pattern * p.module_pitch
    period = 2.0 * p.module_pitch
    leaf_center = 63.0 + 18.0 * np.sin(2.0 * math.pi * global_z / period + 0.65)
    leaf = np.exp(-((yv - leaf_center) / 34.0) ** 2) * (0.45 + 0.55 * np.sin(math.pi * global_z / p.module_pitch) ** 2)
    shoulder = 0.5 + 0.5 * np.sin(2.0 * math.pi * global_z / period + yv / 31.0 + 0.9)
    macro = p.shell_macro_relief * np.clip(0.72 * leaf + 0.28 * shoulder, 0.0, 1.0)
    z_edge = np.clip(np.minimum(zv, p.module_pitch - zv) / 3.0, 0.0, 1.0)
    y_edge = np.clip(np.minimum(yv - 4.8, 118.1 - yv) / 3.0, 0.0, 1.0)
    fade = np.clip(z_edge * y_edge, 0.0, 1.0)
    micro = p.shell_micro_relief * (
        0.52
        + 0.28 * np.sin(2.0 * math.pi * yv / 2.15 + 0.35 * np.sin(global_z / 12.0))
        + 0.20 * np.sin(2.0 * math.pi * global_z / 2.35 + yv / 19.0)
    )
    micro = np.clip(micro, 0.0, p.shell_micro_relief) * fade
    return p.shell_inner_half_width + p.shell_nominal + macro + micro


def side_shell(p: Params, side: int, pattern: int, quality: str = "final") -> trimesh.Trimesh:
    pitch = 0.95 if quality == "final" else 3.4
    ys = np.linspace(4.8, 118.1, max(8, int(math.ceil((118.1 - 4.8) / pitch)) + 1))
    zs = np.linspace(0.0, p.module_pitch, max(8, int(math.ceil(p.module_pitch / pitch)) + 1))
    yy, zz = np.meshgrid(ys, zs, indexing="ij")
    outer_abs = side_outer_abs_x(p, yy, zz, pattern)
    outer = np.column_stack([(side * outer_abs).ravel(), yy.ravel(), zz.ravel()])
    inner = np.column_stack([
        np.full(yy.size, side * p.shell_inner_half_width),
        yy.ravel(),
        zz.ravel(),
    ])
    vertices = np.vstack([outer, inner])
    ny, nz = yy.shape
    offset = ny * nz
    faces: list[list[int]] = []
    def idx(i: int, j: int) -> int:
        return i * nz + j
    for i in range(ny - 1):
        for j in range(nz - 1):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            faces.extend([[a, b, c], [a, c, d]])
            ai, bi, ci, di = a + offset, b + offset, c + offset, d + offset
            faces.extend([[ai, ci, bi], [ai, di, ci]])
    # Close y-min/y-max and z-min/z-max boundaries.
    for i in range(ny - 1):
        for j in (0, nz - 1):
            a, b = idx(i, j), idx(i + 1, j)
            ai, bi = a + offset, b + offset
            faces.extend([[a, ai, bi], [a, bi, b]])
    for j in range(nz - 1):
        for i in (0, ny - 1):
            a, b = idx(i, j), idx(i, j + 1)
            ai, bi = a + offset, b + offset
            faces.extend([[a, b, bi], [a, bi, ai]])
    return clean(trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=False))


def oval_ribbon(p: Params, kind: str, quality: str = "final", phase: float = 0.0) -> trimesh.Trimesh:
    count = 168 if quality == "final" else 56
    if kind == "output":
        ts = np.linspace(-math.pi / 2.0 + 0.72, 3.0 * math.pi / 2.0 - 0.72, count)
        closed = False
    else:
        ts = np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)
        closed = True
    rx = 66.2
    rz = 56.6
    zc = p.module_pitch / 2.0
    pts = np.column_stack([
        rx * np.cos(ts),
        p.front_ribbon_y + 0.26 * np.sin(2.0 * ts + phase),
        zc + rz * np.sin(ts),
    ])
    return tube_sweep(
        pts,
        radius_normal=p.front_ribbon_depth_radius,
        radius_binormal=p.front_ribbon_width_radius,
        sections=16 if quality == "final" else 10,
        closed=closed,
        preferred_normal=[0.0, 1.0, 0.0],
    )


def bezier_curve(control: Sequence[Sequence[float]], count: int = 48) -> np.ndarray:
    pts = np.asarray(control, dtype=float)
    if len(pts) != 4:
        raise ValueError("Cubic Bezier requires four control points")
    t = np.linspace(0.0, 1.0, count)[:, None]
    return (
        (1 - t) ** 3 * pts[0]
        + 3 * (1 - t) ** 2 * t * pts[1]
        + 3 * (1 - t) * t**2 * pts[2]
        + t**3 * pts[3]
    )


def rear_struts(p: Params, quality: str = "final") -> list[trimesh.Trimesh]:
    sections = 14 if quality == "final" else 9
    curves = []
    for side in (-1, 1):
        # Two shallow wave ribs avoid an exposed industrial X or ladder while
        # still tying the central spine to both closed side shells.
        for z0, z1, bow in ((27.0, 41.0, 8.0), (97.0, 83.0, -8.0)):
            curves.append(bezier_curve([
                [side * 8.5, 6.6, z0],
                [side * 25.0, 7.0, z0 + bow],
                [side * 48.0, 7.2, z1 - bow * 0.45],
                [side * 64.8, 7.1, z1],
            ], 58 if quality == "final" else 26))
    return [tube_sweep(c, 1.35, 3.25, sections=sections, preferred_normal=[0, 1, 0]) for c in curves]


def connector_positions() -> list[tuple[float, float]]:
    # Both connector pairs sit close to the wall, outside the cylindrical roll
    # keep-out.  This keeps technical bosses out of the premium front view.
    return [(-66.6, 13.0), (66.6, 13.0), (-66.6, 25.0), (66.6, 25.0)]


def connector_bosses(p: Params, top: bool, bottom: bool, quality: str) -> list[trimesh.Trimesh]:
    sections = 32 if quality == "final" else 18
    items = []
    for x, y in connector_positions():
        if bottom:
            c = cylinder_axis(4.2, 10.0, "z", sections)
            c.apply_translation([x, y, 5.0])
            items.append(c)
        if top:
            c = cylinder_axis(4.2, 10.0, "z", sections)
            c.apply_translation([x, y, p.module_pitch - 5.0])
            items.append(c)
    return items


def connector_hole_cutters(p: Params, top: bool, bottom: bool, height: float | None = None) -> list[trimesh.Trimesh]:
    h = p.module_pitch if height is None else height
    items = []
    for x, y in connector_positions():
        if bottom:
            c = cylinder_axis(p.connector_hole_diameter / 2.0, p.connector_depth + 0.3, "z", 32)
            c.apply_translation([x, y, (p.connector_depth + 0.3) / 2.0 - 0.1])
            items.append(c)
        if top:
            c = cylinder_axis(p.connector_hole_diameter / 2.0, p.connector_depth + 0.3, "z", 32)
            c.apply_translation([x, y, h - (p.connector_depth + 0.3) / 2.0 + 0.1])
            items.append(c)
    return items


def brown_module(p: Params, height: float, quality: str = "final", wall_holes: bool = True) -> trimesh.Trimesh:
    sections = 40 if quality == "final" else 20
    spine = rounded_box([p.rear_spine_width, p.rear_spine_thickness, height], [0.0, p.rear_spine_thickness / 2.0, height / 2.0], 2.2)
    rods = []
    for x in (-67.0, 67.0):
        rod = cylinder_axis(2.65, height, "z", sections)
        rod.apply_translation([x, 6.0, height / 2.0])
        rods.append(rod)
    body = concat_meshes([spine, *rods])
    if wall_holes:
        cutters = []
        z_targets = [height * 0.31, height * 0.71] if height > 70 else [height * 0.50]
        for z in z_targets:
            through = cylinder_axis(2.35, p.rear_spine_thickness + 1.0, "y", sections)
            through.apply_translation([0.0, p.rear_spine_thickness / 2.0, z])
            counter = cylinder_axis(4.7, 2.4, "y", sections)
            counter.apply_translation([0.0, p.rear_spine_thickness - 0.7, z])
            cutters.extend([through, counter])
        body = difference_mesh(body, cutters)
    if height >= 100.0:
        if not WATERMARK_DXF.exists():
            raise FileNotFoundError(f"Approved watermark asset missing: {WATERMARK_DXF}")
        source_path = trimesh.load_path(WATERMARK_DXF)
        mark_cutters = []
        # The selector chose compact JSI-WM-001-R1 at uniform scale 1.0.
        # Keep the approved monogram at 0 degrees so J and S read normally
        # when the finished rear exterior is viewed from +Y.  Extrusion spans
        # 0.05 mm beyond that face and exactly 0.40 mm into the 5.20 mm spine.
        for polygon in source_path.polygons_full:
            cutter = trimesh.creation.extrude_polygon(polygon, height=0.45, engine="earcut")
            old = cutter.vertices.copy()
            cutter.vertices = np.column_stack([
                old[:, 0],
                p.rear_spine_thickness + 0.05 - old[:, 2],
                height / 2.0 + old[:, 1],
            ])
            mark_cutters.append(clean(cutter))
        body = difference_mesh(body, mark_cutters)
    return body


def brown_clearance_cutters(p: Params, height: float, quality: str = "final") -> list[trimesh.Trimesh]:
    sections = 36 if quality == "final" else 18
    items = [rounded_box([p.rear_spine_width + 0.25, p.rear_spine_thickness + 0.2, height + 0.2], [0.0, (p.rear_spine_thickness + 0.2) / 2.0, height / 2.0], 2.2)]
    for x in (-67.0, 67.0):
        rod = cylinder_axis(2.80, height + 0.2, "z", sections)
        rod.apply_translation([x, 6.0, height / 2.0])
        items.append(rod)
    return items


def side_curve_points(p: Params, side: int, pattern: int, seed: float, count: int = 54) -> np.ndarray:
    t = np.linspace(0.0, 1.0, count)
    y = 13.0 + 98.0 * t + 7.0 * np.sin(math.pi * t + seed)
    z = 4.0 + 116.0 * t + 12.0 * np.sin(2.0 * math.pi * t + seed)
    x_abs = side_outer_abs_x(p, y, np.clip(z, 0.0, p.module_pitch), pattern)
    return np.column_stack([side * x_abs, y, np.clip(z, 2.0, p.module_pitch - 2.0)])


def side_surface_sweep(
    p: Params,
    side: int,
    points: np.ndarray,
    width: float,
    embed: float,
    protrude: float,
    quality: str,
) -> trimesh.Trimesh:
    radial = (embed + protrude) / 2.0
    offset = (protrude - embed) / 2.0
    shifted = points.copy()
    shifted[:, 0] += side * offset
    return tube_sweep(
        shifted,
        radius_normal=radial,
        radius_binormal=width / 2.0,
        sections=12 if quality == "final" else 8,
        closed=False,
        preferred_normal=[float(side), 0.0, 0.0],
    )


def front_crack_points(p: Params, side: int, kind: str, pattern: int, count: int = 60) -> np.ndarray:
    z0 = 31.0 if kind == "output" else 3.0
    z = np.linspace(z0, p.module_pitch - 3.0, count)
    norm = np.clip((z - p.module_pitch / 2.0) / 56.6, -0.995, 0.995)
    x = side * 66.2 * np.sqrt(np.maximum(0.0, 1.0 - norm**2))
    x += side * 0.8 * np.sin(z / 15.0 + pattern * 0.8)
    y = np.full_like(z, p.front_ribbon_y + p.front_ribbon_depth_radius)
    return np.column_stack([x, y, z])


def front_surface_sweep(points: np.ndarray, width: float, embed: float, protrude: float, quality: str) -> trimesh.Trimesh:
    radial = (embed + protrude) / 2.0
    offset = (protrude - embed) / 2.0
    shifted = points.copy()
    shifted[:, 1] += offset
    return tube_sweep(
        shifted,
        radius_normal=radial,
        radius_binormal=width / 2.0,
        sections=12 if quality == "final" else 8,
        closed=False,
        preferred_normal=[0.0, 1.0, 0.0],
    )


def seigaiha_curves(p: Params, side: int, pattern: int, quality: str) -> list[np.ndarray]:
    curves = []
    count = 26 if quality == "final" else 12
    for row, base in enumerate((16.0, 48.0, 80.0)):
        shift = 14.0 if (row + pattern) % 2 else 0.0
        for center_y in (26.0 + shift, 72.0 + shift, 118.0 + shift):
            for radius in (12.0, 18.0):
                theta = np.linspace(0.08, math.pi - 0.08, count)
                y = center_y + radius * np.cos(theta)
                z = base + radius * np.sin(theta)
                mask = (y >= 8.0) & (y <= 115.0) & (z >= 5.0) & (z <= p.module_pitch - 5.0)
                if np.count_nonzero(mask) < 6:
                    continue
                y = y[mask]
                z = z[mask]
                x_abs = side_outer_abs_x(p, y, z, pattern)
                curves.append(np.column_stack([side * x_abs, y, z]))
    return curves


def accent_system(p: Params, kind: str, pattern: int, quality: str) -> tuple[trimesh.Trimesh, trimesh.Trimesh, list[trimesh.Trimesh]]:
    gold_items = []
    gold_pockets = []
    sand_items = []
    sand_pockets = []
    for side in (-1, 1):
        primary = side_curve_points(p, side, pattern, seed=0.55 + 0.7 * (side > 0), count=62 if quality == "final" else 30)
        gold_items.append(side_surface_sweep(p, side, primary, 1.05, 0.32, 0.20, quality))
        gold_pockets.append(side_surface_sweep(p, side, primary, 1.28, 0.38, 0.02, quality))
        # One short branch creates the characteristic repaired-ceramic gesture.
        mid = len(primary) // 2
        branch = np.vstack([
            primary[mid],
            primary[mid] + [0.0, -7.0, 6.0],
            primary[mid] + [0.0, -13.0, 14.0],
        ])
        branch[:, 0] = side * side_outer_abs_x(p, branch[:, 1], branch[:, 2], pattern)
        gold_items.append(side_surface_sweep(p, side, branch, 1.00, 0.32, 0.20, quality))
        gold_pockets.append(side_surface_sweep(p, side, branch, 1.24, 0.38, 0.02, quality))
        for curve in seigaiha_curves(p, side, pattern, quality):
            sand_items.append(side_surface_sweep(p, side, curve, 0.96, 0.24, 0.18, quality))
            sand_pockets.append(side_surface_sweep(p, side, curve, 1.16, 0.29, 0.02, quality))
    for side in (-1, 1):
        fp = front_crack_points(p, side, kind, pattern, 64 if quality == "final" else 28)
        gold_items.append(front_surface_sweep(fp, 1.08, 0.32, 0.20, quality))
        gold_pockets.append(front_surface_sweep(fp, 1.30, 0.38, 0.02, quality))
    return concat_meshes(gold_items), concat_meshes(sand_items), [*gold_pockets, *sand_pockets]


def output_cradle(p: Params, quality: str) -> list[trimesh.Trimesh]:
    parts = []
    # Two smooth rails stop the lowest roll but remain open toward the front.
    for x in (-34.0, 34.0):
        rail = rounded_box([11.0, 111.5, 12.0], [x, 61.5, 6.0], 3.2)
        parts.append(rail)
    rear_bridge = tube_sweep(
        np.column_stack([
            np.linspace(-66.8, 66.8, 72 if quality == "final" else 28),
            np.full(72 if quality == "final" else 28, 7.1),
            7.2 + 1.1 * np.cos(np.linspace(-math.pi, math.pi, 72 if quality == "final" else 28)),
        ]),
        1.35,
        3.1,
        sections=12 if quality == "final" else 8,
        preferred_normal=[0, 1, 0],
    )
    parts.append(rear_bridge)
    return parts


def tray_mount_pad(p: Params, quality: str) -> trimesh.Trimesh:
    pad = rounded_box([6.0, 31.0, 22.0], [67.6, p.roll_center_y, 63.0], 2.4)
    cutters = []
    for y in (p.roll_center_y - 8.0, p.roll_center_y + 8.0):
        hole = cylinder_axis(2.25, 7.0, "x", 32 if quality == "final" else 18)
        hole.apply_translation([67.5, y, 63.0])
        cutters.append(hole)
    return difference_mesh(pad, cutters)


def build_module(p: Params, kind: str, pattern: int, quality: str = "final") -> dict[str, trimesh.Trimesh]:
    if kind not in {"output", "middle"}:
        raise ValueError(kind)
    left = side_shell(p, -1, pattern, quality)
    right = side_shell(p, 1, pattern, quality)
    ring = oval_ribbon(p, kind, quality, phase=pattern * 0.55)
    parts = [left, right, ring, *rear_struts(p, quality)]
    parts.extend(connector_bosses(p, top=True, bottom=(kind != "output"), quality=quality))
    if kind == "output":
        parts.extend(output_cradle(p, quality))
    if kind == "middle" and pattern == 0:
        parts.append(tray_mount_pad(p, quality))
    ivory = union_meshes(parts)
    gold, sand, accent_pockets = accent_system(p, kind, pattern, quality)
    cutters = [*brown_clearance_cutters(p, p.module_pitch, quality), *accent_pockets]
    cutters.extend(connector_hole_cutters(p, top=True, bottom=(kind != "output")))
    ivory = keep_largest_component(difference_mesh(ivory, cutters))
    bronze = brown_module(p, p.module_pitch, quality, wall_holes=True)
    return {"ivory": ivory, "gold": gold, "bronze": bronze, "sand": sand}


def crown_ivory(p: Params, pattern: int, quality: str) -> trimesh.Trimesh:
    # Low closed side shoulders keep the top opening visually coherent.
    shoulders = []
    for side in (-1, 1):
        s = rounded_box([4.0, 113.0, 17.0], [side * 66.7, 61.4, 8.5], 2.0)
        shoulders.append(s)
    curves = []
    n = 64 if quality == "final" else 28
    curves.append(bezier_curve([[-66, 118.8, 4], [-58, 120.0, 40], [-24, 120.2, 47], [0, 119.6, 18]], n))
    curves.append(bezier_curve([[66, 118.8, 4], [58, 120.0, 40], [24, 120.2, 47], [0, 119.6, 18]], n))
    curves.append(bezier_curve([[-67, 7.0, 5], [-67.5, 34.0, 42], [-67.3, 91.0, 43], [-67, 118.0, 7]], n))
    curves.append(bezier_curve([[67, 7.0, 5], [67.5, 34.0, 42], [67.3, 91.0, 43], [67, 118.0, 7]], n))
    curves.append(bezier_curve([[-65, 6.3, 7], [-35, 6.0, 33], [35, 6.0, 33], [65, 6.3, 7]], n))
    loops = [tube_sweep(c, 1.45, 3.5, sections=14 if quality == "final" else 9, preferred_normal=[0, 1, 0]) for c in curves]
    base = union_meshes([*shoulders, *loops, *connector_bosses(p, top=False, bottom=True, quality=quality)])
    cutters = brown_clearance_cutters(p, p.crown_height, quality)
    cutters.extend(connector_hole_cutters(p, top=False, bottom=True, height=p.crown_height))
    return keep_largest_component(difference_mesh(base, cutters))


def crown_accents(p: Params, quality: str) -> tuple[trimesh.Trimesh, trimesh.Trimesh]:
    # Gold cap seams follow the two front crown ribbons; a sand zen pebble sits at the right shoulder.
    n = 48 if quality == "final" else 22
    gold_curves = [
        bezier_curve([[-63, 120.5, 8], [-52, 121.0, 29], [-31, 121.0, 38], [-15, 120.4, 27]], n),
        bezier_curve([[64, 120.5, 7], [55, 121.0, 28], [37, 121.0, 39], [21, 120.4, 30]], n),
    ]
    gold = concat_meshes([front_surface_sweep(c, 1.10, 0.30, 0.20, quality) for c in gold_curves])
    pebble = trimesh.creation.icosphere(subdivisions=3 if quality == "final" else 2, radius=1.0)
    pebble.apply_scale([10.5, 6.7, 3.6])
    pebble.apply_translation([57.0, 113.0, 16.0])
    return gold, clean(pebble)


def build_crown(p: Params, quality: str = "final") -> dict[str, trimesh.Trimesh]:
    ivory = crown_ivory(p, 1, quality)
    gold, sand = crown_accents(p, quality)
    bronze = brown_module(p, p.crown_height, quality, wall_holes=True)
    return {"ivory": ivory, "gold": gold, "bronze": bronze, "sand": sand}


def make_connector_pin(p: Params, diameter: float | None = None) -> trimesh.Trimesh:
    d = p.connector_pin_diameter if diameter is None else diameter
    r = d / 2.0
    total = 2.0 * p.connector_depth - 1.0
    profile = np.array([
        [0.0, 0.0], [r - 0.32, 0.0], [r, 1.0], [r, total - 1.0], [r - 0.32, total], [0.0, total]
    ])
    return clean(trimesh.creation.revolve(profile, sections=48))


def make_scent_tray(p: Params, quality: str = "final") -> trimesh.Trimesh:
    sections = 72 if quality == "final" else 32
    center = np.array([88.0, p.roll_center_y, 67.0])
    outer = cylinder_axis(18.0, 7.0, "z", sections)
    outer.apply_translation([center[0], center[1], center[2]])
    inner = cylinder_axis(14.0, 5.8, "z", sections)
    inner.apply_translation([center[0], center[1], center[2] + 2.1])
    bowl = difference_mesh(outer, [inner])
    bracket = rounded_box([19.0, 27.0, 12.0], [74.0, p.roll_center_y, 63.0], 2.2)
    pegs = []
    for y in (p.roll_center_y - 8.0, p.roll_center_y + 8.0):
        peg = cylinder_axis(2.0, 5.0, "x", 32)
        peg.apply_translation([68.0, y, 63.0])
        pegs.append(peg)
    return union_meshes([bowl, bracket, *pegs])


def make_fit_coupon(p: Params) -> dict[str, trimesh.Trimesh]:
    base = rounded_box([72.0, 34.0, 5.0], [36.0, 17.0, 2.5], 3.0)
    cutters = []
    for i, diameter in enumerate((5.10, 5.20, 5.30)):
        hole = cylinder_axis(diameter / 2.0, 5.4, "z", 32)
        hole.apply_translation([12.0 + i * 12.0, 23.0, 2.5])
        cutters.append(hole)
    for i, width in enumerate((1.18, 1.28, 1.38)):
        groove = rounded_box([24.0, width, 0.42], [52.0, 9.0 + i * 6.0, 4.82], 0.2)
        cutters.append(groove)
    ivory = difference_mesh(base, cutters)
    pins = []
    for i, diameter in enumerate((4.70, 4.80, 4.90)):
        pin = make_connector_pin(p, diameter)
        pin.apply_translation([12.0 + i * 12.0, 23.0, 0.0])
        pins.append(pin)
    gold = []
    for i, width in enumerate((1.00, 1.10, 1.20)):
        strip = rounded_box([24.0, width, 0.52], [52.0, 9.0 + i * 6.0, 4.83], 0.18)
        gold.append(strip)
    return {"ivory": ivory, "bronze": concat_meshes(pins), "gold": concat_meshes(gold)}


def make_texture_coupon(p: Params, quality: str = "final") -> dict[str, trimesh.Trimesh]:
    # Vertical coupon: same nominal wall, groove reserve and side texture orientation as the tower.
    pp = Params(**{**asdict(p), "module_pitch": 50.0})
    ys = np.linspace(0.0, 50.0, 54 if quality == "final" else 20)
    zs = np.linspace(0.0, 50.0, 54 if quality == "final" else 20)
    yy, zz = np.meshgrid(ys, zs, indexing="ij")
    texture = 0.22 * np.clip(0.5 + 0.3 * np.sin(2 * math.pi * yy / 2.15) + 0.2 * np.sin(2 * math.pi * zz / 2.35 + yy / 17.0), 0, 1)
    outer = np.column_stack([(1.8 + texture).ravel(), yy.ravel(), zz.ravel()])
    inner = np.column_stack([np.zeros(yy.size), yy.ravel(), zz.ravel()])
    vertices = np.vstack([outer, inner])
    ny, nz = yy.shape
    offset = ny * nz
    faces = []
    def idx(i: int, j: int) -> int: return i * nz + j
    for i in range(ny - 1):
        for j in range(nz - 1):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            faces.extend([[a, b, c], [a, c, d], [a + offset, c + offset, b + offset], [a + offset, d + offset, c + offset]])
    for i in range(ny - 1):
        for j in (0, nz - 1):
            a, b = idx(i, j), idx(i + 1, j)
            faces.extend([[a, a + offset, b + offset], [a, b + offset, b]])
    for j in range(nz - 1):
        for i in (0, ny - 1):
            a, b = idx(i, j), idx(i, j + 1)
            faces.extend([[a, b, b + offset], [a, b + offset, a + offset]])
    ivory = clean(trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=False))
    return {"ivory": ivory}


def make_roll(p: Params, diameter: float, width: float, quality: str = "preview") -> trimesh.Trimesh:
    roll = cylinder_axis(diameter / 2.0, width, "y", 64 if quality == "final" else 40)
    roll.apply_translation([0.0, p.roll_center_y, 0.0])
    return clean(roll)


def mesh_metrics(mesh: trimesh.Trimesh) -> dict:
    components = mesh.split(only_watertight=False)
    return {
        "triangles": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "components": int(len(components)),
        "volume_mm3": float(abs(mesh.volume)),
        "surface_area_mm2": float(mesh.area),
        "bounds_mm": np.round(mesh.bounds, 3).tolist(),
    }


def export_stl(mesh: trimesh.Trimesh, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path, file_type="stl")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_default(value):
    """Convert NumPy scalar values emitted by geometry checks to JSON types."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def add_3mf_object(resources: ET.Element, object_id: int, mesh: trimesh.Trimesh, material_index: int, name: str) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "pid": "1", "pindex": str(material_index), "name": name})
    mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
    verts = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
    for v in mesh.vertices:
        ET.SubElement(verts, f"{{{ns}}}vertex", {"x": f"{v[0]:.6f}", "y": f"{v[1]:.6f}", "z": f"{v[2]:.6f}"})
    tris = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
    for face in mesh.faces:
        ET.SubElement(tris, f"{{{ns}}}triangle", {"v1": str(int(face[0])), "v2": str(int(face[1])), "v3": str(int(face[2]))})


def write_3mf(path: Path, objects: list[tuple[str, trimesh.Trimesh, int]], build_items: list[tuple[int, Sequence[float]]], title: str) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "de-DE"})
    metadata = ET.SubElement(model, f"{{{ns}}}metadata", {"name": "Title"})
    metadata.text = title
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    mats = ET.SubElement(resources, f"{{{ns}}}basematerials", {"id": "1"})
    for name, color in PALETTE:
        ET.SubElement(mats, f"{{{ns}}}base", {"name": name, "displaycolor": color})
    for idx, (name, mesh, material) in enumerate(objects, start=2):
        add_3mf_object(resources, idx, mesh, material, name)
    build = ET.SubElement(model, f"{{{ns}}}build")
    for obj_index, xyz in build_items:
        attrs = {"objectid": str(obj_index + 2)}
        if any(abs(float(v)) > 1e-9 for v in xyz):
            attrs["transform"] = f"1 0 0 0 1 0 0 0 1 {xyz[0]:.6f} {xyz[1]:.6f} {xyz[2]:.6f}"
        ET.SubElement(build, f"{{{ns}}}item", attrs)
    model_bytes = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    content_types = b'''<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'''
    rels = b'''<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("3D/3dmodel.model", model_bytes)
    temporary.replace(path)


def write_obj(path: Path, scene_items: list[tuple[str, trimesh.Trimesh, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mtl_path = path.with_suffix(".mtl")
    lines = [f"mtllib {mtl_path.name}"]
    offset = 1
    for name, mesh, material in scene_items:
        lines.extend([f"o {name}", f"usemtl {material}"])
        lines.extend(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}" for v in mesh.vertices)
        lines.extend(f"f {int(f[0])+offset} {int(f[1])+offset} {int(f[2])+offset}" for f in mesh.faces)
        offset += len(mesh.vertices)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    mtl_lines = []
    for (name, color), material in zip(PALETTE, ("ivory", "gold", "bronze", "sand")):
        rgb = tuple(int(color[i:i+2], 16) / 255.0 for i in (1, 3, 5))
        mtl_lines.extend([f"newmtl {material}", f"Kd {rgb[0]:.5f} {rgb[1]:.5f} {rgb[2]:.5f}", "Ks 0.18 0.18 0.18", "Ns 36", ""])
    mtl_path.write_text("\n".join(mtl_lines), encoding="utf-8")


def render_meshes(path: Path, meshes: list[tuple[trimesh.Trimesh, str]], yaw_deg: float, pitch_deg: float, title: str, figsize=(7.0, 12.0)) -> None:
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    rz = np.array([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(pitch), -math.sin(pitch)], [0, math.sin(pitch), math.cos(pitch)]])
    rot = rx @ rz
    light = np.array([-0.32, -0.52, 0.79]); light /= np.linalg.norm(light)
    colors = {
        "ivory": np.array([0.84, 0.81, 0.74]), "gold": np.array([0.73, 0.52, 0.18]),
        "bronze": np.array([0.29, 0.17, 0.11]), "sand": np.array([0.67, 0.58, 0.46]),
        "roll": np.array([0.96, 0.95, 0.90]),
    }
    polys, depths, face_colors = [], [], []
    for mesh, material in meshes:
        vertices = mesh.vertices @ rot.T
        projected = vertices[:, :2].copy(); projected[:, 1] *= -1
        mpolys = projected[mesh.faces]
        mdepth = vertices[mesh.faces][:, :, 2].mean(axis=1)
        normals = mesh.face_normals @ rot.T
        shade = np.clip(0.34 + 0.66 * np.maximum(0.0, normals @ light), 0.26, 1.0)
        base = colors[material]
        mcolors = np.clip(base[None, :] * shade[:, None] + 0.055, 0, 1)
        polys.extend(mpolys); depths.extend(mdepth); face_colors.extend(mcolors)
    order = np.argsort(depths)
    ordered_polys = [polys[i] for i in order]
    ordered_colors = [face_colors[i] for i in order]
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    fig.patch.set_facecolor("#EEE8DC"); ax.set_facecolor("#EEE8DC")
    ax.add_collection(PolyCollection(ordered_polys, facecolors=ordered_colors, edgecolors="none"))
    pts = np.concatenate(ordered_polys, axis=0)
    minxy, maxxy = pts.min(axis=0), pts.max(axis=0)
    margin = (maxxy - minxy) * np.array([0.08, 0.045])
    ax.set_xlim(minxy[0] - margin[0], maxxy[0] + margin[0])
    ax.set_ylim(minxy[1] - margin[1], maxxy[1] + margin[1])
    ax.set_aspect("equal"); ax.axis("off")
    fig.text(0.055, 0.976, title, ha="left", va="top", fontsize=15, weight="bold", color="#2F2924")
    fig.text(0.055, 0.950, "DRAFT v2.1 · actual generated geometry", ha="left", va="top", fontsize=8.5, color="#62594F")
    fig.subplots_adjust(left=0.03, right=0.97, bottom=0.025, top=0.925)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fifo_collision_test(p: Params, preview_modules: dict[str, dict[str, trimesh.Trimesh]], crown: dict[str, trimesh.Trimesh]) -> dict:
    # Accent geometry is outside every keep-out; test the four physical colour regions anyway.
    assembly_parts = []
    sequence = [("output", 0)]
    for index in range(1, p.roll_count):
        sequence.append(("middle_a" if index % 2 else "middle_b", index))
    for key, index in sequence:
        z = index * p.module_pitch
        for mesh in preview_modules[key].values():
            assembly_parts.append(transform_copy(mesh, [0, 0, z]))
    for mesh in crown.values():
        assembly_parts.append(transform_copy(mesh, [0, 0, p.roll_count * p.module_pitch]))
    tray = make_scent_tray(p, "preview")
    assembly_parts.append(transform_copy(tray, [0, 0, p.tray_module_index * p.module_pitch]))
    assembly = concat_meshes(assembly_parts)
    proxy = make_roll(p, p.proxy_diameter, p.proxy_width, "preview")
    samples = np.linspace(74.0, p.roll_count * p.module_pitch - p.proxy_diameter / 2.0 - 2.0, 121)
    collisions = []
    max_volume = 0.0
    # Spatially crop by module before robust intersection to keep the test bounded.
    for zc in samples:
        roll = transform_copy(proxy, [0, 0, zc])
        inter = trimesh.boolean.intersection([assembly, roll], engine="manifold", check_volume=False)
        vol = 0.0 if inter is None or len(inter.faces) == 0 else abs(float(inter.volume))
        max_volume = max(max_volume, vol)
        if vol > 0.05:
            collisions.append({"roll_center_z_mm": round(float(zc), 4), "intersection_volume_mm3": vol})
    # Verify that the output stop is intentional at a small overtravel.
    rail_inner_x = 34.0 - 11.0 / 2.0
    rest_center = 12.0 + math.sqrt((p.proxy_diameter / 2.0) ** 2 - rail_inner_x**2)
    stop_roll = transform_copy(proxy, [0, 0, rest_center - 0.6])
    output_all = concat_meshes(preview_modules["output"].values())
    stop_inter = trimesh.boolean.intersection([output_all, stop_roll], engine="manifold", check_volume=False)
    stop_volume = 0.0 if stop_inter is None or len(stop_inter.faces) == 0 else abs(float(stop_inter.volume))
    return {
        "method": "121-position robust mesh Boolean sweep on low-tessellation geometry with identical protected inner surfaces",
        "proxy_mm": [p.proxy_diameter, p.proxy_width],
        "positions_tested": len(samples),
        "free_shaft_start_center_z_mm": float(samples[0]),
        "free_shaft_end_center_z_mm": float(samples[-1]),
        "collision_count": len(collisions),
        "max_intersection_volume_mm3": max_volume,
        "intentional_output_stop_center_z_mm": rest_center,
        "output_stop_intersection_at_0p6mm_overtravel_mm3": stop_volume,
        "collisions": collisions[:20],
    }


def expected_components(name: str) -> int | None:
    if "_ivory" in name:
        return 1
    if "connector_pin" in name or "scent_tray" in name:
        return 1
    return None


def validate_exports(stl_dir: Path) -> dict:
    report = {}
    for path in sorted(stl_dir.glob("*.stl")):
        mesh = trimesh.load_mesh(path, process=True)
        metrics = mesh_metrics(mesh)
        exp = expected_components(path.name)
        metrics["expected_components"] = exp if exp is not None else "documented-multibody-color-solid"
        metrics["passed"] = bool(metrics["watertight"] and metrics["winding_consistent"] and metrics["volume_mm3"] > 0 and (exp is None or metrics["components"] == exp))
        report[path.name] = metrics
    return report


def build_preview_scene(p: Params, modules: dict[str, dict[str, trimesh.Trimesh]], crown: dict[str, trimesh.Trimesh]) -> list[tuple[trimesh.Trimesh, str]]:
    items = []
    sequence = [("output", 0)] + [("middle_a" if i % 2 else "middle_b", i) for i in range(1, p.roll_count)]
    for key, index in sequence:
        for material, mesh in modules[key].items():
            items.append((transform_copy(mesh, [0, 0, index * p.module_pitch]), material))
    for material, mesh in crown.items():
        items.append((transform_copy(mesh, [0, 0, p.roll_count * p.module_pitch]), material))
    items.append((transform_copy(make_scent_tray(p, "preview"), [0, 0, p.tray_module_index * p.module_pitch]), "sand"))
    nominal = make_roll(p, p.roll_diameter, p.roll_width, "preview")
    rail_inner_x = 34.0 - 11.0 / 2.0
    rest_center = 12.0 + math.sqrt((p.roll_diameter / 2.0) ** 2 - rail_inner_x**2)
    for i in range(p.roll_count):
        items.append((transform_copy(nominal, [0, 0, rest_center + i * p.roll_diameter]), "roll"))
    return items


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)


def build(p: Params, out_dir: Path, quality: str) -> None:
    if p.roll_count < 3 or p.roll_count > 8:
        raise ValueError("roll_count must be in [3, 8]")
    if p.body_width_max > 142.0 + 1e-6:
        raise ValueError("body width exceeds approved envelope")
    stl_dir = out_dir / "STL"; mf_dir = out_dir / "3MF"; obj_dir = out_dir / "OBJ"; preview_dir = out_dir / "preview"; report_dir = out_dir / "reports"
    for directory in (stl_dir, mf_dir, obj_dir, preview_dir, report_dir):
        directory.mkdir(parents=True, exist_ok=True)

    module_defs = {
        "output": ("output", 0),
        "middle_a": ("middle", 1),
        "middle_b": ("middle", 0),
    }
    modules = {key: build_module(p, kind, pattern, quality) for key, (kind, pattern) in module_defs.items()}
    crown = build_crown(p, quality)
    pin = make_connector_pin(p)
    tray = make_scent_tray(p, quality)
    fit_coupon = make_fit_coupon(p)
    texture_coupon = make_texture_coupon(p, quality)

    manufacturing: dict[str, trimesh.Trimesh] = {}
    labels = {"output": "MODULE_OUTPUT", "middle_a": "MODULE_MIDDLE_A", "middle_b": "MODULE_MIDDLE_B"}
    for key, bodies in modules.items():
        for material, mesh in bodies.items():
            manufacturing[f"{labels[key]}_{material}.stl"] = mesh
    for material, mesh in crown.items():
        manufacturing[f"MODULE_CROWN_{material}.stl"] = mesh
    manufacturing["connector_pin_4p8mm_bronze.stl"] = pin
    manufacturing["scent_tray_sand.stl"] = tray
    for material, mesh in fit_coupon.items():
        manufacturing[f"FIT_COUPON_{material}.stl"] = mesh
    for material, mesh in texture_coupon.items():
        manufacturing[f"TEXTURE_COUPON_{material}.stl"] = mesh
    for name, mesh in manufacturing.items():
        export_stl(mesh, stl_dir / name)

    # Per-module four-colour projects.
    for key, bodies in modules.items():
        objects = [(f"{labels[key]}_{material}", mesh, {"ivory": IVORY, "gold": GOLD, "bronze": BRONZE, "sand": SAND}[material]) for material, mesh in bodies.items()]
        write_3mf(mf_dir / f"{labels[key]}_4COLOR.3mf", objects, [(i, (0, 0, 0)) for i in range(len(objects))], f"{labels[key]} four-colour module")
    crown_objects = [(f"MODULE_CROWN_{material}", mesh, {"ivory": IVORY, "gold": GOLD, "bronze": BRONZE, "sand": SAND}[material]) for material, mesh in crown.items()]
    write_3mf(mf_dir / "MODULE_CROWN_4COLOR.3mf", crown_objects, [(i, (0, 0, 0)) for i in range(len(crown_objects))], "ZEN KINTSUGI WAVE crown")

    objects: list[tuple[str, trimesh.Trimesh, int]] = []
    obj_index: dict[tuple[str, str], int] = {}
    for key, bodies in modules.items():
        for material, mesh in bodies.items():
            obj_index[(key, material)] = len(objects)
            objects.append((f"{labels[key]}_{material}", mesh, {"ivory": IVORY, "gold": GOLD, "bronze": BRONZE, "sand": SAND}[material]))
    for material, mesh in crown.items():
        obj_index[("crown", material)] = len(objects)
        objects.append((f"MODULE_CROWN_{material}", mesh, {"ivory": IVORY, "gold": GOLD, "bronze": BRONZE, "sand": SAND}[material]))
    obj_index[("tray", "sand")] = len(objects); objects.append(("SCENT_TRAY_sand", tray, SAND))
    obj_index[("pin", "bronze")] = len(objects); objects.append(("CONNECTOR_PIN_bronze", pin, BRONZE))
    build_items = []
    sequence = [("output", 0)] + [("middle_a" if i % 2 else "middle_b", i) for i in range(1, p.roll_count)]
    for key, index in sequence:
        z = index * p.module_pitch
        for material in modules[key]:
            build_items.append((obj_index[(key, material)], (0, 0, z)))
    for material in crown:
        build_items.append((obj_index[("crown", material)], (0, 0, p.roll_count * p.module_pitch)))
    build_items.append((obj_index[("tray", "sand")], (0, 0, p.tray_module_index * p.module_pitch)))
    pin_height = 2.0 * p.connector_depth - 1.0
    for interface in range(1, p.roll_count + 1):
        z = interface * p.module_pitch - pin_height / 2.0
        for x, y in connector_positions():
            build_items.append((obj_index[("pin", "bronze")], (x, y, z)))
    write_3mf(mf_dir / f"{PRODUCT}_ASSEMBLY_5R_4COLOR_DRAFT.3mf", objects, build_items, "ZEN KINTSUGI WAVE 5-roll assembly DRAFT")

    assembly_obj = []
    for key, index in sequence:
        for material, mesh in modules[key].items():
            assembly_obj.append((f"{key}_{index}_{material}", transform_copy(mesh, [0, 0, index * p.module_pitch]), material))
    for material, mesh in crown.items():
        assembly_obj.append((f"crown_{material}", transform_copy(mesh, [0, 0, p.roll_count * p.module_pitch]), material))
    assembly_obj.append(("scent_tray_sand", transform_copy(tray, [0, 0, p.tray_module_index * p.module_pitch]), "sand"))
    write_obj(obj_dir / f"{PRODUCT}_ASSEMBLY_5R_DRAFT.obj", assembly_obj)

    validation = validate_exports(stl_dir)
    preview_modules = {key: build_module(p, kind, pattern, "preview") for key, (kind, pattern) in module_defs.items()}
    preview_crown = build_crown(p, "preview")
    fifo = fifo_collision_test(p, preview_modules, preview_crown)
    scene = build_preview_scene(p, preview_modules, preview_crown)
    render_meshes(preview_dir / "preview_hero_front_right.png", scene, yaw_deg=-12.0, pitch_deg=78.0, title="ZEN KINTSUGI WAVE · HERO")
    render_meshes(preview_dir / "preview_front.png", scene, yaw_deg=0.0, pitch_deg=90.0, title="ZEN KINTSUGI WAVE · FRONT")
    render_meshes(preview_dir / "preview_side.png", scene, yaw_deg=-82.0, pitch_deg=80.0, title="ZEN KINTSUGI WAVE · SIDE")
    rear_scene = [(m, mat) for m, mat in scene if mat != "roll"]
    render_meshes(preview_dir / "preview_rear.png", rear_scene, yaw_deg=168.0, pitch_deg=80.0, title="ZEN KINTSUGI WAVE · REAR")

    previous_volume = 890326.54
    selected_volume = 0.0
    for key, index in sequence:
        selected_volume += sum(abs(m.volume) for m in modules[key].values())
    selected_volume += sum(abs(m.volume) for m in crown.values()) + abs(tray.volume) + 20 * abs(pin.volume)
    reduction = 100.0 * (1.0 - selected_volume / previous_volume)
    wall_report = {
        "side_shell_nominal_mm": p.shell_nominal,
        "maximum_microtexture_added_outward_mm": p.shell_micro_relief,
        "maximum_accent_pocket_penetration_mm": 0.38,
        "calculated_minimum_remaining_shell_mm": p.shell_nominal - 0.38,
        "acceptance_minimum_mm": 1.4,
        "passed": p.shell_nominal - 0.38 >= 1.4,
        "protected_faces": ["all inner roll-facing shell faces", "module seams 3 mm", "mount seats", "connector bores", "output touch lip"],
    }
    envelope = {
        "body_without_removable_tray_mm": [round(p.body_width_max, 2), round(p.front_ribbon_y + p.front_ribbon_depth_radius, 2), round(p.tower_height, 2)],
        "removable_tray_max_x_mm": round(tray.bounds[1, 0], 2),
        "printer_build_volume_mm": [420, 420, 500],
        "largest_module_bounds_mm": np.round(modules["middle_a"]["ivory"].extents, 2).tolist(),
        "all_individual_parts_fit": all(np.all(mesh.extents <= np.array([420, 420, 500]) + 1e-6) for mesh in manufacturing.values()),
    }
    report = {
        "release_status": "DRAFT-final-approval-required",
        "version": VERSION,
        "parameters": asdict(p),
        "topology": validation,
        "fifo": fifo,
        "wall_thickness": wall_report,
        "envelope": envelope,
        "optimization": {
            "previous_cad_solid_volume_mm3": previous_volume,
            "selected_candidate_solid_volume_mm3": selected_volume,
            "cad_solid_volume_reduction_percent": reduction,
            "target_reduction_percent": 25.0,
            "passed": reduction >= 25.0,
            "note": "CAD solid-volume comparison; exact slicer mass/time remain pending in Anycubic Slicer Next.",
        },
        "slicer": {
            "target": "Anycubic Slicer Next",
            "status": "NOT_RUN-in-current-environment",
            "required_user_checks": ["slot mapping", "thin walls", "organic arch overhangs", "support", "purge", "time", "mass"],
        },
        "physical_tests": {
            "fifo_20_cycles": "NOT_RUN",
            "oval_roll": "NOT_RUN",
            "mounting_proof": "NOT_RUN",
            "texture_wipe": "NOT_RUN",
            "fit_coupon": "NOT_RUN",
        },
    }
    (report_dir / "validation_report_DRAFT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    write_csv(report_dir / "optimization_comparison.csv", [
        {"candidate": "previous_hybrid_v2", "solid_volume_mm3": round(previous_volume, 2), "reduction_percent": 0.0, "status": "reference"},
        {"candidate": "v2.1_thin_freeform_shell", "solid_volume_mm3": round(selected_volume, 2), "reduction_percent": round(reduction, 2), "status": "selected-DRAFT"},
    ])
    manifest = {str(path.relative_to(out_dir)): {"sha256": file_sha256(path), "bytes": path.stat().st_size} for path in sorted(out_dir.rglob("*")) if path.is_file() and path.name != "manifest_DRAFT.json"}
    (out_dir / "manifest_DRAFT.json").write_text(json.dumps({"version": VERSION, "files": manifest}, indent=2, default=json_default), encoding="utf-8")

    print(json.dumps({
        "version": VERSION,
        "quality": quality,
        "manufacturing_files": len(manufacturing),
        "fifo_collisions": fifo["collision_count"],
        "volume_reduction_percent": round(reduction, 2),
        "all_topology_passed": all(v["passed"] for v in validation.values()),
        "output": str(out_dir),
    }, indent=2, default=json_default))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=PROJECT_DIR)
    parser.add_argument("--roll-diameter", type=float, default=120.0)
    parser.add_argument("--roll-width", type=float, default=105.0)
    parser.add_argument("--roll-count", type=int, default=5)
    parser.add_argument("--clearance", type=float, default=4.0)
    parser.add_argument("--quality", choices=["preview", "final"], default="final")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    params = Params(
        roll_diameter=args.roll_diameter,
        roll_width=args.roll_width,
        roll_count=args.roll_count,
        radial_clearance=args.clearance,
        module_pitch=args.roll_diameter + args.clearance,
    )
    build(params, args.output, args.quality)
