#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-027 ShelfCue vinyl index batch."""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gridfont import FONT_ID, layout, pixel_rectangles  # noqa: E402


PARAMETERS = ROOT / "config/model-parameters.json"
LABEL_CSV = ROOT / "config/labels.csv"
LABEL_BATCH = ROOT / "config/label-batch.json"
CSV_REPORT = ROOT / "reports/csv-import.json"
LIVE_PREVIEW = ROOT / "renders/MM-ORG-027-live-batch-preview.svg"
LIVE_PROOF = ROOT / "reports/live-batch-preview.json"
FONT_ALLOWLIST = ROOT / "assets/font-allowlist.json"
GRIDFONT = ROOT / "cad/gridfont.py"
PROJECT_ID = "MM-ORG-027"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
VARIANTS = ROOT / "exports/variants"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def report(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations: list[str]) -> dict:
    return {"schema_version": "1.0", "tool": tool, "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [input_record(path) for path in inputs], "checks": checks, "metrics": metrics, "limitations": limitations, "required_capabilities": []}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rounded_plate(width: float, height: float, thickness: float, radius: float) -> cq.Shape:
    return cq.Workplane("XY").box(width, height, thickness, centered=(True, True, False)).edges("|Z").fillet(radius).val()


def make_carrier(parameters: dict, *, windowed: bool = False) -> tuple[cq.Shape, dict]:
    item = parameters["carrier"]
    shape = rounded_plate(item["length_mm"], item["height_mm"], item["thickness_mm"], item["corner_radius_mm"])
    windows = []
    if windowed:
        available = item["length_mm"] - 2.0 * item["window_end_margin_mm"]
        window_width = (available - item["window_gap_mm"]) / 2.0
        window_height = item["height_mm"] - 2.0 * item["window_edge_rail_mm"]
        centers = [-(window_width + item["window_gap_mm"]) / 2.0, (window_width + item["window_gap_mm"]) / 2.0]
        for center in centers:
            cutter = cq.Solid.makeBox(window_width, window_height, item["thickness_mm"] + 0.2, cq.Vector(center - window_width / 2.0, -window_height / 2.0, -0.1))
            shape = shape.cut(cutter)
            windows.append({"center_x_mm": center, "width_mm": window_width, "height_mm": window_height})
        shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("carrier is not one valid solid")
    bounds = shape.BoundingBox()
    return shape, {"part_id": "windowed-carrier" if windowed else "smooth-carrier", "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen], "thickness_mm": item["thickness_mm"], "windowed": windowed, "windows": windows, "print_orientation": "broad_face_down", "record_contact_surface": "continuous" if not windowed else "interrupted", "external_assets": []}


def make_label_cap(parameters: dict, label_item: dict) -> tuple[cq.Shape, dict]:
    cap = parameters["label_cap"]
    shape = rounded_plate(cap["width_mm"], cap["height_mm"], cap["thickness_mm"], cap["corner_radius_mm"])
    slot_center = label_item["slot_center_x_mm"]
    slot_width = cap["nominal_slot_width_mm"]
    slot_depth = cap["slot_insertion_depth_mm"]
    slot = cq.Solid.makeBox(slot_width, slot_depth + 0.1, cap["thickness_mm"] + 0.2, cq.Vector(slot_center - slot_width / 2.0, -cap["height_mm"] / 2.0 - 0.05, -0.1))
    shape = shape.cut(slot)
    text_center_y = -cap["height_mm"] / 2.0 + cap["text_center_y_mm"]
    cutters = []
    for x, y, size in pixel_rectangles(label_item["normalized_label"], label_item["layout"], 0.0, text_center_y):
        cutters.append(cq.Solid.makeBox(size, size, cap["engraving_depth_mm"] + 0.1, cq.Vector(x, y, cap["thickness_mm"] - cap["engraving_depth_mm"])))
    shape = shape.cut(*cutters).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"label cap {label_item['normalized_label']} is not one valid solid")
    bounds = shape.BoundingBox()
    text_bottom = text_center_y - label_item["layout"]["text_height_mm"] / 2.0
    slot_top = -cap["height_mm"] / 2.0 + slot_depth
    return shape, {"part_id": f"label-cap-{label_item['index']:02d}", "normalized_label": label_item["normalized_label"], "tab_position": label_item["tab_position"], "font_id": FONT_ID, "layout": label_item["layout"], "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen], "slot_width_mm": slot_width, "slot_center_x_mm": slot_center, "slot_insertion_depth_mm": slot_depth, "text_to_slot_margin_mm": text_bottom - slot_top, "minimum_backing_mm": cap["thickness_mm"] - cap["engraving_depth_mm"], "print_orientation": "back_face_down_slot_bridged_under_2mm", "external_assets": []}


def make_slot_gauge(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    shape = rounded_plate(coupon["gauge_width_mm"], coupon["gauge_height_mm"], coupon["gauge_thickness_mm"], 3.0)
    for center, width in zip(coupon["station_centers_x_mm"], coupon["candidate_slot_widths_mm"]):
        cutter = cq.Solid.makeBox(width, coupon["slot_insertion_depth_mm"] + 0.1, coupon["gauge_thickness_mm"] + 0.2, cq.Vector(center - width / 2.0, -coupon["gauge_height_mm"] / 2.0 - 0.05, -0.1))
        shape = shape.cut(cutter)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("slot gauge is not one valid solid")
    return shape, {"part_id": "cap-slot-gauge", "candidate_slot_widths_mm": coupon["candidate_slot_widths_mm"], "station_centers_x_mm": coupon["station_centers_x_mm"], "slot_insertion_depth_mm": coupon["slot_insertion_depth_mm"], "outer_dimensions_mm": [coupon["gauge_width_mm"], coupon["gauge_height_mm"], coupon["gauge_thickness_mm"]], "print_orientation": "broad_face_down", "external_assets": []}


def make_fit_key(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    carrier = parameters["carrier"]
    shape = rounded_plate(coupon["key_width_mm"], coupon["key_height_mm"], carrier["thickness_mm"], 2.0)
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("fit key is not one valid solid")
    return shape, {"part_id": "carrier-fit-key", "thickness_mm": carrier["thickness_mm"], "outer_dimensions_mm": [coupon["key_width_mm"], coupon["key_height_mm"], carrier["thickness_mm"]], "print_orientation": "broad_face_down", "external_assets": []}


def validate_parameters(parameters: dict, batch: dict) -> None:
    carrier = parameters["carrier"]
    cap = parameters["label_cap"]
    coupon = parameters["coupon"]
    contract = parameters["workflow_contract"]
    fonts = load_json(FONT_ALLOWLIST)["fonts"]
    proof = load_json(LIVE_PROOF)
    assert parameters["project"]["id"] == PROJECT_ID and batch["project"] == PROJECT_ID
    assert batch["font_id"] == FONT_ID and any(item["font_id"] == FONT_ID and item["design_use_status"] == "APPROVED_INTERNAL_DIGITAL_CANDIDATE" for item in fonts)
    assert sha256_file(LABEL_CSV) == batch["source_csv"]["sha256"]
    assert proof["status"] == "PASS" and proof["metrics"]["font_id"] == FONT_ID
    assert proof["metrics"]["labels"] == [item["normalized_label"] for item in batch["labels"]]
    assert proof["metrics"]["svg_sha256"] == sha256_file(LIVE_PREVIEW)
    assert 1 <= len(batch["labels"]) <= parameters["batch"]["maximum_labels"]
    assert np.isclose(cap["nominal_slot_width_mm"] - carrier["thickness_mm"], 0.3)
    assert coupon["candidate_slot_widths_mm"] == [1.8, 1.9, 2.0]
    assert min(item["layout"]["pixel_width_mm"] for item in batch["labels"]) >= cap["minimum_pixel_width_mm"]
    assert cap["height_mm"] <= contract["single_part_envelope_mm"][1]
    assert carrier["length_mm"] <= contract["single_part_envelope_mm"][0]
    assert max(carrier["thickness_mm"], cap["thickness_mm"], coupon["gauge_thickness_mm"]) <= contract["single_part_envelope_mm"][2]
    assert np.isclose(carrier["thickness_mm"] / parameters["printer"]["selected_layer_height_mm"], 8.0)
    assert np.isclose(cap["thickness_mm"] / parameters["printer"]["selected_layer_height_mm"], 12.0)
    assert contract["claim"] == "dry_indoor_shelf_index_only_not_record_support_or_archival_protection"


def move_to_origin(shape: cq.Shape) -> cq.Shape:
    bounds = shape.BoundingBox()
    return shape.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def export_step(shape: cq.Shape, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path), exportType="STEP")


def export_stl(shape: cq.Shape, path: Path, linear: float, angular: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(move_to_origin(shape), str(path), tolerance=linear, angularTolerance=angular)
    mesh = trimesh.load_mesh(path, force="mesh", process=False)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    mesh.process(validate=True)
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


def rectangle_overlap(a: dict, b: dict, gap: float) -> bool:
    return not (a["x1"] + gap <= b["x0"] or b["x1"] + gap <= a["x0"] or a["y1"] + gap <= b["y0"] or b["y1"] + gap <= a["y0"])


def nesting(parameters: dict, labels: list[dict]) -> tuple[list[tuple[float, float]], list[dict], list[dict]]:
    n = parameters["nesting"]
    carrier = parameters["carrier"]
    cap = parameters["label_cap"]
    coupon = parameters["coupon"]
    placements = []
    boxes = []
    for index, item in enumerate(labels):
        x, y = n["carrier_origin_x_mm"], n["carrier_origin_y_mm"] + index * n["carrier_row_pitch_mm"]
        placements.append((x, y))
        boxes.append({"name": f"carrier-{index + 1:02d}", "x0": x, "y0": y, "x1": x + carrier["length_mm"], "y1": y + carrier["height_mm"]})
    for index, item in enumerate(labels):
        x, y = n["cap_origin_x_mm"], n["cap_origin_y_mm"] + index * n["cap_row_pitch_mm"]
        placements.append((x, y))
        boxes.append({"name": f"label-cap-{index + 1:02d}-{slug(item['normalized_label'])}", "x0": x, "y0": y, "x1": x + cap["width_mm"], "y1": y + cap["height_mm"]})
    x, y = n["coupon_origin_x_mm"], n["coupon_origin_y_mm"]
    placements.append((x, y))
    boxes.append({"name": "cap-slot-gauge", "x0": x, "y0": y, "x1": x + coupon["gauge_width_mm"], "y1": y + coupon["gauge_height_mm"]})
    x, y = n["key_origin_x_mm"], n["key_origin_y_mm"]
    placements.append((x, y))
    boxes.append({"name": "carrier-fit-key", "x0": x, "y0": y, "x1": x + coupon["key_width_mm"], "y1": y + coupon["key_height_mm"]})
    collisions = []
    for i, first in enumerate(boxes):
        for second in boxes[i + 1:]:
            if rectangle_overlap(first, second, n["minimum_object_gap_mm"]):
                collisions.append([first["name"], second["name"]])
    return placements, boxes, collisions


def main() -> None:
    parameters = load_json(PARAMETERS)
    batch = load_json(LABEL_BATCH)
    validate_parameters(parameters, batch)
    labels = batch["labels"]
    mesh_p = parameters["mesh"]
    shapes: dict[str, cq.Shape] = {}
    interfaces: dict[str, dict] = {}
    shapes["smooth-carrier"], interfaces["smooth-carrier"] = make_carrier(parameters)
    shapes["windowed-carrier"], interfaces["windowed-carrier"] = make_carrier(parameters, windowed=True)
    for item in labels:
        name = f"label-cap-{item['index']:02d}-{slug(item['normalized_label'])}"
        shapes[name], interfaces[name] = make_label_cap(parameters, item)
    shapes["cap-slot-gauge"], interfaces["cap-slot-gauge"] = make_slot_gauge(parameters)
    shapes["carrier-fit-key"], interfaces["carrier-fit-key"] = make_fit_key(parameters)

    step_paths = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    print_set = cq.Compound.makeCompound([shape.translate((0.0, index * 50.0, 0.0)) for index, shape in enumerate(shapes.values())])
    print_set_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-print-set-{REVISION}.step"
    export_step(print_set, print_set_path)
    step_paths.append(print_set_path)

    selected_meshes: dict[str, Path] = {}
    carrier_path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-smooth-carrier-print-six-{REVISION}.stl"
    export_stl(shapes["smooth-carrier"], carrier_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    selected_meshes["smooth-carrier"] = carrier_path
    for item in labels:
        name = f"label-cap-{item['index']:02d}-{slug(item['normalized_label'])}"
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        selected_meshes[name] = path
    for name in ("cap-slot-gauge", "carrier-fit-key"):
        path = COUPONS / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        selected_meshes[name] = path
    windowed_path = VARIANTS / f"DRAFT-{PROJECT_ID}-windowed-carrier-print-six-{REVISION}.stl"
    export_stl(shapes["windowed-carrier"], windowed_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])

    placements, boxes, collisions = nesting(parameters, labels)
    parts_selected = [(f"smooth-carrier-{i + 1:02d}", carrier_path) for i in range(len(labels))]
    parts_selected += [(f"label-cap-{item['index']:02d}-{slug(item['normalized_label'])}", selected_meshes[f"label-cap-{item['index']:02d}-{slug(item['normalized_label'])}"]) for item in labels]
    parts_selected += [("cap-slot-gauge", selected_meshes["cap-slot-gauge"]), ("carrier-fit-key", selected_meshes["carrier-fit-key"])]
    parts_windowed = [(f"windowed-carrier-{i + 1:02d}", windowed_path) for i in range(len(labels))] + parts_selected[len(labels):]
    package_selected = THREE_MF / f"DRAFT-{PROJECT_ID}-shelfcue-selected-batch-{REVISION}.3mf"
    package_windowed = VARIANTS / f"DRAFT-{PROJECT_ID}-shelfcue-windowed-batch-{REVISION}.3mf"
    write_3mf(package_selected, parts_selected, placements)
    write_3mf(package_windowed, parts_windowed, placements)

    all_meshes = {**selected_meshes, "windowed-carrier": windowed_path}
    metrics = {name: mesh_metrics(path) for name, path in all_meshes.items()}
    mesh_checks = []
    for name, item in metrics.items():
        mesh_checks.extend([
            check(f"{name}:watertight", item["watertight"], f"{name} is watertight"),
            check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"),
            check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"),
            check(f"{name}:component", item["components"] == 1, f"{name} is one component"),
            check(f"{name}:triangles", item["triangles"] <= mesh_p["triangle_stop"], "Triangle budget", {"actual": item["triangles"], "limit": mesh_p["triangle_stop"]}),
            check(f"{name}:file", item["file_mib"] <= mesh_p["max_mesh_mib"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": mesh_p["max_mesh_mib"]}),
        ])

    font_record = next(item for item in load_json(FONT_ALLOWLIST)["fonts"] if item["font_id"] == FONT_ID)
    cap_interfaces = [interfaces[name] for name in interfaces if name.startswith("label-cap-")]
    unique_labels = len({item["normalized_label"] for item in labels}) == len(labels)
    cap = parameters["label_cap"]
    carrier = parameters["carrier"]
    coupon = parameters["coupon"]
    contract = parameters["workflow_contract"]
    parametric_checks = [
        check("parameter-validation", True, "Fail-closed parameter relations pass"),
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All source and variant B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every unique deliverable is one B-Rep solid"),
        check("font-allowlist", font_record["design_use_status"] == "APPROVED_INTERNAL_DIGITAL_CANDIDATE", "Repository-owned glyph font is allowlisted for internal candidate design"),
        check("csv-import", load_json(CSV_REPORT)["status"] == "PASS", "CSV label import reports PASS"),
        check("live-preview", load_json(LIVE_PROOF)["status"] == "PASS" and load_json(LIVE_PROOF)["metrics"]["svg_sha256"] == sha256_file(LIVE_PREVIEW), "Exact batch SVG proof reports PASS and matches its retained hash"),
        check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "No external font, logo, icon, vector or mesh asset is used"),
    ]
    interface_checks = [
        check("carrier-cap-clearance", np.isclose(cap["nominal_slot_width_mm"] - carrier["thickness_mm"], 0.3), "Production cap slot retains 0.3 mm total clearance"),
        check("gauge-brackets-production", coupon["candidate_slot_widths_mm"] == [1.8, 1.9, 2.0] and cap["nominal_slot_width_mm"] == 1.9, "Gauge brackets production by plus/minus 0.1 mm"),
        check("fit-key-matches-carrier", interfaces["carrier-fit-key"]["thickness_mm"] == carrier["thickness_mm"], "Fit key exactly reproduces carrier thickness"),
        check("batch-count", len(labels) == parameters["batch"]["maximum_labels"] and unique_labels, "Default batch contains six unique normalized labels"),
        check("tab-positions", [item["tab_position"] for item in labels] == ["left", "center", "right", "left", "center", "right"], "Default batch demonstrates all tab offsets twice"),
        check("font-id", all(item["font_id"] == FONT_ID for item in cap_interfaces), "Every engraved cap uses the allowlisted geometric glyph source"),
        check("proof-labels", load_json(LIVE_PROOF)["metrics"]["labels"] == [item["normalized_label"] for item in labels], "Exact proof and CAD use the same normalized label sequence"),
        check("minimum-pixels", min(item["layout"]["pixel_width_mm"] for item in cap_interfaces) >= cap["minimum_pixel_width_mm"], "Every label retains printable minimum pixel width", {"minimum_mm": min(item["layout"]["pixel_width_mm"] for item in cap_interfaces)}),
        check("text-slot-separation", min(item["text_to_slot_margin_mm"] for item in cap_interfaces) >= 2.0, "Text engraving stays at least 2 mm above the connector slot", {"minimum_mm": min(item["text_to_slot_margin_mm"] for item in cap_interfaces)}),
        check("single-part-envelope", carrier["length_mm"] <= 235.0 and cap["width_mm"] <= 105.0 and max(carrier["thickness_mm"], cap["thickness_mm"]) <= 5.0, "Every selected part respects the retained 235 x 105 x 5 mm envelope"),
        check("nesting", not collisions, "Fourteen selected objects have a non-overlapping nominal bed layout", {"collisions": collisions}),
        check("nesting-bounds", max(box["x1"] for box in boxes) <= parameters["printer"]["build_volume_mm"][0] - parameters["nesting"]["exclusion_margin_mm"] and max(box["y1"] for box in boxes) <= parameters["printer"]["build_volume_mm"][1] - parameters["nesting"]["exclusion_margin_mm"], "Nominal layout remains inside the conservative rectangular bed margin", {"max_x_mm": max(box["x1"] for box in boxes), "max_y_mm": max(box["y1"] for box in boxes)}),
        check("selected-contact-surface", interfaces["smooth-carrier"]["record_contact_surface"] == "continuous", "Selected carrier retains uninterrupted sleeve-facing surfaces"),
        check("claim-boundary", contract["claim"] == "dry_indoor_shelf_index_only_not_record_support_or_archival_protection", "Storage-index claim boundary is explicit"),
    ]
    source_inputs = [PARAMETERS, LABEL_CSV, LABEL_BATCH, CSV_REPORT, LIVE_PREVIEW, LIVE_PROOF, Path(__file__), GRIDFONT, FONT_ALLOWLIST]
    write_json(VALIDATION / "parametric-source-report.json", report(f"{PROJECT_ID}-parametric-source", source_inputs, parametric_checks, {"python": platform.python_version(), "cadquery": cq.__version__, "font_id": FONT_ID, "unique_parts": list(shapes), "selected_print_objects": [name for name, _ in parts_selected]}, ["Any CSV, label, font, geometry or parameter change requires regeneration of downstream evidence."]))
    write_json(VALIDATION / "mesh-generation-report.json", report(f"{PROJECT_ID}-mesh-generation", [PARAMETERS, LABEL_BATCH, Path(__file__), GRIDFONT], mesh_checks, {"meshes": metrics}, ["Topology does not prove printed flatness, sleeve-contact safety, cap retention or engraved-text readability."]))
    write_json(VALIDATION / "interface-report.json", report(f"{PROJECT_ID}-interface-validation", [PARAMETERS, LABEL_CSV, LABEL_BATCH, CSV_REPORT, LIVE_PREVIEW, LIVE_PROOF, Path(__file__), GRIDFONT, FONT_ALLOWLIST, ROOT / "design-spec.yaml"], interface_checks, {"interfaces": interfaces, "labels": labels, "nesting_boxes": boxes, "workflow_contract": contract, "font_record": font_record, "live_proof": load_json(LIVE_PROOF)}, ["Analytic clearance, text and nesting checks cannot establish real PETG fit, warping, abrasion or user visibility."]))
    write_json(REPORTS / "nesting-layout.json", report(f"{PROJECT_ID}-nesting-layout", [PARAMETERS, LABEL_BATCH, Path(__file__)], [check("non-overlap", not collisions, "All selected objects retain the configured nominal gap", {"collisions": collisions}), check("bed-bounds", max(box["x1"] for box in boxes) <= 420.0 and max(box["y1"] for box in boxes) <= 414.0, "Layout respects conservative Kobra 3 Max rectangular margins")], {"objects": boxes, "placements_mm": placements, "object_count": len(boxes), "minimum_gap_mm": parameters["nesting"]["minimum_object_gap_mm"]}, ["The exact destination profile may contain non-rectangular exclusion zones; exact slicing remains authoritative."]))

    count = len(labels)
    conventional_volume = count * carrier["length_mm"] * 100.0 * carrier["thickness_mm"]
    selected_volume = count * float(shapes["smooth-carrier"].Volume()) + sum(float(shapes[f"label-cap-{item['index']:02d}-{slug(item['normalized_label'])}"].Volume()) for item in labels) + float(shapes["cap-slot-gauge"].Volume()) + float(shapes["carrier-fit-key"].Volume())
    windowed_volume = count * float(shapes["windowed-carrier"].Volume()) + selected_volume - count * float(shapes["smooth-carrier"].Volume())
    geometric = {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "baseline": {"id": "legacy-full-panel", "description": "six 230 x 100 x 1.6 mm full plates", "volume_mm3": conventional_volume}, "selected": {"id": "smooth-carrier-cap", "description": "six smooth carrier strips, engraved caps and coupon pair", "volume_mm3": selected_volume, "reduction_percent": 100.0 * (1.0 - selected_volume / conventional_volume), "constraint": "continuous sleeve-facing carrier"}, "windowed": {"id": "windowed-carrier-cap", "description": "two large windows per carrier with identical caps and coupons", "volume_mm3": windowed_volume, "reduction_percent_vs_selected": 100.0 * (1.0 - windowed_volume / selected_volume), "constraint": "REJECTED_PENDING_PHYSICAL_EDGE_AND_RACKING_EVIDENCE"}, "thin_plate_core": {"plate_thickness_mm": 1.6, "estimated_combined_two_side_wall_depth_mm": 1.7141592653589792, "status": "NO_INFILL_CORE", "infill_percentage_is_not_a_material_lever": True}, "exact_profile_comparison": "PENDING_SLICER_RUNS"}
    write_json(REPORTS / "optimization-geometric.json", geometric)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL", "meshes": metrics, "simplification": "NOT_BENEFICIAL", "reason": "Rounded sleeve-facing edges, U-slots and geometric glyph recesses are protected; all meshes are already below budget."})
    outputs = [*step_paths, *all_meshes.values(), package_selected, package_windowed]
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "source_inputs": [input_record(path) for path in source_inputs], "outputs": [input_record(path) for path in outputs], "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*selected_meshes.values(), package_selected]], "optimization_variants": [str(windowed_path.relative_to(ROOT)), str(package_windowed.relative_to(ROOT))]})
    gates = [load_json(VALIDATION / name) for name in ("parametric-source-report.json", "mesh-generation-report.json", "interface-report.json")]
    if any(value["status"] != "PASS" for value in [*gates, geometric]):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "labels": len(labels), "unique_selected_meshes": len(selected_meshes), "selected_objects": len(parts_selected), "selected_3mf": str(package_selected.relative_to(ROOT)), "windowed_3mf": str(package_windowed.relative_to(ROOT)), "geometric_reduction_percent": geometric["selected"]["reduction_percent"], "font_id": FONT_ID}, indent=2))


if __name__ == "__main__":
    main()
