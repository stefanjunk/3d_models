#!/usr/bin/env python3
"""Apply a CAD-owned flat base, tapered nursery-pot cavity and visible drain tunnel."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from cadquery import exporters


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def facts(mesh: trimesh.Trimesh) -> dict[str, object]:
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "components": int(len(mesh.split(only_watertight=False))),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "bounds_mm": np.asarray(mesh.bounds).tolist(),
        "extents_mm": np.asarray(mesh.extents).tolist(),
        "volume_mm3": float(mesh.volume),
    }


def load_mesh(path: Path, role: str) -> trimesh.Trimesh:
    loaded = trimesh.load_mesh(path, process=True)
    if isinstance(loaded, trimesh.Scene):
        loaded = loaded.to_geometry()
    if not isinstance(loaded, trimesh.Trimesh):
        raise RuntimeError(f"{role} is not a triangle mesh: {path}")
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("parameters", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    parameter_path = args.parameters.resolve()
    params = json.loads(parameter_path.read_text(encoding="utf-8"))
    product_root = parameter_path.parent.parent
    source_path = (product_root / params["source_mesh"]).resolve()
    source = load_mesh(source_path, "source")
    if not source.is_watertight or len(source.split(only_watertight=False)) != 1:
        raise RuntimeError("source must be one watertight component")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    base_cut = float(params["base_cut_mm"])
    base_cutter = trimesh.creation.box(
        extents=[400.0, 400.0, base_cut + 20.0],
        transform=trimesh.transformations.translation_matrix([0.0, 0.0, (base_cut - 20.0) / 2.0]),
    )
    flat = trimesh.boolean.difference([source, base_cutter], engine="manifold")
    if not isinstance(flat, trimesh.Trimesh):
        raise RuntimeError("base Boolean did not return a mesh")
    flat.apply_translation([0.0, 0.0, -float(flat.bounds[0, 2])])
    flat_path = output_dir / "02-flat-base.stl"
    flat.export(flat_path)

    cavity = params["cavity"]
    drain = params["drain_tunnel"]
    center_x, center_y = map(float, cavity["center_xy_mm"])
    floor_z = float(cavity["floor_z_after_base_cut_mm"])
    top_z = float(cavity["cutter_top_z_mm"])
    cavity_cutter = (
        cq.Workplane("XY", origin=(center_x, center_y, floor_z))
        .circle(float(cavity["bottom_diameter_mm"]) / 2.0)
        .workplane(offset=top_z - floor_z)
        .circle(float(cavity["top_diameter_mm"]) / 2.0)
        .loft(combine=True)
    )
    exit_y = float(drain["exit_y_mm"])
    drain_length = exit_y - center_y + 10.0
    drain_height = float(drain["height_mm"])
    drain_box = (
        cq.Workplane("XY")
        .box(float(drain["width_mm"]), drain_length, drain_height, centered=(True, True, True))
        .translate(
            (
                center_x,
                center_y + (exit_y - center_y) / 2.0,
                floor_z + float(drain["top_overlap_above_cavity_floor_mm"]) - drain_height / 2.0,
            )
        )
    )
    cutter = cavity_cutter.union(drain_box)
    cutter_step = output_dir / "cavity-and-drain-cutter.step"
    cutter_stl = output_dir / "cavity-and-drain-cutter.stl"
    exporters.export(cutter, str(cutter_step))
    exporters.export(cutter, str(cutter_stl))
    cutter_mesh = load_mesh(cutter_stl, "cutter")

    final = trimesh.boolean.difference([flat, cutter_mesh], engine="manifold")
    if not isinstance(final, trimesh.Trimesh):
        raise RuntimeError("cavity Boolean did not return a mesh")
    raw_candidate_path = output_dir / "03-cavity-and-drain-boolean.stl"
    final.export(raw_candidate_path)
    raw_candidate_facts = facts(final)
    final.merge_vertices()
    area_threshold = max(float(final.area), 1.0) * np.finfo(float).eps * 100.0
    final.update_faces(np.asarray(final.area_faces) > area_threshold)
    final.remove_unreferenced_vertices()
    if not final.is_watertight:
        trimesh.repair.fill_holes(final)
        trimesh.repair.fix_normals(final, multibody=True)
    final_path = output_dir / "04-cavity-and-drain-clean.stl"
    final.export(final_path)

    report = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "UNQUALIFIED_DESIGN_CANDIDATE",
        "authority": {
            "organic_surface": str(source_path),
            "flat_base_and_wet_interface": "parametric CAD owned by this product",
            "host_fit": "UNQUALIFIED; no nursery pot has been measured",
        },
        "inputs": {"parameters": {"path": str(parameter_path), "sha256": sha256(parameter_path)}, "source": {"path": str(source_path), "sha256": sha256(source_path)}},
        "parameters": params,
        "source_facts": facts(source),
        "flat_base": {"path": str(flat_path), "sha256": sha256(flat_path), **facts(flat)},
        "cutter": {"step": str(cutter_step), "step_sha256": sha256(cutter_step), "stl": str(cutter_stl), "stl_sha256": sha256(cutter_stl)},
        "raw_boolean_candidate": {"path": str(raw_candidate_path), "sha256": sha256(raw_candidate_path), **raw_candidate_facts},
        "candidate": {"path": str(final_path), "sha256": sha256(final_path), **facts(final)},
        "release_blockers": ["exact host pot unmeasured", "cavity clearance unqualified", "drainage and hidden-pooling test NOT_RUN", "loaded tip-stability test NOT_RUN", "minimum wall and slicer review pending"],
    }
    report_path = output_dir / "functionalization-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
