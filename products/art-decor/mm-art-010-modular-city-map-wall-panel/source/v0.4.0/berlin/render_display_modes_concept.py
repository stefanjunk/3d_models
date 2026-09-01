#!/usr/bin/env python3
"""Render the two Berlin display-mode concepts from frozen project vectors.

This script creates visual gate evidence only. It deliberately does not create
manufacturing geometry or imply that the existing Berlin-only extract is large
enough for the context-mode production build.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, shape
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
SOURCE = PRODUCT / "source-data" / "v0.3.0" / "berlin"
PARAMETER_SOURCE = HERE / "display-mode-parameters.json"
PARAMETERS = json.loads(PARAMETER_SOURCE.read_text())
OUTPUT = PRODUCT / "concepts" / "berlin-display-modes-concept-v03.png"
REPORT = PRODUCT / "concepts" / "berlin-display-modes-concept-v03.json"

CANVAS = (1800, 1120)
WALL = "#F4F0E8"
CARD = "#FCFAF5"
INK = "#242321"
MUTED = "#68645D"
PALETTE = PARAMETERS["shared"]["palette"]
PALETTE_LABELS = PARAMETERS["shared"].get("palette_labels", {name: name for name in PALETTE})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_union(name: str):
    data = json.loads((SOURCE / name).read_text())
    geometries = [shape(feature["geometry"]) for feature in data["features"] if feature.get("geometry")]
    return unary_union(geometries) if geometries else GeometryCollection()


def load_features(name: str):
    return json.loads((SOURCE / name).read_text())["features"]


def polygons(geometry):
    if geometry.is_empty:
        return
    if isinstance(geometry, Polygon):
        yield geometry
    elif isinstance(geometry, MultiPolygon):
        yield from geometry.geoms
    elif hasattr(geometry, "geoms"):
        for child in geometry.geoms:
            yield from polygons(child)


def line_sequences(geometry: dict):
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates", [])
    if kind == "LineString":
        yield coordinates
    elif kind == "MultiLineString":
        yield from coordinates
    elif kind == "GeometryCollection":
        for child in geometry.get("geometries", []):
            yield from line_sequences(child)


def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def transformer(bounds, viewport, padding: int = 0):
    minx, miny, maxx, maxy = bounds
    vx0, vy0, vx1, vy1 = viewport
    width = maxx - minx
    height = maxy - miny
    scale = min((vx1 - vx0 - 2 * padding) / width, (vy1 - vy0 - 2 * padding) / height)
    ox = vx0 + (vx1 - vx0 - width * scale) / 2 - minx * scale
    oy = vy0 + (vy1 - vy0 - height * scale) / 2 + maxy * scale

    def point(x, y):
        return (round(ox + x * scale), round(oy - y * scale))

    return point, scale


def polygon_mask(size, geometry, point):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for poly in polygons(geometry):
        draw.polygon([point(x, y) for x, y in poly.exterior.coords], fill=255)
        for ring in poly.interiors:
            draw.polygon([point(x, y) for x, y in ring.coords], fill=0)
    return mask


def draw_network(layer, features, point, color, width):
    draw = ImageDraw.Draw(layer)
    for feature in features:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        for line in line_sequences(geometry):
            points = [point(x, y) for x, y in line]
            if len(points) >= 2:
                draw.line(points, fill=color, width=width, joint="curve")


def draw_clipped_network(base, mask, point, widths):
    network = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_network(network, load_features("roads-major.geojson"), point, PALETTE["Nardo Grey"], widths[0])
    draw_network(network, load_features("rail.geojson"), point, PALETTE["Black"], widths[1])
    draw_network(network, load_features("roads-major.geojson"), point, PALETTE["Black"], widths[1])
    draw_network(network, load_features("roads-accent.geojson"), point, PALETTE["Orange"], widths[2])
    clipped = Image.new("RGBA", base.size, (0, 0, 0, 0))
    clipped.paste(network, mask=mask)
    base.alpha_composite(clipped)


def draw_boundary_crop(canvas, boundary, viewport):
    point, scale = transformer(boundary.bounds, viewport, padding=22)
    mask = polygon_mask(canvas.size, boundary, point)

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shifted = Image.new("L", canvas.size, 0)
    shifted.paste(mask, (8, 12))
    glow = shifted.filter(ImageFilter.GaussianBlur(16))
    shadow.paste((72, 55, 35, 90), mask=glow)
    canvas.alpha_composite(shadow)

    face = Image.new("RGBA", canvas.size, PALETTE["Bone White"])
    canvas.paste(face, mask=mask)
    draw_clipped_network(canvas, mask, point, (6, 3, 3))

    waterways = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw_network(waterways, load_features("waterways.geojson"), point, "#FFF4D4", 4)
    clipped_water = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    clipped_water.paste(waterways, mask=mask)
    canvas.alpha_composite(clipped_water)

    minx, _, maxx, _ = boundary.bounds
    seam_x = (minx + maxx) / 2
    seam = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    seam_draw = ImageDraw.Draw(seam)
    seam_draw.line([point(seam_x, boundary.bounds[1]), point(seam_x, boundary.bounds[3])], fill=(80, 76, 70, 120), width=2)
    clipped_seam = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    clipped_seam.paste(seam, mask=mask)
    canvas.alpha_composite(clipped_seam)
    return scale


def draw_context_outline(canvas, boundary, viewport, margin_ratio):
    minx, miny, maxx, maxy = boundary.bounds
    width = maxx - minx
    height = maxy - miny
    bounds = (
        minx - width * margin_ratio,
        miny - height * margin_ratio,
        maxx + width * margin_ratio,
        maxy + height * margin_ratio,
    )
    point, scale = transformer(bounds, viewport, padding=0)
    x0, y0, x1, y1 = viewport
    card_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(card_mask).rounded_rectangle(viewport, radius=5, fill=255)

    face = Image.new("RGBA", canvas.size, PALETTE["Bone White"])
    canvas.paste(face, mask=card_mask)

    berlin_mask = polygon_mask(canvas.size, boundary, point)
    tint = Image.new("RGBA", canvas.size, (115, 119, 122, 28))
    clipped_tint = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    clipped_tint.paste(tint, mask=berlin_mask)
    canvas.alpha_composite(clipped_tint)
    draw_clipped_network(canvas, card_mask, point, (5, 3, 2))

    boundary_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    boundary_draw = ImageDraw.Draw(boundary_layer)
    outline_px = max(4, round(2.4 * scale / (600.0 / (x1 - x0))))
    for poly in polygons(boundary):
        boundary_draw.line([point(x, y) for x, y in poly.exterior.coords], fill=PALETTE["Orange"], width=outline_px, joint="curve")
    clipped_boundary = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    clipped_boundary.paste(boundary_layer, mask=card_mask)
    canvas.alpha_composite(clipped_boundary)

    seam_x = (bounds[0] + bounds[2]) / 2
    seam = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(seam).line([point(seam_x, bounds[1]), point(seam_x, bounds[3])], fill=(80, 76, 70, 110), width=2)
    clipped_seam = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    clipped_seam.paste(seam, mask=card_mask)
    canvas.alpha_composite(clipped_seam)
    ImageDraw.Draw(canvas).rounded_rectangle(viewport, radius=5, outline="#CDC6BA", width=2)
    return bounds, scale


def main():
    boundary = load_union("boundary.geojson")
    if boundary.is_empty:
        raise RuntimeError("Berlin boundary source is empty")
    if OUTPUT.exists() or REPORT.exists():
        raise FileExistsError("Refusing to overwrite concept evidence")

    image = Image.new("RGBA", CANVAS, WALL)
    draw = ImageDraw.Draw(image)
    draw.text((90, 55), "BERLIN · ZWEI DARSTELLUNGSMODI", font=font(52, True), fill=INK)
    draw.text((92, 120), "Vier Farben · zwei permanente Druckteile · Halo-/Durchlicht vorbereitet", font=font(25), fill=MUTED)

    cards = [(70, 190, 865, 910), (935, 190, 1730, 910)]
    for card in cards:
        draw.rounded_rectangle(card, radius=22, fill=CARD, outline="#DDD6CA", width=2)

    draw.text((105, 225), "A  NUR BERLIN", font=font(31, True), fill=INK)
    draw.text((105, 270), "display_mode = boundary_crop", font=font(20), fill=MUTED)
    draw.text((970, 225), "B  BERLIN MIT UMLAND", font=font(31, True), fill=INK)
    draw.text((970, 270), "display_mode = context_outline", font=font(20), fill=MUTED)

    crop_view = (120, 330, 815, 770)
    context_view = (1000, 340, 1665, 783)
    crop_scale = draw_boundary_crop(image, boundary, crop_view)
    margin_ratio = PARAMETERS["modes"]["context_outline"]["context_margin_ratio"]["default"]
    context_bounds, context_scale = draw_context_outline(image, boundary, context_view, margin_ratio)

    draw = ImageDraw.Draw(image)
    draw.text((105, 800), "Außenkontur = Berliner Landesgrenze", font=font(22, True), fill=INK)
    draw.text((105, 837), "Kein Material und keine gedruckte Freifläche außerhalb Berlins.", font=font(19), fill=MUTED)
    draw.text((105, 870), "Max. Hüllmaß 600 × 400 mm; reale Silhouette bleibt unregelmäßig.", font=font(19), fill=MUTED)

    draw.text((970, 800), "Rechteck = vollständiger Umland-Ausschnitt", font=font(22, True), fill=INK)
    boundary_name = PALETTE_LABELS.get("Orange", "Orange")
    draw.text((970, 837), f"{boundary_name} = Berliner Landesgrenze als eigener Reliefzug (2,4 mm).", font=font(19), fill=MUTED)
    draw.text((970, 870), "Standard-Umlandrand 12 % je Seite; einstellbar von 5–30 %.", font=font(19), fill=MUTED)

    draw.text((92, 955), "FARBLOGIK", font=font(22, True), fill=INK)
    x = 245
    for name, color in PALETTE.items():
        draw.rounded_rectangle((x, 948, x + 42, 990), radius=6, fill=color, outline="#B9B1A5")
        draw.text((x + 55, 952), PALETTE_LABELS.get(name, name), font=font(19), fill=INK)
        x += 300

    footer = PARAMETERS.get(
        "concept_footer",
        "Konzeptdarstellung, keine Fertigungszeichnung. Für Modus B wird vor CAD ein größerer, eingefrorener Berlin/Brandenburg-Quelldatensatz benötigt.",
    )
    draw.text((92, 1030), footer, font=font(18), fill=MUTED)
    draw.text((92, 1063), "Die senkrechte Linie zeigt die vorgesehene Teilung in zwei dauerhafte Hauptdrucke; Beleuchtung bleibt ein optionales Kunden-Add-on.", font=font(18), fill=MUTED)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUTPUT, quality=95, dpi=(150, 150))
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": PARAMETERS["revision"],
        "status": "PASS",
        "artifact": str(OUTPUT.relative_to(PRODUCT)),
        "artifact_sha256": sha256(OUTPUT),
        "parameter_source": str(PARAMETER_SOURCE.relative_to(PRODUCT)),
        "parameter_source_sha256": sha256(PARAMETER_SOURCE),
        "frozen_inputs": {
            name: sha256(SOURCE / name)
            for name in ["boundary.geojson", "roads-major.geojson", "roads-accent.geojson", "rail.geojson", "waterways.geojson"]
        },
        "display_modes": ["boundary_crop", "context_outline"],
        "crop_source_units_per_pixel": 1.0 / crop_scale,
        "context_source_bounds": list(context_bounds),
        "context_source_units_per_pixel": 1.0 / context_scale,
        "limitations": PARAMETERS.get(
            "concept_limitations",
            [
                "visual concept only",
                "the existing Berlin-only extract does not qualify the context-mode production extent",
                "rear interfaces and light apertures are not dimensionally depicted",
            ],
        ),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
