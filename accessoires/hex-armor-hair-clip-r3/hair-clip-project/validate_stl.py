#!/usr/bin/env python3
"""Deterministic binary-STL structural audit without external mesh libraries."""

from __future__ import annotations

import argparse
import json
import math
import struct
from collections import Counter, defaultdict, deque
from pathlib import Path


def quantize(vertex: tuple[float, float, float], digits: int = 5) -> tuple[float, float, float]:
    return tuple(round(value, digits) for value in vertex)


def read_binary_stl(path: Path):
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError("STL is shorter than its binary header")
    triangle_count = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + triangle_count * 50
    if len(data) != expected:
        raise ValueError(f"Expected {expected} bytes for binary STL, found {len(data)}")
    triangles = []
    normals = []
    offset = 84
    for _ in range(triangle_count):
        values = struct.unpack_from("<12fH", data, offset)
        normals.append(values[0:3])
        triangles.append((values[3:6], values[6:9], values[9:12]))
        offset += 50
    return triangles, normals


def vector_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def audit(path: Path):
    triangles, normals = read_binary_stl(path)
    vertex_ids: dict[tuple[float, float, float], int] = {}
    vertices: list[tuple[float, float, float]] = []
    indexed = []
    degenerate = 0
    duplicate_counter = Counter()
    signed_volume = 0.0
    surface_area = 0.0

    for triangle in triangles:
        ids = []
        for vertex in triangle:
            key = quantize(vertex)
            if key not in vertex_ids:
                vertex_ids[key] = len(vertices)
                vertices.append(key)
            ids.append(vertex_ids[key])
        indexed.append(tuple(ids))
        duplicate_counter[tuple(sorted(ids))] += 1

        a, b, c = triangle
        ab = vector_sub(b, a)
        ac = vector_sub(c, a)
        cr = cross(ab, ac)
        double_area = math.sqrt(dot(cr, cr))
        if len(set(ids)) < 3 or double_area < 1e-9:
            degenerate += 1
        surface_area += 0.5 * double_area
        signed_volume += dot(a, cross(b, c)) / 6.0

    edges = Counter()
    edge_to_triangles = defaultdict(list)
    for tri_idx, (a, b, c) in enumerate(indexed):
        for u, v in ((a, b), (b, c), (c, a)):
            edge = (min(u, v), max(u, v))
            edges[edge] += 1
            edge_to_triangles[edge].append(tri_idx)

    adjacency = [[] for _ in indexed]
    for tri_ids in edge_to_triangles.values():
        for i in range(len(tri_ids)):
            for j in range(i + 1, len(tri_ids)):
                adjacency[tri_ids[i]].append(tri_ids[j])
                adjacency[tri_ids[j]].append(tri_ids[i])

    seen = set()
    components = 0
    for start in range(len(indexed)):
        if start in seen:
            continue
        components += 1
        queue = deque([start])
        seen.add(start)
        while queue:
            current = queue.popleft()
            for nxt in adjacency[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)

    mins = [min(v[i] for v in vertices) for i in range(3)]
    maxs = [max(v[i] for v in vertices) for i in range(3)]
    boundary_edges = sum(1 for count in edges.values() if count == 1)
    nonmanifold_edges = sum(1 for count in edges.values() if count != 2)
    duplicate_triangles = sum(count - 1 for count in duplicate_counter.values() if count > 1)

    return {
        "file": str(path),
        "size_bytes": path.stat().st_size,
        "triangle_count": len(triangles),
        "unique_vertices_quantized_1e-5_mm": len(vertices),
        "bounds_mm": {"min": mins, "max": maxs},
        "dimensions_mm": [maxs[i] - mins[i] for i in range(3)],
        "surface_area_mm2": surface_area,
        "signed_volume_mm3": signed_volume,
        "absolute_volume_mm3": abs(signed_volume),
        "triangle_components": components,
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "degenerate_triangles": degenerate,
        "duplicate_triangles": duplicate_triangles,
        "watertight_edge_test": nonmanifold_edges == 0,
        "positive_winding_volume": signed_volume > 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stl", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expect-components", type=int, default=1)
    args = parser.parse_args()
    result = audit(args.stl)
    result["expected_components"] = args.expect_components
    result["component_test_pass"] = result["triangle_components"] == args.expect_components
    result["overall_pass"] = (
        result["watertight_edge_test"]
        and result["positive_winding_volume"]
        and result["component_test_pass"]
        and result["degenerate_triangles"] == 0
        and result["duplicate_triangles"] == 0
    )
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    raise SystemExit(0 if result["overall_pass"] else 2)


if __name__ == "__main__":
    main()

