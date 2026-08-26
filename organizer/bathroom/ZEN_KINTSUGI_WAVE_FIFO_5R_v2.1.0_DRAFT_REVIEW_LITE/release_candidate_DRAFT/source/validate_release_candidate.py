#!/usr/bin/env python3
"""Independently validate the ZEN KINTSUGI WAVE DRAFT release candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parent.parent
STL_DIR = ROOT / "STL"
THREEMF_DIR = ROOT / "3MF"
REPORT_DIR = ROOT / "reports"
MANIFEST = ROOT / "manifest_DRAFT.json"
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def as_mesh(value) -> trimesh.Trimesh:
    if isinstance(value, trimesh.Scene):
        return trimesh.util.concatenate(tuple(value.geometry.values()))
    if not isinstance(value, trimesh.Trimesh):
        raise TypeError(f"Expected Trimesh, received {type(value)!r}")
    return value


def mesh_metrics(mesh: trimesh.Trimesh) -> dict:
    components = mesh.split(only_watertight=False)
    return {
        "triangles": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "components": int(len(components)),
        "volume_mm3": float(abs(mesh.volume)),
        "bounds_mm": np.round(mesh.bounds, 6).tolist(),
    }


def validate_stls(expected: dict) -> tuple[list[dict], bool]:
    results: list[dict] = []
    passed = True
    for path in sorted(STL_DIR.glob("*.stl")):
        mesh = as_mesh(trimesh.load_mesh(path, process=True))
        metrics = mesh_metrics(mesh)
        expected_entry = expected.get(path.name, {})
        expected_components = expected_entry.get("components")
        checks = {
            "watertight": metrics["watertight"],
            "winding_consistent": metrics["winding_consistent"],
            "positive_volume": metrics["is_volume"] and metrics["volume_mm3"] > 0,
            "component_count": expected_components is None or metrics["components"] == expected_components,
        }
        entry = {
            "file": path.name,
            "sha256": sha256(path),
            **metrics,
            "expected_components": expected_components,
            "checks": checks,
            "passed": all(checks.values()),
        }
        (REPORT_DIR / f"mesh_{path.stem}.json").write_text(
            json.dumps(entry, indent=2), encoding="utf-8"
        )
        results.append(entry)
        passed = passed and entry["passed"]
    return results, passed and len(results) == 22


def parse_3mf(path: Path) -> dict:
    with ZipFile(path) as archive:
        corrupt_member = archive.testzip()
        names = sorted(archive.namelist())
        model_data = archive.read("3D/3dmodel.model")
    root = ET.fromstring(model_data)
    ns = {"m": CORE_NS}
    bases = root.findall(".//m:basematerials/m:base", ns)
    objects = root.findall(".//m:resources/m:object", ns)
    build_items = root.findall(".//m:build/m:item", ns)
    object_reports = []
    material_indices = set()
    for obj in objects:
        vertices = np.array(
            [[float(v.attrib[axis]) for axis in ("x", "y", "z")]
             for v in obj.findall("./m:mesh/m:vertices/m:vertex", ns)],
            dtype=float,
        )
        faces = np.array(
            [[int(t.attrib[key]) for key in ("v1", "v2", "v3")]
             for t in obj.findall("./m:mesh/m:triangles/m:triangle", ns)],
            dtype=np.int64,
        )
        if len(vertices) == 0 or len(faces) == 0:
            metrics = {"triangles": 0, "vertices": 0, "watertight": False,
                       "winding_consistent": False, "is_volume": False,
                       "components": 0, "volume_mm3": 0.0, "bounds_mm": []}
        else:
            metrics = mesh_metrics(trimesh.Trimesh(vertices=vertices, faces=faces, process=False))
        pindex = int(obj.attrib.get("pindex", "-1"))
        material_indices.add(pindex)
        object_reports.append({
            "id": int(obj.attrib["id"]),
            "name": obj.attrib.get("name", ""),
            "material_index": pindex,
            **metrics,
            "passed": metrics["watertight"] and metrics["winding_consistent"]
                      and metrics["is_volume"] and metrics["volume_mm3"] > 0,
        })
    checks = {
        "zip_crc": corrupt_member is None,
        "required_members": {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}.issubset(names),
        "four_materials": len(bases) == 4,
        "material_indices": material_indices == set(range(4)),
        "unique_object_names": len({o["name"] for o in object_reports}) == len(object_reports),
        "all_meshes_pass": bool(object_reports) and all(o["passed"] for o in object_reports),
        "build_items_present": len(build_items) > 0,
    }
    return {
        "file": path.name,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "materials": [
            {"name": b.attrib.get("name"), "displaycolor": b.attrib.get("displaycolor")}
            for b in bases
        ],
        "objects": object_reports,
        "build_item_count": len(build_items),
        "members": names,
        "checks": checks,
        "passed": all(checks.values()),
    }


def validate_3mfs() -> tuple[list[dict], bool]:
    reports = []
    passed = True
    for path in sorted(THREEMF_DIR.glob("*.3mf")):
        report = parse_3mf(path)
        (REPORT_DIR / f"3mf_{path.stem}.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        reports.append(report)
        passed = passed and report["passed"]
    return reports, passed and len(reports) == 5


def validate_sources() -> dict:
    results = {}
    for path in sorted((ROOT / "source").glob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            results[path.name] = "PASS"
        except SyntaxError as error:
            results[path.name] = f"FAIL: {error}"
    return results


def write_manifest() -> dict:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        files.append({
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {"version": "2.1.0-DRAFT", "files": files}
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    validation_path = REPORT_DIR / "validation_report_DRAFT.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    stls, stl_pass = validate_stls(validation.get("topology", {}))
    threemfs, threemf_pass = validate_3mfs()
    source_checks = validate_sources()
    watermark = json.loads(
        (REPORT_DIR / "watermark" / "watermark_validation_DRAFT.json").read_text(encoding="utf-8")
    )
    fifo = validation.get("fifo", {})
    checks = {
        "source_syntax": all(value == "PASS" for value in source_checks.values()),
        "stl_count_22": len(stls) == 22,
        "all_stls_pass": stl_pass,
        "3mf_count_5": len(threemfs) == 5,
        "all_3mfs_pass": threemf_pass,
        "fifo_121_positions_zero_collisions": fifo.get("positions_tested") == 121 and fifo.get("collision_count") == 0,
        "wall_thickness_pass": bool(validation.get("wall_thickness", {}).get("passed")),
        "bed_fit_pass": bool(validation.get("envelope", {}).get("all_individual_parts_fit")),
        "optimization_pass": bool(validation.get("optimization", {}).get("passed")),
        "watermark_topology": watermark.get("watertight") is True and watermark.get("winding_consistent") is True,
        "watermark_reading_orientation": watermark.get("rotation_deg") == 0.0,
        "watermark_residual_wall": watermark.get("residual_host_wall_mm", 0) >= 4.8,
    }
    report = {
        "status": "PASS-DIGITAL-DRAFT" if all(checks.values()) else "FAIL",
        "checks": checks,
        "source_checks": source_checks,
        "stl_files": len(stls),
        "3mf_files": len(threemfs),
        "3mf_object_counts": {item["file"]: len(item["objects"]) for item in threemfs},
        "3mf_build_item_counts": {item["file"]: item["build_item_count"] for item in threemfs},
        "remaining_release_gates": [
            "Anycubic Slicer Next layer/toolpath review",
            "explicit user approval of the current model and marking after the slicer evidence passes",
            "physical fit, texture, FIFO, and wall-mount tests",
        ],
    }
    (REPORT_DIR / "release-regression-DRAFT.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    manifest = write_manifest()
    report["manifest_entries"] = len(manifest["files"])
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS-DIGITAL-DRAFT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
