#!/usr/bin/env python3
"""Preprocess an image into a physically sampled printable height map."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np

from heightmap_common import (
    apply_blur_mm,
    apply_contrast,
    apply_gamma,
    apply_highpass_mm,
    apply_soft_threshold,
    apply_unsharp_mm,
    blend_periodic_edges,
    image_stats,
    load_image_float,
    make_preview,
    parse_pair,
    percentile_levels,
    resize_fit,
    save_dat,
    save_png,
    save_scad_array,
    seam_metrics,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert an image into a normalized height map with physical-size-aware "
            "resampling, levels, gamma, filtering, seam blending, and reports."
        )
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, help="Output PNG")
    parser.add_argument("--physical-width-mm", type=float)
    parser.add_argument("--physical-height-mm", type=float)
    parser.add_argument("--sample-pitch-mm", type=float)
    parser.add_argument("--target-px", help="Explicit WIDTHxHEIGHT; overrides sample-pitch dimensions")
    parser.add_argument("--fit", choices=("stretch", "cover", "contain", "tile"), default="stretch")
    parser.add_argument("--repeat-x", type=float, default=1.0)
    parser.add_argument("--repeat-y", type=float, default=1.0)
    parser.add_argument("--pad-level", type=float, default=0.0)
    parser.add_argument(
        "--grayscale",
        choices=("luma", "average", "max", "min", "red", "green", "blue", "alpha"),
        default="luma",
    )
    parser.add_argument(
        "--alpha-mode",
        choices=("base", "black", "white", "multiply", "ignore"),
        default="base",
    )
    parser.add_argument("--base-level", type=float, default=0.0)
    parser.add_argument("--luma-space", choices=("srgb", "linear"), default="srgb")
    parser.add_argument("--invert", action="store_true")
    parser.add_argument("--rotate", type=int, choices=(0, 90, 180, 270), default=0)
    parser.add_argument("--flip-x", action="store_true")
    parser.add_argument("--flip-y", action="store_true")
    parser.add_argument("--levels", default="0,100", help="Percentiles LOW,HIGH, e.g. 1,99")
    parser.add_argument("--gamma", type=float, default=1.0)
    parser.add_argument("--contrast", type=float, default=1.0)
    parser.add_argument("--blur-mm", type=float, default=0.0)
    parser.add_argument("--unsharp-radius-mm", type=float, default=0.0)
    parser.add_argument("--unsharp-amount", type=float, default=0.0)
    parser.add_argument("--highpass-radius-mm", type=float, default=0.0)
    parser.add_argument("--highpass-amount", type=float, default=0.0)
    parser.add_argument("--threshold", type=float)
    parser.add_argument("--threshold-softness", type=float, default=0.0)
    parser.add_argument("--seam-blend-mm", default="0,0", help="X,Y physical blend widths")
    parser.add_argument("--bit-depth", type=int, choices=(8, 16), default=16)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--npy-output", type=Path)
    parser.add_argument("--dat-output", type=Path)
    parser.add_argument("--dat-depth-scale", type=float, default=1.0)
    parser.add_argument("--scad-output", type=Path)
    parser.add_argument("--scad-variable", default="heightmap")
    return parser


def resolve_target(
    source_shape: tuple[int, int],
    target_text: str | None,
    physical_width: float | None,
    physical_height: float | None,
    sample_pitch: float | None,
) -> tuple[int, int, float, float, float, float, list[str]]:
    src_h, src_w = source_shape
    warnings: list[str] = []
    if physical_width is not None and physical_width <= 0:
        raise ValueError("physical-width-mm must be positive")
    if physical_height is not None and physical_height <= 0:
        raise ValueError("physical-height-mm must be positive")
    if physical_width is None and physical_height is not None:
        physical_width = physical_height * src_w / max(src_h, 1)
    if physical_height is None and physical_width is not None:
        physical_height = physical_width * src_h / max(src_w, 1)

    if target_text:
        target_width, target_height = parse_pair(target_text, cast=int)
        if target_width < 2 or target_height < 2:
            raise ValueError("target-px dimensions must both be at least 2")
    elif sample_pitch is not None:
        if sample_pitch <= 0:
            raise ValueError("sample-pitch-mm must be positive")
        if physical_width is None or physical_height is None:
            raise ValueError("sample-pitch-mm requires physical width and height")
        target_width = max(2, int(math.ceil(physical_width / sample_pitch)) + 1)
        target_height = max(2, int(math.ceil(physical_height / sample_pitch)) + 1)
    else:
        target_width, target_height = src_w, src_h

    if physical_width is None:
        physical_width = float(max(1, target_width - 1))
        warnings.append("No physical width supplied; millimetre filters are interpreted as pixels.")
    if physical_height is None:
        physical_height = float(max(1, target_height - 1))
        warnings.append("No physical height supplied; millimetre filters are interpreted as pixels.")

    pitch_x = physical_width / max(1, target_width - 1)
    pitch_y = physical_height / max(1, target_height - 1)
    return (
        target_width,
        target_height,
        float(physical_width),
        float(physical_height),
        pitch_x,
        pitch_y,
        warnings,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    heightmap, metadata = load_image_float(
        args.input,
        grayscale=args.grayscale,
        alpha_mode=args.alpha_mode,
        luma_space=args.luma_space,
        base_level=args.base_level,
    )
    original_shape = heightmap.shape
    original_stats = image_stats(heightmap)
    original_seams = seam_metrics(heightmap)

    if args.rotate:
        # np.rot90 is CCW; the CLI uses conventional clockwise image rotation.
        heightmap = np.rot90(heightmap, k=(4 - args.rotate // 90) % 4)
    if args.flip_x:
        heightmap = np.fliplr(heightmap)
    if args.flip_y:
        heightmap = np.flipud(heightmap)

    (
        target_width,
        target_height,
        physical_width,
        physical_height,
        pitch_x,
        pitch_y,
        warnings,
    ) = resolve_target(
        heightmap.shape,
        args.target_px,
        args.physical_width_mm,
        args.physical_height_mm,
        args.sample_pitch_mm,
    )

    heightmap = resize_fit(
        heightmap,
        target_width,
        target_height,
        fit=args.fit,
        pad_level=args.pad_level,
        repeat_x=args.repeat_x,
        repeat_y=args.repeat_y,
    )

    low_percent, high_percent = parse_pair(args.levels, cast=float)
    heightmap, actual_low, actual_high = percentile_levels(
        heightmap, low_percent, high_percent
    )
    if args.invert:
        heightmap = 1.0 - heightmap
    if args.gamma != 1.0:
        heightmap = apply_gamma(heightmap, args.gamma)
    if args.contrast != 1.0:
        heightmap = apply_contrast(heightmap, args.contrast)
    if args.blur_mm > 0:
        heightmap = apply_blur_mm(heightmap, args.blur_mm, pitch_x, pitch_y)
    if args.highpass_radius_mm > 0 and args.highpass_amount != 0:
        heightmap = apply_highpass_mm(
            heightmap,
            args.highpass_radius_mm,
            args.highpass_amount,
            pitch_x,
            pitch_y,
        )
    if args.unsharp_radius_mm > 0 and args.unsharp_amount != 0:
        heightmap = apply_unsharp_mm(
            heightmap,
            args.unsharp_radius_mm,
            args.unsharp_amount,
            pitch_x,
            pitch_y,
        )
    if args.threshold is not None:
        heightmap = apply_soft_threshold(
            heightmap, args.threshold, args.threshold_softness
        )

    seam_x_mm, seam_y_mm = parse_pair(args.seam_blend_mm, cast=float)
    if seam_x_mm < 0 or seam_y_mm < 0:
        raise ValueError("seam-blend-mm values cannot be negative")
    blend_x_px = int(round(seam_x_mm / max(pitch_x, 1.0e-9)))
    blend_y_px = int(round(seam_y_mm / max(pitch_y, 1.0e-9)))
    if blend_x_px or blend_y_px:
        heightmap = blend_periodic_edges(heightmap, blend_x_px, blend_y_px)

    save_png(heightmap, args.output, args.bit_depth)
    if args.preview:
        make_preview(heightmap, args.preview)
    if args.npy_output:
        args.npy_output.parent.mkdir(parents=True, exist_ok=True)
        np.save(args.npy_output, heightmap.astype(np.float32))
    if args.dat_output:
        save_dat(heightmap, args.dat_output, args.dat_depth_scale)
    if args.scad_output:
        save_scad_array(heightmap, args.scad_output, args.scad_variable)

    report = {
        "input": str(args.input),
        "output": str(args.output),
        "source_metadata": metadata,
        "source_shape_yx": [int(original_shape[0]), int(original_shape[1])],
        "source_stats": original_stats,
        "source_seams": original_seams,
        "physical_width_mm": physical_width,
        "physical_height_mm": physical_height,
        "target_width_px": target_width,
        "target_height_px": target_height,
        "actual_pitch_x_mm": pitch_x,
        "actual_pitch_y_mm": pitch_y,
        "fit": args.fit,
        "repeat_x": args.repeat_x,
        "repeat_y": args.repeat_y,
        "orientation": {
            "rotate_clockwise_deg": args.rotate,
            "flip_x": args.flip_x,
            "flip_y": args.flip_y,
            "invert": args.invert,
        },
        "levels": {
            "requested_percentiles": [low_percent, high_percent],
            "actual_values": [actual_low, actual_high],
        },
        "filters": {
            "gamma": args.gamma,
            "contrast": args.contrast,
            "blur_mm": args.blur_mm,
            "unsharp_radius_mm": args.unsharp_radius_mm,
            "unsharp_amount": args.unsharp_amount,
            "highpass_radius_mm": args.highpass_radius_mm,
            "highpass_amount": args.highpass_amount,
            "threshold": args.threshold,
            "threshold_softness": args.threshold_softness,
            "seam_blend_mm": [seam_x_mm, seam_y_mm],
            "seam_blend_px": [blend_x_px, blend_y_px],
        },
        "output_bit_depth": args.bit_depth,
        "output_stats": image_stats(heightmap),
        "output_seams": seam_metrics(heightmap),
        "warnings": warnings,
    }
    if args.report:
        write_json(report, args.report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
