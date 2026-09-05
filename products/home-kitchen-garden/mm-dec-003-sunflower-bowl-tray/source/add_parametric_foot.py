#!/usr/bin/env python3
"""Add the owner-confirmed parametric disc foot to an unchanged Step1X body."""

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
    vertices_z = np.asarray(mesh.vertices)[:, 2]
    face_z = vertices_z[np.asarray(mesh.faces)]
    flat_indexes = np.flatnonzero(np.all(np.abs(face_z) <= tolerance, axis=1))
    if len(flat_indexes) == 0:
        return {"faces": 0, "area_mm2": 0.0, "span_xy_mm": [0.0, 0.0]}
    triangles = mesh.triangles[flat_indexes]
    points = triangles.reshape((-1, 3))
    return {
        "faces": int(len(flat_indexes)),
        "area_mm2": float(trimesh.triangles.area(triangles).sum()),
        "span_xy_mm": np.ptp(points[:, :2], axis=0).tolist(),
        "plane_z_mm": 0.0,
        "tolerance_mm": tolerance,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("parameters", type=Path)
    parser.add_argument("body", type=Path)
    parser.add_argument("foot_output", type=Path)
    parser.add_argument("result_output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    parameter_path = args.parameters.resolve()
    body_path = args.body.resolve()
    foot_path = args.foot_output.resolve()
    result_path = args.result_output.resolve()
    report_path = args.report.resolve()
    parameters = json.loads(parameter_path.read_text(encoding="utf-8"))
    foot_parameters = parameters["foot"]

    body = trimesh.load_mesh(body_path, process=True)
    if isinstance(body, trimesh.Scene):
        body = body.to_geometry()
    if not isinstance(body, trimesh.Trimesh):
        raise RuntimeError("body did not load as one triangle mesh")
    if not body.is_watertight or not body.is_volume:
        raise RuntimeError("Step1X body must be a positive watertight solid")
    if len(body.split(only_watertight=False)) != 1:
        raise RuntimeError("Step1X body must contain exactly one connected component")
    if abs(float(body.bounds[0, 2])) > 1.0e-5:
        raise RuntimeError("registered Step1X body must have min Z = 0")

    diameter = float(foot_parameters["diameter_mm"])
    thickness = float(foot_parameters["thickness_mm"])
    center_x, center_y = (float(value) for value in foot_parameters["center_xy_mm"])
    protrusion = float(foot_parameters["protrusion_below_generated_min_z_mm"])
    sections = int(foot_parameters["radial_sections"])
    if diameter <= 0.0 or thickness <= 0.0 or not 0.0 < protrusion < thickness:
        raise RuntimeError("foot dimensions and overlap placement are invalid")
    if sections < 64:
        raise RuntimeError("radial_sections must be at least 64")

    foot = trimesh.creation.cylinder(radius=diameter / 2.0, height=thickness, sections=sections)
    foot.apply_translation([center_x, center_y, thickness / 2.0 - protrusion])
    combined = trimesh.boolean.union([body, foot], engine="manifold")
    if not isinstance(combined, trimesh.Trimesh):
        raise RuntimeError("manifold union did not return one mesh")

    final_translation = np.asarray([0.0, 0.0, protrusion])
    foot.apply_translation(final_translation)
    combined.apply_translation(final_translation)
    combined.merge_vertices()
    combined.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(combined, multibody=True)

    foot_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    foot.export(foot_path)
    combined.export(result_path)

    base = flat_base_facts(combined)
    failures: list[str] = []
    if not combined.is_watertight or not combined.is_volume:
        failures.append("result is not a positive watertight solid")
    if len(combined.split(only_watertight=False)) != 1:
        failures.append("result is not one connected component")
    if min(base["span_xy_mm"]) < diameter - 0.1:
        failures.append("flat base span is smaller than the declared disc diameter")

    report = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "operation": "owner-authorized parametric 80 x 6 mm disc-foot union",
        "authority_boundary": {
            "generated_body": "Step1X run-004; no parametric reconstruction or petal repair",
            "parametric_component": "disc foot only",
            "allowed_edit_region": parameters["operation"]["allowed_edit_region"],
        },
        "inputs": {
            "parameters": {"path": str(parameter_path), "sha256": sha256(parameter_path)},
            "body": {"path": str(body_path), "sha256": sha256(body_path), **facts(body)},
        },
        "foot": {"path": str(foot_path), "sha256": sha256(foot_path), **facts(foot)},
        "result": {"path": str(result_path), "sha256": sha256(result_path), **facts(combined)},
        "flat_base": base,
        "failures": failures,
        "release_blockers": [
            "physical rocking, tilt, edge and snag tests not run",
            "final layer/support/seam preview requires human review",
            "commercial rights, marking and signed release approvals remain open",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
