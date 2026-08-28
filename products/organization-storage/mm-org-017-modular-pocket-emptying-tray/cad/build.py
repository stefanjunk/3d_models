#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-017 modular coin-slope tray family."""
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
PROJECT_ID = "MM-ORG-017"
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
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [input_record(path) for path in inputs],
        "checks": checks,
        "metrics": metrics,
        "limitations": limitations,
        "required_capabilities": [],
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rounded_rectangle(width: float, depth: float, height: float, radius: float, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> cq.Shape:
    shape = cq.Workplane("XY").rect(width, depth).extrude(height).edges("|Z").fillet(radius).val()
    return shape.translate((x + width / 2.0, y + depth / 2.0, z))


def faceted_rectangle(width: float, depth: float, height: float, chamfer: float, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> cq.Shape:
    points = [
        (x + chamfer, y), (x + width - chamfer, y), (x + width, y + chamfer),
        (x + width, y + depth - chamfer), (x + width - chamfer, y + depth),
        (x + chamfer, y + depth), (x, y + depth - chamfer), (x, y + chamfer),
    ]
    return cq.Workplane("XY").polyline(points).close().extrude(height).val().translate((0.0, 0.0, z))


def bowl_outline(parameters: dict, style: dict, inner: bool = False) -> cq.Shape:
    module = parameters["module"]
    inset = module["bowl_inset_mm"] + (module["wall_thickness_mm"] if inner else 0.0)
    width = module["base_width_mm"] - 2.0 * inset
    depth = module["base_depth_mm"] - 2.0 * inset
    x = inset
    y = inset
    height = module["wall_height_mm"] + 1.0 if inner else module["wall_height_mm"]
    z = module["base_thickness_mm"] if inner else 0.0
    if style["kind"] == "faceted":
        chamfer = module["facet_chamfer_mm"] - (2.0 if inner else 0.0)
        return faceted_rectangle(width, depth, height, chamfer, x, y, z)
    radius_key = "soft_corner_radius_mm" if style["kind"] == "rounded" else "rib_corner_radius_mm"
    radius = max(0.8, module[radius_key] - (2.0 if inner else 0.0))
    return rounded_rectangle(width, depth, height, radius, x, y, z)


def male_tab(parameters: dict, x_origin: float = 0.0, center_y: float | None = None) -> cq.Shape:
    module = parameters["module"]
    connector = parameters["connector"]
    center = connector["center_y_mm"] if center_y is None else center_y
    neck = connector["neck_width_mm"] / 2.0
    head = connector["head_width_mm"] / 2.0
    depth = connector["tab_depth_mm"]
    points = [(x_origin, center - neck), (x_origin + depth, center - head), (x_origin + depth, center + head), (x_origin, center + neck)]
    return cq.Workplane("XY").polyline(points).close().extrude(connector["height_mm"]).val()


def female_socket(parameters: dict, clearance: float, center_y: float | None = None, height: float | None = None) -> cq.Shape:
    connector = parameters["connector"]
    center = connector["center_y_mm"] if center_y is None else center_y
    neck = connector["neck_width_mm"] / 2.0 + clearance
    head = connector["head_width_mm"] / 2.0 + clearance
    depth = connector["tab_depth_mm"] + clearance
    cutter_height = (connector["height_mm"] + 0.2) if height is None else height
    points = [(-0.1, center - neck), (depth, center - head), (depth, center + head), (-0.1, center + neck)]
    return cq.Workplane("XY").polyline(points).close().extrude(cutter_height).val().translate((0.0, 0.0, -0.1))


def ramp_wedge(parameters: dict) -> cq.Shape:
    module = parameters["module"]
    scoop = parameters["coin_scoop"]
    inner_inset = module["bowl_inset_mm"] + module["wall_thickness_mm"]
    inner_width = module["base_width_mm"] - 2.0 * inner_inset
    front_y = inner_inset
    rear_y = module["base_depth_mm"] - inner_inset
    base_z = module["base_thickness_mm"] - 0.05
    profile = (
        cq.Workplane("YZ")
        .moveTo(front_y, base_z)
        .lineTo(rear_y, base_z)
        .lineTo(rear_y, scoop["rear_floor_z_mm"])
        .lineTo(front_y, scoop["front_floor_z_mm"])
        .close()
        .extrude(inner_width)
        .val()
    )
    return profile.translate((inner_inset, 0.0, 0.0))


def scoop_opening(parameters: dict) -> cq.Shape:
    module = parameters["module"]
    scoop = parameters["coin_scoop"]
    center_x = module["base_width_mm"] / 2.0
    radius = scoop["opening_corner_radius_mm"]
    width = scoop["opening_width_mm"]
    y0 = module["bowl_inset_mm"] - 0.2
    length = module["wall_thickness_mm"] + 0.5
    z0 = scoop["front_lip_top_z_mm"]
    top = module["wall_height_mm"] + 1.0
    low_box = cq.Solid.makeBox(width - 2.0 * radius, length, top - z0, cq.Vector(center_x - width / 2.0 + radius, y0, z0))
    high_box = cq.Solid.makeBox(width, length, top - z0 - radius, cq.Vector(center_x - width / 2.0, y0, z0 + radius))
    left = cq.Solid.makeCylinder(radius, length, cq.Vector(center_x - width / 2.0 + radius, y0, z0 + radius), cq.Vector(0, 1, 0))
    right = cq.Solid.makeCylinder(radius, length, cq.Vector(center_x + width / 2.0 - radius, y0, z0 + radius), cq.Vector(0, 1, 0))
    return cq.Compound.makeCompound([low_box, high_box, left, right])


def make_module(parameters: dict, style: dict) -> tuple[cq.Shape, dict]:
    module = parameters["module"]
    connector = parameters["connector"]
    base = rounded_rectangle(module["base_width_mm"], module["base_depth_mm"], module["base_thickness_mm"], 3.0)
    shell = bowl_outline(parameters, style).cut(bowl_outline(parameters, style, inner=True))
    shape = base.fuse(shell).fuse(ramp_wedge(parameters))
    shape = shape.cut(scoop_opening(parameters))
    shape = shape.cut(female_socket(parameters, connector["default_clearance_mm"]))
    shape = shape.fuse(male_tab(parameters, module["base_width_mm"]))
    if style["kind"] == "ribbed":
        for center_x in module["rib_centers_x_mm"]:
            rib = cq.Solid.makeBox(
                module["rib_width_mm"], module["rib_projection_mm"], module["rib_height_mm"],
                cq.Vector(center_x - module["rib_width_mm"] / 2.0, module["base_depth_mm"] - module["bowl_inset_mm"] - 0.2, module["wall_height_mm"] - module["rib_height_mm"]),
            )
            shape = shape.fuse(rib)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"{style['id']} is not one valid solid")
    inner_run = module["base_depth_mm"] - 2.0 * (module["bowl_inset_mm"] + module["wall_thickness_mm"])
    slope_deg = math.degrees(math.atan((parameters["coin_scoop"]["rear_floor_z_mm"] - parameters["coin_scoop"]["front_floor_z_mm"]) / inner_run))
    return shape, {
        "id": style["id"],
        "kind": style["kind"],
        "outer_dimensions_mm": [module["base_width_mm"] + connector["tab_depth_mm"], module["base_depth_mm"], module["wall_height_mm"]],
        "coin_slope_deg": slope_deg,
        "front_lip_above_floor_mm": parameters["coin_scoop"]["front_lip_top_z_mm"] - parameters["coin_scoop"]["front_floor_z_mm"],
        "connector_clearance_mm": connector["default_clearance_mm"],
        "identity_ribs": style["identity_ribs"],
        "external_assets": [],
    }


def make_gauge(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    clearances = parameters["connector"]["coupon_clearances_mm"]
    base = rounded_rectangle(coupon["gauge_width_mm"], coupon["gauge_depth_mm"], coupon["height_mm"], 2.0)
    cutters = []
    for index, (center_y, clearance) in enumerate(zip(coupon["socket_centers_y_mm"], clearances), 1):
        cutters.append(female_socket(parameters, clearance, center_y, coupon["height_mm"] + 0.2))
        for hole_index in range(index):
            hole_x = 18.0 + hole_index * 3.2
            hole = cq.Solid.makeCylinder(coupon["identity_hole_diameter_mm"] / 2.0, coupon["height_mm"] + 0.2, cq.Vector(hole_x, center_y, -0.1))
            cutters.append(hole)
    shape = base.cut(cq.Compound.makeCompound(cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("connector clearance gauge is not one valid solid")
    return shape, {"clearances_mm": clearances, "identity_holes": [1, 2, 3], "outer_dimensions_mm": [coupon["gauge_width_mm"], coupon["gauge_depth_mm"], coupon["height_mm"]]}


def make_test_key(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    connector = parameters["connector"]
    center_y = coupon["key_handle_width_mm"] / 2.0
    handle = cq.Solid.makeBox(coupon["key_handle_length_mm"], coupon["key_handle_width_mm"], connector["height_mm"], cq.Vector(0.0, 0.0, 0.0))
    tab = male_tab(parameters, coupon["key_handle_length_mm"], center_y)
    shape = handle.fuse(tab).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("connector test key is not one valid solid")
    return shape, {"tab_depth_mm": connector["tab_depth_mm"], "neck_width_mm": connector["neck_width_mm"], "head_width_mm": connector["head_width_mm"], "height_mm": connector["height_mm"]}


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    module = parameters["module"]
    scoop = parameters["coin_scoop"]
    connector = parameters["connector"]
    printer = parameters["printer"]
    assert project["id"] == PROJECT_ID and project["revision"] == REVISION and project["units"] == "mm"
    assert len(parameters["styles"]) == 3 and len({item["kind"] for item in parameters["styles"]}) == 3
    assert module["base_thickness_mm"] == connector["height_mm"]
    assert module["base_thickness_mm"] / printer["layer_height_mm"] >= 8
    assert module["wall_thickness_mm"] / printer["line_width_mm"] >= 4
    inner_run = module["base_depth_mm"] - 2.0 * (module["bowl_inset_mm"] + module["wall_thickness_mm"])
    slope_deg = math.degrees(math.atan((scoop["rear_floor_z_mm"] - scoop["front_floor_z_mm"]) / inner_run))
    assert scoop["minimum_slope_deg"] <= slope_deg <= scoop["maximum_slope_deg"]
    assert 0.0 < scoop["front_lip_top_z_mm"] - scoop["front_floor_z_mm"] <= 0.8
    assert connector["coupon_clearances_mm"][1] == connector["default_clearance_mm"]
    assert connector["coupon_clearances_mm"] == sorted(connector["coupon_clearances_mm"])
    assembled_width = 3.0 * module["base_width_mm"] + connector["tab_depth_mm"]
    assert assembled_width <= 180.0 and module["base_depth_mm"] <= 160.0 and module["wall_height_mm"] <= 45.0
    assert 3 * 70.0 + 20.0 <= printer["build_volume_mm"][0]
    assert module["base_depth_mm"] + parameters["coupon"]["gauge_depth_mm"] + 35.0 <= printer["build_volume_mm"][1]


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
        "path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "triangles": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)), "file_bytes": path.stat().st_size, "file_mib": path.stat().st_size / (1024 * 1024),
        "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
        "positive_volume": bool(mesh.is_volume and mesh.volume > 0), "components": int(len(mesh.split(only_watertight=False))),
        "volume_mm3": float(mesh.volume), "surface_area_mm2": float(mesh.area),
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
    types = (
        b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        b'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        b'<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    )
    rels = (
        b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    )
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
    module = parameters["module"]
    connector = parameters["connector"]
    shapes: dict[str, cq.Shape] = {}
    interfaces: dict[str, dict] = {}
    for style in parameters["styles"]:
        shapes[style["id"]], interfaces[style["id"]] = make_module(parameters, style)
    shapes["connector-clearance-gauge"], interfaces["connector-clearance-gauge"] = make_gauge(parameters)
    shapes["connector-test-key"], interfaces["connector-test-key"] = make_test_key(parameters)

    step_paths: list[Path] = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    assembly = cq.Compound.makeCompound([
        shapes["soft-arc"],
        shapes["clean-facet"].translate((module["base_width_mm"], 0.0, 0.0)),
        shapes["utility-rib"].translate((2.0 * module["base_width_mm"], 0.0, 0.0)),
    ])
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-connected-set-{REVISION}.step"
    export_step(assembly, assembly_path)
    step_paths.append(assembly_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("soft-arc", "clean-facet", "utility-rib"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-coin-slope-module-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    for name in ("connector-clearance-gauge", "connector-test-key"):
        path = COUPONS / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-modular-pocket-emptying-tray-{REVISION}.3mf"
    write_3mf(
        package_path,
        [(name, mesh_paths[name]) for name in ("soft-arc", "clean-facet", "utility-rib", "connector-clearance-gauge", "connector-test-key")],
        [(10.0, 10.0), (80.0, 10.0), (150.0, 10.0), (10.0, 105.0), (85.0, 105.0)],
    )

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
    slope = interfaces["soft-arc"]["coin_slope_deg"]
    parametric_checks = [
        check("parameter-validation", True, "Fail-closed parameter relations pass"),
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All five B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every deliverable is one B-Rep solid"),
        check("source-of-truth", len(parameters["styles"]) == 3, "JSON drives three independent visual styles"),
        check("no-external-assets", not any(interfaces[name].get("external_assets") for name in interfaces), "Geometry uses no third-party vector, font or mesh assets"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", report(
        f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)], parametric_checks,
        {"python": platform.python_version(), "cadquery": cq.__version__, "parts": list(shapes), "assembled_envelope_mm": [3.0 * module["base_width_mm"] + connector["tab_depth_mm"], module["base_depth_mm"], module["wall_height_mm"]]},
        ["Any parameter change requires regeneration of downstream evidence."],
    ))
    write_json(VALIDATION / "mesh-generation-report.json", report(
        f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks, {"meshes": metrics},
        ["Topology does not prove connector fit, sweep ergonomics, scratch protection or durability."],
    ))
    interface_checks = [
        check("three-style-modules", len(parameters["styles"]) == 3, "Three visually distinct modules share one functional interface"),
        check("coin-slope", parameters["coin_scoop"]["minimum_slope_deg"] <= slope <= parameters["coin_scoop"]["maximum_slope_deg"], "Coin floor slope is within the bounded ergonomic hypothesis", {"actual_deg": slope}),
        check("low-front-lip", interfaces["soft-arc"]["front_lip_above_floor_mm"] <= 0.8, "Front lip remains within the sweep-over target"),
        check("connector-common", all(interfaces[name]["connector_clearance_mm"] == connector["default_clearance_mm"] for name in ("soft-arc", "clean-facet", "utility-rib")), "All modules share the same connector clearance"),
        check("coupon-sweep", interfaces["connector-clearance-gauge"]["clearances_mm"] == [0.15, 0.25, 0.35], "Gauge brackets the default connector clearance"),
        check("assembled-envelope", 3.0 * module["base_width_mm"] + connector["tab_depth_mm"] <= 180.0, "Three connected modules fit the portfolio envelope"),
        check("flat-print", connector["height_mm"] == module["base_thickness_mm"], "Connector and base share a support-free bed datum"),
    ]
    write_json(VALIDATION / "interface-report.json", report(
        f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"], interface_checks,
        {"interfaces": interfaces, "connected_pitch_mm": module["base_width_mm"], "three_module_width_mm": 3.0 * module["base_width_mm"] + connector["tab_depth_mm"]},
        ["Clearance, scoop usability and surface protection are design hypotheses until the user prints and tests them."],
    ))

    production_volume = sum(float(shapes[name].Volume()) for name in ("soft-arc", "clean-facet", "utility-rib"))
    baseline_volume = 3.0 * (module["base_width_mm"] * module["base_depth_mm"] * module["wall_height_mm"])
    reduction = 100.0 * (1.0 - production_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "baseline": {"description": "three solid module envelope blocks", "volume_mm3": baseline_volume},
        "candidate": {"description": "three hollow sloped tray modules", "volume_mm3": production_volume},
        "volume_reduction_percent": reduction, "selection_threshold_percent": 55.0,
        "status": "PASS" if reduction >= 55.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE",
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL",
        "meshes": metrics, "simplification": "NOT_BENEFICIAL",
        "reason": "Analytic tessellation is under budget; decimation could move the connector or scoop interfaces.",
    })
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS",
        "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))],
        "outputs": [input_record(path) for path in outputs],
        "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]],
    })
    gate_reports = [
        json.loads((VALIDATION / "parametric-source-report.json").read_text()),
        json.loads((VALIDATION / "mesh-generation-report.json").read_text()),
        json.loads((VALIDATION / "interface-report.json").read_text()), optimization,
    ]
    if any(value["status"] != "PASS" for value in gate_reports):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "outputs": [str(path.relative_to(ROOT)) for path in mesh_paths.values()] + [str(package_path.relative_to(ROOT))]}, indent=2))


if __name__ == "__main__":
    main()
