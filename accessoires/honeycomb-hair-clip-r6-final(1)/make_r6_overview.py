#!/usr/bin/env python3
"""Compose the approved R6 concept and production-candidate views."""

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
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--armor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tile_size = (900, 620)
    header = 68
    sheet = Image.new("RGB", (1800, (tile_size[1] + header) * 2), (13, 14, 16))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype("DejaVuSans.ttf", size=27)
    items = [
        (args.concept, "Freigegebenes Konzept R6"),
        (args.iso, "DRAFT-CAD · Isometrie"),
        (args.profile, "DRAFT-CAD · Offen / Seitenprofil"),
        (args.armor, "DRAFT-CAD · Drei Wabenreihen"),
    ]
    for index, (source, label) in enumerate(items):
        x = (index % 2) * tile_size[0]
        y = (index // 2) * (tile_size[1] + header)
        sheet.paste(fit(Image.open(source), tile_size), (x, y + header))
        draw.text((x + 24, y + 19), label, fill=(232, 234, 238), font=label_font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, quality=95)


if __name__ == "__main__":
    main()
