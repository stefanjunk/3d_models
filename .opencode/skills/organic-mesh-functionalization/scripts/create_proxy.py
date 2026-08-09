#!/usr/bin/env python3
"""Create a reduced proxy mesh for alignment and planning, with deviation sampling."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import dump_json, load_mesh, mesh_metrics


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh")
    p.add_argument("output")
    p.add_argument("--target-faces", type=int, required=True)
    p.add_argument("--samples", type=int, default=10000)
    p.add_argument("--json-out")
    args = p.parse_args()

    source = load_mesh(args.mesh, process=True)
    if args.target_faces <= 0 or args.target_faces >= len(source.faces):
        raise SystemExit("--target-faces must be positive and below source face count")
    try:
        proxy = source.simplify_quadric_decimation(face_count=args.target_faces)
    except Exception as exc:
        raise SystemExit("Quadric decimation requires the optional fast-simplification dependency") from exc
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    proxy.export(out)

    import trimesh
    points, _ = trimesh.sample.sample_surface(source, args.samples, seed=1234)
    method = "point-to-triangle"
    try:
        _, distances, _ = trimesh.proximity.closest_point(proxy, points)
    except Exception:
        from scipy.spatial import cKDTree
        distances, _ = cKDTree(np.asarray(proxy.vertices)).query(points, workers=-1)
        method = "nearest-vertex-fallback"
    report = {
        "source": mesh_metrics(source),
        "proxy": mesh_metrics(proxy),
        "output": str(out.resolve()),
        "deviation_method": method,
        "source_surface_to_proxy_mm": {
            "samples": int(len(distances)),
            "mean": float(np.mean(distances)),
            "p95": float(np.percentile(distances, 95)),
            "max": float(np.max(distances)),
        },
        "warning": "A proxy is for alignment/planning unless project acceptance explicitly permits replacing the source with it.",
    }
    print(dump_json(report, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
