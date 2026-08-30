#!/usr/bin/env python3
"""Build the upright NameForm wood-texture mesh-pitch comparison coupon.

The immutable wood-001 source master stays in the shared texture library.  This
script creates one printer-specific 16-bit build raster per candidate, maps the
same physical source patch to three vertical 3.2 mm panels, masks a raised test
glyph, and joins the panels through one bed-contact foot.  Generated paths are
write-once: use a new --output-root for every additional run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Iterable

import numpy as np
from manifold3d import Error, Manifold, Mesh, OpType
from PIL import Image
import trimesh


HERE = Path(__file__).resolve().parent
COUPON_DIR = HERE.parent


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


REPO_ROOT = find_repo_root(HERE)


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


def smoothstep01(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def candidate_slug(pitch: float) -> str:
    return f"{pitch:.2f}".replace(".", "p")


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


def build_heightmap(
    master: Image.Image,
    output_path: Path,
    pitch: float,
    u_period: float,
    v_period: float,
) -> tuple[PeriodicSampler, dict]:
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {output_path}")
    pixels_u = max(2, math.ceil(u_period / pitch))
    pixels_v = max(2, math.ceil(v_period / pitch))
    resized = master.resize((pixels_u, pixels_v), Image.Resampling.LANCZOS)
    values_u16 = np.asarray(resized, dtype=np.uint16)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(values_u16).save(output_path)
    actual_pitch_u = u_period / pixels_u
    actual_pitch_v = v_period / pixels_v
    metadata = {
        "path": str(output_path),
        "sha256": sha256(output_path),
        "bit_depth": 16,
        "continuous_tone": True,
        "pixels_u_v": [pixels_u, pixels_v],
        "physical_period_u_v_mm": [u_period, v_period],
        "actual_pixel_pitch_u_v_mm": [actual_pitch_u, actual_pitch_v],
        "surface_build_ppi_u_v": [25.4 / actual_pitch_u, 25.4 / actual_pitch_v],
        "resampling": "Lanczos from immutable wood-001 master",
    }
    return PeriodicSampler(values_u16.astype(np.float32) / 65535.0), metadata


def glyph_rectangles(width: float, height: float, stroke: float) -> list[tuple[float, float, float, float]]:
    """Return a centered rectilinear E as local (x0, z0, x1, z1) rectangles."""
    x0 = -width / 2.0
    x1 = width / 2.0
    z0 = -height / 2.0
    z1 = height / 2.0
    middle_z0 = -stroke / 2.0
    middle_z1 = stroke / 2.0
    return [
        (x0, z0, x0 + stroke, z1),
        (x0, z0, x1, z0 + stroke),
        (x0, middle_z0, x1, middle_z1),
        (x0, z1 - stroke, x1, z1),
    ]


def distance_to_rectangles(
    x: np.ndarray,
    z: np.ndarray,
    rectangles: Iterable[tuple[float, float, float, float]],
) -> np.ndarray:
    distance = np.full_like(x, np.inf, dtype=np.float64)
    for x0, z0, x1, z1 in rectangles:
        dx = np.maximum.reduce((x0 - x, np.zeros_like(x), x - x1))
        dz = np.maximum.reduce((z0 - z, np.zeros_like(z), z - z1))
        distance = np.minimum(distance, np.hypot(dx, dz))
    return distance


def boundary_indices(rows: int, columns: int) -> list[int]:
    """CCW boundary in physical X/Z coordinates for a row-major front grid."""
    bottom = [column for column in range(columns)]
    right = [row * columns + columns - 1 for row in range(1, rows)]
    top = [(rows - 1) * columns + column for column in range(columns - 2, -1, -1)]
    left = [row * columns for row in range(rows - 2, 0, -1)]
    return bottom + right + top + left


def make_panel(
    sampler: PeriodicSampler,
    spec: dict,
    x_start: float,
    pitch: float,
) -> tuple[Manifold, dict]:
    geometry = spec["geometry"]
    relief_spec = spec["relief"]
    mapping = spec["mapping"]
    glyph = geometry["glyph"]
    width = float(geometry["panel_width_mm"])
    height = float(geometry["panel_height_mm"])
    thickness = float(geometry["panel_thickness_mm"])
    depth = float(relief_spec["depth_mm"])
    edge_taper_mm = float(relief_spec["edge_taper_mm"])

    nx = max(2, math.ceil(width / pitch))
    nz = max(2, math.ceil(height / pitch))
    xs = np.linspace(x_start, x_start + width, nx + 1)
    zs = np.linspace(0.0, height, nz + 1)
    xx, zz = np.meshgrid(xs, zs, indexing="xy")
    local_x = xx - x_start

    u = float(mapping["u_phase"]) + (height - zz) / float(mapping["u_period_mm"])
    v = float(mapping["v_phase"]) + local_x / float(mapping["v_period_mm"])
    sampled = sampler.sample(u, v)

    edge_distance = np.minimum.reduce((local_x, width - local_x, zz, height - zz))
    edge_mask = smoothstep01(edge_distance / edge_taper_mm)
    centered_rectangles = glyph_rectangles(
        float(glyph["width_mm"]), float(glyph["height_mm"]), float(glyph["stroke_mm"])
    )
    glyph_center_x = width / 2.0
    glyph_center_z = height / 2.0
    local_rectangles = [
        (
            rect[0] + glyph_center_x,
            rect[1] + glyph_center_z,
            rect[2] + glyph_center_x,
            rect[3] + glyph_center_z,
        )
        for rect in centered_rectangles
    ]
    glyph_distance = distance_to_rectangles(local_x, zz, local_rectangles)
    glyph_mask = smoothstep01(glyph_distance / float(glyph["texture_keepout_mm"]))
    mask = edge_mask * glyph_mask
    front_y = depth * sampled * mask

    front = np.dstack((xx, front_y, zz)).reshape(-1, 3)
    vertices: list[list[float]] = front.tolist()
    faces: list[tuple[int, int, int]] = []
    columns = nx + 1
    rows = nz + 1
    for row in range(nz):
        for column in range(nx):
            a = row * columns + column
            b = a + 1
            c = a + columns
            d = c + 1
            faces.append((a, b, d))
            faces.append((a, d, c))

    boundary = boundary_indices(rows, columns)
    back_boundary: list[int] = []
    for front_index in boundary:
        x, _y, z = vertices[front_index]
        back_boundary.append(len(vertices))
        vertices.append([x, thickness, z])

    count = len(boundary)
    for index in range(count):
        nxt = (index + 1) % count
        f0, f1 = boundary[index], boundary[nxt]
        b0, b1 = back_boundary[index], back_boundary[nxt]
        faces.extend(((f0, b1, f1), (f0, b0, b1)))

    back_center = len(vertices)
    vertices.append([x_start + width / 2.0, thickness, height / 2.0])
    for index in range(count):
        nxt = (index + 1) % count
        # The X/Z boundary is counter-clockwise when seen from -Y. Reverse it
        # for the rear cap so its normal points +Y and every shared edge has
        # opposite direction on its two incident faces.
        faces.append((back_center, back_boundary[nxt], back_boundary[index]))

    mesh = Mesh(
        vert_properties=np.ascontiguousarray(vertices, dtype=np.float32),
        tri_verts=np.ascontiguousarray(faces, dtype=np.uint32),
    )
    panel = Manifold(mesh=mesh)
    if panel.status() != Error.NoError or panel.is_empty():
        raise RuntimeError(f"panel mesh rejected by Manifold: {panel.status()}")

    mask_cells = mask[:-1, :-1] > 1.0e-6
    report = {
        "requested_pitch_mm": pitch,
        "actual_grid_pitch_x_z_mm": [width / nx, height / nz],
        "grid_cells_x_z": [nx, nz],
        "front_grid_vertices": int((nx + 1) * (nz + 1)),
        "pre_union_triangles": int(panel.num_tri()),
        "relief_min_max_mm": [float(front_y.min()), float(front_y.max())],
        "masked_displaced_area_estimate_mm2": float(mask_cells.sum() * (width / nx) * (height / nz)),
        "minimum_residual_wall_mm": float(thickness - front_y.max()),
        "texture_at_boundary_max_mm": float(
            max(front_y[0, :].max(), front_y[-1, :].max(), front_y[:, 0].max(), front_y[:, -1].max())
        ),
        "texture_in_glyph_footprint_max_mm": float(front_y[glyph_distance == 0.0].max()),
    }
    return panel, report


def add_glyph_parts(parts: list[Manifold], spec: dict, x_start: float) -> None:
    geometry = spec["geometry"]
    glyph = geometry["glyph"]
    width = float(geometry["panel_width_mm"])
    height = float(geometry["panel_height_mm"])
    rectangles = glyph_rectangles(
        float(glyph["width_mm"]), float(glyph["height_mm"]), float(glyph["stroke_mm"])
    )
    raise_mm = float(glyph["raise_mm"])
    overlap = float(glyph["boolean_overlap_mm"])
    center_x = x_start + width / 2.0
    center_z = height / 2.0
    for x0, z0, x1, z1 in rectangles:
        box = Manifold.cube([x1 - x0, raise_mm + overlap, z1 - z0])
        box = box.translate([center_x + x0, -raise_mm, center_z + z0])
        parts.append(box)


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
    header = b"MM-PER-001 wood pitch coupon v0.1.0 - DRAFT"
    header = header[:80].ljust(80, b" ")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(faces)))
        handle.write(records.tobytes())


def build(spec_path: Path, output_root: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    source = spec["source"]
    master_path = REPO_ROOT / source["master"]
    registration_path = REPO_ROOT / source["registration"]
    recipe_path = REPO_ROOT / source["recipe"]
    for required in (master_path, registration_path, recipe_path):
        if not required.is_file():
            raise FileNotFoundError(required)
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    if sha256(master_path) != registration["master_sha256"]:
        raise ValueError("wood-001 master hash does not match its registration")

    master = Image.open(master_path)
    master_array = np.asarray(master)
    if master_array.ndim != 2 or master_array.dtype != np.uint16:
        raise ValueError(f"expected a 16-bit grayscale master, got {master.mode} {master_array.dtype}")

    geometry = spec["geometry"]
    candidates = spec["relief"]["candidates"]
    panel_width = float(geometry["panel_width_mm"])
    gap = float(geometry["panel_gap_mm"])
    margin = float(geometry["outer_base_margin_mm"])
    total_width = 2.0 * margin + len(candidates) * panel_width + (len(candidates) - 1) * gap

    parts: list[Manifold] = []
    panels_report: list[dict] = []
    heightmap_report: list[dict] = []
    for index, candidate in enumerate(candidates):
        pitch = float(candidate["mesh_pitch_mm"])
        x_start = margin + index * (panel_width + gap)
        build_map_path = (
            output_root / "build" / "heightmaps" / f"wood-001-pitch-{candidate_slug(pitch)}-16bit.png"
        )
        sampler, map_metadata = build_heightmap(
            master,
            build_map_path,
            pitch,
            float(spec["mapping"]["u_period_mm"]),
            float(spec["mapping"]["v_period_mm"]),
        )
        panel, panel_metadata = make_panel(sampler, spec, x_start, pitch)
        parts.append(panel)
        add_glyph_parts(parts, spec, x_start)
        panels_report.append({**candidate, **panel_metadata})
        heightmap_report.append({"candidate_id": candidate["id"], **map_metadata})

    base = Manifold.cube(
        [total_width, float(geometry["base_depth_mm"]), float(geometry["base_thickness_mm"])]
    )
    parts.append(base)
    coupon = Manifold.batch_boolean(parts, OpType.Add)
    if coupon.status() != Error.NoError or coupon.is_empty():
        raise RuntimeError(f"coupon union failed: {coupon.status()}")

    output_mesh = coupon.to_mesh()
    vertices = np.asarray(output_mesh.vert_properties, dtype=np.float64)[:, :3]
    faces = np.asarray(output_mesh.tri_verts, dtype=np.int64)
    stl_path = output_root / "exports" / "DRAFT-nameform-wood-texture-pitch-coupon-v0.1.0.stl"
    write_binary_stl_once(stl_path, vertices, faces)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    components = mesh.split(only_watertight=False)
    bounds = mesh.bounds
    extents = mesh.extents
    expected_bounds = np.asarray(spec["acceptance"]["expected_bounds_mm"], dtype=np.float64)
    max_triangles = int(spec["budgets"]["max_triangles"])
    max_mesh_bytes = float(spec["budgets"]["max_mesh_mib"]) * 1024.0 * 1024.0
    checks = [
        {"id": "watertight", "status": "PASS" if mesh.is_watertight else "FAIL", "actual": bool(mesh.is_watertight)},
        {"id": "winding", "status": "PASS" if mesh.is_winding_consistent else "FAIL", "actual": bool(mesh.is_winding_consistent)},
        {"id": "positive-volume", "status": "PASS" if mesh.volume > 0 else "FAIL", "actual_mm3": float(mesh.volume)},
        {"id": "single-body", "status": "PASS" if len(components) == 1 else "FAIL", "actual": len(components)},
        {"id": "bed-datum", "status": "PASS" if abs(float(bounds[0, 2])) <= 1.0e-6 else "FAIL", "actual_zmin_mm": float(bounds[0, 2])},
        {"id": "bounds", "status": "PASS" if np.allclose(extents, expected_bounds, atol=1.0e-5) else "FAIL", "actual_mm": extents.tolist(), "expected_mm": expected_bounds.tolist()},
        {"id": "triangle-budget", "status": "PASS" if len(faces) <= max_triangles else "FAIL", "actual": int(len(faces)), "maximum": max_triangles},
        {"id": "mesh-file-budget", "status": "PASS" if stl_path.stat().st_size <= max_mesh_bytes else "FAIL", "actual_bytes": stl_path.stat().st_size, "maximum_bytes": int(max_mesh_bytes)},
        {"id": "panel-wall-reserve", "status": "PASS" if all(panel["minimum_residual_wall_mm"] >= float(spec["acceptance"]["minimum_residual_panel_wall_mm"]) - 1.0e-6 for panel in panels_report) else "FAIL", "actual_min_mm": min(panel["minimum_residual_wall_mm"] for panel in panels_report), "minimum_mm": float(spec["acceptance"]["minimum_residual_panel_wall_mm"])},
        {"id": "protected-boundaries", "status": "PASS" if all(panel["texture_at_boundary_max_mm"] <= 1.0e-8 and panel["texture_in_glyph_footprint_max_mm"] <= 1.0e-8 for panel in panels_report) else "FAIL", "boundary_max_mm": max(panel["texture_at_boundary_max_mm"] for panel in panels_report), "glyph_footprint_max_mm": max(panel["texture_in_glyph_footprint_max_mm"] for panel in panels_report)},
    ]
    overall_status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    report = {
        "schema_version": "1.0",
        "tool": "MM-PER-001 wood-texture coupon generator",
        "tool_version": spec["revision"],
        "status": overall_status,
        "profile": "draft",
        "inputs": [
            {"path": str(spec_path), "sha256": sha256(spec_path)},
            {"path": str(master_path), "sha256": sha256(master_path)},
            {"path": str(registration_path), "sha256": sha256(registration_path)},
            {"path": str(recipe_path), "sha256": sha256(recipe_path)},
        ],
        "artifacts": [
            {"path": str(stl_path), "sha256": sha256(stl_path), "size_bytes": stl_path.stat().st_size},
            *heightmap_report,
        ],
        "checks": checks,
        "metrics": {
            "vertices": int(len(vertices)),
            "triangles": int(len(faces)),
            "bounds_min_mm": bounds[0].tolist(),
            "bounds_max_mm": bounds[1].tolist(),
            "extents_mm": extents.tolist(),
            "volume_mm3": float(mesh.volume),
            "surface_area_mm2": float(mesh.area),
            "euler_number": int(mesh.euler_number),
            "body_count": len(components),
            "panels": panels_report,
            "heightmaps": heightmap_report,
        },
        "limitations": [
            "Exact filament product, color, batch, drying state, and flow calibration are not recorded.",
            "The build raster preserves the Honeycomb shelf's intentional anisotropic physical mapping; it is a repeating texture rather than a recognizable subject.",
            "Exact Anycubic slicing and physical appearance/tactility remain separate gates.",
            "No printer upload or print start is performed by this generator.",
        ],
    }
    report_path = output_root / "reports" / "generation-report.json"
    write_json_once(report_path, report)
    if overall_status != "PASS":
        raise RuntimeError(f"coupon generation gate failed; see {report_path}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=COUPON_DIR / "coupon-spec.json")
    parser.add_argument("--output-root", type=Path, default=COUPON_DIR)
    args = parser.parse_args()
    report = build(args.spec.resolve(), args.output_root.resolve())
    print(
        json.dumps(
            {
                "status": report["status"],
                "stl": report["artifacts"][0]["path"],
                "triangles": report["metrics"]["triangles"],
                "extents_mm": report["metrics"]["extents_mm"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
