#!/usr/bin/env python3
"""Independent binary-STL checks for the Regenwasser-Filterbrunnen project."""

from __future__ import annotations

import argparse
import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np


STL_DTYPE = np.dtype(
    [
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ]
)


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = np.arange(size, dtype=np.int64)
        self.rank = np.zeros(size, dtype=np.int8)

    def find(self, item: int) -> int:
        root = item
        while self.parent[root] != root:
            root = int(self.parent[root])
        while self.parent[item] != item:
            next_item = int(self.parent[item])
            self.parent[item] = root
            item = next_item
        return root

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


@dataclass
class ValidationThresholds:
    vertex_quantization_mm: float = 1e-4
    degenerate_area_mm2: float = 1e-7
    volume_relative_tolerance: float = 0.01
    build_volume_mm: tuple[float, float, float] = (420.0, 420.0, 500.0)
    edge_reserve_mm: float = 5.0


def read_binary_stl(path: Path) -> tuple[np.ndarray, np.ndarray]:
    file_size = path.stat().st_size
    with path.open("rb") as handle:
        header = handle.read(80)
        count_bytes = handle.read(4)
        if len(count_bytes) != 4:
            raise ValueError("truncated STL triangle count")
        triangle_count = struct.unpack("<I", count_bytes)[0]
    expected_size = 84 + 50 * triangle_count
    if file_size != expected_size:
        raise ValueError(
            f"not a valid binary STL size: expected {expected_size}, got {file_size}"
        )
    triangles = np.fromfile(path, dtype=STL_DTYPE, count=triangle_count, offset=84)
    if len(triangles) != triangle_count:
        raise ValueError("truncated STL triangle data")
    return triangles["vertices"].astype(np.float64), triangles["normal"].astype(np.float64)


def analyze_stl(
    path: Path,
    expected_volume_mm3: float | None,
    thresholds: ValidationThresholds,
) -> dict:
    vertices, stored_normals = read_binary_stl(path)
    triangle_count = len(vertices)
    flat_vertices = vertices.reshape(-1, 3)
    minimum = flat_vertices.min(axis=0)
    maximum = flat_vertices.max(axis=0)
    dimensions = maximum - minimum

    cross = np.cross(vertices[:, 1] - vertices[:, 0], vertices[:, 2] - vertices[:, 0])
    doubled_area = np.linalg.norm(cross, axis=1)
    degenerate = int(np.count_nonzero(doubled_area <= 2 * thresholds.degenerate_area_mm2))
    signed_volume = float(
        np.sum(np.einsum("ij,ij->i", vertices[:, 0], np.cross(vertices[:, 1], vertices[:, 2])))
        / 6.0
    )
    mesh_volume = abs(signed_volume)

    normal_lengths = np.linalg.norm(stored_normals, axis=1)
    valid_stored = normal_lengths > 1e-10
    normal_alignment = np.einsum("ij,ij->i", stored_normals, cross)
    flipped_normals = int(np.count_nonzero(valid_stored & (normal_alignment < -1e-8)))

    quantized = np.rint(flat_vertices / thresholds.vertex_quantization_mm).astype(np.int64)
    _, inverse = np.unique(quantized, axis=0, return_inverse=True)
    indexed = inverse.reshape(-1, 3)

    edge_map: dict[tuple[int, int], list[int]] = {}
    for triangle_index, tri in enumerate(indexed):
        for first, second in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge = (int(min(first, second)), int(max(first, second)))
            edge_map.setdefault(edge, []).append(triangle_index)

    edge_counts = np.fromiter((len(users) for users in edge_map.values()), dtype=np.int32)
    boundary_edges = int(np.count_nonzero(edge_counts == 1))
    nonmanifold_edges = int(np.count_nonzero(edge_counts > 2))

    union_find = UnionFind(triangle_count)
    for users in edge_map.values():
        if len(users) >= 2:
            anchor = users[0]
            for other in users[1:]:
                union_find.union(anchor, other)
    components = len({union_find.find(index) for index in range(triangle_count)})

    volume_delta = None
    if expected_volume_mm3 and expected_volume_mm3 > 0:
        volume_delta = abs(mesh_volume - expected_volume_mm3) / expected_volume_mm3

    maximum_print_dims = np.asarray(thresholds.build_volume_mm) - 2 * thresholds.edge_reserve_mm
    bed_fit = bool(np.all(dimensions <= maximum_print_dims + 1e-6))
    watertight = boundary_edges == 0 and nonmanifold_edges == 0
    positive_orientation = signed_volume > 0
    volume_match = volume_delta is None or volume_delta <= thresholds.volume_relative_tolerance
    passed = all(
        [
            triangle_count > 0,
            degenerate == 0,
            watertight,
            components == 1,
            positive_orientation,
            flipped_normals == 0,
            bed_fit,
            volume_match,
        ]
    )

    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "triangles": triangle_count,
        "boundsMm": [minimum.round(5).tolist(), maximum.round(5).tolist()],
        "dimensionsMm": dimensions.round(5).tolist(),
        "signedVolumeMm3": round(signed_volume, 3),
        "meshVolumeMm3": round(mesh_volume, 3),
        "expectedBrepVolumeMm3": expected_volume_mm3,
        "volumeRelativeDelta": None if volume_delta is None else round(volume_delta, 7),
        "degenerateTriangles": degenerate,
        "boundaryEdges": boundary_edges,
        "nonmanifoldEdges": nonmanifold_edges,
        "connectedComponents": components,
        "storedNormalMismatches": flipped_normals,
        "bedFitWithReserve": bed_fit,
        "watertight": watertight,
        "passed": passed,
    }


def markdown_report(result: dict) -> str:
    lines = [
        "# DRAFT STL geometry validation — Revision 3",
        "",
        f"Overall result: **{'PASS' if result['passed'] else 'FAIL'}**",
        "",
        "Independent checks use binary STL topology, quantized shared edges, signed mesh volume, B-Rep volume comparison, connected components, and the configured Kobra 3 Max build envelope.",
        "",
        "| Part | Triangles | Bodies | Boundary edges | Volume delta | Print dimensions (mm) | Result |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for item in result["files"]:
        delta = item["volumeRelativeDelta"]
        delta_text = "n/a" if delta is None else f"{100 * delta:.3f}%"
        dims = " × ".join(f"{value:.2f}" for value in item["dimensionsMm"])
        lines.append(
            f"| {item['file']} | {item['triangles']} | {item['connectedComponents']} | "
            f"{item['boundaryEdges']} | {delta_text} | {dims} | "
            f"{'PASS' if item['passed'] else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "## Scope and limits",
            "",
            "- PASS proves closed, consistently oriented, single-body meshes within the configured build volume and close agreement with their B-Rep volume.",
            "- It does not prove slicer toolpaths, watertight FDM process, strength, hydraulic performance, or physical fit.",
            "- Files remain DRAFT until the watermark regression and final release approval are complete.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stl_dir", type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    expected_by_file = {
        Path(part["stl"]).name: float(part["volumeMm3"])
        for part in metadata["parts"]
    }
    thresholds = ValidationThresholds(
        build_volume_mm=tuple(float(value) for value in metadata["parameters"]["printer"]["build"]),
        edge_reserve_mm=float(metadata["parameters"]["printer"]["edgeReserve"]),
    )

    files = []
    for stl_path in sorted(args.stl_dir.glob("*.stl")):
        files.append(analyze_stl(stl_path, expected_by_file.get(stl_path.name), thresholds))
    result = {
        "schemaVersion": 1,
        "filesChecked": len(files),
        "passed": bool(files) and all(item["passed"] for item in files),
        "thresholds": {
            "vertexQuantizationMm": thresholds.vertex_quantization_mm,
            "volumeRelativeTolerance": thresholds.volume_relative_tolerance,
            "buildVolumeMm": thresholds.build_volume_mm,
            "edgeReserveMm": thresholds.edge_reserve_mm,
        },
        "files": files,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown_report(result), encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "filesChecked": len(files)}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
