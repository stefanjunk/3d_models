"""Generate a physically scaled, watertight decorative image-relief insert."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
import trimesh


def _load_normalized(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        array = np.asarray(image)
        if array.ndim == 3:
            rgb = array[..., :3].astype(np.float64)
            array = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
        array = array.astype(np.float64)
    low = float(np.min(array))
    high = float(np.max(array))
    if high - low < 1e-12:
        return np.zeros(array.shape[:2], dtype=np.float64)
    return (array - low) / (high - low)


def _prepare_field(
    source: np.ndarray,
    width_mm: float,
    height_mm: float,
    pitch_mm: float,
    fit: str,
) -> tuple[np.ndarray, dict[str, float | int | str]]:
    nx = max(4, int(math.ceil(width_mm / pitch_mm)) + 1)
    nz = max(4, int(math.ceil(height_mm / pitch_mm)) + 1)
    pitch_x = width_mm / (nx - 1)
    pitch_z = height_mm / (nz - 1)
    source_h, source_w = source.shape
    source_aspect = source_w / source_h
    target_aspect = width_mm / height_mm
    if fit == "contain":
        if source_aspect >= target_aspect:
            placed_w = nx
            placed_h = max(2, round((placed_w - 1) * pitch_x / source_aspect / pitch_z) + 1)
        else:
            placed_h = nz
            placed_w = max(2, round((placed_h - 1) * pitch_z * source_aspect / pitch_x) + 1)
        placed_w = min(nx, placed_w)
        placed_h = min(nz, placed_h)
        resized = np.asarray(
            Image.fromarray(source.astype(np.float32)).resize(
                (placed_w, placed_h), Image.Resampling.LANCZOS
            ),
            dtype=np.float64,
        )
        field = np.zeros((nz, nx), dtype=np.float64)
        x0 = (nx - placed_w) // 2
        z0 = (nz - placed_h) // 2
        field[z0 : z0 + placed_h, x0 : x0 + placed_w] = resized
        placed_width_mm = (placed_w - 1) * pitch_x
        placed_height_mm = (placed_h - 1) * pitch_z
    elif fit == "cover":
        source_image = Image.fromarray(source.astype(np.float32))
        if source_aspect >= target_aspect:
            resized_h = nz
            resized_w = max(
                nx,
                round(height_mm * source_aspect / pitch_x) + 1,
            )
        else:
            resized_w = nx
            resized_h = max(
                nz,
                round(width_mm / source_aspect / pitch_z) + 1,
            )
        resized = np.asarray(
            source_image.resize((resized_w, resized_h), Image.Resampling.LANCZOS),
            dtype=np.float64,
        )
        x0 = (resized_w - nx) // 2
        z0 = (resized_h - nz) // 2
        field = resized[z0 : z0 + nz, x0 : x0 + nx]
        placed_width_mm = (resized_w - 1) * pitch_x
        placed_height_mm = (resized_h - 1) * pitch_z
    else:
        raise ValueError("fit must be 'contain' or 'cover'")
    return np.clip(field, 0.0, 1.0), {
        "samples_x": nx,
        "samples_z": nz,
        "source_pixel_width": source_w,
        "source_pixel_height": source_h,
        "source_aspect": source_aspect,
        "target_physical_aspect": target_aspect,
        "placed_width_mm": placed_width_mm,
        "placed_height_mm": placed_height_mm,
        "fit": fit,
    }


def _heightfield_solid(
    field: np.ndarray,
    width_mm: float,
    height_mm: float,
    base_thickness_mm: float,
    relief_depth_mm: float,
    mode: str,
) -> trimesh.Trimesh:
    rows, columns = field.shape
    xs = np.linspace(-width_mm / 2.0, width_mm / 2.0, columns)
    zs = np.linspace(-height_mm / 2.0, height_mm / 2.0, rows)
    xx, zz = np.meshgrid(xs, zs)
    if mode == "emboss":
        front_y = base_thickness_mm + relief_depth_mm * field
    elif mode == "engrave":
        front_y = base_thickness_mm - relief_depth_mm * field
    else:
        raise ValueError("mode must be 'engrave' or 'emboss'")
    if float(front_y.min()) < 1.2:
        raise ValueError("Image engraving leaves less than 1.2 mm backer thickness")

    count = rows * columns
    back_vertices = np.column_stack([xx.ravel(), np.zeros(count), zz.ravel()])
    front_vertices = np.column_stack([xx.ravel(), front_y.ravel(), zz.ravel()])
    vertices = np.vstack([back_vertices, front_vertices])
    faces: list[list[int]] = []
    for row in range(rows - 1):
        for column in range(columns - 1):
            bl = row * columns + column
            br = bl + 1
            tl = (row + 1) * columns + column
            tr = tl + 1
            faces.extend([[bl, tr, br], [bl, tl, tr]])
            faces.extend(
                [
                    [count + bl, count + br, count + tr],
                    [count + bl, count + tr, count + tl],
                ]
            )
    for column in range(columns - 1):
        a, b = column, column + 1
        faces.extend([[a, b, count + b], [a, count + b, count + a]])
        a = (rows - 1) * columns + column
        b = a + 1
        faces.extend([[a, count + b, b], [a, count + a, count + b]])
    for row in range(rows - 1):
        a, b = row * columns, (row + 1) * columns
        faces.extend([[a, count + b, b], [a, count + a, count + b]])
        a = row * columns + columns - 1
        b = (row + 1) * columns + columns - 1
        faces.extend([[a, b, count + b], [a, count + b, count + a]])
    mesh = trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=True)
    trimesh.repair.fix_normals(mesh)
    return mesh


def generate_image_relief(
    source_path: Path,
    output_stl: Path,
    build_master: Path,
    preview_path: Path,
    metadata_path: Path,
    width_mm: float,
    height_mm: float,
    base_thickness_mm: float,
    relief_depth_mm: float,
    pitch_mm: float,
    mode: str,
    invert: bool,
    fit: str,
    assembly_local_stl: Path | None = None,
    triangle_budget: int = 1_000_000,
    memory_budget_gib: float = 4.0,
    max_mesh_mib: float = 60.0,
    max_slicer_seconds: float = 120.0,
) -> dict[str, object]:
    source = _load_normalized(source_path)
    field, metadata = _prepare_field(source, width_mm, height_mm, pitch_mm, fit)
    if invert:
        field = 1.0 - field
    reconstructed_aspect = metadata["placed_width_mm"] / metadata["placed_height_mm"]
    source_aspect = float(metadata["source_aspect"])
    aspect_error_pct = abs(reconstructed_aspect / source_aspect - 1.0) * 100.0
    if aspect_error_pct > 0.75:
        raise ValueError(
            f"Physical aspect error {aspect_error_pct:.3f}% exceeds 0.75% before geometry"
        )
    build_u16 = np.round(field * 65535.0).astype(np.uint16)
    build_master.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(build_u16).save(build_master)
    preview = np.round(field * 255.0).astype(np.uint8)
    Image.fromarray(preview).resize((1200, 467), Image.Resampling.NEAREST).save(preview_path)

    local_mesh = _heightfield_solid(
        field,
        width_mm,
        height_mm,
        base_thickness_mm,
        relief_depth_mm,
        mode,
    )
    if assembly_local_stl is not None:
        assembly_local_stl.parent.mkdir(parents=True, exist_ok=True)
        local_mesh.export(assembly_local_stl)
    mesh = local_mesh.copy()
    mesh.apply_transform(
        trimesh.transformations.rotation_matrix(math.pi / 2.0, [1.0, 0.0, 0.0])
    )
    mesh.apply_translation([0.0, 0.0, -float(mesh.bounds[0, 2])])
    if len(mesh.faces) > triangle_budget:
        raise ValueError(
            f"Relief mesh has {len(mesh.faces)} triangles, above budget {triangle_budget}"
        )
    output_stl.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(output_stl)
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    build_master_hash = hashlib.sha256(build_master.read_bytes()).hexdigest()
    stl_hash = hashlib.sha256(output_stl.read_bytes()).hexdigest()
    file_size_mib = output_stl.stat().st_size / (1024.0**2)
    estimated_working_memory_gib = len(mesh.faces) * 1024.0 / (1024.0**3)
    report: dict[str, object] = {
        **metadata,
        "source": str(source_path),
        "source_sha256": source_hash,
        "output_stl": str(output_stl),
        "assembly_local_stl": str(assembly_local_stl) if assembly_local_stl else None,
        "build_master_16bit": str(build_master),
        "build_master_sha256": build_master_hash,
        "preview": str(preview_path),
        "physical_width_mm": width_mm,
        "physical_height_mm": height_mm,
        "pitch_mm": pitch_mm,
        "base_thickness_mm": base_thickness_mm,
        "relief_depth_mm": relief_depth_mm,
        "mode": mode,
        "invert": invert,
        "reconstructed_placed_aspect": reconstructed_aspect,
        "aspect_error_pct": aspect_error_pct,
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "triangle_budget": triangle_budget,
        "estimated_working_memory_gib": estimated_working_memory_gib,
        "memory_budget_gib": memory_budget_gib,
        "mesh_file_size_mib": file_size_mib,
        "max_mesh_mib": max_mesh_mib,
        "max_slicer_seconds": max_slicer_seconds,
        "exact_slicer_time_seconds": None,
        "resource_budget_status": (
            "PASS_PLANNING_PENDING_SLICER"
            if estimated_working_memory_gib <= memory_budget_gib
            and file_size_mib <= max_mesh_mib
            else "FAIL"
        ),
        "manufacturing_stl_sha256": stl_hash,
        "watertight": bool(mesh.is_watertight),
        "volume_mm3": float(abs(mesh.volume)),
        "assembly_local_bounds_mm": local_mesh.bounds.tolist(),
        "bounds_mm": mesh.bounds.tolist(),
    }
    metadata_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output_stl", type=Path)
    parser.add_argument("--build-master", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--size-mm", default="180x70")
    parser.add_argument("--base-thickness", type=float, default=2.2)
    parser.add_argument("--depth", type=float, default=0.45)
    parser.add_argument("--pitch", type=float, default=0.60)
    parser.add_argument("--mode", choices=("engrave", "emboss"), default="engrave")
    parser.add_argument("--invert", action="store_true")
    parser.add_argument("--fit", choices=("contain", "cover"), default="contain")
    parser.add_argument("--triangle-budget", type=int, default=1_000_000)
    parser.add_argument("--memory-budget-gib", type=float, default=4.0)
    parser.add_argument("--max-mesh-mib", type=float, default=60.0)
    parser.add_argument("--max-slicer-seconds", type=float, default=120.0)
    args = parser.parse_args()
    width, height = (float(value) for value in args.size_mm.lower().split("x", 1))
    report = generate_image_relief(
        args.source,
        args.output_stl,
        args.build_master,
        args.preview,
        args.metadata,
        width,
        height,
        args.base_thickness,
        args.depth,
        args.pitch,
        args.mode,
        args.invert,
        args.fit,
        None,
        args.triangle_budget,
        args.memory_budget_gib,
        args.max_mesh_mib,
        args.max_slicer_seconds,
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
