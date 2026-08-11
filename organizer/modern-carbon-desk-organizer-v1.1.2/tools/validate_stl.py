#!/usr/bin/env python3
"""Independent vectorized binary-STL topology, bounds, and winding validator."""

from __future__ import annotations

import gc
import json
import struct
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "output" / "validation-report.json"
BUILD_VOLUME = np.array([420.0, 420.0, 500.0])
STL_RECORD = np.dtype(
    [("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")],
    align=False,
)


def read_binary_stl(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"{path.name}: too small for binary STL")
    count = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + count * 50
    if len(data) != expected:
        raise ValueError(f"{path.name}: size {len(data)} != binary STL expectation {expected}")
    return np.frombuffer(data, dtype=STL_RECORD, count=count, offset=84)["vertices"]


def analyze(path: Path, expected_bodies: int, require_build_fit: bool) -> dict:
    triangles = read_binary_stl(path)
    if len(triangles) == 0:
        raise ValueError(f"{path.name}: no triangles")

    flat = triangles.reshape(-1, 3)
    minv = flat.min(axis=0).astype(float)
    maxv = flat.max(axis=0).astype(float)
    size = maxv - minv

    edge_a = triangles[:, 1] - triangles[:, 0]
    edge_b = triangles[:, 2] - triangles[:, 0]
    normals2 = np.cross(edge_a, edge_b)
    double_area = np.linalg.norm(normals2, axis=1)
    degenerate = int(np.count_nonzero(double_area < 1e-9))
    area = float(np.sum(double_area, dtype=np.float64) * 0.5)
    signed_volume = float(
        np.sum(
            np.einsum("ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])),
            dtype=np.float64,
        )
        / 6.0
    )

    # Weld the float32 STL vertices at 1e-5 mm and perform all edge tests on
    # integer vertex IDs. This avoids Python-object memory growth on dense reliefs.
    quantized = np.rint(flat.astype(np.float64) * 100000.0).astype(np.int64)
    unique_vertices, inverse = np.unique(quantized, axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    directed = np.concatenate(
        (faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]), axis=0
    )
    undirected = np.sort(directed, axis=1)
    order = np.lexsort((undirected[:, 1], undirected[:, 0]))
    sorted_edges = undirected[order]
    changed = np.any(sorted_edges[1:] != sorted_edges[:-1], axis=1)
    starts = np.concatenate(([0], np.flatnonzero(changed) + 1))
    counts = np.diff(np.concatenate((starts, [len(sorted_edges)])))
    boundary_edges = int(np.count_nonzero(counts == 1))
    nonmanifold_edges = int(np.count_nonzero(counts > 2))

    sorted_directed = directed[order]
    paired_starts = starts[counts == 2]
    first = sorted_directed[paired_starts]
    second = sorted_directed[paired_starts + 1]
    winding_errors = int(
        np.count_nonzero(~((first[:, 0] == second[:, 1]) & (first[:, 1] == second[:, 0])))
    )

    graph = coo_matrix(
        (np.ones(len(directed), dtype=np.uint8), (directed[:, 0], directed[:, 1])),
        shape=(len(unique_vertices), len(unique_vertices)),
    ).tocsr()
    body_count = int(connected_components(graph, directed=False, return_labels=False))

    report = {
        "file": path.name,
        "relative_path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "triangles": int(len(triangles)),
        "unique_vertices_rounded_1e-5_mm": int(len(unique_vertices)),
        "bounds_mm": [minv.tolist(), maxv.tolist()],
        "size_mm": size.tolist(),
        "surface_area_mm2": area,
        "signed_volume_mm3": signed_volume,
        "absolute_volume_mm3": abs(signed_volume),
        "connected_components": body_count,
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "winding_errors": winding_errors,
        "degenerate_triangles": degenerate,
        "watertight": boundary_edges == 0 and nonmanifold_edges == 0,
        "consistent_winding": winding_errors == 0,
        "expected_components": expected_bodies,
        "component_count_ok": body_count == expected_bodies,
        "fits_kobra_3_max_build_volume": bool(np.all(size <= BUILD_VOLUME + 1e-4)),
        "build_fit_required": require_build_fit,
    }
    del triangles, flat, quantized, unique_vertices, inverse, faces, directed, undirected
    del order, sorted_edges, graph
    gc.collect()
    return report


def main() -> None:
    groups = {
        "manufacturing": {
            "directory": ROOT / "output" / "stl",
            "expected": {
                "01_housing_print_on_back.stl": 1,
                "02_drawer_print_twice.stl": 1,
                "03_top_sorter_print_bottom_down.stl": 1,
                "04_fit_coupon_optional.stl": 6,
                "05_carbon_texture_coupon_optional.stl": 1,
            },
            "build_fit": True,
        },
        "engraving_cutters": {
            "directory": ROOT / "output" / "cutters",
            "expected": {},
            "build_fit": False,
        },
        "untextured_bases": {
            "directory": ROOT / "output" / "base",
            "expected": {},
            "build_fit": False,
        },
    }
    reports: dict[str, list[dict]] = {}
    failures: list[str] = []

    for group_name, config in groups.items():
        group_reports = []
        paths = sorted(config["directory"].glob("*.stl"))
        for path in paths:
            expected = config["expected"].get(path.name, 1)
            report = analyze(path, expected, config["build_fit"])
            group_reports.append(report)
            checks = ["watertight", "consistent_winding", "component_count_ok"]
            if config["build_fit"]:
                checks.append("fits_kobra_3_max_build_volume")
            for check in checks:
                if not report[check]:
                    failures.append(f"{report['relative_path']}: {check} failed")
            if report["degenerate_triangles"]:
                failures.append(
                    f"{report['relative_path']}: degenerate triangles = {report['degenerate_triangles']}"
                )
        reports[group_name] = group_reports

    summary = {
        "status": "pass" if not failures else "fail",
        "scope": (
            "V1 independent exported-mesh topology, winding, volume, body count, and manufacturing "
            "envelope; slicer and physical coupons remain required"
        ),
        "groups": reports,
        "failures": failures,
    }
    REPORT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "files": sum(len(items) for items in reports.values()),
                "failures": failures,
            },
            indent=2,
        )
    )
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
