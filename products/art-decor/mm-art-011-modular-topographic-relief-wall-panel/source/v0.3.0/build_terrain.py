#!/usr/bin/env python3
"""Build the Harz and Rhenish four-band topographic wall-relief pilots.

The immutable 16-bit master is mapped once over the complete 600 x 400 mm
composition.  Manufacturing downsampling, height scaling, color thresholds,
light apertures and the center split are therefore global operations.  The two
print halves are never normalized independently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterator

import manifold3d as m3d
import numpy as np
import tifffile
import trimesh
from PIL import Image
from scipy import ndimage
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import substring, unary_union
from skimage import measure, transform


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[1]
REPO = HERE.parents[4]
PARAMETERS_PATH = HERE / "terrain-pilots.json"
PARAMETERS = json.loads(PARAMETERS_PATH.read_text())
INTERFACE_DIR = (
    REPO
    / "products"
    / "art-decor"
    / "mm-art-010-modular-city-map-wall-panel"
    / "source"
    / "v0.3.0"
)
sys.path.insert(0, str(INTERFACE_DIR))
from interface_geometry import PARAMS as INTERFACE_PARAMS  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        exterior = np.asarray(fixed.exterior.coords[:-1], dtype=np.float64)
        if len(exterior) >= 3:
            contours.append(exterior)
        for ring in fixed.interiors:
            hole = np.asarray(ring.coords[:-1], dtype=np.float64)
            if len(hole) >= 3:
                contours.append(hole)
    return m3d.CrossSection(contours, m3d.FillRule.Positive)


def extrude(geometry, z0: float, z1: float) -> m3d.Manifold:
    if geometry.is_empty:
        return m3d.Manifold()
    return to_cross_section(geometry).extrude(z1 - z0).translate((0.0, 0.0, z0))


def rectangle_manifold(
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
) -> m3d.Manifold:
    return extrude(box(x0, y0, x1, y1), z0, z1)


def manifold_to_trimesh(manifold: m3d.Manifold) -> trimesh.Trimesh:
    mesh = manifold.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(mesh.vert_properties)[:, :3],
        faces=np.asarray(mesh.tri_verts),
        # Validation removes zero-area triangles that can appear where a
        # horizontal color cut is tangent to the sampled terrain.  Keeping
        # them would become repeated indices when a 3MF writer welds vertices.
        process=True,
        validate=True,
    )


def rear_cutters(half: str, local_width: float) -> m3d.Manifold:
    """Approved rear-open seam and hanger/standoff pockets from MM-ART-010."""
    connector = INTERFACE_PARAMS["connector"]
    clearance = connector["selected_provisional_clearance_per_side"]
    throat_half = connector["body_outer_width"] / 2 + clearance
    well_half = connector["barb_outer_width"] / 2 + clearance
    depth = connector["z_thickness"] + clearance
    combined = m3d.Manifold()
    for y in INTERFACE_PARAMS["panel"]["connector_y_positions"]:
        if half == "left":
            combined += rectangle_manifold(
                local_width - 9.0,
                local_width + 0.05,
                y - throat_half,
                y + throat_half,
                -0.05,
                depth,
            )
            combined += rectangle_manifold(
                local_width - 16.0 - clearance,
                local_width - 9.0,
                y - well_half,
                y + well_half,
                -0.05,
                depth,
            )
        else:
            combined += rectangle_manifold(
                -0.05,
                9.0,
                y - throat_half,
                y + throat_half,
                -0.05,
                depth,
            )
            combined += rectangle_manifold(
                9.0,
                16.0 + clearance,
                y - well_half,
                y + well_half,
                -0.05,
                depth,
            )

    socket = INTERFACE_PARAMS["socket_anchor"]
    socket_clearance = socket["selected_provisional_clearance_per_side"]
    socket_depth = socket["head_z_thickness"] + socket_clearance
    x_shift = 0.0 if half == "left" else 300.125
    for global_x, y, _kind in INTERFACE_PARAMS["panel"]["socket_centers_global"]:
        if (half == "left" and global_x >= 300.0) or (half == "right" and global_x <= 300.0):
            continue
        x = global_x - x_shift
        combined += rectangle_manifold(
            x - 8.0 - socket_clearance,
            x,
            y - 5.0 - socket_clearance,
            y + 5.0 + socket_clearance,
            -0.05,
            socket_depth,
        )
        combined += rectangle_manifold(
            x,
            x + 14.0 + socket_clearance,
            y - 3.0 - socket_clearance,
            y + 3.0 + socket_clearance,
            -0.05,
            socket_depth,
        )
        combined += rectangle_manifold(
            x + 10.5,
            x + 13.5,
            y + 3.0,
            y + 3.65 + socket_clearance,
            -0.05,
            socket_depth,
        )
    return combined


def heightfield_mesh(normalized: np.ndarray, base: float, relief: float) -> trimesh.Trimesh:
    """Return a closed heightfield solid with one triangulated bottom fan."""
    rows, columns = normalized.shape
    xs = np.linspace(0.0, 600.0, columns, dtype=np.float32)
    ys = np.linspace(0.0, 400.0, rows, dtype=np.float32)
    xx, yy = np.meshgrid(xs, ys)
    zz = (base + relief * normalized).astype(np.float32)
    top_vertices = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel())).astype(np.float32)

    cell_rows = np.arange(rows - 1, dtype=np.uint32)[:, None]
    cell_columns = np.arange(columns - 1, dtype=np.uint32)[None, :]
    a = cell_rows * columns + cell_columns
    b = a + 1
    d = a + columns
    c = d + 1
    top_faces = np.stack((a, b, c, a, c, d), axis=-1).reshape(-1, 3)

    perimeter = np.concatenate(
        (
            np.arange(columns, dtype=np.uint32),
            np.arange(1, rows, dtype=np.uint32) * columns + columns - 1,
            (rows - 1) * columns + np.arange(columns - 2, -1, -1, dtype=np.int64).astype(np.uint32),
            np.arange(rows - 2, 0, -1, dtype=np.int64).astype(np.uint32) * columns,
        )
    )
    bottom_start = len(top_vertices)
    bottom_vertices = top_vertices[perimeter].copy()
    bottom_vertices[:, 2] = 0.0
    center_index = bottom_start + len(bottom_vertices)
    center = np.array([[300.0, 200.0, 0.0]], dtype=np.float32)
    vertices = np.vstack((top_vertices, bottom_vertices, center))

    next_indices = np.roll(np.arange(len(perimeter), dtype=np.uint32), -1)
    top_current = perimeter
    top_next = perimeter[next_indices]
    bottom_current = bottom_start + np.arange(len(perimeter), dtype=np.uint32)
    bottom_next = bottom_start + next_indices
    side_faces = np.vstack(
        (
            np.column_stack((top_current, bottom_current, bottom_next)),
            np.column_stack((top_current, bottom_next, top_next)),
        )
    )
    bottom_faces = np.column_stack(
        (
            np.full(len(perimeter), center_index, dtype=np.uint32),
            bottom_next,
            bottom_current,
        )
    )
    faces = np.vstack((top_faces, side_faces, bottom_faces)).astype(np.uint32)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    if not mesh.is_watertight or mesh.volume <= 0:
        raise RuntimeError("heightfield mesh failed closed-solid validation")
    return mesh


def heightfield_manifold(normalized: np.ndarray, base: float, relief: float) -> m3d.Manifold:
    mesh = heightfield_mesh(normalized, base, relief)
    manifold = m3d.Manifold(
        m3d.Mesh(
            np.asarray(mesh.vertices, dtype=np.float32),
            np.asarray(mesh.faces, dtype=np.uint32),
        )
    )
    if manifold.status() != m3d.Error.NoError:
        raise RuntimeError(f"Manifold import failed: {manifold.status()}")
    return manifold


def protected_area() -> Polygon:
    """Front-aperture area after border, seam and rear-interface keep-outs."""
    safe = box(8.0, 8.0, 592.0, 392.0)
    safe = safe.difference(box(292.0, 0.0, 308.0, 400.0))
    for y in INTERFACE_PARAMS["panel"]["connector_y_positions"]:
        safe = safe.difference(box(284.0, y - 16.0, 316.0, y + 16.0))
    for x, y, _kind in INTERFACE_PARAMS["panel"]["socket_centers_global"]:
        safe = safe.difference(box(x - 18.0, y - 18.0, x + 30.0, y + 18.0))
    return safe


def contour_lines(normalized: np.ndarray, levels: list[float]) -> list[tuple[float, LineString]]:
    rows, columns = normalized.shape
    found: list[tuple[float, LineString]] = []
    for level in levels:
        for contour in measure.find_contours(normalized, level, fully_connected="high"):
            contour = measure.approximate_polygon(contour, tolerance=0.55)
            if len(contour) < 4:
                continue
            xy = np.column_stack(
                (
                    contour[:, 1] * 600.0 / (columns - 1),
                    contour[:, 0] * 400.0 / (rows - 1),
                )
            )
            line = LineString(xy)
            if line.length >= 30.0:
                found.append((level, line))
    return found


def select_apertures(
    normalized: np.ndarray,
    levels: list[float],
    count: int,
    width: float,
) -> tuple[object, list[dict]]:
    """Select deterministic open contour fragments without creating islands."""
    safe = protected_area()
    candidates: list[tuple[float, float, object]] = []
    for level, line in contour_lines(normalized, levels):
        segment_length = min(88.0, max(28.0, line.length * 0.42))
        for fraction in (0.18, 0.46, 0.72):
            start = min(line.length - segment_length, max(0.0, line.length * fraction - segment_length / 2))
            segment = substring(line, start, start + segment_length)
            buffered = segment.buffer(width / 2, cap_style=1, join_style=1).intersection(safe)
            # A buffered contour fragment with an interior ring would create a
            # loose terrain island when cut through the panel, so reject it.
            pieces = [
                polygon
                for polygon in polygons(buffered)
                if polygon.area >= 30.0 and len(polygon.interiors) == 0
            ]
            if not pieces:
                continue
            piece = max(pieces, key=lambda polygon: polygon.area)
            candidates.append((piece.area, level, piece))

    candidates.sort(key=lambda item: (-item[0], item[1], item[2].centroid.x, item[2].centroid.y))
    target_left = count // 2
    target_right = count - target_left
    selected: list[object] = []
    records: list[dict] = []
    side_counts = {"left": 0, "right": 0}
    for area, level, candidate in candidates:
        side = "left" if candidate.centroid.x < 300.0 else "right"
        side_target = target_left if side == "left" else target_right
        if side_counts[side] >= side_target:
            continue
        if any(candidate.buffer(5.0).intersects(existing) for existing in selected):
            continue
        selected.append(candidate)
        side_counts[side] += 1
        records.append(
            {
                "level_normalized": level,
                "side": side,
                "area_mm2": area,
                "centroid_mm": [candidate.centroid.x, candidate.centroid.y],
            }
        )
        if len(selected) == count:
            break
    if len(selected) != count:
        raise RuntimeError(
            f"could select only {len(selected)} of {count} protected light-aperture segments"
        )
    return unary_union(selected), records


def threshold_heights(normalized: np.ndarray, quantiles: list[float], base: float, relief: float, layer: float) -> list[float]:
    values = [base + relief * float(np.quantile(normalized, quantile)) for quantile in quantiles]
    rounded = [round(value / layer) * layer for value in values]
    if not all(left < right for left, right in zip(rounded, rounded[1:])):
        raise RuntimeError(f"rounded color thresholds are not strictly increasing: {rounded}")
    return rounded


def nudge_vertices_off_color_planes(
    normalized: np.ndarray,
    thresholds: list[float],
    base: float,
    relief: float,
) -> tuple[np.ndarray, dict]:
    """Avoid zero-area split triangles at vertices numerically on a Z plane.

    The measured displacement is capped at approximately 0.0011 mm because a
    vertex can begin 0.0001 mm below the plane and end 0.001 mm above it. This
    remains two orders of magnitude below the 0.2 mm layer height and is
    recorded explicitly. Color planes remain snapped to full layer boundaries.
    """
    surface = (base + relief * normalized).astype(np.float32)
    total = 0
    maximum = 0.0
    per_plane = []
    for threshold in thresholds:
        mask = np.abs(surface - threshold) <= 0.0001
        count = int(np.count_nonzero(mask))
        if count:
            before = surface[mask].copy()
            surface[mask] = threshold + 0.001
            maximum = max(maximum, float(np.max(np.abs(surface[mask] - before))))
        total += count
        per_plane.append({"z_mm": threshold, "vertices_nudged": count})
    return np.clip((surface - base) / relief, 0.0, 1.0).astype(np.float32), {
        "method": "vertices within 0.0001 mm of a color plane moved to plane + 0.001 mm",
        "total_vertices_nudged": total,
        "maximum_displacement_mm": maximum,
        "planes": per_plane,
    }


def split_color_bands(manifold: m3d.Manifold, thresholds: list[float]) -> list[m3d.Manifold]:
    bands: list[m3d.Manifold] = []
    remaining = manifold
    for height in thresholds:
        above, below = remaining.split_by_plane((0.0, 0.0, 1.0), height)
        bands.append(below)
        remaining = above
    bands.append(remaining)
    return bands


def retain_primary_component(manifold: m3d.Manifold) -> tuple[m3d.Manifold, dict]:
    """Remove only Boolean-created zero/tiny orphan shells from a panel body."""
    components = sorted(manifold.decompose(), key=lambda item: item.volume(), reverse=True)
    if not components:
        raise RuntimeError("panel Boolean produced no components")
    removed = [
        {"volume_mm3": float(item.volume()), "triangles": int(item.num_tri())}
        for item in components[1:]
    ]
    if any(item["volume_mm3"] > 25.0 for item in removed):
        raise RuntimeError(f"panel Boolean produced a material disconnected component: {removed}")
    return components[0], {
        "components_before_cleanup": len(components),
        "tiny_orphan_components_removed": removed,
    }


def rgb(hex_color: str) -> np.ndarray:
    value = hex_color.lstrip("#")
    return np.array([int(value[index : index + 2], 16) for index in (0, 2, 4)], dtype=np.float32)


def save_preview(
    normalized: np.ndarray,
    apertures,
    thresholds: list[float],
    palette: list[dict],
    base: float,
    relief: float,
    path: Path,
) -> None:
    surface = base + relief * normalized
    band_index = np.digitize(surface, thresholds)
    colors = np.stack([rgb(entry["display_hex"]) for entry in palette])
    image = colors[band_index]
    dy, dx = np.gradient(normalized)
    light = np.array([-0.45, -0.55, 0.70], dtype=np.float32)
    normals = np.dstack((-dx * 14.0, -dy * 14.0, np.ones_like(normalized)))
    normals /= np.linalg.norm(normals, axis=2, keepdims=True)
    shade = np.clip(normals @ light, 0.25, 1.0)
    image = np.clip(image * (0.68 + 0.38 * shade[..., None]), 0, 255).astype(np.uint8)

    aperture_mask = np.zeros_like(normalized, dtype=bool)
    rows, columns = normalized.shape
    for polygon in polygons(apertures):
        exterior = np.asarray(polygon.exterior.coords)
        pixel_polygon = np.column_stack(
            (
                exterior[:, 0] * (columns - 1) / 600.0,
                exterior[:, 1] * (rows - 1) / 400.0,
            )
        )
        rr, cc = measure.grid_points_in_poly(
            aperture_mask.shape,
            np.column_stack((pixel_polygon[:, 1], pixel_polygon[:, 0])),
        ).nonzero()
        aperture_mask[rr, cc] = True
    aperture_mask = ndimage.binary_dilation(aperture_mask, iterations=1)
    image[aperture_mask] = np.array([255, 196, 78], dtype=np.uint8)
    Image.fromarray(np.flipud(image), mode="RGB").resize((1200, 800), Image.Resampling.LANCZOS).save(path)


def part_report(manifold: m3d.Manifold, path: Path) -> dict:
    mesh = manifold_to_trimesh(manifold)
    mesh.export(path)
    return {
        "path": str(path.relative_to(PRODUCT)),
        "vertices": int(manifold.num_vert()),
        "triangles": int(manifold.num_tri()),
        "volume_mm3": float(manifold.volume()),
        "watertight": bool(mesh.is_watertight),
        "components": int(len(manifold.decompose())),
        "bounds_mm": mesh.bounds.tolist(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def build(pilot_name: str) -> dict:
    common = PARAMETERS["common"]
    pilot = PARAMETERS["pilots"][pilot_name]
    master_path = PRODUCT / pilot["master"]
    float_path = PRODUCT / pilot["float_source"]
    export_dir = PRODUCT / "exports" / "v0.3.0" / pilot_name
    validation_dir = PRODUCT / "validation" / "v0.3.0" / pilot_name
    render_dir = validation_dir / "renders"
    export_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)

    master_raw = tifffile.imread(master_path)
    if master_raw.dtype != np.uint16 or list(master_raw.shape[::-1]) != common["reference_samples"]:
        raise RuntimeError(
            f"expected uint16 {common['reference_samples']} master, got {master_raw.dtype} {master_raw.shape[::-1]}"
        )
    normalized_reference = np.flipud(master_raw).astype(np.float32) / 65535.0
    generation_png = validation_dir / f"{pilot_name}-generation-heightmap-16bit.png"
    Image.fromarray(np.flipud(master_raw), mode="I;16").save(generation_png, dpi=(50.8, 50.8))

    target_columns, target_rows = common["manufacturing_samples"]
    normalized_manufacturing = transform.resize(
        normalized_reference,
        (target_rows, target_columns),
        order=3,
        mode="edge",
        anti_aliasing=True,
        preserve_range=True,
    ).astype(np.float32)
    normalized_manufacturing = np.clip(normalized_manufacturing, 0.0, 1.0)
    manufacturing_master = np.rint(normalized_manufacturing * 65535.0).astype(np.uint16)
    manufacturing_png = validation_dir / f"{pilot_name}-manufacturing-heightmap-16bit.png"
    Image.fromarray(np.flipud(manufacturing_master), mode="I;16").save(
        manufacturing_png,
        dpi=(25.4 / (600.0 / (target_columns - 1)), 25.4 / (400.0 / (target_rows - 1))),
    )

    base = float(common["base_thickness_mm"])
    relief = float(common["relief_depth_mm"])
    thresholds = threshold_heights(
        normalized_manufacturing,
        common["color_quantiles"],
        base,
        relief,
        common["layer_height_mm"],
    )
    aperture_levels = [float(np.quantile(normalized_manufacturing, q)) for q in pilot["light_contour_quantiles"]]
    apertures, aperture_records = select_apertures(
        normalized_manufacturing,
        aperture_levels,
        pilot["light_segment_count"],
        common["light_aperture_width_mm"],
    )
    geometry_manufacturing, color_plane_nudge = nudge_vertices_off_color_planes(
        normalized_manufacturing,
        thresholds,
        base,
        relief,
    )

    reference_path = export_dir / f"{pilot_name}-reference-full.stl"
    reference_mesh = heightfield_mesh(normalized_reference, base, relief)
    reference_mesh.export(reference_path)

    manufacturing_full = heightfield_manifold(geometry_manufacturing, base, relief)
    manufacturing_full -= extrude(apertures, -0.1, base + relief + 0.2)
    half_definitions = {
        "left": ((-1.0, 0.0, 0.0), -299.875, 0.0),
        "right": ((1.0, 0.0, 0.0), 300.125, -300.125),
    }
    artifacts = [reference_path, generation_png, manufacturing_png]
    halves: dict[str, dict] = {}
    part_manifest: dict[str, list[dict]] = {}
    for half, (normal, offset, translate_x) in half_definitions.items():
        half_manifold = manufacturing_full.trim_by_plane(normal, offset)
        if translate_x:
            half_manifold = half_manifold.translate((translate_x, 0.0, 0.0))
        local_width = 299.875
        half_manifold -= rear_cutters(half, local_width)
        half_manifold, component_cleanup = retain_primary_component(half_manifold)
        composite_path = export_dir / f"{pilot_name}-{half}-composite.stl"
        composite_report = part_report(half_manifold, composite_path)
        artifacts.append(composite_path)

        band_manifolds = split_color_bands(half_manifold, thresholds)
        color_reports: dict[str, dict] = {}
        part_manifest[half] = []
        for color_index, (palette_entry, band) in enumerate(zip(pilot["palette"], band_manifolds), start=1):
            color_path = export_dir / f"{pilot_name}-{half}-{color_index:02d}-{palette_entry['id']}.stl"
            report = part_report(band, color_path)
            report["material"] = palette_entry
            report["z_interval_mm"] = [
                0.0 if color_index == 1 else thresholds[color_index - 2],
                thresholds[color_index - 1] if color_index <= len(thresholds) else base + relief,
            ]
            color_reports[palette_entry["id"]] = report
            part_manifest[half].append(
                {
                    "path": str(color_path.relative_to(PRODUCT)),
                    "material_name": palette_entry["name"],
                    "display_hex": palette_entry["display_hex"],
                }
            )
            artifacts.append(color_path)

        global_x0 = 0.0 if half == "left" else 300.125
        global_x1 = 299.875 if half == "left" else 600.0
        half_apertures = apertures.intersection(box(global_x0, 0.0, global_x1, 400.0))
        aperture_area = float(half_apertures.area)
        aperture_fraction = aperture_area / (local_width * 400.0)
        halves[half] = {
            "local_width_mm": local_width,
            "composite": composite_report,
            "component_cleanup": component_cleanup,
            "colors": color_reports,
            "aperture_area_mm2": aperture_area,
            "aperture_fraction": aperture_fraction,
            "aperture_limit": common["maximum_open_area_fraction_per_half"],
            "triangle_target": common["triangle_target_per_half"],
            "triangle_stop": common["triangle_stop_per_half"],
        }

    preview_path = render_dir / f"{pilot_name}-top-color-hillshade-and-light-preview.png"
    save_preview(normalized_manufacturing, apertures, thresholds, pilot["palette"], base, relief, preview_path)
    artifacts.append(preview_path)
    parts_path = validation_dir / f"{pilot_name}-four-color-parts.json"
    parts_path.write_text(json.dumps({"schema_version": "1.0", "halves": part_manifest}, indent=2) + "\n")
    artifacts.append(parts_path)

    restored = transform.resize(
        normalized_manufacturing,
        normalized_reference.shape,
        order=3,
        mode="edge",
        anti_aliasing=False,
        preserve_range=True,
    )
    difference = restored - normalized_reference
    seam_left = normalized_manufacturing[:, np.searchsorted(np.linspace(0.0, 600.0, target_columns), 299.875)]
    seam_right = normalized_manufacturing[:, np.searchsorted(np.linspace(0.0, 600.0, target_columns), 300.125)]
    seam_delta = np.abs(seam_left - seam_right) * relief
    source_min, source_max = pilot["source_elevation_m"]
    threshold_records = []
    for quantile, height in zip(common["color_quantiles"], thresholds):
        normalized_height = (height - base) / relief
        threshold_records.append(
            {
                "quantile": quantile,
                "z_mm": height,
                "source_elevation_m_approx": source_min + normalized_height * (source_max - source_min),
            }
        )

    status = "PASS"
    reasons: list[str] = []
    for half, half_report in halves.items():
        composite = half_report["composite"]
        if not composite["watertight"]:
            status = "FAIL"
            reasons.append(f"{half} composite is not watertight")
        if composite["triangles"] > half_report["triangle_stop"]:
            status = "FAIL"
            reasons.append(f"{half} composite exceeds triangle stop")
        if half_report["aperture_fraction"] > half_report["aperture_limit"]:
            status = "FAIL"
            reasons.append(f"{half} aperture fraction exceeds limit")
        for color_id, color_report in half_report["colors"].items():
            if not color_report["watertight"]:
                status = "FAIL"
                reasons.append(f"{half} {color_id} body is not watertight")

    report = {
        "schema_version": "1.0",
        "project": "MM-ART-011",
        "revision": "0.3.0",
        "pilot": pilot_name,
        "title": pilot["title"],
        "status": status,
        "failure_reasons": reasons,
        "source": {
            "master": str(master_path.relative_to(PRODUCT)),
            "master_sha256": sha256(master_path),
            "float_source": str(float_path.relative_to(PRODUCT)),
            "float_source_sha256": sha256(float_path),
            "source_elevation_m": pilot["source_elevation_m"],
            "extent_epsg25832": pilot["extent_epsg25832"],
            "attribution": pilot["attribution"],
        },
        "heightmap": {
            "reference_samples": common["reference_samples"],
            "reference_generation_pitch_mm": common["reference_pitch_mm"],
            "reference_generation_ppi": 25.4 / common["reference_pitch_mm"],
            "manufacturing_samples": common["manufacturing_samples"],
            "manufacturing_pitch_mm": [600.0 / (target_columns - 1), 400.0 / (target_rows - 1)],
            "manufacturing_ppi_x": 25.4 / (600.0 / (target_columns - 1)),
            "base_thickness_mm": base,
            "relief_depth_mm": relief,
            "independent_half_normalization": False,
            "downsampling": "bicubic order 3 with anti-aliasing from the frozen global 16-bit master",
            "round_trip_normalized_rms": float(np.sqrt(np.mean(difference * difference))),
            "round_trip_normalized_max_abs": float(np.max(np.abs(difference))),
            "round_trip_correlation": float(np.corrcoef(normalized_reference.ravel(), restored.ravel())[0, 1]),
        },
        "color": {
            "palette": pilot["palette"],
            "thresholds": threshold_records,
            "layer_height_mm": common["layer_height_mm"],
            "named_body_count": 8,
            "intended_global_color_changes": 3,
            "dithering": False,
            "color_plane_degeneracy_guard": color_plane_nudge,
        },
        "lighting": {
            "optional_addon_not_included": True,
            "nominal_halo_gap_mm": 18.0,
            "front_through_aperture_width_mm": common["light_aperture_width_mm"],
            "selected_segments": aperture_records,
        },
        "seam": {
            "nominal_gap_mm": common["seam_gap_mm"],
            "global_field_sample_delta_max_mm": float(np.max(seam_delta)),
            "global_field_sample_delta_mean_mm": float(np.mean(seam_delta)),
            "split_after_global_scaling": True,
        },
        "reference_mesh": {
            "path": str(reference_path.relative_to(PRODUCT)),
            "triangles": int(len(reference_mesh.faces)),
            "watertight": bool(reference_mesh.is_watertight),
            "bounds_mm": reference_mesh.bounds.tolist(),
            "bytes": reference_path.stat().st_size,
            "sha256": sha256(reference_path),
        },
        "halves": halves,
        "limitations": [
            "The preview is a palette/hillshade/light-path diagram, not a destination-slicer preview or a lit physical photograph.",
            "The 0.25 mm connector/socket clearance is provisional until the physical four-clearance coupon selects the production value.",
            "Final ACE slot mapping, purge tower, seam, first layer, wall fastening and aperture survival require human destination-slicer and physical review.",
            "Copernicus GLO-30 is a surface model; vegetation and built structures may influence the Harz source elevations.",
        ],
        "physical_validation": "NOT_RUN",
    }
    report_path = validation_dir / f"{pilot_name}-build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    artifacts.append(report_path)
    manifest = {
        "schema_version": "1.0",
        "project": "MM-ART-011",
        "pilot": pilot_name,
        "generator": str(Path(__file__).relative_to(PRODUCT)),
        "generator_sha256": sha256(Path(__file__)),
        "parameters": str(PARAMETERS_PATH.relative_to(PRODUCT)),
        "parameters_sha256": sha256(PARAMETERS_PATH),
        "interface_source": str((INTERFACE_DIR / "interface_geometry.py").relative_to(REPO)),
        "interface_source_sha256": sha256(INTERFACE_DIR / "interface_geometry.py"),
        "interface_parameters_sha256": sha256(INTERFACE_DIR / "interface-parameters.json"),
        "artifacts": [
            {
                "path": str(path.relative_to(PRODUCT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(artifacts)
        ],
    }
    manifest_path = validation_dir / f"{pilot_name}-build-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return {"pilot": pilot_name, "status": status, "report": str(report_path), "manifest": str(manifest_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", choices=sorted(PARAMETERS["pilots"]), required=True)
    args = parser.parse_args()
    result = build(args.pilot)
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
