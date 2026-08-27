#!/usr/bin/env python3
"""Deterministic standalone build for MM-SYS-001 revision 0.2.0-draft.1."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
from cadquery import exporters
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = ROOT / "model-parameters.json"
SOURCE = Path(__file__).resolve()
SHARED_ROOT = ROOT.parents[1]
BASELINE_STL = SHARED_ROOT / "exports" / "stl" / "01_alex_inventory_workplace_tray.stl"
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


def input_record(path: Path) -> dict:
    return {"path": relative(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}


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
        "tool_version": "0.2.0",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks if item["required"]) else "FAIL",
        "profile": "draft",
        "inputs": [input_record(path) for path in inputs],
        "checks": checks,
        "metrics": metrics,
        "limitations": limitations or [],
        "required_capabilities": [],
    }


def rounded_prism(width: float, depth: float, height: float, radius: float = 3.0, z0: float = 0.0) -> cq.Workplane:
    radius = min(radius, width / 2.0, depth / 2.0)
    parts: list[cq.Workplane] = []
    if width - 2.0 * radius > 1e-6:
        parts.append(cq.Workplane("XY").rect(width - 2.0 * radius, depth).extrude(height))
    if depth - 2.0 * radius > 1e-6:
        parts.append(cq.Workplane("XY").rect(width, depth - 2.0 * radius).extrude(height))
    x = width / 2.0 - radius
    y = depth / 2.0 - radius
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            parts.append(cq.Workplane("XY").center(sx * x, sy * y).circle(radius).extrude(height))
    result = parts[0]
    for part in parts[1:]:
        result = result.union(part)
    return result.translate((0.0, 0.0, z0)).clean()


def plate(width: float, depth: float, height: float, center: tuple[float, float], z0: float) -> cq.Workplane:
    return cq.Workplane("XY").box(width, depth, height, centered=(True, True, False)).translate((center[0], center[1], z0))


def cylinder(diameter: float, height: float, center: tuple[float, float], z0: float) -> cq.Workplane:
    return cq.Workplane("XY").center(center[0], center[1]).circle(diameter / 2.0).extrude(height).translate((0.0, 0.0, z0))


def build_tray(p: dict) -> cq.Workplane:
    t = p["tray"]
    width = float(t["width"])
    depth = float(t["depth"])
    height = float(t["height"])
    wall = float(t["wall"])
    floor = float(t["floor"])
    radius = float(t["corner_radius"])
    divider = float(t["divider_wall"])

    outer = rounded_prism(width, depth, height, radius)
    inner = rounded_prism(width - 2.0 * wall, depth - 2.0 * wall, height - floor + 1.0, max(0.8, radius - wall), floor)
    body = outer.cut(inner).clean()

    divider_z = floor - 0.25
    divider_height = height - float(t["divider_top_recess"]) - divider_z
    x_min = -width / 2.0 + wall
    x_max = width / 2.0 - wall
    y_min = -depth / 2.0 + wall
    y_max = depth / 2.0 - wall
    spine_x = float(t["spine_x"])
    left_y = float(t["left_branch_y"])
    right_y = float(t["right_branch_y"])
    short_x = float(t["short_branch_x"])

    parts = [
        plate(divider, y_max - y_min + 0.4, divider_height, (spine_x, 0.0), divider_z),
        plate(spine_x - x_min + divider, divider, divider_height, ((x_min + spine_x) / 2.0, left_y), divider_z),
        plate(x_max - spine_x + divider, divider, divider_height, ((spine_x + x_max) / 2.0, right_y), divider_z),
        plate(divider, y_max - right_y + divider, divider_height, (short_x, (y_max + right_y) / 2.0), divider_z),
    ]
    outer_d = float(t["round_zone_outer_diameter"])
    ring_wall = float(t["round_zone_wall"])
    center = tuple(float(value) for value in t["round_zone_center"])
    ring = cylinder(outer_d, float(t["round_zone_height"]), center, floor - 0.2).cut(
        cylinder(outer_d - 2.0 * ring_wall, float(t["round_zone_height"]) + 1.0, center, floor - 0.2)
    )
    for part in (*parts, ring):
        body = body.union(part)
    return body.clean()


def build_fit_gauge(p: dict, offset: float, marker_count: int) -> cq.Workplane:
    f = p["fit_gauge"]
    width = float(f["nominal_width"]) + offset
    depth = float(f["depth"])
    base_height = float(f["base_height"])
    marker_height = float(f["marker_height"])
    gauge = rounded_prism(width, depth, base_height, min(2.0, depth / 2.0))
    marker_width = 2.2
    marker_depth = 4.0
    start_x = -width / 2.0 + 9.0
    for index in range(marker_count):
        marker = plate(marker_width, marker_depth, marker_height, (start_x + index * 4.5, 0.0), base_height - 0.1)
        gauge = gauge.union(marker)
    return gauge.clean()


def bed_place(workplane: cq.Workplane) -> cq.Workplane:
    shape = workplane.val()
    bb = shape.BoundingBox()
    translated = shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    return cq.Workplane("XY").newObject([translated])


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"Expected a single mesh at {path}")
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


def add_zip_member(archive: zipfile.ZipFile, name: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, payload)


def write_3mf(path: Path, parts: list[tuple[str, Path]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    for name, value in (
        ("Title", "DRAFT MM-SYS-001 ALEX measurement-pilot inventory set"),
        ("Designer", "metriMade / autonomous CAD workflow"),
        ("Description", "Tray plus 209.30, 210.00 and 210.70 mm width gauges; arrange selected objects on separate plates."),
        ("LicenseTerms", "DRAFT engineering artifact; not a compatibility or commercial release"),
    ):
        node = ET.SubElement(model, f"{{{ns}}}metadata", {"name": name})
        node.text = value
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    inventory_y = 0.0
    for object_id, (name, mesh_path) in enumerate(parts, start=1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name, "partnumber": f"MM-SYS-001-{REVISION}-{name}"})
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(triangles, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        transform = f"1 0 0 0 1 0 0 0 1 0 {inventory_y:.3f} 0"
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": transform})
        inventory_y += float(mesh.extents[1]) + 10.0
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
    t = p["tray"]
    f = p["fit_gauge"]
    printer = [float(value) for value in p["printer"]["build_volume"]]
    export = p["export"]
    for directory in (MASTER, MANUFACTURING, THREE_MF, VALIDATION, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)

    width = float(t["width"])
    depth = float(t["depth"])
    height = float(t["height"])
    line_width = float(p["printer"]["line_width"])
    ring_outer = float(t["round_zone_outer_diameter"])
    ring_center = [float(value) for value in t["round_zone_center"]]
    ring_margin_x = width / 2.0 - float(t["wall"]) - (ring_center[0] + ring_outer / 2.0)
    ring_margin_y = depth / 2.0 - float(t["wall"]) - (ring_center[1] + ring_outer / 2.0)
    offsets = [float(value) for value in f["width_offsets"]]

    parameter_checks = [
        check("tray-build-volume", width <= printer[0] and depth <= printer[1] and height <= printer[2], "Tray fits the configured common 220 mm printer."),
        check("wall-line-alignment", math.isclose(float(t["wall"]) / line_width, 6.0, abs_tol=1e-9) and math.isclose(float(t["divider_wall"]) / line_width, 6.0, abs_tol=1e-9), "Perimeter and divider walls equal six nominal line widths."),
        check("floor-minimum", float(t["floor"]) >= 2.4, "Continuous floor is at least 2.4 mm."),
        check("ring-keepout", ring_margin_x >= 0.0 and ring_margin_y >= 0.0, "Circular tool zone remains inside the tray perimeter.", {"margin_x_mm": ring_margin_x, "margin_y_mm": ring_margin_y}),
        check("gauge-ladder", offsets == [-0.7, 0.0, 0.7] and math.isclose(float(f["clearance_each"]), 0.35), "Gauge ladder spans nominal width plus/minus twice the provisional per-side clearance."),
    ]
    if any(item["status"] != "PASS" for item in parameter_checks):
        raise RuntimeError("parameter contract failed")

    tray = bed_place(build_tray(p))
    parts: list[tuple[str, cq.Workplane, str]] = [("tray", tray, "DRAFT-MM-SYS-001-alex-inventory-tray")]
    gauge_names = ("gauge-low-209p30", "gauge-nominal-210p00", "gauge-high-210p70")
    for index, (name, offset) in enumerate(zip(gauge_names, offsets), start=1):
        parts.append((name, bed_place(build_fit_gauge(p, offset, index)), f"DRAFT-MM-SYS-001-{name}"))

    artifacts: dict[str, dict] = {}
    for name, shape, basename in parts:
        stl_path = MANUFACTURING / f"{basename}-{REVISION}.stl"
        step_path = MASTER / f"{basename}-{REVISION}.step"
        exporters.export(shape, str(step_path))
        exporters.export(shape, str(stl_path), tolerance=float(export["chordal_tolerance"]), angularTolerance=float(export["angular_tolerance"]))
        metrics = mesh_metrics(stl_path)
        expected = [width, depth, height] if name == "tray" else [float(f["nominal_width"]) + offsets[len(artifacts) - 1], float(f["depth"]), float(f["base_height"]) + float(f["marker_height"]) - 0.1]
        checks = [
            check("watertight", metrics["watertight"], f"{name} mesh is watertight."),
            check("winding", metrics["winding_consistent"], f"{name} winding is consistent."),
            check("positive-volume", metrics["positive_volume"], f"{name} has positive volume."),
            check("one-component", metrics["components"] == 1, f"{name} is one connected component.", {"components": metrics["components"]}),
            check("expected-envelope", all(math.isclose(a, b, abs_tol=0.05) for a, b in zip(metrics["extents_mm"], expected)), f"{name} matches the controlled envelope.", {"actual_mm": metrics["extents_mm"], "expected_mm": expected}),
            check("build-volume", all(actual <= limit + 0.01 for actual, limit in zip(metrics["extents_mm"], printer)), f"{name} fits the target build volume."),
            check("mesh-budget", metrics["triangles"] <= int(export["max_triangles_per_part"]) and metrics["file_bytes"] <= float(export["max_file_mib_per_part"]) * 1024 * 1024, f"{name} stays within mesh budgets."),
        ]
        part_report = report(f"MM-SYS-001-build-{name}", [PARAMS, SOURCE], checks, {"mesh": metrics, "stl": relative(stl_path), "step": relative(step_path)})
        report_path = VALIDATION / f"build-{name}.json"
        write_json(report_path, part_report)
        if part_report["status"] != "PASS":
            raise RuntimeError(f"part contract failed: {name}")
        artifacts[name] = {"stl": relative(stl_path), "step": relative(step_path), "mesh": metrics, "report": relative(report_path)}

    print_set = THREE_MF / f"DRAFT-MM-SYS-001-alex-measurement-pilot-{REVISION}.3mf"
    write_3mf(print_set, [(name, ROOT / artifacts[name]["stl"]) for name in artifacts])

    interface_checks = [
        check("nominal-width", math.isclose(float(f["nominal_width"]), width), "Nominal gauge width equals tray width."),
        check("gauge-widths", [round(float(f["nominal_width"]) + offset, 2) for offset in offsets] == [209.3, 210.0, 210.7], "Three full-width gauges encode the controlled measurement ladder."),
        check("no-compatibility-claim", True, "Furniture fit remains explicitly PROVISIONAL_UNVERIFIED until measured and printed."),
    ]
    interface_report = report(
        "MM-SYS-001-interface-contract",
        [PARAMS, SOURCE],
        interface_checks,
        {"gauge_widths_mm": [float(f["nominal_width"]) + offset for offset in offsets], "provisional_clearance_each_mm": float(f["clearance_each"])},
        ["The gauge set provides measurement evidence only after printing; no ALEX revision was supplied."],
    )
    write_json(VALIDATION / "interface-report.json", interface_report)

    aggregate_checks = parameter_checks + [
        check("all-parts", all((VALIDATION / f"build-{name}.json").is_file() for name in artifacts), "All four part reports exist and pass."),
        check("print-package", print_set.is_file(), "Inventory 3MF exists."),
        check("interface-contract", interface_report["status"] == "PASS", "Digital measurement interface contract passes."),
    ]
    source_report = report(
        "MM-SYS-001-parametric-source",
        [PARAMS, SOURCE],
        aggregate_checks,
        {"artifacts": artifacts, "print_set": relative(print_set)},
        ["Exact furniture revision, slicer and physical evidence are deferred."],
    )
    write_json(VALIDATION / "parametric-source-report.json", source_report)
    if source_report["status"] != "PASS":
        raise RuntimeError("aggregate contract failed")

    baseline = mesh_metrics(BASELINE_STL)
    selected = artifacts["tray"]["mesh"]
    optimization = report(
        "MM-SYS-001-optimization-comparison",
        [PARAMS, SOURCE, BASELINE_STL],
        [
            check("protected-envelope", all(math.isclose(a, b, abs_tol=0.05) for a, b in zip(selected["extents_mm"], baseline["extents_mm"])), "Product-specific tray preserves the shared concept envelope."),
            check("process-aligned-walls", math.isclose(float(t["divider_wall"]) / line_width, 6.0, abs_tol=1e-9), "Selected divider is process-aligned for six nominal lines."),
            check("mesh-budget", selected["triangles"] <= int(export["max_triangles_per_part"]), "Direct CAD tessellation is already within budget."),
        ],
        {
            "selection": "product-specific parametric control plus fit gauges",
            "baseline_volume_mm3": baseline["volume_mm3"],
            "selected_tray_volume_mm3": selected["volume_mm3"],
            "baseline_triangles": baseline["triangles"],
            "selected_triangles": selected["triangles"],
            "mesh_simplification": "NOT_BENEFICIAL",
            "exact_slicer_metrics": "NOT_RUN",
        },
        ["No print-time or deposited-material claim is made."],
    )
    write_json(REPORTS / "optimization-comparison.json", optimization)

    manifest = {
        "project_id": "MM-SYS-001",
        "revision": REVISION,
        "status": "DRAFT",
        "parameters_sha256": sha256(PARAMS),
        "source_sha256": sha256(SOURCE),
        "artifacts": artifacts,
        "print_set_3mf": relative(print_set),
        "print_set_3mf_sha256": sha256(print_set),
        "compatibility": "PROVISIONAL_UNVERIFIED",
        "exact_slicer": "NOT_RUN",
        "physical_validation": "DEFERRED",
    }
    write_json(REPORTS / "build-manifest.json", manifest)
    print(json.dumps({"status": "PASS", "tray_extents_mm": selected["extents_mm"], "print_set": str(print_set)}, indent=2))


if __name__ == "__main__":
    main()
