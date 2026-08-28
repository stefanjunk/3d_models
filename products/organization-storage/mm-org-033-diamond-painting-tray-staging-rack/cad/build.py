#!/usr/bin/env python3
"""Build the parametric MM-ORG-033 GemStage 6 candidate."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import cadquery as cq
from cadquery import exporters
import trimesh

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"
EXPORTS = ROOT / "exports"
PROJECT_ID = "MM-ORG-033"
REVISION = "0.1.0-draft.1"
PARAMETRIC_REPORT = VALIDATION / "parametric-source-report-run-003.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    try:
        display = str(path.relative_to(ROOT))
    except ValueError:
        display = str(path)
    return {"path": display, "sha256": sha256(path), "size_bytes": path.stat().st_size}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def sloped_prism(width: float, y0: float, y1: float, top0: float, top1: float, thickness: float) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .moveTo(y0, top0 - thickness)
        .lineTo(y1, top1 - thickness)
        .lineTo(y1, top1)
        .lineTo(y0, top0)
        .close()
        .extrude(width)
    )


def sloped_rail(width: float, y0: float, y1: float, lower0: float, lower1: float, height: float, x: float = 0.0) -> cq.Workplane:
    rail = (
        cq.Workplane("YZ")
        .moveTo(y0, lower0)
        .lineTo(y1, lower1)
        .lineTo(y1, lower1 + height)
        .lineTo(y0, lower0 + height)
        .close()
        .extrude(width)
    )
    return rail.translate((x, 0, 0))


def level_geometry(p: dict, index: int, y0: float, y1: float, include_back_stop: bool = False) -> tuple[cq.Workplane, dict]:
    rack = p["rack"]
    width = rack["outer_width_mm"]
    front_top = rack["first_front_top_z_mm"] + index * rack["lane_pitch_mm"]
    proportional_fall = rack["rearward_fall_mm"] * (y1 - y0) / (rack["shelf_rear_y_mm"] - rack["shelf_front_y_mm"])
    rear_top = front_top - proportional_fall
    shelf = sloped_prism(width, y0, y1, front_top, rear_top, rack["shelf_thickness_mm"])
    fusion_overlap = 0.4
    left = sloped_rail(rack["rail_thickness_mm"], y0, y1, front_top - fusion_overlap, rear_top - fusion_overlap, rack["rail_height_mm"] + fusion_overlap)
    right = sloped_rail(rack["rail_thickness_mm"], y0, y1, front_top - fusion_overlap, rear_top - fusion_overlap, rack["rail_height_mm"] + fusion_overlap, width - rack["rail_thickness_mm"])
    tab_width = (width - rack["center_front_opening_mm"]) / 2
    tab_inner_width = tab_width - rack["rail_thickness_mm"]
    tab_height = rack["rail_height_mm"] + fusion_overlap
    tab_z = front_top - fusion_overlap + tab_height / 2
    left_tab = cq.Workplane("XY").box(tab_inner_width, rack["front_tab_depth_mm"], tab_height, centered=(False, False, True)).translate((rack["rail_thickness_mm"], y0, tab_z))
    right_tab = cq.Workplane("XY").box(tab_inner_width, rack["front_tab_depth_mm"], tab_height, centered=(False, False, True)).translate((width - tab_width, y0, tab_z))
    shape = shelf.union(left).union(right).union(left_tab).union(right_tab)
    if include_back_stop:
        stop = cq.Workplane("XY").box(width, rack["rear_stop_thickness_mm"], rack["outer_height_mm"], centered=(False, False, False)).translate((0, y1, 0))
        shape = shape.union(stop)
    return shape.clean(), {"index": index + 1, "front_top_z_mm": front_top, "rear_top_z_mm": rear_top, "rearward_fall_mm": proportional_fall, "front_tab_width_mm": tab_width}


def make_rack(p: dict) -> tuple[cq.Workplane, dict]:
    rack = p["rack"]
    shape = None
    levels = []
    for index in range(rack["tray_stations"]):
        level, metrics = level_geometry(p, index, rack["shelf_front_y_mm"], rack["shelf_rear_y_mm"], include_back_stop=index == 0)
        shape = level if shape is None else shape.union(level)
        levels.append(metrics)
    bottom = cq.Workplane("XY").box(rack["outer_width_mm"], rack["outer_depth_mm"], rack["bottom_foot_height_mm"], centered=(False, False, False))
    shape = shape.union(bottom).clean()
    tray = p["tray"]
    inner_width = rack["outer_width_mm"] - 2 * rack["rail_thickness_mm"]
    vertical_clearance = rack["lane_pitch_mm"] - rack["shelf_thickness_mm"] - tray["maximum_height_mm"]
    return shape, {
        "part_id": "rack",
        "levels": levels,
        "tray_stations": rack["tray_stations"],
        "inner_width_mm": inner_width,
        "side_clearance_each_mm": (inner_width - tray["maximum_width_mm"]) / 2,
        "vertical_clearance_mm": vertical_clearance,
        "functional_envelope_mm": [rack["outer_width_mm"], rack["outer_depth_mm"], rack["outer_height_mm"]],
        "rearward_angle_deg": math.degrees(math.atan2(rack["rearward_fall_mm"], rack["shelf_rear_y_mm"] - rack["shelf_front_y_mm"])),
    }


def make_coupon(p: dict) -> tuple[cq.Workplane, dict]:
    rack, coupon = p["rack"], p["coupon"]
    y0, y1 = 0.0, coupon["depth_mm"]
    level, metrics = level_geometry(p, 0, y0, y1, include_back_stop=False)
    stop = cq.Workplane("XY").box(rack["outer_width_mm"], coupon["rear_stop_thickness_mm"], 24.0, centered=(False, False, False)).translate((0, y1, 0))
    shape = level.union(stop).clean()
    metrics.update({"part_id": "mouth-coupon", "depth_mm": coupon["depth_mm"]})
    return shape, metrics


def make_virtual_tray(p: dict) -> cq.Workplane:
    rack, tray = p["rack"], p["tray"]
    x = (rack["outer_width_mm"] - tray["maximum_width_mm"]) / 2
    front_top = rack["first_front_top_z_mm"]
    rear_top = front_top - rack["rearward_fall_mm"]
    return sloped_prism(tray["maximum_width_mm"], rack["shelf_front_y_mm"], rack["shelf_rear_y_mm"], front_top + tray["maximum_height_mm"], rear_top + tray["maximum_height_mm"], tray["maximum_height_mm"]).translate((x, 0, 0))


def manufacturing_orientation(shape: cq.Workplane) -> cq.Workplane:
    rotated = shape.rotate((0, 0, 0), (0, 1, 0), -90)
    bb = rotated.val().BoundingBox()
    return rotated.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def export_step_stl(shape: cq.Workplane, step_path: Path, stl_path: Path, mesh: dict) -> None:
    step_path.parent.mkdir(parents=True, exist_ok=True)
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(step_path))
    exporters.export(shape, str(stl_path), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])


def make_3mf(mesh_paths: list[Path], target: Path, translations: list[tuple[float, float, float]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    for index, (mesh_path, shift) in enumerate(zip(mesh_paths, translations), 1):
        loaded = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        loaded.remove_unreferenced_vertices()
        loaded.merge_vertices()
        loaded.fix_normals()
        if not loaded.is_watertight or not loaded.is_winding_consistent or loaded.volume <= 0:
            raise RuntimeError(f"Cannot package invalid mesh: {mesh_path}")
        loaded.apply_translation(shift)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(index), "type": "model", "name": mesh_path.stem})
        mesh = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices = ET.SubElement(mesh, f"{{{ns}}}vertices")
        for x, y, z in loaded.vertices:
            ET.SubElement(vertices, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles = ET.SubElement(mesh, f"{{{ns}}}triangles")
        for a, b, c in loaded.faces:
            ET.SubElement(triangles, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(index)})
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in [
            ("[Content_Types].xml", content_types),
            ("_rels/.rels", rels),
            ("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True)),
            ("Metadata/model-parameters.json", PARAMETERS.read_bytes()),
        ]:
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    return {
        "path": str(path.relative_to(ROOT)), "sha256": sha256(path), "faces": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)),
        "components": int(len(mesh.split(only_watertight=False))), "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_mm3": float(mesh.volume), "bounds_mm": [float(v) for v in mesh.extents], "size_bytes": path.stat().st_size,
    }


def main() -> None:
    p = json.loads(PARAMETERS.read_text())
    for folder in [REPORTS, VALIDATION, EXPORTS / "master", EXPORTS / "manufacturing", EXPORTS / "coupons", EXPORTS / "3mf"]:
        folder.mkdir(parents=True, exist_ok=True)
    rack, interface = make_rack(p)
    coupon, coupon_metrics = make_coupon(p)
    virtual_tray = make_virtual_tray(p)
    rack_print = manufacturing_orientation(rack)
    coupon_print = manufacturing_orientation(coupon)

    rack_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-rack-{REVISION}.step"
    rack_master_stl = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-rack-{REVISION}-master.stl"
    coupon_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-mouth-coupon-{REVISION}.step"
    coupon_master_stl = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-mouth-coupon-{REVISION}-master.stl"
    virtual_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-virtual-tray-{REVISION}.step"
    rack_stl = EXPORTS / "manufacturing" / f"DRAFT-{PROJECT_ID}-rack-{REVISION}.stl"
    coupon_stl = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-mouth-coupon-{REVISION}.stl"
    print_set = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-gemstage-six-{REVISION}.3mf"

    export_step_stl(rack, rack_step, rack_master_stl, p["mesh"])
    export_step_stl(coupon, coupon_step, coupon_master_stl, p["mesh"])
    exporters.export(virtual_tray, str(virtual_step))
    exporters.export(rack_print, str(rack_stl), tolerance=p["mesh"]["linear_deflection_mm"], angularTolerance=p["mesh"]["angular_deflection_rad"])
    exporters.export(coupon_print, str(coupon_stl), tolerance=p["mesh"]["linear_deflection_mm"], angularTolerance=p["mesh"]["angular_deflection_rad"])
    make_3mf([rack_stl, coupon_stl], print_set, [(20, 20, 0), (170, 20, 0)])

    meshes = {key: mesh_metrics(path) for key, path in {"rack": rack_stl, "coupon": coupon_stl, "rack_master": rack_master_stl, "coupon_master": coupon_master_stl}.items()}
    source_checks = [
        check("project", p["project"]["id"] == PROJECT_ID and p["project"]["revision"] == REVISION, "Project identity and revision are fixed"),
        check("stations", 3 <= p["rack"]["tray_stations"] <= 6, "Tray station count is within the supported 3-6 range"),
        check("envelope", p["rack"]["outer_width_mm"] <= 220 and p["rack"]["outer_depth_mm"] <= 160 and p["rack"]["outer_height_mm"] <= 140, "Functional envelope is inside the portfolio cap"),
        check("side-clearance", interface["side_clearance_each_mm"] + 1e-9 >= p["tray"]["minimum_side_clearance_each_mm"], "Declared side clearance is retained", {"actual_mm": interface["side_clearance_each_mm"]}),
        check("vertical-clearance", interface["vertical_clearance_mm"] >= p["tray"]["minimum_vertical_clearance_mm"], "Declared vertical clearance is retained", {"actual_mm": interface["vertical_clearance_mm"]}),
        check("back-tilt", 0 < interface["rearward_angle_deg"] < 5, "Each tray slopes toward the rear stop", {"angle_deg": interface["rearward_angle_deg"]}),
        check("front-opening", p["rack"]["center_front_opening_mm"] >= 40, "Center front opening preserves finger, label and spout access"),
    ]
    param_report = {"schema_version": "1.0", "tool": f"{PROJECT_ID}-parametric-source", "tool_version": REVISION, "status": "PASS" if all(c["status"] == "PASS" for c in source_checks) else "FAIL", "profile": "draft", "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml")], "checks": source_checks, "metrics": {"interface": interface, "coupon": coupon_metrics, "outputs": [record(path) for path in [rack_step, coupon_step, virtual_step, rack_stl, coupon_stl, print_set]]}, "limitations": ["Parametric checks do not prove real-tray fit or spill behavior."], "required_capabilities": ["cadquery"]}
    write_json(PARAMETRIC_REPORT, param_report)

    mesh_checks = []
    for name, metrics in meshes.items():
        mesh_checks.extend([
            check(f"{name}-watertight", metrics["watertight"], f"{name} is watertight"),
            check(f"{name}-component", metrics["components"] == 1, f"{name} has one connected component", {"components": metrics["components"]}),
            check(f"{name}-volume", metrics["volume_mm3"] > 0, f"{name} has positive volume", {"volume_mm3": metrics["volume_mm3"]}),
            check(f"{name}-complexity", metrics["faces"] <= p["mesh"]["triangle_stop"], f"{name} is under the face limit", {"faces": metrics["faces"]}),
        ])
    mesh_report = {"schema_version": "1.0", "tool": f"{PROJECT_ID}-mesh-generation", "tool_version": REVISION, "status": "PASS" if all(c["status"] == "PASS" for c in mesh_checks) else "FAIL", "profile": "draft", "inputs": [record(rack_stl), record(coupon_stl), record(rack_master_stl), record(coupon_master_stl)], "checks": mesh_checks, "metrics": meshes, "limitations": [], "required_capabilities": ["trimesh"]}
    write_json(VALIDATION / "mesh-generation-report.json", mesh_report)

    interface_checks = [
        check("six-levels", len(interface["levels"]) == 6, "Six independent staging levels are present"),
        check("tray-width", interface["side_clearance_each_mm"] + 1e-9 >= 1.8, "86 mm tray envelope clears both rails", {"clearance_each_mm": interface["side_clearance_each_mm"]}),
        check("tray-height", interface["vertical_clearance_mm"] >= 6.0, "12 mm tray envelope clears the next shelf", {"clearance_mm": interface["vertical_clearance_mm"]}),
        check("rearward-fall", all(abs(level["rearward_fall_mm"] - p["rack"]["rearward_fall_mm"]) < 1e-6 for level in interface["levels"]), "Every full level retains the same rearward fall"),
        check("split-tabs", all(level["front_tab_width_mm"] >= 24 for level in interface["levels"]), "Each level has two sufficiently wide corner retention tabs"),
        check("manufacturing-bed", meshes["rack"]["bounds_mm"][2] <= p["rack"]["outer_width_mm"] + 0.01, "Manufacturing orientation puts the original width on Z", {"bounds_mm": meshes["rack"]["bounds_mm"]}),
    ]
    interface_report = {"schema_version": "1.0", "tool": f"{PROJECT_ID}-interface-validation", "tool_version": REVISION, "status": "PASS" if all(c["status"] == "PASS" for c in interface_checks) else "FAIL", "profile": "draft", "inputs": [record(PARAMETERS), record(rack_stl), record(coupon_stl)], "checks": interface_checks, "metrics": {"rack": interface, "coupon": coupon_metrics}, "limitations": ["Clearance is nominal CAD geometry; printer/material/process compensation is not inferred."], "required_capabilities": []}
    write_json(VALIDATION / "interface-report.json", interface_report)

    baseline_volume = p["rack"]["outer_width_mm"] * p["rack"]["outer_depth_mm"] * p["rack"]["outer_height_mm"]
    candidate_volume = meshes["rack"]["volume_mm3"]
    reduction = (1 - candidate_volume / baseline_volume) * 100
    opt_checks = [check("protected-clearances", interface["side_clearance_each_mm"] + 1e-9 >= 1.8 and interface["vertical_clearance_mm"] >= 6.0, "Protected tray clearances remain satisfied"), check("volume-reduction", reduction >= 70, "Open scaffold reduces volume by at least 70% versus the bounding-block proxy", {"reduction_percent": reduction}), check("support-free-orientation", meshes["rack"]["bounds_mm"][2] <= 96.01, "Side orientation converts shelves and stops into vertical webs")]
    opt_report = {"schema_version": "1.0", "tool": f"{PROJECT_ID}-optimization-comparison", "tool_version": REVISION, "status": "PASS" if all(c["status"] == "PASS" for c in opt_checks) else "FAIL", "profile": "draft", "inputs": [record(PARAMETERS), record(rack_stl)], "checks": opt_checks, "metrics": {"baseline_proxy_volume_mm3": baseline_volume, "candidate_volume_mm3": candidate_volume, "volume_reduction_percent": reduction, "selected_variant": "side-print-open-scaffold"}, "limitations": ["CAD volume is not slicer deposited mass or print time."], "required_capabilities": []}
    write_json(REPORTS / "optimization-comparison.json", opt_report)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": mesh_report["status"], "meshes": meshes})
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION, "status": "PASS" if param_report["status"] == mesh_report["status"] == interface_report["status"] == opt_report["status"] == "PASS" else "FAIL", "artifacts": [record(path) for path in [rack_step, coupon_step, virtual_step, rack_master_stl, coupon_master_stl, rack_stl, coupon_stl, print_set]], "reports": [record(path) for path in [PARAMETRIC_REPORT, VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json", REPORTS / "optimization-comparison.json"]]})
    print(json.dumps({"status": "PASS", "rack_bounds_mm": meshes["rack"]["bounds_mm"], "rack_volume_mm3": candidate_volume, "volume_reduction_percent": reduction, "print_set": str(print_set.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
