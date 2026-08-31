#!/usr/bin/env python3
"""Build the abstract four-color Berlin wall relief from frozen OSM vectors."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable, Iterator

import manifold3d as m3d
import numpy as np
import trimesh
from PIL import Image, ImageChops, ImageDraw
from scipy import ndimage
from skimage import measure, morphology
from shapely import affinity
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, box, shape
from shapely.geometry.polygon import orient
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PARAMS = json.loads((HERE / "berlin-parameters.json").read_text())
SOURCE = PRODUCT / "source-data" / "v0.3.0" / "berlin"
EXPORT = PRODUCT / "exports" / "v0.3.0" / "berlin"
VALIDATION = PRODUCT / "validation" / "v0.3.0" / "berlin"

# Reuse the approved family authority without copying interface geometry.
INTERFACE_DIR = PRODUCT / "source" / "v0.3.0"
sys.path.insert(0, str(INTERFACE_DIR))
from interface_geometry import PARAMS as INTERFACE_PARAMS  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_geojson(path: Path):
    data = json.loads(path.read_text())
    geoms = [shape(feature["geometry"]) for feature in data["features"] if feature.get("geometry")]
    return unary_union(geoms) if geoms else GeometryCollection()


def polygons(geom) -> Iterator[Polygon]:
    if geom.is_empty:
        return
    if isinstance(geom, Polygon):
        yield geom
    elif isinstance(geom, MultiPolygon):
        yield from geom.geoms
    elif hasattr(geom, "geoms"):
        for child in geom.geoms:
            yield from polygons(child)


def filter_polygons(geom, minimum_area: float):
    kept = [p for p in polygons(geom) if p.area >= minimum_area]
    return unary_union(kept) if kept else GeometryCollection()


def to_cross_section(geom) -> m3d.CrossSection:
    contours: list[np.ndarray] = []
    for poly in polygons(geom):
        fixed = orient(poly, sign=1.0)
        outer = np.asarray(fixed.exterior.coords[:-1], dtype=np.float64)
        if len(outer) >= 3:
            contours.append(outer)
        for ring in fixed.interiors:
            hole = np.asarray(ring.coords[:-1], dtype=np.float64)
            if len(hole) >= 3:
                contours.append(hole)
    return m3d.CrossSection(contours, m3d.FillRule.Positive)


def extrude(geom, z0: float, z1: float) -> m3d.Manifold:
    if geom.is_empty:
        return m3d.Manifold()
    return to_cross_section(geom).extrude(z1 - z0).translate((0.0, 0.0, z0))


def rect_manifold(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> m3d.Manifold:
    return extrude(box(x0, y0, x1, y1), z0, z1)


def extrude_cross_section(section: m3d.CrossSection, z0: float, z1: float) -> m3d.Manifold:
    if section.is_empty():
        return m3d.Manifold()
    return section.extrude(z1 - z0).translate((0.0, 0.0, z0))


def manifold_to_trimesh(manifold: m3d.Manifold) -> trimesh.Trimesh:
    mesh = manifold.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(mesh.vert_properties)[:, :3],
        faces=np.asarray(mesh.tri_verts),
        process=False,
    )


def rear_cutters(half: str, local_width: float) -> m3d.Manifold:
    c = INTERFACE_PARAMS["connector"]["selected_provisional_clearance_per_side"]
    cp = INTERFACE_PARAMS["connector"]
    throat_half = cp["body_outer_width"] / 2 + c
    well_half = cp["barb_outer_width"] / 2 + c
    depth = cp["z_thickness"] + c
    combined = m3d.Manifold()
    for y in INTERFACE_PARAMS["panel"]["connector_y_positions"]:
        if half == "left":
            combined += rect_manifold(local_width - 9.0, local_width + 0.05, y - throat_half, y + throat_half, -0.05, depth)
            combined += rect_manifold(local_width - 16.0 - c, local_width - 9.0, y - well_half, y + well_half, -0.05, depth)
        else:
            combined += rect_manifold(-0.05, 9.0, y - throat_half, y + throat_half, -0.05, depth)
            combined += rect_manifold(9.0, 16.0 + c, y - well_half, y + well_half, -0.05, depth)

    sp = INTERFACE_PARAMS["socket_anchor"]
    sc = sp["selected_provisional_clearance_per_side"]
    socket_depth = sp["head_z_thickness"] + sc
    global_centers = INTERFACE_PARAMS["panel"]["socket_centers_global"]
    x_shift = 0.0 if half == "left" else 300.125
    for xg, y, _kind in global_centers:
        if (half == "left" and xg >= 300.0) or (half == "right" and xg <= 300.0):
            continue
        x = xg - x_shift
        combined += rect_manifold(x - 8.0 - sc, x, y - 5.0 - sc, y + 5.0 + sc, -0.05, socket_depth)
        combined += rect_manifold(x, x + 14.0 + sc, y - 3.0 - sc, y + 3.0 + sc, -0.05, socket_depth)
        combined += rect_manifold(x + 10.5, x + 13.5, y + 3.0, y + 3.65 + sc, -0.05, socket_depth)
    return combined


def panel_transform(boundary):
    p = PARAMS["panel"]
    minx, miny, maxx, maxy = boundary.bounds
    usable_w = p["width"] - 2 * p["outer_border"]
    usable_h = p["height"] - 2 * p["outer_border"]
    scale = min(usable_w / (maxx - minx), usable_h / (maxy - miny))
    tx = p["outer_border"] + (usable_w - (maxx - minx) * scale) / 2 - minx * scale
    ty = p["outer_border"] + (usable_h - (maxy - miny) * scale) / 2 - miny * scale

    def apply(geom):
        return affinity.translate(affinity.scale(geom, xfact=scale, yfact=scale, origin=(0, 0)), tx, ty)

    return apply, {"uniform_scale_mm_per_source_m": scale, "translate_mm": [tx, ty]}


def color_and_aperture_geometry():
    p = PARAMS
    boundary_src = read_geojson(SOURCE / "boundary.geojson")
    roads_src = read_geojson(SOURCE / "roads-major.geojson")
    accent_src = read_geojson(SOURCE / "roads-accent.geojson")
    rail_src = read_geojson(SOURCE / "rail.geojson")
    water_src = read_geojson(SOURCE / "waterways.geojson")
    apply, transform_record = panel_transform(boundary_src)

    boundary = apply(boundary_src)
    roads = apply(roads_src).intersection(boundary).simplify(p["network_widths"]["line_simplification"])
    rail = apply(rail_src).intersection(boundary).simplify(p["network_widths"]["line_simplification"])
    accent = apply(accent_src).intersection(boundary).simplify(p["network_widths"]["line_simplification"])
    water = apply(water_src).intersection(boundary).simplify(p["network_widths"]["line_simplification"])
    frame = box(p["panel"]["outer_border"], p["panel"]["outer_border"], p["panel"]["width"] - p["panel"]["outer_border"], p["panel"]["height"] - p["panel"]["outer_border"])

    network = unary_union([roads, rail])
    nardo = network.buffer(p["network_widths"]["nardo_buffer"], resolution=3).intersection(frame)
    black = network.buffer(p["network_widths"]["black_buffer"], resolution=3).intersection(nardo)
    orange = accent.buffer(p["network_widths"]["orange_buffer"], resolution=3).intersection(black)
    minimum_area = p["network_widths"]["minimum_component_area"]
    nardo = filter_polygons(nardo.simplify(p["network_widths"]["polygon_simplification"], preserve_topology=True), minimum_area)
    black = filter_polygons(black.simplify(p["network_widths"]["polygon_simplification"], preserve_topology=True), minimum_area).intersection(nardo)
    orange = filter_polygons(orange.simplify(p["network_widths"]["polygon_simplification"], preserve_topology=True), minimum_area).intersection(black)

    light_p = p["light_apertures"]
    apertures = water.buffer(light_p["waterway_radius"], resolution=4)
    apertures = apertures.buffer(light_p["ligament_closing_radius"], resolution=3).buffer(-light_p["ligament_closing_radius"], resolution=3)
    safe = frame.difference(box(300.0 - light_p["seam_keepout_half_width"], 0, 300.0 + light_p["seam_keepout_half_width"], 400.0))
    fk = light_p["functional_keepout_half_width"]
    for y in INTERFACE_PARAMS["panel"]["connector_y_positions"]:
        safe = safe.difference(box(300.0 - fk, y - fk, 300.0 + fk, y + fk))
    for x, y, _kind in INTERFACE_PARAMS["panel"]["socket_centers_global"]:
        safe = safe.difference(box(x - fk - 5.0, y - fk - 5.0, x + fk + 20.0, y + fk + 5.0))
    apertures = filter_polygons(apertures.intersection(safe), 6.0)

    # All visible bodies inherit the same negative light paths.
    nardo = nardo.difference(apertures)
    black = black.difference(apertures)
    orange = orange.difference(apertures)
    return {
        "boundary": boundary,
        "nardo": nardo,
        "black": black,
        "orange": orange,
        "apertures": apertures,
        "transform": transform_record,
    }


def localize(geom, x_shift: float):
    return affinity.translate(geom, xoff=-x_shift)


def draw_geometry(image: Image.Image, geom, color: str, scale: int = 2) -> None:
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    for poly in polygons(geom):
        exterior = [(round(x * scale), round((400.0 - y) * scale)) for x, y in poly.exterior.coords]
        draw.polygon(exterior, fill=255)
        for ring in poly.interiors:
            hole = [(round(x * scale), round((400.0 - y) * scale)) for x, y in ring.coords]
            draw.polygon(hole, fill=0)
    layer = Image.new("RGB", image.size, color)
    image.paste(layer, mask=mask)


def _iter_line_coordinates(geometry: dict) -> Iterable[list[list[float]]]:
    kind = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if kind == "LineString":
        yield coords
    elif kind == "MultiLineString":
        yield from coords
    elif kind == "GeometryCollection":
        for child in geometry.get("geometries", []):
            yield from _iter_line_coordinates(child)


def raster_color_and_aperture_masks(resolution_mm: float = 0.25):
    """Rasterize vectors at sub-line-width resolution before contour rebuild.

    The immutable OSM vectors remain authoritative. The raster is a protected
    manufacturing master chosen to cap memory and mesh complexity at a pitch
    well below the 0.45 mm target extrusion width.
    """
    width_px = int(round(PARAMS["panel"]["width"] / resolution_mm))
    height_px = int(round(PARAMS["panel"]["height"] / resolution_mm))
    size = (width_px, height_px)
    boundary_src = read_geojson(SOURCE / "boundary.geojson")
    apply, transform_record = panel_transform(boundary_src)
    transform_record["manufacturing_raster_pitch_mm"] = resolution_mm
    boundary = apply(boundary_src)

    def mm_to_px(x: float, y: float) -> tuple[int, int]:
        return (int(round(x / resolution_mm)), int(round((PARAMS["panel"]["height"] - y) / resolution_mm)))

    boundary_mask = Image.new("L", size, 0)
    boundary_draw = ImageDraw.Draw(boundary_mask)
    for poly in polygons(boundary):
        boundary_draw.polygon([mm_to_px(x, y) for x, y in poly.exterior.coords], fill=255)
        for ring in poly.interiors:
            boundary_draw.polygon([mm_to_px(x, y) for x, y in ring.coords], fill=0)

    frame_mask = Image.new("L", size, 0)
    frame_draw = ImageDraw.Draw(frame_mask)
    border = PARAMS["panel"]["outer_border"]
    frame_draw.rectangle([mm_to_px(border, 400.0 - border), mm_to_px(600.0 - border, border)], fill=255)
    legal_map_mask = ImageChops.multiply(boundary_mask, frame_mask)

    def line_mask(path: Path, width_mm: float) -> Image.Image:
        image = Image.new("L", size, 0)
        draw = ImageDraw.Draw(image)
        data = json.loads(path.read_text())
        scale = transform_record["uniform_scale_mm_per_source_m"]
        tx, ty = transform_record["translate_mm"]
        line_width = max(1, int(round(width_mm / resolution_mm)))
        for feature in data["features"]:
            geom = feature.get("geometry")
            if not geom:
                continue
            for line in _iter_line_coordinates(geom):
                points = [mm_to_px(x * scale + tx, y * scale + ty) for x, y in line]
                if len(points) >= 2:
                    draw.line(points, fill=255, width=line_width, joint="curve")
        return ImageChops.multiply(image, legal_map_mask)

    nw = PARAMS["network_widths"]
    nardo = ImageChops.lighter(
        line_mask(SOURCE / "roads-major.geojson", 2 * nw["nardo_buffer"]),
        line_mask(SOURCE / "rail.geojson", 2 * nw["nardo_buffer"]),
    )
    black = ImageChops.lighter(
        line_mask(SOURCE / "roads-major.geojson", 2 * nw["black_buffer"]),
        line_mask(SOURCE / "rail.geojson", 2 * nw["black_buffer"]),
    )
    orange = line_mask(SOURCE / "roads-accent.geojson", 2 * nw["orange_buffer"])
    lp = PARAMS["light_apertures"]
    apertures = line_mask(SOURCE / "waterways.geojson", 2 * lp["waterway_radius"])

    nardo_a = np.asarray(nardo, dtype=np.uint8) > 0
    black_a = np.asarray(black, dtype=np.uint8) > 0
    orange_a = np.asarray(orange, dtype=np.uint8) > 0
    aperture_a = np.asarray(apertures, dtype=np.uint8) > 0
    radius_px = max(1, int(round(lp["ligament_closing_radius"] / resolution_mm)))
    aperture_a = ndimage.binary_closing(aperture_a, structure=morphology.disk(radius_px))
    minimum_pixels = max(1, int(round(6.0 / (resolution_mm * resolution_mm))))
    aperture_a = morphology.remove_small_objects(aperture_a, max_size=minimum_pixels - 1)

    safe = np.asarray(frame_mask, dtype=np.uint8) > 0
    safe_image = Image.fromarray((safe * 255).astype(np.uint8), mode="L")
    safe_draw = ImageDraw.Draw(safe_image)

    def exclude_rect(x0: float, y0: float, x1: float, y1: float) -> None:
        safe_draw.rectangle([mm_to_px(x0, y1), mm_to_px(x1, y0)], fill=0)

    seam_keepout = lp["seam_keepout_half_width"]
    exclude_rect(300.0 - seam_keepout, 0, 300.0 + seam_keepout, 400.0)
    fk = lp["functional_keepout_half_width"]
    for y in INTERFACE_PARAMS["panel"]["connector_y_positions"]:
        exclude_rect(300.0 - fk, y - fk, 300.0 + fk, y + fk)
    for x, y, _kind in INTERFACE_PARAMS["panel"]["socket_centers_global"]:
        exclude_rect(x - fk - 5.0, y - fk - 5.0, x + fk + 20.0, y + fk + 5.0)
    aperture_a &= np.asarray(safe_image, dtype=np.uint8) > 0

    # Enforce semantic nesting and common negative light paths exactly.
    black_a &= nardo_a
    orange_a &= black_a
    nardo_a &= ~aperture_a
    black_a &= ~aperture_a
    orange_a &= ~aperture_a
    return {
        "nardo": nardo_a,
        "black": black_a,
        "orange": orange_a,
        "apertures": aperture_a,
        "transform": transform_record,
        "resolution_mm": resolution_mm,
    }


def mask_to_cross_section(mask: np.ndarray, resolution_mm: float) -> m3d.CrossSection:
    padded = np.pad(mask.astype(np.uint8), 1)
    raw = measure.find_contours(padded, 0.5, fully_connected="high")
    contours: list[np.ndarray] = []
    height_mm = PARAMS["panel"]["height"]
    for contour in raw:
        contour = measure.approximate_polygon(contour, tolerance=0.65)
        if len(contour) < 4:
            continue
        rows = contour[:, 0] - 1.0
        cols = contour[:, 1] - 1.0
        xy = np.column_stack((cols * resolution_mm, height_mm - rows * resolution_mm))
        if len(xy) >= 3:
            contours.append(xy.astype(np.float64))
    return m3d.CrossSection(contours, m3d.FillRule.EvenOdd).simplify(0.03)


def save_raster_preview(masks: dict, path: Path) -> None:
    def rgb(hex_color: str) -> tuple[int, int, int]:
        value = hex_color.lstrip("#")
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))

    h, w = masks["nardo"].shape
    pixels = np.empty((h, w, 3), dtype=np.uint8)
    pixels[:] = rgb(PARAMS["palette"]["Bone White"])
    pixels[masks["nardo"]] = rgb(PARAMS["palette"]["Nardo Grey"])
    pixels[masks["black"]] = rgb(PARAMS["palette"]["Black"])
    pixels[masks["orange"]] = rgb(PARAMS["palette"]["Orange"])
    pixels[masks["apertures"]] = (255, 200, 87)
    image = Image.fromarray(pixels, mode="RGB").resize((1200, 800), Image.Resampling.LANCZOS)
    image.save(path)


def main() -> None:
    EXPORT.mkdir(parents=True, exist_ok=True)
    (VALIDATION / "renders").mkdir(parents=True, exist_ok=True)
    masks = raster_color_and_aperture_masks()
    p = PARAMS
    z = p["z_bands"]
    seam_gap = p["panel"]["seam_gap"]
    half_defs = {"left": (0.0, 300.0 - seam_gap / 2), "right": (300.0 + seam_gap / 2, 600.0)}
    global_sections = {
        name: mask_to_cross_section(masks[name], masks["resolution_mm"])
        for name in ("nardo", "black", "orange", "apertures")
    }
    artifacts = []
    half_reports = {}
    for half, (x0, x1) in half_defs.items():
        shift = x0
        local_width = x1 - x0
        half_global = m3d.CrossSection.square((local_width, 400.0)).translate((x0, 0.0))
        local_sections = {
            name: (section ^ half_global).translate((-shift, 0.0))
            for name, section in global_sections.items()
        }
        full_local = m3d.CrossSection.square((local_width, 400.0))
        body_sections = {
            "bone-white": full_local - local_sections["apertures"],
            "nardo-grey": local_sections["nardo"],
            "black": local_sections["black"],
            "orange": local_sections["orange"],
        }
        manifolds = {
            "bone-white": extrude_cross_section(body_sections["bone-white"], *z["Bone White"]) - rear_cutters(half, local_width),
            "nardo-grey": extrude_cross_section(body_sections["nardo-grey"], *z["Nardo Grey"]),
            "black": extrude_cross_section(body_sections["black"], *z["Black"]),
            "orange": extrude_cross_section(body_sections["orange"], *z["Orange"]),
        }
        composite = m3d.Manifold()
        color_reports = {}
        for name, manifold in manifolds.items():
            out = EXPORT / f"berlin-{half}-{name}.stl"
            mesh = manifold_to_trimesh(manifold)
            mesh.export(out)
            artifacts.append(out)
            color_reports[name] = {
                "area_mm2": body_sections[name].area(),
                "vertices": int(manifold.num_vert()),
                "triangles": int(manifold.num_tri()),
                "volume_mm3": float(manifold.volume()),
                "watertight": bool(mesh.is_watertight),
                "sha256": sha256(out),
            }
            composite += manifold
        composite_path = EXPORT / f"berlin-{half}-composite.stl"
        composite_mesh = manifold_to_trimesh(composite)
        composite_mesh.export(composite_path)
        artifacts.append(composite_path)
        aperture_fraction = local_sections["apertures"].area() / (local_width * 400.0)
        half_reports[half] = {
            "local_width_mm": local_width,
            "aperture_area_mm2": local_sections["apertures"].area(),
            "aperture_fraction": aperture_fraction,
            "aperture_limit": p["light_apertures"]["maximum_open_area_fraction_per_half"],
            "colors": color_reports,
            "composite": {
                "vertices": int(composite.num_vert()),
                "triangles": int(composite.num_tri()),
                "volume_mm3": float(composite.volume()),
                "watertight": bool(composite_mesh.is_watertight),
                "bounds_mm": composite_mesh.bounds.tolist(),
                "sha256": sha256(composite_path),
            },
        }

    preview_path = VALIDATION / "renders" / "berlin-top-color-and-light-preview.png"
    save_raster_preview(masks, preview_path)
    artifacts.append(preview_path)

    source_paths = [
        SOURCE / "berlin-snapshot.osm.pbf",
        SOURCE / "boundary.geojson",
        SOURCE / "roads-major.geojson",
        SOURCE / "roads-accent.geojson",
        SOURCE / "rail.geojson",
        SOURCE / "waterways.geojson",
    ]
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.3.0",
        "status": "PASS" if all(h["composite"]["watertight"] and h["aperture_fraction"] <= h["aperture_limit"] for h in half_reports.values()) else "FAIL",
        "source_crs": "EPSG:4326",
        "working_crs": "EPSG:25833",
        "panel_transform": masks["transform"],
        "palette": p["palette"],
        "z_bands_mm": z,
        "source_artifacts": [{"path": str(path.relative_to(PRODUCT)), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in source_paths],
        "halves": half_reports,
        "global": {
            "aperture_area_mm2": global_sections["apertures"].area(),
            "nardo_area_mm2": global_sections["nardo"].area(),
            "black_area_mm2": global_sections["black"].area(),
            "orange_area_mm2": global_sections["orange"].area(),
            "manufacturing_raster_pitch_mm": masks["resolution_mm"],
            "named_color_body_count": 8,
            "global_color_changes_intended": 3,
            "dithering": False,
        },
        "limitations": [
            "The preview is a top-color/light-path diagram, not a slicer preview or lit physical photograph.",
            "The 0.25 mm interface clearance is provisional until the physical coupon selects a winner.",
            "Final ACE slot mapping, purge tower, seam, first layer and aperture survival require destination-slicer human review.",
        ],
    }
    report_path = VALIDATION / "berlin-build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    artifacts.append(report_path)
    manifest = {
        "schema_version": "1.0",
        "generator": str(Path(__file__).relative_to(PRODUCT)),
        "generator_sha256": sha256(Path(__file__)),
        "parameters": str((HERE / "berlin-parameters.json").relative_to(PRODUCT)),
        "parameters_sha256": sha256(HERE / "berlin-parameters.json"),
        "interface_source": str((INTERFACE_DIR / "interface_geometry.py").relative_to(PRODUCT)),
        "interface_source_sha256": sha256(INTERFACE_DIR / "interface_geometry.py"),
        "interface_parameters_sha256": sha256(INTERFACE_DIR / "interface-parameters.json"),
        "artifacts": [{"path": str(path.relative_to(PRODUCT)), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(artifacts)],
    }
    manifest_path = VALIDATION / "berlin-build-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "halves": half_reports, "manifest": str(manifest_path)}))


if __name__ == "__main__":
    main()
