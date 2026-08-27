#!/usr/bin/env python3
"""Generate the R5 Anycubic Kobra 3 Max smooth open-bottom purge catcher.

The editable authority is this script plus params/*.json.  No community CAD
or downloaded mesh is embedded.  The generated 3MF files intentionally use a
minimal core structure: one direct mesh object and one direct build item, with
no component hierarchy or slicer-private project metadata.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import re
import struct
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import Delaunay


EPS = 1.0e-9
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
XML_NS = "http://www.w3.org/XML/1998/namespace"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


@dataclass
class Mesh:
    name: str
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]

    def translated(self, xyz: Sequence[float], name: str | None = None) -> "Mesh":
        dx, dy, dz = map(float, xyz)
        return Mesh(
            name or self.name,
            [(x + dx, y + dy, z + dz) for x, y, z in self.vertices],
            list(self.faces),
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def triangle_normal(a: Sequence[float], b: Sequence[float], c: Sequence[float]):
    av, bv, cv = np.asarray(a), np.asarray(b), np.asarray(c)
    normal = np.cross(bv - av, cv - av)
    length = float(np.linalg.norm(normal))
    if length <= EPS:
        return (0.0, 0.0, 0.0)
    return tuple(map(float, normal / length))


def signed_volume(mesh: Mesh) -> float:
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if not len(faces):
        return 0.0
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def orient_positive(mesh: Mesh) -> Mesh:
    if signed_volume(mesh) < 0:
        mesh.faces = [(a, c, b) for a, b, c in mesh.faces]
    return mesh


def mesh_bounds(mesh: Mesh):
    vertices = np.asarray(mesh.vertices, dtype=float)
    return vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()


def write_binary_stl(mesh: Mesh, path: Path):
    orient_positive(mesh)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"metriMade R5 {mesh.name}".encode("ascii", "replace")[:80].ljust(80, b" ")
    with path.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(mesh.faces)))
        for ia, ib, ic in mesh.faces:
            a, b, c = mesh.vertices[ia], mesh.vertices[ib], mesh.vertices[ic]
            handle.write(struct.pack("<12fH", *(triangle_normal(a, b, c) + a + b + c), 0))


def mesh_audit(mesh: Mesh) -> dict:
    verts = np.asarray(mesh.vertices, dtype=float)
    face_keys: set[tuple[int, int, int]] = set()
    edge_faces: dict[tuple[int, int], list[tuple[int, int]]] = {}
    adjacency: list[set[int]] = [set() for _ in mesh.faces]
    degenerate = duplicate = 0
    for fi, (a, b, c) in enumerate(mesh.faces):
        if len({a, b, c}) < 3 or np.linalg.norm(np.cross(verts[b] - verts[a], verts[c] - verts[a])) <= EPS:
            degenerate += 1
        key = tuple(sorted((a, b, c)))
        duplicate += int(key in face_keys)
        face_keys.add(key)
        for u, v in ((a, b), (b, c), (c, a)):
            edge_faces.setdefault((min(u, v), max(u, v)), []).append((fi, 1 if u < v else -1))
    boundary = nonmanifold = winding = 0
    for records in edge_faces.values():
        if len(records) == 1:
            boundary += 1
        elif len(records) != 2:
            nonmanifold += 1
        else:
            (f0, d0), (f1, d1) = records
            adjacency[f0].add(f1)
            adjacency[f1].add(f0)
            winding += int(d0 == d1)
    visited: set[int] = set()
    components = 0
    for start in range(len(mesh.faces)):
        if start in visited:
            continue
        components += 1
        stack = [start]
        visited.add(start)
        while stack:
            for neighbour in adjacency[stack.pop()]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append(neighbour)
    volume = signed_volume(mesh)
    checks = {
        "nonempty": bool(mesh.vertices and mesh.faces),
        "no_degenerate_faces": degenerate == 0,
        "no_duplicate_faces": duplicate == 0,
        "watertight": boundary == 0 and nonmanifold == 0,
        "winding_consistent": winding == 0,
        "positive_volume": volume > 0,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": {
            "vertices": len(mesh.vertices),
            "triangles": len(mesh.faces),
            "components": components,
            "boundary_edges": boundary,
            "nonmanifold_edges": nonmanifold,
            "winding_errors": winding,
            "degenerate_faces": degenerate,
            "duplicate_faces": duplicate,
            "signed_volume_mm3": volume,
            "bounds_min_mm": mesh_bounds(mesh)[0],
            "bounds_max_mm": mesh_bounds(mesh)[1],
        },
    }


def voxel_surface_mesh(occupancy: np.ndarray, pitch: float, origin, name: str) -> Mesh:
    ox, oy, oz = map(float, origin)
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    ids: dict[tuple[float, float, float], int] = {}

    def vertex(point):
        key = tuple(round(float(value), 8) for value in point)
        if key not in ids:
            ids[key] = len(vertices)
            vertices.append(key)
        return ids[key]

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


def regularize_voxel_edge_contacts(occupancy: np.ndarray, allowed: np.ndarray):
    """Fill ambiguous 2x2 diagonal contacts that would create non-manifold edges."""
    added_before = int(np.count_nonzero(occupancy))
    for _ in range(6):
        count_before_pass = int(np.count_nonzero(occupancy))
        orientations = (
            ((slice(None, -1), slice(None, -1), slice(None)), (slice(1, None), slice(None, -1), slice(None)), (slice(None, -1), slice(1, None), slice(None)), (slice(1, None), slice(1, None), slice(None))),
            ((slice(None, -1), slice(None), slice(None, -1)), (slice(1, None), slice(None), slice(None, -1)), (slice(None, -1), slice(None), slice(1, None)), (slice(1, None), slice(None), slice(1, None))),
            ((slice(None), slice(None, -1), slice(None, -1)), (slice(None), slice(1, None), slice(None, -1)), (slice(None), slice(None, -1), slice(1, None)), (slice(None), slice(1, None), slice(1, None))),
        )
        for sa, sb, sc, sd in orientations:
            a, b, c, d = occupancy[sa], occupancy[sb], occupancy[sc], occupancy[sd]
            diag_ad = a & d & ~b & ~c
            diag_bc = b & c & ~a & ~d
            occupancy[sb] |= diag_ad & allowed[sb]
            occupancy[sc] |= diag_ad & allowed[sc]
            occupancy[sa] |= diag_bc & allowed[sa]
            occupancy[sd] |= diag_bc & allowed[sd]
        if int(np.count_nonzero(occupancy)) == count_before_pass:
            break
    return int(np.count_nonzero(occupancy)) - added_before


def honeycomb_surface_mask(u_coords: np.ndarray, z_coords: np.ndarray, radius: float, rib_width: float, pitch: float):
    """Rasterize a regular hex rib network in physical surface coordinates."""
    image = Image.new("L", (len(u_coords), len(z_coords)), 0)
    draw = ImageDraw.Draw(image)
    u_min, u_max = float(u_coords[0] - pitch / 2.0), float(u_coords[-1] + pitch / 2.0)
    z_min, z_max = float(z_coords[0] - pitch / 2.0), float(z_coords[-1] + pitch / 2.0)
    step_u, step_z = 1.5 * radius, math.sqrt(3.0) * radius
    line_width = max(1, int(round(rib_width / pitch)))
    column = 0
    center_u = u_min - 2.0 * radius
    while center_u <= u_max + 2.0 * radius:
        center_z = z_min - 2.0 * radius + (0.5 * step_z if column % 2 else 0.0)
        while center_z <= z_max + 2.0 * radius:
            vertices = []
            for angle_deg in (0, 60, 120, 180, 240, 300):
                angle = math.radians(angle_deg)
                u = center_u + radius * math.cos(angle)
                z = center_z + radius * math.sin(angle)
                vertices.append(((u - u_min) / pitch, (z_max - z) / pitch))
            draw.line(vertices + [vertices[0]], fill=255, width=line_width, joint="curve")
            center_z += step_z
        column += 1
        center_u += step_u
    # Image rows run from high to low z; the returned array is indexed [u, z].
    return (np.asarray(image) > 0)[::-1, :].T


def sample_logo_mask(mask: np.ndarray, u_coords: np.ndarray, z_coords: np.ndarray, params: dict, center_u: float, mirror_u=False):
    """Sample a full-viewBox logo raster onto a physical face coordinate grid."""
    pitch = float(params["logo_pitch_mm"])
    panel_w = float(params["logo_width_mm"])
    panel_h = mask.shape[0] * pitch
    center_u = float(center_u)
    bottom_z = float(params["logo_panel_bottom_z_mm"])
    sample_u = -u_coords if mirror_u else u_coords
    cols = np.floor((sample_u - center_u + panel_w / 2.0) / pitch).astype(int)
    rows = np.floor((bottom_z + panel_h - z_coords) / pitch).astype(int)
    valid_u = (cols >= 0) & (cols < mask.shape[1])
    valid_z = (rows >= 0) & (rows < mask.shape[0])
    sampled = np.zeros((len(u_coords), len(z_coords)), dtype=bool)
    if np.any(valid_u) and np.any(valid_z):
        sampled[np.ix_(valid_u, valid_z)] = mask[np.ix_(rows[valid_z], cols[valid_u])].T
    return sampled


def box_mesh(name: str, x0: float, x1: float, y0: float, y1: float, z0: float, z1: float):
    vertices = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
             (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
             (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return orient_positive(Mesh(name, vertices, faces))


def point_on_segment_2d(point, a, b, tolerance=1.0e-7):
    point, a, b = np.asarray(point, float), np.asarray(a, float), np.asarray(b, float)
    direction, relative = b - a, point - a
    cross = abs(float(direction[0] * relative[1] - direction[1] * relative[0]))
    return cross <= tolerance and float(np.dot(point - a, point - b)) <= tolerance


def point_in_ring_2d(point, ring, include_boundary=True):
    x, y = map(float, point)
    inside = False
    for index, a in enumerate(ring):
        b = ring[(index + 1) % len(ring)]
        if point_on_segment_2d((x, y), a, b):
            return include_boundary
        ax, ay = a
        bx, by = b
        if (ay > y) != (by > y):
            crossing_x = (bx - ax) * (y - ay) / (by - ay) + ax
            if x < crossing_x:
                inside = not inside
    return inside


def triangulate_planar_domain(contours, contains, interior_step=None):
    raw_points = [tuple(map(float, point)) for contour in contours for point in contour]
    if interior_step:
        coords = np.asarray(raw_points)
        for u in np.arange(coords[:, 0].min() + interior_step, coords[:, 0].max(), interior_step):
            for z in np.arange(coords[:, 1].min() + interior_step, coords[:, 1].max(), interior_step):
                if contains((u, z), False):
                    raw_points.append((float(u), float(z)))
    points = []
    ids = {}
    for point in raw_points:
        key = (round(point[0], 7), round(point[1], 7))
        if key not in ids:
            ids[key] = len(points)
            points.append(point)
    coords = np.asarray(points, dtype=float)
    if len(coords) < 3:
        return coords, [], []
    candidate = Delaunay(coords, qhull_options="QJ").simplices
    faces = []
    for triangle in candidate:
        tri = coords[triangle]
        probes = [tri.mean(axis=0)]
        for i in range(3):
            a, b = tri[i], tri[(i + 1) % 3]
            probes.extend((a * 0.75 + b * 0.25, (a + b) * 0.5, a * 0.25 + b * 0.75))
        if not all(contains(probe, True) for probe in probes):
            continue
        a, b, c = map(int, triangle)
        ab, ac = coords[b] - coords[a], coords[c] - coords[a]
        area = float(ab[0] * ac[1] - ab[1] * ac[0])
        if abs(area) <= EPS:
            continue
        faces.append((a, b, c) if area > 0 else (a, c, b))
    edge_counts = {}
    edge_directions = {}
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (c, a)):
            key = (min(u, v), max(u, v))
            edge_counts[key] = edge_counts.get(key, 0) + 1
            edge_directions[key] = (u, v)
    boundary = [edge_directions[key] for key, count in edge_counts.items() if count == 1]
    return coords, faces, boundary


def triangulate_svg_contours(contours):
    """Fast vectorized even/odd triangulation for the supplied SVG paths."""
    if len(contours) == 1:
        polygon = [tuple(map(float, point)) for point in contours[0]]
        cleaned = []
        for point in polygon:
            if not cleaned or np.linalg.norm(np.asarray(point) - np.asarray(cleaned[-1])) > 1.0e-7:
                cleaned.append(point)
        if len(cleaned) > 2 and np.linalg.norm(np.asarray(cleaned[0]) - np.asarray(cleaned[-1])) <= 1.0e-7:
            cleaned.pop()
        if contour_area(cleaned) < 0:
            cleaned.reverse()
        coords = np.asarray(cleaned, dtype=float)
        remaining = list(range(len(coords)))
        faces = []
        guard = 0
        while len(remaining) > 3 and guard < len(coords) * len(coords):
            guard += 1
            ear_found = False
            for position, current in enumerate(remaining):
                previous = remaining[position - 1]
                following = remaining[(position + 1) % len(remaining)]
                a, b, c = coords[previous], coords[current], coords[following]
                ab, ac = b - a, c - a
                cross = ab[0] * ac[1] - ab[1] * ac[0]
                if cross <= 1.0e-10:
                    continue
                candidates = [idx for idx in remaining if idx not in (previous, current, following)]
                if candidates:
                    points = coords[candidates]
                    v0, v1 = c - a, b - a
                    v2 = points - a
                    dot00, dot01, dot11 = float(v0 @ v0), float(v0 @ v1), float(v1 @ v1)
                    denominator = dot00 * dot11 - dot01 * dot01
                    if abs(denominator) <= EPS:
                        continue
                    u = (dot11 * (v2 @ v0) - dot01 * (v2 @ v1)) / denominator
                    v = (dot00 * (v2 @ v1) - dot01 * (v2 @ v0)) / denominator
                    if np.any((u > 1.0e-9) & (v > 1.0e-9) & (u + v < 1.0 - 1.0e-9)):
                        continue
                faces.append((previous, current, following))
                remaining.pop(position)
                ear_found = True
                break
            if not ear_found:
                # Remove the least significant near-collinear sample and retry.
                turns = []
                for position, current in enumerate(remaining):
                    previous = remaining[position - 1]
                    following = remaining[(position + 1) % len(remaining)]
                    a, b, c = coords[previous], coords[current], coords[following]
                    turns.append(abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])))
                remaining.pop(int(np.argmin(turns)))
        if len(remaining) == 3:
            faces.append(tuple(remaining))
        boundary = [(index, (index + 1) % len(coords)) for index in range(len(coords))]
        used_boundary = set(tuple(sorted(edge)) for face in faces for edge in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])))
        if all(tuple(sorted(edge)) in used_boundary for edge in boundary):
            return coords, faces, boundary

    points = []
    ids = {}
    for contour in contours:
        for point in contour:
            key = (round(float(point[0]), 7), round(float(point[1]), 7))
            if key not in ids:
                ids[key] = len(points)
                points.append(tuple(map(float, point)))
    coords = np.asarray(points, dtype=float)
    candidate = Delaunay(coords, qhull_options="QJ").simplices
    triangles = coords[candidate]
    stacked = triangles.mean(axis=1)
    inside = np.zeros(len(stacked), dtype=bool)
    for contour in contours:
        closed = np.vstack((np.asarray(contour, dtype=float), np.asarray(contour[0], dtype=float)))
        inside ^= MplPath(closed).contains_points(stacked)
    faces = []
    for triangle in candidate[inside]:
        a, b, c = map(int, triangle)
        ab, ac = coords[b] - coords[a], coords[c] - coords[a]
        area = float(ab[0] * ac[1] - ab[1] * ac[0])
        if abs(area) > EPS:
            faces.append((a, b, c) if area > 0 else (a, c, b))

    # A filtered Delaunay fill can occasionally create two material regions
    # touching at a single outline sample.  Duplicate that vertex per triangle
    # fan so the extruded SVG solid remains two-manifold without changing shape.
    mutable_faces = [list(face) for face in faces]
    coord_list = [tuple(point) for point in coords]
    original_vertex_count = len(coord_list)
    for vertex in range(original_vertex_count):
        incident = [fi for fi, face in enumerate(mutable_faces) if vertex in face]
        if len(incident) < 2:
            continue
        neighbours = {fi: set() for fi in incident}
        edge_to_faces = {}
        for fi in incident:
            for other in mutable_faces[fi]:
                if other != vertex:
                    edge_to_faces.setdefault(other, []).append(fi)
        for linked in edge_to_faces.values():
            for fi in linked:
                neighbours[fi].update(other for other in linked if other != fi)
        components = []
        unseen = set(incident)
        while unseen:
            start = unseen.pop()
            component = {start}
            stack = [start]
            while stack:
                for neighbour in neighbours[stack.pop()] & unseen:
                    unseen.remove(neighbour)
                    component.add(neighbour)
                    stack.append(neighbour)
            components.append(component)
        for component in components[1:]:
            replacement = len(coord_list)
            coord_list.append(coord_list[vertex])
            for fi in component:
                mutable_faces[fi] = [replacement if value == vertex else value for value in mutable_faces[fi]]
    coords = np.asarray(coord_list, dtype=float)
    faces = [tuple(face) for face in mutable_faces]
    edge_counts = {}
    edge_directions = {}
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (c, a)):
            key = (min(u, v), max(u, v))
            edge_counts[key] = edge_counts.get(key, 0) + 1
            edge_directions[key] = (u, v)
    boundary = [edge_directions[key] for key, count in edge_counts.items() if count == 1]
    return coords, faces, boundary


def extrude_triangulated(name, points, faces, boundary, map_inner, map_outer):
    inner = [tuple(map(float, map_inner(u, z))) for u, z in points]
    outer = [tuple(map(float, map_outer(u, z))) for u, z in points]
    count = len(points)
    mesh_faces = []
    for a, b, c in faces:
        mesh_faces.extend(((a, c, b), (a + count, b + count, c + count)))
    for a, b in boundary:
        mesh_faces.extend(((a, b, b + count), (a, b + count, a + count)))
    return orient_positive(Mesh(name, inner + outer, mesh_faces))


def convex_prism_on_face(name, polygon_uz, face: str, inner_plane: float, outer_plane: float):
    polygon = [tuple(map(float, p)) for p in polygon_uz]
    if contour_area(polygon) < 0:
        polygon.reverse()
    faces = [(0, i, i + 1) for i in range(1, len(polygon) - 1)]
    boundary = [(i, (i + 1) % len(polygon)) for i in range(len(polygon))]
    points = np.asarray(polygon, dtype=float)
    if face == "x":
        return extrude_triangulated(name, points, faces, boundary, lambda u, z: (inner_plane, u, z), lambda u, z: (outer_plane, u, z))
    return extrude_triangulated(name, points, faces, boundary, lambda u, z: (u, inner_plane, z), lambda u, z: (u, outer_plane, z))


def rib_polygon(a, b, width):
    a, b = np.asarray(a, float), np.asarray(b, float)
    direction = b - a
    length = float(np.linalg.norm(direction))
    normal = np.array((-direction[1], direction[0])) / length * (width / 2.0)
    return [tuple(a + normal), tuple(a - normal), tuple(b - normal), tuple(b + normal)]


def honeycomb_segment_layout(u_bounds, z_bounds, radius, rib_width, frame, keepout=None):
    u_min, u_max = u_bounds
    z_min, z_max = z_bounds
    step_u, step_z = 1.5 * radius, math.sqrt(3.0) * radius
    centers = []
    column = 0
    center_u = u_min + frame + radius
    while center_u <= u_max - frame - radius + EPS:
        center_z = z_min + frame + math.sqrt(3.0) * radius / 2.0 + (0.5 * step_z if column % 2 else 0.0)
        while center_z <= z_max - frame - math.sqrt(3.0) * radius / 2.0 + EPS:
            centers.append((center_u, center_z))
            center_z += step_z
        center_u += step_u
        column += 1
    segment_keys = set()
    segments = []
    for center_u, center_z in centers:
        vertices = [(center_u + radius * math.cos(math.radians(angle)), center_z + radius * math.sin(math.radians(angle))) for angle in (0, 60, 120, 180, 240, 300)]
        for index, a in enumerate(vertices):
            b = vertices[(index + 1) % 6]
            key = tuple(sorted(((round(a[0], 5), round(a[1], 5)), (round(b[0], 5), round(b[1], 5)))))
            if key in segment_keys:
                continue
            segment_keys.add(key)
            if keepout:
                ku0, ku1, kz0, kz1 = keepout
                if max(a[0], b[0]) + rib_width / 2.0 >= ku0 and min(a[0], b[0]) - rib_width / 2.0 <= ku1 and max(a[1], b[1]) + rib_width / 2.0 >= kz0 and min(a[1], b[1]) - rib_width / 2.0 <= kz1:
                    continue
            segments.append((a, b))
    return centers, segments


def honeycomb_ribs_for_face(name, face, inner_plane, outer_plane, u_bounds, z_bounds, radius, rib_width, frame, keepout=None):
    centers, segments = honeycomb_segment_layout(u_bounds, z_bounds, radius, rib_width, frame, keepout)
    meshes = [convex_prism_on_face(f"{name}-rib-{index + 1}", rib_polygon(a, b, rib_width), face, inner_plane, outer_plane) for index, (a, b) in enumerate(segments)]
    return meshes, len(centers), len(segments)


def capsule_contour(center_u, center_z, width, length, arc_steps=12):
    radius = width / 2.0
    straight_half = max(0.0, (length - width) / 2.0)
    points = []
    for angle in np.linspace(0.0, math.pi, arc_steps, endpoint=False):
        points.append((center_u + radius * math.cos(angle), center_z + straight_half + radius * math.sin(angle)))
    for angle in np.linspace(math.pi, 2.0 * math.pi, arc_steps, endpoint=False):
        points.append((center_u + radius * math.cos(angle), center_z - straight_half + radius * math.sin(angle)))
    return points


def make_slotted_mount_plate(params, x_outer, x_inner):
    y0, y1 = float(params["mount_plate_y_min_mm"]), float(params["mount_plate_y_max_mm"])
    z0, z1 = float(params["mount_plate_bottom_z_mm"]), float(params["mount_plate_top_z_mm"])
    outer = [(y0, z0), (y1, z0), (y1, z1), (y0, z1)]
    pair_center = float(params["mount_pair_center_z_mm"])
    spacing = float(params["mount_hole_spacing_nominal_mm"])
    holes = [capsule_contour(float(params["mount_slot_center_y_mm"]), pair_center + sign * spacing / 2.0, float(params["mount_slot_width_mm"]), float(params["mount_slot_length_mm"])) for sign in (-1.0, 1.0)]
    def contains(point, boundary):
        return point_in_ring_2d(point, outer, boundary) and not any(point_in_ring_2d(point, hole, not boundary) for hole in holes)
    points, faces, boundary = triangulate_planar_domain([outer] + holes, contains, interior_step=1.0)
    return extrude_triangulated("smooth-right-side-slotted-mount", points, faces, boundary, lambda u, z: (x_inner, u, z), lambda u, z: (x_outer, u, z))


def make_smooth_hood(params, width, depth, wall):
    start = float(params["impact_hood_start_z_mm"])
    top = float(params["impact_wall_height_mm"])
    hood_depth = float(params["impact_hood_depth_mm"])
    outer = []
    inner = []
    for index in range(25):
        t = index / 24.0
        z = start + (top - start) * t
        offset = hood_depth * t * t * (3.0 - 2.0 * t)
        outer.append((width / 2.0 - offset, z))
        inner.append((width / 2.0 - offset - wall, z))
    polygon = outer + inner[::-1]
    def contains(point, boundary):
        return point_in_ring_2d(point, polygon, boundary)
    points, faces, boundary = triangulate_planar_domain([polygon], contains)
    return extrude_triangulated("smooth-impact-hood", points, faces, boundary, lambda x, z: (x, -depth / 2.0, z), lambda x, z: (x, depth / 2.0, z))


def make_catcher(params: dict, masks: dict):
    """Build R5 from analytic prisms and smooth ruled surfaces; no body voxels."""
    width, depth = float(params["upper_width_mm"]), float(params["upper_depth_mm"])
    wall = float(params["wall_mm"])
    radius = float(params["honeycomb_cell_radius_mm"])
    rib = float(params["honeycomb_rib_width_mm"])
    frame = float(params["honeycomb_edge_frame_mm"])
    bottom_h = float(params["bottom_frame_height_mm"])
    impact_h = float(params["impact_wall_height_mm"])
    impact_solid = float(params["impact_solid_band_start_z_mm"])
    hood_start = float(params["impact_hood_start_z_mm"])
    front_h = float(params["front_wall_height_mm"])
    rear_h = float(params["rear_wall_height_mm"])
    mount_h = float(params["display_lower_wall_height_mm"])
    parts = []
    cell_count = segment_count = 0

    def add_honey(name, face, inner, outer, u_bounds, z_bounds, keepout=None):
        nonlocal cell_count, segment_count
        meshes, cells, segments = honeycomb_ribs_for_face(name, face, inner, outer, u_bounds, z_bounds, radius, rib, frame, keepout)
        parts.extend(meshes)
        cell_count += cells
        segment_count += segments

    # +X is the opposite/impact side.  Viewed from the printer front (+Y), it is left.
    add_honey("impact", "x", width / 2.0 - wall, width / 2.0, (-depth / 2.0, depth / 2.0), (0.0, impact_solid))
    parts.extend([
        box_mesh("impact-bottom-frame", width / 2.0 - wall, width / 2.0, -depth / 2.0, depth / 2.0, 0.0, bottom_h),
        box_mesh("impact-front-frame", width / 2.0 - wall, width / 2.0, depth / 2.0 - frame, depth / 2.0, bottom_h, impact_solid),
        box_mesh("impact-rear-frame", width / 2.0 - wall, width / 2.0, -depth / 2.0, -depth / 2.0 + frame, bottom_h, impact_solid),
        box_mesh("impact-solid-band", width / 2.0 - wall, width / 2.0, -depth / 2.0, depth / 2.0, impact_solid, hood_start),
        make_smooth_hood(params, width, depth, wall),
    ])

    # -X is the screw/display side.  Viewed from the printer front (+Y), it is right.
    plate_keepout = (float(params["mount_plate_y_min_mm"]) - rib, float(params["mount_plate_y_max_mm"]), float(params["mount_plate_bottom_z_mm"]) - rib, float(params["mount_plate_top_z_mm"]))
    add_honey("mount", "x", -width / 2.0 + wall, -width / 2.0, (-depth / 2.0, depth / 2.0), (0.0, mount_h), plate_keepout)
    parts.extend([
        box_mesh("mount-bottom-frame", -width / 2.0, -width / 2.0 + wall, -depth / 2.0, depth / 2.0, 0.0, bottom_h),
        box_mesh("mount-rear-frame", -width / 2.0, -width / 2.0 + wall, -depth / 2.0, -depth / 2.0 + frame, bottom_h, mount_h),
        box_mesh("mount-front-frame-low", -width / 2.0, -width / 2.0 + wall, depth / 2.0 - frame, depth / 2.0, bottom_h, float(params["mount_plate_bottom_z_mm"])),
        box_mesh("mount-top-frame-free", -width / 2.0, -width / 2.0 + wall, -depth / 2.0, float(params["mount_plate_y_min_mm"]), mount_h - frame, mount_h),
        make_slotted_mount_plate(params, -width / 2.0, -width / 2.0 + float(params["mount_plate_thickness_mm"])),
    ])

    # +Y is the actual printer front.  -Y is rear.
    add_honey("front", "y", depth / 2.0 - wall, depth / 2.0, (-width / 2.0, width / 2.0), (0.0, front_h))
    add_honey("rear", "y", -depth / 2.0 + wall, -depth / 2.0, (-width / 2.0, width / 2.0), (0.0, rear_h))
    for label, y0, y1, height in (("front", depth / 2.0 - wall, depth / 2.0, front_h), ("rear", -depth / 2.0, -depth / 2.0 + wall, rear_h)):
        parts.extend([
            box_mesh(f"{label}-bottom-frame", -width / 2.0, width / 2.0, y0, y1, 0.0, bottom_h),
            box_mesh(f"{label}-left-frame", -width / 2.0, -width / 2.0 + frame, y0, y1, bottom_h, height),
            box_mesh(f"{label}-right-frame", width / 2.0 - frame, width / 2.0, y0, y1, bottom_h, height),
            box_mesh(f"{label}-top-frame", -width / 2.0, width / 2.0, y0, y1, height - frame, height),
        ])

    # Narrow body-colour lattice continuations support the isolated i-dot in
    # the untouched wordmark.  These are ribs, not a logo background panel.
    support_width = float(params["logo_support_rib_width_mm"])
    support_z = (float(params["logo_support_rib_bottom_z_mm"]), float(params["logo_support_rib_top_z_mm"]))
    support_specs = (
        ("front", "y", depth / 2.0 - wall, depth / 2.0, float(params["logo_support_rib_front_u_mm"])),
        ("impact", "x", width / 2.0 - wall, width / 2.0, float(params["logo_support_rib_impact_u_mm"])),
        ("mount", "x", -width / 2.0 + wall, -width / 2.0, float(params["logo_support_rib_mount_u_mm"])),
    )
    for label, face, inner, outer, support_u in support_specs:
        parts.append(convex_prism_on_face(f"{label}-logo-support-rib", rib_polygon((support_u, support_z[0]), (support_u, support_z[1]), support_width), face, inner, outer))

    body = combine_meshes(parts, "catcher-body-white-smooth-honeycomb")
    vertices = np.asarray(body.vertices, dtype=float)
    faces = np.asarray(body.faces, dtype=np.int64)
    bottom_faces = faces[np.all(np.isclose(vertices[faces, 2], 0.0), axis=1)]
    interior_bottom_faces = 0
    for triangle in bottom_faces:
        center = vertices[triangle].mean(axis=0)
        if abs(center[0]) < width / 2.0 - wall and abs(center[1]) < depth / 2.0 - wall:
            interior_bottom_faces += 1
    open_area_proxy_percent = ((max(radius - rib / 2.0, 0.0) / radius) ** 2) * 100.0
    slot_length = float(params["mount_slot_length_mm"])
    slot_width = float(params["mount_slot_width_mm"])
    pair_spacing = float(params["mount_hole_spacing_nominal_mm"])
    hood_height = impact_h - hood_start
    hood_depth = float(params["impact_hood_depth_mm"])
    return body, None, {
        "geometry_method": params["geometry_method"],
        "body_uses_voxels": False,
        "face_x_mm": width / 2.0,
        "face_y_mm": depth / 2.0,
        "drop_opening_clear_mm": [width - 2.0 * wall, depth - 2.0 * wall],
        "drop_probe_occupied_faces": interior_bottom_faces,
        "center_top_open": True,
        "open_bottom": True,
        "mount_side_viewed_from_printer_front": "right",
        "mount_side_project_axis": "-X",
        "impact_side_viewed_from_printer_front": "left",
        "impact_side_project_axis": "+X",
        "mount_slot_axis": "vertical pair in right-side plate",
        "mount_slots_count": 2,
        "mount_hole_spacing_nominal_mm": pair_spacing,
        "mount_hole_spacing_adjustable_range_mm": [pair_spacing - (slot_length - slot_width), pair_spacing + (slot_length - slot_width)],
        "impact_wall_height_mm": impact_h,
        "impact_solid_band_start_z_mm": impact_solid,
        "impact_solid_band_present": True,
        "impact_hood_start_z_mm": hood_start,
        "impact_hood_depth_mm": hood_depth,
        "impact_hood_max_overhang_from_vertical_deg": math.degrees(math.atan(1.5 * hood_depth / hood_height)),
        "honeycomb_is_through_open": True,
        "honeycomb_cell_radius_mm": radius,
        "honeycomb_rib_width_mm": rib,
        "analytic_honeycomb_cells": cell_count,
        "analytic_honeycomb_rib_segments": segment_count,
        "panel_open_area_proxy_percent": open_area_proxy_percent,
        "logo_background_present": False,
        "logo_support_ribs_count": len(support_specs),
        "logo_support_ribs_are_lattice_extensions": True,
    }


def rounded_rectangle_points(width: float, depth: float, radius: float, segments: int):
    radius = min(radius, width / 2.0 - EPS, depth / 2.0 - EPS)
    corners = (
        (width / 2 - radius, -depth / 2 + radius, -90.0, 0.0),
        (width / 2 - radius, depth / 2 - radius, 0.0, 90.0),
        (-width / 2 + radius, depth / 2 - radius, 90.0, 180.0),
        (-width / 2 + radius, -depth / 2 + radius, 180.0, 270.0),
    )
    points = []
    for cx, cy, a0, a1 in corners:
        for index in range(segments):
            angle = math.radians(a0 + (a1 - a0) * index / segments)
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def add_ring(mesh: Mesh, points: Iterable[Sequence[float]], z_values: Iterable[float]):
    result = []
    for (x, y), z in zip(points, z_values):
        result.append(len(mesh.vertices))
        mesh.vertices.append((float(x), float(y), float(z)))
    return result


def connect_rings(mesh: Mesh, lower: Sequence[int], upper: Sequence[int], outward=True):
    for index in range(len(lower)):
        nxt = (index + 1) % len(lower)
        if outward:
            mesh.faces.extend(((lower[index], lower[nxt], upper[nxt]), (lower[index], upper[nxt], upper[index])))
        else:
            mesh.faces.extend(((lower[index], upper[nxt], lower[nxt]), (lower[index], upper[index], upper[nxt])))


def fan_cap(mesh: Mesh, ring: Sequence[int], z: float, upward: bool):
    center = len(mesh.vertices)
    mesh.vertices.append((sum(mesh.vertices[i][0] for i in ring) / len(ring), sum(mesh.vertices[i][1] for i in ring) / len(ring), z))
    for index in range(len(ring)):
        nxt = (index + 1) % len(ring)
        mesh.faces.append((center, ring[index], ring[nxt]) if upward else (center, ring[nxt], ring[index]))


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def make_bin(params: dict):
    wb, db = float(params["width_bottom_mm"]), float(params["depth_bottom_mm"])
    wt, dt = float(params["width_top_mm"]), float(params["depth_top_mm"])
    hf, hb = float(params["front_height_mm"]), float(params["back_height_mm"])
    wall, floor = float(params["wall_mm"]), float(params["floor_mm"])
    rb, rt = float(params["corner_radius_bottom_mm"]), float(params["corner_radius_top_mm"])
    rim_out, rim_rise = float(params["rim_outset_mm"]), float(params["rim_rise_mm"])
    levels, segments = int(params["levels"]), int(params["corner_segments"])
    mesh = Mesh("lower-bin", [], [])

    def top_height(y_norm):
        return hf + (hb - hf) * smoothstep((y_norm + 1.0) / 2.0)

    outer_rings = []
    for level in range(levels + 1):
        t = level / levels
        width, depth = wb + (wt - wb) * t, db + (dt - db) * t
        radius = rb + (rt - rb) * t
        points = rounded_rectangle_points(width, depth, radius, segments)
        z_values = [t * (top_height(max(-1.0, min(1.0, y / (depth / 2.0)))) - rim_rise) for _, y in points]
        outer_rings.append(add_ring(mesh, points, z_values))
        if level:
            connect_rings(mesh, outer_rings[-2], outer_rings[-1], True)
    flare_points = rounded_rectangle_points(wt + 2 * rim_out, dt + 2 * rim_out, rt + rim_out, segments)
    flare_z = [top_height(max(-1.0, min(1.0, y / ((dt + 2 * rim_out) / 2.0)))) for _, y in flare_points]
    outer_flare = add_ring(mesh, flare_points, flare_z)
    connect_rings(mesh, outer_rings[-1], outer_flare, True)

    inner_rings = []
    for level in range(levels + 1):
        t = level / levels
        width, depth = wb - 2 * wall + (wt - wb) * t, db - 2 * wall + (dt - db) * t
        radius = rb - wall + (rt - rb) * t
        points = rounded_rectangle_points(width, depth, radius, segments)
        z_values = [floor + t * (top_height(max(-1.0, min(1.0, y / (depth / 2.0)))) - floor) for _, y in points]
        inner_rings.append(add_ring(mesh, points, z_values))
        if level:
            connect_rings(mesh, inner_rings[-2], inner_rings[-1], False)
    fan_cap(mesh, outer_rings[0], 0.0, False)
    fan_cap(mesh, inner_rings[0], floor, True)
    for index in range(len(outer_flare)):
        nxt = (index + 1) % len(outer_flare)
        mesh.faces.extend(((outer_flare[index], outer_flare[nxt], inner_rings[-1][nxt]), (outer_flare[index], inner_rings[-1][nxt], inner_rings[-1][index])))
    orient_positive(mesh)

    def rounded_area(width, depth, radius):
        return width * depth - (4.0 - math.pi) * radius * radius

    samples = 1000
    areas = []
    for idx in range(samples + 1):
        t = idx / samples
        areas.append(rounded_area(wb - 2 * wall + (wt - wb) * t, db - 2 * wall + (dt - db) * t, rb - wall + (rt - rb) * t))
    capacity = float(np.trapezoid(np.asarray(areas), dx=(hf - floor) / samples) / 1_000_000.0)
    return mesh, {"usable_capacity_l": capacity, "max_wall_taper_from_vertical_deg": math.degrees(math.atan(max((wt - wb) / 2.0, (dt - db) / 2.0) / hf))}


def make_mount_gauge(params: dict):
    pitch = float(params["voxel_pitch_mm"])
    width, depth, thick = float(params["width_mm"]), float(params["depth_mm"]), float(params["thickness_mm"])
    nx, ny, nz = math.ceil(width / pitch), math.ceil(depth / pitch), math.ceil(thick / pitch)
    xs = -width / 2.0 + (np.arange(nx) + 0.5) * pitch
    ys = -depth / 2.0 + (np.arange(ny) + 0.5) * pitch
    zs = (np.arange(nz) + 0.5) * pitch
    x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")
    occupancy = np.ones((nx, ny, nz), dtype=bool)
    length, slot_width = float(params["mount_slot_length_mm"]), float(params["mount_slot_width_mm"])
    radius, straight_half = slot_width / 2.0, max(0.0, (length - slot_width) / 2.0)
    spacing = float(params["mount_hole_spacing_nominal_mm"])
    slots = np.zeros_like(occupancy)
    for center_y in (-spacing / 2.0, spacing / 2.0):
        dy = np.maximum(np.abs(y - center_y) - straight_half, 0.0)
        slots |= x * x + dy * dy <= radius * radius
    occupancy &= ~slots
    return voxel_surface_mesh(occupancy, pitch, (-width / 2.0, -depth / 2.0, 0.0), "vertical-pair-mount-fit-gauge")


PATH_TOKEN = re.compile(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def parse_svg_path(data: str, curve_steps=10):
    tokens, index, command = PATH_TOKEN.findall(data), 0, None
    current, start = np.array([0.0, 0.0]), np.array([0.0, 0.0])
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
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
            if command.upper() == "Z":
                finish(True)
                current = start.copy()
                command = None
                continue
        if command is None:
            continue
        upper, relative = command.upper(), command.islower()
        need = nargs[upper]
        while index < len(tokens) and not tokens[index].isalpha():
            values = list(map(float, tokens[index:index + need]))
            if len(values) != need:
                raise ValueError(f"Incomplete SVG path command {command}")
            index += need
            if upper == "M":
                finish()
                current = np.array(values[:2]) + (current if relative else 0)
                start = current.copy()
                contour = [tuple(current)]
                upper, command, need = "L", ("l" if relative else "L"), 2
            elif upper == "L":
                current = np.array(values[:2]) + (current if relative else 0)
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
                    contour.append(tuple((1 - t) ** 2 * begin + 2 * (1 - t) * t * control + t * t * end))
                current = end
            elif upper == "C":
                c1 = np.array(values[:2]) + (current if relative else 0)
                c2 = np.array(values[2:4]) + (current if relative else 0)
                end = np.array(values[4:6]) + (current if relative else 0)
                begin = current.copy()
                for step in range(1, curve_steps + 1):
                    t = step / curve_steps
                    contour.append(tuple((1 - t) ** 3 * begin + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t * t * c2 + t ** 3 * end))
                current = end
    finish()
    return contours


def affine_identity():
    return np.eye(3, dtype=float)


def parse_transform(value: str | None):
    result = affine_identity()
    if not value:
        return result
    for name, raw in re.findall(r"([A-Za-z]+)\s*\(([^)]*)\)", value):
        args = [float(x) for x in re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?)", raw)]
        op = affine_identity()
        if name == "translate":
            op[0, 2], op[1, 2] = args[0], (args[1] if len(args) > 1 else 0.0)
        elif name == "scale":
            op[0, 0], op[1, 1] = args[0], (args[1] if len(args) > 1 else args[0])
        elif name == "matrix" and len(args) == 6:
            a, b, c, d, e, f = args
            op = np.array(((a, c, e), (b, d, f), (0, 0, 1)), dtype=float)
        else:
            raise ValueError(f"Unsupported SVG transform {name}")
        result = result @ op
    return result


def contour_area(points):
    return sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points))) / 2.0


def render_logo_masks(svg_path: Path, params: dict):
    pitch = float(params["logo_pitch_mm"])
    colors = ("#112431", "#08777D", "#7FD5D3", "#C7AB82")
    root = ET.parse(svg_path).getroot()
    viewbox = [float(value) for value in root.attrib["viewBox"].replace(",", " ").split()]
    vb_x, vb_y, vb_w, vb_h = viewbox
    logo_w = float(params["logo_width_mm"])
    uniform_scale = logo_w / vb_w
    logo_h = vb_h * uniform_scale
    image_w = int(round(logo_w / pitch))
    image_h = int(math.ceil(logo_h / pitch))
    panel_w, panel_h = image_w * pitch, image_h * pitch
    paths = []

    def visit(element, parent_matrix):
        matrix = parent_matrix @ parse_transform(element.attrib.get("transform"))
        if element.tag.rsplit("}", 1)[-1] == "path":
            color = element.attrib.get("fill", "").upper()
            if color in colors:
                contours = []
                for contour in parse_svg_path(element.attrib["d"]):
                    contours.append([tuple((matrix @ np.array([x, y, 1.0]))[:2]) for x, y in contour])
                paths.append((color, contours))
        for child in list(element):
            visit(child, matrix)

    visit(root, affine_identity())
    palette = np.full((image_h, image_w), -1, dtype=np.int8)
    path_counts = {color: 0 for color in colors}
    for color, contours in paths:
        path_counts[color] += 1
        pixels = []
        for contour in contours:
            converted = []
            for x, y in contour:
                physical_u = -panel_w / 2.0 + (x - vb_x) * uniform_scale
                physical_z = (vb_y + vb_h - y) * uniform_scale
                converted.append(((physical_u + panel_w / 2.0) / pitch, (panel_h - physical_z) / pitch))
            pixels.append(converted)
        ordered = sorted(pixels, key=lambda contour: abs(contour_area(contour)), reverse=True)
        if not ordered:
            continue
        outer_sign = math.copysign(1.0, contour_area(ordered[0]) or 1.0)
        path_mask = Image.new("L", (image_w, image_h), 0)
        draw = ImageDraw.Draw(path_mask)
        for contour in ordered:
            draw.polygon(contour, fill=255 if math.copysign(1.0, contour_area(contour) or outer_sign) == outer_sign else 0)
        palette[np.asarray(path_mask) > 0] = colors.index(color)
    masks = {
        color: Image.fromarray(((palette == index).astype(np.uint8) * 255))
        for index, color in enumerate(colors)
    }
    return masks, {
        "viewbox": viewbox,
        "source_path_count": len(paths),
        "source_color_path_counts": path_counts,
        "uniform_scale_mm_per_svg_unit": uniform_scale,
        "logo_width_mm": logo_w,
        "logo_height_mm": logo_h,
        "raster_panel_mm": [panel_w, panel_h],
        "panel_pixels": [image_w, image_h],
        "cropped": False,
        "rearranged": False,
        "mirrored": False,
        "preserved": ["viewBox", "group transforms", "path order", "path coordinates", "fill colors"],
    }


def four_connected_components(mask: np.ndarray):
    """Yield face-connected 2D regions so diagonal glyph contacts stay manifold."""
    from collections import deque

    visited = np.zeros(mask.shape, dtype=bool)
    height, width = mask.shape
    for row, col in np.argwhere(mask):
        if visited[row, col]:
            continue
        component = np.zeros(mask.shape, dtype=bool)
        queue = deque([(int(row), int(col))])
        visited[row, col] = True
        while queue:
            current_row, current_col = queue.popleft()
            component[current_row, current_col] = True
            for next_row, next_col in (
                (current_row - 1, current_col),
                (current_row + 1, current_col),
                (current_row, current_col - 1),
                (current_row, current_col + 1),
            ):
                if 0 <= next_row < height and 0 <= next_col < width and mask[next_row, next_col] and not visited[next_row, next_col]:
                    visited[next_row, next_col] = True
                    queue.append((next_row, next_col))
        yield component


def combine_meshes(meshes: list[Mesh], name: str):
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    for mesh in meshes:
        offset = len(vertices)
        vertices.extend(mesh.vertices)
        faces.extend((a + offset, b + offset, c + offset) for a, b, c in mesh.faces)
    return orient_positive(Mesh(name, vertices, faces))


def extract_logo_paths(svg_path: Path, params: dict):
    """Return the supplied SVG paths as smooth physical (u, z) contours."""
    colors = ("#112431", "#08777D", "#7FD5D3", "#C7AB82")
    root = ET.parse(svg_path).getroot()
    vb_x, vb_y, vb_w, vb_h = [float(value) for value in root.attrib["viewBox"].replace(",", " ").split()]
    scale = float(params["logo_width_mm"]) / vb_w
    bottom = float(params["logo_panel_bottom_z_mm"])
    paths = []

    def visit(element, parent_matrix):
        matrix = parent_matrix @ parse_transform(element.attrib.get("transform"))
        if element.tag.rsplit("}", 1)[-1] == "path":
            color = element.attrib.get("fill", "").upper()
            if color in colors:
                contours = []
                for contour in parse_svg_path(element.attrib["d"], curve_steps=12):
                    physical = []
                    for x, y in contour:
                        x, y = (matrix @ np.array([x, y, 1.0]))[:2]
                        physical.append((-float(params["logo_width_mm"]) / 2.0 + (x - vb_x) * scale, bottom + (vb_y + vb_h - y) * scale))
                    if len(physical) >= 3:
                        if np.linalg.norm(np.asarray(physical[0]) - np.asarray(physical[-1])) <= EPS:
                            physical.pop()
                        contours.append(physical)
                if contours:
                    paths.append((color, contours))
        for child in list(element):
            visit(child, matrix)

    visit(root, affine_identity())
    return paths


def logo_start_support_metrics(masks: dict, params: dict):
    """Conservative raster proxy against the exact analytic honeycomb layout."""
    pitch = float(params["logo_pitch_mm"])
    radius = float(params["honeycomb_cell_radius_mm"])
    rib = float(params["honeycomb_rib_width_mm"])
    bottom = float(params["logo_panel_bottom_z_mm"])
    frame_height = float(params["bottom_frame_height_mm"])
    first = next(iter(masks.values()))
    panel_w = first.width * pitch
    u_local = -panel_w / 2.0 + (np.arange(first.width) + 0.5) * pitch
    z = bottom + (first.height - 0.5 - np.arange(first.height)) * pitch
    width, depth = float(params["upper_width_mm"]), float(params["upper_depth_mm"])
    frame = float(params["honeycomb_edge_frame_mm"])
    mount_keepout = (float(params["mount_plate_y_min_mm"]) - rib, float(params["mount_plate_y_max_mm"]), float(params["mount_plate_bottom_z_mm"]) - rib, float(params["mount_plate_top_z_mm"]))
    faces = (
        ("front", float(params["logo_panel_center_front_u_mm"]), True, (-width / 2.0, width / 2.0), (0.0, float(params["front_wall_height_mm"])), None),
        ("impact", float(params["logo_panel_center_impact_u_mm"]), False, (-depth / 2.0, depth / 2.0), (0.0, float(params["impact_solid_band_start_z_mm"])), None),
        ("mount", float(params["logo_panel_center_mount_u_mm"]), True, (-depth / 2.0, depth / 2.0), (0.0, float(params["display_lower_wall_height_mm"])), mount_keepout),
    )
    component_count = supported_count = 0
    minimum_contact = None
    per_face = {}
    for face_name, center, mirror, u_bounds, z_bounds, keepout in faces:
        u = center + (-u_local if mirror else u_local)
        uu, zz = np.meshgrid(u, z, indexing="ij")
        support = np.zeros_like(uu, dtype=bool)
        _, segments = honeycomb_segment_layout(u_bounds, z_bounds, radius, rib, frame, keepout)
        tolerance = rib / 2.0 + pitch * 0.75
        for a, b in segments:
            a, b = np.asarray(a, float), np.asarray(b, float)
            direction = b - a
            projection = np.clip(((uu - a[0]) * direction[0] + (zz - a[1]) * direction[1]) / float(direction @ direction), 0.0, 1.0)
            distance = np.hypot(uu - (a[0] + projection * direction[0]), zz - (a[1] + projection * direction[1]))
            support |= distance <= tolerance
        support_u = float(params[f"logo_support_rib_{face_name}_u_mm"])
        support_a = np.array((support_u, float(params["logo_support_rib_bottom_z_mm"])), dtype=float)
        support_b = np.array((support_u, float(params["logo_support_rib_top_z_mm"])), dtype=float)
        direction = support_b - support_a
        projection = np.clip(((uu - support_a[0]) * direction[0] + (zz - support_a[1]) * direction[1]) / float(direction @ direction), 0.0, 1.0)
        distance = np.hypot(uu - (support_a[0] + projection * direction[0]), zz - (support_a[1] + projection * direction[1]))
        support |= distance <= float(params["logo_support_rib_width_mm"]) / 2.0 + pitch * 0.75
        support |= z[None, :] <= frame_height + EPS
        support |= (u[:, None] <= u_bounds[0] + frame + EPS) | (u[:, None] >= u_bounds[1] - frame - EPS)
        if face_name == "impact":
            support |= z[None, :] >= float(params["impact_solid_band_start_z_mm"]) - EPS
        elif face_name == "mount":
            support |= ((u[:, None] >= float(params["mount_plate_y_min_mm"]) - EPS) &
                        (u[:, None] <= float(params["mount_plate_y_max_mm"]) + EPS) &
                        (z[None, :] >= float(params["mount_plate_bottom_z_mm"]) - EPS) &
                        (z[None, :] <= float(params["mount_plate_top_z_mm"]) + EPS))
        face_components = face_supported = 0
        for mask in masks.values():
            for component in four_connected_components(np.asarray(mask) > 0):
                face_components += 1
                rows, cols = np.where(component)
                local_min_z = float(z[rows].min())
                start = component & (z[:, None] <= local_min_z + 1.0 + EPS)
                contacts = int(np.count_nonzero(start.T & support))
                if contacts > 0:
                    face_supported += 1
                    minimum_contact = contacts if minimum_contact is None else min(minimum_contact, contacts)
        component_count += face_components
        supported_count += face_supported
        per_face[face_name] = {"components": face_components, "start_supported": face_supported}
    return {
        "method": "0.2 mm raster contact proxy; manufacturing geometry remains analytic",
        "components_across_three_faces": component_count,
        "start_supported_components": supported_count,
        "unsupported_components": component_count - supported_count,
        "minimum_start_contact_pixels": minimum_contact or 0,
        "per_face": per_face,
    }


def logo_meshes(svg_path: Path, masks: dict, params: dict, face_x: float, face_y: float):
    """Extrude the supplied SVG paths directly; no raster/voxel logo geometry."""
    depth = float(params["logo_extrusion_mm"])
    embed = float(params["logo_embed_mm"])
    names = {
        "#112431": "catcher-logo-navy-3sides-smooth",
        "#08777D": "catcher-logo-teal-3sides-smooth",
        "#7FD5D3": "catcher-logo-aqua-3sides-smooth",
        "#C7AB82": "catcher-logo-sand-3sides-smooth",
    }
    source_paths = extract_logo_paths(svg_path, params)
    by_color = {color: [] for color in names}
    path_counts = {color: 0 for color in names}
    face_specs = (
        ("front", float(params["logo_panel_center_front_u_mm"]),
         lambda u, z: (-u, face_y - embed, z), lambda u, z: (-u, face_y + depth, z)),
        ("impact", float(params["logo_panel_center_impact_u_mm"]),
         lambda u, z: (face_x - embed, u, z), lambda u, z: (face_x + depth, u, z)),
        ("mount", float(params["logo_panel_center_mount_u_mm"]),
         lambda u, z: (-face_x + embed, -u, z), lambda u, z: (-face_x - depth, -u, z)),
    )
    for color, contours in source_paths:
        path_counts[color] += 1

        points, faces, boundary = triangulate_svg_contours(contours)
        if not faces:
            raise ValueError(f"SVG logo path for {color} could not be triangulated")
        for face_name, center, inner_map, outer_map in face_specs:
            by_color[color].append(extrude_triangulated(
                f"{names[color]}-{face_name}-path-{path_counts[color]}",
                points,
                faces,
                boundary,
                lambda u, z, center=center, inner_map=inner_map: inner_map(u + center, z),
                lambda u, z, center=center, outer_map=outer_map: outer_map(u + center, z),
            ))
    result = {color: combine_meshes(meshes, names[color]) for color, meshes in by_color.items()}
    overlap = np.zeros_like(np.asarray(next(iter(masks.values()))), dtype=np.uint8)
    for mask in masks.values():
        overlap += (np.asarray(mask) > 0).astype(np.uint8)
    support = logo_start_support_metrics(masks, params)
    return result, {
        "geometry_method": "analytic SVG polygon extrusion; no logo voxels",
        "background_present": False,
        "mask_overlap_pixels": int(np.count_nonzero(overlap > 1)),
        "faces": ["+Y printer front", "+X impact/left", "-X display/right"],
        "face_x_mm": face_x,
        "face_y_mm": face_y,
        "extrusion_mm": depth,
        "embed_mm": embed,
        "source_path_count": len(source_paths),
        "source_color_path_counts": path_counts,
        "start_support": support,
    }


def number(value):
    return (f"{float(value):.6f}").rstrip("0").rstrip(".") or "0"


def write_3mf(path: Path, object_name: str, parts: list[tuple[Mesh, int]], materials: list[tuple[str, str]]):
    ET.register_namespace("", CORE_NS)
    model = ET.Element(f"{{{CORE_NS}}}model", {"unit": "millimeter", f"{{{XML_NS}}}lang": "en-US"})
    resources = ET.SubElement(model, f"{{{CORE_NS}}}resources")
    base = ET.SubElement(resources, f"{{{CORE_NS}}}basematerials", {"id": "1"})
    for name, color in materials:
        ET.SubElement(base, f"{{{CORE_NS}}}base", {"name": name, "displaycolor": color})
    obj = ET.SubElement(resources, f"{{{CORE_NS}}}object", {"id": "2", "type": "model", "name": object_name})
    mesh_node = ET.SubElement(obj, f"{{{CORE_NS}}}mesh")
    vertices_node = ET.SubElement(mesh_node, f"{{{CORE_NS}}}vertices")
    triangles_node = ET.SubElement(mesh_node, f"{{{CORE_NS}}}triangles")
    offset = 0
    for mesh, material_index in parts:
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices_node, f"{{{CORE_NS}}}vertex", {"x": number(x), "y": number(y), "z": number(z)})
        for a, b, c in mesh.faces:
            props = {"v1": str(a + offset), "v2": str(b + offset), "v3": str(c + offset), "pid": "1", "p1": str(material_index), "p2": str(material_index), "p3": str(material_index)}
            ET.SubElement(triangles_node, f"{{{CORE_NS}}}triangle", props)
        offset += len(mesh.vertices)
    build = ET.SubElement(model, f"{{{CORE_NS}}}build")
    ET.SubElement(build, f"{{{CORE_NS}}}item", {"objectid": "2"})
    model_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(model, encoding="utf-8")
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="{CONTENT_NS}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'''.encode()
    rels = f'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="{REL_NS}"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''.encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in (("[Content_Types].xml", content), ("_rels/.rels", rels), ("3D/3dmodel.model", model_bytes)):
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)


def validate_3mf(path: Path):
    required = {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}
    checks = {}
    metrics = {}
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        checks["required_parts"] = required <= names
        checks["zip_crc"] = archive.testzip() is None
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
    ns = {"m": CORE_NS}
    objects = root.findall(".//m:object", ns)
    components = root.findall(".//m:components", ns)
    build_items = root.findall("./m:build/m:item", ns)
    bases = root.findall(".//m:basematerials/m:base", ns)
    checks["no_component_hierarchy"] = len(components) == 0
    checks["one_direct_mesh_object"] = len(objects) == 1 and objects[0].find("m:mesh", ns) is not None
    checks["one_direct_build_item"] = len(build_items) == 1 and build_items[0].attrib.get("objectid") == objects[0].attrib.get("id")
    vertices = objects[0].findall(".//m:vertex", ns)
    triangles = objects[0].findall(".//m:triangle", ns)
    vertex_count = len(vertices)
    material_ok = True
    indices_ok = True
    for triangle in triangles:
        indices_ok &= all(0 <= int(triangle.attrib[key]) < vertex_count for key in ("v1", "v2", "v3"))
        material_ok &= int(triangle.attrib.get("pid", "-1")) == 1 and all(0 <= int(triangle.attrib[key]) < len(bases) for key in ("p1", "p2", "p3"))
    checks["triangle_indices_valid"] = bool(indices_ok)
    checks["material_references_valid"] = bool(material_ok)
    metrics.update({"objects": len(objects), "component_nodes": len(components), "build_items": len(build_items), "vertices": vertex_count, "triangles": len(triangles), "materials": [base.attrib for base in bases]})
    return {"file": path.name, "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "metrics": metrics}


def plot_mesh(ax, mesh: Mesh, color: str, alpha=1.0, max_faces=12000):
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces, dtype=int)]
    verts = np.asarray(mesh.vertices, dtype=float)
    poly = Poly3DCollection(verts[faces], facecolor=color, edgecolor="none", alpha=alpha)
    ax.add_collection3d(poly)


def save_assembly_preview(path: Path, catcher: Mesh, logos: dict, lower_bin: Mesh):
    from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

    fig, ax = plt.subplots(figsize=(13, 8), facecolor="#F4F1EB")
    ax.set_facecolor("#F4F1EB")
    # Functional front view.  The wiper and screws are on the viewer's right
    # (-X) and eject toward the high opposite/left wall (+X).
    left_wall = [(28, 112), (28, 162), (31, 174), (39, 174), (35, 162), (35, 112)]
    right_wall = [(98, 112), (98, 156), (105, 156), (105, 112)]
    ax.add_patch(Polygon(left_wall, closed=True, facecolor="#F2F2ED", edgecolor="#112431", lw=3))
    ax.add_patch(Polygon(right_wall, closed=True, facecolor="#F2F2ED", edgecolor="#112431", lw=3))
    ax.plot([28, 29, 31, 39], [162, 168, 174, 174], color="#08777D", lw=6, solid_capstyle="round")
    ax.text(18, 142, "58 mm\nPrallwand", ha="right", va="center", fontsize=11, color="#112431")
    ax.annotate("8 mm Überhang", xy=(36, 171), xytext=(-35, 205), arrowprops={"arrowstyle": "->", "color": "#08777D", "lw": 2}, fontsize=12, color="#112431")

    ax.add_patch(Rectangle((98, 139), 7, 35, facecolor="#F2F2ED", edgecolor="#112431", lw=2))
    for hole_z in (149, 164):
        ax.add_patch(plt.Circle((102, hole_z), 2.2, facecolor="#F4F1EB", edgecolor="#112431", lw=1.2))
    ax.add_patch(Rectangle((105, 145), 34, 25, facecolor="#D8D8D3", edgecolor="#112431", lw=2))
    ax.text(122, 157.5, "Purge\nWiper", ha="center", va="center", fontsize=10.5, color="#112431")
    ax.add_patch(FancyArrowPatch((132, 157), (35, 151), connectionstyle="arc3,rad=0.08", arrowstyle="-|>", mutation_scale=20, lw=3, color="#C7AB82"))
    ax.text(76, 163, "Feder-Auswurf", ha="center", color="#8A6A3E", fontsize=11)
    ax.add_patch(FancyArrowPatch((45, 147), (67, 119), connectionstyle="arc3,rad=-0.25", arrowstyle="-|>", mutation_scale=20, lw=3, color="#08777D"))
    ax.add_patch(FancyArrowPatch((67, 111), (67, 82), arrowstyle="-|>", mutation_scale=20, lw=3, color="#08777D"))
    ax.text(75, 98, "freier Fall", color="#08777D", fontsize=11, va="center")

    ax.add_patch(Polygon([(8, 0), (142, 0), (139, 68), (11, 68)], closed=True, facecolor="#112431", edgecolor="#08777D", lw=3))
    ax.plot([10, 140], [68, 68], color="#7FD5D3", lw=7, solid_capstyle="round")
    ax.text(75, 32, "separater Behälter", ha="center", va="center", fontsize=15, color="#F2F2ED")

    ax.text(170, 210, "1  M3-Messlehre am Wischerträger prüfen", fontsize=13, color="#112431")
    ax.annotate("2  Kurze Haube mit zwei Schrauben montieren", xy=(102, 157), xytext=(170, 165), arrowprops={"arrowstyle": "->", "color": "#08777D", "lw": 2}, fontsize=13, color="#112431")
    ax.annotate("3  Beliebigen Behälter darunterstellen", xy=(139, 64), xytext=(170, 96), arrowprops={"arrowstyle": "->", "color": "#08777D", "lw": 2}, fontsize=13, color="#112431")
    ax.text(20, 225, "62 × 44 mm · glatte Waben · offener Boden · Logo ohne Hintergrund × 3", fontsize=12, color="#112431")
    ax.text(8, -12, "Fanghaube und Behälter sind mechanisch nicht verbunden", fontsize=11, color="#112431")
    ax.set_xlim(-50, 420)
    ax.set_ylim(-20, 240)
    ax.set_aspect("equal")
    ax.set_title("R5 – Frontansicht: Befestigung rechts, Prallwand links", fontsize=20, color="#112431", pad=14)
    ax.axis("off")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Software": "metriMade deterministic generator"})
    plt.close(fig)


def save_three_side_preview(path: Path, masks: dict, params: dict):
    from matplotlib.patches import RegularPolygon

    panel_w = next(iter(masks.values())).width * float(params["logo_pitch_mm"])
    panel_h = next(iter(masks.values())).height * float(params["logo_pitch_mm"])
    rgba = np.zeros((next(iter(masks.values())).height, next(iter(masks.values())).width, 4), dtype=np.uint8)
    rgba[:] = (242, 242, 237, 0)
    rgb = {
        "#112431": (17, 36, 49, 255),
        "#08777D": (8, 119, 125, 255),
        "#7FD5D3": (127, 213, 211, 255),
        "#C7AB82": (199, 171, 130, 255),
    }
    for color, value in rgb.items():
        rgba[np.asarray(masks[color]) > 0] = value
    labels = ("Vorderseite (+Y)", "Linke Prallseite (+X)", "Rechte Display-/Schraubseite (−X)")
    fig, axes = plt.subplots(1, 3, figsize=(13, 6), facecolor="#F4F1EB")
    logo_bottom = float(params["logo_panel_bottom_z_mm"])
    heights = (float(params["front_wall_height_mm"]), float(params["impact_wall_height_mm"]), float(params["display_lower_wall_height_mm"]))
    panel_widths = (float(params["upper_width_mm"]), float(params["upper_depth_mm"]), float(params["upper_depth_mm"]))
    centers = (
        float(params["logo_panel_center_front_u_mm"]),
        float(params["logo_panel_center_impact_u_mm"]),
        float(params["logo_panel_center_mount_u_mm"]),
    )
    for face_index, (ax, label, face_height, face_width) in enumerate(zip(axes, labels, heights, panel_widths)):
        ax.set_facecolor("#F2F2ED")
        for hx in np.arange(-face_width / 2.0 + 4, face_width / 2.0, 7.0):
            for hz in np.arange(6 + (4 if int((hx + face_width / 2.0) / 7.0) % 2 else 0), face_height - 3, 8.0):
                if face_index == 1 and hz >= float(params["impact_solid_band_start_z_mm"]):
                    continue
                ax.add_patch(RegularPolygon((hx, hz), 6, radius=3.9, orientation=0, fill=False, edgecolor="#C9CDCB", lw=1.4))
        center = centers[face_index]
        extent = [center - panel_w / 2.0, center + panel_w / 2.0, logo_bottom, logo_bottom + panel_h]
        ax.imshow(rgba, extent=extent, origin="upper", interpolation="nearest", zorder=3)
        ax.add_patch(plt.Rectangle((-face_width / 2.0, 0), face_width, face_height, fill=False, edgecolor="#112431", lw=2.2))
        if face_index == 1:
            ax.axhspan(float(params["impact_solid_band_start_z_mm"]), face_height, color="#E5E5E0", zorder=0)
            ax.text(0, face_height - 6, "massive Trefferzone", ha="center", color="#112431", fontsize=8.5)
        else:
            ax.text(0, face_height - 4, "offene Waben", ha="center", color="#112431", fontsize=8.5)
        margin = max(4.0, face_width * 0.08)
        ax.set_xlim(-face_width / 2.0 - margin, face_width / 2.0 + margin)
        ax.set_ylim(-2, max(heights) + 4)
        ax.set_aspect("equal")
        ax.set_title(label, fontsize=13, color="#112431")
        ax.axis("off")
    fig.suptitle("Unverändertes metriMade-Lockup direkt auf glatten Waben · ohne Hintergrundplatte", fontsize=17, color="#112431")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Software": "metriMade deterministic generator"})
    plt.close(fig)


def save_geometry_preview(path: Path, catcher: Mesh, logos: dict):
    """Render three deterministic views of the exact generated mesh."""
    views = (
        (15, 90, "Front: Schrauben rechts (−X)"),
        (18, 18, "Linke Prallwand (+X)"),
        (-28, 90, "Unterseite: freier Durchfall"),
    )
    palette = {
        "#112431": "#112431",
        "#08777D": "#08777D",
        "#7FD5D3": "#7FD5D3",
        "#C7AB82": "#C7AB82",
    }
    fig = plt.figure(figsize=(15, 6), facecolor="#F4F1EB")
    bounds_min, bounds_max = mesh_bounds(catcher)
    for index, (elev, azim, title) in enumerate(views, start=1):
        ax = fig.add_subplot(1, 3, index, projection="3d")
        ax.set_facecolor("#F4F1EB")
        plot_mesh(ax, catcher, "#BFC7C5", alpha=0.68, max_faces=300000)
        for color, mesh in logos.items():
            plot_mesh(ax, mesh, palette[color], alpha=1.0, max_faces=120000)
        ax.set_xlim(bounds_min[0] - 3, bounds_max[0] + 3)
        ax.set_ylim(bounds_min[1] - 3, bounds_max[1] + 3)
        ax.set_zlim(0, bounds_max[2] + 3)
        ax.set_box_aspect((bounds_max[0] - bounds_min[0] + 6, bounds_max[1] - bounds_min[1] + 6, bounds_max[2] - bounds_min[2] + 3))
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title, color="#112431", fontsize=13, pad=8)
        ax.set_axis_off()
    fig.suptitle("R5 – glatte analytische Waben und SVG-Pfadlogo (kein Referenz-Mesh verwendet)", fontsize=18, color="#112431")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Software": "metriMade deterministic generator"})
    plt.close(fig)


def save_catcher_section_preview(path: Path, params: dict):
    from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

    width = float(params["upper_width_mm"])
    wall = float(params["wall_mm"])
    impact_h = float(params["impact_wall_height_mm"])
    mount_h = float(params["display_lower_wall_height_mm"])
    hood_start = float(params["impact_hood_start_z_mm"])
    hood_depth = float(params["impact_hood_depth_mm"])
    fig, axes = plt.subplots(1, 3, figsize=(15, 6), facecolor="#F4F1EB")

    ax = axes[0]
    ax.add_patch(Rectangle((-width / 2.0, 0), wall, mount_h, facecolor="#C9CDCB", edgecolor="#112431", lw=1.8))
    hood = [(width / 2.0 - wall, 0), (width / 2.0, 0), (width / 2.0, hood_start), (width / 2.0 - hood_depth, impact_h), (width / 2.0 - hood_depth - wall, impact_h), (width / 2.0 - wall, hood_start)]
    ax.add_patch(Polygon(hood, closed=True, facecolor="#C9CDCB", edgecolor="#112431", lw=1.8))
    ax.add_patch(FancyArrowPatch((-width / 2.0 - 5, 48), (width / 2.0 - 4, 46), connectionstyle="arc3,rad=-0.08", arrowstyle="-|>", mutation_scale=18, lw=2.5, color="#C7AB82"))
    ax.add_patch(FancyArrowPatch((width / 2.0 - 7, 43), (0, 7), connectionstyle="arc3,rad=0.22", arrowstyle="-|>", mutation_scale=18, lw=2.5, color="#08777D"))
    ax.text(-width / 2.0 - 2, 53, "Wischer / Schrauben\nrechts (−X)", ha="center", fontsize=9, color="#112431")
    ax.text(width / 2.0 - 5, 61, "Prallwand links (+X)\nmit gerundetem Überhang", ha="center", fontsize=9, color="#112431")
    ax.text(0, -5, "Boden vollständig offen", ha="center", color="#08777D", fontsize=10)
    ax.set_title("Frontschnitt: rechts → links → unten", color="#112431")
    ax.set_xlim(-42, 42); ax.set_ylim(-8, 68)

    ax = axes[1]
    ax.add_patch(Rectangle((-width / 2.0, 0), width, impact_h, fill=False, edgecolor="#112431", lw=2.0))
    for hx in np.arange(-width / 2.0 + 5, width / 2.0 - 2, 7.0):
        for hz in np.arange(6, 38, 8.0):
            ax.add_patch(plt.matplotlib.patches.RegularPolygon((hx, hz), 6, radius=3.8, fill=False, edgecolor="#BFC7C5", lw=1.2))
    ax.axhspan(float(params["impact_solid_band_start_z_mm"]), impact_h, color="#E5E5E0", zorder=-1)
    ax.text(0, 48, "geschlossene Trefferzone", ha="center", color="#112431", fontsize=10)
    ax.text(0, 20, "glatte offene Waben", ha="center", color="#08777D", fontsize=10)
    ax.set_title("Linke Prallseite (+X)", color="#112431")
    ax.set_xlim(-36, 36); ax.set_ylim(-3, 64)

    ax = axes[2]
    plate_y0, plate_y1 = float(params["mount_plate_y_min_mm"]), float(params["mount_plate_y_max_mm"])
    plate_z0, plate_z1 = float(params["mount_plate_bottom_z_mm"]), float(params["mount_plate_top_z_mm"])
    ax.add_patch(Rectangle((plate_y0, plate_z0), plate_y1 - plate_y0, plate_z1 - plate_z0, facecolor="#C9CDCB", edgecolor="#112431", lw=2))
    pair_center = float(params["mount_pair_center_z_mm"]); spacing = float(params["mount_hole_spacing_nominal_mm"])
    for center_z in (pair_center - spacing / 2.0, pair_center + spacing / 2.0):
        ax.add_patch(plt.Circle((float(params["mount_slot_center_y_mm"]), center_z), float(params["mount_slot_width_mm"]) / 2.0, facecolor="#F4F1EB", edgecolor="#08777D", lw=2))
    ax.text(0, 46, "Drucker", ha="center", color="#112431", fontsize=11)
    ax.text(17, 67, "2 vertikale Langlöcher\nauf rechter Seite", ha="center", color="#112431", fontsize=10)
    ax.set_title("Rechte Display-/Schraubseite (−X)", color="#112431")
    ax.set_xlim(-24, 27); ax.set_ylim(20, 70)

    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("R5 – Orientierung und Fangweg · glatte Geometrie ohne Voxelmodell", fontsize=18, color="#112431")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Software": "metriMade deterministic generator"})
    plt.close(fig)


def architecture_validation(plan: dict):
    component_ids = {item["id"] for item in plan["components"]}
    interface_ids = {item["id"] for item in plan["interfaces"]}
    checks = {
        "component_ids_unique": len(component_ids) == len(plan["components"]),
        "interface_ids_unique": len(interface_ids) == len(plan["interfaces"]),
        "interface_references_resolve": all(item["a"] in component_ids and item["b"] in component_ids and item["owner"] in component_ids for item in plan["interfaces"]),
        "component_interface_references_resolve": all(set(item["interface_ids"]) <= interface_ids for item in plan["components"]),
        "flow_references_resolve": all(item["from"] in component_ids and item["to"] in component_ids for item in plan["flow_relationships"]),
        "no_catcher_bin_mechanical_interface": not any({item["a"], item["b"]} == {"CATCHER_BODY", "LOWER_BIN"} for item in plan["interfaces"]),
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}


def build(root: Path):
    params_catcher = json.loads((root / "params/catcher.json").read_text())
    params_bin = json.loads((root / "params/lower-bin.json").read_text())
    params_gauge = json.loads((root / "params/mount-gauge.json").read_text())
    plan = json.loads((root / "plan/hybrid-design-plan.json").read_text())
    logo_path = root / "evidence/metrimade-lockup-stacked-color.svg"
    if not logo_path.exists():
        raise FileNotFoundError(f"Supplied logo evidence missing: {logo_path}")

    masks, mask_metrics = render_logo_masks(logo_path, params_catcher)
    catcher, _, catcher_metrics = make_catcher(params_catcher, masks)
    logos, logo_metrics = logo_meshes(logo_path, masks, params_catcher, catcher_metrics["face_x_mm"], catcher_metrics["face_y_mm"])
    lower_bin, bin_metrics = make_bin(params_bin)
    gauge = make_mount_gauge(params_gauge)

    stl_dir, mf_dir = root / "models/stl", root / "models/3mf"
    for stale in (
        stl_dir / "catcher-body-sand.stl",
        stl_dir / "catcher-logo-navy.stl",
        stl_dir / "catcher-logo-teal.stl",
        stl_dir / "catcher-logo-aqua.stl",
        mf_dir / "metriMade-purge-catcher-4color-core.3mf",
        root / "previews/display-side-logo.png",
        root / "previews/catcher-r3-geometry.png",
        root / "previews/catcher-r3-section.png",
        stl_dir / "catcher-body-white-honeycomb.stl",
        stl_dir / "catcher-body-white-open-honeycomb.stl",
        stl_dir / "catcher-logo-navy-3sides.stl",
        stl_dir / "catcher-logo-teal-3sides.stl",
        stl_dir / "catcher-logo-aqua-3sides.stl",
        stl_dir / "catcher-logo-sand-3sides.stl",
        root / "previews/catcher-r4-geometry.png",
        root / "previews/catcher-r4-section.png",
    ):
        stale.unlink(missing_ok=True)
    for stale_report in (
        "fdm-ci-catcher-3mf.json", "fdm-ci-catcher-body.json", "fdm-ci-doctor.json",
        "fdm-ci-gauge-3mf.json", "fdm-ci-lower-bin-3mf.json", "fdm-ci-lower-bin.json",
        "fdm-ci-mount-gauge.json",
    ):
        (root / "reports" / stale_report).unlink(missing_ok=True)
    (root / "reports-autonomy.json").unlink(missing_ok=True)
    meshes = {
        "catcher_body": catcher,
        "catcher_logo_navy": logos["#112431"],
        "catcher_logo_teal": logos["#08777D"],
        "catcher_logo_aqua": logos["#7FD5D3"],
        "catcher_logo_sand": logos["#C7AB82"],
        "lower_bin": lower_bin,
        "mount_fit_gauge": gauge,
    }
    filenames = {
        "catcher_body": "catcher-body-white-smooth-honeycomb.stl",
        "catcher_logo_navy": "catcher-logo-navy-smooth-3sides.stl",
        "catcher_logo_teal": "catcher-logo-teal-smooth-3sides.stl",
        "catcher_logo_aqua": "catcher-logo-aqua-smooth-3sides.stl",
        "catcher_logo_sand": "catcher-logo-sand-smooth-3sides.stl",
        "lower_bin": "lower-bin.stl",
        "mount_fit_gauge": "mount-fit-gauge.stl",
    }
    for key, mesh in meshes.items():
        write_binary_stl(mesh, stl_dir / filenames[key])

    materials = [("white body", "#F2F2EDFF"), ("navy", "#112431FF"), ("teal", "#08777DFF"), ("aqua", "#7FD5D3FF"), ("sand", "#C7AB82FF")]
    write_3mf(
        mf_dir / "metriMade-purge-catcher-3sides-5material-core.3mf",
        "metriMade smooth open-bottom honeycomb purge catcher R5",
        [(catcher, 0), (logos["#112431"], 1), (logos["#08777D"], 2), (logos["#7FD5D3"], 3), (logos["#C7AB82"], 4)],
        materials,
    )
    write_3mf(mf_dir / "lower-bin-core.3mf", "freestanding lower bin R5", [(lower_bin, 0)], [("navy", "#112431FF")])
    write_3mf(mf_dir / "mount-fit-gauge-core.3mf", "vertical pair mount fit gauge R5", [(gauge, 0)], [("gauge", "#7FD5D3FF")])

    save_assembly_preview(root / "previews/assembly-principle.png", catcher, logos, lower_bin)
    save_three_side_preview(root / "previews/three-side-stacked-logo.png", masks, params_catcher)
    save_geometry_preview(root / "previews/catcher-r5-geometry.png", catcher, logos)
    save_catcher_section_preview(root / "previews/catcher-r5-section.png", params_catcher)

    audits = {key: mesh_audit(mesh) for key, mesh in meshes.items()}
    three_mf = [validate_3mf(path) for path in sorted(mf_dir.glob("*.3mf"))]
    arch = architecture_validation(plan)
    density = float(params_catcher["density_petg_g_cm3"])
    logo_keys = ("catcher_logo_navy", "catcher_logo_teal", "catcher_logo_aqua", "catcher_logo_sand")
    mounted_volume = audits["catcher_body"]["metrics"]["signed_volume_mm3"] + sum(audits[key]["metrics"]["signed_volume_mm3"] for key in logo_keys)
    mounted_mass = mounted_volume / 1000.0 * density
    digital_checks = {
        "architecture": arch["status"] == "PASS",
        "all_meshes": all(item["status"] == "PASS" for item in audits.values()),
        "all_3mf": all(item["status"] == "PASS" for item in three_mf),
        "logo_masks_do_not_overlap": logo_metrics["mask_overlap_pixels"] == 0,
        "exact_source_path_count": mask_metrics["source_path_count"] == 13,
        "analytic_logo_path_count": logo_metrics["source_path_count"] == 13,
        "full_viewbox_not_cropped": not mask_metrics["cropped"],
        "logo_on_three_faces": len(logo_metrics["faces"]) == 3,
        "logo_background_removed": not logo_metrics["background_present"],
        "logo_not_voxelized": "no logo voxels" in logo_metrics["geometry_method"],
        "logo_components_have_start_support": logo_metrics["start_support"]["unsupported_components"] == 0,
        "all_four_logo_colors_present": all(np.count_nonzero(np.asarray(mask)) > 0 for mask in masks.values()),
        "body_not_voxelized": not catcher_metrics["body_uses_voxels"],
        "honeycomb_is_through_open": catcher_metrics["honeycomb_is_through_open"],
        "analytic_honeycomb_ribs_present": catcher_metrics["analytic_honeycomb_rib_segments"] > 0,
        "honeycomb_open_area_proxy_above_20_percent": catcher_metrics["panel_open_area_proxy_percent"] > 20.0,
        "catcher_bottom_open": catcher_metrics["drop_probe_occupied_faces"] == 0,
        "catcher_top_open": catcher_metrics["center_top_open"],
        "slot_cut_present": catcher_metrics["mount_slots_count"] == 2,
        "mount_slots_are_vertical_pair": catcher_metrics["mount_slot_axis"] == "vertical pair in right-side plate",
        "mount_side_is_right": catcher_metrics["mount_side_viewed_from_printer_front"] == "right" and catcher_metrics["mount_side_project_axis"] == "-X",
        "impact_side_is_left": catcher_metrics["impact_side_viewed_from_printer_front"] == "left" and catcher_metrics["impact_side_project_axis"] == "+X",
        "solid_impact_band_present": catcher_metrics["impact_solid_band_present"],
        "impact_hood_present": catcher_metrics["impact_hood_depth_mm"] > 0.0,
        "impact_hood_support_free_proxy": catcher_metrics["impact_hood_max_overhang_from_vertical_deg"] <= 45.0,
    }
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "architecture-validation.json").write_text(json.dumps(arch, indent=2) + "\n")
    (reports / "mesh-audit.json").write_text(json.dumps({"status": "PASS" if all(item["status"] == "PASS" for item in audits.values()) else "FAIL", "artifacts": audits}, indent=2) + "\n")
    (reports / "three-mf-validation.json").write_text(json.dumps({"status": "PASS" if all(item["status"] == "PASS" for item in three_mf) else "FAIL", "artifacts": three_mf}, indent=2) + "\n")
    metrics = {
        "catcher": catcher_metrics,
        "logo": {**mask_metrics, **logo_metrics},
        "lower_bin": bin_metrics,
        "mounted_material_volume_cm3": mounted_volume / 1000.0,
        "estimated_mounted_petg_mass_g": mounted_mass,
        "estimated_lower_bin_petg_mass_g": signed_volume(lower_bin) / 1000.0 * float(params_bin["density_petg_g_cm3"]),
        "smooth_honeycomb": {
            "geometry_method": catcher_metrics["geometry_method"],
            "analytic_cells": catcher_metrics["analytic_honeycomb_cells"],
            "analytic_rib_segments": catcher_metrics["analytic_honeycomb_rib_segments"],
            "open_area_proxy_percent": catcher_metrics["panel_open_area_proxy_percent"],
            "slicer_time_and_filament": "NOT_RUN — Anycubic Slicer Next unavailable",
        },
        "revision": "R5",
    }
    (reports / "design-metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    (reports / "source-build-report.json").write_text(json.dumps({
        "report_contract_version": "1.0",
        "tool": "src/generate_purge_catcher.py",
        "status": "PASS" if all(digital_checks.values()) else "FAIL",
        "inputs": ["params/catcher.json", "params/lower-bin.json", "params/mount-gauge.json", "plan/hybrid-design-plan.json", "evidence/metrimade-lockup-stacked-color.svg"],
        "checks": digital_checks,
        "metrics": metrics,
        "limitations": [
            "Anycubic Slicer Next is not installed in the validation runtime; import and sliced-toolpath checks remain NOT_RUN.",
            "Official Anycubic sources do not provide the wiper-side hole spacing or local motion envelope; gauge and physical clearance checks remain required.",
            "The 20.0 mm nominal vertical screw spacing is an image-derived starting value, not an Anycubic specification; the paired slots cover 16.2-23.8 mm and must be checked with the gauge.",
            "Purge fragment velocity and trajectory are undocumented; the 58 mm impact wall and 8 mm inward hood require three supervised purge cycles before unattended use.",
            "Mass values are geometric PETG estimates, not slicer extrusion estimates.",
            "Exact source colors plus a neutral body require five material assignments; four-slot systems need a deliberate color compromise or a separate secondary operation.",
            "The honeycomb cells are true openings. Fine strings or very small fragments can escape sideways; this must be checked during supervised purge tests.",
            "The logo has no background plate and bridges only between intersected honeycomb ribs. The digital first-layer contact proxy passes, but exact slicer bridge paths still require visual layer-preview inspection.",
            "The analytic rib and frame solids overlap inside the single 3MF mesh object. Standards-compliant slicers normally union these volumes during slicing; Anycubic Slicer Next import and layer preview remain mandatory.",
            "The catcher has no floor or storage volume. A separate bin must stand below the 57 x 39 mm clear drop opening.",
        ],
    }, indent=2) + "\n")
    (reports / "environment.json").write_text(json.dumps({"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "pillow": Image.__version__, "matplotlib": matplotlib.__version__}, indent=2) + "\n")

    tracked = [path for path in root.rglob("*") if path.is_file() and path.name != "manifest.json"]
    manifest = {str(path.relative_to(root)): {"sha256": sha256_file(path), "bytes": path.stat().st_size} for path in sorted(tracked)}
    (root / "build/manifest.json").write_text(json.dumps({"schema_version": "1.0", "files": manifest}, indent=2) + "\n")
    print(json.dumps({"status": "PASS" if all(digital_checks.values()) else "FAIL", "mounted_mass_g": mounted_mass, "lower_bin_capacity_l": bin_metrics["usable_capacity_l"], "files": len(manifest)}, indent=2))
    if not all(digital_checks.values()):
        raise SystemExit(1)


def main():
    build(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    main()
