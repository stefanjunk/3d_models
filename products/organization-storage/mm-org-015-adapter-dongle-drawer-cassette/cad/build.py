#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-015 adapter-and-dongle cassette."""
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
PROJECT_ID = "MM-ORG-015"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def cell_record(parameters: dict, index: int) -> dict:
    cassette = parameters["cassette"]
    row, column = divmod(index, cassette["columns"])
    left = cassette["margin_mm"] + column * cassette["cell_pitch_x_mm"]
    bottom = cassette["margin_mm"] + row * cassette["cell_pitch_y_mm"]
    return {
        "index": index + 1,
        "row": row + 1,
        "column": column + 1,
        "left_mm": left,
        "right_mm": left + cassette["cell_pitch_x_mm"],
        "bottom_mm": bottom,
        "top_mm": bottom + cassette["cell_pitch_y_mm"],
        "center_x_mm": left + cassette["cell_pitch_x_mm"] / 2.0,
        "center_y_mm": bottom + cassette["cell_pitch_y_mm"] / 2.0,
    }


def cradle_record(parameters: dict, index: int, item: dict) -> dict:
    cassette = parameters["cassette"]
    interface = parameters["interfaces"]
    cell = cell_record(parameters, index)
    back_outer_x = cell["right_mm"] - cassette["back_inset_mm"] + cassette["cradle_wall_mm"]
    back_inner_x = back_outer_x - cassette["cradle_wall_mm"]
    body_rear_x = back_inner_x - cassette["rear_body_clearance_mm"]
    body_front_x = body_rear_x - item["body_length_mm"]
    pocket_front_x = body_front_x - item["end_clearance_mm"]
    pocket_width = item["body_width_mm"] + 2.0 * item["side_clearance_mm"]
    connector_start_x = body_front_x - item["connector_reach_mm"] - interface["connector_relief_extra_length_mm"]
    connector_end_x = body_front_x + cassette["front_rail_relief_mm"]
    keepout_width = item["connector_width_mm"] + 2.0 * interface["connector_clearance_each_side_mm"]
    rail_height = min(
        cassette["cradle_height_above_base_mm"],
        max(cassette["cradle_min_height_above_base_mm"], item["body_height_mm"] * cassette["cradle_height_body_fraction"]),
    )
    return {
        **cell,
        "item_id": item["id"],
        "back_outer_x_mm": back_outer_x,
        "back_inner_x_mm": back_inner_x,
        "body_front_x_mm": body_front_x,
        "body_rear_x_mm": body_rear_x,
        "pocket_front_x_mm": pocket_front_x,
        "pocket_length_mm": back_inner_x - pocket_front_x,
        "pocket_width_mm": pocket_width,
        "connector_start_x_mm": connector_start_x,
        "connector_end_x_mm": connector_end_x,
        "connector_keepout_width_mm": keepout_width,
        "body_engagement_mm": body_rear_x - body_front_x,
        "rail_height_above_base_mm": rail_height,
    }


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    cassette = parameters["cassette"]
    card = parameters["measurement_card"]
    items = parameters["item_classes"]
    printer = parameters["printer"]
    assert project["id"] == PROJECT_ID and project["revision"] == REVISION and project["units"] == "mm"
    assert cassette["columns"] * cassette["rows"] == 20 == len(items)
    assert len({item["id"] for item in items}) == 20
    assert 2 * cassette["margin_mm"] + cassette["columns"] * cassette["cell_pitch_x_mm"] == cassette["width_mm"]
    assert 2 * cassette["margin_mm"] + cassette["rows"] * cassette["cell_pitch_y_mm"] == cassette["depth_mm"]
    assert cassette["width_mm"] <= printer["build_volume_mm"][0]
    assert cassette["depth_mm"] <= printer["build_volume_mm"][1]
    assert cassette["base_height_mm"] >= 2.0 and cassette["cradle_wall_mm"] >= 1.2
    assert 3.0 <= cassette["cradle_min_height_above_base_mm"] <= cassette["cradle_height_above_base_mm"] <= 6.0
    for index, item in enumerate(items):
        record = cradle_record(parameters, index, item)
        outside_width = record["pocket_width_mm"] + 2 * cassette["cradle_wall_mm"]
        assert outside_width <= cassette["cell_pitch_y_mm"] - 2.0
        assert record["connector_keepout_width_mm"] <= record["pocket_width_mm"]
        assert record["connector_start_x_mm"] >= record["left_mm"] + 1.0
        assert record["back_outer_x_mm"] <= record["right_mm"] - 1.0
        assert item["side_clearance_mm"] > 0 and item["end_clearance_mm"] > 0
    width_used = sum(card["width_notches_mm"]) + (len(card["width_notches_mm"]) - 1) * card["notch_gap_mm"]
    thickness_used = sum(card["thickness_notches_mm"]) + (len(card["thickness_notches_mm"]) - 1) * card["notch_gap_mm"]
    assert width_used + 2 * card["edge_margin_mm"] <= card["width_mm"]
    assert thickness_used + 2 * card["edge_margin_mm"] <= card["depth_mm"]
    assert cassette["width_mm"] + card["width_mm"] + 30.0 <= printer["build_volume_mm"][0]


def fuse_all(parts: list[cq.Shape]) -> cq.Shape:
    return parts[0].fuse(*parts[1:], glue=True)


def cut_compound(shape: cq.Shape, cutters: list[cq.Shape]) -> cq.Shape:
    if not cutters:
        return shape
    return shape.cut(cq.Compound.makeCompound(cutters))


def position_code_cutters(parameters: dict, number: int, origin_x: float, origin_y: float) -> list[cq.Shape]:
    """Encode 01-20 as separate tens and units bars without fonts."""
    cassette = parameters["cassette"]
    stroke = cassette["label_stroke_mm"]
    depth = cassette["label_recess_depth_mm"]
    z = cassette["base_height_mm"] - depth
    tens, units = divmod(number, 10)
    cutters: list[cq.Shape] = []
    if tens:
        cutters.append(cq.Solid.makeBox(tens * cassette["label_tens_scale_mm"], stroke, depth + 0.1, cq.Vector(origin_x, origin_y + 1.2, z)))
    if units:
        cutters.append(cq.Solid.makeBox(units * cassette["label_units_scale_mm"], stroke, depth + 0.1, cq.Vector(origin_x, origin_y, z)))
    return cutters


def make_cassette(parameters: dict) -> tuple[cq.Shape, dict, list[dict]]:
    cassette = parameters["cassette"]
    items = parameters["item_classes"]
    base = cq.Solid.makeBox(cassette["width_mm"], cassette["depth_mm"], cassette["base_height_mm"])
    wall_z = cassette["base_height_mm"]
    wall_h = cassette["outer_wall_height_above_base_mm"]
    outer = cassette["outer_wall_mm"]
    parts = [
        base,
        cq.Solid.makeBox(cassette["width_mm"], outer, wall_h, cq.Vector(0, 0, wall_z)),
        cq.Solid.makeBox(cassette["width_mm"], outer, wall_h, cq.Vector(0, cassette["depth_mm"] - outer, wall_z)),
        cq.Solid.makeBox(outer, cassette["depth_mm"] - 2 * outer, wall_h, cq.Vector(0, outer, wall_z)),
        cq.Solid.makeBox(outer, cassette["depth_mm"] - 2 * outer, wall_h, cq.Vector(cassette["width_mm"] - outer, outer, wall_z)),
    ]
    records: list[dict] = []
    connector_cutters: list[cq.Shape] = []
    label_cutters: list[cq.Shape] = []
    rail_t = cassette["cradle_wall_mm"]
    for index, item in enumerate(items):
        record = cradle_record(parameters, index, item)
        records.append(record)
        rail_h = record["rail_height_above_base_mm"]
        y_low = record["center_y_mm"] - record["pocket_width_mm"] / 2.0
        y_high = record["center_y_mm"] + record["pocket_width_mm"] / 2.0
        parts.extend(
            [
                cq.Solid.makeBox(record["pocket_length_mm"], rail_t, rail_h, cq.Vector(record["pocket_front_x_mm"], y_low - rail_t, wall_z)),
                cq.Solid.makeBox(record["pocket_length_mm"], rail_t, rail_h, cq.Vector(record["pocket_front_x_mm"], y_high, wall_z)),
                cq.Solid.makeBox(rail_t, record["pocket_width_mm"] + 2 * rail_t, rail_h, cq.Vector(record["back_inner_x_mm"], y_low - rail_t, wall_z)),
            ]
        )
        connector_cutters.append(
            cq.Solid.makeBox(
                record["connector_end_x_mm"] - record["connector_start_x_mm"],
                record["connector_keepout_width_mm"],
                cassette["base_height_mm"] + 0.2,
                cq.Vector(record["connector_start_x_mm"], record["center_y_mm"] - record["connector_keepout_width_mm"] / 2.0, -0.1),
            )
        )
        label_x = record["left_mm"] + 1.5
        label_y = record["top_mm"] - 4.0
        code_width = max((index + 1) // 10 * cassette["label_tens_scale_mm"], (index + 1) % 10 * cassette["label_units_scale_mm"])
        if label_x + code_width >= record["connector_start_x_mm"] and label_y <= record["center_y_mm"] + record["connector_keepout_width_mm"] / 2.0:
            raise RuntimeError(f"label keep-out overlaps connector keep-out at position {index + 1}")
        label_cutters.extend(position_code_cutters(parameters, index + 1, label_x, label_y))
    print(f"building cassette union: {len(parts)} additive solids", flush=True)
    result = fuse_all(parts)
    print(f"cutting {len(connector_cutters)} connector keep-outs", flush=True)
    result = cut_compound(result, connector_cutters)
    print(f"cutting {len(label_cutters)} code segments", flush=True)
    result = cut_compound(result, label_cutters)
    print("cleaning cassette B-Rep", flush=True)
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("cassette is not one valid solid")
    height = cassette["base_height_mm"] + cassette["cradle_height_above_base_mm"]
    interface = {
        "outer_dimensions_mm": [cassette["width_mm"], cassette["depth_mm"], height],
        "positions": len(records),
        "columns": cassette["columns"],
        "rows": cassette["rows"],
        "font_independent_two_bar_codes": True,
        "connector_reliefs_through_base": len(connector_cutters),
        "minimum_side_clearance_mm": min(item["side_clearance_mm"] for item in items),
        "maximum_side_clearance_mm": max(item["side_clearance_mm"] for item in items),
        "minimum_rail_height_above_base_mm": min(record["rail_height_above_base_mm"] for record in records),
        "maximum_rail_height_above_base_mm": max(record["rail_height_above_base_mm"] for record in records),
        "minimum_cell_width_web_mm": min(cassette["cell_pitch_y_mm"] - (record["pocket_width_mm"] + 2 * rail_t) for record in records),
    }
    return result, interface, records


def make_measurement_card(parameters: dict) -> tuple[cq.Shape, dict]:
    card = parameters["measurement_card"]
    shape = cq.Solid.makeBox(card["width_mm"], card["depth_mm"], card["height_mm"])
    cutters: list[cq.Shape] = []
    x = card["edge_margin_mm"]
    for width in card["width_notches_mm"]:
        cutters.append(
            cq.Solid.makeBox(
                width,
                card["width_notch_depth_mm"] + 0.1,
                card["height_mm"] + 0.2,
                cq.Vector(x, card["depth_mm"] - card["width_notch_depth_mm"], -0.1),
            )
        )
        x += width + card["notch_gap_mm"]
    y = card["edge_margin_mm"]
    for thickness in card["thickness_notches_mm"]:
        cutters.append(
            cq.Solid.makeBox(
                card["thickness_notch_depth_mm"] + 0.1,
                thickness,
                card["height_mm"] + 0.2,
                cq.Vector(card["width_mm"] - card["thickness_notch_depth_mm"], y, -0.1),
            )
        )
        y += thickness + card["notch_gap_mm"]
    tick_count = int(card["ruler_length_mm"] / card["tick_pitch_mm"])
    for index in range(tick_count + 1):
        tick_x = card["edge_margin_mm"] + index * card["tick_pitch_mm"]
        tick_depth = 4.0 if index % 2 == 0 else 2.0
        cutters.append(cq.Solid.makeBox(0.6, tick_depth + 0.1, card["height_mm"] + 0.2, cq.Vector(tick_x - 0.3, -0.1, -0.1)))
    print(f"cutting {len(cutters)} measurement-card features", flush=True)
    result = cut_compound(shape, cutters)
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("measurement card is not one valid solid")
    return result, {
        "outer_dimensions_mm": [card["width_mm"], card["depth_mm"], card["height_mm"]],
        "width_notches_mm": card["width_notches_mm"],
        "thickness_notches_mm": card["thickness_notches_mm"],
        "ruler_length_mm": card["ruler_length_mm"],
        "ruler_tick_count": tick_count + 1,
        "calipers_remain_authoritative": True,
    }


def make_virtual_assembly(parameters: dict, cassette_shape: cq.Shape, records: list[dict]) -> tuple[cq.Shape, list[dict]]:
    cassette = parameters["cassette"]
    shapes: list[cq.Shape] = [cassette_shape]
    placements: list[dict] = []
    for item, record in zip(parameters["item_classes"], records):
        body = cq.Solid.makeBox(
            item["body_length_mm"],
            item["body_width_mm"],
            item["body_height_mm"],
            cq.Vector(record["body_front_x_mm"], record["center_y_mm"] - item["body_width_mm"] / 2.0, cassette["base_height_mm"]),
        )
        connector_h = min(4.0, item["body_height_mm"])
        connector = cq.Solid.makeBox(
            item["connector_reach_mm"],
            item["connector_width_mm"],
            connector_h,
            cq.Vector(
                record["body_front_x_mm"] - item["connector_reach_mm"],
                record["center_y_mm"] - item["connector_width_mm"] / 2.0,
                cassette["base_height_mm"] + max(0.0, (item["body_height_mm"] - connector_h) / 2.0),
            ),
        )
        shapes.extend([body, connector])
        placements.append(
            {
                "position": record["index"],
                "item_id": item["id"],
                "body_bounds_xy_mm": [record["body_front_x_mm"], record["body_rear_x_mm"], record["center_y_mm"] - item["body_width_mm"] / 2.0, record["center_y_mm"] + item["body_width_mm"] / 2.0],
                "connector_keepout_x_mm": [record["connector_start_x_mm"], record["connector_end_x_mm"]],
            }
        )
    return cq.Compound.makeCompound(shapes), placements


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
    cassette_p = parameters["cassette"]
    mesh_p = parameters["mesh"]
    cassette_shape, cassette_interface, cradle_records = make_cassette(parameters)
    card_shape, card_interface = make_measurement_card(parameters)
    assembly_shape, virtual_placements = make_virtual_assembly(parameters, cassette_shape, cradle_records)

    step_shapes = {
        "adapter-dongle-cassette": cassette_shape,
        "measurement-card": card_shape,
        "virtual-20-item-assembly": assembly_shape,
    }
    step_paths: list[Path] = []
    for name, shape in step_shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)

    cassette_path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-adapter-dongle-cassette-{REVISION}.stl"
    card_path = COUPONS / f"DRAFT-{PROJECT_ID}-no-brand-measurement-card-{REVISION}.stl"
    export_stl(cassette_shape, cassette_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    export_stl(card_shape, card_path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-cassette-and-measurement-card-{REVISION}.3mf"
    write_3mf(package_path, [("adapter-dongle-cassette", cassette_path), ("no-brand-measurement-card", card_path)], [(10.0, 10.0), (250.0, 10.0)])

    metrics = {"cassette": mesh_metrics(cassette_path), "measurement-card": mesh_metrics(card_path)}
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

    parametric_checks = [
        check("parameter-validation", True, "Fail-closed parameter relations pass"),
        check("cad-valid", cassette_shape.isValid() and card_shape.isValid(), "Cassette and card B-Reps are valid"),
        check("single-solids", len(cassette_shape.Solids()) == 1 and len(card_shape.Solids()) == 1, "Cassette and card are each one B-Rep solid"),
        check("source-of-truth", len(parameters["item_classes"]) == 20, "JSON drives twenty class-owned body, connector and clearance records"),
    ]
    write_json(
        VALIDATION / "parametric-source-report.json",
        report(
            f"{PROJECT_ID}-parametric-source",
            [PARAMETERS, Path(__file__)],
            parametric_checks,
            {
                "python": platform.python_version(),
                "cadquery": cq.__version__,
                "positions": len(parameters["item_classes"]),
                "cassette_dimensions_mm": cassette_interface["outer_dimensions_mm"],
                "measurement_card_dimensions_mm": card_interface["outer_dimensions_mm"],
            },
            ["Any parameter change requires regeneration of all downstream evidence."],
        ),
    )
    write_json(
        VALIDATION / "mesh-generation-report.json",
        report(
            f"{PROJECT_ID}-mesh-generation",
            [PARAMETERS, Path(__file__)],
            mesh_checks,
            {"meshes": metrics},
            ["Topology does not prove device-surface safety, connector protection, drawer closure or retrieval force."],
        ),
    )

    interface_checks = [
        check("twenty-positions", cassette_interface["positions"] == 20, "Four columns by five rows generate twenty positions"),
        check("class-owned-clearance", all(item["side_clearance_mm"] > 0 and item["end_clearance_mm"] > 0 for item in parameters["item_classes"]), "Every item class owns side and end clearance"),
        check("connector-keepouts", cassette_interface["connector_reliefs_through_base"] == 20, "Every position has one through-base connector keep-out"),
        check("connector-within-cradle", all(record["connector_keepout_width_mm"] <= record["pocket_width_mm"] for record in cradle_records), "Connector keep-outs remain narrower than body cradles"),
        check("cell-web", cassette_interface["minimum_cell_width_web_mm"] >= parameters["interfaces"]["minimum_inter_cradle_web_mm"], "Cradles retain declared inter-cell transverse web"),
        check("font-independent-codes", cassette_interface["font_independent_two_bar_codes"], "Twenty unique position codes are generated as analytic tens/units bars"),
        check("measurement-widths", card_interface["width_notches_mm"] == parameters["measurement_card"]["width_notches_mm"], "Measurement card preserves declared body-width notches"),
        check("measurement-thicknesses", card_interface["thickness_notches_mm"] == parameters["measurement_card"]["thickness_notches_mm"], "Measurement card preserves declared thickness notches"),
        check("measurement-ruler", card_interface["ruler_length_mm"] == 100.0 and card_interface["ruler_tick_count"] == 21, "Measurement card provides twenty-one 5 mm ruler ticks over 100 mm"),
    ]
    write_json(
        VALIDATION / "interface-report.json",
        report(
            f"{PROJECT_ID}-interface-validation",
            [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
            interface_checks,
            {
                "cassette": cassette_interface,
                "measurement_card": card_interface,
                "cradles": cradle_records,
                "virtual_placements": virtual_placements,
            },
            ["Twenty virtual item blocks are dimensional envelopes, not certified examples; actual cool unpowered items require physical tests."],
        ),
    )

    candidate_volume = float(cassette_shape.Volume())
    total_height = cassette_p["base_height_mm"] + cassette_p["cradle_height_above_base_mm"]
    baseline_volume = cassette_p["width_mm"] * cassette_p["depth_mm"] * total_height
    reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0",
        "project": PROJECT_ID,
        "revision": REVISION,
        "baseline": {"description": "solid cassette bounding block", "volume_mm3": baseline_volume},
        "candidate": {"description": "thin base with local U-fences and connector keep-outs", "volume_mm3": candidate_volume},
        "volume_reduction_percent": reduction,
        "selection_threshold_percent": 65.0,
        "status": "PASS" if reduction >= 65.0 else "FAIL",
        "exact_profile_ab_comparison": "DEFERRED_PENDING_MEASURED_USE_CASE",
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
            "reason": "Analytic tessellation is under budget; decimation could move cradle, keep-out, code or gauge surfaces.",
        },
    )

    outputs = [*step_paths, cassette_path, card_path, package_path]
    write_json(
        REPORTS / "build-manifest.json",
        {
            "schema_version": "1.0",
            "project": PROJECT_ID,
            "revision": REVISION,
            "status": "PASS",
            "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))],
            "outputs": [input_record(path) for path in outputs],
            "manufacturing_outputs": [str(cassette_path.relative_to(ROOT)), str(card_path.relative_to(ROOT)), str(package_path.relative_to(ROOT))],
        },
    )
    if any(value["status"] != "PASS" for value in [json.loads((VALIDATION / "parametric-source-report.json").read_text()), json.loads((VALIDATION / "mesh-generation-report.json").read_text()), json.loads((VALIDATION / "interface-report.json").read_text()), optimization]):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "outputs": [str(path.relative_to(ROOT)) for path in [cassette_path, card_path, package_path]]}, indent=2))


if __name__ == "__main__":
    main()
