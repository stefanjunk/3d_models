#!/usr/bin/env python3
"""Render geometric layer-preview polygons produced by watermark_layer_preview.mjs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(name, size=size)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    crop = report["cropMm"]
    width, height = 1560, 700
    panel_w, panel_h = 520, 285
    header = 115
    margin = 42
    image = Image.new("RGB", (width, height), (17, 19, 22))
    draw = ImageDraw.Draw(image)
    draw.text((34, 24), "Geometrische 0,20-mm-Layerprüfung · Kennzeichnungszone", fill=(242, 244, 247), font=font(28, True))
    draw.text((34, 65), "Direkte Querschnitte des DRAFT-R6-STL; kein druckerspezifischer G-Code.", fill=(174, 182, 194), font=font(18))
    draw.text((34, 89), "Die getrennten Vertiefungsabschnitte bleiben in allen geprüften Höhen erkennbar.", fill=(174, 182, 194), font=font(18))

    view_w = crop["maxX"] - crop["minX"]
    view_h = crop["maxY"] - crop["minY"]
    for index, layer in enumerate(report["layers"]):
        col, row = index % 3, index // 3
        x0, y0 = col * panel_w, header + row * panel_h
        inner = (x0 + margin, y0 + 44, x0 + panel_w - margin, y0 + panel_h - margin)
        scale = min((inner[2] - inner[0]) / view_w, (inner[3] - inner[1]) / view_h)
        layer_canvas = Image.new("RGB", (inner[2] - inner[0], inner[3] - inner[1]), (17, 19, 22))
        layer_draw = ImageDraw.Draw(layer_canvas)

        def project(point: list[float]) -> tuple[float, float]:
            return (
                (point[0] - crop["minX"]) * scale,
                layer_canvas.height - (point[1] - crop["minY"]) * scale,
            )

        for polygon in layer["relevantPolygonsXy"]:
            points = [project(point) for point in polygon]
            layer_draw.polygon(points, fill=(116, 124, 136), outline=(226, 230, 236))
        image.paste(layer_canvas, (inner[0], inner[1]))
        draw.rectangle(inner, outline=(74, 81, 92), width=2)
        draw.text(
            (x0 + margin, y0 + 12),
            f"Z {layer['zMm']:.2f} mm · Layer {layer['layerIndexAt0_20Mm']}",
            fill=(238, 241, 245),
            font=font(18),
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, quality=95)


if __name__ == "__main__":
    main()
