#!/usr/bin/env python3
"""Build the hybrid organic/parametric ZEN KINTSUGI WAVE v2 release.

The user-supplied GLBs remain immutable source assets.  Their visible front
envelopes are reconstructed as watertight, flat-backed relief solids at a
printer-appropriate physical pitch.  All FIFO, mounting, connector, bowl, and
sliding-interface geometry remains parametric and dimensionally authoritative.
Units are millimetres throughout the manufacturing model.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import trimesh
from scipy import ndimage
from scipy.interpolate import RegularGridInterpolator
from shapely.geometry import Polygon

from generate_zen_kintsugi import (
    GOLD_DENSITY_G_CM3,
    LAYER_HEIGHT,
    LINE_WIDTH,
    NOZZLE,
    STONE_DENSITY_G_CM3,
    WOOD_DENSITY_G_CM3,
    Params,
    back_profile,
    clean,
    collision_check,
    connector_cutters,
    crown_dovetail,
    difference_mesh,
    export_stl,
    extrude_xy,
    extrude_xz,
    extrude_yz,
    front_profile,
    make_connector_pin,
    make_fit_coupon,
    make_test_roll,
    mesh_metrics,
    render_preview,
    side_profile,
    transform_copy,
    union_meshes,
    wall_mount_cutters,
    write_3mf,
)


VERSION = "2.0.0"
PRODUCT = "ZEN_KINTSUGI_WAVE_FIFO_5R_HYBRID"

SIDE_RAIL_Y = (11.8, 109.2)
SIDE_RAIL_Z0 = 10.0
SIDE_RAIL_Z1 = 112.0
SIDE_RAIL_BASE_WIDTH = 4.0
SIDE_RAIL_HEAD_WIDTH = 5.2
SIDE_RAIL_HEIGHT = 1.05
SIDE_CHANNEL_OPEN_WIDTH = 4.50
SIDE_CHANNEL_INNER_WIDTH = 5.70
SIDE_CHANNEL_DEPTH = 1.32
SIDE_PANEL_BACK_GAP = 0.05


@dataclass
class ReliefField:
    name: str
    xs: np.ndarray
    ys: np.ndarray
    mask_cells: np.ndarray
    normalized_nodes: np.ndarray
    used_nodes: np.ndarray
    width_mm: float
    height_mm: float
    pitch_x_mm: float
    pitch_y_mm: float
    source_width: float
    source_height: float
    uniform_scale_mm_per_source_unit: float
    source_height_low: float
    source_height_high: float
    removed_component_count: int


def load_source_mesh(path: Path) -> trimesh.Trimesh:
    scene = trimesh.load(path, force="scene", process=False)
    meshes: list[trimesh.Trimesh] = []
    for node_name in scene.graph.nodes_geometry:
        transform, geometry_name = scene.graph[node_name]
        mesh = scene.geometry[geometry_name].copy()
        mesh.apply_transform(transform)
        meshes.append(mesh)
    if not meshes:
        raise ValueError(f"No triangle mesh in {path}")
    return meshes[0] if len(meshes) == 1 else trimesh.util.concatenate(meshes)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _rasterize_triangles(
    vertices: np.ndarray,
    faces: np.ndarray,
    x_coordinates: np.ndarray,
    y_coordinates: np.ndarray,
) -> np.ndarray:
    """Rasterize the maximum projected Z envelope onto arbitrary XY samples."""
    result = np.full((len(y_coordinates), len(x_coordinates)), -np.inf, dtype=np.float64)
    for face in faces:
        tri = vertices[face]
        x0, y0, z0 = tri[0]
        x1, y1, z1 = tri[1]
        x2, y2, z2 = tri[2]
        denominator = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(denominator) < 1e-13:
            continue
        ix0 = max(0, int(np.searchsorted(x_coordinates, min(x0, x1, x2), side="left")) - 1)
        ix1 = min(len(x_coordinates), int(np.searchsorted(x_coordinates, max(x0, x1, x2), side="right")) + 1)
        iy0 = max(0, int(np.searchsorted(y_coordinates, min(y0, y1, y2), side="left")) - 1)
        iy1 = min(len(y_coordinates), int(np.searchsorted(y_coordinates, max(y0, y1, y2), side="right")) + 1)
        if ix0 >= ix1 or iy0 >= iy1:
            continue
        xx, yy = np.meshgrid(x_coordinates[ix0:ix1], y_coordinates[iy0:iy1])
        w0 = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / denominator
        w1 = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / denominator
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -1e-8) & (w1 >= -1e-8) & (w2 >= -1e-8)
        if not np.any(inside):
            continue
        depth = w0 * z0 + w1 * z1 + w2 * z2
        view = result[iy0:iy1, ix0:ix1]
        np.maximum(view, np.where(inside, depth, -np.inf), out=view)
    return result


def rasterize_front_envelope(
    mesh: trimesh.Trimesh,
    name: str,
    max_width_mm: float,
    max_height_mm: float,
    pitch_mm: float,
    center_xy: tuple[float, float] = (0.0, 0.0),
    min_component_area_mm2: float = 0.8,
) -> ReliefField:
    source_bounds = mesh.bounds
    source_width = float(source_bounds[1, 0] - source_bounds[0, 0])
    source_height = float(source_bounds[1, 1] - source_bounds[0, 1])
    scale = min(max_width_mm / source_width, max_height_mm / source_height)
    width = source_width * scale
    height = source_height * scale
    source_center = (source_bounds[0, :2] + source_bounds[1, :2]) / 2.0

    transformed = mesh.vertices.copy()
    transformed[:, :2] = (transformed[:, :2] - source_center) * scale
    transformed[:, 0] += center_xy[0]
    transformed[:, 1] += center_xy[1]

    nx = max(4, int(math.ceil(width / pitch_mm)))
    ny = max(4, int(math.ceil(height / pitch_mm)))
    xs = np.linspace(center_xy[0] - width / 2.0, center_xy[0] + width / 2.0, nx + 1)
    ys = np.linspace(center_xy[1] - height / 2.0, center_xy[1] + height / 2.0, ny + 1)
    centers_x = (xs[:-1] + xs[1:]) / 2.0
    centers_y = (ys[:-1] + ys[1:]) / 2.0

    node_depth = _rasterize_triangles(transformed, mesh.faces, xs, ys)
    cell_depth = _rasterize_triangles(transformed, mesh.faces, centers_x, centers_y)
    mask = np.isfinite(cell_depth)

    labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=int))
    removed = 0
    if count:
        areas = np.bincount(labels.ravel()) * (width / nx) * (height / ny)
        keep = np.zeros(count + 1, dtype=bool)
        keep[1:] = areas[1:] >= min_component_area_mm2
        largest = int(np.argmax(areas[1:]) + 1)
        keep[largest] = True
        removed = int(count - np.count_nonzero(keep[1:]))
        mask = keep[labels]
    if not np.any(mask):
        raise ValueError(f"Projected envelope is empty: {name}")

    used = np.zeros_like(node_depth, dtype=bool)
    used[:-1, :-1] |= mask
    used[:-1, 1:] |= mask
    used[1:, 1:] |= mask
    used[1:, :-1] |= mask

    finite = np.isfinite(node_depth)
    if not np.any(finite):
        raise ValueError(f"No projected node heights: {name}")
    nearest = ndimage.distance_transform_edt(~finite, return_distances=False, return_indices=True)
    filled = node_depth[tuple(nearest)]
    values = filled[used]
    low, high = np.quantile(values, [0.01, 0.99])
    if high - low < 1e-9:
        high = low + 1.0
    normalized = np.clip((filled - low) / (high - low), 0.0, 1.0)

    return ReliefField(
        name=name,
        xs=xs,
        ys=ys,
        mask_cells=mask,
        normalized_nodes=normalized,
        used_nodes=used,
        width_mm=width,
        height_mm=height,
        pitch_x_mm=width / nx,
        pitch_y_mm=height / ny,
        source_width=source_width,
        source_height=source_height,
        uniform_scale_mm_per_source_unit=scale,
        source_height_low=float(low),
        source_height_high=float(high),
        removed_component_count=removed,
    )


def grid_solid(
    field: ReliefField,
    bottom_nodes: np.ndarray,
    top_nodes: np.ndarray,
) -> trimesh.Trimesh:
    if bottom_nodes.shape != field.normalized_nodes.shape or top_nodes.shape != bottom_nodes.shape:
        raise ValueError("Height array shape mismatch")
    used = field.used_nodes
    bottom_index = np.full(used.shape, -1, dtype=np.int64)
    top_index = np.full(used.shape, -1, dtype=np.int64)
    yy, xx = np.nonzero(used)
    count = len(xx)
    bottom_index[yy, xx] = np.arange(count)
    top_index[yy, xx] = np.arange(count, 2 * count)
    base_vertices = np.column_stack([field.xs[xx], field.ys[yy], bottom_nodes[yy, xx]])
    top_vertices = np.column_stack([field.xs[xx], field.ys[yy], top_nodes[yy, xx]])
    vertices = np.vstack([base_vertices, top_vertices])
    faces: list[list[int]] = []

    rows, columns = field.mask_cells.shape
    for row in range(rows):
        for column in range(columns):
            if not field.mask_cells[row, column]:
                continue
            bl_t = int(top_index[row, column])
            br_t = int(top_index[row, column + 1])
            tr_t = int(top_index[row + 1, column + 1])
            tl_t = int(top_index[row + 1, column])
            bl_b = int(bottom_index[row, column])
            br_b = int(bottom_index[row, column + 1])
            tr_b = int(bottom_index[row + 1, column + 1])
            tl_b = int(bottom_index[row + 1, column])
            faces.extend([[bl_t, br_t, tr_t], [bl_t, tr_t, tl_t]])
            faces.extend([[bl_b, tr_b, br_b], [bl_b, tl_b, tr_b]])

            if column == 0 or not field.mask_cells[row, column - 1]:
                faces.extend([[bl_b, bl_t, tl_t], [bl_b, tl_t, tl_b]])
            if column == columns - 1 or not field.mask_cells[row, column + 1]:
                faces.extend([[br_b, tr_b, tr_t], [br_b, tr_t, br_t]])
            if row == 0 or not field.mask_cells[row - 1, column]:
                faces.extend([[bl_b, br_b, br_t], [bl_b, br_t, bl_t]])
            if row == rows - 1 or not field.mask_cells[row + 1, column]:
                faces.extend([[tl_b, tl_t, tr_t], [tl_b, tr_t, tr_b]])

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=False)
    return clean(mesh)


def relief_mesh(field: ReliefField, backer_mm: float, relief_mm: float) -> tuple[trimesh.Trimesh, np.ndarray]:
    bottom = np.zeros_like(field.normalized_nodes)
    top = backer_mm + relief_mm * field.normalized_nodes
    return grid_solid(field, bottom, top), top


def add_side_channels(panel: trimesh.Trimesh, field: ReliefField) -> trimesh.Trimesh:
    cutters = []
    for body_y in SIDE_RAIL_Y:
        local_x = body_y - 60.5
        cross_section = Polygon(
            [
                (local_x - SIDE_CHANNEL_OPEN_WIDTH / 2.0, -0.08),
                (local_x + SIDE_CHANNEL_OPEN_WIDTH / 2.0, -0.08),
                (local_x + SIDE_CHANNEL_INNER_WIDTH / 2.0, SIDE_CHANNEL_DEPTH),
                (local_x - SIDE_CHANNEL_INNER_WIDTH / 2.0, SIDE_CHANNEL_DEPTH),
            ]
        )
        y0 = SIDE_RAIL_Z0 - 62.0
        y1 = float(field.ys[-1] + 0.35)
        cutters.append(extrude_xz(cross_section, y1 - y0, y0))
    return difference_mesh(panel, cutters)


def make_conformal_inlay(
    source: trimesh.Trimesh,
    name: str,
    panel_field: ReliefField,
    panel_top: np.ndarray,
    max_width_mm: float,
    max_height_mm: float,
    center_xy: tuple[float, float],
) -> tuple[trimesh.Trimesh, trimesh.Trimesh, ReliefField]:
    field = rasterize_front_envelope(
        source,
        name,
        max_width_mm=max_width_mm,
        max_height_mm=max_height_mm,
        pitch_mm=0.42,
        center_xy=center_xy,
        min_component_area_mm2=0.30,
    )
    interpolator = RegularGridInterpolator(
        (panel_field.ys, panel_field.xs), panel_top, bounds_error=False, fill_value=1.8
    )
    xx, yy = np.meshgrid(field.xs, field.ys)
    panel_surface = interpolator(np.column_stack([yy.ravel(), xx.ravel()])).reshape(xx.shape)
    bottom = panel_surface - 0.12
    top = panel_surface + 0.55 + 0.25 * field.normalized_nodes
    conformal = grid_solid(field, bottom, top)
    flat_bottom = np.zeros_like(field.normalized_nodes)
    flat_top = 0.62 + 0.18 * field.normalized_nodes
    flat = grid_solid(field, flat_bottom, flat_top)
    return conformal, flat, field


def make_clean_body(p: Params, kind: str, pattern: str, style: str = "wave") -> trimesh.Trimesh:
    h = p.crown_height if kind == "crown" else p.module_pitch
    phase = 0.15 if pattern == "A" else 1.05
    parts = [
        extrude_yz(side_profile(p, h, style, phase), p.side_thickness, -p.outer_half_width),
        extrude_yz(side_profile(p, h, style, phase + math.pi), p.side_thickness, p.inner_half_width),
        extrude_xz(back_profile(p, h, style, phase), p.back_thickness, 0.0),
        extrude_xz(front_profile(p, h, kind, phase), p.front_thickness, p.front_y),
    ]
    if kind == "output":
        rail_length = p.front_y - p.back_thickness + 1.0
        for x in (-34.0, 34.0):
            rail = trimesh.creation.box(extents=[11.0, rail_length, p.output_rail_height])
            rail.apply_translation(
                [x, p.back_thickness + rail_length / 2.0 - 0.5, p.output_rail_height / 2.0]
            )
            parts.append(rail)
    if kind == "crown":
        _, male_mesh = crown_dovetail(p)
        tray_pad = trimesh.creation.box(extents=[p.side_thickness, 22.0, 40.0])
        tray_pad.apply_translation([p.inner_half_width + p.side_thickness / 2.0, p.roll_center_y, 20.0])
        parts.extend([tray_pad, male_mesh])
    body = union_meshes(parts)
    top = kind != "crown"
    bottom = kind != "output"
    cutters = connector_cutters(p, h, top=top, bottom=bottom)
    if kind != "crown":
        cutters.extend(wall_mount_cutters(p, h))
    return difference_mesh(body, cutters)


def add_side_slide_interface(p: Params, body: trimesh.Trimesh) -> trimesh.Trimesh:
    additions = []
    for center_y in SIDE_RAIL_Y:
        anchor = trimesh.creation.box(extents=[p.side_thickness, 6.4, 114.0])
        anchor.apply_translation([p.inner_half_width + p.side_thickness / 2.0, center_y, 62.0])
        additions.append(anchor)
        cross_section = Polygon(
            [
                (p.outer_half_width - 0.18, center_y - SIDE_RAIL_BASE_WIDTH / 2.0),
                (p.outer_half_width - 0.18, center_y + SIDE_RAIL_BASE_WIDTH / 2.0),
                (p.outer_half_width + SIDE_RAIL_HEIGHT, center_y + SIDE_RAIL_HEAD_WIDTH / 2.0),
                (p.outer_half_width + SIDE_RAIL_HEIGHT, center_y - SIDE_RAIL_HEAD_WIDTH / 2.0),
            ]
        )
        additions.append(extrude_xy(cross_section, SIDE_RAIL_Z1 - SIDE_RAIL_Z0, z0=SIDE_RAIL_Z0))
    return union_meshes([body, *additions])


def front_relief_to_module(
    mesh: trimesh.Trimesh,
    p: Params,
    x_center: float,
    mirror: bool = False,
) -> trimesh.Trimesh:
    result = mesh.copy()
    vertices = result.vertices.copy()
    sign = -1.0 if mirror else 1.0
    result.vertices = np.column_stack(
        [
            x_center + sign * vertices[:, 0],
            p.total_depth - 0.28 + vertices[:, 2],
            p.module_pitch / 2.0 + vertices[:, 1],
        ]
    )
    if mirror:
        result.faces = result.faces[:, ::-1]
    return clean(result)


def crown_relief_to_module(mesh: trimesh.Trimesh, p: Params, field: ReliefField) -> trimesh.Trimesh:
    result = mesh.copy()
    vertices = result.vertices.copy()
    result.vertices = np.column_stack(
        [
            vertices[:, 0],
            p.total_depth - 0.28 + vertices[:, 2],
            p.crown_height - field.ys[0] + vertices[:, 1],
        ]
    )
    return clean(result)


def side_relief_to_module(mesh: trimesh.Trimesh, p: Params) -> trimesh.Trimesh:
    result = mesh.copy()
    vertices = result.vertices.copy()
    result.vertices = np.column_stack(
        [
            p.outer_half_width + SIDE_PANEL_BACK_GAP + vertices[:, 2],
            p.total_depth / 2.0 + vertices[:, 0],
            p.module_pitch / 2.0 + vertices[:, 1],
        ]
    )
    return clean(result)


def make_hybrid_scent_tray(p: Params, fascia: trimesh.Trimesh) -> trimesh.Trimesh:
    outer = trimesh.creation.cylinder(radius=26.0, height=9.0, sections=96)
    outer.apply_translation([p.outer_half_width + 30.0, p.roll_center_y, 26.5])
    inner = trimesh.creation.cylinder(radius=21.5, height=7.6, sections=96)
    inner.apply_translation([p.outer_half_width + 30.0, p.roll_center_y, 29.0])
    bowl = difference_mesh(outer, [inner])

    bracket = trimesh.creation.box(extents=[12.0, 30.0, 40.0])
    bracket.apply_translation([p.outer_half_width + 6.0, p.roll_center_y, 20.0])
    ribs = []
    rib_profile = Polygon(
        [
            (p.outer_half_width + 8.0, 8.0),
            (p.outer_half_width + 8.0, 22.0),
            (p.outer_half_width + 38.0, 22.0),
        ]
    )
    for y_center in (p.roll_center_y - 16.0, p.roll_center_y + 16.0):
        ribs.append(extrude_xz(rib_profile, 4.2, y_center - 2.1))

    fascia_global = fascia.copy()
    vertices = fascia_global.vertices.copy()
    fascia_global.vertices = np.column_stack(
        [
            p.outer_half_width + 11.6 + vertices[:, 2],
            p.roll_center_y + vertices[:, 0],
            34.0 + vertices[:, 1],
        ]
    )
    combined = union_meshes([bowl, bracket, fascia_global, *ribs])
    male, _ = crown_dovetail(p)
    female = male.buffer(0.38, join_style=2)
    slot = extrude_xy(female, 36.0, z0=-0.1)
    return difference_mesh(combined, [slot])


def make_slide_coupon(clearance_extra: float = 0.0) -> tuple[trimesh.Trimesh, trimesh.Trimesh]:
    base = trimesh.creation.box(extents=[18.0, 32.0, 3.0])
    base.apply_translation([0.0, 16.0, 1.5])
    rail_profile = Polygon(
        [
            (-SIDE_RAIL_BASE_WIDTH / 2.0, 3.0 - 0.12),
            (SIDE_RAIL_BASE_WIDTH / 2.0, 3.0 - 0.12),
            (SIDE_RAIL_HEAD_WIDTH / 2.0, 3.0 + SIDE_RAIL_HEIGHT),
            (-SIDE_RAIL_HEAD_WIDTH / 2.0, 3.0 + SIDE_RAIL_HEIGHT),
        ]
    )
    male = union_meshes([base, extrude_xz(rail_profile, 26.0, 3.0)])

    female = trimesh.creation.box(extents=[18.0, 32.0, 1.8])
    female.apply_translation([0.0, 16.0, 0.9])
    channel_profile = Polygon(
        [
            (-(SIDE_CHANNEL_OPEN_WIDTH + clearance_extra) / 2.0, -0.08),
            ((SIDE_CHANNEL_OPEN_WIDTH + clearance_extra) / 2.0, -0.08),
            ((SIDE_CHANNEL_INNER_WIDTH + clearance_extra) / 2.0, SIDE_CHANNEL_DEPTH),
            (-(SIDE_CHANNEL_INNER_WIDTH + clearance_extra) / 2.0, SIDE_CHANNEL_DEPTH),
        ]
    )
    channel = extrude_xz(channel_profile, 28.2, 3.8)
    female = difference_mesh(female, [channel])
    return male, female


def validate_interface_clearance(body: trimesh.Trimesh, panel_assembled: trimesh.Trimesh) -> dict:
    intersection = trimesh.boolean.intersection(
        [body, panel_assembled], engine="manifold", check_volume=False
    )
    volume = 0.0 if intersection is None or not len(intersection.faces) else abs(float(intersection.volume))
    return {
        "male_base_width_mm": SIDE_RAIL_BASE_WIDTH,
        "male_head_width_mm": SIDE_RAIL_HEAD_WIDTH,
        "male_height_mm": SIDE_RAIL_HEIGHT,
        "female_open_width_mm": SIDE_CHANNEL_OPEN_WIDTH,
        "female_inner_width_mm": SIDE_CHANNEL_INNER_WIDTH,
        "female_depth_mm": SIDE_CHANNEL_DEPTH,
        "lateral_clearance_each_side_at_base_mm": (SIDE_CHANNEL_OPEN_WIDTH - SIDE_RAIL_BASE_WIDTH) / 2.0,
        "lateral_clearance_each_side_at_head_mm": (SIDE_CHANNEL_INNER_WIDTH - SIDE_RAIL_HEAD_WIDTH) / 2.0,
        "depth_clearance_mm": SIDE_CHANNEL_DEPTH - SIDE_RAIL_HEIGHT,
        "assembled_body_panel_intersection_mm3": volume,
        "retained_by_undercut": SIDE_RAIL_HEAD_WIDTH > SIDE_CHANNEL_OPEN_WIDTH,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_readme(path: Path, p: Params, relief_report: dict) -> None:
    text = f"""# ZEN KINTSUGI WAVE FIFO – Hybrid v{VERSION}

## Ergebnis

Modulare, wandmontierte FIFO-Säule für **{p.roll_count} Rollen bis Ø {p.roll_diameter:.0f} × {p.roll_width:.0f} mm**. Der funktionskritische Schacht, die Wandbefestigung, Modulverbinder, Dovetailführung und Duftschale sind parametrisch. Die sichtbaren Dekore wurden aus den gelieferten GLB-Quellmeshes als geschlossene, flach rückseitige Druckkörper rekonstruiert.

- Grundkörper: ca. **{2*p.outer_half_width:.0f} × {p.total_depth:.1f} × {p.tower_height:.0f} mm**
- Höhe inklusive organischer Krone: ca. **{p.tower_height + relief_report['crown_wave']['placed_height_mm']:.0f} mm**
- Prüfzylinder im CAD: **Ø {p.roll_diameter + 2:.0f} × {p.roll_width + 2:.0f} mm**
- Alle Herstellungsdateien: Millimeter

## Empfohlene Herstellungsroute

1. Zuerst `rail_coupon_male.stl` und `rail_coupon_female.stl` drucken und die Schiebepassung prüfen.
2. Seitenteile bevorzugt als `SIDE_PANEL_A_multicolor.3mf` beziehungsweise `SIDE_PANEL_B_multicolor.3mf` **flach mit der Rückseite auf dem Bett** drucken. Die Goldader ist ein eigener Farbkörper.
3. Körpermodule aufrecht drucken. Die organischen Frontapplikationen sind bereits mit den Mittelmodulen verschmolzen; die Krone ist mit dem Kronenmodul verschmolzen.
4. Seitenpaneel von oben in beide Führungen einschieben, bis der geschlossene Kanalboden am Schienenanfang stoppt. Paneele vor dem Stapeln der Module montieren.
5. Module mit je vier Pins verbinden und zusätzlich an der Wand verschrauben. Die Pins richten aus; die Schrauben tragen die Last.
6. Duftschale auf die rechte Dovetailschiene der Krone schieben. Nur trockene Duftsteine verwenden.

## Startprofil Anycubic Kobra 3 Max

- Düse: **0,6 mm**
- Schichthöhe: **0,30 mm**, organische Paneele optional 0,20–0,24 mm
- Linienbreite: **0,68 mm**
- Körper: PETG, 3 Wände; lokale Schienen/Verbinder 4 Wände
- Paneele: PETG oder PLA, 3 Wände; 10–15 % Gyroid genügt meist
- Gold: Silk-PLA als separater Farbkörper
- Duftschale: PETG oder Wood-PLA; keine offene Flamme, kein flüssiges Öl direkt einfüllen
- Stützen: Körper normalerweise ohne; Duftschalenrippen und Dovetaildach in der Vorschau kontrollieren

## Dateien

- `STL/body_*.stl`: funktionsfähige Module, organikbereit
- `STL/side_relief_*_slide_panel.stl`: flach druckbare ivory Paneele
- `STL/kintsugi_*_conformal.stl`: deckungsgleiche Goldkörper für Mehrfarbdruck
- `STL/kintsugi_*_flat_optional.stl`: optionale flache Klebevarianten
- `STL/crown_wave_flat_optional.stl` und `STL/front_applique_*_flat_optional.stl`: Ersatz-/Versuchsdekore
- `STL/scent_tray_hybrid.stl`: parametrischer Funktionskern plus organische Fassade
- `*_multicolor.3mf`: Paneel und Goldader als getrennte, registrierte Objektteile
- `ZEN_KINTSUGI_WAVE_5R_HYBRID_assembly.3mf`: komplette Baugruppe
- `raw_organic/*.glb`: unveränderte Quellen mit eingebetteten Texturen
- `relief_reference/*.stl`: unvereinfachte Referenz-Höhenhüllen vor Funktionsschnittstellen

## Wichtige Grenzen

Die eingebetteten GLB-Texturen sind visuelle Referenz und liegen unverändert im Rohordner. Normale FDM-3MF/STL-Dateien bilden Farbe nicht als Foto-Textur ab; Gold und Stein werden deshalb über getrennte Druckkörper/Filamente umgesetzt. Eine exakte Slicerzeit wurde nicht erfunden: Import, Schichtvorschau, kurze Segmente, Brücken und Materialverbrauch müssen im verwendeten Orca-/Anycubic-Slicer geprüft werden. Vor der Gesamtmontage sind Passcoupon und ein Mittelmodul als physischer Test empfohlen.
"""
    path.write_text(text, encoding="utf-8")


def build(raw_dir: Path, out_root: Path, p: Params) -> None:
    release = out_root / "release"
    stl_dir = release / "STL"
    raw_out = release / "raw_organic"
    source_out = release / "source"
    analysis_out = release / "analysis"
    reference_out = release / "relief_reference"
    for directory in (release, stl_dir, raw_out, source_out, analysis_out, reference_out):
        directory.mkdir(parents=True, exist_ok=True)

    expected = [
        "crown_wave.glb",
        "front_applique.glb",
        "kintsugi_inlay1.glb",
        "kintsugi_inlay2.glb",
        "scent_tray.glb",
        "side_wave_A.glb",
        "side_wave_B.glb",
    ]
    missing = [name for name in expected if not (raw_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing raw GLBs: {missing}")
    for name in expected:
        shutil.copy2(raw_dir / name, raw_out / name)

    sources = {name: load_source_mesh(raw_dir / name) for name in expected}
    source_manifest = {
        name: {
            "sha256": file_sha256(raw_dir / name),
            "bytes": (raw_dir / name).stat().st_size,
            "source_bounds": np.round(sources[name].bounds, 8).tolist(),
            "source_extents": np.round(sources[name].extents, 8).tolist(),
            "triangles": int(len(sources[name].faces)),
            "watertight": bool(sources[name].is_watertight),
            "has_uv": bool(getattr(sources[name].visual, "uv", None) is not None),
        }
        for name in expected
    }

    fields: dict[str, ReliefField] = {}
    fields["side_wave_A"] = rasterize_front_envelope(
        sources["side_wave_A.glb"], "side_wave_A", 111.0, 120.0, 0.55
    )
    fields["side_wave_B"] = rasterize_front_envelope(
        sources["side_wave_B.glb"], "side_wave_B", 111.0, 120.0, 0.55
    )
    panel_a_ref, panel_a_top = relief_mesh(fields["side_wave_A"], 1.80, 2.60)
    panel_b_ref, panel_b_top = relief_mesh(fields["side_wave_B"], 1.80, 2.60)
    panel_a = add_side_channels(panel_a_ref, fields["side_wave_A"])
    panel_b = add_side_channels(panel_b_ref, fields["side_wave_B"])

    gold_a, gold_a_flat, fields["kintsugi_inlay1"] = make_conformal_inlay(
        sources["kintsugi_inlay1.glb"],
        "kintsugi_inlay1",
        fields["side_wave_A"],
        panel_a_top,
        56.0,
        104.0,
        (-9.0, 0.0),
    )
    gold_b, gold_b_flat, fields["kintsugi_inlay2"] = make_conformal_inlay(
        sources["kintsugi_inlay2.glb"],
        "kintsugi_inlay2",
        fields["side_wave_B"],
        panel_b_top,
        56.0,
        104.0,
        (7.0, 0.0),
    )

    fields["front_applique"] = rasterize_front_envelope(
        sources["front_applique.glb"], "front_applique", 24.0, 112.0, 0.42
    )
    front_applique, _ = relief_mesh(fields["front_applique"], 1.20, 1.50)
    front_left = front_applique.copy()
    front_right = front_applique.copy()
    front_right.apply_scale([-1.0, 1.0, 1.0])
    front_right.faces = front_right.faces[:, ::-1]
    front_right = clean(front_right)

    fields["crown_wave"] = rasterize_front_envelope(
        sources["crown_wave.glb"], "crown_wave", 126.0, 74.0, 0.48
    )
    crown_wave_flat, _ = relief_mesh(fields["crown_wave"], 1.55, 2.45)

    fields["scent_tray"] = rasterize_front_envelope(
        sources["scent_tray.glb"], "scent_tray_fascia", 62.0, 68.0, 0.50
    )
    scent_fascia, _ = relief_mesh(fields["scent_tray"], 1.70, 2.20)

    output = add_side_slide_interface(p, make_clean_body(p, "output", "A"))
    middle_a_base = add_side_slide_interface(p, make_clean_body(p, "middle", "A"))
    middle_b_base = add_side_slide_interface(p, make_clean_body(p, "middle", "B"))
    applique_l = front_relief_to_module(front_applique, p, -60.0, mirror=False)
    applique_r = front_relief_to_module(front_applique, p, 60.0, mirror=True)
    middle_a = union_meshes([middle_a_base, applique_l, applique_r])
    middle_b = union_meshes([middle_b_base, applique_l, applique_r])

    crown_base = make_clean_body(p, "crown", "B")
    crown_wave_assembled = crown_relief_to_module(crown_wave_flat, p, fields["crown_wave"])
    crown = union_meshes([crown_base, crown_wave_assembled])
    scent_tray = make_hybrid_scent_tray(p, scent_fascia)

    panel_a_assembled = side_relief_to_module(panel_a, p)
    panel_b_assembled = side_relief_to_module(panel_b, p)
    gold_a_assembled = side_relief_to_module(gold_a, p)
    gold_b_assembled = side_relief_to_module(gold_b, p)

    pin = make_connector_pin(p)
    fit_coupon, fit_coupon_inlays = make_fit_coupon(p)
    rail_coupon_male, rail_coupon_female = make_slide_coupon()

    relief_references = {
        "side_wave_A_envelope_master.stl": panel_a_ref,
        "side_wave_B_envelope_master.stl": panel_b_ref,
        "kintsugi_inlay1_flat_master.stl": gold_a_flat,
        "kintsugi_inlay2_flat_master.stl": gold_b_flat,
        "front_applique_envelope_master.stl": front_applique,
        "crown_wave_envelope_master.stl": crown_wave_flat,
        "scent_tray_fascia_envelope_master.stl": scent_fascia,
    }
    for filename, mesh in relief_references.items():
        export_stl(mesh, reference_out / filename)

    manufacturing = {
        "body_output_organic_ready.stl": output,
        "body_middle_A_with_front_applique.stl": middle_a,
        "body_middle_B_with_front_applique.stl": middle_b,
        "body_crown_with_organic_wave.stl": crown,
        "side_relief_A_slide_panel.stl": panel_a,
        "side_relief_B_slide_panel.stl": panel_b,
        "kintsugi_inlay1_conformal_A.stl": gold_a,
        "kintsugi_inlay2_conformal_B.stl": gold_b,
        "kintsugi_inlay1_flat_optional.stl": gold_a_flat,
        "kintsugi_inlay2_flat_optional.stl": gold_b_flat,
        "front_applique_left_flat_optional.stl": front_left,
        "front_applique_right_flat_optional.stl": front_right,
        "crown_wave_flat_optional.stl": crown_wave_flat,
        "scent_tray_hybrid.stl": scent_tray,
        "connector_pin_4p8mm.stl": pin,
        "fit_coupon_body.stl": fit_coupon,
        "fit_coupon_gold_strips.stl": fit_coupon_inlays,
        "rail_coupon_male.stl": rail_coupon_male,
        "rail_coupon_female.stl": rail_coupon_female,
    }
    for filename, mesh in manufacturing.items():
        export_stl(mesh, stl_dir / filename)

    write_3mf(
        release / "SIDE_PANEL_A_multicolor.3mf",
        [("Reliefplatte_A", panel_a, 0), ("Goldader_1", gold_a, 1)],
        [(0, (0, 0, 0)), (1, (0, 0, 0))],
    )
    write_3mf(
        release / "SIDE_PANEL_B_multicolor.3mf",
        [("Reliefplatte_B", panel_b, 0), ("Goldader_2", gold_b, 1)],
        [(0, (0, 0, 0)), (1, (0, 0, 0))],
    )

    objects = [
        ("Ausgabe_OrganicReady", output, 0),
        ("Mittel_A_Organic", middle_a, 0),
        ("Mittel_B_Organic", middle_b, 0),
        ("Krone_Organic", crown, 0),
        ("Seitenrelief_A", panel_a_assembled, 0),
        ("Seitenrelief_B", panel_b_assembled, 0),
        ("Goldader_1", gold_a_assembled, 1),
        ("Goldader_2", gold_b_assembled, 1),
        ("Duftschale_Hybrid", scent_tray, 2),
        ("Verbinder", pin, 3),
    ]
    build_items: list[tuple[int, Sequence[float]]] = [(0, (0, 0, 0)), (4, (0, 0, 0)), (6, (0, 0, 0))]
    for index in range(1, p.roll_count):
        z = index * p.module_pitch
        if index % 2:
            build_items.extend([(1, (0, 0, z)), (5, (0, 0, z)), (7, (0, 0, z))])
        else:
            build_items.extend([(2, (0, 0, z)), (4, (0, 0, z)), (6, (0, 0, z))])
    crown_z = p.roll_count * p.module_pitch
    build_items.extend([(3, (0, 0, crown_z)), (8, (0, 0, crown_z + p.tray_assembly_z_offset))])
    connector_positions = [
        (-p.outer_half_width + p.side_thickness / 2.0, 8.0),
        (p.outer_half_width - p.side_thickness / 2.0, 8.0),
        (-p.outer_half_width + p.side_thickness / 2.0, p.front_y - 3.5),
        (p.outer_half_width - p.side_thickness / 2.0, p.front_y - 3.5),
    ]
    pin_height = 2 * p.connector_depth - 1.0
    for interface in range(1, p.roll_count + 1):
        z = interface * p.module_pitch - pin_height / 2.0
        for x, y in connector_positions:
            build_items.append((9, (x, y, z)))
    write_3mf(
        release / "ZEN_KINTSUGI_WAVE_5R_HYBRID_assembly.3mf", objects, build_items
    )

    output_full = clean(trimesh.util.concatenate([output, panel_a_assembled, gold_a_assembled]))
    middle_a_full = clean(trimesh.util.concatenate([middle_a, panel_b_assembled, gold_b_assembled]))
    middle_b_full = clean(trimesh.util.concatenate([middle_b, panel_a_assembled, gold_a_assembled]))
    fifo = collision_check(p, output_full, middle_a_full, middle_b_full, crown)
    interface = validate_interface_clearance(output, panel_a_assembled)

    reference_path_by_job = {
        "side_wave_A": "relief_reference/side_wave_A_envelope_master.stl",
        "side_wave_B": "relief_reference/side_wave_B_envelope_master.stl",
        "kintsugi_inlay1": "relief_reference/kintsugi_inlay1_flat_master.stl",
        "kintsugi_inlay2": "relief_reference/kintsugi_inlay2_flat_master.stl",
        "front_applique": "relief_reference/front_applique_envelope_master.stl",
        "crown_wave": "relief_reference/crown_wave_envelope_master.stl",
        "scent_tray": "relief_reference/scent_tray_fascia_envelope_master.stl",
    }
    manufacturing_path_by_job = {
        "side_wave_A": "STL/side_relief_A_slide_panel.stl",
        "side_wave_B": "STL/side_relief_B_slide_panel.stl",
        "kintsugi_inlay1": "STL/kintsugi_inlay1_conformal_A.stl",
        "kintsugi_inlay2": "STL/kintsugi_inlay2_conformal_B.stl",
        "front_applique": "STL/body_middle_A_with_front_applique.stl",
        "crown_wave": "STL/body_crown_with_organic_wave.stl",
        "scent_tray": "STL/scent_tray_hybrid.stl",
    }
    manufacturing_mesh_by_job = {
        "side_wave_A": panel_a,
        "side_wave_B": panel_b,
        "kintsugi_inlay1": gold_a,
        "kintsugi_inlay2": gold_b,
        "front_applique": middle_a,
        "crown_wave": crown,
        "scent_tray": scent_tray,
    }
    reference_mesh_by_job = {
        "side_wave_A": panel_a_ref,
        "side_wave_B": panel_b_ref,
        "kintsugi_inlay1": gold_a_flat,
        "kintsugi_inlay2": gold_b_flat,
        "front_applique": front_applique,
        "crown_wave": crown_wave_flat,
        "scent_tray": scent_fascia,
    }
    depth_by_job = {
        "side_wave_A": {"backer_mm": 1.80, "relief_mm": 2.60},
        "side_wave_B": {"backer_mm": 1.80, "relief_mm": 2.60},
        "kintsugi_inlay1": {"flat_mm": [0.62, 0.80], "conformal_mm": [0.55, 0.80]},
        "kintsugi_inlay2": {"flat_mm": [0.62, 0.80], "conformal_mm": [0.55, 0.80]},
        "front_applique": {"backer_mm": 1.20, "relief_mm": 1.50},
        "crown_wave": {"backer_mm": 1.55, "relief_mm": 2.45},
        "scent_tray": {"backer_mm": 1.70, "relief_mm": 2.20},
    }

    relief_report = {}
    for key, field in fields.items():
        natural_aspect = field.source_width / field.source_height
        placed_aspect = field.width_mm / field.height_mm
        estimated_relief_triangles = int(2 * np.count_nonzero(field.mask_cells))
        budget_gate = "PASS" if estimated_relief_triangles <= 1_000_000 else "REVIEW"
        relief_report[key] = {
            "source_class": "user-supplied image-to-3D GLB visible envelope",
            "source_physical_units": "untrusted normalized source coordinates",
            "source_authoring_ppi": "unknown / not applicable to supplied mesh",
            "mapping": "planar maximum-Z envelope with flat parametric back",
            "source_aspect": natural_aspect,
            "placed_width_mm": field.width_mm,
            "placed_height_mm": field.height_mm,
            "placed_aspect": placed_aspect,
            "aspect_error_percent": abs(placed_aspect / natural_aspect - 1.0) * 100.0,
            "pitch_x_mm": field.pitch_x_mm,
            "pitch_y_mm": field.pitch_y_mm,
            "ppi_x_equivalent": 25.4 / field.pitch_x_mm,
            "ppi_y_equivalent": 25.4 / field.pitch_y_mm,
            "physical_pixel_aspect": field.pitch_x_mm / field.pitch_y_mm,
            "raster_cells": [int(field.mask_cells.shape[1]), int(field.mask_cells.shape[0])],
            "active_cells": int(np.count_nonzero(field.mask_cells)),
            "uniform_scale_mm_per_source_unit": field.uniform_scale_mm_per_source_unit,
            "source_height_clip_1pct_99pct": [field.source_height_low, field.source_height_high],
            "removed_projected_components": field.removed_component_count,
            "aspect_policy": "preserve / contain",
            "intentional_xy_distortion": False,
            "height_precision": "float64 continuous local height; no grayscale posterization",
            "depth_plan": depth_by_job[key],
            "triangle_budget": {
                "estimated_top_triangles": estimated_relief_triangles,
                "per_part_limit": 1_000_000,
                "memory_budget_gib": 8,
                "max_mesh_mib": 100,
                "max_exact_slicer_seconds": 120,
                "gate": budget_gate,
            },
            "reference_master_mesh": reference_path_by_job[key],
            "reference_triangles": int(len(reference_mesh_by_job[key].faces)),
            "manufacturing_mesh": manufacturing_path_by_job[key],
            "manufacturing_triangles": int(len(manufacturing_mesh_by_job[key].faces)),
            "post_generation_simplification": "none; direct printer-pitch envelope generation",
            "simplification_metrics": "not applicable; no decimation candidate replaced the reference",
        }

    validation = {
        "version": VERSION,
        "parameters": asdict(p),
        "raw_sources": source_manifest,
        "relief_jobs": relief_report,
        "fifo": fifo,
        "side_slide_interface": interface,
        "manufacturing_files": {},
        "slicer_gate": {
            "status": "PENDING_USER_SLICER",
            "reason": "No Anycubic/Orca/Prusa slicer executable or exact user profile was available.",
            "required_checks": [
                "thin walls and short segments",
                "side-panel relief layer paths",
                "dovetail roof and rail continuity",
                "scent-tray bridges/supports",
                "estimated time and material",
            ],
        },
    }
    for filename in manufacturing:
        mesh = trimesh.load_mesh(stl_dir / filename, process=True)
        validation["manufacturing_files"][filename] = mesh_metrics(mesh)
    (release / "validation_report.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (analysis_out / "raw_source_manifest.json").write_text(
        json.dumps(source_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (analysis_out / "relief_registration_report.json").write_text(
        json.dumps(relief_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    candidate_rows = [
        {
            "candidate": "A_direct_raw_GLB",
            "method": "scale and Boolean raw image-to-3D meshes",
            "protected_fifo": "unknown",
            "watertight_inputs": "no",
            "print_orientation": "poor for large side reliefs",
            "status": "rejected",
            "reason": "5340-14044 boundary edges and 75-1103 face components per decorative source",
        },
        {
            "candidate": "B_global_voxel_remesh",
            "method": "voxelize every organic source",
            "protected_fifo": "yes if kept external",
            "watertight_inputs": "not required",
            "print_orientation": "mixed",
            "status": "rejected",
            "reason": "unnecessary global loss of wave openings, thin gold branches, and flat mating faces",
        },
        {
            "candidate": "C_selected_hybrid",
            "method": "visible-envelope relief + exact parametric interfaces",
            "protected_fifo": "yes",
            "watertight_inputs": "derived outputs verified",
            "print_orientation": "side panels flat; modules upright",
            "status": "selected",
            "reason": "preserves visible height locally and isolates every functional datum",
        },
    ]
    write_csv(release / "candidate_comparison.csv", candidate_rows)

    bom_rows = [
        {"part": "body_output_organic_ready", "qty": 1, "material": "PETG", "color": "stone/ivory"},
        {"part": "body_middle_A_with_front_applique", "qty": 2, "material": "PETG", "color": "stone/ivory"},
        {"part": "body_middle_B_with_front_applique", "qty": 2, "material": "PETG", "color": "stone/ivory"},
        {"part": "body_crown_with_organic_wave", "qty": 1, "material": "PETG", "color": "stone/ivory"},
        {"part": "side_relief_A_slide_panel", "qty": 3, "material": "PETG/PLA", "color": "stone/ivory"},
        {"part": "side_relief_B_slide_panel", "qty": 2, "material": "PETG/PLA", "color": "stone/ivory"},
        {"part": "kintsugi_inlay1_conformal_A", "qty": 3, "material": "Silk PLA", "color": "gold"},
        {"part": "kintsugi_inlay2_conformal_B", "qty": 2, "material": "Silk PLA", "color": "gold"},
        {"part": "connector_pin_4p8mm", "qty": 20, "material": "PETG", "color": "any"},
        {"part": "scent_tray_hybrid", "qty": 1, "material": "PETG/Wood PLA", "color": "wood/stone"},
    ]
    write_csv(release / "BOM.csv", bom_rows)

    path_assumptions = {
        "nozzle_mm": NOZZLE,
        "line_width_mm": LINE_WIDTH,
        "layer_height_mm": LAYER_HEIGHT,
        "side_panel_backer_mm": 1.8,
        "side_panel_relief_mm": 2.6,
        "front_applique_backer_mm": 1.2,
        "front_applique_relief_mm": 1.5,
        "crown_backer_mm": 1.55,
        "crown_relief_mm": 2.45,
        "gold_thickness_range_mm": [0.55, 0.80],
        "gold_overlap_into_panel_mm": 0.12,
        "protected_regions": [
            "roll shaft and output stop",
            "wall mounting holes/counterbores",
            "four module connector bores per interface",
            "right-side sliding rails and channel seam",
            "crown scent-tray dovetail",
            "flat print-bed backs of detachable panels",
        ],
        "support_strategy": {
            "body_modules": "upright; inspect front relief and crown in slicer",
            "side_panels": "flat back on bed; no supports intended",
            "scent_tray": "bowl opening upward; inspect ribs and dovetail roof",
        },
    }
    (release / "path_assumptions.json").write_text(
        json.dumps(path_assumptions, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    preview_meshes: list[tuple[trimesh.Trimesh, str]] = [
        (output, "stone"),
        (panel_a_assembled, "stone"),
        (gold_a_assembled, "gold"),
    ]
    for index in range(1, p.roll_count):
        z = index * p.module_pitch
        body = middle_a if index % 2 else middle_b
        panel = panel_b_assembled if index % 2 else panel_a_assembled
        gold = gold_b_assembled if index % 2 else gold_a_assembled
        preview_meshes.extend(
            [
                (transform_copy(body, [0, 0, z]), "stone"),
                (transform_copy(panel, [0, 0, z]), "stone"),
                (transform_copy(gold, [0, 0, z]), "gold"),
            ]
        )
    preview_meshes.extend(
        [
            (transform_copy(crown, [0, 0, crown_z]), "stone"),
            (transform_copy(scent_tray, [0, 0, crown_z + p.tray_assembly_z_offset]), "wood"),
        ]
    )
    nominal_roll = make_test_roll(p, p.roll_diameter, p.roll_width)
    rail_inner_x = 34.0 - 11.0 / 2.0
    rest_center = p.output_rail_height + math.sqrt((p.roll_diameter / 2.0) ** 2 - rail_inner_x**2)
    for index in range(p.roll_count):
        preview_meshes.append(
            (transform_copy(nominal_roll, [0, 0, rest_center + index * p.roll_diameter]), "roll")
        )
    render_preview(release / "preview_ZEN_KINTSUGI_WAVE_HYBRID.png", preview_meshes, p)

    write_readme(release / "README_DE.md", p, relief_report)
    shutil.copy2(Path(__file__), source_out / Path(__file__).name)
    base_source = Path(__file__).with_name("generate_zen_kintsugi.py")
    shutil.copy2(base_source, source_out / base_source.name)
    inspect_source = Path(__file__).with_name("inspect_organic_glbs.py")
    if inspect_source.exists():
        shutil.copy2(inspect_source, source_out / inspect_source.name)
    (source_out / "requirements.txt").write_text(
        "numpy>=2.0\nscipy>=1.12\ntrimesh>=5.0\nmanifold3d>=3.0\nshapely>=2.0\nmapbox_earcut>=2.0\nmatplotlib>=3.8\n",
        encoding="utf-8",
    )

    archive = out_root / f"{PRODUCT}_v{VERSION}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as handle:
        for file in sorted(release.rglob("*")):
            if file.is_file():
                handle.write(file, Path(f"{PRODUCT}_v{VERSION}") / file.relative_to(release))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    parameters = Params(
        roll_diameter=120.0,
        roll_width=105.0,
        roll_count=5,
        radial_clearance=4.0,
        module_pitch=124.0,
    )
    build(arguments.raw_dir, arguments.output, parameters)
