#!/usr/bin/env python3
"""Shared FDM surface-texture library.

Ported from the proven honeycomb wall shelf generator
(products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf). The
coupon-critical functions keep the exact formulas of the reference
implementation so regenerated coupons stay byte-comparable; new builders
generalize the same primitives to arbitrary planar wall chains and caps.

Coordinate convention: parts stand on the z=0 bed plane. Engraving displaces
surface samples inward along the local surface normal; embossing outward.
"""

from __future__ import annotations

import math
import struct
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.spatial import Delaunay


def smoothstep01(value: np.ndarray | float) -> np.ndarray | float:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


class TileSampler:
    """Periodic bilinear sampler over a grayscale tile (reference HeightMap)."""

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

    def add_ring_surface(self, lower: np.ndarray, upper: np.ndarray) -> None:
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


def write_binary_stl(path: Path, vertices: np.ndarray, faces: np.ndarray, header_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        header = header_text.encode("utf-8", errors="replace")
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
    probes = tri_points.mean(axis=1)
    keep = domain_mask(probes, outer, holes)
    return all_points, candidates[keep]


def circle_polygon(center: tuple[float, float], radius: float, segments: int = 64) -> np.ndarray:
    angles = np.arange(segments, dtype=np.float64) * 2.0 * math.pi / segments
    return np.column_stack(
        (center[0] + radius * np.cos(angles), center[1] + radius * np.sin(angles))
    )


# ---------------------------------------------------------------------------
# High-level texture builders
# ---------------------------------------------------------------------------


def textured_rect_coupons_fields(
    sampler: TileSampler,
    width: float,
    height: float,
    thickness: float,
    depth: float,
    edge_taper: float,
    pitch: float,
    tile_width: float,
    tile_height: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Reference coupon fields: top/bottom grid + boundary loops (shelf formulas)."""
    nx = max(2, math.ceil(width / pitch))
    ny = max(2, math.ceil(height / pitch))
    xs = np.linspace(-width / 2, width / 2, nx + 1)
    ys = np.linspace(-height / 2, height / 2, ny + 1)
    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    edge_distance = np.minimum.reduce(
        (xx + width / 2, width / 2 - xx, yy + height / 2, height / 2 - yy)
    )
    taper = smoothstep01(edge_distance / edge_taper)
    relief = sampler.sample_periodic(xx / float(tile_width), yy / float(tile_height))
    top = np.dstack((xx, yy, thickness - depth * relief * taper))
    bottom = np.dstack((xx, yy, np.zeros_like(xx)))
    return top, bottom


def build_reference_coupon(
    mesh: MeshBuilder,
    sampler: TileSampler,
    width: float,
    height: float,
    thickness: float,
    depth: float,
    edge_taper: float,
    pitch: float,
    tile_width: float,
    tile_height: float,
) -> None:
    """Shelf-identical watertight texture coupon (regression baseline)."""
    top, bottom = textured_rect_coupons_fields(
        sampler, width, height, thickness, depth, edge_taper, pitch, tile_width, tile_height
    )
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


def textured_wall_chain(
    mesh: MeshBuilder,
    sampler: TileSampler,
    chain: np.ndarray,
    z0: float,
    z1: float,
    depth: float,
    pitch: float,
    edge_taper: float,
    u_period_mm: float,
    v_period_mm: float,
    *,
    closed: bool = False,
    engrave: bool = True,
    v_offset_mm: float = 0.0,
    segment_enabled: list[bool] | None = None,
) -> float:
    """Vertical wall band along an XY polygon chain, grain (tile u) along z.

    Displacement follows each segment's outward normal; engraving moves points
    against the normal. Smooth segments (segment_enabled False) keep the exact
    planar wall but share corner vertices and z rows so textured and smooth
    stretches merge watertight. The height field tapers to zero at z edges and,
    for open chains, at the chain ends. Returns the arc length consumed.
    """
    chain = np.asarray(chain, dtype=np.float64)
    if chain.shape[1] != 2 or len(chain) < 2:
        raise ValueError("wall chain must be an (N, 2) point list")
    height_span = z1 - z0
    if height_span <= 0:
        raise ValueError("wall chain z range must be positive")
    if u_period_mm <= 0 or v_period_mm <= 0:
        raise ValueError("tile periods must be positive")
    z_segments = max(2, math.ceil(height_span / pitch))
    z_values = np.linspace(z0, z1, z_segments + 1)
    segment_count = len(chain) - (0 if closed else 1)
    if segment_enabled is None:
        segment_enabled = [True] * segment_count
    if len(segment_enabled) != segment_count:
        raise ValueError("segment_enabled length must match segment count")
    arc_offset = 0.0
    for index in range(segment_count):
        start = chain[index]
        end = chain[(index + 1) % len(chain)]
        edge = end - start
        seg_len = float(np.linalg.norm(edge))
        if seg_len <= 0:
            continue
        outward = np.array([edge[1], -edge[0]]) / seg_len
        enabled = bool(segment_enabled[index])
        segments = max(2, math.ceil(seg_len / pitch))
        t_values = np.linspace(0.0, 1.0, segments + 1)
        tt, zz = np.meshgrid(t_values, z_values, indexing="xy")
        nominal_xy = start + edge * tt[..., None]
        if enabled:
            edge_distance_t = np.minimum(tt, 1.0 - tt) * seg_len
            z_distance = np.minimum(zz - z0, z1 - zz)
            if closed:
                taper = smoothstep01(z_distance / edge_taper)
            else:
                taper = smoothstep01(edge_distance_t / edge_taper) * smoothstep01(
                    z_distance / edge_taper
                )
            arc = arc_offset + tt * seg_len
            u = (1.0 - (zz - z0) / height_span) * height_span / u_period_mm
            v = (arc + v_offset_mm) / v_period_mm
            relief = sampler.sample_periodic(u, v) * taper
        else:
            relief = np.zeros_like(tt)
        sign = 1.0 if engrave else -1.0
        displaced_xy = nominal_xy - sign * outward * (depth * relief)[..., None]
        grid = np.dstack((displaced_xy, zz))
        mesh.add_surface_grid(grid)
        arc_offset += seg_len
    return arc_offset


def sampled_chain_boundary(polygon: np.ndarray, pitch: float, closed: bool = True) -> np.ndarray:
    """Sample polygon edges with the same linspace rule as textured_wall_chain.

    Cap triangulations must consume exactly these points so wall rims and cap
    boundaries share every edge. Collinear runs are intentional: they keep the
    straight wall edges exactly straight while still matching wall subdivisions.
    """
    polygon = np.asarray(polygon, dtype=np.float64)
    count = len(polygon) if closed else len(polygon) - 1
    samples: list[np.ndarray] = []
    for index in range(count):
        start = polygon[index]
        end = polygon[(index + 1) % len(polygon)]
        length = float(np.linalg.norm(end - start))
        if length <= 0:
            continue
        segments = max(2, math.ceil(length / pitch))
        steps = np.linspace(0.0, 1.0, segments + 1)[:-1]
        samples.append(start + (end - start) * steps[:, None])
    return np.vstack(samples)


def triangulate_cap(
    outer: np.ndarray,
    holes: list[np.ndarray],
    boundary_points: np.ndarray,
    grid_pitch: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Delaunay cap fill with inside tests on centroid AND circumcenter.

    The combined filter keeps non-convex boundaries faithful within the grid
    pitch; callers must verify watertightness afterwards (fail closed).
    """
    points, candidates = triangulate_plane_with_holes(
        outer, holes, boundary_points, grid_pitch
    )
    tri_points = points[candidates]
    keep = domain_mask(tri_points.mean(axis=1), outer, holes)
    circumcenters = _circumcenters(tri_points)
    keep &= domain_mask(circumcenters, outer, holes)
    return points, candidates[keep]


def _circumcenters(tri_points: np.ndarray) -> np.ndarray:
    a = tri_points[:, 0]
    b = tri_points[:, 1]
    c = tri_points[:, 2]
    d = 2.0 * (a[:, 0] * (b[:, 1] - c[:, 1]) + b[:, 0] * (c[:, 1] - a[:, 1]) + c[:, 0] * (a[:, 1] - b[:, 1]))
    degenerate = np.abs(d) < 1e-12
    a2 = (a * a).sum(axis=1)
    b2 = (b * b).sum(axis=1)
    c2 = (c * c).sum(axis=1)
    ux = (a2 * (b[:, 1] - c[:, 1]) + b2 * (c[:, 1] - a[:, 1]) + c2 * (a[:, 1] - b[:, 1])) / np.where(degenerate, 1.0, d)
    uy = (a2 * (c[:, 0] - b[:, 0]) + b2 * (a[:, 0] - c[:, 0]) + c2 * (b[:, 0] - a[:, 0])) / np.where(degenerate, 1.0, d)
    centers = np.column_stack((ux, uy))
    centers[degenerate] = tri_points[degenerate].mean(axis=1)[:, :2]
    return centers


def textured_planar_polygon(
    mesh: MeshBuilder,
    sampler: TileSampler | None,
    outer: np.ndarray,
    holes: list[np.ndarray],
    boundary_points: np.ndarray,
    z: float,
    depth: float,
    pitch: float,
    edge_taper: float,
    *,
    tile_width_mm: float = 120.0,
    tile_height_mm: float = 45.0,
    origin: tuple[float, float] = (0.0, 0.0),
    engrave: bool = True,
    facing_up: bool = True,
) -> None:
    """Planar cap fill; sampler None or depth 0 keeps the cap perfectly flat.

    Relief uses a global XY projection in the cap plane coordinate frame; the
    boundary stays exactly on z so adjacent walls meet precisely, and relief
    falls to zero within edge_taper of the polygon boundary.
    """
    outer = np.asarray(outer, dtype=np.float64)
    points, faces = triangulate_cap(outer, holes, boundary_points, grid_pitch=pitch)
    xy = points
    if sampler is not None and depth > 0.0:
        edge_distance = _boundary_distance(xy, outer, holes)
        taper = smoothstep01(edge_distance / edge_taper)
        relief = sampler.sample_periodic(
            (xy[:, 0] - origin[0]) / tile_width_mm,
            (xy[:, 1] - origin[1]) / tile_height_mm,
        )
        dz = depth * relief * taper
    else:
        dz = np.zeros(len(xy))
    if not facing_up:
        dz = -dz
    sign = 1.0 if engrave else -1.0
    zz = z - sign * dz
    mesh.add_triangles_3d(np.column_stack((xy, zz)), faces)


def _boundary_distance(points: np.ndarray, outer: np.ndarray, holes: list[np.ndarray]) -> np.ndarray:
    distance = np.full(len(points), np.inf, dtype=np.float64)
    for polygon in [outer, *holes]:
        previous = polygon[-1]
        for current in polygon:
            edge = current - previous
            length_sq = float(edge @ edge)
            if length_sq < 1e-15:
                previous = current
                continue
            t = np.clip(((points - previous) @ edge) / length_sq, 0.0, 1.0)
            closest = previous + t[:, None] * edge
            distance = np.minimum(distance, np.linalg.norm(points - closest, axis=1))
            previous = current
    return distance
