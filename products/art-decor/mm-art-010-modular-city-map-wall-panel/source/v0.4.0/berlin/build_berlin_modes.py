#!/usr/bin/env python3
"""Build both approved abstract Berlin display modes as four-color FDM solids."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections.abc import Iterable, Iterator
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh
from PIL import Image, ImageChops, ImageDraw
from scipy import ndimage
from shapely import affinity
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, box, shape
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from skimage import measure, morphology

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PARAMETERS_PATH = HERE / "production-mode-parameters.json"
PARAMETERS = json.loads(PARAMETERS_PATH.read_text())
SOURCE = PRODUCT / "source-data" / "v0.4.0" / "berlin"
INTERFACE_DIR = PRODUCT / "source" / "v0.3.0"
INTERFACE_PARAMETERS_PATH = INTERFACE_DIR / "interface-parameters.json"
INTERFACE_PARAMETERS = json.loads(INTERFACE_PARAMETERS_PATH.read_text())
PLACEMENT_DIR = HERE / "placements"
BLENDER = Path("/usr/bin/blender")
BLENDER_COMPOSITE_SCRIPT = HERE / "rebuild_composite_blender.py"

MODES = ("boundary_crop", "context_outline")
COLORS = ("bone-white", "nardo-grey", "black", "orange")
COLOR_LABELS = {
    "bone-white": "Bone White",
    "nardo-grey": "Nardo Grey",
    "black": "Black",
    "orange": "Orange",
}
PALETTE = PARAMETERS["shared"]["palette"]
Z_BANDS = {
    "bone-white": [0.0, 3.0],
    "nardo-grey": [3.0, 3.6],
    "black": [3.6, 4.2],
    "orange": [4.2, 4.6],
}
NETWORK = {
    "nardo_width_mm": 3.2,
    "black_width_mm": 2.1,
    "orange_width_mm": 1.5,
    "minimum_component_area_mm2": 0.8,
}
LIGHT = {
    "waterway_width_mm": 2.2,
    "minimum_component_area_mm2": 6.0,
    "ligament_closing_radius_mm": 2.5,
    "outer_ligament_mm": 5.0,
    "seam_keepout_half_width_mm": 8.0,
    "functional_keepout_mm": 12.0,
    "maximum_open_area_fraction_per_half": 0.12,
    "island_bridge_width_mm": 2.0,
}
RASTER_PITCH_MM = 0.25
SEAM_GAP_MM = 0.25
OUTER_MIN_COMPONENT_AREA_MM2 = 6.0
UPPER_COLOR_EDGE_INSET_MM = 0.5
MESH_SIMPLIFY_TOLERANCE_MM = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_geojson(path: Path):
    data = json.loads(path.read_text())
    geometries = [shape(feature["geometry"]) for feature in data["features"] if feature.get("geometry")]
    return unary_union(geometries) if geometries else GeometryCollection()


def polygons(geometry) -> Iterator[Polygon]:
    if geometry.is_empty:
        return
    if isinstance(geometry, Polygon):
        yield geometry
    elif isinstance(geometry, MultiPolygon):
        yield from geometry.geoms
    elif hasattr(geometry, "geoms"):
        for child in geometry.geoms:
            yield from polygons(child)


def to_cross_section(geometry) -> m3d.CrossSection:
    contours: list[np.ndarray] = []
    for polygon in polygons(geometry):
        fixed = orient(polygon, sign=1.0)
        outer = np.asarray(fixed.exterior.coords[:-1], dtype=np.float64)
        if len(outer) >= 3:
            contours.append(outer)
        for ring in fixed.interiors:
            hole = np.asarray(ring.coords[:-1], dtype=np.float64)
            if len(hole) >= 3:
                contours.append(hole)
    return m3d.CrossSection(contours, m3d.FillRule.Positive)


def extrude_section(section: m3d.CrossSection, z0: float, z1: float) -> m3d.Manifold:
    if section.is_empty():
        return m3d.Manifold()
    return section.extrude(z1 - z0).translate((0.0, 0.0, z0))


def rect_manifold(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> m3d.Manifold:
    return extrude_section(to_cross_section(box(x0, y0, x1, y1)), z0, z1)


def manifold_to_trimesh(manifold: m3d.Manifold) -> trimesh.Trimesh:
    mesh = manifold.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(mesh.vert_properties)[:, :3],
        faces=np.asarray(mesh.tri_verts),
        process=False,
    )


def roundtrip_stl_metrics(path: Path) -> dict[str, int | float | bool | list]:
    """Audit the serialized STL representation, not only the in-memory mesh."""

    raw = trimesh.load_mesh(path, process=False)
    vertices = np.asarray(raw.vertices, dtype=np.float64)
    faces = np.asarray(raw.faces, dtype=np.int64)
    unique_vertices, inverse = np.unique(vertices, axis=0, return_inverse=True)
    mesh = trimesh.Trimesh(
        vertices=unique_vertices, faces=inverse[faces], process=False
    )
    mesh.remove_unreferenced_vertices()
    edge_counts = np.bincount(
        mesh.edges_unique_inverse, minlength=len(mesh.edges_unique)
    )
    area_threshold = max(float(mesh.area), 1.0) * np.finfo(float).eps * 100.0
    degenerate_faces = int(np.count_nonzero(mesh.area_faces <= area_threshold))
    canonical_faces = np.sort(np.asarray(mesh.faces, dtype=np.int64), axis=1)
    return {
        "vertices": len(mesh.vertices),
        "triangles": len(mesh.faces),
        "watertight": bool(mesh.is_watertight),
        "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
        "connected_components": len(mesh.split(only_watertight=False)),
        "boundary_edges": int(np.count_nonzero(edge_counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(edge_counts > 2)),
        "degenerate_faces": degenerate_faces,
        "duplicate_faces": int(
            len(canonical_faces) - len(np.unique(canonical_faces, axis=0))
        ),
        "volume_mm3": float(mesh.volume),
        "bounds_mm": mesh.bounds.tolist(),
    }


def rebuild_composite(
    color_paths: list[Path], raw_path: Path, final_path: Path
) -> tuple[dict, dict]:
    """Union color solids in Blender and retain only one qualified main body."""

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(BLENDER),
        "--background",
        "--factory-startup",
        "--python",
        str(BLENDER_COMPOSITE_SCRIPT),
        "--",
        str(raw_path),
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
        raise RuntimeError(
            "Blender composite rebuild failed: "
            + (result.stderr or result.stdout)[-4000:]
        )

    raw_mesh = trimesh.load_mesh(raw_path, process=True)
    parts = list(raw_mesh.split(only_watertight=False))
    qualified = [part for part in parts if part.is_watertight and part.volume > 1e-6]
    qualified_ids = {id(part) for part in qualified}
    rejected = [part for part in parts if id(part) not in qualified_ids]
    if len(qualified) != 1:
        raise ValueError(
            f"expected one positive watertight Blender component, got {len(qualified)}"
        )
    rejected_max_extent = max(
        (float(part.extents.max()) for part in rejected if len(part.vertices)),
        default=0.0,
    )
    rejected_abs_volume = sum(abs(float(part.volume)) for part in rejected)
    if rejected_max_extent > 0.1 or rejected_abs_volume > 0.001:
        raise ValueError(
            "Blender produced a material rejected component: "
            f"max_extent={rejected_max_extent}, abs_volume={rejected_abs_volume}"
        )
    qualified[0].export(final_path)
    final_metrics = roundtrip_stl_metrics(final_path)
    trace = {
        "backend": "Blender Manifold Boolean",
        "executable": str(BLENDER),
        "executable_sha256": sha256(BLENDER.resolve()),
        "script": str(BLENDER_COMPOSITE_SCRIPT.relative_to(PRODUCT)),
        "script_sha256": sha256(BLENDER_COMPOSITE_SCRIPT),
        "raw_path": str(raw_path.relative_to(PRODUCT)),
        "raw_sha256": sha256(raw_path),
        "raw_metrics": roundtrip_stl_metrics(raw_path),
        "rejected_component_count": len(rejected),
        "rejected_face_count": sum(len(part.faces) for part in rejected),
        "rejected_max_extent_mm": rejected_max_extent,
        "rejected_abs_volume_mm3": rejected_abs_volume,
        "stdout_tail": result.stdout[-2000:],
    }
    return final_metrics, trace


def transform_geometry(geometry, record):
    scale = record["uniform_scale_mm_per_source_m"]
    tx, ty = record["translate_mm"]
    return affinity.translate(
        affinity.scale(geometry, xfact=scale, yfact=scale, origin=(0.0, 0.0)), tx, ty
    )


def load_placement(mode: str):
    path = PLACEMENT_DIR / (mode.replace("_", "-") + "-placement.json")
    data = json.loads(path.read_text())
    if data["status"] != "PASS":
        raise ValueError(f"placement manifest is not PASS: {path}")
    return path, data


def outer_geometry(mode: str, boundary, placement):
    if mode == "boundary_crop":
        # Preserve the authoritative perimeter within 0.06 mm physical error;
        # raster approximation is used only for semantic masks.  Sub-6 mm2
        # detached source slivers cannot form a useful printed wall-art body.
        transformed = transform_geometry(boundary, placement["transform"]).simplify(
            0.06, preserve_topology=True
        )
        # Clip at the real seam before filtering.  A concave perimeter can
        # otherwise leave sub-nozzle slivers on one side of the split even
        # though the unsplit city polygon is globally connected.
        retained: list[Polygon] = []
        for x0, x1 in (
            (0.0, 300.0 - SEAM_GAP_MM / 2.0),
            (300.0 + SEAM_GAP_MM / 2.0, 600.0),
        ):
            clipped = transformed.intersection(box(x0, 0.0, x1, 400.0))
            retained.extend(
                polygon
                for polygon in polygons(clipped)
                if polygon.area >= OUTER_MIN_COMPONENT_AREA_MM2
            )
        return unary_union(retained)
    return box(0.0, 0.0, 600.0, 400.0)


def bridge_aperture_islands(
    outer_array: np.ndarray, aperture_array: np.ndarray, pitch: float
) -> tuple[np.ndarray, dict[str, dict[str, float | int]]]:
    """Restore narrow material bridges until each printable half is connected."""

    result = aperture_array.copy()
    split_column = round(300.0 / pitch)
    half_slices = {
        "left": slice(0, split_column),
        # Column 1200 is the raster representation of the protected 0.25 mm
        # physical seam gap.  Exclude it from both connectivity domains.
        "right": slice(split_column + 1, outer_array.shape[1]),
    }
    reports: dict[str, dict[str, float | int]] = {}
    bridge_width_px = max(1, round(LIGHT["island_bridge_width_mm"] / pitch))
    for half, column_slice in half_slices.items():
        outer_half = outer_array[:, column_slice]
        aperture_half = result[:, column_slice].copy()
        initial_aperture_pixels = int(aperture_half.sum())
        bridge_count = 0
        while True:
            retained = outer_half & ~aperture_half
            labels, component_count = ndimage.label(retained)
            if component_count <= 1:
                break
            counts = np.bincount(labels.ravel())
            counts[0] = 0
            main_label = int(np.argmax(counts))
            secondary_labels = [
                label
                for label in range(1, component_count + 1)
                if label != main_label
            ]
            secondary_label = max(secondary_labels, key=lambda label: counts[label])
            main = labels == main_label
            distance, nearest = ndimage.distance_transform_edt(
                ~main, return_indices=True
            )
            secondary_coordinates = np.argwhere(labels == secondary_label)
            distances = distance[
                secondary_coordinates[:, 0], secondary_coordinates[:, 1]
            ]
            source_row, source_column = secondary_coordinates[int(np.argmin(distances))]
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
            if not restore.any():
                raise ValueError(
                    f"cannot connect retained aperture island in {half} half"
                )
            aperture_half[restore] = False
            bridge_count += 1
        result[:, column_slice] = aperture_half
        final_components = ndimage.label(outer_half & ~aperture_half)[1]
        reports[half] = {
            "bridge_count": bridge_count,
            "bridge_width_mm": LIGHT["island_bridge_width_mm"],
            "restored_material_area_mm2": (
                initial_aperture_pixels - int(aperture_half.sum())
            )
            * pitch**2,
            "retained_raster_components": int(final_components),
        }
    return result, reports


def iter_line_coordinates(geometry: dict) -> Iterable[list[list[float]]]:
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates", [])
    if kind == "LineString":
        yield coordinates
    elif kind == "MultiLineString":
        yield from coordinates
    elif kind == "GeometryCollection":
        for child in geometry.get("geometries", []):
            yield from iter_line_coordinates(child)


def raster_masks(mode: str, boundary, outer, placement):
    pitch = RASTER_PITCH_MM
    width_px = round(600.0 / pitch)
    height_px = round(400.0 / pitch)
    size = (width_px, height_px)
    transform = placement["transform"]
    scale = transform["uniform_scale_mm_per_source_m"]
    tx, ty = transform["translate_mm"]

    def mm_to_px(x: float, y: float):
        return round(x / pitch), round((400.0 - y) / pitch)

    def draw_polygon_mask(geometry) -> Image.Image:
        image = Image.new("L", size, 0)
        draw = ImageDraw.Draw(image)
        for polygon in polygons(geometry):
            draw.polygon([mm_to_px(x, y) for x, y in polygon.exterior.coords], fill=255)
            for ring in polygon.interiors:
                draw.polygon([mm_to_px(x, y) for x, y in ring.coords], fill=0)
        return image

    outer_image = draw_polygon_mask(outer)

    def line_mask(path: Path, width_mm: float) -> Image.Image:
        image = Image.new("L", size, 0)
        draw = ImageDraw.Draw(image)
        data = json.loads(path.read_text())
        line_width = max(1, round(width_mm / pitch))
        for feature in data["features"]:
            geometry = feature.get("geometry")
            if not geometry:
                continue
            for line in iter_line_coordinates(geometry):
                points = [mm_to_px(x * scale + tx, y * scale + ty) for x, y in line]
                if len(points) >= 2:
                    draw.line(points, fill=255, width=line_width, joint="curve")
        return ImageChops.multiply(image, outer_image)

    roads_path = SOURCE / "roads-major.geojson"
    rail_path = SOURCE / "rail.geojson"
    accent_path = SOURCE / "roads-accent.geojson"
    water_path = SOURCE / "waterways.geojson"
    nardo = ImageChops.lighter(
        line_mask(roads_path, NETWORK["nardo_width_mm"]),
        line_mask(rail_path, NETWORK["nardo_width_mm"]),
    )
    black = ImageChops.lighter(
        line_mask(roads_path, NETWORK["black_width_mm"]),
        line_mask(rail_path, NETWORK["black_width_mm"]),
    )
    orange = line_mask(accent_path, NETWORK["orange_width_mm"])

    if mode == "context_outline":
        marker_width = PARAMETERS["modes"]["context_outline"]["boundary_marker"]["nominal_width_mm"]
        marker_image = Image.new("L", size, 0)
        marker_draw = ImageDraw.Draw(marker_image)
        transformed_boundary = transform_geometry(boundary, transform)
        width_px_marker = max(1, round(marker_width / pitch))
        for polygon in polygons(transformed_boundary):
            marker_draw.line(
                [mm_to_px(x, y) for x, y in polygon.exterior.coords],
                fill=255,
                width=width_px_marker,
                joint="curve",
            )
            for ring in polygon.interiors:
                marker_draw.line(
                    [mm_to_px(x, y) for x, y in ring.coords],
                    fill=255,
                    width=width_px_marker,
                    joint="curve",
                )
        marker_image = ImageChops.multiply(marker_image, outer_image)
        nardo = ImageChops.lighter(nardo, marker_image)
        black = ImageChops.lighter(black, marker_image)
        orange = ImageChops.lighter(orange, marker_image)

    apertures = line_mask(water_path, LIGHT["waterway_width_mm"])
    outer_array = np.asarray(outer_image, dtype=np.uint8) > 0
    nardo_array = np.asarray(nardo, dtype=np.uint8) > 0
    black_array = np.asarray(black, dtype=np.uint8) > 0
    orange_array = np.asarray(orange, dtype=np.uint8) > 0
    aperture_array = np.asarray(apertures, dtype=np.uint8) > 0

    color_edge_radius = max(1, round(UPPER_COLOR_EDGE_INSET_MM / pitch))
    upper_color_safe = morphology.erosion(
        outer_array, footprint=morphology.disk(color_edge_radius)
    )
    seam_min_column = round(
        (300.0 - SEAM_GAP_MM / 2.0 - UPPER_COLOR_EDGE_INSET_MM) / pitch
    )
    seam_max_column = round(
        (300.0 + SEAM_GAP_MM / 2.0 + UPPER_COLOR_EDGE_INSET_MM) / pitch
    )
    upper_color_safe[:, seam_min_column : seam_max_column + 1] = False
    nardo_array &= upper_color_safe
    black_array &= upper_color_safe
    orange_array &= upper_color_safe

    network_min_pixels = max(1, round(NETWORK["minimum_component_area_mm2"] / pitch**2))
    nardo_array = morphology.remove_small_objects(nardo_array, max_size=network_min_pixels - 1)
    black_array = morphology.remove_small_objects(black_array, max_size=network_min_pixels - 1)
    orange_array = morphology.remove_small_objects(orange_array, max_size=network_min_pixels - 1)

    close_radius = max(1, round(LIGHT["ligament_closing_radius_mm"] / pitch))
    aperture_array = ndimage.binary_closing(aperture_array, structure=morphology.disk(close_radius))
    aperture_min_pixels = max(1, round(LIGHT["minimum_component_area_mm2"] / pitch**2))
    aperture_array = morphology.remove_small_objects(aperture_array, max_size=aperture_min_pixels - 1)

    edge_radius = max(1, round(LIGHT["outer_ligament_mm"] / pitch))
    safe = morphology.erosion(outer_array, footprint=morphology.disk(edge_radius))
    safe_image = Image.fromarray((safe * 255).astype(np.uint8))
    safe_draw = ImageDraw.Draw(safe_image)

    def exclude_rect(x0: float, y0: float, x1: float, y1: float):
        safe_draw.rectangle([mm_to_px(x0, y1), mm_to_px(x1, y0)], fill=0)

    exclude_rect(300.0 - LIGHT["seam_keepout_half_width_mm"], 0.0, 300.0 + LIGHT["seam_keepout_half_width_mm"], 400.0)
    keep = LIGHT["functional_keepout_mm"]
    for y in placement["connector_y_positions_mm"]:
        exclude_rect(300.0 - keep - 17.0, y - keep, 300.0 + keep + 17.0, y + keep)
    for x, y in placement["socket_centers_global_mm"].values():
        exclude_rect(x - keep - 13.0, y - keep - 21.0, x + keep + 25.0, y + keep + 21.0)
    # Reserve two rear information lands even before the final watermark gate.
    exclude_rect(20.0, 10.0, 150.0, 38.0)
    exclude_rect(450.0, 10.0, 580.0, 38.0)
    aperture_array &= np.asarray(safe_image, dtype=np.uint8) > 0
    aperture_array, bridge_reports = bridge_aperture_islands(
        outer_array, aperture_array, pitch
    )

    nardo_array &= outer_array
    black_array &= nardo_array
    orange_array &= black_array
    nardo_array &= ~aperture_array
    black_array &= ~aperture_array
    orange_array &= ~aperture_array
    return {
        "outer": outer_array,
        "nardo": nardo_array,
        "black": black_array,
        "orange": orange_array,
        "apertures": aperture_array,
        "aperture_bridges": bridge_reports,
        "resolution_mm": pitch,
    }


def mask_to_cross_section(mask: np.ndarray, pitch: float) -> m3d.CrossSection:
    padded = np.pad(mask.astype(np.uint8), 1)
    raw = measure.find_contours(padded, 0.5, fully_connected="high")
    contours: list[np.ndarray] = []
    for contour in raw:
        contour = measure.approximate_polygon(contour, tolerance=0.65)
        if len(contour) < 4:
            continue
        rows = contour[:, 0] - 1.0
        columns = contour[:, 1] - 1.0
        xy = np.column_stack((columns * pitch, 400.0 - rows * pitch))
        if len(xy) >= 3:
            contours.append(xy.astype(np.float64))
    return m3d.CrossSection(contours, m3d.FillRule.EvenOdd).simplify(0.03)


def rear_cutters(half: str, local_width: float, placement) -> m3d.Manifold:
    connector = INTERFACE_PARAMETERS["connector"]
    clearance = connector["selected_provisional_clearance_per_side"]
    throat_half = connector["body_outer_width"] / 2.0 + clearance
    well_half = connector["barb_outer_width"] / 2.0 + clearance
    depth = connector["z_thickness"] + clearance
    combined = m3d.Manifold()
    for y in placement["connector_y_positions_mm"]:
        if half == "left":
            combined += rect_manifold(local_width - 9.0, local_width + 0.05, y - throat_half, y + throat_half, -0.05, depth)
            combined += rect_manifold(local_width - 16.0 - clearance, local_width - 9.0, y - well_half, y + well_half, -0.05, depth)
        else:
            combined += rect_manifold(-0.05, 9.0, y - throat_half, y + throat_half, -0.05, depth)
            combined += rect_manifold(9.0, 16.0 + clearance, y - well_half, y + well_half, -0.05, depth)

    socket = INTERFACE_PARAMETERS["socket_anchor"]
    socket_clearance = socket["selected_provisional_clearance_per_side"]
    socket_depth = socket["head_z_thickness"] + socket_clearance
    x_shift = 0.0 if half == "left" else 300.0 + SEAM_GAP_MM / 2.0
    for kind, (x_global, y) in placement["socket_centers_global_mm"].items():
        expected_half = "left" if kind.endswith("left") else "right"
        if expected_half != half:
            continue
        x = x_global - x_shift
        combined += rect_manifold(x - 8.0 - socket_clearance, x, y - 5.0 - socket_clearance, y + 5.0 + socket_clearance, -0.05, socket_depth)
        combined += rect_manifold(x, x + 14.0 + socket_clearance, y - 3.0 - socket_clearance, y + 3.0 + socket_clearance, -0.05, socket_depth)
        combined += rect_manifold(x + 10.5, x + 13.5, y + 3.0, y + 3.65 + socket_clearance, -0.05, socket_depth)
    return combined


def save_preview(masks, mode: str, path: Path):
    def rgb(value: str):
        value = value.lstrip("#")
        return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))

    height, width = masks["outer"].shape
    pixels = np.zeros((height, width, 4), dtype=np.uint8)
    pixels[masks["outer"]] = (*rgb(PALETTE["Bone White"]), 255)
    pixels[masks["nardo"]] = (*rgb(PALETTE["Nardo Grey"]), 255)
    pixels[masks["black"]] = (*rgb(PALETTE["Black"]), 255)
    pixels[masks["orange"]] = (*rgb(PALETTE["Orange"]), 255)
    pixels[masks["apertures"]] = (255, 200, 87, 255)
    image = Image.fromarray(pixels).resize((1200, 800), Image.Resampling.LANCZOS)
    image.save(path)


def build_mode(mode: str, export_dir: Path, validation_dir: Path):
    placement_path, placement = load_placement(mode)
    boundary = read_geojson(SOURCE / "boundary.geojson")
    outer = outer_geometry(mode, boundary, placement)
    masks = raster_masks(mode, boundary, outer, placement)
    outer_section = to_cross_section(outer)
    upper_color_section = to_cross_section(
        outer.buffer(-UPPER_COLOR_EDGE_INSET_MM)
    )
    sections = {
        name: mask_to_cross_section(masks[name], RASTER_PITCH_MM)
        ^ upper_color_section
        for name in ("nardo", "black", "orange")
    }
    sections["apertures"] = (
        mask_to_cross_section(masks["apertures"], RASTER_PITCH_MM) ^ outer_section
    )
    preview = validation_dir / f"berlin-{mode.replace('_', '-')}-top-preview.png"
    save_preview(masks, mode, preview)

    half_definitions = {
        "left": (0.0, 300.0 - SEAM_GAP_MM / 2.0),
        "right": (300.0 + SEAM_GAP_MM / 2.0, 600.0),
    }
    artifacts = [preview]
    half_reports = {}
    for half, (x0, x1) in half_definitions.items():
        local_width = x1 - x0
        half_global = to_cross_section(box(x0, 0.0, x1, 400.0))
        upper_half_global = to_cross_section(
            box(
                x0 + UPPER_COLOR_EDGE_INSET_MM,
                UPPER_COLOR_EDGE_INSET_MM,
                x1 - UPPER_COLOR_EDGE_INSET_MM,
                400.0 - UPPER_COLOR_EDGE_INSET_MM,
            )
        )
        local_sections = {
            name: (
                section
                ^ (half_global if name == "apertures" else upper_half_global)
            ).translate((-x0, 0.0))
            for name, section in sections.items()
        }
        local_outer = (outer_section ^ half_global).translate((-x0, 0.0))
        body_sections = {
            "bone-white": local_outer - local_sections["apertures"],
            "nardo-grey": local_sections["nardo"],
            "black": local_sections["black"],
            "orange": local_sections["orange"],
        }
        manifolds = {
            "bone-white": extrude_section(body_sections["bone-white"], *Z_BANDS["bone-white"]) - rear_cutters(half, local_width, placement),
            "nardo-grey": extrude_section(body_sections["nardo-grey"], *Z_BANDS["nardo-grey"]),
            "black": extrude_section(body_sections["black"], *Z_BANDS["black"]),
            "orange": extrude_section(body_sections["orange"], *Z_BANDS["orange"]),
        }
        color_reports = {}
        color_paths: list[Path] = []
        prefix = f"berlin-{mode.replace('_', '-')}-{half}"
        for color in COLORS:
            manifold = manifolds[color].simplify(MESH_SIMPLIFY_TOLERANCE_MM)
            manifolds[color] = manifold
            if manifold.is_empty() or manifold.volume() <= 0:
                raise ValueError(f"{mode}/{half}/{color} is empty")
            path = export_dir / f"{prefix}-{color}.stl"
            mesh = manifold_to_trimesh(manifold)
            mesh.export(path)
            artifacts.append(path)
            color_paths.append(path)
            roundtrip = roundtrip_stl_metrics(path)
            color_reports[color] = {
                "semantic_name": COLOR_LABELS[color],
                "area_mm2": body_sections[color].area(),
                **roundtrip,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        composite_path = export_dir / f"{prefix}-composite.stl"
        raw_composite_path = (
            validation_dir.parent
            / "composite-raw"
            / f"{prefix}-composite-blender-raw.stl"
        )
        composite_roundtrip, composite_trace = rebuild_composite(
            color_paths, raw_composite_path, composite_path
        )
        artifacts.append(composite_path)
        artifacts.append(raw_composite_path)
        aperture_area = local_sections["apertures"].area()
        retained_area = local_outer.area()
        aperture_fraction = aperture_area / retained_area
        half_reports[half] = {
            "local_width_mm": local_width,
            "retained_outer_area_mm2": retained_area,
            "aperture_area_mm2": aperture_area,
            "aperture_fraction_of_retained_body": aperture_fraction,
            "aperture_limit": LIGHT["maximum_open_area_fraction_per_half"],
            "aperture_island_control": masks["aperture_bridges"][half],
            "colors": color_reports,
            "composite": {
                **composite_roundtrip,
                "bytes": composite_path.stat().st_size,
                "sha256": sha256(composite_path),
                "rebuild_trace": composite_trace,
            },
        }

    mode_status = "PASS" if all(
        half_report["composite"]["watertight"]
        and half_report["composite"]["positive_volume"]
        and half_report["composite"]["connected_components"] == 1
        and half_report["composite"]["boundary_edges"] == 0
        and half_report["composite"]["nonmanifold_edges"] == 0
        and half_report["composite"]["degenerate_faces"] == 0
        and half_report["composite"]["duplicate_faces"] == 0
        and half_report["composite"]["triangles"] <= 750_000
        and half_report["aperture_fraction_of_retained_body"] <= half_report["aperture_limit"]
        and all(
            color["watertight"]
            and color["positive_volume"]
            and color["boundary_edges"] == 0
            and color["nonmanifold_edges"] == 0
            and color["degenerate_faces"] == 0
            and color["duplicate_faces"] == 0
            for color in half_report["colors"].values()
        )
        for half_report in half_reports.values()
    ) else "FAIL"
    return {
        "status": mode_status,
        "placement_manifest": {"path": str(placement_path.relative_to(PRODUCT)), "sha256": sha256(placement_path)},
        "outer_bounds_mm": list(outer.bounds),
        "outer_area_mm2": outer.area,
        "positive_area_outside_mode_outer_mm2": 0.0,
        "panel_transform": placement["transform"],
        "halves": half_reports,
        "preview": str(preview.relative_to(PRODUCT)),
        "artifacts": [
            {"path": str(path.relative_to(PRODUCT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in artifacts
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, help="new immutable output ID, for example digital-candidate-r1")
    args = parser.parse_args()
    if not args.candidate.replace("-", "").isalnum():
        raise SystemExit("candidate must contain only letters, digits and hyphens")

    required = [
        PARAMETERS_PATH,
        INTERFACE_PARAMETERS_PATH,
        BLENDER,
        BLENDER_COMPOSITE_SCRIPT,
        SOURCE / "source-manifest.json",
        SOURCE / "boundary.geojson",
        SOURCE / "roads-major.geojson",
        SOURCE / "roads-accent.geojson",
        SOURCE / "rail.geojson",
        SOURCE / "waterways.geojson",
        PLACEMENT_DIR / "boundary-crop-placement.json",
        PLACEMENT_DIR / "context-outline-placement.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing source or gate input(s): {missing}")
    source_manifest = json.loads((SOURCE / "source-manifest.json").read_text())
    if source_manifest.get("status") != "PASS":
        raise SystemExit("source manifest is not PASS")

    export_root = PRODUCT / "exports" / "v0.4.0" / "berlin" / args.candidate
    validation_root = PRODUCT / "validation" / "v0.4.0" / "berlin" / args.candidate
    if export_root.exists() or validation_root.exists():
        raise SystemExit("refusing destructive overwrite of an existing candidate directory")
    export_root.mkdir(parents=True)
    (validation_root / "renders").mkdir(parents=True)

    reports = {}
    for mode in MODES:
        mode_export = export_root / mode.replace("_", "-")
        mode_export.mkdir()
        reports[mode] = build_mode(mode, mode_export, validation_root / "renders")
    status = "PASS" if all(report["status"] == "PASS" for report in reports.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.4.0",
        "candidate": args.candidate,
        "status": status,
        "representation": "two display modes, two permanent halves per mode, four named disjoint Z-band solids per half",
        "source_manifest": {"path": str((SOURCE / "source-manifest.json").relative_to(PRODUCT)), "sha256": sha256(SOURCE / "source-manifest.json")},
        "parameters": {"path": str(PARAMETERS_PATH.relative_to(PRODUCT)), "sha256": sha256(PARAMETERS_PATH)},
        "interface_parameters": {"path": str(INTERFACE_PARAMETERS_PATH.relative_to(PRODUCT)), "sha256": sha256(INTERFACE_PARAMETERS_PATH)},
        "palette": PALETTE,
        "z_bands_mm": Z_BANDS,
        "manufacturing_raster_pitch_mm": RASTER_PITCH_MM,
        "upper_color_edge_inset_mm": UPPER_COLOR_EDGE_INSET_MM,
        "mesh_simplify_tolerance_mm": MESH_SIMPLIFY_TOLERANCE_MM,
        "modes": reports,
        "shared_secondary_parts": {
            "seam_connector": "exports/v0.3.0/interfaces/seam-connector-c025.stl",
            "upper_hanger": "exports/v0.3.0/interfaces/upper-hanger-18mm.stl",
            "lower_standoff": "exports/v0.3.0/interfaces/lower-standoff-18mm.stl",
            "interface_coupon": "coupons/v0.3.0/interface-coupon-all-clearances.stl",
            "reuse_basis": "shape authority unchanged; only mode-specific pockets and placements changed",
        },
        "resource_budget": {
            "triangle_target_per_main_half": 750_000,
            "triangle_stop_per_main_half": 1_500_000,
            "peak_memory_gib": 4.0,
            "max_mesh_mib_per_main_half": 75.0,
        },
        "limitations": [
            "DRAFT digital candidate only; 0.25 mm connector and socket compensation remains physical-coupon controlled.",
            "Exact filament batches, ACE slot identity, directed purge matrix, wall anchors, physical load, lit appearance and release are not approved.",
            "The boundary perimeter uses a 0.06 mm physical simplification; semantic color and aperture masks use a protected 0.25 mm manufacturing raster.",
        ],
    }
    report_path = validation_root / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    manifest = {
        "schema_version": "1.0",
        "generator": str(Path(__file__).resolve().relative_to(PRODUCT)),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "build_report": str(report_path.relative_to(PRODUCT)),
        "build_report_sha256": sha256(report_path),
    }
    (validation_root / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(report_path), "export_root": str(export_root)}))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
