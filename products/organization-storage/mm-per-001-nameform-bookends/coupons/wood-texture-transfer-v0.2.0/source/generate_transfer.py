#!/usr/bin/env python3
"""Generate the direct-sampled wood transfer coupon and NameForm candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
from manifold3d import Error, Manifold, Mesh, OpType
from PIL import Image
import shapely
import shapely.affinity
from shapely.geometry import MultiPolygon, Polygon, box
import trimesh


HERE = Path(__file__).resolve().parent
JOB_ROOT = HERE.parent


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


REPO_ROOT = find_repo_root(HERE)
NAMEFORM_SOURCE = (
    REPO_ROOT
    / "products/organization-storage/mm-per-001-nameform-bookends/source/v0.3.0"
)
sys.path.insert(0, str(NAMEFORM_SOURCE))
import nameform_bookends as nb  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_once(path: Path, payload: dict) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_png_once(path: Path, values: np.ndarray) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.round(np.clip(values, 0.0, 1.0) * 65535.0).astype(np.uint16)).save(path)


def write_binary_stl_once(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    triangles = vertices[faces]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    normals[lengths > 0] /= lengths[lengths > 0, None]
    record_dtype = np.dtype(
        [("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]
    )
    records = np.zeros(len(faces), dtype=record_dtype)
    records["normal"] = normals.astype(np.float32)
    records["vertices"] = triangles.astype(np.float32)
    header = b"MM-PER-001 direct wood transfer v0.2.0 DRAFT"[:80].ljust(80, b" ")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(faces)))
        handle.write(records.tobytes())


def smoothstep01(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def periodic_edge_blend(values: np.ndarray, blend_px: int) -> np.ndarray:
    if blend_px <= 0:
        return values.copy()
    out = values.copy()
    height, width = values.shape
    bx = min(blend_px, width // 4)
    by = min(blend_px, height // 4)
    seam_x = 0.5 * (values[:, 0] + values[:, -1])
    seam_y = 0.5 * (values[0, :] + values[-1, :])
    for column in range(bx):
        alpha = (column + 1) / (bx + 1)
        out[:, column] = values[:, column] * alpha + seam_x * (1.0 - alpha)
        out[:, width - 1 - column] = (
            values[:, width - 1 - column] * alpha + seam_x * (1.0 - alpha)
        )
    for row in range(by):
        alpha = (row + 1) / (by + 1)
        out[row, :] = out[row, :] * alpha + seam_y * (1.0 - alpha)
        out[height - 1 - row, :] = (
            out[height - 1 - row, :] * alpha + seam_y * (1.0 - alpha)
        )
    return out


class PeriodicSampler:
    def __init__(self, values: np.ndarray) -> None:
        if values.ndim != 2:
            raise ValueError("heightmap must be two-dimensional")
        self.values = np.asarray(values, dtype=np.float32)
        self.height, self.width = self.values.shape

    def sample(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        x = np.mod(u, 1.0) * self.width
        y = np.mod(v, 1.0) * self.height
        x0 = np.floor(x).astype(np.int64) % self.width
        y0 = np.floor(y).astype(np.int64) % self.height
        x1 = (x0 + 1) % self.width
        y1 = (y0 + 1) % self.height
        fx = (x - np.floor(x)).astype(np.float32)
        fy = (y - np.floor(y)).astype(np.float32)
        lower = self.values[y0, x0] * (1.0 - fx) + self.values[y0, x1] * fx
        upper = self.values[y1, x0] * (1.0 - fx) + self.values[y1, x1] * fx
        return lower * (1.0 - fy) + upper * fy


def glyph_rectangles(width: float, height: float, stroke: float) -> list[tuple[float, float, float, float]]:
    x0, x1 = -width / 2.0, width / 2.0
    z0, z1 = -height / 2.0, height / 2.0
    return [
        (x0, z0, x0 + stroke, z1),
        (x0, z0, x1, z0 + stroke),
        (x0, -stroke / 2.0, x1, stroke / 2.0),
        (x0, z1 - stroke, x1, z1),
    ]


def distance_to_rectangles(
    x: np.ndarray, z: np.ndarray, rectangles: list[tuple[float, float, float, float]]
) -> np.ndarray:
    distance = np.full_like(x, np.inf, dtype=np.float64)
    for x0, z0, x1, z1 in rectangles:
        dx = np.maximum.reduce((x0 - x, np.zeros_like(x), x - x1))
        dz = np.maximum.reduce((z0 - z, np.zeros_like(z), z - z1))
        distance = np.minimum(distance, np.hypot(dx, dz))
    return distance


def boundary_indices(rows: int, columns: int) -> list[int]:
    bottom = [column for column in range(columns)]
    right = [row * columns + columns - 1 for row in range(1, rows)]
    top = [(rows - 1) * columns + column for column in range(columns - 2, -1, -1)]
    left = [row * columns for row in range(rows - 2, 0, -1)]
    return bottom + right + top + left


def candidate_coordinates(
    candidate: dict, local_x: np.ndarray, z: np.ndarray, panel_height: float
) -> tuple[np.ndarray, np.ndarray]:
    period_x, period_y = map(float, candidate["period_x_y_mm"])
    if candidate["id"] == "A":
        return (panel_height - z) / period_x, local_x / period_y
    return local_x / period_x, (panel_height - z) / period_y


def make_coupon_panel(
    sampler: PeriodicSampler, spec: dict, candidate: dict, x_start: float
) -> tuple[Manifold, dict]:
    coupon = spec["coupon"]
    glyph = coupon["glyph"]
    width = float(coupon["panel_width_mm"])
    height = float(coupon["panel_height_mm"])
    thickness = float(coupon["panel_thickness_mm"])
    pitch = float(coupon["mesh_pitch_mm"])
    depth = float(candidate["depth_mm"])
    nx, nz = math.ceil(width / pitch), math.ceil(height / pitch)
    xs = np.linspace(x_start, x_start + width, nx + 1)
    zs = np.linspace(0.0, height, nz + 1)
    xx, zz = np.meshgrid(xs, zs, indexing="xy")
    local_x = xx - x_start
    u, v = candidate_coordinates(candidate, local_x, zz, height)
    sampled = sampler.sample(u, v)
    edge_distance = np.minimum.reduce((local_x, width - local_x, zz, height - zz))
    edge_mask = smoothstep01(edge_distance / float(coupon["edge_taper_mm"]))
    centered = glyph_rectangles(
        float(glyph["width_mm"]), float(glyph["height_mm"]), float(glyph["stroke_mm"])
    )
    rectangles = [
        (
            rectangle[0] + width / 2.0,
            rectangle[1] + height / 2.0,
            rectangle[2] + width / 2.0,
            rectangle[3] + height / 2.0,
        )
        for rectangle in centered
    ]
    glyph_distance = distance_to_rectangles(local_x, zz, rectangles)
    mask = edge_mask * smoothstep01(glyph_distance / float(glyph["texture_keepout_mm"]))
    relief = depth * sampled * mask

    front = np.dstack((xx, relief, zz)).reshape(-1, 3)
    vertices: list[list[float]] = front.tolist()
    faces: list[tuple[int, int, int]] = []
    columns, rows = nx + 1, nz + 1
    for row in range(nz):
        for column in range(nx):
            a = row * columns + column
            b, c, d = a + 1, a + columns, a + columns + 1
            faces.extend(((a, b, d), (a, d, c)))
    boundary = boundary_indices(rows, columns)
    back_boundary: list[int] = []
    for front_index in boundary:
        x, _y, z = vertices[front_index]
        back_boundary.append(len(vertices))
        vertices.append([x, thickness, z])
    for index in range(len(boundary)):
        nxt = (index + 1) % len(boundary)
        f0, f1 = boundary[index], boundary[nxt]
        b0, b1 = back_boundary[index], back_boundary[nxt]
        faces.extend(((f0, b1, f1), (f0, b0, b1)))
    back_center = len(vertices)
    vertices.append([x_start + width / 2.0, thickness, height / 2.0])
    for index in range(len(boundary)):
        nxt = (index + 1) % len(boundary)
        faces.append((back_center, back_boundary[nxt], back_boundary[index]))
    panel = Manifold(
        mesh=Mesh(
            vert_properties=np.ascontiguousarray(vertices, dtype=np.float32),
            tri_verts=np.ascontiguousarray(faces, dtype=np.uint32),
        )
    )
    if panel.status() != Error.NoError or panel.is_empty():
        raise RuntimeError(f"panel {candidate['id']} rejected by Manifold: {panel.status()}")
    active = relief[mask > 0.95]
    return panel, {
        "id": candidate["id"],
        "role": candidate["role"],
        "master": candidate["master"],
        "period_x_y_mm": candidate["period_x_y_mm"],
        "depth_mm": depth,
        "grid_cells_x_z": [nx, nz],
        "actual_grid_pitch_x_z_mm": [width / nx, height / nz],
        "pre_union_triangles": int(panel.num_tri()),
        "sample_min_max": [float(sampled.min()), float(sampled.max())],
        "relief_min_max_mm": [float(relief.min()), float(relief.max())],
        "active_relief_p05_p95_mm": [float(np.percentile(active, 5)), float(np.percentile(active, 95))],
        "active_relief_robust_span_mm": float(np.percentile(active, 95) - np.percentile(active, 5)),
        "minimum_residual_wall_mm": float(thickness - relief.max()),
        "texture_at_boundary_max_mm": float(
            max(relief[0, :].max(), relief[-1, :].max(), relief[:, 0].max(), relief[:, -1].max())
        ),
        "texture_in_glyph_footprint_max_mm": float(relief[glyph_distance == 0.0].max()),
    }


def add_coupon_glyphs(parts: list[Manifold], spec: dict, x_start: float) -> None:
    coupon, glyph = spec["coupon"], spec["coupon"]["glyph"]
    width, height = float(coupon["panel_width_mm"]), float(coupon["panel_height_mm"])
    for x0, z0, x1, z1 in glyph_rectangles(
        float(glyph["width_mm"]), float(glyph["height_mm"]), float(glyph["stroke_mm"])
    ):
        solid = Manifold.cube(
            [x1 - x0, float(glyph["raise_mm"]) + float(glyph["boolean_overlap_mm"]), z1 - z0]
        ).translate(
            [
                x_start + width / 2.0 + x0,
                -float(glyph["raise_mm"]),
                height / 2.0 + z0,
            ]
        )
        parts.append(solid)


def manifold_to_arrays(manifold: Manifold) -> tuple[np.ndarray, np.ndarray]:
    output = manifold.to_mesh()
    return (
        np.asarray(output.vert_properties, dtype=np.float64)[:, :3],
        np.asarray(output.tri_verts, dtype=np.int64),
    )


def remove_degenerate_triangles(
    vertices: np.ndarray, faces: np.ndarray
) -> tuple[np.ndarray, np.ndarray, int]:
    """Weld sub-micron Boolean residues, drop collapsed faces, and compact."""
    clean = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    original_faces = len(clean.faces)
    # Manifold/CadQuery can leave a few sub-micron sliver triangles at text
    # junctions.  Four decimal places is a 0.0001 mm weld: far below both the
    # 0.45 mm geometry pitch and STL/FDM process resolution.
    clean.merge_vertices(digits_vertex=4)
    clean.update_faces(clean.nondegenerate_faces(height=1.0e-8))
    clean.remove_unreferenced_vertices()
    removed = int(original_faces - len(clean.faces))
    return (
        np.ascontiguousarray(clean.vertices, dtype=np.float64),
        np.ascontiguousarray(clean.faces, dtype=np.int64),
        removed,
    )


def validate_mesh(vertices: np.ndarray, faces: np.ndarray) -> tuple[trimesh.Trimesh, dict]:
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    components = mesh.split(only_watertight=False)
    return mesh, {
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "body_count": len(components),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "bounds_min_mm": mesh.bounds[0].tolist(),
        "bounds_max_mm": mesh.bounds[1].tolist(),
        "extents_mm": mesh.extents.tolist(),
    }


def build_coupon(spec: dict, samplers: dict[str, PeriodicSampler], output_root: Path) -> tuple[Path, dict]:
    coupon = spec["coupon"]
    candidates = coupon["candidates"]
    width = float(coupon["panel_width_mm"])
    gap = float(coupon["panel_gap_mm"])
    margin = 2.0
    total_width = 2.0 * margin + len(candidates) * width + (len(candidates) - 1) * gap
    parts: list[Manifold] = []
    panel_reports = []
    for index, candidate in enumerate(candidates):
        x_start = margin + index * (width + gap)
        panel, report = make_coupon_panel(samplers[candidate["master"]], spec, candidate, x_start)
        parts.append(panel)
        add_coupon_glyphs(parts, spec, x_start)
        panel_reports.append(report)
    parts.append(
        Manifold.cube([total_width, float(coupon["base_depth_mm"]), float(coupon["base_thickness_mm"])])
    )
    result = Manifold.batch_boolean(parts, OpType.Add)
    if result.status() != Error.NoError or result.is_empty():
        raise RuntimeError(f"coupon Boolean failed: {result.status()}")
    vertices, faces = manifold_to_arrays(result)
    vertices, faces, removed_degenerate = remove_degenerate_triangles(vertices, faces)
    path = output_root / "exports/DRAFT-nameform-wood-direct-transfer-coupon-v0.2.0.stl"
    write_binary_stl_once(path, vertices, faces)
    mesh, metrics = validate_mesh(vertices, faces)
    expected = [total_width, float(coupon["base_depth_mm"]) + 2.0, float(coupon["panel_height_mm"])]
    checks = {
        "watertight": bool(mesh.is_watertight),
        "winding": bool(mesh.is_winding_consistent),
        "single_body": bool(metrics["body_count"] == 1),
        "positive_volume": bool(mesh.volume > 0),
        "bounds": bool(np.allclose(mesh.extents, expected, atol=1.0e-5)),
        "triangle_budget": bool(len(faces) <= int(spec["budgets"]["max_coupon_triangles"])),
        "protected_boundaries": bool(all(
            panel["texture_at_boundary_max_mm"] <= 1.0e-8
            and panel["texture_in_glyph_footprint_max_mm"] <= 1.0e-8
            for panel in panel_reports
        )),
        "wall_reserve": bool(min(panel["minimum_residual_wall_mm"] for panel in panel_reports) >= 2.2),
    }
    metrics["removed_degenerate_faces"] = removed_degenerate
    return path, {"metrics": metrics, "panels": panel_reports, "checks": checks}


def nameform_text_geometry(text: str, plan: nb.PairText, center_x: float) -> Polygon | MultiPolygon:
    geometry = nb._polygonal_text(text)
    raw = nb.text_bounds(text)
    centered = shapely.affinity.translate(geometry, xoff=-(raw[0] + raw[2]) / 2.0)
    scaled = shapely.affinity.scale(centered, xfact=plan.scale, yfact=plan.scale, origin=(0.0, 0.0))
    return shapely.affinity.translate(scaled, xoff=center_x, yoff=plan.baseline_z)


def make_nameform_cutter(
    side: str, text: str, plan: nb.PairText, sampler: PeriodicSampler, spec: dict
) -> tuple[Manifold, dict]:
    transfer = spec["nameform_candidate"]
    depth = float(transfer["depth_mm"])
    pitch = float(transfer["mesh_pitch_mm"])
    if side == "left":
        x0, x1, center_x = -nb.WING_W, 0.0, -nb.WING_W / 2.0
    else:
        x0, x1, center_x = 0.0, nb.WING_W, nb.WING_W / 2.0
    nx, nz = math.ceil((x1 - x0) / pitch), math.ceil(nb.WING_H / pitch)
    xs = np.linspace(x0, x1, nx + 1)
    zs = np.linspace(0.0, nb.WING_H, nz + 1)
    xx, zz = np.meshgrid(xs, zs, indexing="xy")
    sample = sampler.sample(xx / 120.0, (nb.WING_H - zz) / 45.0)

    wing = box(x0, 0.0, x1, nb.WING_H).buffer(-nb.WING_CORNER_R).buffer(nb.WING_CORNER_R)
    points = shapely.points(xx.ravel(), zz.ravel())
    inside = shapely.contains(wing, points).reshape(xx.shape)
    edge_distance = shapely.distance(points, wing.boundary).reshape(xx.shape)
    edge_mask = smoothstep01(edge_distance / float(transfer["wing_edge_taper_mm"])) * inside
    text_geometry = nameform_text_geometry(text, plan, center_x).buffer(float(transfer["text_keepout_mm"]))
    text_distance = shapely.distance(points, text_geometry).reshape(xx.shape)
    text_mask = smoothstep01(text_distance / float(transfer["text_keepout_mm"]))
    mask = edge_mask * text_mask
    relief = depth * sample * mask
    top_y = -0.01 + relief
    bottom_y = -0.05

    top = np.dstack((xx, top_y, zz)).reshape(-1, 3)
    bottom = np.dstack((xx, np.full_like(xx, bottom_y), zz)).reshape(-1, 3)
    vertices = np.vstack((top, bottom))
    faces: list[tuple[int, int, int]] = []
    columns, rows = nx + 1, nz + 1
    offset = len(top)
    for row in range(nz):
        for column in range(nx):
            a = row * columns + column
            b, c, d = a + 1, a + columns, a + columns + 1
            faces.extend(((a, d, b), (a, c, d)))
            a2, b2, c2, d2 = a + offset, b + offset, c + offset, d + offset
            faces.extend(((a2, b2, d2), (a2, d2, c2)))
    boundary = boundary_indices(rows, columns)
    for index in range(len(boundary)):
        nxt = (index + 1) % len(boundary)
        f0, f1 = boundary[index], boundary[nxt]
        b0, b1 = f0 + offset, f1 + offset
        faces.extend(((f0, f1, b1), (f0, b1, b0)))
    cutter = Manifold(
        mesh=Mesh(
            vert_properties=np.ascontiguousarray(vertices, dtype=np.float32),
            tri_verts=np.ascontiguousarray(faces, dtype=np.uint32),
        )
    )
    if cutter.status() != Error.NoError or cutter.is_empty():
        raise RuntimeError(f"{side} cutter rejected by Manifold: {cutter.status()}")
    active = relief[mask > 0.95]
    return cutter, {
        "side": side,
        "grid_cells_x_z": [nx, nz],
        "cutter_triangles": int(cutter.num_tri()),
        "sample_min_max": [float(sample.min()), float(sample.max())],
        "relief_min_max_mm": [float(relief.min()), float(relief.max())],
        "active_relief_robust_span_mm": float(np.percentile(active, 95) - np.percentile(active, 5)),
        "edge_mask_max": float(edge_mask.max()),
        "text_mask_min": float(text_mask.min()),
    }


def load_manifold(path: Path) -> tuple[Manifold, trimesh.Trimesh]:
    loaded = trimesh.load_mesh(path, process=True)
    if not isinstance(loaded, trimesh.Trimesh):
        raise RuntimeError(f"expected one mesh: {path}")
    manifold = Manifold(
        mesh=Mesh(
            vert_properties=np.ascontiguousarray(loaded.vertices, dtype=np.float32),
            tri_verts=np.ascontiguousarray(loaded.faces, dtype=np.uint32),
        )
    )
    if manifold.status() != Error.NoError or manifold.is_empty():
        raise RuntimeError(f"base mesh rejected by Manifold: {path}: {manifold.status()}")
    return manifold, loaded


def cadquery_shape_to_manifold(shape: object) -> Manifold:
    """Tessellate a CadQuery shape without creating an intermediate file."""
    cq_vertices, cq_faces = shape.tessellate(nb.MESH_TOLERANCE, nb.MESH_ANGULAR_TOLERANCE)
    vertices = np.asarray(
        [[vertex.x, vertex.y, vertex.z] for vertex in cq_vertices], dtype=np.float32
    )
    faces = np.asarray(cq_faces, dtype=np.uint32)
    welded = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    result = Manifold(
        mesh=Mesh(
            vert_properties=np.ascontiguousarray(welded.vertices, dtype=np.float32),
            tri_verts=np.ascontiguousarray(welded.faces, dtype=np.uint32),
        )
    )
    if result.status() != Error.NoError or result.is_empty():
        raise RuntimeError(f"CadQuery text mesh rejected by Manifold: {result.status()}")
    return result


def build_nameform_pair(
    spec: dict, sampler: PeriodicSampler, output_root: Path
) -> tuple[list[Path], list[dict]]:
    transfer = spec["nameform_candidate"]
    plan = nb.pair_text()
    outputs, reports = [], []
    for side, text in (("left", plan.left), ("right", plan.right)):
        source = REPO_ROOT / transfer[f"source_{side}"]
        base, base_mesh = load_manifold(source)
        cutter, cutter_report = make_nameform_cutter(side, text, plan, sampler, spec)
        # The source STL already contains text with a 0.1 mm bond overlap.  A
        # closed subtractive height-field must extend slightly in front of y=0
        # and would otherwise slice through that overlap even where its height
        # mask is zero.  Re-union the exact original CadQuery text solid after
        # engraving; this restores the full glyph and its bond while the
        # buffered texture keep-out leaves the underlying wing flat.
        center_x = -nb.WING_W / 2.0 if side == "left" else nb.WING_W / 2.0
        letters = cadquery_shape_to_manifold(
            nb.text_solid(text, plan.scale, center_x, plan.baseline_z)
        )
        result = (base - cutter) + letters
        if result.status() != Error.NoError or result.is_empty():
            raise RuntimeError(f"{side} texture Boolean failed: {result.status()}")
        vertices, faces = manifold_to_arrays(result)
        vertices, faces, removed_degenerate = remove_degenerate_triangles(vertices, faces)
        path = (
            output_root
            / "exports/nameform"
            / f"DRAFT-nameform-STE-FAN-{side}-wood-direct-v0.3.0-tx0.2.0.stl"
        )
        write_binary_stl_once(path, vertices, faces)
        mesh, metrics = validate_mesh(vertices, faces)
        metrics["removed_degenerate_faces"] = removed_degenerate
        checks = {
            "watertight": bool(mesh.is_watertight),
            "winding": bool(mesh.is_winding_consistent),
            "single_body": bool(metrics["body_count"] == 1),
            "positive_volume": bool(mesh.volume > 0),
            "bed_datum": bool(abs(float(mesh.bounds[0, 2])) <= 1.0e-6),
            "envelope_preserved": bool(np.allclose(mesh.bounds, base_mesh.bounds, atol=1.0e-5)),
            "volume_reduced": bool(0.0 < mesh.volume < base_mesh.volume),
            "triangle_budget": bool(len(faces) <= int(spec["budgets"]["max_nameform_triangles_each"])),
        }
        outputs.append(path)
        reports.append(
            {
                "side": side,
                "text": text,
                "source": str(source),
                "source_sha256": sha256(source),
                "output": str(path),
                "output_sha256": sha256(path),
                "source_volume_mm3": float(base_mesh.volume),
                "engraved_volume_mm3": float(mesh.volume),
                "removed_volume_mm3": float(base_mesh.volume - mesh.volume),
                "metrics": metrics,
                "cutter": cutter_report,
                "checks": checks,
            }
        )
    return outputs, reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=JOB_ROOT / "transfer-spec.json")
    parser.add_argument("--output-root", type=Path, default=JOB_ROOT)
    args = parser.parse_args()
    spec_path = args.spec.resolve()
    output_root = args.output_root.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    master_path = REPO_ROOT / spec["source"]["master"]
    registration_path = REPO_ROOT / spec["source"]["registration"]
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    if sha256(master_path) != registration["master_sha256"]:
        raise ValueError("wood master hash does not match its registration")
    raw_u16 = np.asarray(Image.open(master_path))
    if raw_u16.dtype != np.uint16 or raw_u16.ndim != 2:
        raise ValueError("wood master must be 16-bit grayscale")
    raw = raw_u16.astype(np.float32) / 65535.0
    blend_px = int(spec["source"]["periodic_edge_blend_px"])
    blended = periodic_edge_blend(raw, blend_px)
    blended_path = output_root / "build/wood-001-tile-16bit-blend24.png"
    write_png_once(blended_path, blended)
    samplers = {"raw": PeriodicSampler(raw), "blend24": PeriodicSampler(blended)}

    coupon_path, coupon_report = build_coupon(spec, samplers, output_root)
    nameform_paths, nameform_reports = build_nameform_pair(spec, samplers["blend24"], output_root)
    checks = {
        "coupon": all(coupon_report["checks"].values()),
        "nameform": all(all(report["checks"].values()) for report in nameform_reports),
        "direct_master_resolution": raw.shape == (1254, 1254),
        "no_build_raster_downsampling": True,
    }
    report = {
        "schema_version": "1.0",
        "tool": "MM-PER-001 direct wood transfer generator",
        "tool_version": "0.2.0",
        "profile": "draft",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": [
            {"path": str(spec_path), "sha256": sha256(spec_path)},
            {"path": str(Path(__file__).resolve()), "sha256": sha256(Path(__file__).resolve())},
            {"path": str(master_path), "sha256": sha256(master_path)},
            {"path": str(registration_path), "sha256": sha256(registration_path)},
        ],
        "artifacts": [
            {"path": str(blended_path), "sha256": sha256(blended_path), "size_bytes": blended_path.stat().st_size},
            {"path": str(coupon_path), "sha256": sha256(coupon_path), "size_bytes": coupon_path.stat().st_size},
            *[
                {"path": str(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}
                for path in nameform_paths
            ],
        ],
        "checks": checks,
        "metrics": {
            "master_pixels": [int(raw.shape[1]), int(raw.shape[0])],
            "periodic_blend_px": blend_px,
            "coupon": coupon_report,
            "nameform": nameform_reports,
        },
        "limitations": [
            "The failed v0.1 physical print establishes failure but no measured relief amplitude or photos were supplied.",
            "The integrated NameForm pair uses candidate C before physical qualification; it remains DRAFT.",
            "Exact filament identity and conditioning remain unknown.",
            "No printer upload or print start is performed.",
        ],
    }
    report_path = output_root / "reports/generation-report.json"
    write_json_once(report_path, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "coupon": str(coupon_path),
                "nameform": [str(path) for path in nameform_paths],
                "coupon_triangles": coupon_report["metrics"]["triangles"],
                "nameform_triangles": [item["metrics"]["triangles"] for item in nameform_reports],
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
