#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-026 SignRail desk nameplate."""
from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gridfont import FONT_ID, layout, normalize_text, pixel_rectangles  # noqa: E402


PARAMETERS = ROOT / "config/model-parameters.json"
FONT_ALLOWLIST = ROOT / "assets/font-allowlist.json"
GRIDFONT = ROOT / "cad/gridfont.py"
LIVE_PREVIEW = ROOT / "renders/MM-ORG-026-live-text-preview.svg"
LIVE_PROOF = ROOT / "reports/live-text-preview.json"
PROJECT_ID = "MM-ORG-026"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


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


def rounded_plate(width: float, depth: float, thickness: float, radius: float) -> cq.Shape:
    return cq.Workplane("XY").box(width, depth, thickness, centered=(True, True, False)).edges("|Z").fillet(radius).val()


def normalized_personalization(parameters: dict) -> tuple[str, str]:
    personal = parameters["personalization"]
    name = normalize_text(personal["name"], personal["allowed_characters"], personal["name_maximum_characters_after_transliteration"])
    title = normalize_text(personal["title"], personal["allowed_characters"], personal["title_maximum_characters_after_transliteration"])
    return name, title


def text_layouts(parameters: dict, name: str, title: str) -> dict:
    plate = parameters["plate"]
    available = plate["width_mm"] - 2.0 * plate["text_margin_x_mm"]
    return {
        "name": layout(name, available, plate["name_height_mm"], plate["maximum_pixel_pitch_mm"], plate["minimum_pixel_width_mm"]),
        "title": layout(title, available, plate["title_height_mm"], plate["maximum_pixel_pitch_mm"], plate["minimum_pixel_width_mm"]),
    }


def engraving_cutters(parameters: dict, name: str, title: str, layouts: dict) -> list[cq.Shape]:
    plate = parameters["plate"]
    cutters = []
    for text, data, center_y in ((name, layouts["name"], plate["name_center_y_mm"]), (title, layouts["title"], plate["title_center_y_mm"])):
        for x, y, size in pixel_rectangles(text, data, 0.0, center_y):
            cutters.append(cq.Solid.makeBox(size, size, plate["engraving_depth_mm"] + 0.1, cq.Vector(x, y, plate["thickness_mm"] - plate["engraving_depth_mm"])))
    inset = plate["border_inset_mm"]
    border = plate["border_width_mm"]
    inner_w = plate["width_mm"] - 2.0 * inset
    inner_h = plate["height_mm"] - 2.0 * inset
    z = plate["thickness_mm"] - plate["engraving_depth_mm"]
    cutters.extend([
        cq.Solid.makeBox(inner_w, border, plate["engraving_depth_mm"] + 0.1, cq.Vector(-inner_w / 2.0, -inner_h / 2.0, z)),
        cq.Solid.makeBox(inner_w, border, plate["engraving_depth_mm"] + 0.1, cq.Vector(-inner_w / 2.0, inner_h / 2.0 - border, z)),
        cq.Solid.makeBox(border, inner_h, plate["engraving_depth_mm"] + 0.1, cq.Vector(-inner_w / 2.0, -inner_h / 2.0, z)),
        cq.Solid.makeBox(border, inner_h, plate["engraving_depth_mm"] + 0.1, cq.Vector(inner_w / 2.0 - border, -inner_h / 2.0, z)),
    ])
    return cutters


def make_plate(parameters: dict) -> tuple[cq.Shape, dict]:
    plate = parameters["plate"]
    name, title = normalized_personalization(parameters)
    layouts = text_layouts(parameters, name, title)
    shape = rounded_plate(plate["width_mm"], plate["height_mm"], plate["thickness_mm"], plate["corner_radius_mm"])
    cutters = engraving_cutters(parameters, name, title, layouts)
    shape = shape.cut(*cutters).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("personalized plate is not one valid solid")
    bounds = shape.BoundingBox()
    return shape, {
        "part_id": "personalized-insert",
        "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
        "normalized_name": name,
        "normalized_title": title,
        "font_id": FONT_ID,
        "name_layout": layouts["name"],
        "title_layout": layouts["title"],
        "engraving_depth_mm": plate["engraving_depth_mm"],
        "minimum_backing_mm": plate["thickness_mm"] - plate["engraving_depth_mm"],
        "print_orientation": "back_face_down",
        "external_assets": [],
    }


def slot_cutter(width_x: float, slot_width: float, slot_depth: float, bottom_y: float, bottom_z: float, angle_from_horizontal_deg: float) -> cq.Shape:
    rotation = angle_from_horizontal_deg - 90.0
    return (
        cq.Workplane("XY")
        .box(width_x, slot_width, slot_depth, centered=(True, True, False))
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), rotation)
        .translate((0.0, bottom_y, bottom_z))
        .val()
    )


def make_stand(parameters: dict) -> tuple[cq.Shape, dict]:
    stand = parameters["stand"]
    shape = rounded_plate(stand["width_mm"], stand["depth_mm"], stand["height_mm"], stand["corner_radius_mm"])
    cutter = slot_cutter(stand["width_mm"] + 2.0, stand["slot_width_mm"], stand["slot_depth_mm"], stand["slot_bottom_y_mm"], stand["slot_bottom_z_mm"], stand["slot_angle_from_horizontal_deg"])
    shape = shape.cut(cutter).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("end stand is not one valid solid")
    bounds = shape.BoundingBox()
    insertion_depth = (stand["height_mm"] - stand["slot_bottom_z_mm"]) / math.sin(math.radians(stand["slot_angle_from_horizontal_deg"]))
    return shape, {
        "part_id": "angled-end-stand",
        "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
        "slot_width_mm": stand["slot_width_mm"],
        "slot_angle_from_horizontal_deg": stand["slot_angle_from_horizontal_deg"],
        "slot_bottom_y_mm": stand["slot_bottom_y_mm"],
        "slot_bottom_z_mm": stand["slot_bottom_z_mm"],
        "minimum_open_insertion_depth_mm": insertion_depth,
        "print_orientation": "base_down",
        "external_assets": [],
    }


def make_slot_gauge(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    stand = parameters["stand"]
    shape = rounded_plate(coupon["gauge_width_mm"], coupon["gauge_depth_mm"], coupon["gauge_height_mm"], 3.0)
    for x, slot_width in zip(coupon["station_centers_x_mm"], coupon["candidate_slot_widths_mm"]):
        cutter = slot_cutter(coupon["key_width_mm"] + 2.0, slot_width, stand["slot_depth_mm"], stand["slot_bottom_y_mm"], stand["slot_bottom_z_mm"], stand["slot_angle_from_horizontal_deg"]).translate((x, 0.0, 0.0))
        shape = shape.cut(cutter)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("slot gauge is not one valid solid")
    return shape, {
        "part_id": "angled-slot-gauge",
        "candidate_slot_widths_mm": coupon["candidate_slot_widths_mm"],
        "station_centers_x_mm": coupon["station_centers_x_mm"],
        "slot_angle_from_horizontal_deg": stand["slot_angle_from_horizontal_deg"],
        "outer_dimensions_mm": [coupon["gauge_width_mm"], coupon["gauge_depth_mm"], coupon["gauge_height_mm"]],
        "print_orientation": "base_down",
        "external_assets": [],
    }


def make_fit_key(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    plate = parameters["plate"]
    shape = rounded_plate(coupon["key_width_mm"], coupon["key_height_mm"], plate["thickness_mm"], 2.0)
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("fit key is not one valid solid")
    return shape, {
        "part_id": "insert-fit-key",
        "thickness_mm": plate["thickness_mm"],
        "outer_dimensions_mm": [coupon["key_width_mm"], coupon["key_height_mm"], plate["thickness_mm"]],
        "print_orientation": "back_face_down",
        "external_assets": [],
    }


def installed_height(parameters: dict) -> float:
    return parameters["stand"]["slot_bottom_z_mm"] + parameters["plate"]["height_mm"] * math.sin(math.radians(parameters["stand"]["slot_angle_from_horizontal_deg"]))


def validate_parameters(parameters: dict) -> None:
    plate = parameters["plate"]
    stand = parameters["stand"]
    coupon = parameters["coupon"]
    contract = parameters["workflow_contract"]
    name, title = normalized_personalization(parameters)
    layouts = text_layouts(parameters, name, title)
    fonts = json.loads(FONT_ALLOWLIST.read_text(encoding="utf-8"))["fonts"]
    proof = json.loads(LIVE_PROOF.read_text(encoding="utf-8"))
    assert parameters["project"]["id"] == PROJECT_ID
    assert parameters["personalization"]["font_id"] == FONT_ID
    assert any(item["font_id"] == FONT_ID and item["design_use_status"] == "APPROVED_INTERNAL_DIGITAL_CANDIDATE" for item in fonts)
    assert proof["font_id"] == FONT_ID and proof["normalized_name"] == name and proof["normalized_title"] == title
    assert proof["svg_sha256"] == sha256_file(LIVE_PREVIEW)
    assert np.isclose(stand["slot_width_mm"] - plate["thickness_mm"], 0.4)
    assert coupon["candidate_slot_widths_mm"] == [3.2, 3.4, 3.6]
    assert min(layouts["name"]["pixel_width_mm"], layouts["title"]["pixel_width_mm"]) >= plate["minimum_pixel_width_mm"]
    assert plate["thickness_mm"] - plate["engraving_depth_mm"] >= 2.4
    assert plate["width_mm"] <= contract["assembly_envelope_mm"][0]
    assert stand["depth_mm"] <= contract["assembly_envelope_mm"][1]
    assert installed_height(parameters) <= contract["assembly_envelope_mm"][2]
    assert np.isclose(plate["thickness_mm"] / parameters["printer"]["layer_height_mm"], 15.0)
    assert np.isclose(stand["height_mm"] / parameters["printer"]["layer_height_mm"], 100.0)
    assert contract["claim"] == "indoor_decorative_identification_only_no_affiliation_or_accessibility_claim"


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
        _zip_member("Metadata/font-allowlist.json", FONT_ALLOWLIST.read_bytes(), archive)


def main() -> None:
    parameters = load_parameters()
    validate_parameters(parameters)
    mesh_p = parameters["mesh"]
    shapes: dict[str, cq.Shape] = {}
    interfaces: dict[str, dict] = {}
    shapes["personalized-insert"], interfaces["personalized-insert"] = make_plate(parameters)
    shapes["angled-end-stand"], interfaces["angled-end-stand"] = make_stand(parameters)
    shapes["angled-slot-gauge"], interfaces["angled-slot-gauge"] = make_slot_gauge(parameters)
    shapes["insert-fit-key"], interfaces["insert-fit-key"] = make_fit_key(parameters)
    step_paths = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    exploded = cq.Compound.makeCompound([shapes["personalized-insert"], shapes["angled-end-stand"].translate((-70.0, 70.0, 0.0)), shapes["angled-end-stand"].translate((70.0, 70.0, 0.0)), shapes["angled-slot-gauge"].translate((0.0, 120.0, 0.0)), shapes["insert-fit-key"].translate((65.0, 120.0, 0.0))])
    exploded_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"
    export_step(exploded, exploded_path)
    step_paths.append(exploded_path)
    mesh_paths: dict[str, Path] = {}
    for name in ("personalized-insert", "angled-end-stand"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    for name in ("angled-slot-gauge", "insert-fit-key"):
        path = COUPONS / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-personalized-desk-nameplate-{REVISION}.3mf"
    parts = [("personalized-insert", mesh_paths["personalized-insert"]), ("angled-end-stand-left", mesh_paths["angled-end-stand"]), ("angled-end-stand-right", mesh_paths["angled-end-stand"]), ("angled-slot-gauge", mesh_paths["angled-slot-gauge"]), ("insert-fit-key", mesh_paths["insert-fit-key"])]
    placements = [(10.0, 10.0), (10.0, 75.0), (45.0, 75.0), (85.0, 75.0), (170.0, 75.0)]
    write_3mf(package_path, parts, placements)
    metrics = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
    mesh_checks = []
    for name, item in metrics.items():
        mesh_checks.extend([check(f"{name}:watertight", item["watertight"], f"{name} is watertight"), check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"), check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"), check(f"{name}:component", item["components"] == 1, f"{name} is one component"), check(f"{name}:triangles", item["triangles"] <= mesh_p["triangle_stop"], "Triangle budget", {"actual": item["triangles"], "limit": mesh_p["triangle_stop"]}), check(f"{name}:file", item["file_mib"] <= mesh_p["max_mesh_mib"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": mesh_p["max_mesh_mib"]})])
    plate_i = interfaces["personalized-insert"]
    stand_i = interfaces["angled-end-stand"]
    gauge_i = interfaces["angled-slot-gauge"]
    key_i = interfaces["insert-fit-key"]
    font_record = next(item for item in json.loads(FONT_ALLOWLIST.read_text(encoding="utf-8"))["fonts"] if item["font_id"] == FONT_ID)
    proof = json.loads(LIVE_PROOF.read_text(encoding="utf-8"))
    parametric_checks = [check("parameter-validation", True, "Fail-closed parameter relations pass"), check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All four B-Reps are valid"), check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every unique deliverable is one B-Rep solid"), check("font-allowlist", font_record["design_use_status"] == "APPROVED_INTERNAL_DIGITAL_CANDIDATE", "Repository-owned glyph font is allowlisted for internal candidate design"), check("live-preview", proof["svg_sha256"] == sha256_file(LIVE_PREVIEW), "Live SVG proof hash matches the generated preview"), check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "No external font file, logo, icon, vector or mesh asset is used")]
    write_json(VALIDATION / "parametric-source-report.json", report(f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__), GRIDFONT, FONT_ALLOWLIST, LIVE_PREVIEW, LIVE_PROOF], parametric_checks, {"python": platform.python_version(), "cadquery": cq.__version__, "font_id": FONT_ID, "unique_parts": list(shapes), "print_objects": [name for name, _ in parts]}, ["Any text, title, font, geometry or parameter change requires regeneration of downstream evidence."]))
    write_json(VALIDATION / "mesh-generation-report.json", report(f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__), GRIDFONT], mesh_checks, {"meshes": metrics}, ["Topology does not prove printed text readability, stand fit, tip resistance or desk-surface behavior."]))
    interface_checks = [
        check("insert-slot-clearance", np.isclose(stand_i["slot_width_mm"] - parameters["plate"]["thickness_mm"], 0.4), "Production insert has 0.4 mm total slot clearance"),
        check("gauge-brackets-production", gauge_i["candidate_slot_widths_mm"] == [3.2, 3.4, 3.6] and stand_i["slot_width_mm"] == 3.4, "Gauge brackets production slot by plus/minus 0.2 mm"),
        check("fit-key-matches-insert", key_i["thickness_mm"] == parameters["plate"]["thickness_mm"], "Fit key exactly reproduces insert thickness"),
        check("shared-angle", gauge_i["slot_angle_from_horizontal_deg"] == stand_i["slot_angle_from_horizontal_deg"] == 70.0, "Coupon and stands share the 70 degree display angle"),
        check("font-id", plate_i["font_id"] == FONT_ID == proof["font_id"], "CAD, preview and allowlist use the same font ID"),
        check("proof-text", plate_i["normalized_name"] == proof["normalized_name"] and plate_i["normalized_title"] == proof["normalized_title"], "CAD and live preview use the same normalized text"),
        check("minimum-pixels", min(plate_i["name_layout"]["pixel_width_mm"], plate_i["title_layout"]["pixel_width_mm"]) >= parameters["plate"]["minimum_pixel_width_mm"], "Both text lines retain printable minimum pixel width", {"name_mm": plate_i["name_layout"]["pixel_width_mm"], "title_mm": plate_i["title_layout"]["pixel_width_mm"]}),
        check("backing", plate_i["minimum_backing_mm"] >= 2.4, "Engraving leaves at least 2.4 mm backing"),
        check("assembly-envelope", parameters["plate"]["width_mm"] <= 200.0 and parameters["stand"]["depth_mm"] <= 62.0 and installed_height(parameters) <= 55.0, "Installed assembly fits the 200 x 62 x 55 mm envelope", {"installed_height_mm": installed_height(parameters)}),
        check("two-stands", parameters["stand"]["default_center_offsets_x_mm"] == [-78.0, 78.0], "Two identical default stand centers are symmetric"),
        check("support-conscious", all(item["print_orientation"] in {"base_down", "back_face_down"} for item in interfaces.values()), "All unique parts have support-free declared orientations"),
        check("claim-boundary", parameters["workflow_contract"]["claim"] == "indoor_decorative_identification_only_no_affiliation_or_accessibility_claim", "Decorative identification claim boundary is explicit"),
    ]
    write_json(VALIDATION / "interface-report.json", report(f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), GRIDFONT, FONT_ALLOWLIST, LIVE_PREVIEW, LIVE_PROOF, ROOT / "design-spec.yaml"], interface_checks, {"interfaces": interfaces, "workflow_contract": parameters["workflow_contract"], "font_record": font_record, "live_proof": proof}, ["Analytic clearances and preview identity cannot establish real PLA fit, legibility, tipping, abrasion, or customer proof approval."]))
    baseline_volume = parameters["plate"]["width_mm"] * parameters["stand"]["depth_mm"] * parameters["stand"]["height_mm"]
    baseline_volume += float(np.prod(plate_i["outer_dimensions_mm"])) + float(np.prod(gauge_i["outer_dimensions_mm"])) + float(np.prod(key_i["outer_dimensions_mm"]))
    candidate_volume = float(shapes["personalized-insert"].Volume()) + 2.0 * float(shapes["angled-end-stand"].Volume()) + float(shapes["angled-slot-gauge"].Volume()) + float(shapes["insert-fit-key"].Volume())
    reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "baseline": {"description": "solid full-width 200 x 62 x 20 mm conventional holder plus insert and coupon envelope blocks", "volume_mm3": baseline_volume}, "candidate": {"description": "two reusable end stands, engraved insert and fit-first coupon pair", "volume_mm3": candidate_volume}, "volume_reduction_percent": reduction, "selection_threshold_percent": 35.0, "status": "PASS" if reduction >= 35.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE"}
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL", "meshes": metrics, "simplification": "NOT_BENEFICIAL", "reason": "Glyph pixels, shallow border, inclined slots and rounded contact edges are under budget; decimation risks protected personalization and fit geometry."})
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "source_inputs": [input_record(path) for path in (PARAMETERS, Path(__file__), GRIDFONT, FONT_ALLOWLIST, LIVE_PREVIEW, LIVE_PROOF)], "outputs": [input_record(path) for path in outputs], "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]]})
    gate_reports = [json.loads((VALIDATION / name).read_text()) for name in ("parametric-source-report.json", "mesh-generation-report.json", "interface-report.json")]
    if any(value["status"] != "PASS" for value in [*gate_reports, optimization]):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "unique_meshes": len(mesh_paths), "objects": len(parts), "3mf": str(package_path.relative_to(ROOT)), "volume_reduction_percent": reduction, "font_id": FONT_ID}, indent=2))


if __name__ == "__main__":
    main()
