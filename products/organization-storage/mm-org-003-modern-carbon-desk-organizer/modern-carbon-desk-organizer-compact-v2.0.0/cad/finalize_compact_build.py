#!/usr/bin/env python3
"""Finalize isolated MM-ORG-003 part builds without importing CadQuery."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = ROOT / "model-parameters.json"
SOURCE = ROOT / "cad" / "build_compact_organizer.py"
VALIDATION = ROOT / "validation"
REPORTS = ROOT / "reports"
MASTER = ROOT / "exports" / "master"
THREE_MF = ROOT / "exports" / "3mf"
PROJECT_ID = "MM-ORG-003"
REVISION = "2.0.0-draft.2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def report(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations: list[str] | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": "2.0.0",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks if item["required"]) else "FAIL",
        "profile": "draft",
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}
            for path in inputs
        ],
        "checks": checks,
        "metrics": metrics,
        "limitations": limitations or [],
        "required_capabilities": [],
    }


def add_zip_member(archive: zipfile.ZipFile, name: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, payload)


def write_print_set_3mf(path: Path, parts: list[tuple[str, Path, int]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    for name, value in (
        ("Title", "DRAFT MM-ORG-003 Modern Carbon Compact print set"),
        ("Designer", "metriMade / autonomous CAD workflow"),
        ("Description", "Four inventory-strip build items; place each unique part on a separate 220 mm plate and print the drawer twice."),
        ("LicenseTerms", "DRAFT engineering artifact; not a commercial release"),
    ):
        metadata = ET.SubElement(model, f"{{{ns}}}metadata", {"name": name})
        metadata.text = value
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    inventory_x = 0.0
    for object_id, (name, mesh_path, quantity) in enumerate(parts, start=1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        if not isinstance(mesh, trimesh.Trimesh) or not mesh.is_watertight or mesh.volume <= 0:
            raise RuntimeError(f"invalid 3MF source: {mesh_path}")
        obj = ET.SubElement(
            resources,
            f"{{{ns}}}object",
            {"id": str(object_id), "type": "model", "name": name, "partnumber": f"{PROJECT_ID}-{REVISION}-{name}"},
        )
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices_node = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices_node, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles_node = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(triangles_node, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        for _ in range(quantity):
            transform = f"1 0 0 0 1 0 0 0 1 {inventory_x:.3f} 0 0"
            ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": transform})
            inventory_x += float(mesh.extents[0]) + 12.0
    model_bytes = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        add_zip_member(archive, "[Content_Types].xml", content_types)
        add_zip_member(archive, "_rels/.rels", rels)
        add_zip_member(archive, "3D/3dmodel.model", model_bytes)
        add_zip_member(archive, "Metadata/model-parameters.json", PARAMS.read_bytes())


def main() -> None:
    p = json.loads(PARAMS.read_text(encoding="utf-8"))
    names = ("housing", "drawer", "sorter", "fit_coupon", "texture_coupon")
    part_reports = {}
    for name in names:
        path = VALIDATION / f"isolated-{name}-build.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("status") != "PASS":
            raise RuntimeError(f"part report is not PASS: {path}")
        part_reports[name] = payload
    artifacts = {name: part_reports[name]["metrics"] for name in names}

    width = float(p["housing"]["width"])
    drawer_width = float(p["drawer"]["body_width"])
    housing_bottom = float(p["housing"]["bottom"])
    opening_height = float(p["housing"]["opening_height"])
    shelf = float(p["housing"]["shelf"])
    housing_height = float(p["housing"]["height"])

    assembly_meshes: list[trimesh.Trimesh] = []
    for name in ("housing", "drawer", "sorter"):
        mesh = trimesh.load_mesh(ROOT / artifacts[name]["assembly_source_stl"], force="mesh", process=True)
        if name == "drawer":
            for z in (housing_bottom + 0.25, housing_bottom + opening_height + shelf + 0.25):
                placed = mesh.copy()
                placed.apply_translation(((width - drawer_width) / 2.0, 0.0, z))
                assembly_meshes.append(placed)
        elif name == "sorter":
            mesh.apply_translation((0.0, 0.0, housing_height))
            assembly_meshes.append(mesh)
        else:
            assembly_meshes.append(mesh)
    assembly = trimesh.util.concatenate(assembly_meshes)
    assembly_preview = MASTER / f"DRAFT-MM-ORG-003-compact-assembly-preview-{REVISION}.stl"
    assembly.export(assembly_preview)
    assembly_extents = np.round(assembly.extents, 5).tolist()

    print_set = THREE_MF / f"DRAFT-MM-ORG-003-modern-carbon-compact-{REVISION}.3mf"
    write_print_set_3mf(
        print_set,
        [
            ("housing", ROOT / artifacts["housing"]["manufacturing_stl"], 1),
            ("drawer", ROOT / artifacts["drawer"]["manufacturing_stl"], 2),
            ("sorter", ROOT / artifacts["sorter"]["manufacturing_stl"], 1),
        ],
    )

    production = ("housing", "drawer", "sorter")
    selected_volume = sum(artifacts[name]["mesh"]["volume_mm3"] * (2 if name == "drawer" else 1) for name in production)
    compact_baseline_volume = sum(float(artifacts[name]["baseline_volume_mm3"]) * (2 if name == "drawer" else 1) for name in production)
    dense_baseline_triangles = 1467224 + 2 * 239554 + 1012370
    selected_triangles = sum(artifacts[name]["mesh"]["triangles"] * (2 if name == "drawer" else 1) for name in production)
    optimization = report(
        "MM-ORG-003-optimization-comparison",
        [PARAMS, SOURCE],
        [
            check("common-printer", all(next(item for item in part_reports[name]["checks"] if item["id"] == "build-volume")["status"] == "PASS" for name in production), "All production parts fit 220 x 220 x 250 mm"),
            check("mesh-burden", selected_triangles < dense_baseline_triangles, "Procedural candidate reduces stored manufacturing triangle burden"),
            check("protected-contract", (ROOT / "protected-geometry-map.md").is_file(), "Protected geometry map is present"),
        ],
        {
            "selection": "C — compact geometry plus procedural twill",
            "v1_1_2_dense_triangles_job": dense_baseline_triangles,
            "selected_triangles_job": selected_triangles,
            "triangle_burden_reduction_percent": 100.0 * (dense_baseline_triangles - selected_triangles) / dense_baseline_triangles,
            "compact_untextured_volume_mm3": compact_baseline_volume,
            "selected_textured_volume_mm3": selected_volume,
            "compact_volume_reduction_percent": 100.0 * (compact_baseline_volume - selected_volume) / compact_baseline_volume,
            "estimated_pla_mass_g_at_1_24": selected_volume / 1000.0 * 1.24,
            "exact_slicer_metrics": "NOT_RUN",
        },
        ["No exact slicer CLI/profile is installed; no print-time or deposited-material savings percentage is claimed."],
    )
    write_json(REPORTS / "optimization-comparison.json", optimization)

    side_clearance = (width - 2.0 * float(p["housing"]["side_wall"]) - drawer_width) / 2.0
    depth_stack = float(p["drawer"]["body_depth"]) + float(p["drawer"]["rear_clearance"])
    cavity_depth = float(p["housing"]["depth"]) - float(p["housing"]["rear_wall"])
    wall_reserve = min(float(p["housing"]["side_wall"]), float(p["sorter"]["outer_wall"]), float(p["drawer"]["front_depth"])) - float(p["texture"]["groove_depth"])
    source_report = report(
        "MM-ORG-003-parametric-source",
        [PARAMS, SOURCE],
        [
            check("part-reports", all(part_reports[name]["status"] == "PASS" for name in names), "All isolated deterministic part builds pass"),
            check("assembly-envelope", all(math.isclose(a, b, abs_tol=0.05) for a, b in zip(assembly_extents, [width, float(p["housing"]["depth"]) + float(p["drawer"]["front_depth"]), housing_height + float(p["sorter"]["height"])])), "Assembly envelope includes the proud drawer fascia", {"extents_mm": assembly_extents}),
            check("side-clearance", math.isclose(side_clearance, 0.45, abs_tol=1e-9), "Drawer side clearance is 0.45 mm per side", {"clearance_mm": side_clearance}),
            check("depth-stack", math.isclose(depth_stack, cavity_depth, abs_tol=1e-9), "Drawer body/rear-clearance depth stack closes exactly", {"depth_stack_mm": depth_stack, "cavity_depth_mm": cavity_depth}),
            check("wall-reserve", wall_reserve >= 1.76, "Texture host wall reserve is at least 1.76 mm", {"reserve_mm": wall_reserve}),
            check("print-set", print_set.is_file(), "DRAFT 3MF print set exists"),
        ],
        {"parts": artifacts, "assembly_extents_mm": assembly_extents},
        ["Exact slicer and physical validation are deferred."],
    )
    write_json(VALIDATION / "parametric-source-report.json", source_report)
    if source_report["status"] != "PASS":
        raise RuntimeError("aggregate source contract failed")

    manifest = {
        "project_id": PROJECT_ID,
        "revision": REVISION,
        "status": "DRAFT",
        "parameters_sha256": sha256(PARAMS),
        "source_sha256": sha256(SOURCE),
        "parts": artifacts,
        "assembly_preview_stl": str(assembly_preview.relative_to(ROOT)),
        "assembly_preview_stl_sha256": sha256(assembly_preview),
        "print_set_3mf": str(print_set.relative_to(ROOT)),
        "print_set_3mf_sha256": sha256(print_set),
        "print_set_note": "Inventory strip; place each unique part on a separate 220 mm plate and print drawer twice.",
        "physical_validation": "DEFERRED",
    }
    write_json(REPORTS / "build-manifest.json", manifest)
    print(json.dumps({"status": "PASS", "assembly_extents_mm": assembly_extents, "print_set": str(print_set)}, indent=2))


if __name__ == "__main__":
    main()
