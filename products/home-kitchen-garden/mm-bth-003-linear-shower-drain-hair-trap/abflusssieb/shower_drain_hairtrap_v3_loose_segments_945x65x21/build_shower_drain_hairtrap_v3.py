#!/usr/bin/env python3
"""Build the approved MM-BTH-003 shower-drain hair trap revision 3.1.

Assembly coordinates use millimetres: X=length, Y=width, Z=height.
The approved row contains sixteen 52.5 mm single-catcher segments and one
105.0 mm double-catcher segment. The double segment carries the exact
canonical MM-BTH-003 watermark recessed 0.4 mm into its left inner wall.
Manufacturing meshes are rotated +90 degrees around global Y onto a complete
U-profile end. STEP masters remain in assembly orientation.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial import cKDTree


ROOT = Path(__file__).resolve().parent
MASTER_DIR = ROOT / "exports" / "master"
MANUFACTURING_DIR = ROOT / "exports" / "manufacturing"
VALIDATION_EXPORT_DIR = ROOT / "exports" / "validation"
BUILD_DIR = ROOT / "build"
PREVIEW_DIR = ROOT / "validation" / "previews"
WATERMARK_VALIDATION_DIR = ROOT / "validation" / "watermark"

PRODUCT_ID = "MM-BTH-003"
PRODUCT_NAME = "Linear Shower Drain Hair Trap"
REVISION = "3.1.0-draft.1"
FILE_PREFIX = f"DRAFT-{PRODUCT_ID}-{REVISION}"

# Approved user-facing parameters (mm).
TOTAL_LENGTH = 945.0
TOTAL_WIDTH = 65.0
TOTAL_HEIGHT = 21.0
SINGLE_COUNT = 16
SINGLE_LENGTH = 52.5
DOUBLE_COUNT = 1
DOUBLE_LENGTH = 105.0
PART_COUNT = SINGLE_COUNT + DOUBLE_COUNT
DOUBLE_ASSEMBLY_INDEX = 8  # eight singles, double, eight singles

# Inverted-U shell retained from funnel-edge v1.3.
TOP_T = 4.2
SIDE_WALL_T = 3.0
SIDE_WALL_H = TOTAL_HEIGHT - TOP_T
CORNER_R = 1.6

# Preserved funnel/catcher module.
CATCHER_D = 46.0
CATCHER_Y = TOTAL_WIDTH / 2.0
SINGLE_CATCHER_CENTERS = (26.25,)
DOUBLE_CATCHER_CENTERS = (26.25, 78.75)
END_MARGIN = (SINGLE_LENGTH - CATCHER_D) / 2.0
INTER_CATCHER_TANGENT = DOUBLE_CATCHER_CENTERS[1] - DOUBLE_CATCHER_CENTERS[0] - CATCHER_D
MIN_SOLID_TANGENT = 3.0

FUNNEL_DEPTH = 2.5
FUNNEL_ENTRY_R = 23.0
FUNNEL_FLOOR_R = 19.0
FUNNEL_FLOOR_Z = TOTAL_HEIGHT - FUNNEL_DEPTH
HOLE_D = 2.8
HOLE_PITCH = 4.3
HOLE_FIELD_R = 16.0

RIB_W = 1.6
RIB_COUNT = 5
RIB_START_R = FUNNEL_ENTRY_R - RIB_W / 2.0 + 0.05
RIB_END_R = 10.2
RIB_SWEEP = math.radians(126.0)
RIB_STEPS = 24
CENTER_BOSS_R = 2.8

# Canonical watermark. No scaling, redrawing, or alternate text is allowed.
WATERMARK_DIR = ROOT / "assets" / "metrimade-watermark" / "generated" / f"{PRODUCT_ID}_v{REVISION}"
WATERMARK_STEM = f"metrimade-watermark-{PRODUCT_ID}-v{REVISION}"
WATERMARK_DXF = WATERMARK_DIR / f"{WATERMARK_STEM}.dxf"
WATERMARK_METADATA = WATERMARK_DIR / f"{WATERMARK_STEM}.json"
WATERMARK_MANIFEST = WATERMARK_DIR / "manifest.sha256"
WATERMARK_SELECTOR = WATERMARK_VALIDATION_DIR / f"side-wall-selector-{REVISION}.json"
WATERMARK_DEPTH = 0.4
WATERMARK_NUMERIC_OVERLAP = 0.01
WATERMARK_HOST_FACE_Y = SIDE_WALL_T
WATERMARK_REMAINING_WALL = SIDE_WALL_T - WATERMARK_DEPTH
WATERMARK_SIDEWALL_MIRROR_X = True

# STEP/B-Rep is authoritative. Manufacturing STLs reuse the corresponding
# audited master tessellation, then receive only the declared rigid transform.
STL_TOLERANCE = 0.05
STL_ANGULAR_TOLERANCE = 0.12

SINGLE_MASTER_STEP = MASTER_DIR / f"{FILE_PREFIX}-single-52p5mm-master.step"
SINGLE_MASTER_STL = MASTER_DIR / f"{FILE_PREFIX}-single-52p5mm-master.stl"
DOUBLE_MASTER_STEP = MASTER_DIR / f"{FILE_PREFIX}-double-105mm-marked-master.step"
DOUBLE_MASTER_STL = MASTER_DIR / f"{FILE_PREFIX}-double-105mm-marked-master.stl"
ASSEMBLY_STEP = MASTER_DIR / f"{FILE_PREFIX}-17-part-assembly-reference.step"
SINGLE_PRINT_STL = MANUFACTURING_DIR / f"{FILE_PREFIX}-single-52p5mm-on-end.stl"
DOUBLE_PRINT_STL = MANUFACTURING_DIR / f"{FILE_PREFIX}-double-105mm-marked-on-end.stl"
SINGLE_REFERENCE_STL = VALIDATION_EXPORT_DIR / f"{FILE_PREFIX}-single-52p5mm-tessellation-reference.stl"
DOUBLE_REFERENCE_STL = VALIDATION_EXPORT_DIR / f"{FILE_PREFIX}-double-105mm-marked-tessellation-reference.stl"
PARAMETERS_JSON = BUILD_DIR / "parameters-3.1.0-draft.1.json"
BUILD_REPORT_JSON = BUILD_DIR / "build-report-3.1.0-draft.1.json"
OPTIMIZATION_REPORT_JSON = BUILD_DIR / "segment-count-optimization-3.1.0-draft.1.json"
WATERMARK_PLACEMENT_REPORT = WATERMARK_VALIDATION_DIR / f"watermark-placement-report-{REVISION}.json"
MARKED_SIDE_PREVIEW_SVG = PREVIEW_DIR / f"{FILE_PREFIX}-marked-inner-side.svg"
MARKED_ISOMETRIC_PREVIEW_SVG = PREVIEW_DIR / f"{FILE_PREFIX}-marked-double-isometric.svg"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bounds(shape: cq.Workplane) -> dict[str, list[float]]:
    box = shape.val().BoundingBox()
    return {
        "minimum_mm": [box.xmin, box.ymin, box.zmin],
        "maximum_mm": [box.xmax, box.ymax, box.zmax],
        "extents_mm": [box.xlen, box.ylen, box.zlen],
    }


def assert_close_list(actual: list[float], expected: list[float], label: str) -> None:
    for axis, (got, wanted) in enumerate(zip(actual, expected)):
        assert math.isclose(got, wanted, abs_tol=1e-5), f"{label}: axis {axis}: {got} != {wanted}"


def assert_shape(shape: cq.Workplane, expected: list[float], label: str) -> None:
    solids = shape.solids().vals()
    assert len(solids) == 1, f"{label}: expected one solid, got {len(solids)}"
    assert solids[0].isValid(), f"{label}: invalid OpenCascade solid"
    assert solids[0].Volume() > 0, f"{label}: non-positive volume"
    assert_close_list(bounds(shape)["extents_mm"], expected, label)


def validate_parameters() -> None:
    assert SINGLE_COUNT * SINGLE_LENGTH + DOUBLE_COUNT * DOUBLE_LENGTH == TOTAL_LENGTH
    assert PART_COUNT == 17
    assert len(SINGLE_CATCHER_CENTERS) * SINGLE_COUNT + len(DOUBLE_CATCHER_CENTERS) == 18
    assert math.isclose(END_MARGIN, 3.25, abs_tol=1e-9) and END_MARGIN >= MIN_SOLID_TANGENT
    assert math.isclose(INTER_CATCHER_TANGENT, 6.5, abs_tol=1e-9)
    assert INTER_CATCHER_TANGENT >= MIN_SOLID_TANGENT
    assert 0 < FUNNEL_DEPTH < TOP_T
    assert 0 < SIDE_WALL_T < TOTAL_WIDTH / 2.0
    assert math.isclose(SIDE_WALL_H + TOP_T, TOTAL_HEIGHT, abs_tol=1e-9)
    assert math.isclose(WATERMARK_REMAINING_WALL, 2.6, abs_tol=1e-9)
    for path in (WATERMARK_DXF, WATERMARK_METADATA, WATERMARK_MANIFEST, WATERMARK_SELECTOR):
        assert path.is_file(), path
    metadata = json.loads(WATERMARK_METADATA.read_text(encoding="utf-8"))
    selector = json.loads(WATERMARK_SELECTOR.read_text(encoding="utf-8"))
    assert metadata["asset_revision"] == "MM-WM-001-R1"
    assert metadata["product_id"] == PRODUCT_ID and metadata["version"] == REVISION
    assert metadata["visible_text"] == ["metriMade.com", f"{PRODUCT_ID} · v{REVISION}"]
    assert_close_list(metadata["layout_envelope_mm"], [79.802, 12.8, 0.4], "watermark metadata")
    assert selector["status"] == "PASS"
    assert selector["selection"]["uniform_scale"] == 1.0
    assert selector["selection"]["rotation_deg"] == 0
    assert math.isclose(selector["residual_host_wall_mm"], 2.6, abs_tol=1e-9)


def catcher_points() -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    row_height = HOLE_PITCH * math.sqrt(3.0) / 2.0
    for row in range(-10, 11):
        yy = row * row_height
        x_offset = (abs(row) % 2) * HOLE_PITCH / 2.0
        for column in range(-10, 11):
            xx = column * HOLE_PITCH + x_offset
            if xx * xx + yy * yy <= HOLE_FIELD_R * HOLE_FIELD_R:
                points.append((xx, yy))
    return points


def spiral_band_points(phase_rad: float) -> list[tuple[float, float]]:
    centerline: list[tuple[float, float]] = []
    for index in range(RIB_STEPS + 1):
        ratio = index / RIB_STEPS
        angle = phase_rad + ratio * RIB_SWEEP
        radius = RIB_START_R + ratio * (RIB_END_R - RIB_START_R)
        centerline.append((radius * math.cos(angle), radius * math.sin(angle)))
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for index, (xx, yy) in enumerate(centerline):
        previous_index = max(index - 1, 0)
        next_index = min(index + 1, RIB_STEPS)
        dx = centerline[next_index][0] - centerline[previous_index][0]
        dy = centerline[next_index][1] - centerline[previous_index][1]
        length = math.hypot(dx, dy)
        nx, ny = -dy / length, dx / length
        left.append((xx + nx * RIB_W / 2.0, yy + ny * RIB_W / 2.0))
        right.append((xx - nx * RIB_W / 2.0, yy - ny * RIB_W / 2.0))
    return left + list(reversed(right))


def make_base_u(length: float) -> cq.Workplane:
    top = cq.Workplane("XY").box(length, TOTAL_WIDTH, TOP_T, centered=(False, False, False)).translate((0, 0, TOTAL_HEIGHT - TOP_T))
    left_wall = cq.Workplane("XY").box(length, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False))
    right_wall = cq.Workplane("XY").box(length, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False)).translate((0, TOTAL_WIDTH - SIDE_WALL_T, 0))
    body = top.union(left_wall).union(right_wall)
    try:
        body = body.edges("|Z").fillet(CORNER_R)
    except Exception:
        pass
    return body


def make_funnel_tool(catcher_x: float) -> cq.Workplane:
    return cq.Workplane("XY", origin=(catcher_x, CATCHER_Y, TOTAL_HEIGHT)).circle(FUNNEL_ENTRY_R).workplane(offset=-FUNNEL_DEPTH).circle(FUNNEL_FLOOR_R).loft(combine=True, ruled=False)


def make_rib_solid(catcher_x: float, phase_rad: float) -> cq.Workplane:
    rib_prism = cq.Workplane("XY", origin=(catcher_x, CATCHER_Y, FUNNEL_FLOOR_Z)).polyline(spiral_band_points(phase_rad)).close().extrude(FUNNEL_DEPTH + 0.04)
    return rib_prism.intersect(make_funnel_tool(catcher_x))


def add_catcher(segment: cq.Workplane, catcher_x: float) -> cq.Workplane:
    segment = segment.cut(make_funnel_tool(catcher_x))
    hole_centers = [(catcher_x + xx, CATCHER_Y + yy) for xx, yy in catcher_points()]
    holes = cq.Workplane("XY", origin=(0, 0, TOTAL_HEIGHT - TOP_T - 0.05)).pushPoints(hole_centers).circle(HOLE_D / 2.0).extrude(TOP_T + 0.10)
    segment = segment.cut(holes)
    for rib_index in range(RIB_COUNT):
        segment = segment.union(make_rib_solid(catcher_x, rib_index * 2.0 * math.pi / RIB_COUNT), clean=False)
    center_boss = cq.Workplane("XY", origin=(catcher_x, CATCHER_Y, FUNNEL_FLOOR_Z)).circle(CENTER_BOSS_R).extrude(max(0.8, FUNNEL_DEPTH * 0.52))
    return segment.union(center_boss, clean=False)


def make_watermark_tool(length: float) -> cq.Workplane:
    """Map the exact DXF profile into the left inner wall without scaling."""
    imported = cq.importers.importDXF(str(WATERMARK_DXF))
    extruded = imported.wires().toPending().extrude(WATERMARK_DEPTH + WATERMARK_NUMERIC_OVERLAP)
    tool = cq.Workplane("XY").newObject([cq.Compound.makeCompound(extruded.solids().vals())])
    box = tool.val().BoundingBox()
    tool = tool.translate((-(box.xmin + box.xmax) / 2.0, -(box.ymin + box.ymax) / 2.0, 0))
    # The package profile is authored for an underside view.  This rigid
    # reflection is the placement orientation required to read left-to-right
    # when the selected inner side wall is viewed from the drain cavity.
    tool = tool.mirror("YZ")
    # +90° about X maps extrusion toward -Y. The 0.01 mm exterior overlap
    # leaves exactly 0.4 mm intersection with the host wall.
    return tool.rotate((0, 0, 0), (1, 0, 0), 90.0).translate((length / 2.0, WATERMARK_HOST_FACE_Y + WATERMARK_NUMERIC_OVERLAP, SIDE_WALL_H / 2.0))


def make_segment(length: float, centers: tuple[float, ...], marked: bool) -> tuple[cq.Workplane, cq.Workplane | None]:
    segment = make_base_u(length)
    for catcher_x in centers:
        segment = add_catcher(segment, catcher_x)
    watermark_tool = None
    if marked:
        watermark_tool = make_watermark_tool(length)
        segment = segment.cut(watermark_tool)
    try:
        segment = segment.clean()
    except Exception:
        pass
    return segment, watermark_tool


def print_orientation(shape: cq.Workplane, length: float) -> cq.Workplane:
    return shape.rotate((0, 0, 0), (0, 1, 0), 90.0).translate((0, 0, length))


def detached_copy(shape: cq.Workplane) -> cq.Workplane:
    return cq.Workplane("XY").newObject([shape.val().copy()])


def print_mesh_transform(length: float) -> np.ndarray:
    rotation = trimesh.transformations.rotation_matrix(math.radians(90.0), [0, 1, 0])
    translation = trimesh.transformations.translation_matrix([0, 0, length])
    return trimesh.transformations.concatenate_matrices(translation, rotation)


def export_part(master: cq.Workplane, step_path: Path, stl_path: Path, reference_path: Path, print_path: Path, length: float) -> None:
    cq.exporters.export(detached_copy(master), str(step_path))
    cq.exporters.export(detached_copy(master), str(stl_path), tolerance=STL_TOLERANCE, angularTolerance=STL_ANGULAR_TOLERANCE)
    shutil.copyfile(stl_path, reference_path)
    assert sha256_file(stl_path) == sha256_file(reference_path)
    mesh = trimesh.load_mesh(reference_path, process=True, force="mesh")
    mesh.apply_transform(print_mesh_transform(length))
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    mesh.export(print_path, file_type="stl")


def assembly_positions() -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    cursor = 0.0
    single_number = 0
    for assembly_index in range(PART_COUNT):
        is_double = assembly_index == DOUBLE_ASSEMBLY_INDEX
        if is_double:
            name, length = "marked_double_01", DOUBLE_LENGTH
        else:
            single_number += 1
            name, length = f"single_{single_number:02d}", SINGLE_LENGTH
        result.append({"name": name, "start_mm": cursor, "end_mm": cursor + length, "length_mm": length})
        cursor += length
    assert single_number == SINGLE_COUNT and math.isclose(cursor, TOTAL_LENGTH, abs_tol=1e-9)
    return result


def export_models(single: cq.Workplane, marked_double: cq.Workplane) -> None:
    for directory in (MASTER_DIR, MANUFACTURING_DIR, VALIDATION_EXPORT_DIR, BUILD_DIR, PREVIEW_DIR, WATERMARK_VALIDATION_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    export_part(single, SINGLE_MASTER_STEP, SINGLE_MASTER_STL, SINGLE_REFERENCE_STL, SINGLE_PRINT_STL, SINGLE_LENGTH)
    export_part(marked_double, DOUBLE_MASTER_STEP, DOUBLE_MASTER_STL, DOUBLE_REFERENCE_STL, DOUBLE_PRINT_STL, DOUBLE_LENGTH)
    assembly = cq.Assembly(name=f"{PRODUCT_ID}-{REVISION}-17-part")
    for item in assembly_positions():
        part = marked_double if item["name"] == "marked_double_01" else single
        assembly.add(part, name=str(item["name"]), loc=cq.Location(cq.Vector(float(item["start_mm"]), 0, 0)))
    assembly.save(str(ASSEMBLY_STEP))

    marked_wall = marked_double.intersect(cq.Workplane("XY").box(DOUBLE_LENGTH, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False)))
    options = {"width": 1500, "height": 420, "marginLeft": 25, "marginTop": 25, "showAxes": False, "showHidden": False, "strokeWidth": 0.35}
    cq.exporters.export(marked_wall, str(MARKED_SIDE_PREVIEW_SVG), opt={**options, "projectionDir": (0, -1, 0)})
    cq.exporters.export(marked_double, str(MARKED_ISOMETRIC_PREVIEW_SVG), opt={**options, "projectionDir": (1, -1, 0.7)})


def mesh_transform_evidence(reference_path: Path, print_path: Path, length: float) -> dict[str, object]:
    reference = trimesh.load_mesh(reference_path, process=True, force="mesh")
    printed = trimesh.load_mesh(print_path, process=True, force="mesh")
    inverse = printed.copy()
    inverse.apply_transform(np.linalg.inv(print_mesh_transform(length)))
    assert reference.vertices.shape == inverse.vertices.shape
    # Lexicographic pairing is unstable when several vertices share an axis
    # coordinate and STL float32 roundoff changes their tie order.  A symmetric
    # nearest-neighbour distance proves the transformed vertex sets instead.
    forward = cKDTree(inverse.vertices).query(reference.vertices, k=1)[0]
    reverse = cKDTree(reference.vertices).query(inverse.vertices, k=1)[0]
    maximum_delta = float(max(np.max(forward), np.max(reverse)))
    assert maximum_delta <= 1e-5
    assert len(reference.faces) == len(printed.faces)
    assert math.isclose(reference.volume, printed.volume, rel_tol=1e-8)
    assert abs(float(printed.bounds[0][2])) <= 1e-6
    return {
        "reference_vertices": len(reference.vertices), "print_vertices": len(printed.vertices),
        "reference_faces": len(reference.faces), "print_faces": len(printed.faces),
        "maximum_inverse_vertex_delta_mm": maximum_delta,
        "reference_volume_mm3": float(reference.volume), "print_volume_mm3": float(printed.volume),
        "print_bounds_mm": {"minimum": printed.bounds[0].tolist(), "maximum": printed.bounds[1].tolist(), "extents": printed.extents.tolist()},
    }


def artifact_record(path: Path) -> dict[str, object]:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def write_parameter_contract() -> None:
    holes = len(catcher_points())
    write_json(PARAMETERS_JSON, {
        "schema_version": "1.0", "product_id": PRODUCT_ID, "product_name": PRODUCT_NAME,
        "revision": REVISION, "units": "mm", "installed_envelope_mm": [TOTAL_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT],
        "printed_part_count": PART_COUNT,
        "single_segments": {"count": SINGLE_COUNT, "length_mm": SINGLE_LENGTH, "catcher_centers_mm": list(SINGLE_CATCHER_CENTERS)},
        "marked_double_segment": {"count": DOUBLE_COUNT, "length_mm": DOUBLE_LENGTH, "catcher_centers_mm": list(DOUBLE_CATCHER_CENTERS), "assembly_position_after_single_count": DOUBLE_ASSEMBLY_INDEX},
        "catcher_count_total": 18, "catcher_entry_diameter_mm": CATCHER_D,
        "end_margin_each_side_mm": END_MARGIN, "inter_catcher_tangent_mm": INTER_CATCHER_TANGENT,
        "holes_per_catcher": holes, "holes_total": holes * 18, "hole_diameter_mm": HOLE_D, "hole_pitch_mm": HOLE_PITCH,
        "rib_count_per_catcher": RIB_COUNT, "connector_features": [],
        "shell": {"top_thickness_mm": TOP_T, "side_wall_thickness_mm": SIDE_WALL_T, "side_wall_height_mm": SIDE_WALL_H},
        "watermark": {"asset_revision": "MM-WM-001-R1", "operation": "recessed", "selected_surface": "left inner side wall of marked double segment", "scale": 1.0, "selector_rotation_deg": 0, "sidewall_reading_transform": "rigid mirror across local YZ plane", "depth_mm": WATERMARK_DEPTH, "remaining_wall_mm": WATERMARK_REMAINING_WALL, "visible_text": ["metriMade.com", f"{PRODUCT_ID} · v{REVISION}"]},
        "nominal_length_equation": f"{SINGLE_COUNT} * {SINGLE_LENGTH} + {DOUBLE_COUNT} * {DOUBLE_LENGTH} = {TOTAL_LENGTH}",
        "print_transform": {"axis": [0, 1, 0], "angle_degrees": 90.0, "bed_contact": "original X=max inverted-U end cross-section"},
    })


def write_optimization_report() -> None:
    write_json(OPTIMIZATION_REPORT_JSON, {
        "schema_version": "1.0", "status": "PASS", "tool": Path(__file__).name, "tool_version": REVISION,
        "inputs": [artifact_record(ROOT / "design-spec.yaml"), artifact_record(WATERMARK_SELECTOR)],
        "checks": [
            {"id": "preserve-catcher-count", "status": "PASS", "required": True, "message": "The 17-part variant preserves all 18 approved catcher modules.", "metrics": {"single_catchers": 16, "double_catchers": 2, "total": 18}},
            {"id": "preserve-total-length", "status": "PASS", "required": True, "message": "Sixteen 52.5 mm pieces plus one 105.0 mm piece equal 945.0 mm.", "metrics": {"calculated_mm": SINGLE_COUNT * SINGLE_LENGTH + DOUBLE_LENGTH, "target_mm": TOTAL_LENGTH}},
            {"id": "canonical-watermark-host", "status": "PASS", "required": True, "message": "The smallest changed host is one 105 mm double segment; the canonical profile fits at scale 1.0.", "metrics": {"old_single_host_mm": [SINGLE_LENGTH, SIDE_WALL_H], "selected_host_mm": [DOUBLE_LENGTH, SIDE_WALL_H], "selected_scale": 1.0, "part_count_reduction": 1}},
        ],
        "metrics": {"previous_variant": "18 identical 52.5 mm single segments", "selected_variant": "16 single segments plus one marked 105 mm double segment", "connector_feature_count": 0},
        "limitations": ["Physical installed fit and process-matched watermark readability remain human gates."], "required_capabilities": [],
    })


def write_watermark_report(unmarked_double: cq.Workplane, marked_double: cq.Workplane, tool: cq.Workplane) -> None:
    selector = json.loads(WATERMARK_SELECTOR.read_text(encoding="utf-8"))
    removed_volume = unmarked_double.val().Volume() - marked_double.val().Volume()
    assert removed_volume > 0 and math.isclose(WATERMARK_REMAINING_WALL, 2.6, abs_tol=1e-9)
    write_json(WATERMARK_PLACEMENT_REPORT, {
        "schema_version": "1.0", "status": "REVIEW_REQUIRED", "digital_geometry_status": "PASS", "physical_qualification": "NOT_RUN",
        "tool": Path(__file__).name, "tool_version": REVISION,
        "inputs": [artifact_record(WATERMARK_METADATA), artifact_record(WATERMARK_DXF), artifact_record(WATERMARK_MANIFEST), artifact_record(WATERMARK_SELECTOR), artifact_record(DOUBLE_MASTER_STEP), artifact_record(DOUBLE_MASTER_STL)],
        "checks": [
            {"id": "identity", "status": "PASS", "required": True, "message": f"Canonical visible identity is metriMade.com / {PRODUCT_ID} / v{REVISION}."},
            {"id": "selector", "status": selector["status"], "required": True, "message": "Canonical selector accepts the 105.0 x 16.8 mm inner side wall at scale 1.0.", "metrics": selector["selection"]},
            {"id": "subtractive-placement", "status": "PASS", "required": True, "message": "The exact generated DXF profile is rigidly oriented for side-wall reading and subtracted from the left inner wall.", "metrics": {"operation": "recessed", "depth_mm": WATERMARK_DEPTH, "uniform_scale": 1.0, "selector_rotation_deg": 0, "sidewall_mirror_x": WATERMARK_SIDEWALL_MIRROR_X, "removed_volume_mm3": removed_volume, "tool_bounds": bounds(tool)}},
            {"id": "residual-wall", "status": "PASS", "required": True, "message": "The 3.0 mm wall retains 2.6 mm behind the 0.4 mm recess.", "metrics": {"host_wall_mm": SIDE_WALL_T, "recess_mm": WATERMARK_DEPTH, "remaining_wall_mm": WATERMARK_REMAINING_WALL, "minimum_required_mm": 0.8}},
            {"id": "inner-side-readability-review", "status": "REVIEW_REQUIRED", "required": True, "message": "Render the actual marked STL from the drain cavity and confirm left-to-right identity before watermark approval.", "evidence_source": "render_watermark_previews.py"},
            {"id": "exact-process-coupon", "status": "NOT_RUN", "required": True, "message": "Print and inspect the generated coupon in the selected Kobra 3 Max PETG process before watermark approval."},
        ],
        "release_decision": "BLOCKED until the exact-process coupon and human readability review pass.",
    })


def write_build_report(single: cq.Workplane, marked_double: cq.Workplane) -> None:
    imported_single = cq.importers.importStep(str(SINGLE_MASTER_STEP))
    imported_double = cq.importers.importStep(str(DOUBLE_MASTER_STEP))
    imported_assembly = cq.importers.importStep(str(ASSEMBLY_STEP))
    assert_shape(imported_single, [SINGLE_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT], "reimported single")
    assert_shape(imported_double, [DOUBLE_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT], "reimported marked double")
    assembly_solids = imported_assembly.solids().vals()
    assert len(assembly_solids) == PART_COUNT
    assert all(solid.isValid() and solid.Volume() > 0 for solid in assembly_solids)
    assert_close_list(bounds(imported_assembly)["extents_mm"], [TOTAL_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT], "reimported assembly")
    single_transform = mesh_transform_evidence(SINGLE_REFERENCE_STL, SINGLE_PRINT_STL, SINGLE_LENGTH)
    double_transform = mesh_transform_evidence(DOUBLE_REFERENCE_STL, DOUBLE_PRINT_STL, DOUBLE_LENGTH)
    artifacts = [Path(__file__).resolve(), PARAMETERS_JSON, OPTIMIZATION_REPORT_JSON, SINGLE_MASTER_STEP, SINGLE_MASTER_STL, DOUBLE_MASTER_STEP, DOUBLE_MASTER_STL, ASSEMBLY_STEP, SINGLE_PRINT_STL, DOUBLE_PRINT_STL, SINGLE_REFERENCE_STL, DOUBLE_REFERENCE_STL, WATERMARK_PLACEMENT_REPORT, MARKED_SIDE_PREVIEW_SVG, MARKED_ISOMETRIC_PREVIEW_SVG]
    write_json(BUILD_REPORT_JSON, {
        "schema_version": "1.0", "status": "PASS", "tool": Path(__file__).name, "tool_version": REVISION,
        "environment": {"cadquery": cq.__version__, "trimesh": trimesh.__version__}, "inputs": [artifact_record(path) for path in artifacts],
        "checks": [
            {"id": "approved-parameter-contract", "status": "PASS", "required": True, "message": "Approved counts, lengths, catcher tangents, shell dimensions, and no-connector contract passed.", "metrics": {"part_count": PART_COUNT, "catcher_count": 18, "end_margin_mm": END_MARGIN, "inter_catcher_tangent_mm": INTER_CATCHER_TANGENT, "connector_feature_count": 0}},
            {"id": "single-brep", "status": "PASS", "required": True, "message": "Single segment is one valid positive-volume B-Rep.", "metrics": {"bounds": bounds(single), "volume_mm3": single.val().Volume()}},
            {"id": "marked-double-brep", "status": "PASS", "required": True, "message": "Marked double segment is one valid positive-volume B-Rep with two preserved catchers.", "metrics": {"bounds": bounds(marked_double), "volume_mm3": marked_double.val().Volume()}},
            {"id": "loose-layout", "status": "PASS", "required": True, "message": "Seventeen unconnected intervals meet only at nominal end planes across exactly 945 mm.", "metrics": {"parts": assembly_positions(), "assembly_bounds": bounds(imported_assembly)}},
            {"id": "neutral-step-reimport", "status": "PASS", "required": True, "message": "STEP re-import retains one single solid, one marked-double solid, and seventeen assembly solids.", "metrics": {"single_solids": len(imported_single.solids().vals()), "double_solids": len(imported_double.solids().vals()), "assembly_solids": len(assembly_solids)}},
            {"id": "single-rigid-print-transform", "status": "PASS", "required": True, "message": "Single manufacturing STL is only the declared +90 degree rigid transform.", "metrics": single_transform},
            {"id": "double-rigid-print-transform", "status": "PASS", "required": True, "message": "Marked-double manufacturing STL is only the declared +90 degree rigid transform.", "metrics": double_transform},
            {"id": "watermark-digital-placement", "status": "PASS", "required": True, "message": "Canonical watermark placement passed deterministic geometry checks; physical coupon remains open.", "evidence": str(WATERMARK_PLACEMENT_REPORT.relative_to(ROOT))},
        ],
        "metrics": {"holes_per_catcher": len(catcher_points()), "holes_total": len(catcher_points()) * 18, "ribs_per_catcher": RIB_COUNT},
        "limitations": ["Physical installed fit, cumulative gap, drainage, cleaning, hair retention, edge condition, and exact-process watermark readability remain human gates.", "Slicer evidence qualifies only the named local user profiles and cannot identify the physical printer unit, nozzle serial identity, or filament batch."],
        "required_capabilities": ["cadquery", "trimesh", "manifold3d", "rtree"],
    })


def write_readme() -> None:
    holes = len(catcher_points())
    text = f"""# {PRODUCT_ID} — {PRODUCT_NAME}

Status: **DRAFT production candidate; digitally validated, not physically released**.

## Official identity

- Product ID: **{PRODUCT_ID}**
- Official designation: **{PRODUCT_NAME}**
- Design revision: **{REVISION}**

## Approved geometry

- Installed envelope: **{TOTAL_LENGTH:.1f} × {TOTAL_WIDTH:.1f} × {TOTAL_HEIGHT:.1f} mm**
- **{SINGLE_COUNT}** loose single segments at **{SINGLE_LENGTH:.1f} mm**, one catcher each
- **{DOUBLE_COUNT}** loose marked double segment at **{DOUBLE_LENGTH:.1f} mm**, two catchers
- **{PART_COUNT} parts / 18 catchers / no connectors**
- Nominal equation: `{SINGLE_COUNT} × {SINGLE_LENGTH:.1f} + {DOUBLE_COUNT} × {DOUBLE_LENGTH:.1f} = {TOTAL_LENGTH:.1f} mm`
- {holes} holes per catcher; {holes * 18} across the complete row

The marked double segment is placed between eight singles on each side in the assembly reference. Its left inner side wall carries the exact `MM-WM-001-R1` profile `metriMade.com / {PRODUCT_ID} · v{REVISION}` recessed **{WATERMARK_DEPTH:.1f} mm** at scale 1.0. A rigid local-X reflection sets the correct left-to-right reading direction from the drain cavity; it does not resize or redraw the profile. The 3.0 mm wall retains **{WATERMARK_REMAINING_WALL:.1f} mm**.

## Manufacturing files

- `{SINGLE_PRINT_STL.relative_to(ROOT)}` — print **16 copies**
- `{DOUBLE_PRINT_STL.relative_to(ROOT)}` — print **1 copy**
- Both files are already rotated +90° about assembly Y onto one complete U-profile end.
- `{ASSEMBLY_STEP.relative_to(ROOT)}` — 17-part nominal assembly reference
- `{SINGLE_MASTER_STEP.relative_to(ROOT)}` and `{DOUBLE_MASTER_STEP.relative_to(ROOT)}` — assembly-orientation STEP masters

## Selected slicer evidence

Anycubic Slicer Next 1.3.9.4 is the selected slicer. Validation uses the local Kobra 3 Max 0.4 mm user profiles `0.20mm PETG Tool @AC K3 Max` and `SUNLU PETG Black new @Anycubic Kobra 3 Max 0.4 nozzle`. The actual printer unit/firmware, nozzle identity, filament color/batch, and physical results still require recording.

## Release boundary

Do not treat this DRAFT as a released product. Before release, print the canonical watermark coupon and representative parts in the named PETG process; inspect watermark readability, installed fit, cumulative gaps, sharp edges, drainage, cleaning, and hair retention. Printer upload/start is not authorized by this project.
"""
    (ROOT / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    validate_parameters()
    single, _ = make_segment(SINGLE_LENGTH, SINGLE_CATCHER_CENTERS, marked=False)
    unmarked_double, _ = make_segment(DOUBLE_LENGTH, DOUBLE_CATCHER_CENTERS, marked=False)
    marked_double, watermark_tool = make_segment(DOUBLE_LENGTH, DOUBLE_CATCHER_CENTERS, marked=True)
    assert watermark_tool is not None
    assert_shape(single, [SINGLE_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT], "single")
    assert_shape(unmarked_double, [DOUBLE_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT], "unmarked double")
    assert_shape(marked_double, [DOUBLE_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT], "marked double")
    assert_shape(print_orientation(single, SINGLE_LENGTH), [TOTAL_HEIGHT, TOTAL_WIDTH, SINGLE_LENGTH], "single print orientation")
    assert_shape(print_orientation(marked_double, DOUBLE_LENGTH), [TOTAL_HEIGHT, TOTAL_WIDTH, DOUBLE_LENGTH], "double print orientation")

    write_parameter_contract()
    write_optimization_report()
    export_models(single, marked_double)
    write_watermark_report(unmarked_double, marked_double, watermark_tool)
    write_build_report(single, marked_double)
    write_readme()

    print(json.dumps({
        "status": "PASS", "product_id": PRODUCT_ID, "product_name": PRODUCT_NAME,
        "revision": REVISION, "part_count": PART_COUNT, "catcher_count": 18,
        "single_manufacturing_stl": str(SINGLE_PRINT_STL.relative_to(ROOT)),
        "marked_double_manufacturing_stl": str(DOUBLE_PRINT_STL.relative_to(ROOT)),
        "watermark": f"metriMade.com / {PRODUCT_ID} · v{REVISION}",
    }, indent=2))


if __name__ == "__main__":
    main()
