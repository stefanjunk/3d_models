#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-009 tapered drawer filler set.

All dimensions are millimetres. STEP is the neutral master; separate high-
fidelity and manufacturing STL tessellations are retained for comparison.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
PROJECT_ID = "MM-ORG-009"
REVISION = "0.1.0-draft.1"

MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def effective_width(gap: float, rail: dict) -> float:
    return gap - rail["organizer_clearance"] - rail["wall_clearance"]


def width_at(front: float, rear: float, length: float, x: float) -> float:
    return front + (rear - front) * x / length


def rail_widths(parameters: dict, side: str) -> tuple[float, float]:
    rail = parameters["rail"]
    return (
        effective_width(rail[f"{side}_front_gap"], rail),
        effective_width(rail[f"{side}_rear_gap"], rail),
    )


def rib_layout(length: float, end_wall: float, max_pitch: float) -> tuple[list[float], float]:
    usable = length - 2.0 * end_wall
    bay_count = max(1, math.ceil(usable / max_pitch))
    pitch = usable / bay_count
    positions = [end_wall + pitch * index for index in range(1, bay_count)]
    return positions, pitch


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    rail = parameters["rail"]
    gauge = parameters["gauge"]
    limits = parameters["limits"]
    export = parameters["export"]

    assert project["id"] == PROJECT_ID, "project ID mismatch"
    assert project["revision"] == REVISION, "revision mismatch"
    assert project["units"] == "mm", "only millimetres are supported"
    assert limits["length"][0] <= rail["length"] <= limits["length"][1]
    assert limits["height"][0] <= rail["height"] <= limits["height"][1]
    assert rail["length"] <= limits["maximum_part_envelope"][0] - 10.0
    assert rail["height"] <= limits["maximum_part_envelope"][2]
    assert rail["top_skin"] >= 2.0
    assert rail["side_wall"] >= 2.25
    assert rail["end_wall"] >= 2.4
    assert rail["rib_thickness"] >= 1.8
    assert rail["height"] > rail["top_skin"] + 8.0
    assert 0.0 < rail["end_relief"] < rail["end_wall"]
    assert rail["scallop_end_offset"] > rail["scallop_radius"] + rail["end_wall"]
    assert rail["length"] > 2.0 * (rail["scallop_end_offset"] + rail["scallop_radius"])

    gap_names = (
        "left_front_gap",
        "left_rear_gap",
        "right_front_gap",
        "right_rear_gap",
    )
    for name in gap_names:
        assert limits["gap"][0] <= rail[name] <= limits["gap"][1], f"{name} outside range"

    for side in ("left", "right"):
        front, rear = rail_widths(parameters, side)
        assert min(front, rear) >= rail["scallop_depth"] + 1.8, f"{side} scallop wall reserve"
        assert min(front, rear) > 2.0 * rail["side_wall"] + 1.0, f"{side} cavity too narrow"
        assert max(front, rear) <= limits["maximum_part_envelope"][1]
        _, pitch = rib_layout(rail["length"], rail["end_wall"], rail["max_rib_pitch"])
        assert pitch <= rail["max_rib_pitch"] + 1e-9

    assert gauge["minimum_width"] > 0.0
    assert gauge["maximum_width"] <= limits["maximum_part_envelope"][1]
    assert gauge["minimum_width"] < gauge["maximum_width"]
    assert gauge["notch_widths"] == sorted(gauge["notch_widths"])
    assert gauge["notch_widths"][0] > gauge["minimum_width"]
    assert gauge["notch_widths"][-1] <= gauge["maximum_width"]
    assert gauge["thickness"] >= 3.0
    assert gauge["wedge_length"] + gauge["handle_length"] <= 210.0
    assert export["mesh_triangle_budget_each"] > 0
    assert export["mesh_file_budget_mib_each"] > 0.0


def _outer_rail(front: float, rear: float, rail: dict) -> cq.Shape:
    length = rail["length"]
    outer = (
        cq.Workplane("XY")
        .polyline([(0.0, 0.0), (length, 0.0), (length, rear), (0.0, front)])
        .close()
        .extrude(rail["height"])
        .edges("|Z")
        .chamfer(rail["end_relief"])
        .val()
    )
    return outer


def _apply_scallops(shape: cq.Shape, front: float, rear: float, rail: dict) -> cq.Shape:
    centers = (rail["scallop_end_offset"], rail["length"] - rail["scallop_end_offset"])
    for x_pos in centers:
        local_width = width_at(front, rear, rail["length"], x_pos)
        cut_depth = min(rail["scallop_depth"], local_width - 1.8)
        cutter = cq.Solid.makeCylinder(
            rail["scallop_radius"],
            cut_depth + 0.1,
            cq.Vector(x_pos, -0.05, rail["height"] + rail["scallop_center_above_top"]),
            cq.Vector(0.0, 1.0, 0.0),
        )
        shape = shape.cut(cutter)
    return shape.clean()


def make_solid_rail(parameters: dict, side: str) -> cq.Shape:
    rail = parameters["rail"]
    front, rear = rail_widths(parameters, side)
    return _apply_scallops(_outer_rail(front, rear, rail), front, rear, rail)


def make_rail(parameters: dict, side: str) -> cq.Shape:
    rail = parameters["rail"]
    length = rail["length"]
    height = rail["height"]
    front, rear = rail_widths(parameters, side)
    outer = _outer_rail(front, rear, rail)

    x0 = rail["end_wall"]
    x1 = length - rail["end_wall"]
    y0 = rail["side_wall"]
    inner_front = width_at(front, rear, length, x0) - rail["side_wall"]
    inner_rear = width_at(front, rear, length, x1) - rail["side_wall"]
    cavity = (
        cq.Workplane("XY")
        .polyline([(x0, y0), (x1, y0), (x1, inner_rear), (x0, inner_front)])
        .close()
        .extrude(height - rail["top_skin"] + 0.1)
        .translate((0.0, 0.0, -0.05))
        .val()
    )
    result = outer.cut(cavity)

    rib_positions, _ = rib_layout(length, rail["end_wall"], rail["max_rib_pitch"])
    for x_pos in rib_positions:
        rib_box = cq.Solid.makeBox(
            rail["rib_thickness"],
            max(front, rear) + 1.0,
            height - rail["top_skin"],
            cq.Vector(x_pos - rail["rib_thickness"] / 2.0, 0.0, 0.0),
        )
        result = result.fuse(rib_box.intersect(outer))

    result = _apply_scallops(result, front, rear, rail)
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError(f"{side} rail is not one valid solid")
    return result


def make_taper_gauge(parameters: dict) -> cq.Shape:
    gauge = parameters["gauge"]
    length = gauge["wedge_length"]
    minimum = gauge["minimum_width"]
    maximum = gauge["maximum_width"]
    thickness = gauge["thickness"]

    wedge = (
        cq.Workplane("XY")
        .polyline(
            [
                (0.0, -minimum / 2.0),
                (length, -maximum / 2.0),
                (length, maximum / 2.0),
                (0.0, minimum / 2.0),
            ]
        )
        .close()
        .extrude(thickness)
        .val()
    )
    handle_overlap = 4.0
    handle_length = gauge["handle_length"] + handle_overlap
    handle_center_x = (-gauge["handle_length"] + handle_overlap) / 2.0
    handle = (
        cq.Workplane("XY")
        .center(handle_center_x, 0.0)
        .rect(handle_length, gauge["handle_width"])
        .extrude(thickness)
        .edges("|Z")
        .fillet(3.0)
        .val()
    )
    result = handle.fuse(wedge)

    handle_hole = cq.Solid.makeCylinder(
        gauge["handle_hole_diameter"] / 2.0,
        thickness + 0.2,
        cq.Vector(-gauge["handle_length"] + 8.0, 0.0, -0.1),
        cq.Vector(0.0, 0.0, 1.0),
    )
    result = result.cut(handle_hole)

    for target_width in gauge["notch_widths"]:
        x_pos = length * (target_width - minimum) / (maximum - minimum)
        half_width = target_width / 2.0
        for y_pos in (-half_width, half_width):
            notch = cq.Solid.makeCylinder(
                gauge["notch_radius"],
                thickness + 0.2,
                cq.Vector(x_pos, y_pos, -0.1),
                cq.Vector(0.0, 0.0, 1.0),
            )
            result = result.cut(notch)
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("taper gauge is not one valid solid")
    return result


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
    rail = parameters["rail"]
    export = parameters["export"]

    shapes = {
        "left-rail": make_rail(parameters, "left"),
        "right-rail": make_rail(parameters, "right"),
        "taper-gauge": make_taper_gauge(parameters),
    }
    solid_references = {
        "left-rail": make_solid_rail(parameters, "left"),
        "right-rail": make_solid_rail(parameters, "right"),
    }

    manufacturing_paths: dict[str, Path] = {}
    master_metrics: dict[str, dict] = {}
    manufacturing_metrics: dict[str, dict] = {}

    for name, shape in shapes.items():
        step_path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        master_mesh_path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}-master.stl"
        selected_folder = COUPONS if name == "taper-gauge" else MANUFACTURING
        manufacturing_path = selected_folder / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_step(shape, step_path)
        export_stl(shape, master_mesh_path, 0.025, export["angular_tolerance"] / 2.0)
        export_stl(shape, manufacturing_path, export["chordal_tolerance"], export["angular_tolerance"])
        manufacturing_paths[name] = manufacturing_path
        master_metrics[name] = mesh_metrics(master_mesh_path)
        manufacturing_metrics[name] = mesh_metrics(manufacturing_path)

    left_widths = rail_widths(parameters, "left")
    right_widths = rail_widths(parameters, "right")
    layout_y_left = 5.0
    layout_y_right = layout_y_left + max(left_widths) + 8.0
    layout_y_gauge = layout_y_right + max(right_widths) + 8.0
    placements = [(5.0, layout_y_left), (5.0, layout_y_right), (5.0, layout_y_gauge)]
    print_set = THREE_MF / f"DRAFT-{PROJECT_ID}-tapered-drawer-filler-set-{REVISION}.3mf"
    write_3mf(print_set, list(manufacturing_paths.items()), placements)

    mesh_checks: list[dict] = []
    for name, metrics in manufacturing_metrics.items():
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
        {"manufacturing_meshes": manufacturing_metrics, "master_meshes": master_metrics},
        ["Topology and resource budgets do not prove physical fit, finish contact or print quality."],
    )
    write_json(VALIDATION / "mesh-generation-report.json", mesh_report)

    rib_positions, rib_pitch = rib_layout(rail["length"], rail["end_wall"], rail["max_rib_pitch"])
    minimum_scallop_reserve = min(*left_widths, *right_widths) - rail["scallop_depth"]
    interface_report = report(
        f"{PROJECT_ID}-interface-validation",
        [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
        [
            check(
                "loose-clearance",
                rail["organizer_clearance"] > 0.0 and rail["wall_clearance"] > 0.0,
                "Both interface clearances are explicitly loose",
                {
                    "organizer_clearance_mm": rail["organizer_clearance"],
                    "wall_clearance_mm": rail["wall_clearance"],
                },
            ),
            check(
                "effective-widths",
                min(*left_widths, *right_widths) > 0.0,
                "All effective front/rear widths are positive",
                {"left_mm": left_widths, "right_mm": right_widths},
            ),
            check(
                "scallop-reserve",
                minimum_scallop_reserve >= 1.8,
                "Lift scallops retain at least 1.8 mm outer-wall reserve",
                {"minimum_reserve_mm": minimum_scallop_reserve},
            ),
            check(
                "bridge-span",
                rib_pitch - rail["rib_thickness"] <= 12.0,
                "Unsupported top-skin bay remains at or below 12 mm",
                {
                    "rib_pitch_mm": rib_pitch,
                    "rib_count": len(rib_positions),
                    "unsupported_span_mm": rib_pitch - rail["rib_thickness"],
                },
            ),
            check(
                "envelope",
                all(
                    metrics["extents_mm"][0] <= parameters["limits"]["maximum_part_envelope"][0]
                    and metrics["extents_mm"][1] <= parameters["limits"]["maximum_part_envelope"][1]
                    and metrics["extents_mm"][2] <= parameters["limits"]["maximum_part_envelope"][2]
                    for metrics in manufacturing_metrics.values()
                ),
                "All parts fit the declared research envelope",
                {name: metrics["extents_mm"] for name, metrics in manufacturing_metrics.items()},
            ),
        ],
        {
            "left_effective_front_rear_mm": left_widths,
            "right_effective_front_rear_mm": right_widths,
            "physical_fit": "NOT_RUN",
            "finish_contact": "NOT_RUN",
            "removal_cycles": "NOT_RUN",
        },
        ["Nominal dimensions and loose clearances do not prove a real drawer fit or prevent all finish marking."],
    )
    write_json(VALIDATION / "interface-report.json", interface_report)

    baseline_volumes = {name: float(shape.Volume()) for name, shape in solid_references.items()}
    selected_volumes = {
        name: float(shapes[name].Volume()) for name in ("left-rail", "right-rail")
    }
    reductions = {
        name: 100.0 * (baseline_volumes[name] - selected_volumes[name]) / baseline_volumes[name]
        for name in baseline_volumes
    }
    optimization_report = report(
        f"{PROJECT_ID}-optimization-comparison",
        [PARAMETERS, Path(__file__), ROOT / "protected-geometry-map.md"],
        [
            check("protected-map", True, "Protected geometry map is present"),
            check(
                "left-volume-reduction",
                reductions["left-rail"] >= 25.0,
                "Left ribbed shell materially reduces CAD volume",
                {"reduction_percent": reductions["left-rail"]},
            ),
            check(
                "right-volume-reduction",
                reductions["right-rail"] >= 25.0,
                "Right ribbed shell materially reduces CAD volume",
                {"reduction_percent": reductions["right-rail"]},
            ),
            check(
                "support-free",
                rib_pitch - rail["rib_thickness"] <= 12.0,
                "Modeled roof bridges are bounded for support-free orientation",
            ),
        ],
        {
            "baseline_solid_volume_mm3": baseline_volumes,
            "selected_ribbed_volume_mm3": selected_volumes,
            "cad_volume_reduction_percent": reductions,
            "exact_slicer_material_and_time": "NOT_RUN",
        },
        ["CAD volume is not deposited mass or print time; exact slicer metrics remain deferred."],
    )
    write_json(REPORTS / "optimization-comparison.json", optimization_report)

    mesh_policy = {
        "project_id": PROJECT_ID,
        "revision": REVISION,
        "decision": "not-beneficial",
        "master_tessellation_mm": 0.025,
        "manufacturing_tessellation_mm": export["chordal_tolerance"],
        "downstream_decimation": False,
        "reason": "All analytic CAD meshes are modest and under budget; protected fit datums outweigh unmeasured decimation benefit.",
        "master_meshes": master_metrics,
        "manufacturing_meshes": manufacturing_metrics,
        "slicer_resolution_check": "NOT_RUN",
    }
    write_json(REPORTS / "mesh-complexity.json", mesh_policy)

    source_report = report(
        f"{PROJECT_ID}-parametric-source",
        [
            PARAMETERS,
            Path(__file__),
            ROOT / "design-spec.yaml",
            ROOT / "decomposition.md",
            ROOT / "protected-geometry-map.md",
        ],
        [
            check("parameters", True, "Default and boundary-oriented assertions pass"),
            check("part-count", len(shapes) == 3, "Two rails and one gauge are generated"),
            check("mesh-generation", mesh_report["status"] == "PASS", "Mesh generation checks pass"),
            check("interfaces", interface_report["status"] == "PASS", "Nominal interface checks pass"),
            check("optimization", optimization_report["status"] == "PASS", "Selected shell optimization passes"),
            check("3mf", print_set.is_file(), "Three-object DRAFT 3MF exists"),
        ],
        {
            "parts": list(shapes),
            "print_set": str(print_set.relative_to(ROOT)),
            "print_set_sha256": sha256_file(print_set),
        },
        ["Exact slicer preflight, physical fit, finish contact, cycles and watermark approval are deferred."],
    )
    write_json(VALIDATION / "parametric-source-report.json", source_report)

    build_manifest = {
        "project_id": PROJECT_ID,
        "revision": REVISION,
        "status": "DRAFT",
        "source": str(Path(__file__).relative_to(ROOT)),
        "parameters": input_record(PARAMETERS),
        "manufacturing_parts": manufacturing_metrics,
        "master_parts": master_metrics,
        "print_set": str(print_set.relative_to(ROOT)),
        "print_set_sha256": sha256_file(print_set),
        "physical_validation": "DEFERRED",
        "watermark": "NOT_INTEGRATED_RELEASE_BLOCKER",
    }
    write_json(REPORTS / "build-manifest.json", build_manifest)
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
                "parts": {name: metrics["extents_mm"] for name, metrics in manufacturing_metrics.items()},
                "print_set": str(print_set),
                "volume_reduction_percent": reductions,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
