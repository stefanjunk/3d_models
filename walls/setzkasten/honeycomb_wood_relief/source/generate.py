#!/usr/bin/env python3
"""Generate exact CadQuery masters and nozzle-aware wood-relief STL derivatives."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import resource
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any

import cadquery as cq
import numpy as np
import trimesh
from PIL import Image, ImageOps
from scipy import ndimage


SOURCE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SOURCE_DIR.parent
PARAMETERS_PATH = PROJECT_DIR / "parameters.json"
EXPORT_DIR = PROJECT_DIR / "exports"
PREVIEW_DIR = PROJECT_DIR / "previews"
REPORT_DIR = PROJECT_DIR / "reports"
FACE_ANGLES_DEG = np.arange(0.0, 360.0, 60.0, dtype=np.float64)
FACE_ANGLES_RAD = np.deg2rad(FACE_ANGLES_DEG)
OUTWARD_2D = np.column_stack((np.cos(FACE_ANGLES_RAD), np.sin(FACE_ANGLES_RAD)))
TANGENT_2D = np.column_stack((-np.sin(FACE_ANGLES_RAD), np.cos(FACE_ANGLES_RAD)))


def load_parameters() -> dict[str, Any]:
    params = json.loads(PARAMETERS_PATH.read_text(encoding="utf-8"))
    if params.get("units") != "mm":
        raise ValueError("parameters.json must use millimeters")
    texture = params["texture"]
    if texture["enabled_surfaces"].get("front_rim") and texture.get(
        "front_relief_print_strategy", "bed_contact_disabled"
    ) == "bed_contact_disabled":
        raise ValueError(
            "front_rim relief is forbidden while the front rim contacts the bed; "
            "declare a non-bed-contact front_relief_print_strategy first"
        )
    if float(texture["final_max_edge_mm"]) > float(texture["minimum_printable_feature_mm"]) / 2.0:
        raise ValueError(
            "The declared minimum printable feature requires final_max_edge_mm <= feature / 2"
        )
    return params


def source_path(params: dict[str, Any], key: str) -> Path:
    return (PROJECT_DIR / params["source"][key]).resolve()


def provenance_entry(params: dict[str, Any], key: str, fallback: dict[str, str] | None = None) -> dict[str, str]:
    values = params.get("provenance", {}).get(key, {})
    if not isinstance(values, dict):
        values = {}
    defaults = {
        "status": "BLOCKED_LIBRARY_ASSET",
        "license": "unknown",
        "basis": "no file-level license recorded",
    }
    if fallback:
        defaults.update(fallback)
    return {
        "status": str(values.get("status", defaults["status"])),
        "license": str(values.get("license", defaults["license"])),
        "basis": str(values.get("basis", defaults["basis"])),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_base_module(params: dict[str, Any]) -> ModuleType:
    path = source_path(params, "cadquery_script")
    if not path.is_file():
        raise FileNotFoundError(f"CadQuery base source missing: {path}")
    spec = importlib.util.spec_from_file_location("honeycomb_cadquery_base", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import CadQuery base source: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    configure_base_module(module, params)
    return module


def configure_base_module(module: ModuleType, params: dict[str, Any]) -> None:
    g = params["geometry"]
    e = params["export"]
    assignments = {
        "SIDE_LENGTH": g["side_length_mm"],
        "DEPTH": g["depth_mm"],
        "WALL_THICKNESS": g["wall_thickness_mm"],
        "CORNER_RADIUS": g["corner_radius_mm"],
        "HANGER_THICKNESS": g["hanger_thickness_mm"],
        "HANGER_BOSS_DIAMETER": g["hanger_boss_diameter_mm"],
        "HANGER_HOLE_DIAMETER": g["hanger_hole_diameter_mm"],
        "HANGER_COUNTERBORE_DIAMETER": g["hanger_counterbore_diameter_mm"],
        "HANGER_COUNTERBORE_DEPTH": g["hanger_counterbore_depth_mm"],
        "HANGER_INSET": g["hanger_inset_mm"],
        "HANGER_TANGENT_FRACTION": g["hanger_tangent_fraction"],
        "CONNECTORS_PER_FACE": g["connectors_per_face"],
        "CONNECTOR_TANGENT_FRACTION": g["connector_tangent_fraction"],
        "CONNECTOR_INSERT_LENGTH": g["connector_insert_length_mm"],
        "CONNECTOR_RECESS": g["connector_recess_mm"],
        "CONNECTOR_WAIST_WIDTH": g["connector_waist_width_mm"],
        "CONNECTOR_LOBE_WIDTH": g["connector_lobe_width_mm"],
        "CONNECTOR_CLEARANCE": g["connector_clearance_each_side_mm"],
        "CONNECTOR_LEADIN": g["connector_leadin_mm"],
        "EXPORT_STL_TOLERANCE": e["stl_linear_tolerance_mm"],
        "EXPORT_ANGULAR_TOLERANCE": e["stl_angular_tolerance_rad"],
    }
    for name, value in assignments.items():
        setattr(module, name, value)

    sqrt3 = math.sqrt(3.0)
    module.SQRT3 = sqrt3
    module.OUTER_R = module.SIDE_LENGTH
    module.OUTER_APOTHEM = sqrt3 * module.SIDE_LENGTH / 2.0
    module.FLAT_TO_FLAT = 2.0 * module.OUTER_APOTHEM
    module.POINT_TO_POINT = 2.0 * module.SIDE_LENGTH
    module.INNER_APOTHEM = module.OUTER_APOTHEM - module.WALL_THICKNESS
    module.INNER_R = module.INNER_APOTHEM / (sqrt3 / 2.0)
    module.INNER_SIDE_LENGTH = module.INNER_R
    module.INNER_CORNER_RADIUS = max(0.8, module.CORNER_RADIUS - module.WALL_THICKNESS * 0.35)
    module.validate_parameters()

    # The downloaded base script rotates auxiliary bridge rectangles around the
    # global origin, which creates unrelated blocks at other inner walls. The
    # circular bosses already overlap the wall by HANGER_INSET, so this local,
    # exact B-Rep override removes only those erroneous helper blocks.
    expected_style = "boss overlaps inner wall directly; no auxiliary rectangular bridge blocks"
    if g.get("hanger_connection_style") != expected_style:
        raise ValueError("Unsupported hanger_connection_style in parameters.json")

    def add_internal_hangers_without_bridge(part: cq.Workplane) -> cq.Workplane:
        if not module.ENABLE_HANGERS:
            return part
        z0 = module.DEPTH - module.HANGER_THICKNESS
        boss_radius = module.HANGER_BOSS_DIAMETER / 2.0
        tangent_amount = module.INNER_SIDE_LENGTH * module.HANGER_TANGENT_FRACTION
        result = part
        for angle, tangential in ((60.0, tangent_amount), (120.0, -tangent_amount)):
            cx, cy = module.hanger_boss_center(angle, tangential)
            boss = (
                cq.Workplane("XY", origin=(0, 0, z0))
                .center(cx, cy)
                .circle(boss_radius)
                .extrude(module.HANGER_THICKNESS)
            )
            result = result.union(boss)
            through = (
                cq.Workplane("XY", origin=(0, 0, z0 - module.EPS))
                .center(cx, cy)
                .circle(module.HANGER_HOLE_DIAMETER / 2.0)
                .extrude(module.HANGER_THICKNESS + 2.0 * module.EPS)
            )
            result = result.cut(through)
            counterbore = (
                cq.Workplane("XY", origin=(0, 0, z0 - module.EPS))
                .center(cx, cy)
                .circle(module.HANGER_COUNTERBORE_DIAMETER / 2.0)
                .extrude(module.HANGER_COUNTERBORE_DEPTH + module.EPS)
            )
            result = result.cut(counterbore)
        return result.clean()

    module.add_internal_hangers = add_internal_hangers_without_bridge


def derived_geometry(params: dict[str, Any]) -> dict[str, float]:
    g = params["geometry"]
    sqrt3 = math.sqrt(3.0)
    outer_apothem = sqrt3 * g["side_length_mm"] / 2.0
    inner_apothem = outer_apothem - g["wall_thickness_mm"]
    inner_side = inner_apothem / (sqrt3 / 2.0)
    return {
        "outer_apothem_mm": outer_apothem,
        "inner_apothem_mm": inner_apothem,
        "outer_side_mm": g["side_length_mm"],
        "inner_side_mm": inner_side,
        "inner_corner_radius_mm": max(0.8, g["corner_radius_mm"] - g["wall_thickness_mm"] * 0.35),
    }


def inspect_cq_object(obj: cq.Workplane | cq.Shape) -> dict[str, Any]:
    shape = obj.val() if isinstance(obj, cq.Workplane) else obj
    if not isinstance(shape, cq.Shape):
        raise TypeError(f"Expected CadQuery Shape, got {type(shape).__name__}")
    bounds = shape.BoundingBox()
    return {
        "brep_valid": bool(shape.isValid()),
        "solid_count": int(len(shape.Solids())),
        "volume_mm3": float(shape.Volume()),
        "area_mm2": float(shape.Area()),
        "bounds_xyz_mm": [
            [float(bounds.xmin), float(bounds.ymin), float(bounds.zmin)],
            [float(bounds.xmax), float(bounds.ymax), float(bounds.zmax)],
        ],
        "extents_xyz_mm": [float(bounds.xlen), float(bounds.ylen), float(bounds.zlen)],
    }


def export_cadquery(obj: cq.Workplane | cq.Shape, path: Path, params: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".stl":
        e = params["export"]
        cq.exporters.export(
            obj,
            str(path),
            tolerance=e["stl_linear_tolerance_mm"],
            angularTolerance=e["stl_angular_tolerance_rad"],
        )
    else:
        cq.exporters.export(obj, str(path))
    if not path.is_file() or path.stat().st_size <= 0:
        raise RuntimeError(f"Empty export: {path}")


def reload_step_report(path: Path) -> dict[str, Any]:
    return inspect_cq_object(cq.importers.importStep(str(path)))


def build_periodic_heightmap(params: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    texture = params["texture"]
    source = source_path(params, "wood_image")
    if not source.is_file():
        raise FileNotFoundError(f"Wood image missing: {source}")

    pixels = int(texture["heightmap_pixels"])
    if pixels < 128 or pixels % 2:
        raise ValueError("heightmap_pixels must be an even number >= 128")
    half = pixels // 2
    original = Image.open(source).convert("L")
    fitted = ImageOps.fit(original, (half, half), method=Image.Resampling.LANCZOS)
    fitted = ImageOps.autocontrast(fitted, cutoff=0.5)

    # Mirror the source first, then filter periodically. This removes artificial
    # border lines while making both UV axes seamless at the tile boundary.
    source_arr = np.asarray(fitted, dtype=np.float32) / 255.0
    horizontal = np.concatenate((source_arr, source_arr[:, ::-1]), axis=1)
    periodic_source = np.concatenate((horizontal, horizontal[::-1, :]), axis=0)

    # The vertical repeat is 300 mm / 512 px = 0.586 mm. Periodic Gaussian filtering
    # suppresses image noise below the declared 1.2 mm printable feature.
    fine_arr = ndimage.gaussian_filter(periodic_source, sigma=0.95, mode="wrap")
    local_arr = ndimage.gaussian_filter(periodic_source, sigma=7.0, mode="wrap")
    dark_grain = np.clip((local_arr - fine_arr) * 5.0, 0.0, 1.0)
    grad_x = ndimage.sobel(fine_arr, axis=1, mode="wrap")
    grad_y = ndimage.sobel(fine_arr, axis=0, mode="wrap")
    edges = np.hypot(grad_x, grad_y)
    edge_scale = float(np.percentile(edges, 99.2))
    edges = np.clip(edges / max(edge_scale, 1e-6), 0.0, 1.0)
    broad = np.clip((1.0 - local_arr - 0.18) / 0.82, 0.0, 1.0)
    relief = 0.72 * dark_grain + 0.24 * edges + 0.08 * broad

    p08, p995 = np.percentile(relief, [8.0, 99.5])
    periodic = np.clip((relief - p08) / max(1e-6, p995 - p08), 0.0, 1.0)
    periodic = (np.clip((periodic - 0.10) / 0.90, 0.0, 1.0) ** 1.10).astype(np.float32)
    # Bilinear sampling is C0 at pixel boundaries.  Make the cyclic X join and
    # the mirrored half-tile join C1 too; the latter is the third hex-face join.
    periodic[:, 0] = (periodic[:, 1] + periodic[:, -1]) * 0.5
    periodic[:, half] = (periodic[:, half - 1] + periodic[:, half + 1]) * 0.5
    output = PREVIEW_DIR / "holz_heightmap.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.uint8(np.clip(periodic, 0.0, 1.0) * 255.0), mode="L").save(output)

    return periodic, {
        "source": str(source),
        "source_sha256": sha256_file(source),
        "source_pixels": list(original.size),
        "heightmap": str(output),
        "heightmap_pixels": list(periodic.shape[::-1]),
        "heightmap_sha256": sha256_file(output),
        "vertical_repeat_mm": float(texture["tile_size_mm"]),
        "vertical_mapping_mm_per_pixel": float(texture["tile_size_mm"] / pixels),
        "minimum_printable_feature_mm": float(texture["minimum_printable_feature_mm"]),
        "filter": "periodic grayscale local dark-detail + Sobel edges; mirrored 2x2 before filtering",
        "value_min": float(periodic.min()),
        "value_max": float(periodic.max()),
        "value_mean": float(periodic.mean()),
    }

def hex_support(points_xy: np.ndarray) -> np.ndarray:
    return np.max(points_xy @ OUTWARD_2D.T, axis=1)


def continuous_perimeter_u_mm(points_xy: np.ndarray, side_length: float) -> np.ndarray:
    projections = points_xy @ OUTWARD_2D.T
    face_index = np.argmax(projections, axis=1)
    local_tangent = np.sum(points_xy * TANGENT_2D[face_index], axis=1)
    return face_index.astype(np.float64) * side_length + local_tangent + side_length / 2.0


def normalized_perimeter_u(points_xy: np.ndarray, side_length: float) -> np.ndarray:
    """Map the complete six-face perimeter to exactly one [0, 1) image cycle."""
    return np.mod(continuous_perimeter_u_mm(points_xy, side_length) / (6.0 * side_length), 1.0)


def validate_perimeter_seams(heightmap: np.ndarray) -> dict[str, Any]:
    """Numerically verify C0/C1 sampling at all face joins and cycle closure."""
    epsilon = 1.0e-4
    value_tolerance = 1.0e-6
    slope_tolerance = 1.0e-4
    boundaries = np.arange(7, dtype=np.float64) / 6.0
    # Multiple heights exercise the full side-image convention, not one scanline.
    v_samples = np.array([0.0, 0.17, 0.5, 0.83], dtype=np.float64)
    max_value_error = 0.0
    max_slope_error = 0.0
    for face_boundary, boundary in enumerate(boundaries):
        for v in v_samples:
            center = sample_heightmap(heightmap, np.array([boundary]), np.array([v]))[0]
            left = sample_heightmap(heightmap, np.array([boundary - epsilon]), np.array([v]))[0]
            right = sample_heightmap(heightmap, np.array([boundary + epsilon]), np.array([v]))[0]
            # Evaluate the prior face's end and next face's start independently.
            # At face 6, this explicitly compares the closure at u=1 to u=0.
            previous_face_end = face_boundary / 6.0
            next_face_start = 0.0 if face_boundary == 6 else face_boundary / 6.0
            prior_value = sample_heightmap(heightmap, np.array([previous_face_end]), np.array([v]))[0]
            next_value = sample_heightmap(heightmap, np.array([next_face_start]), np.array([v]))[0]
            max_value_error = max(max_value_error, float(abs(prior_value - next_value)))
            max_slope_error = max(
                max_slope_error,
                float(abs((center - left) / epsilon - (right - center) / epsilon)),
            )
    result = {
        "perimeter_cycle_count": 1,
        "face_boundaries_checked": [float(value) for value in boundaries],
        "v_samples_normalized": v_samples.tolist(),
        "finite_difference_epsilon_normalized": epsilon,
        "max_value_error": max_value_error,
        "max_first_difference_error": max_slope_error,
        "value_tolerance": value_tolerance,
        "first_difference_tolerance": slope_tolerance,
    }
    result["passed"] = bool(max_value_error <= value_tolerance and max_slope_error <= slope_tolerance)
    if not result["passed"]:
        raise RuntimeError(f"Perimeter seam continuity failed: {result}")
    return result


def local_wall_residual_check(heightmap: np.ndarray, params: dict[str, Any]) -> dict[str, Any]:
    """Conservative local field check for the opposed engraved side walls.

    This is evaluated from the actual displacement mapping, not a B-Rep wall
    thickness measurement; rounded corners and mesh normals remain outside scope.
    """
    texture = params["texture"]
    if not (texture["enabled_surfaces"]["outer_sides"] and texture["enabled_surfaces"]["inner_sides"]):
        return {"method": "not_applicable: both side engravings are not enabled", "passed": None}
    u = np.linspace(0.0, 1.0, 513, endpoint=False)
    z = np.linspace(float(texture["side_texture_z_start_mm"]), float(texture["side_texture_z_end_mm"]), 257)
    uu, zz = np.meshgrid(u, z, indexing="xy")
    feather = float(texture["transition_feather_mm"])
    weight = smoothstep01((zz - texture["side_texture_z_start_mm"]) / feather) * smoothstep01(
        (texture["side_texture_z_end_mm"] - zz) / feather
    )
    sample = sample_heightmap(heightmap, uu.ravel(), (zz / texture["tile_size_mm"]).ravel()).reshape(uu.shape)
    residual = float(params["geometry"]["wall_thickness_mm"]) - 2.0 * sample * float(texture["side_max_depth_mm"]) * weight
    minimum = float(residual.min())
    declared = float(params["manufacturing"]["declared_minimum_wall_after_relief_mm"])
    return {
        "method": "conservative local mapped-field residual; not a measured B-Rep thickness",
        "sample_grid": [int(uu.shape[1]), int(uu.shape[0])],
        "minimum_residual_mm": minimum,
        "declared_minimum_wall_after_relief_mm": declared,
        "criterion_pass": bool(minimum >= declared - 1e-9),
    }


def smoothstep01(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def sample_heightmap(heightmap: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    height, width = heightmap.shape
    x = np.mod(u, 1.0) * width
    y = np.mod(v, 1.0) * height
    x0 = np.floor(x).astype(np.int64) % width
    y0 = np.floor(y).astype(np.int64) % height
    x1 = (x0 + 1) % width
    y1 = (y0 + 1) % height
    fx = x - np.floor(x)
    fy = y - np.floor(y)
    return (
        heightmap[y0, x0] * (1.0 - fx) * (1.0 - fy)
        + heightmap[y0, x1] * fx * (1.0 - fy)
        + heightmap[y1, x0] * (1.0 - fx) * fy
        + heightmap[y1, x1] * fx * fy
    )


def triangle_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    tri = vertices[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    normals /= np.maximum(lengths[:, None], 1e-15)
    return normals


def active_texture_faces(
    vertices: np.ndarray,
    faces: np.ndarray,
    params: dict[str, Any],
    derived: dict[str, float],
) -> np.ndarray:
    texture = params["texture"]
    surfaces = texture["enabled_surfaces"]
    centers = vertices[faces].mean(axis=1)
    normals = triangle_normals(vertices, faces)
    support = hex_support(centers[:, :2])
    orientation = np.sum(normals[:, :2] * centers[:, :2], axis=1)

    side_range = (
        (centers[:, 2] >= texture["side_texture_z_start_mm"] - texture["transition_feather_mm"])
        & (centers[:, 2] <= texture["side_texture_z_end_mm"] + texture["transition_feather_mm"])
    )
    horizontal = np.abs(normals[:, 2]) < 0.60
    outer_band = (
        (support >= derived["outer_apothem_mm"] - params["geometry"]["corner_radius_mm"] - 1.0)
        & (support <= derived["outer_apothem_mm"] + 1.0)
        & (orientation > 0.0)
    )
    inner_band = (
        (support >= derived["inner_apothem_mm"] - 1.0)
        & (support <= derived["inner_apothem_mm"] + derived["inner_corner_radius_mm"] + 1.0)
        & (orientation < 0.0)
    )

    active = np.zeros(len(faces), dtype=bool)
    if surfaces["outer_sides"]:
        active |= side_range & horizontal & outer_band
    if surfaces["inner_sides"]:
        active |= side_range & horizontal & inner_band
    if surfaces["front_rim"]:
        front = (
            (np.abs(centers[:, 2]) <= 0.20)
            & (normals[:, 2] < -0.72)
            & (support >= derived["inner_apothem_mm"] - 0.5)
            & (support <= derived["outer_apothem_mm"] + 0.5)
        )
        active |= front
    return active


def split_edges_conforming(
    vertices: np.ndarray,
    faces: np.ndarray,
    active_faces: np.ndarray,
    max_edge_mm: float,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    face_count = len(faces)
    edge_rows = np.concatenate(
        (faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]), axis=0
    )
    edge_keys = np.sort(edge_rows, axis=1)
    unique_edges, inverse = np.unique(edge_keys, axis=0, return_inverse=True)
    face_for_edge = np.tile(np.arange(face_count, dtype=np.int64), 3)
    edge_is_active = np.zeros(len(unique_edges), dtype=bool)
    np.logical_or.at(edge_is_active, inverse, active_faces[face_for_edge])
    lengths = np.linalg.norm(
        vertices[unique_edges[:, 1]] - vertices[unique_edges[:, 0]], axis=1
    )
    split_unique = edge_is_active & (lengths > max_edge_mm * (1.0 + 1e-9))
    if not np.any(split_unique):
        active_lengths = lengths[edge_is_active]
        return vertices, faces, {
            "split_edges": 0,
            "active_unique_edges": int(np.count_nonzero(edge_is_active)),
            "max_active_edge_mm": float(active_lengths.max()) if len(active_lengths) else 0.0,
        }

    midpoint_index = np.full(len(unique_edges), -1, dtype=np.int64)
    selected_edges = unique_edges[split_unique]
    midpoint_index[split_unique] = len(vertices) + np.arange(len(selected_edges), dtype=np.int64)
    midpoints = (vertices[selected_edges[:, 0]] + vertices[selected_edges[:, 1]]) * 0.5
    new_vertices = np.vstack((vertices, midpoints))

    m0 = midpoint_index[inverse[:face_count]]
    m1 = midpoint_index[inverse[face_count : 2 * face_count]]
    m2 = midpoint_index[inverse[2 * face_count :]]
    code = (m0 >= 0).astype(np.uint8) + 2 * (m1 >= 0).astype(np.uint8) + 4 * (m2 >= 0).astype(np.uint8)
    chunks: list[np.ndarray] = []

    def stack_triangles(parts: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> np.ndarray:
        return np.stack([np.column_stack(part) for part in parts], axis=1).reshape(-1, 3)

    for case in range(8):
        idx = np.flatnonzero(code == case)
        if not len(idx):
            continue
        a, b, c = faces[idx, 0], faces[idx, 1], faces[idx, 2]
        ab, bc, ca = m0[idx], m1[idx], m2[idx]
        if case == 0:
            chunks.append(faces[idx])
        elif case == 1:
            chunks.append(stack_triangles([(a, ab, c), (ab, b, c)]))
        elif case == 2:
            chunks.append(stack_triangles([(a, b, bc), (a, bc, c)]))
        elif case == 3:
            chunks.append(stack_triangles([(a, ab, bc), (ab, b, bc), (a, bc, c)]))
        elif case == 4:
            chunks.append(stack_triangles([(a, b, ca), (b, c, ca)]))
        elif case == 5:
            chunks.append(stack_triangles([(a, ab, ca), (ab, b, c), (ab, c, ca)]))
        elif case == 6:
            chunks.append(stack_triangles([(a, b, bc), (a, bc, ca), (bc, c, ca)]))
        else:
            chunks.append(
                stack_triangles(
                    [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]
                )
            )

    new_faces = np.vstack(chunks).astype(np.int64, copy=False)
    active_lengths = lengths[edge_is_active]
    return new_vertices, new_faces, {
        "split_edges": int(np.count_nonzero(split_unique)),
        "active_unique_edges": int(np.count_nonzero(edge_is_active)),
        "max_active_edge_mm": float(active_lengths.max()) if len(active_lengths) else 0.0,
    }


def adaptive_refine(
    mesh: trimesh.Trimesh,
    params: dict[str, Any],
    max_edge_mm: float,
) -> tuple[trimesh.Trimesh, dict[str, Any]]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    derived = derived_geometry(params)
    history: list[dict[str, Any]] = []
    for iteration in range(16):
        active = active_texture_faces(vertices, faces, params, derived)
        vertices, faces, step = split_edges_conforming(vertices, faces, active, max_edge_mm)
        step.update(
            {
                "iteration": iteration + 1,
                "active_faces": int(np.count_nonzero(active)),
                "vertices_after": int(len(vertices)),
                "faces_after": int(len(faces)),
            }
        )
        history.append(step)
        if step["split_edges"] == 0:
            break
    else:
        raise RuntimeError("Adaptive refinement did not converge in 16 iterations")

    refined = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    refined.remove_unreferenced_vertices()
    final_active = active_texture_faces(np.asarray(refined.vertices), np.asarray(refined.faces), params, derived)
    final_edges = np.concatenate(
        (refined.faces[:, [0, 1]], refined.faces[:, [1, 2]], refined.faces[:, [2, 0]]), axis=0
    )
    final_edge_faces = np.tile(np.arange(len(refined.faces), dtype=np.int64), 3)
    final_edge_keys = np.sort(final_edges, axis=1)
    final_unique_edges, final_inverse = np.unique(final_edge_keys, axis=0, return_inverse=True)
    final_edge_active = np.zeros(len(final_unique_edges), dtype=bool)
    np.logical_or.at(final_edge_active, final_inverse, final_active[final_edge_faces])
    final_lengths = np.linalg.norm(
        refined.vertices[final_unique_edges[:, 1]] - refined.vertices[final_unique_edges[:, 0]], axis=1
    )
    return refined, {
        "method": "shared-edge conforming adaptive bisection",
        "target_max_edge_mm": float(max_edge_mm),
        "iterations": history,
        "vertices_final": int(len(refined.vertices)),
        "faces_final": int(len(refined.faces)),
        "max_active_edge_final_mm": float(final_lengths[final_edge_active].max()) if np.any(final_edge_active) else 0.0,
        "watertight_before_displacement": bool(refined.is_watertight),
        "winding_consistent_before_displacement": bool(refined.is_winding_consistent),
    }


def apply_relief(
    mesh: trimesh.Trimesh,
    heightmap: np.ndarray,
    params: dict[str, Any],
) -> tuple[trimesh.Trimesh, dict[str, Any]]:
    texture = params["texture"]
    surfaces = texture["enabled_surfaces"]
    derived = derived_geometry(params)
    vertices = np.asarray(mesh.vertices, dtype=np.float64).copy()
    normals = np.asarray(mesh.vertex_normals, dtype=np.float64)
    support = hex_support(vertices[:, :2])
    orientation = np.sum(normals[:, :2] * vertices[:, :2], axis=1)
    vertical_repeat = float(texture["tile_size_mm"])
    feather = float(texture["transition_feather_mm"])
    z_start = float(texture["side_texture_z_start_mm"])
    z_end = float(texture["side_texture_z_end_mm"])
    horizontal = np.abs(normals[:, 2]) < 0.36
    z_weight = smoothstep01((vertices[:, 2] - z_start) / feather) * smoothstep01(
        (z_end - vertices[:, 2]) / feather
    )

    displacement = np.zeros(len(vertices), dtype=np.float64)
    surface_counts: dict[str, int] = {}

    outer_mask = (
        horizontal
        & (orientation > 0.0)
        & (support >= derived["outer_apothem_mm"] - params["geometry"]["corner_radius_mm"] - 0.9)
        & (support <= derived["outer_apothem_mm"] + 0.9)
        & (z_weight > 0.0)
    )
    if surfaces["outer_sides"] and np.any(outer_mask):
        u = normalized_perimeter_u(vertices[outer_mask, :2], derived["outer_side_mm"])
        sampled = sample_heightmap(heightmap, u, vertices[outer_mask, 2] / vertical_repeat)
        displacement[outer_mask] = sampled * texture["side_max_depth_mm"] * z_weight[outer_mask]
    surface_counts["outer_side_vertices"] = int(np.count_nonzero(outer_mask))

    inner_mask = (
        horizontal
        & (orientation < 0.0)
        & (support >= derived["inner_apothem_mm"] - 0.9)
        & (support <= derived["inner_apothem_mm"] + derived["inner_corner_radius_mm"] + 0.9)
        & (z_weight > 0.0)
    )
    if surfaces["inner_sides"] and np.any(inner_mask):
        u = normalized_perimeter_u(vertices[inner_mask, :2], derived["inner_side_mm"])
        sampled = sample_heightmap(heightmap, u, vertices[inner_mask, 2] / vertical_repeat)
        displacement[inner_mask] = sampled * texture["side_max_depth_mm"] * z_weight[inner_mask]
    surface_counts["inner_side_vertices"] = int(np.count_nonzero(inner_mask))

    margin = float(texture["front_edge_margin_mm"])
    inner_distance = support - derived["inner_apothem_mm"]
    outer_distance = derived["outer_apothem_mm"] - support
    front_weight = smoothstep01(inner_distance / margin) * smoothstep01(outer_distance / margin)
    front_mask = (normals[:, 2] < -0.86) & (np.abs(vertices[:, 2]) < 0.12) & (front_weight > 0.0)
    if surfaces["front_rim"] and np.any(front_mask):
        sampled = sample_heightmap(
            heightmap,
            vertices[front_mask, 0] / vertical_repeat,
            vertices[front_mask, 1] / vertical_repeat,
        )
        front_amount = sampled * texture["front_max_depth_mm"] * front_weight[front_mask]
        displacement[front_mask] = np.maximum(displacement[front_mask], front_amount)
    surface_counts["front_rim_vertices"] = int(np.count_nonzero(front_mask))

    moved = displacement > 1e-8
    vertices[moved] -= normals[moved] * displacement[moved, None]
    textured = trimesh.Trimesh(vertices=vertices, faces=np.asarray(mesh.faces), process=False)
    textured.remove_unreferenced_vertices()
    rear_cutoff = params["geometry"]["depth_mm"] - params["geometry"]["connector_insert_length_mm"]
    moved_in_rear_zone = moved & (np.asarray(mesh.vertices)[:, 2] >= rear_cutoff - 1e-9)
    return textured, {
        **surface_counts,
        "moved_vertices": int(np.count_nonzero(moved)),
        "maximum_applied_displacement_mm": float(displacement.max(initial=0.0)),
        "mean_nonzero_displacement_mm": float(displacement[moved].mean()) if np.any(moved) else 0.0,
        "rear_functional_zone_starts_z_mm": float(rear_cutoff),
        "moved_vertices_in_rear_functional_zone": int(np.count_nonzero(moved_in_rear_zone)),
        "watertight_after_displacement": bool(textured.is_watertight),
        "winding_consistent_after_displacement": bool(textured.is_winding_consistent),
    }


def mesh_summary(mesh: trimesh.Trimesh) -> dict[str, Any]:
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_mm3": float(mesh.volume),
        "area_mm2": float(mesh.area),
        "bounds_xyz_mm": np.asarray(mesh.bounds).round(6).tolist(),
        "extents_xyz_mm": np.asarray(mesh.extents).round(6).tolist(),
        "body_count": int(len(mesh.split(only_watertight=False))),
    }


def load_stl(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load_mesh(path, force="mesh", process=True)
    if not isinstance(loaded, trimesh.Trimesh):
        raise TypeError(f"Expected a mesh in {path}")
    loaded.merge_vertices()
    return loaded


def generate_variant(
    name: str,
    cad_object: cq.Workplane,
    quality: str,
    max_edge_mm: float,
    heightmap: np.ndarray,
    params: dict[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    if quality == "preview":
        smooth_path = PREVIEW_DIR / f".{name}_smooth_tmp.stl"
        textured_path = PREVIEW_DIR / f"{name}_preview.stl"
        step_path = None
    else:
        smooth_path = EXPORT_DIR / f"{name}_smooth.stl"
        textured_path = EXPORT_DIR / f"{name}_wood_relief.stl"
        step_path = EXPORT_DIR / f"{name}.step"

    cad_report = inspect_cq_object(cad_object)
    if not cad_report["brep_valid"] or cad_report["solid_count"] != 1:
        raise RuntimeError(f"Invalid CadQuery body for {name}: {cad_report}")
    if step_path is not None:
        export_cadquery(cad_object, step_path, params)
        cad_report["step_path"] = str(step_path)
        cad_report["step_bytes"] = step_path.stat().st_size
        cad_report["step_reload"] = reload_step_report(step_path)

    export_cadquery(cad_object, smooth_path, params)
    smooth = load_stl(smooth_path)
    smooth_report = mesh_summary(smooth)
    if not smooth.is_watertight or not smooth.is_winding_consistent:
        raise RuntimeError(f"Smooth CadQuery STL is invalid: {smooth_path}")

    refined, refinement_report = adaptive_refine(smooth, params, max_edge_mm)
    if not refined.is_watertight or not refined.is_winding_consistent:
        raise RuntimeError("Conforming refinement damaged mesh topology")
    textured, displacement_report = apply_relief(refined, heightmap, params)
    if not textured.is_watertight or not textured.is_winding_consistent:
        raise RuntimeError("Heightmap displacement damaged mesh topology")
    if displacement_report["moved_vertices_in_rear_functional_zone"] != 0:
        raise RuntimeError("Relief reached the protected rear connector zone")

    textured.export(textured_path, file_type="stl")
    reloaded = load_stl(textured_path)
    final_report = mesh_summary(reloaded)
    file_mib = textured_path.stat().st_size / (1024.0 * 1024.0)
    max_triangles = params["export"]["maximum_textured_triangles"]
    max_mib = params["export"]["maximum_textured_stl_mib"]
    feature = float(params["texture"]["minimum_printable_feature_mm"])
    sampling_pass = refinement_report["max_active_edge_final_mm"] <= feature / 2.0 + 1e-9
    bounds_not_larger = bool(
        np.all(np.asarray(reloaded.extents) <= np.asarray(smooth.extents) + 0.06)
    )
    acceptance = {
        "reloaded_watertight": bool(reloaded.is_watertight),
        "reloaded_winding_consistent": bool(reloaded.is_winding_consistent),
        "reloaded_one_body": final_report["body_count"] == 1,
        "reloaded_positive_volume": final_report["volume_mm3"] > 0.0,
        "triangle_budget_pass": final_report["faces"] <= max_triangles,
        "file_budget_pass": file_mib <= max_mib,
        "edge_feature_criterion": {
            "applicable": quality == "final",
            "minimum_printable_feature_mm": feature,
            "required_max_edge_mm": feature / 2.0,
            "measured_max_active_edge_mm": refinement_report["max_active_edge_final_mm"],
            "passed": sampling_pass,
        },
        "bounds_do_not_exceed_smooth_master": bounds_not_larger,
        "rear_functional_zone_untouched": displacement_report["moved_vertices_in_rear_functional_zone"] == 0,
    }
    acceptance["passed"] = bool(
        all(value for key, value in acceptance.items() if key != "edge_feature_criterion")
        and (quality != "final" or acceptance["edge_feature_criterion"]["passed"])
    )
    if not acceptance["passed"]:
        raise RuntimeError(f"Generation acceptance failed for {name}: {acceptance}")

    if quality == "preview" and smooth_path.exists():
        smooth_path.unlink()

    return {
        "name": name,
        "quality": quality,
        "cadquery": cad_report,
        "smooth_mesh": smooth_report,
        "refinement": refinement_report,
        "displacement": displacement_report,
        "textured_export": str(textured_path),
        "textured_file_mib": file_mib,
        "textured_reloaded": final_report,
        "acceptance": acceptance,
        "elapsed_seconds": time.perf_counter() - started,
        "peak_process_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
    }


def software_report() -> dict[str, str]:
    import PIL
    import scipy

    return {
        "python": platform.python_version(),
        "cadquery": cq.__version__,
        "numpy": np.__version__,
        "trimesh": trimesh.__version__,
        "pillow": PIL.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality", choices=("preview", "final"), required=True)
    parser.add_argument("--variant", choices=("plain", "hanger", "both"), default="both")
    args = parser.parse_args()

    for directory in (EXPORT_DIR, PREVIEW_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    params = load_parameters()
    texture = params["texture"]
    max_edge = float(
        texture["preview_max_edge_mm"] if args.quality == "preview" else texture["final_max_edge_mm"]
    )
    if args.quality == "final" and max_edge > texture["minimum_printable_feature_mm"] / 2.0:
        raise ValueError("Final mesh edge is too coarse for the declared printable feature")

    base = load_base_module(params)
    heightmap, heightmap_report = build_periodic_heightmap(params)
    derived = derived_geometry(params)
    seam_report = validate_perimeter_seams(heightmap)
    mapping_report = {
        "side_mapping": {
            "coordinate": "continuous_perimeter_u_mm / (6 * actual_side_length_mm)",
            "outer_perimeter_mm": 6.0 * derived["outer_side_mm"],
            "inner_perimeter_mm": 6.0 * derived["inner_side_mm"],
            "cycles_per_hex_perimeter": 1,
            "vertical_coordinate": "+Z / vertical_repeat_mm",
        },
        "front_mapping": {"coordinate": "world X / vertical_repeat_mm, world Y / vertical_repeat_mm", "orientation": "+Y"},
        "seam_continuity": seam_report,
    }
    image_convention = {
        "grayscale_policy": "Pillow convert('L'), ImageOps.fit cover crop to square, autocontrast cutoff=0.5; dark local detail and Sobel edges produce relief intensity",
        "source_crop_fit_behavior": "cover crop (no stretch), then mirrored 2x2 periodic tile; source image is read-only",
        "orientation": {"side_vertical_image_axis": "+Z", "front_vertical_image_axis": "+Y"},
        "engraving_sign": "positive relief intensity is displaced opposite the outward mesh normal (material removal)",
        "mode": texture["heightmap_mode"],
    }
    variants: list[tuple[str, cq.Workplane]] = []
    if args.variant in ("plain", "both"):
        variants.append(("wabe_ohne_aufhaengung", base.make_hex_module(enable_hangers=False)))
    if args.variant in ("hanger", "both"):
        variants.append(("wabe_mit_aufhaengung", base.make_hex_module(enable_hangers=True)))

    report: dict[str, Any] = {
        "method": "CadQuery exact B-Rep master plus conforming adaptive surface-mesh heightmap engraving",
        "hanger_geometry": params["geometry"]["hanger_connection_style"],
        "quality": args.quality,
        "target_max_edge_mm": max_edge,
        "parameters": str(PARAMETERS_PATH),
        "parameters_sha256": sha256_file(PARAMETERS_PATH),
        "base_cadquery_source": str(source_path(params, "cadquery_script")),
        "base_cadquery_source_sha256": sha256_file(source_path(params, "cadquery_script")),
        "heightmap": heightmap_report,
        "image_convention": image_convention,
        "mapping": mapping_report,
        "wall_residual": local_wall_residual_check(heightmap, params),
        "provenance": {
            "wood_image": {
                "path": str(source_path(params, "wood_image")),
                **provenance_entry(params, "wood_image", {"status": "BLOCKED_LIBRARY_ASSET", "license": "unknown", "basis": "no file-level license recorded"}),
            },
            "external_cadquery_source": {
                "path": str(source_path(params, "cadquery_script")),
                "status": "BLOCKED_LIBRARY_ASSET",
                "license": "unknown",
                "basis": "no file-level license recorded",
            },
        },
        "software": software_report(),
        "variants": [],
    }
    for name, cad_object in variants:
        print(f"Generating {args.quality}: {name} at {max_edge:.3f} mm target edge")
        variant_report = generate_variant(name, cad_object, args.quality, max_edge, heightmap, params)
        report["variants"].append(variant_report)
        print(
            f"  {variant_report['textured_reloaded']['faces']} faces, "
            f"{variant_report['textured_file_mib']:.2f} MiB, "
            f"watertight={variant_report['textured_reloaded']['watertight']}"
        )

    if args.quality == "final":
        connector = base.make_connector_key()
        connector_step = EXPORT_DIR / "waben_verbinder.step"
        connector_stl = EXPORT_DIR / "waben_verbinder.stl"
        export_cadquery(connector, connector_step, params)
        export_cadquery(connector, connector_stl, params)
        connector_mesh = load_stl(connector_stl)
        report["connector"] = {
            "cadquery": inspect_cq_object(connector),
            "step_reload": reload_step_report(connector_step),
            "mesh_reload": mesh_summary(connector_mesh),
        }

    report["passed"] = bool(
        report["variants"]
        and all(item["acceptance"]["passed"] for item in report["variants"])
        and (args.quality != "final" or report["connector"]["mesh_reload"]["watertight"])
    )
    report_path = REPORT_DIR / f"generation_{args.quality}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Report: {report_path}")
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
