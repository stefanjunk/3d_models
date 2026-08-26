#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _relief_utils import (
    load_grayscale_float,
    rasterize_physical_fit,
    read_json,
    save_16bit_png,
    sha256_file,
    sidecar_path,
    write_json,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Register a raw/generated image as an immutable 16-bit source master without anisotropic stretching.")
    p.add_argument("input_image")
    p.add_argument("output_master")
    p.add_argument("--spec", required=True, help="source-spec JSON created by plan_ai_source/init_relief_job")
    p.add_argument("--source-kind", default="supplied", choices=["supplied", "ai-generated", "procedural", "scanned", "other"])
    p.add_argument("--fit", choices=["contain", "cover", "crop", "stretch"], help="Default: contain for subjects, cover for textures")
    p.add_argument("--allow-aspect-distortion", action="store_true")
    args = p.parse_args()

    spec = read_json(args.spec)
    phys = spec["physical"]
    author = spec["authoring"]
    w_mm, h_mm = float(phys["width_mm"]), float(phys["height_mm"])
    ppi = float(author["ppi"])
    pitch = 25.4 / ppi
    target_w_px = max(1, int(round(w_mm / pitch)))
    target_h_px = max(1, int(round(h_mm / pitch)))

    arr, src_info = load_grayscale_float(args.input_image)
    sh, sw = arr.shape
    raw_aspect = sw / sh
    requested_aspect = w_mm / h_mm
    raw_aspect_error_pct = abs(raw_aspect / requested_aspect - 1.0) * 100.0
    effective_ppi_x = sw / (w_mm / 25.4)
    effective_ppi_y = sh / (h_mm / 25.4)

    image_class = str(spec.get("image_class", "subject")).lower()
    fit = args.fit or ("cover" if image_class in {"texture", "pattern", "wood", "carbon", "fabric", "stone"} else "contain")

    # Source raw pixels are assumed square; use their pixel dimensions as a physical proxy.
    canonical, fit_info = rasterize_physical_fit(
        arr,
        source_size_mm=(float(sw), float(sh)),
        target_size_mm=(w_mm, h_mm),
        pitch_mm=(pitch, pitch),
        fit=fit,
        background_value=0.0,
        aspect_policy="preserve" if not args.allow_aspect_distortion else "allow-distortion",
        allow_aspect_distortion=args.allow_aspect_distortion,
    )
    save_16bit_png(canonical, args.output_master, ppi, ppi)

    warnings: list[str] = []
    if raw_aspect_error_pct > 1.0:
        warnings.append(
            f"Generated/supplied raster aspect differs from requested physical authoring aspect by {raw_aspect_error_pct:.3f}%. "
            f"Registration used {fit} rather than anisotropic stretch."
        )
    if min(effective_ppi_x, effective_ppi_y) < ppi * 0.85:
        warnings.append("Raw source undershoots requested authoring PPI by more than 15% on at least one axis.")
    if src_info.get("source_bit_depth_guess", 8) < 16:
        warnings.append("Raw source appears to be <=8-bit. The 16-bit master prevents further loss but cannot recreate tonal information that was never present.")

    manifest = {
        "schema": "heightmap-relief-source-master-v2.2",
        "source_kind": args.source_kind,
        "raw_source": {
            "path": str(Path(args.input_image)),
            "sha256": sha256_file(args.input_image),
            "pixel_width": sw,
            "pixel_height": sh,
            "raster_aspect": raw_aspect,
            "effective_ppi_x_at_requested_size": effective_ppi_x,
            "effective_ppi_y_at_requested_size": effective_ppi_y,
            "requested_physical_aspect_error_pct": raw_aspect_error_pct,
            **src_info,
        },
        "physical": {"width_mm": w_mm, "height_mm": h_mm, "aspect": requested_aspect},
        "authoring": {
            "ppi": ppi,
            "pitch_mm": pitch,
            "square_pixels": True,
            "requested_width_px": author.get("requested_width_px"),
            "requested_height_px": author.get("requested_height_px"),
            "canonical_width_px": canonical.shape[1],
            "canonical_height_px": canonical.shape[0],
            "fit_mode": fit,
        },
        "master": {
            "path": str(Path(args.output_master)),
            "sha256": sha256_file(args.output_master),
            "bit_depth": 16,
            "dpi_x": ppi,
            "dpi_y": ppi,
        },
        "physical_fit": fit_info,
        "generation_prompt": spec.get("generation_prompt"),
        "warnings": warnings,
    }
    write_json(sidecar_path(args.output_master, ".source.json"), manifest)
    print(f"Registered 16-bit source master: {args.output_master}")
    print(f"Canonical authoring raster: {canonical.shape[1]} x {canonical.shape[0]} px @ {ppi:g} PPI")
    print(f"Raw requested-aspect mismatch: {raw_aspect_error_pct:.4f}%")
    for w in warnings:
        print(f"warning: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
