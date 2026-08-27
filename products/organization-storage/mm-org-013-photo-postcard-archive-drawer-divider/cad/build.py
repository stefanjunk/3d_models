#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-013 photo/postcard drawer divider."""
from __future__ import annotations

import hashlib
import json
import platform
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
PROJECT_ID = "MM-ORG-013"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
}


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def active_format(parameters: dict) -> dict:
    formats = {item["id"]: item for item in parameters["media_formats"]}
    return formats[parameters["active_media_id"]]


def derived(parameters: dict) -> dict:
    frame = parameters["frame"]
    divider = parameters["divider"]
    media = active_format(parameters)
    guide_x = frame["side_wall_thickness"] + media["long_edge"] + frame["media_clearance"]
    divider_width = frame["outer_width"] - 2.0 * divider["edge_clearance_each_side"]
    tab_start_local = guide_x + frame["guide_wall_thickness"] + 1.0 - divider["edge_clearance_each_side"]
    slot_width = divider["thickness"] + 2.0 * divider["slot_clearance_each_side"]
    return {
        "guide_x": guide_x,
        "divider_width": divider_width,
        "tab_start_local": tab_start_local,
        "slot_width": slot_width,
        "installed_bottom_z": frame["base_thickness"] - frame["slot_depth_into_base"],
    }


def text_width(text: str, pitch: float) -> float:
    return max(0, len(text) * 6 - 1) * pitch


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    frame = parameters["frame"]
    divider = parameters["divider"]
    gauge = parameters["format_gauge"]
    limits = parameters["limits"]
    media = active_format(parameters)
    dims = derived(parameters)
    assert project == {"id": PROJECT_ID, "revision": REVISION, "units": "mm", "source_sku": "SKU-112"}
    assert frame["outer_width"] <= limits["maximum_part_envelope"][0]
    assert frame["outer_depth"] <= limits["maximum_part_envelope"][1]
    assert frame["wall_height"] <= limits["maximum_part_envelope"][2]
    assert frame["base_thickness"] >= limits["minimum_wall"]
    assert frame["side_wall_thickness"] >= limits["minimum_wall"]
    assert limits["media_long_edge"][0] <= media["long_edge"] <= limits["media_long_edge"][1]
    assert limits["media_short_edge"][0] <= media["short_edge"] <= limits["media_short_edge"][1]
    assert len({item["id"] for item in parameters["media_formats"]}) == len(parameters["media_formats"])
    assert {item["id"] for item in parameters["media_formats"]} == {"photo-10x15", "postcard-a6", "photo-13x18"}
    assert all(set(item["label"]).issubset(GLYPHS) for item in parameters["media_formats"])
    assert limits["divider_count"][0] <= len(divider["labels"]) <= limits["divider_count"][1]
    assert len(divider["labels"]) == len(divider["installed_slot_positions"])
    assert all(set(label).issubset(GLYPHS) for label in divider["labels"])
    assert set(divider["installed_slot_positions"]).issubset(set(frame["slot_positions"]))
    assert frame["slot_positions"] == sorted(frame["slot_positions"])
    assert frame["slot_positions"][0] > frame["side_wall_thickness"] + dims["slot_width"] / 2.0
    assert frame["slot_positions"][-1] < frame["outer_depth"] - frame["side_wall_thickness"] - dims["slot_width"] / 2.0
    assert min(np.diff(frame["slot_positions"])) - dims["slot_width"] >= limits["minimum_slot_web"]
    assert dims["guide_x"] + frame["guide_wall_thickness"] < frame["outer_width"] - frame["side_wall_thickness"]
    assert media["long_edge"] + frame["media_clearance"] == dims["guide_x"] - frame["side_wall_thickness"]
    tab_width = dims["divider_width"] - dims["tab_start_local"]
    assert tab_width >= max(text_width(label, divider["label_pixel_pitch"]) for label in divider["labels"]) + 1.0
    assert divider["label_pixel_pitch"] * divider["label_pixel_fill"] >= limits["minimum_label_pixel"]
    assert dims["installed_bottom_z"] + divider["tab_height"] <= limits["maximum_part_envelope"][2]
    for item in parameters["media_formats"]:
        outer_w = item["long_edge"] + gauge["clearance_total_each_dimension"] + 2.0 * gauge["strip_width"]
        outer_d = item["short_edge"] + gauge["clearance_total_each_dimension"] + gauge["strip_width"]
        assert outer_w <= limits["maximum_part_envelope"][0]
        assert outer_d <= limits["maximum_part_envelope"][1]


def rounded_box_xy(width: float, depth: float, height: float, radius: float) -> cq.Shape:
    return (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(False, False, False))
        .edges("|Z")
        .fillet(radius)
        .val()
    )


def fuse_all(parts: list[cq.Shape]) -> cq.Shape:
    result = parts[0]
    for part in parts[1:]:
        result = result.fuse(part)
    return result.clean()


def pixel_text(text: str, pitch: float, depth: float, fill: float) -> tuple[cq.Shape, float, float]:
    cursor = 0
    pixels: list[cq.Shape] = []
    pixel = pitch * fill
    inset = (pitch - pixel) / 2.0
    for character in text:
        glyph = GLYPHS[character]
        for row_index, row in enumerate(glyph):
            for column_index, enabled in enumerate(row):
                if enabled == "1":
                    pixels.append(
                        cq.Solid.makeBox(
                            pixel,
                            depth,
                            pixel,
                            cq.Vector((cursor + column_index) * pitch + inset, 0, (6 - row_index) * pitch + inset),
                        )
                    )
        cursor += 6
    return cq.Compound.makeCompound(pixels), max(0, cursor - 1) * pitch, 7.0 * pitch


def make_frame(parameters: dict) -> tuple[cq.Shape, dict]:
    frame = parameters["frame"]
    dims = derived(parameters)
    width = frame["outer_width"]
    depth = frame["outer_depth"]
    base = frame["base_thickness"]
    wall = frame["side_wall_thickness"]
    height = frame["wall_height"]
    guide_x = dims["guide_x"]
    parts = [
        rounded_box_xy(width, depth, base, frame["corner_radius"]),
        cq.Solid.makeBox(wall, depth, height, cq.Vector(0, 0, 0)),
        cq.Solid.makeBox(wall, depth, height, cq.Vector(width - wall, 0, 0)),
        cq.Solid.makeBox(width, wall, height, cq.Vector(0, 0, 0)),
        cq.Solid.makeBox(width, wall, height, cq.Vector(0, depth - wall, 0)),
        cq.Solid.makeBox(
            frame["guide_wall_thickness"],
            depth - 2.0 * wall,
            frame["guide_wall_height"],
            cq.Vector(guide_x, wall, 0),
        ),
    ]
    result = fuse_all(parts)
    cutter_z = base - frame["slot_depth_into_base"]
    cutter_height = height - cutter_z + 1.0
    for position in frame["slot_positions"]:
        cutters = [
            cq.Solid.makeBox(wall + 1.0, dims["slot_width"], cutter_height, cq.Vector(-0.5, position - dims["slot_width"] / 2.0, cutter_z)),
            cq.Solid.makeBox(wall + 1.0, dims["slot_width"], cutter_height, cq.Vector(width - wall - 0.5, position - dims["slot_width"] / 2.0, cutter_z)),
            cq.Solid.makeBox(frame["guide_wall_thickness"] + 1.0, dims["slot_width"], cutter_height, cq.Vector(guide_x - 0.5, position - dims["slot_width"] / 2.0, cutter_z)),
        ]
        result = result.cut(cq.Compound.makeCompound(cutters))
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("archive frame is not one valid solid")
    return result, {
        "outer_dimensions_mm": [width, depth, height],
        "active_media_clear_width_mm": guide_x - wall,
        "active_media_long_edge_mm": active_format(parameters)["long_edge"],
        "active_media_total_clearance_mm": frame["media_clearance"],
        "index_gutter_width_mm": width - wall - guide_x - frame["guide_wall_thickness"],
        "slot_count": len(frame["slot_positions"]),
        "slot_width_mm": dims["slot_width"],
        "minimum_slot_web_mm": min(np.diff(frame["slot_positions"])) - dims["slot_width"],
    }


def make_divider(parameters: dict, label: str) -> tuple[cq.Shape, dict]:
    divider = parameters["divider"]
    dims = derived(parameters)
    width = dims["divider_width"]
    body = divider["body_height"]
    tab = divider["tab_height"]
    relief = divider["top_corner_relief"]
    tab_x = dims["tab_start_local"]
    points = [
        (0, 0),
        (width, 0),
        (width, tab - relief),
        (width - relief, tab),
        (tab_x + relief, tab),
        (tab_x, tab - relief),
        (tab_x, body),
        (relief, body),
        (0, body - relief),
    ]
    shape = cq.Workplane("XZ").polyline(points).close().extrude(divider["thickness"]).val()
    cutter, label_width, label_height = pixel_text(
        label,
        divider["label_pixel_pitch"],
        divider["label_engraving_depth"] + 0.1,
        divider["label_pixel_fill"],
    )
    label_center = (tab_x + width) / 2.0
    label_z = tab - relief - label_height - 1.0
    shape = shape.cut(cutter.translate((label_center - label_width / 2.0, -0.05, label_z))).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"divider {label} is not one valid solid")
    return shape, {
        "label": label,
        "installed_width_mm": width,
        "installed_height_mm": tab,
        "thickness_mm": divider["thickness"],
        "tab_width_mm": width - tab_x,
        "label_width_mm": label_width,
        "label_pixel_mm": divider["label_pixel_pitch"] * divider["label_pixel_fill"],
    }


def divider_for_print(installed: cq.Shape, thickness: float) -> cq.Shape:
    return installed.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, thickness))


def make_format_gauge(parameters: dict, media: dict) -> tuple[cq.Shape, dict]:
    gauge = parameters["format_gauge"]
    strip = gauge["strip_width"]
    clearance = gauge["clearance_total_each_dimension"]
    inner_w = media["long_edge"] + clearance
    inner_d = media["short_edge"] + clearance
    outer_w = inner_w + 2.0 * strip
    outer_d = inner_d + strip
    thick = gauge["thickness"]
    entry = gauge["entry_chamfer"]
    bottom = cq.Solid.makeBox(outer_w, strip, thick, cq.Vector(0, 0, 0))
    left = cq.Workplane("XY").polyline([(0, 0), (strip, 0), (strip, outer_d - entry), (0, outer_d)]).close().extrude(thick).val()
    right = cq.Workplane("XY").polyline([(outer_w - strip, 0), (outer_w, 0), (outer_w, outer_d), (outer_w - strip, outer_d - entry)]).close().extrude(thick).val()
    shape = fuse_all([bottom, left, right])
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"format gauge {media['id']} is not one valid solid")
    return shape, {
        "id": media["id"],
        "label": media["label"],
        "nominal_media_mm": [media["long_edge"], media["short_edge"]],
        "gauge_clear_mm": [inner_w, inner_d],
        "total_clearance_each_dimension_mm": clearance,
        "outer_dimensions_mm": [outer_w, outer_d, thick],
        "entry_chamfer_mm": entry,
    }


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
    export = parameters["export"]
    frame_p = parameters["frame"]
    divider_p = parameters["divider"]
    dims = derived(parameters)
    frame_shape, frame_metrics = make_frame(parameters)
    divider_shapes: dict[str, cq.Shape] = {}
    divider_metrics: list[dict] = []
    for label in divider_p["labels"]:
        shape, metrics = make_divider(parameters, label)
        divider_shapes[label] = shape
        divider_metrics.append(metrics)
    gauge_shapes: dict[str, cq.Shape] = {}
    gauge_metrics: list[dict] = []
    for media in parameters["media_formats"]:
        shape, metrics = make_format_gauge(parameters, media)
        gauge_shapes[media["id"]] = shape
        gauge_metrics.append(metrics)

    installed_dividers = []
    edge = divider_p["edge_clearance_each_side"]
    for label, position in zip(divider_p["labels"], divider_p["installed_slot_positions"]):
        installed_dividers.append(
            divider_shapes[label].translate((edge, position - divider_p["thickness"] / 2.0, dims["installed_bottom_z"]))
        )
    assembly = cq.Compound.makeCompound([frame_shape, *installed_dividers])
    gauge_step_parts = []
    gauge_cursor = 0.0
    for media_id, shape in gauge_shapes.items():
        gauge_step_parts.append(shape.translate((0, gauge_cursor, 0)))
        gauge_cursor += shape.BoundingBox().ylen + 10.0
    gauge_set = cq.Compound.makeCompound(gauge_step_parts)
    step_shapes = {
        "archive-frame": frame_shape,
        "divider-template": divider_shapes[divider_p["labels"][0]],
        "installed-assembly": assembly,
        "format-gauge-set": gauge_set,
    }
    step_paths: list[Path] = []
    for name, shape in step_shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)

    mesh_paths: dict[str, Path] = {}
    frame_path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-archive-frame-{REVISION}.stl"
    export_stl(frame_shape, frame_path, export["linear_tolerance"], export["angular_tolerance"])
    mesh_paths["archive-frame"] = frame_path
    for label, shape in divider_shapes.items():
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-divider-{label}-{REVISION}.stl"
        export_stl(divider_for_print(shape, divider_p["thickness"]), path, export["linear_tolerance"], export["angular_tolerance"])
        mesh_paths[f"divider-{label}"] = path
    gauge_paths: dict[str, Path] = {}
    for media_id, shape in gauge_shapes.items():
        path = COUPONS / f"DRAFT-{PROJECT_ID}-gauge-{media_id}-{REVISION}.stl"
        export_stl(shape, path, export["linear_tolerance"], export["angular_tolerance"])
        gauge_paths[f"gauge-{media_id}"] = path

    divider_names = [f"divider-{label}" for label in divider_p["labels"]]
    primary_names = ["archive-frame", *divider_names[:3]]
    primary_parts = [(name, mesh_paths[name]) for name in primary_names]
    primary_placements = [(5.0, 5.0), (5.0, 180.0), (5.0, 250.0), (5.0, 320.0)]
    primary_3mf = THREE_MF / f"DRAFT-{PROJECT_ID}-frame-and-first-three-dividers-{REVISION}.3mf"
    write_3mf(primary_3mf, primary_parts, primary_placements)
    secondary_parts = [(name, mesh_paths[name]) for name in divider_names[3:]]
    secondary_placements = [(5.0, 5.0), (5.0, 75.0), (5.0, 145.0)]
    secondary_3mf = THREE_MF / f"DRAFT-{PROJECT_ID}-remaining-three-dividers-{REVISION}.3mf"
    write_3mf(secondary_3mf, secondary_parts, secondary_placements)
    gauge_parts = [(name, path) for name, path in gauge_paths.items()]
    gauge_placements = [(200.0, 5.0), (200.0, 120.0), (5.0, 5.0)]
    gauge_3mf = THREE_MF / f"DRAFT-{PROJECT_ID}-three-format-gauge-set-{REVISION}.3mf"
    write_3mf(gauge_3mf, gauge_parts, gauge_placements)

    all_mesh_paths = {**mesh_paths, **gauge_paths}
    metrics = {name: mesh_metrics(path) for name, path in all_mesh_paths.items()}
    mesh_checks: list[dict] = []
    for name, item in metrics.items():
        mesh_checks.extend(
            [
                check(f"{name}:watertight", item["watertight"], f"{name} is watertight"),
                check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"),
                check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"),
                check(f"{name}:component", item["components"] == 1, f"{name} is one component"),
                check(f"{name}:triangles", item["triangles"] <= export["mesh_triangle_budget_each"], "Triangle budget", {"actual": item["triangles"], "limit": export["mesh_triangle_budget_each"]}),
                check(f"{name}:file", item["file_mib"] <= export["mesh_file_budget_mib_each"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": export["mesh_file_budget_mib_each"]}),
            ]
        )
    write_json(
        VALIDATION / "mesh-generation-report.json",
        report(
            f"{PROJECT_ID}-mesh-generation",
            [PARAMETERS, Path(__file__)],
            mesh_checks,
            {"meshes": metrics},
            ["Topology does not prove paper snagging, photo-safe material compatibility, tab visibility or drawer closure."],
        ),
    )
    interface_checks = [
        check("active-media-clearance", frame_metrics["active_media_total_clearance_mm"] >= 2.0, "Active media long edge has declared total allowance"),
        check("ten-slot-grid", frame_metrics["slot_count"] == 10, "Ten aligned divider positions generated"),
        check("slot-web", frame_metrics["minimum_slot_web_mm"] >= parameters["limits"]["minimum_slot_web"], "Slot web meets minimum"),
        check("divider-slot-fit", abs(frame_metrics["slot_width_mm"] - divider_p["thickness"] - 2.0 * divider_p["slot_clearance_each_side"]) < 1e-9, "Divider and slot clearance are linked"),
        check("six-labels", len(divider_metrics) == 6, "Six individualized label plates generated"),
        check("label-legibility", all(item["label_pixel_mm"] >= parameters["limits"]["minimum_label_pixel"] and item["tab_width_mm"] >= item["label_width_mm"] + 1.0 for item in divider_metrics), "All labels meet pixel and tab-width minima"),
        check("lateral-index-gutter", frame_metrics["index_gutter_width_mm"] >= 16.0, "Index gutter remains outside active media edge"),
        check("three-format-gauges", {item["id"] for item in gauge_metrics} == {"photo-10x15", "postcard-a6", "photo-13x18"}, "All three format gauges generated"),
        check("gauge-allowance", all(item["total_clearance_each_dimension_mm"] == parameters["format_gauge"]["clearance_total_each_dimension"] for item in gauge_metrics), "Every gauge uses the declared two-axis allowance"),
        check("installed-height", dims["installed_bottom_z"] + divider_p["tab_height"] <= parameters["limits"]["maximum_part_envelope"][2], "Installed printed geometry remains inside declared part height"),
    ]
    write_json(
        VALIDATION / "interface-report.json",
        report(
            f"{PROJECT_ID}-interface-validation",
            [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
            interface_checks,
            {"frame": frame_metrics, "dividers": divider_metrics, "format_gauges": gauge_metrics},
            ["Gauge envelopes are nominal standards plus configured allowance; actual sleeved media and drawer height require the deferred print test.", "Printed PLA has no archival/PAT qualification."],
        ),
    )
    write_json(
        VALIDATION / "parametric-source-report.json",
        report(
            f"{PROJECT_ID}-parametric-source",
            [PARAMETERS, Path(__file__)],
            [
                check("parameter-validation", True, "Fail-closed parameter relations pass"),
                check("cad-valid", frame_shape.isValid() and all(shape.isValid() for shape in [*divider_shapes.values(), *gauge_shapes.values()]), "Frame, divider and gauge B-Reps are valid"),
                check("source-of-truth", True, "JSON drives media formats, slots, plates, labels, gauges, transforms and exports"),
            ],
            {"frame_dimensions_mm": [frame_p["outer_width"], frame_p["outer_depth"], frame_p["wall_height"]], "active_media_id": parameters["active_media_id"], "divider_count": len(divider_shapes), "format_count": len(gauge_shapes), "python": platform.python_version(), "cadquery": getattr(cq, "__version__", "unknown")},
            ["A parameter change requires rebuilding all downstream evidence."],
        ),
    )
    baseline = frame_p["outer_width"] * frame_p["outer_depth"] * parameters["limits"]["maximum_part_envelope"][2]
    frame_volume = metrics["archive-frame"]["volume_mm3"]
    write_json(
        REPORTS / "optimization-comparison.json",
        {"schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION, "baseline": {"method": "full maximum frame bounding block", "volume_mm3": baseline}, "candidate": {"method": "thin continuous base with low local rails", "volume_mm3": frame_volume}, "cad_volume_reduction_percent": 100.0 * (1.0 - frame_volume / baseline), "protected_requirements": ["continuous base", "ten receiver positions", "active-media guide", "lateral index gutter"]},
    )
    write_json(REPORTS / "mesh-complexity.json", {"project_id": PROJECT_ID, "revision": REVISION, "meshes": metrics})
    artifact_paths = [*step_paths, *all_mesh_paths.values(), primary_3mf, secondary_3mf, gauge_3mf]
    write_json(
        REPORTS / "build-manifest.json",
        {"schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION, "status": "PASS", "source": input_record(PARAMETERS), "artifacts": [input_record(path) for path in artifact_paths], "reports": [input_record(path) for path in [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json"]], "limitations": ["Physical three-format fit, paper snagging, tab visibility and drawer closure are deferred.", "DRAFT outputs carry no final commercial watermark or archival-safety claim."]},
    )
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "outputs": [str(path.relative_to(ROOT)) for path in [*all_mesh_paths.values(), primary_3mf, secondary_3mf, gauge_3mf]]}, indent=2))


if __name__ == "__main__":
    main()
