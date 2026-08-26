#!/usr/bin/env python3
"""Audit structural properties and scale of an exported triangular mesh.

Binary and ASCII STL are supported with NumPy only. OBJ/PLY/GLB and other
formats use the optional trimesh dependency. The script never repairs input.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import struct
from typing import Any, Iterable

import numpy as np


@dataclass
class MeshArrays:
    name: str
    vertices: np.ndarray
    faces: np.ndarray
    units: str | None = None


def positive(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report mesh bounds, topology signals, and complexity without modifying it."
    )
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-max-dimension-mm", type=positive)
    parser.add_argument("--size-tolerance-percent", type=positive, default=2.0)
    parser.add_argument("--max-faces", type=int)
    parser.add_argument("--require-watertight", action="store_true")
    parser.add_argument("--require-winding-consistent", action="store_true")
    parser.add_argument("--require-single-component", action="store_true")
    parser.add_argument("--skip-components", action="store_true")
    parser.add_argument(
        "--duplicate-face-limit",
        type=int,
        default=500_000,
        help="Skip duplicate-face detection above this face count (default: 500000).",
    )
    return parser.parse_args()


def chunk_slices(length: int, size: int = 250_000) -> Iterable[slice]:
    for start in range(0, length, size):
        yield slice(start, min(start + size, length))


def load_stl(path: Path) -> list[MeshArrays]:
    data = path.read_bytes()
    raw_vertices: np.ndarray
    if len(data) >= 84:
        triangle_count = struct.unpack_from("<I", data, 80)[0]
        expected_size = 84 + 50 * triangle_count
    else:
        triangle_count = 0
        expected_size = -1

    if expected_size == len(data):
        dtype = np.dtype(
            [
                ("normal", "<f4", (3,)),
                ("vertices", "<f4", (3, 3)),
                ("attribute", "<u2"),
            ]
        )
        records = np.frombuffer(data, dtype=dtype, count=triangle_count, offset=84)
        raw_vertices = records["vertices"].reshape(-1, 3).astype(np.float64)
    else:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SystemExit(
                "STL is neither a size-consistent binary STL nor decodable ASCII STL"
            ) from exc
        parsed: list[list[float]] = []
        for line in text.splitlines():
            parts = line.strip().split()
            if len(parts) == 4 and parts[0].lower() == "vertex":
                parsed.append([float(parts[1]), float(parts[2]), float(parts[3])])
        if not parsed or len(parsed) % 3:
            raise SystemExit("ASCII STL contains no complete triangle vertex groups")
        raw_vertices = np.asarray(parsed, dtype=np.float64)

    if len(raw_vertices) == 0:
        raise SystemExit("STL contains no triangles")
    vertices, inverse = np.unique(raw_vertices, axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3).astype(np.int64)
    return [MeshArrays(path.stem, vertices, faces, None)]


def load_with_trimesh(path: Path) -> list[MeshArrays]:
    try:
        import trimesh
    except ImportError as exc:
        raise SystemExit(
            f"{path.suffix} requires the optional trimesh dependency. STL can be "
            "audited without it. Install packages only with environment-owner approval."
        ) from exc
    loaded = trimesh.load(path, process=False)
    if isinstance(loaded, trimesh.Trimesh):
        meshes = [(path.stem, loaded)]
    elif isinstance(loaded, trimesh.Scene):
        try:
            dumped = loaded.dump(concatenate=False)
        except TypeError:
            dumped = loaded.dump()
        if isinstance(dumped, trimesh.Trimesh):
            meshes = [(path.stem, dumped)]
        else:
            meshes = [
                (f"geometry-{index + 1}", geometry)
                for index, geometry in enumerate(list(dumped))
                if isinstance(geometry, trimesh.Trimesh)
            ]
    else:
        meshes = []
    result = [
        MeshArrays(
            name,
            np.asarray(mesh.vertices, dtype=np.float64),
            np.asarray(mesh.faces, dtype=np.int64),
            getattr(mesh, "units", None),
        )
        for name, mesh in meshes
        if len(mesh.faces)
    ]
    if not result:
        raise SystemExit("No triangular mesh geometry was found in the file")
    return result


def load_meshes(path: Path) -> list[MeshArrays]:
    if path.suffix.lower() == ".stl":
        return load_stl(path)
    return load_with_trimesh(path)


def combine_meshes(meshes: list[MeshArrays]) -> MeshArrays:
    vertices: list[np.ndarray] = []
    faces: list[np.ndarray] = []
    offset = 0
    for mesh in meshes:
        vertices.append(mesh.vertices)
        faces.append(mesh.faces + offset)
        offset += len(mesh.vertices)
    return MeshArrays(
        "combined",
        np.concatenate(vertices, axis=0),
        np.concatenate(faces, axis=0),
        meshes[0].units if len({mesh.units for mesh in meshes}) == 1 else None,
    )


def bounds(mesh: MeshArrays) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    minimum = np.min(mesh.vertices, axis=0)
    maximum = np.max(mesh.vertices, axis=0)
    return minimum, maximum, maximum - minimum


def triangle_area_and_volume(mesh: MeshArrays) -> tuple[float, float, int, float]:
    _, _, extents = bounds(mesh)
    diagonal = float(np.linalg.norm(extents))
    area_epsilon = max((diagonal**2) * 1e-14, 1e-24)
    area = 0.0
    signed_volume = 0.0
    degenerate = 0
    for part in chunk_slices(len(mesh.faces)):
        triangles = mesh.vertices[mesh.faces[part]]
        cross = np.cross(
            triangles[:, 1] - triangles[:, 0],
            triangles[:, 2] - triangles[:, 0],
        )
        triangle_areas = 0.5 * np.linalg.norm(cross, axis=1)
        area += float(np.sum(triangle_areas))
        degenerate += int(np.count_nonzero(triangle_areas <= area_epsilon))
        signed_volume += float(
            np.sum(np.einsum("ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])))
            / 6.0
        )
    return area, signed_volume, degenerate, area_epsilon


def edge_topology(mesh: MeshArrays) -> dict[str, Any]:
    faces = mesh.faces
    directed = np.concatenate(
        [faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]], axis=0
    )
    canonical = np.sort(directed, axis=1)
    unique_edges, inverse, counts = np.unique(
        canonical, axis=0, return_inverse=True, return_counts=True
    )
    signs = np.where(directed[:, 0] == canonical[:, 0], 1, -1)
    orientation_sum = np.bincount(inverse, weights=signs, minlength=len(unique_edges))
    watertight = bool(np.all(counts == 2))
    winding_consistent = bool(np.all((counts == 2) & (orientation_sum == 0)))
    return {
        "unique_edges": unique_edges,
        "inverse": inverse,
        "counts": counts,
        "watertight": watertight,
        "winding_consistent": winding_consistent,
        "boundary_edges": int(np.count_nonzero(counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(counts > 2)),
    }


def count_components(mesh: MeshArrays, topology: dict[str, Any]) -> int:
    face_count = len(mesh.faces)
    parent = np.arange(face_count, dtype=np.int64)
    rank = np.zeros(face_count, dtype=np.uint8)

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = int(parent[item])
        return item

    def union(first: int, second: int) -> None:
        root_a, root_b = find(first), find(second)
        if root_a == root_b:
            return
        if rank[root_a] < rank[root_b]:
            root_a, root_b = root_b, root_a
        parent[root_b] = root_a
        if rank[root_a] == rank[root_b]:
            rank[root_a] += 1

    inverse = topology["inverse"]
    counts = topology["counts"]
    face_ids = np.concatenate([np.arange(face_count, dtype=np.int64)] * 3)
    order = np.argsort(inverse, kind="stable")
    starts = np.cumsum(np.concatenate(([0], counts[:-1])))
    for start, count in zip(starts, counts):
        if count < 2:
            continue
        group_faces = face_ids[order[start : start + count]]
        anchor = int(group_faces[0])
        for other in group_faces[1:]:
            union(anchor, int(other))
    roots = {find(index) for index in range(face_count)}
    return len(roots)


def count_unreferenced_vertices(mesh: MeshArrays) -> int:
    referenced = np.zeros(len(mesh.vertices), dtype=bool)
    for part in chunk_slices(len(mesh.faces)):
        referenced[mesh.faces[part].reshape(-1)] = True
    return int(np.count_nonzero(~referenced))


def count_duplicate_faces(mesh: MeshArrays, limit: int) -> int | None:
    if len(mesh.faces) > limit:
        return None
    canonical = np.sort(mesh.faces, axis=1)
    return int(len(mesh.faces) - len(np.unique(canonical, axis=0)))


def finite(value: Any) -> Any:
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, np.ndarray):
        return [finite(item) for item in value.tolist()]
    return value


def simple_geometry_report(mesh: MeshArrays) -> dict[str, Any]:
    minimum, maximum, extents = bounds(mesh)
    return {
        "name": mesh.name,
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "bounds": [finite(minimum), finite(maximum)],
        "extents": finite(extents),
        "metadata_units": mesh.units,
    }


def main() -> int:
    args = parse_args()
    if not args.mesh.is_file():
        raise SystemExit(f"Mesh not found: {args.mesh}")
    if args.max_faces is not None and args.max_faces <= 0:
        raise SystemExit("--max-faces must be greater than zero")
    if args.duplicate_face_limit < 0:
        raise SystemExit("--duplicate-face-limit cannot be negative")

    geometries = load_meshes(args.mesh)
    mesh = combine_meshes(geometries)
    minimum, maximum, extents = bounds(mesh)
    area, signed_volume, degenerate_count, area_epsilon = triangle_area_and_volume(mesh)
    topology = edge_topology(mesh)
    watertight = topology["watertight"]
    winding = topology["winding_consistent"]
    outward = signed_volume > 0
    is_volume = watertight and winding and outward
    unreferenced_vertices = count_unreferenced_vertices(mesh)
    duplicate_faces = count_duplicate_faces(mesh, args.duplicate_face_limit)
    components = None if args.skip_components else count_components(mesh, topology)
    euler = len(mesh.vertices) - len(topology["unique_edges"]) + len(mesh.faces)

    warnings: list[str] = []
    failures: list[str] = []
    if duplicate_faces is None:
        warnings.append(
            "Duplicate-face detection was skipped because the mesh exceeds --duplicate-face-limit."
        )
    if args.skip_components:
        warnings.append("Connected-component analysis was skipped by request.")
    if not watertight:
        warnings.append("Mesh is not watertight; printable-volume claims are unsafe.")
    if not winding:
        warnings.append("Face winding is inconsistent or non-manifold.")
    if watertight and winding and not outward:
        warnings.append("Mesh is closed and consistently wound but appears inward-facing.")
    if degenerate_count:
        warnings.append(f"Detected {degenerate_count} near-zero-area faces.")
    if unreferenced_vertices:
        warnings.append(f"Detected {unreferenced_vertices} unreferenced vertices.")
    if duplicate_faces:
        warnings.append(f"Detected {duplicate_faces} duplicate faces by vertex index.")
    if components is not None and components != 1:
        warnings.append(f"Mesh contains {components} edge-connected face components.")

    max_extent = float(np.max(extents))
    size_check = None
    if args.expected_max_dimension_mm:
        deviation_percent = (
            100.0
            * (max_extent - args.expected_max_dimension_mm)
            / args.expected_max_dimension_mm
        )
        size_check = {
            "expected_max_dimension_mm": args.expected_max_dimension_mm,
            "observed_max_coordinate_extent": max_extent,
            "deviation_percent_assuming_mesh_units_are_mm": deviation_percent,
            "tolerance_percent": args.size_tolerance_percent,
            "passes": abs(deviation_percent) <= args.size_tolerance_percent,
        }
        if not size_check["passes"]:
            failures.append("expected size")

    if args.max_faces is not None and len(mesh.faces) > args.max_faces:
        failures.append("maximum face count")
    if args.require_watertight and not watertight:
        failures.append("watertightness")
    if args.require_winding_consistent and not winding:
        failures.append("winding consistency")
    if args.require_single_component and components != 1:
        failures.append("single component")

    triangle_count = len(mesh.faces)
    report: dict[str, Any] = {
        "file": {
            "path": str(args.mesh.resolve()),
            "size_bytes": args.mesh.stat().st_size,
            "extension": args.mesh.suffix.lower(),
            "loader": "built-in STL" if args.mesh.suffix.lower() == ".stl" else "trimesh",
        },
        "scene_geometry_count": len(geometries),
        "scene_geometries": [simple_geometry_report(item) for item in geometries],
        "combined_mesh": {
            "vertices": len(mesh.vertices),
            "faces": triangle_count,
            "bounds_coordinate_units": [finite(minimum), finite(maximum)],
            "extents_coordinate_units": finite(extents),
            "max_extent_coordinate_units": max_extent,
            "metadata_units": mesh.units,
            "surface_area_coordinate_units_squared": area,
            "volume_coordinate_units_cubed": signed_volume if is_volume else None,
            "raw_signed_volume_even_if_invalid": signed_volume,
            "euler_number": int(euler),
            "watertight": watertight,
            "winding_consistent": winding,
            "outward_orientation_from_signed_volume": outward,
            "is_volume": is_volume,
            "connected_face_components": components,
            "unique_edges": len(topology["unique_edges"]),
            "boundary_edges": topology["boundary_edges"],
            "nonmanifold_edges": topology["nonmanifold_edges"],
            "degenerate_faces": degenerate_count,
            "degenerate_area_epsilon_coordinate_units_squared": area_epsilon,
            "duplicate_faces_by_vertex_index": duplicate_faces,
            "unreferenced_vertices": unreferenced_vertices,
        },
        "complexity_estimates": {
            "binary_stl_bytes_if_exported": 84 + 50 * triangle_count,
            "working_mesh_mib_range_80_to_240_bytes_per_triangle": [
                triangle_count * 80 / (1024**2),
                triangle_count * 240 / (1024**2),
            ],
        },
        "size_check": size_check,
        "warnings": warnings,
        "failures": failures,
        "limitations": [
            "STL units are absent; compare against an expected dimension.",
            "Exact-coordinate welding is used for STL. Near-coincident seams may remain separate.",
            "This audit does not certify minimum wall thickness, self-intersection, clearances, load capacity, or slicer behavior.",
            "No automatic repairs were applied.",
        ],
    }

    rendered = json.dumps(report, indent=2, allow_nan=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
