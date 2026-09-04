#!/usr/bin/env python3
"""Render the MM-ART-010 v0.5.2 water/transit concept approval sheet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, shape
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
REPO = PRODUCT.parents[2]
BASE = PRODUCT / "source-data" / "v0.4.0" / "berlin"
SEMANTIC = PRODUCT / "source-data" / "v0.5.2" / "berlin"
ADDRESS = PRODUCT / "source-data" / "v0.5.0" / "berlin" / "metri-create-headquarters-address.json"
BRAND = REPO / "business" / "01-strategy" / "brand-assets" / "metrimade" / "exports" / "metrimade-lockup-stacked-color.png"
OUTPUT = PRODUCT / "concepts" / "berlin-water-transit-concept-v07.png"
REPORT = PRODUCT / "concepts" / "berlin-water-transit-concept-v07.json"

CANVAS = (2000, 1400)
WALL = "#ECE8DF"
CARD = "#FBF8F0"
INK = "#17232B"
MUTED = "#67635C"
OAK = "#C69A61"
MINT = "#78C7A1"
MIDNIGHT = "#182536"
SKY = "#54BCEB"
WATER_LIGHT = "#FFF5D8"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def features(path: Path) -> list[dict]:
    return json.loads(path.read_text())["features"]


def union(path: Path):
    geometries = [shape(feature["geometry"]) for feature in features(path) if feature.get("geometry")]
    return unary_union(geometries) if geometries else GeometryCollection()


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


def transformer(bounds, viewport, padding=0):
    minx, miny, maxx, maxy = bounds
    vx0, vy0, vx1, vy1 = viewport
    scale = min((vx1 - vx0 - 2 * padding) / (maxx - minx), (vy1 - vy0 - 2 * padding) / (maxy - miny))
    ox = vx0 + (vx1 - vx0 - (maxx - minx) * scale) / 2 - minx * scale
    oy = vy0 + (vy1 - vy0 - (maxy - miny) * scale) / 2 + maxy * scale
    return (lambda x, y: (round(ox + x * scale), round(oy - y * scale))), scale


def polygon_mask(size, geometry, point):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for poly in polygons(geometry):
        draw.polygon([point(x, y) for x, y in poly.exterior.coords], fill=255)
        for ring in poly.interiors:
            draw.polygon([point(x, y) for x, y in ring.coords], fill=0)
    return mask


def draw_lines(layer, source_features, point, color, width):
    draw = ImageDraw.Draw(layer)
    for feature in source_features:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        for line in line_sequences(geometry):
            points = [point(x, y) for x, y in line]
            if len(points) > 1:
                draw.line(points, fill=color, width=width, joint="curve")


def clipped_lines(canvas, mask, source_features, point, color, width):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw_lines(layer, source_features, point, color, width)
    clipped = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    clipped.paste(layer, mask=mask)
    canvas.alpha_composite(clipped)


def cut_water(canvas, land_mask, point, width_px):
    areas = union(SEMANTIC / "water-areas.geojson")
    water_mask = polygon_mask(canvas.size, areas, point)
    water_lines = Image.new("L", canvas.size, 0)
    draw_lines(water_lines, features(SEMANTIC / "water-lines.geojson"), point, 255, width_px)
    water_mask = Image.composite(Image.new("L", canvas.size, 255), water_mask, water_lines)
    water_mask = Image.composite(water_mask, Image.new("L", canvas.size, 0), land_mask)
    glow = water_mask.filter(ImageFilter.GaussianBlur(5))
    glow_layer = Image.new("RGBA", canvas.size, (255, 230, 150, 0))
    glow_layer.putalpha(glow.point(lambda value: round(value * 0.55)))
    canvas.alpha_composite(glow_layer)
    opening = Image.new("RGBA", canvas.size, WATER_LIGHT)
    canvas.paste(opening, mask=water_mask)


def draw_marker(canvas, point, scale, bounds, coordinate):
    center = point(*coordinate)
    source_width = bounds[2] - bounds[0]
    source_height = bounds[3] - bounds[1]
    panel_mm_per_source_m = min(600.0 / source_width, 400.0 / source_height)
    width_px = max(24, round(54.0 * scale / panel_mm_per_source_m))
    height_px = max(25, round(width_px * 57.176471 / 54.0))
    source = Image.open(BRAND).convert("RGBA")
    alpha = source.getchannel("A").resize((width_px, height_px), Image.Resampling.LANCZOS)
    mark = Image.new("RGBA", (width_px, height_px), SKY)
    mark.putalpha(alpha)
    canvas.alpha_composite(mark, (round(center[0] - width_px / 2), round(center[1] - height_px / 2)))


def draw_map(canvas, boundary, viewport, mode, coordinate):
    if mode == "boundary_crop":
        bounds = boundary.bounds
        point, scale = transformer(bounds, viewport, padding=18)
        land_mask = polygon_mask(canvas.size, boundary, point)
    else:
        minx, miny, maxx, maxy = boundary.bounds
        margin = 0.12
        bounds = (minx - (maxx - minx) * margin, miny - (maxy - miny) * margin, maxx + (maxx - minx) * margin, maxy + (maxy - miny) * margin)
        point, scale = transformer(bounds, viewport)
        land_mask = Image.new("L", canvas.size, 0)
        ImageDraw.Draw(land_mask).rounded_rectangle(viewport, radius=5, fill=255)

    canvas.paste(Image.new("RGBA", canvas.size, OAK), mask=land_mask)
    roads = features(BASE / "roads-major.geojson")
    clipped_lines(canvas, land_mask, roads, point, MINT, 8)
    clipped_lines(canvas, land_mask, roads, point, MIDNIGHT, 3)
    transit = features(SEMANTIC / "sbahn-routes.geojson") + features(SEMANTIC / "ubahn-routes.geojson")
    clipped_lines(canvas, land_mask, transit, point, SKY, 5)
    cut_water(canvas, land_mask, point, 5)

    if mode == "context_outline":
        outline = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(outline)
        for poly in polygons(boundary):
            draw.line([point(x, y) for x, y in poly.exterior.coords], fill=SKY, width=5, joint="curve")
        clipped = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        clipped.paste(outline, mask=land_mask)
        canvas.alpha_composite(clipped)

    draw_marker(canvas, point, scale, bounds, coordinate)
    seam_x = (bounds[0] + bounds[2]) / 2
    seam = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(seam).line([point(seam_x, bounds[1]), point(seam_x, bounds[3])], fill=(255, 255, 255, 100), width=2)
    clipped = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    clipped.paste(seam, mask=land_mask)
    canvas.alpha_composite(clipped)
    return point, scale, land_mask


def main() -> None:
    if OUTPUT.exists() or REPORT.exists():
        raise FileExistsError("Refusing to overwrite concept evidence")
    required = [
        BASE / "boundary.geojson",
        BASE / "roads-major.geojson",
        SEMANTIC / "water-areas.geojson",
        SEMANTIC / "water-lines.geojson",
        SEMANTIC / "sbahn-routes.geojson",
        SEMANTIC / "ubahn-routes.geojson",
        SEMANTIC / "concept-source-manifest.json",
        ADDRESS,
        BRAND,
    ]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    boundary = union(BASE / "boundary.geojson")
    address = json.loads(ADDRESS.read_text())["geocode"]["coordinate"]
    tegeler = next(
        shape(feature["geometry"])
        for feature in features(SEMANTIC / "water-areas.geojson")
        if feature.get("properties", {}).get("osm_id") == "451908"
    )

    image = Image.new("RGBA", CANVAS, WALL)
    draw = ImageDraw.Draw(image)
    draw.text((90, 45), "BERLIN · GEWÄSSER & ÖPNV", font=font(50, True), fill=INK)
    draw.text((92, 110), "Konzept v07 · alle kartierten Gewässer offen · Sky Blue = S-/U-Bahn", font=font(25), fill=MUTED)

    cards = [(65, 180, 965, 930), (1035, 180, 1935, 930)]
    for card in cards:
        draw.rounded_rectangle(card, radius=22, fill=CARD, outline="#D5CEC2", width=2)
    draw.text((105, 215), "A  NUR BERLIN", font=font(30, True), fill=INK)
    draw.text((1075, 215), "B  BERLIN MIT UMLAND", font=font(30, True), fill=INK)
    crop_point, crop_scale, crop_mask = draw_map(image, boundary, (115, 285, 915, 790), "boundary_crop", address)
    draw_map(image, boundary, (1085, 285, 1885, 790), "context_outline", address)

    draw = ImageDraw.Draw(image)
    draw.text((105, 810), "Wasserflächen + Flüsse/Kanäle/Bäche = echte Öffnungen", font=font(20, True), fill=INK)
    draw.text((105, 848), "Autobahn/Trunk bleibt Midnight; kein blaues Autobahn-Layer.", font=font(19), fill=MUTED)
    draw.text((105, 884), "600 × 400 mm · zwei permanente Hauptdrucke", font=font(19), fill=MUTED)
    draw.text((1075, 810), "Sky Blue = S-Bahn + U-Bahn + Berliner Grenzlinie + Standortlogo", font=font(20, True), fill=INK)
    draw.text((1075, 848), "Umland außerhalb des lokalen PBF ist hier nur Konzeptbereich.", font=font(19), fill=MUTED)
    draw.text((1075, 884), "Produktionsquelle muss den gesamten 12-%-Rand abdecken.", font=font(19), fill=MUTED)

    detail_card = (65, 970, 1230, 1325)
    legend_card = (1260, 970, 1935, 1325)
    draw.rounded_rectangle(detail_card, radius=20, fill=CARD, outline="#D5CEC2", width=2)
    draw.rounded_rectangle(legend_card, radius=20, fill=CARD, outline="#D5CEC2", width=2)
    draw.text((100, 1002), "PRÜFPUNKT · TEGELER SEE", font=font(25, True), fill=INK)
    detail_bounds = tegeler.buffer(1100).bounds
    detail_point, _ = transformer(detail_bounds, (100, 1055, 720, 1285), padding=10)
    detail_mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(detail_mask).rounded_rectangle((100, 1055, 720, 1285), radius=8, fill=255)
    image.paste(Image.new("RGBA", image.size, OAK), mask=detail_mask)
    roads = features(BASE / "roads-major.geojson")
    clipped_lines(image, detail_mask, roads, detail_point, MINT, 8)
    clipped_lines(image, detail_mask, roads, detail_point, MIDNIGHT, 3)
    transit = features(SEMANTIC / "sbahn-routes.geojson") + features(SEMANTIC / "ubahn-routes.geojson")
    clipped_lines(image, detail_mask, transit, detail_point, SKY, 5)
    tegeler_mask = polygon_mask(image.size, tegeler, detail_point)
    image.paste(Image.new("RGBA", image.size, WATER_LIGHT), mask=tegeler_mask)
    draw = ImageDraw.Draw(image)
    draw.text((755, 1065), "OSM relation 451908", font=font(20, True), fill=INK)
    draw.text((755, 1105), "im Quelldatensatz vorhanden", font=font(18), fill=MUTED)
    draw.text((755, 1140), "im Konzept als Lichtausschnitt", font=font(18), fill=MUTED)
    draw.text((755, 1175), "Produktions-Eval: nicht leer,", font=font(18), fill=MUTED)
    draw.text((755, 1208), "nicht stillschweigend entfernt", font=font(18), fill=MUTED)

    draw.text((1295, 1002), "MATERIAL-/FORMLOGIK", font=font(25, True), fill=INK)
    legend = [(OAK, "Oak · Grundplatte"), (MINT, "Mint Green · Flächenebene"), (MIDNIGHT, "Midnight · Straßennetz"), (SKY, "Sky Blue · S-/U-Bahn + Akzente"), (WATER_LIGHT, "Gewässer · kein Material / Durchlicht")]
    y = 1050
    for color, label in legend:
        draw.rounded_rectangle((1298, y, 1340, y + 32), radius=5, fill=color, outline="#B7B0A4")
        draw.text((1360, y + 2), label, font=font(18), fill=INK)
        y += 49

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUTPUT, quality=95, dpi=(150, 150))
    source_manifest = json.loads((SEMANTIC / "concept-source-manifest.json").read_text())
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.2-concept-v07",
        "status": "PASS_CONCEPT_EVIDENCE_REVIEW_REQUIRED",
        "artifact": str(OUTPUT.relative_to(PRODUCT)),
        "artifact_sha256": sha256(OUTPUT),
        "semantic_contract": source_manifest["semantic_contract"],
        "named_regression_fixtures": source_manifest["named_regression_fixtures"],
        "tool_count": 4,
        "geometry_generated": False,
        "manufacturing_3mf_generated": False,
        "previous_candidate_status": "REJECTED_SEMANTICALLY_INCONSISTENT",
        "limitations": source_manifest["limitations"] + [
            "display colors are uncalibrated visual approximations",
            "concept approval is required before CAD, mesh, and 3MF regeneration",
            "minimum ligaments and the 12-percent per-half opening cap are production constraints, not proven by this image",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
