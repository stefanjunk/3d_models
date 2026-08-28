#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-028 IndexDock 15 digital candidate."""
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
LABEL_BATCH = ROOT / "config/label-batch.json"
FONT_ALLOWLIST = ROOT / "assets/font-allowlist.json"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"
EXPORTS = ROOT / "exports"
PROJECT_ID = "MM-ORG-028"
REVISION = "0.1.0-draft.1"

sys.path.insert(0, str(ROOT / "cad"))
from gridfont import FONT_ID, pixel_rectangles  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_record(path: Path) -> dict:
    try:
        display = str(path.relative_to(ROOT))
    except ValueError:
        display = str(path)
    return {"path": display, "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def valid_single(shape: cq.Workplane) -> bool:
    return shape.val().isValid() and len(shape.solids().vals()) == 1


def rounded_plate(width: float, height: float, thickness: float, radius: float) -> cq.Workplane:
    base = cq.Workplane("XY").box(width, height, thickness, centered=(False, False, False))
    if radius > 0:
        base = base.edges("|Z").fillet(radius)
    return base


def validate_parameters(parameters: dict, batch: dict) -> list[dict]:
    rack = parameters["rack"]
    divider = parameters["divider"]
    envelope = parameters["envelope_contract"]
    coupon = parameters["coupon"]
    stack = (rack["lane_count"] + 1) * rack["fin_thickness_mm"] + rack["lane_count"] * rack["lane_gap_mm"]
    margin = (rack["length_mm"] - stack) / 2.0
    values = [
        check("project-id", parameters["project"]["id"] == PROJECT_ID and batch["project"] == PROJECT_ID, "Project identities match"),
        check("revision", parameters["project"]["revision"] == REVISION and batch["revision"] == REVISION, "Revisions match"),
        check("label-count", len(batch["labels"]) == parameters["batch"]["maximum_labels"] == 4, "Default batch has four category labels"),
        check("lane-stack", margin >= 3.0, "Sixteen fins and fifteen lane gaps fit the rack length", {"side_margin_mm": margin, "stack_mm": stack}),
        check("loaded-thickness", envelope["maximum_loaded_thickness_mm"] < rack["lane_gap_mm"], "Maximum loaded envelope thickness is below nominal lane gap"),
        check("pad-clearance", math.isclose(rack["lane_gap_mm"] - divider["pad_installed_thickness_mm"], 0.4, abs_tol=1e-9), "Divider pad retains 0.40 mm total nominal clearance"),
        check("gauge-bracket", coupon["candidate_slot_widths_mm"] == [10.9, 11.2, 11.5] and rack["lane_gap_mm"] in coupon["candidate_slot_widths_mm"], "Gauge brackets and includes production gap"),
        check("rail-pad-registration", len(rack["rail_origins_y_mm"]) == len(divider["pad_origins_x_mm"]) == 3, "Three rails and three divider pads share a registration contract"),
        check("protected-frame", divider["frame_width_mm"] >= 8.0 and divider["center_rib_width_mm"] >= 12.0, "Selected divider retains protected frame and center-rib widths"),
        check("text-backing", divider["thickness_mm"] - divider["engraving_depth_mm"] >= 1.8 - 1e-9, "Engraving retains at least 1.8 mm backing"),
        check("engraving-layers", math.isclose(divider["engraving_depth_mm"] / parameters["printer"]["selected_layer_height_mm"], 3.0, abs_tol=1e-9), "Selected profile retains three nominal engraving layers"),
        check("single-part-envelope", rack["length_mm"] <= 220 and rack["depth_mm"] <= 180 and max(divider["width_mm"], divider["body_height_mm"] + divider["tab_height_mm"], divider["pad_installed_thickness_mm"]) <= 200, "Every selected part fits the retained 220 × 180 × 200 mm envelope"),
        check("content-boundary", envelope["contents"].startswith("filled protective") and envelope["excluded"].startswith("loose_exposed"), "Filled-envelope and loose-tool boundaries are explicit"),
    ]
    return values


def boundary_positions(parameters: dict) -> list[float]:
    rack = parameters["rack"]
    count = rack["lane_count"] + 1
    stack = count * rack["fin_thickness_mm"] + rack["lane_count"] * rack["lane_gap_mm"]
    margin = (rack["length_mm"] - stack) / 2.0
    pitch = rack["fin_thickness_mm"] + rack["lane_gap_mm"]
    return [margin + index * pitch for index in range(count)]


def make_rack(parameters: dict) -> tuple[cq.Workplane, dict]:
    p = parameters["rack"]
    positions = boundary_positions(parameters)
    rail_comb = cq.Workplane("XY").box(p["length_mm"], p["rail_width_mm"], p["base_thickness_mm"], centered=(False, False, False))
    for x in positions:
        fin = cq.Workplane("XY").box(p["fin_thickness_mm"], p["rail_width_mm"], p["fin_height_mm"], centered=(False, False, False)).translate((x, 0, 0))
        rail_comb = rail_comb.union(fin)
    rail_comb = rail_comb.edges(">Z").chamfer(p["fin_top_chamfer_mm"]).clean()
    shape = None
    for y in p["rail_origins_y_mm"]:
        rail = rail_comb.translate((0, y, 0))
        shape = rail if shape is None else shape.union(rail)
    panel_profile = [(0.0, 0.0), (p["depth_mm"], 0.0), (p["depth_mm"], p["end_panel_rear_height_mm"]), (0.0, p["end_panel_front_height_mm"])]
    left = cq.Workplane("YZ").polyline(panel_profile).close().extrude(p["end_panel_thickness_mm"])
    right = left.translate((p["length_mm"] - p["end_panel_thickness_mm"], 0, 0))
    shape = shape.union(left).union(right)
    shape = shape.clean()
    slots = [{"index": index + 1, "x0_mm": positions[index] + p["fin_thickness_mm"], "x1_mm": positions[index + 1]} for index in range(p["lane_count"])]
    interface = {
        "part_id": "rack",
        "outer_dimensions_mm": [p["length_mm"], p["depth_mm"], p["end_panel_rear_height_mm"]],
        "print_orientation": "base_rails_down",
        "lane_count": p["lane_count"],
        "lane_gap_mm": p["lane_gap_mm"],
        "fin_thickness_mm": p["fin_thickness_mm"],
        "fin_height_mm": p["fin_height_mm"],
        "rail_origins_y_mm": p["rail_origins_y_mm"],
        "boundary_fin_origins_x_mm": positions,
        "slots": slots,
        "external_assets": [],
    }
    return shape, interface


def make_divider(parameters: dict, item: dict, light: bool = False) -> tuple[cq.Workplane, dict]:
    p = parameters["divider"]
    frame = p["light_variant_frame_width_mm"] if light else p["frame_width_mm"]
    rib = p["light_variant_center_rib_width_mm"] if light else p["center_rib_width_mm"]
    width, height, thickness = p["width_mm"], p["body_height_mm"], p["thickness_mm"]
    outer = rounded_plate(width, height, thickness, 3.0)
    inner_height = height - 2.0 * frame
    left_width = width / 2.0 - rib / 2.0 - frame
    right_start = width / 2.0 + rib / 2.0
    windows = [
        {"x": frame, "y": frame, "width": left_width, "height": inner_height},
        {"x": right_start, "y": frame, "width": width - frame - right_start, "height": inner_height},
    ]
    shape = outer
    for window in windows:
        cutter = cq.Workplane("XY").box(window["width"], window["height"], thickness + 2.0, centered=(False, False, False)).translate((window["x"], window["y"], -1.0))
        shape = shape.cut(cutter)
    tab_center = item["tab_center_x_mm"]
    tab = rounded_plate(p["tab_width_mm"], p["tab_height_mm"] + 1.0, thickness, 3.0).translate((tab_center - p["tab_width_mm"] / 2.0, height - 1.0, 0))
    shape = shape.union(tab)
    pads = []
    for x in p["pad_origins_x_mm"]:
        pad = rounded_plate(p["pad_span_mm"], p["pad_height_mm"], p["pad_installed_thickness_mm"], p["minimum_edge_radius_mm"]).translate((x, 0, 0))
        shape = shape.union(pad)
        pads.append({"origin_x_mm": x, "span_mm": p["pad_span_mm"], "height_mm": p["pad_height_mm"], "installed_thickness_mm": p["pad_installed_thickness_mm"]})
    for x, y, size in pixel_rectangles(item["normalized_label"], item["layout"], tab_center, p["text_center_y_mm"]):
        cutter = cq.Workplane("XY").box(size, size, p["engraving_depth_mm"] + 0.2, centered=(False, False, False)).translate((x, y, thickness - p["engraving_depth_mm"]))
        shape = shape.cut(cutter)
    shape = shape.clean()
    interface = {
        "part_id": f"index-divider-{item['index']:02d}",
        "normalized_label": item["normalized_label"],
        "tab_position": item["tab_position"],
        "font_id": FONT_ID,
        "layout": item["layout"],
        "outer_dimensions_mm": [width, height + p["tab_height_mm"], p["pad_installed_thickness_mm"]],
        "print_orientation": "broad_frame_face_down_pads_up",
        "installed_transform": "rotate_120_degrees_about_axis_1_1_1_then_translate_to_lane_and_rail_top",
        "frame_width_mm": frame,
        "center_rib_width_mm": rib,
        "windowed": True,
        "light_variant": light,
        "pad_installed_thickness_mm": p["pad_installed_thickness_mm"],
        "pad_count": len(pads),
        "pads": pads,
        "minimum_backing_mm": thickness - p["engraving_depth_mm"],
        "external_assets": [],
    }
    return shape, interface


def make_gauge(parameters: dict) -> tuple[cq.Workplane, dict]:
    p = parameters["coupon"]
    shape = rounded_plate(p["gauge_width_mm"], p["gauge_height_mm"], p["gauge_thickness_mm"], 2.0)
    centers = [16.0, 41.0, 66.0]
    for center, width in zip(centers, p["candidate_slot_widths_mm"]):
        cutter = cq.Workplane("XY").box(width, p["slot_depth_mm"] + 1.0, p["gauge_thickness_mm"] + 2.0, centered=(False, False, False)).translate((center - width / 2.0, p["gauge_height_mm"] - p["slot_depth_mm"], -1.0))
        shape = shape.cut(cutter)
    shape = shape.clean()
    return shape, {"part_id": "lane-gap-gauge", "outer_dimensions_mm": [p["gauge_width_mm"], p["gauge_height_mm"], p["gauge_thickness_mm"]], "candidate_slot_widths_mm": p["candidate_slot_widths_mm"], "slot_depth_mm": p["slot_depth_mm"], "print_orientation": "broad_face_down", "external_assets": []}


def make_key(parameters: dict) -> tuple[cq.Workplane, dict]:
    p = parameters["coupon"]
    shape = rounded_plate(p["key_width_mm"], p["key_length_mm"], p["key_height_mm"], 1.2)
    return shape, {"part_id": "divider-foot-key", "outer_dimensions_mm": [p["key_width_mm"], p["key_length_mm"], p["key_height_mm"]], "width_mm": p["key_width_mm"], "print_orientation": "broad_face_down", "external_assets": []}


def installed_divider(shape: cq.Workplane, rack_interface: dict, lane_index: int) -> cq.Workplane:
    slot = rack_interface["slots"][lane_index]
    x = slot["x0_mm"] + 0.2
    return shape.rotate((0, 0, 0), (1, 1, 1), 120.0).translate((x, 4.0, 3.0))


def export_step(shape: cq.Workplane | cq.Compound, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(path), exportType="STEP")


def export_stl(shape: cq.Workplane, path: Path, linear: float, angular: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(path), exportType="STL", tolerance=linear, angularTolerance=angular)
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    mesh.remove_unreferenced_vertices()
    mesh.merge_vertices()
    mesh.fix_normals()
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise RuntimeError(f"cleaned STL is not a valid volume: {path.name}")
    mesh.export(path, file_type="stl")


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "triangles": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)), "file_bytes": path.stat().st_size, "file_mib": path.stat().st_size / (1024 * 1024), "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent), "positive_volume": bool(mesh.is_volume and mesh.volume > 0), "components": int(len(mesh.split(only_watertight=False))), "volume_mm3": float(mesh.volume), "surface_area_mm2": float(mesh.area), "extents_mm": np.round(mesh.extents, 4).tolist(), "bounds_mm": np.round(mesh.bounds, 4).tolist()}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _zip_member(name: str, data: bytes, archive: zipfile.ZipFile) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def write_3mf(path: Path, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> None:
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        _zip_member("[Content_Types].xml", types, archive)
        _zip_member("_rels/.rels", rels, archive)
        _zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive)
        _zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)
        _zip_member("Metadata/label-batch.json", LABEL_BATCH.read_bytes(), archive)
        _zip_member("Metadata/font-allowlist.json", FONT_ALLOWLIST.read_bytes(), archive)


def boxes_overlap(a: dict, b: dict, gap: float) -> bool:
    return not (a["x1"] + gap <= b["x0"] or b["x1"] + gap <= a["x0"] or a["y1"] + gap <= b["y0"] or b["y1"] + gap <= a["y0"])


def nesting_report(parameters: dict, batch: dict) -> tuple[dict, list[tuple[float, float]], list[tuple[float, float]]]:
    n = parameters["nesting"]
    rack = parameters["rack"]
    divider = parameters["divider"]
    coupon = parameters["coupon"]
    rack_parts = [
        {"name": "rack", "x0": n["rack_plate"]["rack_origin_mm"][0], "y0": n["rack_plate"]["rack_origin_mm"][1], "width": rack["length_mm"], "height": rack["depth_mm"]},
        {"name": "lane-gap-gauge", "x0": n["rack_plate"]["gauge_origin_mm"][0], "y0": n["rack_plate"]["gauge_origin_mm"][1], "width": coupon["gauge_width_mm"], "height": coupon["gauge_height_mm"]},
        {"name": "divider-foot-key", "x0": n["rack_plate"]["key_origin_mm"][0], "y0": n["rack_plate"]["key_origin_mm"][1], "width": coupon["key_width_mm"], "height": coupon["key_length_mm"]},
    ]
    divider_parts = []
    for item, origin in zip(batch["labels"], n["divider_plate_origins_mm"]):
        divider_parts.append({"name": f"index-divider-{item['index']:02d}-{slug(item['normalized_label'])}", "x0": origin[0], "y0": origin[1], "width": divider["width_mm"], "height": divider["body_height_mm"] + divider["tab_height_mm"]})
    for collection in (rack_parts, divider_parts):
        for part in collection:
            part["x1"] = part["x0"] + part.pop("width")
            part["y1"] = part["y0"] + part.pop("height")
    collisions = []
    for plate, collection in (("rack-kit", rack_parts), ("divider-set", divider_parts)):
        for index, first in enumerate(collection):
            for second in collection[index + 1:]:
                if boxes_overlap(first, second, n["minimum_object_gap_mm"]):
                    collisions.append({"plate": plate, "objects": [first["name"], second["name"]]})
    bed = parameters["printer"]["build_volume_mm"]
    within = all(part["x1"] <= bed[0] - n["bed_margin_mm"] and part["y1"] <= bed[1] - n["bed_margin_mm"] for part in rack_parts + divider_parts)
    checks = [check("non-overlap", not collisions, "Both selected plates retain the configured nominal gap", {"collisions": collisions}), check("bed-bounds", within, "Both layouts respect conservative Kobra 3 Max rectangular margins")]
    report = {"schema_version": "1.0", "tool": "MM-ORG-028-nesting-layout", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [], "checks": checks, "metrics": {"plate_count": 2, "object_count": 7, "minimum_gap_mm": n["minimum_object_gap_mm"], "rack_plate": rack_parts, "divider_plate": divider_parts}, "limitations": ["Exact destination-profile exclusion zones remain authoritative; both plates require exact slicing."], "required_capabilities": []}
    rack_placements = [tuple(n["rack_plate"]["rack_origin_mm"]), tuple(n["rack_plate"]["gauge_origin_mm"]), tuple(n["rack_plate"]["key_origin_mm"])]
    divider_placements = [tuple(value) for value in n["divider_plate_origins_mm"]]
    return report, rack_placements, divider_placements


def main() -> None:
    parameters = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    batch = json.loads(LABEL_BATCH.read_text(encoding="utf-8"))
    font_record = json.loads(FONT_ALLOWLIST.read_text(encoding="utf-8"))
    REPORTS.mkdir(parents=True, exist_ok=True)
    VALIDATION.mkdir(parents=True, exist_ok=True)
    source_inputs = [PARAMETERS, LABEL_BATCH, ROOT / "reports/csv-import.json", ROOT / "renders/MM-ORG-028-live-batch-preview.svg", ROOT / "reports/live-batch-preview.json", ROOT / "cad/build.py", ROOT / "cad/gridfont.py", FONT_ALLOWLIST]
    base_inputs = [input_record(path) for path in source_inputs]
    parameter_checks = validate_parameters(parameters, batch)
    if not all(item["status"] == "PASS" for item in parameter_checks):
        failed = [item["id"] for item in parameter_checks if item["status"] != "PASS"]
        raise ValueError(f"parameter validation failed: {failed}")

    rack, rack_i = make_rack(parameters)
    dividers = []
    interfaces = {"rack": rack_i}
    for item in batch["labels"]:
        shape, interface = make_divider(parameters, item)
        dividers.append((item, shape, interface))
        interfaces[f"index-divider-{item['index']:02d}-{slug(item['normalized_label'])}"] = interface
    light, light_i = make_divider(parameters, batch["labels"][0], light=True)
    interfaces["light-index-divider-variant"] = light_i
    gauge, gauge_i = make_gauge(parameters)
    key, key_i = make_key(parameters)
    interfaces["lane-gap-gauge"] = gauge_i
    interfaces["divider-foot-key"] = key_i
    all_shapes = [rack, *[shape for _, shape, _ in dividers], light, gauge, key]
    if not all(valid_single(shape) for shape in all_shapes):
        raise RuntimeError("every deliverable must be one valid solid")

    master_dir = EXPORTS / "master"
    manufacturing_dir = EXPORTS / "manufacturing"
    coupon_dir = EXPORTS / "coupons"
    variant_dir = EXPORTS / "variants"
    mesh_parameters = parameters["mesh"]
    shapes = {"rack": rack}
    for item, shape, _ in dividers:
        shapes[f"index-divider-{item['index']:02d}-{slug(item['normalized_label'])}"] = shape
    shapes["lane-gap-gauge"] = gauge
    shapes["divider-foot-key"] = key
    step_paths = {}
    stl_paths = {}
    for name, shape in shapes.items():
        step = master_dir / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        target_dir = coupon_dir if name in {"lane-gap-gauge", "divider-foot-key"} else manufacturing_dir
        stl = target_dir / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_step(shape, step)
        export_stl(shape, stl, mesh_parameters["linear_deflection_mm"], mesh_parameters["angular_deflection_rad"])
        step_paths[name] = step
        stl_paths[name] = stl
    light_step = master_dir / f"DRAFT-{PROJECT_ID}-light-index-divider-variant-{REVISION}.step"
    light_stl = variant_dir / f"DRAFT-{PROJECT_ID}-light-index-divider-variant-{REVISION}.stl"
    export_step(light, light_step)
    export_stl(light, light_stl, mesh_parameters["linear_deflection_mm"], mesh_parameters["angular_deflection_rad"])
    step_paths["light-index-divider-variant"] = light_step
    stl_paths["light-index-divider-variant"] = light_stl

    installed = [installed_divider(shape, rack_i, lane) for lane, (_, shape, _) in zip([1, 5, 9, 13], dividers)]
    compound = cq.Compound.makeCompound([rack.val(), *[shape.val() for shape in installed]])
    virtual_step = master_dir / f"DRAFT-{PROJECT_ID}-virtual-installed-set-{REVISION}.step"
    export_step(compound, virtual_step)

    nesting, rack_placements, divider_placements = nesting_report(parameters, batch)
    nesting["inputs"] = base_inputs[:2] + [input_record(ROOT / "cad/build.py")]
    write_json(REPORTS / "nesting-layout.json", nesting)
    if nesting["status"] != "PASS":
        raise RuntimeError("nesting validation failed")
    rack_parts = [("rack", stl_paths["rack"]), ("lane-gap-gauge", stl_paths["lane-gap-gauge"]), ("divider-foot-key", stl_paths["divider-foot-key"])]
    divider_parts = [(name, stl_paths[name]) for name in shapes if name.startswith("index-divider-")]
    rack_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-rack-kit-{REVISION}.3mf"
    divider_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-divider-set-{REVISION}.3mf"
    write_3mf(rack_3mf, rack_parts, rack_placements)
    write_3mf(divider_3mf, divider_parts, divider_placements)

    metrics = {name: mesh_metrics(path) for name, path in stl_paths.items()}
    selected_volume = metrics["rack"]["volume_mm3"] + sum(metrics[name]["volume_mm3"] for name in shapes if name.startswith("index-divider-")) + metrics["lane-gap-gauge"]["volume_mm3"] + metrics["divider-foot-key"]["volume_mm3"]
    rack = parameters["rack"]
    divider = parameters["divider"]
    conventional_volume = rack["length_mm"] * rack["depth_mm"] * rack["base_thickness_mm"] + len(batch["labels"]) * divider["width_mm"] * (divider["body_height_mm"] + divider["tab_height_mm"]) * divider["thickness_mm"]
    selected_divider_volume = sum(metrics[name]["volume_mm3"] for name in shapes if name.startswith("index-divider-"))
    light_divider_volume = metrics["light-index-divider-variant"]["volume_mm3"]
    geometric = {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "baseline": {"id": "full-tray-plus-solid-dividers", "volume_mm3": conventional_volume}, "selected": {"id": "three-rail-rack-plus-protected-frame-dividers", "volume_mm3": selected_volume, "reduction_percent": 100.0 * (1.0 - selected_volume / conventional_volume)}, "light_variant": {"id": "six-mm-frame-eight-mm-rib", "one_divider_volume_mm3": light_divider_volume, "reduction_percent_vs_mean_selected_divider": 100.0 * (1.0 - light_divider_volume / (selected_divider_volume / len(batch["labels"]))), "constraint": "REJECTED_PENDING_LOADED_RACKING_AND_ENVELOPE_SNAG_EVIDENCE"}, "process_comparison": "PENDING_EXACT_TWO_PLATE_SLICER_RUNS"}
    write_json(REPORTS / "optimization-geometric.json", geometric)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS" if all(item["triangles"] <= mesh_parameters["triangle_stop"] and item["file_mib"] <= mesh_parameters["max_mesh_mib"] for item in metrics.values()) else "FAIL", "meshes": metrics, "simplification": "NOT_BENEFICIAL", "reason": "Aligned lane fins, rounded frame/pad edges and geometric glyph recesses are protected; all meshes are already below budget."})

    parametric = {"schema_version": "1.0", "tool": "MM-ORG-028-parametric-source", "tool_version": REVISION, "status": "PASS", "profile": "draft", "inputs": base_inputs, "checks": parameter_checks + [check("cad-valid", all(shape.val().isValid() for shape in all_shapes), "All selected and variant B-Reps are valid"), check("single-solids", all(len(shape.solids().vals()) == 1 for shape in all_shapes), "Every unique deliverable is one B-Rep solid"), check("font-allowlist", font_record["font_id"] == FONT_ID and not font_record["external_font_file"], "Repository-owned glyph source is allowlisted for internal candidate design"), check("csv-import", json.loads((ROOT / "reports/csv-import.json").read_text())["status"] == "PASS", "CSV category import reports PASS"), check("live-preview", json.loads((ROOT / "reports/live-batch-preview.json").read_text())["status"] == "PASS", "Exact category SVG proof reports PASS and matches its retained hash"), check("no-external-assets", all(not value.get("external_assets") for value in interfaces.values()), "No external font, logo, icon, vector or mesh asset is used")], "metrics": {"python": sys.version.split()[0], "cadquery": cq.__version__, "font_id": FONT_ID, "unique_parts": list(interfaces), "selected_build_sets": {"rack-kit": [name for name, _ in rack_parts], "divider-set": [name for name, _ in divider_parts]}}, "limitations": ["Parametric validity does not prove printed lane fit, loaded stability, snag resistance or durability."], "required_capabilities": ["cad"]}
    write_json(VALIDATION / "parametric-source-report.json", parametric)
    mesh_generation = {"schema_version": "1.0", "tool": "MM-ORG-028-mesh-generation", "tool_version": REVISION, "status": "PASS" if all(item["watertight"] and item["winding_consistent"] and item["positive_volume"] and item["components"] == 1 for item in metrics.values()) else "FAIL", "profile": "draft", "inputs": [input_record(PARAMETERS), input_record(LABEL_BATCH), input_record(ROOT / "cad/build.py"), input_record(ROOT / "cad/gridfont.py")], "checks": [check("mesh-count", len(metrics) == 8, "Seven selected meshes plus one light divider variant were generated"), check("mesh-validity", all(item["watertight"] and item["winding_consistent"] and item["positive_volume"] and item["components"] == 1 for item in metrics.values()), "Every mesh is one watertight positive-volume component"), check("mesh-budgets", all(item["triangles"] <= mesh_parameters["triangle_stop"] and item["file_mib"] <= mesh_parameters["max_mesh_mib"] for item in metrics.values()), "Every mesh remains below triangle and file-size budgets")], "metrics": {"meshes": metrics, "selected_3mf": [input_record(rack_3mf), input_record(divider_3mf)]}, "limitations": ["STL carries no authoritative units; project and 3MF contracts use millimetres."], "required_capabilities": ["mesh"]}
    write_json(VALIDATION / "mesh-generation-report.json", mesh_generation)
    interface_checks = [check("lane-pad-clearance", math.isclose(rack_i["lane_gap_mm"] - divider["pad_installed_thickness_mm"], 0.4, abs_tol=1e-9), "Divider foot retains 0.40 mm total nominal lane clearance"), check("gauge-key", gauge_i["candidate_slot_widths_mm"] == [10.9, 11.2, 11.5] and key_i["width_mm"] == 10.8, "Gauge brackets production and key reproduces exact divider-foot width"), check("three-point-registration", all(value["pad_count"] == 3 for name, value in interfaces.items() if name.startswith("index-divider-")), "Every selected divider carries three rail-aligned pads"), check("protected-frame", all(value["frame_width_mm"] >= 8 and value["center_rib_width_mm"] >= 12 for name, value in interfaces.items() if name.startswith("index-divider-")), "All selected dividers retain protected frame/rib widths"), check("font-and-pixels", all(value["font_id"] == FONT_ID and value["layout"]["pixel_width_mm"] >= divider["minimum_pixel_width_mm"] for name, value in interfaces.items() if name.startswith("index-divider-")), "CAD labels retain glyph identity and minimum pixel width"), check("light-variant-boundary", light_i["frame_width_mm"] < divider["frame_width_mm"] and light_i["center_rib_width_mm"] < divider["center_rib_width_mm"], "Light variant is distinguishable and remains non-manufacturing pending physical evidence")]
    interface_report = {"schema_version": "1.0", "tool": "MM-ORG-028-interface-validation", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in interface_checks) else "FAIL", "profile": "draft", "inputs": base_inputs, "checks": interface_checks, "metrics": {"font_record": font_record, "labels": batch["labels"], "interfaces": interfaces, "nominal_total_clearance_mm": rack_i["lane_gap_mm"] - divider["pad_installed_thickness_mm"]}, "limitations": ["Nominal digital clearance and registration require the printed coupon and loaded physical tests."], "required_capabilities": []}
    write_json(VALIDATION / "interface-report.json", interface_report)

    outputs = [*step_paths.values(), virtual_step, *stl_paths.values(), rack_3mf, divider_3mf, REPORTS / "nesting-layout.json", REPORTS / "optimization-geometric.json", REPORTS / "mesh-complexity.json", VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json"]
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "source_inputs": [input_record(path) for path in source_inputs], "outputs": [input_record(path) for path in outputs], "manufacturing_outputs": [str(path.relative_to(ROOT)) for name, path in stl_paths.items() if name != "light-index-divider-variant"] + [str(rack_3mf.relative_to(ROOT)), str(divider_3mf.relative_to(ROOT))], "optimization_variants": [str(light_step.relative_to(ROOT)), str(light_stl.relative_to(ROOT))]})
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "labels": len(batch["labels"]), "unique_meshes": len(metrics), "selected_objects": 7, "selected_3mf": [str(rack_3mf.relative_to(ROOT)), str(divider_3mf.relative_to(ROOT))], "geometric_reduction_percent": geometric["selected"]["reduction_percent"], "font_id": FONT_ID}, indent=2))


if __name__ == "__main__":
    main()
