#!/usr/bin/env python3
"""Deterministic parametric CAD build for MM-ORG-004.

All dimensions are millimetres. STEP masters retain the centered module datum;
manufacturing STLs are shifted onto the positive XY plane with z=0 on the bed.
The 3MF is a DRAFT inventory strip, not a validated slicer project.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = ROOT / "config" / "model-parameters.json"
MASTER = ROOT / "exports" / "master"
MANUFACTURING = ROOT / "exports" / "manufacturing"
COUPONS = ROOT / "exports" / "coupons"
THREE_MF = ROOT / "exports" / "3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"
PROJECT_ID = "MM-ORG-004"
REVISION = "0.1.0-draft.1"


def load_params() -> dict:
    return json.loads(PARAMS.read_text(encoding="utf-8"))


def validate_parameters(p: dict) -> None:
    assert p["project"]["id"] == PROJECT_ID
    assert p["project"]["revision"] == REVISION
    shell = p["shell"]
    interface = p["interface"]
    printer = p["printer"]
    assert shell["wall"] >= 2.25
    assert shell["floor"] >= 2.2
    assert math.isclose(interface["clearance_each_side"], 0.30, abs_tol=1e-9)
    assert math.isclose(
        interface["socket_height"] - interface["link_height"],
        interface["vertical_clearance"],
        abs_tol=1e-9,
    )
    assert interface["receiver_height"] - interface["socket_height"] >= 2.0
    assert interface["socket_depth"] - interface["link_head_depth"] >= 0.30 - 1e-9
    assert interface["socket_depth"] <= interface["receiver_boss_out"] + shell["wall"] - 0.6
    assert interface["receiver_boss_width"] >= interface["link_head_width"] + 2.0 * interface["clearance_each_side"] + 3.0
    max_x = printer["build_volume"][0] - 2.0 * printer["bed_margin_xy"]
    max_y = printer["build_volume"][1] - 2.0 * printer["bed_margin_xy"]
    for variant in p["tray_variants"].values():
        assert variant["length"] + 2.0 * interface["receiver_boss_out"] <= max_x
        assert variant["width"] + 2.0 * interface["receiver_boss_out"] <= max_y
        assert variant["height"] <= printer["build_volume"][2]
        assert variant["corner_radius"] > shell["wall"]
        assert variant["corner_radius"] < min(variant["length"], variant["width"]) / 2.0


def rounded_prism(length: float, width: float, height: float, radius: float) -> cq.Workplane:
    body = cq.Workplane("XY").rect(length, width).extrude(height)
    return body.edges("|Z").fillet(radius)


def receiver_boss(side: str, length: float, width: float, p: dict) -> cq.Workplane:
    i = p["interface"]
    wall = p["shell"]["wall"]
    out = i["receiver_boss_out"]
    span = i["receiver_boss_width"]
    height = i["receiver_height"]
    overlap = 0.8
    if side in {"east", "west"}:
        dx = out + wall + overlap
        x = (length / 2.0 + (out - wall - overlap) / 2.0) * (1.0 if side == "east" else -1.0)
        return cq.Workplane("XY").box(dx, span, height).translate((x, 0.0, height / 2.0))
    dy = out + wall + overlap
    y = (width / 2.0 + (out - wall - overlap) / 2.0) * (1.0 if side == "north" else -1.0)
    return cq.Workplane("XY").box(span, dy, height).translate((0.0, y, height / 2.0))


def socket_cutter(side: str, length: float, width: float, p: dict) -> cq.Workplane:
    i = p["interface"]
    out = i["receiver_boss_out"]
    depth = i["socket_depth"] + 0.05
    neck = i["link_neck_width"] + 2.0 * i["clearance_each_side"]
    head = i["link_head_width"] + 2.0 * i["clearance_each_side"]
    z_height = i["socket_height"] + 0.05
    if side == "east":
        outer = length / 2.0 + out + 0.05
        inner = outer - depth
        points = [(inner, -head / 2), (outer, -neck / 2), (outer, neck / 2), (inner, head / 2)]
    elif side == "west":
        outer = -length / 2.0 - out - 0.05
        inner = outer + depth
        points = [(outer, -neck / 2), (inner, -head / 2), (inner, head / 2), (outer, neck / 2)]
    elif side == "north":
        outer = width / 2.0 + out + 0.05
        inner = outer - depth
        points = [(-head / 2, inner), (-neck / 2, outer), (neck / 2, outer), (head / 2, inner)]
    else:
        outer = -width / 2.0 - out - 0.05
        inner = outer + depth
        points = [(-neck / 2, outer), (-head / 2, inner), (head / 2, inner), (neck / 2, outer)]
    return cq.Workplane("XY").polyline(points).close().extrude(z_height).translate((0.0, 0.0, -0.05))


def make_tray(name: str, p: dict, *, wall: float | None = None, floor: float | None = None) -> cq.Workplane:
    variant = p["tray_variants"][name]
    shell = p["shell"]
    actual_wall = float(wall if wall is not None else shell["wall"])
    actual_floor = float(floor if floor is not None else shell["floor"])
    length = float(variant["length"])
    width = float(variant["width"])
    height = float(variant["height"])
    radius = float(variant["corner_radius"])
    outer = rounded_prism(length, width, height, radius)
    inner = rounded_prism(
        length - 2.0 * actual_wall,
        width - 2.0 * actual_wall,
        height - actual_floor + 0.1,
        max(radius - actual_wall, 0.6),
    ).translate((0.0, 0.0, actual_floor))
    body = outer.cut(inner)
    for side in ("east", "west", "north", "south"):
        body = body.union(receiver_boss(side, length, width, p))
    for side in ("east", "west", "north", "south"):
        body = body.cut(socket_cutter(side, length, width, p))
    body = body.edges(">Z").fillet(float(shell["rim_radius"]))
    if not body.val().isValid() or len(body.val().Solids()) != 1:
        raise RuntimeError(f"Invalid tray B-Rep: {name}")
    return body


def make_link(p: dict) -> cq.Workplane:
    i = p["interface"]
    gap = i["receiver_face_gap"] / 2.0
    depth = i["link_head_depth"]
    neck = i["link_neck_width"] / 2.0
    head = i["link_head_width"] / 2.0
    points = [
        (-gap - depth, -head),
        (-gap, -neck),
        (gap, -neck),
        (gap + depth, -head),
        (gap + depth, head),
        (gap, neck),
        (-gap, neck),
        (-gap - depth, head),
    ]
    link = cq.Workplane("XY").polyline(points).close().extrude(i["link_height"])
    link = link.edges("|Z").fillet(0.6)
    if not link.val().isValid() or len(link.val().Solids()) != 1:
        raise RuntimeError("Invalid connector B-Rep")
    return link


def make_coupon(p: dict) -> cq.Workplane:
    i = p["interface"]
    c = p["coupon"]
    gap = i["receiver_face_gap"] / 2.0
    block_depth = c["receiver_block_depth"]
    width = i["receiver_boss_width"]
    height = i["receiver_height"]
    left = cq.Workplane("XY").box(block_depth, width, height).translate((-gap - block_depth / 2.0, 0.0, height / 2.0))
    right = cq.Workplane("XY").box(block_depth, width, height).translate((gap + block_depth / 2.0, 0.0, height / 2.0))
    total = 2.0 * block_depth + i["receiver_face_gap"]
    bridge = cq.Workplane("XY").box(total, c["bridge_width"], p["shell"]["floor"]).translate(
        (0.0, -width / 2.0 - c["bridge_width"] / 2.0 + 0.4, p["shell"]["floor"] / 2.0)
    )
    body = left.union(right).union(bridge)
    # East-facing cavity in the left block.
    outer = -gap + 0.05
    inner = outer - i["socket_depth"] - 0.05
    neck = i["link_neck_width"] + 2.0 * i["clearance_each_side"]
    head = i["link_head_width"] + 2.0 * i["clearance_each_side"]
    cut_left = cq.Workplane("XY").polyline(
        [(inner, -head / 2), (outer, -neck / 2), (outer, neck / 2), (inner, head / 2)]
    ).close().extrude(i["socket_height"] + 0.05).translate((0.0, 0.0, -0.05))
    # West-facing cavity in the right block.
    outer = gap - 0.05
    inner = outer + i["socket_depth"] + 0.05
    cut_right = cq.Workplane("XY").polyline(
        [(outer, -neck / 2), (inner, -head / 2), (inner, head / 2), (outer, neck / 2)]
    ).close().extrude(i["socket_height"] + 0.05).translate((0.0, 0.0, -0.05))
    body = body.cut(cut_left).cut(cut_right)
    if not body.val().isValid() or len(body.val().Solids()) != 1:
        raise RuntimeError("Invalid coupon B-Rep")
    return body


def shift_to_origin(shape: cq.Shape) -> cq.Shape:
    box = shape.BoundingBox()
    return shape.translate((-box.xmin, -box.ymin, -box.zmin))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def export_shape(shape: cq.Shape, path: Path, p: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".step", ".stp"}:
        cq.exporters.export(shape, str(path), exportType="STEP")
    elif path.suffix.lower() == ".stl":
        cq.exporters.export(
            shape,
            str(path),
            tolerance=p["export"]["chordal_tolerance"],
            angularTolerance=p["export"]["angular_tolerance"],
        )
    else:
        raise ValueError(path)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"Unexpected mesh scene: {path}")
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "file_bytes": path.stat().st_size,
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "positive_volume": bool(mesh.volume > 0.0),
        "components": int(len(mesh.split(only_watertight=False))),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "bounds_mm": np.round(mesh.bounds, 5).tolist(),
        "extents_mm": np.round(mesh.extents, 5).tolist(),
    }


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None, *, required: bool = True) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": required,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def report(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations: list[str] | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks if item["required"]) else "FAIL",
        "profile": "draft",
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}
            for path in inputs
        ],
        "checks": checks,
        "metrics": metrics,
        "limitations": limitations or [],
        "required_capabilities": [],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def add_zip_member(archive: zipfile.ZipFile, name: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, payload)


def shape_to_mesh(shape: cq.Shape, p: dict) -> tuple[np.ndarray, np.ndarray]:
    vertices, faces = shape.tessellate(p["export"]["chordal_tolerance"], p["export"]["angular_tolerance"])
    mesh = trimesh.Trimesh(
        vertices=np.asarray([[v.x, v.y, v.z] for v in vertices], dtype=float),
        faces=np.asarray(faces, dtype=np.int64),
        process=True,
        validate=True,
    )
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0.0:
        raise RuntimeError("3MF source mesh is not a valid closed positive volume")
    return np.asarray(mesh.vertices), np.asarray(mesh.faces)


def write_3mf(path: Path, parts: list[tuple[str, cq.Shape, int]], p: dict) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    for name, value in (
        ("Title", "DRAFT MM-ORG-004 Modular Desktop Tray System"),
        ("Designer", "metriMade / autonomous CAD workflow"),
        ("Description", "Three tray modules and two identical bow-tie links; inventory strip only."),
        ("LicenseTerms", "DRAFT engineering artifact; not a commercial release"),
    ):
        node = ET.SubElement(model, f"{{{ns}}}metadata", {"name": name})
        node.text = value
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    inventory_x = 0.0
    for object_id, (name, shape, quantity) in enumerate(parts, start=1):
        vertices, faces = shape_to_mesh(shape, p)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {
            "id": str(object_id), "type": "model", "name": name,
            "partnumber": f"{PROJECT_ID}-{REVISION}-{name}",
        })
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices_node = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in vertices:
            ET.SubElement(vertices_node, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles_node = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in faces:
            ET.SubElement(triangles_node, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        for _ in range(quantity):
            ET.SubElement(build, f"{{{ns}}}item", {
                "objectid": str(object_id),
                "transform": f"1 0 0 0 1 0 0 0 1 {inventory_x:.3f} 0 0",
            })
            inventory_x += shape.BoundingBox().xlen + 10.0
    model_bytes = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        add_zip_member(archive, "[Content_Types].xml", content_types)
        add_zip_member(archive, "_rels/.rels", rels)
        add_zip_member(archive, "3D/3dmodel.model", model_bytes)
        add_zip_member(archive, "Metadata/model-parameters.json", PARAMS.read_bytes())


def main() -> None:
    p = load_params()
    validate_parameters(p)
    source = Path(__file__).resolve()
    variants = ("precision", "soft", "lounge")
    trays = {name: make_tray(name, p) for name in variants}
    link = make_link(p)
    coupon = make_coupon(p)

    manufacturing_shapes: dict[str, cq.Shape] = {}
    mesh_data: dict[str, dict] = {}
    for name, workplane in {**trays, "bowtie_link": link}.items():
        native = workplane.val()
        step_path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        stl_path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_shape(native, step_path, p)
        print_shape = shift_to_origin(native)
        export_shape(print_shape, stl_path, p)
        manufacturing_shapes[name] = print_shape
        mesh_data[name] = mesh_metrics(stl_path)
    coupon_step = MASTER / f"DRAFT-{PROJECT_ID}-interface-coupon-{REVISION}.step"
    coupon_stl = COUPONS / f"DRAFT-{PROJECT_ID}-interface-coupon-{REVISION}.stl"
    export_shape(coupon.val(), coupon_step, p)
    export_shape(shift_to_origin(coupon.val()), coupon_stl, p)
    mesh_data["interface_coupon"] = mesh_metrics(coupon_stl)

    i = p["interface"]
    precision_ext_x = p["tray_variants"]["precision"]["length"] + 2.0 * i["receiver_boss_out"]
    soft_ext_x = p["tray_variants"]["soft"]["length"] + 2.0 * i["receiver_boss_out"]
    common_ext_y = p["tray_variants"]["soft"]["width"] + 2.0 * i["receiver_boss_out"]
    top_y = common_ext_y + i["receiver_face_gap"]
    right_x = soft_ext_x / 2.0 + i["receiver_face_gap"] + precision_ext_x / 2.0
    joint_x = soft_ext_x / 2.0 + i["receiver_face_gap"] / 2.0
    joint_y = common_ext_y / 2.0 + i["receiver_face_gap"] / 2.0
    link_y = link.rotate((0, 0, 0), (0, 0, 1), 90.0)
    assembly_shapes = [
        trays["lounge"].val(),
        trays["soft"].val().translate((0.0, top_y, 0.0)),
        trays["precision"].val().translate((right_x, top_y, 0.0)),
        link.val().translate((joint_x, top_y, 0.0)),
        link_y.val().translate((0.0, joint_y, 0.0)),
    ]
    assembly = cq.Compound.makeCompound(assembly_shapes)
    assembly_path = MASTER / f"DRAFT-{PROJECT_ID}-assembly-preview-{REVISION}.stl"
    export_shape(shift_to_origin(assembly), assembly_path, p)
    assembly_box = assembly.BoundingBox()
    assembly_extents = [assembly_box.xlen, assembly_box.ylen, assembly_box.zlen]

    print_set = THREE_MF / f"DRAFT-{PROJECT_ID}-modular-desktop-tray-system-{REVISION}.3mf"
    write_3mf(print_set, [
        ("tray_precision", manufacturing_shapes["precision"], 1),
        ("tray_soft", manufacturing_shapes["soft"], 1),
        ("tray_lounge", manufacturing_shapes["lounge"], 1),
        ("bowtie_link", manufacturing_shapes["bowtie_link"], 2),
    ], p)

    mesh_checks = []
    for name, metrics in mesh_data.items():
        mesh_checks.extend([
            check(f"{name}-watertight", metrics["watertight"], f"{name} is watertight"),
            check(f"{name}-winding", metrics["winding_consistent"], f"{name} has consistent winding"),
            check(f"{name}-volume", metrics["positive_volume"], f"{name} has positive volume"),
            check(f"{name}-component", metrics["components"] == 1, f"{name} is one connected component", {"components": metrics["components"]}),
            check(f"{name}-mesh-budget", metrics["triangles"] <= p["export"]["max_triangles_per_part"], f"{name} stays within triangle budget", {"triangles": metrics["triangles"]}),
        ])
    mesh_report = report(
        f"{PROJECT_ID}-mesh-generation",
        [PARAMS, source],
        mesh_checks,
        {"meshes": mesh_data},
        ["Topology and envelope checks do not prove process-specific bridging, fit, strength or appearance."],
    )
    write_json(VALIDATION / "mesh-generation-report.json", mesh_report)

    connector_clearance = (i["link_head_width"] + 2.0 * i["clearance_each_side"] - i["link_head_width"]) / 2.0
    interface_report = report(
        f"{PROJECT_ID}-interface-validation",
        [PARAMS, source, MANUFACTURING / f"DRAFT-{PROJECT_ID}-bowtie_link-{REVISION}.stl", coupon_stl],
        [
            check("per-side-clearance", math.isclose(connector_clearance, 0.30, abs_tol=1e-9), "Nominal connector clearance is 0.30 mm per side", {"clearance_mm": connector_clearance}),
            check("vertical-clearance", math.isclose(i["socket_height"] - i["link_height"], 0.30, abs_tol=1e-9), "Vertical connector clearance is 0.30 mm", {"clearance_mm": i["socket_height"] - i["link_height"]}),
            check("socket-roof", i["receiver_height"] - i["socket_height"] >= 2.0, "Socket roof reserve is at least 2.0 mm", {"roof_mm": i["receiver_height"] - i["socket_height"]}),
            check("coupon-present", coupon_stl.is_file(), "Dedicated interface coupon is exported"),
        ],
        {
            "connector_head_width_mm": i["link_head_width"],
            "socket_head_width_mm": i["link_head_width"] + 2.0 * i["clearance_each_side"],
            "bridge_span_mm": i["link_head_width"] + 2.0 * i["clearance_each_side"],
            "physical_fit": "NOT_RUN",
        },
        ["Interference-free nominal CAD dimensions do not establish printed fit; the coupon is mandatory before a full set."],
    )
    write_json(VALIDATION / "interface-report.json", interface_report)

    max_part = [170.0, 90.0, 45.0]
    source_report = report(
        f"{PROJECT_ID}-parametric-source",
        [PARAMS, source, ROOT / "design-spec.yaml", ROOT / "protected-geometry-map.md"],
        [
            check("parameter-contract", True, "Default and declared boundary parameter assertions pass"),
            check("expected-parts", set(mesh_data) == {"precision", "soft", "lounge", "bowtie_link", "interface_coupon"}, "All expected production parts and coupon are generated"),
            check("part-envelope", all(all(actual <= limit + 0.05 for actual, limit in zip(metrics["extents_mm"], max_part)) for name, metrics in mesh_data.items() if name != "interface_coupon"), "Every production part stays inside the declared part envelope", {"limit_mm": max_part}),
            check("assembly-envelope", assembly_extents[0] <= 230.0 and assembly_extents[1] <= 180.0 and assembly_extents[2] <= 45.0, "Reference arrangement stays within the research envelope", {"extents_mm": assembly_extents}),
            check("mesh-stage", mesh_report["status"] == "PASS", "All deterministic mesh checks pass"),
            check("interface-stage", interface_report["status"] == "PASS", "Nominal interface checks pass"),
            check("print-set", print_set.is_file(), "DRAFT multi-object 3MF exists"),
        ],
        {
            "assembly_extents_mm": assembly_extents,
            "wall_mm": p["shell"]["wall"],
            "floor_mm": p["shell"]["floor"],
            "receiver_roof_mm": i["receiver_height"] - i["socket_height"],
            "print_set": str(print_set.relative_to(ROOT)),
        },
        ["Exact slicer preflight and all physical tests are intentionally deferred."],
    )
    write_json(VALIDATION / "parametric-source-report.json", source_report)

    baseline = {name: make_tray(name, p, wall=3.0, floor=3.0).val().Volume() for name in variants}
    selected_volume = sum(mesh_data[name]["volume_mm3"] for name in variants) + 2.0 * mesh_data["bowtie_link"]["volume_mm3"]
    baseline_volume = sum(baseline.values()) + 2.0 * mesh_data["bowtie_link"]["volume_mm3"]
    optimization = report(
        f"{PROJECT_ID}-optimization-comparison",
        [PARAMS, source, ROOT / "protected-geometry-map.md"],
        [
            check("protected-map", (ROOT / "protected-geometry-map.md").is_file(), "Protected geometry map exists"),
            check("candidate-volume", selected_volume < baseline_volume, "Separated shell parameters reduce CAD volume against the conservative shell baseline"),
            check("support-intent", i["link_head_width"] + 2.0 * i["clearance_each_side"] <= 15.0, "Largest socket roof bridge span is at most 15 mm", {"bridge_span_mm": i["link_head_width"] + 2.0 * i["clearance_each_side"]}),
        ],
        {
            "baseline": "A conservative 3.0 mm walls and 3.0 mm floors",
            "selected": "B separated 2.4 mm walls/floors with local receiver reinforcement",
            "candidate_C": "0.6 mm nozzle process hypothesis; NOT_SELECTED",
            "baseline_cad_volume_mm3": baseline_volume,
            "selected_cad_volume_mm3": selected_volume,
            "cad_volume_reduction_percent": 100.0 * (baseline_volume - selected_volume) / baseline_volume,
            "estimated_selected_pla_mass_g_at_1_24": selected_volume / 1000.0 * 1.24,
            "exact_slicer_metrics": "NOT_RUN",
        },
        ["CAD volume is not deposited material and does not establish print-time savings. Exact A/B/C slicing is deferred."],
    )
    write_json(REPORTS / "optimization-comparison.json", optimization)

    manifest = {
        "project_id": PROJECT_ID,
        "revision": REVISION,
        "status": "DRAFT",
        "parameters_sha256": sha256(PARAMS),
        "source_sha256": sha256(source),
        "parts": mesh_data,
        "assembly_preview_stl": str(assembly_path.relative_to(ROOT)),
        "assembly_preview_stl_sha256": sha256(assembly_path),
        "assembly_extents_mm": assembly_extents,
        "print_set_3mf": str(print_set.relative_to(ROOT)),
        "print_set_3mf_sha256": sha256(print_set),
        "physical_validation": "DEFERRED",
    }
    write_json(REPORTS / "build-manifest.json", manifest)
    if any(item["status"] != "PASS" for item in (mesh_report, interface_report, source_report, optimization)):
        raise RuntimeError("One or more deterministic reports failed")
    print(json.dumps({"status": "PASS", "assembly_extents_mm": assembly_extents, "print_set": str(print_set)}, indent=2))


if __name__ == "__main__":
    main()
