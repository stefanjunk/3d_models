#!/usr/bin/env python3
"""Measure the successful direct sampler against the failed prefiltered path."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


JOB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[6]
REFERENCE = REPO_ROOT / (
    "products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf/"
    "setzkasten/honeycomb-wood-wall-shelf/assets/holz.png"
)
MASTER = REPO_ROOT / "libraries/surface-textures/wood-001/master/wood-001-tile-16bit.png"
FAILED_BUILD_RASTER = REPO_ROOT / (
    "products/organization-storage/mm-per-001-nameform-bookends/coupons/"
    "wood-texture-pitch-v0.1.0/build/heightmaps/wood-001-pitch-0p45-16bit.png"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized(path: Path) -> np.ndarray:
    values = np.asarray(Image.open(path))
    if values.ndim == 3:
        values = values[..., :3].astype(np.float32).mean(axis=2)
    else:
        values = values.astype(np.float32)
    divisor = 65535.0 if float(values.max()) > 255.0 else 255.0
    return np.clip(values / divisor, 0.0, 1.0)


def sample_periodic(values: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    height, width = values.shape
    x = np.mod(u, 1.0) * width
    y = np.mod(v, 1.0) * height
    x_floor, y_floor = np.floor(x), np.floor(y)
    x0, y0 = x_floor.astype(np.int64) % width, y_floor.astype(np.int64) % height
    x1, y1 = (x0 + 1) % width, (y0 + 1) % height
    fx, fy = (x - x_floor).astype(np.float32), (y - y_floor).astype(np.float32)
    lower = values[y0, x0] * (1.0 - fx) + values[y0, x1] * fx
    upper = values[y1, x0] * (1.0 - fx) + values[y1, x1] * fx
    return lower * (1.0 - fy) + upper * fy


def metrics(values: np.ndarray, u: np.ndarray, v: np.ndarray, depth_mm: float) -> dict:
    sampled = sample_periodic(values, u, v)
    p05, p95 = np.percentile(sampled, [5.0, 95.0])
    span = float(p95 - p05)
    return {
        "source_pixels_xy": [int(values.shape[1]), int(values.shape[0])],
        "sample_min_max": [float(sampled.min()), float(sampled.max())],
        "sample_standard_deviation": float(sampled.std()),
        "sample_p05_p95": [float(p05), float(p95)],
        "sample_p05_p95_span": span,
        "relief_p05_p95_span_mm_at_0p6": depth_mm * span,
        "maximum_relief_mm_at_0p6": depth_mm * float(sampled.max()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out", type=Path, default=JOB_ROOT / "reports/reference-pipeline-comparison.json"
    )
    args = parser.parse_args()
    reference, master, failed = normalized(REFERENCE), normalized(MASTER), normalized(FAILED_BUILD_RASTER)
    if reference.shape != master.shape:
        raise ValueError("registered master and Honeycomb source shape differ")
    difference = np.abs(reference - master)
    correlation = float(np.corrcoef(reference.reshape(-1), master.reshape(-1))[0, 1])
    coordinates = np.linspace(0.0, 45.0, 101)
    xx, zz = np.meshgrid(coordinates, coordinates, indexing="xy")
    u, v = (45.0 - zz) / 62.0, xx / 252.0
    direct = metrics(reference, u, v, 0.6)
    registered = metrics(master, u, v, 0.6)
    prefiltered = metrics(failed, u, v, 0.6)
    direct_span = direct["sample_p05_p95_span"]
    failed_span = prefiltered["sample_p05_p95_span"]
    loss_percent = 100.0 * (direct_span - failed_span) / direct_span
    checks = {
        "registered_master_matches_reference": correlation >= 0.999999
        and float(difference.max()) <= 1.0e-5,
        "same_physical_coordinates": True,
        "failed_path_contains_low_resolution_prefilter": failed.shape != reference.shape,
        "direct_sampling_preserves_more_robust_span": direct_span > failed_span,
        "documented_span_loss_reproduced": abs(loss_percent - 34.8) <= 0.1,
    }
    report = {
        "schema_version": "1.0",
        "tool": "MM-PER-001 reference relief pipeline comparison",
        "tool_version": "0.2.0",
        "profile": "diagnostic",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": [
            {"path": str(Path(__file__).resolve()), "sha256": sha256(Path(__file__).resolve())},
            {"path": str(REFERENCE), "sha256": sha256(REFERENCE)},
            {"path": str(MASTER), "sha256": sha256(MASTER)},
            {"path": str(FAILED_BUILD_RASTER), "sha256": sha256(FAILED_BUILD_RASTER)},
        ],
        "checks": checks,
        "metrics": {
            "comparison_patch_mm": [45.0, 45.0],
            "mesh_pitch_mm": 0.45,
            "grid_vertices_xy": [101, 101],
            "mapping": "u=(45-z)/62, v=x/252",
            "reference_to_registered_master": {
                "maximum_absolute_error": float(difference.max()),
                "root_mean_square_error": float(np.sqrt(np.mean(difference * difference))),
                "pearson_correlation": correlation,
            },
            "honeycomb_direct_source": direct,
            "registered_master_direct": registered,
            "failed_v0p1_lanczos_build_raster": prefiltered,
            "robust_span_loss_percent": loss_percent,
            "direct_span_gain_over_failed_percent": 100.0 * (direct_span - failed_span) / failed_span,
        },
        "limitations": [
            "This isolates the digital sampling path; it does not prove physical causation.",
            "The physical v0.1 failure has no photo or profilometry and its exact filament and slicer overrides remain unknown."
        ],
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    if args.json_out.exists():
        raise FileExistsError(f"refusing to overwrite {args.json_out}")
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": checks, "loss_percent": loss_percent}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
