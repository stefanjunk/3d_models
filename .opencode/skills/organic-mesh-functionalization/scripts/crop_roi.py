#!/usr/bin/env python3
"""Extract an open analysis patch whose face centroids or vertices intersect an ROI."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import dump_json, load_mesh, load_structured, mesh_metrics, roi_contains


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh")
    p.add_argument("--plan", required=True)
    p.add_argument("--margin", type=float, default=0.0)
    p.add_argument("--mode", choices=["centroid", "any-vertex", "all-vertices"], default="any-vertex")
    p.add_argument("--output", required=True)
    p.add_argument("--json-out")
    args = p.parse_args()

    mesh = load_mesh(args.mesh, process=False)
    plan = load_structured(args.plan)
    roi = plan["functional_roi"]
    faces = np.asarray(mesh.faces)
    if args.mode == "centroid":
        mask = roi_contains(np.asarray(mesh.triangles_center), roi, args.margin)
    else:
        vertex_mask = roi_contains(np.asarray(mesh.vertices), roi, args.margin)
        face_values = vertex_mask[faces]
        mask = face_values.any(axis=1) if args.mode == "any-vertex" else face_values.all(axis=1)
    if not np.any(mask):
        raise SystemExit("ROI selected no faces")
    patch = mesh.submesh([np.flatnonzero(mask)], append=True, repair=False)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    patch.export(out)
    report = {
        "output": str(out.resolve()),
        "mode": args.mode,
        "margin_mm": args.margin,
        "selected_faces": int(mask.sum()),
        "source_faces": int(len(mesh.faces)),
        "patch": mesh_metrics(patch),
        "warning": "The crop is normally an open analysis/processing patch, not a printable solid.",
    }
    print(dump_json(report, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
