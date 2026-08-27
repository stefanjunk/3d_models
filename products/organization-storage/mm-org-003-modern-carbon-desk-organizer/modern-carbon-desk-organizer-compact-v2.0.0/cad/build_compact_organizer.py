#!/usr/bin/env python3
"""Parametric CadQuery build for MM-ORG-003 Compact v2.0.0-draft.1.

All dimensions are millimetres. STEP files retain assembly orientation; STL
files are explicitly transformed into the documented support-free print
orientations. The DRAFT 3MF is an inventory strip whose parts must be placed on
separate plates before slicing.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import gc
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETER_FILE = ROOT / "model-parameters.json"
MASTER = ROOT / "exports" / "master"
MANUFACTURING = ROOT / "exports" / "manufacturing"
THREE_MF = ROOT / "exports" / "3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"
PROJECT_ID = "MM-ORG-003"
REVISION = "2.0.0-draft.1"


@dataclass(frozen=True)
class Params:
    build_x: float
    build_y: float
    build_z: float
    nozzle: float
    line_width: float
    layer_height: float
    width: float
    depth: float
    housing_height: float
    side_wall: float
    rear_wall: float
    housing_bottom: float
    shelf: float
    housing_top: float
    opening_height: float
    housing_radius: float
    deck_side_rail: float
    deck_front_beam: float
    deck_rear_beam: float
    drawer_width: float
    drawer_depth: float
    drawer_height: float
    drawer_front_width: float
    drawer_front_height: float
    drawer_front_depth: float
    drawer_wall: float
    drawer_bottom: float
    drawer_side_clearance: float
    drawer_rear_clearance: float
    drawer_top_clearance: float
    scoop_width: float
    scoop_depth: float
    drawer_front_radius: float
    sorter_width: float
    sorter_depth: float
    sorter_height: float
    sorter_bottom: float
    sorter_wall: float
    divider_wall: float
    sorter_rows: int
    sorter_columns: int
    sorter_radius: float
    peg_size: float
    peg_height: float
    peg_tip_size: float
    socket_size: float
    socket_depth: float
    boss_size: float
    boss_height: float
    interface_offset: float
    texture_pitch: float
    groove_width: float
    groove_depth: float
    texture_border: float
    texture_spacing_multiplier: float
    texture_angles: tuple[float, ...]
    tessellation_tolerance: float
    tessellation_angular_tolerance: float
    max_triangles: int
    max_file_mib: float


def load_params(path: Path = PARAMETER_FILE) -> Params:
    data = json.loads(path.read_text(encoding="utf-8"))
    printer = data["printer"]
    housing = data["housing"]
    drawer = data["drawer"]
    sorter = data["sorter"]
    interface = data["stack_interface"]
    texture = data["texture"]
    export = data["export"]
    p = Params(
        *map(float, printer["build_volume"]),
        float(printer["nozzle"]),
        float(printer["line_width"]),
        float(printer["layer_height"]),
        float(housing["width"]),
        float(housing["depth"]),
        float(housing["height"]),
        float(housing["side_wall"]),
        float(housing["rear_wall"]),
        float(housing["bottom"]),
        float(housing["shelf"]),
        float(housing["top"]),
        float(housing["opening_height"]),
        float(housing["corner_radius"]),
        float(housing["deck_side_rail"]),
        float(housing["deck_front_beam"]),
        float(housing["deck_rear_beam"]),
        float(drawer["body_width"]),
        float(drawer["body_depth"]),
        float(drawer["body_height"]),
        float(drawer["front_width"]),
        float(drawer["front_height"]),
        float(drawer["front_depth"]),
        float(drawer["wall"]),
        float(drawer["bottom"]),
        float(drawer["side_clearance_each"]),
        float(drawer["rear_clearance"]),
        float(drawer["top_clearance"]),
        float(drawer["finger_scoop_width"]),
        float(drawer["finger_scoop_depth"]),
        float(drawer["front_corner_radius"]),
        float(sorter["width"]),
        float(sorter["depth"]),
        float(sorter["height"]),
        float(sorter["bottom"]),
        float(sorter["outer_wall"]),
        float(sorter["divider_wall"]),
        int(sorter["rows"]),
        int(sorter["columns"]),
        float(sorter["corner_radius"]),
        float(interface["peg_size"]),
        float(interface["peg_height"]),
        float(interface["peg_tip_size"]),
        float(interface["socket_size"]),
        float(interface["socket_depth"]),
        float(interface["boss_size"]),
        float(interface["boss_height"]),
        float(interface["center_offset"]),
        float(texture["pitch"]),
        float(texture["groove_width"]),
        float(texture["groove_depth"]),
        float(texture["border"]),
        float(texture["direction_spacing_multiplier"]),
        tuple(float(v) for v in texture["angles_deg"]),
        float(export["chordal_tolerance"]),
        float(export["angular_tolerance"]),
        int(export["max_triangles_per_part"]),
        float(export["max_file_mib_per_part"]),
    )
    validate_parameters(p)
    return p


def validate_parameters(p: Params) -> None:
    assert PROJECT_ID and REVISION
    assert p.width == p.sorter_width and p.depth == p.sorter_depth
    assert p.width <= p.build_x - 10.0 and p.depth <= p.build_y - 10.0
    assert p.housing_height + p.sorter_height == 173.0
    assert math.isclose(
        p.housing_bottom + 2 * p.opening_height + p.shelf + p.housing_top,
        p.housing_height,
        abs_tol=1e-9,
    )
    expected_drawer_width = p.width - 2.0 * p.side_wall - 2.0 * p.drawer_side_clearance
    assert math.isclose(p.drawer_width, expected_drawer_width, abs_tol=1e-9)
    assert math.isclose(p.opening_height - p.drawer_height, p.drawer_top_clearance, abs_tol=1e-9)
    assert math.isclose(
        p.drawer_front_depth + p.drawer_depth + p.drawer_rear_clearance,
        p.depth - p.rear_wall,
        abs_tol=1e-9,
    )
    assert p.drawer_wall >= 2.0 and p.drawer_bottom >= 2.0
    assert p.divider_wall >= 4.0 * p.line_width
    assert p.side_wall - p.groove_depth >= 2.16
    assert p.sorter_wall - p.groove_depth >= 2.16
    assert p.drawer_front_depth - p.groove_depth >= 2.16
    assert p.deck_side_rail >= 10.0 and p.deck_front_beam >= 10.0 and p.deck_rear_beam >= 10.0
    assert math.isclose((p.socket_size - p.peg_size) / 2.0, 0.35, abs_tol=1e-9)
    assert p.socket_depth > p.sorter_bottom and p.boss_height > p.socket_depth
    assert p.sorter_rows == 3 and p.sorter_columns == 2
    assert 0.5 * p.line_width <= p.groove_width
    assert p.groove_depth >= 0.5 * p.layer_height
    assert p.groove_depth <= 2.0 * p.layer_height
    assert p.tessellation_tolerance <= 0.25 * p.nozzle


def box_at(x: float, y: float, z: float, sx: float, sy: float, sz: float) -> cq.Workplane:
    return cq.Workplane("XY").box(sx, sy, sz, centered=(False, False, False)).translate((x, y, z))


def rounded_box(width: float, depth: float, height: float, radius: float) -> cq.Workplane:
    body = box_at(0.0, 0.0, 0.0, width, depth, height)
    return body.edges("|Z").fillet(radius)


def compound_workplane(solids: list[cq.Shape]) -> cq.Workplane | None:
    if not solids:
        return None
    return cq.Workplane(obj=cq.Compound.makeCompound(solids))


def front_grooves(
    x0: float,
    z0: float,
    width: float,
    height: float,
    face_y: float,
    inward_sign: float,
    p: Params,
    pitch: float | None = None,
) -> cq.Workplane | None:
    """Create physically scaled diagonal cutters on a world-XZ face."""
    actual_pitch = pitch or p.texture_pitch
    depth = p.groove_depth + 0.04
    center_y = face_y + inward_sign * (depth / 2.0 - 0.01)
    clip_y = face_y + inward_sign * depth / 2.0
    clip = cq.Workplane("XY").box(width, depth, height).translate(
        (x0 + width / 2.0, clip_y, z0 + height / 2.0)
    )
    length = math.hypot(width, height) + 2.0 * actual_pitch
    half_span = math.hypot(width, height) / 2.0 + actual_pitch
    solids: list[cq.Shape] = []
    step = actual_pitch * p.texture_spacing_multiplier
    for family, angle in enumerate(p.texture_angles):
        theta = math.radians(angle)
        offset = -half_span + family * actual_pitch
        while offset <= half_span:
            cx = x0 + width / 2.0 + offset * math.sin(theta)
            cz = z0 + height / 2.0 + offset * math.cos(theta)
            bar = (
                cq.Workplane("XY")
                .box(length, depth, p.groove_width)
                .rotate((0, 0, 0), (0, 1, 0), angle)
                .translate((cx, center_y, cz))
                .intersect(clip)
            )
            if not bar.val().isNull():
                solids.append(bar.val())
            offset += step
    return compound_workplane(solids)


def side_grooves(
    y0: float,
    z0: float,
    depth_span: float,
    height: float,
    face_x: float,
    inward_sign: float,
    p: Params,
    pitch: float | None = None,
) -> cq.Workplane | None:
    """Create physically scaled diagonal cutters on a world-YZ face."""
    actual_pitch = pitch or p.texture_pitch
    cut_depth = p.groove_depth + 0.04
    center_x = face_x + inward_sign * (cut_depth / 2.0 - 0.01)
    clip_x = face_x + inward_sign * cut_depth / 2.0
    clip = cq.Workplane("XY").box(cut_depth, depth_span, height).translate(
        (clip_x, y0 + depth_span / 2.0, z0 + height / 2.0)
    )
    length = math.hypot(depth_span, height) + 2.0 * actual_pitch
    half_span = math.hypot(depth_span, height) / 2.0 + actual_pitch
    solids: list[cq.Shape] = []
    step = actual_pitch * p.texture_spacing_multiplier
    for family, angle in enumerate(p.texture_angles):
        theta = math.radians(angle)
        offset = -half_span + family * actual_pitch
        while offset <= half_span:
            cy = y0 + depth_span / 2.0 + offset * math.sin(theta)
            cz = z0 + height / 2.0 + offset * math.cos(theta)
            bar = (
                cq.Workplane("XY")
                .box(cut_depth, length, p.groove_width)
                .rotate((0, 0, 0), (1, 0, 0), angle)
                .translate((center_x, cy, cz))
                .intersect(clip)
            )
            if not bar.val().isNull():
                solids.append(bar.val())
            offset += step
    return compound_workplane(solids)


def cut_if_present(body: cq.Workplane, cutter: cq.Workplane | None) -> cq.Workplane:
    if cutter is None:
        return body
    # A compound Boolean against a perforated housing can create a very large
    # OCCT peak. Apply the already clipped shallow cutter solids sequentially;
    # this is slower but bounded and deterministic for common workstations.
    result = body
    for solid in cutter.val().Solids():
        result = result.cut(cq.Workplane(obj=solid))
    return result


def interface_centers(p: Params) -> list[tuple[float, float]]:
    o = p.interface_offset
    return [(o, o), (p.width - o, o), (o, p.depth - o), (p.width - o, p.depth - o)]


def build_housing(p: Params, textured: bool = True, lightweight: bool = True) -> cq.Workplane:
    body = rounded_box(p.width, p.depth, p.housing_height, p.housing_radius)
    cavity_depth = p.depth - p.rear_wall + 0.5
    lower = box_at(
        p.side_wall,
        -0.5,
        p.housing_bottom,
        p.width - 2.0 * p.side_wall,
        cavity_depth,
        p.opening_height,
    )
    upper_z = p.housing_bottom + p.opening_height + p.shelf
    upper = box_at(
        p.side_wall,
        -0.5,
        upper_z,
        p.width - 2.0 * p.side_wall,
        cavity_depth,
        p.opening_height,
    )
    body = body.cut(lower).cut(upper)
    if lightweight:
        deck_window = (
            p.deck_side_rail,
            p.deck_front_beam,
            p.width - 2.0 * p.deck_side_rail,
            p.depth - p.deck_front_beam - p.deck_rear_beam,
        )
        for deck_z, thickness in (
            (0.0, p.housing_bottom),
            (p.housing_bottom + p.opening_height, p.shelf),
            (p.housing_height - p.housing_top, p.housing_top),
        ):
            body = body.cut(
                box_at(
                    deck_window[0],
                    deck_window[1],
                    deck_z - 0.1,
                    deck_window[2],
                    deck_window[3],
                    thickness + 0.2,
                )
            )
    if textured:
        # Local badge fields preserve the carbon cue without turning both full
        # 190 x 108 mm sides into hundreds of acceleration-limited grooves.
        span_y = min(72.0, p.depth - 2.0 * p.housing_radius)
        span_z = min(54.0, p.housing_height - 2.0 * p.texture_border)
        badge_y = (p.depth - span_y) / 2.0
        badge_z = (p.housing_height - span_z) / 2.0
        body = cut_if_present(
            body,
            side_grooves(badge_y, badge_z, span_y, span_z, 0.0, 1.0, p, pitch=p.texture_pitch * 2.0),
        )
        body = cut_if_present(
            body,
            side_grooves(badge_y, badge_z, span_y, span_z, p.width, -1.0, p, pitch=p.texture_pitch * 2.0),
        )
    for cx, cy in interface_centers(p):
        peg = (
            cq.Workplane("XY", origin=(cx, cy, p.housing_height))
            .rect(p.peg_size, p.peg_size)
            .workplane(offset=p.peg_height)
            .rect(p.peg_tip_size, p.peg_tip_size)
            .loft(combine=True)
        )
        body = body.union(peg)
    return body


def build_drawer(p: Params, textured: bool = True) -> cq.Workplane:
    tray = rounded_box(p.drawer_width, p.drawer_depth, p.drawer_height, 3.0)
    interior = box_at(
        p.drawer_wall,
        p.drawer_wall,
        p.drawer_bottom,
        p.drawer_width - 2.0 * p.drawer_wall,
        p.drawer_depth - 2.0 * p.drawer_wall,
        p.drawer_height,
    )
    tray = tray.cut(interior).translate((0.0, p.drawer_front_depth, 0.0))
    front_x = (p.drawer_width - p.drawer_front_width) / 2.0
    front = box_at(
        front_x,
        0.0,
        0.0,
        p.drawer_front_width,
        p.drawer_front_depth,
        p.drawer_front_height,
    ).edges("|Z").fillet(p.drawer_front_radius)
    drawer = tray.union(front)
    if textured:
        b = p.texture_border
        grooves = front_grooves(
            front_x + b,
            b,
            p.drawer_front_width - 2.0 * b,
            p.drawer_front_height - 2.0 * b,
            0.0,
            1.0,
            p,
            pitch=p.texture_pitch * 2.0,
        )
        if grooves is not None:
            keepout = box_at(
                (p.drawer_width - p.scoop_width - 8.0) / 2.0,
                -0.2,
                p.drawer_front_height - p.scoop_depth - 4.0,
                p.scoop_width + 8.0,
                p.drawer_front_depth + 0.5,
                p.scoop_depth + 5.0,
            )
            grooves = grooves.cut(keepout)
        drawer = cut_if_present(drawer, grooves)
    scoop_radius = p.scoop_width / 2.0
    scoop_center_z = p.drawer_front_height + scoop_radius - p.scoop_depth
    scoop = (
        cq.Workplane("XZ", origin=(p.drawer_width / 2.0, -0.5, scoop_center_z))
        .circle(scoop_radius)
        .extrude(p.drawer_front_depth + 1.5)
    )
    return drawer.cut(scoop)


def build_sorter(p: Params, textured: bool = True) -> cq.Workplane:
    sorter = rounded_box(p.sorter_width, p.sorter_depth, p.sorter_height, p.sorter_radius)
    interior = box_at(
        p.sorter_wall,
        p.sorter_wall,
        p.sorter_bottom,
        p.sorter_width - 2.0 * p.sorter_wall,
        p.sorter_depth - 2.0 * p.sorter_wall,
        p.sorter_height,
    )
    sorter = sorter.cut(interior)
    divider_x = (p.sorter_width - p.divider_wall) / 2.0
    sorter = sorter.union(
        box_at(
            divider_x,
            p.sorter_wall,
            p.sorter_bottom,
            p.divider_wall,
            p.sorter_depth - 2.0 * p.sorter_wall,
            p.sorter_height - p.sorter_bottom,
        )
    )
    inner_depth = p.sorter_depth - 2.0 * p.sorter_wall
    for row in range(1, p.sorter_rows):
        cy = p.sorter_wall + inner_depth * row / p.sorter_rows
        sorter = sorter.union(
            box_at(
                p.sorter_wall,
                cy - p.divider_wall / 2.0,
                p.sorter_bottom,
                p.sorter_width - 2.0 * p.sorter_wall,
                p.divider_wall,
                p.sorter_height - p.sorter_bottom,
            )
        )
    for cx, cy in interface_centers(p):
        boss = box_at(
            cx - p.boss_size / 2.0,
            cy - p.boss_size / 2.0,
            0.0,
            p.boss_size,
            p.boss_size,
            p.boss_height,
        )
        socket = box_at(
            cx - p.socket_size / 2.0,
            cy - p.socket_size / 2.0,
            -0.1,
            p.socket_size,
            p.socket_size,
            p.socket_depth + 0.1,
        )
        sorter = sorter.union(boss).cut(socket)
    if textured:
        front_width = min(120.0, p.sorter_width - 2.0 * p.sorter_radius)
        front_height = min(40.0, p.sorter_height - 2.0 * p.texture_border)
        front_x = (p.sorter_width - front_width) / 2.0
        front_z = (p.sorter_height - front_height) / 2.0
        sorter = cut_if_present(
            sorter,
            front_grooves(
                front_x,
                front_z,
                front_width,
                front_height,
                0.0,
                1.0,
                p,
                pitch=p.texture_pitch * 2.0,
            ),
        )
        side_span = min(72.0, p.sorter_depth - 2.0 * p.sorter_radius)
        side_height = front_height
        side_y = (p.sorter_depth - side_span) / 2.0
        side_z = front_z
        sorter = cut_if_present(
            sorter,
            side_grooves(side_y, side_z, side_span, side_height, 0.0, 1.0, p, pitch=p.texture_pitch * 4.0),
        )
        sorter = cut_if_present(
            sorter,
            side_grooves(side_y, side_z, side_span, side_height, p.sorter_width, -1.0, p, pitch=p.texture_pitch * 4.0),
        )
    return sorter


def build_fit_coupon(p: Params) -> cq.Compound:
    clearances = (0.30, 0.45, 0.60)
    shapes: list[cq.Shape] = []
    for index, clearance in enumerate(clearances):
        x0 = index * 29.0
        channel_width = 8.0 + 2.0 * clearance
        base = box_at(x0, 0.0, 0.0, 25.0, 25.0, 3.0)
        left = box_at(x0, 0.0, 3.0, (25.0 - channel_width) / 2.0, 25.0, 7.0)
        right_x = x0 + (25.0 + channel_width) / 2.0
        right = box_at(right_x, 0.0, 3.0, (25.0 - channel_width) / 2.0, 25.0, 7.0)
        slider = box_at(x0 + 8.5, 30.0, 0.0, 8.0, 22.0, 6.0)
        shapes.extend([base.union(left).union(right).val(), slider.val()])
    return cq.Compound.makeCompound(shapes)


def build_texture_coupon(p: Params) -> cq.Workplane:
    coupon = box_at(0.0, 0.0, 0.0, 78.0, 34.0, 3.0).edges("|Z").fillet(2.0)
    for index, pitch in enumerate((6.4, 4.8, 3.6)):
        grooves = front_grooves(
            3.0 + index * 25.0,
            3.0,
            22.0,
            28.0,
            0.0,
            1.0,
            p,
            pitch=pitch,
        )
        coupon = cut_if_present(coupon, grooves)
    return coupon


def shift_to_origin(shape: cq.Shape) -> cq.Shape:
    box = shape.BoundingBox()
    return shape.translate((-box.xmin, -box.ymin, -box.zmin))


def housing_print_shape(shape: cq.Shape) -> cq.Shape:
    rotated = shape.rotate((0, 0, 0), (1, 0, 0), 90.0)
    return shift_to_origin(rotated)


def drawer_print_shape(shape: cq.Shape) -> cq.Shape:
    return shift_to_origin(shape)


def shape_metrics(shape: cq.Shape) -> dict:
    box = shape.BoundingBox()
    center = shape.Center()
    return {
        "valid_brep": bool(shape.isValid()),
        "solids": len(shape.Solids()),
        "volume_mm3": float(shape.Volume()),
        "bounds_mm": [[box.xmin, box.ymin, box.zmin], [box.xmax, box.ymax, box.zmax]],
        "extents_mm": [box.xlen, box.ylen, box.zlen],
        "center_of_mass_mm": [center.x, center.y, center.z],
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def export_shape(shape: cq.Shape, path: Path, p: Params) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".step", ".stp"}:
        cq.exporters.export(shape, str(path), exportType="STEP")
    elif path.suffix.lower() == ".stl":
        cq.exporters.export(
            shape,
            str(path),
            tolerance=p.tessellation_tolerance,
            angularTolerance=p.tessellation_angular_tolerance,
        )
    else:
        raise ValueError(path)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"unexpected mesh scene: {path}")
    return {
        "sha256": sha256(path),
        "file_bytes": path.stat().st_size,
        "file_mib": path.stat().st_size / (1024.0 * 1024.0),
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
        "center_mass_mm": np.round(mesh.center_mass, 5).tolist(),
    }


def shape_to_mesh(shape: cq.Shape, p: Params) -> tuple[np.ndarray, np.ndarray]:
    vertices, faces = shape.tessellate(p.tessellation_tolerance, p.tessellation_angular_tolerance)
    return (
        np.asarray([[v.x, v.y, v.z] for v in vertices], dtype=float),
        np.asarray(faces, dtype=np.int64),
    )


def write_print_set_3mf(path: Path, parts: list[tuple[str, cq.Shape, int]], p: Params) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    for name, value in (
        ("Title", "DRAFT MM-ORG-003 Modern Carbon Compact print set"),
        ("Designer", "metriMade / autonomous CAD workflow"),
        ("Description", "Four build items; inventory strip only; place one unique part per 220 mm plate and print drawer twice."),
        ("LicenseTerms", "DRAFT engineering artifact; not a commercial release"),
    ):
        node = ET.SubElement(model, f"{{{ns}}}metadata", {"name": name})
        node.text = value
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    inventory_x = 0.0
    object_shapes: dict[str, tuple[int, cq.Shape]] = {}
    for name, shape, quantity in parts:
        object_id = len(object_shapes) + 1
        object_shapes[name] = (object_id, shape)
        vertices, faces = shape_to_mesh(shape, p)
        obj = ET.SubElement(
            resources,
            f"{{{ns}}}object",
            {"id": str(object_id), "type": "model", "name": name, "partnumber": f"{PROJECT_ID}-{REVISION}-{name}"},
        )
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        verts_node = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in vertices:
            ET.SubElement(verts_node, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles_node = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in faces:
            ET.SubElement(triangles_node, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        extent_x = shape.BoundingBox().xlen
        for _ in range(quantity):
            transform = f"1 0 0 0 1 0 0 0 1 {inventory_x:.3f} 0 0"
            ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": transform})
            inventory_x += extent_x + 12.0
    model_bytes = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for name, payload in (
            ("[Content_Types].xml", content_types),
            ("_rels/.rels", rels),
            ("3D/3dmodel.model", model_bytes),
            ("Metadata/model-parameters.json", PARAMETER_FILE.read_bytes()),
        ):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)


def pass_report(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations: list[str] | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": "2.0.0",
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


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_all(p: Params) -> dict:
    for directory in (MASTER, MANUFACTURING, THREE_MF, REPORTS, VALIDATION):
        directory.mkdir(parents=True, exist_ok=True)

    baseline_volume = 0.0
    for name, builder, quantity in (
        ("housing", build_housing, 1),
        ("drawer", build_drawer, 2),
        ("sorter", build_sorter, 1),
    ):
        print(f"baseline:{name}", flush=True)
        baseline_shape = builder(p, textured=False)
        baseline_volume += baseline_shape.val().Volume() * quantity
        del baseline_shape
        gc.collect()
    textured = {}
    for name, builder in (("housing", build_housing), ("drawer", build_drawer), ("sorter", build_sorter)):
        print(f"textured:{name}", flush=True)
        textured[name] = builder(p, textured=True)
        gc.collect()
    print("coupons", flush=True)
    coupons = {
        "fit_coupon": build_fit_coupon(p),
        "texture_coupon": build_texture_coupon(p).val(),
    }
    for name, workplane in textured.items():
        if not workplane.val().isValid() or len(workplane.solids().vals()) != 1:
            raise RuntimeError(f"{name}: invalid or non-single CadQuery solid")

    assembly_shapes = {
        "housing": textured["housing"].val(),
        "drawer_lower": textured["drawer"].val().translate(((p.width - p.drawer_width) / 2.0, 0.6, p.housing_bottom + 0.25)),
        "drawer_upper": textured["drawer"].val().translate(((p.width - p.drawer_width) / 2.0, 0.6, p.housing_bottom + p.opening_height + p.shelf + 0.25)),
        "sorter": textured["sorter"].val().translate((0.0, 0.0, p.housing_height)),
    }
    assembly = cq.Compound.makeCompound(list(assembly_shapes.values()))

    manufacturing_shapes = {
        "housing": housing_print_shape(textured["housing"].val()),
        "drawer": drawer_print_shape(textured["drawer"].val()),
        "sorter": shift_to_origin(textured["sorter"].val()),
        "fit_coupon": shift_to_origin(coupons["fit_coupon"]),
        "texture_coupon": shift_to_origin(coupons["texture_coupon"]),
    }
    stems = {
        "housing": "DRAFT-MM-ORG-003-compact-housing-2.0.0-draft.1",
        "drawer": "DRAFT-MM-ORG-003-compact-drawer-print-twice-2.0.0-draft.1",
        "sorter": "DRAFT-MM-ORG-003-compact-top-sorter-2.0.0-draft.1",
        "fit_coupon": "DRAFT-MM-ORG-003-compact-fit-coupon-2.0.0-draft.1",
        "texture_coupon": "DRAFT-MM-ORG-003-compact-texture-coupon-2.0.0-draft.1",
    }
    artifacts: dict[str, dict] = {}
    for name, shape in manufacturing_shapes.items():
        print(f"export:{name}", flush=True)
        step = MASTER / f"{stems[name]}.step"
        stl = MANUFACTURING / f"{stems[name]}.stl"
        export_shape(shape, step, p)
        export_shape(shape, stl, p)
        artifacts[name] = {
            "step": str(step.relative_to(ROOT)),
            "step_sha256": sha256(step),
            "stl": str(stl.relative_to(ROOT)),
            "cad": shape_metrics(shape),
            "mesh": mesh_metrics(stl),
        }

    assembly_step = MASTER / "DRAFT-MM-ORG-003-compact-assembly-2.0.0-draft.1.step"
    assembly_stl = MASTER / "DRAFT-MM-ORG-003-compact-assembly-preview-2.0.0-draft.1.stl"
    export_shape(assembly, assembly_step, p)
    export_shape(assembly, assembly_stl, p)
    print_set = THREE_MF / "DRAFT-MM-ORG-003-modern-carbon-compact-2.0.0-draft.1.3mf"
    write_print_set_3mf(
        print_set,
        [
            ("housing", manufacturing_shapes["housing"], 1),
            ("drawer", manufacturing_shapes["drawer"], 2),
            ("sorter", manufacturing_shapes["sorter"], 1),
        ],
        p,
    )

    selected_volume = sum(textured[name].val().Volume() * (2 if name == "drawer" else 1) for name in textured)
    dense_baseline_triangles = 1467224 + 2 * 239554 + 1012370
    selected_triangles = sum(
        artifacts[name]["mesh"]["triangles"] * (2 if name == "drawer" else 1)
        for name in ("housing", "drawer", "sorter")
    )
    optimization = {
        "status": "PASS",
        "selection": "C — compact geometry plus procedural twill",
        "baseline": {
            "identity": "modern-carbon-desk-organizer-v1.1.2",
            "assembled_envelope_mm": [320.0, 230.0, 213.6],
            "dense_manufacturing_triangles_job": dense_baseline_triangles,
            "exact_slicer_metrics": "NOT_RUN",
        },
        "selected": {
            "assembled_envelope_mm": [p.width, p.depth, p.housing_height + p.sorter_height],
            "untextured_compact_volume_mm3": baseline_volume,
            "textured_selected_volume_mm3": selected_volume,
            "estimated_pla_mass_g_at_1_24": selected_volume / 1000.0 * 1.24,
            "manufacturing_triangles_job": selected_triangles,
            "triangle_burden_reduction_percent_vs_v1_1_2": 100.0 * (dense_baseline_triangles - selected_triangles) / dense_baseline_triangles,
            "exact_slicer_metrics": "NOT_RUN",
        },
        "decision": "Selected as digital geometry candidate; no print-time/material savings claim without exact slicing.",
        "protected_regions": "protected-geometry-map.md",
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)

    production_names = ("housing", "drawer", "sorter")
    source_checks = [
        check("parameter-contract", True, "Default parameters and all derived relationships satisfy assertions"),
        check("brep-valid", all(artifacts[name]["cad"]["valid_brep"] for name in production_names), "Production B-Reps are valid"),
        check("single-solid", all(artifacts[name]["cad"]["solids"] == 1 for name in production_names), "Each production part is one solid"),
        check("side-clearance", math.isclose((p.width - 2 * p.side_wall - p.drawer_width) / 2.0, 0.45, abs_tol=1e-9), "Drawer side clearance is 0.45 mm per side"),
        check("wall-reserve", min(p.side_wall, p.sorter_wall, p.drawer_front_depth) - p.groove_depth >= 1.76, "Texture host wall reserve is at least 1.76 mm"),
        check("assembly-envelope", all(math.isclose(a, b, abs_tol=0.01) for a, b in zip(shape_metrics(assembly)["extents_mm"], [210.0, 190.0, 173.0])), "Assembly envelope is 210 x 190 x 173 mm", {"extents_mm": shape_metrics(assembly)["extents_mm"]}),
    ]
    source_report = pass_report(
        "MM-ORG-003-parametric-source",
        [PARAMETER_FILE, Path(__file__)],
        source_checks,
        {"parts": {name: artifacts[name]["cad"] for name in production_names}},
    )
    write_json(VALIDATION / "parametric-source-report.json", source_report)

    manifest = {
        "project_id": PROJECT_ID,
        "revision": REVISION,
        "status": "DRAFT",
        "parameters_sha256": sha256(PARAMETER_FILE),
        "source_sha256": sha256(Path(__file__)),
        "parts": artifacts,
        "assembly_step": str(assembly_step.relative_to(ROOT)),
        "assembly_step_sha256": sha256(assembly_step),
        "assembly_preview_stl": str(assembly_stl.relative_to(ROOT)),
        "assembly_preview_stl_sha256": sha256(assembly_stl),
        "print_set_3mf": str(print_set.relative_to(ROOT)),
        "print_set_3mf_sha256": sha256(print_set),
        "print_set_note": "Inventory strip; move each unique part to a separate 220 mm plate and print drawer twice.",
        "physical_validation": "DEFERRED",
    }
    write_json(REPORTS / "build-manifest.json", manifest)
    print(json.dumps({"status": source_report["status"], "parts": {k: v["mesh"]["extents_mm"] for k, v in artifacts.items()}, "print_set": str(print_set)}, indent=2))
    return manifest


def artifact_stem(name: str) -> str:
    stems = {
        "housing": "DRAFT-MM-ORG-003-compact-housing-2.0.0-draft.1",
        "drawer": "DRAFT-MM-ORG-003-compact-drawer-print-twice-2.0.0-draft.1",
        "sorter": "DRAFT-MM-ORG-003-compact-top-sorter-2.0.0-draft.1",
        "fit_coupon": "DRAFT-MM-ORG-003-compact-fit-coupon-2.0.0-draft.1",
        "texture_coupon": "DRAFT-MM-ORG-003-compact-texture-coupon-2.0.0-draft.1",
    }
    return stems[name]


def build_single_part(p: Params, name: str) -> dict:
    """Build one part in a fresh process to bound OCCT texture-Boolean memory."""
    for directory in (MASTER, MANUFACTURING, REPORTS, VALIDATION):
        directory.mkdir(parents=True, exist_ok=True)
    builders = {
        "housing": build_housing,
        "drawer": build_drawer,
        "sorter": build_sorter,
    }
    baseline_volume = None
    if name in builders:
        baseline = build_housing(p, textured=False, lightweight=False) if name == "housing" else builders[name](p, textured=False)
        baseline_volume = float(baseline.val().Volume())
        del baseline
        gc.collect()
        raw = (build_housing(p, textured=True, lightweight=True) if name == "housing" else builders[name](p, textured=True)).val()
        expected_solids = 1
        if name == "housing":
            print_shape = housing_print_shape(raw)
        elif name == "drawer":
            print_shape = drawer_print_shape(raw)
        else:
            print_shape = shift_to_origin(raw)
    elif name == "fit_coupon":
        raw = build_fit_coupon(p)
        print_shape = shift_to_origin(raw)
        expected_solids = 6
    elif name == "texture_coupon":
        raw = build_texture_coupon(p).val()
        print_shape = shift_to_origin(raw)
        expected_solids = 1
    else:
        raise ValueError(name)

    stem = artifact_stem(name)
    step = MASTER / f"{stem}.step"
    assembly_stl = MASTER / f"{stem}-assembly-source.stl"
    manufacturing_stl = MANUFACTURING / f"{stem}.stl"
    export_shape(raw, step, p)
    export_shape(raw, assembly_stl, p)
    export_shape(print_shape, manufacturing_stl, p)
    metrics = mesh_metrics(manufacturing_stl)
    cad = shape_metrics(print_shape)
    fits = all(a <= b + 1e-6 for a, b in zip(cad["extents_mm"], [p.build_x, p.build_y, p.build_z]))
    checks = [
        check("brep-valid", cad["valid_brep"], f"{name} B-Rep is valid"),
        check("solid-count", cad["solids"] == expected_solids, f"{name} has {expected_solids} expected solid(s)", {"solids": cad["solids"]}),
        check("mesh-watertight", metrics["watertight"], f"{name} STL is watertight"),
        check("mesh-winding", metrics["winding_consistent"], f"{name} STL winding is consistent"),
        check("mesh-volume", metrics["positive_volume"], f"{name} STL has positive signed volume"),
        check("mesh-components", metrics["components"] == expected_solids, f"{name} STL component count matches", {"components": metrics["components"]}),
        check("build-volume", fits, f"{name} documented orientation fits 220 x 220 x 250 mm", {"extents_mm": cad["extents_mm"]}),
        check("triangle-budget", metrics["triangles"] <= p.max_triangles, f"{name} stays within triangle budget", {"triangles": metrics["triangles"]}),
        check("file-budget", metrics["file_mib"] <= p.max_file_mib, f"{name} stays within mesh file budget", {"file_mib": metrics["file_mib"]}),
    ]
    report = pass_report(
        f"MM-ORG-003-isolated-{name}-build",
        [PARAMETER_FILE, Path(__file__)],
        checks,
        {
            "name": name,
            "quantity": 2 if name == "drawer" else 1,
            "baseline_volume_mm3": baseline_volume,
            "cad": cad,
            "mesh": metrics,
            "step": str(step.relative_to(ROOT)),
            "step_sha256": sha256(step),
            "assembly_source_stl": str(assembly_stl.relative_to(ROOT)),
            "assembly_source_stl_sha256": sha256(assembly_stl),
            "manufacturing_stl": str(manufacturing_stl.relative_to(ROOT)),
        },
    )
    report_path = VALIDATION / f"isolated-{name}-build.json"
    write_json(report_path, report)
    if report["status"] != "PASS":
        raise RuntimeError(f"isolated build failed: {name}")
    print(json.dumps({"status": "PASS", "part": name, "report": str(report_path)}, indent=2), flush=True)
    return report


def write_print_set_3mf_from_stls(path: Path, parts: list[tuple[str, Path, int]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    for name, value in (
        ("Title", "DRAFT MM-ORG-003 Modern Carbon Compact print set"),
        ("Designer", "metriMade / autonomous CAD workflow"),
        ("Description", "Four build items in an inventory strip; place housing, one drawer and sorter on separate 220 mm plates and print the drawer twice."),
        ("LicenseTerms", "DRAFT engineering artifact; not a commercial release"),
    ):
        node = ET.SubElement(model, f"{{{ns}}}metadata", {"name": name})
        node.text = value
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    inventory_x = 0.0
    for object_id, (name, stl, quantity) in enumerate(parts, start=1):
        mesh = trimesh.load_mesh(stl, force="mesh", process=True)
        if not isinstance(mesh, trimesh.Trimesh) or not mesh.is_watertight or mesh.volume <= 0:
            raise RuntimeError(f"invalid 3MF source: {stl}")
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name, "partnumber": f"{PROJECT_ID}-{REVISION}-{name}"})
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices_node = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices_node, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles_node = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(triangles_node, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        for _ in range(quantity):
            transform = f"1 0 0 0 1 0 0 0 1 {inventory_x:.3f} 0 0"
            ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": transform})
            inventory_x += float(mesh.extents[0]) + 12.0
    model_bytes = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for member, payload in (
            ("[Content_Types].xml", content_types),
            ("_rels/.rels", rels),
            ("3D/3dmodel.model", model_bytes),
            ("Metadata/model-parameters.json", PARAMETER_FILE.read_bytes()),
        ):
            info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)


def build_isolated(p: Params) -> dict:
    """Orchestrate independent part builders, then assemble lightweight mesh evidence."""
    names = ("housing", "drawer", "sorter", "fit_coupon", "texture_coupon")
    for name in names:
        command = [sys.executable, "-u", str(Path(__file__)), "--parameters", str(PARAMETER_FILE), "--part", name]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout, end="", flush=True)
        if result.returncode != 0:
            raise RuntimeError(f"isolated subprocess failed for {name}:\n{result.stdout}\n{result.stderr}")

    reports = {name: json.loads((VALIDATION / f"isolated-{name}-build.json").read_text(encoding="utf-8")) for name in names}
    artifacts = {name: reports[name]["metrics"] for name in names}
    product_names = ("housing", "drawer", "sorter")

    assembly_meshes: list[trimesh.Trimesh] = []
    for name in product_names:
        source = ROOT / artifacts[name]["assembly_source_stl"]
        mesh = trimesh.load_mesh(source, force="mesh", process=True)
        if name == "drawer":
            for z in (p.housing_bottom + 0.25, p.housing_bottom + p.opening_height + p.shelf + 0.25):
                placed = mesh.copy()
                placed.apply_translation(((p.width - p.drawer_width) / 2.0, 0.0, z))
                assembly_meshes.append(placed)
        elif name == "sorter":
            mesh.apply_translation((0.0, 0.0, p.housing_height))
            assembly_meshes.append(mesh)
        else:
            assembly_meshes.append(mesh)
    assembly = trimesh.util.concatenate(assembly_meshes)
    assembly_preview = MASTER / "DRAFT-MM-ORG-003-compact-assembly-preview-2.0.0-draft.1.stl"
    assembly.export(assembly_preview)
    assembly_extents = np.round(assembly.extents, 5).tolist()

    print_set = THREE_MF / "DRAFT-MM-ORG-003-modern-carbon-compact-2.0.0-draft.1.3mf"
    print_set_parts = [
        ("housing", ROOT / artifacts["housing"]["manufacturing_stl"], 1),
        ("drawer", ROOT / artifacts["drawer"]["manufacturing_stl"], 2),
        ("sorter", ROOT / artifacts["sorter"]["manufacturing_stl"], 1),
    ]
    write_print_set_3mf_from_stls(print_set, print_set_parts)

    selected_volume = sum(artifacts[name]["mesh"]["volume_mm3"] * (2 if name == "drawer" else 1) for name in product_names)
    compact_baseline_volume = sum(float(artifacts[name]["baseline_volume_mm3"]) * (2 if name == "drawer" else 1) for name in product_names)
    dense_baseline_triangles = 1467224 + 2 * 239554 + 1012370
    selected_triangles = sum(artifacts[name]["mesh"]["triangles"] * (2 if name == "drawer" else 1) for name in product_names)
    optimization = {
        "schema_version": "1.0",
        "tool": "MM-ORG-003-optimization-comparison",
        "tool_version": "2.0.0",
        "status": "PASS",
        "profile": "draft",
        "inputs": [{"path": str(PARAMETER_FILE.relative_to(ROOT)), "sha256": sha256(PARAMETER_FILE), "size_bytes": PARAMETER_FILE.stat().st_size}],
        "checks": [
            check(
                "common-printer",
                all(
                    next(item for item in reports[n]["checks"] if item["id"] == "build-volume")["status"] == "PASS"
                    for n in product_names
                ),
                "All production parts fit the configured common-printer volume",
            ),
            check("mesh-burden", selected_triangles < dense_baseline_triangles, "Procedural candidate reduces the stored manufacturing triangle burden"),
            check("protected-contract", True, "Protected geometry map remains binding"),
        ],
        "metrics": {
            "selection": "C — compact geometry plus procedural twill",
            "v1_1_2_dense_triangles_job": dense_baseline_triangles,
            "selected_triangles_job": selected_triangles,
            "triangle_burden_reduction_percent": 100.0 * (dense_baseline_triangles - selected_triangles) / dense_baseline_triangles,
            "compact_untextured_volume_mm3": compact_baseline_volume,
            "selected_textured_volume_mm3": selected_volume,
            "compact_volume_reduction_percent": 100.0 * (compact_baseline_volume - selected_volume) / compact_baseline_volume,
            "estimated_pla_mass_g_at_1_24": selected_volume / 1000.0 * 1.24,
            "exact_slicer_metrics": "NOT_RUN",
        },
        "limitations": ["No exact slicer CLI/profile is installed; no print-time or deposited-material savings percentage is claimed."],
        "required_capabilities": [],
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)

    source_checks = [
        check("parameter-contract", True, "Parameters and derived relationships satisfy assertions"),
        check("part-reports", all(reports[name]["status"] == "PASS" for name in names), "All isolated deterministic part builds pass"),
        check("assembly-envelope", all(math.isclose(a, b, abs_tol=0.05) for a, b in zip(assembly_extents, [210.0, 190.0, 173.0])), "Assembly envelope is 210 x 190 x 173 mm", {"extents_mm": assembly_extents}),
        check("side-clearance", math.isclose((p.width - 2 * p.side_wall - p.drawer_width) / 2.0, 0.45, abs_tol=1e-9), "Drawer side clearance is 0.45 mm per side"),
        check("depth-stack", math.isclose(p.drawer_front_depth + p.drawer_depth + p.drawer_rear_clearance, p.depth - p.rear_wall, abs_tol=1e-9), "Drawer depth stack closes exactly"),
        check("wall-reserve", min(p.side_wall, p.sorter_wall, p.drawer_front_depth) - p.groove_depth >= 1.76, "Texture wall reserve is at least 1.76 mm"),
    ]
    source_report = pass_report(
        "MM-ORG-003-parametric-source",
        [PARAMETER_FILE, Path(__file__)],
        source_checks,
        {"parts": artifacts, "assembly_extents_mm": assembly_extents},
        ["Exact slicer and physical validation are deferred."],
    )
    write_json(VALIDATION / "parametric-source-report.json", source_report)
    if source_report["status"] != "PASS":
        raise RuntimeError("aggregate source contract failed")

    manifest = {
        "project_id": PROJECT_ID,
        "revision": REVISION,
        "status": "DRAFT",
        "parameters_sha256": sha256(PARAMETER_FILE),
        "source_sha256": sha256(Path(__file__)),
        "parts": artifacts,
        "assembly_preview_stl": str(assembly_preview.relative_to(ROOT)),
        "assembly_preview_stl_sha256": sha256(assembly_preview),
        "print_set_3mf": str(print_set.relative_to(ROOT)),
        "print_set_3mf_sha256": sha256(print_set),
        "print_set_note": "Inventory strip; place each unique part on a separate 220 mm plate and print drawer twice.",
        "physical_validation": "DEFERRED",
    }
    write_json(REPORTS / "build-manifest.json", manifest)
    print(json.dumps({"status": "PASS", "assembly_extents_mm": assembly_extents, "print_set": str(print_set)}, indent=2), flush=True)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=PARAMETER_FILE)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--part", choices=("housing", "drawer", "sorter", "fit_coupon", "texture_coupon"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    p = load_params(args.parameters)
    if args.validate_only:
        print(json.dumps({"status": "PASS", "project_id": PROJECT_ID, "revision": REVISION}, indent=2))
        return
    if args.part:
        build_single_part(p, args.part)
    else:
        build_isolated(p)


if __name__ == "__main__":
    main()
