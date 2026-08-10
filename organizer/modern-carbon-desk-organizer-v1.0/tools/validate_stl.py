#!/usr/bin/env python3
"""Independent binary-STL topology and bounds validator.

This intentionally reloads exported manufacturing meshes instead of trusting
the in-memory CSG result. It checks edge incidence, winding, components, bounds,
area, and signed volume. It is not a slicer or a self-intersection solver.
"""

from __future__ import annotations

import json
import math
import struct
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STL_DIR = ROOT / "output" / "stl"
REPORT = ROOT / "output" / "validation-report.json"


def read_binary_stl(path: Path):
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"{path.name}: too small for binary STL")
    n = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + n * 50
    if len(data) != expected:
        raise ValueError(f"{path.name}: size {len(data)} != binary STL expectation {expected}")
    triangles = []
    offset = 84
    for _ in range(n):
        values = struct.unpack_from("<12fH", data, offset)
        triangles.append((values[3:6], values[6:9], values[9:12]))
        offset += 50
    return triangles


def key(v, precision=5):
    return tuple(round(float(x), precision) for x in v)


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def analyze(path: Path):
    tris = read_binary_stl(path)
    if not tris:
        raise ValueError(f"{path.name}: no triangles")

    edge_counts = Counter()
    directed = Counter()
    adjacency = defaultdict(set)
    area = 0.0
    signed_volume = 0.0
    vertices = set()
    minv = [math.inf, math.inf, math.inf]
    maxv = [-math.inf, -math.inf, -math.inf]
    degenerate = 0

    for tri in tris:
        ks = [key(v) for v in tri]
        vertices.update(ks)
        for v in tri:
            for i in range(3):
                minv[i] = min(minv[i], v[i])
                maxv[i] = max(maxv[i], v[i])
        normal2 = cross(sub(tri[1], tri[0]), sub(tri[2], tri[0]))
        double_area = math.sqrt(dot(normal2, normal2))
        if double_area < 1e-9:
            degenerate += 1
        area += 0.5 * double_area
        signed_volume += dot(tri[0], cross(tri[1], tri[2])) / 6.0
        for i, j in ((0, 1), (1, 2), (2, 0)):
            a, b = ks[i], ks[j]
            undirected = tuple(sorted((a, b)))
            edge_counts[undirected] += 1
            directed[(a, b)] += 1
            adjacency[a].add(b)
            adjacency[b].add(a)

    unseen = set(vertices)
    components = 0
    while unseen:
        components += 1
        start = unseen.pop()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nxt in adjacency[node]:
                if nxt in unseen:
                    unseen.remove(nxt)
                    queue.append(nxt)

    boundary_edges = sum(1 for count in edge_counts.values() if count == 1)
    nonmanifold_edges = sum(1 for count in edge_counts.values() if count > 2)
    winding_errors = 0
    for a, b in edge_counts:
        if edge_counts[(a, b)] == 2 and not (directed[(a, b)] == 1 and directed[(b, a)] == 1):
            winding_errors += 1

    size = [maxv[i] - minv[i] for i in range(3)]
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "triangles": len(tris),
        "unique_vertices_rounded_1e-5_mm": len(vertices),
        "bounds_mm": [minv, maxv],
        "size_mm": size,
        "surface_area_mm2": area,
        "signed_volume_mm3": signed_volume,
        "absolute_volume_mm3": abs(signed_volume),
        "connected_components": components,
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "winding_errors": winding_errors,
        "degenerate_triangles": degenerate,
        "watertight": boundary_edges == 0 and nonmanifold_edges == 0,
        "consistent_winding": winding_errors == 0,
    }


def main():
    expected_components = {
        "01_housing_print_on_back.stl": 1,
        "02_drawer_print_twice.stl": 1,
        "03_top_sorter_print_bottom_down.stl": 1,
        "04_fit_coupon_optional.stl": 6,
        "05_carbon_texture_coupon_optional.stl": 1,
    }
    reports = []
    failures = []
    for path in sorted(STL_DIR.glob("*.stl")):
        report = analyze(path)
        report["expected_components"] = expected_components[path.name]
        report["component_count_ok"] = report["connected_components"] == expected_components[path.name]
        report["fits_kobra_3_max_build_volume"] = all(
            actual <= limit + 1e-4 for actual, limit in zip(report["size_mm"], (420, 420, 500))
        )
        reports.append(report)
        for check in ("watertight", "consistent_winding", "component_count_ok", "fits_kobra_3_max_build_volume"):
            if not report[check]:
                failures.append(f"{path.name}: {check} failed")
        if report["degenerate_triangles"]:
            failures.append(f"{path.name}: degenerate triangles = {report['degenerate_triangles']}")

    summary = {
        "status": "pass" if not failures else "fail",
        "scope": "V1 exported-mesh topology and envelope; slicer and physical coupons remain required",
        "files": reports,
        "failures": failures,
    }
    REPORT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "files": len(reports), "failures": failures}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
