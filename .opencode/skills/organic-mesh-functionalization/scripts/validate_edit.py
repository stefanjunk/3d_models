#!/usr/bin/env python3
"""Compare source and edited meshes, emphasizing preservation outside an ROI."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from scipy.spatial import cKDTree


def load_mesh(path: Path) -> trimesh.Trimesh:
    obj = trimesh.load(path, force=None, process=True)
    if isinstance(obj, trimesh.Scene):
        parts = [g for g in obj.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not parts:
            raise ValueError(f"No meshes in {path}")
        obj = trimesh.util.concatenate(parts)
    if not isinstance(obj, trimesh.Trimesh):
        raise TypeError(type(obj))
    return obj


def points_in_shape(points: np.ndarray, shape: dict[str, Any]) -> np.ndarray:
    kind = shape["type"].lower()
    c = np.asarray(shape.get("center", [0, 0, 0]), dtype=float)
    p = points - c
    pad = float(shape.get("padding", 0.0))
    if kind == "box":
        half = np.asarray(shape["size"], dtype=float) / 2 + pad
        return np.all(np.abs(p) <= half, axis=1)
    if kind == "sphere":
        return np.linalg.norm(p, axis=1) <= float(shape["radius"]) + pad
    if kind == "cylinder":
        axis = str(shape.get("axis", "z")).lower()
        idx = {"x": 0, "y": 1, "z": 2}[axis]
        radial_idx = [i for i in range(3) if i != idx]
        radial = np.linalg.norm(p[:, radial_idx], axis=1)
        axial = np.abs(p[:, idx])
        return (radial <= float(shape["radius"]) + pad) & (axial <= float(shape["height"]) / 2 + pad)
    raise ValueError(f"Unsupported ROI shape: {kind}")


def roi_mask(points: np.ndarray, roi: dict[str, Any] | None) -> np.ndarray:
    if not roi:
        return np.zeros(len(points), dtype=bool)
    result = np.zeros(len(points), dtype=bool)
    for shape in roi.get("shapes", []):
        result |= points_in_shape(points, shape)
    return result


def sample_surface(mesh: trimesh.Trimesh, count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if len(mesh.faces) == 0:
        return np.empty((0, 3))
    areas = np.asarray(mesh.area_faces, dtype=float)
    total = areas.sum()
    if total <= 0:
        idx = rng.integers(0, len(mesh.vertices), size=min(count, len(mesh.vertices)))
        return mesh.vertices[idx]
    probs = areas / total
    face_idx = rng.choice(len(mesh.faces), size=count, p=probs)
    tri = mesh.triangles[face_idx]
    r1 = np.sqrt(rng.random(count))
    r2 = rng.random(count)
    a = 1 - r1
    b = r1 * (1 - r2)
    c = r1 * r2
    return tri[:, 0] * a[:, None] + tri[:, 1] * b[:, None] + tri[:, 2] * c[:, None]


def nearest_distances(target: trimesh.Trimesh, points: np.ndarray) -> tuple[np.ndarray, str]:
    if len(points) == 0:
        return np.empty(0), "none"
    try:
        _, dist, _ = trimesh.proximity.closest_point(target, points)
        return np.asarray(dist), "triangle"
    except Exception:
        # Scalable fallback when rtree is unavailable: query nearby triangle
        # centroids, then compute exact point-to-triangle distance among those
        # candidates. This is approximate for very large/irregular triangles,
        # but much more meaningful than nearest-vertex distance.
        triangles = np.asarray(target.triangles)
        if len(triangles) == 0:
            return np.full(len(points), np.inf), "none"
        centers = np.asarray(target.triangles_center)
        tree = cKDTree(centers)
        k = min(32, len(triangles))
        output = []
        chunk_size = 4000
        for start in range(0, len(points), chunk_size):
            block = points[start:start + chunk_size]
            _, idx = tree.query(block, k=k, workers=-1)
            if k == 1:
                idx = np.asarray(idx)[:, None]
            candidate_triangles = triangles[np.asarray(idx).reshape(-1)]
            repeated_points = np.repeat(block, k, axis=0)
            closest = trimesh.triangles.closest_point(candidate_triangles, repeated_points)
            dist = np.linalg.norm(closest - repeated_points, axis=1).reshape(len(block), k)
            output.append(np.min(dist, axis=1))
        return np.concatenate(output), "triangle-candidate-fallback"


def stats(values: np.ndarray) -> dict[str, float | None]:
    if len(values) == 0:
        return {"count": 0, "median": None, "p95": None, "p99": None, "max": None, "mean": None}
    return {
        "count": int(len(values)),
        "median": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
        "p99": float(np.percentile(values, 99)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("result", type=Path)
    p.add_argument("--roi", type=Path)
    p.add_argument("--samples", type=int, default=30000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-outside-p95", type=float)
    p.add_argument("--max-outside-max", type=float)
    p.add_argument("--require-watertight", action="store_true")
    p.add_argument("--max-components", type=int)
    p.add_argument("--json", dest="json_path", type=Path)
    return p


def main() -> int:
    args = parser().parse_args()
    source = load_mesh(args.source)
    result = load_mesh(args.result)
    roi = json.loads(args.roi.read_text()) if args.roi else None

    src_pts = sample_surface(source, args.samples, args.seed)
    res_pts = sample_surface(result, args.samples, args.seed + 1)
    src_out = src_pts[~roi_mask(src_pts, roi)]
    res_out = res_pts[~roi_mask(res_pts, roi)]

    d_src_res, method_a = nearest_distances(result, src_out)
    d_res_src, method_b = nearest_distances(source, res_out)
    a_stats = stats(d_src_res)
    b_stats = stats(d_res_src)

    try:
        components = len(result.split(only_watertight=False, repair=False))
    except Exception:
        components = None

    failures: list[str] = []
    if args.require_watertight and not result.is_watertight:
        failures.append("result is not watertight")
    if args.max_components is not None and (components is None or components > args.max_components):
        failures.append(f"result components {components} > {args.max_components}")
    if args.max_outside_p95 is not None:
        worst_p95 = max(v for v in [a_stats["p95"], b_stats["p95"]] if v is not None)
        if worst_p95 > args.max_outside_p95:
            failures.append(f"outside ROI p95 {worst_p95:.6g} > {args.max_outside_p95}")
    if args.max_outside_max is not None:
        worst_max = max(v for v in [a_stats["max"], b_stats["max"]] if v is not None)
        if worst_max > args.max_outside_max:
            failures.append(f"outside ROI max {worst_max:.6g} > {args.max_outside_max}")

    report = {
        "source": str(args.source),
        "result": str(args.result),
        "roi": str(args.roi) if args.roi else None,
        "samples_requested_per_mesh": args.samples,
        "source_outside_to_result": a_stats,
        "result_outside_to_source": b_stats,
        "distance_method": {"source_to_result": method_a, "result_to_source": method_b},
        "source_volume": float(source.volume),
        "result_volume": float(result.volume),
        "volume_delta": float(result.volume - source.volume),
        "result_watertight": bool(result.is_watertight),
        "result_winding_consistent": bool(result.is_winding_consistent),
        "result_components": components,
        "passed": not failures,
        "failures": failures,
        "caution": "Candidate-triangle fallback is approximate; install rtree for exact indexed triangle distance in critical acceptance.",
    }
    text = json.dumps(report, indent=2)
    print(text)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(text + "\n", encoding="utf-8")
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
