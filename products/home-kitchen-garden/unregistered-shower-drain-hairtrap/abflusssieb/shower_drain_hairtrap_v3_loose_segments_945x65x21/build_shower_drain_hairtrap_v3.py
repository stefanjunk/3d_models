#!/usr/bin/env python3
"""Build the approved loose-segment shower-drain hair trap v3.

Assembly coordinates use millimetres:
    X = installed drain length
    Y = installed drain width
    Z = installed height

The manufacturing STL is rotated +90 degrees around global Y. The original
X=max U-profile end is translated onto Z=0, so segment length becomes print
height. STEP remains in assembly orientation.
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


ROOT = Path(__file__).resolve().parent
MASTER_DIR = ROOT / "exports" / "master"
MANUFACTURING_DIR = ROOT / "exports" / "manufacturing"
VALIDATION_EXPORT_DIR = ROOT / "exports" / "validation"
BUILD_DIR = ROOT / "build"

PRODUCT_ID = "SHOWER-DRAIN-HAIRTRAP"
REVISION = "3.0.0-draft.1"
FILE_PREFIX = f"DRAFT-{PRODUCT_ID}-{REVISION}"

# ---------------------------------------------------------------------------
# Approved user-facing parameters (mm)
# ---------------------------------------------------------------------------
TOTAL_LENGTH = 945.0
TOTAL_WIDTH = 65.0
TOTAL_HEIGHT = 21.0
SEGMENT_COUNT = 18
SEGMENT_LENGTH = TOTAL_LENGTH / SEGMENT_COUNT

# Inverted-U shell retained from funnel-edge v1.3.
TOP_T = 4.2
SIDE_WALL_T = 3.0
SIDE_WALL_H = TOTAL_HEIGHT - TOP_T
CORNER_R = 1.6

# One retained funnel/catcher per segment.
CATCHER_COUNT_PER_SEGMENT = 1
CATCHER_D = 46.0
CATCHER_R = CATCHER_D / 2.0
CATCHER_X = SEGMENT_LENGTH / 2.0
CATCHER_Y = TOTAL_WIDTH / 2.0
END_MARGIN = (SEGMENT_LENGTH - CATCHER_D) / 2.0
MIN_END_MARGIN = 3.0

FUNNEL_DEPTH = 2.5
FUNNEL_ENTRY_R = 23.0
FUNNEL_FLOOR_R = 19.0
FUNNEL_FLOOR_Z = TOTAL_HEIGHT - FUNNEL_DEPTH
HOLE_D = 2.8
HOLE_PITCH = 4.3
HOLE_FIELD_R = 16.0

# Edge-start swirl ribs retained from funnel-edge v1.3.
RIB_W = 1.6
RIB_H = FUNNEL_DEPTH - 0.02
RIB_COUNT = 5
RIB_START_R = FUNNEL_ENTRY_R - RIB_W / 2.0 + 0.05
RIB_END_R = 10.2
RIB_SWEEP = math.radians(126.0)
RIB_STEPS = 24
CENTER_BOSS_R = 2.8

# Export policy. STEP/B-Rep is authoritative. Manufacturing reuses the exact
# master tessellation because the available validation environment cannot run
# an exact triangle-distance check for an independently simplified mesh.
MASTER_STL_TOLERANCE = 0.05
MASTER_STL_ANGULAR_TOLERANCE = 0.12
MANUFACTURING_STL_TOLERANCE = MASTER_STL_TOLERANCE
MANUFACTURING_STL_ANGULAR_TOLERANCE = MASTER_STL_ANGULAR_TOLERANCE

MASTER_STEP = MASTER_DIR / f"{FILE_PREFIX}-segment-master.step"
MASTER_STL = MASTER_DIR / f"{FILE_PREFIX}-segment-master.stl"
ASSEMBLY_STEP = MASTER_DIR / f"{FILE_PREFIX}-18x-assembly-reference.step"
MANUFACTURING_STL = MANUFACTURING_DIR / f"{FILE_PREFIX}-segment-on-end.stl"
MANUFACTURING_REFERENCE_STL = (
    VALIDATION_EXPORT_DIR / f"{FILE_PREFIX}-segment-manufacturing-tessellation-reference.stl"
)
PARAMETERS_JSON = BUILD_DIR / "parameters.json"
BUILD_REPORT_JSON = BUILD_DIR / "build-report.json"
OPTIMIZATION_REPORT_JSON = BUILD_DIR / "segment-count-optimization.json"


def validate_parameters() -> None:
    """Reject geometry that violates the approved contract before booleans."""
    assert TOTAL_LENGTH > 0 and TOTAL_WIDTH > 0 and TOTAL_HEIGHT > 0
    assert isinstance(SEGMENT_COUNT, int) and SEGMENT_COUNT > 0
    assert math.isclose(SEGMENT_COUNT * SEGMENT_LENGTH, TOTAL_LENGTH, abs_tol=1e-9)
    assert math.isclose(SEGMENT_LENGTH, 52.5, abs_tol=1e-9)
    assert CATCHER_COUNT_PER_SEGMENT == 1
    assert math.isclose(CATCHER_D, 46.0, abs_tol=1e-9)
    assert END_MARGIN >= MIN_END_MARGIN
    assert math.isclose(END_MARGIN, 3.25, abs_tol=1e-9)
    assert 0 < FUNNEL_DEPTH < TOP_T
    assert 0 < HOLE_FIELD_R < FUNNEL_FLOOR_R < FUNNEL_ENTRY_R
    assert 0 < SIDE_WALL_T < TOTAL_WIDTH / 2.0
    assert math.isclose(SIDE_WALL_H + TOP_T, TOTAL_HEIGHT, abs_tol=1e-9)
    assert 0 < CORNER_R < min(SIDE_WALL_T, TOP_T)


def single_catcher_points() -> list[tuple[float, float]]:
    """Return the v1.3 hexagonal sieve field in catcher-local coordinates."""
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
    """Create one closed, constant-width curved rib profile."""
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


def make_base_u() -> cq.Workplane:
    """Build one connector-free inverted-U shell in assembly coordinates."""
    top = (
        cq.Workplane("XY")
        .box(SEGMENT_LENGTH, TOTAL_WIDTH, TOP_T, centered=(False, False, False))
        .translate((0.0, 0.0, TOTAL_HEIGHT - TOP_T))
    )
    left_wall = cq.Workplane("XY").box(
        SEGMENT_LENGTH, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False)
    )
    right_wall = (
        cq.Workplane("XY")
        .box(SEGMENT_LENGTH, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False))
        .translate((0.0, TOTAL_WIDTH - SIDE_WALL_T, 0.0))
    )
    body = top.union(left_wall).union(right_wall)
    try:
        body = body.edges("|Z").fillet(CORNER_R)
    except Exception:
        # The exact v1.3 behavior permits a valid unfilleted fallback.
        pass
    return body


def make_funnel_tool() -> cq.Workplane:
    """Create the shallow funnel cut at the single segment center."""
    return (
        cq.Workplane("XY", origin=(CATCHER_X, CATCHER_Y, TOTAL_HEIGHT))
        .circle(FUNNEL_ENTRY_R)
        .workplane(offset=-FUNNEL_DEPTH)
        .circle(FUNNEL_FLOOR_R)
        .loft(combine=True, ruled=False)
    )


def make_rib_solid(phase_rad: float) -> cq.Workplane:
    """Intersect a rib prism with the funnel so its outer end stays flush."""
    rib_prism = (
        cq.Workplane("XY", origin=(CATCHER_X, CATCHER_Y, FUNNEL_FLOOR_Z))
        .polyline(spiral_band_points(phase_rad))
        .close()
        .extrude(FUNNEL_DEPTH + 0.04)
    )
    return rib_prism.intersect(make_funnel_tool())


def make_segment() -> cq.Workplane:
    """Build the approved single solid with one funnel and no connectors."""
    segment = make_base_u().cut(make_funnel_tool())

    hole_centers = [
        (CATCHER_X + xx, CATCHER_Y + yy) for xx, yy in single_catcher_points()
    ]
    holes = (
        cq.Workplane("XY", origin=(0.0, 0.0, TOTAL_HEIGHT - TOP_T - 0.05))
        .pushPoints(hole_centers)
        .circle(HOLE_D / 2.0)
        .extrude(TOP_T + 0.10)
    )
    segment = segment.cut(holes)

    for rib_index in range(RIB_COUNT):
        phase = rib_index * 2.0 * math.pi / RIB_COUNT
        segment = segment.union(make_rib_solid(phase), clean=False)

    center_boss = (
        cq.Workplane("XY", origin=(CATCHER_X, CATCHER_Y, FUNNEL_FLOOR_Z))
        .circle(CENTER_BOSS_R)
        .extrude(max(0.8, FUNNEL_DEPTH * 0.52))
    )
    segment = segment.union(center_boss, clean=False)
    try:
        segment = segment.clean()
    except Exception:
        pass
    return segment


def print_orientation(segment: cq.Workplane) -> cq.Workplane:
    """Stand the original X=max U-profile end on Z=0."""
    return segment.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0).translate(
        (0.0, 0.0, SEGMENT_LENGTH)
    )


def bounding_box(shape: cq.Workplane) -> list[float]:
    box = shape.val().BoundingBox()
    return [box.xlen, box.ylen, box.zlen]


def bounding_box_limits(shape: cq.Workplane) -> dict[str, list[float]]:
    box = shape.val().BoundingBox()
    return {
        "minimum_mm": [box.xmin, box.ymin, box.zmin],
        "maximum_mm": [box.xmax, box.ymax, box.zmax],
        "extents_mm": [box.xlen, box.ylen, box.zlen],
    }


def assert_shape(shape: cq.Workplane, expected_bounds: list[float], label: str) -> None:
    solids = shape.solids().vals()
    assert len(solids) == 1, f"{label}: expected one solid, got {len(solids)}"
    assert solids[0].isValid(), f"{label}: OpenCascade reports an invalid solid"
    actual_bounds = bounding_box(shape)
    for axis, (actual, expected) in enumerate(zip(actual_bounds, expected_bounds)):
        assert math.isclose(actual, expected, abs_tol=1e-5), (
            f"{label}: axis {axis} bound {actual} != {expected}"
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parameter_contract() -> dict[str, object]:
    points_per_catcher = len(single_catcher_points())
    return {
        "schema_version": "1.0",
        "product_id": PRODUCT_ID,
        "revision": REVISION,
        "units": "mm",
        "installed_envelope_mm": [TOTAL_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT],
        "segment_count": SEGMENT_COUNT,
        "segment_length_mm": SEGMENT_LENGTH,
        "segment_width_mm": TOTAL_WIDTH,
        "segment_height_mm": TOTAL_HEIGHT,
        "catchers_per_segment": CATCHER_COUNT_PER_SEGMENT,
        "catcher_count_total": SEGMENT_COUNT * CATCHER_COUNT_PER_SEGMENT,
        "catcher_entry_diameter_mm": CATCHER_D,
        "catcher_center_xy_mm": [CATCHER_X, CATCHER_Y],
        "end_margin_each_side_mm": END_MARGIN,
        "minimum_end_margin_mm": MIN_END_MARGIN,
        "top_thickness_mm": TOP_T,
        "side_wall_thickness_mm": SIDE_WALL_T,
        "side_wall_height_mm": SIDE_WALL_H,
        "funnel_floor_diameter_mm": 2.0 * FUNNEL_FLOOR_R,
        "funnel_depth_mm": FUNNEL_DEPTH,
        "hole_diameter_mm": HOLE_D,
        "hole_pitch_mm": HOLE_PITCH,
        "holes_per_catcher": points_per_catcher,
        "holes_total": SEGMENT_COUNT * points_per_catcher,
        "rib_count_per_catcher": RIB_COUNT,
        "connector_features": [],
        "nominal_length_equation": f"{SEGMENT_COUNT} * {SEGMENT_LENGTH} = {TOTAL_LENGTH}",
        "print_transform": {
            "axis": [0.0, 1.0, 0.0],
            "angle_degrees": 90.0,
            "translation_mm": [0.0, 0.0, SEGMENT_LENGTH],
            "bed_contact": "original X=max inverted-U end cross-section",
        },
        "export_tessellation": {
            "master_stl": {
                "linear_tolerance_mm": MASTER_STL_TOLERANCE,
                "angular_tolerance_rad": MASTER_STL_ANGULAR_TOLERANCE,
            },
            "manufacturing_stl": {
                "linear_tolerance_mm": MANUFACTURING_STL_TOLERANCE,
                "angular_tolerance_rad": MANUFACTURING_STL_ANGULAR_TOLERANCE,
            },
        },
    }


def segment_count_candidates() -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for count in (16, 17, 18, 19):
        length = TOTAL_LENGTH / count
        margin = (length - CATCHER_D) / 2.0
        candidates.append(
            {
                "segment_count": count,
                "catcher_count": count,
                "segment_length_mm": length,
                "end_margin_each_side_mm": margin,
                "minimum_margin_pass": margin >= MIN_END_MARGIN,
                "feasible": margin >= MIN_END_MARGIN,
            }
        )
    return candidates


def write_optimization_report() -> None:
    candidates = segment_count_candidates()
    feasible = [candidate for candidate in candidates if candidate["feasible"]]
    selected = max(feasible, key=lambda candidate: int(candidate["catcher_count"]))
    assert selected["segment_count"] == SEGMENT_COUNT
    write_json(
        OPTIMIZATION_REPORT_JSON,
        {
            "schema_version": "1.0",
            "tool": "build_shower_drain_hairtrap_v3.py",
            "tool_version": REVISION,
            "status": "PASS",
            "inputs": [
                {
                    "path": "design-spec.yaml",
                    "sha256": sha256_file(ROOT / "design-spec.yaml"),
                    "size_bytes": (ROOT / "design-spec.yaml").stat().st_size,
                }
            ],
            "checks": [
                {
                    "id": "candidate-count",
                    "status": "PASS",
                    "required": True,
                    "message": "Compared the approved baseline and adjacent integer segment counts.",
                    "metrics": {"candidate_count": len(candidates)},
                },
                {
                    "id": "maximum-feasible-catcher-count",
                    "status": "PASS",
                    "required": True,
                    "message": "Selected the highest catcher count retaining at least the approved 3.0 mm end margin.",
                    "metrics": {
                        "selected_segment_count": selected["segment_count"],
                        "selected_segment_length_mm": selected["segment_length_mm"],
                        "selected_end_margin_mm": selected["end_margin_each_side_mm"],
                        "first_rejected_segment_count": 19,
                        "first_rejected_end_margin_mm": candidates[-1]["end_margin_each_side_mm"],
                    },
                },
                {
                    "id": "exact-nominal-total-length",
                    "status": "PASS",
                    "required": True,
                    "message": "Selected identical segments sum exactly to the 945 mm nominal drain length.",
                    "metrics": {
                        "calculated_total_length_mm": SEGMENT_COUNT * SEGMENT_LENGTH,
                        "target_total_length_mm": TOTAL_LENGTH,
                    },
                },
            ],
            "metrics": {
                "objective": "maximize catcher count",
                "constraint": f"end_margin_each_side_mm >= {MIN_END_MARGIN}",
                "candidates": candidates,
                "selected_variant": f"{SEGMENT_COUNT}-identical-segments",
            },
            "limitations": [
                "This report selects segment/catcher count geometrically; it does not provide exact-slicer time or material metrics.",
                "Cumulative installed-fit error remains a physical gate because the loose parts have no connectors or prescribed gaps.",
            ],
            "required_capabilities": [],
        },
    )


def detached_copy(shape: cq.Workplane) -> cq.Workplane:
    """Copy a B-Rep before tessellation mutates its cached bounding box."""
    return cq.Workplane("XY").newObject([shape.val().copy()])


def print_mesh_transform() -> np.ndarray:
    """Return the declared assembly-to-print rigid transform."""
    rotation = trimesh.transformations.rotation_matrix(
        math.radians(90.0), [0.0, 1.0, 0.0]
    )
    translation = trimesh.transformations.translation_matrix(
        [0.0, 0.0, SEGMENT_LENGTH]
    )
    return trimesh.transformations.concatenate_matrices(translation, rotation)


def export_models(segment: cq.Workplane, print_segment: cq.Workplane) -> None:
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    MANUFACTURING_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    cq.exporters.export(detached_copy(segment), str(MASTER_STEP))
    cq.exporters.export(
        detached_copy(segment),
        str(MASTER_STL),
        tolerance=MASTER_STL_TOLERANCE,
        angularTolerance=MASTER_STL_ANGULAR_TOLERANCE,
    )
    shutil.copyfile(MASTER_STL, MANUFACTURING_REFERENCE_STL)
    assert sha256_file(MASTER_STL) == sha256_file(MANUFACTURING_REFERENCE_STL)

    # Derive the actual print STL from the already-selected tessellation. This
    # guarantees that orientation is a pure rigid mesh transform, not a second
    # independently tessellated approximation.
    manufacturing_mesh = trimesh.load_mesh(
        MANUFACTURING_REFERENCE_STL, process=True, force="mesh"
    )
    manufacturing_mesh.apply_transform(print_mesh_transform())
    assert manufacturing_mesh.is_watertight
    assert manufacturing_mesh.is_winding_consistent
    manufacturing_mesh.export(MANUFACTURING_STL, file_type="stl")

    assembly = cq.Assembly(name=f"{PRODUCT_ID}-{REVISION}-18x")
    for index in range(SEGMENT_COUNT):
        assembly.add(
            segment,
            name=f"segment_{index + 1:02d}",
            loc=cq.Location(cq.Vector(index * SEGMENT_LENGTH, 0.0, 0.0)),
        )
    assembly.save(str(ASSEMBLY_STEP))


def write_build_report(segment: cq.Workplane, print_segment: cq.Workplane) -> None:
    artifacts = [
        Path(__file__).resolve(),
        PARAMETERS_JSON,
        OPTIMIZATION_REPORT_JSON,
        MASTER_STEP,
        MASTER_STL,
        ASSEMBLY_STEP,
        MANUFACTURING_STL,
        MANUFACTURING_REFERENCE_STL,
    ]
    segment_bounds = bounding_box_limits(segment)
    print_bounds = bounding_box_limits(print_segment)
    segment_volume = segment.val().Volume()
    print_volume = print_segment.val().Volume()
    segment_intervals = [
        [index * SEGMENT_LENGTH, (index + 1) * SEGMENT_LENGTH]
        for index in range(SEGMENT_COUNT)
    ]
    neighbor_gaps = [
        segment_intervals[index + 1][0] - segment_intervals[index][1]
        for index in range(SEGMENT_COUNT - 1)
    ]
    assert all(math.isclose(gap, 0.0, abs_tol=1e-9) for gap in neighbor_gaps)

    # Re-import neutral CAD exports to prove that their stored topology and
    # envelopes survive serialization independently of the in-memory source.
    imported_master = cq.importers.importStep(str(MASTER_STEP))
    imported_assembly = cq.importers.importStep(str(ASSEMBLY_STEP))
    imported_master_solids = imported_master.solids().vals()
    imported_assembly_solids = imported_assembly.solids().vals()
    imported_master_bounds = bounding_box_limits(imported_master)
    imported_assembly_bounds = bounding_box_limits(imported_assembly)
    assert_shape(
        imported_master,
        [SEGMENT_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT],
        "reimported_master_step",
    )
    assert len(imported_assembly_solids) == SEGMENT_COUNT
    assert all(solid.isValid() for solid in imported_assembly_solids)
    for actual, expected in zip(
        imported_assembly_bounds["extents_mm"],
        [TOTAL_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT],
    ):
        assert math.isclose(actual, expected, abs_tol=1e-5)

    # The print STL must differ from the selected manufacturing tessellation
    # only by the declared rigid transform. Compare its inverse-transformed
    # vertex set after both STL files are independently parsed and welded.
    reference_mesh = trimesh.load_mesh(
        MANUFACTURING_REFERENCE_STL, process=True, force="mesh"
    )
    stored_print_mesh = trimesh.load_mesh(
        MANUFACTURING_STL, process=True, force="mesh"
    )
    inverse_oriented_mesh = stored_print_mesh.copy()
    inverse_oriented_mesh.apply_transform(np.linalg.inv(print_mesh_transform()))
    reference_vertices = reference_mesh.vertices[
        np.lexsort(
            (
                reference_mesh.vertices[:, 2],
                reference_mesh.vertices[:, 1],
                reference_mesh.vertices[:, 0],
            )
        )
    ]
    inverse_vertices = inverse_oriented_mesh.vertices[
        np.lexsort(
            (
                inverse_oriented_mesh.vertices[:, 2],
                inverse_oriented_mesh.vertices[:, 1],
                inverse_oriented_mesh.vertices[:, 0],
            )
        )
    ]
    assert reference_vertices.shape == inverse_vertices.shape
    max_inverse_vertex_delta = float(
        np.max(np.abs(reference_vertices - inverse_vertices))
    )
    assert max_inverse_vertex_delta <= 1e-5
    assert len(reference_mesh.faces) == len(stored_print_mesh.faces)
    assert math.isclose(reference_mesh.volume, stored_print_mesh.volume, rel_tol=1e-8)
    print_mesh_bounds = {
        "minimum_mm": stored_print_mesh.bounds[0].tolist(),
        "maximum_mm": stored_print_mesh.bounds[1].tolist(),
        "extents_mm": stored_print_mesh.extents.tolist(),
    }
    assert abs(print_mesh_bounds["minimum_mm"][2]) <= 1e-6
    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "tool": "build_shower_drain_hairtrap_v3.py",
        "tool_version": REVISION,
        "environment": {"cadquery": cq.__version__, "trimesh": trimesh.__version__},
        "inputs": [
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for path in artifacts
        ],
        "checks": [
            {
                "id": "parameter-assertions",
                "status": "PASS",
                "required": True,
                "message": "Approved dimension, margin, catcher-count and no-connector assertions passed before geometry generation.",
                "metrics": {
                    "segment_count": SEGMENT_COUNT,
                    "segment_length_mm": SEGMENT_LENGTH,
                    "end_margin_each_side_mm": END_MARGIN,
                    "nominal_total_length_mm": SEGMENT_COUNT * SEGMENT_LENGTH,
                    "connector_feature_count": 0,
                },
            },
            {
                "id": "assembly-brep",
                "status": "PASS",
                "required": True,
                "message": "Assembly-orientation segment is one valid positive-volume B-Rep with approved extents.",
                "metrics": {
                    "bounds": segment_bounds,
                    "solid_count": len(segment.solids().vals()),
                    "valid": segment.val().isValid(),
                    "volume_mm3": segment_volume,
                },
            },
            {
                "id": "loose-segment-layout",
                "status": "PASS",
                "required": True,
                "message": "Eighteen unconnected segment intervals meet only at nominal end planes, with zero nominal gap, overlap or protrusion across 945 mm.",
                "metrics": {
                    "segment_intervals_mm": segment_intervals,
                    "neighbor_gap_mm": neighbor_gaps,
                    "minimum_neighbor_gap_mm": min(neighbor_gaps),
                    "maximum_neighbor_gap_mm": max(neighbor_gaps),
                    "total_layout_length_mm": segment_intervals[-1][1],
                },
            },
            {
                "id": "print-brep",
                "status": "PASS",
                "required": True,
                "message": "Print-oriented segment is one valid B-Rep with 21 x 65 x 52.5 mm extents and Z minimum at the bed.",
                "metrics": {
                    "bounds": print_bounds,
                    "solid_count": len(print_segment.solids().vals()),
                    "valid": print_segment.val().isValid(),
                    "volume_mm3": print_volume,
                },
            },
            {
                "id": "rigid-print-transform",
                "status": "PASS",
                "required": True,
                "message": "The declared 90-degree rigid transform preserves B-Rep volume and places one U-profile end on Z=0.",
                "metrics": {
                    "volume_delta_mm3": print_volume - segment_volume,
                    "volume_delta_percent": abs(print_volume - segment_volume) / segment_volume * 100.0,
                    "print_z_min_mm": print_bounds["minimum_mm"][2],
                    "axis": [0.0, 1.0, 0.0],
                    "angle_degrees": 90.0,
                },
            },
            {
                "id": "neutral-step-reimport",
                "status": "PASS",
                "required": True,
                "message": "Re-imported STEP exports retain one valid segment solid and eighteen valid loose assembly solids with nominal extents.",
                "metrics": {
                    "master_solid_count": len(imported_master_solids),
                    "master_bounds": imported_master_bounds,
                    "assembly_solid_count": len(imported_assembly_solids),
                    "assembly_bounds": imported_assembly_bounds,
                    "assembly_all_solids_valid": all(
                        solid.isValid() for solid in imported_assembly_solids
                    ),
                },
            },
            {
                "id": "stored-mesh-orientation",
                "status": "PASS",
                "required": True,
                "message": "Inverse-transforming the stored on-end STL reproduces the selected assembly-oriented manufacturing tessellation within numeric STL precision.",
                "metrics": {
                    "reference_vertex_count": len(reference_mesh.vertices),
                    "print_vertex_count": len(stored_print_mesh.vertices),
                    "reference_face_count": len(reference_mesh.faces),
                    "print_face_count": len(stored_print_mesh.faces),
                    "maximum_inverse_vertex_delta_mm": max_inverse_vertex_delta,
                    "reference_volume_mm3": reference_mesh.volume,
                    "print_volume_mm3": stored_print_mesh.volume,
                    "print_mesh_bounds": print_mesh_bounds,
                },
            },
            {
                "id": "manufacturing-tessellation-source",
                "status": "PASS",
                "required": True,
                "message": "The assembly-oriented manufacturing reference is a byte-identical copy of the audited master STL; no unverified mesh simplification is used.",
                "metrics": {
                    "master_sha256": sha256_file(MASTER_STL),
                    "manufacturing_reference_sha256": sha256_file(
                        MANUFACTURING_REFERENCE_STL
                    ),
                    "byte_identical": sha256_file(MASTER_STL)
                    == sha256_file(MANUFACTURING_REFERENCE_STL),
                },
            },
        ],
        "metrics": {
            "holes_per_catcher": len(single_catcher_points()),
            "catchers_total": SEGMENT_COUNT,
            "ribs_per_catcher": RIB_COUNT,
        },
        "limitations": [
            "No exact slicer/profile was available; toolpath, support and time metrics are not asserted.",
            "Physical installed fit, cumulative gaps, drainage, cleaning and hair retention remain human gates.",
            "Watermark integration is intentionally deferred until after primary candidate verification.",
        ],
        "required_capabilities": ["cadquery", "trimesh"],
    }
    write_json(BUILD_REPORT_JSON, report)


def write_readme() -> None:
    holes_per_catcher = len(single_catcher_points())
    gross_open_area = (
        SEGMENT_COUNT * holes_per_catcher * math.pi * (HOLE_D / 2.0) ** 2
    )
    text = f"""# Shower drain hair trap v3 — loose single-funnel segments

Status: **DRAFT print candidate; not physically validated and not released**.

## Geometry

- Nominal installed envelope: **{TOTAL_LENGTH:.1f} × {TOTAL_WIDTH:.1f} × {TOTAL_HEIGHT:.1f} mm**
- Loose identical segments: **{SEGMENT_COUNT}**
- Segment size in assembly orientation: **{SEGMENT_LENGTH:.1f} × {TOTAL_WIDTH:.1f} × {TOTAL_HEIGHT:.1f} mm**
- One centered {CATCHER_D:.1f} mm funnel per segment
- Solid end margin: **{END_MARGIN:.2f} mm per end**
- Nominal length equation: `{SEGMENT_COUNT} × {SEGMENT_LENGTH:.1f} = {TOTAL_LENGTH:.1f} mm`
- Connectors: **none**

## Preserved catcher geometry

- {holes_per_catcher} sieve holes per catcher, {SEGMENT_COUNT * holes_per_catcher} total
- Hole diameter {HOLE_D:.1f} mm on {HOLE_PITCH:.1f} mm hexagonal pitch
- Five edge-start swirl ribs and one center boss per funnel
- Gross circular hole area across all segments: approximately {gross_open_area:.0f} mm² before rib overlap

## Print orientation

`exports/manufacturing/{MANUFACTURING_STL.name}` is already rotated +90° about assembly Y and translated to the bed. Its envelope is **{TOTAL_HEIGHT:.1f} × {TOTAL_WIDTH:.1f} × {SEGMENT_LENGTH:.1f} mm**. The original X=max U-profile end is the bed-contact cross-section.

The user reports that the earlier coupon worked after a 90° rotation. The exact printer, PETG product, nozzle and slicer profile are not recorded, so support-free behavior remains a slicer and physical test gate.

## Files

- `build_shower_drain_hairtrap_v3.py`: parametric CadQuery source
- `exports/master/{MASTER_STEP.name}`: editable STEP master in assembly orientation
- `exports/master/{MASTER_STL.name}`: high-fidelity STL master in assembly orientation
- `exports/master/{ASSEMBLY_STEP.name}`: eighteen-part nominal assembly reference
- `exports/manufacturing/{MANUFACTURING_STL.name}`: DRAFT on-end manufacturing STL; print 18 copies after validation
- `exports/validation/{MANUFACTURING_REFERENCE_STL.name}`: byte-identical validation copy of the master tessellation
- `build/parameters.json`: machine-readable parameter contract
- `build/build-report.json`: deterministic source/export evidence

Do not add a gap, connector or scaling compensation to all eighteen pieces without a measured installed-fit test; cumulative process error must be handled from physical evidence.
"""
    (ROOT / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    validate_parameters()
    segment = make_segment()
    print_segment = print_orientation(segment)
    assert_shape(segment, [SEGMENT_LENGTH, TOTAL_WIDTH, TOTAL_HEIGHT], "segment")
    assert_shape(
        print_segment,
        [TOTAL_HEIGHT, TOTAL_WIDTH, SEGMENT_LENGTH],
        "print_segment",
    )

    write_json(PARAMETERS_JSON, parameter_contract())
    write_optimization_report()
    export_models(segment, print_segment)
    write_build_report(segment, print_segment)
    write_readme()

    print(
        json.dumps(
            {
                "status": "PASS",
                "segment_count": SEGMENT_COUNT,
                "segment_length_mm": SEGMENT_LENGTH,
                "end_margin_mm": END_MARGIN,
                "holes_per_catcher": len(single_catcher_points()),
                "master_step": str(MASTER_STEP.relative_to(ROOT)),
                "manufacturing_stl": str(MANUFACTURING_STL.relative_to(ROOT)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
