#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-022 labelable small-parts bin family."""
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
PROJECT_ID = "MM-ORG-022"
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


def rounded_box(width: float, depth: float, height: float, radius: float) -> cq.Shape:
    return (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(False, False, False))
        .edges("|Z").fillet(radius)
        .val()
    )


def label_projection(parameters: dict) -> float:
    bin_p = parameters["bin"]
    return bin_p["label_slot_gap_mm"] + bin_p["label_lip_depth_mm"]


def bin_outer_dimensions(parameters: dict, preset: dict) -> list[float]:
    bin_p = parameters["bin"]
    return [preset["outer_width_mm"], bin_p["outer_depth_mm"] + label_projection(parameters), bin_p["outer_height_mm"]]


def make_label_rails(parameters: dict, width: float) -> cq.Shape:
    bin_p = parameters["bin"]
    margin = bin_p["label_side_margin_mm"]
    pocket_width = width - 2.0 * margin
    z0 = bin_p["label_bottom_z_mm"]
    height = bin_p["label_pocket_height_mm"]
    side = bin_p["label_side_spacer_width_mm"]
    overlap = bin_p["label_lip_overlap_mm"]
    stop = bin_p["label_bottom_stop_height_mm"]
    gap = bin_p["label_slot_gap_mm"]
    lip_depth = bin_p["label_lip_depth_mm"]
    spacer_depth = gap + 0.10
    lip_y = -(gap + lip_depth)

    pieces = [
        cq.Solid.makeBox(pocket_width, spacer_depth, stop, cq.Vector(margin, -gap, z0)),
        cq.Solid.makeBox(side, spacer_depth, height, cq.Vector(margin, -gap, z0)),
        cq.Solid.makeBox(side, spacer_depth, height, cq.Vector(margin + pocket_width - side, -gap, z0)),
        cq.Solid.makeBox(pocket_width, lip_depth + 0.05, stop + overlap, cq.Vector(margin, lip_y, z0)),
        cq.Solid.makeBox(side + overlap, lip_depth + 0.05, height, cq.Vector(margin, lip_y, z0)),
        cq.Solid.makeBox(side + overlap, lip_depth + 0.05, height, cq.Vector(margin + pocket_width - side - overlap, lip_y, z0)),
    ]
    shape = pieces[0]
    for piece in pieces[1:]:
        shape = shape.fuse(piece)
    return shape.clean()


def make_bin(parameters: dict, preset: dict) -> tuple[cq.Shape, dict]:
    bin_p = parameters["bin"]
    width = preset["outer_width_mm"]
    depth = bin_p["outer_depth_mm"]
    height = bin_p["outer_height_mm"]
    wall = bin_p["wall_mm"]
    floor = bin_p["floor_mm"]
    outer_r = bin_p["outer_corner_radius_mm"]
    inner_r = outer_r - wall

    outer = rounded_box(width, depth, height, outer_r)
    inner = rounded_box(width - 2.0 * wall, depth - 2.0 * wall, height - floor + 0.5, inner_r).translate((wall, wall, floor))
    shape = outer.cut(inner)

    grip = cq.Solid.makeCylinder(
        bin_p["front_grip_radius_mm"], wall + 0.4,
        cq.Vector(width / 2.0, -0.2, height), cq.Vector(0.0, 1.0, 0.0),
    )
    shape = shape.cut(grip)

    ramp = (
        cq.Workplane("YZ")
        .polyline([
            (wall - 0.05, floor - 0.05),
            (wall + bin_p["scoop_depth_mm"], floor - 0.05),
            (wall - 0.05, floor + bin_p["scoop_rise_mm"]),
        ])
        .close()
        .extrude(width - 2.0 * wall + 0.1)
        .val()
        .translate((wall - 0.05, 0.0, 0.0))
    )
    shape = shape.fuse(ramp).fuse(make_label_rails(parameters, width))

    identity_cutters = []
    for index in range(preset["identity_holes"]):
        identity_cutters.append(cq.Solid.makeCylinder(
            1.2, 0.65,
            cq.Vector(width - 7.0 - index * 5.0, depth - 7.0, -0.1), cq.Vector(0.0, 0.0, 1.0),
        ))
    shape = shape.cut(cq.Compound.makeCompound(identity_cutters)).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"{preset['id']} bin is not one valid solid")

    card_width = width - 2.0 * (bin_p["label_side_margin_mm"] + bin_p["label_side_spacer_width_mm"])
    return shape, {
        "part_id": preset["id"], "outer_dimensions_mm": bin_outer_dimensions(parameters, preset),
        "body_width_mm": width, "body_depth_mm": depth, "body_height_mm": height,
        "inner_clear_dimensions_mm": [width - 2.0 * wall, depth - 2.0 * wall, height - floor],
        "wall_mm": wall, "floor_mm": floor, "grip_radius_mm": bin_p["front_grip_radius_mm"],
        "pickup_ramp_mm": [bin_p["scoop_depth_mm"], bin_p["scoop_rise_mm"]],
        "label_slot_gap_mm": bin_p["label_slot_gap_mm"], "label_card_max_mm": [card_width, height - bin_p["label_bottom_z_mm"] - (height - bin_p["label_bottom_z_mm"] - bin_p["label_pocket_height_mm"]), bin_p["paper_card_thickness_max_mm"]],
        "identity_holes": preset["identity_holes"], "external_assets": [],
    }


def carrier_dimensions(parameters: dict) -> dict:
    carrier = parameters["carrier"]
    inner_width = carrier["packing_width_mm"] + 2.0 * carrier["side_clearance_mm"]
    inner_depth = carrier["rows"] * carrier["bin_depth_mm"] + (carrier["rows"] - 1) * carrier["row_clearance_mm"]
    return {
        "inner_width_mm": inner_width, "inner_depth_mm": inner_depth,
        "outer_width_mm": inner_width + 2.0 * carrier["frame_wall_mm"],
        "outer_depth_mm": inner_depth + 2.0 * carrier["frame_wall_mm"],
        "height_mm": carrier["frame_height_mm"],
    }


def make_carrier(parameters: dict) -> tuple[cq.Shape, dict]:
    carrier = parameters["carrier"]
    dims = carrier_dimensions(parameters)
    wall = carrier["frame_wall_mm"]
    height = carrier["frame_height_mm"]
    shape = rounded_box(dims["outer_width_mm"], dims["outer_depth_mm"], height, carrier["outer_corner_radius_mm"])
    for row in range(carrier["rows"]):
        y = wall + row * (carrier["bin_depth_mm"] + carrier["row_clearance_mm"])
        cutter = cq.Solid.makeBox(dims["inner_width_mm"], carrier["bin_depth_mm"], height + 0.2, cq.Vector(wall, y, -0.1))
        shape = shape.cut(cutter)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("matrix frame is not one valid solid")
    return shape, {
        "part_id": "matrix-frame", "outer_dimensions_mm": [dims["outer_width_mm"], dims["outer_depth_mm"], height],
        "packing_width_mm": carrier["packing_width_mm"], "rows": carrier["rows"],
        "side_clearance_mm": carrier["side_clearance_mm"], "row_clearance_mm": carrier["row_clearance_mm"],
        "open_floor": True, "external_assets": [],
    }


def gauge_width(parameters: dict) -> float:
    gauge = parameters["gauge"]
    return 2.0 * gauge["side_margin_mm"] + gauge["station_width_mm"] + (len(gauge["slot_gaps_mm"]) - 1) * gauge["station_pitch_mm"]


def make_label_slot_gauge(parameters: dict) -> tuple[cq.Shape, dict]:
    gauge = parameters["gauge"]
    width = gauge_width(parameters)
    base_t = gauge["base_thickness_mm"]
    shape = cq.Solid.makeBox(width, gauge["base_depth_mm"], base_t)
    for station, gap in enumerate(gauge["slot_gaps_mm"], 1):
        x = gauge["side_margin_mm"] + (station - 1) * gauge["station_pitch_mm"]
        z = base_t - 0.1
        height = gauge["plate_height_above_base_mm"] + 0.1
        back = cq.Solid.makeBox(gauge["station_width_mm"], gauge["back_plate_depth_mm"], height, cq.Vector(x, gauge["back_plate_y_mm"], z))
        front_y = gauge["back_plate_y_mm"] - gap - gauge["front_plate_depth_mm"]
        front = cq.Solid.makeBox(gauge["station_width_mm"], gauge["front_plate_depth_mm"], height, cq.Vector(x, front_y, z))
        shape = shape.fuse(back).fuse(front)
        holes = []
        for hole in range(station):
            holes.append(cq.Solid.makeCylinder(
                gauge["identity_hole_diameter_mm"] / 2.0, base_t + 0.2,
                cq.Vector(x + gauge["station_width_mm"] / 2.0 + (hole - (station - 1) / 2.0) * 3.0, 5.0, -0.1),
            ))
        shape = shape.cut(cq.Compound.makeCompound(holes))
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("label-slot gauge is not one valid solid")
    return shape, {
        "part_id": "label-slot-gauge", "slot_gaps_mm": gauge["slot_gaps_mm"],
        "identity_holes": [1, 2, 3],
        "outer_dimensions_mm": [width, gauge["base_depth_mm"], base_t + gauge["plate_height_above_base_mm"]],
        "external_assets": [],
    }


def validate_parameters(parameters: dict) -> None:
    bin_p = parameters["bin"]
    carrier = parameters["carrier"]
    widths = {item["id"]: item["outer_width_mm"] for item in parameters["bins"]}
    assert parameters["project"]["id"] == PROJECT_ID
    assert 4.0 * widths["narrow"] == carrier["packing_width_mm"]
    assert widths["wide"] + 2.0 * widths["narrow"] == carrier["packing_width_mm"]
    assert 2.0 * widths["medium"] + widths["narrow"] == carrier["packing_width_mm"]
    assert bin_p["paper_card_thickness_max_mm"] < bin_p["label_slot_gap_mm"]
    assert bin_p["wall_mm"] / parameters["printer"]["line_width_mm"] == 4.0
    assert bin_p["floor_mm"] / parameters["printer"]["layer_height_mm"] == 9.0
    assert bin_p["scoop_depth_mm"] < bin_p["outer_depth_mm"] / 4.0
    assert bin_p["scoop_rise_mm"] < bin_p["outer_height_mm"] / 3.0
    assert parameters["gauge"]["slot_gaps_mm"] == [0.5, 0.7, 0.9]
    dims = carrier_dimensions(parameters)
    assert dims["outer_width_mm"] <= 220.0 and dims["outer_depth_mm"] <= 160.0 and dims["height_mm"] <= 140.0
    assert parameters["workflow_contract"]["small_parts_warning"] == "adult_storage_only_not_child_directed"


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
    for preset in parameters["bins"]:
        shapes[preset["id"]], interfaces[preset["id"]] = make_bin(parameters, preset)
    shapes["matrix-frame"], interfaces["matrix-frame"] = make_carrier(parameters)
    shapes["label-slot-gauge"], interfaces["label-slot-gauge"] = make_label_slot_gauge(parameters)

    step_paths: list[Path] = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    assembly = cq.Compound.makeCompound([
        shapes["matrix-frame"],
        shapes["narrow"].translate((205.0, 0.0, 0.0)),
        shapes["medium"].translate((260.0, 0.0, 0.0)),
        shapes["wide"].translate((340.0, 0.0, 0.0)),
        shapes["label-slot-gauge"].translate((205.0, 95.0, 0.0)),
    ])
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"
    export_step(assembly, assembly_path)
    step_paths.append(assembly_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("narrow", "medium", "wide"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-bin-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    carrier_path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-matrix-frame-{REVISION}.stl"
    export_stl(shapes["matrix-frame"], carrier_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    mesh_paths["matrix-frame"] = carrier_path
    gauge_path = COUPONS / f"DRAFT-{PROJECT_ID}-label-slot-gauge-{REVISION}.stl"
    export_stl(shapes["label-slot-gauge"], gauge_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    mesh_paths["label-slot-gauge"] = gauge_path

    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-labelable-small-parts-bin-set-{REVISION}.3mf"
    order = ["matrix-frame", "narrow", "medium", "wide", "label-slot-gauge"]
    placements = [(10.0, 10.0), (215.0, 10.0), (275.0, 10.0), (10.0, 190.0), (120.0, 190.0)]
    write_3mf(package_path, [(name, mesh_paths[name]) for name in order], placements)

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
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All five B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every deliverable is one B-Rep solid"),
        check("three-bin-widths", [interfaces[name]["body_width_mm"] for name in ("narrow", "medium", "wide")] == [45.0, 67.5, 90.0], "All three measured widths are generated"),
        check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "No external font, vector or mesh asset is used"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", report(
        f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)], parametric_checks,
        {"python": platform.python_version(), "cadquery": cq.__version__, "unique_parts": list(shapes), "print_objects": list(mesh_paths)},
        ["Any parameter change requires regeneration of downstream evidence."],
    ))
    write_json(VALIDATION / "mesh-generation-report.json", report(
        f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks, {"meshes": metrics},
        ["Topology does not prove drawer fit, label retention or small-part retrieval."],
    ))

    bins = [interfaces[name] for name in ("narrow", "medium", "wide")]
    carrier = interfaces["matrix-frame"]
    gauge = interfaces["label-slot-gauge"]
    interface_checks = [
        check("electronics-row-a", 4.0 * bins[0]["body_width_mm"] == carrier["packing_width_mm"], "Four narrow bins tile 180 mm"),
        check("electronics-row-b", bins[2]["body_width_mm"] + 2.0 * bins[0]["body_width_mm"] == carrier["packing_width_mm"], "One wide and two narrow bins tile 180 mm"),
        check("sewing-row", 2.0 * bins[1]["body_width_mm"] + bins[0]["body_width_mm"] == carrier["packing_width_mm"], "Two medium and one narrow bin tile 180 mm"),
        check("common-depth-height", all(item["body_depth_mm"] == 75.0 and item["body_height_mm"] == 36.0 for item in bins), "All bins share depth and height"),
        check("printable-shell", all(item["wall_mm"] == 1.8 and item["floor_mm"] == 1.8 for item in bins), "Every bin has four-line walls and nine-layer floor"),
        check("pickup-ramp", all(item["pickup_ramp_mm"] == [13.0, 7.0] for item in bins), "Every bin retains the pickup ramp"),
        check("label-slot", all(item["label_slot_gap_mm"] == 0.7 for item in bins), "Every bin retains the target label gap"),
        check("gauge-series", gauge["slot_gaps_mm"] == [0.5, 0.7, 0.9], "Coupon brackets the target label gap"),
        check("carrier-clearance", carrier["side_clearance_mm"] == 0.6 and carrier["row_clearance_mm"] == 1.2, "Carrier clearances are exact"),
        check("portfolio-envelope", all(item["outer_dimensions_mm"][0] <= 220.0 and item["outer_dimensions_mm"][1] <= 160.0 and item["outer_dimensions_mm"][2] <= 140.0 for item in interfaces.values()), "Every part fits the portfolio envelope"),
        check("claim-boundary", parameters["workflow_contract"]["electrical_claim"] == "passive_storage_only_no_batteries_or_energized_parts", "Passive-storage boundary is explicit"),
    ]
    write_json(VALIDATION / "interface-report.json", report(
        f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"], interface_checks,
        {"interfaces": interfaces, "workflow_contract": parameters["workflow_contract"]},
        ["Analytic clearances do not replace a printed coupon or actual drawer/use-case pilot."],
    ))

    baseline_volume = 0.0
    for name in ("narrow", "medium", "wide"):
        dims = interfaces[name]["outer_dimensions_mm"]
        baseline_volume += dims[0] * dims[1] * dims[2]
    for name in ("matrix-frame", "label-slot-gauge"):
        dims = interfaces[name]["outer_dimensions_mm"]
        baseline_volume += dims[0] * dims[1] * dims[2]
    candidate_volume = sum(float(shapes[name].Volume()) for name in shapes)
    reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "baseline": {"description": "five solid unique-part envelope blocks", "volume_mm3": baseline_volume},
        "candidate": {"description": "three thin shells, local rails and ramp, open carrier and slot gauge", "volume_mm3": candidate_volume},
        "volume_reduction_percent": reduction, "selection_threshold_percent": 65.0,
        "status": "PASS" if reduction >= 65.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE",
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL",
        "meshes": metrics, "simplification": "NOT_BENEFICIAL",
        "reason": "Analytic rounded corners and narrow label rails are under budget; decimation risks closing the measured slot.",
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
