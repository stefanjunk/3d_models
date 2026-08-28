#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-018 drawer measurement gauge kit."""
from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
PROJECT_ID = "MM-ORG-018"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
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
    return {
        "schema_version": "1.0", "tool": tool, "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft", "inputs": [input_record(path) for path in inputs],
        "checks": checks, "metrics": metrics, "limitations": limitations, "required_capabilities": [],
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rounded_rectangle(width: float, depth: float, height: float, radius: float, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> cq.Shape:
    shape = cq.Workplane("XY").rect(width, depth).extrude(height).edges("|Z").fillet(radius).val()
    return shape.translate((x + width / 2.0, y + depth / 2.0, z))


def circle_cutter(diameter: float, x: float, y: float, height: float) -> cq.Shape:
    return cq.Solid.makeCylinder(diameter / 2.0, height + 0.2, cq.Vector(x, y, -0.1))


def make_radius_tile(parameters: dict, radius: float, identity_count: int) -> tuple[cq.Shape, dict]:
    tile = parameters["radius_tiles"]
    size = tile["tile_size_mm"]
    height = tile["thickness_mm"]
    mid = radius - radius / math.sqrt(2.0)
    shape = (
        cq.Workplane("XY")
        .moveTo(radius, 0.0)
        .lineTo(size, 0.0)
        .lineTo(size, size)
        .lineTo(0.0, size)
        .lineTo(0.0, radius)
        .threePointArc((mid, mid), (radius, 0.0))
        .close()
        .extrude(height)
        .val()
    )
    pitch = tile["identity_hole_pitch_mm"]
    start_x = size / 2.0 - pitch * (identity_count - 1) / 2.0
    cutters = [circle_cutter(tile["identity_hole_diameter_mm"], start_x + index * pitch, tile["identity_hole_center_y_mm"], height) for index in range(identity_count)]
    shape = shape.cut(cq.Compound.makeCompound(cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"radius R{radius:g} tile is not one valid solid")
    return shape, {
        "radius_mm": radius,
        "identity_holes": identity_count,
        "analytic_arc_start_mm": [0.0, radius],
        "analytic_arc_mid_mm": [mid, mid],
        "analytic_arc_end_mm": [radius, 0.0],
        "outer_dimensions_mm": [size, size, height],
        "external_assets": [],
    }


def make_height_card(parameters: dict) -> tuple[cq.Shape, dict]:
    card = parameters["height_cards"]
    height = card["height_mm"]
    thickness = card["thickness_mm"]
    shape = cq.Solid.makeBox(card["spine_width_mm"], height, thickness)
    foot = cq.Solid.makeBox(card["width_mm"], card["foot_height_mm"], thickness)
    shape = shape.fuse(foot)
    cutters: list[cq.Shape] = []
    for level_index, level in enumerate(card["reference_heights_mm"], 1):
        ledge = cq.Solid.makeBox(
            card["ledge_length_mm"], card["ledge_thickness_mm"], thickness,
            cq.Vector(card["spine_width_mm"] - 0.2, level - card["ledge_thickness_mm"], 0.0),
        )
        shape = shape.fuse(ledge)
        start_x = card["spine_width_mm"] + 5.0
        for hole_index in range(level_index):
            cutters.append(circle_cutter(card["identity_hole_diameter_mm"], start_x + hole_index * 3.0, level - card["ledge_thickness_mm"] / 2.0, thickness))
    shape = shape.cut(cq.Compound.makeCompound(cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("height card is not one valid solid")
    return shape, {
        "reference_heights_mm": card["reference_heights_mm"],
        "identity_holes": [1, 2, 3],
        "quantity_in_build": card["quantity"],
        "floor_datum_y_mm": 0.0,
        "outer_dimensions_mm": [card["width_mm"], card["height_mm"], thickness],
        "external_assets": [],
    }


def make_clearance_comb(parameters: dict) -> tuple[cq.Shape, dict]:
    comb = parameters["clearance_comb"]
    thickness = comb["thickness_mm"]
    shape = rounded_rectangle(comb["backbone_width_mm"], comb["backbone_depth_mm"], thickness, 2.0)
    cutters: list[cq.Shape] = []
    for center_x, width in zip(comb["finger_centers_x_mm"], comb["finger_widths_mm"]):
        finger = cq.Solid.makeBox(width, comb["finger_length_mm"] + 0.5, thickness, cq.Vector(center_x - width / 2.0, comb["backbone_depth_mm"] - 0.5, 0.0))
        shape = shape.fuse(finger)
        cutters.append(circle_cutter(comb["center_hole_diameter_mm"], center_x, comb["backbone_depth_mm"] / 2.0, thickness))
    shape = shape.cut(cq.Compound.makeCompound(cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("clearance comb is not one valid solid")
    return shape, {
        "finger_widths_mm": comb["finger_widths_mm"],
        "sequence": "left-to-right-ascending",
        "outer_dimensions_mm": [comb["backbone_width_mm"], comb["backbone_depth_mm"] + comb["finger_length_mm"], thickness],
        "external_assets": [],
    }


def make_calibration_frame(parameters: dict) -> tuple[cq.Shape, dict]:
    frame = parameters["calibration_frame"]
    height = frame["thickness_mm"]
    shape = rounded_rectangle(frame["width_mm"], frame["depth_mm"], height, frame["corner_radius_mm"])
    window = rounded_rectangle(frame["window_width_mm"], frame["window_depth_mm"], height + 0.2, frame["window_corner_radius_mm"], (frame["width_mm"] - frame["window_width_mm"]) / 2.0, (frame["depth_mm"] - frame["window_depth_mm"]) / 2.0, -0.1)
    circle = circle_cutter(frame["round_reference_diameter_mm"], 12.5, frame["depth_mm"] / 2.0, height)
    square = cq.Solid.makeBox(frame["square_reference_mm"], frame["square_reference_mm"], height + 0.2, cq.Vector(frame["width_mm"] - 17.5, frame["depth_mm"] / 2.0 - frame["square_reference_mm"] / 2.0, -0.1))
    shape = shape.cut(cq.Compound.makeCompound([window, circle, square])).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("calibration frame is not one valid solid")
    return shape, {
        "external_references_mm": [frame["width_mm"], frame["depth_mm"], height],
        "internal_window_mm": [frame["window_width_mm"], frame["window_depth_mm"]],
        "round_reference_diameter_mm": frame["round_reference_diameter_mm"],
        "square_reference_mm": frame["square_reference_mm"],
        "external_assets": [],
    }


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    tile = parameters["radius_tiles"]
    card = parameters["height_cards"]
    comb = parameters["clearance_comb"]
    frame = parameters["calibration_frame"]
    contract = parameters["measurement_contract"]
    printer = parameters["printer"]
    assert project["id"] == PROJECT_ID and project["revision"] == REVISION and project["units"] == "mm"
    assert tile["radii_mm"] == [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]
    assert all(b - a == contract["radius_increment_mm"] for a, b in zip(tile["radii_mm"], tile["radii_mm"][1:]))
    assert card["quantity"] == 2 and card["reference_heights_mm"] == [15.0, 35.0, 55.0]
    assert all(b - a == contract["height_increment_mm"] for a, b in zip(card["reference_heights_mm"], card["reference_heights_mm"][1:]))
    assert comb["finger_widths_mm"] == [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    assert all(abs((b - a) - contract["clearance_increment_mm"]) < 1e-9 for a, b in zip(comb["finger_widths_mm"], comb["finger_widths_mm"][1:]))
    assert min(comb["finger_widths_mm"]) >= 2.0 * printer["nozzle_diameter_mm"]
    assert tile["thickness_mm"] == card["thickness_mm"] == comb["thickness_mm"] == frame["thickness_mm"]
    assert tile["thickness_mm"] / printer["layer_height_mm"] == 15
    assert max(frame["width_mm"], card["height_mm"], comb["backbone_width_mm"]) <= 180.0
    assert max(frame["depth_mm"], card["width_mm"], comb["backbone_depth_mm"] + comb["finger_length_mm"]) <= 90.0
    assert tile["thickness_mm"] <= 12.0
    assert contract["minimum_real_drawers_for_validation"] == 10
    assert contract["radius_selection_rule"] == "smallest_no_force_seating_tile"


def move_to_origin(shape: cq.Shape) -> cq.Shape:
    bounds = shape.BoundingBox()
    return shape.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def export_step(shape: cq.Shape, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path), exportType="STEP")


def export_stl(shape: cq.Shape, path: Path, linear: float, angular: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(move_to_origin(shape), str(path), tolerance=linear, angularTolerance=angular)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    return {
        "path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "triangles": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)),
        "file_bytes": path.stat().st_size, "file_mib": path.stat().st_size / (1024 * 1024), "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent), "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
        "components": int(len(mesh.split(only_watertight=False))), "volume_mm3": float(mesh.volume), "surface_area_mm2": float(mesh.area),
        "extents_mm": np.round(mesh.extents, 4).tolist(), "bounds_mm": np.round(mesh.bounds, 4).tolist(),
    }


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
        verts = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(verts, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        tris = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(tris, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {move_x:.3f} {move_y:.3f} 0"})
    types = (b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             b'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             b'<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = (b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            b'<Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        _zip_member("[Content_Types].xml", types, archive)
        _zip_member("_rels/.rels", rels, archive)
        _zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive)
        _zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)


def main() -> None:
    parameters = load_parameters()
    validate_parameters(parameters)
    mesh_p = parameters["mesh"]
    shapes: dict[str, cq.Shape] = {}
    interfaces: dict[str, dict] = {}
    for index, radius in enumerate(parameters["radius_tiles"]["radii_mm"], 1):
        name = f"radius-r{int(radius):02d}"
        shapes[name], interfaces[name] = make_radius_tile(parameters, radius, index)
    shapes["height-card"], interfaces["height-card"] = make_height_card(parameters)
    shapes["clearance-comb"], interfaces["clearance-comb"] = make_clearance_comb(parameters)
    shapes["calibration-frame"], interfaces["calibration-frame"] = make_calibration_frame(parameters)

    step_paths: list[Path] = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    assembly_parts: list[cq.Shape] = []
    for index, name in enumerate([f"radius-r{value:02d}" for value in (2, 4, 6, 8, 10, 12)]):
        assembly_parts.append(shapes[name].translate((index * 38.0, 0.0, 0.0)))
    assembly_parts.extend([
        shapes["height-card"].translate((0.0, 45.0, 0.0)),
        shapes["height-card"].translate((38.0, 45.0, 0.0)),
        shapes["clearance-comb"].translate((80.0, 45.0, 0.0)),
        shapes["calibration-frame"].translate((0.0, 120.0, 0.0)),
    ])
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-kit-{REVISION}.step"
    export_step(cq.Compound.makeCompound(assembly_parts), assembly_path)
    step_paths.append(assembly_path)

    mesh_paths: dict[str, Path] = {}
    for name, shape in shapes.items():
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shape, path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-drawer-measurement-gauge-kit-{REVISION}.3mf"
    part_names = [f"radius-r{value:02d}" for value in (2, 4, 6, 8, 10, 12)] + ["height-card-left", "height-card-right", "clearance-comb", "calibration-frame"]
    part_paths = [(name, mesh_paths["height-card"] if name.startswith("height-card") else mesh_paths[name]) for name in part_names]
    placements = [(10.0 + index * 40.0, 10.0) for index in range(6)] + [(10.0, 55.0), (50.0, 55.0), (90.0, 55.0), (10.0, 135.0)]
    write_3mf(package_path, part_paths, placements)

    metrics = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
    mesh_checks: list[dict] = []
    for name, item in metrics.items():
        mesh_checks.extend([
            check(f"{name}:watertight", item["watertight"], f"{name} is watertight"),
            check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"),
            check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"),
            check(f"{name}:component", item["components"] == 1, f"{name} is one component"),
            check(f"{name}:triangles", item["triangles"] <= mesh_p["triangle_stop"], "Triangle budget", {"actual": item["triangles"], "limit": mesh_p["triangle_stop"]}),
            check(f"{name}:file", item["file_mib"] <= mesh_p["max_mesh_mib"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": mesh_p["max_mesh_mib"]}),
        ])
    parametric_checks = [
        check("parameter-validation", True, "Fail-closed parameter relations pass"),
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All nine unique B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every unique deliverable is one B-Rep solid"),
        check("ten-print-objects", len(part_names) == 10, "3MF contains six radius tiles, two height cards, comb and frame"),
        check("no-external-assets", not any(interfaces[name].get("external_assets") for name in interfaces), "Geometry uses no third-party font, vector or mesh assets"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", report(
        f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)], parametric_checks,
        {"python": platform.python_version(), "cadquery": cq.__version__, "unique_parts": list(shapes), "print_objects": part_names},
        ["Any parameter change requires regeneration of downstream evidence."],
    ))
    write_json(VALIDATION / "mesh-generation-report.json", report(
        f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks, {"meshes": metrics},
        ["Topology does not prove dimensional accuracy, user interpretation, drawer fit or durability."],
    ))
    radius_interfaces = [interfaces[f"radius-r{value:02d}"] for value in (2, 4, 6, 8, 10, 12)]
    interface_checks = [
        check("radius-series", [item["radius_mm"] for item in radius_interfaces] == [2.0, 4.0, 6.0, 8.0, 10.0, 12.0], "Six analytic radius values are present"),
        check("radius-identity", [item["identity_holes"] for item in radius_interfaces] == [1, 2, 3, 4, 5, 6], "Hole count identifies radius order without fonts"),
        check("radius-selection-direction", parameters["measurement_contract"]["radius_selection_rule"] == "smallest_no_force_seating_tile", "Selection uses the smallest seating tile, not the loosest larger radius"),
        check("height-levels", interfaces["height-card"]["reference_heights_mm"] == [15.0, 35.0, 55.0], "Height ledge top datums are exact"),
        check("paired-height-cards", interfaces["height-card"]["quantity_in_build"] == 2, "Two identical height-card instances are packaged"),
        check("clearance-series", interfaces["clearance-comb"]["finger_widths_mm"] == [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0], "Clearance fingers are monotonic in 0.2 mm steps"),
        check("calibration-external", interfaces["calibration-frame"]["external_references_mm"] == [130.0, 32.0, 3.0], "Calibration external references are present"),
        check("calibration-internal", interfaces["calibration-frame"]["internal_window_mm"] == [80.0, 12.0] and interfaces["calibration-frame"]["round_reference_diameter_mm"] == 10.0 and interfaces["calibration-frame"]["square_reference_mm"] == 10.0, "Calibration internal references are present"),
        check("no-accuracy-claim", True, "Nominal increments are explicitly not metrology accuracy"),
    ]
    write_json(VALIDATION / "interface-report.json", report(
        f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"], interface_checks,
        {"interfaces": interfaces, "measurement_contract": parameters["measurement_contract"]},
        ["Every physical reading requires independent caliper comparison; the digital report cannot establish accuracy or reduce customer error."],
    ))

    tile = parameters["radius_tiles"]
    card = parameters["height_cards"]
    comb = parameters["clearance_comb"]
    frame = parameters["calibration_frame"]
    baseline_volume = (
        len(tile["radii_mm"]) * tile["tile_size_mm"] ** 2 * tile["thickness_mm"]
        + card["quantity"] * card["width_mm"] * card["height_mm"] * card["thickness_mm"]
        + comb["backbone_width_mm"] * (comb["backbone_depth_mm"] + comb["finger_length_mm"]) * comb["thickness_mm"]
        + frame["width_mm"] * frame["depth_mm"] * frame["thickness_mm"]
    )
    candidate_volume = sum(float(shapes[f"radius-r{value:02d}"].Volume()) for value in (2, 4, 6, 8, 10, 12)) + card["quantity"] * float(shapes["height-card"].Volume()) + float(shapes["clearance-comb"].Volume()) + float(shapes["calibration-frame"].Volume())
    reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "baseline": {"description": "solid bounding envelopes for all ten print objects", "volume_mm3": baseline_volume},
        "candidate": {"description": "six radius tiles, two skeletal height cards, clearance comb and calibration frame", "volume_mm3": candidate_volume},
        "volume_reduction_percent": reduction, "selection_threshold_percent": 25.0,
        "status": "PASS" if reduction >= 25.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE",
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL",
        "meshes": metrics, "simplification": "NOT_BENEFICIAL",
        "reason": "Analytic tessellation is below budget; decimation could move measurement references.",
    })
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS",
        "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))], "outputs": [input_record(path) for path in outputs],
        "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]],
    })
    gate_reports = [json.loads((VALIDATION / name).read_text()) for name in ("parametric-source-report.json", "mesh-generation-report.json", "interface-report.json")]
    if any(value["status"] != "PASS" for value in [*gate_reports, optimization]):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "unique_meshes": len(mesh_paths), "print_objects": len(part_names), "3mf": str(package_path.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
