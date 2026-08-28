#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-023 S/M/L thumb page-holder family."""
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
PROJECT_ID = "MM-ORG-023"
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


def slot_prism(length: float, width: float, height: float) -> cq.Shape:
    return cq.Workplane("XY").slot2D(length, width).extrude(height).val()


def holder_dimensions(parameters: dict, preset: dict) -> list[float]:
    holder = parameters["holder"]
    center_depth = preset["opening_minor_mm"] + holder["opening_wall_allowance_mm"]
    return [preset["span_mm"], max(center_depth, holder["wing_depth_mm"]), holder["body_thickness_mm"] + holder["page_pad_height_mm"]]


def make_holder(parameters: dict, preset: dict) -> tuple[cq.Shape, dict]:
    holder = parameters["holder"]
    span = preset["span_mm"]
    thickness = holder["body_thickness_mm"]
    center_width = preset["opening_major_mm"] + holder["opening_wall_allowance_mm"]
    center_depth = preset["opening_minor_mm"] + holder["opening_wall_allowance_mm"]

    center = cq.Workplane("XY").ellipse(center_width / 2.0, center_depth / 2.0).extrude(thickness).val()
    half_wing = slot_prism(span / 2.0, holder["wing_depth_mm"], thickness)
    body = center.fuse(half_wing.translate((span / 4.0, 0.0, 0.0))).fuse(half_wing.translate((-span / 4.0, 0.0, 0.0))).clean()
    opening = slot_prism(preset["opening_major_mm"], preset["opening_minor_mm"], thickness + 2.0).translate((0.0, 0.0, -1.0))
    body = body.cut(opening).clean()
    body = cq.Workplane(obj=body).edges().fillet(holder["body_edge_radius_mm"]).val()

    pad = slot_prism(holder["page_pad_length_mm"], holder["page_pad_width_mm"], holder["page_pad_height_mm"] + holder["page_pad_overlap_mm"])
    pad = cq.Workplane(obj=pad).edges().fillet(holder["page_pad_edge_radius_mm"]).val()
    pad_x = span / 2.0 - holder["page_pad_length_mm"] / 2.0
    pad_z = thickness - holder["page_pad_overlap_mm"]
    shape = body.fuse(pad.translate((pad_x, 0.0, pad_z))).fuse(pad.translate((-pad_x, 0.0, pad_z)))

    recesses = []
    for index in range(preset["identity_holes"]):
        recesses.append(cq.Solid.makeCylinder(
            1.2, 0.65,
            cq.Vector(-span / 2.0 + 11.0 + index * 5.0, 0.0, -0.1), cq.Vector(0.0, 0.0, 1.0),
        ))
    shape = shape.cut(cq.Compound.makeCompound(recesses)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"{preset['id']} holder is not one valid solid")
    minimum_ring_wall = min((center_width - preset["opening_major_mm"]) / 2.0, (center_depth - preset["opening_minor_mm"]) / 2.0)
    return shape, {
        "part_id": preset["id"], "opening_obround_mm": [preset["opening_major_mm"], preset["opening_minor_mm"]],
        "span_mm": span, "outer_dimensions_mm": holder_dimensions(parameters, preset),
        "minimum_ring_wall_mm": minimum_ring_wall, "body_edge_radius_mm": holder["body_edge_radius_mm"],
        "page_pads": 2, "page_pad_mm": [holder["page_pad_length_mm"], holder["page_pad_width_mm"], holder["page_pad_height_mm"]],
        "identity_holes": preset["identity_holes"], "print_orientation": "broad_face_down_pads_up", "external_assets": [],
    }


def make_sizing_guide(parameters: dict) -> tuple[cq.Shape, dict]:
    gauge = parameters["gauge"]
    base = (
        cq.Workplane("XY")
        .box(gauge["outer_width_mm"], gauge["outer_depth_mm"], gauge["thickness_mm"], centered=(True, True, False))
        .edges("|Z").fillet(gauge["corner_radius_mm"])
        .val()
    )
    shape = base
    openings = []
    for x, preset in zip(gauge["station_centers_x_mm"], parameters["presets"]):
        openings.append([preset["opening_major_mm"], preset["opening_minor_mm"]])
        cutter = slot_prism(preset["opening_major_mm"], preset["opening_minor_mm"], gauge["thickness_mm"] + 2.0).translate((x, 0.0, -1.0))
        shape = shape.cut(cutter)
    shape = cq.Workplane(obj=shape.clean()).edges().fillet(gauge["comfort_edge_radius_mm"]).val()

    recesses = []
    for station, x in enumerate(gauge["station_centers_x_mm"], 1):
        for index in range(station):
            recesses.append(cq.Solid.makeCylinder(
                gauge["identity_hole_diameter_mm"] / 2.0, 0.65,
                cq.Vector(x + (index - (station - 1) / 2.0) * 3.0, gauge["identity_row_y_mm"], -0.1), cq.Vector(0.0, 0.0, 1.0),
            ))
    shape = shape.cut(cq.Compound.makeCompound(recesses)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("sizing guide is not one valid solid")
    return shape, {
        "part_id": "sizing-guide", "openings_obround_mm": openings,
        "station_centers_x_mm": gauge["station_centers_x_mm"], "identity_holes": [1, 2, 3],
        "comfort_edge_radius_mm": gauge["comfort_edge_radius_mm"],
        "outer_dimensions_mm": [gauge["outer_width_mm"], gauge["outer_depth_mm"], gauge["thickness_mm"]],
        "print_orientation": "broad_face_down", "external_assets": [],
    }


def validate_parameters(parameters: dict) -> None:
    holder = parameters["holder"]
    gauge = parameters["gauge"]
    assert parameters["project"]["id"] == PROJECT_ID
    assert [item["opening_major_mm"] for item in parameters["presets"]] == [20.0, 23.0, 26.0]
    assert [item["opening_minor_mm"] for item in parameters["presets"]] == [16.5, 19.0, 21.5]
    assert [item["span_mm"] for item in parameters["presets"]] == [82.0, 92.0, 102.0]
    assert holder["opening_wall_allowance_mm"] / 2.0 == holder["minimum_ring_wall_mm"]
    assert holder["body_thickness_mm"] / parameters["printer"]["layer_height_mm"] == 25.0
    assert holder["wing_depth_mm"] / parameters["printer"]["line_width_mm"] == 40.0
    assert holder["body_edge_radius_mm"] < holder["body_thickness_mm"] / 2.0
    assert holder["page_pad_height_mm"] / parameters["printer"]["layer_height_mm"] == 4.0
    assert len(gauge["station_centers_x_mm"]) == len(parameters["presets"])
    for preset in parameters["presets"]:
        dims = holder_dimensions(parameters, preset)
        assert dims[0] <= 120.0 and dims[1] <= 60.0 and dims[2] <= 20.0
        assert preset["opening_major_mm"] > preset["opening_minor_mm"]
    assert parameters["workflow_contract"]["ergonomic_claim"] == "sizing_aid_only_no_medical_or_universal_fit_claim"


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


def main() -> None:
    parameters = load_parameters()
    validate_parameters(parameters)
    mesh_p = parameters["mesh"]
    shapes: dict[str, cq.Shape] = {}
    interfaces: dict[str, dict] = {}
    for preset in parameters["presets"]:
        shapes[preset["id"]], interfaces[preset["id"]] = make_holder(parameters, preset)
    shapes["sizing-guide"], interfaces["sizing-guide"] = make_sizing_guide(parameters)

    step_paths = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    assembly = cq.Compound.makeCompound([
        shapes["small"], shapes["medium"].translate((105.0, 0.0, 0.0)),
        shapes["large"].translate((220.0, 0.0, 0.0)), shapes["sizing-guide"].translate((65.0, 65.0, 0.0)),
    ])
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"
    export_step(assembly, assembly_path)
    step_paths.append(assembly_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("small", "medium", "large"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-holder-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    gauge_path = COUPONS / f"DRAFT-{PROJECT_ID}-sizing-guide-{REVISION}.stl"
    export_stl(shapes["sizing-guide"], gauge_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    mesh_paths["sizing-guide"] = gauge_path

    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-page-holder-thumb-tool-{REVISION}.3mf"
    order = ["small", "medium", "large", "sizing-guide"]
    write_3mf(package_path, [(name, mesh_paths[name]) for name in order], [(10.0, 10.0), (110.0, 10.0), (225.0, 10.0), (10.0, 75.0)])

    metrics = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
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
    parametric_checks = [
        check("parameter-validation", True, "Fail-closed parameter relations pass"),
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All four B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every deliverable is one B-Rep solid"),
        check("three-comfort-samples", [interfaces[name]["opening_obround_mm"] for name in ("small", "medium", "large")] == [[20.0, 16.5], [23.0, 19.0], [26.0, 21.5]], "All three protected openings are generated"),
        check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "No external font, vector or mesh asset is used"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", report(
        f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)], parametric_checks,
        {"python": platform.python_version(), "cadquery": cq.__version__, "unique_parts": list(shapes), "print_objects": list(mesh_paths)},
        ["Any parameter change requires regeneration of downstream evidence."],
    ))
    write_json(VALIDATION / "mesh-generation-report.json", report(
        f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks, {"meshes": metrics},
        ["Topology does not prove comfort, retention, page turning or paper safety."],
    ))

    holders = [interfaces[name] for name in ("small", "medium", "large")]
    guide = interfaces["sizing-guide"]
    interface_checks = [
        check("opening-series", [item["opening_obround_mm"] for item in holders] == [[20.0, 16.5], [23.0, 19.0], [26.0, 21.5]], "S/M/L openings are exact"),
        check("guide-matches", guide["openings_obround_mm"] == [item["opening_obround_mm"] for item in holders], "Sizing guide reproduces every holder opening"),
        check("span-series", [item["span_mm"] for item in holders] == [82.0, 92.0, 102.0], "S/M/L spans are exact"),
        check("ring-wall", all(item["minimum_ring_wall_mm"] >= 10.0 for item in holders), "Every center ring retains at least 10 mm wall"),
        check("comfort-radius", all(item["body_edge_radius_mm"] == 1.0 for item in holders) and guide["comfort_edge_radius_mm"] == 0.8, "Holder and guide comfort radii are exact"),
        check("page-pads", all(item["page_pads"] == 2 and item["page_pad_mm"] == [24.0, 12.0, 0.8] for item in holders), "Two local page pads are protected on every holder"),
        check("orientation", all(item["print_orientation"] == "broad_face_down_pads_up" for item in holders), "All holders use the support-free orientation"),
        check("portfolio-envelope", all(item["outer_dimensions_mm"][0] <= 120.0 and item["outer_dimensions_mm"][1] <= 60.0 and item["outer_dimensions_mm"][2] <= 20.0 for item in holders), "All holders fit the product envelope"),
        check("claim-boundary", parameters["workflow_contract"]["ergonomic_claim"] == "sizing_aid_only_no_medical_or_universal_fit_claim", "No medical or universal-fit claim is present"),
    ]
    write_json(VALIDATION / "interface-report.json", report(
        f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"], interface_checks,
        {"interfaces": interfaces, "workflow_contract": parameters["workflow_contract"]},
        ["Analytic opening dimensions and radii cannot establish physical comfort or book behavior."],
    ))

    baseline_volume = sum(np.prod(interfaces[name]["outer_dimensions_mm"]) for name in shapes)
    candidate_volume = sum(float(shapes[name].Volume()) for name in shapes)
    reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "baseline": {"description": "four solid rectangular envelope blocks", "volume_mm3": float(baseline_volume)},
        "candidate": {"description": "rounded capsule wings, obround openings and local contact pads", "volume_mm3": candidate_volume},
        "volume_reduction_percent": reduction, "selection_threshold_percent": 35.0,
        "status": "PASS" if reduction >= 35.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE",
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL",
        "meshes": metrics, "simplification": "NOT_BENEFICIAL",
        "reason": "Comfort fillets and obround openings are under budget; decimation risks altering hand and paper contact surfaces.",
    })
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS",
        "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))],
        "outputs": [input_record(path) for path in outputs],
        "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]],
    })
    gate_reports = [json.loads((VALIDATION / name).read_text()) for name in ("parametric-source-report.json", "mesh-generation-report.json", "interface-report.json")]
    if any(value["status"] != "PASS" for value in [*gate_reports, optimization]):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "unique_meshes": len(mesh_paths), "3mf": str(package_path.relative_to(ROOT)), "volume_reduction_percent": reduction}, indent=2))


if __name__ == "__main__":
    main()
