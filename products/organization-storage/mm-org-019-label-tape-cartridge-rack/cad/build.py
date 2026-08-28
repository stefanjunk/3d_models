#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-019 label-tape cartridge rack family."""
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
PROJECT_ID = "MM-ORG-019"
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
    return {
        "schema_version": "1.0", "tool": tool, "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft", "inputs": [input_record(path) for path in inputs],
        "checks": checks, "metrics": metrics, "limitations": limitations, "required_capabilities": [],
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rounded_rectangle(width: float, depth: float, height: float, radius: float) -> cq.Shape:
    return (
        cq.Workplane("XY").rect(width, depth).extrude(height).edges("|Z").fillet(radius).val()
        .translate((width / 2.0, depth / 2.0, 0.0))
    )


def rack_dimensions(parameters: dict, preset: dict) -> dict:
    rack = parameters["rack"]
    clear_width = preset["measured_envelope_thickness_mm"] + 2.0 * preset["slot_clearance_mm"]
    clear_depth = preset["measured_envelope_depth_mm"] + rack["depth_clearance_mm"]
    width = (preset["slot_count"] + 1) * rack["divider_thickness_mm"] + preset["slot_count"] * clear_width
    depth = rack["front_wall_thickness_mm"] + clear_depth + rack["rear_wall_thickness_mm"]
    pitch = clear_width + rack["divider_thickness_mm"]
    return {"clear_width_mm": clear_width, "clear_depth_mm": clear_depth, "width_mm": width, "depth_mm": depth, "pitch_mm": pitch}


def male_tab(parameters: dict, x_origin: float, center_y: float) -> cq.Shape:
    connector = parameters["connector"]
    neck = connector["neck_width_mm"] / 2.0
    head = connector["head_width_mm"] / 2.0
    depth = connector["tab_depth_mm"]
    points = [(x_origin, center_y - neck), (x_origin + depth, center_y - head), (x_origin + depth, center_y + head), (x_origin, center_y + neck)]
    return cq.Workplane("XY").polyline(points).close().extrude(connector["height_mm"]).val()


def female_socket(parameters: dict, center_y: float) -> cq.Shape:
    connector = parameters["connector"]
    clearance = connector["default_clearance_mm"]
    neck = connector["neck_width_mm"] / 2.0 + clearance
    head = connector["head_width_mm"] / 2.0 + clearance
    depth = connector["tab_depth_mm"] + clearance
    points = [(-0.1, center_y - neck), (depth, center_y - head), (depth, center_y + head), (-0.1, center_y + neck)]
    return cq.Workplane("XY").polyline(points).close().extrude(connector["height_mm"] + 0.2).val().translate((0.0, 0.0, -0.1))


def rear_rest(width: float, depth: float, parameters: dict) -> cq.Shape:
    rack = parameters["rack"]
    inside_bottom_y = depth - rack["rear_wall_thickness_mm"]
    shift = math.tan(math.radians(rack["lean_angle_deg"])) * rack["retaining_height_mm"]
    profile = (
        cq.Workplane("YZ")
        .moveTo(inside_bottom_y, 0.0)
        .lineTo(depth, 0.0)
        .lineTo(depth, rack["retaining_height_mm"])
        .lineTo(inside_bottom_y - shift, rack["retaining_height_mm"])
        .close()
        .extrude(width)
        .val()
    )
    return profile


def make_rack(parameters: dict, preset: dict) -> tuple[cq.Shape, dict]:
    rack = parameters["rack"]
    connector = parameters["connector"]
    dims = rack_dimensions(parameters, preset)
    width = dims["width_mm"]
    depth = dims["depth_mm"]
    shape = rounded_rectangle(width, depth, rack["base_thickness_mm"], rack["outer_corner_radius_mm"])

    for index in range(preset["slot_count"] + 1):
        x = index * dims["pitch_mm"]
        divider = cq.Solid.makeBox(
            rack["divider_thickness_mm"], depth, rack["retaining_height_mm"], cq.Vector(x, 0.0, 0.0)
        )
        shape = shape.fuse(divider)

    front = cq.Solid.makeBox(width, rack["front_wall_thickness_mm"], rack["front_lip_height_mm"])
    shape = shape.fuse(front).fuse(rear_rest(width, depth, parameters))

    joint_centers = connector["centers_y_mm"]
    for center_y in joint_centers:
        shape = shape.fuse(male_tab(parameters, width, center_y))
        shape = shape.cut(female_socket(parameters, center_y))

    recess_cutters: list[cq.Shape] = []
    dot_cutters: list[cq.Shape] = []
    for slot_index in range(preset["slot_count"]):
        slot_start = rack["divider_thickness_mm"] + slot_index * dims["pitch_mm"]
        recess_width = dims["clear_width_mm"] - 2.0 * rack["label_recess_side_margin_mm"]
        recess_cutters.append(cq.Solid.makeBox(
            recess_width, rack["label_recess_depth_mm"] + 0.1, rack["label_recess_height_mm"],
            cq.Vector(slot_start + rack["label_recess_side_margin_mm"], -0.1, rack["label_recess_bottom_z_mm"]),
        ))
        slot_center = slot_start + dims["clear_width_mm"] / 2.0
        for offset in (-2.5, 2.5):
            dot_cutters.append(cq.Solid.makeCylinder(
                rack["status_dot_diameter_mm"] / 2.0,
                rack["label_recess_depth_mm"] + rack["status_dot_depth_mm"] + 0.1,
                cq.Vector(slot_center + offset, -0.1, rack["label_recess_bottom_z_mm"] + rack["label_recess_height_mm"] / 2.0),
                cq.Vector(0.0, 1.0, 0.0),
            ))
    shape = shape.cut(cq.Compound.makeCompound(recess_cutters))
    shape = shape.cut(cq.Compound.makeCompound(dot_cutters))

    marker_cutters: list[cq.Shape] = []
    marker_y = depth - 1.0
    for index in range(preset["identity_holes"]):
        marker_cutters.append(cq.Solid.makeCylinder(
            1.2, 0.7, cq.Vector(7.0 + 5.0 * index, marker_y, rack["retaining_height_mm"] - 0.6)
        ))
    shape = shape.cut(cq.Compound.makeCompound(marker_cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"{preset['id']} is not one valid solid")
    return shape, {
        "preset_id": preset["id"], "slot_count": preset["slot_count"],
        "measured_envelope_mm": [preset["measured_envelope_depth_mm"], preset["measured_envelope_thickness_mm"], preset["measured_envelope_height_mm"]],
        "slot_clearance_per_side_mm": preset["slot_clearance_mm"],
        "slot_clear_width_mm": dims["clear_width_mm"], "slot_clear_depth_mm": dims["clear_depth_mm"],
        "outer_dimensions_mm": [width + connector["tab_depth_mm"], depth, rack["retaining_height_mm"]],
        "lean_angle_deg": rack["lean_angle_deg"], "label_fields": preset["slot_count"],
        "status_dot_pairs": preset["slot_count"], "joint_centers_y_mm": joint_centers,
        "identity_holes": preset["identity_holes"], "external_assets": [],
    }


def make_clearance_coupon(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    clearances = coupon["clearances_mm"]
    bay_widths = [coupon["nominal_thickness_mm"] + 2.0 * value for value in clearances]
    total_width = sum(bay_widths) + (len(bay_widths) + 1) * coupon["wall_thickness_mm"]
    total_depth = coupon["bay_depth_mm"] + coupon["back_wall_thickness_mm"]
    shape = rounded_rectangle(total_width, total_depth, coupon["base_thickness_mm"], 1.5)
    x = 0.0
    divider_positions = [x]
    for bay_width in bay_widths:
        x += coupon["wall_thickness_mm"] + bay_width
        divider_positions.append(x)
    for divider_x in divider_positions:
        shape = shape.fuse(cq.Solid.makeBox(
            coupon["wall_thickness_mm"], total_depth, coupon["wall_height_mm"], cq.Vector(divider_x, 0.0, 0.0)
        ))
    shape = shape.fuse(cq.Solid.makeBox(total_width, coupon["back_wall_thickness_mm"], coupon["wall_height_mm"], cq.Vector(0.0, coupon["bay_depth_mm"], 0.0)))
    marker_cutters: list[cq.Shape] = []
    x = coupon["wall_thickness_mm"]
    for bay_index, bay_width in enumerate(bay_widths, 1):
        center = x + bay_width / 2.0
        for hole_index in range(bay_index):
            marker_cutters.append(cq.Solid.makeCylinder(
                coupon["identity_hole_diameter_mm"] / 2.0, 0.7,
                cq.Vector(center + (hole_index - (bay_index - 1) / 2.0) * 3.0, total_depth - 1.0, coupon["wall_height_mm"] - 0.6),
            ))
        x += bay_width + coupon["wall_thickness_mm"]
    shape = shape.cut(cq.Compound.makeCompound(marker_cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("clearance coupon is not one valid solid")
    return shape, {
        "nominal_thickness_mm": coupon["nominal_thickness_mm"], "clearances_per_side_mm": clearances,
        "bay_clear_widths_mm": bay_widths, "identity_holes": [1, 2, 3],
        "outer_dimensions_mm": [total_width, total_depth, coupon["wall_height_mm"]], "external_assets": [],
    }


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    rack = parameters["rack"]
    connector = parameters["connector"]
    coupon = parameters["coupon"]
    printer = parameters["printer"]
    assert project["id"] == PROJECT_ID and project["revision"] == REVISION and project["units"] == "mm"
    assert [item["id"] for item in parameters["presets"]] == ["compact-six", "extended-five"]
    assert all(item["slot_count"] >= 3 for item in parameters["presets"])
    assert all(item["slot_clearance_mm"] == connector["default_clearance_mm"] * 2.0 for item in parameters["presets"])
    assert rack["base_thickness_mm"] == connector["height_mm"] == coupon["base_thickness_mm"]
    assert rack["divider_thickness_mm"] / printer["line_width_mm"] >= 4.0
    assert rack["front_wall_thickness_mm"] - rack["label_recess_depth_mm"] - rack["status_dot_depth_mm"] >= 1.0
    assert 5.0 <= rack["lean_angle_deg"] <= 12.0
    assert coupon["clearances_mm"] == [0.3, 0.5, 0.7]
    assert coupon["clearances_mm"][1] == parameters["presets"][0]["slot_clearance_mm"]
    assert connector["default_clearance_mm"] == 0.25
    assert parameters["workflow_contract"]["compatibility_claim"] == "none_until_physical_fit_test"
    for preset in parameters["presets"]:
        dims = rack_dimensions(parameters, preset)
        assert dims["width_mm"] + connector["tab_depth_mm"] <= 220.0
        assert dims["depth_mm"] <= 140.0
        assert rack["retaining_height_mm"] <= 120.0


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
    for preset in parameters["presets"]:
        shapes[preset["id"]], interfaces[preset["id"]] = make_rack(parameters, preset)
    shapes["clearance-coupon"], interfaces["clearance-coupon"] = make_clearance_coupon(parameters)

    step_paths: list[Path] = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    compact_width = rack_dimensions(parameters, parameters["presets"][0])["width_mm"] + parameters["connector"]["tab_depth_mm"]
    assembly = cq.Compound.makeCompound([
        shapes["compact-six"], shapes["extended-five"].translate((compact_width + 20.0, 0.0, 0.0)),
        shapes["clearance-coupon"].translate((0.0, 115.0, 0.0)),
    ])
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"
    export_step(assembly, assembly_path)
    step_paths.append(assembly_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("compact-six", "extended-five"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-rack-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    coupon_path = COUPONS / f"DRAFT-{PROJECT_ID}-clearance-coupon-{REVISION}.stl"
    export_stl(shapes["clearance-coupon"], coupon_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    mesh_paths["clearance-coupon"] = coupon_path

    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-label-tape-cartridge-rack-{REVISION}.3mf"
    write_3mf(package_path, [(name, mesh_paths[name]) for name in ("compact-six", "extended-five", "clearance-coupon")], [(10.0, 10.0), (160.0, 10.0), (10.0, 130.0)])

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
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All three unique B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every deliverable is one B-Rep solid"),
        check("two-unbranded-presets", [item["preset_id"] for key, item in interfaces.items() if key != "clearance-coupon"] == ["compact-six", "extended-five"], "Two measured-envelope presets are generated"),
        check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "Geometry uses no third-party font, vector or mesh assets"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", report(
        f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)], parametric_checks,
        {"python": platform.python_version(), "cadquery": cq.__version__, "unique_parts": list(shapes), "print_objects": list(mesh_paths)},
        ["Any parameter change requires regeneration of downstream evidence."],
    ))
    write_json(VALIDATION / "mesh-generation-report.json", report(
        f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks, {"meshes": metrics},
        ["Topology does not prove cartridge compatibility, connector fit, label adhesion or retrieval durability."],
    ))
    rack_interfaces = [interfaces[item["id"]] for item in parameters["presets"]]
    interface_checks = [
        check("slot-clearance", all(item["slot_clearance_per_side_mm"] == 0.5 for item in rack_interfaces), "Both presets apply 0.50 mm clearance on each thickness side"),
        check("depth-clearance", all(item["slot_clear_depth_mm"] - item["measured_envelope_mm"][0] == 1.0 for item in rack_interfaces), "Both presets apply 1.00 mm rear depth clearance"),
        check("lean-angle", all(item["lean_angle_deg"] == 8.0 for item in rack_interfaces), "Rear rests share the bounded 8 degree lean"),
        check("label-fields", all(item["label_fields"] == item["slot_count"] for item in rack_interfaces), "Every slot has one adhesive-label field"),
        check("status-fields", all(item["status_dot_pairs"] == item["slot_count"] for item in rack_interfaces), "Every slot has a two-state dot field"),
        check("connector-common", rack_interfaces[0]["joint_centers_y_mm"] == rack_interfaces[1]["joint_centers_y_mm"] == [25.0, 55.0], "Both rack depths use the same two absolute connector datums"),
        check("coupon-brackets-default", interfaces["clearance-coupon"]["clearances_per_side_mm"] == [0.3, 0.5, 0.7], "Coupon brackets the 0.50 mm default"),
        check("portfolio-envelope", all(item["outer_dimensions_mm"][0] <= 220.0 and item["outer_dimensions_mm"][1] <= 140.0 and item["outer_dimensions_mm"][2] <= 120.0 for item in rack_interfaces), "Both racks fit the portfolio envelope"),
        check("no-compatibility-claim", parameters["workflow_contract"]["compatibility_claim"] == "none_until_physical_fit_test", "Named compatibility remains blocked"),
    ]
    write_json(VALIDATION / "interface-report.json", report(
        f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"], interface_checks,
        {"interfaces": interfaces, "workflow_contract": parameters["workflow_contract"]},
        ["The nominal envelopes are transparent examples, not evidence of fit with any named cartridge family."],
    ))

    rack_names = ("compact-six", "extended-five")
    baseline_volume = sum(
        rack_dimensions(parameters, preset)["width_mm"] * rack_dimensions(parameters, preset)["depth_mm"] * parameters["rack"]["retaining_height_mm"]
        for preset in parameters["presets"]
    )
    candidate_volume = sum(float(shapes[name].Volume()) for name in rack_names)
    reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "baseline": {"description": "two solid rack envelope blocks", "volume_mm3": baseline_volume},
        "candidate": {"description": "thin bases, dividers, label rails, rear rests and planar joints", "volume_mm3": candidate_volume},
        "volume_reduction_percent": reduction, "selection_threshold_percent": 65.0,
        "status": "PASS" if reduction >= 65.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE",
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL",
        "meshes": metrics, "simplification": "NOT_BENEFICIAL",
        "reason": "Analytic tessellation is below budget; decimation could move slot and connector interfaces.",
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
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "unique_meshes": len(mesh_paths), "3mf": str(package_path.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
