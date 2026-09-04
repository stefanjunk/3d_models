#!/usr/bin/env python3
"""Build MM-ART-010 revision 0.5.3 with complete water and S/U transit.

Revision 0.5.1 remains the marker, interface and mesh authority. This wrapper
replaces only the map semantic raster: water polygons plus water lines become
negative geometry, S/U route relations become tool 4, motorway/trunk stays in
tool 3, and detached land is prevented by the minimum logged bridge set.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageChops, ImageDraw
from scipy import ndimage
from shapely import affinity
from shapely.geometry import GeometryCollection, LineString, MultiLineString, box, shape
from shapely.ops import unary_union
from skimage import morphology


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PREVIOUS_GENERATOR = PRODUCT / "source" / "v0.5.1" / "berlin" / "build_berlin_metrimade_marker.py"
PARAMETERS = HERE / "water-transit-parameters.json"
SOURCE = PRODUCT / "source-data" / "v0.5.3" / "berlin"
COMPOSITE_BUILDER = PRODUCT / "source" / "v0.5.1" / "berlin" / "rebuild_composite_blender.py"
SITE_PARAMETERS = PRODUCT / "source" / "v0.5.1" / "berlin" / "site-marker-parameters.json"
MODE_AUDITS: dict[str, dict] = {}
TOOL_REPAIR_TRACES: dict[str, dict] = {}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_subminimum_boolean_debris_filter(base) -> None:
    """Allow the existing audited micro-repair to receive a clean main mesh.

    Blender can serialize isolated one-triangle Boolean debris below the approved
    0.9 mm minimum printable stroke. Such a face is neither a closed printable
    feature nor intended map geometry. Any larger, multi-face or volumetric
    rejected component remains a hard failure.
    """

    def rebuild_composite(color_paths, raw_path, final_path):
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(base.BLENDER), "--background", "--factory-startup", "--python",
            str(base.BLENDER_COMPOSITE_SCRIPT), "--", str(raw_path),
            *(str(path) for path in color_paths),
        ]
        result = subprocess.run(
            command,
            cwd=PRODUCT.parents[2],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if result.returncode != 0 or not raw_path.is_file():
            raise RuntimeError("Blender composite rebuild failed: " + (result.stderr or result.stdout)[-4000:])
        raw_mesh = trimesh.load_mesh(raw_path, process=True)
        parts = list(raw_mesh.split(only_watertight=False))
        qualified = [part for part in parts if part.is_watertight and part.volume > 1e-6]
        if len(qualified) != 1:
            raise ValueError(f"expected one positive watertight Blender component, got {len(qualified)}")
        rejected = [part for part in parts if id(part) != id(qualified[0])]
        rejected_details = []
        for part in rejected:
            extents = np.asarray(part.extents, dtype=float)
            detail = {
                "faces": int(len(part.faces)),
                "xy_max_extent_mm": float(max(extents[0], extents[1])),
                "z_extent_mm": float(extents[2]),
                "maximum_extent_mm": float(extents.max()),
                "abs_volume_mm3": abs(float(part.volume)),
            }
            rejected_details.append(detail)
            if detail["faces"] > 1 or detail["maximum_extent_mm"] > 0.9 or detail["abs_volume_mm3"] > 0.1:
                raise ValueError(f"Blender produced material rejected geometry: {detail}")
        qualified[0].export(final_path)
        return base.roundtrip_stl_metrics(final_path), {
            "backend": "Blender Manifold Boolean with fail-closed sub-0.9-mm one-triangle debris filter",
            "executable": str(base.BLENDER),
            "executable_sha256": base.sha256(base.BLENDER.resolve()),
            "script": str(base.BLENDER_COMPOSITE_SCRIPT.relative_to(PRODUCT)),
            "script_sha256": base.sha256(base.BLENDER_COMPOSITE_SCRIPT),
            "raw_path": str(raw_path.relative_to(PRODUCT)),
            "raw_sha256": base.sha256(raw_path),
            "raw_metrics": base.roundtrip_stl_metrics(raw_path),
            "rejected_component_count": len(rejected),
            "rejected_components": rejected_details,
            "stdout_tail": result.stdout[-2000:],
        }

    base.rebuild_composite = rebuild_composite


def install_serialized_tool_micro_repair(base, repair_mesh) -> None:
    """Repair only zero-area faces introduced by STL float32 serialization.

    The prior revision already audits the same topology-preserving one-ULP
    repair for composites. Apply it here to individual tool STLs only when
    every topology gate except a maximum of eight degenerate faces passes.
    A temporary serialization must pass before it replaces the newly generated
    candidate artifact.
    """

    original_metrics = base.roundtrip_stl_metrics

    def roundtrip_stl_metrics(path: Path):
        metrics = original_metrics(path)
        if "-tool" not in path.name or metrics["degenerate_faces"] == 0:
            return metrics
        required_preconditions = {
            "watertight": True,
            "positive_volume": True,
            "connected_components": 1,
            "boundary_edges": 0,
            "nonmanifold_edges": 0,
            "duplicate_faces": 0,
        }
        failed = {
            key: {"expected": expected, "actual": metrics.get(key)}
            for key, expected in required_preconditions.items()
            if metrics.get(key) != expected
        }
        if failed or metrics["degenerate_faces"] > 8:
            return metrics

        input_hash = sha256(path)
        source = trimesh.load_mesh(path, process=True)
        repaired, trace = repair_mesh(source)
        temporary_path = path.with_suffix(".micro-repair.tmp.stl")
        if temporary_path.exists():
            raise ValueError(
                f"refusing to overwrite temporary repair artifact: {temporary_path}"
            )
        repaired.export(temporary_path)
        repaired_metrics = original_metrics(temporary_path)
        required_final = {**required_preconditions, "degenerate_faces": 0}
        failed_final = {
            key: {"expected": expected, "actual": repaired_metrics.get(key)}
            for key, expected in required_final.items()
            if repaired_metrics.get(key) != expected
        }
        if failed_final:
            raise ValueError(f"serialized tool micro-repair failed: {failed_final}")
        temporary_path.replace(path)
        relative_path = str(path.relative_to(PRODUCT))
        TOOL_REPAIR_TRACES[relative_path] = {
            "status": "PASS",
            "scope": "individual semantic tool STL after float32 serialization",
            "input_sha256": input_hash,
            "input_metrics": metrics,
            "repair": trace,
            "output_sha256": sha256(path),
            "output_metrics": repaired_metrics,
        }
        return repaired_metrics

    base.roundtrip_stl_metrics = roundtrip_stl_metrics


def line_geometries(geometry):
    if isinstance(geometry, LineString):
        yield geometry
    elif isinstance(geometry, MultiLineString):
        yield from geometry.geoms
    elif hasattr(geometry, "geoms"):
        for child in geometry.geoms:
            yield from line_geometries(child)


def transformed_feature_geometry(feature: dict, transform: dict):
    geometry = shape(feature["geometry"])
    scale = transform["uniform_scale_mm_per_source_m"]
    tx, ty = transform["translate_mm"]
    return affinity.translate(
        affinity.scale(geometry, xfact=scale, yfact=scale, origin=(0.0, 0.0)),
        tx,
        ty,
    )


def bridge_aperture_islands(base, outer_array: np.ndarray, aperture_array: np.ndarray, pitch: float):
    """Restore only aperture pixels needed to join detached land to the main body."""

    result = aperture_array.copy()
    split_column = round(300.0 / pitch)
    domains = {
        "left": (slice(0, split_column), 0),
        "right": (slice(split_column + 1, outer_array.shape[1]), split_column + 1),
    }
    reports = {}
    width_mm = float(json.loads(PARAMETERS.read_text())["water"]["mandatory_topology_bridge_width_mm"])
    bridge_width_px = max(1, round(width_mm / pitch))
    for half, (column_slice, column_offset) in domains.items():
        outer_half = outer_array[:, column_slice]
        aperture_half = result[:, column_slice].copy()
        initial_pixels = int(aperture_half.sum())
        initial_components = int(ndimage.label(outer_half & ~aperture_half)[1])
        bridges = []
        while True:
            retained = outer_half & ~aperture_half
            labels, component_count = ndimage.label(retained)
            if component_count <= 1:
                break
            counts = np.bincount(labels.ravel())
            counts[0] = 0
            main_label = int(np.argmax(counts))
            secondary_labels = [value for value in range(1, component_count + 1) if value != main_label]
            secondary_label = max(secondary_labels, key=lambda value: counts[value])
            main = labels == main_label
            distance, nearest = ndimage.distance_transform_edt(~main, return_indices=True)
            coordinates = np.argwhere(labels == secondary_label)
            distances = distance[coordinates[:, 0], coordinates[:, 1]]
            source_row, source_column = coordinates[int(np.argmin(distances))]
            target_row = int(nearest[0, source_row, source_column])
            target_column = int(nearest[1, source_row, source_column])
            bridge_image = Image.new("L", (outer_half.shape[1], outer_half.shape[0]), 0)
            ImageDraw.Draw(bridge_image).line(
                [(int(source_column), int(source_row)), (target_column, target_row)],
                fill=255,
                width=bridge_width_px,
            )
            bridge = np.asarray(bridge_image, dtype=np.uint8) > 0
            restore = bridge & aperture_half & outer_half
            restored_pixels = int(restore.sum())
            if restored_pixels == 0:
                raise ValueError(f"cannot connect retained aperture island in {half} half")
            aperture_half[restore] = False
            source_global_column = int(source_column) + column_offset
            target_global_column = int(target_column) + column_offset
            source_mm = [source_global_column * pitch, 400.0 - int(source_row) * pitch]
            target_mm = [target_global_column * pitch, 400.0 - target_row * pitch]
            bridges.append({
                "id": f"{half}-bridge-{len(bridges) + 1:03d}",
                "half": half,
                "source_global_mm": source_mm,
                "target_global_mm": target_mm,
                "length_mm": math.dist(source_mm, target_mm),
                "width_mm": width_mm,
                "restored_area_mm2": restored_pixels * pitch**2,
                "reason": "connect_detached_land_component_to_primary_backer",
                "placement_preference": "shortest raster path across a narrow opening location",
            })
        result[:, column_slice] = aperture_half
        reports[half] = {
            "candidate_a_openings_only": {
                "retained_raster_components": initial_components,
                "connected": initial_components == 1,
            },
            "candidate_b_mandatory_topology_bridges": {
                "retained_raster_components": int(ndimage.label(outer_half & ~aperture_half)[1]),
                "connected": True,
                "bridge_count": len(bridges),
                "bridge_width_mm": width_mm,
                "restored_material_area_mm2": (initial_pixels - int(aperture_half.sum())) * pitch**2,
                "bridges": bridges,
            },
            "candidate_c_conditional_local_rear_ribs": {
                "generated": False,
                "reason": "candidate B is connected; rear ribs would compromise rear-datum-down printing and reserved halo lands",
            },
            "selected_candidate": "A_openings_only" if initial_components == 1 else "B_mandatory_topology_bridges",
            "bridge_count": len(bridges),
            "bridge_width_mm": width_mm,
            "restored_material_area_mm2": (initial_pixels - int(aperture_half.sum())) * pitch**2,
            "retained_raster_components": int(ndimage.label(outer_half & ~aperture_half)[1]),
        }
    return result, reports


def feature_window_mask(base, geometry, pitch: float, raster_shape: tuple[int, int], line_width_mm: float | None):
    if geometry.is_empty:
        return None
    min_x, min_y, max_x, max_y = geometry.bounds
    padding = max(2, math.ceil((line_width_mm or 0.0) / pitch) + 1)
    column0 = max(0, math.floor(min_x / pitch) - padding)
    column1 = min(raster_shape[1], math.ceil(max_x / pitch) + padding + 1)
    row0 = max(0, math.floor((400.0 - max_y) / pitch) - padding)
    row1 = min(raster_shape[0], math.ceil((400.0 - min_y) / pitch) + padding + 1)
    if column1 <= column0 or row1 <= row0:
        return None

    def point(x: float, y: float):
        return round(x / pitch) - column0, round((400.0 - y) / pitch) - row0

    image = Image.new("L", (column1 - column0, row1 - row0), 0)
    draw = ImageDraw.Draw(image)
    if line_width_mm is None:
        for polygon in base.polygons(geometry):
            draw.polygon([point(x, y) for x, y in polygon.exterior.coords], fill=255)
            for ring in polygon.interiors:
                draw.polygon([point(x, y) for x, y in ring.coords], fill=0)
    else:
        width_px = max(1, round(line_width_mm / pitch))
        for line in line_geometries(geometry):
            coordinates = [point(x, y) for x, y in line.coords]
            if len(coordinates) >= 2:
                draw.line(coordinates, fill=255, width=width_px, joint="curve")
    return (slice(row0, row1), slice(column0, column1)), np.asarray(image, dtype=np.uint8) > 0


def account_water_components(base, transform: dict, outer_array: np.ndarray, final_aperture: np.ndarray, pitch: float, line_width_mm: float):
    records = []
    layer_definitions = (
        ("water_area", SOURCE / "water-areas.geojson", None),
        ("water_line", SOURCE / "water-lines.geojson", line_width_mm),
    )
    for kind, path, width in layer_definitions:
        for feature in json.loads(path.read_text())["features"]:
            geometry = transformed_feature_geometry(feature, transform)
            window = feature_window_mask(base, geometry, pitch, outer_array.shape, width)
            properties = feature.get("properties", {})
            if window is None:
                outer_pixels = final_pixels = 0
            else:
                slices, mask = window
                outer_pixels = int(np.count_nonzero(mask & outer_array[slices]))
                final_pixels = int(np.count_nonzero(mask & final_aperture[slices]))
            if outer_pixels == 0:
                disposition = "outside_display_mode"
            elif final_pixels == 0:
                disposition = "removed_by_minimum_feature_or_protected_keepout"
            elif final_pixels < outer_pixels:
                disposition = "partially_retained_after_keepouts_and_topology_bridges"
            else:
                disposition = "retained_as_opening"
            records.append({
                "source_layer": kind,
                "osm_id": str(properties.get("osm_id") or properties.get("osm_way_id") or ""),
                "name": properties.get("name"),
                "source_pixels_inside_mode": outer_pixels,
                "final_opening_pixels": final_pixels,
                "final_opening_area_mm2": final_pixels * pitch**2,
                "disposition": disposition,
            })
    counts = {}
    for record in records:
        counts[record["disposition"]] = counts.get(record["disposition"], 0) + 1
    return records, counts


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
            image = Image.new("L", size, 0)
            draw = ImageDraw.Draw(image)
            for polygon in base.polygons(geometry):
                draw.polygon([mm_to_px(x, y) for x, y in polygon.exterior.coords], fill=255)
                for ring in polygon.interiors:
                    draw.polygon([mm_to_px(x, y) for x, y in ring.coords], fill=0)
            return image

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

        roads = SOURCE / "roads-major.geojson"
        sbahn = SOURCE / "sbahn-routes.geojson"
        ubahn = SOURCE / "ubahn-routes.geojson"
        widths = parameters["network_widths_mm"]
        mint = line_mask(roads, widths["mint_middle_relief"])
        midnight = line_mask(roads, widths["midnight_streets"])
        sky = ImageChops.lighter(
            line_mask(sbahn, widths["sky_blue_s_u_bahn"]),
            line_mask(ubahn, widths["sky_blue_s_u_bahn"]),
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

        # Higher tools need material beneath them. The support footprint belongs
        # to lower Z bands but the visible top remains Sky Blue.
        mint = ImageChops.lighter(mint, sky)
        midnight = ImageChops.lighter(midnight, sky)

        water_area_geometry = base.read_geojson(SOURCE / "water-areas.geojson")
        water_area_image = draw_polygon_mask(base.transform_geometry(water_area_geometry, transform))
        water_line_image = line_mask(SOURCE / "water-lines.geojson", parameters["water"]["line_opening_width_mm"])
        aperture_image = ImageChops.lighter(water_area_image, water_line_image)
        aperture_image = ImageChops.multiply(aperture_image, outer_image)

        outer_array = np.asarray(outer_image, dtype=np.uint8) > 0
        mint_array = np.asarray(mint, dtype=np.uint8) > 0
        midnight_array = np.asarray(midnight, dtype=np.uint8) > 0
        sky_array = np.asarray(sky, dtype=np.uint8) > 0
        aperture_array = np.asarray(aperture_image, dtype=np.uint8) > 0

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

        minimum_aperture_pixels = max(1, round(parameters["water"]["minimum_component_area_mm2"] / pitch**2))
        aperture_array = morphology.remove_small_objects(aperture_array, max_size=minimum_aperture_pixels - 1)
        edge_radius = max(1, round(parameters["water"]["outer_ligament_mm"] / pitch))
        safe = morphology.erosion(outer_array, footprint=morphology.disk(edge_radius))
        safe_image = Image.fromarray((safe * 255).astype(np.uint8))
        safe_draw = ImageDraw.Draw(safe_image)

        def exclude_rect(x0: float, y0: float, x1: float, y1: float):
            safe_draw.rectangle([mm_to_px(x0, y1), mm_to_px(x1, y0)], fill=0)

        exclude_rect(292.0, 0.0, 308.0, 400.0)
        keep = 12.0
        for y in placement["connector_y_positions_mm"]:
            exclude_rect(300.0 - keep - 17.0, y - keep, 300.0 + keep + 17.0, y + keep)
        for x, y in placement["socket_centers_global_mm"].values():
            exclude_rect(x - keep - 13.0, y - keep - 21.0, x + keep + 25.0, y + keep + 21.0)
        exclude_rect(20.0, 10.0, 150.0, 38.0)
        exclude_rect(450.0, 10.0, 580.0, 38.0)
        aperture_array &= np.asarray(safe_image, dtype=np.uint8) > 0

        aperture_array, bridge_reports = bridge_aperture_islands(base, outer_array, aperture_array, pitch)
        mint_array &= outer_array & ~aperture_array
        midnight_array &= mint_array
        sky_array &= midnight_array

        accounting, accounting_counts = account_water_components(
            base,
            transform,
            outer_array,
            aperture_array,
            pitch,
            parameters["water"]["line_opening_width_mm"],
        )
        tegeler = [record for record in accounting if record["source_layer"] == "water_area" and record["osm_id"] == "451908"]
        if len(tegeler) != 1 or tegeler[0]["final_opening_pixels"] <= 0:
            raise ValueError(f"{mode}: Tegeler See relation 451908 has no final opening")

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
                    maximum_span = max(maximum_span, (rows.max() - rows.min() + 1) * pitch, (cols.max() - cols.min() + 1) * pitch)
            aperture_components[half] = {"component_count": int(count), "maximum_axis_aligned_span_mm": maximum_span}

        MODE_AUDITS[mode] = {
            "water_component_accounting": accounting,
            "water_component_disposition_counts": accounting_counts,
            "tegeler_see": tegeler[0],
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    if not args.candidate.replace("-", "").isalnum():
        raise SystemExit("candidate must contain only letters, digits and hyphens")

    parameters = json.loads(PARAMETERS.read_text())
    if parameters.get("revision") != "0.5.3" or parameters.get("approval", {}).get("decomposition") != "approved":
        raise SystemExit("revision 0.5.3 parameters are not approved")
    sys.path.insert(0, str(PREVIOUS_GENERATOR.parent))
    legacy = load_module(PREVIOUS_GENERATOR, "mm_art_010_build_v053_legacy")
    previous = legacy.load_previous_generator()
    previous.BASE.BLENDER_COMPOSITE_SCRIPT = COMPOSITE_BUILDER
    install_subminimum_boolean_debris_filter(previous.BASE)
    legacy.install_revision_composite_repair(previous)
    install_serialized_tool_micro_repair(previous.BASE, legacy.repair_mesh)
    previous.BASE.SOURCE = SOURCE
    previous.BASE.raster_masks = make_raster_masks(previous.BASE, parameters)
    previous.SITE_PARAMETERS_PATH = SITE_PARAMETERS
    previous.SITE_PARAMETERS = json.loads(SITE_PARAMETERS.read_text())
    previous.TOOL_LABEL.update({
        "bone-white": "Tool 1 — Oak land base",
        "nardo-grey": "Tool 2 — Mint Green middle relief",
        "black": "Tool 3 — Midnight street network",
        "orange": "Tool 4 — Sky Blue S/U transit, boundary and site marker",
    })

    coordinate, geocode_path, geocode = previous.load_location()
    artwork_mask, artwork_path, renderer = previous.render_artwork_mask()
    required = [
        Path(__file__).resolve(), PREVIOUS_GENERATOR, PARAMETERS, SITE_PARAMETERS,
        COMPOSITE_BUILDER, previous.BASE_SCRIPT, previous.BASE.PARAMETERS_PATH,
        previous.BASE.INTERFACE_PARAMETERS_PATH, previous.BASE.BLENDER,
        previous.PALETTE_CATALOG_PATH, geocode_path, artwork_path,
        SOURCE / "source-manifest.json", *(SOURCE / name for name in (
            "boundary.geojson", "roads-major.geojson", "water-areas.geojson",
            "water-lines.geojson", "sbahn-routes.geojson", "ubahn-routes.geojson",
        )),
        previous.BASE.PLACEMENT_DIR / "boundary-crop-placement.json",
        previous.BASE.PLACEMENT_DIR / "context-outline-placement.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing source or gate input(s): {missing}")
    if json.loads((SOURCE / "source-manifest.json").read_text()).get("status") != "PASS":
        raise SystemExit("revision 0.5.3 source manifest is not PASS")

    export_root = PRODUCT / "exports" / "v0.5.3" / "berlin" / args.candidate
    validation_root = PRODUCT / "validation" / "v0.5.3" / "berlin" / args.candidate
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
        audit_path = validation_root / f"{mode.replace('_', '-')}-water-bridge-accounting.json"
        audit_path.write_text(json.dumps(MODE_AUDITS[mode], indent=2, ensure_ascii=False) + "\n")
        mode_reports[mode]["water_bridge_accounting"] = {
            "path": str(audit_path.relative_to(PRODUCT)),
            "sha256": sha256(audit_path),
            "disposition_counts": MODE_AUDITS[mode]["water_component_disposition_counts"],
            "tegeler_see_final_opening_area_mm2": MODE_AUDITS[mode]["tegeler_see"]["final_opening_area_mm2"],
            "reinforcement_candidates": MODE_AUDITS[mode]["reinforcement_candidates"],
            "aperture_components": MODE_AUDITS[mode]["aperture_components"],
        }

    status = "PASS" if all(report["status"] == "PASS" for report in mode_reports.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.3",
        "candidate": args.candidate,
        "status": status,
        "representation": "two modes and two independently mounted halves with four named semantic tools; all-water openings and minimum logged topology bridges",
        "source_manifest": {"path": str((SOURCE / "source-manifest.json").relative_to(PRODUCT)), "sha256": sha256(SOURCE / "source-manifest.json")},
        "parameters": {"path": str(PARAMETERS.relative_to(PRODUCT)), "sha256": sha256(PARAMETERS)},
        "site_marker_parameters": {"path": str(SITE_PARAMETERS.relative_to(PRODUCT)), "sha256": sha256(SITE_PARAMETERS)},
        "selected_palette": {"preset": previous.SELECTED_PALETTE, "tools": [previous.PALETTE[index] for index in sorted(previous.PALETTE)]},
        "tool_z_bands_mm": previous.BASE.Z_BANDS,
        "manufacturing_raster_pitch_mm": previous.BASE.RASTER_PITCH_MM,
        "serialized_tool_micro_repairs": TOOL_REPAIR_TRACES,
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
            "coordinate_epsg25833": coordinate,
            "address": geocode["address_input"],
            "renderer": renderer,
        },
        "shared_secondary_parts": {
            "seam_connector": "exports/v0.3.0/interfaces/seam-connector-c025.stl",
            "upper_hanger": "exports/v0.3.0/interfaces/upper-hanger-18mm.stl",
            "lower_standoff": "exports/v0.3.0/interfaces/lower-standoff-18mm.stl",
        },
        "limitations": [
            "DRAFT digital candidate; digital connectivity is not a wall-load or stiffness claim.",
            "Physical connector, handling, installed proof-load, opacity, lit appearance, ACE/purge, logo recognition, watermark, rights and release gates remain open.",
            "No printer upload or print start is performed.",
        ],
    }
    report_path = validation_root / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    manifest = {
        "schema_version": "1.0",
        "generator": str(Path(__file__).resolve().relative_to(PRODUCT)),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "build_report": str(report_path.relative_to(PRODUCT)),
        "build_report_sha256": sha256(report_path),
    }
    (validation_root / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(report_path), "export_root": str(export_root)}, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
