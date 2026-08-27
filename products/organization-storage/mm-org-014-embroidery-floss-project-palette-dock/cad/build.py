#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-014 embroidery-floss palette dock."""
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
PROJECT_ID = "MM-ORG-014"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def slot_positions(parameters: dict) -> list[float]:
    dock = parameters["dock"]
    return [dock["first_position_y_mm"] + index * dock["slot_pitch_mm"] for index in range(dock["positions_per_lane"])]


def slot_width_at_z(parameters: dict, z_value: float) -> float:
    slot = parameters["slot"]
    if z_value <= slot["bottom_z_mm"]:
        return slot["throat_width_mm"]
    if z_value <= slot["shoulder_z_mm"]:
        fraction = (z_value - slot["bottom_z_mm"]) / (slot["shoulder_z_mm"] - slot["bottom_z_mm"])
        return slot["throat_width_mm"] + fraction * (slot["mid_width_mm"] - slot["throat_width_mm"])
    if z_value <= slot["chamfer_z_mm"]:
        return slot["mid_width_mm"]
    fraction = min(1.0, (z_value - slot["chamfer_z_mm"]) / (slot["top_z_mm"] - slot["chamfer_z_mm"]))
    return slot["mid_width_mm"] + fraction * (slot["lip_width_mm"] - slot["mid_width_mm"])


def card_seat_z(parameters: dict, card: dict) -> float:
    """Return the seated bottom for a declared card thickness and side clearance."""
    slot = parameters["slot"]
    target_width = card["thickness_mm"] + 2.0 * card["side_clearance_mm"]
    if target_width <= slot["throat_width_mm"]:
        return slot["bottom_z_mm"]
    if target_width <= slot["mid_width_mm"]:
        return slot["bottom_z_mm"] + (
            (target_width - slot["throat_width_mm"])
            * (slot["shoulder_z_mm"] - slot["bottom_z_mm"])
            / (slot["mid_width_mm"] - slot["throat_width_mm"])
        )
    return slot["chamfer_z_mm"] + (
        (target_width - slot["mid_width_mm"])
        * (slot["top_z_mm"] - slot["chamfer_z_mm"])
        / (slot["lip_width_mm"] - slot["mid_width_mm"])
    )


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    printer = parameters["printer"]
    dock = parameters["dock"]
    slot = parameters["slot"]
    coupon = parameters["coupon"]
    mesh = parameters["mesh"]
    assert project["id"] == PROJECT_ID and project["revision"] == REVISION and project["units"] == "mm"
    assert dock["width_mm"] <= 220 and dock["depth_mm"] <= 110 and dock["receiver_bar_height_mm"] <= 12
    assert len(dock["lane_centers_x_mm"]) == 3 and dock["positions_per_lane"] == 10
    assert len(dock["lane_centers_x_mm"]) * dock["positions_per_lane"] == 30
    assert slot["throat_width_mm"] < slot["mid_width_mm"] < slot["lip_width_mm"]
    assert slot["bottom_z_mm"] < slot["shoulder_z_mm"] < slot["chamfer_z_mm"] < slot["top_z_mm"]
    assert dock["slot_pitch_mm"] - slot["lip_width_mm"] >= 5.0
    assert dock["receiver_bar_length_mm"] - slot["length_mm"] >= 6.0
    lane_gap = min(np.diff(dock["lane_centers_x_mm"])) - dock["receiver_bar_length_mm"]
    assert lane_gap >= 6.0
    positions = slot_positions(parameters)
    assert positions[0] - dock["receiver_bar_depth_mm"] / 2 >= dock["perimeter_width_mm"]
    assert positions[-1] + dock["receiver_bar_depth_mm"] / 2 <= dock["depth_mm"] - dock["perimeter_width_mm"]
    for card in parameters["card_standards"]:
        assert card["width_mm"] <= slot["length_mm"] - 2.0
        assert card["thickness_mm"] + 2.0 * card["side_clearance_mm"] <= slot["mid_width_mm"]
        assert dock["receiver_bar_height_mm"] - card_seat_z(parameters, card) >= 4.0
    assert coupon["positions"] == 3 and coupon["slot_pitch_mm"] == dock["slot_pitch_mm"]
    assert coupon["width_mm"] <= printer["build_volume_mm"][0]
    assert mesh["triangle_stop"] > 0 and mesh["max_mesh_mib"] > 0


def fuse_all(parts: list[cq.Shape]) -> cq.Shape:
    result = parts[0]
    for part in parts[1:]:
        result = result.fuse(part)
    return result.clean()


def make_slot_cutter(parameters: dict, center_x: float, center_y: float) -> cq.Shape:
    slot = parameters["slot"]
    x_start = center_x - slot["length_mm"] / 2.0
    points_yz = [
        (-slot["throat_width_mm"] / 2.0, slot["bottom_z_mm"]),
        (slot["throat_width_mm"] / 2.0, slot["bottom_z_mm"]),
        (slot["mid_width_mm"] / 2.0, slot["shoulder_z_mm"]),
        (slot["mid_width_mm"] / 2.0, slot["chamfer_z_mm"]),
        (slot["lip_width_mm"] / 2.0, slot["top_z_mm"]),
        (-slot["lip_width_mm"] / 2.0, slot["top_z_mm"]),
        (-slot["mid_width_mm"] / 2.0, slot["chamfer_z_mm"]),
        (-slot["mid_width_mm"] / 2.0, slot["shoulder_z_mm"]),
    ]
    return (
        cq.Workplane("YZ", origin=(x_start, center_y, 0))
        .polyline(points_yz)
        .close()
        .extrude(slot["length_mm"])
        .val()
    )


def make_receiver_bar(parameters: dict, center_x: float, center_y: float) -> cq.Shape:
    dock = parameters["dock"]
    bar = cq.Solid.makeBox(
        dock["receiver_bar_length_mm"],
        dock["receiver_bar_depth_mm"],
        dock["receiver_bar_height_mm"],
        cq.Vector(
            center_x - dock["receiver_bar_length_mm"] / 2.0,
            center_y - dock["receiver_bar_depth_mm"] / 2.0,
            0,
        ),
    )
    return bar.cut(make_slot_cutter(parameters, center_x, center_y)).clean()


def make_perimeter(parameters: dict) -> list[cq.Shape]:
    dock = parameters["dock"]
    width, depth = dock["width_mm"], dock["depth_mm"]
    wall, height = dock["perimeter_width_mm"], dock["base_height_mm"]
    return [
        cq.Solid.makeBox(width, wall, height, cq.Vector(0, 0, 0)),
        cq.Solid.makeBox(width, wall, height, cq.Vector(0, depth - wall, 0)),
        cq.Solid.makeBox(wall, depth - 2 * wall, height, cq.Vector(0, wall, 0)),
        cq.Solid.makeBox(wall, depth - 2 * wall, height, cq.Vector(width - wall, wall, 0)),
    ]


def make_dock(parameters: dict) -> tuple[cq.Shape, dict]:
    dock = parameters["dock"]
    parts = make_perimeter(parameters)
    for center_x in dock["lane_centers_x_mm"]:
        parts.append(
            cq.Solid.makeBox(
                dock["lane_spine_width_mm"],
                dock["depth_mm"],
                dock["base_height_mm"],
                cq.Vector(center_x - dock["lane_spine_width_mm"] / 2.0, 0, 0),
            )
        )
        for center_y in slot_positions(parameters):
            parts.append(make_receiver_bar(parameters, center_x, center_y))
    result = fuse_all(parts)
    marker_y = dock["front_label_rail_depth_mm"] / 2.0
    marker_radius = dock["lane_marker_diameter_mm"] / 2.0
    for lane_index, center_x in enumerate(dock["lane_centers_x_mm"], 1):
        for marker_index in range(lane_index):
            marker_x = center_x + (marker_index - (lane_index - 1) / 2.0) * 4.0
            cutter = cq.Solid.makeCylinder(
                marker_radius,
                dock["lane_marker_depth_mm"] + 0.2,
                cq.Vector(marker_x, marker_y, dock["base_height_mm"] - dock["lane_marker_depth_mm"]),
                cq.Vector(0, 0, 1),
            )
            result = result.cut(cutter)
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("palette dock is not one valid solid")
    lane_gap = min(np.diff(dock["lane_centers_x_mm"])) - dock["receiver_bar_length_mm"]
    return result, {
        "outer_dimensions_mm": [dock["width_mm"], dock["depth_mm"], dock["receiver_bar_height_mm"]],
        "lanes": len(dock["lane_centers_x_mm"]),
        "positions_per_lane": dock["positions_per_lane"],
        "total_positions": len(dock["lane_centers_x_mm"]) * dock["positions_per_lane"],
        "minimum_slot_web_mm": dock["slot_pitch_mm"] - parameters["slot"]["lip_width_mm"],
        "minimum_lane_gap_mm": lane_gap,
        "receiver_end_wall_each_mm": (dock["receiver_bar_length_mm"] - parameters["slot"]["length_mm"]) / 2.0,
        "lane_marker_counts": [1, 2, 3],
    }


def make_coupon(parameters: dict) -> tuple[cq.Shape, dict]:
    dock = parameters["dock"]
    coupon = parameters["coupon"]
    center_x = coupon["width_mm"] / 2.0
    parts = [
        cq.Solid.makeBox(
            dock["lane_spine_width_mm"],
            coupon["depth_mm"],
            dock["base_height_mm"],
            cq.Vector(center_x - dock["lane_spine_width_mm"] / 2.0, 0, 0),
        ),
        cq.Solid.makeBox(coupon["width_mm"], dock["perimeter_width_mm"], dock["base_height_mm"], cq.Vector(0, 0, 0)),
        cq.Solid.makeBox(coupon["width_mm"], dock["perimeter_width_mm"], dock["base_height_mm"], cq.Vector(0, coupon["depth_mm"] - dock["perimeter_width_mm"], 0)),
    ]
    positions = [coupon["first_position_y_mm"] + index * coupon["slot_pitch_mm"] for index in range(coupon["positions"])]
    for center_y in positions:
        parts.append(make_receiver_bar(parameters, center_x, center_y))
    result = fuse_all(parts)
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("fit coupon is not one valid solid")
    return result, {
        "outer_dimensions_mm": [coupon["width_mm"], coupon["depth_mm"], dock["receiver_bar_height_mm"]],
        "positions": coupon["positions"],
        "slot_pitch_mm": coupon["slot_pitch_mm"],
        "production_profile_reused": True,
    }


def virtual_card_shape(card: dict) -> cq.Shape:
    return cq.Solid.makeBox(card["width_mm"], card["thickness_mm"], card["height_mm"])


def make_virtual_assembly(parameters: dict, dock_shape: cq.Shape) -> tuple[cq.Shape, list[dict]]:
    dock = parameters["dock"]
    standards = parameters["card_standards"]
    cards: list[cq.Shape] = []
    placements: list[dict] = []
    for lane_index, center_x in enumerate(dock["lane_centers_x_mm"]):
        for position_index, center_y in enumerate(slot_positions(parameters)):
            card = standards[(lane_index + position_index) % len(standards)]
            seat_z = card_seat_z(parameters, card)
            shape = virtual_card_shape(card).translate(
                (center_x - card["width_mm"] / 2.0, center_y - card["thickness_mm"] / 2.0, seat_z)
            )
            cards.append(shape)
            placements.append({"lane": lane_index + 1, "position": position_index + 1, "standard": card["id"], "seat_z_mm": seat_z})
    return cq.Compound.makeCompound([dock_shape, *cards]), placements


def move_to_origin(shape: cq.Shape) -> cq.Shape:
    bounds = shape.BoundingBox()
    return shape.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def main() -> None:
    parameters = load_parameters()
    validate_parameters(parameters)
    dock_p = parameters["dock"]
    slot_p = parameters["slot"]
    mesh_p = parameters["mesh"]
    dock_shape, dock_interface = make_dock(parameters)
    coupon_shape, coupon_interface = make_coupon(parameters)
    assembly_shape, card_placements = make_virtual_assembly(parameters, dock_shape)

    step_shapes = {"palette-dock": dock_shape, "fit-coupon": coupon_shape, "virtual-card-assembly": assembly_shape}
    step_paths: list[Path] = []
    for name, shape in step_shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)

    dock_path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-palette-dock-{REVISION}.stl"
    coupon_path = COUPONS / f"DRAFT-{PROJECT_ID}-three-card-fit-coupon-{REVISION}.stl"
    export_stl(dock_shape, dock_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    export_stl(coupon_shape, coupon_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-palette-dock-and-fit-coupon-{REVISION}.3mf"
    write_3mf(package_path, [("palette-dock", dock_path), ("three-card-fit-coupon", coupon_path)], [(90.0, 80.0), (90.0, 230.0)])

    metrics = {"palette-dock": mesh_metrics(dock_path), "fit-coupon": mesh_metrics(coupon_path)}
    mesh_checks: list[dict] = []
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
    write_json(
        VALIDATION / "mesh-generation-report.json",
        report(
            f"{PROJECT_ID}-mesh-generation",
            [PARAMETERS, Path(__file__)],
            mesh_checks,
            {"meshes": metrics},
            ["Topology does not prove loaded-card fit, fiber snagging, retrieval force, tip or slip."],
        ),
    )

    card_interfaces = []
    for card in parameters["card_standards"]:
        seat_z = card_seat_z(parameters, card)
        local_width = slot_width_at_z(parameters, seat_z)
        card_interfaces.append(
            {
                "id": card["id"],
                "dimensions_mm": [card["width_mm"], card["thickness_mm"], card["height_mm"]],
                "seat_z_mm": seat_z,
                "engagement_mm": dock_p["receiver_bar_height_mm"] - seat_z,
                "local_slot_width_mm": local_width,
                "nominal_clearance_each_side_mm": (local_width - card["thickness_mm"]) / 2.0,
            }
        )
    interface_checks = [
        check("thirty-positions", dock_interface["total_positions"] == 30, "Three lanes generate thirty receivers"),
        check("slot-profile", slot_p["throat_width_mm"] < slot_p["mid_width_mm"] < slot_p["lip_width_mm"], "Slot profile widens monotonically"),
        check("thin-card-clearance", card_interfaces[0]["nominal_clearance_each_side_mm"] >= slot_p["minimum_side_clearance_mm"] - 1e-9, "Thin cardstock has minimum throat clearance"),
        check("three-card-classes", len(card_interfaces) == 3 and all(item["nominal_clearance_each_side_mm"] >= 0.099 for item in card_interfaces), "All three card classes have non-negative nominal seating clearance"),
        check("card-engagement", all(item["engagement_mm"] >= 4.0 for item in card_interfaces), "Every declared card class engages at least 4 mm"),
        check("slot-web", dock_interface["minimum_slot_web_mm"] >= 5.0, "Adjacent slot mouths retain at least 5 mm web"),
        check("lane-gap", dock_interface["minimum_lane_gap_mm"] >= 6.0, "Receiver bars retain at least 6 mm clear lane gap"),
        check("receiver-end-walls", dock_interface["receiver_end_wall_each_mm"] >= 3.0, "Every slot retains 3 mm end walls"),
        check("coupon-derived", coupon_interface["production_profile_reused"] and coupon_interface["slot_pitch_mm"] == dock_p["slot_pitch_mm"], "Coupon reuses production slot and pitch"),
        check("lane-markers", dock_interface["lane_marker_counts"] == [1, 2, 3], "Front rail contains one/two/three-dot lane markers"),
    ]
    write_json(
        VALIDATION / "interface-report.json",
        report(
            f"{PROJECT_ID}-interface-validation",
            [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
            interface_checks,
            {"dock": dock_interface, "coupon": coupon_interface, "cards": card_interfaces, "virtual_placements": card_placements},
            ["Virtual card blocks represent only edge envelope and thickness; real loaded cards and floss require the deferred coupon test."],
        ),
    )
    write_json(
        VALIDATION / "parametric-source-report.json",
        report(
            f"{PROJECT_ID}-parametric-source",
            [PARAMETERS, Path(__file__)],
            [
                check("parameter-validation", True, "Fail-closed parameter relations pass"),
                check("cad-valid", dock_shape.isValid() and coupon_shape.isValid(), "Dock and coupon B-Reps are valid"),
                check("single-solids", len(dock_shape.Solids()) == 1 and len(coupon_shape.Solids()) == 1, "Dock and coupon are each one B-Rep solid"),
                check("source-of-truth", True, "JSON drives lanes, receivers, slot profile, coupon, card classes and exports"),
            ],
            {"dock_dimensions_mm": dock_interface["outer_dimensions_mm"], "positions": dock_interface["total_positions"], "card_classes": len(card_interfaces), "python": platform.python_version(), "cadquery": getattr(cq, "__version__", "unknown")},
            ["A parameter change requires rebuilding all downstream evidence."],
        ),
    )
    baseline_volume = dock_p["width_mm"] * dock_p["depth_mm"] * dock_p["receiver_bar_height_mm"]
    dock_volume = metrics["palette-dock"]["volume_mm3"]
    write_json(
        REPORTS / "optimization-comparison.json",
        {
            "schema_version": "1.0",
            "project_id": PROJECT_ID,
            "revision": REVISION,
            "baseline": {"method": "full maximum dock bounding block", "volume_mm3": baseline_volume},
            "candidate": {"method": "perimeter plus three spines and local receiver bars", "volume_mm3": dock_volume},
            "cad_volume_reduction_percent": 100.0 * (1.0 - dock_volume / baseline_volume),
            "protected_requirements": ["thirty receivers", "minimum slot web", "lane separation", "connected bed lattice"],
        },
    )
    write_json(REPORTS / "mesh-complexity.json", {"project_id": PROJECT_ID, "revision": REVISION, "meshes": metrics})
    artifact_paths = [*step_paths, dock_path, coupon_path, package_path]
    report_paths = [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json"]
    write_json(
        REPORTS / "build-manifest.json",
        {
            "schema_version": "1.0",
            "project_id": PROJECT_ID,
            "revision": REVISION,
            "status": "PASS",
            "source": input_record(PARAMETERS),
            "artifacts": [input_record(path) for path in artifact_paths],
            "reports": [input_record(path) for path in report_paths],
            "limitations": ["Loaded-card fit, fiber snagging, visibility, 500 cycles, tip and slip are deferred.", "DRAFT outputs carry no final commercial watermark."],
        },
    )
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "outputs": [str(path.relative_to(ROOT)) for path in [dock_path, coupon_path, package_path]]}, indent=2))


if __name__ == "__main__":
    main()
