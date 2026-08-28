#!/usr/bin/env python3
"""Build the parametric MM-ORG-031 PageHarbor Duo 5 candidate."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import zipfile
import xml.etree.ElementTree as ET

import cadquery as cq
import numpy as np
import trimesh
from cadquery import exporters

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
REPORTS, VALIDATION, EXPORTS = ROOT / "reports", ROOT / "validation", ROOT / "exports"
PROJECT_ID, REVISION = "MM-ORG-031", "0.1.0-draft.1"


def sha256(target: Path) -> str:
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(target: Path) -> dict:
    try:
        display = str(target.relative_to(ROOT))
    except ValueError:
        display = str(target)
    return {"path": display, "sha256": sha256(target), "size_bytes": target.stat().st_size}


def write_json(target: Path, value: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def _structure(parameters: dict, light: bool) -> tuple[float, float, float]:
    dock = parameters["dock"]
    if light:
        return dock["light_base_mm"], dock["light_wall_mm"], dock["light_backrest_thickness_mm"]
    return dock["base_mm"], dock["wall_mm"], dock["backrest_thickness_mm"]


def dock_datums(parameters: dict, light: bool = False) -> dict:
    dock, fit = parameters["dock"], parameters["fit"]
    base, wall, rail_thickness = _structure(parameters, light)
    clearance = fit["clearance_per_side_mm"]
    book_slot = fit["selected_book_thickness_mm"] + 2 * clearance
    device_slot = fit["selected_device_case_thickness_mm"] + 2 * clearance
    front_wall_y = dock["front_margin_mm"]
    book_front = front_wall_y + wall
    divider_y = book_front + book_slot
    device_front = divider_y + wall
    backrest_front_at_shoe = device_front + device_slot
    lean = math.tan(math.radians(dock["backrest_lean_from_vertical_deg"]))
    backrest_front_base = backrest_front_at_shoe - lean * (dock["device_shoe_top_z_mm"] - base)
    backrest_front_top = backrest_front_at_shoe + lean * (dock["height_mm"] - dock["device_shoe_top_z_mm"])
    return {
        "base_mm": base,
        "wall_mm": wall,
        "rail_thickness_mm": rail_thickness,
        "book_slot_mm": book_slot,
        "device_slot_mm": device_slot,
        "front_wall_y_mm": front_wall_y,
        "book_front_y_mm": book_front,
        "divider_y_mm": divider_y,
        "device_front_y_mm": device_front,
        "backrest_front_at_shoe_mm": backrest_front_at_shoe,
        "backrest_front_base_mm": backrest_front_base,
        "backrest_front_top_mm": backrest_front_top,
    }


def _yz_prism(points: list[tuple[float, float]], width: float, x: float) -> cq.Workplane:
    return cq.Workplane("YZ").polyline(points).close().extrude(width).translate((x, 0, 0))


def make_dock(parameters: dict, light: bool = False) -> tuple[cq.Workplane, dict]:
    dock, fit = parameters["dock"], parameters["fit"]
    datum = dock_datums(parameters, light)
    base, wall, rail_t = datum["base_mm"], datum["wall_mm"], datum["rail_thickness_mm"]
    width, depth, height = dock["width_mm"], dock["depth_mm"], dock["height_mm"]
    side = dock["side_margin_mm"]
    shape = cq.Workplane("XY").box(width, depth, base, centered=(False, False, False))
    front_wall = cq.Workplane("XY").box(width - 2 * side, wall, dock["front_wall_height_mm"], centered=(False, False, False)).translate((side, datum["front_wall_y_mm"], 0))
    divider = cq.Workplane("XY").box(width - 2 * side, wall, dock["divider_height_mm"], centered=(False, False, False)).translate((side, datum["divider_y_mm"], 0))
    shape = shape.union(front_wall).union(divider)
    shoe_depth = datum["backrest_front_at_shoe_mm"] - datum["device_front_y_mm"] + 1.2
    for x0, x1 in dock["device_shoe_x_ranges_mm"]:
        shoe = cq.Workplane("XY").box(x1 - x0, shoe_depth, dock["device_shoe_top_z_mm"] - base, centered=(False, False, False)).translate((x0, datum["device_front_y_mm"], base))
        shape = shape.union(shoe)
    rail_points = [
        (datum["backrest_front_base_mm"], base),
        (datum["backrest_front_base_mm"] + rail_t, base),
        (datum["backrest_front_top_mm"] + rail_t, height),
        (datum["backrest_front_top_mm"], height),
    ]
    for x0 in dock["rail_x_mm"]:
        shape = shape.union(_yz_prism(rail_points, dock["rail_width_mm"], x0))
    gusset_points = [
        (datum["backrest_front_base_mm"] + rail_t - 0.4, base),
        (depth - dock["rear_margin_mm"], base),
        (datum["backrest_front_top_mm"] + rail_t - 0.4, height),
    ]
    for x0 in [side, width - side - wall]:
        shape = shape.union(_yz_prism(gusset_points, wall, x0))
    shape = shape.clean()
    keepout_actual = dock["device_shoe_x_ranges_mm"][1][0] - dock["device_shoe_x_ranges_mm"][0][1]
    min_device_left = (width - fit["minimum_device_width_mm"]) / 2
    min_device_right = min_device_left + fit["minimum_device_width_mm"]
    contact_overlap = sum(max(0.0, min(x + dock["rail_width_mm"], min_device_right) - max(x, min_device_left)) for x in dock["rail_x_mm"])
    return shape, {
        "part_id": "light-dock" if light else "dock",
        "outer_bounds_mm": [width, depth, height],
        "book_slot_mm": datum["book_slot_mm"],
        "device_slot_at_shoe_mm": datum["device_slot_mm"],
        "device_shoe_top_z_mm": dock["device_shoe_top_z_mm"],
        "connector_vertical_clearance_mm": dock["device_shoe_top_z_mm"] - base,
        "connector_keepout_width_mm": keepout_actual,
        "backrest_lean_from_vertical_deg": dock["backrest_lean_from_vertical_deg"],
        "rail_count": len(dock["rail_x_mm"]),
        "minimum_device_contact_overlap_mm": contact_overlap,
        "base_mm": base,
        "wall_mm": wall,
        "rail_thickness_mm": rail_t,
        "print_orientation": "base_down",
        "support_required": False,
        "light_variant": light,
        "external_assets": [],
    }


def gauge_width(slot_widths: list[float], wall: float) -> float:
    return sum(slot_widths) + wall * (len(slot_widths) + 1)


def make_slot_gauge(parameters: dict, family: str) -> tuple[cq.Workplane, dict]:
    fit, coupon = parameters["fit"], parameters["coupon"]
    targets = fit["device_case_thickness_presets_mm"] if family == "device" else fit["book_thickness_presets_mm"]
    slots = [value + 2 * fit["clearance_per_side_mm"] for value in targets]
    wall, depth, height, base = coupon["wall_mm"], coupon["depth_mm"], coupon["height_mm"], coupon["base_mm"]
    width = gauge_width(slots, wall)
    shape = cq.Workplane("XY").box(width, depth, base, centered=(False, False, False))
    shape = shape.union(cq.Workplane("XY").box(width, wall, height, centered=(False, False, False)).translate((0, depth - wall, 0)))
    x = 0.0
    for index, slot in enumerate(slots):
        shape = shape.union(cq.Workplane("XY").box(wall, depth, height, centered=(False, False, False)).translate((x, 0, 0)))
        x += wall + slot
        if index == len(slots) - 1:
            shape = shape.union(cq.Workplane("XY").box(wall, depth, height, centered=(False, False, False)).translate((x, 0, 0)))
    shape = shape.clean()
    return shape, {"part_id": f"{family}-fit-gauge", "targets_mm": targets, "slot_widths_mm": slots, "clearance_per_side_mm": fit["clearance_per_side_mm"], "outer_bounds_mm": [width, depth, height], "station_order": "left_to_right_ascending", "print_orientation": "base_down", "external_assets": []}


def make_key_comb(parameters: dict, family: str) -> tuple[cq.Workplane, dict]:
    fit, coupon = parameters["fit"], parameters["coupon"]
    targets = fit["device_case_thickness_presets_mm"] if family == "device" else fit["book_thickness_presets_mm"]
    gap, depth, height = coupon["key_gap_mm"], coupon["key_depth_mm"], coupon["key_height_mm"]
    spine_depth = coupon["wall_mm"] * 2
    width = sum(targets) + gap * (len(targets) - 1)
    shape = cq.Workplane("XY").box(width, spine_depth, height, centered=(False, False, False))
    x = 0.0
    for target in targets:
        tongue = cq.Workplane("XY").box(target, depth - spine_depth, height, centered=(False, False, False)).translate((x, spine_depth, 0))
        shape = shape.union(tongue)
        x += target + gap
    shape = shape.clean()
    return shape, {"part_id": f"{family}-key-comb", "tongue_widths_mm": targets, "outer_bounds_mm": [width, depth, height], "station_order": "left_to_right_ascending", "print_orientation": "broad_face_down", "external_assets": []}


def export_step(shape: cq.Workplane | cq.Compound, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(target), exportType="STEP")


def export_stl(shape: cq.Workplane, target: Path, linear: float, angular: float) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(target), exportType="STL", tolerance=linear, angularTolerance=angular)
    mesh = trimesh.load_mesh(target, force="mesh", process=True)
    mesh.remove_unreferenced_vertices()
    mesh.merge_vertices()
    mesh.fix_normals()
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise RuntimeError(f"Invalid mesh: {target}")
    mesh.export(target, file_type="stl")


def mesh_metrics(target: Path) -> dict:
    mesh = trimesh.load_mesh(target, force="mesh", process=True)
    return {"path": str(target.relative_to(ROOT)), "sha256": sha256(target), "triangles": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)), "file_bytes": target.stat().st_size, "file_mib": target.stat().st_size / (1024 * 1024), "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent), "positive_volume": bool(mesh.is_volume and mesh.volume > 0), "components": int(len(mesh.split(only_watertight=False))), "volume_mm3": float(mesh.volume), "surface_area_mm2": float(mesh.area), "extents_mm": np.round(mesh.extents, 4).tolist(), "bounds_mm": np.round(mesh.bounds, 4).tolist()}


def zip_member(name: str, data: bytes, archive: zipfile.ZipFile) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def write_3mf(target: Path, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources, build = ET.SubElement(model, f"{{{ns}}}resources"), ET.SubElement(model, f"{{{ns}}}build")
    for object_id, ((name, mesh_path), (mx, my)) in enumerate(zip(parts, placements), 1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name})
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(triangles, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {mx:.3f} {my:.3f} 0"})
    types = b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        zip_member("[Content_Types].xml", types, archive)
        zip_member("_rels/.rels", rels, archive)
        zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive)
        zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)


def nesting_report(parameters: dict, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> dict:
    gap, margin, bed = parameters["nesting"]["minimum_object_gap_mm"], parameters["nesting"]["bed_margin_mm"], parameters["printer"]["build_volume_mm"]
    items = []
    for (name, target), (mx, my) in zip(parts, placements):
        bounds = trimesh.load_mesh(target, force="mesh", process=True).bounds
        items.append({"name": name, "x0": float(bounds[0][0] + mx), "y0": float(bounds[0][1] + my), "x1": float(bounds[1][0] + mx), "y1": float(bounds[1][1] + my)})
    collisions = []
    for index, a in enumerate(items):
        for b in items[index + 1:]:
            separated = a["x1"] + gap <= b["x0"] or b["x1"] + gap <= a["x0"] or a["y1"] + gap <= b["y0"] or b["y1"] + gap <= a["y0"]
            if not separated:
                collisions.append([a["name"], b["name"]])
    within = all(item["x0"] >= margin and item["y0"] >= margin and item["x1"] <= bed[0] - margin and item["y1"] <= bed[1] - margin for item in items)
    checks = [check("non-overlap", not collisions, "Five objects retain the configured gap", {"collisions": collisions}), check("bed-bounds", within, "Layout respects conservative bed margins")]
    return {"schema_version": "1.0", "tool": "MM-ORG-031-nesting-layout", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [], "checks": checks, "metrics": {"plate_count": 1, "object_count": len(items), "minimum_gap_mm": gap, "objects": items}, "limitations": ["Exact destination profile remains authoritative."], "required_capabilities": []}


def virtual_use_assembly(parameters: dict, dock_shape: cq.Workplane) -> cq.Compound:
    dock, fit = parameters["dock"], parameters["fit"]
    datum = dock_datums(parameters)
    book_w, book_t, book_h = 130.0, fit["selected_book_thickness_mm"], 170.0
    book = cq.Workplane("XY").box(book_w, book_t, book_h, centered=(False, False, False)).translate(((dock["width_mm"] - book_w) / 2, datum["book_front_y_mm"] + fit["clearance_per_side_mm"], datum["base_mm"]))
    device_w, device_t, device_h = fit["minimum_device_width_mm"], fit["selected_device_case_thickness_mm"], 160.0
    pivot_y = datum["device_front_y_mm"] + fit["clearance_per_side_mm"]
    pivot_z = dock["device_shoe_top_z_mm"]
    device = cq.Workplane("XY").box(device_w, device_t, device_h, centered=(False, False, False)).translate(((dock["width_mm"] - device_w) / 2, pivot_y, pivot_z)).rotate((0, pivot_y, pivot_z), (1, pivot_y, pivot_z), -dock["backrest_lean_from_vertical_deg"])
    return cq.Compound.makeCompound([dock_shape.val(), book.val(), device.val()])


def main() -> None:
    parameters = json.loads(PARAMETERS.read_text())
    REPORTS.mkdir(exist_ok=True)
    VALIDATION.mkdir(exist_ok=True)
    source_inputs = [PARAMETERS, ROOT / "cad/build.py"]
    inputs = [record(path) for path in source_inputs]
    dock_p, fit, mesh_p = parameters["dock"], parameters["fit"], parameters["mesh"]
    selected_datum = dock_datums(parameters)
    checks = [
        check("identity", parameters["project"]["id"] == PROJECT_ID, "Project identity matches"),
        check("device-presets", fit["device_case_thickness_presets_mm"] == [8, 10, 12, 14, 16], "Five device case presets exist"),
        check("book-presets", fit["book_thickness_presets_mm"] == [18, 30, 42], "Paperback, selected and hardcover presets exist"),
        check("envelope", dock_p["width_mm"] <= 180 and dock_p["depth_mm"] <= 120 and dock_p["height_mm"] <= 180, "Dock fits the portfolio envelope"),
        check("selected-shell", dock_p["base_mm"] >= 3 and dock_p["wall_mm"] >= 3 and dock_p["backrest_thickness_mm"] >= 4, "Selected structural sections are protected"),
        check("selected-gaps", selected_datum["device_slot_mm"] == 13 and selected_datum["book_slot_mm"] == 31, "Selected fit gaps are exact"),
        check("content", parameters["physical_contract"]["contents"] == "passive_storage_of_one_ereader_and_one_closed_book_only", "Passive storage boundary is explicit"),
    ]
    dock_shape, dock_interface = make_dock(parameters)
    light_shape, light_interface = make_dock(parameters, light=True)
    device_gauge, device_gauge_i = make_slot_gauge(parameters, "device")
    device_keys, device_keys_i = make_key_comb(parameters, "device")
    book_gauge, book_gauge_i = make_slot_gauge(parameters, "book")
    book_keys, book_keys_i = make_key_comb(parameters, "book")
    shapes = {"dock": dock_shape, "device-fit-gauge": device_gauge, "device-key-comb": device_keys, "book-fit-gauge": book_gauge, "book-key-comb": book_keys}
    all_shapes = [*shapes.values(), light_shape]
    if not all(shape.val().isValid() and len(shape.solids().vals()) == 1 for shape in all_shapes):
        raise RuntimeError("Invalid or multi-solid B-Rep")
    interfaces = {"dock": dock_interface, "device-fit-gauge": device_gauge_i, "device-key-comb": device_keys_i, "book-fit-gauge": book_gauge_i, "book-key-comb": book_keys_i, "light-dock": light_interface}
    step_paths, stl_paths = {}, {}
    for name, shape in shapes.items():
        step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        folder = "manufacturing" if name == "dock" else "coupons"
        stl = EXPORTS / folder / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_step(shape, step)
        export_stl(shape, stl, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        step_paths[name], stl_paths[name] = step, stl
    light_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-light-dock-{REVISION}.step"
    light_stl = EXPORTS / "variants" / f"DRAFT-{PROJECT_ID}-light-dock-{REVISION}.stl"
    export_step(light_shape, light_step)
    export_stl(light_shape, light_stl, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    step_paths["light-dock"], stl_paths["light-dock"] = light_step, light_stl
    virtual_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-virtual-use-assembly-{REVISION}.step"
    export_step(virtual_use_assembly(parameters, dock_shape), virtual_step)
    order = ["dock", "device-fit-gauge", "device-key-comb", "book-fit-gauge", "book-key-comb"]
    parts = [(name, stl_paths[name]) for name in order]
    origins = parameters["nesting"]["origins_mm"]
    placements = [tuple(origins[name]) for name in order]
    nesting = nesting_report(parameters, parts, placements)
    nesting["inputs"] = inputs
    write_json(REPORTS / "nesting-layout.json", nesting)
    if nesting["status"] != "PASS":
        raise RuntimeError("Nesting failed")
    selected_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-pageharbor-duo-five-{REVISION}.3mf"
    write_3mf(selected_3mf, parts, placements)
    metrics = {name: mesh_metrics(path) for name, path in stl_paths.items()}
    baseline_volume = dock_p["width_mm"] * dock_p["depth_mm"] * dock_p["height_mm"]
    selected_volume = metrics["dock"]["volume_mm3"]
    light_reduction = 100 * (1 - metrics["light-dock"]["volume_mm3"] / selected_volume)
    geometric = {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "baseline": {"id": "solid-dock-envelope", "volume_mm3": baseline_volume}, "selected": {"id": "sparse-rail-dual-slot-dock", "volume_mm3": selected_volume, "reduction_percent": 100 * (1 - selected_volume / baseline_volume)}, "light_variant": {"id": "2.4-mm-wall-3.2-mm-rail-dock", "volume_mm3": metrics["light-dock"]["volume_mm3"], "reduction_percent_vs_selected_dock": light_reduction, "constraint": "REJECTED_PENDING_DEVICE_BOOK_TIP_DROP_AND_CYCLE_EVIDENCE"}, "process_comparison": "PENDING_EXACT_SLICES"}
    write_json(REPORTS / "optimization-geometric.json", geometric)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": "PASS", "meshes": metrics, "simplification": "NOT_BENEFICIAL", "reason": "Every retained edge defines a fit station, sparse load path or connector keepout and all meshes remain below budget."})
    parametric_checks = checks + [check("cad-valid", all(shape.val().isValid() for shape in all_shapes), "All B-Reps are valid"), check("single-solids", all(len(shape.solids().vals()) == 1 for shape in all_shapes), "Every unique printable deliverable is one solid")]
    parametric = {"schema_version": "1.0", "tool": "MM-ORG-031-parametric-source", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in parametric_checks) else "FAIL", "profile": "draft", "inputs": inputs, "checks": parametric_checks, "metrics": {"python": sys.version.split()[0], "cadquery": cq.__version__, "unique_parts": list(interfaces)}, "limitations": ["Digital dimensions do not prove device, case, connector or book fit."], "required_capabilities": ["cad"]}
    write_json(VALIDATION / "parametric-source-report.json", parametric)
    mesh_checks = [check("mesh-count", len(metrics) == 6, "Five selected meshes plus one light variant generated"), check("mesh-validity", all(item["watertight"] and item["winding_consistent"] and item["components"] == 1 and item["positive_volume"] for item in metrics.values()), "Every mesh is one watertight positive volume"), check("mesh-budget", all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()), "Every mesh stays below budget")]
    meshgen = {"schema_version": "1.0", "tool": "MM-ORG-031-mesh-generation", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in mesh_checks) else "FAIL", "profile": "draft", "inputs": inputs, "checks": mesh_checks, "metrics": {"meshes": metrics, "selected_3mf": record(selected_3mf)}, "limitations": ["STL units rely on the project millimetre contract."], "required_capabilities": ["mesh"]}
    write_json(VALIDATION / "mesh-generation-report.json", meshgen)
    interface_checks = [
        check("selected-device-slot", dock_interface["device_slot_at_shoe_mm"] == 13.0, "Selected cased-device gap is 13 mm"),
        check("selected-book-slot", dock_interface["book_slot_mm"] == 31.0, "Selected closed-book gap is 31 mm"),
        check("device-fit-pair", device_gauge_i["slot_widths_mm"] == [value + 1 for value in device_keys_i["tongue_widths_mm"]], "Five device keys receive 1 mm total clearance"),
        check("book-fit-pair", book_gauge_i["slot_widths_mm"] == [value + 1 for value in book_keys_i["tongue_widths_mm"]], "Three book keys receive 1 mm total clearance"),
        check("connector-keepout", dock_interface["connector_keepout_width_mm"] >= 40 and dock_interface["connector_vertical_clearance_mm"] >= 10, "Connector region retains horizontal and vertical access"),
        check("device-contact", dock_interface["rail_count"] == 4 and dock_interface["minimum_device_contact_overlap_mm"] >= 40, "Four rails overlap the minimum centered device width"),
        check("light-rejected", light_interface["light_variant"] and light_interface["wall_mm"] == 2.4, "Light variant is distinguishable and non-manufacturing"),
    ]
    interface = {"schema_version": "1.0", "tool": "MM-ORG-031-interface-validation", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in interface_checks) else "FAIL", "profile": "draft", "inputs": inputs, "checks": interface_checks, "metrics": {"interfaces": interfaces, "selected_device_case_thickness_mm": fit["selected_device_case_thickness_mm"], "selected_book_thickness_mm": fit["selected_book_thickness_mm"], "selected_clearance_per_side_mm": fit["clearance_per_side_mm"]}, "limitations": ["Printed clearance, controls, vents, connector access and combined device/book stability require physical checks."], "required_capabilities": []}
    write_json(VALIDATION / "interface-report.json", interface)
    outputs = [*step_paths.values(), virtual_step, *stl_paths.values(), selected_3mf, REPORTS / "nesting-layout.json", REPORTS / "optimization-geometric.json", REPORTS / "mesh-complexity.json", VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json"]
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "source_inputs": inputs, "outputs": [record(path) for path in outputs], "manufacturing_outputs": [str(stl_paths[name].relative_to(ROOT)) for name in order] + [str(selected_3mf.relative_to(ROOT))], "optimization_variants": [str(light_step.relative_to(ROOT)), str(light_stl.relative_to(ROOT))]})
    if any(report["status"] != "PASS" for report in [nesting, parametric, meshgen, interface]):
        raise RuntimeError("One or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "unique_meshes": len(metrics), "selected_objects": len(parts), "geometric_reduction_percent": geometric["selected"]["reduction_percent"]}, indent=2))


if __name__ == "__main__":
    main()
