#!/usr/bin/env python3
"""Deterministic V0/V1 validation for the DRAFT revision-3 candidate.

This script intentionally does not claim slicer, physical FIFO, wall-anchor,
proof-load, cleaning, or service validation. It rebuilds the CadQuery model,
checks the five nominal rigid roll gauges, and cross-checks draft exports
against the build manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "source"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import generate_r3 as generator  # noqa: E402


INTERSECTION_TOLERANCE_MM3 = 1.0e-4
METRIC_TOLERANCE_MM = 1.0e-3


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_normalized(value: Any) -> Any:
    return json.loads(json.dumps(value))


def add_check(checks: list[dict[str, Any]], check_id: str, passed: bool, evidence: Any) -> None:
    checks.append(
        {
            "id": check_id,
            "status": "PASS" if passed else "FAIL",
            "evidence": evidence,
        }
    )


def shape_bounds(shape) -> list[list[float]]:
    bounds = shape.BoundingBox()
    return [
        [round(bounds.xmin, 3), round(bounds.ymin, 3), round(bounds.zmin, 3)],
        [round(bounds.xmax, 3), round(bounds.ymax, 3), round(bounds.zmax, 3)],
    ]


def combined_bounds(shapes) -> tuple[list[list[float]], list[float]]:
    boxes = [shape.BoundingBox() for shape in shapes]
    lower = [min(getattr(box, axis + "min") for box in boxes) for axis in "xyz"]
    upper = [max(getattr(box, axis + "max") for box in boxes) for axis in "xyz"]
    extents = [upper[index] - lower[index] for index in range(3)]
    return (
        [[round(value, 3) for value in lower], [round(value, 3) for value in upper]],
        [round(value, 3) for value in extents],
    )


def validate(project_root: Path) -> dict[str, Any]:
    spec_path = project_root / "design-spec.yaml"
    manifest_path = project_root / "validation" / "build-manifest-r3.json"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    params = generator.load_params(spec_path)
    result = generator.build_model(params)
    checks: list[dict[str, Any]] = []

    revision = str(spec["project"]["revision"])
    workflow = spec["workflow"]
    gate_evidence = {
        "project_revision": revision,
        "requirements_status": workflow["requirements_approval"]["status"],
        "requirements_revision": str(workflow["requirements_approval"]["spec_revision"]),
        "concept_status": workflow["concept_approval"]["status"],
        "concept_revision": str(workflow["concept_approval"]["spec_revision"]),
    }
    gates_current = (
        gate_evidence["requirements_status"] == "approved"
        and gate_evidence["requirements_revision"] == revision
        and gate_evidence["concept_status"] == "approved"
        and gate_evidence["concept_revision"] == revision
    )
    add_check(checks, "workflow-gates-current", gates_current, gate_evidence)

    configured_geometry_revision = spec["production_parameters"]["geometry_revision"]
    revision_evidence = {
        "spec": configured_geometry_revision,
        "generator": generator.GEOMETRY_REVISION,
        "manifest": manifest.get("geometry_revision"),
        "manifest_status": manifest.get("status"),
    }
    revision_current = (
        configured_geometry_revision
        == generator.GEOMETRY_REVISION
        == manifest.get("geometry_revision")
        and manifest.get("status") == "DRAFT"
    )
    add_check(checks, "draft-revision-consistency", revision_current, revision_evidence)

    expected_params = json_normalized(asdict(params))
    add_check(
        checks,
        "manifest-parameters-current",
        manifest.get("parameters") == expected_params,
        {"matches_generator_parameters": manifest.get("parameters") == expected_params},
    )

    shape_evidence = []
    shapes_valid = True
    for part in [*result.parts, *result.coupons]:
        solid_count = len(part.print_shape.Solids())
        valid = bool(part.print_shape.isValid())
        positive_volume = float(part.print_shape.Volume()) > 0.0
        passed = valid and solid_count == 1 and positive_volume
        shapes_valid = shapes_valid and passed
        shape_evidence.append(
            {
                "part": part.name,
                "valid": valid,
                "solids": solid_count,
                "positive_volume": positive_volume,
                "bounds_mm": shape_bounds(part.print_shape),
            }
        )
    add_check(checks, "brep-single-solid-parts", shapes_valid, shape_evidence)

    body_names = ("body_bottom", "body_middle", "body_top")
    gauge_results = []
    gauges_clear = True
    gauge_base_y = params.back_thickness + params.rear_clearance
    for index in range(5):
        center_z = params.output_rest_center_z + index * params.gauge_diameter
        gauge = generator.cylinder(
            params.gauge_diameter / 2.0,
            params.gauge_width,
            (0.0, gauge_base_y, center_z),
            (0.0, 1.0, 0.0),
        )
        intersections = {
            name: round(
                abs(result.assembly_shapes[name].intersect(gauge).Volume()),
                6,
            )
            for name in body_names
        }
        total = round(sum(intersections.values()), 6)
        clear = total <= INTERSECTION_TOLERANCE_MM3
        gauges_clear = gauges_clear and clear
        gauge_results.append(
            {
                "position": index + 1,
                "center_z_mm": round(center_z, 6),
                "axis": "+Y",
                "base_y_mm": round(gauge_base_y, 3),
                "diameter_mm": params.gauge_diameter,
                "width_mm": params.gauge_width,
                "intersection_mm3": intersections,
                "total_intersection_mm3": total,
                "clear": clear,
            }
        )
    add_check(checks, "five-position-rigid-roll-gauges", gauges_clear, gauge_results)

    seam_results = []
    seams_clear = True
    for lower, upper in (("body_bottom", "body_middle"), ("body_middle", "body_top")):
        overlap = round(
            abs(result.assembly_shapes[lower].intersect(result.assembly_shapes[upper]).Volume()),
            6,
        )
        clear = overlap <= INTERSECTION_TOLERANCE_MM3
        seams_clear = seams_clear and clear
        seam_results.append(
            {
                "pair": [lower, upper],
                "positive_volume_intersection_mm3": overlap,
                "clear": clear,
            }
        )
    add_check(checks, "assembled-module-seams", seams_clear, seam_results)

    envelope_names = (
        "body_bottom",
        "body_middle",
        "body_top",
        "skin_bottom",
        "gold_bottom",
        "skin_middle",
        "gold_middle",
        "skin_top",
        "gold_top",
    )
    envelope_bounds, envelope_extents = combined_bounds(
        result.assembly_shapes[name] for name in envelope_names
    )
    target = spec["dimensions"]["proposed_envelope_target_mm"]
    envelope_pass = (
        envelope_extents[0] <= float(target["width_without_accessory_max"]) + METRIC_TOLERANCE_MM
        and envelope_extents[1] <= float(target["depth_max"]) + METRIC_TOLERANCE_MM
        and envelope_extents[2]
        <= float(target["height_without_optional_crown_max"]) + METRIC_TOLERANCE_MM
    )
    add_check(
        checks,
        "approved-base-envelope",
        envelope_pass,
        {
            "bounds_mm": envelope_bounds,
            "extents_mm": envelope_extents,
            "maximum_mm": [
                float(target["width_without_accessory_max"]),
                float(target["depth_max"]),
                float(target["height_without_optional_crown_max"]),
            ],
        },
    )

    crown_bounds = result.assembly_shapes["crown_optional"].BoundingBox()
    crown_top_z = crown_bounds.zmax
    crown_height_pass = crown_top_z <= (
        params.total_body_height + params.crown_height + METRIC_TOLERANCE_MM
    )
    add_check(
        checks,
        "optional-crown-height",
        crown_height_pass,
        {
            "body_top_z_mm": round(params.total_body_height, 3),
            "crown_top_z_mm": round(crown_top_z, 3),
            "maximum_crown_top_z_mm": round(params.total_body_height + params.crown_height, 3),
        },
    )

    mount_clearance = gauge_base_y - params.wall_boss_depth
    gauge_front_y = gauge_base_y + params.gauge_width
    nose_start_y = gauge_front_y + 0.3
    nose_length = params.front_y - nose_start_y
    local_clearances = {
        "wall_boss_to_gauge_axial_mm": round(mount_clearance, 3),
        "parked_gauge_to_output_nose_axial_mm": round(nose_start_y - gauge_front_y, 3),
        "output_nose_axial_length_mm": round(nose_length, 3),
    }
    add_check(
        checks,
        "candidate-02-local-clearances",
        mount_clearance >= 0.3 - METRIC_TOLERANCE_MM
        and nose_start_y - gauge_front_y >= 0.3 - METRIC_TOLERANCE_MM
        and nose_length >= 1.2,
        local_clearances,
    )

    manifest_parts = {item["name"]: item for item in manifest.get("parts", [])}
    export_evidence = []
    exports_valid = len(manifest_parts) == len(result.parts) + len(result.coupons)
    build_volume = np.asarray(spec["printer"]["build_volume_mm"], dtype=float)
    for part in [*result.parts, *result.coupons]:
        item = manifest_parts.get(part.name)
        if item is None:
            exports_valid = False
            export_evidence.append({"part": part.name, "error": "missing from manifest"})
            continue
        stl_path = project_root / item["stl"]
        step_path = project_root / item["step"]
        files_exist = stl_path.is_file() and step_path.is_file()
        if not files_exist:
            exports_valid = False
            export_evidence.append({"part": part.name, "files_exist": False})
            continue
        mesh = trimesh.load_mesh(stl_path, force="mesh", process=True)
        components = len(mesh.split(only_watertight=False))
        extents = np.asarray(mesh.extents, dtype=float)
        sha_matches = file_sha256(stl_path) == item["sha256_stl"]
        metrics_match = (
            int(len(mesh.faces)) == int(item["triangles"])
            and bool(mesh.is_watertight) == bool(item["watertight"])
            and bool(mesh.is_volume) == bool(item["is_volume"])
            and components == int(item["components"])
        )
        part_pass = (
            sha_matches
            and metrics_match
            and mesh.is_watertight
            and mesh.is_volume
            and components == 1
            and bool(np.all(extents <= build_volume + METRIC_TOLERANCE_MM))
        )
        exports_valid = exports_valid and part_pass
        export_evidence.append(
            {
                "part": part.name,
                "sha256_matches_manifest": sha_matches,
                "metrics_match_manifest": metrics_match,
                "vertices": int(len(mesh.vertices)),
                "triangles": int(len(mesh.faces)),
                "file_bytes": stl_path.stat().st_size,
                "watertight": bool(mesh.is_watertight),
                "is_volume": bool(mesh.is_volume),
                "components": components,
                "bounds_mm": np.round(mesh.bounds, 3).tolist(),
                "extents_mm": np.round(extents, 3).tolist(),
                "volume_mm3": round(abs(float(mesh.volume)), 3),
                "surface_area_mm2": round(float(mesh.area), 3),
                "fits_provisional_build_volume": bool(
                    np.all(extents <= build_volume + METRIC_TOLERANCE_MM)
                ),
            }
        )
    add_check(checks, "draft-export-manifest-integrity", exports_valid, export_evidence)

    passed = all(check["status"] == "PASS" for check in checks)
    return {
        "project": spec["project"]["id"],
        "spec_revision": revision,
        "geometry_revision": generator.GEOMETRY_REVISION,
        "artifact_status": "DRAFT",
        "validation_level": "V0 source and V1 digital geometry only",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "not_validated": [
            "exact slicer behavior or toolpaths",
            "continuous roll descent and removal motion",
            "physical roll variation, FIFO cycles, paper snagging or double release",
            "module-joint, decorative-inlay or heat-set-insert coupon fit",
            "wall substrate, anchors, installed proof load or long-term creep",
            "cleaning, bathroom exposure or optional accessory retention",
            "watermark integration or final release approval",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "validation" / "digital-validation-r3.json",
    )
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = validate(args.project_root.resolve())
    if not args.no_write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "geometry_revision": report["geometry_revision"],
                "checks": {item["id"]: item["status"] for item in report["checks"]},
                "report": None if args.no_write else str(args.output),
            },
            indent=2,
        )
    )
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
