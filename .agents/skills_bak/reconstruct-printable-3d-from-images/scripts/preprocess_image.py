#!/usr/bin/env python3
"""Create auditable image derivatives for image-to-3D reconstruction.

This script never overwrites the source. Automatic background segmentation is
deliberately simple and must be reviewed before it is used as measurement truth.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def positive(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preserve/normalize a source image and derive masks, edges, and palette."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--background",
        choices=("auto", "alpha", "white", "black", "none"),
        default="auto",
    )
    parser.add_argument(
        "--bg-tolerance",
        type=positive,
        default=32.0,
        help="RGB Euclidean distance used by simple background thresholding.",
    )
    parser.add_argument("--invert-mask", action="store_true")
    parser.add_argument("--padding-fraction", type=float, default=0.06)
    parser.add_argument("--max-side-px", type=int, default=2048)
    parser.add_argument("--palette-colors", type=int, default=8)
    parser.add_argument("--edge-percentile", type=float, default=85.0)
    parser.add_argument("--autocontrast", action="store_true")
    parser.add_argument("--median-size", type=int, choices=(0, 3, 5), default=0)
    parser.add_argument("--unsharp-percent", type=int, default=0)
    parser.add_argument("--target-width-mm", type=positive)
    parser.add_argument("--effective-feature-mm", type=positive)
    parser.add_argument("--samples-per-feature", type=positive, default=3.0)
    return parser.parse_args()


def corner_background(rgb: np.ndarray) -> np.ndarray:
    height, width, _ = rgb.shape
    band = max(2, min(height, width) // 40)
    samples = np.concatenate(
        [
            rgb[:band, :band].reshape(-1, 3),
            rgb[:band, -band:].reshape(-1, 3),
            rgb[-band:, :band].reshape(-1, 3),
            rgb[-band:, -band:].reshape(-1, 3),
        ],
        axis=0,
    )
    return np.median(samples.astype(np.float32), axis=0)


def derive_mask(
    rgba: np.ndarray, method: str, tolerance: float
) -> tuple[np.ndarray, str, list[str]]:
    alpha = rgba[:, :, 3]
    rgb = rgba[:, :, :3].astype(np.float32)
    warnings: list[str] = []

    if method == "none":
        return np.ones(alpha.shape, dtype=bool), "full frame", warnings

    if method in ("alpha", "auto") and np.any(alpha < 250):
        return alpha > 8, "existing alpha channel", warnings

    if method == "alpha":
        warnings.append("The image has no useful transparency; the mask is full frame.")
        return np.ones(alpha.shape, dtype=bool), "opaque alpha fallback", warnings

    if method == "white":
        background = np.array([255.0, 255.0, 255.0], dtype=np.float32)
        label = "white background threshold"
    elif method == "black":
        background = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        label = "black background threshold"
    else:
        background = corner_background(rgba[:, :, :3])
        label = f"corner-color threshold around {background.round(1).tolist()}"
        warnings.append(
            "Automatic background segmentation is a color-distance heuristic. "
            "Review thin parts, holes, shadows, and foreground regions similar to the background."
        )

    distance = np.linalg.norm(rgb - background.reshape(1, 1, 3), axis=2)
    mask = distance > tolerance
    mask_image = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    mask_image = mask_image.filter(ImageFilter.MedianFilter(size=3))
    return np.asarray(mask_image) > 127, label, warnings


def bbox_from_mask(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def padded_square(
    image: Image.Image, mask: Image.Image, padding_fraction: float, max_side: int
) -> tuple[Image.Image, Image.Image, dict[str, int]]:
    bbox = mask.getbbox()
    if bbox is None:
        bbox = (0, 0, image.width, image.height)
    left, top, right, bottom = bbox
    span = max(right - left, bottom - top)
    padding = max(2, int(math.ceil(span * max(padding_fraction, 0.0))))
    side = max(1, span + 2 * padding)
    center_x = (left + right) / 2.0
    center_y = (top + bottom) / 2.0
    crop_box = (
        int(math.floor(center_x - side / 2)),
        int(math.floor(center_y - side / 2)),
        int(math.ceil(center_x + side / 2)),
        int(math.ceil(center_y + side / 2)),
    )

    subject = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    subject_mask = Image.new("L", (side, side), 0)
    src_left = max(crop_box[0], 0)
    src_top = max(crop_box[1], 0)
    src_right = min(crop_box[2], image.width)
    src_bottom = min(crop_box[3], image.height)
    dst_x = src_left - crop_box[0]
    dst_y = src_top - crop_box[1]
    cropped_image = image.crop((src_left, src_top, src_right, src_bottom))
    cropped_mask = mask.crop((src_left, src_top, src_right, src_bottom))
    subject.paste(cropped_image, (dst_x, dst_y), cropped_mask)
    subject_mask.paste(cropped_mask, (dst_x, dst_y))

    if side > max_side:
        new_size = (max_side, max_side)
        subject = subject.resize(new_size, Image.Resampling.LANCZOS)
        subject_mask = subject_mask.resize(new_size, Image.Resampling.NEAREST)

    crop_report = {
        "source_left": crop_box[0],
        "source_top": crop_box[1],
        "source_right": crop_box[2],
        "source_bottom": crop_box[3],
        "output_side_px": subject.width,
    }
    return subject, subject_mask, crop_report


def laplacian_variance(gray: np.ndarray) -> float:
    arr = gray.astype(np.float32) / 255.0
    lap = np.zeros_like(arr)
    lap[1:-1, 1:-1] = (
        -4.0 * arr[1:-1, 1:-1]
        + arr[:-2, 1:-1]
        + arr[2:, 1:-1]
        + arr[1:-1, :-2]
        + arr[1:-1, 2:]
    )
    return float(np.var(lap[1:-1, 1:-1])) if min(arr.shape) > 2 else 0.0


def edge_image(gray: np.ndarray, mask: np.ndarray, percentile: float) -> np.ndarray:
    arr = gray.astype(np.float32)
    grad_y, grad_x = np.gradient(arr)
    magnitude = np.hypot(grad_x, grad_y)
    values = magnitude[mask]
    threshold = float(np.percentile(values, percentile)) if values.size else 255.0
    threshold = max(threshold, 2.0)
    return ((magnitude >= threshold) & mask).astype(np.uint8) * 255


def extract_palette(
    rgb: np.ndarray, mask: np.ndarray, colors: int
) -> list[dict[str, Any]]:
    pixels = rgb[mask]
    if pixels.size == 0:
        return []
    if len(pixels) > 250_000:
        step = math.ceil(len(pixels) / 250_000)
        pixels = pixels[::step]
    strip = Image.fromarray(pixels.reshape(1, -1, 3).astype(np.uint8), mode="RGB")
    quantized = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette() or []
    counts = quantized.getcolors(maxcolors=len(pixels)) or []
    total = sum(count for count, _ in counts) or 1
    result: list[dict[str, Any]] = []
    for count, index in sorted(counts, reverse=True):
        base = index * 3
        color = palette[base : base + 3]
        if len(color) != 3:
            continue
        result.append(
            {
                "rgb": color,
                "hex": "#" + "".join(f"{channel:02X}" for channel in color),
                "fraction": count / total,
            }
        )
    return result


def save_palette_swatch(palette: list[dict[str, Any]], path: Path) -> None:
    if not palette:
        return
    width, row = 640, 72
    swatch = Image.new("RGB", (width, row * len(palette)), "white")
    from PIL import ImageDraw

    draw = ImageDraw.Draw(swatch)
    for index, entry in enumerate(palette):
        y0 = index * row
        color = tuple(entry["rgb"])
        draw.rectangle((0, y0, 180, y0 + row), fill=color)
        draw.text(
            (195, y0 + 24),
            f"{entry['hex']}  {entry['fraction'] * 100:.1f}%",
            fill="black",
        )
    swatch.save(path)


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        raise SystemExit(f"Input image not found: {args.input}")
    if not 0 <= args.padding_fraction <= 1:
        raise SystemExit("--padding-fraction must be between 0 and 1")
    if args.max_side_px <= 0:
        raise SystemExit("--max-side-px must be greater than zero")
    if not 2 <= args.palette_colors <= 32:
        raise SystemExit("--palette-colors must be between 2 and 32")
    if not 0 < args.edge_percentile < 100:
        raise SystemExit("--edge-percentile must be between 0 and 100")
    if args.unsharp_percent < 0:
        raise SystemExit("--unsharp-percent cannot be negative")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(args.input) as opened:
        original_mode = opened.mode
        original_size = opened.size
        exif = opened.getexif()
        normalized = ImageOps.exif_transpose(opened).convert("RGBA")

    normalized.save(args.output_dir / "normalized.png")
    rgba = np.asarray(normalized)
    mask_array, mask_method, warnings = derive_mask(
        rgba, args.background, args.bg_tolerance
    )
    if args.invert_mask:
        mask_array = ~mask_array
        mask_method += " (inverted)"
    mask = Image.fromarray(mask_array.astype(np.uint8) * 255, mode="L")
    mask.save(args.output_dir / "silhouette.png")

    working_rgb = normalized.convert("RGB")
    operations: list[str] = []
    if args.autocontrast:
        working_rgb = ImageOps.autocontrast(working_rgb)
        operations.append("autocontrast")
    if args.median_size:
        working_rgb = working_rgb.filter(ImageFilter.MedianFilter(args.median_size))
        operations.append(f"median_filter_{args.median_size}")
    if args.unsharp_percent > 0:
        working_rgb = working_rgb.filter(
            ImageFilter.UnsharpMask(radius=1.5, percent=args.unsharp_percent, threshold=3)
        )
        operations.append(f"unsharp_{args.unsharp_percent}_percent")
    working_rgb.save(args.output_dir / "processed-rgb.png")

    subject_rgba = working_rgb.convert("RGBA")
    subject_rgba.putalpha(mask)
    subject, subject_mask, crop_report = padded_square(
        subject_rgba, mask, args.padding_fraction, args.max_side_px
    )
    subject.save(args.output_dir / "subject-square.png")
    subject_mask.save(args.output_dir / "subject-square-mask.png")

    gray_image = ImageOps.grayscale(working_rgb)
    gray_image.save(args.output_dir / "grayscale.png")
    gray = np.asarray(gray_image)
    edges = edge_image(gray, mask_array, args.edge_percentile)
    Image.fromarray(edges, mode="L").save(args.output_dir / "edges.png")

    rgb = np.asarray(working_rgb)
    palette = extract_palette(rgb, mask_array, args.palette_colors)
    save_palette_swatch(palette, args.output_dir / "palette.png")

    bbox = bbox_from_mask(mask_array)
    foreground_fraction = float(mask_array.mean())
    touches_border = bool(
        mask_array[0].any()
        or mask_array[-1].any()
        or mask_array[:, 0].any()
        or mask_array[:, -1].any()
    )
    if foreground_fraction < 0.01:
        warnings.append("Foreground mask covers less than 1% of the image.")
    if foreground_fraction > 0.98:
        warnings.append(
            "Foreground mask covers more than 98% of the image; silhouette metrics may be meaningless."
        )
    if touches_border:
        warnings.append("The foreground mask touches the image border; the object may be cropped.")

    gray_subject = gray[mask_array]
    if gray_subject.size:
        p01, p50, p99 = np.percentile(gray_subject, [1, 50, 99]).tolist()
        clipped_black = float(np.mean(gray_subject <= 2))
        clipped_white = float(np.mean(gray_subject >= 253))
    else:
        p01 = p50 = p99 = clipped_black = clipped_white = 0.0

    resolution_hint = None
    if args.target_width_mm and args.effective_feature_mm:
        pitch = args.effective_feature_mm / args.samples_per_feature
        recommended = math.ceil(args.target_width_mm / pitch) + 1
        resolution_hint = {
            "target_width_mm": args.target_width_mm,
            "effective_feature_mm": args.effective_feature_mm,
            "samples_per_feature": args.samples_per_feature,
            "target_pitch_mm": pitch,
            "recommended_width_samples": recommended,
            "source_width_px": normalized.width,
            "source_has_recommended_width_samples": normalized.width >= recommended,
        }
    elif args.target_width_mm or args.effective_feature_mm:
        warnings.append(
            "Both --target-width-mm and --effective-feature-mm are required for a resolution hint."
        )

    report: dict[str, Any] = {
        "source": {
            "path": str(args.input.resolve()),
            "original_mode": original_mode,
            "original_size_px": list(original_size),
            "normalized_size_px": [normalized.width, normalized.height],
            "exif_orientation": exif.get(274),
            "original_was_not_overwritten": True,
        },
        "derivatives": {
            "operations": operations,
            "mask_method": mask_method,
            "mask_bbox_px": list(bbox) if bbox else None,
            "foreground_fraction": foreground_fraction,
            "foreground_touches_border": touches_border,
            "square_crop": crop_report,
        },
        "quality_signals": {
            "grayscale_percentile_01": p01,
            "grayscale_median": p50,
            "grayscale_percentile_99": p99,
            "clipped_black_fraction": clipped_black,
            "clipped_white_fraction": clipped_white,
            "normalized_laplacian_variance": laplacian_variance(gray),
            "edge_pixel_fraction_in_mask": float(np.mean(edges[mask_array] > 0))
            if mask_array.any()
            else 0.0,
            "note": "Signals are diagnostics, not universal pass/fail thresholds.",
        },
        "palette_srgb_observations": palette,
        "resolution_hint": resolution_hint,
        "base_image_memory": {
            "rgba8_mib": normalized.width * normalized.height * 4 / (1024**2),
            "rgb_float32_mib": normalized.width
            * normalized.height
            * 12
            / (1024**2),
        },
        "warnings": warnings,
    }
    report_path = args.output_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
