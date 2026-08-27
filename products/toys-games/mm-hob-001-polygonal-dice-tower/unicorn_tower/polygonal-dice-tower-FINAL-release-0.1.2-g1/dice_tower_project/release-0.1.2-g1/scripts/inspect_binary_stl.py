#!/usr/bin/env python3
"""Independent binary-STL topology and geometry inspection."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import numpy as np


RECORD_DTYPE = np.dtype(
    [
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ]
)


def read_binary_stl(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open("rb") as handle:
        header = handle.read(80)
        if len(header) != 80:
            raise ValueError("Incomplete STL header")
        count_bytes = handle.read(4)
        if len(count_bytes) != 4:
            raise ValueError("Missing STL facet count")
        count = struct.unpack("<I", count_bytes)[0]
        records = np.fromfile(handle, dtype=RECORD_DTYPE, count=count)
    if len(records) != count:
        raise ValueError(f"Expected {count} facets, read {len(records)}")
    if path.stat().st_size != 84 + 50 * count:
        raise ValueError("File size does not match binary-STL facet count")
    return records["vertices"].astype(np.float64), records["normal"].astype(np.float64)


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = np.arange(size, dtype=np.int64)
        self.rank = np.zeros(size, dtype=np.int8)

    def find(self, item: int) -> int:
        root = item
        while self.parent[root] != root:
            root = int(self.parent[root])
        while self.parent[item] != item:
            parent = int(self.parent[item])
            self.parent[item] = root
            item = parent
        return root

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


def inspect(path: Path) -> dict[str, object]:
    triangles, stored_normals = read_binary_stl(path)
    unique_vertices, inverse = np.unique(
        triangles.reshape(-1, 3), axis=0, return_inverse=True
    )
    faces = inverse.reshape(-1, 3)

    edges = np.concatenate(
        [faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]], axis=0
    )
    sorted_edges = np.sort(edges, axis=1)
    unique_edges, edge_counts = np.unique(sorted_edges, axis=0, return_counts=True)
    boundary_edges = int(np.count_nonzero(edge_counts == 1))
    overconnected_edges = int(np.count_nonzero(edge_counts > 2))

    duplicate_faces = int(
        len(faces) - len(np.unique(np.sort(faces, axis=1), axis=0))
    )
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    doubled_area = np.linalg.norm(cross, axis=1)
    degenerate_faces = int(np.count_nonzero(doubled_area <= 1e-10))
    calculated_normals = cross / np.maximum(doubled_area[:, None], 1e-30)
    stored_lengths = np.linalg.norm(stored_normals, axis=1)
    normalized_stored = stored_normals / np.maximum(stored_lengths[:, None], 1e-30)
    consistent_normals = float(
        np.mean(np.einsum("ij,ij->i", calculated_normals, normalized_stored) > 0.999)
    )

    union_find = UnionFind(len(faces))
    edge_to_face: dict[tuple[int, int], int] = {}
    for face_index, face in enumerate(faces):
        for first, second in ((0, 1), (1, 2), (2, 0)):
            edge = tuple(sorted((int(face[first]), int(face[second]))))
            previous = edge_to_face.get(edge)
            if previous is None:
                edge_to_face[edge] = face_index
            else:
                union_find.union(previous, face_index)
    components = len({union_find.find(index) for index in range(len(faces))})

    signed_volume = float(
        np.einsum(
            "ij,ij->i",
            triangles[:, 0],
            np.cross(triangles[:, 1], triangles[:, 2]),
        ).sum()
        / 6.0
    )
    bounds_min = triangles.reshape(-1, 3).min(axis=0)
    bounds_max = triangles.reshape(-1, 3).max(axis=0)

    return {
        "file": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sizeBytes": path.stat().st_size,
        "triangleCount": int(len(triangles)),
        "uniqueVertexCountExact": int(len(unique_vertices)),
        "connectedFaceComponents": components,
        "boundaryEdges": boundary_edges,
        "overconnectedEdges": overconnected_edges,
        "duplicateFaces": duplicate_faces,
        "degenerateFaces": degenerate_faces,
        "watertightByEdgeIncidence": boundary_edges == 0 and overconnected_edges == 0,
        "consistentStoredNormalsFraction": consistent_normals,
        "boundsMin": bounds_min.tolist(),
        "boundsMax": bounds_max.tolist(),
        "extents": (bounds_max - bounds_min).tolist(),
        "surfaceAreaMm2": float(doubled_area.sum() / 2.0),
        "signedVolumeMm3": signed_volume,
        "positiveVolume": signed_volume > 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stl", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--require-watertight", action="store_true")
    parser.add_argument("--max-components", type=int)
    args = parser.parse_args()
    report = inspect(args.stl.resolve())
    rendered = json.dumps(report, indent=2) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if args.require_watertight and not report["watertightByEdgeIncidence"]:
        raise SystemExit(2)
    if args.max_components is not None and report["connectedFaceComponents"] > args.max_components:
        raise SystemExit(3)
    if not report["positiveVolume"]:
        raise SystemExit(4)


if __name__ == "__main__":
    main()
