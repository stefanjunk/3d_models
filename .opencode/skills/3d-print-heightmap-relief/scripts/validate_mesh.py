#!/usr/bin/env python3
"""Validate mesh topology and print-oriented geometric sanity checks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import trimesh

from heightmap_common import write_json


def load_mesh(path: str | Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="scene", process=False)
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ValueError(f"No triangle mesh found in {path}")
        mesh = trimesh.util.concatenate(meshes)
    elif isinstance(loaded, trimesh.Trimesh):
        mesh = loaded
    else:
        raise ValueError(f"Unsupported mesh object in {path}: {type(loaded).__name__}")
    mesh.remove_unreferenced_vertices()
    mesh.merge_vertices()
    return mesh


def edge_counts(mesh: trimesh.Trimesh) -> tuple[int, int]:
    if len(mesh.edges) == 0:
        return 0, 0
    edges = np.sort(mesh.edges, axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    return int(np.sum(counts == 1)), int(np.sum(counts > 2))


def report_for(mesh: trimesh.Trimesh, source: str | None = None) -> dict[str, Any]:
    boundary, nonmanifold = edge_counts(mesh)
    areas = np.asarray(mesh.area_faces) if len(mesh.faces) else np.array([], dtype=float)
    broken = trimesh.repair.broken_faces(mesh)
    components = mesh.split(only_watertight=False)
    bounds = mesh.bounds.tolist() if len(mesh.vertices) else None
    extents = mesh.extents.tolist() if len(mesh.vertices) else [0.0, 0.0, 0.0]
    report = {
        "source": source,
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "body_count": int(mesh.body_count),
        "connected_components": int(len(components)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "euler_number": int(mesh.euler_number),
        "boundary_edges": boundary,
        "nonmanifold_edges": nonmanifold,
        "broken_faces": int(len(broken)),
        "bounds_mm": bounds,
        "extents_mm": extents,
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "minimum_triangle_area_mm2": float(np.min(areas)) if areas.size else 0.0,
        "p01_triangle_area_mm2": float(np.percentile(areas, 1)) if areas.size else 0.0,
        "tiny_faces_below_1e-8_mm2": int(np.sum(areas < 1e-8)) if areas.size else 0,
    }
    return report


def evaluate(report: dict[str, Any], args: argparse.Namespace) -> list[str]:
    failures: list[str] = []
    if args.require_watertight and not report["watertight"]:
        failures.append("mesh is not watertight")
    if args.require_volume and not report["is_volume"]:
        failures.append("mesh is not a consistently oriented volume")
    if args.require_single_body and report["body_count"] != 1:
        failures.append(f"expected one body, found {report['body_count']}")
    if args.max_faces is not None and report["triangles"] > args.max_faces:
        failures.append(f"triangle count exceeds {args.max_faces:,}")
    if args.min_extent_mm is not None and min(report["extents_mm"]) < args.min_extent_mm:
        failures.append(f"at least one extent is below {args.min_extent_mm} mm")
    if report["nonmanifold_edges"]:
        failures.append(f"mesh has {report['nonmanifold_edges']} non-manifold edges")
    return failures


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh", type=Path)
    p.add_argument("--report", type=Path)
    p.add_argument("--require-watertight", action="store_true")
    p.add_argument("--require-volume", action="store_true")
    p.add_argument("--require-single-body", action="store_true")
    p.add_argument("--max-faces", type=int)
    p.add_argument("--min-extent-mm", type=float)
    return p


def main() -> int:
    args = build_parser().parse_args()
    mesh = load_mesh(args.mesh)
    report = report_for(mesh, str(args.mesh))
    failures = evaluate(report, args)
    report["failures"] = failures
    if args.report:
        write_json(report, args.report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
