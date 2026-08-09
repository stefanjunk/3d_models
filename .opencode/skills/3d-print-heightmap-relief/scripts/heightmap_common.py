#!/usr/bin/env python3
"""Shared image, sampling, and geometry helpers for printable height maps."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
from PIL import Image
from scipy import ndimage

EPS = 1.0e-12


def parse_pair(value: str, cast: Callable[[str], Any] = float) -> tuple[Any, Any]:
    text = value.lower().replace("x", ",")
    parts = [item.strip() for item in text.split(",") if item.strip()]
    if len(parts) != 2:
        raise ValueError(f"Expected two values, got: {value!r}")
    return cast(parts[0]), cast(parts[1])


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb, dtype=np.float32)
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    values = np.asarray(vectors)
    lengths = np.linalg.norm(values, axis=-1, keepdims=True)
    return values / np.maximum(lengths, EPS)


def smoothstep01(value: np.ndarray) -> np.ndarray:
    x = np.clip(np.asarray(value, dtype=np.float32), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def load_image_float(
    path: str | Path,
    *,
    grayscale: str = "luma",
    alpha_mode: str = "base",
    luma_space: str = "srgb",
    base_level: float = 0.0,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Load an image as normalized float32 while preserving 16-bit grayscale."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)

    with Image.open(source) as im:
        original_mode = im.mode
        original_size = im.size
        raw = np.asarray(im)
        is_high_depth_gray = original_mode.startswith("I;16") or original_mode in {"I", "F"}

        if is_high_depth_gray and raw.ndim == 2:
            values = raw.astype(np.float32)
            raw_min = float(np.nanmin(values))
            raw_max = float(np.nanmax(values))
            if original_mode.startswith("I;16"):
                divisor = 65535.0
            elif original_mode == "F" and raw_min >= 0.0 and raw_max <= 1.0:
                divisor = 1.0
            elif raw_min >= 0.0 and raw_max <= 255.0:
                divisor = 255.0
            elif raw_min >= 0.0 and raw_max <= 65535.0:
                divisor = 65535.0
            else:
                divisor = max(raw_max - raw_min, EPS)
                values = values - raw_min
            gray_native = np.clip(values / divisor, 0.0, 1.0)
            alpha = np.ones_like(gray_native, dtype=np.float32)
            if grayscale == "alpha":
                gray = alpha
            elif grayscale in {"luma", "average", "max", "min", "red", "green", "blue"}:
                gray = gray_native
            else:
                raise ValueError(f"Unsupported grayscale mode: {grayscale}")
        else:
            rgba = np.asarray(im.convert("RGBA"), dtype=np.float32) / 255.0
            rgb = rgba[..., :3]
            alpha = rgba[..., 3]
            work_rgb = srgb_to_linear(rgb) if luma_space == "linear" else rgb
            if grayscale == "luma":
                gray = (
                    0.2126 * work_rgb[..., 0]
                    + 0.7152 * work_rgb[..., 1]
                    + 0.0722 * work_rgb[..., 2]
                )
            elif grayscale == "average":
                gray = np.mean(work_rgb, axis=2)
            elif grayscale == "max":
                gray = np.max(work_rgb, axis=2)
            elif grayscale == "min":
                gray = np.min(work_rgb, axis=2)
            elif grayscale in {"red", "green", "blue", "alpha"}:
                channel = {"red": 0, "green": 1, "blue": 2}.get(grayscale)
                gray = alpha if channel is None else work_rgb[..., channel]
            else:
                raise ValueError(f"Unsupported grayscale mode: {grayscale}")

    if alpha_mode == "base":
        gray = gray * alpha + float(base_level) * (1.0 - alpha)
    elif alpha_mode in {"black", "multiply"}:
        gray = gray * alpha
    elif alpha_mode == "white":
        gray = gray * alpha + (1.0 - alpha)
    elif alpha_mode == "ignore":
        pass
    else:
        raise ValueError(f"Unsupported alpha mode: {alpha_mode}")

    gray = np.clip(gray, 0.0, 1.0).astype(np.float32, copy=False)
    metadata = {
        "source": str(source),
        "source_mode": original_mode,
        "source_dtype": str(raw.dtype),
        "source_width_px": int(original_size[0]),
        "source_height_px": int(original_size[1]),
        "alpha_present": bool(np.any(alpha < 0.99999)),
        "transparent_fraction": float(np.mean(alpha < 0.99999)),
        "grayscale": grayscale,
        "alpha_mode": alpha_mode,
        "luma_space": luma_space,
        "base_level": float(base_level),
    }
    return gray, metadata


def _resample(array: np.ndarray, width: int, height: int, order: int = 3) -> np.ndarray:
    if width < 1 or height < 1:
        raise ValueError("Target dimensions must be positive")
    src_h, src_w = array.shape
    if src_w == width and src_h == height:
        return np.asarray(array, dtype=np.float32).copy()
    x = np.linspace(0.0, max(0, src_w - 1), width, dtype=np.float64)
    y = np.linspace(0.0, max(0, src_h - 1), height, dtype=np.float64)
    X, Y = np.meshgrid(x, y, indexing="xy")
    result = ndimage.map_coordinates(
        np.asarray(array, dtype=np.float32),
        [Y, X],
        order=int(order),
        mode="nearest",
        prefilter=order > 1,
    )
    return np.clip(result, 0.0, 1.0).astype(np.float32, copy=False)


def resize_fit(
    array: np.ndarray,
    target_width: int,
    target_height: int,
    *,
    fit: str = "stretch",
    pad_level: float = 0.0,
    repeat_x: float = 1.0,
    repeat_y: float = 1.0,
    interpolation_order: int = 3,
) -> np.ndarray:
    """Resize using stretch, aspect-preserving cover/contain, or periodic tile."""
    source = np.asarray(array, dtype=np.float32)
    if source.ndim != 2:
        raise ValueError("resize_fit expects a 2D array")
    target_width = int(target_width)
    target_height = int(target_height)
    if target_width < 1 or target_height < 1:
        raise ValueError("Target dimensions must be positive")

    if fit == "stretch":
        return _resample(source, target_width, target_height, interpolation_order)

    if fit == "tile":
        if repeat_x <= 0 or repeat_y <= 0:
            raise ValueError("Tile repeat counts must be positive")
        src_h, src_w = source.shape
        # Endpoint is intentionally omitted: a periodic raster stores samples
        # over [0, period), and the first pixel follows the last at the seam.
        x = (np.arange(target_width, dtype=np.float64) / target_width * repeat_x * src_w) % src_w
        y = (np.arange(target_height, dtype=np.float64) / target_height * repeat_y * src_h) % src_h
        X, Y = np.meshgrid(x, y, indexing="xy")
        result = ndimage.map_coordinates(
            source,
            [Y, X],
            order=int(interpolation_order),
            mode="wrap",
            prefilter=interpolation_order > 1,
        )
        return np.clip(result, 0.0, 1.0).astype(np.float32, copy=False)

    if fit not in {"cover", "contain"}:
        raise ValueError(f"Unsupported fit mode: {fit}")

    src_h, src_w = source.shape
    scale_x = target_width / max(src_w, 1)
    scale_y = target_height / max(src_h, 1)
    scale = max(scale_x, scale_y) if fit == "cover" else min(scale_x, scale_y)
    resized_w = max(1, int(round(src_w * scale)))
    resized_h = max(1, int(round(src_h * scale)))
    resized = _resample(source, resized_w, resized_h, interpolation_order)

    if fit == "cover":
        x0 = max(0, (resized_w - target_width) // 2)
        y0 = max(0, (resized_h - target_height) // 2)
        cropped = resized[y0:y0 + target_height, x0:x0 + target_width]
        # Rounding can leave one pixel short.
        if cropped.shape != (target_height, target_width):
            cropped = _resample(cropped, target_width, target_height, interpolation_order)
        return cropped.astype(np.float32, copy=False)

    output = np.full((target_height, target_width), float(pad_level), dtype=np.float32)
    x0 = (target_width - resized_w) // 2
    y0 = (target_height - resized_h) // 2
    output[y0:y0 + resized_h, x0:x0 + resized_w] = resized
    return np.clip(output, 0.0, 1.0)


def percentile_levels(array: np.ndarray, low_percent: float, high_percent: float) -> tuple[np.ndarray, float, float]:
    if not 0 <= low_percent < high_percent <= 100:
        raise ValueError("Levels must satisfy 0 <= low < high <= 100")
    low, high = np.percentile(array, [low_percent, high_percent])
    if high <= low + EPS:
        return np.zeros_like(array, dtype=np.float32), float(low), float(high)
    result = (array - low) / (high - low)
    return np.clip(result, 0.0, 1.0).astype(np.float32), float(low), float(high)


def apply_gamma(array: np.ndarray, gamma: float) -> np.ndarray:
    if gamma <= 0:
        raise ValueError("Gamma must be positive")
    return np.clip(np.asarray(array, dtype=np.float32), 0.0, 1.0) ** float(gamma)


def apply_contrast(array: np.ndarray, contrast: float) -> np.ndarray:
    if contrast < 0:
        raise ValueError("Contrast cannot be negative")
    return np.clip(0.5 + (np.asarray(array, dtype=np.float32) - 0.5) * contrast, 0.0, 1.0)


def _sigma(radius_mm: float, pitch_x: float, pitch_y: float) -> tuple[float, float]:
    return (
        max(0.0, float(radius_mm) / max(float(pitch_y), EPS)),
        max(0.0, float(radius_mm) / max(float(pitch_x), EPS)),
    )


def apply_blur_mm(array: np.ndarray, radius_mm: float, pitch_x: float, pitch_y: float) -> np.ndarray:
    if radius_mm <= 0:
        return np.asarray(array, dtype=np.float32)
    return ndimage.gaussian_filter(array, sigma=_sigma(radius_mm, pitch_x, pitch_y), mode="reflect").astype(np.float32)


def apply_unsharp_mm(
    array: np.ndarray,
    radius_mm: float,
    amount: float,
    pitch_x: float,
    pitch_y: float,
) -> np.ndarray:
    blurred = apply_blur_mm(array, radius_mm, pitch_x, pitch_y)
    return np.clip(array + float(amount) * (array - blurred), 0.0, 1.0).astype(np.float32)


def apply_highpass_mm(
    array: np.ndarray,
    radius_mm: float,
    amount: float,
    pitch_x: float,
    pitch_y: float,
) -> np.ndarray:
    blurred = apply_blur_mm(array, radius_mm, pitch_x, pitch_y)
    high = array - blurred
    return np.clip(0.5 + float(amount) * high, 0.0, 1.0).astype(np.float32)


def apply_soft_threshold(array: np.ndarray, threshold: float, softness: float = 0.0) -> np.ndarray:
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be in [0,1]")
    values = np.asarray(array, dtype=np.float32)
    if softness <= 0:
        return (values >= threshold).astype(np.float32)
    half = max(float(softness) / 2.0, EPS)
    return smoothstep01((values - (threshold - half)) / (2.0 * half))


def blend_periodic_edges(array: np.ndarray, blend_x_px: int = 0, blend_y_px: int = 0) -> np.ndarray:
    """Blend opposite strips toward one another; boundary pixels become equal."""
    out = np.asarray(array, dtype=np.float32).copy()
    h, w = out.shape
    bx = min(max(int(blend_x_px), 0), w // 2)
    by = min(max(int(blend_y_px), 0), h // 2)
    for i in range(bx):
        weight = float(smoothstep01(np.array((bx - i) / max(bx, 1))))
        left = out[:, i].copy()
        right = out[:, w - 1 - i].copy()
        average = 0.5 * (left + right)
        out[:, i] = left * (1.0 - weight) + average * weight
        out[:, w - 1 - i] = right * (1.0 - weight) + average * weight
    for i in range(by):
        weight = float(smoothstep01(np.array((by - i) / max(by, 1))))
        top = out[i, :].copy()
        bottom = out[h - 1 - i, :].copy()
        average = 0.5 * (top + bottom)
        out[i, :] = top * (1.0 - weight) + average * weight
        out[h - 1 - i, :] = bottom * (1.0 - weight) + average * weight
    return np.clip(out, 0.0, 1.0)


def seam_metrics(array: np.ndarray) -> dict[str, float]:
    """Measure seam steps and compare them with normal adjacent-pixel steps."""
    values = np.asarray(array, dtype=np.float32)
    lr = values[:, 0] - values[:, -1]
    tb = values[0, :] - values[-1, :]
    dx = np.diff(values, axis=1)
    dy = np.diff(values, axis=0)

    lr_rms = float(np.sqrt(np.mean(lr * lr)))
    tb_rms = float(np.sqrt(np.mean(tb * tb)))
    dx_rms = float(np.sqrt(np.mean(dx * dx))) if dx.size else 0.0
    dy_rms = float(np.sqrt(np.mean(dy * dy))) if dy.size else 0.0
    return {
        "left_right_rms": lr_rms,
        "left_right_max": float(np.max(np.abs(lr))),
        "top_bottom_rms": tb_rms,
        "top_bottom_max": float(np.max(np.abs(tb))),
        "horizontal_adjacent_rms": dx_rms,
        "vertical_adjacent_rms": dy_rms,
        "left_right_to_adjacent_ratio": lr_rms / max(dx_rms, EPS),
        "top_bottom_to_adjacent_ratio": tb_rms / max(dy_rms, EPS),
        "left_right_excess_rms": max(0.0, lr_rms - dx_rms),
        "top_bottom_excess_rms": max(0.0, tb_rms - dy_rms),
    }


def image_stats(array: np.ndarray) -> dict[str, float]:
    values = np.asarray(array, dtype=np.float32)
    return {
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "p01": float(np.percentile(values, 1)),
        "p50": float(np.percentile(values, 50)),
        "p99": float(np.percentile(values, 99)),
        "near_black_fraction": float(np.mean(values <= 0.01)),
        "near_white_fraction": float(np.mean(values >= 0.99)),
    }


def save_png(array: np.ndarray, path: str | Path, bit_depth: int = 16) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(array, 0.0, 1.0)
    if bit_depth == 8:
        image = Image.fromarray(np.round(clipped * 255.0).astype(np.uint8))
    elif bit_depth == 16:
        image = Image.fromarray(np.round(clipped * 65535.0).astype(np.uint16))
    else:
        raise ValueError("bit_depth must be 8 or 16")
    image.save(output)


def make_preview(array: np.ndarray, path: str | Path, max_dimension: int = 1600) -> None:
    values = np.clip(array, 0.0, 1.0)
    image = Image.fromarray(np.round(values * 255.0).astype(np.uint8))
    if max(image.size) > max_dimension:
        scale = max_dimension / max(image.size)
        image = image.resize(
            (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
            Image.Resampling.LANCZOS,
        )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def save_dat(array: np.ndarray, path: str | Path, depth_scale: float = 1.0) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(output, np.asarray(array, dtype=np.float64) * float(depth_scale), fmt="%.8g")


def save_scad_array(array: np.ndarray, path: str | Path, variable: str = "heightmap") -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for row in np.asarray(array):
        rows.append("  [" + ", ".join(f"{float(value):.8g}" for value in row) + "]")
    output.write_text(f"{variable} = [\n" + ",\n".join(rows) + "\n];\n", encoding="utf-8")


def write_json(value: Any, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
