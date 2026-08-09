#!/usr/bin/env python3
"""Generate simple closed cutter/keep-out primitives as STL/PLY/GLB."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import dump_json


def align_z_to_axis(mesh, axis: str) -> None:
    import trimesh

    if axis == "z":
        return
    target = {"x": [1, 0, 0], "y": [0, 1, 0]}[axis]
    matrix = trimesh.geometry.align_vectors([0, 0, 1], target)
    mesh.apply_transform(matrix)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="kind", required=True)
    box = sub.add_parser("box")
    box.add_argument("--size", type=float, nargs=3, required=True)
    sph = sub.add_parser("sphere")
    sph.add_argument("--radius", type=float, required=True)
    cyl = sub.add_parser("cylinder")
    cyl.add_argument("--radius", type=float, required=True)
    cyl.add_argument("--height", type=float, required=True)
    cyl.add_argument("--axis", choices=["x", "y", "z"], default="z")
    cyl.add_argument("--sections", type=int, default=96)
    cap = sub.add_parser("capsule")
    cap.add_argument("--radius", type=float, required=True)
    cap.add_argument("--height", type=float, required=True, help="Cylinder segment height between hemispheres")
    cap.add_argument("--axis", choices=["x", "y", "z"], default="z")
    for sp in [box, sph, cyl, cap]:
        sp.add_argument("--center", type=float, nargs=3, default=[0, 0, 0])
        sp.add_argument("--output", required=True)
        sp.add_argument("--json-out")
    args = p.parse_args()

    import trimesh

    if args.kind == "box":
        mesh = trimesh.creation.box(extents=args.size)
    elif args.kind == "sphere":
        mesh = trimesh.creation.icosphere(subdivisions=4, radius=args.radius)
    elif args.kind == "cylinder":
        mesh = trimesh.creation.cylinder(radius=args.radius, height=args.height, sections=args.sections)
        align_z_to_axis(mesh, args.axis)
    else:
        mesh = trimesh.creation.capsule(height=args.height, radius=args.radius)
        align_z_to_axis(mesh, args.axis)
    mesh.apply_translation(np.asarray(args.center, dtype=float))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(out)
    report = {"output": str(out.resolve()), "kind": args.kind, "vertices": len(mesh.vertices), "faces": len(mesh.faces), "watertight": bool(mesh.is_watertight), "volume_mm3": float(mesh.volume)}
    print(dump_json(report, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
