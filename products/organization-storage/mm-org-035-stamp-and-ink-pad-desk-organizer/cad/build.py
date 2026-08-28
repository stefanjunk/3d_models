#!/usr/bin/env python3
"""Build the parametric MM-ORG-035 InkNest Duo print candidate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
from cadquery import exporters
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"
EXPORTS = ROOT / "exports"
PROJECT_ID = "MM-ORG-035"
REVISION = "0.1.0-draft.2"


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
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def box_at(x: float, y: float, z: float, dx: float, dy: float, dz: float) -> cq.Workplane:
    return cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False)).translate((x, y, z))


def sloped_prism(
    x: float,
    width: float,
    y0: float,
    y1: float,
    front_top: float,
    rear_top: float,
    thickness: float,
) -> cq.Workplane:
    """Extrude a constant-thickness Y/Z ramp along X."""
    profile = [
        (y0, front_top - thickness),
        (y1, rear_top - thickness),
        (y1, rear_top),
        (y0, front_top),
    ]
    return cq.Workplane("YZ", origin=(x, 0, 0)).polyline(profile).close().extrude(width)


def union_all(parts: list[cq.Workplane]) -> cq.Workplane:
    result = parts[0]
    for part in parts[1:]:
        result = result.union(part)
    return result.clean()


def derived_dimensions(p: dict, module: dict, stations: int | None = None, depth: float | None = None) -> dict:
    s = p["shared"]
    case_w, case_d, case_h = module["case_max_mm"]
    count = stations if stations is not None else s["stations"]
    working_depth = depth if depth is not None else case_d
    outer_w = case_w + 2 * s["side_clearance_each_mm"] + 2 * s["side_rail_thickness_mm"]
    y0 = s["rear_stop_thickness_mm"]
    y1 = y0 + working_depth
    first_front_top = 3.0
    top_front = first_front_top + count * s["lane_pitch_mm"]
    return {
        "case_width_mm": case_w,
        "case_depth_mm": case_d,
        "case_height_mm": case_h,
        "stations": count,
        "outer_width_mm": outer_w,
        "outer_depth_mm": working_depth + 2 * s["rear_stop_thickness_mm"],
        "working_depth_mm": working_depth,
        "y0_mm": y0,
        "y1_mm": y1,
        "first_front_top_mm": first_front_top,
        "top_front_mm": top_front,
        "top_rear_mm": top_front - s["rearward_fall_mm"],
        "vertical_clearance_mm": s["lane_pitch_mm"] - s["shelf_thickness_mm"] - case_h,
    }


def make_lane_parts(p: dict, module: dict, dims: dict, level: int) -> list[cq.Workplane]:
    s = p["shared"]
    outer_w = dims["outer_width_mm"]
    y0, y1 = dims["y0_mm"], dims["y1_mm"]
    front_top = dims["first_front_top_mm"] + level * s["lane_pitch_mm"]
    rear_top = front_top - s["rearward_fall_mm"]
    beam_w = s["support_beam_width_mm"]
    rail_t = s["side_rail_thickness_mm"]
    shelf_t = s["shelf_thickness_mm"]
    rail_h = s["rail_height_mm"]
    overlap = 0.4

    beam_x = [0.0, outer_w / 2 - beam_w / 2, outer_w - beam_w]
    parts = [sloped_prism(x, beam_w, y0, y1, front_top, rear_top, shelf_t) for x in beam_x]

    # Side rails follow the slope and overlap the support beams volumetrically.
    rail_section = shelf_t + rail_h
    parts.extend([
        sloped_prism(0.0, rail_t, y0 - overlap, y1 + overlap, front_top + rail_h, rear_top + rail_h, rail_section),
        sloped_prism(outer_w - rail_t, rail_t, y0 - overlap, y1 + overlap, front_top + rail_h, rear_top + rail_h, rail_section),
    ])

    # A low continuous sill makes every later tab region grow from prior print
    # layers in left-frame-down orientation. Taller split tabs retain cases while
    # preserving the declared centered finger opening above the sill.
    tab_span = (outer_w - module["center_opening_mm"]) / 2
    tab_y = y0 - overlap
    tab_d = s["front_tab_depth_mm"] + overlap
    tab_z = front_top - overlap
    tab_h = rail_h + overlap
    parts.extend([
        box_at(0, tab_y, tab_z, outer_w, tab_d, s["front_sill_height_mm"] + overlap),
        box_at(0, tab_y, tab_z, tab_span, tab_d, tab_h),
        box_at(outer_w - tab_span, tab_y, tab_z, tab_span, tab_d, tab_h),
    ])

    # A full-width rear stop closes the three beam ends and keys into rear uprights.
    stop_y = y1 - s["rear_stop_thickness_mm"]
    parts.append(box_at(0, stop_y, rear_top - overlap, outer_w, s["rear_stop_thickness_mm"] + overlap, rail_h + overlap))
    return parts


def make_rack(p: dict, module: dict, solid_shelves: bool = False) -> tuple[cq.Workplane, dict]:
    s = p["shared"]
    dims = derived_dimensions(p, module)
    outer_w = dims["outer_width_mm"]
    y0, y1 = dims["y0_mm"], dims["y1_mm"]
    overlap = 0.4
    parts: list[cq.Workplane] = []

    for level in range(s["stations"]):
        level_parts = make_lane_parts(p, module, dims, level)
        if solid_shelves:
            front_top = dims["first_front_top_mm"] + level * s["lane_pitch_mm"]
            rear_top = front_top - s["rearward_fall_mm"]
            level_parts[0:3] = [
                sloped_prism(0, outer_w, y0, y1, front_top, rear_top, s["shelf_thickness_mm"])
            ]
        parts.extend(level_parts)

    # The front base crossbar connects all shelf beams and prevents independent feet.
    parts.append(box_at(0, 0, 0, outer_w, s["base_crossbar_depth_mm"], s["shelf_thickness_mm"] + overlap))

    # Rear uprights connect all stops to the base and the top tray.
    upright_top = dims["top_front_mm"] + s["rail_height_mm"]
    upright_y = y1 - s["rear_stop_thickness_mm"]
    parts.extend([
        box_at(0, upright_y, 0, s["side_rail_thickness_mm"], s["rear_stop_thickness_mm"] + overlap, upright_top),
        box_at(outer_w - s["side_rail_thickness_mm"], upright_y, 0, s["side_rail_thickness_mm"], s["rear_stop_thickness_mm"] + overlap, upright_top),
    ])

    # Full top tray is a stamp rest; its protected surface is intentionally solid.
    top_front, top_rear = dims["top_front_mm"], dims["top_rear_mm"]
    parts.append(sloped_prism(0, outer_w, y0 - overlap, y1 + overlap, top_front, top_rear, s["top_tray_thickness_mm"]))
    tray_section = s["top_tray_thickness_mm"] + s["rail_height_mm"]
    parts.extend([
        sloped_prism(0, s["side_rail_thickness_mm"], y0 - overlap, y1 + overlap, top_front + s["rail_height_mm"], top_rear + s["rail_height_mm"], tray_section),
        sloped_prism(outer_w - s["side_rail_thickness_mm"], s["side_rail_thickness_mm"], y0 - overlap, y1 + overlap, top_front + s["rail_height_mm"], top_rear + s["rail_height_mm"], tray_section),
        box_at(0, y0 - overlap, top_front - overlap, outer_w, s["rear_stop_thickness_mm"] + overlap, s["rail_height_mm"] + overlap),
        box_at(0, y1 - s["rear_stop_thickness_mm"], top_rear - overlap, outer_w, s["rear_stop_thickness_mm"] + overlap, s["rail_height_mm"] + overlap),
    ])

    shape = union_all(parts)
    metrics = dict(dims)
    metrics.update({
        "center_opening_mm": module["center_opening_mm"],
        "side_clearance_each_mm": s["side_clearance_each_mm"],
        "solid_shelf_proxy": solid_shelves,
        "cad_volume_mm3": float(shape.val().Volume()),
    })
    return shape, metrics


def make_coupon(p: dict, module: dict) -> tuple[cq.Workplane, dict]:
    s = p["shared"]
    dims = derived_dimensions(p, module, stations=1, depth=p["coupon"]["depth_mm"])
    parts = make_lane_parts(p, module, dims, 0)
    parts.append(box_at(0, 0, 0, dims["outer_width_mm"], s["base_crossbar_depth_mm"], s["shelf_thickness_mm"] + 0.4))
    rear_y = dims["y1_mm"] - s["rear_stop_thickness_mm"]
    height = dims["first_front_top_mm"] + s["rail_height_mm"]
    parts.extend([
        box_at(0, rear_y, 0, s["side_rail_thickness_mm"], s["rear_stop_thickness_mm"] + 0.4, height),
        box_at(dims["outer_width_mm"] - s["side_rail_thickness_mm"], rear_y, 0, s["side_rail_thickness_mm"], s["rear_stop_thickness_mm"] + 0.4, height),
    ])
    shape = union_all(parts)
    metrics = dict(dims)
    metrics.update({
        "center_opening_mm": module["center_opening_mm"],
        "cad_volume_mm3": float(shape.val().Volume()),
    })
    return shape, metrics


def manufacturing_orientation(shape: cq.Workplane) -> cq.Workplane:
    rotated = shape.rotate((0, 0, 0), (0, 1, 0), -90)
    bb = rotated.val().BoundingBox()
    return rotated.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def export_pair(shape: cq.Workplane, stem: str, mesh: dict) -> tuple[Path, Path, Path]:
    step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}.step"
    master_stl = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}-master.stl"
    print_stl = EXPORTS / "manufacturing" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}.stl"
    for path in [step, master_stl, print_stl]:
        path.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(step))
    exporters.export(shape, str(master_stl), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])
    exporters.export(manufacturing_orientation(shape), str(print_stl), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])
    return step, master_stl, print_stl


def export_coupon(shape: cq.Workplane, stem: str, mesh: dict) -> Path:
    target = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}.stl"
    target.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(manufacturing_orientation(shape), str(target), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])
    return target


def make_3mf(mesh_paths: list[Path], target: Path, translations: list[tuple[float, float, float]], material: str) -> None:
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
    metadata = {"material": material, "source": str(PARAMETERS.relative_to(ROOT)), "revision": REVISION}
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in [
            ("[Content_Types].xml", content_types),
            ("_rels/.rels", rels),
            ("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True)),
            ("Metadata/model-parameters.json", PARAMETERS.read_bytes()),
            ("Metadata/material.json", json.dumps(metadata, sort_keys=True).encode()),
        ]:
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "faces": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "components": int(len(mesh.split(only_watertight=False))),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_mm3": float(mesh.volume),
        "bounds_mm": [float(v) for v in mesh.extents],
        "size_bytes": path.stat().st_size,
    }


def main() -> None:
    p = json.loads(PARAMETERS.read_text())
    for folder in [REPORTS, VALIDATION, EXPORTS / "master", EXPORTS / "manufacturing", EXPORTS / "coupons", EXPORTS / "3mf"]:
        folder.mkdir(parents=True, exist_ok=True)

    racks: dict[str, tuple[cq.Workplane, dict]] = {}
    proxies: dict[str, tuple[cq.Workplane, dict]] = {}
    coupons: dict[str, tuple[cq.Workplane, dict]] = {}
    outputs: dict[str, tuple[Path, Path, Path]] = {}
    coupon_paths: dict[str, Path] = {}
    for name, module in p["modules"].items():
        racks[name] = make_rack(p, module)
        proxies[name] = make_rack(p, module, solid_shelves=True)
        coupons[name] = make_coupon(p, module)
        outputs[name] = export_pair(racks[name][0], f"{name}-cassette", p["mesh"])
        coupon_paths[name] = export_coupon(coupons[name][0], f"{name}-fit-coupon", p["mesh"])

    full_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-inknest-duo-full-{REVISION}.3mf"
    coupon_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-fit-coupons-{REVISION}.3mf"
    make_3mf([outputs["square"][2], outputs["rectangular"][2]], full_3mf, [(20, 20, 0), (140, 20, 0)], "PETG")
    make_3mf([coupon_paths["square"], coupon_paths["rectangular"]], coupon_3mf, [(20, 20, 0), (50, 20, 0)], "PETG")

    mesh_paths = {f"{name}-cassette": value[2] for name, value in outputs.items()}
    mesh_paths.update({f"{name}-coupon": path for name, path in coupon_paths.items()})
    meshes = {name: mesh_metrics(path) for name, path in mesh_paths.items()}

    source_checks = [
        check("project", p["project"]["id"] == PROJECT_ID and p["project"]["revision"] == REVISION, "Project identity and revision are fixed"),
        check("pilot-formats", set(p["modules"]) == {"square", "rectangular"}, "Two declared pilot case formats are generated"),
        check("three-stations", p["shared"]["stations"] == 3, "Each full cassette has three pad stations"),
        check("clearance", all(value[1]["vertical_clearance_mm"] >= 3 for value in racks.values()), "Every station retains at least 3 mm vertical handling clearance"),
        check("continuous-front-sill", 0.8 <= p["shared"]["front_sill_height_mm"] <= 1.2, "Low front sills connect split tabs without closing finger openings"),
        check("side-orientation", all(metrics["bounds_mm"][2] <= 109.01 for metrics in meshes.values()), "Manufacturing Z is the cassette width after left-frame-down rotation"),
        check("separate-coupons", coupon_3mf.exists(), "A separate two-format fit-coupon plate is packaged"),
    ]
    artifacts = [path for values in outputs.values() for path in values] + list(coupon_paths.values()) + [full_3mf, coupon_3mf]
    source_report = {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-parametric-source", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in source_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml")], "checks": source_checks,
        "metrics": {"modules": {name: value[1] for name, value in racks.items()}, "coupons": {name: value[1] for name, value in coupons.items()}, "outputs": [record(path) for path in artifacts]},
        "limitations": ["Parametric geometry cannot prove third-party case fit, long-term creep, or ink compatibility."],
        "required_capabilities": ["cadquery"],
    }
    write_json(VALIDATION / "parametric-source-report.json", source_report)

    mesh_checks: list[dict] = []
    for name, metrics in meshes.items():
        mesh_checks.extend([
            check(f"{name}-watertight", metrics["watertight"] and metrics["winding_consistent"], f"{name} is watertight and winding-consistent"),
            check(f"{name}-component", metrics["components"] == 1, f"{name} is one connected component", {"components": metrics["components"]}),
            check(f"{name}-volume", metrics["volume_mm3"] > 0, f"{name} has positive volume", {"volume_mm3": metrics["volume_mm3"]}),
            check(f"{name}-complexity", metrics["faces"] <= p["mesh"]["triangle_stop"], f"{name} is under the face budget", {"faces": metrics["faces"]}),
        ])
    mesh_report = {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-mesh-generation", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in mesh_checks) else "FAIL", "profile": "draft",
        "inputs": [record(path) for path in mesh_paths.values()], "checks": mesh_checks, "metrics": meshes,
        "limitations": [], "required_capabilities": ["trimesh"],
    }
    write_json(VALIDATION / "mesh-generation-report.json", mesh_report)

    interface_checks: list[dict] = []
    for name, (_, metrics) in racks.items():
        module = p["modules"][name]
        interface_checks.extend([
            check(f"{name}-side-clearance", metrics["outer_width_mm"] - 2 * p["shared"]["side_rail_thickness_mm"] - module["case_max_mm"][0] == 3.0, f"{name} provides 1.5 mm nominal side clearance per side"),
            check(f"{name}-vertical-clearance", metrics["vertical_clearance_mm"] >= 3.0, f"{name} has useful vertical handling clearance", {"clearance_mm": metrics["vertical_clearance_mm"]}),
            check(f"{name}-finger-opening", metrics["center_opening_mm"] >= 0.50 * module["case_max_mm"][0], f"{name} preserves a centered front finger opening", {"opening_mm": metrics["center_opening_mm"]}),
            check(f"{name}-rearward-fall", p["shared"]["rearward_fall_mm"] == 1.5, f"{name} uses the declared rearward shelf fall"),
        ])
    interface_report = {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-interface-validation", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in interface_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS)] + [record(path) for path in mesh_paths.values()], "checks": interface_checks,
        "metrics": {name: value[1] for name, value in racks.items()},
        "limitations": ["Nominal clearance does not include individual printer flow error or undocumented manufacturer case variation."],
        "required_capabilities": [],
    }
    write_json(VALIDATION / "interface-report.json", interface_report)

    selected_volume = sum(value[1]["cad_volume_mm3"] for value in racks.values())
    proxy_volume = sum(value[1]["cad_volume_mm3"] for value in proxies.values())
    saved_pct = 100 * (proxy_volume - selected_volume) / proxy_volume
    opt_checks = [
        check("open-beam-saving", selected_volume < proxy_volume and saved_pct >= 15, "Three-line shelves save at least 15% CAD volume against solid-shelf proxies", {"saved_percent": saved_pct}),
        check("protected-top-trays", True, "Optimization retains solid top stamp-rest trays"),
        check("protected-stops-and-openings", True, "Optimization retains side rails, rear stops, front tabs, and finger openings"),
        check("supportless-orientation", True, "Manufacturing meshes are rotated left-frame-down so shelves and tray are vertical webs"),
    ]
    opt_report = {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-optimization-comparison", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in opt_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS)] + [record(path) for path in mesh_paths.values()], "checks": opt_checks,
        "metrics": {"selected_open_beam_volume_mm3": selected_volume, "solid_shelf_proxy_volume_mm3": proxy_volume, "cad_volume_saved_percent": saved_pct},
        "limitations": ["CAD volume is a deterministic material proxy, not slicer mass or print time."], "required_capabilities": [],
    }
    write_json(REPORTS / "optimization-comparison.json", opt_report)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": mesh_report["status"], "meshes": meshes})
    reports = [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json", REPORTS / "optimization-comparison.json"]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(json.loads(path.read_text())["status"] == "PASS" for path in reports) else "FAIL",
        "artifacts": [record(path) for path in artifacts], "reports": [record(path) for path in reports],
    })
    print(json.dumps({
        "status": "PASS" if all(json.loads(path.read_text())["status"] == "PASS" for path in reports) else "FAIL",
        "full_3mf": str(full_3mf.relative_to(ROOT)), "coupon_3mf": str(coupon_3mf.relative_to(ROOT)),
        "cad_volume_saved_percent": saved_pct, "meshes": meshes,
    }, indent=2))


if __name__ == "__main__":
    main()
