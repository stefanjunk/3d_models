#!/usr/bin/env python3
"""Render the MM-ART-010 revision 0.5.1 metriMade site-marker concept gate."""

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
MARKER_PARAMETERS = HERE / "site-marker-concept-parameters.json"
ADDRESS_SOURCE = PRODUCT / "source-data" / "v0.5.0" / "berlin" / "metri-create-headquarters-address.json"
BRAND_ROOT = REPO / "business" / "01-strategy" / "brand-assets" / "metrimade"
BRAND_SVG = BRAND_ROOT / "exports" / "metrimade-lockup-stacked-mono.svg"
BRAND_PREVIEW = BRAND_ROOT / "exports" / "metrimade-lockup-stacked-color.png"
BRAND_PROVENANCE = BRAND_ROOT / "provenance.json"
BRAND_MANIFEST = BRAND_ROOT / "manifest.sha256"
OUTPUT = PRODUCT / "concepts" / "berlin-site-marker-concept-v06.png"
REPORT = PRODUCT / "concepts" / "berlin-site-marker-concept-v06.json"

CANVAS = (2000, 1320)
WALL = "#F1EEE8"
CARD = "#FCFAF5"
INK = "#17232B"
MUTED = "#69665F"
OUTLINE = "#D7D0C5"
FIT = {
    "boundary_crop": {"perimeter_clearance_mm": 20.36, "center_seam_clearance_mm": 68.94},
    "context_outline": {"perimeter_clearance_mm": 104.06, "center_seam_clearance_mm": 50.37},
}


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
    spec = importlib.util.spec_from_file_location("mm_art_010_display_renderer_v051", LEGACY_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load renderer: {LEGACY_RENDERER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def paste_monochrome_lockup(canvas, center, width_px, height_px, color):
    """Place the complete stacked-logo view box without changing its aspect ratio."""
    source = Image.open(BRAND_PREVIEW).convert("RGBA")
    alpha = source.getchannel("A").resize((width_px, height_px), Image.Resampling.LANCZOS)
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
    for required in (BRAND_SVG, BRAND_PREVIEW, BRAND_PROVENANCE, BRAND_MANIFEST):
        if not required.is_file():
            raise FileNotFoundError(required)

    legacy = load_legacy_renderer()
    palette_parameters = json.loads(PALETTE_PARAMETERS.read_text())
    marker_parameters = json.loads(MARKER_PARAMETERS.read_text())
    address = json.loads(ADDRESS_SOURCE.read_text())
    palette = palette_parameters["shared"]["palette"]

    legacy.SOURCE = PRODUCT / "source-data" / "v0.4.0" / "berlin"
    legacy.PALETTE = palette
    legacy.PALETTE_LABELS = palette_parameters["shared"]["palette_labels"]
    boundary = legacy.load_union("boundary.geojson")
    if boundary.is_empty:
        raise RuntimeError("Berlin boundary source is empty")

    image = Image.new("RGBA", CANVAS, WALL)
    draw = ImageDraw.Draw(image)
    draw.text((90, 50), "BERLIN · METRIMADE-STANDORTLOGO", font=font(50, True), fill=INK)
    draw.text((92, 116), "Konzept v06 · kanonischer gestapelter Lockup · 54 mm · Karte unverändert", font=font(25), fill=MUTED)

    cards = [(70, 185, 965, 925), (1035, 185, 1930, 925)]
    for card in cards:
        draw.rounded_rectangle(card, radius=22, fill=CARD, outline=OUTLINE, width=2)
    draw.text((105, 220), "A  NUR BERLIN", font=font(31, True), fill=INK)
    draw.text((1070, 220), "B  BERLIN MIT UMLAND", font=font(31, True), fill=INK)

    crop_view = (120, 305, 915, 770)
    context_view = (1085, 305, 1880, 770)
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
    crop_size = (
        max(20, round(width_mm * crop_source_px / crop_mm_per_source_m)),
        max(20, round(height_mm * crop_source_px / crop_mm_per_source_m)),
    )
    context_size = (
        max(20, round(width_mm * context_source_px / context_mm_per_source_m)),
        max(20, round(height_mm * context_source_px / context_mm_per_source_m)),
    )
    crop_bbox = paste_monochrome_lockup(image, crop_center, *crop_size, palette["Orange"])
    context_bbox = paste_monochrome_lockup(image, context_center, *context_size, palette["Orange"])

    draw = ImageDraw.Draw(image)
    for center, x0 in ((crop_center, 105), (context_center, 1070)):
        draw.ellipse((center[0] - 17, center[1] - 17, center[0] + 17, center[1] + 17), outline="#FFFFFF", width=2)
        draw.line((center[0] + 18, center[1] - 18, x0 + 610, 810), fill="#8B8378", width=2)

    draw.text((105, 790), "54,0 × 57,18 mm · Tool 4 Sky Blue · Relief +0,60 mm", font=font(20, True), fill=INK)
    draw.text((105, 830), "Rand ≥ 20,36 mm · Mittelnaht ≥ 68,94 mm", font=font(19), fill=MUTED)
    draw.text((105, 867), "Ziel: metriMade aus ca. 2 m erkennbar", font=font(19), fill=MUTED)
    draw.text((1070, 790), "54,0 × 57,18 mm · gleiche Adresse, eigener Transform", font=font(20, True), fill=INK)
    draw.text((1070, 830), "Rand ≥ 104,06 mm · Mittelnaht ≥ 50,37 mm", font=font(19), fill=MUTED)
    draw.text((1070, 867), "Gestapeltes Logo bleibt vollständig auf dem linken Teil", font=font(19), fill=MUTED)

    lower_cards = [(70, 960, 965, 1245), (1035, 960, 1930, 1245)]
    for card in lower_cards:
        draw.rounded_rectangle(card, radius=20, fill=CARD, outline=OUTLINE, width=2)

    draw.text((105, 994), "UNVERÄNDERTE KARTE", font=font(25, True), fill=INK)
    unchanged = [
        "600 × 400 mm · zwei dauerhafte Druckhälften",
        "Straßen, Flächen, Stadtgrenze, Steckverbinder und Lichtöffnungen",
        "Oak · Mint Green · Midnight · Sky Blue",
    ]
    y = 1045
    for line in unchanged:
        draw.ellipse((110, y + 8, 120, y + 18), fill=palette["Orange"])
        draw.text((140, y), line, font=font(20), fill=MUTED)
        y += 53

    draw.text((1070, 994), "PARAMETRISCHER STANDORT", font=font(25, True), fill=INK)
    parameters = [
        "Adresse/Koordinate bleibt austauschbar",
        "Logo, Icon oder monochrome Bildmaske bleibt austauschbar",
        "Breite, Ausrichtung, Reliefhöhe und Farbwerkzeug bleiben separat",
        "2-m-Erkennung muss am Oak/Sky-Blue-Coupon bestätigt werden",
    ]
    y = 1042
    for line in parameters:
        draw.ellipse((1075, y + 7, 1085, y + 17), fill=palette["Orange"])
        draw.text((1105, y), line, font=font(18), fill=MUTED)
        y += 45

    draw.text((92, 1278), "Konzeptdarstellung. Explizite Freigabe erforderlich, bevor CAD, Mesh und Anycubic-3MF v0.5.1 erzeugt werden.", font=font(18), fill=MUTED)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUTPUT, quality=95, dpi=(150, 150))
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.1-concept-v06",
        "status": "PASS_CONCEPT_EVIDENCE_REVIEW_REQUIRED",
        "artifact": str(OUTPUT.relative_to(PRODUCT)),
        "artifact_sha256": sha256(OUTPUT),
        "parameter_sources": {
            str(MARKER_PARAMETERS.relative_to(PRODUCT)): sha256(MARKER_PARAMETERS),
            str(ADDRESS_SOURCE.relative_to(PRODUCT)): sha256(ADDRESS_SOURCE),
            str(PALETTE_PARAMETERS.relative_to(PRODUCT)): sha256(PALETTE_PARAMETERS),
        },
        "brand_assets": {
            str(BRAND_SVG.relative_to(REPO)): sha256(BRAND_SVG),
            str(BRAND_PREVIEW.relative_to(REPO)): sha256(BRAND_PREVIEW),
            str(BRAND_PROVENANCE.relative_to(REPO)): sha256(BRAND_PROVENANCE),
            str(BRAND_MANIFEST.relative_to(REPO)): sha256(BRAND_MANIFEST),
        },
        "address_coordinate_epsg25833": coordinate,
        "resolved_panel_coordinates_mm": address["resolved_panel_coordinates_mm"],
        "marker_size_mm": [width_mm, height_mm],
        "marker_relief_mm": marker["relief"]["height_above_highest_local_face_mm"],
        "semantic_tool": marker["relief"]["semantic_tool"],
        "fit_clearances_mm": FIT,
        "minimum_brand_clear_space_mm": width_mm / 4,
        "minimum_source_component_dimension_mm": marker["relief"]["minimum_source_component_dimension_mm"],
        "recognition_distance_target_mm": marker["viewing_intent"]["recognition_distance_mm"],
        "concept_marker_pixel_bounds": {"boundary_crop": crop_bbox, "context_outline": context_bbox},
        "map_redesign": False,
        "limitations": [
            "visual concept only",
            "no revision 0.5.1 production geometry or 3MF generated before approval",
            "display colors are approximations, not calibrated filament measurements",
            "2 m recognition is a physical human sight-test target, not proven by this render",
            "official address data verifies location, not company occupancy",
            "brand clearance remains open",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
