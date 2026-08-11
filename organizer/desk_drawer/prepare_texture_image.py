#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageOps


def make_lowres_texture(src: Path, target_res: int, out: Path | None = None,
                        target_width: int | None = None,
                        target_height: int | None = None,
                        bit_depth: int = 16) -> Path:
    img = Image.open(src).convert('L')
    img = ImageOps.autocontrast(img)
    width = target_width or target_res
    height = target_height or target_res
    if width <= 0 or height <= 0:
        raise ValueError('target dimensions must be positive')
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    if out is None:
        out = src.with_name(f"{src.stem}_{target_res}.png")
    if bit_depth == 16:
        # Explicit 16-bit output preserves tonal precision for relief workflows.
        img = img.point(lambda value: value * 257).convert('I;16')
        img.save(out, format='PNG', bits=16)
    elif bit_depth == 8:
        # OpenSCAD surface() expects an 8-bit grayscale PNG in this workflow.
        img.save(out, format='PNG', bits=8)
    else:
        raise ValueError('bit depth must be 8 or 16')
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description='Create a low-resolution grayscale engraving image for OpenSCAD surface().')
    ap.add_argument('src', help='source image file')
    ap.add_argument('--target-res', type=int, default=256, help='target width/height in pixels (default: 256)')
    ap.add_argument('--target-width', type=int, default=None, help='optional physical-sampling width in pixels')
    ap.add_argument('--target-height', type=int, default=None, help='optional physical-sampling height in pixels')
    ap.add_argument('--bit-depth', type=int, choices=(8, 16), default=16,
                    help='output PNG bit depth (default: 16; use 8 for OpenSCAD surface())')
    ap.add_argument('--out', default=None, help='optional output path')
    args = ap.parse_args()

    src = Path(args.src)
    out = Path(args.out) if args.out else None
    result = make_lowres_texture(src, args.target_res, out, args.target_width, args.target_height, args.bit_depth)
    print(result)


if __name__ == '__main__':
    main()
