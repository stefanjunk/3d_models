#!/usr/bin/env python3
"""Prepare the immutable source mesh and emit OpenSCAD parameters."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
PARAMS_PATH = ROOT / "parameters.json"
REPORT_PATH = ROOT / "reports" / "source_preparation.json"
UPRIGHT_PATH = ROOT / "exports" / "upright_exterior_source_mesh.stl"
SCAD_PARAMS_PATH = ROOT / "generated_parameters.scad"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scad_literal(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(scad_literal(v) for v in value) + "]"
    raise TypeError(f"Unsupported OpenSCAD value: {type(value).__name__}")


def main() -> int:
    params = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    source = (ROOT / params["source"]["path"]).resolve()
    expected_hash = params["source"]["sha256"]
    actual_hash = sha256(source)
    if actual_hash != expected_hash:
        raise RuntimeError(f"Source hash changed: expected {expected_hash}, got {actual_hash}")

    raw = trimesh.load_mesh(source, process=False)
    original_bounds = np.asarray(raw.bounds, dtype=float)
    original_faces = int(len(raw.faces))

    # STL repeats triangle vertices. Processing/welding changes only indexing,
    # not the visible surface, and makes topology checks meaningful.
    mesh = trimesh.load_mesh(source, process=True)
    mesh.merge_vertices(digits_vertex=6)
    if not mesh.is_watertight or not mesh.is_winding_consistent:
        raise RuntimeError("Welded source is not a coherent watertight solid")

    rotation_deg = float(params["source"]["rotation_x_deg"])
    rotation = trimesh.transformations.rotation_matrix(
        np.deg2rad(rotation_deg), [1.0, 0.0, 0.0]
    )
    mesh.apply_transform(rotation)
    mesh.apply_scale(float(params["source"]["uniform_scale_mm_per_source_unit"]))
    mesh.apply_translation([0.0, 0.0, -float(mesh.bounds[0, 2])])
    mesh.units = "mm"

    UPRIGHT_PATH.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(UPRIGHT_PATH)
    reloaded = trimesh.load_mesh(UPRIGHT_PATH, process=True)
    reloaded.merge_vertices()
    if not reloaded.is_watertight or reloaded.body_count != 1:
        raise RuntimeError("Reloaded upright derivative failed topology checks")

    fg = params["functional_geometry"]
    spiral = fg["spiral"]
    inlet = fg["inlet"]
    outlet = fg["outlet"]
    values = {
        "source_mesh_path": "exports/upright_exterior_source_mesh.stl",
        "final_mesh_path": "exports/functional_unicorn_dice_tower.stl",
        "core_center_x": fg["core_center_x_mm"],
        "core_center_y": fg["core_center_y_mm"],
        "core_rx": fg["core_radius_x_mm"],
        "core_ry": fg["core_radius_y_mm"],
        "core_start_z": fg["core_start_z_mm"],
        "core_end_z": fg["core_end_z_mm"],
        # Spiral slide (v2 interior)
        "spiral_t_start": spiral["t_start_deg"],
        "spiral_t_end": spiral["t_end_deg"],
        "spiral_z_top": spiral["z_top_surface_start_mm"],
        "spiral_z_end": spiral["z_top_surface_end_mm"],
        "spiral_thickness": spiral["thickness_mm"],
        "spiral_edge_radius": spiral["edge_radius_mm"],
        "spiral_in_rx": spiral["inner_ellipse_rx_mm"],
        "spiral_in_ry": spiral["inner_ellipse_ry_mm"],
        "spiral_out_rx": spiral["outer_ellipse_rx_mm"],
        "spiral_out_ry": spiral["outer_ellipse_ry_mm"],
        "spiral_facets": spiral["facet_count"],
        "spiral_facet_overlap": spiral["facet_overlap_deg"],
        "spiral_fn": 20,
        # Openings
        "inlet_center_y": inlet["center_y_mm"],
        "inlet_center_z": inlet["center_z_mm"],
        "inlet_depth": inlet["depth_mm"],
        "inlet_width": inlet["clear_width_mm"],
        "inlet_height": inlet["clear_height_mm"],
        "inlet_radius": inlet["corner_radius_mm"],
        "outlet_center_y": outlet["center_y_mm"],
        "outlet_center_z": outlet["center_z_mm"],
        "outlet_depth": outlet["depth_mm"],
        "outlet_width": outlet["clear_width_mm"],
        "outlet_height": outlet["clear_height_mm"],
        "outlet_radius": outlet["corner_radius_mm"],
        # Die path
        "die_size": fg["die_path"]["cube_size_mm"],
        "die_path": fg["die_path"]["waypoints_mm"],
        "die_pose": fg["die_path"]["waypoint_pose_deg"],
        "render_fn": 48,
    }
    lines = [
        "// Generated from parameters.json by prepare_source.py; do not edit values here.",
        "// Units: millimetres. Interior: spiral slide v2.",
    ]
    lines.extend(f"{key} = {scad_literal(value)};" for key, value in values.items())
    SCAD_PARAMS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    centered = mesh.vertices - mesh.vertices.mean(axis=0)
    eigenvalues, eigenvectors = np.linalg.eigh(np.cov(centered.T))
    order = np.argsort(eigenvalues)[::-1]
    report = {
        "source": str(source),
        "source_sha256": actual_hash,
        "source_original_faces": original_faces,
        "source_original_bounds": original_bounds.round(9).tolist(),
        "welded_vertices": int(len(mesh.vertices)),
        "welded_faces": int(len(mesh.faces)),
        "rotation_x_deg": rotation_deg,
        "scale_mm_per_source_unit": params["source"]["uniform_scale_mm_per_source_unit"],
        "principal_axis_eigenvalues_after_orientation": eigenvalues[order].round(9).tolist(),
        "principal_axes_after_orientation_columns": eigenvectors[:, order].round(9).tolist(),
        "upright_bounds_mm": np.asarray(reloaded.bounds).round(6).tolist(),
        "upright_extents_mm": np.asarray(reloaded.extents).round(6).tolist(),
        "upright_watertight": bool(reloaded.is_watertight),
        "upright_winding_consistent": bool(reloaded.is_winding_consistent),
        "upright_body_count": int(reloaded.body_count),
        "upright_volume_mm3": float(reloaded.volume),
        "orientation_evidence": params["source"]["orientation_reason"],
        "front_back_evidence": params["orientation"]["visual_basis"],
        "interior_generation": "spiral_v2",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
