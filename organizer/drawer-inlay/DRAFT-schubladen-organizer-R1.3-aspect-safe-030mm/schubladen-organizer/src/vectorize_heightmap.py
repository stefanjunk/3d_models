#!/usr/bin/env python3
"""Prepare a continuous 16-bit height-field manifest for Manifold3D.

The former implementation thresholded the prepared image into three classes.
This implementation keeps one unsigned 16-bit sample at every geometry-grid
vertex.  No depth threshold or height-level quantization is applied after the
single spatial resampling step.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(path: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else (path.parent / candidate).resolve()


def load_u16(path: Path) -> np.ndarray:
    image = Image.open(path)
    data = np.asarray(image)
    if data.ndim != 2:
        image = image.convert("L")
        data = np.asarray(image)
    if data.dtype == np.uint16:
        return data
    if np.issubdtype(data.dtype, np.integer):
        maximum = float(np.iinfo(data.dtype).max)
        return np.rint(data.astype(np.float64) * (65535.0 / maximum)).astype(np.uint16)
    field = np.asarray(data, dtype=np.float64)
    if not np.all(np.isfinite(field)):
        raise ValueError("height map contains non-finite samples")
    low = float(np.min(field))
    high = float(np.max(field))
    normalized = (field - low) / max(high - low, 1.0e-12)
    return np.rint(np.clip(normalized, 0.0, 1.0) * 65535.0).astype(np.uint16)


def resample_u16(data: np.ndarray, width: int, height: int) -> np.ndarray:
    """Spatially resample once, retaining a full uint16 value per output vertex."""
    if data.shape == (height, width):
        return data.copy()
    floating = Image.fromarray(data.astype(np.float32), mode="F")
    resized = floating.resize((width, height), Image.Resampling.LANCZOS)
    values = np.asarray(resized, dtype=np.float64)
    return np.rint(np.clip(values, 0.0, 65535.0)).astype(np.uint16)


def config_u16(value: object, default: int) -> int:
    if value is None:
        return default
    parsed = int(value)
    if not 0 <= parsed <= 65535:
        raise ValueError("16-bit mapping limits must be in [0, 65535]")
    return parsed


def save_preview(path: Path, field: np.ndarray, neutral: int) -> None:
    # The preview is display-only.  It deliberately shows a smooth tonal ramp,
    # with neutral gray at 50%, dark engraving below, and bright emboss above.
    low = max(1, neutral)
    high = max(1, 65535 - neutral)
    signed = np.where(
        field < neutral,
        -((neutral - field.astype(np.float64)) / low),
        (field.astype(np.float64) - neutral) / high,
    )
    gray = np.rint(np.clip(0.5 + 0.5 * signed, 0.0, 1.0) * 255.0).astype(np.uint8)
    image = Image.fromarray(gray, mode="L")
    scale = max(1, min(4, 1400 // max(field.shape)))
    if scale > 1:
        image = image.resize((field.shape[1] * scale, field.shape[0] * scale), Image.Resampling.NEAREST)
    image.save(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()

    cfg = load_config(args.config)
    job_path = resolve(args.config, cfg["relief_job"])
    job = load_config(job_path)
    job_dir = job_path.parent
    requested_pitch = float(cfg["geometry_pitch_mm"])
    source = resolve(job_path, job["outputs"]["heightmap"])
    metadata_path = resolve(job_path, job["outputs"]["heightmap_metadata"])
    build_manifest_path = resolve(job_path, job["outputs"]["build_manifest"])
    metadata = load_config(metadata_path)
    validation = metadata.get("aspect_validation") or {}
    if validation.get("passed") is not True:
        raise ValueError("physical aspect validation has not passed; geometry generation is blocked")
    physical_fit = metadata.get("physical_fit") or {}
    tile_width = float(physical_fit["tile_width_mm"])
    tile_height = float(physical_fit["tile_height_mm"])
    tile_pixel_width = int(physical_fit["tile_pixel_width"])
    tile_pixel_height = int(physical_fit["tile_pixel_height"])
    if tile_width <= 0 or tile_height <= 0 or requested_pitch <= 0:
        raise ValueError("tile dimensions and geometry pitch must be positive")

    # Include both periodic endpoints. The prepared tile has matching borders,
    # so the 180 x 120 mm source tile repeats without an outer 180 x 180 seam.
    nx = max(3, int(np.ceil(tile_width / requested_pitch)) + 1)
    ny = max(3, int(np.ceil(tile_height / requested_pitch)) + 1)
    source_digest = sha256_file(source)
    if metadata.get("output_sha256") != source_digest:
        raise ValueError("surface-build sidecar hash does not match the current heightmap; rerun rebuild.py")
    build_manifest = load_config(build_manifest_path)
    if build_manifest.get("source", {}).get("asset_id") != job.get("source", {}).get("asset_id"):
        raise ValueError("relief build manifest refers to a stale source asset; rerun rebuild.py")
    surface_build = load_u16(source)
    if tile_pixel_width > surface_build.shape[1] or tile_pixel_height > surface_build.shape[0]:
        raise ValueError("registered source tile exceeds the prepared surface-build raster")
    original = surface_build[:tile_pixel_height, :tile_pixel_width]
    field = resample_u16(original, nx, ny)

    policy = cfg.get("neutral_policy", "median")
    if policy == "median":
        neutral = int(np.rint(np.median(original)))
    elif policy == "midpoint":
        neutral = 32768
    elif policy == "explicit":
        neutral = config_u16(cfg.get("neutral_u16"), 32768)
    else:
        raise ValueError(f"unsupported neutral_policy: {policy}")

    source_min = int(np.min(original))
    source_max = int(np.max(original))
    input_min = config_u16(cfg.get("input_min_u16"), source_min)
    input_max = config_u16(cfg.get("input_max_u16"), source_max)
    if not input_min < neutral < input_max:
        raise ValueError("input_min_u16 < neutral_u16 < input_max_u16 is required")

    exponent = float(cfg.get("height_curve_exponent", 1.0))
    if not np.isfinite(exponent) or exponent <= 0:
        raise ValueError("height_curve_exponent must be finite and positive")

    payload = base64.b64encode(field.astype("<u2", copy=False).tobytes(order="C")).decode("ascii")
    unique_values = int(np.unique(field).size)
    manifest = {
        "schema_version": 2,
        "representation": "continuous-heightfield-u16",
        "source_heightmap": str(source),
        "source_heightmap_sha256": source_digest,
        "source_asset_id": job["source"]["asset_id"],
        "relief_job": str(job_path),
        "heightmap_metadata": str(metadata_path),
        "build_manifest": str(build_manifest_path),
        "tile_width_mm": tile_width,
        "tile_height_mm": tile_height,
        "mapping_domain": "registered physical repeat tile extracted from surface-build origin",
        "requested_pitch_mm": requested_pitch,
        "pitch_x_mm": tile_width / (nx - 1),
        "pitch_y_mm": tile_height / (ny - 1),
        "grid": [nx, ny],
        "periodic_x": bool(cfg.get("repeat_x", True)),
        "periodic_y": bool(cfg.get("repeat_y", True)),
        "samples_encoding": "base64-u16le-row-major",
        "samples_u16_base64": payload,
        "height_mapping": {
            "neutral_policy": policy,
            "neutral_u16": neutral,
            "input_min_u16": input_min,
            "input_max_u16": input_max,
            "curve_exponent": exponent,
            "dark_direction": "engrave",
            "bright_direction": "emboss",
        },
        "aspect_validation": validation,
        "physical_mapping": {
            "source_tile_size_mm": [tile_width, tile_height],
            "source_tile_grid": [tile_pixel_width, tile_pixel_height],
            "geometry_raster_aspect": nx / ny,
            "physical_pixel_aspect": (tile_width / (nx - 1)) / (tile_height / (ny - 1)),
            "reconstructed_physical_aspect": (nx - 1) * (tile_width / (nx - 1)) / ((ny - 1) * (tile_height / (ny - 1))),
        },
        "statistics": {
            "surface_build_grid": [int(surface_build.shape[1]), int(surface_build.shape[0])],
            "source_grid": [int(original.shape[1]), int(original.shape[0])],
            "source_pitch_mm": [metadata["pitch_x_mm"], metadata["pitch_y_mm"]],
            "source_dpi": [metadata["dpi_x"], metadata["dpi_y"]],
            "source_min_u16": source_min,
            "source_max_u16": source_max,
            "source_unique_values": int(np.unique(original).size),
            "geometry_unique_values": unique_values,
            "retained_height_bits": 16,
            "additional_height_level_quantization": False,
            "sample_count": int(field.size),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if args.preview:
        save_preview(args.preview, field, neutral)
    print(json.dumps(manifest["statistics"], sort_keys=True))


if __name__ == "__main__":
    main()
