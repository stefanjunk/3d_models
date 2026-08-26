#!/usr/bin/env python3
"""Portable geometry helpers for parametric-freeform-surfacing.

The module intentionally depends only on NumPy.  It provides deterministic
curve fairing, section alignment, lofting, simple mesh I/O, topology metrics,
and Bernstein-lattice free-form deformation for examples and regression tests.
It is not a replacement for an exact NURBS/B-Rep kernel.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

Array = np.ndarray


class GeometryError(ValueError):
    """Raised when geometry input cannot produce a valid deterministic result."""


def as_points(points: Sequence[Sequence[float]] | Array, minimum: int = 2) -> Array:
    array = np.asarray(points, dtype=float)
    if array.ndim != 2 or array.shape[0] < minimum or array.shape[1] not in (2, 3):
        raise GeometryError(f"Expected at least {minimum} 2D/3D points; got {array.shape}")
    if not np.isfinite(array).all():
        raise GeometryError("Points contain NaN or infinite values")
    return array


def remove_consecutive_duplicates(points: Array, tolerance: float = 1e-12, closed: bool = False) -> Array:
    pts = as_points(points)
    keep = np.ones(len(pts), dtype=bool)
    keep[1:] = np.linalg.norm(np.diff(pts, axis=0), axis=1) > tolerance
    pts = pts[keep]
    if closed and len(pts) > 2 and np.linalg.norm(pts[0] - pts[-1]) <= tolerance:
        pts = pts[:-1]
    if len(pts) < (3 if closed else 2):
        raise GeometryError("Too few distinct points after duplicate removal")
    return pts


def polyline_length(points: Array, closed: bool = False) -> float:
    pts = as_points(points)
    segments = np.diff(pts, axis=0)
    length = float(np.linalg.norm(segments, axis=1).sum())
    if closed:
        length += float(np.linalg.norm(pts[0] - pts[-1]))
    return length


def resample_polyline(points: Array, count: int, closed: bool = False) -> Array:
    """Resample a polyline approximately uniformly by arc length."""
    if count < (3 if closed else 2):
        raise GeometryError("Resample count is too small")
    pts = remove_consecutive_duplicates(points, closed=closed)
    chain = np.vstack([pts, pts[0]]) if closed else pts
    lengths = np.linalg.norm(np.diff(chain, axis=0), axis=1)
    cumulative = np.concatenate([[0.0], np.cumsum(lengths)])
    total = float(cumulative[-1])
    if total <= 1e-12:
        raise GeometryError("Polyline has zero length")
    targets = np.linspace(0.0, total, count, endpoint=not closed)
    result = np.empty((count, pts.shape[1]), dtype=float)
    segment_index = 0
    for i, target in enumerate(targets):
        while segment_index < len(lengths) - 1 and cumulative[segment_index + 1] < target:
            segment_index += 1
        segment_length = lengths[segment_index]
        local = 0.0 if segment_length <= 1e-15 else (target - cumulative[segment_index]) / segment_length
        result[i] = chain[segment_index] * (1.0 - local) + chain[segment_index + 1] * local
    return result


def regularized_smooth(
    points: Array,
    strength: float = 10.0,
    closed: bool = False,
    preserve_ends: bool = True,
    endpoint_weight: float = 1e8,
) -> Array:
    """Smooth samples by penalizing discrete second differences.

    Solves ``argmin ||Q-P||² + strength * ||D2 Q||²``.  This is a portable
    screening/fairing helper; use an exact spline fitter for production NURBS.
    """
    pts = as_points(points, minimum=3)
    if strength < 0:
        raise GeometryError("strength must be non-negative")
    n = len(pts)
    if closed:
        d2 = np.zeros((n, n), dtype=float)
        for i in range(n):
            d2[i, (i - 1) % n] = 1.0
            d2[i, i] = -2.0
            d2[i, (i + 1) % n] = 1.0
    else:
        d2 = np.zeros((n - 2, n), dtype=float)
        for i in range(n - 2):
            d2[i, i : i + 3] = (1.0, -2.0, 1.0)
    system = np.eye(n) + float(strength) * (d2.T @ d2)
    rhs = pts.copy()
    if not closed and preserve_ends:
        system[0, 0] += endpoint_weight
        system[-1, -1] += endpoint_weight
        rhs[0] += endpoint_weight * pts[0]
        rhs[-1] += endpoint_weight * pts[-1]
    return np.linalg.solve(system, rhs)


def fourier_smooth_closed(points: Array, harmonics: int = 8, output_count: int | None = None) -> Array:
    """Low-pass fair a periodic closed outline using discrete Fourier modes."""
    pts = as_points(points, minimum=4)
    count = int(output_count or len(pts))
    periodic = resample_polyline(pts, count=count, closed=True)
    max_harmonics = max(1, (count - 1) // 2)
    if harmonics < 1 or harmonics > max_harmonics:
        raise GeometryError(f"harmonics must be between 1 and {max_harmonics}")
    spectrum = np.fft.fft(periodic, axis=0)
    filtered = np.zeros_like(spectrum)
    filtered[: harmonics + 1] = spectrum[: harmonics + 1]
    filtered[-harmonics:] = spectrum[-harmonics:]
    return np.fft.ifft(filtered, axis=0).real


def discrete_curvature(points: Array, closed: bool = False) -> Array:
    """Return discrete signed 2D or unsigned 3D curvature at samples."""
    pts = as_points(points, minimum=3)
    n = len(pts)
    curvature = np.full(n, np.nan, dtype=float)
    indices = range(n) if closed else range(1, n - 1)
    for i in indices:
        prev = pts[(i - 1) % n]
        current = pts[i]
        nxt = pts[(i + 1) % n]
        a = current - prev
        b = nxt - current
        c = nxt - prev
        denominator = np.linalg.norm(a) * np.linalg.norm(b) * np.linalg.norm(c)
        if denominator <= 1e-15:
            curvature[i] = 0.0
            continue
        if pts.shape[1] == 2:
            cross = a[0] * b[1] - a[1] * b[0]
            curvature[i] = 2.0 * cross / denominator
        else:
            curvature[i] = 2.0 * np.linalg.norm(np.cross(a, b)) / denominator
    if not closed:
        curvature[0] = curvature[1]
        curvature[-1] = curvature[-2]
    return curvature


def _extrema_count(values: Array, noise_fraction: float = 0.02) -> int:
    values = np.asarray(values, dtype=float)
    if len(values) < 3:
        return 0
    scale = max(float(np.max(np.abs(values))), 1e-12)
    threshold = scale * noise_fraction
    count = 0
    for i in range(1, len(values) - 1):
        left = values[i] - values[i - 1]
        right = values[i + 1] - values[i]
        if abs(left) < threshold and abs(right) < threshold:
            continue
        if left * right < 0:
            count += 1
    return count


def curve_metrics(points: Array, closed: bool = False) -> dict[str, Any]:
    pts = as_points(points, minimum=3)
    kappa = discrete_curvature(pts, closed=closed)
    finite = kappa[np.isfinite(kappa)]
    segment_lengths = np.linalg.norm(np.diff(np.vstack([pts, pts[0]]) if closed else pts, axis=0), axis=1)
    variation = float(np.abs(np.diff(np.r_[finite, finite[0]] if closed else finite)).sum()) if len(finite) else 0.0
    return {
        "point_count": int(len(pts)),
        "dimension": int(pts.shape[1]),
        "closed": bool(closed),
        "length": polyline_length(pts, closed=closed),
        "minimum_segment_length": float(segment_lengths.min()),
        "maximum_segment_length": float(segment_lengths.max()),
        "curvature_rms": float(np.sqrt(np.mean(finite**2))) if len(finite) else 0.0,
        "curvature_max_abs": float(np.max(np.abs(finite))) if len(finite) else 0.0,
        "curvature_total_variation": variation,
        "curvature_extrema_count": _extrema_count(finite),
        "curvature": finite.tolist(),
    }


def fairing_displacement(original: Array, faired: Array, closed: bool = False) -> dict[str, float]:
    target = resample_polyline(original, len(faired), closed=closed)
    distances = np.linalg.norm(target - faired, axis=1)
    return {
        "rms_displacement": float(np.sqrt(np.mean(distances**2))),
        "maximum_displacement": float(distances.max()),
    }


def pchip_profile(x: Array | Sequence[float] | float, knots: Sequence[float], values: Sequence[float]) -> Array:
    """Portable monotone cubic Hermite interpolation similar to PCHIP."""
    xq = np.asarray(x, dtype=float)
    k = np.asarray(knots, dtype=float)
    y = np.asarray(values, dtype=float)
    if k.ndim != 1 or y.ndim != 1 or len(k) != len(y) or len(k) < 2:
        raise GeometryError("knots and values must be equal-length 1D arrays")
    if not np.all(np.diff(k) > 0):
        raise GeometryError("knots must be strictly increasing")
    h = np.diff(k)
    delta = np.diff(y) / h
    slopes = np.zeros_like(y)
    slopes[0] = delta[0]
    slopes[-1] = delta[-1]
    for i in range(1, len(y) - 1):
        if delta[i - 1] * delta[i] <= 0:
            slopes[i] = 0.0
        else:
            w1 = 2.0 * h[i] + h[i - 1]
            w2 = h[i] + 2.0 * h[i - 1]
            slopes[i] = (w1 + w2) / (w1 / delta[i - 1] + w2 / delta[i])
    clipped = np.clip(xq, k[0], k[-1])
    interval = np.searchsorted(k, clipped, side="right") - 1
    interval = np.clip(interval, 0, len(k) - 2)
    hi = h[interval]
    t = (clipped - k[interval]) / hi
    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2
    return h00 * y[interval] + h10 * hi * slopes[interval] + h01 * y[interval + 1] + h11 * hi * slopes[interval + 1]


def smoothstep(value: Array | float, edge0: float = 0.0, edge1: float = 1.0) -> Array:
    if edge1 <= edge0:
        raise GeometryError("edge1 must be greater than edge0")
    t = np.clip((np.asarray(value, dtype=float) - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def smootherstep(value: Array | float, edge0: float = 0.0, edge1: float = 1.0) -> Array:
    if edge1 <= edge0:
        raise GeometryError("edge1 must be greater than edge0")
    t = np.clip((np.asarray(value, dtype=float) - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t**3 * (t * (t * 6.0 - 15.0) + 10.0)


def align_closed_sections(sections: Sequence[Array], point_count: int | None = None) -> tuple[list[Array], list[dict[str, Any]]]:
    """Resample and align seams/orientation of closed sections.

    Correspondence is chosen from centered coordinates, so station translation
    does not dominate the seam decision. Semantic landmarks should still be
    used for production surfaces when symmetry makes several shifts equivalent.
    """
    if len(sections) < 2:
        raise GeometryError("At least two sections are required")
    count = int(point_count or max(len(section) for section in sections))
    sampled = [resample_polyline(section, count=count, closed=True) for section in sections]
    aligned = [sampled[0]]
    records: list[dict[str, Any]] = [{"section": 0, "shift": 0, "reversed": False, "rms_correspondence": 0.0}]
    for section_index, section in enumerate(sampled[1:], start=1):
        previous_centered = aligned[-1] - aligned[-1].mean(axis=0)
        best: tuple[float, int, bool, Array] | None = None
        for reversed_flag, base in ((False, section), (True, section[::-1])):
            centered = base - base.mean(axis=0)
            for shift in range(count):
                candidate_centered = np.roll(centered, shift, axis=0)
                rms = float(np.sqrt(np.mean(np.sum((candidate_centered - previous_centered) ** 2, axis=1))))
                candidate = np.roll(base, shift, axis=0)
                if best is None or rms < best[0]:
                    best = (rms, shift, reversed_flag, candidate)
        assert best is not None
        aligned.append(best[3])
        records.append({
            "section": section_index,
            "shift": int(best[1]),
            "reversed": bool(best[2]),
            "rms_correspondence": float(best[0]),
        })
    return aligned, records


def loft_closed_sections(
    sections: Sequence[Array],
    cap_start: bool = True,
    cap_end: bool = True,
    align: bool = True,
    point_count: int | None = None,
) -> tuple[Array, Array, list[dict[str, Any]]]:
    """Triangulate a deterministic loft through closed sections."""
    aligned, records = align_closed_sections(sections, point_count=point_count) if align else (
        [as_points(section, minimum=3) for section in sections],
        [{"section": i, "shift": 0, "reversed": False, "rms_correspondence": 0.0} for i in range(len(sections))],
    )
    count = len(aligned[0])
    if any(len(section) != count or section.shape[1] != 3 for section in aligned):
        raise GeometryError("All loft sections must have equal point counts and be 3D")
    vertices = np.vstack(aligned)
    faces: list[tuple[int, int, int]] = []
    for station in range(len(aligned) - 1):
        base = station * count
        nxt = (station + 1) * count
        for j in range(count):
            jn = (j + 1) % count
            a, b, c, d = base + j, base + jn, nxt + j, nxt + jn
            faces.append((a, b, d))
            faces.append((a, d, c))
    if cap_start:
        center_index = len(vertices)
        vertices = np.vstack([vertices, aligned[0].mean(axis=0)])
        for j in range(count):
            faces.append((center_index, (j + 1) % count, j))
    if cap_end:
        center_index = len(vertices)
        offset = (len(aligned) - 1) * count
        vertices = np.vstack([vertices, aligned[-1].mean(axis=0)])
        for j in range(count):
            faces.append((center_index, offset + j, offset + (j + 1) % count))
    face_array = np.asarray(faces, dtype=np.int64)
    face_array = orient_faces_positive_volume(vertices, face_array)
    return vertices, face_array, records


def extrude_closed_profile(profile: Array, z_bottom: float, z_top: float) -> tuple[Array, Array]:
    pts = as_points(profile, minimum=3)
    if pts.shape[1] == 3:
        xy = pts[:, :2]
    else:
        xy = pts
    if z_top <= z_bottom:
        raise GeometryError("z_top must be greater than z_bottom")
    n = len(xy)
    bottom = np.column_stack([xy, np.full(n, z_bottom)])
    top = np.column_stack([xy, np.full(n, z_top)])
    vertices = np.vstack([bottom, top, [[xy[:, 0].mean(), xy[:, 1].mean(), z_bottom]], [[xy[:, 0].mean(), xy[:, 1].mean(), z_top]]])
    bottom_center = 2 * n
    top_center = 2 * n + 1
    faces: list[tuple[int, int, int]] = []
    for i in range(n):
        j = (i + 1) % n
        faces.extend([(i, j, n + j), (i, n + j, n + i)])
        faces.append((bottom_center, j, i))
        faces.append((top_center, n + i, n + j))
    face_array = orient_faces_positive_volume(vertices, np.asarray(faces, dtype=np.int64))
    return vertices, face_array


def signed_volume(vertices: Array, faces: Array) -> float:
    tri = np.asarray(vertices, dtype=float)[np.asarray(faces, dtype=np.int64)]
    return float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6.0)


def orient_faces_positive_volume(vertices: Array, faces: Array) -> Array:
    result = np.asarray(faces, dtype=np.int64).copy()
    if signed_volume(vertices, result) < 0:
        result = result[:, [0, 2, 1]]
    return result


def weld_vertices(vertices: Array, faces: Array, tolerance: float = 1e-8) -> tuple[Array, Array]:
    """Merge vertices within a quantized tolerance and remove degenerate faces.

    CAD tessellators commonly duplicate coincident vertices across surface
    patches. Edge-incidence checks must weld those vertices before interpreting
    patch seams as physical boundaries.
    """
    v = np.asarray(vertices, dtype=float)
    f = np.asarray(faces, dtype=np.int64)
    if tolerance <= 0:
        raise GeometryError("weld tolerance must be positive")
    quantized = np.round(v / tolerance).astype(np.int64)
    _, first_indices, inverse = np.unique(quantized, axis=0, return_index=True, return_inverse=True)
    welded_vertices = v[first_indices]
    welded_faces = inverse[f]
    keep = (
        (welded_faces[:, 0] != welded_faces[:, 1])
        & (welded_faces[:, 1] != welded_faces[:, 2])
        & (welded_faces[:, 2] != welded_faces[:, 0])
    )
    welded_faces = welded_faces[keep]
    return welded_vertices, welded_faces


def merge_meshes(meshes: Sequence[tuple[Array, Array]]) -> tuple[Array, Array]:
    vertices: list[Array] = []
    faces: list[Array] = []
    offset = 0
    for mesh_vertices, mesh_faces in meshes:
        v = np.asarray(mesh_vertices, dtype=float)
        f = np.asarray(mesh_faces, dtype=np.int64)
        vertices.append(v)
        faces.append(f + offset)
        offset += len(v)
    return np.vstack(vertices), np.vstack(faces)


def mesh_metrics(vertices: Array, faces: Array) -> dict[str, Any]:
    v = np.asarray(vertices, dtype=float)
    f = np.asarray(faces, dtype=np.int64)
    if v.ndim != 2 or v.shape[1] != 3 or f.ndim != 2 or f.shape[1] != 3:
        raise GeometryError("Mesh must be Vx3 vertices and Fx3 triangle indices")
    if len(v) == 0 or len(f) == 0:
        raise GeometryError("Mesh is empty")
    if f.min() < 0 or f.max() >= len(v):
        raise GeometryError("Face index is out of range")
    triangles = v[f]
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    double_area = np.linalg.norm(cross, axis=1)
    degenerate = int(np.count_nonzero(double_area <= 1e-12))
    area = float(0.5 * double_area.sum())

    edge_counts: dict[tuple[int, int], int] = {}
    for tri in f:
        for a, b in ((int(tri[0]), int(tri[1])), (int(tri[1]), int(tri[2])), (int(tri[2]), int(tri[0]))):
            edge = (a, b) if a < b else (b, a)
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
    boundary_edges = sum(1 for count in edge_counts.values() if count == 1)
    nonmanifold_edges = sum(1 for count in edge_counts.values() if count > 2)

    parent = np.arange(len(v), dtype=np.int64)

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = int(parent[index])
        return index

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    used = np.zeros(len(v), dtype=bool)
    for tri in f:
        a, b, c = map(int, tri)
        used[[a, b, c]] = True
        union(a, b)
        union(b, c)
    components = len({find(int(i)) for i in np.flatnonzero(used)})
    volume = signed_volume(v, f)
    bounds_min = v.min(axis=0)
    bounds_max = v.max(axis=0)
    return {
        "vertex_count": int(len(v)),
        "face_count": int(len(f)),
        "edge_count": int(len(edge_counts)),
        "boundary_edge_count": int(boundary_edges),
        "nonmanifold_edge_count": int(nonmanifold_edges),
        "degenerate_face_count": degenerate,
        "watertight_edge_incidence": bool(boundary_edges == 0 and nonmanifold_edges == 0),
        "connected_components": int(components),
        "surface_area": area,
        "signed_volume": volume,
        "absolute_volume": abs(volume),
        "bounds_min": bounds_min.tolist(),
        "bounds_max": bounds_max.tolist(),
        "extents": (bounds_max - bounds_min).tolist(),
    }


def write_obj(path: str | Path, vertices: Array, faces: Array, object_name: str = "surface") -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# generated by parametric-freeform-surfacing\no {object_name}\n")
        for x, y, z in np.asarray(vertices, dtype=float):
            handle.write(f"v {x:.9f} {y:.9f} {z:.9f}\n")
        for a, b, c in np.asarray(faces, dtype=np.int64):
            handle.write(f"f {a + 1} {b + 1} {c + 1}\n")


def read_obj(path: str | Path) -> tuple[Array, Array]:
    vertices: list[list[float]] = []
    faces: list[tuple[int, int, int]] = []
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] == "v" and len(parts) >= 4:
            vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
        elif parts[0] == "f" and len(parts) >= 4:
            indices: list[int] = []
            for token in parts[1:]:
                raw_index = int(token.split("/")[0])
                indices.append(raw_index - 1 if raw_index > 0 else len(vertices) + raw_index)
            for i in range(1, len(indices) - 1):
                faces.append((indices[0], indices[i], indices[i + 1]))
    if not vertices or not faces:
        raise GeometryError(f"OBJ contains no usable vertices/faces: {path}")
    return np.asarray(vertices, dtype=float), np.asarray(faces, dtype=np.int64)


def write_ascii_stl(path: str | Path, vertices: Array, faces: Array, solid_name: str = "surface") -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    v = np.asarray(vertices, dtype=float)
    f = np.asarray(faces, dtype=np.int64)
    with destination.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"solid {solid_name}\n")
        for tri_indices in f:
            tri = v[tri_indices]
            normal = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            norm = float(np.linalg.norm(normal))
            if norm > 1e-15:
                normal /= norm
            else:
                normal[:] = 0.0
            handle.write(f"  facet normal {normal[0]:.9e} {normal[1]:.9e} {normal[2]:.9e}\n")
            handle.write("    outer loop\n")
            for point in tri:
                handle.write(f"      vertex {point[0]:.9e} {point[1]:.9e} {point[2]:.9e}\n")
            handle.write("    endloop\n  endfacet\n")
        handle.write(f"endsolid {solid_name}\n")


def read_csv_points(path: str | Path) -> Array:
    rows: list[list[float]] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.reader(handle):
            if not raw or not raw[0].strip() or raw[0].lstrip().startswith("#"):
                continue
            values: list[float] = []
            for token in raw[:3]:
                try:
                    values.append(float(token))
                except ValueError:
                    values = []
                    break
            if len(values) >= 2:
                rows.append(values)
    if not rows:
        raise GeometryError(f"No numeric 2D/3D points found in {path}")
    dimension = max(len(row) for row in rows)
    if any(len(row) != dimension for row in rows):
        raise GeometryError("CSV rows have mixed dimensions")
    return as_points(rows)


def write_csv_points(path: str | Path, points: Array) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    pts = as_points(points)
    header = ["x", "y"] if pts.shape[1] == 2 else ["x", "y", "z"]
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows([[f"{value:.9f}" for value in row] for row in pts])


def write_json(path: str | Path, data: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bernstein_all(degree: int, value: Array) -> Array:
    if degree < 1:
        raise GeometryError("Bernstein degree must be at least one")
    t = np.asarray(value, dtype=float)
    result = np.empty((len(t), degree + 1), dtype=float)
    for i in range(degree + 1):
        result[:, i] = math.comb(degree, i) * (t**i) * ((1.0 - t) ** (degree - i))
    return result


def _distance_to_box(points: Array, minimum: Array, maximum: Array) -> Array:
    below = np.maximum(minimum - points, 0.0)
    above = np.maximum(points - maximum, 0.0)
    outside = np.linalg.norm(below + above, axis=1)
    inside = np.all((points >= minimum) & (points <= maximum), axis=1)
    outside[inside] = 0.0
    return outside


def ffd_deform_vertices(vertices: Array, config: dict[str, Any]) -> tuple[Array, dict[str, Any]]:
    """Apply regular Bernstein-lattice FFD with optional fixed boxes."""
    v = np.asarray(vertices, dtype=float)
    if v.ndim != 2 or v.shape[1] != 3 or len(v) < 1:
        raise GeometryError("FFD vertices must be Vx3")
    lattice = config.get("lattice", [4, 3, 3])
    if len(lattice) != 3 or any(int(value) < 2 for value in lattice):
        raise GeometryError("lattice must contain three counts >= 2")
    nx, ny, nz = map(int, lattice)
    minimum = v.min(axis=0)
    maximum = v.max(axis=0)
    extent = maximum - minimum
    if np.any(extent <= 1e-12):
        raise GeometryError("FFD source bounding box is degenerate")
    uvw = np.clip((v - minimum) / extent, 0.0, 1.0)
    bx = bernstein_all(nx - 1, uvw[:, 0])
    by = bernstein_all(ny - 1, uvw[:, 1])
    bz = bernstein_all(nz - 1, uvw[:, 2])

    gx = np.linspace(minimum[0], maximum[0], nx)
    gy = np.linspace(minimum[1], maximum[1], ny)
    gz = np.linspace(minimum[2], maximum[2], nz)
    control = np.stack(np.meshgrid(gx, gy, gz, indexing="ij"), axis=-1)
    for item in config.get("displacements", []):
        index = item.get("index")
        delta = item.get("delta_mm")
        if not isinstance(index, list) or len(index) != 3 or not isinstance(delta, list) or len(delta) != 3:
            raise GeometryError("Each FFD displacement needs index[3] and delta_mm[3]")
        i, j, k = map(int, index)
        if not (0 <= i < nx and 0 <= j < ny and 0 <= k < nz):
            raise GeometryError(f"FFD control index out of range: {index}")
        control[i, j, k] += np.asarray(delta, dtype=float)

    deformed = np.zeros_like(v)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                weight = bx[:, i] * by[:, j] * bz[:, k]
                deformed += weight[:, None] * control[i, j, k]

    protection_weight = np.ones(len(v), dtype=float)
    for box in config.get("fixed_boxes", []):
        box_min = np.asarray(box.get("minimum_mm"), dtype=float)
        box_max = np.asarray(box.get("maximum_mm"), dtype=float)
        if box_min.shape != (3,) or box_max.shape != (3,) or np.any(box_max < box_min):
            raise GeometryError("fixed_boxes require valid minimum_mm and maximum_mm")
        falloff = float(box.get("falloff_mm", 0.0))
        distance = _distance_to_box(v, box_min, box_max)
        if falloff <= 0:
            local = (distance > 0).astype(float)
        else:
            local = smoothstep(distance, 0.0, falloff)
        protection_weight = np.minimum(protection_weight, local)
    result = v + protection_weight[:, None] * (deformed - v)
    displacement = np.linalg.norm(result - v, axis=1)
    report = {
        "lattice": [nx, ny, nz],
        "source_bounds_min": minimum.tolist(),
        "source_bounds_max": maximum.tolist(),
        "vertex_count": int(len(v)),
        "maximum_displacement_mm": float(displacement.max()),
        "rms_displacement_mm": float(np.sqrt(np.mean(displacement**2))),
        "fixed_vertex_count": int(np.count_nonzero(protection_weight <= 1e-12)),
        "partially_protected_vertex_count": int(np.count_nonzero((protection_weight > 1e-12) & (protection_weight < 1.0 - 1e-12))),
    }
    return result, report


@dataclass(frozen=True)
class Mesh:
    vertices: Array
    faces: Array

    def metrics(self) -> dict[str, Any]:
        return mesh_metrics(self.vertices, self.faces)

    def write(self, obj: str | Path | None = None, stl: str | Path | None = None, name: str = "surface") -> None:
        if obj is not None:
            write_obj(obj, self.vertices, self.faces, object_name=name)
        if stl is not None:
            write_ascii_stl(stl, self.vertices, self.faces, solid_name=name)
