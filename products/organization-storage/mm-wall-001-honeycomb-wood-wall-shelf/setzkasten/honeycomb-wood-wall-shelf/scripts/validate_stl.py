#!/usr/bin/env python3
"""Independent STL re-import and topology validation for generated deliverables."""

from __future__ import annotations

import argparse
import json
import struct
from collections import defaultdict, deque
from pathlib import Path

import numpy as np


def load_stl(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = path.read_bytes()
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if 84 + count * 50 == len(data):
            records = np.frombuffer(data, dtype=np.dtype([
                ("normal", "<f4", (3,)),
                ("vertices", "<f4", (3, 3)),
                ("attribute", "<u2"),
            ]), count=count, offset=84)
            vertices = records["vertices"].reshape(-1, 3).astype(np.float64)
            faces = np.arange(len(vertices), dtype=np.int64).reshape(-1, 3)
            return vertices, faces
    raise ValueError(f"Only valid binary STL is supported: {path}")


def merge_vertices(vertices: np.ndarray, faces: np.ndarray, tolerance: float) -> tuple[np.ndarray, np.ndarray]:
    quantized = np.round(vertices / tolerance).astype(np.int64)
    unique, first, inverse = np.unique(
        quantized, axis=0, return_index=True, return_inverse=True
    )
    del unique
    return vertices[first], inverse[faces]


def validate(vertices: np.ndarray, faces: np.ndarray) -> dict:
    edges: dict[tuple[int, int], list[int]] = defaultdict(list)
    face_adjacency: list[list[int]] = [[] for _ in range(len(faces))]
    for face_index, face in enumerate(faces):
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            key = (int(min(a, b)), int(max(a, b)))
            direction = 1 if (a, b) == key else -1
            edges[key].append(direction)
    boundary = sum(len(uses) == 1 for uses in edges.values())
    nonmanifold = sum(len(uses) > 2 for uses in edges.values())
    inconsistent = sum(len(uses) == 2 and uses[0] == uses[1] for uses in edges.values())

    edge_faces: dict[tuple[int, int], list[int]] = defaultdict(list)
    for face_index, face in enumerate(faces):
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge_faces[(int(min(a, b)), int(max(a, b)))].append(face_index)
    for uses in edge_faces.values():
        if len(uses) == 2:
            first, second = uses
            face_adjacency[first].append(second)
            face_adjacency[second].append(first)
    visited = np.zeros(len(faces), dtype=bool)
    bodies = 0
    for start in range(len(faces)):
        if visited[start]:
            continue
        bodies += 1
        visited[start] = True
        queue: deque[int] = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in face_adjacency[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)

    tri = vertices[faces]
    double_area = np.linalg.norm(
        np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1
    )
    signed_volume = float(
        np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum()
        / 6.0
    )
    return {
        "vertices_merged": int(len(vertices)),
        "triangles": int(len(faces)),
        "bounds_min_mm": vertices.min(axis=0).tolist(),
        "bounds_max_mm": vertices.max(axis=0).tolist(),
        "bounds_size_mm": np.ptp(vertices, axis=0).tolist(),
        "signed_volume_mm3": signed_volume,
        "boundary_edges": int(boundary),
        "nonmanifold_edges": int(nonmanifold),
        "inconsistent_winding_edges": int(inconsistent),
        "degenerate_triangles": int(np.count_nonzero(double_area < 1e-10)),
        "bodies": int(bodies),
        "watertight": bool(boundary == 0 and nonmanifold == 0),
        "passed": bool(
            boundary == 0
            and nonmanifold == 0
            and inconsistent == 0
            and np.count_nonzero(double_area < 1e-10) == 0
            and bodies == 1
            and signed_volume > 0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stl", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--merge-tolerance", type=float, default=1e-5)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    raw_vertices, raw_faces = load_stl(args.stl)
    vertices, faces = merge_vertices(raw_vertices, raw_faces, args.merge_tolerance)
    report = validate(vertices, faces)
    report["file"] = str(args.stl)
    report["file_size_bytes"] = args.stl.stat().st_size
    report["merge_tolerance_mm"] = args.merge_tolerance
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if args.require_pass and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
