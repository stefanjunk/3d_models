#!/usr/bin/env python3
"""Validate the vendor-extension geometry of the tools 1/4 coupon 3MF."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
import trimesh


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PREVIOUS = PRODUCT / "source" / "v0.5.0" / "berlin" / "validate_anycubic_project_geometry.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_previous():
    spec = importlib.util.spec_from_file_location("mm_art_010_coupon_validate_v050", PREVIOUS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator: {PREVIOUS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-3mf", type=Path, required=True)
    parser.add_argument("--packaging-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.output}")
    previous = load_previous()
    package = json.loads(args.packaging_report.read_text())
    with zipfile.ZipFile(args.project_3mf) as archive:
        members = set(archive.namelist())
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
        item = root.find("m:build/m:item", previous.NS)
        if item is None:
            raise SystemExit("coupon project has no build item")
        build_transform = previous.matrix(item.get("transform"))
        build_object = root.find(
            f"m:resources/m:object[@id='{item.get('objectid')}']", previous.NS
        )
        if build_object is None:
            raise SystemExit("coupon project build object is missing")
        resolved = []
        for component in build_object.findall("m:components/m:component", previous.NS):
            reference = component.get(f"{{{previous.PRODUCTION}}}path")
            if not reference or reference.lstrip("/") not in members:
                raise SystemExit("coupon component target is missing")
            member = reference.lstrip("/")
            model = ET.fromstring(archive.read(member))
            object_id = component.get("objectid")
            obj = model.find(f"m:resources/m:object[@id='{object_id}']", previous.NS)
            if obj is None:
                raise SystemExit("coupon component object is missing")
            vertices, faces = previous.parse_mesh(obj)
            _, metrics = previous.metric_mesh(vertices, faces)
            world = build_transform @ previous.matrix(component.get("transform"))
            global_vertices = trimesh.transform_points(vertices, world)
            metrics["component_path"] = member
            metrics["global_bounds_mm"] = [
                np.min(global_vertices, axis=0).tolist(),
                np.max(global_vertices, axis=0).tolist(),
            ]
            resolved.append(metrics)
        model_settings = archive.read("Metadata/model_settings.config").decode("utf-8")
        extruders = [
            int(value)
            for value in re.findall(r'key="extruder" value="(\d+)"', model_settings)
        ]

    components = []
    translation = np.asarray(package["normalization"]["build_translation_mm"])
    for metrics, source in zip(resolved, package["source_parts"], strict=True):
        expected_bounds = np.asarray(source["mesh"]["bounds_mm"], dtype=float) + translation
        actual_bounds = np.asarray(metrics["global_bounds_mm"], dtype=float)
        volume_delta = abs(metrics["volume_mm3"] - source["mesh"]["volume_mm3"])
        checks = {
            "nonempty": metrics["vertices"] > 0 and metrics["triangles"] > 0,
            "watertight": metrics["watertight"] is True,
            "positive_volume": metrics["positive_volume"] is True,
            "triangle_count_matches": metrics["triangles"] == source["mesh"]["triangles"],
            "volume_matches": volume_delta <= max(0.001, abs(source["mesh"]["volume_mm3"]) * 1e-5),
            "placed_bounds_match": bool(np.allclose(actual_bounds, expected_bounds, atol=2e-4, rtol=0.0)),
        }
        components.append(
            {
                "tool": source["tool"],
                "source": source,
                "metrics": metrics,
                "checks": checks,
                "status": "PASS" if all(checks.values()) else "FAIL",
            }
        )
    checks = {
        "project_hash_matches_packaging_report": sha256(args.project_3mf) == package["output"]["sha256"],
        "packaging_report_passed": package["status"] == "PASS",
        "two_component_references": len(resolved) == 2,
        "tool_assignments_are_1_and_4": extruders == [1, 4],
        "all_referenced_meshes_pass": all(item["status"] == "PASS" for item in components),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.1",
        "candidate": package["candidate"],
        "status": status,
        "scope": "vendor-aware coupon 3MF geometry and product tool assignments",
        "checks": checks,
        "extruder_assignments": extruders,
        "components": components,
        "totals": {
            "components": len(resolved),
            "triangles": sum(item["triangles"] for item in resolved),
            "volume_mm3": sum(item["volume_mm3"] for item in resolved),
        },
        "validator": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256(Path(__file__).resolve()),
            "parser_authority": str(PREVIOUS.resolve()),
            "parser_authority_sha256": sha256(PREVIOUS),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(args.output), "totals": report["totals"]}))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
