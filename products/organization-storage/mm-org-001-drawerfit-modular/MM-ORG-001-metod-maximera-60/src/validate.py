#!/usr/bin/env python3
"""Fail-closed digital validation for MM-ORG-001 DRAFT geometry and package."""

from __future__ import annotations

import json
import math
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parent.parent
TOL = 1.0e-4


def finite_list(values: np.ndarray) -> list[float]:
    return [float(value) for value in values]


def validate_mesh(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, process=True, validate=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"expected one mesh in {path}")
    areas = np.asarray(mesh.area_faces)
    components = mesh.split(only_watertight=False)
    checks = {
        "finite_vertices": bool(np.isfinite(mesh.vertices).all()),
        "positive_volume": bool(mesh.volume > 1.0),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "single_connected_body": len(components) == 1,
        "no_degenerate_faces": bool(np.all(areas > 1.0e-10)),
    }
    return {
        "file": str(path.relative_to(ROOT)),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "bounds_min_mm": finite_list(mesh.bounds[0]),
        "bounds_max_mm": finite_list(mesh.bounds[1]),
        "size_mm": finite_list(mesh.extents),
        "volume_mm3": float(mesh.volume),
        "connected_bodies": len(components),
        "checks": checks,
        "pass": all(checks.values()),
    }


def validate_3mf(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        required = {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}
        xml = archive.read("3D/3dmodel.model")
    root = ET.fromstring(xml)
    namespace = root.tag.split("}")[0].lstrip("{")
    ns = {"m": namespace}
    objects = root.findall(".//m:resources/m:object", ns)
    items = root.findall(".//m:build/m:item", ns)
    names_in_model = [obj.attrib.get("name", "") for obj in objects]
    checks = {
        "required_package_parts": required.issubset(names),
        "core_namespace": namespace == "http://schemas.microsoft.com/3dmanufacturing/core/2015/02",
        "exactly_ten_objects": len(objects) == 10,
        "exactly_ten_build_items": len(items) == 10,
        "nine_modules": sum(name.startswith("module-r") for name in names_in_model) == 9,
        "one_comb": names_in_model.count("screwdriver-comb") == 1,
        "all_items_have_transform": all("transform" in item.attrib for item in items),
    }
    return {
        "file": str(path.relative_to(ROOT)),
        "objects": names_in_model,
        "object_count": len(objects),
        "build_item_count": len(items),
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> None:
    params = json.loads((ROOT / "config" / "model-params.json").read_text(encoding="utf-8"))
    build = json.loads((ROOT / "reports" / "build-report.json").read_text(encoding="utf-8"))
    modules = []
    global_min = np.array([math.inf, math.inf, math.inf])
    global_max = np.array([-math.inf, -math.inf, -math.inf])
    for item in build["modules"]:
        result = validate_mesh(ROOT / item["manufacturing_file"])
        result["id"] = item["id"]
        translation = np.asarray(item["assembly_translation_mm"], dtype=float)
        global_min = np.minimum(global_min, np.asarray(result["bounds_min_mm"]) + translation)
        global_max = np.maximum(global_max, np.asarray(result["bounds_max_mm"]) + translation)
        result["bed_fit"] = bool(
            result["size_mm"][0] <= params["segmentation"]["usable_bed_x"] + TOL
            and result["size_mm"][1] <= params["segmentation"]["usable_bed_y"] + TOL
        )
        result["pass"] = result["pass"] and result["bed_fit"]
        modules.append(result)

    accessories = {
        name: validate_mesh(ROOT / item["manufacturing_file"])
        for name, item in build["accessories"].items()
    }
    three_mf_path = ROOT / "output" / "DRAFT" / params["export"]["assembly_3mf"]
    three_mf = validate_3mf(three_mf_path)

    expected_max = np.array([
        params["organizer"]["width_x"],
        params["organizer"]["depth_y"],
        params["organizer"]["outer_wall_height"],
    ])
    envelope_checks = {
        "minimum_origin": bool(np.all(np.abs(global_min) <= TOL)),
        "nominal_maximum": bool(np.all(np.abs(global_max - expected_max) <= TOL)),
        "below_release_maximum": bool(
            global_max[0] <= 514.0 + TOL
            and global_max[1] <= 493.0 + TOL
            and global_max[2] <= 50.5 + TOL
        ),
    }
    parameter_checks = {
        "exactly_nine_modules": len(modules) == 9,
        "all_modules_fit_216_bed": all(item["bed_fit"] for item in modules),
        "exactly_eighteen_bins_declared": params["layout"]["hardware_columns"] * params["layout"]["hardware_rows"] == 18,
        "eight_slot_comb_declared": params["comb"]["slot_count"] == 8,
        "minimal_one_connector_per_seam_segment": (
            params["connectors"]["mating_location_count"]
            == (params["segmentation"]["columns"] - 1) * params["segmentation"]["rows"]
            + (params["segmentation"]["rows"] - 1) * params["segmentation"]["columns"]
            == 12
        ),
        "connector_coupon_sweep_includes_draft": params["connectors"]["draft_clearance_per_side"] in params["connectors"]["coupon_clearances_per_side"],
        "watermark_block_respected": params["branding"]["enabled"] is False,
    }
    all_meshes_pass = all(item["pass"] for item in modules) and all(item["pass"] for item in accessories.values())
    digital_pass = all_meshes_pass and all(envelope_checks.values()) and all(parameter_checks.values()) and three_mf["pass"]
    report = {
        "status": "PASS_DRAFT_DIGITAL" if digital_pass else "FAIL",
        "release_status": "BLOCKED_PHYSICAL_AND_SLICER_GATES",
        "geometry_revision": params["geometry_revision"],
        "validator": "Trimesh topology plus deterministic parameter/package checks",
        "modules": modules,
        "accessories": accessories,
        "assembly_envelope_mm": {
            "min": finite_list(global_min),
            "max": finite_list(global_max),
            "size": finite_list(global_max - global_min),
            "checks": envelope_checks,
        },
        "parameter_checks": parameter_checks,
        "three_mf": three_mf,
        "slicer": {
            "status": "NOT_RUN",
            "reason": "No supported slicer executable was found in PATH; exact printer/material profile is unresolved.",
        },
        "physical": {
            "status": "NOT_RUN",
            "required_next": [
                "print connector clearance sweep before any full module",
                "print comb interface gauge and actual comb",
                "measure the exact target drawer and test the fit-corner coupon",
            ],
        },
        "pass": digital_pass,
    }
    destination = ROOT / "reports" / "validation-report.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "modules": len(modules), "accessories": len(accessories), "assembly_size_mm": report["assembly_envelope_mm"]["size"]}))
    if not digital_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
