#!/usr/bin/env python3
"""Create release-gate evidence from the exact copied DXF watermark outlines."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path("/usr/share/fonts/truetype/dejavu") / name
    return ImageFont.truetype(path, size) if path.exists() else ImageFont.load_default()


def parse_dxf(path: Path) -> list[list[tuple[float, float]]]:
    lines = path.read_text(encoding="utf-8").replace("\r", "").splitlines()
    pairs = [(int(lines[i].strip()), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    polygons: list[list[tuple[float, float]]] = []
    points: list[tuple[float, float]] = []
    vertex: dict[str, float] | None = None
    active = False

    def flush_vertex() -> None:
        nonlocal vertex
        if vertex and "x" in vertex and "y" in vertex:
            points.append((vertex["x"], vertex["y"]))
        vertex = None

    def flush_polygon() -> None:
        nonlocal points, active
        flush_vertex()
        if len(points) >= 3:
            if points[0] == points[-1]:
                points.pop()
            polygons.append(points)
        points = []
        active = False

    for code, value in pairs:
        if code == 0:
            if value in {"POLYLINE", "LWPOLYLINE"}:
                if active:
                    flush_polygon()
                active = True
            elif value == "VERTEX" and active:
                flush_vertex()
                vertex = {}
            elif value == "SEQEND" and active:
                flush_polygon()
            continue
        if active and vertex is not None:
            if code == 10:
                vertex["x"] = float(value)
            elif code == 20:
                vertex["y"] = float(value)
    if active:
        flush_polygon()
    return polygons


def centered_polygons(polygons: list[list[tuple[float, float]]], scale: float) -> list[list[tuple[float, float]]]:
    flat = [point for polygon in polygons for point in polygon]
    min_x = min(point[0] for point in flat)
    max_x = max(point[0] for point in flat)
    min_y = min(point[1] for point in flat)
    max_y = max(point[1] for point in flat)
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    return [[((x - cx) * scale, (y - cy) * scale) for x, y in polygon] for polygon in polygons]


def mark_mask(size: tuple[int, int], polygons, center, px_per_mm, readable_bottom=True) -> Image.Image:
    mask = Image.new("1", size, 0)
    for polygon in polygons:
        layer = Image.new("1", size, 0)
        draw = ImageDraw.Draw(layer)
        points = []
        for x, y in polygon:
            # The model mirrors X before cutting; direct bottom view mirrors X again.
            view_x = x if readable_bottom else -x
            points.append((center[0] + view_x * px_per_mm, center[1] - y * px_per_mm))
        draw.polygon(points, fill=1)
        mask = ImageChops.logical_xor(mask, layer)
    return mask


def overlay_mark(image, polygons, center, px_per_mm, color=(35, 35, 35)) -> None:
    mask = mark_mask(image.size, polygons, center, px_per_mm)
    fill = Image.new("RGB", image.size, color)
    image.paste(fill, mask=mask)


def arrow(draw, start, end, color=(25, 25, 25), width=2) -> None:
    draw.line([start, end], fill=color, width=width)
    for point, sign in ((start, 1), (end, -1)):
        x, y = point
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = max((dx * dx + dy * dy) ** 0.5, 1)
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        tip = (x + sign * ux * 8, y + sign * uy * 8)
        draw.polygon([point, (tip[0] + px * 4, tip[1] + py * 4), (tip[0] - px * 4, tip[1] - py * 4)], fill=color)


def underside_view(polygons, cfg, output: Path) -> None:
    image = Image.new("RGB", (900, 1080), (244, 245, 247))
    draw = ImageDraw.Draw(image)
    draw.text((35, 25), "Fertige Unterseite – direkte Außenansicht", font=font(30, True), fill=(25, 28, 31))
    draw.text((35, 65), "Vier markierte Hauptmodule; Leserichtung nach dem Umdrehen des Druckteils", font=font(18), fill=(60, 64, 68))
    scale = 2.45
    origin = (170, 105)
    total_w = 227.0
    total_d = 357.0
    modules = [
        (0, 92, 0, 178.5, "Driver vorn"),
        (0, 92, 178.5, 357, "Driver hinten"),
        (92, 227, 0, 178.5, "Hardware vorn"),
        (92, 227, 178.5, 357, "Hardware hinten"),
    ]
    for x0, x1, y0, y1, label in modules:
        # Bottom view reverses global X.
        sx0 = origin[0] + (total_w - x1) * scale
        sx1 = origin[0] + (total_w - x0) * scale
        sy0 = origin[1] + y0 * scale
        sy1 = origin[1] + y1 * scale
        draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=8, fill=(205, 209, 213), outline=(75, 80, 84), width=2)
        draw.text((sx0 + 8, sy0 + 8), label, font=font(14), fill=(70, 74, 78))
    placements = cfg["placements_global_xy"]
    for name, (x, y) in placements.items():
        screen = (origin[0] + (total_w - x) * scale, origin[1] + y * scale)
        overlay_mark(image, polygons, screen, scale, (25, 25, 25))
    image.save(output)


def closeup(polygons, cfg, output: Path) -> None:
    image = Image.new("RGB", (1000, 620), (247, 248, 249))
    draw = ImageDraw.Draw(image)
    draw.text((35, 25), "Dimensionierte Unterseiten-Nahansicht", font=font(30, True), fill=(25, 28, 31))
    rect = [130, 130, 830, 530]
    draw.rectangle(rect, fill=(205, 209, 213), outline=(55, 60, 64), width=3)
    center = ((rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2)
    px_per_mm = 10
    overlay_mark(image, polygons, center, px_per_mm, (25, 25, 25))
    mark_w, mark_h = cfg["actual_envelope"]
    x0 = center[0] - mark_w * px_per_mm / 2
    x1 = center[0] + mark_w * px_per_mm / 2
    y0 = center[1] - mark_h * px_per_mm / 2
    y1 = center[1] + mark_h * px_per_mm / 2
    arrow(draw, (x0, y1 + 45), (x1, y1 + 45))
    draw.text((center[0] - 70, y1 + 55), f"{mark_w:.3f} mm", font=font(18, True), fill=(30, 30, 30))
    arrow(draw, (x1 + 55, y0), (x1 + 55, y1))
    draw.text((x1 + 70, center[1] - 12), f"{mark_h:.1f} mm", font=font(18, True), fill=(30, 30, 30))
    clear_x = (cfg["safe_rectangle"][0] - mark_w) / 2
    clear_y = (cfg["safe_rectangle"][1] - mark_h) / 2
    draw.text((130, 555), f"Freie Prüffläche 70 × 40 mm · rechnerische Randreserve {clear_x:.1f} / {clear_y:.1f} mm · Mindestwert 2,0 mm", font=font(17), fill=(55, 58, 61))
    image.save(output)


def section_view(cfg, floor_thickness: float, output: Path) -> None:
    image = Image.new("RGB", (1000, 620), (247, 248, 249))
    draw = ImageDraw.Draw(image)
    draw.text((35, 25), "Schnitt durch die vertiefte Unterseitenkennzeichnung", font=font(30, True), fill=(25, 28, 31))
    scale = 150
    base_y = 500
    residual = floor_thickness - cfg["depth"]
    top_y = base_y - floor_thickness * scale
    draw.rectangle([120, top_y, 880, base_y], fill=(155, 161, 167), outline=(45, 48, 51), width=2)
    recess_x0, recess_x1 = 410, 590
    recess_top = base_y - 0.4 * scale
    draw.rectangle([recess_x0, recess_top, recess_x1, base_y + 2], fill=(247, 248, 249))
    draw.line([(120, base_y), (880, base_y)], fill=(200, 40, 40), width=3)
    draw.text((125, base_y + 16), "Druckbett-Datum z = 0 bleibt an den umliegenden Auflageflächen unverändert", font=font(17), fill=(150, 35, 35))
    arrow(draw, (650, base_y), (650, recess_top))
    draw.text((670, recess_top + 15), "0,40 mm Vertiefung", font=font(18, True), fill=(30, 30, 30))
    arrow(draw, (760, top_y), (760, recess_top))
    draw.text((780, top_y + 120), f"{residual:.2f} mm Restboden", font=font(18, True), fill=(30, 30, 30))
    draw.text((120, 90), f"Ausgangsboden: {floor_thickness:.2f} mm · Cutter-Überdeckung: 0,08 mm · keine Geometrie unter z = 0", font=font(19), fill=(55, 58, 61))
    image.save(output)


def layer_preview(polygons, cfg, output: Path) -> None:
    image = Image.new("RGB", (1320, 520), (247, 248, 249))
    draw = ImageDraw.Draw(image)
    draw.text((30, 20), "Erste kennzeichnungstragende Schichten – geometrische Toolpath-Simulation", font=font(28, True), fill=(25, 28, 31))
    draw.text((30, 58), "0,20-mm-Schichten · 0,44-mm-Linienbreite · keine druckerspezifische G-Code-Erzeugung", font=font(17), fill=(70, 74, 78))
    heights = [0.10, 0.30, 0.50]
    for index, height in enumerate(heights):
        panel = [45 + index * 420, 120, 375 + index * 420, 430]
        draw.rectangle(panel, fill=(225, 228, 231), outline=(65, 70, 74), width=2)
        mark = mark_mask(image.size, polygons, ((panel[0] + panel[2]) / 2, (panel[1] + panel[3]) / 2), 10)
        hatch = Image.new("RGB", image.size, (225, 228, 231))
        hatch_draw = ImageDraw.Draw(hatch)
        spacing = max(2, round(0.44 * 10))
        for y in range(panel[1] + 4, panel[3] - 3, spacing):
            hatch_draw.line([(panel[0] + 4, y), (panel[2] - 4, y)], fill=(70, 110, 145), width=2)
        panel_mask = Image.new("1", image.size, 0)
        ImageDraw.Draw(panel_mask).rectangle(panel, fill=1)
        if height < cfg["depth"]:
            panel_mask = ImageChops.logical_and(panel_mask, ImageChops.invert(mark))
        image.paste(hatch, mask=panel_mask)
        draw.text((panel[0], 450), f"z = {height:.2f} mm", font=font(18, True), fill=(35, 38, 41))
        state = "Kontur bleibt ausgespart" if height < cfg["depth"] else "Deckschicht schließt Kontur"
        draw.text((panel[0], 478), state, font=font(15), fill=(65, 68, 71))
    image.save(output)


def main() -> None:
    model_params = json.loads((ROOT / "config" / "model-params.json").read_text(encoding="utf-8"))
    cfg = model_params["watermark"]
    dxf = (ROOT / "config" / cfg["dxf"]).resolve()
    polygons = centered_polygons(parse_dxf(dxf), cfg["uniform_scale"])
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    underside_view(polygons, cfg, report_dir / "watermark-underside.png")
    closeup(polygons, cfg, report_dir / "watermark-closeup.png")
    section_view(cfg, float(model_params["organizer"]["floor_thickness"]), report_dir / "watermark-section.png")
    layer_preview(polygons, cfg, report_dir / "watermark-layer-preview.png")
    print("watermark evidence written")


if __name__ == "__main__":
    main()
