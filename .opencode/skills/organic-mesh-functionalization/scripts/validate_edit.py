#!/usr/bin/env python3
"""Compare source and result outside the allowed ROI and validate topology against an operation plan."""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np

from common import dump_json, load_mesh, load_structured, mesh_metrics, roi_contains


def sample_protected(mesh, roi: dict[str, Any], margin: float, count: int, seed: int) -> np.ndarray:
    import trimesh

    rng = np.random.default_rng(seed)
    chunks: list[np.ndarray] = []
    needed = count
    for _ in range(12):
        draw = max(needed * 3, 2000)
        points, _ = trimesh.sample.sample_surface(mesh, draw, seed=rng)
        mask = ~roi_contains(points, roi, margin=margin)
        if np.any(mask):
            chunks.append(points[mask])
            needed = count - sum(len(x) for x in chunks)
            if needed <= 0:
                break
    if not chunks:
        return np.empty((0, 3), dtype=float)
    return np.concatenate(chunks, axis=0)[:count]


def distances_to_mesh(mesh, points: np.ndarray) -> tuple[np.ndarray, str]:
    if len(points) == 0:
        return np.empty(0), "none"
    try:
        import trimesh

        closest, distances, _ = trimesh.proximity.closest_point(mesh, points)
        if np.all(np.isfinite(distances)):
            return np.asarray(distances, dtype=float), "point-to-triangle"
    except Exception:
        pass
    try:
        from scipy.spatial import cKDTree
        import trimesh
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("scipy and trimesh are required for proximity fallback") from exc

    # R-tree is optional in Trimesh. When unavailable, query nearby triangle
    # centroids and calculate exact closest points on that candidate set.
    # This is an approximation of the global search, but much better than a
    # nearest-vertex metric and exact for ordinary local triangulations.
    # Avoid constructing a large triangle array for multi-million-face meshes.
    # In that case the vertex fallback is cheaper but must be interpreted as
    # an approximate screening metric.
    triangles = np.asarray(mesh.triangles) if len(mesh.faces) <= 750_000 else np.empty((0, 3, 3))
    if len(triangles):
        centroids = triangles.mean(axis=1)
        tree = cKDTree(centroids)
        k = min(32, len(triangles))
        _, indices = tree.query(points, k=k, workers=-1)
        if k == 1:
            indices = indices[:, None]
        candidates = triangles[indices.reshape(-1)]
        repeated = np.repeat(points, k, axis=0)
        closest = trimesh.triangles.closest_point(candidates, repeated)
        d = np.linalg.norm(closest - repeated, axis=1).reshape(len(points), k)
        return d.min(axis=1), "candidate-triangle-fallback"

    tree = cKDTree(np.asarray(mesh.vertices))
    distances, _ = tree.query(points, workers=-1)
    return np.asarray(distances, dtype=float), "nearest-vertex-fallback"


def stats(values: np.ndarray) -> dict[str, float | int | None]:
    if len(values) == 0:
        return {"count": 0, "mean_mm": None, "median_mm": None, "p95_mm": None, "p99_mm": None, "max_mm": None}
    return {
        "count": int(len(values)),
        "mean_mm": float(np.mean(values)),
        "median_mm": float(np.median(values)),
        "p95_mm": float(np.percentile(values, 95)),
        "p99_mm": float(np.percentile(values, 99)),
        "max_mm": float(np.max(values)),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source")
    p.add_argument("result")
    p.add_argument("--plan", required=True)
    p.add_argument("--samples", type=int)
    p.add_argument("--seed", type=int, default=12345)
    p.add_argument("--json-out")
    args = p.parse_args()

    plan = load_structured(args.plan)
    roi = plan["functional_roi"]
    margin = float(plan.get("transition_band_mm", 0.0))
    protected = plan.get("protected_region", {})
    sample_count = int(args.samples or protected.get("sample_count", 20000))
    max_limit = float(protected.get("max_surface_deviation_mm", 0.20))
    p95_limit = float(protected.get("p95_surface_deviation_mm", 0.10))

    source = load_mesh(args.source, process=True)
    result = load_mesh(args.result, process=True)
    src_points = sample_protected(source, roi, margin, sample_count, args.seed)
    res_points = sample_protected(result, roi, margin, sample_count, args.seed + 1)
    src_to_res, method1 = distances_to_mesh(result, src_points)
    res_to_src, method2 = distances_to_mesh(source, res_points)
    combined = np.concatenate([src_to_res, res_to_src]) if len(src_to_res) + len(res_to_src) else np.empty(0)
    dev = stats(combined)
    dev["fraction_above_max"] = float(np.mean(combined > max_limit)) if len(combined) else None

    acceptance = plan.get("acceptance", {})
    result_metrics = mesh_metrics(result)
    topology_checks = {
        "watertight": result_metrics["watertight"] if acceptance.get("require_watertight", False) else True,
        "body_count": result_metrics["body_count"] == int(acceptance.get("expected_body_count", result_metrics["body_count"])),
        "positive_volume": result_metrics["volume_mm3_signed"] > 0 if acceptance.get("require_watertight", False) else True,
    }
    protected_checks = {
        "samples_available": len(combined) > 0 or roi.get("type") == "all",
        "p95_within_limit": (dev["p95_mm"] is not None and dev["p95_mm"] <= p95_limit) if roi.get("type") != "all" else True,
        "max_within_limit": (dev["max_mm"] is not None and dev["max_mm"] <= max_limit) if roi.get("type") != "all" else True,
    }
    report = {
        "source": {"file": str(Path(args.source).resolve()), **mesh_metrics(source)},
        "result": {"file": str(Path(args.result).resolve()), **result_metrics},
        "functional_roi": roi,
        "transition_band_mm": margin,
        "protected_surface": {
            "sample_target_each_direction": sample_count,
            "source_to_result_method": method1,
            "result_to_source_method": method2,
            "limits_mm": {"p95": p95_limit, "max": max_limit},
            "symmetric_deviation": dev,
            "note": "Nearest-vertex fallback is conservative/approximate and can overestimate deviation on coarse or uneven meshes.",
        },
        "checks": {"topology": topology_checks, "protected_surface": protected_checks},
    }
    report["passed"] = all(topology_checks.values()) and all(protected_checks.values())
    report["required_manual_checks"] = [
        "Inspect overlays and sections through every opening and transition.",
        "Verify residual wall and functional clearances.",
        "Re-import final export and review slicer preview.",
    ]
    print(dump_json(report, args.json_out))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
