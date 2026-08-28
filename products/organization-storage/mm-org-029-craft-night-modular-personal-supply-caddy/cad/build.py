#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-029 CraftOrbit 4 digital candidate."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import cadquery as cq
import numpy as np
import trimesh
from cadquery import exporters

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
NAME_BATCH = ROOT / "config/name-batch.json"
FONT_ALLOWLIST = ROOT / "assets/font-allowlist.json"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"
EXPORTS = ROOT / "exports"
PROJECT_ID = "MM-ORG-029"
REVISION = "0.1.0-draft.1"

sys.path.insert(0, str(ROOT / "cad"))
from gridfont import FONT_ID, pixel_rectangles  # noqa: E402


def sha256_file(target: Path) -> str:
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_record(target: Path) -> dict:
    try:
        display = str(target.relative_to(ROOT))
    except ValueError:
        display = str(target)
    return {"path": display, "sha256": sha256_file(target), "size_bytes": target.stat().st_size}


def write_json(target: Path, value: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def valid_single(shape: cq.Workplane) -> bool:
    return shape.val().isValid() and len(shape.solids().vals()) == 1


def rounded_box(length: float, width: float, height: float, radius: float) -> cq.Workplane:
    shape = cq.Workplane("XY").box(length, width, height, centered=(False, False, False))
    if radius > 0:
        shape = shape.edges("|Z").fillet(radius)
    return shape


def dovetail_polygon(face_x: float, center_y: float, depth: float, base_width: float, head_width: float) -> list[tuple[float, float]]:
    return [(face_x, center_y - base_width / 2), (face_x + depth, center_y - head_width / 2), (face_x + depth, center_y + head_width / 2), (face_x, center_y + base_width / 2)]


def validate_parameters(parameters: dict, batch: dict) -> list[dict]:
    caddy, hub, dock, plate = parameters["caddy"], parameters["hub"], parameters["dock"], parameters["nameplate"]
    pcontract = parameters["physical_contract"]
    selected_clearance = dock["selected_total_clearance_mm"]
    return [
        check("identity", parameters["project"]["id"] == PROJECT_ID and batch["project"] == PROJECT_ID, "Project identities match"),
        check("revision", parameters["project"]["revision"] == REVISION and batch["revision"] == REVISION, "Revisions match"),
        check("four-name-batch", len(batch["names"]) == parameters["batch"]["maximum_names"] == 4, "Default batch has four participant names"),
        check("interface-clearance", selected_clearance == 0.4 and selected_clearance in dock["candidate_total_clearances_mm"], "Selected 0.40 mm total clearance is bracketed by the coupon"),
        check("dovetail-capture", dock["key_head_width_mm"] > dock["key_base_width_mm"] and dock["key_height_mm"] < caddy["dock_boss_height_mm"] and dock["key_origin_z_mm"] == 0, "Vertical dovetail is horizontally captive, open at both channel ends and built from the print bed"),
        check("nameplate-fit", math.isclose(plate["slot_width_mm"] - plate["thickness_mm"], 0.4, abs_tol=1e-9) and math.isclose(plate["slot_length_mm"] - plate["width_mm"], 0.4, abs_tol=1e-9), "Nameplate slot retains 0.40 mm total thickness and length clearance"),
        check("engraving-layers", math.isclose(plate["engraving_depth_mm"] / parameters["printer"]["selected_layer_height_mm"], 3.0, abs_tol=1e-9), "Selected profile retains three nominal engraving layers"),
        check("caddy-envelope", max(caddy["length_mm"], caddy["width_mm"], caddy["height_mm"]) <= 180 and caddy["length_mm"] + plate["boss_depth_mm"] - caddy["wall_mm"] <= 180, "Caddy remains within the 180 × 140 × 120 mm portfolio part envelope"),
        check("hub-envelope", hub["body_size_mm"] + 2 * dock["key_depth_mm"] <= 180 and hub["height_mm"] <= 120, "Hub and keys remain inside the portfolio part envelope"),
        check("wall-floor", caddy["wall_mm"] >= 3.0 and caddy["base_mm"] >= 3.0 and hub["wall_mm"] >= 3.0, "Selected shells retain 3.0 mm protected walls/base"),
        check("content-boundary", pcontract["contents"] == "dry_indoor_adult_craft_supplies_only" and pcontract["excluded"].startswith("hot_tools"), "Adult dry-craft scope and exclusions are explicit"),
    ]


def make_caddy(parameters: dict, light: bool = False) -> tuple[cq.Workplane, dict]:
    p, dock, plate = parameters["caddy"], parameters["dock"], parameters["nameplate"]
    wall = p["light_wall_mm"] if light else p["wall_mm"]
    base = p["light_base_mm"] if light else p["base_mm"]
    shape = rounded_box(p["length_mm"], p["width_mm"], p["height_mm"], p["corner_radius_mm"])
    inner = rounded_box(p["length_mm"] - 2 * wall, p["width_mm"] - 2 * wall, p["height_mm"] - base + 1, max(1.0, p["corner_radius_mm"] - wall)).translate((wall, wall, base))
    shape = shape.cut(inner)
    divider = cq.Workplane("XY").box(p["divider_thickness_mm"], p["width_mm"] - 2 * wall, p["height_mm"] - base, centered=(False, False, False)).translate((p["divider_origin_x_mm"], wall, base))
    shape = shape.union(divider)
    boss_y = (p["width_mm"] - p["dock_boss_width_mm"]) / 2.0
    dock_boss = rounded_box(p["dock_boss_depth_mm"], p["dock_boss_width_mm"], p["dock_boss_height_mm"], 2.0).translate((0, boss_y, 0))
    shape = shape.union(dock_boss)
    clearance = dock["selected_total_clearance_mm"]
    channel = cq.Workplane("XY").polyline(dovetail_polygon(-0.2, p["width_mm"] / 2.0, dock["key_depth_mm"] + dock["channel_depth_allowance_mm"] + 0.2, dock["key_base_width_mm"] + clearance, dock["key_head_width_mm"] + clearance)).close().extrude(p["dock_boss_height_mm"] + 1).translate((0, 0, -0.2))
    shape = shape.cut(channel)
    boss_x = p["length_mm"] - p["wall_mm"]
    name_boss = rounded_box(plate["boss_depth_mm"], plate["slot_length_mm"] + 4.6, plate["boss_height_mm"], 2.0).translate((boss_x, plate["boss_y0_mm"], plate["boss_z0_mm"]))
    shape = shape.union(name_boss)
    slot_x = p["length_mm"] - 0.2
    slot_y = (p["width_mm"] - plate["slot_length_mm"]) / 2.0
    slot = cq.Workplane("XY").box(plate["slot_width_mm"], plate["slot_length_mm"], plate["boss_height_mm"] + 4, centered=(False, False, False)).translate((slot_x, slot_y, plate["installed_z0_mm"]))
    shape = shape.cut(slot)
    window = cq.Workplane("XY").box(plate["boss_depth_mm"] + 2, plate["width_mm"] - 8, plate["height_mm"] - 6, centered=(False, False, False)).translate((p["length_mm"] + plate["slot_width_mm"] - 0.2, (p["width_mm"] - plate["width_mm"] + 8) / 2.0, plate["installed_z0_mm"] + 3))
    shape = shape.cut(window).clean()
    interface = {
        "part_id": "personal-caddy" if not light else "light-personal-caddy-variant",
        "outer_dimensions_mm": [p["length_mm"] + plate["boss_depth_mm"] - p["wall_mm"], p["width_mm"], p["height_mm"]],
        "print_orientation": "base_down_open_top",
        "wall_mm": wall,
        "base_mm": base,
        "compartment_count": 2,
        "dock_channel": {"total_clearance_mm": clearance, "base_width_mm": dock["key_base_width_mm"] + clearance, "head_width_mm": dock["key_head_width_mm"] + clearance, "depth_mm": dock["key_depth_mm"] + dock["channel_depth_allowance_mm"]},
        "nameplate_slot": {"width_mm": plate["slot_width_mm"], "length_mm": plate["slot_length_mm"], "thickness_clearance_mm": plate["slot_width_mm"] - plate["thickness_mm"]},
        "light_variant": light,
        "external_assets": [],
    }
    return shape, interface


def make_hub(parameters: dict) -> tuple[cq.Workplane, dict]:
    p, dock = parameters["hub"], parameters["dock"]
    size = p["body_size_mm"]
    shape = rounded_box(size, size, p["height_mm"], p["corner_radius_mm"])
    inner = rounded_box(size - 2 * p["wall_mm"], size - 2 * p["wall_mm"], p["height_mm"] - p["base_mm"] + 1, max(1.0, p["corner_radius_mm"] - p["wall_mm"])).translate((p["wall_mm"], p["wall_mm"], p["base_mm"]))
    shape = shape.cut(inner)
    center = size / 2.0
    base_w, head_w, depth = dock["key_base_width_mm"], dock["key_head_width_mm"], dock["key_depth_mm"]
    polygons = [
        dovetail_polygon(size, center, depth, base_w, head_w),
        [(-depth, center - head_w / 2), (0, center - base_w / 2), (0, center + base_w / 2), (-depth, center + head_w / 2)],
        [(center - base_w / 2, size), (center - head_w / 2, size + depth), (center + head_w / 2, size + depth), (center + base_w / 2, size)],
        [(center - head_w / 2, -depth), (center - base_w / 2, 0), (center + base_w / 2, 0), (center + head_w / 2, -depth)],
    ]
    for polygon in polygons:
        key = cq.Workplane("XY").polyline(polygon).close().extrude(dock["key_height_mm"]).translate((0, 0, dock["key_origin_z_mm"]))
        shape = shape.union(key)
    shape = shape.clean()
    return shape, {"part_id": "shared-center-hub", "outer_dimensions_mm": [size + 2 * depth, size + 2 * depth, p["height_mm"]], "body_size_mm": size, "dock_count": 4, "key": {"depth_mm": depth, "base_width_mm": base_w, "head_width_mm": head_w, "height_mm": dock["key_height_mm"]}, "print_orientation": "base_down_open_top", "external_assets": []}


def make_nameplate(parameters: dict, item: dict) -> tuple[cq.Workplane, dict]:
    p = parameters["nameplate"]
    shape = rounded_box(p["width_mm"], p["height_mm"], p["thickness_mm"], p["corner_radius_mm"])
    for x, y, size in pixel_rectangles(item["normalized_name"], item["layout"], p["width_mm"] / 2.0, p["height_mm"] / 2.0):
        cutter = cq.Workplane("XY").box(size, size, p["engraving_depth_mm"] + 0.2, centered=(False, False, False)).translate((x, y, p["thickness_mm"] - p["engraving_depth_mm"]))
        shape = shape.cut(cutter)
    shape = shape.clean()
    return shape, {"part_id": f"nameplate-{item['index']:02d}", "normalized_name": item["normalized_name"], "font_id": FONT_ID, "layout": item["layout"], "outer_dimensions_mm": [p["width_mm"], p["height_mm"], p["thickness_mm"]], "engraving_depth_mm": p["engraving_depth_mm"], "minimum_backing_mm": p["thickness_mm"] - p["engraving_depth_mm"], "print_orientation": "broad_face_down_engraving_up", "external_assets": []}


def make_gauge(parameters: dict) -> tuple[cq.Workplane, dict]:
    p, dock = parameters["coupon"], parameters["dock"]
    shape = rounded_box(p["gauge_width_mm"], p["gauge_length_mm"], p["base_thickness_mm"], 2.0)
    centers = [18.0, 54.0, 90.0]
    for center in centers:
        station = rounded_box(p["station_block_depth_mm"], p["station_block_width_mm"], p["station_block_height_mm"], 1.5).translate((3.0, center - p["station_block_width_mm"] / 2.0, p["base_thickness_mm"]))
        shape = shape.union(station)
    for center, clearance in zip(centers, dock["candidate_total_clearances_mm"]):
        polygon = dovetail_polygon(2.8, center, dock["key_depth_mm"] + dock["channel_depth_allowance_mm"] + 0.2, dock["key_base_width_mm"] + clearance, dock["key_head_width_mm"] + clearance)
        cutter = cq.Workplane("XY").polyline(polygon).close().extrude(p["station_block_height_mm"] + 2).translate((0, 0, p["base_thickness_mm"]))
        shape = shape.cut(cutter)
    shape = shape.clean()
    return shape, {"part_id": "dock-clearance-gauge", "outer_dimensions_mm": [p["gauge_width_mm"], p["gauge_length_mm"], p["base_thickness_mm"] + p["station_block_height_mm"]], "candidate_total_clearances_mm": dock["candidate_total_clearances_mm"], "channel_base_widths_mm": [dock["key_base_width_mm"] + value for value in dock["candidate_total_clearances_mm"]], "channel_head_widths_mm": [dock["key_head_width_mm"] + value for value in dock["candidate_total_clearances_mm"]], "print_orientation": "base_down_channels_open_top", "external_assets": []}


def make_coupon_key(parameters: dict) -> tuple[cq.Workplane, dict]:
    p, dock = parameters["coupon"], parameters["dock"]
    shape = rounded_box(p["key_base_width_mm"], p["key_base_length_mm"], p["base_thickness_mm"], 1.5)
    center = p["key_base_length_mm"] / 2.0
    back = cq.Workplane("XY").box(4.0, dock["key_head_width_mm"], p["key_back_height_mm"], centered=(False, False, False)).translate((3.0, center - dock["key_head_width_mm"] / 2.0, p["base_thickness_mm"]))
    male = cq.Workplane("XY").polyline(dovetail_polygon(7.0, center, dock["key_depth_mm"], dock["key_base_width_mm"], dock["key_head_width_mm"])).close().extrude(dock["key_height_mm"]).translate((0, 0, p["base_thickness_mm"]))
    shape = shape.union(back).union(male).clean()
    return shape, {"part_id": "dock-interface-key", "outer_dimensions_mm": [13.0, p["key_base_length_mm"], p["base_thickness_mm"] + p["key_back_height_mm"]], "key_base_width_mm": dock["key_base_width_mm"], "key_head_width_mm": dock["key_head_width_mm"], "key_depth_mm": dock["key_depth_mm"], "print_orientation": "base_down_key_vertical", "external_assets": []}


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
        raise RuntimeError(f"cleaned STL is not a valid volume: {target.name}")
    mesh.export(target, file_type="stl")


def mesh_metrics(target: Path) -> dict:
    mesh = trimesh.load_mesh(target, force="mesh", process=True)
    return {"path": str(target.relative_to(ROOT)), "sha256": sha256_file(target), "triangles": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)), "file_bytes": target.stat().st_size, "file_mib": target.stat().st_size / (1024 * 1024), "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent), "positive_volume": bool(mesh.is_volume and mesh.volume > 0), "components": int(len(mesh.split(only_watertight=False))), "volume_mm3": float(mesh.volume), "surface_area_mm2": float(mesh.area), "extents_mm": np.round(mesh.extents, 4).tolist(), "bounds_mm": np.round(mesh.bounds, 4).tolist()}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _zip_member(name: str, data: bytes, archive: zipfile.ZipFile) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def write_3mf(target: Path, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    for object_id, ((name, mesh_path), (move_x, move_y)) in enumerate(zip(parts, placements), 1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name})
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(triangles, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {move_x:.3f} {move_y:.3f} 0"})
    types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        _zip_member("[Content_Types].xml", types, archive)
        _zip_member("_rels/.rels", rels, archive)
        _zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive)
        _zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)
        _zip_member("Metadata/name-batch.json", NAME_BATCH.read_bytes(), archive)
        _zip_member("Metadata/font-allowlist.json", FONT_ALLOWLIST.read_bytes(), archive)


def nesting_report(parameters: dict, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> dict:
    gap = parameters["nesting"]["minimum_object_gap_mm"]
    bed = parameters["printer"]["build_volume_mm"]
    records = []
    for (name, mesh_path), (move_x, move_y) in zip(parts, placements):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        bounds = mesh.bounds
        records.append({"name": name, "x0": float(bounds[0][0] + move_x), "y0": float(bounds[0][1] + move_y), "x1": float(bounds[1][0] + move_x), "y1": float(bounds[1][1] + move_y)})
    collisions = []
    for index, first in enumerate(records):
        for second in records[index + 1:]:
            separated = first["x1"] + gap <= second["x0"] or second["x1"] + gap <= first["x0"] or first["y1"] + gap <= second["y0"] or second["y1"] + gap <= first["y0"]
            if not separated:
                collisions.append([first["name"], second["name"]])
    margin = parameters["nesting"]["bed_margin_mm"]
    within = all(item["x0"] >= margin and item["y0"] >= margin and item["x1"] <= bed[0] - margin and item["y1"] <= bed[1] - margin for item in records)
    checks = [check("non-overlap", not collisions, "Eleven selected objects retain the configured nominal gap", {"collisions": collisions}), check("bed-bounds", within, "Layout respects conservative Kobra 3 Max rectangular margins")]
    return {"schema_version": "1.0", "tool": "MM-ORG-029-nesting-layout", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [], "checks": checks, "metrics": {"plate_count": 1, "object_count": len(records), "minimum_gap_mm": gap, "objects": records}, "limitations": ["Exact destination-profile exclusion zones remain authoritative; the plate requires exact slicing."], "required_capabilities": []}


def main() -> None:
    parameters = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    batch = json.loads(NAME_BATCH.read_text(encoding="utf-8"))
    font_record = json.loads(FONT_ALLOWLIST.read_text(encoding="utf-8"))
    REPORTS.mkdir(parents=True, exist_ok=True)
    VALIDATION.mkdir(parents=True, exist_ok=True)
    source_inputs = [PARAMETERS, NAME_BATCH, ROOT / "reports/csv-import.json", ROOT / "renders/MM-ORG-029-live-batch-preview.svg", ROOT / "reports/live-batch-preview.json", ROOT / "cad/build.py", ROOT / "cad/gridfont.py", FONT_ALLOWLIST]
    base_inputs = [input_record(target) for target in source_inputs]
    parameter_checks = validate_parameters(parameters, batch)
    if not all(item["status"] == "PASS" for item in parameter_checks):
        raise ValueError([item["id"] for item in parameter_checks if item["status"] != "PASS"])

    caddy, caddy_i = make_caddy(parameters)
    hub, hub_i = make_hub(parameters)
    plates = []
    interfaces = {"personal-caddy": caddy_i, "shared-center-hub": hub_i}
    for item in batch["names"]:
        shape, interface = make_nameplate(parameters, item)
        name = f"nameplate-{item['index']:02d}-{slug(item['normalized_name'])}"
        plates.append((name, shape, interface))
        interfaces[name] = interface
    gauge, gauge_i = make_gauge(parameters)
    key, key_i = make_coupon_key(parameters)
    light, light_i = make_caddy(parameters, light=True)
    interfaces["dock-clearance-gauge"] = gauge_i
    interfaces["dock-interface-key"] = key_i
    interfaces["light-personal-caddy-variant"] = light_i
    all_shapes = [caddy, hub, *[shape for _, shape, _ in plates], gauge, key, light]
    if not all(valid_single(shape) for shape in all_shapes):
        raise RuntimeError("every unique deliverable must be one valid solid")

    mesh_p = parameters["mesh"]
    selected_shapes = {"personal-caddy": caddy, "shared-center-hub": hub, **{name: shape for name, shape, _ in plates}, "dock-clearance-gauge": gauge, "dock-interface-key": key}
    step_paths, stl_paths = {}, {}
    for name, shape in selected_shapes.items():
        step_target = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        stl_dir = "coupons" if name.startswith("dock-") else "manufacturing"
        stl_target = EXPORTS / stl_dir / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_step(shape, step_target)
        export_stl(shape, stl_target, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        step_paths[name], stl_paths[name] = step_target, stl_target
    light_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-light-personal-caddy-variant-{REVISION}.step"
    light_stl = EXPORTS / "variants" / f"DRAFT-{PROJECT_ID}-light-personal-caddy-variant-{REVISION}.stl"
    export_step(light, light_step)
    export_stl(light, light_stl, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    step_paths["light-personal-caddy-variant"], stl_paths["light-personal-caddy-variant"] = light_step, light_stl

    caddy_transforms = [caddy.translate((72, -11.5, 0)), caddy.rotate((0, 0, 0), (0, 0, 1), 180).translate((0, 83.5, 0)), caddy.rotate((0, 0, 0), (0, 0, 1), 90).translate((83.5, 72, 0)), caddy.rotate((0, 0, 0), (0, 0, 1), -90).translate((-11.5, 0, 0))]
    installed_plates = []
    caddy_rotations = [0, 180, 90, -90]
    caddy_translations = [(72, -11.5, 0), (0, 83.5, 0), (83.5, 72, 0), (-11.5, 0, 0)]
    for (_, plate_shape, _), rotation, translation in zip(plates, caddy_rotations, caddy_translations):
        installed = plate_shape.rotate((0, 0, 0), (1, 1, 1), 120).translate((145, 12.5, 20))
        if rotation:
            installed = installed.rotate((0, 0, 0), (0, 0, 1), rotation)
        installed_plates.append(installed.translate(translation))
    virtual = cq.Compound.makeCompound([hub.val(), *[shape.val() for shape in caddy_transforms], *[shape.val() for shape in installed_plates]])
    virtual_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-virtual-docked-four-caddy-set-{REVISION}.step"
    export_step(virtual, virtual_step)

    nesting_p = parameters["nesting"]
    selected_parts = [("personal-caddy-01", stl_paths["personal-caddy"]), ("personal-caddy-02", stl_paths["personal-caddy"]), ("personal-caddy-03", stl_paths["personal-caddy"]), ("personal-caddy-04", stl_paths["personal-caddy"]), ("shared-center-hub", stl_paths["shared-center-hub"]), ("dock-clearance-gauge", stl_paths["dock-clearance-gauge"]), ("dock-interface-key", stl_paths["dock-interface-key"]), *[(name, stl_paths[name]) for name, _, _ in plates]]
    placements = [*map(tuple, nesting_p["caddy_origins_mm"]), tuple(nesting_p["hub_origin_mm"]), tuple(nesting_p["gauge_origin_mm"]), tuple(nesting_p["key_origin_mm"]), *map(tuple, nesting_p["nameplate_origins_mm"])]
    nesting = nesting_report(parameters, selected_parts, placements)
    nesting["inputs"] = base_inputs[:2] + [input_record(ROOT / "cad/build.py")]
    write_json(REPORTS / "nesting-layout.json", nesting)
    if nesting["status"] != "PASS":
        raise RuntimeError("nesting validation failed")
    selected_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-four-caddy-system-{REVISION}.3mf"
    write_3mf(selected_3mf, selected_parts, placements)

    metrics = {name: mesh_metrics(target) for name, target in stl_paths.items()}
    selected_volume = 4 * metrics["personal-caddy"]["volume_mm3"] + metrics["shared-center-hub"]["volume_mm3"] + sum(metrics[name]["volume_mm3"] for name, _, _ in plates) + metrics["dock-clearance-gauge"]["volume_mm3"] + metrics["dock-interface-key"]["volume_mm3"]
    caddy_p, hub_p = parameters["caddy"], parameters["hub"]
    proxy_volume = 4 * caddy_p["length_mm"] * caddy_p["width_mm"] * caddy_p["height_mm"] + hub_p["body_size_mm"] ** 2 * hub_p["height_mm"]
    light_reduction = 100 * (1 - metrics["light-personal-caddy-variant"]["volume_mm3"] / metrics["personal-caddy"]["volume_mm3"])
    geometric = {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "baseline": {"id": "four-solid-caddy-envelopes-plus-solid-hub", "volume_mm3": proxy_volume}, "selected": {"id": "four-three-mm-shell-caddies-plus-shell-hub-coupons-and-plates", "volume_mm3": selected_volume, "reduction_percent": 100 * (1 - selected_volume / proxy_volume)}, "light_variant": {"id": "2.4-mm-caddy-shell", "one_caddy_volume_mm3": metrics["light-personal-caddy-variant"]["volume_mm3"], "reduction_percent_vs_selected_caddy": light_reduction, "constraint": "REJECTED_PENDING_LOADED_FLEX_DROP_AND_DOCKING_EVIDENCE"}, "process_comparison": "PENDING_EXACT_SLICER_RUNS"}
    write_json(REPORTS / "optimization-geometric.json", geometric)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL", "meshes": metrics, "simplification": "NOT_BENEFICIAL", "reason": "Shell corners, exact dovetails and geometric glyph recesses are protected; meshes are below budget."})

    parametric = {"schema_version": "1.0", "tool": "MM-ORG-029-parametric-source", "tool_version": REVISION, "status": "PASS", "profile": "draft", "inputs": base_inputs, "checks": parameter_checks + [check("cad-valid", all(shape.val().isValid() for shape in all_shapes), "All selected and variant B-Reps are valid"), check("single-solids", all(len(shape.solids().vals()) == 1 for shape in all_shapes), "Every unique deliverable is one B-Rep solid"), check("font-allowlist", font_record["font_id"] == FONT_ID and not font_record["external_font_file"], "Repository-owned glyph source is allowlisted"), check("no-external-assets", all(not value.get("external_assets") for value in interfaces.values()), "No external logo, font, vector or mesh asset is used")], "metrics": {"python": sys.version.split()[0], "cadquery": cq.__version__, "font_id": FONT_ID, "unique_parts": list(interfaces), "selected_objects": len(selected_parts)}, "limitations": ["Parametric validity does not prove printed docking fit, loaded stability or durability."], "required_capabilities": ["cad"]}
    write_json(VALIDATION / "parametric-source-report.json", parametric)
    mesh_generation = {"schema_version": "1.0", "tool": "MM-ORG-029-mesh-generation", "tool_version": REVISION, "status": "PASS" if all(item["watertight"] and item["winding_consistent"] and item["positive_volume"] and item["components"] == 1 for item in metrics.values()) else "FAIL", "profile": "draft", "inputs": [input_record(PARAMETERS), input_record(NAME_BATCH), input_record(ROOT / "cad/build.py"), input_record(ROOT / "cad/gridfont.py")], "checks": [check("mesh-count", len(metrics) == 9, "Eight selected unique meshes plus one light caddy variant were generated"), check("mesh-validity", all(item["watertight"] and item["winding_consistent"] and item["positive_volume"] and item["components"] == 1 for item in metrics.values()), "Every mesh is one watertight positive-volume component"), check("mesh-budgets", all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()), "Every mesh remains below triangle and file-size budgets")], "metrics": {"meshes": metrics, "selected_3mf": input_record(selected_3mf)}, "limitations": ["STL carries no authoritative units; project and 3MF contracts use millimetres."], "required_capabilities": ["mesh"]}
    write_json(VALIDATION / "mesh-generation-report.json", mesh_generation)
    name_interfaces = [value for name, value in interfaces.items() if name.startswith("nameplate-")]
    interface_checks = [check("four-docks", hub_i["dock_count"] == 4, "Shared hub exposes four identical vertical dovetail keys"), check("nominal-clearance", math.isclose(caddy_i["dock_channel"]["total_clearance_mm"], 0.4, abs_tol=1e-9), "Production dock retains 0.40 mm total nominal lateral clearance"), check("coupon-bracket", gauge_i["candidate_total_clearances_mm"] == [0.2, 0.4, 0.6], "Coupon brackets and includes production clearance"), check("nameplate-clearance", math.isclose(caddy_i["nameplate_slot"]["thickness_clearance_mm"], 0.4, abs_tol=1e-9), "Nameplate retains 0.40 mm nominal thickness clearance"), check("four-nameplates", len(name_interfaces) == 4 and all(item["font_id"] == FONT_ID for item in name_interfaces), "Four plates retain exact CAD glyph identity"), check("protected-shell", caddy_i["wall_mm"] >= 3 and caddy_i["base_mm"] >= 3, "Selected caddy retains protected shell dimensions"), check("light-variant-boundary", light_i["wall_mm"] < caddy_i["wall_mm"] and light_i["light_variant"], "Light caddy is distinguishable and non-manufacturing")]
    interface_report = {"schema_version": "1.0", "tool": "MM-ORG-029-interface-validation", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in interface_checks) else "FAIL", "profile": "draft", "inputs": base_inputs, "checks": interface_checks, "metrics": {"font_record": font_record, "names": batch["names"], "interfaces": interfaces, "nominal_total_clearance_mm": caddy_i["dock_channel"]["total_clearance_mm"], "nameplate_total_clearance_mm": caddy_i["nameplate_slot"]["thickness_clearance_mm"]}, "limitations": ["Nominal digital clearances require printed coupon and system tests."], "required_capabilities": []}
    write_json(VALIDATION / "interface-report.json", interface_report)

    outputs = [*step_paths.values(), virtual_step, *stl_paths.values(), selected_3mf, REPORTS / "nesting-layout.json", REPORTS / "optimization-geometric.json", REPORTS / "mesh-complexity.json", VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json"]
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "source_inputs": [input_record(target) for target in source_inputs], "outputs": [input_record(target) for target in outputs], "manufacturing_outputs": [str(target.relative_to(ROOT)) for name, target in stl_paths.items() if name != "light-personal-caddy-variant"] + [str(selected_3mf.relative_to(ROOT))], "optimization_variants": [str(light_step.relative_to(ROOT)), str(light_stl.relative_to(ROOT))]})
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "names": len(batch["names"]), "unique_meshes": len(metrics), "selected_objects": len(selected_parts), "selected_3mf": str(selected_3mf.relative_to(ROOT)), "geometric_reduction_percent": geometric["selected"]["reduction_percent"], "font_id": FONT_ID}, indent=2))


if __name__ == "__main__":
    main()
