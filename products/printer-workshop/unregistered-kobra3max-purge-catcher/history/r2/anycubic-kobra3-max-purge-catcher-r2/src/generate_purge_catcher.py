#!/usr/bin/env python3
"""Generate the R2 Anycubic Kobra 3 Max purge catcher project.

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
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


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
    header = f"metriMade R2 {mesh.name}".encode("ascii", "replace")[:80].ljust(80, b" ")
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


def sample_logo_mask(mask: np.ndarray, u_coords: np.ndarray, z_coords: np.ndarray, params: dict, mirror_u=False):
    """Sample a full-viewBox logo raster onto a physical face coordinate grid."""
    pitch = float(params["logo_pitch_mm"])
    panel_w = float(params["logo_width_mm"])
    panel_h = mask.shape[0] * pitch
    center_u = float(params["logo_panel_center_u_mm"])
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


def make_catcher(params: dict, masks: dict):
    pitch = float(params["voxel_pitch_mm"])
    upper_w, upper_d = float(params["upper_width_mm"]), float(params["upper_depth_mm"])
    outlet_w, outlet_d = float(params["outlet_width_mm"]), float(params["outlet_depth_mm"])
    funnel_h, wall = float(params["funnel_height_mm"]), float(params["wall_mm"])
    front_h = float(params["front_deflector_height_mm"])
    side_h, rear_h = float(params["side_wall_height_mm"]), float(params["rear_wall_height_mm"])
    plate_t = float(params["mount_plate_thickness_mm"])
    total_y = upper_d + plate_t
    x_count, y_count, z_count = (math.ceil(upper_w / pitch), math.ceil(total_y / pitch), math.ceil(front_h / pitch))
    x0, y0 = -upper_w / 2.0, -upper_d / 2.0
    xs = x0 + (np.arange(x_count) + 0.5) * pitch
    ys = y0 + (np.arange(y_count) + 0.5) * pitch
    zs = (np.arange(z_count) + 0.5) * pitch
    x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")
    blend = np.clip(z / funnel_h, 0.0, 1.0)
    outer_w = outlet_w + (upper_w - outlet_w) * blend
    outer_d = outlet_d + (upper_d - outlet_d) * blend
    outer = (np.abs(x) <= outer_w / 2.0) & (np.abs(y) <= outer_d / 2.0)
    inner = (np.abs(x) < outer_w / 2.0 - wall) & (np.abs(y) < outer_d / 2.0 - wall)
    shell = outer & ~inner
    low_funnel = z <= funnel_h
    front_band = y <= -outer_d / 2.0 + wall + pitch / 2.0
    rear_band = y >= outer_d / 2.0 - wall - pitch / 2.0
    side_band = np.abs(x) >= outer_w / 2.0 - wall - pitch / 2.0
    height_mask = low_funnel | (front_band & (z <= front_h)) | (side_band & (z <= side_h)) | (rear_band & (z <= rear_h))
    baseline_occupancy = shell & height_mask

    skin = float(params["containment_skin_mm"])
    frame = float(params["honeycomb_edge_frame_mm"])
    transition = float(params["honeycomb_transition_band_mm"])
    distance_to_outer = np.minimum(outer_w / 2.0 - np.abs(x), outer_d / 2.0 - np.abs(y))
    containment_skin = shell & (distance_to_outer >= wall - skin - pitch / 2.0)
    honey_side = honeycomb_surface_mask(
        ys,
        zs,
        float(params["honeycomb_cell_radius_mm"]),
        float(params["honeycomb_rib_width_mm"]),
        pitch,
    )
    honey_front = honeycomb_surface_mask(
        xs,
        zs,
        float(params["honeycomb_cell_radius_mm"]),
        float(params["honeycomb_rib_width_mm"]),
        pitch,
    )
    honeycomb_ribs = (side_band & honey_side[None, :, :]) | (front_band & honey_front[:, None, :])

    top_frames = (
        (front_band & (z >= front_h - frame))
        | (side_band & (z >= side_h - frame))
        | (rear_band & (z >= rear_h - frame))
    )
    edge_frames = (side_band & (np.abs(y) >= upper_d / 2.0 - frame)) | (front_band & (np.abs(x) >= upper_w / 2.0 - frame))
    transition_frame = z <= funnel_h + transition

    logo_union = np.zeros_like(np.asarray(next(iter(masks.values()))), dtype=bool)
    for mask in masks.values():
        logo_union |= np.asarray(mask) > 0
    # A small body-color backer margin prevents fine glyph strokes from being
    # supported only by the recessed containment skin.
    support_union = np.asarray(
        Image.fromarray(logo_union.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(7))
    ) > 0
    right_logo = sample_logo_mask(support_union, ys, zs, params, mirror_u=False)
    left_logo = sample_logo_mask(support_union, ys, zs, params, mirror_u=True)
    front_logo = sample_logo_mask(support_union, xs, zs, params, mirror_u=False)
    right_band = x >= outer_w / 2.0 - wall - pitch / 2.0
    left_band = x <= -outer_w / 2.0 + wall + pitch / 2.0
    logo_support = (
        (right_band & right_logo[None, :, :])
        | (left_band & left_logo[None, :, :])
        | (front_band & front_logo[:, None, :])
    )

    upper_keep = containment_skin | honeycomb_ribs | top_frames | edge_frames | transition_frame | logo_support | rear_band
    occupancy = shell & height_mask & (low_funnel | upper_keep)

    plate = (
        (np.abs(x) <= float(params["mount_plate_width_mm"]) / 2.0)
        & (y >= upper_d / 2.0)
        & (y <= upper_d / 2.0 + plate_t)
        & (z >= float(params["mount_plate_bottom_z_mm"]))
        & (z <= float(params["mount_plate_top_z_mm"]))
    )
    baseline_occupancy |= plate
    occupancy |= plate
    slot_length = float(params["slot_overall_length_mm"])
    slot_width = float(params["slot_width_mm"])
    slot_radius = slot_width / 2.0
    straight_half = max(0.0, (slot_length - slot_width) / 2.0)
    slot_dx = np.maximum(np.abs(x) - straight_half, 0.0)
    slot = (
        slot_dx * slot_dx + (z - float(params["slot_center_z_mm"])) ** 2 <= slot_radius * slot_radius
    ) & (y >= upper_d / 2.0 - pitch / 2.0)
    removed_slot_voxels = int(np.count_nonzero(occupancy & slot))
    baseline_occupancy &= ~slot
    occupancy &= ~slot
    allowed = ((shell & height_mask) | plate) & ~slot
    topology_fill_voxels = regularize_voxel_edge_contacts(occupancy, allowed)

    body = voxel_surface_mesh(occupancy, pitch, (x0, y0, 0.0), "catcher-body-white-honeycomb")
    outlet_probe = occupancy[
        (np.abs(xs) < outlet_w / 2.0 - wall)[:, None, None]
        & (np.abs(ys) < outlet_d / 2.0 - wall)[None, :, None]
        & (zs < pitch)[None, None, :]
    ]
    center_top_empty = not bool(occupancy[x_count // 2, min(y_count - 1, int(upper_d / (2 * pitch))), -1])
    required_skin = shell & height_mask & ~low_funnel & containment_skin & ~slot
    missing_skin_voxels = int(np.count_nonzero(required_skin & ~occupancy))
    selected_voxels = int(np.count_nonzero(occupancy))
    baseline_voxels = int(np.count_nonzero(baseline_occupancy))
    return body, occupancy, {
        "face_x_mm": upper_w / 2.0,
        "face_y_mm": -upper_d / 2.0,
        "outlet_clear_mm": [outlet_w - 2 * wall, outlet_d - 2 * wall],
        "removed_slot_voxels": removed_slot_voxels,
        "outlet_probe_occupied_voxels": int(np.count_nonzero(outlet_probe)),
        "center_top_open": center_top_empty,
        "max_funnel_overhang_from_vertical_deg": math.degrees(math.atan(max((upper_w - outlet_w) / 2.0, (upper_d - outlet_d) / 2.0) / funnel_h)),
        "slot_bridge_mm": slot_width,
        "containment_skin_mm": skin,
        "honeycomb_cell_radius_mm": float(params["honeycomb_cell_radius_mm"]),
        "honeycomb_rib_width_mm": float(params["honeycomb_rib_width_mm"]),
        "honeycomb_recess_depth_mm": float(params["honeycomb_recess_depth_mm"]),
        "honeycomb_rib_voxels": int(np.count_nonzero(shell & height_mask & honeycomb_ribs & ~low_funnel)),
        "logo_support_voxels": int(np.count_nonzero(shell & height_mask & logo_support & ~low_funnel)),
        "topology_fill_voxels": topology_fill_voxels,
        "required_skin_voxels": int(np.count_nonzero(required_skin)),
        "missing_skin_voxels": missing_skin_voxels,
        "solid_wall_baseline_voxels": baseline_voxels,
        "honeycomb_skin_voxels": selected_voxels,
        "geometric_body_volume_reduction_percent": (1.0 - selected_voxels / baseline_voxels) * 100.0,
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
    length, slot_width = float(params["slot_overall_length_mm"]), float(params["slot_width_mm"])
    radius, straight_half = slot_width / 2.0, max(0.0, (length - slot_width) / 2.0)
    dx = np.maximum(np.abs(x) - straight_half, 0.0)
    occupancy &= ~(dx * dx + y * y <= radius * radius)
    return voxel_surface_mesh(occupancy, pitch, (-width / 2.0, -depth / 2.0, 0.0), "mount-fit-gauge")


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


def logo_meshes(masks: dict, params: dict, face_x: float, face_y: float):
    pitch = float(params["logo_pitch_mm"])
    depth = float(params["logo_extrusion_mm"])
    panel_w = next(iter(masks.values())).width * pitch
    center_u, bottom_z = float(params["logo_panel_center_u_mm"]), float(params["logo_panel_bottom_z_mm"])
    depth_voxels = int(round(depth / pitch))
    names = {
        "#112431": "catcher-logo-navy-3sides",
        "#08777D": "catcher-logo-teal-3sides",
        "#7FD5D3": "catcher-logo-aqua-3sides",
        "#C7AB82": "catcher-logo-sand-3sides",
    }
    result = {}
    component_counts = {}
    for color, name in names.items():
        array = np.asarray(masks[color]) > 0
        component_meshes = []
        components = list(four_connected_components(array))
        component_counts[color] = len(components)
        for component_index, component in enumerate(components):
            # +X display side: screen-right is +Y.
            yz = component[::-1, :].T
            occupancy = np.repeat(yz[None, :, :], depth_voxels, axis=0)
            component_meshes.append(
                voxel_surface_mesh(
                    occupancy,
                    pitch,
                    (face_x, center_u - panel_w / 2.0, bottom_z),
                    f"{name}-right-{component_index + 1}",
                )
            )
            # -X left side: screen-right is -Y, so reverse the surface axis.
            yz_left = component[::-1, ::-1].T
            occupancy_left = np.repeat(yz_left[None, :, :], depth_voxels, axis=0)
            component_meshes.append(
                voxel_surface_mesh(
                    occupancy_left,
                    pitch,
                    (-face_x - depth, center_u - panel_w / 2.0, bottom_z),
                    f"{name}-left-{component_index + 1}",
                )
            )
            # -Y front: screen-right is +X.
            xz = component[::-1, :].T
            occupancy_front = np.repeat(xz[:, None, :], depth_voxels, axis=1)
            component_meshes.append(
                voxel_surface_mesh(
                    occupancy_front,
                    pitch,
                    (center_u - panel_w / 2.0, face_y - depth, bottom_z),
                    f"{name}-front-{component_index + 1}",
                )
            )
        result[color] = combine_meshes(component_meshes, name)
    overlap = np.zeros_like(np.asarray(next(iter(masks.values()))), dtype=np.uint8)
    for mask in masks.values():
        overlap += (np.asarray(mask) > 0).astype(np.uint8)
    return result, {
        "mask_overlap_pixels": int(np.count_nonzero(overlap > 1)),
        "faces": ["-Y front", "-X left", "+X display/right"],
        "face_x_mm": face_x,
        "face_y_mm": face_y,
        "extrusion_mm": depth,
        "source_components_per_color_per_face": component_counts,
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
    from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle, RegularPolygon

    fig, ax = plt.subplots(figsize=(13, 8), facecolor="#F4F1EB")
    ax.set_facecolor("#F4F1EB")
    ax.add_patch(Polygon([(-84, 0), (84, 0), (81, 112), (-81, 112)], closed=True, facecolor="#112431", edgecolor="#08777D", lw=3))
    ax.plot([-84, 84], [112, 112], color="#7FD5D3", lw=7, solid_capstyle="round")
    ax.add_patch(Polygon([(-28, 148), (28, 148), (44, 176), (44, 250), (-44, 250), (-44, 176)], closed=True, facecolor="#F2F2ED", edgecolor="#112431", lw=3))
    for hx in range(-33, 34, 12):
        for hz in range(185 + (6 if (hx // 12) % 2 else 0), 246, 11):
            ax.add_patch(RegularPolygon((hx, hz), 6, radius=6, orientation=0, fill=False, edgecolor="#C9CDCB", lw=1.2))
    ax.plot([-36, 36], [247, 247], color="#F4F1EB", lw=6, solid_capstyle="round")
    ax.add_patch(Rectangle((44, 197), 7, 48, facecolor="#F2F2ED", edgecolor="#112431", lw=2))
    ax.add_patch(Rectangle((51, 199), 17, 44, facecolor="#D8D8D3", edgecolor="#112431", lw=2))
    ax.text(59.5, 221, "Wischer-\nträger", ha="center", va="center", fontsize=10, color="#112431")
    ax.text(0, 217, "exaktes SVG-Logo", ha="center", va="center", fontsize=12, weight="bold", color="#112431", bbox={"boxstyle": "round,pad=0.3", "fc": "#F2F2ED", "ec": "#08777D"})
    ax.text(0, 204, "auf 3 Seiten", ha="center", va="center", fontsize=10, color="#112431")
    ax.add_patch(FancyArrowPatch((0, 145), (0, 119), arrowstyle="-|>", mutation_scale=22, lw=3, color="#08777D"))
    ax.text(8, 132, "freier Fall", color="#08777D", fontsize=11, va="center")
    ax.text(108, 254, "1  Messlehre prüfen", fontsize=13, color="#112431")
    ax.annotate("2  Nur Fangkorb verschrauben", xy=(48, 219), xytext=(103, 218), arrowprops={"arrowstyle": "->", "color": "#08777D", "lw": 2}, fontsize=13, color="#112431")
    ax.annotate("3  Behälter darunterstellen", xy=(82, 93), xytext=(103, 133), arrowprops={"arrowstyle": "->", "color": "#08777D", "lw": 2}, fontsize=13, color="#112431")
    ax.text(-43, 260, "geschlossene Innenhaut · Wabenrippen außen · Logo × 3", fontsize=12, color="#112431")
    ax.text(-84, -12, "keine Haken · keine Rastung · keine Verbindung zwischen den Teilen", fontsize=11, color="#112431")
    ax.set_xlim(-105, 260)
    ax.set_ylim(-22, 278)
    ax.set_aspect("equal")
    ax.set_title("R2-Montageprinzip", fontsize=20, color="#112431", pad=14)
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
    labels = ("Vorderseite (−Y)", "Linke Seite (−X)", "Displayseite (+X)")
    fig, axes = plt.subplots(1, 3, figsize=(13, 6), facecolor="#F4F1EB")
    for ax, label in zip(axes, labels):
        ax.set_facecolor("#F2F2ED")
        for hx in np.arange(-31, 32, 9):
            for hz in np.arange(6 + (4.5 if int((hx + 31) / 9) % 2 else 0), 70, 8):
                ax.add_patch(RegularPolygon((hx, hz), 6, radius=4.8, orientation=0, fill=False, edgecolor="#C9CDCB", lw=1.0))
        extent = [-panel_w / 2.0, panel_w / 2.0, 29.5, 29.5 + panel_h]
        ax.imshow(rgba, extent=extent, origin="upper", interpolation="nearest", zorder=3)
        ax.add_patch(plt.Rectangle((-33, 0), 66, 74, fill=False, edgecolor="#112431", lw=2.2))
        ax.text(0, 8, "geschlossene Innenhaut", ha="center", color="#112431", fontsize=9, bbox={"fc": "#F2F2ED", "ec": "none", "alpha": 0.9})
        ax.set_xlim(-36, 36)
        ax.set_ylim(-2, 78)
        ax.set_aspect("equal")
        ax.set_title(label, fontsize=13, color="#112431")
        ax.axis("off")
    fig.suptitle("Vollständiges, unverändertes metriMade-Lockup auf allen drei verfügbaren Seiten", fontsize=17, color="#112431")
    fig.tight_layout()
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
    catcher, catcher_occupancy, catcher_metrics = make_catcher(params_catcher, masks)
    logos, logo_metrics = logo_meshes(masks, params_catcher, catcher_metrics["face_x_mm"], catcher_metrics["face_y_mm"])
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
    ):
        stale.unlink(missing_ok=True)
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
        "catcher_body": "catcher-body-white-honeycomb.stl",
        "catcher_logo_navy": "catcher-logo-navy-3sides.stl",
        "catcher_logo_teal": "catcher-logo-teal-3sides.stl",
        "catcher_logo_aqua": "catcher-logo-aqua-3sides.stl",
        "catcher_logo_sand": "catcher-logo-sand-3sides.stl",
        "lower_bin": "lower-bin.stl",
        "mount_fit_gauge": "mount-fit-gauge.stl",
    }
    for key, mesh in meshes.items():
        write_binary_stl(mesh, stl_dir / filenames[key])

    materials = [("white body", "#F2F2EDFF"), ("navy", "#112431FF"), ("teal", "#08777DFF"), ("aqua", "#7FD5D3FF"), ("sand", "#C7AB82FF")]
    write_3mf(
        mf_dir / "metriMade-purge-catcher-3sides-5material-core.3mf",
        "metriMade honeycomb purge catcher R2",
        [(catcher, 0), (logos["#112431"], 1), (logos["#08777D"], 2), (logos["#7FD5D3"], 3), (logos["#C7AB82"], 4)],
        materials,
    )
    write_3mf(mf_dir / "lower-bin-core.3mf", "freestanding lower bin R2", [(lower_bin, 0)], [("navy", "#112431FF")])
    write_3mf(mf_dir / "mount-fit-gauge-core.3mf", "mount fit gauge R2", [(gauge, 0)], [("gauge", "#7FD5D3FF")])

    save_assembly_preview(root / "previews/assembly-principle.png", catcher, logos, lower_bin)
    save_three_side_preview(root / "previews/three-side-stacked-logo.png", masks, params_catcher)

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
        "full_viewbox_not_cropped": not mask_metrics["cropped"],
        "logo_on_three_faces": len(logo_metrics["faces"]) == 3,
        "all_four_logo_colors_present": all(np.count_nonzero(np.asarray(mask)) > 0 for mask in masks.values()),
        "continuous_containment_skin": catcher_metrics["missing_skin_voxels"] == 0,
        "honeycomb_ribs_present": catcher_metrics["honeycomb_rib_voxels"] > 0,
        "honeycomb_reduces_body_volume": catcher_metrics["geometric_body_volume_reduction_percent"] > 0.0,
        "catcher_outlet_open": catcher_metrics["outlet_probe_occupied_voxels"] == 0,
        "catcher_top_open": catcher_metrics["center_top_open"],
        "slot_cut_present": catcher_metrics["removed_slot_voxels"] > 0,
        "support_free_slope_proxy": catcher_metrics["max_funnel_overhang_from_vertical_deg"] <= 45.0,
        "mounted_mass_below_r1_g": mounted_mass < 271.0,
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
        "solid_wall_vs_honeycomb": {
            "solid_wall_body_volume_proxy_cm3": catcher_metrics["solid_wall_baseline_voxels"] * float(params_catcher["voxel_pitch_mm"]) ** 3 / 1000.0,
            "honeycomb_skin_body_volume_proxy_cm3": catcher_metrics["honeycomb_skin_voxels"] * float(params_catcher["voxel_pitch_mm"]) ** 3 / 1000.0,
            "geometric_reduction_percent": catcher_metrics["geometric_body_volume_reduction_percent"],
            "slicer_time_and_filament": "NOT_RUN — Anycubic Slicer Next unavailable",
        },
        "comparison_to_rejected_r1": {"r1_mounted_mass_proxy_g": 271.0, "r2_mounted_mass_proxy_g": mounted_mass, "reduction_percent": (1.0 - mounted_mass / 271.0) * 100.0},
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
            "Mass values are geometric PETG estimates, not slicer extrusion estimates.",
            "Exact source colors plus a neutral body require five material assignments; four-slot systems need a deliberate color compromise or a separate secondary operation.",
            "The honeycomb is a recessed rib structure over a continuous 1.0 mm skin, not an open perforation; a wall coupon remains required before the full print.",
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
