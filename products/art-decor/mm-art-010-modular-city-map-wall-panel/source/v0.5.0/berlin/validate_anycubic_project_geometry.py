#!/usr/bin/env python3
"""Validate geometry stored through Anycubic production-extension components."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
import trimesh

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PRODUCTION = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
NS = {"m": CORE, "p": PRODUCTION}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix(value: str | None) -> np.ndarray:
    result = np.eye(4, dtype=np.float64)
    if value is None:
        return result
    fields = [float(item) for item in value.split()]
    if len(fields) != 12:
        raise ValueError(f"3MF transform requires 12 fields, got {len(fields)}")
    result[:3, :4] = np.asarray(fields, dtype=np.float64).reshape(4, 3).T
    return result


def parse_mesh(obj: ET.Element) -> tuple[np.ndarray, np.ndarray]:
    vertices_element = obj.find("m:mesh/m:vertices", NS)
    triangles_element = obj.find("m:mesh/m:triangles", NS)
    if vertices_element is None or triangles_element is None:
        raise ValueError(f"object {obj.get('id')} contains no mesh")
    vertices = np.asarray(
        [
            [float(vertex.get(axis, "nan")) for axis in ("x", "y", "z")]
            for vertex in vertices_element.findall("m:vertex", NS)
        ],
        dtype=np.float64,
    )
    faces = np.asarray(
        [
            [int(triangle.get(axis, "-1")) for axis in ("v1", "v2", "v3")]
            for triangle in triangles_element.findall("m:triangle", NS)
        ],
        dtype=np.int64,
    )
    return vertices, faces


def metric_mesh(vertices: np.ndarray, faces: np.ndarray) -> tuple[trimesh.Trimesh, dict]:
    indices_valid = bool(
        len(vertices) > 0
        and len(faces) > 0
        and np.isfinite(vertices).all()
        and faces.min() >= 0
        and faces.max() < len(vertices)
    )
    if not indices_valid:
        return trimesh.Trimesh(), {
            "vertices": int(len(vertices)),
            "triangles": int(len(faces)),
            "indices_valid": False,
        }
    unique_vertices, inverse = np.unique(vertices, axis=0, return_inverse=True)
    mesh = trimesh.Trimesh(
        vertices=unique_vertices, faces=inverse[faces], process=False
    )
    mesh.remove_unreferenced_vertices()
    edge_counts = np.bincount(
        mesh.edges_unique_inverse, minlength=len(mesh.edges_unique)
    )
    metrics = {
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "indices_valid": True,
        "watertight": bool(mesh.is_watertight),
        "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
        "connected_components": int(len(mesh.split(only_watertight=False))),
        "boundary_edges": int(np.count_nonzero(edge_counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(edge_counts > 2)),
        "volume_mm3": float(mesh.volume),
        "bounds_mm": np.asarray(mesh.bounds, dtype=float).tolist(),
    }
    return mesh, metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-3mf", type=Path, required=True)
    parser.add_argument("--packaging-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.output}")
    required = [args.project_3mf, args.packaging_report]
    missing = [str(path) for path in required if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise SystemExit(f"missing or empty input(s): {missing}")

    package = json.loads(args.packaging_report.read_text())
    with zipfile.ZipFile(args.project_3mf) as archive:
        members = set(archive.namelist())
        root_name = "3D/3dmodel.model"
        if root_name not in members:
            raise SystemExit("native project has no 3D/3dmodel.model")
        root = ET.fromstring(archive.read(root_name))
        item = root.find("m:build/m:item", NS)
        if item is None:
            raise SystemExit("native project has no build item")
        build_transform = matrix(item.get("transform"))
        build_object_id = item.get("objectid")
        build_object = root.find(f"m:resources/m:object[@id='{build_object_id}']", NS)
        if build_object is None:
            raise SystemExit("native project build object is missing")
        components = build_object.findall("m:components/m:component", NS)
        resolved = []
        for component in components:
            reference = component.get(f"{{{PRODUCTION}}}path")
            if not reference:
                raise SystemExit("component has no production-extension path")
            member = reference.lstrip("/")
            if member not in members:
                raise SystemExit(f"component target is missing: {member}")
            model = ET.fromstring(archive.read(member))
            object_id = component.get("objectid")
            obj = model.find(f"m:resources/m:object[@id='{object_id}']", NS)
            if obj is None:
                raise SystemExit(f"component object {object_id} is missing from {member}")
            vertices, faces = parse_mesh(obj)
            mesh, metrics = metric_mesh(vertices, faces)
            component_transform = matrix(component.get("transform"))
            world = build_transform @ component_transform
            global_vertices = trimesh.transform_points(vertices, world)
            metrics["component_path"] = member
            metrics["component_object_id"] = int(object_id)
            metrics["global_bounds_mm"] = [
                np.min(global_vertices, axis=0).tolist(),
                np.max(global_vertices, axis=0).tolist(),
            ]
            resolved.append((mesh, metrics))
        model_settings = archive.read("Metadata/model_settings.config").decode("utf-8")
        extruders = [
            int(value)
            for value in re.findall(r'key="extruder" value="(\d+)"', model_settings)
        ]

    source_parts = package["source_parts"]
    component_reports = []
    for index, ((_, metrics), source) in enumerate(
        zip(resolved, source_parts, strict=False), start=1
    ):
        source_mesh = source["mesh"]
        volume_delta = abs(metrics.get("volume_mm3", 0.0) - source_mesh["volume_mm3"])
        volume_limit = max(0.001, abs(source_mesh["volume_mm3"]) * 1e-5)
        expected_global = np.asarray(source_mesh["bounds_mm"], dtype=float)
        expected_global += np.asarray(package["normalization"]["build_translation_mm"])
        global_bounds = np.asarray(metrics.get("global_bounds_mm", [[0] * 3, [0] * 3]))
        checks = {
            "nonempty_mesh": metrics.get("vertices", 0) > 0 and metrics.get("triangles", 0) > 0,
            "indices_valid": metrics.get("indices_valid") is True,
            "watertight": metrics.get("watertight") is True,
            "positive_volume": metrics.get("positive_volume") is True,
            "triangle_count_matches_source": metrics.get("triangles") == source_mesh["triangles"],
            "volume_matches_source": volume_delta <= volume_limit,
            "global_bounds_match_source_placement": bool(
                np.allclose(global_bounds, expected_global, atol=2e-4, rtol=0.0)
            ),
        }
        component_reports.append(
            {
                "tool": index,
                "source": source,
                "metrics": metrics,
                "expected_global_bounds_mm": expected_global.tolist(),
                "volume_delta_mm3": volume_delta,
                "volume_tolerance_mm3": volume_limit,
                "checks": checks,
                "status": "PASS" if all(checks.values()) else "FAIL",
            }
        )

    checks = {
        "project_hash_matches_packaging_report": sha256(args.project_3mf)
        == package["output"]["sha256"],
        "packaging_report_passed": package.get("status") == "PASS",
        "four_component_references": len(resolved) == 4,
        "four_source_parts": len(source_parts) == 4,
        "extruder_assignments_1_through_4": extruders == [1, 2, 3, 4],
        "all_referenced_meshes_pass": len(component_reports) == 4
        and all(item["status"] == "PASS" for item in component_reports),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.0",
        "candidate": package.get("candidate"),
        "mode": package.get("mode"),
        "half": package.get("half"),
        "status": status,
        "scope": "vendor-aware 3MF geometry validation following production-extension component paths",
        "inputs": {
            "project_3mf": {
                "path": str(args.project_3mf.resolve()),
                "bytes": args.project_3mf.stat().st_size,
                "sha256": sha256(args.project_3mf),
            },
            "packaging_report": {
                "path": str(args.packaging_report.resolve()),
                "sha256": sha256(args.packaging_report),
            },
        },
        "checks": checks,
        "extruder_assignments": extruders,
        "totals": {
            "components": len(resolved),
            "vertices": sum(item[1].get("vertices", 0) for item in resolved),
            "triangles": sum(item[1].get("triangles", 0) for item in resolved),
            "volume_mm3": sum(item[1].get("volume_mm3", 0.0) for item in resolved),
        },
        "components": component_reports,
        "interpretation": "A PASS proves that all four native Anycubic component references resolve to nonempty watertight meshes matching the authored STL triangle count, volume and placed bounds; it directly covers right-half geometry presence.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(args.output), "totals": report["totals"]}))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
