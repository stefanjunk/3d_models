#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-024 BridgeKey pull-face family."""
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
PROJECT_ID = "MM-ORG-024"
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
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


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


def rounded_plate(width: float, height: float, thickness: float, radius: float, edge_radius: float) -> cq.Shape:
    plate = (
        cq.Workplane("XY")
        .box(width, height, thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(radius)
    )
    return plate.edges().fillet(edge_radius).val()


def key_slot_cutter(
    face: dict,
    entry_center_x: float,
    locked_center_x: float,
    center_y: float,
    thickness: float,
) -> cq.Shape:
    direction = 1.0 if entry_center_x > locked_center_x else -1.0
    inner_edge = locked_center_x - direction * face["key_entry_width_mm"] / 2.0
    outer_edge = entry_center_x
    track_center_x = (inner_edge + outer_edge) / 2.0
    track_width = abs(outer_edge - inner_edge)
    entry = (
        cq.Workplane("XY")
        .box(
            face["key_entry_width_mm"],
            face["key_entry_height_mm"],
            thickness,
            centered=(True, True, False),
        )
        .translate((entry_center_x, center_y, -1.0))
        .val()
    )
    track = (
        cq.Workplane("XY")
        .box(track_width, face["key_track_height_mm"], thickness, centered=(True, True, False))
        .translate((track_center_x, center_y, -1.0))
        .val()
    )
    return entry.fuse(track)


def make_face(parameters: dict) -> tuple[cq.Shape, dict]:
    face = parameters["face"]
    plate = rounded_plate(
        face["width_mm"],
        face["height_mm"],
        face["plate_thickness_mm"],
        face["corner_radius_mm"],
        face["edge_radius_mm"],
    )

    y0 = -face["height_mm"] / 2.0
    wedge = (
        cq.Workplane("YZ")
        .polyline(
            [
                (y0, face["plate_thickness_mm"] - 0.2),
                (y0, face["pull_depth_mm"]),
                (y0 + face["pull_flat_mm"], face["pull_depth_mm"]),
                (y0 + face["pull_height_mm"], face["plate_thickness_mm"] - 0.2),
            ]
        )
        .close()
        .extrude(face["pull_width_mm"] / 2.0, both=True)
    )
    wedge = wedge.edges("|X").fillet(0.8).val()
    shape = plate.fuse(wedge).clean()

    pocket = (
        cq.Workplane("XY")
        .box(
            face["label_pocket_width_mm"],
            face["label_pocket_height_mm"],
            face["label_recess_depth_mm"] + 0.2,
            centered=(True, True, False),
        )
        .translate(
            (
                0.0,
                face["label_pocket_center_y_mm"],
                face["plate_thickness_mm"] - face["label_recess_depth_mm"],
            )
        )
        .val()
    )
    shape = shape.cut(pocket)

    rail_z = face["plate_thickness_mm"] - 0.1
    rail_w = face["label_rail_width_mm"]
    rail_h = face["label_rail_height_mm"] + 0.1
    pocket_w = face["label_pocket_width_mm"]
    pocket_h = face["label_pocket_height_mm"]
    pocket_y = face["label_pocket_center_y_mm"]
    rails = [
        cq.Workplane("XY").box(rail_w, pocket_h + rail_w, rail_h, centered=(True, True, False)).translate((-(pocket_w + rail_w) / 2.0, pocket_y, rail_z)).val(),
        cq.Workplane("XY").box(rail_w, pocket_h + rail_w, rail_h, centered=(True, True, False)).translate(((pocket_w + rail_w) / 2.0, pocket_y, rail_z)).val(),
        cq.Workplane("XY").box(pocket_w + 2.0 * rail_w, rail_w, rail_h, centered=(True, True, False)).translate((0.0, pocket_y - (pocket_h + rail_w) / 2.0, rail_z)).val(),
    ]
    for rail in rails:
        rail = cq.Workplane(obj=rail).edges().fillet(0.3).val()
        shape = shape.fuse(rail)

    for sign in (-1.0, 1.0):
        cutter = key_slot_cutter(
            face,
            sign * face["key_entry_center_x_mm"],
            sign * face["key_locked_center_x_mm"],
            face["key_center_y_mm"],
            face["plate_thickness_mm"] + 2.0,
        )
        shape = shape.cut(cutter)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("pull/label face is not one valid solid")
    bounds = shape.BoundingBox()
    return shape, {
        "part_id": "pull-label-face",
        "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
        "label_insert_mm": [face["label_insert_width_mm"], face["label_insert_height_mm"]],
        "label_pocket_mm": [pocket_w, pocket_h, face["label_recess_depth_mm"]],
        "key_entry_centers_x_mm": [-face["key_entry_center_x_mm"], face["key_entry_center_x_mm"]],
        "key_locked_centers_x_mm": [-face["key_locked_center_x_mm"], face["key_locked_center_x_mm"]],
        "key_slot_mm": [
            face["key_entry_width_mm"],
            face["key_entry_height_mm"],
            face["key_track_height_mm"],
        ],
        "pull_mm": [face["pull_width_mm"], face["pull_height_mm"], face["pull_depth_mm"]],
        "print_orientation": "broad_back_face_down",
        "external_assets": [],
    }


def make_clip(parameters: dict, preset: dict) -> tuple[cq.Shape, dict]:
    clip = parameters["clip"]
    face = parameters["face"]
    arm = clip["arm_thickness_mm"]
    gap = preset["gap_mm"]
    total_depth = 2.0 * arm + gap
    height = clip["height_mm"]
    width = clip["body_width_mm"]
    outer = cq.Workplane("XY").box(total_depth, height, width, centered=(False, False, False)).val()
    opening = (
        cq.Workplane("XY")
        .box(gap, height - clip["bridge_height_mm"] + 1.0, width + 2.0, centered=(False, False, False))
        .translate((arm, clip["bridge_height_mm"], -1.0))
        .val()
    )
    shape = outer.cut(opening)

    key_y = clip["key_center_y_mm"]
    neck_h = clip["key_neck_height_mm"]
    stem = (
        cq.Workplane("XY")
        .box(clip["key_stem_length_mm"], neck_h, width, centered=(False, False, False))
        .translate((-clip["key_stem_length_mm"], key_y - neck_h / 2.0, 0.0))
        .val()
    )
    head = (
        cq.Workplane("XY")
        .box(
            clip["key_head_thickness_mm"],
            clip["key_head_height_mm"],
            width,
            centered=(False, False, False),
        )
        .translate(
            (
                -clip["key_stem_length_mm"] - clip["key_head_thickness_mm"],
                key_y - clip["key_head_height_mm"] / 2.0,
                0.0,
            )
        )
        .val()
    )
    shape = shape.fuse(stem).fuse(head).clean()

    for index in range(preset["identity_holes"]):
        x = total_depth / 2.0 + (index - (preset["identity_holes"] - 1) / 2.0) * 1.4
        recess = cq.Solid.makeCylinder(
            clip["identity_hole_diameter_mm"] / 2.0,
            clip["identity_recess_depth_mm"] + 0.1,
            cq.Vector(x, clip["bridge_height_mm"] / 2.0, width - clip["identity_recess_depth_mm"]),
            cq.Vector(0.0, 0.0, 1.0),
        )
        shape = shape.cut(recess)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"{preset['id']} clip is not one valid solid")
    bounds = shape.BoundingBox()
    return shape, {
        "part_id": f"clip-{preset['id']}",
        "gap_mm": gap,
        "target_host_thickness_mm": preset["target_host_thickness_mm"],
        "nominal_clearance_mm": gap - preset["target_host_thickness_mm"],
        "arm_thickness_mm": arm,
        "bridge_height_mm": clip["bridge_height_mm"],
        "key_mm": [
            width,
            neck_h,
            clip["key_head_height_mm"],
            clip["key_stem_length_mm"],
            clip["key_head_thickness_mm"],
        ],
        "identity_holes": preset["identity_holes"],
        "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
        "print_orientation": "broad_profile_face_down",
        "external_assets": [],
    }


def make_gap_gauge(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupons"]
    face = parameters["face"]
    width = coupon["gap_gauge_width_mm"]
    height = coupon["gap_gauge_height_mm"]
    thickness = coupon["gap_gauge_thickness_mm"]
    shape = rounded_plate(width, height, thickness, 3.0, 0.6)
    gaps = []
    for station, (x, preset) in enumerate(zip(coupon["gap_station_centers_x_mm"], parameters["clip_presets"]), 1):
        gap = preset["gap_mm"]
        gaps.append(gap)
        stop = coupon["gap_slot_stop_y_mm"]
        cutter_height = height / 2.0 - stop + 2.0
        cutter = (
            cq.Workplane("XY")
            .box(gap, cutter_height, thickness + 2.0, centered=(True, True, False))
            .translate((x, stop + cutter_height / 2.0, -1.0))
            .val()
        )
        shape = shape.cut(cutter)
        for index in range(station):
            hole = cq.Solid.makeCylinder(
                0.7,
                thickness + 2.0,
                cq.Vector(x + (index - (station - 1) / 2.0) * 2.2, -11.0, -1.0),
                cq.Vector(0.0, 0.0, 1.0),
            )
            shape = shape.cut(hole)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("gap gauge is not one valid solid")
    return shape, {
        "part_id": "gap-gauge",
        "gaps_mm": gaps,
        "station_centers_x_mm": coupon["gap_station_centers_x_mm"],
        "slot_stop_y_mm": coupon["gap_slot_stop_y_mm"],
        "outer_dimensions_mm": [width, height, thickness],
        "identity_holes": [1, 2, 3],
        "print_orientation": "broad_face_down",
        "external_assets": [],
    }


def make_key_coupon(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupons"]
    face = parameters["face"]
    width = coupon["key_coupon_width_mm"]
    height = coupon["key_coupon_height_mm"]
    thickness = coupon["key_coupon_thickness_mm"]
    shape = rounded_plate(width, height, thickness, 3.0, 0.6)
    cutter = key_slot_cutter(face, 8.0, 0.5, 0.0, thickness + 2.0)
    shape = shape.cut(cutter).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("key-slot coupon is not one valid solid")
    return shape, {
        "part_id": "key-slot-coupon",
        "key_slot_mm": [
            face["key_entry_width_mm"],
            face["key_entry_height_mm"],
            face["key_track_height_mm"],
        ],
        "outer_dimensions_mm": [width, height, thickness],
        "print_orientation": "broad_face_down",
        "external_assets": [],
    }


def validate_parameters(parameters: dict) -> None:
    face = parameters["face"]
    clip = parameters["clip"]
    gaps = [item["gap_mm"] for item in parameters["clip_presets"]]
    targets = [item["target_host_thickness_mm"] for item in parameters["clip_presets"]]
    assert parameters["project"]["id"] == PROJECT_ID
    assert gaps == [2.2, 2.9, 3.6]
    assert targets == [1.92, 2.67, 3.3]
    assert np.allclose(np.subtract(gaps, targets), [0.28, 0.23, 0.30])
    assert face["label_insert_width_mm"] == 76.2
    assert face["label_insert_height_mm"] == 20.0
    assert face["label_pocket_width_mm"] > face["label_insert_width_mm"]
    assert face["label_pocket_height_mm"] > face["label_insert_height_mm"]
    assert face["key_entry_height_mm"] > clip["key_head_height_mm"]
    assert face["key_track_height_mm"] > clip["key_neck_height_mm"]
    assert face["key_entry_width_mm"] > clip["body_width_mm"]
    assert clip["key_stem_length_mm"] > face["plate_thickness_mm"]
    assert face["plate_thickness_mm"] / parameters["printer"]["layer_height_mm"] == 15.0
    assert clip["bridge_height_mm"] / parameters["printer"]["layer_height_mm"] == 15.0
    assert face["width_mm"] <= 180.0 and face["height_mm"] <= 50.0 and face["pull_depth_mm"] <= 55.0
    assert parameters["workflow_contract"]["claim"] == "light_horizontal_slide_pull_only_no_lifting_or_load_rating"


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
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_file(path),
        "triangles": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "file_bytes": path.stat().st_size,
        "file_mib": path.stat().st_size / (1024 * 1024),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
        "components": int(len(mesh.split(only_watertight=False))),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "extents_mm": np.round(mesh.extents, 4).tolist(),
        "bounds_mm": np.round(mesh.bounds, 4).tolist(),
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
    shapes["pull-label-face"], interfaces["pull-label-face"] = make_face(parameters)
    for preset in parameters["clip_presets"]:
        name = f"clip-{preset['id']}"
        shapes[name], interfaces[name] = make_clip(parameters, preset)
    shapes["gap-gauge"], interfaces["gap-gauge"] = make_gap_gauge(parameters)
    shapes["key-slot-coupon"], interfaces["key-slot-coupon"] = make_key_coupon(parameters)

    step_paths = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    exploded = cq.Compound.makeCompound(
        [
            shapes["pull-label-face"],
            shapes["clip-thin"].translate((75.0, -25.0, 0.0)),
            shapes["clip-shelffit"].translate((95.0, -25.0, 0.0)),
            shapes["clip-thick"].translate((115.0, -25.0, 0.0)),
            shapes["gap-gauge"].translate((-20.0, 60.0, 0.0)),
            shapes["key-slot-coupon"].translate((60.0, 60.0, 0.0)),
        ]
    )
    exploded_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"
    export_step(exploded, exploded_path)
    step_paths.append(exploded_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("pull-label-face", "clip-thin", "clip-shelffit", "clip-thick"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    for name in ("gap-gauge", "key-slot-coupon"):
        path = COUPONS / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path

    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-deep-shelf-pull-tab-bin-front-{REVISION}.3mf"
    order = ["pull-label-face", "clip-thin", "clip-shelffit", "clip-thick", "gap-gauge", "key-slot-coupon"]
    placements = [(10.0, 10.0), (145.0, 10.0), (165.0, 10.0), (185.0, 10.0), (10.0, 75.0), (100.0, 75.0)]
    write_3mf(package_path, [(name, mesh_paths[name]) for name in order], placements)

    metrics = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
    mesh_checks = []
    for name, item in metrics.items():
        mesh_checks.extend(
            [
                check(f"{name}:watertight", item["watertight"], f"{name} is watertight"),
                check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"),
                check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"),
                check(f"{name}:component", item["components"] == 1, f"{name} is one component"),
                check(f"{name}:triangles", item["triangles"] <= mesh_p["triangle_stop"], "Triangle budget", {"actual": item["triangles"], "limit": mesh_p["triangle_stop"]}),
                check(f"{name}:file", item["file_mib"] <= mesh_p["max_mesh_mib"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": mesh_p["max_mesh_mib"]}),
            ]
        )

    parametric_checks = [
        check("parameter-validation", True, "Fail-closed parameter relations pass"),
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All six B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every deliverable is one B-Rep solid"),
        check("three-clip-gaps", [interfaces[f"clip-{item['id']}"]["gap_mm"] for item in parameters["clip_presets"]] == [2.2, 2.9, 3.6], "All protected clip gaps are generated"),
        check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "No external font, vector or mesh asset is used"),
    ]
    write_json(
        VALIDATION / "parametric-source-report.json",
        report(
            f"{PROJECT_ID}-parametric-source",
            [PARAMETERS, Path(__file__)],
            parametric_checks,
            {"python": platform.python_version(), "cadquery": cq.__version__, "unique_parts": list(shapes), "print_objects": list(mesh_paths)},
            ["Any parameter change requires regeneration of downstream evidence."],
        ),
    )
    write_json(
        VALIDATION / "mesh-generation-report.json",
        report(
            f"{PROJECT_ID}-mesh-generation",
            [PARAMETERS, Path(__file__)],
            mesh_checks,
            {"meshes": metrics},
            ["Topology does not prove clip preload, fatigue, host marking, label retention or safe pull behavior."],
        ),
    )

    face_i = interfaces["pull-label-face"]
    clip_i = [interfaces[f"clip-{item['id']}"] for item in parameters["clip_presets"]]
    gauge_i = interfaces["gap-gauge"]
    key_i = interfaces["key-slot-coupon"]
    expected_clearances = [0.28, 0.23, 0.30]
    interface_checks = [
        check("clip-gap-series", [item["gap_mm"] for item in clip_i] == [2.2, 2.9, 3.6], "Clip gap series is exact"),
        check("gauge-matches", gauge_i["gaps_mm"] == [item["gap_mm"] for item in clip_i], "Gap gauge reproduces every clip gap"),
        check("host-clearance-series", np.allclose([item["nominal_clearance_mm"] for item in clip_i], expected_clearances), "Nominal host clearances are bounded", {"clearance_mm": [item["nominal_clearance_mm"] for item in clip_i]}),
        check("key-entry-clearance", np.isclose(parameters["face"]["key_entry_height_mm"] - parameters["clip"]["key_head_height_mm"], 0.4), "Key head has 0.4 mm entry-height clearance"),
        check("key-track-clearance", np.isclose(parameters["face"]["key_track_height_mm"] - parameters["clip"]["key_neck_height_mm"], 0.4), "Key neck has 0.4 mm track-height clearance"),
        check("key-width-clearance", np.isclose(parameters["face"]["key_entry_width_mm"] - parameters["clip"]["body_width_mm"], 0.6), "Key has 0.6 mm entry-width clearance"),
        check("key-coupon-matches", key_i["key_slot_mm"] == face_i["key_slot_mm"], "Coupon reproduces the face key slot"),
        check("label-clearance", np.allclose([parameters["face"]["label_pocket_width_mm"] - parameters["face"]["label_insert_width_mm"], parameters["face"]["label_pocket_height_mm"] - parameters["face"]["label_insert_height_mm"]], [1.2, 1.2]), "Paper label has 1.2 mm total width and height clearance"),
        check("two-locked-centers", face_i["key_locked_centers_x_mm"] == [-46.5, 46.5], "Two locked clip centers remain exact"),
        check("orientation", all(item["print_orientation"] in {"broad_back_face_down", "broad_profile_face_down", "broad_face_down"} for item in interfaces.values()), "All unique parts have support-conscious broad-face orientations"),
        check("portfolio-envelope", all(max(item["outer_dimensions_mm"]) <= 180.0 and sorted(item["outer_dimensions_mm"])[-2] <= 55.0 for item in interfaces.values()), "All parts fit the product envelope"),
        check("claim-boundary", parameters["workflow_contract"]["claim"] == "light_horizontal_slide_pull_only_no_lifting_or_load_rating", "No lifting or load-rating claim is present"),
    ]
    write_json(
        VALIDATION / "interface-report.json",
        report(
            f"{PROJECT_ID}-interface-validation",
            [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
            interface_checks,
            {"interfaces": interfaces, "workflow_contract": parameters["workflow_contract"]},
            ["Analytic gaps and key clearances cannot establish real PETG preload, fatigue, creep, marking or pull comfort."],
        ),
    )

    baseline_volume = sum(np.prod(interfaces[name]["outer_dimensions_mm"]) for name in shapes)
    candidate_volume = sum(float(shapes[name].Volume()) for name in shapes)
    reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0",
        "project": PROJECT_ID,
        "revision": REVISION,
        "baseline": {"description": "six solid rectangular envelope blocks", "volume_mm3": float(baseline_volume)},
        "candidate": {"description": "local pull wedge, U-clips, open key slots and measurement notches", "volume_mm3": candidate_volume},
        "volume_reduction_percent": reduction,
        "selection_threshold_percent": 35.0,
        "status": "PASS" if reduction >= 35.0 else "FAIL",
        "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE",
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(
        REPORTS / "mesh-complexity.json",
        {
            "schema_version": "1.0",
            "project": PROJECT_ID,
            "revision": REVISION,
            "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL",
            "meshes": metrics,
            "simplification": "NOT_BENEFICIAL",
            "reason": "Exact clip gaps, key clearances, label rails and pull edges are under budget; decimation risks protected interfaces.",
        },
    )
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(
        REPORTS / "build-manifest.json",
        {
            "schema_version": "1.0",
            "project": PROJECT_ID,
            "revision": REVISION,
            "status": "PASS",
            "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))],
            "outputs": [input_record(path) for path in outputs],
            "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]],
        },
    )
    gate_reports = [json.loads((VALIDATION / name).read_text()) for name in ("parametric-source-report.json", "mesh-generation-report.json", "interface-report.json")]
    if any(value["status"] != "PASS" for value in [*gate_reports, optimization]):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "unique_meshes": len(mesh_paths), "3mf": str(package_path.relative_to(ROOT)), "volume_reduction_percent": reduction}, indent=2))


if __name__ == "__main__":
    main()
