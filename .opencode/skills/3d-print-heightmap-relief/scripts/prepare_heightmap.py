#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _relief_utils import (
    apply_levels_gamma,
    default_aspect_tolerance_pct,
    load_grayscale_float,
    natural_aspect_from_source_info,
    rasterize_physical_fit,
    read_json,
    recommend_pitch,
    resize_quality_warnings,
    save_16bit_png,
    save_square_pixel_preview,
    sidecar_path,
    write_json,
)


def pair(text: str) -> tuple[float, float]:
    for sep in ("x", ",", ";"):
        if sep in text:
            a, b = text.split(sep, 1)
            return float(a), float(b)
    raise argparse.ArgumentTypeError("expected pair like 80x40")


def main() -> int:
    p = argparse.ArgumentParser(description="Prepare a 16-bit target heightmap while preserving PHYSICAL aspect ratio.")
    p.add_argument("input_image")
    p.add_argument("output_png")
    p.add_argument("--size-mm", required=True, type=pair, help="Target surface patch width x height in mm")
    p.add_argument("--source-size-mm", type=pair, help="Source master's intended physical width x height. If omitted, read source manifest or assume square source pixels.")
    p.add_argument("--source-manifest", help="Optional registered source-master manifest JSON")
    p.add_argument("--pitch-mm", type=pair, help="Explicit target X/Y mm per pixel")
    p.add_argument("--process", default="fdm", choices=["fdm", "resin", "sla", "msla", "dlp"])
    p.add_argument("--nozzle-mm", type=float, default=0.4)
    p.add_argument("--layer-height-mm", type=float, default=0.2)
    p.add_argument("--resin-xy-mm", type=float, default=0.05)
    p.add_argument("--axis-mode", default="xy-z", choices=["xy-xy", "xy-z", "z-xy", "mixed"])
    p.add_argument("--fit", default="contain", choices=["contain", "cover", "crop", "stretch", "repeat"])
    p.add_argument("--tile-mm", type=pair, help="Physical repeat tile size for repeat mode")
    p.add_argument("--image-class", default="subject")
    p.add_argument("--surface-type", default="plane")
    p.add_argument("--placement-mode", default="single_patch")
    p.add_argument("--aspect-policy", default="preserve", choices=["preserve", "allow-distortion"])
    p.add_argument("--allow-aspect-distortion", action="store_true", help="Explicit opt-in for anisotropic physical stretching")
    p.add_argument("--aspect-tolerance-pct", type=float, help="Fail if reconstructed physical aspect exceeds this error")
    p.add_argument("--black-point", type=float, default=0.0)
    p.add_argument("--white-point", type=float, default=1.0)
    p.add_argument("--gamma", type=float, default=1.0)
    p.add_argument("--invert", action="store_true")
    p.add_argument("--background", type=float, default=0.0, help="Normalized contain padding/background, 0..1")
    p.add_argument("--preview", help="Optional square-pixel preview path; never use as geometry input")
    p.add_argument("--preview-ppi", type=float, default=150.0)
    args = p.parse_args()

    target_w_mm, target_h_mm = args.size_mm
    arr, src_info = load_grayscale_float(args.input_image)
    src_h_px, src_w_px = arr.shape

    src_manifest = read_json(args.source_manifest) if args.source_manifest else None
    if args.source_size_mm:
        src_w_mm, src_h_mm = args.source_size_mm
        source_aspect_origin = "explicit --source-size-mm"
    else:
        _, (src_w_mm, src_h_mm) = natural_aspect_from_source_info(src_manifest, (src_w_px, src_h_px))
        source_aspect_origin = "source manifest" if src_manifest else "source square-pixel aspect fallback"

    if args.pitch_mm:
        pitch_x, pitch_y = args.pitch_mm
        pitch_note = ["Explicit target pitch supplied."]
        dpi_x, dpi_y = 25.4 / pitch_x, 25.4 / pitch_y
    else:
        rec = recommend_pitch(target_w_mm, target_h_mm, args.process, args.nozzle_mm, args.layer_height_mm, args.resin_xy_mm, args.axis_mode)
        pitch_x, pitch_y = rec.pitch_x_mm, rec.pitch_y_mm
        dpi_x, dpi_y = rec.dpi_x, rec.dpi_y
        pitch_note = rec.notes

    allow_distortion = args.allow_aspect_distortion or args.aspect_policy == "allow-distortion"
    built, fit = rasterize_physical_fit(
        arr,
        source_size_mm=(src_w_mm, src_h_mm),
        target_size_mm=(target_w_mm, target_h_mm),
        pitch_mm=(pitch_x, pitch_y),
        fit=args.fit,
        background_value=args.background,
        aspect_policy=args.aspect_policy,
        allow_aspect_distortion=allow_distortion,
        repeat_tile_size_mm=args.tile_mm,
    )
    built = apply_levels_gamma(built, args.black_point, args.white_point, args.gamma, args.invert)

    tolerance = args.aspect_tolerance_pct if args.aspect_tolerance_pct is not None else default_aspect_tolerance_pct(args.image_class)
    aspect_error = float(fit.get("rasterization_aspect_error_pct", fit.get("physical_aspect_error_pct", 0.0)))
    if args.fit != "repeat" and not allow_distortion and aspect_error > tolerance:
        raise SystemExit(
            f"Physical aspect validation failed: {aspect_error:.4f}% error exceeds {tolerance:.4f}% tolerance. "
            "Do not continue to geometry generation."
        )

    save_16bit_png(built, args.output_png, dpi_x, dpi_y)
    preview_meta = None
    if args.preview:
        preview_meta = save_square_pixel_preview(built, args.preview, (target_w_mm, target_h_mm), args.preview_ppi)

    placed_px = (int(fit.get("placed_pixel_width", built.shape[1])), int(fit.get("placed_pixel_height", built.shape[0])))
    warnings = list(pitch_note)
    warnings += resize_quality_warnings((src_w_px, src_h_px), placed_px, args.image_class)
    if args.fit == "stretch" and allow_distortion:
        warnings.append("Physical aspect distortion was explicitly allowed; verify the subject visually before geometry generation.")
    if abs(pitch_x - pitch_y) > 1e-9:
        warnings.append("Geometry raster uses non-square physical pixels. A normal image viewer may look distorted; inspect the square-pixel preview instead.")

    meta = {
        "schema": "heightmap-relief-build-v2.2",
        "source": {
            "path": str(Path(args.input_image)),
            "manifest": str(Path(args.source_manifest)) if args.source_manifest else None,
            "source_size_px": [src_w_px, src_h_px],
            "source_size_mm": [src_w_mm, src_h_mm],
            "source_physical_aspect": src_w_mm / src_h_mm,
            "aspect_origin": source_aspect_origin,
            **src_info,
        },
        "target": {
            "width_mm": target_w_mm,
            "height_mm": target_h_mm,
            "physical_aspect": target_w_mm / target_h_mm,
            "pixel_width": built.shape[1],
            "pixel_height": built.shape[0],
            "raster_aspect": built.shape[1] / built.shape[0],
            "pitch_x_mm": pitch_x,
            "pitch_y_mm": pitch_y,
            "physical_pixel_aspect": pitch_x / pitch_y,
            "dpi_x": dpi_x,
            "dpi_y": dpi_y,
            "bit_depth": 16,
        },
        "classification": {
            "image_class": args.image_class,
            "surface_type": args.surface_type,
            "placement_mode": args.placement_mode,
        },
        "processing": {
            "fit_mode": args.fit,
            "aspect_policy": args.aspect_policy,
            "allow_aspect_distortion": allow_distortion,
            "aspect_tolerance_pct": tolerance,
            "black_point": args.black_point,
            "white_point": args.white_point,
            "gamma": args.gamma,
            "invert": args.invert,
            "background": args.background,
        },
        "physical_fit": fit,
        "aspect_validation": {
            "source_physical_aspect": src_w_mm / src_h_mm,
            "placed_physical_aspect": fit.get("reconstructed_physical_aspect", fit.get("placed_aspect")),
            "error_pct": aspect_error,
            "tolerance_pct": tolerance,
            "passed": allow_distortion or aspect_error <= tolerance,
        },
        "preview": preview_meta,
        "warnings": warnings,
    }
    write_json(sidecar_path(args.output_png), meta)

    print(f"Wrote geometry heightmap: {args.output_png}")
    print(f"Physical target: {target_w_mm:g} x {target_h_mm:g} mm")
    print(f"Raster: {built.shape[1]} x {built.shape[0]} px at {dpi_x:.2f} x {dpi_y:.2f} PPI")
    print(f"Physical aspect error: {aspect_error:.5f}% (tolerance {tolerance:.3f}%)")
    if args.preview:
        print(f"Square-pixel visual preview: {args.preview}")
    for w in warnings:
        print(f"warning: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
