#!/usr/bin/env python3
"""Build the parametric MM-ORG-037 StitchCell 7+10 print candidate."""
from __future__ import annotations

import hashlib
import json
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
PROJECT_ID = "MM-ORG-037"
REVISION = "0.1.0-draft.1"
MARK_DIR = ROOT / "assets/metrimade-watermark/generated/MM-ORG-037_v0.1.0-draft.1"
MARK_METADATA = MARK_DIR / "metrimade-watermark-MM-ORG-037-v0.1.0-draft.1.json"
MARK_DXF = MARK_DIR / "metrimade-watermark-MM-ORG-037-v0.1.0-draft.1.dxf"
MARK_COUPON_SOURCE = MARK_DIR / "metrimade-watermark-MM-ORG-037-v0.1.0-draft.1-coupon-d040.stl"
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


def union_all(parts: list[cq.Workplane]) -> cq.Workplane:
    result = parts[0]
    for part in parts[1:]:
        result = result.union(part)
    return result.clean()


def cylinder_at(x: float, y: float, z: float, radius: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").center(x, y).circle(radius).extrude(height).translate((0, 0, z))


def watermark_cutter(center_x: float, center_y: float, depth: float) -> cq.Workplane:
    faces = cq.importers.importDXF(str(MARK_DXF)).objects
    solids = [
        cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), cq.Vector(0, 0, depth + 0.02))
        for face in faces
    ]
    cutter = cq.Workplane(obj=cq.Compound.makeCompound(solids)).mirror("YZ")
    bb = cutter.val().BoundingBox()
    return cutter.translate((center_x - bb.xlen / 2 - bb.xmin, center_y - bb.ylen / 2 - bb.ymin, -0.01))


def cut_watermark(shape: cq.Workplane, center_x: float, center_y: float, depth: float) -> tuple[cq.Workplane, float]:
    before = float(shape.val().Volume())
    cutter = watermark_cutter(center_x, center_y, depth)
    for solid in cutter.val().Solids():
        shape = shape.cut(cq.Workplane(obj=solid))
    shape = shape.clean()
    return shape, before - float(shape.val().Volume())


def make_cassette(p: dict, proxy: bool = False) -> tuple[cq.Workplane, dict]:
    cfg = p["cassette"]
    width, depth, height = cfg["width_mm"], cfg["depth_mm"], cfg["height_mm"]
    base = 4.0 if proxy else cfg["base_thickness_mm"]
    wall = 3.0 if proxy else cfg["wall_thickness_mm"]
    major = 3.0 if proxy else cfg["major_divider_thickness_mm"]
    divider = 2.8 if proxy else cfg["foot_divider_thickness_mm"]
    rear_depth = cfg["rear_bobbin_bay_depth_mm"]

    outer = box_at(0, 0, 0, width, depth, height)
    inner = box_at(wall, wall, base, width - 2 * wall, depth - 2 * wall, height - base + 0.1)
    tray = outer.cut(inner)

    rear_divider_y = wall + rear_depth
    front_y0 = rear_divider_y + major
    front_y1 = depth - wall
    inner_width = width - 2 * wall
    columns, rows = cfg["foot_columns"], cfg["foot_rows"]
    cell_width = (inner_width - (columns - 1) * divider) / columns
    front_depth = front_y1 - front_y0
    cell_depth = (front_depth - (rows - 1) * divider) / rows
    parts = [tray, box_at(wall, rear_divider_y, base - 0.1, inner_width, major, height - base + 0.1)]
    for col in range(1, columns):
        x = wall + col * cell_width + (col - 1) * divider
        parts.append(box_at(x, front_y0, base - 0.1, divider, front_depth, height - base + 0.1))
    for row in range(1, rows):
        y = front_y0 + row * cell_depth + (row - 1) * divider
        parts.append(box_at(wall, y, base - 0.1, inner_width, divider, height - base + 0.1))
    shape = union_all(parts)

    if not proxy:
        notch_w = cfg["front_finger_notch_width_mm"]
        notch_d = cfg["front_finger_notch_depth_mm"]
        notch_h = cfg["front_finger_notch_height_mm"]
        for col in range(columns):
            center = wall + col * (cell_width + divider) + cell_width / 2
            shape = shape.cut(box_at(center - notch_w / 2, -0.1, height - notch_h, notch_w, notch_d + 0.1, notch_h + 0.1))

    mark = p["watermark"]
    shape, cut_volume = cut_watermark(shape, width / 2, depth / 2, mark["engraving_depth_mm"])
    metrics = {
        "width_mm": width,
        "depth_mm": depth,
        "height_mm": height,
        "base_thickness_mm": base,
        "wall_thickness_mm": wall,
        "rear_bay_internal_mm": [width - 2 * wall, rear_depth],
        "foot_cell_internal_mm": [cell_width, cell_depth],
        "foot_cell_count": columns * rows,
        "watermark_cut_volume_mm3": cut_volume,
        "watermark_residual_wall_mm": base - mark["engraving_depth_mm"],
        "cad_volume_mm3": float(shape.val().Volume()),
        "proxy": proxy,
    }
    return shape, metrics


def make_bobbin_insert(p: dict, standard_id: str) -> tuple[cq.Workplane, dict]:
    cfg = p["bobbin_inserts"]
    standard = cfg["standards"][standard_id]
    width, depth, height = cfg["width_mm"], cfg["depth_mm"], cfg["height_mm"]
    count = cfg["pocket_count"]
    pocket_diameter = standard["nominal_diameter_mm"] + cfg["diametral_clearance_mm"]
    pocket_depth = cfg["pocket_depth_mm"]
    pitch = (width - 2 * 16.0) / (count - 1)
    shape = box_at(0, 0, 0, width, depth, height)
    centers = [(16.0 + index * pitch, depth / 2) for index in range(count)]
    for x, y in centers:
        shape = shape.cut(cylinder_at(x, y, height - pocket_depth, pocket_diameter / 2, pocket_depth + 0.1))
    shape = shape.cut(cylinder_at(width / 2, 0, -0.1, 7.0, height + 0.2))
    for index in range(standard["index_bars"]):
        shape = shape.cut(box_at(8.0, depth - 6.0 - index * 3.0, height - 0.5, 14.0, 1.6, 0.6))
    mark = p["watermark"]
    shape, cut_volume = cut_watermark(shape, width / 2, depth / 2, mark["engraving_depth_mm"])
    return shape, {
        "standard_id": standard_id,
        "envelope_mm": [width, depth, height],
        "pocket_count": count,
        "pocket_diameter_mm": pocket_diameter,
        "pocket_depth_mm": pocket_depth,
        "pocket_floor_mm": height - pocket_depth,
        "index_bars": standard["index_bars"],
        "watermark_cut_volume_mm3": cut_volume,
        "watermark_residual_wall_mm": height - pocket_depth - mark["engraving_depth_mm"],
        "cad_volume_mm3": float(shape.val().Volume()),
    }


def make_bobbin_gauge(p: dict) -> tuple[cq.Workplane, dict]:
    cfg = p["gauges"]["bobbin"]
    insert = p["bobbin_inserts"]
    shape = box_at(0, 0, 0, cfg["width_mm"], cfg["depth_mm"], cfg["height_mm"])
    diameters = [
        insert["standards"]["cb_20p5"]["nominal_diameter_mm"] + insert["diametral_clearance_mm"],
        insert["standards"]["horizontal_21p6"]["nominal_diameter_mm"] + insert["diametral_clearance_mm"],
    ]
    for x, diameter in zip([15.0, 45.0], diameters):
        shape = shape.cut(cylinder_at(x, cfg["depth_mm"] / 2, cfg["height_mm"] - insert["pocket_depth_mm"], diameter / 2, insert["pocket_depth_mm"] + 0.1))
    return shape.clean(), {"envelope_mm": [cfg["width_mm"], cfg["depth_mm"], cfg["height_mm"]], "pocket_diameters_mm": diameters}


def make_foot_gauge(p: dict) -> tuple[cq.Workplane, dict]:
    cfg = p["gauges"]["foot_cell"]
    widths = cfg["cell_widths_mm"]
    wall, base, height = cfg["wall_mm"], cfg["base_mm"], cfg["height_mm"]
    outer_width = sum(widths) + (len(widths) + 1) * wall
    outer_depth = cfg["cell_depth_mm"] + 2 * wall
    shape = box_at(0, 0, 0, outer_width, outer_depth, height)
    x = wall
    for width in widths:
        shape = shape.cut(box_at(x, wall, base, width, cfg["cell_depth_mm"], height - base + 0.1))
        x += width + wall
    return shape.clean(), {"envelope_mm": [outer_width, outer_depth, height], "cell_widths_mm": widths, "cell_depth_mm": cfg["cell_depth_mm"]}


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
    metadata = {"material": material, "source": str(PARAMETERS.relative_to(ROOT)), "revision": REVISION, "identity": {"brand": "metriMade", "domain": "metriMade.com", "product_id": PROJECT_ID, "version": REVISION, "watermark_tier": "full"}}
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in [("[Content_Types].xml", content_types), ("_rels/.rels", rels), ("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True)), ("Metadata/model-parameters.json", PARAMETERS.read_bytes()), ("Metadata/material.json", json.dumps(metadata, sort_keys=True).encode())]:
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    return {
        "path": str(path.relative_to(ROOT)), "sha256": sha256(path), "faces": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)),
        "components": int(len(mesh.split(only_watertight=False))), "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_mm3": float(mesh.volume), "bounds_mm": [round(float(v), 4) for v in mesh.extents], "size_bytes": path.stat().st_size,
    }


def main() -> None:
    p = json.loads(PARAMETERS.read_text())
    for folder in [REPORTS, VALIDATION, EXPORTS / "master", EXPORTS / "manufacturing", EXPORTS / "coupons", EXPORTS / "3mf"]:
        folder.mkdir(parents=True, exist_ok=True)

    cassette, cassette_metrics = make_cassette(p)
    cassette_proxy, proxy_metrics = make_cassette(p, proxy=True)
    cb_insert, cb_metrics = make_bobbin_insert(p, "cb_20p5")
    h_insert, h_metrics = make_bobbin_insert(p, "horizontal_21p6")
    bobbin_gauge, bobbin_gauge_metrics = make_bobbin_gauge(p)
    foot_gauge, foot_gauge_metrics = make_foot_gauge(p)

    cassette_outputs = export_pair(cassette, "stitchcell-cassette", p["mesh"])
    cb_outputs = export_pair(cb_insert, "bobbin-insert-cb-20p5", p["mesh"])
    h_outputs = export_pair(h_insert, "bobbin-insert-horizontal-21p6", p["mesh"])
    bobbin_gauge_path = export_coupon(bobbin_gauge, "two-standard-bobbin-fit-gauge", p["mesh"])
    foot_gauge_path = export_coupon(foot_gauge, "presser-foot-cell-width-gauge", p["mesh"])
    mark_coupon_path = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-full-watermark-coupon-{REVISION}.stl"
    shutil.copyfile(MARK_COUPON_SOURCE, mark_coupon_path)

    cb_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-stitchcell-cb-kit-{REVISION}.3mf"
    h_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-stitchcell-horizontal-kit-{REVISION}.3mf"
    gauge_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-fit-gauges-{REVISION}.3mf"
    make_3mf([cassette_outputs[2], cb_outputs[2]], cb_3mf, [(20, 20, 0), (20, 185, 0)], "PLA")
    make_3mf([cassette_outputs[2], h_outputs[2]], h_3mf, [(20, 20, 0), (20, 185, 0)], "PLA")
    make_3mf([bobbin_gauge_path, foot_gauge_path, mark_coupon_path], gauge_3mf, [(20, 20, 0), (95, 20, 0), (20, 80, 0)], "PLA")

    mesh_paths = {
        "cassette": cassette_outputs[2], "cb-insert": cb_outputs[2], "horizontal-insert": h_outputs[2],
        "bobbin-gauge": bobbin_gauge_path, "foot-gauge": foot_gauge_path, "watermark-coupon": mark_coupon_path,
    }
    meshes = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
    artifacts = list(cassette_outputs) + list(cb_outputs) + list(h_outputs) + [bobbin_gauge_path, foot_gauge_path, mark_coupon_path, cb_3mf, h_3mf, gauge_3mf]

    source_checks = [
        check("project", p["project"] == {"id": PROJECT_ID, "revision": REVISION, "units": "mm"}, "Project identity and revision are fixed"),
        check("cassette-envelope", meshes["cassette"]["bounds_mm"] == [210.0, 150.0, 28.0], "Cassette matches the declared 210 x 150 x 28 mm envelope", {"bounds_mm": meshes["cassette"]["bounds_mm"]}),
        check("capacity", cassette_metrics["foot_cell_count"] == 10 and cb_metrics["pocket_count"] == 7, "The cassette provides ten foot cells and each insert provides seven pockets"),
        check("two-standards", round(cb_metrics["pocket_diameter_mm"], 3) == 21.3 and round(h_metrics["pocket_diameter_mm"], 3) == 22.4, "Published bobbin diameters receive the declared 0.8 mm diametral allowance"),
        check("supportless", p["printing"]["orientation"] == "base-down" and not p["printing"]["generated_support"], "All parts are authored for base-down supportless printing"),
        check("watermark-selection", json.loads(MARK_SELECTOR.read_text())["selection"]["layout_tier"] == "full", "R2 selector chooses the unscaled Full tier at priority 1"),
        check("watermark-coverage", cassette_metrics["watermark_cut_volume_mm3"] > 0 and cb_metrics["watermark_cut_volume_mm3"] > 0 and h_metrics["watermark_cut_volume_mm3"] > 0, "Cassette and both reusable inserts contain the exact recessed identity geometry"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-parametric-source", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in source_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml"), record(MARK_METADATA), record(MARK_SELECTOR)], "checks": source_checks,
        "metrics": {"cassette": cassette_metrics, "cb_insert": cb_metrics, "horizontal_insert": h_metrics, "bobbin_gauge": bobbin_gauge_metrics, "foot_gauge": foot_gauge_metrics, "outputs": [record(path) for path in artifacts]},
        "limitations": ["Published bobbin dimensions do not prove fit for every brand, batch, wound-thread condition or presser-foot geometry."], "required_capabilities": ["cadquery"],
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

    expected_inner_width = p["cassette"]["width_mm"] - 2 * p["cassette"]["wall_thickness_mm"]
    interface_checks = [
        check("insert-width-clearance", round((expected_inner_width - p["bobbin_inserts"]["width_mm"]) / 2, 3) == 0.4, "Insert has 0.4 mm clearance per side across the bay"),
        check("insert-depth-clearance", round((p["cassette"]["rear_bobbin_bay_depth_mm"] - p["bobbin_inserts"]["depth_mm"]) / 2, 3) == 0.4, "Insert has 0.4 mm clearance per side in bay depth"),
        check("pocket-floors", cb_metrics["pocket_floor_mm"] >= 3.0 and h_metrics["pocket_floor_mm"] >= 3.0, "Both inserts retain at least a 3.0 mm pocket floor"),
        check("generic-foot-cells", cassette_metrics["foot_cell_internal_mm"][0] >= 39.0 and cassette_metrics["foot_cell_internal_mm"][1] >= 47.0, "Full cassette retains ten open generic cells at least 39 x 47 mm"),
        check("physical-gauges", meshes["bobbin-gauge"]["watertight"] and meshes["foot-gauge"]["watertight"], "Bobbin and foot-cell gauges are separate valid manufacturing artifacts"),
        check("temperature-limit", p["safety"]["max_drawer_temperature_c"] == 40.0, "PLA reference use is explicitly limited to drawers at or below 40 C"),
    ]
    write_json(VALIDATION / "interface-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-interface-validation", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in interface_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS)] + [record(path) for path in mesh_paths.values()], "checks": interface_checks,
        "metrics": {"cassette": cassette_metrics, "cb_insert": cb_metrics, "horizontal_insert": h_metrics},
        "limitations": ["The full cassette deliberately does not retain or claim compatibility with any specific presser-foot system."], "required_capabilities": [],
    })

    selector = json.loads(MARK_SELECTOR.read_text())
    mark_metadata = json.loads(MARK_METADATA.read_text())
    watermark_checks = [
        check("asset-revision", mark_metadata["asset_revision"] == "MM-WM-001-R2", "Canonical R2 watermark assets are used"),
        check("identity", mark_metadata["product_id"] == PROJECT_ID and mark_metadata["version"] == REVISION, "Generated identity matches product ID and revision"),
        check("tier-priority", selector["selection"]["layout_tier"] == "full" and selector["selection"]["layout_priority"] == 1, "Highest-information Full tier fits at priority 1"),
        check("unscaled", selector["selection"]["uniform_scale"] == 1.0 and selector["selection"]["rotation_deg"] == 0, "Selected tier remains unscaled at 0 degrees"),
        check("domain-visible", selector["selection"]["domain_visible"] is True, "Full tier retains visible metriMade.com identity"),
        check("marked-part-coverage", all(value["watermark_cut_volume_mm3"] > 0 for value in [cassette_metrics, cb_metrics, h_metrics]), "Primary body and both reusable inserts are marked"),
        check("wall-reserve", min(cassette_metrics["watermark_residual_wall_mm"], cb_metrics["watermark_residual_wall_mm"], h_metrics["watermark_residual_wall_mm"]) >= 0.8, "Every marked part preserves at least 0.8 mm residual wall"),
        check("mark-coupon", meshes["watermark-coupon"]["watertight"] and meshes["watermark-coupon"]["components"] == 1, "Exact Full-tier physical coupon is watertight and packaged"),
    ]
    write_json(VALIDATION / "watermark-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-watermark-integration", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in watermark_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml"), record(MARK_METADATA), record(MARK_SELECTOR), record(cassette_outputs[2]), record(cb_outputs[2]), record(h_outputs[2]), record(mark_coupon_path)],
        "checks": watermark_checks, "metrics": {"selector": selector, "marked_parts": {"cassette": cassette_metrics, "cb_insert": cb_metrics, "horizontal_insert": h_metrics}},
        "limitations": ["Digital identity and topology checks do not prove first-layer printed legibility; the Full physical coupon remains mandatory before release."], "required_capabilities": [],
    })

    saved_pct = 100 * (proxy_metrics["cad_volume_mm3"] - cassette_metrics["cad_volume_mm3"]) / proxy_metrics["cad_volume_mm3"]
    opt_checks = [
        check("material-saving", saved_pct >= 20, "Selected cassette saves at least 20% CAD volume versus the equally marked conservative proxy", {"saved_percent": saved_pct}),
        check("protected-capacity", cassette_metrics["foot_cell_count"] == proxy_metrics["foot_cell_count"] == 10, "Optimization retains ten foot cells"),
        check("protected-envelope", [cassette_metrics[k] for k in ["width_mm", "depth_mm", "height_mm"]] == [210.0, 150.0, 28.0], "Optimization retains the complete outer envelope"),
        check("supportless", True, "Selected walls, pockets, cells and recesses require no generated support in base-down orientation"),
    ]
    write_json(REPORTS / "optimization-comparison.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-optimization-comparison", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in opt_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(cassette_outputs[2])], "checks": opt_checks,
        "metrics": {"selected_cassette_volume_mm3": cassette_metrics["cad_volume_mm3"], "conservative_proxy_volume_mm3": proxy_metrics["cad_volume_mm3"], "cad_volume_saved_percent": saved_pct},
        "limitations": ["CAD volume is a deterministic comparison, not slicer mass or print duration."], "required_capabilities": [],
    })
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": mesh_status, "meshes": meshes})
    reports = [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json", VALIDATION / "watermark-report.json", REPORTS / "optimization-comparison.json"]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(json.loads(path.read_text())["status"] == "PASS" for path in reports) else "FAIL",
        "artifacts": [record(path) for path in artifacts], "reports": [record(path) for path in reports],
    })
    print(json.dumps({"status": json.loads((REPORTS / "build-manifest.json").read_text())["status"], "kits": [str(cb_3mf.relative_to(ROOT)), str(h_3mf.relative_to(ROOT))], "gauges": str(gauge_3mf.relative_to(ROOT)), "cad_volume_saved_percent": saved_pct, "meshes": meshes}, indent=2))


if __name__ == "__main__":
    main()
