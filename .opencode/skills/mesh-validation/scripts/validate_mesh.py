#!/usr/bin/env python3
"""Inspect a triangle mesh without modifying it and emit JSON evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np


def load_mesh(path: Path, process: bool):
    try:
        import trimesh
    except ImportError as exc:
        raise SystemExit("trimesh is required: python -m pip install trimesh") from exc
    loaded = trimesh.load(path, force=None, process=process)
    if isinstance(loaded, trimesh.Scene):
        if not loaded.geometry:
            raise ValueError(f"No triangle mesh in scene: {path}")
        if hasattr(loaded, "to_geometry"):
            loaded = loaded.to_geometry()
        else:  # pragma: no cover - compatibility with older Trimesh
            loaded = loaded.dump(concatenate=True)
    if not hasattr(loaded, "faces"):
        raise ValueError(f"Input is not a triangle mesh: {path}")
    return loaded


def edge_counts(mesh) -> tuple[int, int]:
    if not len(mesh.faces):
        return 0, 0
    counts = np.bincount(mesh.edges_unique_inverse)
    return int(np.count_nonzero(counts == 1)), int(np.count_nonzero(counts > 2))


def report_for(source_mesh, source: str | None = None) -> dict[str, object]:
    mesh = source_mesh.copy()
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    boundary_edges, nonmanifold_edges = edge_counts(mesh)
    components = mesh.split(only_watertight=False)
    nondegenerate = mesh.nondegenerate_faces() if len(mesh.faces) else np.array([], dtype=bool)
    return {
        "source": source,
        "analysis_normalization": "in-memory copy with merged vertices and unreferenced vertices removed",
        "raw_vertices": int(len(source_mesh.vertices)),
        "raw_faces": int(len(source_mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "triangles": int(len(mesh.faces)),
        "body_count": int(len(components)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "volume_mm3_signed": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "bounds_mm": np.asarray(mesh.bounds, dtype=float).tolist(),
        "extents_mm": np.asarray(mesh.extents, dtype=float).tolist(),
        "euler_number": int(mesh.euler_number),
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "degenerate_faces": int((~nondegenerate).sum()) if len(nondegenerate) else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--report", "--json-out", dest="report", type=Path)
    parser.add_argument("--process", action="store_true")
    parser.add_argument("--no-process", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--require-watertight", action="store_true")
    parser.add_argument("--require-volume", action="store_true")
    parser.add_argument("--require-single-body", action="store_true")
    parser.add_argument("--expected-bodies", type=int)
    parser.add_argument("--max-faces", type=int)
    parser.add_argument("--min-extent-mm", type=float)
    parser.add_argument("--bed", type=float, nargs=3, metavar=("X", "Y", "Z"))
    args = parser.parse_args()

    source_mesh = load_mesh(args.mesh, process=args.process)
    report = {
        **report_for(source_mesh, str(args.mesh)),
        "file": str(args.mesh.resolve()),
        "sha256": hashlib.sha256(args.mesh.read_bytes()).hexdigest(),
        "load_processing": args.process,
    }
    checks = {
        "nonempty": report["vertices"] > 0 and report["faces"] > 0,
        "positive_extents": all(value > 0 for value in report["extents_mm"]),
        "watertight": report["watertight"] if args.require_watertight else True,
        "volume": report["is_volume"] if args.require_volume else True,
        "single_body": report["body_count"] == 1 if args.require_single_body else True,
        "expected_bodies": report["body_count"] == args.expected_bodies if args.expected_bodies is not None else True,
        "max_faces": report["faces"] <= args.max_faces if args.max_faces is not None else True,
        "min_extent": min(report["extents_mm"]) >= args.min_extent_mm if args.min_extent_mm is not None else True,
        "bed_fit_axis_aligned": all(report["extents_mm"][i] <= args.bed[i] for i in range(3)) if args.bed else True,
        "manifold_edges": report["nonmanifold_edges"] == 0,
    }
    report["checks"] = checks
    report["passed"] = all(checks.values())
    report["limitations"] = [
        "Self-intersection is not exhaustively tested.",
        "Minimum wall thickness is not inferred.",
        "Topology processing is disabled unless --process is explicit.",
    ]
    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
