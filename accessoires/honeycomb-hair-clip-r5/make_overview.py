#!/usr/bin/env python3
"""Compose the approved concept and canonical current-revision renders."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (20, 21, 23))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concept", type=Path, required=True)
    parser.add_argument("--iso", type=Path, required=True)
    parser.add_argument("--side", type=Path, required=True)
    parser.add_argument("--top", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tile_size = (900, 650)
    header = 64
    sheet = Image.new("RGB", (tile_size[0] * 2, (tile_size[1] + header) * 2), (13, 14, 16))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("DejaVuSans.ttf", size=28)
    items = [
        (args.concept, "Freigegebenes Konzept"),
        (args.iso, "CAD - Isometrie"),
        (args.top, "CAD - Hexagonoberseite"),
        (args.side, "CAD - Nicht-Bettseite"),
    ]
    for index, (source, label) in enumerate(items):
        x = (index % 2) * tile_size[0]
        y = (index // 2) * (tile_size[1] + header)
        sheet.paste(fit(Image.open(source), tile_size), (x, y + header))
        draw.text((x + 24, y + 18), label, fill=(232, 234, 238), font=font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, quality=95)


if __name__ == "__main__":
    main()
