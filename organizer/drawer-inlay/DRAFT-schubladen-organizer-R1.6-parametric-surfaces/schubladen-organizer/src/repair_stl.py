#!/usr/bin/env python3
"""Repair Float32-collapsed STL slivers by deterministic local edge collapse."""

from __future__ import annotations

import argparse
import json
import struct
from collections import Counter
from pathlib import Path

import numpy as np


def read_stl(path: Path) -> tuple[np.ndarray, np.ndarray]:
    raw = path.read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + count * 50:
        raise ValueError(f"invalid binary STL: {path}")
    dtype = np.dtype([
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ])
    triangles = np.frombuffer(raw, dtype=dtype, count=count, offset=84)["vertices"].copy()
    vertex_map: dict[tuple[float, float, float], int] = {}
    vertices: list[np.ndarray] = []
    faces = np.empty((count, 3), dtype=np.int64)
    for face_index, triangle in enumerate(triangles):
        for corner, point in enumerate(triangle):
            key = tuple(float(value) for value in point)
            vertex = vertex_map.get(key)
            if vertex is None:
                vertex = len(vertices)
                vertex_map[key] = vertex
                vertices.append(point.astype(np.float64))
            faces[face_index, corner] = vertex
    return np.asarray(vertices, dtype=np.float64), faces


def face_norms(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    points = vertices[faces]
    return np.linalg.norm(np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0]), axis=1)


def compact(vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    used = np.unique(faces.reshape(-1))
    remap = np.full(len(vertices), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return vertices[used], remap[faces]


def edge_counts(faces: np.ndarray) -> Counter[tuple[int, int]]:
    counts: Counter[tuple[int, int]] = Counter()
    for a, b, c in faces:
        for left, right in ((a, b), (b, c), (c, a)):
            edge = (int(left), int(right)) if left < right else (int(right), int(left))
            counts[edge] += 1
    return counts


def repair(vertices: np.ndarray, faces: np.ndarray, area2_epsilon: float) -> tuple[np.ndarray, np.ndarray, dict]:
    original_faces = len(faces)
    collapsed_edges = 0
    for _ in range(16):
        norms = face_norms(vertices, faces)
        bad = np.flatnonzero(norms <= area2_epsilon)
        if not len(bad):
            break
        replacements: dict[int, int] = {}
        for face_index in bad:
            face = faces[face_index]
            points = vertices[face]
            candidates = [
                (float(np.linalg.norm(points[0] - points[1])), int(face[0]), int(face[1])),
                (float(np.linalg.norm(points[1] - points[2])), int(face[1]), int(face[2])),
                (float(np.linalg.norm(points[2] - points[0])), int(face[2]), int(face[0])),
            ]
            _, keep, drop = min(candidates)
            while keep in replacements:
                keep = replacements[keep]
            while drop in replacements:
                drop = replacements[drop]
            if keep == drop:
                continue
            vertices[keep] = 0.5 * (vertices[keep] + vertices[drop])
            replacements[drop] = keep
            collapsed_edges += 1
        if not replacements:
            faces = faces[norms > area2_epsilon]
            break
        for drop, keep in replacements.items():
            faces[faces == drop] = keep
        distinct = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 2] != faces[:, 0])
        faces = faces[distinct]
        vertices, faces = compact(vertices, faces)
    norms = face_norms(vertices, faces)
    faces = faces[norms > area2_epsilon]
    vertices, faces = compact(vertices, faces)

    # Deduplicate any identical oriented faces created by an edge collapse.
    seen: set[tuple[int, int, int]] = set()
    kept = []
    for face in faces:
        key = tuple(sorted(int(value) for value in face))
        if key not in seen:
            seen.add(key)
            kept.append(face)
    faces = np.asarray(kept, dtype=np.int64)
    vertices, faces = compact(vertices, faces)
    edges = edge_counts(faces)
    report = {
        "original_faces": original_faces,
        "repaired_faces": int(len(faces)),
        "collapsed_edges": collapsed_edges,
        "boundary_edges": sum(count == 1 for count in edges.values()),
        "non_manifold_edges": sum(count > 2 for count in edges.values()),
        "remaining_degenerate_faces": int(np.count_nonzero(face_norms(vertices, faces) <= area2_epsilon)),
    }
    if report["boundary_edges"] or report["non_manifold_edges"] or report["remaining_degenerate_faces"]:
        raise ValueError(f"local STL repair did not close the mesh: {report}")
    return vertices, faces, report


def write_stl(path: Path, vertices: np.ndarray, faces: np.ndarray, header: str) -> None:
    buffer = bytearray(84 + len(faces) * 50)
    buffer[:80] = header.encode("ascii", "replace")[:80].ljust(80, b"\0")
    struct.pack_into("<I", buffer, 80, len(faces))
    for index, face in enumerate(faces):
        points = vertices[face].astype(np.float32)
        normal = np.cross(points[1] - points[0], points[2] - points[0])
        length = float(np.linalg.norm(normal))
        normal = normal / length
        offset = 84 + index * 50
        struct.pack_into("<12fH", buffer, offset, *normal, *points.reshape(-1), 0)
    path.write_bytes(buffer)


def write_mesh_cache(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(struct.pack("<4sIII", b"MSH1", len(vertices), len(faces), 3))
        handle.write(vertices.astype("<f4", copy=False).tobytes(order="C"))
        handle.write(faces.astype("<u4", copy=False).tobytes(order="C"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--area2-epsilon", type=float, default=1.0e-18)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--mesh-cache-dir", type=Path)
    args = parser.parse_args()
    results = []
    for path in args.files:
        vertices, faces = read_stl(path)
        vertices, faces, report = repair(vertices, faces, args.area2_epsilon)
        write_stl(path, vertices, faces, f"DRAFT repaired continuous16 {path.stem}")
        cache_path = None
        if args.mesh_cache_dir and path.name.endswith("-surface.stl"):
            module_id = path.name.removeprefix("DRAFT-").removesuffix("-surface.stl")
            cache_path = args.mesh_cache_dir / f"{module_id}.meshbin"
            write_mesh_cache(cache_path, vertices, faces)
        results.append({"file": str(path), "mesh_cache": str(cache_path) if cache_path else None, **report})
    output = {"repair": "local-degenerate-edge-collapse-v1", "files": results}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
