#!/usr/bin/env python3
"""Dependency-light implicit CAD generator for the Tethys Mini ROV.

It uses NumPy plus marching tetrahedra to create smooth, watertight binary STL
meshes.  Dimensions are millimetres.  The generated meshes are design-starting
points: motor hole patterns, cable diameters, and WTE dimensions must be checked
against the purchased revision before printing the full set.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import math
from pathlib import Path
import struct
from typing import Callable

import numpy as np

SDF = Callable[[np.ndarray], np.ndarray]


def box(center, size, angle_deg=0.0) -> SDF:
    center = np.asarray(center, dtype=float)
    half = np.asarray(size, dtype=float) / 2.0
    angle = math.radians(angle_deg)
    ca, sa = math.cos(angle), math.sin(angle)

    def fn(points):
        q = points - center
        if angle_deg:
            x = ca * q[..., 0] + sa * q[..., 1]
            y = -sa * q[..., 0] + ca * q[..., 1]
            q = np.stack((x, y, q[..., 2]), axis=-1)
        d = np.abs(q) - half
        outside = np.linalg.norm(np.maximum(d, 0.0), axis=-1)
        inside = np.minimum(np.max(d, axis=-1), 0.0)
        return outside + inside

    return fn


def cylinder(center, axis, radius, length) -> SDF:
    center = np.asarray(center, dtype=float)
    radial_axes = [index for index in range(3) if index != axis]

    def fn(points):
        q = points - center
        radial = np.sqrt(q[..., radial_axes[0]] ** 2 + q[..., radial_axes[1]] ** 2)
        d_radial = radial - radius
        d_axial = np.abs(q[..., axis]) - length / 2.0
        outside = np.hypot(np.maximum(d_radial, 0.0), np.maximum(d_axial, 0.0))
        inside = np.minimum(np.maximum(d_radial, d_axial), 0.0)
        return outside + inside

    return fn


def ring(center, axis, inner_radius, outer_radius, length) -> SDF:
    center = np.asarray(center, dtype=float)
    radial_axes = [index for index in range(3) if index != axis]

    def fn(points):
        q = points - center
        radial = np.sqrt(q[..., radial_axes[0]] ** 2 + q[..., radial_axes[1]] ** 2)
        return np.maximum.reduce(
            (radial - outer_radius, inner_radius - radial, np.abs(q[..., axis]) - length / 2.0)
        )

    return fn


def capsule_xy(start, end, radius, center_z, thickness) -> SDF:
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    delta = end - start
    length_sq = float(delta @ delta)

    def fn(points):
        xy = points[..., :2]
        t = np.clip(np.sum((xy - start) * delta, axis=-1) / length_sq, 0.0, 1.0)
        closest = start + t[..., None] * delta
        radial = np.linalg.norm(xy - closest, axis=-1) - radius
        axial = np.abs(points[..., 2] - center_z) - thickness / 2.0
        return np.maximum(radial, axial)

    return fn


def union(*shapes: SDF) -> SDF:
    return lambda points: np.minimum.reduce([shape(points) for shape in shapes])


def intersection(*shapes: SDF) -> SDF:
    return lambda points: np.maximum.reduce([shape(points) for shape in shapes])


def difference(base: SDF, *cuts: SDF) -> SDF:
    return lambda points: np.maximum.reduce([base(points)] + [-cut(points) for cut in cuts])


def radial_boxes(radius, length, width, thickness, z, angles=(0, 90, 180, 270)):
    items = []
    for angle in angles:
        radians = math.radians(angle)
        center = (radius * math.cos(radians), radius * math.sin(radians), z)
        items.append(box(center, (length, width, thickness), angle))
    return items


def polar_cylinders(radius, z, hole_radius, length, angles=(0, 90, 180, 270)):
    return [
        cylinder(
            (radius * math.cos(math.radians(angle)), radius * math.sin(math.radians(angle)), z),
            2,
            hole_radius,
            length,
        )
        for angle in angles
    ]


@dataclass(frozen=True)
class Part:
    name: str
    sdf: SDF
    bounds: tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
    pitch: float
    quantity: int
    note: str


def make_parts() -> list[Part]:
    # 10 mm CFK saddle: two identical pieces form an orthogonal corner node.
    saddle_body = box((0, 0, 4), (34, 24, 8))
    saddle = difference(
        saddle_body,
        cylinder((0, 0, 9), 0, 5.35, 40),
        box((-10, 0, 4), (3.4, 18, 12)),
        box((10, 0, 4), (3.4, 18, 12)),
        cylinder((0, 0, 4), 2, 1.7, 12),
    )

    # 75 mm-series WTE cradle.  The nominal contact radius has 0.4 mm clearance.
    cradle_body = box((0, 0, 11), (32, 92, 22))
    cradle = difference(
        cradle_body,
        cylinder((0, 0, 42.4), 0, 38.4, 42),
        box((0, -40, 11), (19, 4.2, 28)),
        box((0, 40, 11), (19, 4.2, 28)),
        cylinder((0, 0, 8), 2, 1.7, 24),
    )

    # 60 mm propeller guard/nozzle: 68 mm clear bore, 78 mm OD.
    nozzle_shell = ring((0, 0, 0), 2, 34.0, 39.0, 52.0)
    rear_interface = ring((0, 0, -24), 2, 7.0, 22.0, 4.0)
    rear_spokes = radial_boxes(28.0, 16.0, 4.2, 4.0, -24)
    front_lugs = polar_cylinders(43.5, 24, 5.5, 4.0)
    rear_lugs = polar_cylinders(43.5, -24, 5.5, 4.0)
    nozzle_positive = union(nozzle_shell, rear_interface, *rear_spokes, *front_lugs, *rear_lugs)
    nozzle_holes = polar_cylinders(43.5, 24, 1.7, 8.0) + polar_cylinders(43.5, -24, 1.7, 8.0)
    nozzle_holes += polar_cylinders(17.5, -24, 2.1, 8.0, angles=(45, 135, 225, 315))
    nozzle = difference(nozzle_positive, *nozzle_holes)

    grid_bars = []
    for offset in np.arange(-30.0, 30.1, 7.5):
        grid_bars.append(intersection(box((0, offset, 0), (68, 2.4, 3.2)), cylinder((0, 0, 0), 2, 34, 5)))
        grid_bars.append(intersection(box((offset, 0, 0), (2.4, 68, 3.2)), cylinder((0, 0, 0), 2, 34, 5)))
    guard_positive = union(ring((0, 0, 0), 2, 34, 39, 3.2), *grid_bars, *polar_cylinders(43.5, 0, 5.5, 3.2))
    front_guard = difference(guard_positive, *polar_cylinders(43.5, 0, 1.7, 8.0))

    adapter = cylinder((0, 0, 0), 2, 22, 4)
    adapter_cuts = [cylinder((0, 0, 0), 2, 6.0, 8)]
    adapter_cuts += polar_cylinders(17.5, 0, 2.1, 8, angles=(0, 90, 180, 270))
    for angle in (45, 135, 225, 315):
        start = (7.5 * math.cos(math.radians(angle)), 7.5 * math.sin(math.radians(angle)))
        end = (11.5 * math.cos(math.radians(angle)), 11.5 * math.sin(math.radians(angle)))
        adapter_cuts.append(capsule_xy(start, end, 1.7, 0, 8))
    motor_adapter = difference(adapter, *adapter_cuts)

    # Two slide-on links keep each horizontal guard parallel to a longitudinal rail.
    rail_link_positive = union(
        ring((0, 0, 0), 2, 39.6, 44.0, 8),
        ring((0, -52, 0), 2, 5.3, 9.5, 8),
        box((0, -39, 0), (18, 26, 8)),
    )
    rail_link = difference(rail_link_positive, box((0, -39, 0), (4, 12, 12)))

    vertical_bridge = difference(
        box((0, 0, 2.5), (100, 32, 5)),
        cylinder((-43.5, 0, 2.5), 2, 1.7, 10),
        cylinder((43.5, 0, 2.5), 2, 1.7, 10),
        cylinder((0, 0, 2.5), 2, 1.7, 10),
        box((-22, 0, 2.5), (22, 18, 8)),
        box((22, 0, 2.5), (22, 18, 8)),
    )

    foam_saddle = difference(
        box((0, 0, 6), (60, 42, 12)),
        cylinder((0, 0, 0), 0, 5.35, 66),
        box((-18, 0, 6), (4.2, 32, 18)),
        box((18, 0, 6), (4.2, 32, 18)),
    )

    cleat_positive = union(
        box((0, 0, 2.5), (80, 34, 5)),
        cylinder((-24, 7, 13.5), 2, 6, 22),
        cylinder((0, -7, 13.5), 2, 6, 22),
        cylinder((24, 7, 13.5), 2, 6, 22),
    )
    tether_cleat = difference(
        cleat_positive,
        cylinder((-34, 0, 2.5), 2, 2.1, 10),
        cylinder((34, 0, 2.5), 2, 2.1, 10),
    )

    tray_positive = union(
        box((0, 0, 1.2), (220, 62, 2.4)),
        box((0, -29.5, 4.5), (220, 3, 9)),
        box((0, 29.5, 4.5), (220, 3, 9)),
    )
    tray_cuts = [box((x, 0, 1.2), (3.4, 48, 5)) for x in (-85, -50, -15, 20, 55, 90)]
    electronics_tray = difference(tray_positive, *tray_cuts)

    camera_positive = union(
        box((0, 0, 1.5), (48, 36, 3)),
        box((22.5, 0, 16), (3, 36, 32)),
    )
    camera_holes = [
        cylinder((-16, -12, 1.5), 2, 1.6, 8),
        cylinder((-16, 12, 1.5), 2, 1.6, 8),
        cylinder((22.5, -10.5, 16), 0, 1.2, 8),
        cylinder((22.5, 10.5, 16), 0, 1.2, 8),
    ]
    camera_bracket = difference(camera_positive, *camera_holes)

    ballast_positive = union(
        box((0, 0, 2), (120, 40, 4)),
        box((0, -18.5, 7), (120, 3, 14)),
        box((0, 18.5, 7), (120, 3, 14)),
    )
    ballast_tray = difference(
        ballast_positive,
        box((-38, 0, 2), (4.2, 30, 8)),
        box((0, 0, 2), (4.2, 30, 8)),
        box((38, 0, 2), (4.2, 30, 8)),
        cylinder((-52, 0, 2), 2, 2.1, 10),
        cylinder((52, 0, 2), 2, 2.1, 10),
    )

    end_plug = union(cylinder((0, 0, 5), 2, 3.85, 10), cylinder((0, 0, 10.8), 2, 5.5, 1.6))

    return [
        Part("tube_saddle", saddle, ((-19, 19), (-14, 14), (-1, 11)), 0.55, 12, "10 mm CFK/GFK rail saddle; use TPU shim and two 4.8 mm zip ties."),
        Part("wte_cradle_75mm", cradle, ((-18, 18), (-48, 48), (-1, 24)), 0.65, 2, "Verify the purchased 75 mm-series tube OD and add rubber strip."),
        Part("thruster_nozzle_60mm", nozzle, ((-51, 51), (-51, 51), (-29, 29)), 0.75, 3, "68 mm clear bore for a nominal 60 mm prop; verify runout and motor geometry."),
        Part("thruster_front_guard", front_guard, ((-51, 51), (-51, 51), (-3, 3)), 0.60, 3, "Nominal square opening 5.1 mm; use M3x8 fasteners."),
        Part("motor_adapter_slotted", motor_adapter, ((-24, 24), (-24, 24), (-3, 3)), 0.50, 3, "Universal starting pattern; measure the actual stationary motor base before use."),
        Part("thruster_rail_link", rail_link, ((-47, 47), (-65, 47), (-5, 5)), 0.70, 4, "Slide-on parallel-axis link for horizontal thrusters; two per thruster."),
        Part("vertical_thruster_bridge", vertical_bridge, ((-52, 52), (-18, 18), (-1, 6)), 0.55, 1, "Bolts to two rear nozzle lugs and a tube saddle; install below the nozzle."),
        Part("foam_saddle", foam_saddle, ((-32, 32), (-23, 23), (-1, 13)), 0.60, 4, "Strap closed-cell EVA/PE foam to the upper rails."),
        Part("tether_strain_relief", tether_cleat, ((-42, 42), (-19, 19), (-1, 26)), 0.60, 1, "Weave tether in an S path; tether load must not reach the penetrator."),
        Part("electronics_tray_75mm", electronics_tray, ((-112, 112), (-33, 33), (-1, 10)), 0.70, 1, "220 x 62 mm nominal tray; verify flange/rail clearance."),
        Part("camera_bracket", camera_bracket, ((-26, 26), (-20, 20), (-1, 34)), 0.55, 1, "Print on its side; nominal Camera Module 3 mounting slots."),
        Part("ballast_tray", ballast_tray, ((-62, 62), (-22, 22), (-1, 16)), 0.60, 1, "Low-mounted stainless ballast holder; straps pass through the three slots."),
        Part("tube_end_plug_8mm", end_plug, ((-7, 7), (-7, 7), (-1, 13)), 0.40, 8, "Epoxy into cleaned tube ends; not a pressure component."),
    ]


_CORNERS = np.asarray(
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
    dtype=int,
)
_TETS = ((0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6))


def polygonise(part: Part):
    axes = [np.arange(lo, hi + part.pitch * 0.5, part.pitch, dtype=np.float32) for lo, hi in part.bounds]
    grid = np.stack(np.meshgrid(*axes, indexing="ij"), axis=-1)
    # A tiny inward iso-level offset avoids zero-valued grid vertices where
    # coplanar CSG faces meet.  Those exact coincidences otherwise create
    # degenerate triangles in marching tetrahedra.  The dimensional change is
    # below 0.001 mm at every configured grid pitch.
    values = (part.sdf(grid) - part.pitch * 1.0e-4).astype(np.float32)
    inside = values <= 0.0
    corners_inside = [inside[dx : inside.shape[0] - 1 + dx, dy : inside.shape[1] - 1 + dy, dz : inside.shape[2] - 1 + dz] for dx, dy, dz in _CORNERS]
    any_inside = np.logical_or.reduce(corners_inside)
    all_inside = np.logical_and.reduce(corners_inside)
    active = np.argwhere(any_inside & ~all_inside)

    ny, nz = len(axes[1]), len(axes[2])
    vertices: list[np.ndarray] = []
    faces: list[tuple[int, int, int]] = []
    edge_cache: dict[tuple[int, int], int] = {}

    def global_id(index):
        return (int(index[0]) * ny + int(index[1])) * nz + int(index[2])

    def edge_vertex(index_a, index_b, value_a, value_b):
        id_a, id_b = global_id(index_a), global_id(index_b)
        key = (id_a, id_b) if id_a < id_b else (id_b, id_a)
        cached = edge_cache.get(key)
        if cached is not None:
            return cached
        point_a = np.asarray((axes[0][index_a[0]], axes[1][index_a[1]], axes[2][index_a[2]]), dtype=float)
        point_b = np.asarray((axes[0][index_b[0]], axes[1][index_b[1]], axes[2][index_b[2]]), dtype=float)
        denom = float(value_a - value_b)
        fraction = 0.5 if abs(denom) < 1e-12 else float(value_a) / denom
        point = point_a + np.clip(fraction, 0.0, 1.0) * (point_b - point_a)
        edge_cache[key] = len(vertices)
        vertices.append(point)
        return len(vertices) - 1

    for cell in active:
        corner_indices = [tuple((cell + offset).tolist()) for offset in _CORNERS]
        corner_values = [float(values[index]) for index in corner_indices]
        for tet in _TETS:
            local_inside = [slot for slot in tet if corner_values[slot] <= 0.0]
            local_outside = [slot for slot in tet if corner_values[slot] > 0.0]
            count = len(local_inside)
            if count in (0, 4):
                continue

            def intersection_vertex(a, b):
                return edge_vertex(corner_indices[a], corner_indices[b], corner_values[a], corner_values[b])

            if count == 1:
                a = local_inside[0]
                faces.append(tuple(intersection_vertex(a, b) for b in local_outside))
            elif count == 3:
                a = local_outside[0]
                tri = tuple(intersection_vertex(a, b) for b in local_inside)
                faces.append((tri[0], tri[2], tri[1]))
            else:
                a, b = local_inside
                c, d = local_outside
                ac, ad = intersection_vertex(a, c), intersection_vertex(a, d)
                bc, bd = intersection_vertex(b, c), intersection_vertex(b, d)
                faces.append((ac, ad, bd))
                faces.append((ac, bd, bc))

    vertices_array = np.asarray(vertices, dtype=np.float64)
    faces_array = np.asarray(faces, dtype=np.int64)
    # Collapse coincident vertices created where the surface hits a grid vertex.
    # Collapse only numerically identical intersections.  If coplanar CSG
    # coincidences remain, main() automatically switches that part to the
    # topology-guaranteed voxel surface extractor below.
    unique_vertices, inverse = np.unique(np.round(vertices_array, 6), axis=0, return_inverse=True)
    faces_array = inverse[faces_array]
    faces_array = faces_array[
        (faces_array[:, 0] != faces_array[:, 1])
        & (faces_array[:, 1] != faces_array[:, 2])
        & (faces_array[:, 2] != faces_array[:, 0])
    ]
    triangles = unique_vertices[faces_array]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    valid = lengths > 1e-10
    faces_array = faces_array[valid]
    normals = normals[valid]
    lengths = lengths[valid]
    unit = normals / lengths[:, None]
    centroids = unique_vertices[faces_array].mean(axis=1)
    epsilon = part.pitch * 0.05
    points_plus = centroids + unit * epsilon
    points_minus = centroids - unit * epsilon
    flip = part.sdf(points_plus) < part.sdf(points_minus)
    faces_array[flip] = faces_array[flip][:, (0, 2, 1)]
    return unique_vertices, faces_array


def voxel_surface(part: Part):
    """Create a guaranteed-closed orthogonal surface from occupied voxels.

    This is a robust fallback for thin coplanar CSG grids where marching
    tetrahedra can retain microscopic cracks.  Its dimensional stair step is
    at most one configured grid pitch and remains below the recommended 0.6 mm
    nozzle diameter for the parts that need it.
    """
    axes = [np.arange(lo + part.pitch / 2.0, hi, part.pitch, dtype=np.float32) for lo, hi in part.bounds]
    grid = np.stack(np.meshgrid(*axes, indexing="ij"), axis=-1)
    occupied = part.sdf(grid) <= 0.0
    shape = occupied.shape
    vertices: list[tuple[float, float, float]] = []
    vertex_map: dict[tuple[int, int, int], int] = {}
    faces: list[tuple[int, int, int]] = []
    origins = np.asarray([bounds[0] for bounds in part.bounds], dtype=float)

    def vertex(index):
        key = tuple(int(value) for value in index)
        if key not in vertex_map:
            vertex_map[key] = len(vertices)
            point = origins + np.asarray(key, dtype=float) * part.pitch
            vertices.append(tuple(point.tolist()))
        return vertex_map[key]

    face_defs = (
        (0, -1, ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
        (0, 1, ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
        (1, -1, ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
        (1, 1, ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
        (2, -1, ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
        (2, 1, ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
    )
    for axis, direction, offsets in face_defs:
        neighbour = np.zeros_like(occupied)
        if direction < 0:
            destination = [slice(None)] * 3
            source = [slice(None)] * 3
            destination[axis] = slice(1, None)
            source[axis] = slice(None, -1)
            neighbour[tuple(destination)] = occupied[tuple(source)]
        else:
            destination = [slice(None)] * 3
            source = [slice(None)] * 3
            destination[axis] = slice(None, -1)
            source[axis] = slice(1, None)
            neighbour[tuple(destination)] = occupied[tuple(source)]
        for cell in np.argwhere(occupied & ~neighbour):
            quad = [vertex(cell + np.asarray(offset, dtype=int)) for offset in offsets]
            faces.append((quad[0], quad[1], quad[2]))
            faces.append((quad[0], quad[2], quad[3]))
    return np.asarray(vertices, dtype=float), np.asarray(faces, dtype=np.int64)


def mesh_metrics(vertices, faces):
    triangles = vertices[faces]
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    area = float(np.linalg.norm(cross, axis=1).sum() / 2.0)
    signed_volume = float(np.einsum("ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])).sum() / 6.0)
    edges = np.sort(
        np.concatenate((faces[:, (0, 1)], faces[:, (1, 2)], faces[:, (2, 0)]), axis=0),
        axis=1,
    )
    _, counts = np.unique(edges, axis=0, return_counts=True)
    return {
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "surface_area_mm2": round(area, 2),
        "solid_volume_cm3": round(abs(signed_volume) / 1000.0, 3),
        "boundary_edges": int(np.count_nonzero(counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(counts > 2)),
        "watertight_topology": bool(np.all(counts == 2)),
    }


def write_binary_stl(path: Path, vertices, faces):
    triangles = vertices[faces].astype(np.float32)
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    normals = normals / np.maximum(lengths[:, None], 1e-20)
    with path.open("wb") as handle:
        handle.write(b"Tethys Mini implicit CAD".ljust(80, b"\0"))
        handle.write(struct.pack("<I", len(faces)))
        for normal, triangle in zip(normals, triangles):
            handle.write(struct.pack("<12fH", *normal, *triangle[0], *triangle[1], *triangle[2], 0))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "stl")
    parser.add_argument("--part", action="append", help="generate only the named part; repeatable")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    selected = set(args.part or [])
    manifest = {"generator": "generate_parts.py", "units": "millimetres", "parts": {}}
    for part in make_parts():
        if selected and part.name not in selected:
            continue
        print(f"Generating {part.name} at {part.pitch:.2f} mm grid ...", flush=True)
        vertices, faces = polygonise(part)
        metrics = mesh_metrics(vertices, faces)
        meshing_method = "marching_tetrahedra"
        if not metrics["watertight_topology"]:
            print(
                f"  microscopic CSG cracks detected ({metrics['boundary_edges']} boundary edges); "
                "using closed voxel fallback",
                flush=True,
            )
            vertices, faces = voxel_surface(part)
            metrics = mesh_metrics(vertices, faces)
            meshing_method = "closed_voxel_fallback"
        metrics.update(
            {
                "quantity": part.quantity,
                "note": part.note,
                "grid_pitch_mm": part.pitch,
                "solid_petg_mass_upper_g_each": round(metrics["solid_volume_cm3"] * 1.27, 1),
                "meshing_method": meshing_method,
            }
        )
        write_binary_stl(args.output / f"{part.name}.stl", vertices, faces)
        manifest["parts"][part.name] = metrics
        print(json.dumps(metrics, sort_keys=True))
    manifest_path = args.output / "mesh_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bad = [name for name, data in manifest["parts"].items() if not data["watertight_topology"]]
    if bad:
        raise SystemExit("Non-watertight output: " + ", ".join(bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
