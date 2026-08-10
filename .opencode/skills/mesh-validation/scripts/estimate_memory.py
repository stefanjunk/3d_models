#!/usr/bin/env python3
"""Estimate lower-bound mesh and dense-voxel memory before allocation."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from validate_mesh import load_mesh


def gib(value: float) -> float:
    return value / (1024.0**3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=Path)
    parser.add_argument("--extents", type=float, nargs=3, metavar=("X", "Y", "Z"))
    parser.add_argument("--voxel-mm", type=float)
    parser.add_argument("--padding-voxels", type=int, default=4)
    parser.add_argument("--copies", type=float, default=4.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.mesh and not args.extents:
        parser.error("Provide --mesh or --extents")

    report: dict[str, object] = {}
    extents = args.extents
    if args.mesh:
        mesh = load_mesh(args.mesh, process=False)
        extents = [float(value) for value in mesh.extents]
        raw = len(mesh.vertices) * 3 * 8 + len(mesh.faces) * 3 * 8
        report["mesh"] = {
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "raw_vertices_faces_gib": round(gib(raw), 4),
            "planning_with_caches_gib": round(gib(raw * args.copies), 4),
            "planning_multiplier": args.copies,
        }
    report["extents_mm"] = extents
    if args.voxel_mm:
        if args.voxel_mm <= 0:
            parser.error("--voxel-mm must be positive")
        dimensions = [int(math.ceil(value / args.voxel_mm)) + 2 * args.padding_voxels for value in extents]
        voxels = math.prod(dimensions)
        report["voxel"] = {
            "spacing_mm": args.voxel_mm,
            "dimensions": dimensions,
            "voxels": voxels,
            "boolean_mask_gib": round(gib(voxels), 4),
            "float32_field_gib": round(gib(4 * voxels), 4),
            "float64_field_gib": round(gib(8 * voxels), 4),
            "warning": "Peak memory can be several times these lower bounds due to temporaries and mesh output.",
        }
    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
