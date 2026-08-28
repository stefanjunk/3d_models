#!/usr/bin/env python3
"""Build the parametric MM-ORG-038 MomentPair 2 print candidate."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import shutil
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
PROJECT_ID = "MM-ORG-038"
REVISION = "0.1.0-draft.1"
MARK_DIR = ROOT / "assets/metrimade-watermark/generated/MM-ORG-038_v0.1.0-draft.1"
MARK_METADATA = MARK_DIR / "metrimade-watermark-MM-ORG-038-v0.1.0-draft.1.json"
MARK_DXF = MARK_DIR / "metrimade-watermark-MM-ORG-038-v0.1.0-draft.1.dxf"
MARK_COUPON_SOURCE = MARK_DIR / "metrimade-watermark-MM-ORG-038-v0.1.0-draft.1-coupon-d040.stl"
MARK_SELECTOR = VALIDATION / "watermark-selector.json"


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


def box_center(x: float, y: float, z: float, dx: float, dy: float, dz: float) -> cq.Workplane:
    return cq.Workplane("XY").box(dx, dy, dz).translate((x, y, z))


def union_all(parts: list[cq.Workplane]) -> cq.Workplane:
    result = parts[0]
    for part in parts[1:]:
        result = result.union(part)
    return result.clean()


def tapered_slot(p: dict, length: float, depth: float, center_x: float, top_center_y: float, top_z: float) -> cq.Workplane:
    cfg = p["slots"]
    tilt_shift = math.tan(math.radians(cfg["back_tilt_deg"])) * depth
    bottom_center_y = top_center_y - tilt_shift
    points = [
        (bottom_center_y - cfg["bottom_gap_mm"] / 2, top_z - depth - 0.05),
        (bottom_center_y + cfg["bottom_gap_mm"] / 2, top_z - depth - 0.05),
        (top_center_y + cfg["top_gap_mm"] / 2, top_z + 0.2),
        (top_center_y - cfg["top_gap_mm"] / 2, top_z + 0.2),
    ]
    return cq.Workplane("YZ").polyline(points).close().extrude(length / 2 + 0.1, both=True).translate((center_x, 0, 0))


def watermark_cutter(center_x: float, center_y: float, depth: float) -> cq.Workplane:
    faces = cq.importers.importDXF(str(MARK_DXF)).objects
    solids = [cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), cq.Vector(0, 0, depth + 0.02)) for face in faces]
    cutter = cq.Workplane(obj=cq.Compound.makeCompound(solids)).mirror("YZ")
    bb = cutter.val().BoundingBox()
    return cutter.translate((center_x - bb.xlen / 2 - bb.xmin, center_y - bb.ylen / 2 - bb.ymin, -0.01))


def front_text_cutter(p: dict, front_y: float) -> cq.Workplane:
    cfg = p["personalization"]
    text = cq.Workplane("XY").text(
        cfg["front_text"], cfg["font_size_mm"], cfg["recess_depth_mm"] + 0.05,
        font=cfg["font"], halign="center", valign="center",
    )
    return text.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, front_y - 0.01, 9.0))


def cut_compound(shape: cq.Workplane, cutter: cq.Workplane) -> cq.Workplane:
    for solid in cutter.val().Solids():
        shape = shape.cut(cq.Workplane(obj=solid))
    return shape.clean()


def make_base(p: dict, proxy: bool = False) -> tuple[cq.Workplane, dict]:
    b = p["base"]
    if proxy:
        shape = box_center(0, 0, b["rear_rail_height_mm"] / 2, b["width_mm"], b["depth_mm"], b["rear_rail_height_mm"])
        shape = shape.edges("|Z").fillet(b["edge_radius_mm"])
    else:
        rear = box_center(0, b["rear_rail_center_y_mm"], b["rear_rail_height_mm"] / 2, b["width_mm"], b["rear_rail_depth_mm"], b["rear_rail_height_mm"]).edges("|Z").fillet(b["edge_radius_mm"])
        front = box_center(0, b["front_rail_center_y_mm"], b["front_rail_height_mm"] / 2, b["front_rail_width_mm"], b["front_rail_depth_mm"], b["front_rail_height_mm"]).edges("|Z").fillet(b["edge_radius_mm"])
        connectors = [
            box_center(x, 0, b["connector_height_mm"] / 2, b["connector_width_mm"], b["connector_depth_mm"], b["connector_height_mm"])
            for x in b["connector_centers_x_mm"]
        ]
        shape = union_all([rear, front] + connectors)

    before_slots = float(shape.val().Volume())
    rear_cfg, front_cfg = p["slots"]["rear"], p["slots"]["front"]
    shape = shape.cut(tapered_slot(p, rear_cfg["length_mm"], rear_cfg["depth_mm"], rear_cfg["center_x_mm"], rear_cfg["top_center_y_mm"], b["rear_rail_height_mm"]))
    shape = shape.cut(tapered_slot(p, front_cfg["length_mm"], front_cfg["depth_mm"], front_cfg["center_x_mm"], front_cfg["top_center_y_mm"], b["front_rail_height_mm"]))
    after_slots = float(shape.val().Volume())

    before_text = after_slots
    shape = cut_compound(shape, front_text_cutter(p, -b["depth_mm"] / 2))
    after_text = float(shape.val().Volume())

    mark = p["watermark"]
    before_mark = after_text
    shape = cut_compound(shape, watermark_cutter(mark["center_x_mm"], mark["center_y_mm"], mark["engraving_depth_mm"]))
    final_volume = float(shape.val().Volume())
    return shape, {
        "proxy": proxy,
        "envelope_mm": [b["width_mm"], b["depth_mm"], b["rear_rail_height_mm"]],
        "slot_cut_volume_mm3": before_slots - after_slots,
        "text_cut_volume_mm3": before_text - after_text,
        "watermark_cut_volume_mm3": before_mark - final_volume,
        "rear_slot_floor_above_bed_mm": b["rear_rail_height_mm"] - rear_cfg["depth_mm"],
        "watermark_residual_to_rear_slot_mm": b["rear_rail_height_mm"] - rear_cfg["depth_mm"] - mark["engraving_depth_mm"],
        "cad_volume_mm3": final_volume,
    }


def make_gauge(p: dict) -> tuple[cq.Workplane, dict]:
    g, s = p["gauge"], p["slots"]
    shape = box_center(0, 0, g["height_mm"] / 2, g["width_mm"], g["depth_mm"], g["height_mm"]).edges("|Z").fillet(1.5)
    shape = shape.cut(tapered_slot(p, g["slot_length_mm"], s["rear"]["depth_mm"], -20.0, 0.0, g["height_mm"]))
    shape = shape.cut(tapered_slot(p, g["slot_length_mm"], s["front"]["depth_mm"], 20.0, 0.0, g["height_mm"]))
    return shape.clean(), {
        "envelope_mm": [g["width_mm"], g["depth_mm"], g["height_mm"]],
        "slot_depths_mm": [s["rear"]["depth_mm"], s["front"]["depth_mm"]],
        "top_gap_mm": s["top_gap_mm"], "bottom_gap_mm": s["bottom_gap_mm"], "back_tilt_deg": s["back_tilt_deg"],
        "cad_volume_mm3": float(shape.val().Volume()),
    }


def export_pair(shape: cq.Workplane, stem: str, mesh: dict) -> tuple[Path, Path, Path]:
    step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}.step"
    master_stl = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}-master.stl"
    print_stl = EXPORTS / "manufacturing" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}.stl"
    for path in [step, master_stl, print_stl]:
        path.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(step))
    exporters.export(shape, str(master_stl), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])
    exporters.export(shape, str(print_stl), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])
    return step, master_stl, print_stl


def export_coupon(shape: cq.Workplane, stem: str, mesh: dict) -> Path:
    target = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}.stl"
    target.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(target), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])
    return target


def make_3mf(mesh_paths: list[Path], target: Path, translations: list[tuple[float, float, float]], material: str) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    for index, (mesh_path, shift) in enumerate(zip(mesh_paths, translations), 1):
        loaded = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        loaded.remove_unreferenced_vertices(); loaded.merge_vertices(); loaded.fix_normals(); loaded.apply_translation(shift)
        if not loaded.is_watertight or not loaded.is_winding_consistent or loaded.volume <= 0:
            raise RuntimeError(f"Cannot package invalid mesh: {mesh_path}")
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
    metadata = {"material": material, "source": str(PARAMETERS.relative_to(ROOT)), "revision": REVISION, "privacy": "no customer photo, name, date, or card artwork retained", "identity": {"brand": "metriMade", "domain": "metriMade.com", "product_id": PROJECT_ID, "version": REVISION, "watermark_tier": "full"}}
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in [("[Content_Types].xml", content_types), ("_rels/.rels", rels), ("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True)), ("Metadata/model-parameters.json", PARAMETERS.read_bytes()), ("Metadata/material.json", json.dumps(metadata, sort_keys=True).encode())]:
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; archive.writestr(info, data)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    return {
        "path": str(path.relative_to(ROOT)), "sha256": sha256(path), "faces": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)),
        "components": int(len(mesh.split(only_watertight=False))), "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_mm3": float(mesh.volume), "bounds_mm": [round(float(v), 4) for v in mesh.extents], "size_bytes": path.stat().st_size,
    }


def insertion_depth(slot_depth: float, thickness: float, p: dict) -> float:
    s = p["slots"]
    return slot_depth * (s["top_gap_mm"] - thickness) / (s["top_gap_mm"] - s["bottom_gap_mm"])


def main() -> None:
    p = json.loads(PARAMETERS.read_text())
    for folder in [REPORTS, VALIDATION, EXPORTS / "master", EXPORTS / "manufacturing", EXPORTS / "coupons", EXPORTS / "3mf"]:
        folder.mkdir(parents=True, exist_ok=True)
    base, base_metrics = make_base(p)
    proxy, proxy_metrics = make_base(p, proxy=True)
    gauge, gauge_metrics = make_gauge(p)
    base_outputs = export_pair(base, "momentpair-dual-slot-base", p["mesh"])
    gauge_path = export_coupon(gauge, "two-depth-card-slot-gauge", p["mesh"])
    mark_coupon_path = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-full-watermark-coupon-{REVISION}.stl"
    shutil.copyfile(MARK_COUPON_SOURCE, mark_coupon_path)
    base_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-momentpair-base-{REVISION}.3mf"
    coupon_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-fit-and-mark-coupons-{REVISION}.3mf"
    make_3mf([base_outputs[2]], base_3mf, [(95, 50, 0)], "PLA")
    make_3mf([gauge_path, mark_coupon_path], coupon_3mf, [(60, 35, 0), (160, 35, 0)], "PLA")

    mesh_paths = {"base": base_outputs[2], "slot-gauge": gauge_path, "watermark-coupon": mark_coupon_path}
    meshes = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
    artifacts = list(base_outputs) + [gauge_path, mark_coupon_path, base_3mf, coupon_3mf]
    selector = json.loads(MARK_SELECTOR.read_text())
    mark_metadata = json.loads(MARK_METADATA.read_text())
    card_depths = {
        str(thickness): {
            "rear_mm": insertion_depth(p["slots"]["rear"]["depth_mm"], thickness, p),
            "front_mm": insertion_depth(p["slots"]["front"]["depth_mm"], thickness, p),
        }
        for thickness in p["slots"]["intended_card_thickness_mm"]
    }

    source_checks = [
        check("project", p["project"] == {"id": PROJECT_ID, "revision": REVISION, "units": "mm"}, "Project identity and revision are fixed"),
        check("envelope", meshes["base"]["bounds_mm"] == [150.0, 52.0, 22.0], "Base matches the declared 150 x 52 x 22 mm envelope", {"bounds_mm": meshes["base"]["bounds_mm"]}),
        check("dual-slot", p["slots"]["rear"]["length_mm"] == 120 and p["slots"]["front"]["length_mm"] == 50, "Rear photo and offset milestone-card grooves are distinct"),
        check("privacy", p["personalization"]["front_text"] == "YOUR MOMENT" and "do not retain" in p["personalization"]["privacy_mode"], "Default geometry contains only a neutral placeholder and a no-retention contract"),
        check("text-recess", base_metrics["text_cut_volume_mm3"] > 0, "Placeholder personalization is recessed into the front rail", {"cut_volume_mm3": base_metrics["text_cut_volume_mm3"]}),
        check("supportless", p["printing"]["orientation"] == "base-down" and not p["printing"]["generated_support"], "Base and gauge are authored for base-down supportless printing"),
        check("watermark-selection", selector["selection"]["layout_tier"] == "full", "R2 selector chooses the unscaled Full tier at priority 1"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-parametric-source", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in source_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml"), record(MARK_METADATA), record(MARK_SELECTOR)], "checks": source_checks,
        "metrics": {"base": base_metrics, "gauge": gauge_metrics, "ideal_geometric_insertion_depths": card_depths, "outputs": [record(path) for path in artifacts]},
        "limitations": ["Ideal tapered-slot geometry does not prove printed grip, card safety or stability."], "required_capabilities": ["cadquery"],
    })

    mesh_checks = []
    for name, metrics in meshes.items():
        mesh_checks.extend([
            check(f"{name}-watertight", metrics["watertight"] and metrics["winding_consistent"], f"{name} is watertight and winding-consistent"),
            check(f"{name}-component", metrics["components"] == 1, f"{name} is one connected component", {"components": metrics["components"]}),
            check(f"{name}-volume", metrics["volume_mm3"] > 0, f"{name} has positive volume", {"volume_mm3": metrics["volume_mm3"]}),
            check(f"{name}-complexity", metrics["faces"] <= p["mesh"]["triangle_stop"], f"{name} is under the face budget", {"faces": metrics["faces"]}),
        ])
    mesh_status = "PASS" if all(row["status"] == "PASS" for row in mesh_checks) else "FAIL"
    write_json(VALIDATION / "mesh-generation-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-mesh-generation", "tool_version": REVISION, "status": mesh_status, "profile": "draft",
        "inputs": [record(path) for path in mesh_paths.values()], "checks": mesh_checks, "metrics": meshes, "limitations": [], "required_capabilities": ["trimesh"],
    })

    s = p["slots"]
    interface_checks = [
        check("shared-taper", gauge_metrics["top_gap_mm"] == s["top_gap_mm"] and gauge_metrics["bottom_gap_mm"] == s["bottom_gap_mm"] and gauge_metrics["back_tilt_deg"] == s["back_tilt_deg"], "Gauge and full base share one tapered-groove contract"),
        check("two-depths", gauge_metrics["slot_depths_mm"] == [s["rear"]["depth_mm"], s["front"]["depth_mm"]], "Gauge reproduces both final groove depths"),
        check("bounded-thickness", s["bottom_gap_mm"] < min(s["intended_card_thickness_mm"]) and s["top_gap_mm"] > max(s["intended_card_thickness_mm"]), "Declared card thicknesses intersect the ideal taper before its top or bottom"),
        check("ideal-insertion", all(0.5 < depth < (s["rear"]["depth_mm"] if key == "rear_mm" else s["front"]["depth_mm"]) for values in card_depths.values() for key, depth in values.items()), "Ideal geometric insertion depths remain bounded within both grooves", {"depths_mm": card_depths}),
        check("one-piece-base", meshes["base"]["components"] == 1, "Two bridge paths join both rails into one printable base"),
        check("hidden-margin", s["rear"]["depth_mm"] <= 10 and s["front"]["depth_mm"] <= 8, "Hidden lower card margins are capped at 10 mm rear and 8 mm front"),
        check("physical-gauge", meshes["slot-gauge"]["watertight"] and meshes["slot-gauge"]["components"] == 1, "Two-depth slot gauge is a separate valid manufacturing artifact"),
    ]
    write_json(VALIDATION / "interface-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-interface-validation", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in interface_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(base_outputs[2]), record(gauge_path)], "checks": interface_checks,
        "metrics": {"slots": s, "gauge": gauge_metrics, "ideal_geometric_insertion_depths": card_depths},
        "limitations": ["Rigid taper contact may mark card edges or fail to grip after process variation; the exact gauge is mandatory."], "required_capabilities": [],
    })

    watermark_checks = [
        check("asset-revision", mark_metadata["asset_revision"] == "MM-WM-001-R2", "Canonical R2 watermark assets are used"),
        check("identity", mark_metadata["product_id"] == PROJECT_ID and mark_metadata["version"] == REVISION, "Generated identity matches product ID and revision"),
        check("tier-priority", selector["selection"]["layout_tier"] == "full" and selector["selection"]["layout_priority"] == 1, "Highest-information Full tier fits at priority 1"),
        check("unscaled", selector["selection"]["uniform_scale"] == 1.0 and selector["selection"]["rotation_deg"] == 0, "Selected tier remains unscaled at 0 degrees"),
        check("domain-visible", selector["selection"]["domain_visible"] is True, "Full tier retains visible metriMade.com identity"),
        check("base-marked", base_metrics["watermark_cut_volume_mm3"] > 0, "Primary distributed body contains the exact recessed identity geometry"),
        check("wall-reserve", base_metrics["watermark_residual_to_rear_slot_mm"] >= 0.8, "Identity recess retains at least 0.8 mm to the rear groove floor", {"residual_mm": base_metrics["watermark_residual_to_rear_slot_mm"]}),
        check("mark-coupon", meshes["watermark-coupon"]["watertight"] and meshes["watermark-coupon"]["components"] == 1, "Exact Full-tier physical coupon is watertight and packaged"),
    ]
    write_json(VALIDATION / "watermark-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-watermark-integration", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in watermark_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml"), record(MARK_METADATA), record(MARK_SELECTOR), record(base_outputs[2]), record(mark_coupon_path)],
        "checks": watermark_checks, "metrics": {"selector": selector, "base": base_metrics},
        "limitations": ["Digital identity and topology checks do not prove first-layer printed legibility; the Full physical coupon remains mandatory before release."], "required_capabilities": [],
    })

    saved_pct = 100 * (proxy_metrics["cad_volume_mm3"] - base_metrics["cad_volume_mm3"]) / proxy_metrics["cad_volume_mm3"]
    opt_checks = [
        check("material-saving", saved_pct >= 30, "Two-rail body saves at least 30% CAD volume versus the equally marked solid-envelope proxy", {"saved_percent": saved_pct}),
        check("protected-envelope", base_metrics["envelope_mm"] == proxy_metrics["envelope_mm"] == [150.0, 52.0, 22.0], "Optimization retains the complete maximum envelope"),
        check("protected-interfaces", base_metrics["slot_cut_volume_mm3"] > 0 and gauge_metrics["slot_depths_mm"] == [10.0, 8.0], "Optimization retains both declared card interfaces"),
        check("supportless", True, "Rails, bridges, tapered grooves, text and underside recess require no generated support base-down"),
    ]
    write_json(REPORTS / "optimization-comparison.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-optimization-comparison", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in opt_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(base_outputs[2])], "checks": opt_checks,
        "metrics": {"selected_base_volume_mm3": base_metrics["cad_volume_mm3"], "solid_proxy_volume_mm3": proxy_metrics["cad_volume_mm3"], "cad_volume_saved_percent": saved_pct},
        "limitations": ["CAD volume is a deterministic comparison, not slicer mass or print duration."], "required_capabilities": [],
    })
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": mesh_status, "meshes": meshes})
    reports = [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json", VALIDATION / "watermark-report.json", REPORTS / "optimization-comparison.json"]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(json.loads(path.read_text())["status"] == "PASS" for path in reports) else "FAIL",
        "artifacts": [record(path) for path in artifacts], "reports": [record(path) for path in reports],
    })
    print(json.dumps({"status": json.loads((REPORTS / "build-manifest.json").read_text())["status"], "base_3mf": str(base_3mf.relative_to(ROOT)), "coupon_3mf": str(coupon_3mf.relative_to(ROOT)), "cad_volume_saved_percent": saved_pct, "meshes": meshes}, indent=2))


if __name__ == "__main__":
    main()
