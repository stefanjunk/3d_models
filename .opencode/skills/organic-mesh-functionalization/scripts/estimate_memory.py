#!/usr/bin/env python3
"""Estimate lower-bound mesh and dense voxel memory before expensive operations."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from common import dump_json, load_mesh


def gib(n: float) -> float:
    return n / (1024.0**3)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mesh")
    p.add_argument("--extents", type=float, nargs=3, metavar=("X", "Y", "Z"))
    p.add_argument("--voxel-mm", type=float)
    p.add_argument("--padding-voxels", type=int, default=4)
    p.add_argument("--copies", type=float, default=4.0, help="Planning multiplier for mesh arrays/caches")
    p.add_argument("--json-out")
    args = p.parse_args()

    if not args.mesh and not args.extents:
        p.error("Provide --mesh or --extents")

    report: dict[str, object] = {}
    extents = args.extents
    if args.mesh:
        mesh = load_mesh(Path(args.mesh), process=False)
        extents = [float(v) for v in mesh.extents]
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
            p.error("--voxel-mm must be positive")
        dims = [int(math.ceil(v / args.voxel_mm)) + 2 * args.padding_voxels for v in extents]
        n = dims[0] * dims[1] * dims[2]
        report["voxel"] = {
            "spacing_mm": args.voxel_mm,
            "dimensions": dims,
            "voxels": n,
            "boolean_mask_gib": round(gib(n), 4),
            "float32_field_gib": round(gib(4 * n), 4),
            "float64_field_gib": round(gib(8 * n), 4),
            "three_float64_coordinate_grids_gib": round(gib(24 * n), 4),
            "warning": "Peak memory can be several times these figures due to temporaries, marching cubes output, and mesh caches.",
        }
    print(dump_json(report, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
