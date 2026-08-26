#!/usr/bin/env python3
"""Inspect a triangle mesh and emit a reproducible JSON report."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force=None, process=True)
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ValueError("Scene contains no triangle meshes")
        return trimesh.util.concatenate(meshes)
    if not isinstance(loaded, trimesh.Trimesh):
        raise TypeError(f"Unsupported geometry type: {type(loaded)!r}")
    return loaded


def edge_counts(mesh: trimesh.Trimesh) -> tuple[int, int, int]:
    if len(mesh.faces) == 0:
        return 0, 0, 0
    inverse = mesh.edges_unique_inverse
    counts = np.bincount(inverse, minlength=len(mesh.edges_unique))
    boundary = int(np.count_nonzero(counts == 1))
    manifold = int(np.count_nonzero(counts == 2))
    over = int(np.count_nonzero(counts > 2))
    return boundary, manifold, over


def duplicate_face_count(mesh: trimesh.Trimesh) -> int:
    if len(mesh.faces) == 0:
        return 0
    canonical = np.sort(mesh.faces, axis=1)
    unique = np.unique(canonical, axis=0)
    return int(len(mesh.faces) - len(unique))


def safe_float(value: Any) -> float | None:
    try:
        result = float(value)
    except Exception:
        return None
    return result if math.isfinite(result) else None


def estimate_array_bytes(mesh: trimesh.Trimesh) -> int:
    arrays = [mesh.vertices, mesh.faces]
    return int(sum(getattr(a, "nbytes", 0) for a in arrays))


def inspect(mesh: trimesh.Trimesh, path: Path) -> dict[str, Any]:
    boundary, manifold_edges, over = edge_counts(mesh)
    areas = np.asarray(mesh.area_faces) if len(mesh.faces) else np.empty(0)
    area_scale = max(float(mesh.area), 1.0)
    degenerate_threshold = np.finfo(np.float64).eps * area_scale * 100
    degenerate = int(np.count_nonzero(areas <= degenerate_threshold))

    try:
        components = mesh.split(only_watertight=False, repair=False)
        component_faces = sorted((int(len(c.faces)) for c in components), reverse=True)
    except Exception:
        components = []
        component_faces = []

    bounds = np.asarray(mesh.bounds, dtype=float) if len(mesh.vertices) else np.zeros((2, 3))
    extents = np.asarray(mesh.extents, dtype=float) if len(mesh.vertices) else np.zeros(3)

    report: dict[str, Any] = {
        "file": str(path),
        "sha256": sha256_file(path),
        "file_bytes": path.stat().st_size,
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "connected_components": int(len(components)) if components else None,
        "component_face_counts": component_faces,
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "euler_number": int(mesh.euler_number),
        "boundary_edges": boundary,
        "manifold_edges": manifold_edges,
        "overconnected_edges": over,
        "duplicate_faces": duplicate_face_count(mesh),
        "degenerate_faces_estimate": degenerate,
        "bounds": bounds.tolist(),
        "extents": extents.tolist(),
        "area": safe_float(mesh.area),
        "volume": safe_float(mesh.volume),
        "center_mass": np.asarray(mesh.center_mass, dtype=float).tolist() if len(mesh.vertices) else None,
        "raw_vertex_face_array_bytes": estimate_array_bytes(mesh),
        "peak_memory_note": "Boolean/BVH/adjacency/undo peak can be many times raw arrays",
    }
    return report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh", type=Path)
    p.add_argument("--json", dest="json_path", type=Path)
    p.add_argument("--require-watertight", action="store_true")
    p.add_argument("--require-positive-volume", action="store_true")
    p.add_argument("--max-components", type=int)
    p.add_argument("--max-boundary-edges", type=int)
    return p


def main() -> int:
    args = build_parser().parse_args()
    mesh = load_mesh(args.mesh)
    report = inspect(mesh, args.mesh)

    failures: list[str] = []
    if args.require_watertight and not report["is_watertight"]:
        failures.append("mesh is not watertight")
    if args.require_positive_volume and not report["is_volume"]:
        failures.append("mesh is not a consistently oriented positive volume")
    if args.max_components is not None:
        count = report["connected_components"]
        if count is None or count > args.max_components:
            failures.append(f"connected components {count} > {args.max_components}")
    if args.max_boundary_edges is not None and report["boundary_edges"] > args.max_boundary_edges:
        failures.append(f"boundary edges {report['boundary_edges']} > {args.max_boundary_edges}")

    report["passed"] = not failures
    report["failures"] = failures
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(text + "\n", encoding="utf-8")
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
