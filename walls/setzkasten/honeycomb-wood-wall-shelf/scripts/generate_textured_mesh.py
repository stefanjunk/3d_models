#!/usr/bin/env python3
"""Generate the final watertight, wood-engraved honeycomb module.

The structural master remains a compact B-Rep/STEP. This script samples only
the visible surface families and creates the dense printable mesh directly,
avoiding a high-face-count mesh-to-BRep conversion or a global voxel remesh.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image
from scipy.spatial import Delaunay


PROJECT_DIR = Path(__file__).resolve().parents[1]


def smoothstep01(value: np.ndarray | float) -> np.ndarray | float:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def regular_hex(radius: float) -> np.ndarray:
    angles = np.arange(6, dtype=np.float64) * math.pi / 3.0
    return np.column_stack((radius * np.cos(angles), radius * np.sin(angles)))


def polygon_boundary_samples(points: np.ndarray, segments_per_side: int) -> np.ndarray:
    samples: list[np.ndarray] = []
    for index in range(len(points)):
        start = points[index]
        end = points[(index + 1) % len(points)]
        for step in range(segments_per_side):
            samples.append(start + (end - start) * (step / segments_per_side))
    return np.asarray(samples, dtype=np.float64)


def circle_polygon(center: tuple[float, float], radius: float, segments: int = 64) -> np.ndarray:
    angles = np.arange(segments, dtype=np.float64) * 2.0 * math.pi / segments
    return np.column_stack(
        (center[0] + radius * np.cos(angles), center[1] + radius * np.sin(angles))
    )


def mounting_ear_polygon(
    center: tuple[float, float],
    radius: float,
    neck_width: float,
    inner_top_y: float,
    arc_segments: int = 72,
) -> np.ndarray:
    """Return a circular mounting ear with two tangent gussets to the top frame."""
    half_neck = neck_width / 2.0
    if not (0.0 < half_neck < radius):
        raise ValueError("ear neck half-width must be smaller than the ear radius")
    cx, cy = center
    if not (cy < inner_top_y):
        raise ValueError("mounting ear center must sit below the inner top edge")
    external = np.asarray([half_neck, inner_top_y - cy], dtype=np.float64)
    distance_squared = float(np.dot(external, external))
    if distance_squared <= radius * radius:
        raise ValueError("mounting-ear neck corners must sit outside the circular pad")
    base = (radius * radius / distance_squared) * external
    tangent_scale = (
        radius * math.sqrt(distance_squared - radius * radius) / distance_squared
    )
    perpendicular = np.asarray([-external[1], external[0]], dtype=np.float64)
    right_tangent = base - tangent_scale * perpendicular
    right_angle = math.atan2(float(right_tangent[1]), float(right_tangent[0]))
    left_angle = math.pi - right_angle
    angles = np.linspace(left_angle, 2.0 * math.pi + right_angle, arc_segments + 1)
    arc = np.column_stack((cx + radius * np.cos(angles), cy + radius * np.sin(angles)))
    return np.vstack(
        (
            np.asarray([[cx - half_neck, inner_top_y]], dtype=np.float64),
            arc,
            np.asarray([[cx + half_neck, inner_top_y]], dtype=np.float64),
        )
    )


def top_attachment_intervals(
    inner: np.ndarray,
    mounting: dict,
) -> list[tuple[float, float, tuple[float, float]]]:
    """Map mounting-neck spans to normalized coordinates on the top inner edge."""
    start = inner[1]
    end = inner[2]
    width = float(start[0] - end[0])
    half_neck = float(mounting["ear_neck_width"]) / 2.0
    intervals: list[tuple[float, float, tuple[float, float]]] = []
    for raw_center in mounting["hole_centers"]:
        center = tuple(map(float, raw_center))
        right_x = center[0] + half_neck
        left_x = center[0] - half_neck
        t0 = (start[0] - right_x) / width
        t1 = (start[0] - left_x) / width
        if not (0.0 < t0 < t1 < 1.0):
            raise ValueError("mounting ear neck must lie strictly inside the top inner edge")
        intervals.append((float(t0), float(t1), center))
    intervals.sort(key=lambda value: value[0])
    for first, second in zip(intervals, intervals[1:]):
        if first[1] >= second[0]:
            raise ValueError("mounting ear necks overlap")
    return intervals


def top_side_patches(
    intervals: list[tuple[float, float, tuple[float, float]]],
    ear_thickness: float,
) -> list[tuple[float, float, float]]:
    patches: list[tuple[float, float, float]] = []
    cursor = 0.0
    for t0, t1, _center in intervals:
        if t0 > cursor:
            patches.append((cursor, t0, 0.0))
        patches.append((t0, t1, ear_thickness))
        cursor = t1
    if cursor < 1.0:
        patches.append((cursor, 1.0, 0.0))
    return patches


def side_tangent_values(
    side: int,
    segments_per_side: int,
    attachment_intervals: list[tuple[float, float, tuple[float, float]]] | None = None,
) -> np.ndarray:
    values = np.linspace(0.0, 1.0, segments_per_side + 1)
    if side == 1 and attachment_intervals:
        extras = np.asarray(
            [value for interval in attachment_intervals for value in interval[:2]],
            dtype=np.float64,
        )
        values = np.unique(np.concatenate((values, extras)))
    return values


def points_in_polygon(points: np.ndarray, polygon: np.ndarray) -> np.ndarray:
    """Vectorized even/odd test; probes are triangle interiors, not boundaries."""
    x = points[:, 0]
    y = points[:, 1]
    inside = np.zeros(len(points), dtype=bool)
    previous = polygon[-1]
    for current in polygon:
        x1, y1 = previous
        x2, y2 = current
        crossing = (y1 > y) != (y2 > y)
        denominator = y2 - y1
        if abs(denominator) < 1e-15:
            denominator = 1e-15
        x_cross = (x2 - x1) * (y - y1) / denominator + x1
        inside ^= crossing & (x < x_cross)
        previous = current
    return inside


def domain_mask(probes: np.ndarray, outer: np.ndarray, holes: list[np.ndarray]) -> np.ndarray:
    mask = points_in_polygon(probes, outer)
    for hole in holes:
        mask &= ~points_in_polygon(probes, hole)
    return mask


def triangulate_plane_with_holes(
    outer: np.ndarray,
    holes: list[np.ndarray],
    boundary_points: np.ndarray,
    grid_pitch: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Delaunay triangulation filtered by centroid and edge-midpoint probes."""
    mins = outer.min(axis=0)
    maxs = outer.max(axis=0)
    xs = np.arange(mins[0] + grid_pitch, maxs[0], grid_pitch)
    ys = np.arange(mins[1] + grid_pitch, maxs[1], grid_pitch)
    gx, gy = np.meshgrid(xs, ys, indexing="xy")
    grid = np.column_stack((gx.ravel(), gy.ravel()))
    grid = grid[domain_mask(grid, outer, holes)]
    all_points = np.vstack([boundary_points, *holes, grid])
    quantized = np.round(all_points / 1e-8).astype(np.int64)
    _, unique_indices = np.unique(quantized, axis=0, return_index=True)
    all_points = all_points[np.sort(unique_indices)]

    triangulation = Delaunay(all_points)
    candidates = triangulation.simplices.astype(np.int64)
    tri_points = all_points[candidates]
    # Boundary midpoints lie exactly on the polygon and an even/odd test can
    # classify alternate edges differently. Dense circular constraint points
    # and the convex outer core make centroid filtering deterministic here.
    probes = tri_points.mean(axis=1)
    keep = domain_mask(probes, outer, holes)
    return all_points, candidates[keep]


class HeightMap:
    def __init__(self, path: Path) -> None:
        raw = np.asarray(Image.open(path))
        if raw.ndim == 3:
            raw = raw[..., :3].astype(np.float32).mean(axis=2)
        raw = raw.astype(np.float32)
        maximum = float(raw.max())
        if maximum > 1.0:
            raw /= 65535.0 if maximum > 255.0 else 255.0
        self.values = np.clip(raw, 0.0, 1.0)
        self.height, self.width = self.values.shape

    def sample_periodic(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        x = np.mod(u, 1.0) * self.width
        y = np.mod(v, 1.0) * self.height
        x0 = np.floor(x).astype(np.int64) % self.width
        y0 = np.floor(y).astype(np.int64) % self.height
        x1 = (x0 + 1) % self.width
        y1 = (y0 + 1) % self.height
        fx = (x - np.floor(x)).astype(np.float32)
        fy = (y - np.floor(y)).astype(np.float32)
        a = self.values[y0, x0] * (1.0 - fx) + self.values[y0, x1] * fx
        b = self.values[y1, x0] * (1.0 - fx) + self.values[y1, x1] * fx
        return a * (1.0 - fy) + b * fy


class MeshBuilder:
    def __init__(self) -> None:
        self.vertices: list[tuple[float, float, float]] = []
        self.faces: list[tuple[int, int, int]] = []

    def add_surface_grid(self, grid: np.ndarray) -> None:
        rows, columns, _ = grid.shape
        start = len(self.vertices)
        self.vertices.extend(map(tuple, grid.reshape(-1, 3)))
        for row in range(rows - 1):
            for column in range(columns - 1):
                a = start + row * columns + column
                b = a + 1
                c = a + columns
                d = c + 1
                self.faces.append((a, b, d))
                self.faces.append((a, d, c))

    def add_triangles(self, points: np.ndarray, faces: np.ndarray, z: float) -> None:
        start = len(self.vertices)
        self.vertices.extend((float(x), float(y), float(z)) for x, y in points)
        self.faces.extend(tuple(int(value) + start for value in face) for face in faces)

    def add_triangles_3d(self, points: np.ndarray, faces: np.ndarray) -> None:
        start = len(self.vertices)
        self.vertices.extend((float(x), float(y), float(z)) for x, y, z in points)
        self.faces.extend(tuple(int(value) + start for value in face) for face in faces)

    def add_ring_surface(
        self,
        lower: np.ndarray,
        upper: np.ndarray,
    ) -> None:
        if len(lower) != len(upper):
            raise ValueError("Ring boundaries must have equal samples")
        start = len(self.vertices)
        self.vertices.extend((float(x), float(y), float(z)) for x, y, z in lower)
        self.vertices.extend((float(x), float(y), float(z)) for x, y, z in upper)
        count = len(lower)
        for index in range(count):
            nxt = (index + 1) % count
            self.faces.append((start + index, start + nxt, start + count + nxt))
            self.faces.append((start + index, start + count + nxt, start + count + index))

    def finalized(self, merge_tolerance: float = 1e-6) -> tuple[np.ndarray, np.ndarray, dict]:
        vertices = np.asarray(self.vertices, dtype=np.float64)
        faces = np.asarray(self.faces, dtype=np.int64)
        quantized = np.round(vertices / merge_tolerance).astype(np.int64)
        mapping: dict[tuple[int, int, int], int] = {}
        remap = np.empty(len(vertices), dtype=np.int64)
        merged: list[np.ndarray] = []
        for index, key_array in enumerate(quantized):
            key = tuple(int(value) for value in key_array)
            target = mapping.get(key)
            if target is None:
                target = len(merged)
                mapping[key] = target
                merged.append(vertices[index])
            remap[index] = target
        faces = remap[faces]
        nondegenerate = (
            (faces[:, 0] != faces[:, 1])
            & (faces[:, 1] != faces[:, 2])
            & (faces[:, 2] != faces[:, 0])
        )
        faces = faces[nondegenerate]
        vertices = np.asarray(merged, dtype=np.float64)
        faces, orientation_report = orient_mesh(vertices, faces)
        report = mesh_report(vertices, faces)
        report.update(orientation_report)
        return vertices, faces, report


def orient_mesh(vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, dict]:
    edge_uses: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for face_index, face in enumerate(faces):
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            key = (int(min(a, b)), int(max(a, b)))
            direction = 1 if (a, b) == key else -1
            edge_uses[key].append((face_index, direction))

    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(len(faces))]
    for uses in edge_uses.values():
        if len(uses) == 2:
            (first, first_dir), (second, second_dir) = uses
            relation = -first_dir * second_dir
            adjacency[first].append((second, relation))
            adjacency[second].append((first, relation))

    orientation = np.zeros(len(faces), dtype=np.int8)
    components: list[list[int]] = []
    conflicts = 0
    for start in range(len(faces)):
        if orientation[start] != 0:
            continue
        orientation[start] = 1
        component: list[int] = []
        queue: deque[int] = deque([start])
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor, relation in adjacency[current]:
                expected = orientation[current] * relation
                if orientation[neighbor] == 0:
                    orientation[neighbor] = expected
                    queue.append(neighbor)
                elif orientation[neighbor] != expected:
                    conflicts += 1
        components.append(component)

    oriented = faces.copy()
    flip = orientation == -1
    oriented[flip, 1], oriented[flip, 2] = oriented[flip, 2].copy(), oriented[flip, 1].copy()
    component_volumes: list[float] = []
    for component in components:
        indices = np.asarray(component, dtype=np.int64)
        tri = vertices[oriented[indices]]
        volume = float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6.0)
        if volume < 0:
            oriented[indices, 1], oriented[indices, 2] = (
                oriented[indices, 2].copy(),
                oriented[indices, 1].copy(),
            )
            volume = -volume
        component_volumes.append(volume)
    return oriented, {
        "orientation_conflicts": int(conflicts),
        "oriented_components": len(components),
        "component_signed_volumes_mm3": component_volumes,
    }


def mesh_report(vertices: np.ndarray, faces: np.ndarray) -> dict:
    edge_uses: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for face in faces:
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            key = (int(min(a, b)), int(max(a, b)))
            direction = 1 if (a, b) == key else -1
            edge_uses[key].append((int(a), int(b)))
    boundary = sum(len(uses) == 1 for uses in edge_uses.values())
    nonmanifold = sum(len(uses) > 2 for uses in edge_uses.values())
    inconsistent = sum(
        len(uses) == 2 and uses[0] == uses[1] for uses in edge_uses.values()
    )
    tri = vertices[faces]
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    double_areas = np.linalg.norm(cross, axis=1)
    signed_volume = float(
        np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6.0
    )
    return {
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "bounds_min_mm": vertices.min(axis=0).tolist(),
        "bounds_max_mm": vertices.max(axis=0).tolist(),
        "bounds_size_mm": np.ptp(vertices, axis=0).tolist(),
        "signed_volume_mm3": signed_volume,
        "boundary_edges": int(boundary),
        "nonmanifold_edges": int(nonmanifold),
        "inconsistent_winding_edges": int(inconsistent),
        "degenerate_triangles": int(np.count_nonzero(double_areas < 1e-10)),
        "watertight": bool(boundary == 0 and nonmanifold == 0),
    }


def write_binary_stl(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        header = b"Honeycomb wood wall shelf - generated mesh"
        handle.write(header.ljust(80, b"\0")[:80])
        handle.write(struct.pack("<I", len(faces)))
        for face in faces:
            triangle = vertices[face]
            normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
            length = float(np.linalg.norm(normal))
            if length > 0:
                normal /= length
            record = np.concatenate((normal, triangle.reshape(-1))).astype("<f4")
            handle.write(record.tobytes())
            handle.write(struct.pack("<H", 0))


def add_textured_walls(
    mesh: MeshBuilder,
    heightmap: HeightMap,
    outer: np.ndarray,
    inner: np.ndarray,
    depth: float,
    back: float,
    relief_depth: float,
    pitch: float,
    edge_taper: float,
    wall_depth_repeat: float,
    wall_perimeter_repeat: float,
    open_mounting: dict | None = None,
) -> int:
    side_length = float(np.linalg.norm(outer[1] - outer[0]))
    tangential_segments = max(2, math.ceil(side_length / pitch))
    outer_z_segments = max(2, math.ceil(depth / pitch))
    attachment_intervals = (
        top_attachment_intervals(inner, open_mounting) if open_mounting is not None else []
    )
    if open_mounting is not None:
        global_inner_z = np.unique(
            np.concatenate(
                (
                    np.linspace(0.0, depth, outer_z_segments + 1),
                    np.asarray([float(open_mounting["ear_thickness"])], dtype=np.float64),
                )
            )
        )
    else:
        global_inner_z = np.asarray([], dtype=np.float64)

    for side in range(6):
        outer_start, outer_end = outer[side], outer[(side + 1) % 6]
        inner_start, inner_end = inner[side], inner[(side + 1) % 6]
        edge = outer_end - outer_start
        outward = np.array([edge[1], -edge[0]], dtype=np.float64)
        outward /= np.linalg.norm(outward)
        tangent = side_tangent_values(side, tangential_segments, attachment_intervals)

        z_values = np.linspace(0.0, depth, outer_z_segments + 1)
        tt, zz = np.meshgrid(tangent, z_values, indexing="xy")
        nominal_xy = outer_start + (outer_end - outer_start) * tt[..., None]
        side_distance = np.minimum(tt, 1.0 - tt) * side_length
        z_distance = np.minimum(zz, depth - zz)
        taper = smoothstep01(side_distance / edge_taper) * smoothstep01(z_distance / edge_taper)
        u = (1.0 - zz / depth) * wall_depth_repeat
        v = ((side + tt) / 6.0) * wall_perimeter_repeat
        height = heightmap.sample_periodic(u, v) * taper
        displaced_xy = nominal_xy - outward * (relief_depth * height)[..., None]
        grid = np.dstack((displaced_xy, zz))
        mesh.add_surface_grid(grid)

        inner_side_length = float(np.linalg.norm(inner_end - inner_start))
        if open_mounting is not None and side == 1:
            patches = top_side_patches(
                attachment_intervals,
                float(open_mounting["ear_thickness"]),
            )
        else:
            patches = [(0.0, 1.0, 0.0 if open_mounting is not None else back)]

        for t0, t1, z_start in patches:
            patch_tangent = tangent[(tangent >= t0 - 1e-12) & (tangent <= t1 + 1e-12)]
            if len(patch_tangent) < 2:
                patch_tangent = np.asarray([t0, t1], dtype=np.float64)
            if open_mounting is None:
                inner_z_segments = max(2, math.ceil((depth - z_start) / pitch))
                z_values = np.linspace(z_start, depth, inner_z_segments + 1)
            else:
                z_values = global_inner_z[global_inner_z >= z_start - 1e-12]
            tt, zz = np.meshgrid(patch_tangent, z_values, indexing="xy")
            nominal_xy = inner_start + (inner_end - inner_start) * tt[..., None]
            side_distance = np.minimum(tt, 1.0 - tt) * inner_side_length
            patch_distance = np.minimum(tt - t0, t1 - tt) * inner_side_length
            side_distance = np.minimum(side_distance, patch_distance)
            z_distance = np.minimum(zz - z_start, depth - zz)
            taper = smoothstep01(side_distance / edge_taper) * smoothstep01(
                z_distance / edge_taper
            )
            if open_mounting is None:
                u = (1.0 - (zz - back) / (depth - back)) * wall_depth_repeat
            else:
                u = (1.0 - zz / depth) * wall_depth_repeat
            v = ((side + tt) / 6.0) * wall_perimeter_repeat
            height = heightmap.sample_periodic(u, v) * taper
            displaced_xy = nominal_xy + outward * (relief_depth * height)[..., None]
            grid = np.dstack((displaced_xy, zz))
            mesh.add_surface_grid(grid)

    return tangential_segments


def add_textured_front_ring(
    mesh: MeshBuilder,
    heightmap: HeightMap,
    outer: np.ndarray,
    inner: np.ndarray,
    depth: float,
    relief_depth: float,
    pitch: float,
    edge_taper: float,
    tangential_segments: int,
    tile_width: float,
    tile_height: float,
    open_mounting: dict | None = None,
) -> None:
    nominal_wall = float(np.linalg.norm(outer[0] - inner[0]))
    radial_segments = max(2, math.ceil(nominal_wall / pitch))
    radial = np.linspace(0.0, 1.0, radial_segments + 1)
    attachment_intervals = (
        top_attachment_intervals(inner, open_mounting) if open_mounting is not None else []
    )
    for side in range(6):
        tangent = side_tangent_values(side, tangential_segments, attachment_intervals)
        tt, rr = np.meshgrid(tangent, radial, indexing="xy")
        outer_line = outer[side] + (outer[(side + 1) % 6] - outer[side]) * tt[..., None]
        inner_line = inner[side] + (inner[(side + 1) % 6] - inner[side]) * tt[..., None]
        xy = inner_line * (1.0 - rr[..., None]) + outer_line * rr[..., None]
        radial_distance = np.minimum(rr, 1.0 - rr) * nominal_wall
        taper = smoothstep01(radial_distance / edge_taper)
        height = heightmap.sample_periodic(xy[..., 0] / tile_width, xy[..., 1] / tile_height)
        zz = depth - relief_depth * height * taper
        mesh.add_surface_grid(np.dstack((xy, zz)))


def add_back_and_mounting_surfaces(
    mesh: MeshBuilder,
    outer: np.ndarray,
    inner: np.ndarray,
    segments_per_side: int,
    back: float,
    holes: list[tuple[float, float]],
    shank_radius: float,
    head_radius: float,
    counterbore_depth: float,
) -> None:
    shank_holes = [circle_polygon(center, shank_radius) for center in holes]
    head_holes = [circle_polygon(center, head_radius) for center in holes]

    def stitched_plane(
        boundary: np.ndarray,
        hole_centers: list[tuple[float, float]],
        hole_radius: float,
        z: float,
        strip_width: float = 3.0,
    ) -> None:
        """Guarantee exact dense outer edges, then triangulate a simpler core."""
        boundary_radius = float(np.linalg.norm(boundary[0]))
        core_radius = boundary_radius - strip_width / math.cos(math.pi / 6.0)
        if core_radius <= 0:
            raise ValueError("Planar boundary strip consumes polygon")
        core = regular_hex(core_radius)

        for side in range(6):
            start = boundary[side]
            end = boundary[(side + 1) % 6]
            dense = np.asarray(
                [
                    start + (end - start) * (step / segments_per_side)
                    for step in range(segments_per_side + 1)
                ],
                dtype=np.float64,
            )
            points_2d = np.vstack((core[side], dense, core[(side + 1) % 6]))
            last = len(points_2d) - 1
            faces: list[tuple[int, int, int]] = []
            for step in range(segments_per_side):
                faces.append((0, 1 + step, 2 + step))
            faces.append((0, last - 1, last))
            points_3d = np.column_stack((points_2d, np.full(len(points_2d), z)))
            mesh.add_triangles_3d(points_3d, np.asarray(faces, dtype=np.int64))

        outer_holes = [
            circle_polygon(center, hole_radius + strip_width)
            for center in hole_centers
        ]
        exact_holes = [circle_polygon(center, hole_radius) for center in hole_centers]
        for exact, expanded in zip(exact_holes, outer_holes):
            exact_3d = np.column_stack((exact, np.full(len(exact), z)))
            expanded_3d = np.column_stack((expanded, np.full(len(expanded), z)))
            mesh.add_ring_surface(exact_3d, expanded_3d)

        core_points, core_faces = triangulate_plane_with_holes(
            core,
            outer_holes,
            core,
            grid_pitch=4.0,
        )
        mesh.add_triangles(core_points, core_faces, z=z)

    stitched_plane(outer, holes, shank_radius, z=0.0)
    stitched_plane(inner, holes, head_radius, z=back, strip_width=1.2)

    z_counterbore = back - counterbore_depth
    for center, shank_ring, head_ring in zip(holes, shank_holes, head_holes):
        shank_lower = np.column_stack((shank_ring, np.zeros(len(shank_ring))))
        shank_upper = np.column_stack(
            (shank_ring, np.full(len(shank_ring), z_counterbore))
        )
        mesh.add_ring_surface(shank_lower, shank_upper)

        ledge_inner = np.column_stack(
            (shank_ring, np.full(len(shank_ring), z_counterbore))
        )
        ledge_outer = np.column_stack(
            (head_ring, np.full(len(head_ring), z_counterbore))
        )
        mesh.add_ring_surface(ledge_inner, ledge_outer)

        head_lower = np.column_stack(
            (head_ring, np.full(len(head_ring), z_counterbore))
        )
        head_upper = np.column_stack((head_ring, np.full(len(head_ring), back)))
        mesh.add_ring_surface(head_lower, head_upper)


def add_open_back_and_mounting_ears(
    mesh: MeshBuilder,
    outer: np.ndarray,
    inner: np.ndarray,
    depth: float,
    segments_per_side: int,
    pitch: float,
    mounting: dict,
) -> None:
    """Close the rear frame ring and add two integrated, visible mounting ears."""
    ear_thickness = float(mounting["ear_thickness"])
    ear_radius = float(mounting["ear_outer_radius"])
    neck_width = float(mounting["ear_neck_width"])
    shank_radius = float(mounting["shank_clearance_diameter"]) / 2.0
    head_radius = float(mounting["head_counterbore_diameter"]) / 2.0
    counterbore_depth = float(mounting["counterbore_depth"])
    z_counterbore = ear_thickness - counterbore_depth
    inner_top_y = float(inner[1, 1])
    intervals = top_attachment_intervals(inner, mounting)
    top_tangent = side_tangent_values(1, segments_per_side, intervals)
    z_segments = max(2, math.ceil(depth / pitch))
    global_z = np.unique(
        np.concatenate(
            (
                np.linspace(0.0, depth, z_segments + 1),
                np.asarray([ear_thickness], dtype=np.float64),
            )
        )
    )
    ear_z = global_z[global_z <= ear_thickness + 1e-12]

    ears: list[tuple[tuple[float, float], np.ndarray]] = []
    for _t0, _t1, center in intervals:
        ear = mounting_ear_polygon(center, ear_radius, neck_width, inner_top_y)
        ears.append((center, ear))

    nominal_wall = float(np.linalg.norm(outer[0] - inner[0]))
    radial_segments = max(2, math.ceil(nominal_wall / pitch))
    radial = np.linspace(0.0, 1.0, radial_segments + 1)
    for side in range(6):
        tangent = side_tangent_values(side, segments_per_side, intervals)
        tt, rr = np.meshgrid(tangent, radial, indexing="xy")
        outer_line = outer[side] + (outer[(side + 1) % 6] - outer[side]) * tt[..., None]
        inner_line = inner[side] + (inner[(side + 1) % 6] - inner[side]) * tt[..., None]
        xy = inner_line * (1.0 - rr[..., None]) + outer_line * rr[..., None]
        mesh.add_surface_grid(np.dstack((xy, np.zeros_like(tt))))

    def add_exposed_ear_wall(ear: np.ndarray) -> None:
        # The omitted closing edge is the neck-to-frame attachment and is internal.
        for index in range(len(ear) - 1):
            grid = np.empty((len(ear_z), 2, 3), dtype=np.float64)
            grid[:, 0, :2] = ear[index]
            grid[:, 1, :2] = ear[index + 1]
            grid[:, :, 2] = ear_z[:, None]
            mesh.add_surface_grid(grid)

    interval_by_center = {center: (t0, t1) for t0, t1, center in intervals}
    for center, ear in ears:
        head_hole = circle_polygon(center, head_radius)
        shank_ring = circle_polygon(center, shank_radius)
        t0, t1 = interval_by_center[center]
        attachment_values = top_tangent[
            (top_tangent >= t0 - 1e-12) & (top_tangent <= t1 + 1e-12)
        ]
        attachment_points = inner[1] + (inner[2] - inner[1]) * attachment_values[:, None]
        if len(attachment_points) > 2:
            ear_surface_boundary = np.vstack((ear, attachment_points[1:-1]))
        else:
            ear_surface_boundary = ear
        rear_points, rear_faces = triangulate_plane_with_holes(
            ear_surface_boundary,
            [shank_ring],
            ear_surface_boundary,
            grid_pitch=min(2.0, max(1.0, pitch * 3.0)),
        )
        mesh.add_triangles(rear_points, rear_faces, z=0.0)
        top_points, top_faces = triangulate_plane_with_holes(
            ear_surface_boundary,
            [head_hole],
            ear_surface_boundary,
            grid_pitch=min(2.0, max(1.0, pitch * 3.0)),
        )
        mesh.add_triangles(top_points, top_faces, z=ear_thickness)
        add_exposed_ear_wall(ear)

        shank_lower = np.column_stack((shank_ring, np.zeros(len(shank_ring))))
        shank_upper = np.column_stack(
            (shank_ring, np.full(len(shank_ring), z_counterbore))
        )
        mesh.add_ring_surface(shank_lower, shank_upper)

        ledge_inner = np.column_stack(
            (shank_ring, np.full(len(shank_ring), z_counterbore))
        )
        ledge_outer = np.column_stack(
            (head_hole, np.full(len(head_hole), z_counterbore))
        )
        mesh.add_ring_surface(ledge_inner, ledge_outer)

        head_lower = np.column_stack(
            (head_hole, np.full(len(head_hole), z_counterbore))
        )
        head_upper = np.column_stack(
            (head_hole, np.full(len(head_hole), ear_thickness))
        )
        mesh.add_ring_surface(head_lower, head_upper)


def build_module(params: dict, pitch_override: float | None = None) -> tuple[np.ndarray, np.ndarray, dict]:
    module = params["module"]
    texture = params["texture"]
    mounting = params["mounting"]
    radius = float(module["outer_radius"])
    wall = float(module["wall_thickness"])
    depth = float(module["depth"])
    back = float(module["back_thickness"])
    back_panel_enabled = bool(module.get("back_panel_enabled", True))
    relief_depth = float(texture["depth"])
    pitch = float(pitch_override or texture["mesh_pitch"])
    inner_radius = radius - wall / math.cos(math.pi / 6.0)

    if inner_radius <= 0:
        raise ValueError("wall_thickness consumes the hexagon")
    if not (0 < back < depth):
        raise ValueError("back_thickness must be between zero and depth")
    if not (0 < relief_depth < wall * 0.25):
        raise ValueError("texture depth must stay below 25% of wall thickness")
    if pitch <= 0:
        raise ValueError("mesh pitch must be positive")
    mounting_thickness = (
        back if back_panel_enabled else float(mounting["ear_thickness"])
    )
    if not (0.0 < mounting_thickness < depth):
        raise ValueError("mounting feature thickness must be between zero and depth")
    if not (0.0 < float(mounting["counterbore_depth"]) < mounting_thickness):
        raise ValueError("counterbore depth must leave mounting material")
    if float(mounting["ear_outer_radius"]) <= (
        float(mounting["head_counterbore_diameter"]) / 2.0 + 2.0
    ):
        raise ValueError("mounting ears need at least 2 mm around the screw head")

    heightmap_path = PROJECT_DIR / texture["heightmap"]
    heightmap = HeightMap(heightmap_path)
    outer = regular_hex(radius)
    inner = regular_hex(inner_radius)
    mesh = MeshBuilder()
    segments_per_side = add_textured_walls(
        mesh,
        heightmap,
        outer,
        inner,
        depth,
        back,
        relief_depth,
        pitch,
        float(texture["edge_taper"]),
        float(texture["wall_depth_repeat"]),
        float(texture["wall_perimeter_repeat"]),
        None if back_panel_enabled else mounting,
    )
    add_textured_front_ring(
        mesh,
        heightmap,
        outer,
        inner,
        depth,
        relief_depth,
        pitch,
        float(texture["edge_taper"]),
        segments_per_side,
        float(texture["front_tile_width"]),
        float(texture["front_tile_height"]),
        None if back_panel_enabled else mounting,
    )
    if back_panel_enabled:
        add_back_and_mounting_surfaces(
            mesh,
            outer,
            inner,
            segments_per_side,
            back,
            [tuple(map(float, value)) for value in mounting["hole_centers"]],
            float(mounting["shank_clearance_diameter"]) / 2.0,
            float(mounting["head_counterbore_diameter"]) / 2.0,
            float(mounting["counterbore_depth"]),
        )
    else:
        add_open_back_and_mounting_ears(
            mesh,
            outer,
            inner,
            depth,
            segments_per_side,
            pitch,
            mounting,
        )
    vertices, faces, report = mesh.finalized()
    report["parameters"] = params
    report["derived"] = {
        "inner_radius_mm": inner_radius,
        "back_panel_enabled": back_panel_enabled,
        "nominal_inside_depth_mm": depth - back if back_panel_enabled else depth,
        "mounting_feature_thickness_mm": mounting_thickness,
        "mesh_pitch_mm": pitch,
        "relief_depth_mm": relief_depth,
        "raw_array_lower_bound_mib": (
            vertices.nbytes + faces.nbytes
        ) / (1024.0 * 1024.0),
        "working_memory_guidance": "Plan roughly 3-10x raw arrays for topology, spatial indices, export, and slicer processing.",
    }
    return vertices, faces, report


def build_texture_coupon(params: dict, pitch_override: float | None = None) -> tuple[np.ndarray, np.ndarray, dict]:
    texture = params["texture"]
    heightmap = HeightMap(PROJECT_DIR / texture["heightmap"])
    width, height, thickness = 70.0, 45.0, 2.4
    pitch = float(pitch_override or texture["mesh_pitch"])
    depth = float(texture["depth"])
    edge = float(texture["edge_taper"])
    nx = max(2, math.ceil(width / pitch))
    ny = max(2, math.ceil(height / pitch))
    xs = np.linspace(-width / 2, width / 2, nx + 1)
    ys = np.linspace(-height / 2, height / 2, ny + 1)
    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    edge_distance = np.minimum.reduce(
        (xx + width / 2, width / 2 - xx, yy + height / 2, height / 2 - yy)
    )
    taper = smoothstep01(edge_distance / edge)
    relief = heightmap.sample_periodic(xx / float(texture["front_tile_width"]), yy / float(texture["front_tile_height"]))
    top = np.dstack((xx, yy, thickness - depth * relief * taper))
    bottom = np.dstack((xx, yy, np.zeros_like(xx)))
    mesh = MeshBuilder()
    mesh.add_surface_grid(top)
    mesh.add_surface_grid(bottom)
    top_boundary = np.vstack(
        (
            top[0, :-1],
            top[:-1, -1],
            top[-1, :0:-1],
            top[:0:-1, 0],
        )
    )
    bottom_boundary = np.vstack(
        (
            bottom[0, :-1],
            bottom[:-1, -1],
            bottom[-1, :0:-1],
            bottom[:0:-1, 0],
        )
    )
    mesh.add_ring_surface(bottom_boundary, top_boundary)
    vertices, faces, report = mesh.finalized()
    report["coupon"] = {"width_mm": width, "height_mm": height, "thickness_mm": thickness}
    return vertices, faces, report


def require_valid(report: dict, label: str) -> None:
    failures = []
    for key in ("boundary_edges", "nonmanifold_edges", "inconsistent_winding_edges", "degenerate_triangles", "orientation_conflicts"):
        if report.get(key, 0) != 0:
            failures.append(f"{key}={report[key]}")
    if not report.get("watertight", False):
        failures.append("watertight=false")
    if report.get("signed_volume_mm3", 0.0) <= 0:
        failures.append("signed_volume_mm3<=0")
    if report.get("oriented_components", 0) != 1:
        failures.append(f"oriented_components={report.get('oriented_components')}")
    if failures:
        raise RuntimeError(f"{label} validation failed: {', '.join(failures)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=Path, default=PROJECT_DIR / "parameters.json")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "generated")
    parser.add_argument("--mesh-pitch", type=float, help="Override production surface pitch in millimetres")
    args = parser.parse_args()

    params = json.loads(args.params.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    vertices, faces, report = build_module(params, args.mesh_pitch)
    require_valid(report, "module")
    write_binary_stl(args.output_dir / "honeycomb-module-textured.stl", vertices, faces)
    (args.output_dir / "textured-mesh-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )

    coupon_vertices, coupon_faces, coupon_report = build_texture_coupon(params, args.mesh_pitch)
    require_valid(coupon_report, "texture coupon")
    write_binary_stl(args.output_dir / "wood-texture-coupon.stl", coupon_vertices, coupon_faces)
    (args.output_dir / "texture-coupon-report.json").write_text(
        json.dumps(coupon_report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"module": report, "coupon": coupon_report}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
