#!/usr/bin/env python3
"""Prepare a grayscale height map at a physically justified resolution.

Supports stretching, center-cropping, containing with padding, and repeating a
texture. Outputs 8-bit or 16-bit PNG and reports the implied mesh size.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def load_float(path: Path) -> Image.Image:
    with Image.open(path) as image:
        # Convert through luminance; preserve useful precision in a float image.
        if image.mode in {"I;16", "I;16B", "I;16L", "I", "F"}:
            arr = np.asarray(image, dtype=np.float64)
            finite = arr[np.isfinite(arr)]
            if finite.size == 0:
                raise ValueError("Input image contains no finite values.")
            lo, hi = float(finite.min()), float(finite.max())
            if hi <= lo:
                arr = np.zeros_like(arr, dtype=np.float32)
            else:
                arr = ((arr - lo) / (hi - lo)).astype(np.float32)
        else:
            rgb = image.convert("RGB")
            arr_rgb = np.asarray(rgb, dtype=np.float32) / 255.0
            # Linear luminance weights as a deterministic grayscale conversion.
            arr = (0.2126 * arr_rgb[..., 0] + 0.7152 * arr_rgb[..., 1] + 0.0722 * arr_rgb[..., 2]).astype(np.float32)
    return Image.fromarray(arr)


def resize_float(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return image.resize(size, resample=Image.Resampling.LANCZOS)


def fit_geometry(image: Image.Image, target: tuple[int, int], mode: str, tile_count: tuple[int, int], background: float) -> Image.Image:
    tw, th = target
    iw, ih = image.size
    if mode == "stretch":
        return resize_float(image, target)

    if mode == "crop":
        scale = max(tw / iw, th / ih)
        resized = resize_float(image, (max(1, round(iw * scale)), max(1, round(ih * scale))))
        left = (resized.width - tw) // 2
        top = (resized.height - th) // 2
        return resized.crop((left, top, left + tw, top + th))

    if mode == "contain":
        scale = min(tw / iw, th / ih)
        resized = resize_float(image, (max(1, round(iw * scale)), max(1, round(ih * scale))))
        canvas = Image.new("F", target, float(background))
        canvas.paste(resized, ((tw - resized.width) // 2, (th - resized.height) // 2))
        return canvas

    if mode == "tile":
        tx, ty = tile_count
        if tx < 1 or ty < 1:
            raise ValueError("Tile counts must be positive integers.")
        tile_w = max(1, math.ceil(tw / tx))
        tile_h = max(1, math.ceil(th / ty))
        tile = resize_float(image, (tile_w, tile_h))
        canvas = Image.new("F", target, float(background))
        for y in range(0, th, tile_h):
            for x in range(0, tw, tile_w):
                canvas.paste(tile, (x, y))
        return canvas.crop((0, 0, tw, th))

    raise ValueError(f"Unknown mode: {mode}")


def process_values(image: Image.Image, low_pct: float, high_pct: float, gamma: float, contrast: float, invert: bool, blur: float) -> np.ndarray:
    if blur > 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=blur))
    arr = np.asarray(image, dtype=np.float32)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        raise ValueError("Processed image contains no finite pixels.")
    if not 0 <= low_pct < high_pct <= 100:
        raise ValueError("Percentiles must satisfy 0 <= low < high <= 100.")
    lo, hi = np.percentile(finite, [low_pct, high_pct])
    if hi <= lo:
        arr = np.zeros_like(arr)
    else:
        arr = np.clip((arr - lo) / (hi - lo), 0.0, 1.0)
    if gamma <= 0:
        raise ValueError("Gamma must be positive.")
    arr = np.power(arr, gamma, dtype=np.float32)
    if contrast <= 0:
        raise ValueError("Contrast must be positive.")
    arr = np.clip((arr - 0.5) * contrast + 0.5, 0.0, 1.0)
    if invert:
        arr = 1.0 - arr
    return arr


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--physical-size-mm", nargs=2, type=float, metavar=("W", "H"), help="Physical relief size")
    parser.add_argument("--sample-pitch-mm", type=float, help="Desired sample spacing; use with physical size")
    parser.add_argument("--pixels", nargs=2, type=int, metavar=("W", "H"), help="Explicit output dimensions")
    parser.add_argument("--mode", choices=("stretch", "crop", "contain", "tile"), default="crop")
    parser.add_argument("--tile-count", nargs=2, type=int, default=(1, 1), metavar=("X", "Y"))
    parser.add_argument("--background", type=float, default=0.5, help="Padding value for contain mode, 0..1")
    parser.add_argument("--invert", action="store_true")
    parser.add_argument("--gamma", type=float, default=1.0)
    parser.add_argument("--contrast", type=float, default=1.0)
    parser.add_argument("--blur-radius", type=float, default=0.0, help="Gaussian blur in output pixels")
    parser.add_argument("--low-percentile", type=float, default=0.5)
    parser.add_argument("--high-percentile", type=float, default=99.5)
    parser.add_argument("--bit-depth", type=int, choices=(8, 16), default=16)
    parser.add_argument("--report", type=Path, help="Write JSON processing report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        inp = args.input.expanduser().resolve()
        out = args.output.expanduser().resolve()
        if not inp.is_file():
            raise FileNotFoundError(inp)

        derived: tuple[int, int] | None = None
        if args.physical_size_mm or args.sample_pitch_mm:
            if not (args.physical_size_mm and args.sample_pitch_mm):
                raise ValueError("Use --physical-size-mm and --sample-pitch-mm together.")
            if any(v <= 0 for v in args.physical_size_mm) or args.sample_pitch_mm <= 0:
                raise ValueError("Physical size and sample pitch must be positive.")
            derived = tuple(math.ceil(v / args.sample_pitch_mm) + 1 for v in args.physical_size_mm)

        explicit = tuple(args.pixels) if args.pixels else None
        if explicit and any(v < 2 for v in explicit):
            raise ValueError("Output dimensions must be at least 2 × 2.")
        if explicit and derived and explicit != derived:
            raise ValueError(f"--pixels {explicit} conflicts with physically derived size {derived}.")
        target = explicit or derived
        if target is None:
            raise ValueError("Provide --pixels or both --physical-size-mm and --sample-pitch-mm.")
        if not 0.0 <= args.background <= 1.0:
            raise ValueError("--background must be between 0 and 1.")

        source = load_float(inp)
        fitted = fit_geometry(source, target, args.mode, tuple(args.tile_count), args.background)
        values = process_values(
            fitted, args.low_percentile, args.high_percentile,
            args.gamma, args.contrast, args.invert, args.blur_radius
        )
        if args.bit_depth == 16:
            encoded = np.round(values * 65535.0).astype(np.uint16)
            image_out = Image.fromarray(encoded)
        else:
            encoded = np.round(values * 255.0).astype(np.uint8)
            image_out = Image.fromarray(encoded)

        out.parent.mkdir(parents=True, exist_ok=True)
        image_out.save(out, format="PNG")
        triangles = 2 * (target[0] - 1) * (target[1] - 1)
        report = {
            "input": str(inp),
            "output": str(out),
            "input_pixels": list(source.size),
            "output_pixels": list(target),
            "mode": args.mode,
            "tile_count": list(args.tile_count),
            "bit_depth": args.bit_depth,
            "gamma": args.gamma,
            "contrast": args.contrast,
            "invert": args.invert,
            "blur_radius_pixels": args.blur_radius,
            "normalization_percentiles": [args.low_percentile, args.high_percentile],
            "physical_size_mm": list(args.physical_size_mm) if args.physical_size_mm else None,
            "sample_pitch_mm": args.sample_pitch_mm,
            "approx_heightfield_triangles": triangles,
            "note": "Use a transfer coupon; source pixels beyond printer/casting capability do not add physical detail."
        }
        if args.report:
            rp = args.report.expanduser().resolve()
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
