#!/usr/bin/env python3
"""Independent binary/ASCII STL topology validator with vertex welding."""

from __future__ import annotations

import argparse
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def load_binary_stl(path: Path) -> np.ndarray:
    raw = path.read_bytes()
    if len(raw) < 84:
        raise ValueError("file too small for binary STL")
    count = struct.unpack_from("<I", raw, 80)[0]
    expected = 84 + count * 50
    if expected != len(raw):
        raise ValueError(f"binary STL length mismatch: expected {expected}, got {len(raw)}")
    dtype = np.dtype([
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ])
    records = np.frombuffer(raw, dtype=dtype, count=count, offset=84)
    return records["vertices"].astype(np.float64)


class DisjointSet:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        a = self.find(left)
        b = self.find(right)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1


def validate(path: Path, weld_tolerance: float) -> dict:
    triangles = load_binary_stl(path)
    if triangles.size == 0:
        raise ValueError("STL contains no triangles")
    if not np.isfinite(triangles).all():
        raise ValueError("STL contains non-finite coordinates")

    flat = triangles.reshape(-1, 3)
    quantized = np.rint(flat / weld_tolerance).astype(np.int64)
    vertex_map: dict[tuple[int, int, int], int] = {}
    unique_vertices: list[np.ndarray] = []
    ids = np.empty(len(flat), dtype=np.int64)
    for index, (point, key_values) in enumerate(zip(flat, quantized, strict=True)):
        key = tuple(int(value) for value in key_values)
        vertex_id = vertex_map.get(key)
        if vertex_id is None:
            vertex_id = len(unique_vertices)
            vertex_map[key] = vertex_id
            unique_vertices.append(point)
        ids[index] = vertex_id
    face_ids = ids.reshape(-1, 3)

    edges: Counter[tuple[int, int]] = Counter()
    oriented_edges: Counter[tuple[int, int]] = Counter()
    edge_faces: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    duplicate_face_keys: Counter[tuple[int, int, int]] = Counter()
    dsu = DisjointSet(len(face_ids))
    zero_area = 0
    signed_volume = 0.0

    for face_index, (face, points) in enumerate(zip(face_ids, triangles, strict=True)):
        a, b, c = (int(v) for v in face)
        duplicate_face_keys[tuple(sorted((a, b, c)))] += 1
        cross = np.cross(points[1] - points[0], points[2] - points[0])
        if float(np.linalg.norm(cross)) <= weld_tolerance * weld_tolerance:
            zero_area += 1
        signed_volume += float(np.dot(points[0], np.cross(points[1], points[2]))) / 6.0
        for start, end in ((a, b), (b, c), (c, a)):
            undirected = (start, end) if start < end else (end, start)
            edges[undirected] += 1
            oriented_edges[(start, end)] += 1
            for other_face in edge_faces[undirected]:
                dsu.union(face_index, other_face)
            edge_faces[undirected].append(face_index)

    boundary_edges = sum(1 for count in edges.values() if count == 1)
    non_manifold_edges = sum(1 for count in edges.values() if count > 2)
    inconsistent_edges = 0
    for left, right in edges:
        if edges[(left, right)] == 2:
            if oriented_edges[(left, right)] != 1 or oriented_edges[(right, left)] != 1:
                inconsistent_edges += 1
    duplicate_faces = sum(count - 1 for count in duplicate_face_keys.values() if count > 1)
    bodies = len({dsu.find(index) for index in range(len(face_ids))})
    minimum = triangles.min(axis=(0, 1))
    maximum = triangles.max(axis=(0, 1))
    volume = abs(signed_volume)
    result = {
        "file": str(path),
        "triangles": int(len(triangles)),
        "welded_vertices": int(len(unique_vertices)),
        "bounds_min": minimum.tolist(),
        "bounds_max": maximum.tolist(),
        "size_mm": (maximum - minimum).tolist(),
        "signed_volume_mm3": signed_volume,
        "volume_mm3": volume,
        "boundary_edges": boundary_edges,
        "non_manifold_edges": non_manifold_edges,
        "inconsistent_winding_edges": inconsistent_edges,
        "zero_area_triangles": zero_area,
        "duplicate_faces": duplicate_faces,
        "connected_bodies": bodies,
    }
    result["checks"] = {
        "finite": True,
        "positive_volume": volume > 1.0,
        "watertight": boundary_edges == 0,
        "manifold_edges": non_manifold_edges == 0,
        "consistent_winding": inconsistent_edges == 0,
        "single_body": bodies == 1,
        "no_zero_area_triangles": zero_area == 0,
        "no_duplicate_faces": duplicate_faces == 0,
    }
    result["pass"] = all(result["checks"].values())
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--weld-tolerance", type=float, default=1.0e-9)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    results = []
    for path in args.files:
        results.append(validate(path, args.weld_tolerance))
    summary = {
        "validator": "independent-stl-edge-audit-v1",
        "weld_tolerance_mm": args.weld_tolerance,
        "files": results,
        "pass": all(result["pass"] for result in results),
    }
    rendered = json.dumps(summary, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if args.require_pass and not summary["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
