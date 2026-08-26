#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage.color import deltaE_ciede2000, rgb2lab
import trimesh

from common import hex_to_rgb8, load_palette, save_json, sha256_file


def load_single_textured_mesh(path: Path) -> tuple[trimesh.Trimesh, Image.Image]:
    loaded = trimesh.load(path, force="scene", process=False)
    scene = loaded if isinstance(loaded, trimesh.Scene) else trimesh.Scene(loaded)
    meshes = [geometry for geometry in scene.geometry.values() if isinstance(geometry, trimesh.Trimesh)]
    if len(meshes) != 1:
        raise ValueError(f"Expected one textured mesh, found {len(meshes)}. Bake/merge the asset first.")
    mesh = meshes[0]
    uv = getattr(mesh.visual, "uv", None)
    material = getattr(mesh.visual, "material", None)
    image = getattr(material, "image", None) if material is not None else None
    if image is None and material is not None:
        image = getattr(material, "baseColorTexture", None)
    if uv is None or len(uv) != len(mesh.vertices):
        raise ValueError("Mesh has no per-vertex UV coordinates")
    if image is None:
        raise ValueError("No base-color image found in the textured material")
    if not isinstance(image, Image.Image):
        try:
            image = Image.fromarray(np.asarray(image))
        except Exception as exc:
            raise ValueError(f"Unsupported texture image type: {type(image).__name__}") from exc
    return mesh, image.convert("RGBA")


def palette_labels(rgb01: np.ndarray, palette_rgb01: np.ndarray) -> np.ndarray:
    sample_lab = rgb2lab(rgb01.reshape(-1, 1, 3)).reshape(-1, 3)
    palette_lab = rgb2lab(palette_rgb01.reshape(1, -1, 3)).reshape(-1, 3)
    distance = np.stack([deltaE_ciede2000(sample_lab, color[None, :]) for color in palette_lab], axis=1)
    return np.argmin(distance, axis=1).astype(np.int16)


def closest_triangles(mesh: trimesh.Trimesh, points: np.ndarray, *, k: int = 8, chunk: int = 20_000) -> tuple[np.ndarray, np.ndarray]:
    centers = np.asarray(mesh.triangles_center)
    tree = cKDTree(centers)
    chosen_faces = np.empty(len(points), dtype=np.int64)
    chosen_points = np.empty_like(points, dtype=float)
    k = min(k, len(centers))
    for start in range(0, len(points), chunk):
        stop = min(start + chunk, len(points))
        query = points[start:stop]
        _, candidates = tree.query(query, k=k)
        if k == 1:
            candidates = candidates[:, None]
        candidate_triangles = mesh.triangles[candidates.reshape(-1)]
        repeated = np.repeat(query, k, axis=0)
        nearest = trimesh.triangles.closest_point(candidate_triangles, repeated)
        distance2 = np.sum((nearest - repeated) ** 2, axis=1).reshape(len(query), k)
        selection = np.argmin(distance2, axis=1)
        rows = np.arange(len(query))
        chosen_faces[start:stop] = candidates[rows, selection]
        chosen_points[start:stop] = nearest.reshape(len(query), k, 3)[rows, selection]
    return chosen_faces, chosen_points


def sample_texture(mesh: trimesh.Trimesh, image: Image.Image, points: np.ndarray, palette_rgb01: np.ndarray, *, chunk: int = 20_000) -> np.ndarray:
    uv = np.asarray(mesh.visual.uv, dtype=float)
    image_array = np.asarray(image, dtype=np.float64) / 255.0
    height, width = image_array.shape[:2]
    labels = np.empty(len(points), dtype=np.int16)
    for start in range(0, len(points), chunk):
        stop = min(start + chunk, len(points))
        faces, closest = closest_triangles(mesh, points[start:stop], chunk=chunk)
        triangles = mesh.triangles[faces]
        bary = trimesh.triangles.points_to_barycentric(triangles, closest)
        face_uv = uv[mesh.faces[faces]]
        sampled_uv = np.sum(face_uv * bary[:, :, None], axis=1)
        u = np.mod(sampled_uv[:, 0], 1.0)
        v = np.clip(sampled_uv[:, 1], 0.0, 1.0)
        px = np.clip(np.rint(u * (width - 1)).astype(int), 0, width - 1)
        py = np.clip(np.rint((1.0 - v) * (height - 1)).astype(int), 0, height - 1)
        rgba = image_array[py, px]
        rgb = rgba[:, :3] * rgba[:, 3:4] + palette_rgb01[0][None, :] * (1.0 - rgba[:, 3:4])
        labels[start:stop] = palette_labels(rgb, palette_rgb01)
    return labels


def remove_small_components(label_grid: np.ndarray, occupied: np.ndarray, minimum: int, base_index: int) -> dict[str, Any]:
    removed = 0
    voxels = 0
    structure = ndimage.generate_binary_structure(3, 1)
    for color in np.unique(label_grid[occupied]):
        if color == base_index:
            continue
        components, count = ndimage.label((label_grid == color) & occupied, structure=structure)
        if count == 0:
            continue
        sizes = np.bincount(components.ravel())
        for component in range(1, count + 1):
            size = int(sizes[component])
            if size < minimum:
                mask = components == component
                label_grid[mask] = base_index
                removed += 1
                voxels += size
    return {"minimum_component_voxels": minimum, "components_reassigned": removed, "voxels_reassigned": voxels}


def mask_to_mesh(mask: np.ndarray, pitch: float, origin: np.ndarray) -> trimesh.Trimesh:
    padded = np.pad(mask.astype(bool), 1, mode="constant")
    mesh = trimesh.voxel.ops.matrix_to_marching_cubes(padded, pitch=pitch)
    mesh.apply_translation(np.asarray(origin, dtype=float) - pitch)
    mesh.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(mesh, multibody=True)
    return mesh


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a textured watertight OBJ/GLB into aligned color-part solids through a voxel shell partition.")
    parser.add_argument("asset", type=Path)
    parser.add_argument("--palette", required=True, type=Path)
    parser.add_argument("--pitch", required=True, type=float)
    parser.add_argument("--shell-depth", required=True, type=float)
    parser.add_argument("--base-color")
    parser.add_argument("--minimum-component-voxels", type=int, default=4)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if args.pitch <= 0 or args.shell_depth <= 0:
        raise SystemExit("Pitch and shell depth must be positive")
    palette = load_palette(args.palette)
    palette_rgb8 = np.array([hex_to_rgb8(item["display_hex"]) for item in palette], dtype=np.uint8)
    palette_rgb01 = palette_rgb8.astype(float) / 255.0
    id_to_index = {item["id"]: i for i, item in enumerate(palette)}
    base_index = id_to_index.get(args.base_color, 0)

    mesh, image = load_single_textured_mesh(args.asset)
    # UV seams commonly duplicate coincident vertices. Preserve the textured mesh for
    # sampling, but weld a geometry-only copy for watertightness and voxel filling.
    voxel_mesh = mesh.copy()
    voxel_mesh.merge_vertices(merge_tex=True, merge_norm=True)
    voxel_mesh.remove_unreferenced_vertices()
    if not voxel_mesh.is_watertight:
        raise SystemExit("Input geometry is not watertight after welding coincident UV-seam vertices. Repair it first.")

    voxel_grid = voxel_mesh.voxelized(args.pitch).fill()
    occupied = np.asarray(voxel_grid.matrix, dtype=bool)
    if not occupied.any():
        raise SystemExit("Voxelization produced an empty grid")
    distance_inside = ndimage.distance_transform_edt(occupied) * args.pitch
    shell = occupied & (distance_inside <= args.shell_depth + args.pitch * 0.51)
    boundary = occupied & ~ndimage.binary_erosion(occupied, structure=ndimage.generate_binary_structure(3, 1), border_value=0)
    boundary_indices = np.argwhere(boundary)
    boundary_points = voxel_grid.indices_to_points(boundary_indices)
    boundary_labels = sample_texture(mesh, image, boundary_points, palette_rgb01)

    boundary_grid = np.full(occupied.shape, -1, dtype=np.int16)
    boundary_grid[tuple(boundary_indices.T)] = boundary_labels
    _, nearest_indices = ndimage.distance_transform_edt(~boundary, return_indices=True)
    propagated = boundary_grid[tuple(nearest_indices)]
    label_grid = np.full(occupied.shape, base_index, dtype=np.int16)
    label_grid[shell] = propagated[shell]
    cleanup = remove_small_components(label_grid, occupied, max(args.minimum_component_voxels, 1), base_index)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    parts = []
    mesh_reports = []
    origin = np.asarray(voxel_grid.transform[:3, 3], dtype=float)
    for index, item in enumerate(palette):
        mask = occupied & (label_grid == index)
        count = int(mask.sum())
        if count == 0:
            continue
        part_mesh = mask_to_mesh(mask, args.pitch, origin)
        part_path = args.output_dir / f"{index + 1:02d}-{item['id']}.stl"
        part_mesh.export(part_path)
        parts.append({
            "id": item["id"],
            "material_name": item["name"],
            "display_hex": item["display_hex"],
            "path": part_path.name,
            "temporary_slot": item.get("temporary_slot"),
        })
        mesh_reports.append({
            "id": item["id"],
            "voxel_count": count,
            "vertices": int(len(part_mesh.vertices)),
            "faces": int(len(part_mesh.faces)),
            "watertight": bool(part_mesh.is_watertight),
            "connected_bodies": int(part_mesh.body_count),
            "volume_mm3": float(part_mesh.volume) if part_mesh.is_volume else None,
            "path": str(part_path.resolve()),
        })

    manifest = {
        "version": 1,
        "source": str(args.asset.resolve()),
        "source_sha256": sha256_file(args.asset),
        "palette": str(args.palette.resolve()),
        "pitch_mm": args.pitch,
        "shell_depth_mm": args.shell_depth,
        "base_color": palette[base_index]["id"],
        "parts": parts,
    }
    manifest_path = args.output_dir / "parts-manifest.json"
    save_json(manifest_path, manifest)

    report: dict[str, Any] = {
        "source": str(args.asset.resolve()),
        "source_sha256": sha256_file(args.asset),
        "source_faces": int(len(mesh.faces)),
        "source_vertices": int(len(mesh.vertices)),
        "source_bounds_mm": mesh.bounds.round(6).tolist(),
        "voxel_geometry_watertight_after_weld": bool(voxel_mesh.is_watertight),
        "voxel_pitch_mm": args.pitch,
        "voxel_shape": list(map(int, occupied.shape)),
        "occupied_voxels": int(occupied.sum()),
        "shell_voxels": int(shell.sum()),
        "estimated_dense_arrays_mb": float(np.prod(occupied.shape) * 18 / (1024 ** 2)),
        "shell_depth_mm": args.shell_depth,
        "cleanup": cleanup,
        "parts_manifest": str(manifest_path.resolve()),
        "parts": mesh_reports,
    }
    if args.report:
        save_json(args.report, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
