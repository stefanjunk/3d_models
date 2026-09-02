#!/usr/bin/env python3
"""Render the MM-ART-010 revision 0.5.0 site-marker concept gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
REPO = PRODUCT.parents[2]
LEGACY_RENDERER = PRODUCT / "source" / "v0.4.0" / "berlin" / "render_display_modes_concept.py"
PALETTE_PARAMETERS = PRODUCT / "source" / "v0.4.1" / "berlin" / "display-mode-parameters.json"
MARKER_PARAMETERS = HERE / "site-marker-parameters.json"
ADDRESS_SOURCE = PRODUCT / "source-data" / "v0.5.0" / "berlin" / "metri-create-headquarters-address.json"
BRAND_SVG = PRODUCT / "source-data" / "v0.5.0" / "branding" / "metricreate-mark-mono.svg"
BRAND_PREVIEW = REPO / "business" / "01-strategy" / "brand-assets" / "metricreate" / "exports" / "metricreate-mark-color.png"
OUTPUT = PRODUCT / "concepts" / "berlin-site-marker-concept-v05.png"
REPORT = PRODUCT / "concepts" / "berlin-site-marker-concept-v05.json"

CANVAS = (2000, 1320)
WALL = "#F1EEE8"
CARD = "#FCFAF5"
INK = "#17232B"
MUTED = "#69665F"
OUTLINE = "#D7D0C5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def load_legacy_renderer():
    spec = importlib.util.spec_from_file_location("mm_art_010_display_renderer_v05", LEGACY_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load renderer: {LEGACY_RENDERER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def paste_monochrome_mark(canvas, center, width_px, height_px, color):
    source = Image.open(BRAND_PREVIEW).convert("RGBA")
    alpha = source.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("Brand preview has no visible pixels")
    alpha = alpha.crop(bbox).resize((width_px, height_px), Image.Resampling.LANCZOS)
    mark = Image.new("RGBA", (width_px, height_px), color)
    mark.putalpha(alpha)

    x = round(center[0] - width_px / 2)
    y = round(center[1] - height_px / 2)
    shadow = Image.new("RGBA", mark.size, (16, 25, 30, 0))
    shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(2)))
    canvas.alpha_composite(shadow, (x + 3, y + 4))
    canvas.alpha_composite(mark, (x, y))
    return [x, y, x + width_px, y + height_px]


def main() -> None:
    if OUTPUT.exists() or REPORT.exists():
        raise FileExistsError("Refusing to overwrite concept evidence")

    legacy = load_legacy_renderer()
    palette_parameters = json.loads(PALETTE_PARAMETERS.read_text())
    marker_parameters = json.loads(MARKER_PARAMETERS.read_text())
    address = json.loads(ADDRESS_SOURCE.read_text())
    palette = palette_parameters["shared"]["palette"]
    labels = palette_parameters["shared"]["palette_labels"]

    legacy.SOURCE = PRODUCT / "source-data" / "v0.4.0" / "berlin"
    legacy.PALETTE = palette
    legacy.PALETTE_LABELS = labels
    boundary = legacy.load_union("boundary.geojson")
    if boundary.is_empty:
        raise RuntimeError("Berlin boundary source is empty")

    image = Image.new("RGBA", CANVAS, WALL)
    draw = ImageDraw.Draw(image)
    draw.text((90, 55), "BERLIN · PARAMETRISCHER STANDORTMARKER", font=font(50, True), fill=INK)
    draw.text((92, 120), "Konzept v05 · kompakte metriCreate-Marke · Adresse und Grafik später austauschbar", font=font(25), fill=MUTED)

    cards = [(70, 190, 965, 925), (1035, 190, 1930, 925)]
    for card in cards:
        draw.rounded_rectangle(card, radius=22, fill=CARD, outline=OUTLINE, width=2)
    draw.text((105, 225), "A  NUR BERLIN", font=font(31, True), fill=INK)
    draw.text((1070, 225), "B  BERLIN MIT UMLAND", font=font(31, True), fill=INK)

    crop_view = (120, 315, 915, 770)
    context_view = (1085, 315, 1880, 770)
    legacy.draw_boundary_crop(image, boundary, crop_view)
    context_bounds, _ = legacy.draw_context_outline(
        image,
        boundary,
        context_view,
        palette_parameters["modes"]["context_outline"]["context_margin_ratio"]["default"],
    )

    coordinate = address["geocode"]["coordinate"]
    crop_point, crop_source_px = legacy.transformer(boundary.bounds, crop_view, padding=22)
    context_point, context_source_px = legacy.transformer(context_bounds, context_view, padding=0)
    crop_center = crop_point(*coordinate)
    context_center = context_point(*coordinate)

    marker = marker_parameters["site_marker"]
    width_mm = marker["placement"]["width_mm"]
    height_mm = marker["placement"]["resolved_height_mm"]
    crop_mm_per_source_m = 0.010599171038984969
    context_mm_per_source_m = 0.008547718579785249
    crop_width_px = max(20, round(width_mm * crop_source_px / crop_mm_per_source_m))
    crop_height_px = max(20, round(height_mm * crop_source_px / crop_mm_per_source_m))
    context_width_px = max(20, round(width_mm * context_source_px / context_mm_per_source_m))
    context_height_px = max(20, round(height_mm * context_source_px / context_mm_per_source_m))
    crop_bbox = paste_monochrome_mark(image, crop_center, crop_width_px, crop_height_px, palette["Orange"])
    context_bbox = paste_monochrome_mark(image, context_center, context_width_px, context_height_px, palette["Orange"])

    draw = ImageDraw.Draw(image)
    for center, label_x in ((crop_center, 105), (context_center, 1070)):
        draw.ellipse((center[0] - 18, center[1] - 18, center[0] + 18, center[1] + 18), outline="#FFFFFF", width=2)
        draw.line((center[0] + 18, center[1] - 18, label_x + 610, 815), fill="#8B8378", width=2)

    draw.text((105, 790), "Standort: Sterkrader Straße 24 · 13507 Berlin", font=font(21, True), fill=INK)
    draw.text((105, 830), "Marke 16,5 mm breit · Mittelpunkt auf amtlichem Adresspunkt", font=font(19), fill=MUTED)
    draw.text((105, 866), "Tool 4 = Sky Blue · 0,60 mm über höchster lokaler Fläche", font=font(19), fill=MUTED)
    draw.text((1070, 790), "Gleicher Adresspunkt, eigener Modus-Transform", font=font(21, True), fill=INK)
    draw.text((1070, 830), "Bleibt vollständig auf dem linken 300 × 400-mm-Druckteil", font=font(19), fill=MUTED)
    draw.text((1070, 866), "Mehr als 50 mm Abstand zur dauerhaften Mittelnaht", font=font(19), fill=MUTED)

    lower_cards = [(70, 960, 965, 1245), (1035, 960, 1930, 1245)]
    for card in lower_cards:
        draw.rounded_rectangle(card, radius=20, fill=CARD, outline=OUTLINE, width=2)

    draw.text((105, 995), "AUSTAUSCHBARE MARKER-PARAMETER", font=font(25, True), fill=INK)
    params = [
        "Adresse oder dokumentierte EPSG:25833-Koordinate",
        "SVG/DXF-Logo, Vektor-Icon oder monochrome Bildmaske",
        "Breite, Drehung, Reliefhöhe und vorhandenes Farbwerkzeug",
    ]
    y = 1045
    for line in params:
        draw.ellipse((110, y + 8, 120, y + 18), fill=palette["Orange"])
        draw.text((140, y), line, font=font(20), fill=MUTED)
        y += 53

    base_x, base_y = 770, 1050
    draw.rectangle((base_x, base_y, base_x + 120, base_y + 30), fill=palette["Bone White"], outline="#A79E92")
    draw.rectangle((base_x + 32, base_y - 18, base_x + 88, base_y), fill=palette["Orange"], outline="#426E87")
    draw.text((base_x - 4, base_y + 40), "Seite: +0,60 mm", font=font(15), fill=MUTED)

    draw.text((1070, 995), "DRITTE FARVARIANTE · METRICREATE FORGE", font=font(25, True), fill=INK)
    forge = [
        ("1", "Midnight", "#1E2B36", "Grundplatte"),
        ("2", "Mint Green", "#72CFAE", "Relieffläche"),
        ("3", "White", "#F2F3EE", "Straßennetz"),
        ("4", "Orange", "#F36B32", "Grenze + Logo"),
    ]
    y = 1048
    for tool, name, color, role in forge:
        draw.rounded_rectangle((1075, y, 1120, y + 36), radius=5, fill=color, outline="#AAA196")
        draw.text((1140, y + 3), f"Tool {tool}  {name}", font=font(19, True), fill=INK)
        draw.text((1445, y + 3), role, font=font(19), fill=MUTED)
        y += 46
    draw.text((1075, 1210), "Aqua entfällt bewusst: vier Farben, kein Dithering, keine fünfte Rolle.", font=font(17), fill=MUTED)

    draw.text((92, 1278), "Konzeptdarstellung, keine Fertigungszeichnung. Freigabe erforderlich, bevor CAD, Mesh und Anycubic-3MF v0.5.0 erzeugt werden.", font=font(18), fill=MUTED)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUTPUT, quality=95, dpi=(150, 150))
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.0-concept",
        "status": "PASS",
        "artifact": str(OUTPUT.relative_to(PRODUCT)),
        "artifact_sha256": sha256(OUTPUT),
        "parameter_sources": {
            str(MARKER_PARAMETERS.relative_to(PRODUCT)): sha256(MARKER_PARAMETERS),
            str(ADDRESS_SOURCE.relative_to(PRODUCT)): sha256(ADDRESS_SOURCE),
            str(PALETTE_PARAMETERS.relative_to(PRODUCT)): sha256(PALETTE_PARAMETERS),
        },
        "brand_assets": {
            str(BRAND_SVG.relative_to(PRODUCT)): sha256(BRAND_SVG),
            str(BRAND_PREVIEW.relative_to(REPO)): sha256(BRAND_PREVIEW),
        },
        "address_coordinate_epsg25833": coordinate,
        "resolved_panel_coordinates_mm": address["resolved_panel_coordinates_mm"],
        "marker_size_mm": [width_mm, height_mm],
        "marker_relief_mm": marker["relief"]["height_above_highest_local_face_mm"],
        "semantic_tool": marker["relief"]["semantic_tool"],
        "concept_marker_pixel_bounds": {
            "boundary_crop": crop_bbox,
            "context_outline": context_bbox,
        },
        "limitations": [
            "visual concept only",
            "no production geometry or 3MF generated before approval",
            "display colors are approximations, not calibrated filament measurements",
            "official address data verifies location, not company occupancy",
            "brand clearance and physical mark readability remain open",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
