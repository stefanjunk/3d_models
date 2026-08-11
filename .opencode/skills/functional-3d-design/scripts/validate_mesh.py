#!/usr/bin/env python3
"""Validate printable mesh topology, size, and component count with Trimesh."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_as_mesh(path: Path):
    try:
        import trimesh
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("trimesh is required: python -m pip install trimesh") from exc
    loaded = trimesh.load(path, force=None, process=True)
    if isinstance(loaded, trimesh.Scene):
        geometries = [g for g in loaded.geometry.values() if hasattr(g, "faces")]
        if not geometries:
            raise SystemExit("No mesh geometry found in scene")
        return trimesh.util.concatenate(geometries)
    if not hasattr(loaded, "faces"):
        raise SystemExit("Input did not load as a triangle mesh")
    return loaded


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh")
    p.add_argument("--require-watertight", action="store_true")
    p.add_argument("--max-bodies", type=int)
    p.add_argument("--bed", type=float, nargs=3, metavar=("X", "Y", "Z"))
    p.add_argument("--json-out")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    path = Path(args.mesh)
    if not path.exists():
        raise SystemExit(f"Mesh not found: {path}")
    mesh = load_as_mesh(path)

    try:
        components = mesh.split(only_watertight=False)
        body_count = len(components)
    except Exception:
        body_count = None

    try:
        nondegenerate_mask = mesh.nondegenerate_faces()
        degenerate = int((~nondegenerate_mask).sum())
    except Exception:
        degenerate = None

    extents = [float(v) for v in mesh.extents]
    bounds = [[float(v) for v in row] for row in mesh.bounds]
    is_watertight = bool(mesh.is_watertight)
    is_winding = bool(mesh.is_winding_consistent)
    is_volume = bool(mesh.is_volume)
    volume = float(mesh.volume)

    checks = {
        "has_vertices": len(mesh.vertices) > 0,
        "has_faces": len(mesh.faces) > 0,
        "positive_extents": all(v > 0 for v in extents),
        "watertight": (is_watertight if args.require_watertight else True),
        "body_count": (body_count <= args.max_bodies if args.max_bodies is not None and body_count is not None else True),
        "bed_fit_axis_aligned": (all(extents[i] <= args.bed[i] for i in range(3)) if args.bed else True),
    }

    report = {
        "file": str(path.resolve()),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "body_count": body_count,
        "watertight": is_watertight,
        "winding_consistent": is_winding,
        "is_volume": is_volume,
        "volume_mm3_signed": round(volume, 6),
        "surface_area_mm2": round(float(mesh.area), 6),
        "bounds_mm": bounds,
        "extents_mm": extents,
        "euler_number": int(mesh.euler_number),
        "degenerate_faces": degenerate,
        "checks": checks,
        "passed": all(checks.values()),
        "normalization": "Trimesh processing welds coincident STL vertices and performs standard topology cleanup before checks; it is not treated as a dimensional repair.",
        "limitations": [
            "No minimum-wall-thickness analysis is performed.",
            "Axis-aligned bed fit does not search alternate orientations.",
            "A watertight mesh can still have poor tolerances, trapped supports, or weak print orientation.",
        ],
    }

    text = json.dumps(report, indent=2)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    if not args.quiet:
        print(text)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
