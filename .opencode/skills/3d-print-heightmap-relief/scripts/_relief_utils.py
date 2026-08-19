#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
import hashlib
import json
import math

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class PitchRecommendation:
    pitch_x_mm: float
    pitch_y_mm: float
    dpi_x: float
    dpi_y: float
    pixel_width: int
    pixel_height: int
    axis_mode: str
    notes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PhysicalFit:
    fit_mode: str
    source_width_mm: float
    source_height_mm: float
    target_width_mm: float
    target_height_mm: float
    placed_width_mm: float
    placed_height_mm: float
    placed_x_mm: float
    placed_y_mm: float
    uniform_scale: float | None
    source_aspect: float
    placed_aspect: float
    physical_aspect_error_pct: float
    aspect_policy: str

    def to_dict(self) -> dict:
        return asdict(self)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def mm_to_dpi(mm_per_pixel: float) -> float:
    if mm_per_pixel <= 0:
        raise ValueError("mm_per_pixel must be > 0")
    return 25.4 / mm_per_pixel


def dpi_to_pitch_mm(ppi: float) -> float:
    if ppi <= 0:
        raise ValueError("ppi must be > 0")
    return 25.4 / ppi


def pixels_for_mm(mm: float, pitch_mm: float) -> int:
    if mm <= 0 or pitch_mm <= 0:
        raise ValueError("mm and pitch_mm must be > 0")
    return max(1, int(round(mm / pitch_mm)))


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def recommend_pitch(
    width_mm: float,
    height_mm: float,
    process: str = "fdm",
    nozzle_mm: float = 0.4,
    layer_height_mm: float = 0.2,
    resin_xy_mm: float = 0.05,
    axis_mode: str = "xy-z",
) -> PitchRecommendation:
    process = process.lower()
    axis_mode = axis_mode.lower()
    notes: list[str] = []

    if process == "fdm":
        pitch_xy = clamp(nozzle_mm * 0.5, 0.06, nozzle_mm * 0.75)
        pitch_z = clamp(layer_height_mm, 0.03, 0.32)
        notes.append(
            f"FDM starting heuristic: pitch_xy=nozzle*0.5={pitch_xy:.4g} mm; "
            f"pitch_z=layer_height={pitch_z:.4g} mm."
        )
    elif process in {"resin", "sla", "msla", "dlp"}:
        pitch_xy = clamp(resin_xy_mm, 0.01, 0.12)
        pitch_z = clamp(layer_height_mm, 0.01, 0.12)
        notes.append(
            f"Resin starting heuristic: pitch_xy≈printer pixel={pitch_xy:.4g} mm; "
            f"pitch_z≈layer height={pitch_z:.4g} mm."
        )
    else:
        raise ValueError("process must be fdm, resin, sla, msla, or dlp")

    if axis_mode == "xy-xy":
        pitch_x = pitch_xy
        pitch_y = pitch_xy
        notes.append("Both image axes map mainly to printed XY.")
    elif axis_mode == "xy-z":
        pitch_x = pitch_xy
        pitch_y = pitch_z
        notes.append("Image X maps mainly to printed XY; image Y maps mainly to model Z.")
    elif axis_mode == "z-xy":
        pitch_x = pitch_z
        pitch_y = pitch_xy
        notes.append("Image X maps mainly to model Z; image Y maps mainly to printed XY.")
    elif axis_mode == "mixed":
        # Keep a conservative isotropic sampling by default for unknown freeform orientation.
        pitch_x = min(pitch_xy, pitch_z)
        pitch_y = min(pitch_xy, pitch_z)
        notes.append("Mixed/freeform mapping uses isotropic conservative sampling by default.")
    else:
        raise ValueError("axis_mode must be xy-xy, xy-z, z-xy, or mixed")

    return PitchRecommendation(
        pitch_x_mm=pitch_x,
        pitch_y_mm=pitch_y,
        dpi_x=mm_to_dpi(pitch_x),
        dpi_y=mm_to_dpi(pitch_y),
        pixel_width=pixels_for_mm(width_mm, pitch_x),
        pixel_height=pixels_for_mm(height_mm, pitch_y),
        axis_mode=axis_mode,
        notes=notes,
    )


def default_aspect_tolerance_pct(image_class: str) -> float:
    c = image_class.lower()
    if c in {"person", "portrait", "animal", "object", "subject", "text", "writing", "logo", "motif", "qr", "symbol"}:
        return 0.75
    if c in {"texture", "pattern", "wood", "carbon", "fabric", "stone"}:
        return 1.5
    return 1.0


def source_physical_size_from_pixels(width_px: int, height_px: int, authoring_ppi: float | None = None) -> tuple[float, float]:
    if width_px <= 0 or height_px <= 0:
        raise ValueError("source dimensions must be > 0")
    if authoring_ppi and authoring_ppi > 0:
        pitch = dpi_to_pitch_mm(authoring_ppi)
        return width_px * pitch, height_px * pitch
    # Unitless square-pixel fallback. Only the aspect matters.
    return float(width_px), float(height_px)


def physical_fit(
    source_size_mm: tuple[float, float],
    target_size_mm: tuple[float, float],
    fit: str,
    aspect_policy: str = "preserve",
    allow_aspect_distortion: bool = False,
) -> PhysicalFit:
    """Fit in physical millimetre space, never in raw raster aspect space.

    contain/cover preserve source physical aspect using one uniform scale.
    stretch is allowed only with an explicit distortion opt-in unless source and target
    aspects already match to floating point tolerance.
    repeat keeps the supplied physical tile size and is handled by the rasterizer.
    """
    sw, sh = source_size_mm
    tw, th = target_size_mm
    for name, val in (("source width", sw), ("source height", sh), ("target width", tw), ("target height", th)):
        if val <= 0 or not math.isfinite(val):
            raise ValueError(f"{name} must be finite and > 0")
    fit = fit.lower()
    aspect_policy = aspect_policy.lower()
    src_aspect = sw / sh
    target_aspect = tw / th

    if fit == "contain":
        scale = min(tw / sw, th / sh)
        pw, ph = sw * scale, sh * scale
        x, y = (tw - pw) / 2.0, (th - ph) / 2.0
    elif fit in {"cover", "crop"}:
        scale = max(tw / sw, th / sh)
        pw, ph = sw * scale, sh * scale
        # Negative placement means physical crop outside the target rectangle.
        x, y = (tw - pw) / 2.0, (th - ph) / 2.0
    elif fit == "stretch":
        scale = None
        pw, ph = tw, th
        x, y = 0.0, 0.0
        error_pct = abs((target_aspect / src_aspect) - 1.0) * 100.0
        if aspect_policy == "preserve" and error_pct > 1e-9 and not allow_aspect_distortion:
            raise ValueError(
                f"stretch would change physical aspect ratio by {error_pct:.3f}% "
                "while aspect_policy=preserve. Use contain/cover/crop or explicitly allow distortion."
            )
    elif fit == "repeat":
        scale = 1.0
        pw, ph = sw, sh
        x, y = 0.0, 0.0
    else:
        raise ValueError("fit must be contain, cover, crop, stretch, or repeat")

    placed_aspect = pw / ph
    error_pct = abs((placed_aspect / src_aspect) - 1.0) * 100.0
    return PhysicalFit(
        fit_mode=fit,
        source_width_mm=sw,
        source_height_mm=sh,
        target_width_mm=tw,
        target_height_mm=th,
        placed_width_mm=pw,
        placed_height_mm=ph,
        placed_x_mm=x,
        placed_y_mm=y,
        uniform_scale=scale,
        source_aspect=src_aspect,
        placed_aspect=placed_aspect,
        physical_aspect_error_pct=error_pct,
        aspect_policy=aspect_policy,
    )


def load_grayscale_float(path: str | Path, background: int = 65535) -> tuple[np.ndarray, dict]:
    """Load a raster as float32 luminance in [0,1] without deliberate quantization."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(p)
    with Image.open(p) as im:
        im.load()
        info = {
            "source_mode": im.mode,
            "source_size_px": [im.width, im.height],
            "embedded_dpi": list(im.info.get("dpi", [])) if im.info.get("dpi") else None,
        }
        if im.mode.startswith("I;16"):
            arr = np.asarray(im, dtype=np.uint16).astype(np.float32) / 65535.0
            info["source_bit_depth_guess"] = 16
            return arr, info
        if im.mode == "L":
            arr = np.asarray(im, dtype=np.uint8).astype(np.float32) / 255.0
            info["source_bit_depth_guess"] = 8
            return arr, info
        if im.mode == "I":
            raw = np.asarray(im, dtype=np.int64)
            maxv = int(raw.max()) if raw.size else 0
            denom = 65535.0 if maxv <= 65535 else float(max(1, maxv))
            info["source_bit_depth_guess"] = 16 if maxv > 255 else 8
            return np.clip(raw.astype(np.float32) / denom, 0.0, 1.0), info

        rgba = np.asarray(im.convert("RGBA"), dtype=np.float32) / 255.0
        bg = clamp(background / 65535.0, 0.0, 1.0)
        rgb = rgba[..., :3]
        alpha = rgba[..., 3:4]
        comp = rgb * alpha + bg * (1.0 - alpha)
        gray = comp[..., 0] * 0.2126 + comp[..., 1] * 0.7152 + comp[..., 2] * 0.0722
        info["source_bit_depth_guess"] = 8
        return gray.astype(np.float32), info


def resize_float(arr: np.ndarray, size_px: tuple[int, int], resample: str = "lanczos") -> np.ndarray:
    w, h = map(int, size_px)
    if w < 1 or h < 1:
        raise ValueError("target raster dimensions must be positive")
    filters = {
        "nearest": Image.Resampling.NEAREST,
        "bilinear": Image.Resampling.BILINEAR,
        "bicubic": Image.Resampling.BICUBIC,
        "lanczos": Image.Resampling.LANCZOS,
    }
    if resample not in filters:
        raise ValueError(f"unknown resample filter: {resample}")
    im = Image.fromarray(np.asarray(arr, dtype=np.float32), mode="F")
    out = im.resize((w, h), resample=filters[resample])
    return np.asarray(out, dtype=np.float32)


def apply_levels_gamma(arr: np.ndarray, black: float = 0.0, white: float = 1.0, gamma: float = 1.0, invert: bool = False) -> np.ndarray:
    if white <= black:
        raise ValueError("white must be greater than black")
    if gamma <= 0:
        raise ValueError("gamma must be > 0")
    out = np.clip((np.asarray(arr, dtype=np.float32) - black) / (white - black), 0.0, 1.0)
    if invert:
        out = 1.0 - out
    if gamma != 1.0:
        out = np.power(out, gamma, dtype=np.float32)
    return np.clip(out, 0.0, 1.0).astype(np.float32)


def rasterize_physical_fit(
    arr: np.ndarray,
    source_size_mm: tuple[float, float],
    target_size_mm: tuple[float, float],
    pitch_mm: tuple[float, float],
    fit: str,
    background_value: float = 0.0,
    aspect_policy: str = "preserve",
    allow_aspect_distortion: bool = False,
    repeat_tile_size_mm: tuple[float, float] | None = None,
    resample: str = "lanczos",
) -> tuple[np.ndarray, dict]:
    """Rasterize by physical coordinates, preserving physical—not pixel—aspect ratio."""
    tw, th = target_size_mm
    px, py = pitch_mm
    target_w_px = pixels_for_mm(tw, px)
    target_h_px = pixels_for_mm(th, py)
    bg = float(clamp(background_value, 0.0, 1.0))

    if fit == "repeat":
        tile_size_mm = repeat_tile_size_mm or source_size_mm
        source_aspect = source_size_mm[0] / source_size_mm[1]
        tile_aspect = tile_size_mm[0] / tile_size_mm[1]
        tile_aspect_error_pct = abs(tile_aspect / source_aspect - 1.0) * 100.0
        if tile_aspect_error_pct > 1e-9 and aspect_policy == "preserve" and not allow_aspect_distortion:
            raise ValueError(
                f"repeat tile size would change physical tile aspect by {tile_aspect_error_pct:.3f}%. "
                "Change repeat count/tile scale uniformly or explicitly allow aspect distortion."
            )
        tile_w_px = pixels_for_mm(tile_size_mm[0], px)
        tile_h_px = pixels_for_mm(tile_size_mm[1], py)
        tile = resize_float(arr, (tile_w_px, tile_h_px), resample=resample)
        reps_x = max(1, math.ceil(target_w_px / tile_w_px))
        reps_y = max(1, math.ceil(target_h_px / tile_h_px))
        out = np.tile(tile, (reps_y, reps_x))[:target_h_px, :target_w_px].astype(np.float32)
        fit_info = physical_fit(tile_size_mm, target_size_mm, "repeat", aspect_policy, allow_aspect_distortion).to_dict()
        fit_info.update({
            "tile_width_px": tile_w_px,
            "tile_height_px": tile_h_px,
            "repeat_counts": [reps_x, reps_y],
            "source_tile_aspect": source_aspect,
            "requested_tile_aspect": tile_aspect,
            "tile_aspect_error_pct": tile_aspect_error_pct,
        })
        return out, fit_info

    pf = physical_fit(source_size_mm, target_size_mm, fit, aspect_policy, allow_aspect_distortion)
    placed_w_px = max(1, int(round(pf.placed_width_mm / px)))
    placed_h_px = max(1, int(round(pf.placed_height_mm / py)))
    resized = resize_float(arr, (placed_w_px, placed_h_px), resample=resample)
    out = np.full((target_h_px, target_w_px), bg, dtype=np.float32)

    # Convert physical placement offset to raster position. Negative values mean crop.
    x0 = int(round(pf.placed_x_mm / px))
    y0 = int(round(pf.placed_y_mm / py))

    src_x0 = max(0, -x0)
    src_y0 = max(0, -y0)
    dst_x0 = max(0, x0)
    dst_y0 = max(0, y0)
    copy_w = min(target_w_px - dst_x0, placed_w_px - src_x0)
    copy_h = min(target_h_px - dst_y0, placed_h_px - src_y0)
    if copy_w > 0 and copy_h > 0:
        out[dst_y0:dst_y0 + copy_h, dst_x0:dst_x0 + copy_w] = resized[src_y0:src_y0 + copy_h, src_x0:src_x0 + copy_w]

    info = pf.to_dict()
    info.update({
        "target_pixel_width": target_w_px,
        "target_pixel_height": target_h_px,
        "placed_pixel_width": placed_w_px,
        "placed_pixel_height": placed_h_px,
        "placed_pixel_x": x0,
        "placed_pixel_y": y0,
        "raster_pixel_aspect": placed_w_px / placed_h_px,
        "physical_pixel_aspect": px / py,
        "reconstructed_physical_aspect": (placed_w_px * px) / (placed_h_px * py),
    })
    info["rasterization_aspect_error_pct"] = abs(
        (info["reconstructed_physical_aspect"] / pf.source_aspect) - 1.0
    ) * 100.0
    return out, info


def save_16bit_png(arr: np.ndarray, path: str | Path, dpi_x: float | None = None, dpi_y: float | None = None) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    u16 = np.clip(np.round(np.asarray(arr, dtype=np.float32) * 65535.0), 0, 65535).astype(np.uint16)
    im = Image.fromarray(u16)
    kwargs = {}
    if dpi_x and dpi_y:
        kwargs["dpi"] = (float(dpi_x), float(dpi_y))
    im.save(p, **kwargs)


def save_square_pixel_preview(arr: np.ndarray, path: str | Path, target_size_mm: tuple[float, float], preview_ppi: float = 150.0) -> dict:
    """Create a human-viewing preview with square pixels and the intended physical aspect.

    Never use this preview as geometry input.
    """
    w_mm, h_mm = target_size_mm
    pitch = dpi_to_pitch_mm(preview_ppi)
    w = pixels_for_mm(w_mm, pitch)
    h = pixels_for_mm(h_mm, pitch)
    preview = resize_float(arr, (w, h), resample="lanczos")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(np.clip(np.round(preview * 255.0), 0, 255).astype(np.uint8), mode="L")
    im.save(p, dpi=(preview_ppi, preview_ppi))
    return {"preview_path": str(p), "preview_width_px": w, "preview_height_px": h, "preview_ppi": preview_ppi}


def sidecar_path(path: str | Path, suffix: str = ".json") -> Path:
    p = Path(path)
    return p.with_suffix(p.suffix + suffix)


def write_json(path: str | Path, data: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def natural_aspect_from_source_info(source_manifest: dict | None, source_size_px: tuple[int, int]) -> tuple[float, tuple[float, float]]:
    """Return canonical source aspect and a physical-size proxy.

    Prefer authoring physical dimensions from a source manifest. Fall back to square-pixel
    source aspect using pixel dimensions.
    """
    if source_manifest:
        physical = source_manifest.get("physical") or source_manifest.get("authoring") or {}
        w = physical.get("width_mm") or physical.get("authoring_width_mm")
        h = physical.get("height_mm") or physical.get("authoring_height_mm")
        if w and h and float(w) > 0 and float(h) > 0:
            return float(w) / float(h), (float(w), float(h))
    wpx, hpx = source_size_px
    return wpx / hpx, (float(wpx), float(hpx))


def resize_quality_warnings(source_size_px: tuple[int, int], placed_size_px: tuple[int, int], image_class: str) -> list[str]:
    sw, sh = source_size_px
    pw, ph = placed_size_px
    sx = pw / sw
    sy = ph / sh
    scale = max(sx, sy)
    warnings: list[str] = []
    if scale > 2.0:
        warnings.append("Source is enlarged by more than 200% in at least one raster axis; obtain a larger source or reduce placement size.")
    elif scale > 1.5:
        warnings.append("Source is enlarged by more than 150%; inspect fine detail carefully.")
    elif scale > 1.25:
        warnings.append("Source is enlarged by more than 125%; verify that the source still oversamples printable detail.")
    if image_class.lower() not in {"texture", "pattern", "wood", "carbon", "fabric", "stone"} and abs(sx - sy) > 0.01:
        # This difference is expected when target physical pixels are anisotropic, so warn only
        # that raw raster scale is not meaningful; physical aspect validation is authoritative.
        warnings.append("X/Y raster scale factors differ. This is acceptable only because physical pixel pitches differ; use physical-aspect validation, not raw pixel aspect.")
    return warnings


def recommended_depth_range(image_class: str, mode: str) -> tuple[tuple[float, float], str]:
    c = image_class.lower()
    mode = mode.lower()
    if c in {"texture", "pattern", "wood", "carbon", "fabric", "stone"}:
        return ((0.10, 0.35) if mode == "engrave" else (0.20, 0.50), "Texture starting range")
    if c in {"text", "writing", "logo", "motif", "symbol"}:
        return ((0.30, 0.80) if mode == "engrave" else (0.50, 1.20), "Text/logo starting range")
    if c in {"object", "person", "animal", "portrait", "photo", "subject"}:
        return ((0.30, 0.90) if mode == "engrave" else (0.60, 1.50), "Single-subject starting range")
    return ((0.20, 0.60) if mode == "engrave" else (0.50, 1.00), "General starting range")


def minimum_remaining_wall(nozzle_mm: float) -> float:
    return max(1.2, 3.0 * nozzle_mm)
