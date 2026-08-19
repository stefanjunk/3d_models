#!/usr/bin/env python3
"""Compose release-gate evidence for the exact JuSt Innovation watermark."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BG = (17, 19, 22)
FG = (240, 243, 247)
MUTED = (174, 182, 194)
ACCENT = (91, 214, 192)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size=size)


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, BG)
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color=ACCENT) -> None:
    draw.line((start, end), fill=color, width=3)
    sx, sy = start
    ex, ey = end
    draw.polygon([(sx, sy), (sx + 10, sy - 5), (sx + 10, sy + 5)], fill=color)
    draw.polygon([(ex, ey), (ex - 10, ey - 5), (ex - 10, ey + 5)], fill=color)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--face", type=Path, required=True)
    parser.add_argument("--layers", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sheet = Image.new("RGB", (1800, 1260), BG)
    draw = ImageDraw.Draw(sheet)
    draw.text((32, 22), "JuSt Innovation · Kennzeichnungsnachweis R6", fill=FG, font=font(30, True))
    draw.text((32, 63), "Exakte Originalkontur JSI-WM-001-R1 · kompakt · 0,40 mm vertieft", fill=MUTED, font=font(20))

    face = Image.open(args.face).convert("RGB")
    full = fit(face, (880, 500))
    sheet.paste(full, (20, 112))
    draw.text((42, 126), "Direkte Außenansicht des DRAFT-STL", fill=FG, font=font(23, True))
    draw.text((42, 160), "Glatte Mittelfläche einer vollständigen Wabe; keine Rille wird geschnitten.", fill=MUTED, font=font(17))

    center_x = int(face.width * 0.5)
    center_y = int(face.height * 0.549)
    half = int(face.width * 0.125)
    crop = face.crop((center_x - half, center_y - half, center_x + half, center_y + half))
    zoom = fit(crop, (840, 500))
    sheet.paste(zoom, (940, 112))
    draw.text((962, 126), "Dimensionierte Nahansicht", fill=FG, font=font(23, True))
    arrow(draw, (1110, 548), (1610, 548))
    draw.text((1280, 510), "11,423 mm", fill=ACCENT, font=font(21, True))
    draw.line((1645, 220, 1645, 510), fill=ACCENT, width=3)
    draw.polygon([(1645, 220), (1640, 230), (1650, 230)], fill=ACCENT)
    draw.polygon([(1645, 510), (1640, 500), (1650, 500)], fill=ACCENT)
    draw.text((1660, 342), "10,00 mm", fill=ACCENT, font=font(20, True))
    draw.text((962, 574), "Mind. 2,0 mm Randabstand im sicheren 15,6 × 14,0-mm-Feld", fill=MUTED, font=font(17))

    panel_x, panel_y = 20, 660
    panel_w, panel_h = 880, 560
    draw.rectangle((panel_x, panel_y, panel_x + panel_w, panel_y + panel_h), outline=(73, 80, 91), width=2)
    draw.text((42, 680), "Schnitt durch die markierte Wabe", fill=FG, font=font(23, True))
    draw.text((42, 714), "Außenfläche oben · Vertiefung nach innen · ursprünglicher Bauraum bleibt unverändert", fill=MUTED, font=font(17))
    x0, y0 = 170, 810
    scale = 105
    total = 3.3
    shell_h = int(2.4 * scale)
    armor_h = int(0.9 * scale)
    draw.rectangle((x0, y0, x0 + 470, y0 + armor_h), fill=(108, 116, 129), outline=FG)
    draw.rectangle((x0, y0 + armor_h, x0 + 470, y0 + armor_h + shell_h), fill=(72, 79, 91), outline=FG)
    recess_w = 190
    recess_h = int(0.4 * scale)
    draw.rectangle((x0 + 140, y0, x0 + 140 + recess_w, y0 + recess_h), fill=BG, outline=ACCENT, width=3)
    draw.text((x0 + 165, y0 + 7), "0,40 mm", fill=ACCENT, font=font(18, True))
    draw.text((x0 + 500, y0 + 24), "Armor 0,90 mm", fill=FG, font=font(19))
    draw.text((x0 + 500, y0 + armor_h + 85), "Schale 2,40 mm", fill=FG, font=font(19))
    draw.text((x0 + 500, y0 + armor_h + shell_h - 22), "Restwand 2,90 mm", fill=ACCENT, font=font(19, True))
    draw.line((x0 - 30, y0 + armor_h + shell_h, x0 + 490, y0 + armor_h + shell_h), fill=(220, 224, 230), width=3)
    draw.text((x0, y0 + armor_h + shell_h + 18), "Keine Geometrie unter ursprünglichem Datum", fill=MUTED, font=font(17))

    layer_image = fit(Image.open(args.layers), (840, 560))
    sheet.paste(layer_image, (940, 660))
    draw.text((962, 680), "Geometrische 0,20-mm-Layerprüfung", fill=FG, font=font(23, True))
    draw.text((962, 714), "Direkte STL-Schnitte; druckerspezifische G-Code-Vorschau bleibt Profilaufgabe.", fill=MUTED, font=font(17))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, quality=95)


if __name__ == "__main__":
    main()
