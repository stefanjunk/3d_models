#!/usr/bin/env python3
"""Recommend a primary and supporting tool route for a mesh/CAD intervention."""
from __future__ import annotations

import argparse

from common import dump_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", choices=["dense-mesh", "clean-mesh", "step"], required=True)
    p.add_argument("--operation", choices=["simple-csg", "precise-insert", "conformal", "repair", "uniform-offset", "assembly", "fem"], required=True)
    p.add_argument("--headless", action="store_true")
    p.add_argument("--preserve-detail", action="store_true")
    p.add_argument("--json-out")
    args = p.parse_args()

    reasons: list[str] = []
    if args.source == "step":
        primary = "cadquery" if args.headless else "freecad"
        support = ["freecad" if primary == "cadquery" else "cadquery"]
        reasons.append("The source is B-Rep/STEP, so preserve exact CAD geometry.")
    elif args.operation == "repair":
        primary = "blender"
        support = ["trimesh", "sdf-voxel"]
        reasons.append("Repair and segmentation are mesh-native tasks.")
    elif args.operation == "uniform-offset":
        primary = "sdf-voxel"
        support = ["blender-solidify", "trimesh"]
        reasons.append("Uniform organic offsets are more robust as distance-field operations.")
    elif args.operation == "precise-insert":
        primary = "cadquery"
        support = ["blender", "manifold3d", "trimesh"]
        reasons.append("Create the functional component as parametric B-Rep, then tessellate for mesh integration.")
    elif args.operation == "conformal":
        primary = "blender"
        support = ["cadquery", "sdf-voxel", "trimesh"]
        reasons.append("Conformal fitting needs local mesh surface tools such as Shrinkwrap or a distance field.")
    elif args.operation == "simple-csg" and args.source == "clean-mesh":
        primary = "openscad" if not args.headless else "manifold3d"
        support = ["trimesh", "blender"]
        reasons.append("The input is clean and the operation is simple CSG.")
    elif args.operation == "assembly":
        primary = "freecad" if not args.headless else "cadquery"
        support = ["blender", "trimesh"]
        reasons.append("Assembly review benefits from STEP context and measured placement.")
    elif args.operation == "fem":
        primary = "freecad"
        support = ["cadquery"]
        reasons.append("FEM should use a simplified meaningful solid, not the full decorative mesh.")
    else:
        primary = "blender"
        support = ["trimesh", "manifold3d", "cadquery"]
        reasons.append("Dense organic source defaults to a mesh-native host with parametric support parts.")

    if args.preserve_detail:
        reasons.append("Preserve the full-resolution exterior; use proxies and local ROI processing rather than global remesh.")
    print(dump_json({"primary": primary, "support": support, "reasons": reasons}, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
