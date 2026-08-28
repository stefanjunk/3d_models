#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-020 belt/scarf shelf-comb family."""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
PROJECT_ID = "MM-ORG-020"
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


def comb_dimensions(parameters: dict, preset: dict) -> dict:
    comb = parameters["comb"]
    width = (preset["slot_count"] + 1) * comb["divider_thickness_mm"] + preset["slot_count"] * preset["clear_slot_width_mm"]
    return {"width_mm": width, "depth_mm": comb["depth_mm"], "pitch_mm": preset["clear_slot_width_mm"] + comb["divider_thickness_mm"]}


def soft_fin(thickness: float, depth: float, height: float, leading_radius: float, top_radius: float, x: float = 0.0, y: float = 0.0) -> cq.Shape:
    shape = (
        cq.Workplane("XY")
        .box(thickness, depth, height, centered=(False, False, False))
        .edges("|Z").fillet(leading_radius)
        .faces(">Z").edges().fillet(top_radius)
        .val()
    )
    return shape.translate((x, y, 0.0))


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


def make_comb(parameters: dict, preset: dict) -> tuple[cq.Shape, dict]:
    comb = parameters["comb"]
    connector = parameters["connector"]
    dims = comb_dimensions(parameters, preset)
    width = dims["width_mm"]
    front = cq.Solid.makeBox(width, comb["front_rail_depth_mm"], comb["front_rail_height_mm"])
    rear = cq.Solid.makeBox(width, comb["rear_rail_depth_mm"], comb["rear_rail_height_mm"], cq.Vector(0.0, comb["depth_mm"] - comb["rear_rail_depth_mm"], 0.0))
    shape = front.fuse(rear)
    for index in range(preset["slot_count"] + 1):
        x = index * dims["pitch_mm"]
        shape = shape.fuse(soft_fin(
            comb["divider_thickness_mm"], comb["depth_mm"], comb["divider_height_mm"],
            comb["leading_edge_radius_mm"], comb["top_edge_radius_mm"], x,
        ))
    for center_y in connector["centers_y_mm"]:
        shape = shape.fuse(male_tab(parameters, width, center_y)).cut(female_socket(parameters, center_y))

    label_cutters: list[cq.Shape] = []
    for slot_index in range(preset["slot_count"]):
        slot_start = comb["divider_thickness_mm"] + slot_index * dims["pitch_mm"]
        label_width = preset["clear_slot_width_mm"] - 2.0 * comb["label_side_margin_mm"]
        label_cutters.append(cq.Solid.makeBox(
            label_width, comb["label_recess_depth_mm"] + 0.1, comb["label_recess_height_mm"],
            cq.Vector(slot_start + comb["label_side_margin_mm"], -0.1, comb["label_recess_bottom_z_mm"]),
        ))
    shape = shape.cut(cq.Compound.makeCompound(label_cutters))

    marker_cutters: list[cq.Shape] = []
    for index in range(preset["identity_holes"]):
        marker_cutters.append(cq.Solid.makeCylinder(
            1.2, 0.7, cq.Vector(width - 9.0 - index * 5.0, comb["depth_mm"] - 5.0, comb["rear_rail_height_mm"] - 0.6)
        ))
    shape = shape.cut(cq.Compound.makeCompound(marker_cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"{preset['id']} is not one valid solid")
    return shape, {
        "preset_id": preset["id"], "slot_count": preset["slot_count"], "clear_slot_width_mm": preset["clear_slot_width_mm"],
        "roll_diameter_allowance_mm": preset["clear_slot_width_mm"] - preset["intended_roll_diameter_max_mm"],
        "outer_dimensions_mm": [width + connector["tab_depth_mm"], comb["depth_mm"], comb["divider_height_mm"]],
        "divider_leading_radius_mm": comb["leading_edge_radius_mm"], "divider_top_radius_mm": comb["top_edge_radius_mm"],
        "front_retention_height_mm": comb["front_rail_height_mm"], "label_fields": preset["slot_count"],
        "joint_centers_y_mm": connector["centers_y_mm"], "identity_holes": preset["identity_holes"], "external_assets": [],
    }


def make_edge_coupon(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    # Keep the coupon base prismatic.  The textile-facing radii belong to the
    # test ribs; filleting the thin base before the rib fusions can leave
    # coincident tessellation seams even when the final B-Rep is one solid.
    base = cq.Solid.makeBox(coupon["base_width_mm"], coupon["base_depth_mm"], coupon["base_thickness_mm"])
    shape = base
    for center_x, radius in zip(coupon["rib_centers_x_mm"], coupon["leading_radii_mm"]):
        rib = soft_fin(coupon["rib_thickness_mm"], coupon["rib_depth_mm"], coupon["rib_height_mm"], radius, min(radius, 1.2), center_x - coupon["rib_thickness_mm"] / 2.0, 6.0)
        shape = shape.fuse(rib)
    cutters: list[cq.Shape] = []
    for group_index, center_x in enumerate(coupon["rib_centers_x_mm"], 1):
        for hole_index in range(group_index):
            cutters.append(cq.Solid.makeCylinder(
                coupon["identity_hole_diameter_mm"] / 2.0, coupon["base_thickness_mm"] + 0.2,
                cq.Vector(center_x + (hole_index - (group_index - 1) / 2.0) * 3.0, 3.0, -0.1),
            ))
    shape = shape.cut(cq.Compound.makeCompound(cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("edge coupon is not one valid solid")
    return shape, {
        "leading_radii_mm": coupon["leading_radii_mm"], "identity_holes": [1, 2, 3],
        "outer_dimensions_mm": [coupon["base_width_mm"], coupon["base_depth_mm"], coupon["rib_height_mm"]], "external_assets": [],
    }


def make_connector_key(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    connector = parameters["connector"]
    handle = cq.Workplane("XY").box(coupon["key_handle_length_mm"], coupon["key_handle_width_mm"], connector["height_mm"], centered=(False, False, False)).edges("|Z").fillet(2.0).val()
    shape = handle.fuse(male_tab(parameters, coupon["key_handle_length_mm"], coupon["key_handle_width_mm"] / 2.0)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("connector key is not one valid solid")
    return shape, {
        "tab_depth_mm": connector["tab_depth_mm"], "neck_width_mm": connector["neck_width_mm"],
        "head_width_mm": connector["head_width_mm"], "height_mm": connector["height_mm"], "external_assets": [],
    }


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    comb = parameters["comb"]
    connector = parameters["connector"]
    coupon = parameters["coupon"]
    printer = parameters["printer"]
    assert project["id"] == PROJECT_ID and project["revision"] == REVISION and project["units"] == "mm"
    assert [item["id"] for item in parameters["presets"]] == ["belt-four", "scarf-three"]
    assert comb["divider_thickness_mm"] / printer["line_width_mm"] >= 6.0
    assert comb["leading_edge_radius_mm"] < comb["divider_thickness_mm"] / 2.0
    assert comb["top_edge_radius_mm"] < comb["divider_thickness_mm"] / 2.0
    assert comb["front_rail_height_mm"] >= 0.14 * max(item["intended_roll_diameter_max_mm"] for item in parameters["presets"])
    assert comb["front_rail_depth_mm"] - comb["label_recess_depth_mm"] >= 10.0
    assert connector["height_mm"] == comb["base_thickness_mm"] == coupon["base_thickness_mm"]
    assert connector["centers_y_mm"] == [28.0, 77.0]
    assert coupon["leading_radii_mm"] == [0.6, 1.0, 1.4]
    assert coupon["leading_radii_mm"][-1] == comb["leading_edge_radius_mm"]
    assert parameters["workflow_contract"]["load_claim"] == "none_dry_soft_goods_only"
    for preset in parameters["presets"]:
        dims = comb_dimensions(parameters, preset)
        assert dims["width_mm"] + connector["tab_depth_mm"] <= 220.0
        assert dims["depth_mm"] <= 120.0 and comb["divider_height_mm"] <= 100.0
        assert preset["clear_slot_width_mm"] - preset["intended_roll_diameter_max_mm"] >= 2.0


def move_to_origin(shape: cq.Shape) -> cq.Shape:
    bounds = shape.BoundingBox()
    return shape.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def export_step(shape: cq.Shape, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path), exportType="STEP")


def export_stl(shape: cq.Shape, path: Path, linear: float, angular: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(move_to_origin(shape), str(path), tolerance=linear, angularTolerance=angular)
    # OCC can emit isolated zero-area facets where two small fillets meet.
    # They are not part of the B-Rep, so remove them deterministically before
    # the manufacturing mesh and 3MF consume the STL.
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
    for preset in parameters["presets"]: shapes[preset["id"]], interfaces[preset["id"]] = make_comb(parameters, preset)
    shapes["edge-radius-coupon"], interfaces["edge-radius-coupon"] = make_edge_coupon(parameters)
    shapes["connector-key"], interfaces["connector-key"] = make_connector_key(parameters)

    step_paths: list[Path] = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"; export_step(shape, path); step_paths.append(path)
    belt_width = comb_dimensions(parameters, parameters["presets"][0])["width_mm"] + parameters["connector"]["tab_depth_mm"]
    assembly = cq.Compound.makeCompound([shapes["belt-four"], shapes["scarf-three"].translate((belt_width + 15.0, 0.0, 0.0)), shapes["edge-radius-coupon"].translate((0.0, 130.0, 0.0)), shapes["connector-key"].translate((100.0, 130.0, 0.0))])
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"; export_step(assembly, assembly_path); step_paths.append(assembly_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("belt-four", "scarf-three"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-comb-{REVISION}.stl"; export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"]); mesh_paths[name] = path
    for name in ("edge-radius-coupon", "connector-key"):
        path = COUPONS / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"; export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"]); mesh_paths[name] = path
    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-belt-scarf-shelf-comb-{REVISION}.3mf"
    write_3mf(package_path, [(name, mesh_paths[name]) for name in ("belt-four", "scarf-three", "edge-radius-coupon", "connector-key")], [(10.0, 10.0), (10.0, 130.0), (240.0, 10.0), (340.0, 10.0)])

    metrics = {name: mesh_metrics(path) for name, path in mesh_paths.items()}; mesh_checks: list[dict] = []
    for name, item in metrics.items():
        mesh_checks.extend([check(f"{name}:watertight", item["watertight"], f"{name} is watertight"), check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"), check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"), check(f"{name}:component", item["components"] == 1, f"{name} is one component"), check(f"{name}:triangles", item["triangles"] <= mesh_p["triangle_stop"], "Triangle budget", {"actual": item["triangles"], "limit": mesh_p["triangle_stop"]}), check(f"{name}:file", item["file_mib"] <= mesh_p["max_mesh_mib"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": mesh_p["max_mesh_mib"]})])
    parametric_checks = [check("parameter-validation", True, "Fail-closed parameter relations pass"), check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All four B-Reps are valid"), check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every deliverable is one B-Rep solid"), check("two-width-presets", [interfaces[name]["clear_slot_width_mm"] for name in ("belt-four", "scarf-three")] == [46.0, 64.0], "Two measured width presets are generated"), check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "No external font, vector or mesh asset is used")]
    write_json(VALIDATION / "parametric-source-report.json", report(f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)], parametric_checks, {"python": platform.python_version(), "cadquery": cq.__version__, "unique_parts": list(shapes), "print_objects": list(mesh_paths)}, ["Any parameter change requires regeneration of downstream evidence."]))
    write_json(VALIDATION / "mesh-generation-report.json", report(f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks, {"meshes": metrics}, ["Topology does not prove fabric safety, roll retention, connector fit or shelf stability."]))
    comb_interfaces = [interfaces[name] for name in ("belt-four", "scarf-three")]
    interface_checks = [check("slot-widths", [item["clear_slot_width_mm"] for item in comb_interfaces] == [46.0, 64.0], "Belt and scarf clear widths are exact"), check("diameter-allowance", all(item["roll_diameter_allowance_mm"] >= 2.0 for item in comb_interfaces), "Each example has at least 2 mm diametral allowance"), check("production-leading-radius", all(item["divider_leading_radius_mm"] == 1.4 for item in comb_interfaces), "All production fin noses use R1.4"), check("production-top-radius", all(item["divider_top_radius_mm"] == 1.2 for item in comb_interfaces), "All production fin tops use R1.2"), check("coupon-series", interfaces["edge-radius-coupon"]["leading_radii_mm"] == [0.6, 1.0, 1.4], "Fabric coupon brackets the production nose radius"), check("connector-datums", all(item["joint_centers_y_mm"] == [28.0, 77.0] for item in comb_interfaces), "Both modules share connector datums"), check("label-fields", all(item["label_fields"] == item["slot_count"] for item in comb_interfaces), "Every compartment has a label field"), check("portfolio-envelope", all(item["outer_dimensions_mm"][0] <= 220.0 and item["outer_dimensions_mm"][1] <= 120.0 and item["outer_dimensions_mm"][2] <= 100.0 for item in comb_interfaces), "Both combs fit the portfolio envelope"), check("no-load-claim", parameters["workflow_contract"]["load_claim"] == "none_dry_soft_goods_only", "No load-bearing claim is present")]
    write_json(VALIDATION / "interface-report.json", report(f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"], interface_checks, {"interfaces": interfaces, "workflow_contract": parameters["workflow_contract"]}, ["Analytic radii reduce sharpness but do not establish snag-free behavior for any fabric."]))

    baseline_volume = sum(comb_dimensions(parameters, preset)["width_mm"] * parameters["comb"]["depth_mm"] * parameters["comb"]["divider_height_mm"] for preset in parameters["presets"])
    candidate_volume = sum(float(shapes[name].Volume()) for name in ("belt-four", "scarf-three")); reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "baseline": {"description": "two solid comb envelope blocks", "volume_mm3": baseline_volume}, "candidate": {"description": "open-floor rails, rounded fins and planar joints", "volume_mm3": candidate_volume}, "volume_reduction_percent": reduction, "selection_threshold_percent": 80.0, "status": "PASS" if reduction >= 80.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE"}
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL", "meshes": metrics, "simplification": "NOT_BENEFICIAL", "reason": "Analytic fillets are under budget; decimation could flatten protected textile-contact radii."})
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))], "outputs": [input_record(path) for path in outputs], "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]]})
    gate_reports = [json.loads((VALIDATION / name).read_text()) for name in ("parametric-source-report.json", "mesh-generation-report.json", "interface-report.json")]
    if any(value["status"] != "PASS" for value in [*gate_reports, optimization]): raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "unique_meshes": len(mesh_paths), "3mf": str(package_path.relative_to(ROOT))}, indent=2))


if __name__ == "__main__": main()
