#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-016 stencil-ruler bookmark set."""
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
PROJECT_ID = "MM-ORG-016"
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


def rounded_plate(width: float, length: float, height: float, radius: float) -> cq.Shape:
    shape = cq.Workplane("XY").rect(width, length).extrude(height).edges("|Z").fillet(radius).val()
    return shape.translate((width / 2.0, length / 2.0, 0.0))


def circle_cutter(diameter: float, x: float, y: float, height: float) -> cq.Shape:
    return cq.Solid.makeCylinder(diameter / 2.0, height + 0.2, cq.Vector(x, y, -0.1))


def box_cutter(width: float, depth: float, x: float, y: float, height: float) -> cq.Shape:
    return cq.Solid.makeBox(width, depth, height + 0.2, cq.Vector(x - width / 2.0, y - depth / 2.0, -0.1))


def rounded_rect_cutter(width: float, depth: float, x: float, y: float, height: float, radius: float) -> cq.Shape:
    value = cq.Workplane("XY").rect(width, depth).extrude(height + 0.2).edges("|Z").fillet(radius).val()
    return value.translate((x, y, -0.1))


def polygon_cutter(points: list[tuple[float, float]], x: float, y: float, height: float) -> cq.Shape:
    return cq.Workplane("XY").polyline(points).close().extrude(height + 0.2).val().translate((x, y, -0.1))


def ellipse_cutter(rx: float, ry: float, x: float, y: float, height: float) -> cq.Shape:
    return cq.Workplane("XY").ellipse(rx, ry).extrude(height + 0.2).val().translate((x, y, -0.1))


def cut_compound(shape: cq.Shape, cutters: list[cq.Shape]) -> cq.Shape:
    return shape.cut(cq.Compound.makeCompound(cutters)) if cutters else shape


def identity_cutters(parameters: dict, count: int) -> list[cq.Shape]:
    plate = parameters["plate"]
    spacing = 3.2
    start = plate["width_mm"] / 2.0 - spacing * (count - 1) / 2.0
    return [circle_cutter(plate["identity_hole_diameter_mm"], start + i * spacing, 136.0, plate["height_mm"]) for i in range(count)]


def registration_cutters(parameters: dict, pitch: float) -> list[cq.Shape]:
    plate = parameters["plate"]
    count = int(round(plate["registration_length_mm"] / pitch)) + 1
    return [
        circle_cutter(
            plate["registration_hole_diameter_mm"],
            plate["registration_x_mm"],
            plate["registration_start_y_mm"] + index * pitch,
            plate["height_mm"],
        )
        for index in range(count)
    ]


def make_layout_plate(parameters: dict, style: dict) -> tuple[cq.Shape, dict]:
    plate = parameters["plate"]
    cutters = registration_cutters(parameters, style["grid_pitch_mm"])
    box_centers_y = [17.0, 29.0, 41.0, 53.0]
    for width, center_y in zip(style["box_widths_mm"], box_centers_y):
        cutters.append(rounded_rect_cutter(width, 3.2, 25.0, center_y, plate["height_mm"], plate["internal_corner_radius_mm"]))
    for center_y in style["horizontal_slot_y_mm"]:
        cutters.append(rounded_rect_cutter(plate["rule_slot_length_mm"], plate["rule_slot_width_mm"], 23.6, center_y, plate["height_mm"], 0.55))
    for center_x in style["vertical_slot_x_mm"]:
        cutters.append(rounded_rect_cutter(plate["rule_slot_width_mm"], 24.0, center_x, 98.0, plate["height_mm"], 0.55))
    for center_y in (118.0, 127.0):
        cutters.append(rounded_rect_cutter(plate["rule_slot_length_mm"], plate["rule_slot_width_mm"], 23.6, center_y, plate["height_mm"], 0.55))
    cutters.extend(identity_cutters(parameters, style["identity_holes"]))
    base = rounded_plate(plate["width_mm"], plate["length_mm"], plate["height_mm"], plate["corner_radius_mm"])
    result = cut_compound(base, cutters).clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError(f"{style['id']} is not one valid solid")
    return result, {
        "id": style["id"],
        "kind": style["kind"],
        "grid_pitch_mm": style["grid_pitch_mm"],
        "registration_holes": int(round(plate["registration_length_mm"] / style["grid_pitch_mm"])) + 1,
        "box_openings": len(style["box_widths_mm"]),
        "horizontal_rule_slots": len(style["horizontal_slot_y_mm"]) + 2,
        "vertical_rule_slots": len(style["vertical_slot_x_mm"]),
        "identity_holes": style["identity_holes"],
        "total_cutters": len(cutters),
    }


def star_points(outer: float, inner: float, points: int = 8) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    for index in range(points * 2):
        radius = outer if index % 2 == 0 else inner
        angle = math.pi / 2.0 + index * math.pi / points
        result.append((radius * math.cos(angle), radius * math.sin(angle)))
    return result


def signal_cutter(name: str, x: float, y: float, height: float) -> cq.Shape:
    if name == "orbit":
        return ellipse_cutter(4.0, 2.5, x, y, height)
    if name == "facet":
        return polygon_cutter([(0, 4), (3.6, 2), (3.6, -2), (0, -4), (-3.6, -2), (-3.6, 2)], x, y, height)
    if name == "seed":
        return polygon_cutter([(0, 4), (3.5, 1.4), (3.0, -2.4), (0, -4), (-3.0, -2.4), (-3.5, 1.4)], x, y, height)
    if name == "gate":
        return polygon_cutter([(-4, -3), (4, -3), (4, 1.4), (2, 4), (-2, 4), (-4, 1.4)], x, y, height)
    if name == "ribbon":
        return polygon_cutter([(-4, -3), (0, -1.1), (4, -3), (3.2, 3.5), (0, 2.2), (-3.2, 3.5)], x, y, height)
    if name == "pulse":
        return polygon_cutter([(-3.5, 3.5), (0.5, 3.5), (-0.4, 0.8), (3.5, 0.8), (-2.0, -3.5), (-0.7, -0.3), (-3.5, -0.3)], x, y, height)
    if name == "bracket":
        return polygon_cutter([(-4, -4), (3.6, -4), (3.6, -2.2), (-1.8, -2.2), (-1.8, 2.2), (3.6, 2.2), (3.6, 4), (-4, 4)], x, y, height)
    if name == "comet":
        head = circle_cutter(5.0, x - 1.0, y + 1.0, height)
        tail = polygon_cutter([(-3.0, 1.0), (4.0, -4.0), (1.0, 2.8)], x, y, height)
        return head.fuse(tail)
    if name == "tile":
        return polygon_cutter([(-4, -3.5), (-1.2, -3.5), (0, -2.0), (1.2, -3.5), (4, -3.5), (4, 3.5), (-4, 3.5)], x, y, height)
    if name == "flare":
        return polygon_cutter(star_points(4.0, 2.3), x, y, height)
    if name == "pin":
        head = circle_cutter(5.2, x, y + 1.2, height)
        stem = polygon_cutter([(-1.3, 0.2), (1.3, 0.2), (0, -4.0)], x, y, height)
        return head.fuse(stem)
    if name == "bridge":
        return polygon_cutter([(-4, -3), (-4, 3), (-1.5, 3), (0, 1.2), (1.5, 3), (4, 3), (4, -3), (2.2, -3), (2.2, 0.2), (0, -1.7), (-2.2, 0.2), (-2.2, -3)], x, y, height)
    raise ValueError(f"unknown signal icon: {name}")


def make_signal_plate(parameters: dict, style: dict) -> tuple[cq.Shape, dict]:
    plate = parameters["plate"]
    cutters = registration_cutters(parameters, style["grid_pitch_mm"])
    centers_x = [10.0, 21.0, 32.0]
    centers_y = [20.0, 48.0, 76.0, 104.0]
    placements = []
    for name, (x, y) in zip(style["icon_names"], [(x, y) for y in centers_y for x in centers_x]):
        cutters.append(signal_cutter(name, x, y, plate["height_mm"]))
        placements.append({"name": name, "center_mm": [x, y], "cell_mm": [11.0, 28.0]})
    for center_y in (121.0, 128.0):
        cutters.append(rounded_rect_cutter(plate["rule_slot_length_mm"], plate["rule_slot_width_mm"], 23.6, center_y, plate["height_mm"], 0.55))
    cutters.extend(identity_cutters(parameters, style["identity_holes"]))
    base = rounded_plate(plate["width_mm"], plate["length_mm"], plate["height_mm"], plate["corner_radius_mm"])
    result = cut_compound(base, cutters).clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("signal-12 is not one valid solid")
    return result, {
        "id": style["id"],
        "kind": style["kind"],
        "registration_holes": int(round(plate["registration_length_mm"] / style["grid_pitch_mm"])) + 1,
        "icons": placements,
        "identity_holes": style["identity_holes"],
        "total_cutters": len(cutters),
        "external_assets": [],
    }


def make_coupon(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    base = rounded_plate(coupon["width_mm"], coupon["depth_mm"], coupon["height_mm"], coupon["corner_radius_mm"])
    cutters: list[cq.Shape] = []
    for size, center_x in zip(coupon["feature_sizes_mm"], coupon["feature_centers_x_mm"]):
        cutters.append(rounded_rect_cutter(size, coupon["slot_length_mm"], center_x, coupon["slot_center_y_mm"], coupon["height_mm"], min(0.35, size / 3.0)))
        cutters.append(circle_cutter(size, center_x, coupon["round_center_y_mm"], coupon["height_mm"]))
    result = cut_compound(base, cutters).clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("minimum-feature coupon is not one valid solid")
    return result, {
        "outer_dimensions_mm": [coupon["width_mm"], coupon["depth_mm"], coupon["height_mm"]],
        "slot_widths_mm": coupon["feature_sizes_mm"],
        "round_diameters_mm": coupon["feature_sizes_mm"],
        "production_minimum_mm": parameters["minimum_features"]["production_opening_mm"],
        "subminimum_features_are_coupon_only": True,
    }


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    plate = parameters["plate"]
    minimum = parameters["minimum_features"]
    styles = parameters["styles"]
    coupon = parameters["coupon"]
    printer = parameters["printer"]
    assert project["id"] == PROJECT_ID and project["revision"] == REVISION and project["units"] == "mm"
    assert len(styles) == 3 and [style["identity_holes"] for style in styles] == [1, 2, 3]
    assert plate["height_mm"] == 4 * printer["layer_height_mm"]
    assert plate["registration_hole_diameter_mm"] >= minimum["production_opening_mm"]
    assert plate["rule_slot_width_mm"] >= minimum["production_opening_mm"]
    assert plate["registration_x_mm"] - plate["registration_hole_diameter_mm"] / 2.0 >= minimum["paper_edge_boundary_mm"]
    for style in styles[:2]:
        assert plate["registration_length_mm"] % style["grid_pitch_mm"] == 0
        assert style["box_widths_mm"] == [style["grid_pitch_mm"] * value for value in (1, 2, 3, 4)]
        gaps = [b - a - plate["rule_slot_width_mm"] for a, b in zip(style["horizontal_slot_y_mm"], style["horizontal_slot_y_mm"][1:])]
        assert min(gaps) >= minimum["production_ligament_mm"]
    assert len(styles[2]["icon_names"]) == 12 == len(set(styles[2]["icon_names"]))
    assert min(coupon["feature_sizes_mm"]) == minimum["coupon_only_minimum_mm"] < minimum["production_opening_mm"]
    assert 3 * plate["width_mm"] + coupon["width_mm"] + 50.0 <= printer["build_volume_mm"][0]
    assert plate["length_mm"] + 20.0 <= printer["build_volume_mm"][1]


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
    plate = parameters["plate"]
    mesh_p = parameters["mesh"]
    shapes: dict[str, cq.Shape] = {}
    interfaces: dict[str, dict] = {}
    for style in parameters["styles"]:
        shape, interface = make_layout_plate(parameters, style) if style["kind"] == "layout" else make_signal_plate(parameters, style)
        shapes[style["id"]] = shape
        interfaces[style["id"]] = interface
    coupon_shape, coupon_interface = make_coupon(parameters)
    shapes["minimum-feature-coupon"] = coupon_shape
    interfaces["minimum-feature-coupon"] = coupon_interface

    step_paths: list[Path] = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    assembly = cq.Compound.makeCompound([
        shapes["layout-5mm"],
        shapes["layout-4mm"].translate((50.0, 0.0, 0.0)),
        shapes["signal-12"].translate((100.0, 0.0, 0.0)),
        shapes["minimum-feature-coupon"].translate((150.0, 0.0, 0.0)),
    ])
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"
    export_step(assembly, assembly_path)
    step_paths.append(assembly_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("layout-5mm", "layout-4mm", "signal-12"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    coupon_path = COUPONS / f"DRAFT-{PROJECT_ID}-minimum-feature-coupon-{REVISION}.stl"
    export_stl(coupon_shape, coupon_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    mesh_paths["minimum-feature-coupon"] = coupon_path
    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-stencil-ruler-bookmark-set-{REVISION}.3mf"
    write_3mf(
        package_path,
        [(name, mesh_paths[name]) for name in ("layout-5mm", "layout-4mm", "signal-12", "minimum-feature-coupon")],
        [(10.0, 10.0), (60.0, 10.0), (110.0, 10.0), (160.0, 10.0)],
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

    parametric_checks = [
        check("parameter-validation", True, "Fail-closed parameter relations pass"),
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All four B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every deliverable is one B-Rep solid"),
        check("source-of-truth", len(parameters["styles"]) == 3, "JSON drives three independent production styles"),
        check("no-external-assets", not any(interfaces[name].get("external_assets") for name in interfaces), "Geometry uses no third-party vector, font or mesh assets"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", report(
        f"{PROJECT_ID}-parametric-source",
        [PARAMETERS, Path(__file__)],
        parametric_checks,
        {"python": platform.python_version(), "cadquery": cq.__version__, "parts": list(shapes), "plate_dimensions_mm": [plate["width_mm"], plate["length_mm"], plate["height_mm"]]},
        ["Any parameter or analytic icon-path change requires regeneration of downstream evidence."],
    ))
    write_json(VALIDATION / "mesh-generation-report.json", report(
        f"{PROJECT_ID}-mesh-generation",
        [PARAMETERS, Path(__file__)],
        mesh_checks,
        {"meshes": metrics},
        ["Topology does not prove paper safety, ink behavior, trace quality, flexural life or dimensional accuracy."],
    ))

    minimum = parameters["minimum_features"]
    interface_checks = [
        check("three-production-plates", len(parameters["styles"]) == 3, "Three production plates are generated"),
        check("native-grid-pitches", [style["grid_pitch_mm"] for style in parameters["styles"][:2]] == [5.0, 4.0], "Independent 5 mm and 4 mm systems are present"),
        check("registration-length", plate["registration_length_mm"] == 120.0, "Both grid plates cover a 120 mm registration run"),
        check("production-openings", plate["registration_hole_diameter_mm"] >= minimum["production_opening_mm"] and plate["rule_slot_width_mm"] >= minimum["production_opening_mm"], "Production holes and rule slots meet the minimum opening"),
        check("paper-boundary", plate["registration_x_mm"] - plate["registration_hole_diameter_mm"] / 2.0 >= minimum["paper_edge_boundary_mm"], "Registration holes preserve the paper-edge boundary"),
        check("signal-count", len(interfaces["signal-12"]["icons"]) == 12, "Twelve named analytic signal silhouettes are present"),
        check("identity-codes", [style["identity_holes"] for style in parameters["styles"]] == [1, 2, 3], "One/two/three-hole codes distinguish the plates without fonts"),
        check("coupon-sweep", coupon_interface["slot_widths_mm"] == [0.8, 1.0, 1.2, 1.4, 1.6], "Coupon sweeps five slot and round-opening sizes"),
        check("clip-free", True, "No page clip or paper-pinching interface is generated"),
    ]
    write_json(VALIDATION / "interface-report.json", report(
        f"{PROJECT_ID}-interface-validation",
        [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
        interface_checks,
        {"plate": {"outer_dimensions_mm": [plate["width_mm"], plate["length_mm"], plate["height_mm"]], "minimum_features": minimum}, "interfaces": interfaces},
        ["Feature rules are digital design minima, not a validated pen/process capability claim."],
    ))

    production_volume = sum(float(shapes[name].Volume()) for name in ("layout-5mm", "layout-4mm", "signal-12"))
    baseline_volume = 3.0 * plate["width_mm"] * plate["length_mm"] * plate["height_mm"]
    reduction = 100.0 * (1.0 - production_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0",
        "project": PROJECT_ID,
        "revision": REVISION,
        "baseline": {"description": "three solid rounded-envelope bounding plates", "volume_mm3": baseline_volume},
        "candidate": {"description": "three useful stencil plates", "volume_mm3": production_volume},
        "volume_reduction_percent": reduction,
        "selection_threshold_percent": 8.0,
        "status": "PASS" if reduction >= 8.0 else "FAIL",
        "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE",
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {
        "schema_version": "1.0",
        "project": PROJECT_ID,
        "revision": REVISION,
        "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL",
        "meshes": metrics,
        "simplification": "NOT_BENEFICIAL",
        "reason": "Analytic tessellation is under budget; decimation could move stencil apertures or paper boundaries.",
    })
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0",
        "project": PROJECT_ID,
        "revision": REVISION,
        "status": "PASS",
        "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))],
        "outputs": [input_record(path) for path in outputs],
        "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]],
    })
    if any(value["status"] != "PASS" for value in [
        json.loads((VALIDATION / "parametric-source-report.json").read_text()),
        json.loads((VALIDATION / "mesh-generation-report.json").read_text()),
        json.loads((VALIDATION / "interface-report.json").read_text()),
        optimization,
    ]):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "outputs": [str(path.relative_to(ROOT)) for path in mesh_paths.values()] + [str(package_path.relative_to(ROOT))]}, indent=2))


if __name__ == "__main__":
    main()
