#!/usr/bin/env python3
"""Fit a rigid or uniform-scale transform from corresponding 3D landmarks."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import dump_json, load_structured


def umeyama(source: np.ndarray, target: np.ndarray, with_scale: bool) -> tuple[np.ndarray, float]:
    if source.shape != target.shape or source.ndim != 2 or source.shape[1] != 3 or len(source) < 3:
        raise ValueError("Need matching Nx3 source and target arrays with N >= 3")
    mu_s = source.mean(axis=0)
    mu_t = target.mean(axis=0)
    xs = source - mu_s
    xt = target - mu_t
    cov = (xt.T @ xs) / len(source)
    u, singular, vt = np.linalg.svd(cov)
    d = np.ones(3)
    if np.linalg.det(u) * np.linalg.det(vt) < 0:
        d[-1] = -1
    rotation = u @ np.diag(d) @ vt
    scale = 1.0
    if with_scale:
        variance = np.sum(xs * xs) / len(source)
        if variance <= 0:
            raise ValueError("Source landmarks have zero variance")
        scale = float(np.sum(singular * d) / variance)
    translation = mu_t - scale * rotation @ mu_s
    matrix = np.eye(4)
    matrix[:3, :3] = scale * rotation
    matrix[:3, 3] = translation
    transformed = (scale * (rotation @ source.T)).T + translation
    rms = float(np.sqrt(np.mean(np.sum((transformed - target) ** 2, axis=1))))
    return matrix, rms


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("landmarks")
    p.add_argument("--allow-uniform-scale", action="store_true")
    p.add_argument("--json-out", required=True)
    args = p.parse_args()
    data = load_structured(args.landmarks)
    source = np.asarray(data["source_points_mm"], dtype=float)
    target = np.asarray(data["target_points_mm"], dtype=float)
    allow = args.allow_uniform_scale or bool(data.get("allow_uniform_scale", False))
    matrix, rms = umeyama(source, target, allow)
    report = {"matrix": matrix.tolist(), "rms_error_mm": rms, "point_count": len(source), "uniform_scale_allowed": allow}
    print(dump_json(report, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
