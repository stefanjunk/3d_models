#!/usr/bin/env python3
"""Create the CAD-owned flat underside of the Step1X sunflower shell."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh


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
        "positive_volume": bool(mesh.is_volume),
        "bounds_mm": np.asarray(mesh.bounds).tolist(),
        "extents_mm": np.asarray(mesh.extents).tolist(),
        "volume_mm3": float(mesh.volume),
        "area_mm2": float(mesh.area),
    }


def flat_base_facts(mesh: trimesh.Trimesh, tolerance: float = 1.0e-5) -> dict[str, object]:
    z = np.asarray(mesh.vertices)[:, 2]
    face_z = z[np.asarray(mesh.faces)]
    bottom_faces = np.all(np.abs(face_z) <= tolerance, axis=1)
    indexes = np.flatnonzero(bottom_faces)
    if len(indexes) == 0:
        return {"faces": 0, "area_mm2": 0.0, "span_xy_mm": [0.0, 0.0], "equivalent_diameter_mm": 0.0}
    triangles = mesh.triangles[indexes]
    area = float(trimesh.triangles.area(triangles).sum())
    points = triangles.reshape((-1, 3))
    spans = np.ptp(points[:, :2], axis=0)
    equivalent_diameter = float(np.sqrt(4.0 * area / np.pi))
    return {
        "faces": int(len(indexes)),
        "area_mm2": area,
        "span_xy_mm": spans.tolist(),
        "equivalent_diameter_mm": equivalent_diameter,
        "plane_z_mm": 0.0,
        "tolerance_mm": tolerance,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("parameters", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    parameter_path = args.parameters.resolve()
    source_path = args.source.resolve()
    output_path = args.output.resolve()
    report_path = args.report.resolve()
    params = json.loads(parameter_path.read_text(encoding="utf-8"))
    source = trimesh.load_mesh(source_path, process=True)
    if isinstance(source, trimesh.Scene):
        source = source.to_geometry()
    if not isinstance(source, trimesh.Trimesh) or not source.is_watertight or not source.is_volume:
        raise RuntimeError("source must be one positive watertight mesh")
    if len(source.split(only_watertight=False)) != 1:
        raise RuntimeError("source must contain exactly one connected component")

    base_cut = float(params["base_cut_mm"])
    edit_band = float(params["underside_edit_band_max_z_mm"])
    if not 0.0 < base_cut <= edit_band:
        raise RuntimeError("base cut must be positive and stay inside the underside edit band")
    cutter = trimesh.creation.box(
        extents=[500.0, 500.0, base_cut + 20.0],
        transform=trimesh.transformations.translation_matrix([0.0, 0.0, (base_cut - 20.0) / 2.0]),
    )
    candidate = trimesh.boolean.difference([source, cutter], engine="manifold")
    if not isinstance(candidate, trimesh.Trimesh):
        raise RuntimeError("planar base Boolean did not return a mesh")
    candidate.apply_translation([0.0, 0.0, -float(candidate.bounds[0, 2])])
    candidate.merge_vertices()
    area_threshold = max(float(candidate.area), 1.0) * np.finfo(float).eps * 100.0
    candidate.update_faces(np.asarray(candidate.area_faces) > area_threshold)
    candidate.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(candidate, multibody=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    candidate.export(output_path)
    base = flat_base_facts(candidate)
    failures = []
    if not candidate.is_watertight or not candidate.is_volume:
        failures.append("candidate is not a positive watertight solid")
    if len(candidate.split(only_watertight=False)) != 1:
        failures.append("candidate is not one connected component")
    if float(candidate.extents[2]) > float(params["maximum_height_mm"]) + 1.0e-4:
        failures.append("candidate exceeds the maximum height")
    if min(base["span_xy_mm"]) < float(params["minimum_flat_support_span_mm"]):
        failures.append("flat support span is below the declared minimum")

    report = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "operation": "bounded underside planar trim and automatic manifold cap",
        "authority": {
            "organic_visible_surface": str(source_path),
            "parametric_underside": str(parameter_path),
            "manufacturing_candidate": str(output_path),
        },
        "inputs": {
            "parameters": {"path": str(parameter_path), "sha256": sha256(parameter_path)},
            "source": {"path": str(source_path), "sha256": sha256(source_path), **facts(source)},
        },
        "parameters": params,
        "candidate": {"path": str(output_path), "sha256": sha256(output_path), **facts(candidate)},
        "flat_base": base,
        "protected_region": {
            "source_z_mm": [edit_band, float(source.bounds[1, 2])],
            "operation": "identity; no Boolean cutter intersection at or above the declared 3 mm boundary",
        },
        "failures": failures,
        "release_blockers": [
            "exact-profile slicer and final layer review pending",
            "physical rocking, tilt, edge-comfort and snag tests NOT_RUN",
            "commercial rights, marking and human release approvals remain open"
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
