#!/usr/bin/env python3
"""Deterministic product build for MM-SYS-002 revision 0.2.0-draft.1."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
from cadquery import exporters
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = ROOT / "model-parameters.json"
SOURCE = Path(__file__).resolve()
SHARED_ROOT = ROOT.parents[1]
sys.path.insert(0, str(SHARED_ROOT))
from systemmoebel_top20.common import cylinder, open_tray, plate, rounded_prism  # noqa: E402


BASELINE_STL = SHARED_ROOT / "exports" / "stl" / "02_bror_tool_shadow_tray.stl"
MASTER = ROOT / "exports" / "master"
MANUFACTURING = ROOT / "exports" / "manufacturing"
THREE_MF = ROOT / "exports" / "3mf"
VALIDATION = ROOT / "validation"
REPORTS = ROOT / "reports"
REVISION = "0.2.0-draft.1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return os.path.relpath(path, ROOT)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def report(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations: list[str] | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": "0.2.0",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks if item["required"]) else "FAIL",
        "profile": "draft",
        "inputs": [{"path": relative(path), "sha256": sha256(path), "size_bytes": path.stat().st_size} for path in inputs],
        "checks": checks,
        "metrics": metrics,
        "limitations": limitations or [],
        "required_capabilities": [],
    }


def rounded_at(size: list[float], center: list[float], height: float, z0: float, radius: float) -> cq.Workplane:
    return rounded_prism(float(size[0]), float(size[1]), height, radius, z0).translate((float(center[0]), float(center[1]), 0.0))


def union(base: cq.Workplane, *parts: cq.Workplane) -> cq.Workplane:
    result = base
    for part in parts:
        result = result.union(part)
    return result.clean()


def build_tray(p: dict) -> cq.Workplane:
    t = p["tray"]
    width = float(t["width"])
    depth = float(t["depth"])
    height = float(t["height"])
    wall = float(t["wall"])
    floor = float(t["floor_ligament"])
    pocket_depth = float(t["pocket_depth"])
    cutter_height = pocket_depth + 1.0
    body = open_tray(width, depth, height, wall, floor + pocket_depth, float(t["corner_radius"]))

    hammer = union(
        rounded_at(p["hammer"]["handle_size"], p["hammer"]["handle_center"], cutter_height, floor, 5.0),
        rounded_at(p["hammer"]["head_size"], p["hammer"]["head_center"], cutter_height, floor, 6.0),
    )
    screwdriver = union(
        rounded_at(p["screwdriver"]["grip_size"], p["screwdriver"]["grip_center"], cutter_height, floor, 8.0),
        rounded_at(p["screwdriver"]["shaft_size"], p["screwdriver"]["shaft_center"], cutter_height, floor, 4.0),
        rounded_at(p["screwdriver"]["tip_size"], p["screwdriver"]["tip_center"], cutter_height, floor, 3.0),
    )
    wrench = union(
        rounded_at(p["wrench"]["body_size"], p["wrench"]["body_center"], cutter_height, floor, 6.0),
        cylinder(float(p["wrench"]["head_diameter"]), cutter_height, tuple(p["wrench"]["head_center"]), floor),
    )
    wrench_mouth = union(
        cylinder(float(p["wrench"]["mouth_diameter"]), cutter_height + 0.5, tuple(p["wrench"]["mouth_center"]), floor),
        plate(float(p["wrench"]["mouth_slot_size"][0]), float(p["wrench"]["mouth_slot_size"][1]), cutter_height + 0.5, tuple(p["wrench"]["mouth_slot_center"]), floor),
    )
    wrench = wrench.cut(wrench_mouth).clean()

    cutters = [hammer, screwdriver, wrench]
    cutters.extend(cylinder(float(item["diameter"]), cutter_height, tuple(item["center"]), floor) for item in p["socket_pockets"])
    for cutter in cutters:
        body = body.cut(cutter)
    return body.clean()


def build_fit_gauge(p: dict, offset: float, marker_count: int) -> cq.Workplane:
    f = p["fit_gauge"]
    width = float(f["nominal_width"]) + offset
    base_height = float(f["base_height"])
    gauge = rounded_prism(width, float(f["depth"]), base_height, 2.0)
    for index in range(marker_count):
        gauge = gauge.union(plate(2.2, 4.0, float(f["marker_height"]), (-width / 2.0 + 9.0 + index * 4.5, 0.0), base_height - 0.1))
    return gauge.clean()


def bed_place(workplane: cq.Workplane) -> cq.Workplane:
    shape = workplane.val()
    bb = shape.BoundingBox()
    return cq.Workplane("XY").newObject([shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))])


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"Expected one mesh at {path}")
    return {
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "positive_volume": bool(mesh.volume > 0.0),
        "components": len(mesh.split(only_watertight=False)),
        "extents_mm": [round(float(value), 5) for value in mesh.extents],
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "triangles": int(len(mesh.faces)),
        "file_bytes": path.stat().st_size,
    }


def add_member(archive: zipfile.ZipFile, name: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, payload)


def write_3mf(path: Path, parts: list[tuple[str, Path]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    for name, value in (
        ("Title", "DRAFT MM-SYS-002 BROR/tool measurement-pilot inventory set"),
        ("Designer", "metriMade / autonomous CAD workflow"),
        ("Description", "216 mm tray plus 215.30, 216.00 and 216.70 mm width gauges; arrange objects on separate plates."),
        ("LicenseTerms", "DRAFT engineering artifact; not a compatibility or commercial release"),
    ):
        node = ET.SubElement(model, f"{{{ns}}}metadata", {"name": name})
        node.text = value
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    inventory_y = 0.0
    for object_id, (name, mesh_path) in enumerate(parts, start=1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name, "partnumber": f"MM-SYS-002-{REVISION}-{name}"})
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(triangles, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 0 {inventory_y:.3f} 0"})
        inventory_y += float(mesh.extents[1]) + 10.0
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        add_member(archive, "[Content_Types].xml", content_types)
        add_member(archive, "_rels/.rels", rels)
        add_member(archive, "3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True))
        add_member(archive, "Metadata/model-parameters.json", PARAMS.read_bytes())


def main() -> None:
    p = json.loads(PARAMS.read_text(encoding="utf-8"))
    t = p["tray"]
    f = p["fit_gauge"]
    printer = [float(value) for value in p["printer"]["build_volume"]]
    width, depth, height = (float(t[key]) for key in ("width", "depth", "height"))
    margin_x = (printer[0] - width) / 2.0
    offsets = [float(value) for value in f["width_offsets"]]
    line_width = float(p["printer"]["line_width"])
    for directory in (MASTER, MANUFACTURING, THREE_MF, VALIDATION, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)

    parameter_checks = [
        check("build-volume", width <= printer[0] and depth <= printer[1] and height <= printer[2], "Tray fits the configured build volume."),
        check("bed-margin", margin_x >= float(p["printer"]["minimum_xy_bed_margin_each"]), "Tray retains the configured X bed margin.", {"margin_each_mm": margin_x}),
        check("wall-line-alignment", math.isclose(float(t["wall"]) / line_width, 6.0, abs_tol=1e-9), "Perimeter equals six nominal line widths."),
        check("floor-ligament", float(t["floor_ligament"]) >= 2.4, "Pocket floor ligament is at least 2.4 mm."),
        check("pocket-depth", float(t["pocket_depth"]) > 0.0 and float(t["floor_ligament"]) + float(t["pocket_depth"]) < height, "Recess deck leaves a positive upper tray cavity."),
        check("gauge-ladder", offsets == [-0.7, 0.0, 0.7] and math.isclose(float(f["clearance_each"]), 0.35), "Gauge ladder encodes nominal plus/minus twice provisional per-side clearance."),
    ]
    if any(item["status"] != "PASS" for item in parameter_checks):
        raise RuntimeError("parameter contract failed")

    parts: list[tuple[str, cq.Workplane, str]] = [("tray", bed_place(build_tray(p)), "DRAFT-MM-SYS-002-bror-tool-shadow-tray")]
    gauge_names = ("gauge-low-215p30", "gauge-nominal-216p00", "gauge-high-216p70")
    for index, (name, offset) in enumerate(zip(gauge_names, offsets), start=1):
        parts.append((name, bed_place(build_fit_gauge(p, offset, index)), f"DRAFT-MM-SYS-002-{name}"))

    artifacts: dict[str, dict] = {}
    for name, shape, basename in parts:
        step_path = MASTER / f"{basename}-{REVISION}.step"
        stl_path = MANUFACTURING / f"{basename}-{REVISION}.stl"
        exporters.export(shape, str(step_path))
        exporters.export(shape, str(stl_path), tolerance=float(p["export"]["chordal_tolerance"]), angularTolerance=float(p["export"]["angular_tolerance"]))
        metrics = mesh_metrics(stl_path)
        gauge_index = len(artifacts) - 1
        expected = [width, depth, height] if name == "tray" else [float(f["nominal_width"]) + offsets[gauge_index], float(f["depth"]), float(f["base_height"]) + float(f["marker_height"]) - 0.1]
        checks = [
            check("watertight", metrics["watertight"], f"{name} is watertight."),
            check("winding", metrics["winding_consistent"], f"{name} winding is consistent."),
            check("positive-volume", metrics["positive_volume"], f"{name} has positive volume."),
            check("one-component", metrics["components"] == 1, f"{name} is one connected component."),
            check("expected-envelope", all(math.isclose(a, b, abs_tol=0.05) for a, b in zip(metrics["extents_mm"], expected)), f"{name} matches the controlled envelope.", {"actual_mm": metrics["extents_mm"], "expected_mm": expected}),
            check("build-volume", all(actual <= limit + 0.01 for actual, limit in zip(metrics["extents_mm"], printer)), f"{name} fits the build volume."),
            check("mesh-budget", metrics["triangles"] <= int(p["export"]["max_triangles_per_part"]) and metrics["file_bytes"] <= float(p["export"]["max_file_mib_per_part"]) * 1024 * 1024, f"{name} stays within mesh budgets."),
        ]
        part_report = report(f"MM-SYS-002-build-{name}", [PARAMS, SOURCE], checks, {"mesh": metrics, "stl": relative(stl_path), "step": relative(step_path)})
        report_path = VALIDATION / f"build-{name}.json"
        write_json(report_path, part_report)
        if part_report["status"] != "PASS":
            raise RuntimeError(f"part contract failed: {name}")
        artifacts[name] = {"stl": relative(stl_path), "step": relative(step_path), "mesh": metrics, "report": relative(report_path)}

    print_set = THREE_MF / f"DRAFT-MM-SYS-002-bror-measurement-pilot-{REVISION}.3mf"
    write_3mf(print_set, [(name, ROOT / artifacts[name]["stl"]) for name in artifacts])
    interface_report = report(
        "MM-SYS-002-interface-contract",
        [PARAMS, SOURCE],
        [
            check("nominal-width", math.isclose(float(f["nominal_width"]), width), "Nominal gauge width equals tray width."),
            check("gauge-widths", [round(float(f["nominal_width"]) + value, 2) for value in offsets] == [215.3, 216.0, 216.7], "Gauge set encodes the controlled width ladder."),
            check("floor-contract", math.isclose(float(t["floor_ligament"]), 2.4), "All tool recesses start above the protected 2.4 mm floor ligament."),
            check("no-compatibility-claim", True, "Furniture and tool fit remain PROVISIONAL_UNVERIFIED."),
        ],
        {"gauge_widths_mm": [float(f["nominal_width"]) + value for value in offsets], "bed_margin_each_x_mm": margin_x, "floor_ligament_mm": float(t["floor_ligament"])},
        ["Exact drawer and tool measurements require physical evidence."],
    )
    write_json(VALIDATION / "interface-report.json", interface_report)
    source_report = report(
        "MM-SYS-002-parametric-source",
        [PARAMS, SOURCE],
        parameter_checks + [
            check("all-parts", len(artifacts) == 4, "Tray and three gauges built successfully."),
            check("print-package", print_set.is_file(), "Four-object DRAFT 3MF exists."),
            check("interface-contract", interface_report["status"] == "PASS", "Digital interface contract passes."),
        ],
        {"artifacts": artifacts, "print_set": relative(print_set)},
        ["Exact slicer, furniture/tool fit and physical validation are deferred."],
    )
    write_json(VALIDATION / "parametric-source-report.json", source_report)
    if source_report["status"] != "PASS":
        raise RuntimeError("aggregate contract failed")

    baseline = mesh_metrics(BASELINE_STL)
    selected = artifacts["tray"]["mesh"]
    optimization = report(
        "MM-SYS-002-optimization-comparison",
        [PARAMS, SOURCE, BASELINE_STL],
        [
            check("common-bed-margin", margin_x >= 2.0, "Selected envelope replaces zero-margin 220 mm width with 2 mm per-side margin."),
            check("floor-protected", float(t["floor_ligament"]) >= 2.4, "Pocket floor ligament remains protected."),
            check("mesh-budget", selected["triangles"] <= int(p["export"]["max_triangles_per_part"]), "Direct CAD tessellation is within budget."),
        ],
        {
            "selection": "216 mm common-printer measurement pilot plus gauges",
            "baseline_extents_mm": baseline["extents_mm"],
            "selected_extents_mm": selected["extents_mm"],
            "baseline_volume_mm3": baseline["volume_mm3"],
            "selected_volume_mm3": selected["volume_mm3"],
            "baseline_triangles": baseline["triangles"],
            "selected_triangles": selected["triangles"],
            "mesh_simplification": "NOT_BENEFICIAL",
            "exact_slicer_metrics": "NOT_RUN",
        },
        ["No deposited-material or print-time claim is made."],
    )
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "build-manifest.json", {
        "project_id": "MM-SYS-002",
        "revision": REVISION,
        "status": "DRAFT",
        "parameters_sha256": sha256(PARAMS),
        "source_sha256": sha256(SOURCE),
        "artifacts": artifacts,
        "print_set_3mf": relative(print_set),
        "print_set_3mf_sha256": sha256(print_set),
        "furniture_and_tool_fit": "PROVISIONAL_UNVERIFIED",
        "exact_slicer": "NOT_RUN",
        "physical_validation": "DEFERRED",
    })
    print(json.dumps({"status": "PASS", "tray_extents_mm": selected["extents_mm"], "print_set": str(print_set)}, indent=2))


if __name__ == "__main__":
    main()
