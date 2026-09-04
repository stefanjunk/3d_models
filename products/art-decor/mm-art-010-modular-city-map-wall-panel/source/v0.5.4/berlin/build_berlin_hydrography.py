#!/usr/bin/env python3
"""Build MM-ART-010 revision 0.5.4 with complete, gate-checked hydrography.

Revision 0.5.3 produced a candidate whose own report claimed Tegeler See was
retained while the exported land base was 92.5% solid across the lake.  Three
independent defects caused that:

1.  The site-marker aperture keep-out ran in ``build_mode`` *after*
    ``raster_masks`` had already written the water accounting, so the regression
    gate measured an array that was not the one converted to geometry.
2.  The keep-out itself dilated the 54 mm marker by 12.0 mm although the marker
    is centred on the Tegel address, i.e. directly on Tegeler See.
3.  Functional keep-outs were axis-aligned bounding rectangles far larger than
    the rear-cutter footprints they protect, and the outer ligament of 5.0 mm
    deleted every water body that meets the panel outline.

This generator keeps the approved geometry chain and changes only the water
pipeline: exact functional footprints, a 2.5 mm outer ligament, a west-edge
marker anchor, a 2.0 mm marker support ring, and a fail-closed named-water gate
that runs on the final aperture array.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw
from scipy import ndimage
from shapely import affinity
from shapely.geometry import shape
from shapely.ops import unary_union
from skimage import morphology


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
WATER_GENERATOR = PRODUCT / "source" / "v0.5.3" / "berlin" / "build_berlin_water_transit.py"
PARAMETERS = HERE / "hydrography-parameters.json"
SITE_PARAMETERS = HERE / "site-marker-parameters.json"
SOURCE = PRODUCT / "source-data" / "v0.5.4" / "berlin"
COMPOSITE_BUILDER = PRODUCT / "source" / "v0.5.1" / "berlin" / "rebuild_composite_blender.py"

sys.path.insert(0, str(WATER_GENERATOR.parent))
_spec = importlib.util.spec_from_file_location("mm_art_010_water_v053", WATER_GENERATOR)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load revision 0.5.3 generator: {WATER_GENERATOR}")
WATER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WATER)

sha256 = WATER.sha256
MODE_AUDITS: dict[str, dict] = {}
ANCHOR_TRACE: dict[str, dict] = {}
CURRENT_MODE: dict[str, str] = {}
WATER_RASTER: dict[str, np.ndarray] = {}

REQUIRED_SOURCE_FILES = (
    "boundary.geojson",
    "roads-major.geojson",
    "water-areas.geojson",
    "water-areas-osm.geojson",
    "water-areas-berlin-official.geojson",
    "water-lines.geojson",
    "sbahn-routes.geojson",
    "ubahn-routes.geojson",
    "source-manifest.json",
)


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------


def polygon_mask(base, geometry, size, mm_to_px) -> Image.Image:
    """Rasterise polygons with per-polygon hole semantics.

    Drawing every exterior first and every interior afterwards lets the hole of
    one polygon erase a *different* polygon that legitimately lies inside it.
    The Berlin water union contains exactly that case, which is why revision
    0.5.3 opened 0.0% of Schlachtensee and 0.0% of Gross-Glienicker See while
    both are fully present in the frozen source.
    """
    width, height = size
    accumulator = np.zeros((height, width), dtype=bool)
    for polygon in base.polygons(geometry):
        exterior = [mm_to_px(x, y) for x, y in polygon.exterior.coords]
        if len(exterior) < 3:
            continue
        columns = [point[0] for point in exterior]
        rows = [point[1] for point in exterior]
        origin_x, origin_y = min(columns), min(rows)
        tile_width = max(columns) - origin_x + 1
        tile_height = max(rows) - origin_y + 1
        if tile_width <= 0 or tile_height <= 0:
            continue
        tile = Image.new("L", (tile_width, tile_height), 0)
        draw = ImageDraw.Draw(tile)
        draw.polygon([(x - origin_x, y - origin_y) for x, y in exterior], fill=255)
        for ring in polygon.interiors:
            hole = [mm_to_px(x, y) for x, y in ring.coords]
            if len(hole) >= 3:
                draw.polygon([(x - origin_x, y - origin_y) for x, y in hole], fill=0)
        x0, y0 = max(0, origin_x), max(0, origin_y)
        x1 = min(width, origin_x + tile_width)
        y1 = min(height, origin_y + tile_height)
        if x1 <= x0 or y1 <= y0:
            continue
        patch = np.asarray(tile, dtype=np.uint8) > 0
        accumulator[y0:y1, x0:x1] |= patch[y0 - origin_y : y1 - origin_y, x0 - origin_x : x1 - origin_x]
    return Image.fromarray((accumulator * 255).astype(np.uint8))


def socket_footprint_rects(x: float, y: float, clearance: float) -> list[tuple[float, float, float, float]]:
    """Exact rear socket-anchor cutter footprint, identical to BASE.rear_cutters."""
    return [
        (x - 8.0 - clearance, y - 5.0 - clearance, x, y + 5.0 + clearance),
        (x, y - 3.0 - clearance, x + 14.0 + clearance, y + 3.0 + clearance),
        (x + 10.5, y + 3.0, x + 13.5, y + 3.65 + clearance),
    ]


def connector_footprint_rects(y: float, clearance: float, seam_gap: float) -> list[tuple[float, float, float, float]]:
    """Exact rear seam-connector cutter footprint for both halves, in global mm."""
    throat = 4.0 / 2.0 + clearance
    well = 5.2 / 2.0 + clearance
    left_edge = 300.0 - seam_gap / 2.0
    right_edge = 300.0 + seam_gap / 2.0
    return [
        (left_edge - 9.0, y - throat, left_edge + 0.05, y + throat),
        (left_edge - 16.0 - clearance, y - well, left_edge - 9.0, y + well),
        (right_edge, y - throat, right_edge + 9.0, y + throat),
        (right_edge + 9.0, y - well, right_edge + 16.0 + clearance, y + well),
    ]


def named_official_geometries(transform: dict) -> dict[str, object]:
    """Official Berlin Gewaesserkarte polygons grouped by name, in panel mm."""
    scale = transform["uniform_scale_mm_per_source_m"]
    tx, ty = transform["translate_mm"]
    grouped: dict[str, list] = {}
    for feature in json.loads((SOURCE / "water-areas-berlin-official.geojson").read_text())["features"]:
        name = (feature.get("properties") or {}).get("gewname")
        geometry = feature.get("geometry")
        if not name or not geometry:
            continue
        polygon = shape(geometry)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        grouped.setdefault(name, []).append(polygon)
    return {
        name: affinity.translate(
            affinity.scale(unary_union(parts), xfact=scale, yfact=scale, origin=(0.0, 0.0)), tx, ty
        )
        for name, parts in grouped.items()
    }


def evaluate_final_water(base, mode: str, aperture: np.ndarray, outer: np.ndarray, parameters: dict) -> dict:
    """Measure the water actually opened by the array that becomes geometry."""
    pitch = base.RASTER_PITCH_MM
    cell = pitch**2
    _, placement = base.load_placement(mode)
    transform = placement["transform"]
    size = (round(600.0 / pitch), round(400.0 / pitch))

    def mm_to_px(x: float, y: float):
        return round(x / pitch), round((400.0 - y) / pitch)

    def raster(geometry) -> np.ndarray:
        return np.asarray(polygon_mask(base, geometry, size, mm_to_px), dtype=np.uint8) > 0

    regression = parameters["named_regression"]
    named = named_official_geometries(transform)
    production = WATER_RASTER.get(mode)
    if production is None:
        raise ValueError(f"{mode}: production water raster was not captured")

    def measure(geometry) -> dict:
        """Official outline coverage and, separately, coverage of the water we map.

        The official Gewaesserkarte outline of a lake includes its islands, which
        the production water union correctly excludes.  The gate therefore runs
        on the intersection with the production water - the geometry the
        pipeline is actually responsible for - while the plain official fraction
        stays visible so a source gap cannot hide behind the gate.
        """
        mask = raster(geometry) & outer
        in_panel = int(mask.sum())
        mapped_mask = mask & production
        mapped = int(mapped_mask.sum())
        opened = int(np.count_nonzero(mask & aperture))
        mapped_open = int(np.count_nonzero(mapped_mask & aperture))
        return {
            "present": in_panel > 0,
            "in_panel_area_mm2": in_panel * cell,
            "mapped_area_mm2": mapped * cell,
            "open_area_mm2": opened * cell,
            "open_fraction_of_official_outline": (opened / in_panel) if in_panel else 0.0,
            "open_fraction_of_mapped_water": (mapped_open / mapped) if mapped else 0.0,
        }

    records = []
    for name, geometry in sorted(named.items()):
        record = measure(geometry)
        if not record["present"]:
            continue
        record["name"] = name
        records.append(record)

    def fixture(names) -> dict:
        wanted = [names] if isinstance(names, str) else list(names)
        parts = [named[key] for key in wanted if key in named]
        if not parts:
            return {"present": False, "in_panel_area_mm2": 0.0, "mapped_area_mm2": 0.0,
                    "open_area_mm2": 0.0, "open_fraction_of_official_outline": 0.0,
                    "open_fraction_of_mapped_water": 0.0}
        return measure(unary_union(parts))

    fixtures = {}
    failures = []
    for key, config in regression["fixtures"].items():
        measured = fixture(config["gewname"])
        minimum = float(config["minimum_open_fraction"])
        measured["minimum_open_fraction"] = minimum
        measured["status"] = (
            "PASS"
            if measured["present"] and measured["open_fraction_of_mapped_water"] >= minimum
            else "FAIL"
        )
        if measured["status"] != "PASS":
            failures.append(
                f"{mode}/{key} mapped open fraction "
                f"{measured['open_fraction_of_mapped_water']:.4f} < {minimum}"
            )
        fixtures[key] = measured

    all_in_panel = int(production.sum())
    all_open = int(np.count_nonzero(production & aperture))
    aggregate = parameters["named_regression"]["aggregate"]
    named_in_panel = sum(record["mapped_area_mm2"] for record in records)
    named_open = sum(
        record["mapped_area_mm2"] * record["open_fraction_of_mapped_water"] for record in records
    )
    summary = {
        "all_water_in_panel_area_mm2": all_in_panel * cell,
        "all_water_open_area_mm2": all_open * cell,
        "all_water_open_fraction": (all_open / all_in_panel) if all_in_panel else 0.0,
        "named_water_in_panel_area_mm2": named_in_panel,
        "named_water_open_area_mm2": named_open,
        "named_water_open_fraction": (named_open / named_in_panel) if named_in_panel else 0.0,
    }
    minimum_all = float(aggregate[f"minimum_all_water_open_fraction_{mode}"])
    minimum_named = float(aggregate["minimum_named_water_open_fraction"])
    if summary["all_water_open_fraction"] < minimum_all:
        failures.append(f"{mode}/all_water {summary['all_water_open_fraction']:.4f} < {minimum_all}")
    if summary["named_water_open_fraction"] < minimum_named:
        failures.append(f"{mode}/named_water {summary['named_water_open_fraction']:.4f} < {minimum_named}")

    records.sort(key=lambda record: record["open_fraction_of_mapped_water"])
    reporting = float(aggregate.get("reporting_threshold_named_water", minimum_named))
    return {
        "measured_on": "final aperture raster after every keep-out, marker keep-out and topology bridge",
        "thresholds": {"all_water": minimum_all, "named_water": minimum_named},
        "summary": summary,
        "fixtures": fixtures,
        "named_water": records,
        "reporting_threshold_named_water": reporting,
        "named_water_below_threshold": [
            record for record in records
            if record["open_fraction_of_mapped_water"] < reporting
            and record["mapped_area_mm2"] >= 20.0
        ],
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


# --------------------------------------------------------------------------
# raster stage
# --------------------------------------------------------------------------


def make_raster_masks(base, parameters: dict):
    def raster_masks(mode: str, boundary, outer, placement):
        pitch = base.RASTER_PITCH_MM
        size = (round(600.0 / pitch), round(400.0 / pitch))
        transform = placement["transform"]
        scale = transform["uniform_scale_mm_per_source_m"]
        tx, ty = transform["translate_mm"]

        def mm_to_px(x: float, y: float):
            return round(x / pitch), round((400.0 - y) / pitch)

        def draw_polygon_mask(geometry):
            return polygon_mask(base, geometry, size, mm_to_px)

        outer_image = draw_polygon_mask(outer)

        def line_mask(path: Path, width_mm: float):
            image = Image.new("L", size, 0)
            draw = ImageDraw.Draw(image)
            for feature in json.loads(path.read_text())["features"]:
                geometry = feature.get("geometry")
                if not geometry:
                    continue
                for line in base.iter_line_coordinates(geometry):
                    points = [mm_to_px(x * scale + tx, y * scale + ty) for x, y in line]
                    if len(points) >= 2:
                        draw.line(points, fill=255, width=max(1, round(width_mm / pitch)), joint="curve")
            return ImageChops.multiply(image, outer_image)

        widths = parameters["network_widths_mm"]
        roads = SOURCE / "roads-major.geojson"
        mint = line_mask(roads, widths["mint_middle_relief"])
        midnight = line_mask(roads, widths["midnight_streets"])
        sky = ImageChops.lighter(
            line_mask(SOURCE / "sbahn-routes.geojson", widths["sky_blue_s_u_bahn"]),
            line_mask(SOURCE / "ubahn-routes.geojson", widths["sky_blue_s_u_bahn"]),
        )

        if mode == "context_outline":
            marker = Image.new("L", size, 0)
            draw = ImageDraw.Draw(marker)
            transformed_boundary = base.transform_geometry(boundary, transform)
            boundary_width = max(1, round(widths["sky_blue_context_boundary"] / pitch))
            for polygon in base.polygons(transformed_boundary):
                draw.line([mm_to_px(x, y) for x, y in polygon.exterior.coords], fill=255, width=boundary_width, joint="curve")
                for ring in polygon.interiors:
                    draw.line([mm_to_px(x, y) for x, y in ring.coords], fill=255, width=boundary_width, joint="curve")
            sky = ImageChops.lighter(sky, ImageChops.multiply(marker, outer_image))

        mint = ImageChops.lighter(mint, sky)
        midnight = ImageChops.lighter(midnight, sky)

        water_area_geometry = base.read_geojson(SOURCE / "water-areas.geojson")
        water_area_image = draw_polygon_mask(base.transform_geometry(water_area_geometry, transform))
        water_line_image = line_mask(SOURCE / "water-lines.geojson", parameters["water"]["line_opening_width_mm"])
        aperture_image = ImageChops.multiply(
            ImageChops.lighter(water_area_image, water_line_image), outer_image
        )

        outer_array = np.asarray(outer_image, dtype=np.uint8) > 0
        mint_array = np.asarray(mint, dtype=np.uint8) > 0
        midnight_array = np.asarray(midnight, dtype=np.uint8) > 0
        sky_array = np.asarray(sky, dtype=np.uint8) > 0
        aperture_array = np.asarray(aperture_image, dtype=np.uint8) > 0
        WATER_RASTER[mode] = (np.asarray(water_area_image, dtype=np.uint8) > 0) & outer_array

        color_edge_radius = max(1, round(base.UPPER_COLOR_EDGE_INSET_MM / pitch))
        upper_safe = morphology.erosion(outer_array, footprint=morphology.disk(color_edge_radius))
        seam_min = round((300.0 - base.SEAM_GAP_MM / 2.0 - base.UPPER_COLOR_EDGE_INSET_MM) / pitch)
        seam_max = round((300.0 + base.SEAM_GAP_MM / 2.0 + base.UPPER_COLOR_EDGE_INSET_MM) / pitch)
        upper_safe[:, seam_min : seam_max + 1] = False
        mint_array &= upper_safe
        midnight_array &= upper_safe
        sky_array &= upper_safe

        minimum_network_pixels = max(1, round(base.NETWORK["minimum_component_area_mm2"] / pitch**2))
        mint_array = morphology.remove_small_objects(mint_array, max_size=minimum_network_pixels - 1)
        midnight_array = morphology.remove_small_objects(midnight_array, max_size=minimum_network_pixels - 1)
        sky_array = morphology.remove_small_objects(sky_array, max_size=minimum_network_pixels - 1)

        source_water_pixels = int(aperture_array.sum())
        minimum_aperture_pixels = max(1, round(parameters["water"]["minimum_component_area_mm2"] / pitch**2))
        aperture_array = morphology.remove_small_objects(aperture_array, max_size=minimum_aperture_pixels - 1)
        after_minimum = int(aperture_array.sum())

        edge_radius = max(1, round(parameters["water"]["outer_ligament_mm"] / pitch))
        safe_array = morphology.erosion(outer_array, footprint=morphology.disk(edge_radius))
        aperture_array &= safe_array
        after_ligament = int(aperture_array.sum())

        # Retained rectangles: permanent centre seam band and the two title bars.
        protected = parameters["protected_geometry"]
        rectangle_image = Image.new("L", size, 255)
        rectangle_draw = ImageDraw.Draw(rectangle_image)
        for key in ("centre_seam_band_mm", "title_bar_left_mm", "title_bar_right_mm"):
            x0, y0, x1, y1 = protected["retained_rectangles"][key]
            rectangle_draw.rectangle([mm_to_px(x0, y1), mm_to_px(x1, y0)], fill=0)
        aperture_array &= np.asarray(rectangle_image, dtype=np.uint8) > 0
        after_rectangles = int(aperture_array.sum())

        # Exact functional footprints, dilated by the documented functional margin.
        footprint_image = Image.new("L", size, 0)
        footprint_draw = ImageDraw.Draw(footprint_image)
        connector_clearance = base.INTERFACE_PARAMETERS["connector"]["selected_provisional_clearance_per_side"]
        socket_clearance = base.INTERFACE_PARAMETERS["socket_anchor"]["selected_provisional_clearance_per_side"]
        rects: list[tuple[float, float, float, float]] = []
        for y in placement["connector_y_positions_mm"]:
            rects.extend(connector_footprint_rects(y, connector_clearance, base.SEAM_GAP_MM))
        for x, y in placement["socket_centers_global_mm"].values():
            rects.extend(socket_footprint_rects(x, y, socket_clearance))
        for x0, y0, x1, y1 in rects:
            footprint_draw.rectangle([mm_to_px(x0, y1), mm_to_px(x1, y0)], fill=255)
        footprint_array = np.asarray(footprint_image, dtype=np.uint8) > 0
        margin_px = max(1, round(float(protected["functional_margin_mm"]) / pitch))
        functional_keepout = morphology.dilation(footprint_array, footprint=morphology.disk(margin_px))
        aperture_array &= ~functional_keepout
        after_functional = int(aperture_array.sum())

        aperture_array, bridge_reports = WATER.bridge_aperture_islands(base, outer_array, aperture_array, pitch)
        after_bridges = int(aperture_array.sum())
        mint_array &= outer_array & ~aperture_array
        midnight_array &= mint_array
        sky_array &= midnight_array

        half_slices = {
            "left": slice(0, round(300.0 / pitch)),
            "right": slice(round(300.0 / pitch) + 1, outer_array.shape[1]),
        }
        aperture_components = {}
        for half, columns in half_slices.items():
            labels, count = ndimage.label(aperture_array[:, columns])
            maximum_span = 0.0
            for label in range(1, count + 1):
                rows, cols = np.where(labels == label)
                if len(rows):
                    maximum_span = max(
                        maximum_span,
                        (rows.max() - rows.min() + 1) * pitch,
                        (cols.max() - cols.min() + 1) * pitch,
                    )
            aperture_components[half] = {
                "component_count": int(count),
                "maximum_axis_aligned_span_mm": maximum_span,
            }

        cell = pitch**2
        MODE_AUDITS[mode] = {
            "aperture_stage_area_mm2": {
                "source_water_and_lines": source_water_pixels * cell,
                "after_minimum_component": after_minimum * cell,
                "after_outer_ligament": after_ligament * cell,
                "after_retained_rectangles": after_rectangles * cell,
                "after_exact_functional_keepouts": after_functional * cell,
                "after_topology_bridges": after_bridges * cell,
            },
            "functional_keepout_area_mm2": float(np.count_nonzero(functional_keepout & outer_array)) * cell,
            "functional_keepout_derivation": protected["derivation"],
            "outer_ligament_mm": parameters["water"]["outer_ligament_mm"],
            "reinforcement_candidates": bridge_reports,
            "aperture_components": aperture_components,
            "rear_grid": False,
            "blanket_rear_ribs": False,
            "physical_strength_claim": False,
        }
        return {
            "outer": outer_array,
            "nardo": mint_array,
            "black": midnight_array,
            "orange": sky_array,
            "apertures": aperture_array,
            "aperture_bridges": bridge_reports,
            "resolution_mm": pitch,
        }

    return raster_masks


# --------------------------------------------------------------------------
# marker anchor and the final fail-closed water gate
# --------------------------------------------------------------------------


def install_west_edge_anchor(previous, parameters: dict) -> None:
    original = previous.build_mode
    placement_cfg = json.loads(SITE_PARAMETERS.read_text())["site_marker"]["placement"]
    anchor = placement_cfg["anchor"]
    offset_mm = float(placement_cfg.get("anchor_offset_mm", 0.0)) if anchor == "artwork_west_edge" else 0.0

    def build_mode(mode, export_dir, validation_dir, artwork_mask, coordinate):
        CURRENT_MODE["mode"] = mode
        _, placement = previous.BASE.load_placement(mode)
        scale = placement["transform"]["uniform_scale_mm_per_source_m"]
        tx, ty = placement["transform"]["translate_mm"]
        shifted = [coordinate[0] + offset_mm / scale, coordinate[1]]
        ANCHOR_TRACE[mode] = {
            "anchor": anchor,
            "anchor_offset_mm": offset_mm,
            "address_coordinate_epsg25833": list(coordinate),
            "address_panel_mm": [coordinate[0] * scale + tx, coordinate[1] * scale + ty],
            "artwork_center_panel_mm": [shifted[0] * scale + tx, shifted[1] * scale + ty],
            "achieved_seam_clearance_mm": abs(300.0 - (shifted[0] * scale + tx))
            - float(placement_cfg["width_mm"]) / 2.0,
            "required_seam_clearance_mm": float(placement_cfg["minimum_clearance_to_center_seam_mm"]),
        }
        return original(mode, export_dir, validation_dir, artwork_mask, shifted)

    previous.build_mode = build_mode


def install_final_water_gate(previous, parameters: dict) -> None:
    original = previous.update_aperture_keepout

    def update_aperture_keepout(masks, marker_mask):
        pitch = previous.BASE.RASTER_PITCH_MM
        before = masks["apertures"].copy()
        result = original(masks, marker_mask)
        mode = CURRENT_MODE["mode"]
        removed = float(np.count_nonzero(before & ~masks["apertures"])) * pitch**2
        audit = evaluate_final_water(
            previous.BASE, mode, masks["apertures"], masks["outer"], parameters
        )
        audit["marker_keepout_removed_aperture_mm2"] = removed
        audit["marker_keepout_clearance_mm"] = previous.MARKER_APERTURE_CLEARANCE_MM
        audit["anchor"] = ANCHOR_TRACE.get(mode)
        MODE_AUDITS[mode]["final_water"] = audit
        MODE_AUDITS[mode]["aperture_stage_area_mm2"]["after_marker_keepout"] = float(
            masks["apertures"].sum()
        ) * pitch**2
        if audit["status"] != "PASS":
            raise ValueError(f"final water gate failed: {audit['failures']}")
        return result

    previous.update_aperture_keepout = update_aperture_keepout


# --------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    if not args.candidate.replace("-", "").isalnum():
        raise SystemExit("candidate must contain only letters, digits and hyphens")

    parameters = json.loads(PARAMETERS.read_text())
    if parameters.get("revision") != "0.5.4":
        raise SystemExit("parameters are not revision 0.5.4")

    manifest = json.loads((SOURCE / "source-manifest.json").read_text())
    if manifest.get("status") != "PASS":
        raise SystemExit("revision 0.5.4 source manifest is not PASS")
    missing = [name for name in REQUIRED_SOURCE_FILES if not (SOURCE / name).is_file()]
    if missing:
        raise SystemExit(f"missing source file(s): {missing}")

    sys.path.insert(0, str(WATER.PREVIOUS_GENERATOR.parent))
    legacy = WATER.load_module(WATER.PREVIOUS_GENERATOR, "mm_art_010_build_v054_legacy")
    previous = legacy.load_previous_generator()
    previous.BASE.BLENDER_COMPOSITE_SCRIPT = COMPOSITE_BUILDER
    WATER.install_subminimum_boolean_debris_filter(previous.BASE)
    legacy.install_revision_composite_repair(previous)
    WATER.install_serialized_tool_micro_repair(previous.BASE, legacy.repair_mesh)
    previous.BASE.SOURCE = SOURCE
    previous.BASE.LIGHT["maximum_open_area_fraction_per_half"] = float(
        parameters["water"]["maximum_open_area_fraction_per_half"]
    )
    previous.BASE.raster_masks = make_raster_masks(previous.BASE, parameters)
    previous.SITE_PARAMETERS_PATH = SITE_PARAMETERS
    previous.SITE_PARAMETERS = json.loads(SITE_PARAMETERS.read_text())
    previous.MARKER_APERTURE_CLEARANCE_MM = float(
        parameters["protected_geometry"]["site_marker_aperture_clearance_mm"]
    )
    previous.TOOL_LABEL.update({
        "bone-white": "Tool 1 — Oak land base",
        "nardo-grey": "Tool 2 — Mint Green middle relief",
        "black": "Tool 3 — Midnight street network",
        "orange": "Tool 4 — Sky Blue S/U transit, boundary and site marker",
    })
    install_west_edge_anchor(previous, parameters)
    install_final_water_gate(previous, parameters)

    coordinate, geocode_path, geocode = previous.load_location()
    artwork_mask, artwork_path, renderer = previous.render_artwork_mask()

    export_root = PRODUCT / "exports" / "v0.5.4" / "berlin" / args.candidate
    validation_root = PRODUCT / "validation" / "v0.5.4" / "berlin" / args.candidate
    if export_root.exists() or validation_root.exists():
        raise SystemExit("refusing destructive overwrite of an existing candidate directory")
    export_root.mkdir(parents=True)
    (validation_root / "renders").mkdir(parents=True)

    mode_reports = {}
    for mode in previous.MODES:
        mode_export = export_root / mode.replace("_", "-")
        mode_export.mkdir()
        mode_reports[mode] = previous.build_mode(
            mode, mode_export, validation_root / "renders", artwork_mask, coordinate
        )
        audit_path = validation_root / f"{mode.replace('_', '-')}-hydrography-accounting.json"
        audit_path.write_text(json.dumps(MODE_AUDITS[mode], indent=2, ensure_ascii=False) + "\n")
        final_water = MODE_AUDITS[mode]["final_water"]
        mode_reports[mode]["hydrography_accounting"] = {
            "path": str(audit_path.relative_to(PRODUCT)),
            "sha256": sha256(audit_path),
            "aperture_stage_area_mm2": MODE_AUDITS[mode]["aperture_stage_area_mm2"],
            "final_water_summary": final_water["summary"],
            "named_fixtures": final_water["fixtures"],
            "named_water_below_threshold": final_water["named_water_below_threshold"],
            "marker_anchor": ANCHOR_TRACE[mode],
            "reinforcement_candidates": MODE_AUDITS[mode]["reinforcement_candidates"],
            "aperture_components": MODE_AUDITS[mode]["aperture_components"],
            "status": final_water["status"],
        }
        if mode_reports[mode].get("status") == "PASS" and final_water["status"] != "PASS":
            mode_reports[mode]["status"] = "FAIL"

    status = "PASS" if all(report["status"] == "PASS" for report in mode_reports.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.4",
        "candidate": args.candidate,
        "status": status,
        "representation": (
            "two modes and two independently mounted halves with four named semantic tools; "
            "complete water openings behind exact functional footprints and logged topology bridges"
        ),
        "relaxed_guards_requiring_approval": {
            "maximum_open_area_fraction_per_half": {
                "value": parameters["water"]["maximum_open_area_fraction_per_half"],
                "previous": parameters["water"]["maximum_open_area_fraction_per_half_previous"],
                "reason": parameters["water"]["maximum_open_area_fraction_change_reason"],
            },
            "outer_ligament_mm": {
                "value": parameters["water"]["outer_ligament_mm"],
                "previous": parameters["water"]["outer_ligament_previous_mm"],
                "reason": parameters["water"]["outer_ligament_change_reason"],
            },
            "site_marker_aperture_clearance_mm": {
                "value": parameters["protected_geometry"]["site_marker_aperture_clearance_mm"],
                "previous": parameters["protected_geometry"]["site_marker_aperture_clearance_previous_mm"],
                "reason": parameters["protected_geometry"]["site_marker_aperture_clearance_reason"],
            },
            "site_marker_minimum_clearance_to_center_seam_mm": {
                "value": previous.SITE_PARAMETERS["site_marker"]["placement"]["minimum_clearance_to_center_seam_mm"],
                "previous": previous.SITE_PARAMETERS["site_marker"]["placement"]["minimum_clearance_to_center_seam_previous_mm"],
                "reason": previous.SITE_PARAMETERS["site_marker"]["placement"]["seam_clearance_change_reason"],
            },
        },
        "known_residual_conflicts": parameters["known_residual_conflicts"],
        "corrections_against_0_5_3": [
            "the named-water regression now runs on the final aperture array that becomes geometry, not on the pre-marker array",
            "the site marker anchors its west edge on the frozen address instead of its centre, freeing Tegeler See",
            "the marker aperture clearance is the 2.0 mm functional support ring instead of a generic 12.0 mm guard",
            "functional keep-outs are the exact rear-cutter footprints dilated by the documented margin instead of oversized rectangles",
            "the outer water ligament is 2.5 mm so border waters such as the Havel corridor are no longer deleted",
        ],
        "source_manifest": {
            "path": str((SOURCE / "source-manifest.json").relative_to(PRODUCT)),
            "sha256": sha256(SOURCE / "source-manifest.json"),
        },
        "parameters": {"path": str(PARAMETERS.relative_to(PRODUCT)), "sha256": sha256(PARAMETERS)},
        "site_marker_parameters": {"path": str(SITE_PARAMETERS.relative_to(PRODUCT)), "sha256": sha256(SITE_PARAMETERS)},
        "selected_palette": {
            "preset": previous.SELECTED_PALETTE,
            "tools": [previous.PALETTE[index] for index in sorted(previous.PALETTE)],
        },
        "tool_z_bands_mm": previous.BASE.Z_BANDS,
        "manufacturing_raster_pitch_mm": previous.BASE.RASTER_PITCH_MM,
        "serialized_tool_micro_repairs": WATER.TOOL_REPAIR_TRACES,
        "modes": mode_reports,
        "structural_decision": {
            "rear_grid": False,
            "blanket_rear_ribs": False,
            "gravity_load_path": "one upper support per half; center seam is not the primary gravity path",
            "selection": "least-material connected candidate per half",
            "strength_status": "digital connectivity only; physical handling and installed proof test required",
        },
        "site_marker": {
            "artwork": str(artwork_path.relative_to(PRODUCT.parents[2])),
            "artwork_sha256": sha256(artwork_path),
            "geocode": str(geocode_path.relative_to(PRODUCT)),
            "address_coordinate_epsg25833": coordinate,
            "address": geocode["address_input"],
            "anchor": ANCHOR_TRACE,
            "renderer": renderer,
        },
        "shared_secondary_parts": {
            "seam_connector": "exports/v0.3.0/interfaces/seam-connector-c025.stl",
            "upper_hanger": "exports/v0.3.0/interfaces/upper-hanger-18mm.stl",
            "lower_standoff": "exports/v0.3.0/interfaces/lower-standoff-18mm.stl",
        },
        "limitations": [
            "DRAFT digital candidate; digital connectivity is not a wall-load or stiffness claim.",
            "The reduced outer ligament and the relaxed marker seam clearance require human re-approval.",
            "Physical connector, handling, installed proof-load, opacity, lit appearance, ACE/purge, logo recognition, watermark, rights and release gates remain open.",
            "No printer upload or print start is performed.",
        ],
    }
    report_path = validation_root / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    (validation_root / "build-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "generator": str(Path(__file__).resolve().relative_to(PRODUCT)),
                "generator_sha256": sha256(Path(__file__).resolve()),
                "build_report": str(report_path.relative_to(PRODUCT)),
                "build_report_sha256": sha256(report_path),
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps({"status": status, "report": str(report_path), "export_root": str(export_root)}, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
