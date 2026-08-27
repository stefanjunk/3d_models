#!/usr/bin/env python3
"""Run a 20 mm square/circle through the production raster and geometry grids."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from prepare_relief import make_periodic, read_json, repeat_tile_size, repeat_to_target, save_u16
from vectorize_heightmap import resample_u16, save_preview


ROOT = Path(__file__).resolve().parent.parent


def bbox_size(mask: np.ndarray, pitch_x: float, pitch_y: float) -> tuple[float, float]:
    rows, columns = np.nonzero(mask)
    if rows.size == 0:
        raise ValueError("diagnostic marker disappeared during processing")
    return (columns.max() - columns.min() + 1) * pitch_x, (rows.max() - rows.min() + 1) * pitch_y


def error_pct(value: float, nominal: float) -> float:
    return abs(value / nominal - 1.0) * 100.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate physical aspect with known 20 mm markers.")
    parser.add_argument("--job", type=Path, default=ROOT / "relief" / "organizer" / "relief-job.json")
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "relief-config.json")
    parser.add_argument("--report", type=Path, default=ROOT / "reports" / "aspect-diagnostic.json")
    args = parser.parse_args()

    job = read_json(args.job)
    config = read_json(args.config)
    target_w, target_h = float(job["target"]["width_mm"]), float(job["target"]["height_mm"])
    pitch_x, pitch_y = map(float, job["target"]["pitch_mm"])
    target_px_w = round(target_w / pitch_x)
    target_px_h = round(target_h / pitch_y)

    source_aspect = 1.5
    tile_w, tile_h, tile_policy = repeat_tile_size(job["processing"], source_aspect, False)
    tile_px_w = round(tile_w / pitch_x)
    tile_px_h = round(tile_h / pitch_y)
    x = (np.arange(tile_px_w) + 0.5) * pitch_x
    y = (np.arange(tile_px_h) + 0.5) * pitch_y
    xx, yy = np.meshgrid(x, y)
    marker_mm = 20.0
    field = np.full((tile_px_h, tile_px_w), 0.25, dtype=np.float64)
    square = (np.abs(xx - 50.0) <= marker_mm / 2) & (np.abs(yy - 60.0) <= marker_mm / 2)
    circle = (xx - 120.0) ** 2 + (yy - 60.0) ** 2 <= (marker_mm / 2) ** 2
    field[square] = 0.75
    field[circle] = 1.0

    blend_mm = job["processing"]["seam_blend_mm"]
    periodic = make_periodic(
        field,
        max(1, round(float(blend_mm[0]) / pitch_x)),
        max(1, round(float(blend_mm[1]) / pitch_y)),
    )
    build = repeat_to_target(periodic, target_px_w, target_px_h)
    report_dir = args.report.parent
    report_dir.mkdir(parents=True, exist_ok=True)
    build_path = report_dir / "aspect-diagnostic-build.png"
    save_u16(build_path, build, 25.4 / pitch_x, 25.4 / pitch_y)

    geometry_pitch = float(config["geometry_pitch_mm"])
    nx = int(np.ceil(tile_w / geometry_pitch)) + 1
    ny = int(np.ceil(tile_h / geometry_pitch)) + 1
    geometry = resample_u16(np.rint(periodic * 65535.0).astype(np.uint16), nx, ny)
    geometry_pitch_x = tile_w / (nx - 1)
    geometry_pitch_y = tile_h / (ny - 1)
    preview_path = report_dir / "aspect-diagnostic-geometry-preview.png"
    save_preview(preview_path, geometry, 32768)

    gx = np.arange(nx) * geometry_pitch_x
    gy = np.arange(ny) * geometry_pitch_y
    gxx, gyy = np.meshgrid(gx, gy)
    square_window = (gxx >= 30) & (gxx <= 70) & (gyy >= 40) & (gyy <= 80)
    circle_window = (gxx >= 100) & (gxx <= 140) & (gyy >= 40) & (gyy <= 80)
    square_mask = square_window & (geometry >= round(0.60 * 65535)) & (geometry <= round(0.88 * 65535))
    circle_mask = circle_window & (geometry >= round(0.90 * 65535))
    square_w, square_h = bbox_size(square_mask, geometry_pitch_x, geometry_pitch_y)
    circle_w, circle_h = bbox_size(circle_mask, geometry_pitch_x, geometry_pitch_y)

    reconstructed_tile_aspect = (tile_px_w * pitch_x) / (tile_px_h * pitch_y)
    tile_aspect_error = error_pct(reconstructed_tile_aspect, source_aspect)
    dimensions = [square_w, square_h, circle_w, circle_h]
    dimension_errors = [error_pct(value, marker_mm) for value in dimensions]
    circle_ellipticity = error_pct(circle_w, circle_h)
    tolerance = float(job["image"]["aspect_tolerance_pct"])
    # One geometry sample (0.30 mm) across a 20 mm marker equals the 1.5% gate.
    passed = (
        tile_aspect_error <= tolerance
        and max(dimension_errors) <= tolerance + 1.0e-9
        and circle_ellipticity <= tolerance + 1.0e-9
    )
    report = {
        "schema": "heightmap-aspect-diagnostic-v2.2",
        "status": "PASS" if passed else "FAIL",
        "mapping_model": "planar millimetre coordinates; target domain sampled directly by Manifold3D",
        "source": {"physical_size_mm": [tile_w, tile_h], "physical_aspect": source_aspect},
        "target": {"physical_size_mm": [target_w, target_h], "build_grid": [target_px_w, target_px_h]},
        "repeat_tile": {
            "policy": tile_policy,
            "physical_size_mm": [tile_w, tile_h],
            "raster_size_px": [tile_px_w, tile_px_h],
            "reconstructed_physical_aspect": reconstructed_tile_aspect,
            "aspect_error_pct": tile_aspect_error,
        },
        "geometry_grid": {
            "grid": [nx, ny],
            "pitch_mm": [geometry_pitch_x, geometry_pitch_y],
            "nominal_marker_mm": marker_mm,
            "square_measured_mm": [square_w, square_h],
            "circle_measured_diameter_mm": [circle_w, circle_h],
            "dimension_error_pct": dimension_errors,
            "circle_ellipticity_pct": circle_ellipticity,
        },
        "tolerance_pct": tolerance,
        "artifacts": {
            "build_heightmap": str(build_path.relative_to(ROOT)),
            "geometry_preview": str(preview_path.relative_to(ROOT)),
        },
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
