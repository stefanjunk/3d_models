#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-021 eyeglass-case shelf-corral family."""
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
PROJECT_ID = "MM-ORG-021"
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
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": [input_record(path) for path in inputs], "checks": checks, "metrics": metrics,
        "limitations": limitations, "required_capabilities": [],
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def floor_rise(parameters: dict) -> float:
    corral = parameters["corral"]
    return math.tan(math.radians(corral["floor_back_lean_deg"])) * corral["base_depth_mm"]


def corral_dimensions(parameters: dict, preset: dict) -> dict:
    corral = parameters["corral"]
    lanes = preset["lane_clear_widths_mm"]
    width = sum(lanes) + (len(lanes) + 1) * corral["divider_thickness_mm"]
    return {"width_mm": width, "depth_mm": corral["base_depth_mm"], "height_mm": corral["divider_height_mm"], "lane_count": len(lanes)}


def sloped_base(parameters: dict, width: float) -> cq.Shape:
    corral = parameters["corral"]
    depth = corral["base_depth_mm"]
    rear = corral["base_rear_thickness_mm"]
    rise = floor_rise(parameters)
    return (
        cq.Workplane("YZ")
        .polyline([(0.0, 0.0), (depth, 0.0), (depth, rear), (0.0, rear + rise)])
        .close()
        .extrude(width)
        .val()
    )


def soft_divider(parameters: dict, x: float) -> cq.Shape:
    corral = parameters["corral"]
    shape = (
        cq.Workplane("XY")
        .box(corral["divider_thickness_mm"], corral["base_depth_mm"], corral["divider_height_mm"], centered=(False, False, False))
        .edges("|Z").fillet(corral["divider_leading_radius_mm"])
        .faces(">Z").edges().fillet(corral["divider_top_radius_mm"])
        .val()
    )
    return shape.translate((x, 0.0, 0.0))


def make_corral(parameters: dict, preset: dict) -> tuple[cq.Shape, dict]:
    corral = parameters["corral"]
    dims = corral_dimensions(parameters, preset)
    width = dims["width_mm"]
    rise = floor_rise(parameters)
    front_height = corral["base_rear_thickness_mm"] + rise + corral["front_stop_height_above_floor_mm"]
    base = sloped_base(parameters, width)
    front = cq.Solid.makeBox(width, corral["front_stop_depth_mm"], front_height)
    rear = cq.Solid.makeBox(
        width, corral["rear_wall_depth_mm"], corral["rear_wall_height_mm"],
        cq.Vector(0.0, corral["base_depth_mm"] - corral["rear_wall_depth_mm"], 0.0),
    )
    shape = base.fuse(front).fuse(rear)

    divider_positions = [0.0]
    cursor = 0.0
    for lane_width in preset["lane_clear_widths_mm"]:
        cursor += corral["divider_thickness_mm"] + lane_width
        divider_positions.append(cursor)
    for x in divider_positions:
        shape = shape.fuse(soft_divider(parameters, x))

    label_cutters: list[cq.Shape] = []
    cursor = corral["divider_thickness_mm"]
    for lane_width in preset["lane_clear_widths_mm"]:
        label_width = lane_width - 2.0 * corral["label_side_margin_mm"]
        label_cutters.append(cq.Solid.makeBox(
            label_width, corral["label_recess_depth_mm"] + 0.1, corral["label_recess_height_mm"],
            cq.Vector(cursor + corral["label_side_margin_mm"], -0.1, corral["label_recess_bottom_z_mm"]),
        ))
        cursor += lane_width + corral["divider_thickness_mm"]
    shape = shape.cut(cq.Compound.makeCompound(label_cutters))

    marker_cutters: list[cq.Shape] = []
    for index in range(preset["identity_holes"]):
        marker_cutters.append(cq.Solid.makeCylinder(
            1.2, corral["front_stop_depth_mm"] + 0.2,
            cq.Vector(width - 8.0 - index * 5.0, -0.1, front_height - 4.0), cq.Vector(0.0, 1.0, 0.0),
        ))
    shape = shape.cut(cq.Compound.makeCompound(marker_cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"{preset['id']} is not one valid solid")

    allowances = [clear - case for clear, case in zip(preset["lane_clear_widths_mm"], preset["intended_case_thickness_max_mm"])]
    return shape, {
        "preset_id": preset["id"], "lane_count": len(preset["lane_clear_widths_mm"]),
        "clear_lane_widths_mm": preset["lane_clear_widths_mm"], "case_thickness_allowances_mm": allowances,
        "outer_dimensions_mm": [width, corral["base_depth_mm"], corral["divider_height_mm"]],
        "floor_back_lean_deg": corral["floor_back_lean_deg"], "floor_rise_mm": rise,
        "front_stop_height_above_floor_mm": corral["front_stop_height_above_floor_mm"],
        "rear_wall_height_mm": corral["rear_wall_height_mm"],
        "divider_leading_radius_mm": corral["divider_leading_radius_mm"], "divider_top_radius_mm": corral["divider_top_radius_mm"],
        "label_fields": len(preset["lane_clear_widths_mm"]), "identity_holes": preset["identity_holes"], "external_assets": [],
    }


def gauge_width(parameters: dict) -> float:
    gauge = parameters["gauge"]
    return sum(gauge["notch_widths_mm"]) + (len(gauge["notch_widths_mm"]) + 1) * gauge["web_width_mm"]


def make_width_gauge(parameters: dict) -> tuple[cq.Shape, dict]:
    gauge = parameters["gauge"]
    width = gauge_width(parameters)
    shape = cq.Solid.makeBox(width, gauge["depth_mm"], gauge["thickness_mm"])
    cutters: list[cq.Shape] = []
    centers: list[float] = []
    cursor = gauge["web_width_mm"]
    for notch_width in gauge["notch_widths_mm"]:
        cutters.append(cq.Solid.makeBox(
            notch_width, gauge["depth_mm"] - gauge["spine_depth_mm"] + 0.1, gauge["thickness_mm"] + 0.2,
            cq.Vector(cursor, gauge["spine_depth_mm"], -0.1),
        ))
        centers.append(cursor + notch_width / 2.0)
        cursor += notch_width + gauge["web_width_mm"]
    shape = shape.cut(cq.Compound.makeCompound(cutters))
    holes: list[cq.Shape] = []
    for group_index, center_x in enumerate(centers, 1):
        for hole_index in range(group_index):
            holes.append(cq.Solid.makeCylinder(
                gauge["identity_hole_diameter_mm"] / 2.0, gauge["thickness_mm"] + 0.2,
                cq.Vector(center_x + (hole_index - (group_index - 1) / 2.0) * 3.0, gauge["spine_depth_mm"] / 2.0, -0.1),
            ))
    shape = shape.cut(cq.Compound.makeCompound(holes)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("width gauge is not one valid solid")
    return shape, {
        "notch_widths_mm": gauge["notch_widths_mm"], "identity_holes": [1, 2, 3, 4],
        "outer_dimensions_mm": [width, gauge["depth_mm"], gauge["thickness_mm"]], "external_assets": [],
    }


def validate_parameters(parameters: dict) -> None:
    corral = parameters["corral"]
    gauge = parameters["gauge"]
    assert parameters["project"]["id"] == PROJECT_ID
    assert 2.0 <= corral["floor_back_lean_deg"] <= 5.0
    assert floor_rise(parameters) < 8.0
    assert corral["divider_thickness_mm"] / parameters["printer"]["line_width_mm"] >= 6.0
    assert 2.0 * corral["divider_leading_radius_mm"] < corral["divider_thickness_mm"]
    assert 2.0 * corral["divider_top_radius_mm"] < corral["divider_thickness_mm"]
    assert corral["base_rear_thickness_mm"] / parameters["printer"]["layer_height_mm"] == 15
    assert gauge["notch_widths_mm"] == [36.0, 42.0, 50.0, 58.0]
    assert gauge_width(parameters) <= 220.0
    assert parameters["workflow_contract"]["optical_protection_claim"] == "none_storage_corral_only"
    for preset in parameters["presets"]:
        assert len(preset["lane_clear_widths_mm"]) == len(preset["intended_case_thickness_max_mm"])
        assert all(clear - case >= 2.0 for clear, case in zip(preset["lane_clear_widths_mm"], preset["intended_case_thickness_max_mm"]))
        dims = corral_dimensions(parameters, preset)
        assert dims["width_mm"] <= 220.0 and dims["depth_mm"] <= 160.0 and dims["height_mm"] <= 140.0


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
    return {
        "path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "triangles": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)),
        "file_bytes": path.stat().st_size, "file_mib": path.stat().st_size / (1024 * 1024), "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent), "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
        "components": int(len(mesh.split(only_watertight=False))), "volume_mm3": float(mesh.volume), "surface_area_mm2": float(mesh.area),
        "extents_mm": np.round(mesh.extents, 4).tolist(), "bounds_mm": np.round(mesh.bounds, 4).tolist(),
    }


def _zip_member(name: str, data: bytes, archive: zipfile.ZipFile) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; archive.writestr(info, data)


def write_3mf(path: Path, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"; ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"}); resources = ET.SubElement(model, f"{{{ns}}}resources"); build = ET.SubElement(model, f"{{{ns}}}build")
    for object_id, ((name, mesh_path), (move_x, move_y)) in enumerate(zip(parts, placements), 1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True); obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name}); mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh"); verts = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices: ET.SubElement(verts, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        tris = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces: ET.SubElement(tris, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {move_x:.3f} {move_y:.3f} 0"})
    types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        _zip_member("[Content_Types].xml", types, archive); _zip_member("_rels/.rels", rels, archive); _zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive); _zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)


def main() -> None:
    parameters = load_parameters(); validate_parameters(parameters); mesh_p = parameters["mesh"]
    shapes: dict[str, cq.Shape] = {}; interfaces: dict[str, dict] = {}
    for preset in parameters["presets"]: shapes[preset["id"]], interfaces[preset["id"]] = make_corral(parameters, preset)
    shapes["width-gauge"], interfaces["width-gauge"] = make_width_gauge(parameters)

    step_paths: list[Path] = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"; export_step(shape, path); step_paths.append(path)
    first_width = corral_dimensions(parameters, parameters["presets"][0])["width_mm"]
    assembly = cq.Compound.makeCompound([shapes["slim-five"], shapes["mixed-four"].translate((first_width + 15.0, 0.0, 0.0)), shapes["width-gauge"].translate((0.0, 115.0, 0.0))])
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"; export_step(assembly, assembly_path); step_paths.append(assembly_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("slim-five", "mixed-four"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-corral-{REVISION}.stl"; export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"]); mesh_paths[name] = path
    gauge_path = COUPONS / f"DRAFT-{PROJECT_ID}-width-gauge-{REVISION}.stl"; export_stl(shapes["width-gauge"], gauge_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"]); mesh_paths["width-gauge"] = gauge_path
    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-eyeglass-case-shelf-corral-{REVISION}.3mf"
    write_3mf(package_path, [(name, mesh_paths[name]) for name in ("slim-five", "mixed-four", "width-gauge")], [(10.0, 10.0), (10.0, 120.0), (10.0, 230.0)])

    metrics = {name: mesh_metrics(path) for name, path in mesh_paths.items()}; mesh_checks: list[dict] = []
    for name, item in metrics.items():
        mesh_checks.extend([check(f"{name}:watertight", item["watertight"], f"{name} is watertight"), check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"), check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"), check(f"{name}:component", item["components"] == 1, f"{name} is one component"), check(f"{name}:triangles", item["triangles"] <= mesh_p["triangle_stop"], "Triangle budget", {"actual": item["triangles"], "limit": mesh_p["triangle_stop"]}), check(f"{name}:file", item["file_mib"] <= mesh_p["max_mesh_mib"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": mesh_p["max_mesh_mib"]})])
    parametric_checks = [check("parameter-validation", True, "Fail-closed parameter relations pass"), check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All three B-Reps are valid"), check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every deliverable is one B-Rep solid"), check("two-lane-presets", [interfaces[name]["lane_count"] for name in ("slim-five", "mixed-four")] == [5, 4], "Five-lane and four-lane presets are generated"), check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "No external font, vector or mesh asset is used")]
    write_json(VALIDATION / "parametric-source-report.json", report(f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)], parametric_checks, {"python": platform.python_version(), "cadquery": cq.__version__, "unique_parts": list(shapes), "print_objects": list(mesh_paths)}, ["Any parameter change requires regeneration of downstream evidence."]))
    write_json(VALIDATION / "mesh-generation-report.json", report(f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks, {"meshes": metrics}, ["Topology does not prove case fit, tip resistance, retrieval behavior or shelf friction."]))
    corral_interfaces = [interfaces[name] for name in ("slim-five", "mixed-four")]
    interface_checks = [check("lane-widths", [item["clear_lane_widths_mm"] for item in corral_interfaces] == [[36.0] * 5, [36.0, 42.0, 50.0, 58.0]], "Both clear-width lists are exact"), check("case-allowance", all(all(value >= 2.0 for value in item["case_thickness_allowances_mm"]) for item in corral_interfaces), "Each example case thickness has at least 2 mm allowance"), check("floor-angle", all(item["floor_back_lean_deg"] == 3.0 for item in corral_interfaces), "Both floors fall 3 degrees toward the rear"), check("retention", all(item["front_stop_height_above_floor_mm"] == 14.0 and item["rear_wall_height_mm"] == 54.0 for item in corral_interfaces), "Front and rear restraints are exact"), check("rounded-dividers", all(item["divider_leading_radius_mm"] == 1.4 and item["divider_top_radius_mm"] == 1.2 for item in corral_interfaces), "All divider contact edges retain protected radii"), check("gauge-series", interfaces["width-gauge"]["notch_widths_mm"] == [36.0, 42.0, 50.0, 58.0], "Gauge reproduces the mixed lane series"), check("label-fields", all(item["label_fields"] == item["lane_count"] for item in corral_interfaces), "Every lane has one label field"), check("portfolio-envelope", all(item["outer_dimensions_mm"][0] <= 220.0 and item["outer_dimensions_mm"][1] <= 160.0 and item["outer_dimensions_mm"][2] <= 140.0 for item in corral_interfaces), "Both corrals fit the portfolio envelope"), check("claim-boundary", parameters["workflow_contract"]["optical_protection_claim"] == "none_storage_corral_only", "No optical protection claim is present")]
    write_json(VALIDATION / "interface-report.json", report(f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"], interface_checks, {"interfaces": interfaces, "workflow_contract": parameters["workflow_contract"]}, ["Analytic stability features do not establish physical tip resistance for any case class."]))

    baseline_volume = sum(corral_dimensions(parameters, preset)["width_mm"] * parameters["corral"]["base_depth_mm"] * parameters["corral"]["divider_height_mm"] for preset in parameters["presets"])
    candidate_volume = sum(float(shapes[name].Volume()) for name in ("slim-five", "mixed-four")); reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "baseline": {"description": "two solid corral envelope blocks", "volume_mm3": baseline_volume}, "candidate": {"description": "sloped floors, full rounded dividers and partial retention walls", "volume_mm3": candidate_volume}, "volume_reduction_percent": reduction, "selection_threshold_percent": 75.0, "status": "PASS" if reduction >= 75.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE"}
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL", "meshes": metrics, "simplification": "NOT_BENEFICIAL", "reason": "Analytic fillets are under budget; decimation could flatten protected case-contact edges."})
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))], "outputs": [input_record(path) for path in outputs], "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]]})
    gate_reports = [json.loads((VALIDATION / name).read_text()) for name in ("parametric-source-report.json", "mesh-generation-report.json", "interface-report.json")]
    if any(value["status"] != "PASS" for value in [*gate_reports, optimization]): raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "unique_meshes": len(mesh_paths), "3mf": str(package_path.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
