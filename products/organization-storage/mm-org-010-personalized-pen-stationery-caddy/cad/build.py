#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-010 stationery caddy.

All dimensions are millimetres. The personalization uses an embedded 5x7
geometric alphabet and therefore has no runtime font or external font licence
dependency. STEP is the neutral assembly master. Manufacturing STL files are
exported in their intended print orientations.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import unicodedata
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
PROJECT_ID = "MM-ORG-010"
REVISION = "0.1.0-draft.1"

MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
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
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    " ": ("000", "000", "000", "000", "000", "000", "000"),
}


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def sanitize_name(value: str, parameters: dict) -> str:
    replacements = {
        "Ä": "AE",
        "Ö": "OE",
        "Ü": "UE",
        "ä": "AE",
        "ö": "OE",
        "ü": "UE",
        "ẞ": "SS",
        "ß": "SS",
    }
    expanded = "".join(replacements.get(char, char) for char in value.strip())
    normalized = unicodedata.normalize("NFKD", expanded)
    ascii_value = "".join(char for char in normalized if not unicodedata.combining(char)).upper()
    allowed = set(parameters["personalization"]["allowed_characters"])
    if any(char not in allowed for char in ascii_value):
        invalid = sorted(set(char for char in ascii_value if char not in allowed))
        raise ValueError(f"unsupported personalization characters: {invalid}")
    result = " ".join(ascii_value.split())
    maximum = parameters["personalization"]["maximum_characters_after_transliteration"]
    if not result:
        raise ValueError("personalization must not be empty")
    if len(result) > maximum:
        raise ValueError(f"personalization exceeds {maximum} characters after transliteration")
    return result


def text_layout(name: str, plate: dict) -> dict:
    column_counts = [len(GLYPHS[char][0]) for char in name]
    total_columns = sum(column_counts) + max(0, len(name) - 1)
    available_width = plate["width"] - 2.0 * plate["text_margin_x"]
    available_height = plate["height"] - 2.0 * plate["text_margin_y"]
    pitch = min(
        plate["maximum_pixel_pitch"],
        available_width / total_columns,
        available_height / 7.0,
    )
    pixel = pitch * 0.78
    if pixel < plate["minimum_pixel_width"]:
        raise ValueError("personalization would create sub-minimum printable pixels")
    return {
        "total_columns": total_columns,
        "pitch": pitch,
        "pixel_width": pixel,
        "text_width": total_columns * pitch,
        "text_height": 7.0 * pitch,
    }


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    caddy = parameters["caddy"]
    plate = parameters["nameplate"]
    limits = parameters["limits"]
    export = parameters["export"]
    name = sanitize_name(parameters["personalization"]["name"], parameters)

    assert project["id"] == PROJECT_ID
    assert project["revision"] == REVISION
    assert project["units"] == "mm"
    assert limits["width"][0] <= caddy["width"] <= limits["width"][1]
    assert limits["depth"][0] <= caddy["depth"] <= limits["depth"][1]
    assert limits["rear_height"][0] <= caddy["rear_back_height"] <= limits["rear_height"][1]
    assert limits["wall_thickness"][0] <= caddy["wall_thickness"] <= limits["wall_thickness"][1]
    assert caddy["base_thickness"] >= 2.4
    assert caddy["rear_front_y"] < caddy["depth"] - 20.0
    assert caddy["rear_front_height"] < caddy["rear_back_height"]
    assert caddy["rear_partitions_x"] == sorted(caddy["rear_partitions_x"])
    assert caddy["small_tray_width"] + caddy["wall_thickness"] < caddy["phone_cradle_x"]
    assert caddy["phone_cradle_x"] + caddy["phone_cradle_width"] <= caddy["width"]
    slot_bottom = caddy["phone_backrest_y"] - (
        caddy["phone_front_lip_y"] + caddy["wall_thickness"]
    )
    assert slot_bottom >= caddy["maximum_phone_case_thickness"] + 0.5
    assert limits["phone_case_thickness"][0] <= caddy["maximum_phone_case_thickness"]
    assert caddy["maximum_phone_case_thickness"] <= limits["phone_case_thickness"][1]
    assert plate["width"] < caddy["width"] - 2.0 * plate["guide_width"]
    assert plate["height"] < caddy["front_bank_height"] - 4.0
    assert plate["thickness"] - plate["engraving_depth"] >= 1.2
    assert plate["channel_clearance"] >= 0.2
    assert text_layout(name, plate)["pixel_width"] >= plate["minimum_pixel_width"]
    envelope = limits["maximum_part_envelope"]
    assert caddy["width"] <= envelope[0]
    assert caddy["depth"] + plate["guide_depth"] <= envelope[1]
    assert caddy["rear_back_height"] <= envelope[2]
    assert export["mesh_triangle_budget_each"] > 0
    assert export["mesh_file_budget_mib_each"] > 0.0


def _rounded_box_xy(width: float, depth: float, height: float, radius: float) -> cq.Shape:
    shape = (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(False, False, False))
        .edges("|Z")
        .fillet(radius)
        .val()
    )
    return shape


def _top_rounded_box(
    width: float, depth: float, height: float, origin: tuple[float, float, float], radius: float
) -> cq.Shape:
    shape = cq.Solid.makeBox(width, depth, height, cq.Vector(*origin))
    try:
        shape = cq.Workplane(obj=shape).edges(">Z").fillet(radius).val()
    except Exception:
        pass
    return shape


def _sloped_wall_x(parameters: dict, x0: float, thickness: float) -> cq.Shape:
    caddy = parameters["caddy"]
    return (
        cq.Workplane("YZ", origin=(x0, 0.0, 0.0))
        .polyline(
            [
                (caddy["rear_front_y"], caddy["base_thickness"]),
                (caddy["depth"], caddy["base_thickness"]),
                (caddy["depth"], caddy["rear_back_height"]),
                (caddy["rear_front_y"], caddy["rear_front_height"]),
            ]
        )
        .close()
        .extrude(thickness)
        .val()
    )


def _phone_backrest(parameters: dict) -> cq.Shape:
    caddy = parameters["caddy"]
    wall = caddy["wall_thickness"]
    y0 = caddy["phone_backrest_y"]
    top_y = y0 + caddy["phone_backrest_tilt_offset"]
    z0 = caddy["base_thickness"]
    z1 = caddy["phone_backrest_height"]
    return (
        cq.Workplane("YZ", origin=(caddy["phone_cradle_x"], 0.0, 0.0))
        .polyline([(y0, z0), (y0 + wall, z0), (top_y + wall, z1), (top_y, z1)])
        .close()
        .extrude(caddy["phone_cradle_width"])
        .val()
    )


def _channel_parts(
    parameters: dict,
    frame_width: float,
    plate_width: float,
    plate_height: float,
    plate_bottom: float,
) -> list[cq.Shape]:
    plate = parameters["nameplate"]
    inner_left = (frame_width - plate_width) / 2.0
    inner_right = inner_left + plate_width
    clearance = plate["channel_clearance"]
    guide_width = plate["guide_width"]
    guide_depth = plate["guide_depth"]
    overlap = plate["guide_overlap"]
    lip_near_y = -(plate["thickness"] + 2.0 * clearance)
    z_low = plate_bottom - guide_width
    z_high = plate_bottom + plate_height + guide_width

    left_spacer = cq.Solid.makeBox(
        guide_width - clearance,
        guide_depth,
        z_high - z_low,
        cq.Vector(inner_left - guide_width, -guide_depth, z_low),
    )
    right_spacer = cq.Solid.makeBox(
        guide_width - clearance,
        guide_depth,
        z_high - z_low,
        cq.Vector(inner_right + clearance, -guide_depth, z_low),
    )
    left_lip = cq.Solid.makeBox(
        overlap + clearance,
        -lip_near_y,
        z_high - z_low,
        cq.Vector(inner_left - clearance, -guide_depth, z_low),
    )
    right_lip = cq.Solid.makeBox(
        overlap + clearance,
        -lip_near_y,
        z_high - z_low,
        cq.Vector(inner_right - overlap, -guide_depth, z_low),
    )
    bottom_spacer = cq.Solid.makeBox(
        plate_width + 2.0 * guide_width,
        guide_depth,
        guide_width - clearance,
        cq.Vector(inner_left - guide_width, -guide_depth, plate_bottom - guide_width),
    )
    bottom_lip = cq.Solid.makeBox(
        plate_width + 2.0 * guide_width,
        -lip_near_y,
        overlap + clearance,
        cq.Vector(inner_left - guide_width, -guide_depth, plate_bottom - clearance),
    )
    return [left_spacer, right_spacer, left_lip, right_lip, bottom_spacer, bottom_lip]


def make_caddy(parameters: dict) -> cq.Shape:
    caddy = parameters["caddy"]
    plate = parameters["nameplate"]
    wall = caddy["wall_thickness"]
    base = _rounded_box_xy(
        caddy["width"], caddy["depth"], caddy["base_thickness"], caddy["base_corner_radius"]
    )
    parts: list[cq.Shape] = [base]

    parts.append(
        _top_rounded_box(
            caddy["width"], wall, caddy["front_bank_height"], (0.0, 0.0, 0.0), caddy["edge_radius"]
        )
    )
    parts.append(
        _top_rounded_box(
            wall,
            caddy["rear_front_y"],
            caddy["front_bank_height"],
            (0.0, 0.0, 0.0),
            caddy["edge_radius"],
        )
    )
    parts.append(
        _top_rounded_box(
            wall,
            caddy["rear_front_y"],
            caddy["front_bank_height"],
            (caddy["small_tray_width"], 0.0, 0.0),
            caddy["edge_radius"],
        )
    )
    parts.append(
        _top_rounded_box(
            caddy["width"],
            wall,
            caddy["rear_front_height"],
            (0.0, caddy["rear_front_y"], 0.0),
            caddy["edge_radius"],
        )
    )
    parts.append(
        _top_rounded_box(
            caddy["width"],
            wall,
            caddy["rear_back_height"],
            (0.0, caddy["depth"] - wall, 0.0),
            caddy["edge_radius"],
        )
    )
    parts.append(_sloped_wall_x(parameters, 0.0, wall))
    parts.append(_sloped_wall_x(parameters, caddy["width"] - wall, wall))
    for partition in caddy["rear_partitions_x"]:
        parts.append(_sloped_wall_x(parameters, partition - wall / 2.0, wall))

    parts.append(
        _top_rounded_box(
            caddy["phone_cradle_width"],
            wall,
            caddy["phone_front_lip_height"],
            (caddy["phone_cradle_x"], caddy["phone_front_lip_y"], 0.0),
            caddy["edge_radius"],
        )
    )
    parts.append(_phone_backrest(parameters))
    parts.extend(
        _channel_parts(
            parameters,
            caddy["width"],
            plate["width"],
            plate["height"],
            plate["mount_bottom_z"],
        )
    )

    result = parts[0]
    for part in parts[1:]:
        result = result.fuse(part)
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("caddy chassis is not one valid solid")
    return result


def make_text_plate(
    parameters: dict,
    name: str,
    width: float | None = None,
    height: float | None = None,
) -> tuple[cq.Shape, dict]:
    source_plate = parameters["nameplate"]
    local = dict(source_plate)
    if width is not None:
        local["width"] = width
    if height is not None:
        local["height"] = height
    clean_name = sanitize_name(name, parameters)
    layout = text_layout(clean_name, local)
    base = (
        cq.Workplane("XY")
        .box(local["width"], local["height"], local["thickness"], centered=(False, False, False))
        .edges("|Z")
        .fillet(min(local["corner_radius"], min(local["width"], local["height"]) / 8.0))
        .val()
    )

    start_x = (local["width"] - layout["text_width"]) / 2.0
    start_y = (local["height"] - layout["text_height"]) / 2.0
    cursor = 0
    cutters: list[cq.Shape] = []
    pitch = layout["pitch"]
    pixel = layout["pixel_width"]
    inset = (pitch - pixel) / 2.0
    for character in clean_name:
        glyph = GLYPHS[character]
        glyph_width = len(glyph[0])
        for row_index, row in enumerate(glyph):
            for column_index, value in enumerate(row):
                if value != "1":
                    continue
                x_pos = start_x + (cursor + column_index) * pitch + inset
                y_pos = start_y + (6 - row_index) * pitch + inset
                cutters.append(
                    cq.Solid.makeBox(
                        pixel,
                        pixel,
                        local["engraving_depth"] + 0.1,
                        cq.Vector(x_pos, y_pos, local["thickness"] - local["engraving_depth"]),
                    )
                )
        cursor += glyph_width + 1
    if cutters:
        base = base.cut(cq.Compound.makeCompound(cutters)).clean()
    if not base.isValid() or len(base.Solids()) != 1:
        raise RuntimeError("personalized plate is not one valid solid")
    return base, {"sanitized_name": clean_name, **layout}


def nameplate_assembly_orientation(parameters: dict, print_shape: cq.Shape) -> cq.Shape:
    caddy = parameters["caddy"]
    plate = parameters["nameplate"]
    x_offset = (caddy["width"] - plate["width"]) / 2.0
    return (
        print_shape.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .translate((x_offset, -plate["back_clearance"], plate["mount_bottom_z"]))
        .clean()
    )


def make_fit_coupon(parameters: dict) -> tuple[cq.Shape, cq.Shape, dict]:
    coupon = parameters["coupon"]
    caddy = parameters["caddy"]
    plate = parameters["nameplate"]
    holder = cq.Solid.makeBox(
        coupon["holder_width"],
        coupon["holder_depth"],
        caddy["base_thickness"],
        cq.Vector(0.0, 0.0, 0.0),
    )
    holder = holder.fuse(
        cq.Solid.makeBox(
            coupon["holder_width"],
            caddy["wall_thickness"],
            coupon["holder_height"],
            cq.Vector(0.0, 0.0, 0.0),
        )
    )
    plate_bottom = 5.0
    for part in _channel_parts(
        parameters,
        coupon["holder_width"],
        coupon["plate_width"],
        coupon["plate_height"],
        plate_bottom,
    ):
        holder = holder.fuse(part)
    holder = holder.clean()

    coupon_plate, layout = make_text_plate(
        parameters,
        coupon["plate_text"],
        width=coupon["plate_width"],
        height=coupon["plate_height"],
    )
    layout["nominal_back_clearance_mm"] = plate["back_clearance"]
    layout["nominal_front_clearance_mm"] = plate["channel_clearance"]
    if not holder.isValid() or len(holder.Solids()) != 1:
        raise RuntimeError("fit coupon holder is not one valid solid")
    return holder, coupon_plate, layout


def move_to_origin(shape: cq.Shape) -> cq.Shape:
    bounds = shape.BoundingBox()
    return shape.translate(cq.Vector(-bounds.xmin, -bounds.ymin, -bounds.zmin))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_step(shape: cq.Shape, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path), exportType="STEP")


def export_stl(shape: cq.Shape, path: Path, tolerance: float, angular_tolerance: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(
        move_to_origin(shape),
        str(path),
        tolerance=tolerance,
        angularTolerance=angular_tolerance,
    )


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    components = mesh.split(only_watertight=False)
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_file(path),
        "triangles": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "file_bytes": path.stat().st_size,
        "file_mib": path.stat().st_size / (1024.0 * 1024.0),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "positive_volume": bool(mesh.volume > 0.0),
        "components": int(len(components)),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "extents_mm": np.round(mesh.extents, 4).tolist(),
        "bounds_mm": np.round(mesh.bounds, 4).tolist(),
        "center_mass_mm": np.round(mesh.center_mass, 4).tolist(),
    }


def _zip_member(name: str, data: bytes, archive: zipfile.ZipFile) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def write_3mf(path: Path, part_paths: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> None:
    namespace = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", namespace)
    model = ET.Element(f"{{{namespace}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources = ET.SubElement(model, f"{{{namespace}}}resources")
    build = ET.SubElement(model, f"{{{namespace}}}build")
    for object_id, ((name, mesh_path), (move_x, move_y)) in enumerate(zip(part_paths, placements), 1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        obj = ET.SubElement(
            resources,
            f"{{{namespace}}}object",
            {"id": str(object_id), "type": "model", "name": name},
        )
        mesh_node = ET.SubElement(obj, f"{{{namespace}}}mesh")
        vertices_node = ET.SubElement(mesh_node, f"{{{namespace}}}vertices")
        for x_coord, y_coord, z_coord in mesh.vertices:
            ET.SubElement(
                vertices_node,
                f"{{{namespace}}}vertex",
                {"x": f"{x_coord:.6f}", "y": f"{y_coord:.6f}", "z": f"{z_coord:.6f}"},
            )
        triangles_node = ET.SubElement(mesh_node, f"{{{namespace}}}triangles")
        for first, second, third in mesh.faces:
            ET.SubElement(
                triangles_node,
                f"{{{namespace}}}triangle",
                {"v1": str(int(first)), "v2": str(int(second)), "v3": str(int(third))},
            )
        ET.SubElement(
            build,
            f"{{{namespace}}}item",
            {
                "objectid": str(object_id),
                "transform": f"1 0 0 0 1 0 0 0 1 {move_x:.3f} {move_y:.3f} 0",
            },
        )
    content_types = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        b'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        b'<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        b'</Types>'
    )
    relationships = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Target="/3D/3dmodel.model" Id="r0" '
        b'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        b'</Relationships>'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        _zip_member("[Content_Types].xml", content_types, archive)
        _zip_member("_rels/.rels", relationships, archive)
        _zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive)
        _zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)


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


def main() -> None:
    parameters = load_parameters()
    validate_parameters(parameters)
    caddy = parameters["caddy"]
    plate_parameters = parameters["nameplate"]
    export = parameters["export"]
    clean_name = sanitize_name(parameters["personalization"]["name"], parameters)

    body = make_caddy(parameters)
    plate_print, font_layout = make_text_plate(parameters, clean_name)
    plate_assembly = nameplate_assembly_orientation(parameters, plate_print)
    coupon_holder, coupon_plate, coupon_layout = make_fit_coupon(parameters)

    assembly = cq.Compound.makeCompound([body, plate_assembly])
    step_shapes = {
        "caddy-chassis": body,
        "personalized-nameplate-assembly": plate_assembly,
        "caddy-assembly": assembly,
    }
    print_shapes = {
        "caddy-chassis": body,
        "personalized-nameplate": plate_print,
    }
    coupon_shapes = {
        "nameplate-fit-coupon-holder": coupon_holder,
        "nameplate-fit-coupon-plate": coupon_plate,
    }

    for name, shape in step_shapes.items():
        export_step(shape, MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step")

    master_metrics: dict[str, dict] = {}
    manufacturing_metrics: dict[str, dict] = {}
    manufacturing_paths: dict[str, Path] = {}
    for name, shape in print_shapes.items():
        master_path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}-master.stl"
        manufacturing_path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shape, master_path, export["master_chordal_tolerance"], export["angular_tolerance"] / 2.0)
        export_stl(
            shape,
            manufacturing_path,
            export["manufacturing_chordal_tolerance"],
            export["angular_tolerance"],
        )
        master_metrics[name] = mesh_metrics(master_path)
        manufacturing_metrics[name] = mesh_metrics(manufacturing_path)
        manufacturing_paths[name] = manufacturing_path

    coupon_metrics: dict[str, dict] = {}
    for name, shape in coupon_shapes.items():
        path = COUPONS / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shape, path, export["manufacturing_chordal_tolerance"], export["angular_tolerance"])
        coupon_metrics[name] = mesh_metrics(path)

    print_set = THREE_MF / f"DRAFT-{PROJECT_ID}-personalized-stationery-caddy-{REVISION}.3mf"
    write_3mf(
        print_set,
        list(manufacturing_paths.items()),
        [(5.0, 5.0), (5.0, caddy["depth"] + 12.0)],
    )

    mesh_checks: list[dict] = []
    for name, metrics in {**manufacturing_metrics, **coupon_metrics}.items():
        mesh_checks.extend(
            [
                check(f"{name}:watertight", metrics["watertight"], f"{name} is watertight"),
                check(f"{name}:winding", metrics["winding_consistent"], f"{name} winding is consistent"),
                check(f"{name}:volume", metrics["positive_volume"], f"{name} has positive volume"),
                check(f"{name}:component", metrics["components"] == 1, f"{name} is one component"),
                check(
                    f"{name}:triangles",
                    metrics["triangles"] <= export["mesh_triangle_budget_each"],
                    f"{name} is within the triangle budget",
                    {"triangles": metrics["triangles"], "budget": export["mesh_triangle_budget_each"]},
                ),
                check(
                    f"{name}:file-size",
                    metrics["file_mib"] <= export["mesh_file_budget_mib_each"],
                    f"{name} is within the mesh-file budget",
                    {"file_mib": metrics["file_mib"], "budget_mib": export["mesh_file_budget_mib_each"]},
                ),
            ]
        )
    mesh_report = report(
        f"{PROJECT_ID}-mesh-generation",
        [PARAMETERS, Path(__file__)],
        mesh_checks,
        {
            "manufacturing_meshes": manufacturing_metrics,
            "coupon_meshes": coupon_metrics,
            "master_meshes": master_metrics,
        },
        ["Topology checks do not prove physical fit, surface finish, stability or print quality."],
    )
    write_json(VALIDATION / "mesh-generation-report.json", mesh_report)

    slot_bottom = caddy["phone_backrest_y"] - (
        caddy["phone_front_lip_y"] + caddy["wall_thickness"]
    )
    plate_slot_depth = plate_parameters["thickness"] + 2.0 * plate_parameters["channel_clearance"]
    interface_report = report(
        f"{PROJECT_ID}-interface-validation",
        [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
        [
            check(
                "font-independent",
                set(clean_name).issubset(GLYPHS),
                "Personalization resolves only to embedded geometric glyphs",
                font_layout,
            ),
            check(
                "minimum-pixel",
                font_layout["pixel_width"] >= plate_parameters["minimum_pixel_width"],
                "Smallest engraved pixel is above the declared FDM minimum",
                font_layout,
            ),
            check(
                "plate-channel-clearance",
                plate_parameters["channel_clearance"] >= 0.2,
                "Nameplate channel has explicit per-side manufacturing clearance",
                {
                    "per_side_clearance_mm": plate_parameters["channel_clearance"],
                    "nominal_slot_depth_mm": plate_slot_depth,
                },
            ),
            check(
                "phone-case-envelope",
                slot_bottom >= caddy["maximum_phone_case_thickness"] + 0.5,
                "Phone slot bottom clears the declared maximum case thickness",
                {
                    "slot_bottom_mm": slot_bottom,
                    "maximum_case_thickness_mm": caddy["maximum_phone_case_thickness"],
                },
            ),
            check(
                "closed-bottom",
                caddy["base_thickness"] >= 2.4,
                "All stationery wells use a continuous closed base",
                {"base_thickness_mm": caddy["base_thickness"]},
            ),
            check(
                "print-envelope",
                all(
                    metrics["extents_mm"][0] <= parameters["limits"]["maximum_part_envelope"][0]
                    and metrics["extents_mm"][1] <= parameters["limits"]["maximum_part_envelope"][1]
                    and metrics["extents_mm"][2] <= parameters["limits"]["maximum_part_envelope"][2]
                    for metrics in manufacturing_metrics.values()
                ),
                "All production parts fit the declared printer envelope",
                {name: metrics["extents_mm"] for name, metrics in manufacturing_metrics.items()},
            ),
        ],
        {
            "sanitized_name": clean_name,
            "font_layout": font_layout,
            "coupon_layout": coupon_layout,
            "physical_nameplate_fit": "NOT_RUN",
            "loaded_phone_stability": "NOT_RUN",
            "tall_item_tip_test": "NOT_RUN",
        },
        ["Nominal clearances and analytic envelopes do not replace the deferred physical checks."],
    )
    write_json(VALIDATION / "interface-report.json", interface_report)

    baseline_volume = caddy["width"] * caddy["depth"] * caddy["rear_back_height"]
    selected_volume = float(body.Volume())
    volume_reduction = 100.0 * (baseline_volume - selected_volume) / baseline_volume
    optimization_report = report(
        f"{PROJECT_ID}-optimization-comparison",
        [PARAMETERS, Path(__file__), ROOT / "protected-geometry-map.md"],
        [
            check("protected-map", True, "Protected geometry map is present"),
            check(
                "shell-volume-reduction",
                volume_reduction >= 65.0,
                "Open shell and stepped walls materially reduce CAD volume",
                {"cad_volume_reduction_percent": volume_reduction},
            ),
            check(
                "support-free-orientation",
                caddy["phone_backrest_tilt_offset"] / (
                    caddy["phone_backrest_height"] - caddy["base_thickness"]
                )
                < math.tan(math.radians(20.0)),
                "Phone backrest slope remains close to vertical and support-free",
            ),
        ],
        {
            "baseline_bounding_block_volume_mm3": baseline_volume,
            "selected_caddy_volume_mm3": selected_volume,
            "cad_volume_reduction_percent": volume_reduction,
            "exact_slicer_material_and_time": "NOT_RUN",
        },
        ["CAD volume is not deposited mass or print time; exact slicer metrics remain deferred."],
    )
    write_json(REPORTS / "optimization-comparison.json", optimization_report)

    mesh_policy = {
        "project_id": PROJECT_ID,
        "revision": REVISION,
        "decision": "not-beneficial",
        "master_tessellation_mm": export["master_chordal_tolerance"],
        "manufacturing_tessellation_mm": export["manufacturing_chordal_tolerance"],
        "downstream_decimation": False,
        "reason": "Analytic planar and filleted CAD is already far below resource budgets; decimation would only weaken engraved glyph and channel evidence.",
        "master_meshes": master_metrics,
        "manufacturing_meshes": manufacturing_metrics,
        "slicer_resolution_check": "NOT_RUN",
    }
    write_json(REPORTS / "mesh-complexity.json", mesh_policy)

    source_report = report(
        f"{PROJECT_ID}-parametric-source",
        [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml", ROOT / "decomposition.md"],
        [
            check("parameters", True, "Default and boundary assertions pass"),
            check("part-count", len(print_shapes) == 2, "Chassis and personalized plate are generated"),
            check("coupon-count", len(coupon_shapes) == 2, "Two-part nameplate fit coupon is generated"),
            check("mesh-generation", mesh_report["status"] == "PASS", "Mesh generation checks pass"),
            check("interfaces", interface_report["status"] == "PASS", "Nominal interface checks pass"),
            check("optimization", optimization_report["status"] == "PASS", "Shell optimization checks pass"),
            check("3mf", print_set.is_file(), "Two-object DRAFT 3MF exists"),
        ],
        {
            "parts": list(print_shapes),
            "coupons": list(coupon_shapes),
            "print_set": str(print_set.relative_to(ROOT)),
            "print_set_sha256": sha256_file(print_set),
        },
        ["Exact slicer preflight, physical fit, stability, finish and watermark approval are deferred."],
    )
    write_json(VALIDATION / "parametric-source-report.json", source_report)

    write_json(
        REPORTS / "build-manifest.json",
        {
            "project_id": PROJECT_ID,
            "portfolio_sku": parameters["project"]["portfolio_sku"],
            "revision": REVISION,
            "status": "DRAFT",
            "source": str(Path(__file__).relative_to(ROOT)),
            "parameters": input_record(PARAMETERS),
            "sanitized_name": clean_name,
            "font_layout": font_layout,
            "manufacturing_parts": manufacturing_metrics,
            "coupon_parts": coupon_metrics,
            "master_parts": master_metrics,
            "print_set": str(print_set.relative_to(ROOT)),
            "print_set_sha256": sha256_file(print_set),
            "physical_validation": "DEFERRED",
            "watermark": "NOT_INTEGRATED_RELEASE_BLOCKER",
        },
    )
    write_json(
        REPORTS / "environment.json",
        {
            "python": platform.python_version(),
            "cadquery": getattr(cq, "__version__", "unknown"),
            "trimesh": trimesh.__version__,
            "numpy": np.__version__,
            "units": "mm",
        },
    )

    all_reports = (mesh_report, interface_report, optimization_report, source_report)
    if not all(item["status"] == "PASS" for item in all_reports):
        raise RuntimeError("one or more required build reports failed")
    print(
        json.dumps(
            {
                "status": "PASS",
                "project_id": PROJECT_ID,
                "revision": REVISION,
                "sanitized_name": clean_name,
                "font_pixel_width_mm": font_layout["pixel_width"],
                "parts": {name: metrics["extents_mm"] for name, metrics in manufacturing_metrics.items()},
                "coupons": {name: metrics["extents_mm"] for name, metrics in coupon_metrics.items()},
                "print_set": str(print_set),
                "cad_volume_reduction_percent": volume_reduction,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
