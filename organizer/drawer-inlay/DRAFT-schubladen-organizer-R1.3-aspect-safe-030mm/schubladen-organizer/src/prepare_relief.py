#!/usr/bin/env python3
"""Register a source image and derive a physically scaled 16-bit heightmap.

The source image's natural square-pixel aspect is authoritative.  Repeat tiles
are sized in millimetres from one configured anchor dimension; the other
dimension is derived uniformly.  The target raster may have a different raw
pixel aspect, but it may never silently stretch the physical texture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageOps


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(job_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (job_dir / path).resolve()


def load_grayscale_float(path: Path, background_gray: int) -> tuple[np.ndarray, dict[str, Any]]:
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened)
        mode = image.mode
        width, height = image.size
        embedded_dpi = image.info.get("dpi")
        if mode in {"I;16", "I;16L", "I;16B"}:
            raw = np.asarray(image)
            field = raw.astype(np.float64) / 65535.0
            precision = 16
        elif mode == "I":
            raw = np.asarray(image, dtype=np.float64)
            maximum = float(np.max(raw)) if raw.size else 0.0
            field = raw / (65535.0 if maximum > 255 else 255.0)
            precision = 16 if maximum > 255 else 8
        else:
            rgba = np.asarray(image.convert("RGBA"), dtype=np.float64) / 255.0
            rgb = rgba[..., :3]
            alpha = rgba[..., 3:4]
            background = np.full_like(rgb, float(background_gray) / 255.0)
            composited = rgb * alpha + background * (1.0 - alpha)
            field = (
                0.2126 * composited[..., 0]
                + 0.7152 * composited[..., 1]
                + 0.0722 * composited[..., 2]
            )
            precision = 8
    return np.clip(field, 0.0, 1.0), {
        "input_mode": mode,
        "pixel_width": width,
        "pixel_height": height,
        "embedded_dpi": list(embedded_dpi) if embedded_dpi else None,
        "source_precision_bit_depth_guess": precision,
    }


def save_u16(path: Path, field: np.ndarray, dpi_x: float, dpi_y: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    values = np.rint(np.clip(field, 0.0, 1.0) * 65535.0).astype(np.uint16)
    temporary = path.with_name(path.name + ".tmp")
    Image.fromarray(values).save(temporary, format="PNG", dpi=(dpi_x, dpi_y))
    with Image.open(temporary) as check:
        check.load()
        if check.size != (values.shape[1], values.shape[0]):
            raise ValueError("atomic PNG verification returned the wrong raster size")
    temporary.replace(path)


def resize_float(field: np.ndarray, width: int, height: int) -> np.ndarray:
    if field.shape == (height, width):
        return field.copy()
    floating = Image.fromarray(field.astype(np.float32), mode="F")
    resized = floating.resize((width, height), Image.Resampling.LANCZOS)
    return np.clip(np.asarray(resized, dtype=np.float64), 0.0, 1.0)


def seam_metrics(field: np.ndarray) -> dict[str, float]:
    return {
        "x_mean_abs": float(np.mean(np.abs(field[:, 0] - field[:, -1]))),
        "x_max_abs": float(np.max(np.abs(field[:, 0] - field[:, -1]))),
        "y_mean_abs": float(np.mean(np.abs(field[0, :] - field[-1, :]))),
        "y_max_abs": float(np.max(np.abs(field[0, :] - field[-1, :]))),
    }


def make_periodic(field: np.ndarray, blend_x: int, blend_y: int) -> np.ndarray:
    """Cross-fade opposite borders while preserving the untouched central image."""
    result = field.copy()
    width = result.shape[1]
    height = result.shape[0]
    blend_x = max(1, min(blend_x, width // 2))
    blend_y = max(1, min(blend_y, height // 2))
    for index in range(blend_x):
        weight = 1.0 - index / max(1, blend_x - 1)
        left = result[:, index].copy()
        right = result[:, width - 1 - index].copy()
        mean = 0.5 * (left + right)
        result[:, index] = left * (1.0 - weight) + mean * weight
        result[:, width - 1 - index] = right * (1.0 - weight) + mean * weight
    for index in range(blend_y):
        weight = 1.0 - index / max(1, blend_y - 1)
        top = result[index, :].copy()
        bottom = result[height - 1 - index, :].copy()
        mean = 0.5 * (top + bottom)
        result[index, :] = top * (1.0 - weight) + mean * weight
        result[height - 1 - index, :] = bottom * (1.0 - weight) + mean * weight
    result[:, -1] = result[:, 0]
    result[-1, :] = result[0, :]
    return result


def repeat_to_target(tile: np.ndarray, width: int, height: int) -> np.ndarray:
    repeats_y = max(1, int(np.ceil(height / tile.shape[0])))
    repeats_x = max(1, int(np.ceil(width / tile.shape[1])))
    return np.tile(tile, (repeats_y, repeats_x))[:height, :width]


def percent_error(actual: float, expected: float) -> float:
    return abs(actual / expected - 1.0) * 100.0


def source_physical_size(spec: dict, pixel_width: int, pixel_height: int) -> tuple[float, float, str]:
    """Resolve a supplied square-pixel image to an isotropic physical scale."""
    if pixel_width <= 0 or pixel_height <= 0:
        raise ValueError("source raster dimensions must be positive")
    authoring = spec["physical_authoring"]
    natural_aspect = pixel_width / pixel_height
    width_mm = float(authoring["width_mm"])
    policy = authoring.get("replacement_height_policy", "fixed")
    if policy == "derive_from_square_pixel_source_aspect":
        height_mm = width_mm / natural_aspect
        origin = "square-pixel source aspect with configured physical width anchor"
    elif policy == "fixed":
        height_mm = float(authoring["height_mm"])
        origin = "fixed physical authoring dimensions"
    else:
        raise ValueError(f"unsupported replacement_height_policy: {policy}")
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("source physical dimensions must be positive")
    return width_mm, height_mm, origin


def repeat_tile_size(processing: dict, source_aspect: float, allow_distortion: bool) -> tuple[float, float, dict]:
    cfg = processing["repeat_tile"]
    policy = cfg.get("size_policy", "preserve_source_aspect")
    anchor_axis = cfg.get("anchor_axis", "width")
    anchor_mm = float(cfg["anchor_mm"])
    if anchor_mm <= 0:
        raise ValueError("repeat_tile.anchor_mm must be positive")
    if policy == "preserve_source_aspect":
        if anchor_axis == "width":
            width_mm, height_mm = anchor_mm, anchor_mm / source_aspect
        elif anchor_axis == "height":
            width_mm, height_mm = anchor_mm * source_aspect, anchor_mm
        else:
            raise ValueError("repeat_tile.anchor_axis must be width or height")
    elif policy == "explicit":
        width_mm, height_mm = map(float, cfg["size_mm"])
    else:
        raise ValueError(f"unsupported repeat tile size_policy: {policy}")
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("repeat tile dimensions must be positive")
    requested_aspect = width_mm / height_mm
    error = percent_error(requested_aspect, source_aspect)
    if error > 1.0e-9 and not allow_distortion:
        raise ValueError(
            f"repeat tile would change physical aspect by {error:.6f}% while distortion is disabled"
        )
    return width_mm, height_mm, {
        "size_policy": policy,
        "anchor_axis": anchor_axis,
        "anchor_mm": anchor_mm,
        "requested_aspect_error_pct": error,
    }


def save_square_pixel_preview(
    path: Path, field: np.ndarray, width_mm: float, height_mm: float, preview_ppi: float
) -> dict:
    pitch = 25.4 / preview_ppi
    width = max(1, round(width_mm / pitch))
    height = max(1, round(height_mm / pitch))
    preview = resize_float(field, width, height)
    values = np.rint(np.clip(preview, 0.0, 1.0) * 255.0).astype(np.uint8)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(values, mode="L").save(path, dpi=(preview_ppi, preview_ppi))
    return {
        "path": str(path),
        "pixel_width": width,
        "pixel_height": height,
        "ppi": preview_ppi,
        "geometry_input": False,
    }


def register_source(job_path: Path, job: dict, raw_source: Path) -> tuple[Path, dict]:
    job_dir = job_path.parent
    source_cfg = job["source"]
    spec_path = resolve(job_dir, source_cfg["generation_spec_path"])
    spec = read_json(spec_path)
    background = int(job["processing"].get("background_gray", 32768))
    field, info = load_grayscale_float(raw_source, round(background / 257))
    width_mm, height_mm, aspect_origin = source_physical_size(
        spec, info["pixel_width"], info["pixel_height"]
    )
    natural_aspect = info["pixel_width"] / info["pixel_height"]
    physical_aspect = width_mm / height_mm
    source_aspect_error = percent_error(physical_aspect, natural_aspect)
    image_cfg = job["image"]
    allow_distortion = bool(image_cfg.get("allow_aspect_distortion", False))
    if source_aspect_error > float(image_cfg["aspect_tolerance_pct"]) and not allow_distortion:
        raise ValueError("registered physical size violates the natural square-pixel source aspect")
    effective_ppi_x = info["pixel_width"] * 25.4 / width_mm
    effective_ppi_y = info["pixel_height"] * 25.4 / height_mm
    master = resolve(job_dir, source_cfg["master_path"])
    manifest_path = resolve(job_dir, source_cfg["manifest_path"])
    save_u16(master, field, effective_ppi_x, effective_ppi_y)
    digest = sha256_file(master)
    asset_id = f"sha256:{digest[:16]}"
    warnings = []
    if info["source_precision_bit_depth_guess"] < 16:
        warnings.append(
            "The source has approximately 8-bit tonal precision. It is stored in a 16-bit master container, but missing source tones are not invented."
        )
    metrics = seam_metrics(field)
    if metrics["x_mean_abs"] > 0.02 or metrics["y_mean_abs"] > 0.02:
        warnings.append("The supplied master is not natively seamless; configured build-stage seam blending will be applied.")
    manifest = {
        "schema": "heightmap-relief-source-v2.2",
        "schema_version": 2.2,
        "stage": "registered_source_master",
        "asset_id": asset_id,
        "sha256": digest,
        "source_kind": "supplied",
        "input": {"path": str(raw_source), "sha256": sha256_file(raw_source), **info},
        "generation_spec": {"path": str(spec_path.relative_to(job_dir)), "content": spec},
        "semantic": {
            "image_class": job["classification"]["image_class"],
            "polarity": job["classification"]["polarity"],
            "seamless_x": bool(job["classification"]["seamless_x"]),
            "seamless_y": bool(job["classification"]["seamless_y"]),
        },
        "requested_authoring": {
            **spec["physical_authoring"],
            **spec["requested_raster"],
            "square_pixels": True,
            "resolved_width_mm": width_mm,
            "resolved_height_mm": height_mm,
        },
        "registered_master": {
            "path": str(master.relative_to(job_dir)),
            "container_bit_depth": 16,
            "source_precision_bit_depth_guess": info["source_precision_bit_depth_guess"],
            "pixel_width": info["pixel_width"],
            "pixel_height": info["pixel_height"],
            "effective_ppi_x": effective_ppi_x,
            "effective_ppi_y": effective_ppi_y,
            "physical_width_mm": width_mm,
            "physical_height_mm": height_mm,
            "natural_raster_aspect": natural_aspect,
            "physical_aspect": physical_aspect,
            "physical_aspect_error_pct": source_aspect_error,
            "physical_aspect_origin": aspect_origin,
            "physical_pixel_width_mm": width_mm / info["pixel_width"],
            "physical_pixel_height_mm": height_mm / info["pixel_height"],
            "pixel_policy": "preserve",
        },
        "seam_metrics_normalized": metrics,
        "warnings": warnings,
    }
    write_json(manifest_path, manifest)
    job["source"]["asset_id"] = asset_id
    write_json(job_path, job)
    return master, manifest


def prepare_build(job_path: Path, job: dict) -> dict:
    job_dir = job_path.parent
    master = resolve(job_dir, job["source"]["master_path"])
    source_manifest_path = resolve(job_dir, job["source"]["manifest_path"])
    if not master.is_file() or not source_manifest_path.is_file():
        raise SystemExit("No registered source master. Pass an image to rebuild.py first.")
    source_manifest = read_json(source_manifest_path)
    actual_master_hash = sha256_file(master)
    if actual_master_hash != source_manifest.get("sha256"):
        raise SystemExit("Registered source-master hash mismatch. Re-run rebuild.py with the original/replacement image.")
    processing = job["processing"]
    image_cfg = job["image"]
    target = job["target"]
    width_mm = float(target["width_mm"])
    height_mm = float(target["height_mm"])
    requested_pitch_x, requested_pitch_y = map(float, target["pitch_mm"])
    pixel_width = max(1, round(width_mm / requested_pitch_x))
    pixel_height = max(1, round(height_mm / requested_pitch_y))
    pitch_x = width_mm / pixel_width
    pitch_y = height_mm / pixel_height
    dpi_x = 25.4 / pitch_x
    dpi_y = 25.4 / pitch_y

    field, _ = load_grayscale_float(master, round(int(processing.get("background_gray", 32768)) / 257))
    registered = source_manifest["registered_master"]
    source_width_mm = float(registered["physical_width_mm"])
    source_height_mm = float(registered["physical_height_mm"])
    source_aspect = source_width_mm / source_height_mm
    fit_mode = image_cfg["fit_mode"]
    aspect_policy = image_cfg["aspect_policy"]
    allow_distortion = bool(image_cfg.get("allow_aspect_distortion", False))
    tolerance = float(image_cfg["aspect_tolerance_pct"])
    if fit_mode == "stretch" and aspect_policy == "preserve" and not allow_distortion:
        raise ValueError("fit_mode=stretch is forbidden while aspect_policy=preserve")
    if fit_mode != "repeat":
        raise ValueError("this organizer relief job currently supports fit_mode=repeat")
    tile_width_mm, tile_height_mm, tile_policy = repeat_tile_size(
        processing, source_aspect, allow_distortion
    )
    tile_width_px = max(1, round(tile_width_mm / pitch_x))
    tile_height_px = max(1, round(tile_height_mm / pitch_y))
    reconstructed_tile_width_mm = tile_width_px * pitch_x
    reconstructed_tile_height_mm = tile_height_px * pitch_y
    reconstructed_aspect = reconstructed_tile_width_mm / reconstructed_tile_height_mm
    aspect_error = percent_error(reconstructed_aspect, source_aspect)
    aspect_passed = allow_distortion or aspect_error <= tolerance
    if not aspect_passed:
        raise ValueError(
            f"physical aspect validation failed: {aspect_error:.6f}% exceeds {tolerance:.6f}%"
        )
    tile = resize_float(field, tile_width_px, tile_height_px)
    seams_before = seam_metrics(tile)
    blend_mm = processing.get("seam_blend_mm", [0.0, 0.0])
    blend_x_px = max(1, round(float(blend_mm[0]) / pitch_x))
    blend_y_px = max(1, round(float(blend_mm[1]) / pitch_y))
    if job["classification"].get("seamless_x") or job["classification"].get("seamless_y"):
        tile = make_periodic(tile, blend_x_px, blend_y_px)
    build = repeat_to_target(tile, pixel_width, pixel_height)

    black = float(processing.get("black_point", 0.0))
    white = float(processing.get("white_point", 1.0))
    gamma = float(processing.get("gamma", 1.0))
    if not 0 <= black < white <= 1:
        raise ValueError("processing requires 0 <= black_point < white_point <= 1")
    if gamma <= 0:
        raise ValueError("processing.gamma must be positive")
    build = np.clip((build - black) / (white - black), 0.0, 1.0)
    build = np.power(build, gamma)
    if bool(processing.get("invert", False)):
        build = 1.0 - build

    heightmap = resolve(job_dir, job["outputs"]["heightmap"])
    metadata_path = resolve(job_dir, job["outputs"]["heightmap_metadata"])
    build_manifest_path = resolve(job_dir, job["outputs"]["build_manifest"])
    preview_path = resolve(job_dir, job["outputs"]["preview"])
    save_u16(heightmap, build, dpi_x, dpi_y)
    preview = save_square_pixel_preview(
        preview_path,
        build,
        width_mm,
        height_mm,
        float(job["outputs"].get("preview_ppi", 150.0)),
    )
    output_digest = sha256_file(heightmap)
    repeat_counts = [
        max(1, int(np.ceil(pixel_width / tile_width_px))),
        max(1, int(np.ceil(pixel_height / tile_height_px))),
    ]
    warnings = list(source_manifest.get("warnings", []))
    warnings.append(
        "The supplied image is treated as luminance-derived relief; photographic lighting is not calibrated geometric depth."
    )
    if abs(pitch_x - pitch_y) > 1.0e-12:
        warnings.append(
            "The geometry raster has non-square physical pixels; inspect the square-pixel preview, not the raw geometry PNG."
        )
    metadata = {
        "schema": "heightmap-relief-build-v2.2",
        "schema_version": 2.2,
        "stage": "surface_build_heightmap",
        "job_name": job["job_name"],
        "source_asset_id": source_manifest["asset_id"],
        "source_path": str(master.relative_to(job_dir)),
        "source_sha256": source_manifest["sha256"],
        "width_mm": width_mm,
        "height_mm": height_mm,
        "pitch_x_mm": pitch_x,
        "pitch_y_mm": pitch_y,
        "dpi_x": dpi_x,
        "dpi_y": dpi_y,
        "pixel_width": pixel_width,
        "pixel_height": pixel_height,
        "bit_depth": 16,
        "fit_mode": fit_mode,
        "invert": bool(processing.get("invert", False)),
        "gamma": gamma,
        "black_point": black,
        "white_point": white,
        "image_class": job["classification"]["image_class"],
        "surface_type": job["mapping"]["surface_type"],
        "placement_mode": job["mapping"]["placement_mode"],
        "intended_surface_mapping": job["mapping"]["intended_surface_mapping"],
        "tile_mm": [tile_width_mm, tile_height_mm],
        "tile_pixel_size": [tile_width_px, tile_height_px],
        "seam_blend_mm": list(map(float, blend_mm)),
        "seam_metrics_before": seams_before,
        "seam_metrics_after": seam_metrics(tile),
        "output_path": str(heightmap.relative_to(job_dir)),
        "output_sha256": output_digest,
        "source": {
            "size_px": [registered["pixel_width"], registered["pixel_height"]],
            "size_mm": [source_width_mm, source_height_mm],
            "raster_aspect": registered["pixel_width"] / registered["pixel_height"],
            "physical_aspect": source_aspect,
            "aspect_origin": registered["physical_aspect_origin"],
        },
        "target": {
            "width_mm": width_mm,
            "height_mm": height_mm,
            "physical_aspect": width_mm / height_mm,
            "pixel_width": pixel_width,
            "pixel_height": pixel_height,
            "raster_aspect": pixel_width / pixel_height,
            "pitch_x_mm": pitch_x,
            "pitch_y_mm": pitch_y,
            "physical_pixel_aspect": pitch_x / pitch_y,
            "dpi_x": dpi_x,
            "dpi_y": dpi_y,
            "bit_depth": 16,
        },
        "physical_fit": {
            "fit_mode": fit_mode,
            "tile_policy": tile_policy,
            "tile_width_mm": tile_width_mm,
            "tile_height_mm": tile_height_mm,
            "tile_physical_aspect": tile_width_mm / tile_height_mm,
            "tile_pixel_width": tile_width_px,
            "tile_pixel_height": tile_height_px,
            "geometry_raster_tile_aspect": tile_width_px / tile_height_px,
            "reconstructed_tile_width_mm": reconstructed_tile_width_mm,
            "reconstructed_tile_height_mm": reconstructed_tile_height_mm,
            "reconstructed_physical_aspect": reconstructed_aspect,
            "repeat_counts": repeat_counts,
            "visible_repeat_counts": [width_mm / tile_width_mm, height_mm / tile_height_mm],
            "uniform_physical_scale": tile_width_mm / source_width_mm,
            "independent_axis_scaling": False,
        },
        "aspect_validation": {
            "source_physical_aspect": source_aspect,
            "placed_physical_aspect": tile_width_mm / tile_height_mm,
            "reconstructed_physical_aspect": reconstructed_aspect,
            "error_pct": aspect_error,
            "tolerance_pct": tolerance,
            "aspect_policy": aspect_policy,
            "allow_aspect_distortion": allow_distortion,
            "passed": aspect_passed,
        },
        "preview": {
            **preview,
            "path": str(preview_path.relative_to(job_dir)),
        },
        "warnings": warnings,
    }
    write_json(metadata_path, metadata)
    job_digest = sha256_file(job_path)
    build_manifest = {
        "schema": "heightmap-relief-job-build-v2.2",
        "schema_version": 2.2,
        "stage": "relief_job_build",
        "job_name": job["job_name"],
        "job_path": str(job_path),
        "job_sha256": job_digest,
        "source": source_manifest,
        "surface_build": metadata,
        "printer": job["printer"],
        "mapping": job["mapping"],
        "processing": job["processing"],
        "classification": job["classification"],
        "relief": job["relief"],
        "geometry": job["geometry"],
        "warnings": warnings,
    }
    write_json(build_manifest_path, build_manifest)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Register and process a relief source from saved job parameters.")
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    job_path = args.job.resolve()
    job = read_json(job_path)
    if args.source:
        master, source_manifest = register_source(job_path, job, args.source.resolve())
        print(
            f"Registered source master: {master} "
            f"({source_manifest['registered_master']['pixel_width']}x{source_manifest['registered_master']['pixel_height']} px, "
            f"effective {source_manifest['registered_master']['effective_ppi_x']:.2f} PPI)"
        )
        job = read_json(job_path)
    metadata = prepare_build(job_path, job)
    print(
        f"Prepared 16-bit build heightmap: {metadata['pixel_width']}x{metadata['pixel_height']} px, "
        f"{metadata['pitch_x_mm']:.3f} mm/px, {metadata['dpi_x']:.2f} PPI; "
        f"source tile {metadata['tile_mm'][0]:.3f}x{metadata['tile_mm'][1]:.3f} mm; "
        f"aspect error {metadata['aspect_validation']['error_pct']:.6f}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
