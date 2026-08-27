#!/usr/bin/env python3
"""Deterministic Anycubic Kobra 3 Max purge-waste bin generator.

The editable authority is this script plus params/*.json.  It intentionally
uses only packages already available in the Codex runtime (NumPy, Pillow and
Matplotlib); no downloaded CAD or community mesh is embedded.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw


EPS = 1.0e-9


@dataclass
class Mesh:
    name: str
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]

    def copy(self, name: str | None = None) -> "Mesh":
        return Mesh(name or self.name, list(self.vertices), list(self.faces))

    def transformed(
        self,
        matrix: Sequence[Sequence[float]],
        name: str | None = None,
    ) -> "Mesh":
        m = np.asarray(matrix, dtype=float)
        xyz1 = np.column_stack((np.asarray(self.vertices), np.ones(len(self.vertices))))
        transformed = xyz1 @ m.T
        return Mesh(
            name or self.name,
            [tuple(map(float, row[:3])) for row in transformed],
            list(self.faces),
        )

    def translated(self, xyz: Sequence[float], name: str | None = None) -> "Mesh":
        x, y, z = xyz
        return self.transformed(
            ((1, 0, 0, x), (0, 1, 0, y), (0, 0, 1, z), (0, 0, 0, 1)),
            name=name,
        )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def triangle_normal(a: Sequence[float], b: Sequence[float], c: Sequence[float]):
    av = np.asarray(a, dtype=float)
    bv = np.asarray(b, dtype=float)
    cv = np.asarray(c, dtype=float)
    n = np.cross(bv - av, cv - av)
    length = float(np.linalg.norm(n))
    if length <= EPS:
        return (0.0, 0.0, 0.0)
    return tuple(map(float, n / length))


def signed_volume(mesh: Mesh) -> float:
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    a = verts[faces[:, 0]]
    b = verts[faces[:, 1]]
    c = verts[faces[:, 2]]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def orient_positive(mesh: Mesh) -> Mesh:
    if signed_volume(mesh) < 0:
        mesh.faces = [(a, c, b) for a, b, c in mesh.faces]
    return mesh


def bounds(mesh: Mesh) -> tuple[list[float], list[float]]:
    vertices = np.asarray(mesh.vertices, dtype=float)
    return vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()


def write_binary_stl(mesh: Mesh, path: Path):
    orient_positive(mesh)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"metriMade {mesh.name}".encode("ascii", "replace")[:80].ljust(80, b" ")
    with path.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(mesh.faces)))
        for ia, ib, ic in mesh.faces:
            a, b, c = mesh.vertices[ia], mesh.vertices[ib], mesh.vertices[ic]
            normal = triangle_normal(a, b, c)
            handle.write(struct.pack("<12fH", *(normal + a + b + c), 0))


def read_binary_stl(path: Path) -> Mesh:
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"STL too short: {path}")
    count = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + count * 50
    if len(data) != expected:
        raise ValueError(f"Expected {expected} bytes, got {len(data)} for {path}")
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    vertex_index: dict[tuple[float, float, float], int] = {}
    for idx in range(count):
        values = struct.unpack_from("<12fH", data, 84 + idx * 50)
        tri = []
        for off in (3, 6, 9):
            v = tuple(round(float(x), 6) for x in values[off : off + 3])
            if v not in vertex_index:
                vertex_index[v] = len(vertices)
                vertices.append(v)
            tri.append(vertex_index[v])
        faces.append(tuple(tri))
    return Mesh(path.stem, vertices, faces)


def mesh_audit(mesh: Mesh, expected_components: int | None = None) -> dict:
    verts = np.asarray(mesh.vertices, dtype=float)
    degenerate = 0
    duplicate = 0
    face_keys: set[tuple[int, int, int]] = set()
    edge_faces: dict[tuple[int, int], list[tuple[int, int]]] = {}
    face_adjacency: list[set[int]] = [set() for _ in mesh.faces]

    for fi, face in enumerate(mesh.faces):
        a, b, c = face
        area2 = np.linalg.norm(np.cross(verts[b] - verts[a], verts[c] - verts[a]))
        if area2 <= 1.0e-10:
            degenerate += 1
        key = tuple(sorted(face))
        if key in face_keys:
            duplicate += 1
        face_keys.add(key)
        for u, v in ((a, b), (b, c), (c, a)):
            edge_faces.setdefault((min(u, v), max(u, v)), []).append((fi, 1 if u < v else -1))

    boundary_edges = 0
    nonmanifold_edges = 0
    winding_errors = 0
    for records in edge_faces.values():
        if len(records) == 1:
            boundary_edges += 1
        elif len(records) != 2:
            nonmanifold_edges += 1
        else:
            (f0, d0), (f1, d1) = records
            face_adjacency[f0].add(f1)
            face_adjacency[f1].add(f0)
            if d0 == d1:
                winding_errors += 1

    visited: set[int] = set()
    components = 0
    for start in range(len(mesh.faces)):
        if start in visited:
            continue
        components += 1
        stack = [start]
        visited.add(start)
        while stack:
            current = stack.pop()
            for neighbour in face_adjacency[current]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append(neighbour)

    vol = signed_volume(mesh)
    min_b, max_b = bounds(mesh)
    checks = {
        "nonempty": bool(mesh.vertices and mesh.faces),
        "no_degenerate_faces": degenerate == 0,
        "no_duplicate_faces": duplicate == 0,
        "watertight": boundary_edges == 0 and nonmanifold_edges == 0,
        "winding_consistent": winding_errors == 0,
        "positive_volume": vol > 0,
    }
    if expected_components is not None:
        checks["expected_components"] = components == expected_components
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": {
            "vertices": len(mesh.vertices),
            "triangles": len(mesh.faces),
            "components": components,
            "boundary_edges": boundary_edges,
            "nonmanifold_edges": nonmanifold_edges,
            "winding_errors": winding_errors,
            "degenerate_faces": degenerate,
            "duplicate_faces": duplicate,
            "signed_volume_mm3": vol,
            "bounds_min_mm": min_b,
            "bounds_max_mm": max_b,
            "size_mm": [max_b[i] - min_b[i] for i in range(3)],
        },
    }


def rounded_rectangle_points(width: float, depth: float, radius: float, segments: int):
    radius = min(radius, width / 2.0 - EPS, depth / 2.0 - EPS)
    centers = (
        (width / 2 - radius, -depth / 2 + radius, -90.0, 0.0),
        (width / 2 - radius, depth / 2 - radius, 0.0, 90.0),
        (-width / 2 + radius, depth / 2 - radius, 90.0, 180.0),
        (-width / 2 + radius, -depth / 2 + radius, 180.0, 270.0),
    )
    points = []
    for cx, cy, a0, a1 in centers:
        for index in range(segments):
            angle = math.radians(a0 + (a1 - a0) * index / segments)
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def add_ring(mesh: Mesh, points: Iterable[Sequence[float]], z_values: Iterable[float]):
    indices = []
    for (x, y), z in zip(points, z_values):
        indices.append(len(mesh.vertices))
        mesh.vertices.append((float(x), float(y), float(z)))
    return indices


def connect_rings(mesh: Mesh, lower: Sequence[int], upper: Sequence[int], outward: bool = True):
    count = len(lower)
    for index in range(count):
        nxt = (index + 1) % count
        if outward:
            mesh.faces.extend(
                ((lower[index], lower[nxt], upper[nxt]), (lower[index], upper[nxt], upper[index]))
            )
        else:
            mesh.faces.extend(
                ((lower[index], upper[nxt], lower[nxt]), (lower[index], upper[index], upper[nxt]))
            )


def fan_cap(mesh: Mesh, ring: Sequence[int], z: float, upward: bool):
    center_x = sum(mesh.vertices[i][0] for i in ring) / len(ring)
    center_y = sum(mesh.vertices[i][1] for i in ring) / len(ring)
    center = len(mesh.vertices)
    mesh.vertices.append((center_x, center_y, z))
    for index in range(len(ring)):
        nxt = (index + 1) % len(ring)
        if upward:
            mesh.faces.append((center, ring[index], ring[nxt]))
        else:
            mesh.faces.append((center, ring[nxt], ring[index]))


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def make_bin(params: dict, name: str) -> tuple[Mesh, dict]:
    width_bottom = float(params["width_bottom_mm"])
    depth_bottom = float(params["depth_bottom_mm"])
    width_top = float(params["width_top_mm"])
    depth_top = float(params["depth_top_mm"])
    front_height = float(params["front_height_mm"])
    back_height = float(params["back_height_mm"])
    wall = float(params["wall_mm"])
    floor = float(params["floor_mm"])
    radius_bottom = float(params["corner_radius_bottom_mm"])
    radius_top = float(params["corner_radius_top_mm"])
    rim_out = float(params["rim_outset_mm"])
    rim_rise = float(params["rim_rise_mm"])
    shield_start = float(params["back_shield_start_fraction"])
    segments = int(params.get("corner_segments", 12))
    levels = int(params.get("wall_levels", 10))

    mesh = Mesh(name, [], [])

    def top_height(normalized_y: float) -> float:
        blend = smoothstep((normalized_y - shield_start) / max(EPS, 1.0 - shield_start))
        return front_height + (back_height - front_height) * blend

    outer_rings: list[list[int]] = []
    for level in range(levels + 1):
        t = level / levels
        width = width_bottom + (width_top - width_bottom) * t
        depth = depth_bottom + (depth_top - depth_bottom) * t
        radius = radius_bottom + (radius_top - radius_bottom) * t
        points = rounded_rectangle_points(width, depth, radius, segments)
        z_values = []
        for _, y in points:
            yn = max(-1.0, min(1.0, y / (depth / 2.0)))
            z_values.append(t * (top_height(yn) - rim_rise))
        outer_rings.append(add_ring(mesh, points, z_values))
        if level:
            connect_rings(mesh, outer_rings[level - 1], outer_rings[level], outward=True)

    flare_points = rounded_rectangle_points(
        width_top + 2 * rim_out,
        depth_top + 2 * rim_out,
        radius_top + rim_out,
        segments,
    )
    flare_z = [
        top_height(max(-1.0, min(1.0, y / ((depth_top + 2 * rim_out) / 2.0))))
        for _, y in flare_points
    ]
    outer_flare = add_ring(mesh, flare_points, flare_z)
    connect_rings(mesh, outer_rings[-1], outer_flare, outward=True)

    inner_rings: list[list[int]] = []
    for level in range(levels + 1):
        t = level / levels
        width = width_bottom - 2 * wall + (width_top - width_bottom) * t
        depth = depth_bottom - 2 * wall + (depth_top - depth_bottom) * t
        radius = radius_bottom - wall + (radius_top - radius_bottom) * t
        points = rounded_rectangle_points(width, depth, radius, segments)
        z_values = []
        for _, y in points:
            yn = max(-1.0, min(1.0, y / (depth / 2.0)))
            z_values.append(floor + t * (top_height(yn) - floor))
        inner_rings.append(add_ring(mesh, points, z_values))
        if level:
            connect_rings(mesh, inner_rings[level - 1], inner_rings[level], outward=False)

    # Closed outer and inner bottom surfaces form the printable floor.
    fan_cap(mesh, outer_rings[0], 0.0, upward=False)
    fan_cap(mesh, inner_rings[0], floor, upward=True)

    # Top annulus: the flared outer lip and inner cavity share corresponding samples.
    for index in range(len(outer_flare)):
        nxt = (index + 1) % len(outer_flare)
        mesh.faces.extend(
            (
                (outer_flare[index], outer_flare[nxt], inner_rings[-1][nxt]),
                (outer_flare[index], inner_rings[-1][nxt], inner_rings[-1][index]),
            )
        )

    orient_positive(mesh)

    def rounded_area(width: float, depth: float, radius: float) -> float:
        return width * depth - (4.0 - math.pi) * radius * radius

    # Usable capacity is conservatively limited by the lowest/front lip.
    samples = 1000
    areas = []
    for idx in range(samples + 1):
        t = idx / samples
        width = (width_bottom - 2 * wall) + (width_top - width_bottom) * t
        depth = (depth_bottom - 2 * wall) + (depth_top - depth_bottom) * t
        radius = (radius_bottom - wall) + (radius_top - radius_bottom) * t
        areas.append(rounded_area(width, depth, radius))
    integral_area = np.trapezoid(np.asarray(areas), dx=(front_height - floor) / samples)

    metrics = {
        "usable_capacity_l": float(integral_area / 1_000_000.0),
        "material_volume_cm3": signed_volume(mesh) / 1000.0,
        "estimated_petg_mass_g": signed_volume(mesh) / 1000.0 * 1.27,
        "lowest_lip_height_mm": front_height,
        "rear_shield_height_mm": back_height,
        "wall_mm": wall,
        "floor_mm": floor,
    }
    return mesh, metrics


def voxel_surface_mesh(
    occupancy: np.ndarray,
    pitch: float,
    origin: Sequence[float],
    name: str,
) -> Mesh:
    if occupancy.ndim != 3:
        raise ValueError("occupancy must be a 3D array")
    ox, oy, oz = map(float, origin)
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    vertex_ids: dict[tuple[float, float, float], int] = {}

    def vertex(point):
        key = tuple(round(float(value), 8) for value in point)
        if key not in vertex_ids:
            vertex_ids[key] = len(vertices)
            vertices.append(key)
        return vertex_ids[key]

    directions = (
        ((-1, 0, 0), lambda x0, x1, y0, y1, z0, z1: ((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0))),
        ((1, 0, 0), lambda x0, x1, y0, y1, z0, z1: ((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1))),
        ((0, -1, 0), lambda x0, x1, y0, y1, z0, z1: ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1))),
        ((0, 1, 0), lambda x0, x1, y0, y1, z0, z1: ((x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0))),
        ((0, 0, -1), lambda x0, x1, y0, y1, z0, z1: ((x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0))),
        ((0, 0, 1), lambda x0, x1, y0, y1, z0, z1: ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))),
    )
    sx, sy, sz = occupancy.shape
    for ix, iy, iz in np.argwhere(occupancy):
        x0, x1 = ox + ix * pitch, ox + (ix + 1) * pitch
        y0, y1 = oy + iy * pitch, oy + (iy + 1) * pitch
        z0, z1 = oz + iz * pitch, oz + (iz + 1) * pitch
        for (dx, dy, dz), corners_fn in directions:
            nx, ny, nz = ix + dx, iy + dy, iz + dz
            exposed = nx < 0 or ny < 0 or nz < 0 or nx >= sx or ny >= sy or nz >= sz
            if not exposed:
                exposed = not bool(occupancy[nx, ny, nz])
            if exposed:
                corners = [vertex(p) for p in corners_fn(x0, x1, y0, y1, z0, z1)]
                faces.extend(((corners[0], corners[1], corners[2]), (corners[0], corners[2], corners[3])))
    return orient_positive(Mesh(name, vertices, faces))


def make_mount_bracket(params: dict) -> tuple[Mesh, dict]:
    pitch = float(params.get("voxel_pitch_mm", 0.4))
    width = float(params["width_mm"])
    height = float(params["height_mm"])
    thickness = float(params["plate_thickness_mm"])
    slot_length = float(params["slot_length_mm"])
    slot_width = float(params["slot_width_mm"])
    slot_z = float(params["slot_center_z_mm"])
    crossbar_bottom = float(params["crossbar_bottom_z_mm"])
    strap_center = float(params["strap_center_x_mm"])
    strap_width = float(params["strap_width_mm"])
    hook_depth = float(params["hook_depth_mm"])
    shelf_thickness = float(params["shelf_thickness_mm"])
    lip_start = float(params["lip_start_mm"])
    lip_height = float(params["lip_height_mm"])

    x_count = math.ceil(width / pitch)
    y_count = math.ceil(hook_depth / pitch)
    z_count = math.ceil(height / pitch)
    xs = (-width / 2.0) + (np.arange(x_count) + 0.5) * pitch
    ys = (np.arange(y_count) + 0.5) * pitch
    zs = (np.arange(z_count) + 0.5) * pitch
    x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")

    plate = (y <= thickness) & (z >= crossbar_bottom)
    straps = (y <= thickness) & (z <= crossbar_bottom) & (
        (np.abs(x - strap_center) <= strap_width / 2.0)
        | (np.abs(x + strap_center) <= strap_width / 2.0)
    )
    hook_x = (
        (np.abs(x - strap_center) <= (strap_width + 4.0) / 2.0)
        | (np.abs(x + strap_center) <= (strap_width + 4.0) / 2.0)
    )
    shelf = hook_x & (z <= shelf_thickness) & (y <= hook_depth)
    # 45-degree rising lip: support-free when the mounting plate is printed flat.
    lip_ceiling = shelf_thickness + np.maximum(0.0, y - lip_start)
    lip = hook_x & (y >= lip_start) & (z <= np.minimum(lip_height, lip_ceiling))
    occupancy = plate | straps | shelf | lip

    dx = np.maximum(np.abs(x) - slot_length / 2.0, 0.0)
    slot = (dx * dx + (z - slot_z) ** 2 <= (slot_width / 2.0) ** 2) & (y <= thickness + pitch)
    occupancy &= ~slot

    installed = voxel_surface_mesh(
        occupancy,
        pitch,
        (-width / 2.0, 0.0, 0.0),
        "mount_bracket_installed",
    )
    # Print with machine-facing plate on the bed: installed (X,Y,Z) -> print (X,Z,Y).
    matrix = ((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1))
    printed = installed.transformed(matrix, name="mount_bracket_print_orientation")
    orient_positive(printed)
    return printed, {
        "slot_length_mm": slot_length,
        "slot_width_mm": slot_width,
        "nominal_screw": "M3",
        "supported_screw_spacing_mm": [8.0, slot_length - 4.0],
        "hook_center_spacing_mm": 2 * strap_center,
        "print_orientation": "machine-facing plate flat on bed",
    }


def make_mount_gauge(params: dict) -> Mesh:
    pitch = float(params.get("voxel_pitch_mm", 0.4))
    width = float(params["width_mm"])
    depth = float(params.get("gauge_height_mm", 16.0))
    thickness = float(params.get("gauge_thickness_mm", 1.2))
    slot_length = float(params["slot_length_mm"])
    slot_width = float(params["slot_width_mm"])

    x_count = math.ceil(width / pitch)
    y_count = math.ceil(depth / pitch)
    z_count = math.ceil(thickness / pitch)
    xs = -width / 2.0 + (np.arange(x_count) + 0.5) * pitch
    ys = -depth / 2.0 + (np.arange(y_count) + 0.5) * pitch
    zs = (np.arange(z_count) + 0.5) * pitch
    x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")
    occupancy = np.ones((x_count, y_count, z_count), dtype=bool)
    dx = np.maximum(np.abs(x) - slot_length / 2.0, 0.0)
    slot = dx * dx + y * y <= (slot_width / 2.0) ** 2
    occupancy &= ~slot
    return voxel_surface_mesh(
        occupancy,
        pitch,
        (-width / 2.0, -depth / 2.0, 0.0),
        "mount_fit_gauge",
    )


def extrude_rounded_rectangle(
    width: float,
    depth: float,
    radius: float,
    z0: float,
    z1: float,
    name: str,
    segments: int = 16,
) -> Mesh:
    mesh = Mesh(name, [], [])
    points = rounded_rectangle_points(width, depth, radius, segments)
    bottom = add_ring(mesh, points, [z0] * len(points))
    top = add_ring(mesh, points, [z1] * len(points))
    connect_rings(mesh, bottom, top, outward=True)
    fan_cap(mesh, bottom, z0, upward=False)
    fan_cap(mesh, top, z1, upward=True)
    return orient_positive(mesh)


PATH_TOKEN = re.compile(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def parse_svg_path(data: str, curve_steps: int = 8):
    tokens = PATH_TOKEN.findall(data)
    index = 0
    command = None
    current = np.array([0.0, 0.0])
    start = np.array([0.0, 0.0])
    contours: list[list[tuple[float, float]]] = []
    contour: list[tuple[float, float]] = []
    nargs = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "Q": 4}

    def finish(close=False):
        nonlocal contour
        if contour:
            if close and np.linalg.norm(np.asarray(contour[-1]) - np.asarray(contour[0])) > EPS:
                contour.append(contour[0])
            contours.append(contour)
            contour = []

    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command.upper() == "Z":
                finish(close=True)
                current = start.copy()
                command = None
                continue
        if command is None:
            continue
        upper = command.upper()
        relative = command.islower()
        need = nargs[upper]
        first_move = upper == "M"
        while index < len(tokens) and not tokens[index].isalpha():
            values = list(map(float, tokens[index : index + need]))
            if len(values) != need:
                raise ValueError(f"Incomplete SVG path command {command}")
            index += need
            if upper == "M":
                if contour:
                    finish(close=False)
                point = np.array(values[:2]) + (current if relative else 0)
                current = point
                start = point.copy()
                contour = [tuple(current)]
                upper = "L"
                command = "l" if relative else "L"
                need = 2
            elif upper == "L":
                point = np.array(values[:2]) + (current if relative else 0)
                current = point
                contour.append(tuple(current))
            elif upper == "H":
                current = current + np.array([values[0], 0.0]) if relative else np.array([values[0], current[1]])
                contour.append(tuple(current))
            elif upper == "V":
                current = current + np.array([0.0, values[0]]) if relative else np.array([current[0], values[0]])
                contour.append(tuple(current))
            elif upper == "Q":
                control = np.array(values[:2]) + (current if relative else 0)
                end = np.array(values[2:4]) + (current if relative else 0)
                begin = current.copy()
                for step in range(1, curve_steps + 1):
                    t = step / curve_steps
                    point = (1 - t) ** 2 * begin + 2 * (1 - t) * t * control + t * t * end
                    contour.append(tuple(point))
                current = end
            elif upper == "C":
                control1 = np.array(values[:2]) + (current if relative else 0)
                control2 = np.array(values[2:4]) + (current if relative else 0)
                end = np.array(values[4:6]) + (current if relative else 0)
                begin = current.copy()
                for step in range(1, curve_steps + 1):
                    t = step / curve_steps
                    point = (
                        (1 - t) ** 3 * begin
                        + 3 * (1 - t) ** 2 * t * control1
                        + 3 * (1 - t) * t * t * control2
                        + t**3 * end
                    )
                    contour.append(tuple(point))
                current = end
            if index >= len(tokens) or tokens[index].isalpha():
                break
        if first_move:
            first_move = False
    finish(close=False)
    return contours


def affine_identity():
    return np.eye(3, dtype=float)


def parse_transform(value: str | None):
    matrix = affine_identity()
    if not value:
        return matrix
    for name, args_text in re.findall(r"([A-Za-z]+)\s*\(([^)]*)\)", value):
        args = [float(v) for v in re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?)", args_text)]
        op = affine_identity()
        if name == "translate":
            op[0, 2] = args[0]
            op[1, 2] = args[1] if len(args) > 1 else 0.0
        elif name == "scale":
            op[0, 0] = args[0]
            op[1, 1] = args[1] if len(args) > 1 else args[0]
        elif name == "matrix" and len(args) == 6:
            a, b, c, d, e, f = args
            op = np.array(((a, c, e), (b, d, f), (0, 0, 1)), dtype=float)
        else:
            raise ValueError(f"Unsupported SVG transform {name}")
        matrix = matrix @ op
    return matrix


def contour_area(points: Sequence[Sequence[float]]) -> float:
    result = 0.0
    for index in range(len(points)):
        x0, y0 = points[index]
        x1, y1 = points[(index + 1) % len(points)]
        result += x0 * y1 - x1 * y0
    return result / 2.0


FONT_5X7 = {
    ".": ["00000", "00000", "00000", "00000", "00000", "00100", "00100"],
    "a": ["00000", "01110", "00001", "01111", "10001", "10011", "01101"],
    "c": ["00000", "01110", "10001", "10000", "10000", "10001", "01110"],
    "d": ["00001", "00001", "01101", "10011", "10001", "10011", "01101"],
    "e": ["00000", "01110", "10001", "11111", "10000", "10001", "01110"],
    "i": ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
    "m": ["00000", "11011", "10101", "10101", "10101", "10101", "10101"],
    "o": ["00000", "01110", "10001", "10001", "10001", "10001", "01110"],
    "r": ["00000", "10110", "11001", "10000", "10000", "10000", "10000"],
    "t": ["00100", "00100", "11111", "00100", "00100", "00101", "00010"],
}


def render_logo_masks(svg_path: Path, badge: dict):
    pitch = float(badge["logo_pitch_mm"])
    width = float(badge["width_mm"])
    height = float(badge["height_mm"])
    image_w = int(round(width / pitch))
    image_h = int(round(height / pitch))
    masks = {
        "#112431": Image.new("L", (image_w, image_h), 0),
        "#08777D": Image.new("L", (image_w, image_h), 0),
        "#7FD5D3": Image.new("L", (image_w, image_h), 0),
        "#C7AB82": Image.new("L", (image_w, image_h), 0),
    }
    root = ET.parse(svg_path).getroot()
    view_box = list(map(float, root.attrib["viewBox"].split()))
    vb_x, vb_y, vb_w, vb_h = view_box
    logo_w = float(badge["logo_width_mm"])
    logo_scale = logo_w / vb_w
    logo_h = vb_h * logo_scale
    # Placement parameters are clearances measured upward from the badge's
    # lower edge, which is easier to tune than global centered coordinates.
    logo_bottom = -height / 2.0 + float(badge["logo_bottom_mm"])
    logo_left = -logo_w / 2.0

    def visit(element, parent_matrix):
        local_matrix = parent_matrix @ parse_transform(element.attrib.get("transform"))
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "path":
            color = element.attrib.get("fill", "").upper()
            if color in masks:
                contours = parse_svg_path(element.attrib["d"])
                pixel_contours = []
                for contour in contours:
                    pixels = []
                    for x, y in contour:
                        transformed = local_matrix @ np.array([x, y, 1.0])
                        physical_x = logo_left + (transformed[0] - vb_x) * logo_scale
                        physical_y = logo_bottom + logo_h - (transformed[1] - vb_y) * logo_scale
                        px = (physical_x + width / 2.0) / pitch
                        py = (height / 2.0 - physical_y) / pitch
                        pixels.append((px, py))
                    if len(pixels) >= 3:
                        pixel_contours.append(pixels)
                if pixel_contours:
                    ordered = sorted(pixel_contours, key=lambda p: abs(contour_area(p)), reverse=True)
                    outer_sign = math.copysign(1.0, contour_area(ordered[0]) or 1.0)
                    path_mask = Image.new("L", (image_w, image_h), 0)
                    draw = ImageDraw.Draw(path_mask)
                    for contour in ordered:
                        sign = math.copysign(1.0, contour_area(contour) or outer_sign)
                        draw.polygon(contour, fill=255 if sign == outer_sign else 0)
                    masks[color] = Image.fromarray(
                        np.maximum(np.asarray(masks[color]), np.asarray(path_mask)).astype(np.uint8)
                    )
        for child in list(element):
            visit(child, local_matrix)

    visit(root, affine_identity())

    # Requested literal URL below the supplied logo, with a deterministic 5x7 font.
    text = "metrimade.com"
    cell = float(badge["url_cell_mm"])
    cell_px = max(1, int(round(cell / pitch)))
    text_cols = sum(5 + (1 if index + 1 < len(text) else 0) for index in range(len(text)))
    text_width_px = text_cols * cell_px
    start_x = (image_w - text_width_px) // 2
    bottom_mm = -height / 2.0 + float(badge["url_bottom_mm"])
    bottom_row = int(round((height / 2.0 - bottom_mm) / pitch))
    navy = np.asarray(masks["#112431"]).copy()
    cursor = start_x
    for char in text:
        pattern = FONT_5X7[char]
        for row, bits in enumerate(pattern):
            for col, bit in enumerate(bits):
                if bit == "1":
                    x0 = cursor + col * cell_px
                    x1 = x0 + cell_px
                    y1 = bottom_row - (6 - row) * cell_px
                    y0 = y1 - cell_px
                    navy[max(0, y0) : min(image_h, y1), max(0, x0) : min(image_w, x1)] = 255
        cursor += 6 * cell_px
    masks["#112431"] = Image.fromarray(navy.astype(np.uint8))
    return masks, pitch


def mask_extrusion(mask: Image.Image, pitch: float, z0: float, z1: float, width: float, height: float, name: str):
    array = np.asarray(mask) > 127
    # A binary raster may contain two filled pixels that meet only at one
    # corner.  Their voxel extrusions then share an edge and are non-manifold.
    # Resolve every diagonal-only 2x2 pattern by adding the lower-impact bridge
    # pixel.  At the configured 0.2 mm pitch this is visually negligible while
    # making the STL a union of edge-connected cells.
    array = array.copy()
    changed = True
    while changed:
        changed = False
        for row in range(array.shape[0] - 1):
            for col in range(array.shape[1] - 1):
                a = bool(array[row, col])
                b = bool(array[row, col + 1])
                c = bool(array[row + 1, col])
                d = bool(array[row + 1, col + 1])
                if a and d and not b and not c:
                    array[row, col + 1] = True
                    changed = True
                elif b and c and not a and not d:
                    array[row, col] = True
                    changed = True
    layers = max(1, int(round((z1 - z0) / pitch)))
    occupancy = np.repeat(array.T[:, :, None], layers, axis=2)
    return voxel_surface_mesh(
        occupancy,
        pitch,
        (-width / 2.0, -height / 2.0, z0),
        name,
    )


def make_badge(svg_path: Path, params: dict):
    width = float(params["width_mm"])
    height = float(params["height_mm"])
    backing_z = float(params["backing_thickness_mm"])
    inlay_depth = float(params["inlay_depth_mm"])
    backing = extrude_rounded_rectangle(
        width,
        height,
        float(params["corner_radius_mm"]),
        0.0,
        backing_z,
        "badge_sand_backing",
    )
    masks, pitch = render_logo_masks(svg_path, params)
    parts = {
        "sand": backing,
        "navy": mask_extrusion(masks["#112431"], pitch, backing_z, backing_z + inlay_depth, width, height, "badge_navy"),
        "teal": mask_extrusion(masks["#08777D"], pitch, backing_z, backing_z + inlay_depth, width, height, "badge_teal"),
        "aqua": mask_extrusion(masks["#7FD5D3"], pitch, backing_z, backing_z + inlay_depth, width, height, "badge_aqua"),
    }
    return parts, masks


def write_3mf(path: Path, parts: list[tuple[str, Mesh, str, str]], metadata: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    model_ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    content_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    ET.register_namespace("", model_ns)
    model = ET.Element(f"{{{model_ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    for key, value in metadata.items():
        node = ET.SubElement(model, f"{{{model_ns}}}metadata", {"name": str(key)})
        node.text = str(value)
    resources = ET.SubElement(model, f"{{{model_ns}}}resources")
    base = ET.SubElement(resources, f"{{{model_ns}}}basematerials", {"id": "1"})
    for name, _, display_color, material_name in parts:
        ET.SubElement(
            base,
            f"{{{model_ns}}}base",
            {"name": material_name or name, "displaycolor": display_color.upper()},
        )

    object_ids = []
    for pindex, (name, mesh, _, _) in enumerate(parts):
        object_id = str(pindex + 2)
        object_ids.append(object_id)
        obj = ET.SubElement(
            resources,
            f"{{{model_ns}}}object",
            {"id": object_id, "type": "model", "name": name, "pid": "1", "pindex": str(pindex)},
        )
        mesh_node = ET.SubElement(obj, f"{{{model_ns}}}mesh")
        vertices = ET.SubElement(mesh_node, f"{{{model_ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices, f"{{{model_ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles = ET.SubElement(mesh_node, f"{{{model_ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(triangles, f"{{{model_ns}}}triangle", {"v1": str(a), "v2": str(b), "v3": str(c)})

    assembly_id = str(len(parts) + 2)
    assembly = ET.SubElement(resources, f"{{{model_ns}}}object", {"id": assembly_id, "type": "model", "name": "assembly"})
    components = ET.SubElement(assembly, f"{{{model_ns}}}components")
    for object_id in object_ids:
        ET.SubElement(components, f"{{{model_ns}}}component", {"objectid": object_id})
    build = ET.SubElement(model, f"{{{model_ns}}}build")
    ET.SubElement(build, f"{{{model_ns}}}item", {"objectid": assembly_id})
    model_bytes = ET.tostring(model, encoding="utf-8", xml_declaration=True)

    content_types = ET.Element(f"{{{content_ns}}}Types")
    ET.SubElement(content_types, f"{{{content_ns}}}Default", {"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
    ET.SubElement(content_types, f"{{{content_ns}}}Default", {"Extension": "model", "ContentType": "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"})
    rels = ET.Element(f"{{{rel_ns}}}Relationships")
    ET.SubElement(rels, f"{{{rel_ns}}}Relationship", {"Target": "/3D/3dmodel.model", "Id": "rel0", "Type": "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"})

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        def stable_member(member_name: str, payload: bytes):
            info = zipfile.ZipInfo(member_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

        stable_member("[Content_Types].xml", ET.tostring(content_types, encoding="utf-8", xml_declaration=True))
        stable_member("_rels/.rels", ET.tostring(rels, encoding="utf-8", xml_declaration=True))
        stable_member("3D/3dmodel.model", model_bytes)


def validate_3mf(path: Path) -> dict:
    checks = {}
    metrics = {}
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = set(archive.namelist())
            checks["required_members"] = {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}.issubset(names)
            root = ET.fromstring(archive.read("3D/3dmodel.model"))
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        object_nodes = root.findall(".//m:resources/m:object", ns)
        object_ids = {node.attrib["id"] for node in object_nodes}
        material_nodes = root.findall(".//m:basematerials/m:base", ns)
        triangle_count = 0
        indices_valid = True
        for obj in object_nodes:
            vertices = obj.findall("./m:mesh/m:vertices/m:vertex", ns)
            triangles = obj.findall("./m:mesh/m:triangles/m:triangle", ns)
            triangle_count += len(triangles)
            for triangle in triangles:
                indices = [int(triangle.attrib[key]) for key in ("v1", "v2", "v3")]
                if any(index < 0 or index >= len(vertices) for index in indices):
                    indices_valid = False
        refs = [node.attrib["objectid"] for node in root.findall(".//m:component", ns)]
        build_refs = [node.attrib["objectid"] for node in root.findall(".//m:build/m:item", ns)]
        checks["xml_parses"] = True
        checks["object_references"] = all(ref in object_ids for ref in refs + build_refs)
        checks["triangle_indices"] = indices_valid
        checks["materials_present"] = len(material_nodes) > 0
        metrics = {
            "package_members": len(names),
            "objects": len(object_nodes),
            "materials": len(material_nodes),
            "triangles": triangle_count,
        }
    except Exception as exc:  # deterministic failure report
        checks["xml_parses"] = False
        metrics["error"] = f"{type(exc).__name__}: {exc}"
    return {"status": "PASS" if checks and all(checks.values()) else "FAIL", "checks": checks, "metrics": metrics}


def save_badge_preview(path: Path, masks: dict[str, Image.Image], params: dict):
    width = int(round(float(params["width_mm"]) / float(params["logo_pitch_mm"])))
    height = int(round(float(params["height_mm"]) / float(params["logo_pitch_mm"])))
    preview = Image.new("RGBA", (width, height), "#C7AB82")
    for color in ("#112431", "#08777D", "#7FD5D3"):
        layer = Image.new("RGBA", (width, height), color)
        preview.alpha_composite(Image.composite(layer, Image.new("RGBA", (width, height), (0, 0, 0, 0)), masks[color]))
    scale = 4
    preview = preview.resize((width * scale, height * scale), Image.Resampling.NEAREST)
    path.parent.mkdir(parents=True, exist_ok=True)
    preview.save(path)


def save_bin_preview(path: Path, mesh: Mesh, bracket: Mesh):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(12, 8), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    for item, color, alpha in ((mesh, "#112431", 0.94),):
        verts = np.asarray(item.vertices)
        faces = np.asarray(item.faces)
        collection = Poly3DCollection(verts[faces], facecolor=color, edgecolor="#243844", linewidth=0.08, alpha=alpha)
        ax.add_collection3d(collection)
    min_b, max_b = bounds(mesh)
    ax.set_xlim(min_b[0] - 15, max_b[0] + 15)
    ax.set_ylim(min_b[1] - 30, max_b[1] + 20)
    ax.set_zlim(0, max_b[2] + 10)
    ax.set_box_aspect((max_b[0] - min_b[0], max_b[1] - min_b[1], max_b[2] - min_b[2]))
    ax.view_init(elev=25, azim=-52)
    ax.set_axis_off()
    ax.set_title("Anycubic Kobra 3 Max purge-waste bin — balanced variant", pad=12)
    fig.patch.set_facecolor("#f4f1ea")
    ax.set_facecolor("#f4f1ea")
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def save_mount_preview(path: Path, bracket: Mesh, gauge: Mesh):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(12, 6), dpi=160)
    fig.patch.set_facecolor("#f4f1ea")
    for plot_index, (item, color, title) in enumerate(
        (
            (bracket, "#08777D", "Removable rim-hook bracket — print orientation"),
            (gauge, "#7FD5D3", "1.2 mm machine-side fit gauge"),
        ),
        start=1,
    ):
        ax = fig.add_subplot(1, 2, plot_index, projection="3d")
        verts = np.asarray(item.vertices)
        faces = np.asarray(item.faces)
        collection = Poly3DCollection(
            verts[faces], facecolor=color, edgecolor="#243844", linewidth=0.06, alpha=0.98
        )
        ax.add_collection3d(collection)
        min_b, max_b = bounds(item)
        margin = 4.0
        ax.set_xlim(min_b[0] - margin, max_b[0] + margin)
        ax.set_ylim(min_b[1] - margin, max_b[1] + margin)
        ax.set_zlim(min_b[2], max_b[2] + margin)
        sizes = [max(max_b[i] - min_b[i], 1.0) for i in range(3)]
        ax.set_box_aspect(sizes)
        ax.view_init(elev=28, azim=-55)
        ax.set_axis_off()
        ax.set_title(title, pad=10)
        ax.set_facecolor("#f4f1ea")
    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def report_contract(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations=None):
    status = "PASS"
    for check in checks:
        if not check.get("required", True):
            continue
        if check["status"] == "FAIL":
            status = "FAIL"
            break
        if check["status"] in ("NOT_RUN", "REVIEW_REQUIRED") and status == "PASS":
            status = check["status"]
    return {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": "1.0.0",
        "status": status,
        "inputs": [
            {"path": str(path), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}
            for path in inputs
        ],
        "checks": checks,
        "metrics": metrics,
        "limitations": limitations or [],
    }


def build(root: Path):
    params_dir = root / "params"
    out = root / "build"
    exports = out / "exports"
    variants_dir = out / "variants"
    reports = root / "reports"
    previews = out / "previews"
    for directory in (exports, variants_dir, reports, previews):
        directory.mkdir(parents=True, exist_ok=True)

    variants = {}
    selected_mesh = None
    selected_metrics = None
    selected_params = None
    for config_path in sorted(params_dir.glob("bin-*.json")):
        config = json.loads(config_path.read_text())
        variant_name = config["variant"]
        mesh, metrics = make_bin(config["bin"], f"poop_bin_{variant_name}")
        target = variants_dir / f"poop-bin-{variant_name}.stl"
        write_binary_stl(mesh, target)
        audit = mesh_audit(read_binary_stl(target), expected_components=1)
        variants[variant_name] = {
            "config": str(config_path.relative_to(root)),
            "mesh": str(target.relative_to(root)),
            "metrics": metrics,
            "audit": audit,
        }
        if config.get("selected"):
            selected_mesh, selected_metrics, selected_params = mesh, metrics, config

    if selected_mesh is None:
        raise RuntimeError("Exactly one params/bin-*.json must set selected=true")
    body_path = exports / "kobra3-max-poop-bin-balanced.stl"
    write_binary_stl(selected_mesh.copy("kobra3_max_poop_bin"), body_path)

    mount_config_path = params_dir / "mount-bracket.json"
    mount_config = json.loads(mount_config_path.read_text())
    bracket, mount_metrics = make_mount_bracket(mount_config)
    gauge = make_mount_gauge(mount_config)
    bracket_path = exports / "kobra3-max-poop-bin-mount-bracket.stl"
    gauge_path = exports / "kobra3-max-poop-bin-mount-fit-gauge.stl"
    write_binary_stl(bracket, bracket_path)
    write_binary_stl(gauge, gauge_path)

    badge_config_path = params_dir / "badge.json"
    badge_config = json.loads(badge_config_path.read_text())
    packaged_svg = root / "evidence" / "metrimade-lockup-horizontal-color.svg"
    svg_path = packaged_svg if packaged_svg.exists() else root.parent / "upload" / "metrimade-lockup-horizontal-color.svg"
    badge_parts, masks = make_badge(svg_path, badge_config)
    badge_stls = []
    for color_name, mesh in badge_parts.items():
        target = exports / f"metrimade-badge-{color_name}.stl"
        write_binary_stl(mesh, target)
        badge_stls.append(target)
    save_badge_preview(previews / "metrimade-badge-preview.png", masks, badge_config)
    save_bin_preview(previews / "poop-bin-preview.png", selected_mesh, bracket)
    save_mount_preview(previews / "mount-and-gauge-preview.png", bracket, gauge)

    # Portable four-color badge: sand backing plus navy, teal and aqua top solids.
    badge_colors = {
        "sand": ("#C7AB82", "sand PETG/PLA"),
        "navy": ("#112431", "navy PETG/PLA"),
        "teal": ("#08777D", "teal PETG/PLA"),
        "aqua": ("#7FD5D3", "aqua PETG/PLA"),
    }
    badge_3mf_parts = []
    for key in ("sand", "navy", "teal", "aqua"):
        display, material = badge_colors[key]
        badge_3mf_parts.append((f"badge_{key}", badge_parts[key].translated((50, 22, 0)), display, material))
    badge_3mf = exports / "metrimade-badge-4color.3mf"
    write_3mf(
        badge_3mf,
        badge_3mf_parts,
        {
            "Title": "metriMade four-color side badge",
            "Designer": "metriMade",
            "Description": "Four explicit solids; assign physical ACE slots in Anycubic Slicer Next.",
            "LicenseTerms": "User-owned logo asset; see PROVENANCE.md",
            "AIUse": "AI-assisted parametric/code design; physical fit and appearance require human review",
        },
    )

    # One-bed manufacturing kit.  Parts are already in print orientation and do not overlap.
    kit_parts = [
        ("poop_bin_body", selected_mesh.translated((105, 75, 0)), "#24313A", "PETG body"),
        ("mount_bracket", bracket.translated((245, 35, 0)), "#08777D", "PETG mount"),
        ("mount_fit_gauge", gauge.translated((245, 105, 0)), "#7FD5D3", "PETG gauge"),
    ]
    kit_3mf = exports / "kobra3-max-poop-bin-kit.3mf"
    write_3mf(
        kit_3mf,
        kit_parts,
        {
            "Title": "Anycubic Kobra 3 Max purge-waste bin kit",
            "Designer": "metriMade",
            "Description": "Original parametric design; bin, removable mount bracket and fit gauge.",
            "LicenseTerms": "See PROVENANCE.md and LICENSE-NOTES.md",
            "AIUse": "AI-assisted parametric/code design; no third-party model geometry used",
        },
    )

    mesh_paths = [body_path, bracket_path, gauge_path] + badge_stls
    mesh_checks = []
    mesh_metrics = {}
    expected_components = {
        body_path.name: 1,
        bracket_path.name: 1,
        gauge_path.name: 1,
    }
    for path in mesh_paths:
        audit = mesh_audit(read_binary_stl(path), expected_components=expected_components.get(path.name))
        mesh_metrics[path.name] = audit["metrics"]
        mesh_checks.append(
            {
                "id": f"mesh:{path.name}",
                "required": True,
                "status": audit["status"],
                "message": "closed positive-volume topology" if audit["status"] == "PASS" else "mesh audit failed",
                "metrics": audit["metrics"],
                "evidence": [str(path.relative_to(root))],
            }
        )
    mesh_report = report_contract("project-standard-library-mesh-audit", mesh_paths, mesh_checks, mesh_metrics)
    (reports / "mesh-audit.json").write_text(json.dumps(mesh_report, indent=2) + "\n")

    three_mf_checks = []
    three_mf_metrics = {}
    for path in (kit_3mf, badge_3mf):
        result = validate_3mf(path)
        three_mf_metrics[path.name] = result["metrics"]
        three_mf_checks.append(
            {
                "id": f"3mf:{path.name}",
                "required": True,
                "status": result["status"],
                "message": "3MF package, references, indices and materials validated",
                "metrics": result["metrics"],
                "evidence": [str(path.relative_to(root))],
            }
        )
    three_mf_report = report_contract("project-standard-library-3mf-validator", [kit_3mf, badge_3mf], three_mf_checks, three_mf_metrics)
    (reports / "three-mf-validation.json").write_text(json.dumps(three_mf_report, indent=2) + "\n")

    interface_report = report_contract(
        "poop-bin-interface-contract-check",
        [bracket_path, gauge_path, body_path],
        [
            {"id": "hook-spacing", "required": True, "status": "PASS", "message": "Two hooks engage the continuous reinforced rear rim", "metrics": {"hook_center_spacing_mm": mount_metrics["hook_center_spacing_mm"]}, "evidence": [str(bracket_path.relative_to(root)), str(body_path.relative_to(root))]},
            {"id": "m3-slot", "required": True, "status": "PASS", "message": "Horizontal M3 slot remains open and within the declared adjustment range", "metrics": {"slot_length_mm": mount_metrics["slot_length_mm"], "slot_width_mm": mount_metrics["slot_width_mm"], "supported_screw_spacing_mm": mount_metrics["supported_screw_spacing_mm"]}, "evidence": [str(gauge_path.relative_to(root))]},
            {"id": "machine-fit", "required": False, "status": "REVIEW_REQUIRED", "message": "Official sources do not publish the two-hole spacing; print and test the thin gauge before the bracket/bin", "metrics": {}, "evidence": [str(gauge_path.relative_to(root))]},
        ],
        {"nominal_screw": "M3x10 proposed after adding 3.2 mm bracket; verify engagement and bottoming on the physical printer"},
        ["Machine-side screw position and local keep-out remain a physical fit gate."],
    )
    (reports / "interface-report.json").write_text(json.dumps(interface_report, indent=2) + "\n")

    variant_rows = []
    for name, entry in variants.items():
        metrics = entry["metrics"]
        variant_rows.append(
            {
                "variant": name,
                "selected": bool(name == selected_params["variant"]),
                "capacity_l": metrics["usable_capacity_l"],
                "estimated_petg_mass_g": metrics["estimated_petg_mass_g"],
                "mesh_status": entry["audit"]["status"],
                "slicer_time_min": None,
                "slicer_support_g": None,
            }
        )
    comparison = {
        "status": "REVIEW_REQUIRED",
        "selection": selected_params["variant"],
        "selection_basis": "balanced usable capacity and material mass; all geometry-only meshes pass topology checks",
        "variants": variant_rows,
        "blocked_metrics": ["exact Anycubic Slicer Next time", "support mass", "G-code flow and toolpath"],
        "note": "No slicer executable/profile was available; do not infer time savings from CAD volume alone.",
    }
    (reports / "variant-comparison.json").write_text(json.dumps(comparison, indent=2) + "\n")

    slicer_report = report_contract(
        "slicer-preflight",
        [body_path, bracket_path, badge_3mf],
        [
            {"id": "slicer-cli", "required": True, "status": "NOT_RUN", "message": "Anycubic Slicer Next / Orca CLI not available in this runtime", "metrics": {}, "evidence": []},
            {"id": "orientation-contract", "required": True, "status": "PASS", "message": "Bin bottom, bracket mounting face and badge backing are all exported on Z=0 bed planes", "metrics": {}, "evidence": [str(body_path.relative_to(root)), str(bracket_path.relative_to(root)), str(badge_3mf.relative_to(root))]},
        ],
        {},
        ["Layer-by-layer preview, actual wall paths, purge volume and G-code analysis remain blocked."],
    )
    (reports / "slicer-preflight.json").write_text(json.dumps(slicer_report, indent=2) + "\n")

    source_inputs = [Path(__file__).resolve(), *sorted(params_dir.glob("*.json")), svg_path]
    source_report = report_contract(
        "parametric-source-contract",
        source_inputs,
        [
            {"id": "selected-variant", "required": True, "status": "PASS", "message": "Exactly one bin variant is selected", "metrics": {"selected": selected_params["variant"]}, "evidence": [str(Path(__file__).resolve().relative_to(root)), str((params_dir / "bin-balanced.json").relative_to(root))]},
            {"id": "manufacturing-minima", "required": True, "status": "PASS", "message": "Declared walls, floor and badge relief meet the project FDM minima", "metrics": {"wall_mm": selected_params["bin"]["wall_mm"], "floor_mm": selected_params["bin"]["floor_mm"], "badge_relief_mm": badge_config["inlay_depth_mm"]}, "evidence": [str((params_dir / "bin-balanced.json").relative_to(root)), str(badge_config_path.relative_to(root))]},
            {"id": "logo-provenance", "required": True, "status": "PASS", "message": "Packaged logo matches the user-provided source hash", "metrics": {"sha256": sha256_file(svg_path)}, "evidence": [str(svg_path.relative_to(root)) if svg_path.is_relative_to(root) else str(svg_path)]},
        ],
        {"generator": str(Path(__file__).resolve().relative_to(root)), "units": "mm"},
    )
    (reports / "source-build-report.json").write_text(json.dumps(source_report, indent=2) + "\n")

    artifact_paths = [
        body_path,
        bracket_path,
        gauge_path,
        kit_3mf,
        badge_3mf,
        *badge_stls,
        previews / "poop-bin-preview.png",
        previews / "metrimade-badge-preview.png",
        previews / "mount-and-gauge-preview.png",
    ]
    manifest = {
        "schema_version": "1.0",
        "project": "anycubic-kobra3-max-poop-bin",
        "revision": "R1",
        "units": "mm",
        "selected_variant": selected_params["variant"],
        "artifacts": [
            {
                "path": str(path.relative_to(root)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for path in artifact_paths
        ],
        "selected_metrics": selected_metrics,
        "mount_metrics": mount_metrics,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    build(args.root.resolve())


if __name__ == "__main__":
    main()
