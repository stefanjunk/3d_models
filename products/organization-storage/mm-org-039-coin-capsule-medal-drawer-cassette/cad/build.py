#!/usr/bin/env python3
"""Build the parametric MM-ORG-039 CollectorGrid 6 print candidate."""
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
PROJECT_ID = "MM-ORG-039"
REVISION = "0.1.0-draft.1"
MARK_ROOT = ROOT / "assets/metrimade-watermark/generated"
FULL_DIR = MARK_ROOT / "MM-ORG-039_v0.1.0-draft.1"
MICRO_DIR = MARK_ROOT / "MM-ORG-039_v0.1.0-draft.1_micro"
FULL_METADATA = FULL_DIR / "metrimade-watermark-MM-ORG-039-v0.1.0-draft.1.json"
MICRO_METADATA = MICRO_DIR / "metrimade-watermark-MM-ORG-039-v0.1.0-draft.1-micro.json"
FULL_DXF = FULL_DIR / "metrimade-watermark-MM-ORG-039-v0.1.0-draft.1.dxf"
MICRO_DXF = MICRO_DIR / "metrimade-watermark-MM-ORG-039-v0.1.0-draft.1-micro.dxf"
FULL_COUPON = FULL_DIR / "metrimade-watermark-MM-ORG-039-v0.1.0-draft.1-coupon-d040.stl"
MICRO_COUPON = MICRO_DIR / "metrimade-watermark-MM-ORG-039-v0.1.0-draft.1-micro-coupon-d040.stl"
HOST_SELECTOR = VALIDATION / "watermark-selector-host.json"
ADAPTER_SELECTOR = VALIDATION / "watermark-selector-adapter.json"


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


def cut_compound(shape: cq.Workplane, cutter: cq.Workplane) -> cq.Workplane:
    for solid in cutter.val().Solids():
        shape = shape.cut(cq.Workplane(obj=solid))
    return shape.clean()


def watermark_cutter(path: Path, center_x: float, center_y: float, depth: float) -> cq.Workplane:
    faces = cq.importers.importDXF(str(path)).objects
    solids = [cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), cq.Vector(0, 0, depth + 0.02)) for face in faces]
    cutter = cq.Workplane(obj=cq.Compound.makeCompound(solids)).mirror("YZ")
    bb = cutter.val().BoundingBox()
    return cutter.translate((center_x - bb.xlen / 2 - bb.xmin, center_y - bb.ylen / 2 - bb.ymin, -0.01))


def derived_geometry(p: dict) -> dict:
    h, i = p["host"], p["interfaces"]
    inner_w = h["width_mm"] - 2 * h["wall_thickness_mm"]
    inner_d = h["depth_mm"] - 2 * h["wall_thickness_mm"]
    cell_w = (inner_w - (h["columns"] - 1) * h["wall_thickness_mm"]) / h["columns"]
    cell_d = (inner_d - (h["rows"] - 1) * h["wall_thickness_mm"]) / h["rows"]
    x_pitch = cell_w + h["wall_thickness_mm"]
    y_pitch = cell_d + h["wall_thickness_mm"]
    return {
        "inner_width_mm": inner_w,
        "inner_depth_mm": inner_d,
        "cell_width_mm": cell_w,
        "cell_depth_mm": cell_d,
        "cell_centers_x_mm": [(-1 + col) * x_pitch for col in range(h["columns"])],
        "cell_centers_y_mm": [-y_pitch / 2, y_pitch / 2],
        "vertical_divider_centers_x_mm": [-x_pitch / 2, x_pitch / 2],
        "adapter_width_mm": cell_w - 2 * i["adapter_clearance_per_side_mm"],
        "adapter_depth_mm": cell_d - 2 * i["adapter_clearance_per_side_mm"],
        "square_opening_mm": i["square_capsule_target_mm"][0] + 2 * i["capsule_clearance_per_side_mm"],
        "round_opening_diameter_mm": i["round_capsule_outer_target_mm"] + 2 * i["capsule_clearance_per_side_mm"],
    }


def make_host(p: dict, proxy: bool = False) -> tuple[cq.Workplane, dict]:
    h, mark = p["host"], p["watermark"]
    g = derived_geometry(p)
    t, floor = h["wall_thickness_mm"], h["floor_thickness_mm"]
    parts: list[cq.Workplane] = []
    if proxy:
        parts.append(box_center(0, 0, floor / 2, h["width_mm"], h["depth_mm"], floor))
    else:
        rim_outer = box_center(0, 0, floor / 2, h["width_mm"], h["depth_mm"], floor)
        rim_inner = box_center(0, 0, floor / 2, h["width_mm"] - 2 * h["floor_rim_width_mm"], h["depth_mm"] - 2 * h["floor_rim_width_mm"], floor + 0.2)
        parts.append(rim_outer.cut(rim_inner))
        for x in g["vertical_divider_centers_x_mm"]:
            parts.append(box_center(x, 0, floor / 2, h["support_rail_width_mm"], h["depth_mm"] - 2 * t, floor))
        parts.append(box_center(0, 0, floor / 2, h["width_mm"] - 2 * t, h["support_rail_width_mm"], floor))
        parts.append(box_center(mark["host_center_xy_mm"][0], mark["host_center_xy_mm"][1], floor / 2, mark["host_land_mm"][0], mark["host_land_mm"][1], floor))

    zc = h["height_mm"] / 2
    parts.extend([
        box_center(0, -h["depth_mm"] / 2 + t / 2, zc, h["width_mm"], t, h["height_mm"]),
        box_center(0, h["depth_mm"] / 2 - t / 2, zc, h["width_mm"], t, h["height_mm"]),
        box_center(-h["width_mm"] / 2 + t / 2, 0, zc, t, h["depth_mm"] - 2 * t, h["height_mm"]),
        box_center(h["width_mm"] / 2 - t / 2, 0, zc, t, h["depth_mm"] - 2 * t, h["height_mm"]),
    ])
    for x in g["vertical_divider_centers_x_mm"]:
        parts.append(box_center(x, 0, zc, t, g["inner_depth_mm"], h["height_mm"]))
    parts.append(box_center(0, 0, zc, g["inner_width_mm"], t, h["height_mm"]))

    for cx in g["cell_centers_x_mm"]:
        for cy in g["cell_centers_y_mm"]:
            for local_y in h["support_rail_centers_y_mm"]:
                parts.append(box_center(cx, cy + local_y, h["support_top_z_mm"] / 2, g["cell_width_mm"] + 0.2, h["support_rail_width_mm"], h["support_top_z_mm"]))

    shape = union_all(parts)
    notch_height = h["height_mm"] - h["front_access_notch_floor_z_mm"] + 0.2
    notch_z = h["front_access_notch_floor_z_mm"] + notch_height / 2
    for cx in g["cell_centers_x_mm"]:
        shape = shape.cut(box_center(cx, -h["depth_mm"] / 2, notch_z, h["front_access_notch_width_mm"], t + 1.0, notch_height))
        shape = shape.cut(box_center(cx, 0, notch_z, h["front_access_notch_width_mm"], t + 1.0, notch_height))
    before_mark = float(shape.val().Volume())
    shape = cut_compound(shape, watermark_cutter(FULL_DXF, mark["host_center_xy_mm"][0], mark["host_center_xy_mm"][1], mark["engraving_depth_mm"]))
    final_volume = float(shape.val().Volume())
    return shape.clean(), {
        "proxy": proxy,
        "envelope_mm": [h["width_mm"], h["depth_mm"], h["height_mm"]],
        "cad_volume_mm3": final_volume,
        "watermark_cut_volume_mm3": before_mark - final_volume,
        "watermark_residual_wall_mm": h["floor_thickness_mm"] - mark["engraving_depth_mm"],
        "derived": g,
    }


def make_adapter(p: dict, kind: str) -> tuple[cq.Workplane, dict]:
    i, mark = p["interfaces"], p["watermark"]
    g = derived_geometry(p)
    height = i["adapter_thickness_mm"]
    shape = box_center(0, 0, height / 2, g["adapter_width_mm"], g["adapter_depth_mm"], height).edges("|Z").fillet(2.0)
    if kind == "square-50":
        opening = box_center(0, i["adapter_opening_center_y_mm"], height / 2, g["square_opening_mm"], g["square_opening_mm"], height + 0.3).edges("|Z").fillet(1.5)
        target = i["square_capsule_target_mm"][:2]
        opening_metric: object = [g["square_opening_mm"], g["square_opening_mm"]]
    elif kind == "round-46":
        opening = cq.Workplane("XY").circle(g["round_opening_diameter_mm"] / 2).extrude(height + 0.3).translate((0, i["adapter_opening_center_y_mm"], -0.15))
        target = i["round_capsule_outer_target_mm"]
        opening_metric = g["round_opening_diameter_mm"]
    else:
        raise ValueError(kind)
    shape = shape.cut(opening)
    label = box_center(0, i["label_bay_center_y_mm"], height - i["label_bay_recess_mm"] / 2 + 0.01, i["label_bay_width_mm"], i["label_bay_depth_mm"], i["label_bay_recess_mm"] + 0.02)
    before_label = float(shape.val().Volume())
    shape = shape.cut(label)
    after_label = float(shape.val().Volume())
    before_mark = after_label
    shape = cut_compound(shape, watermark_cutter(MICRO_DXF, mark["adapter_center_xy_mm"][0], mark["adapter_center_xy_mm"][1], mark["engraving_depth_mm"]))
    final_volume = float(shape.val().Volume())
    return shape.clean(), {
        "kind": kind,
        "envelope_mm": [g["adapter_width_mm"], g["adapter_depth_mm"], height],
        "target_mm": target,
        "opening_mm": opening_metric,
        "label_cut_volume_mm3": before_label - after_label,
        "watermark_cut_volume_mm3": before_mark - final_volume,
        "opposed_recess_residual_mm": height - i["label_bay_recess_mm"] - mark["engraving_depth_mm"],
        "cad_volume_mm3": final_volume,
    }


def make_gauge(p: dict) -> tuple[cq.Workplane, dict]:
    gauge, i = p["gauge"], p["interfaces"]
    g = derived_geometry(p)
    shape = box_center(0, 0, gauge["height_mm"] / 2, gauge["width_mm"], gauge["depth_mm"], gauge["height_mm"]).edges("|Z").fillet(3.0)
    large = box_center(-45, 0, gauge["height_mm"] / 2, g["cell_width_mm"], g["cell_depth_mm"], gauge["height_mm"] + 0.3).edges("|Z").fillet(1.5)
    square = box_center(48, 25, gauge["height_mm"] / 2, g["square_opening_mm"], g["square_opening_mm"], gauge["height_mm"] + 0.3).edges("|Z").fillet(1.5)
    round_cut = cq.Workplane("XY").circle(g["round_opening_diameter_mm"] / 2).extrude(gauge["height_mm"] + 0.3).translate((48, -25, -0.15))
    shape = shape.cut(large).cut(square).cut(round_cut)
    label = box_center(-45, 44, gauge["height_mm"] - i["label_bay_recess_mm"] / 2 + 0.01, i["label_bay_width_mm"], i["label_bay_depth_mm"], i["label_bay_recess_mm"] + 0.02)
    shape = shape.cut(label)
    return shape.clean(), {
        "envelope_mm": [gauge["width_mm"], gauge["depth_mm"], gauge["height_mm"]],
        "direct_cell_opening_mm": [g["cell_width_mm"], g["cell_depth_mm"]],
        "square_opening_mm": [g["square_opening_mm"], g["square_opening_mm"]],
        "round_opening_diameter_mm": g["round_opening_diameter_mm"],
        "label_bay_mm": [i["label_bay_width_mm"], i["label_bay_depth_mm"], i["label_bay_recess_mm"]],
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


def make_3mf(mesh_paths: list[Path], target: Path, translations: list[tuple[float, float, float]], material: str, package_variant: str) -> None:
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
    metadata = {
        "material": material,
        "source": str(PARAMETERS.relative_to(ROOT)),
        "revision": REVISION,
        "variant": package_variant,
        "contact_boundary": "protective plastic capsules only; no bare collectible contact or archival claim",
        "identity": {"brand": "metriMade", "domain": "metriMade.com", "product_id": PROJECT_ID, "version": REVISION, "host_tier": "full", "adapter_tier": "micro"},
    }
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


def main() -> None:
    p = json.loads(PARAMETERS.read_text())
    for folder in [REPORTS, VALIDATION, EXPORTS / "master", EXPORTS / "manufacturing", EXPORTS / "coupons", EXPORTS / "3mf"]:
        folder.mkdir(parents=True, exist_ok=True)
    host, host_metrics = make_host(p)
    baseline, baseline_metrics = make_host(p, proxy=True)
    square, square_metrics = make_adapter(p, "square-50")
    round_adapter, round_metrics = make_adapter(p, "round-46")
    gauge, gauge_metrics = make_gauge(p)

    host_outputs = export_pair(host, "collectorgrid-six-cell-host", p["mesh"])
    square_outputs = export_pair(square, "square-50-label-adapter", p["mesh"])
    round_outputs = export_pair(round_adapter, "round-46-label-adapter", p["mesh"])
    gauge_path = export_coupon(gauge, "three-interface-label-gauge", p["mesh"])
    full_coupon_path = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-full-watermark-coupon-{REVISION}.stl"
    micro_coupon_path = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-micro-watermark-coupon-{REVISION}.stl"
    shutil.copyfile(FULL_COUPON, full_coupon_path); shutil.copyfile(MICRO_COUPON, micro_coupon_path)

    square_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-collectorgrid-square-50-kit-{REVISION}.3mf"
    round_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-collectorgrid-round-46-kit-{REVISION}.3mf"
    gauge_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-fit-label-and-mark-gauges-{REVISION}.3mf"
    adapter_positions = [(260, 40, 0), (335, 40, 0), (260, 115, 0), (335, 115, 0), (260, 190, 0), (335, 190, 0)]
    make_3mf([host_outputs[2]] + [square_outputs[2]] * 6, square_3mf, [(110, 75, 0)] + adapter_positions, "PLA", "square-50-six-cell-kit")
    make_3mf([host_outputs[2]] + [round_outputs[2]] * 6, round_3mf, [(110, 75, 0)] + adapter_positions, "PLA", "round-46-six-cell-kit")
    make_3mf([gauge_path, square_outputs[2], round_outputs[2], full_coupon_path, micro_coupon_path], gauge_3mf, [(100, 60, 0), (230, 40, 0), (310, 40, 0), (250, 110, 0), (350, 110, 0)], "PLA", "fit-label-and-selected-mark-gauges")

    mesh_paths = {
        "host": host_outputs[2], "square-adapter": square_outputs[2], "round-adapter": round_outputs[2], "interface-gauge": gauge_path,
        "full-watermark-coupon": full_coupon_path, "micro-watermark-coupon": micro_coupon_path,
    }
    meshes = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
    artifacts = list(host_outputs) + list(square_outputs) + list(round_outputs) + [gauge_path, full_coupon_path, micro_coupon_path, square_3mf, round_3mf, gauge_3mf]
    host_selector = json.loads(HOST_SELECTOR.read_text()); adapter_selector = json.loads(ADAPTER_SELECTOR.read_text())
    full_metadata = json.loads(FULL_METADATA.read_text()); micro_metadata = json.loads(MICRO_METADATA.read_text())
    g = derived_geometry(p)

    source_checks = [
        check("project", p["project"] == {"id": PROJECT_ID, "revision": REVISION, "units": "mm"}, "Project identity and revision are fixed"),
        check("host-envelope", meshes["host"]["bounds_mm"] == [214.0, 144.0, 16.0], "Host matches the declared 214 x 144 x 16 mm envelope", {"bounds_mm": meshes["host"]["bounds_mm"]}),
        check("six-cells", p["host"]["columns"] * p["host"]["rows"] == 6, "Host declares six independent cells"),
        check("derived-cells", abs(g["cell_width_mm"] - p["host"]["cell_width_mm"]) < 1e-6 and abs(g["cell_depth_mm"] - p["host"]["cell_depth_mm"]) < 1e-6, "Cell dimensions derive from the host, walls and divider count"),
        check("contact-boundary", p["safety"]["encapsulated_items_only"] and p["safety"]["no_bare_coin_or_medal_contact_claim"], "Source excludes bare collectible contact and archival claims"),
        check("supportless", p["printing"]["orientation"] == "base-down" and not p["printing"]["generated_support"], "Host, adapters and gauge are authored for base-down supportless printing"),
        check("watermark-selection", host_selector["selection"]["layout_tier"] == "full" and adapter_selector["selection"]["layout_tier"] == "micro", "R2 selectors choose Full for the host and Micro for the constrained adapter band"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-parametric-source", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in source_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml"), record(FULL_METADATA), record(MICRO_METADATA), record(HOST_SELECTOR), record(ADAPTER_SELECTOR)],
        "checks": source_checks, "metrics": {"host": host_metrics, "square_adapter": square_metrics, "round_adapter": round_metrics, "gauge": gauge_metrics, "outputs": [record(path) for path in artifacts]},
        "limitations": ["Measured CAD interfaces do not prove capsule compatibility, abrasion safety, archival suitability or drawer function."], "required_capabilities": ["cadquery"],
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

    i = p["interfaces"]
    direct_clearance = [(g["cell_width_mm"] - i["direct_large_square_target_mm"][0]) / 2, (g["cell_depth_mm"] - i["direct_large_square_target_mm"][1]) / 2]
    interface_checks = [
        check("direct-large-clearance", min(direct_clearance) >= 0.4, "Direct large-square cell has at least 0.4 mm clearance per side", {"clearance_per_side_mm": direct_clearance}),
        check("adapter-host-clearance", abs((g["cell_width_mm"] - g["adapter_width_mm"]) / 2 - 0.4) < 1e-6 and abs((g["cell_depth_mm"] - g["adapter_depth_mm"]) / 2 - 0.4) < 1e-6, "Both adapters use the declared loose 0.4 mm-per-side host clearance"),
        check("square-opening", square_metrics["opening_mm"] == [50.8, 50.8], "Square adapter adds 0.4 mm clearance per side to the measured 50 mm target"),
        check("round-opening", round_metrics["opening_mm"] == 46.8, "Round adapter adds 0.4 mm radial clearance to the measured 46 mm target"),
        check("exact-gauge", gauge_metrics["direct_cell_opening_mm"] == [g["cell_width_mm"], g["cell_depth_mm"]] and gauge_metrics["square_opening_mm"] == square_metrics["opening_mm"] and gauge_metrics["round_opening_diameter_mm"] == round_metrics["opening_mm"], "Gauge reproduces the host cell and both adapter openings"),
        check("label-contract", gauge_metrics["label_bay_mm"] == [i["label_bay_width_mm"], i["label_bay_depth_mm"], i["label_bay_recess_mm"]], "Gauge reproduces the adapter paper-label bay"),
        check("loaded-height", p["host"]["support_top_z_mm"] + i["square_capsule_target_mm"][2] <= p["host"]["height_mm"] + 0.5, "Declared square capsule remains at or below the protected loaded-height allowance"),
        check("opposed-recess-reserve", min(square_metrics["opposed_recess_residual_mm"], round_metrics["opposed_recess_residual_mm"]) >= 0.8, "Adapter retains at least 0.8 mm between the top label recess and underside identity"),
        check("access-notches", p["host"]["front_access_notch_width_mm"] >= 40 and p["host"]["front_access_notch_floor_z_mm"] <= p["host"]["support_top_z_mm"], "Each cell front edge opens to the support level for fingertip access"),
    ]
    write_json(VALIDATION / "interface-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-interface-validation", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in interface_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(host_outputs[2]), record(square_outputs[2]), record(round_outputs[2]), record(gauge_path)], "checks": interface_checks,
        "metrics": {"derived": g, "direct_large_clearance_per_side_mm": direct_clearance, "square_adapter": square_metrics, "round_adapter": round_metrics, "gauge": gauge_metrics},
        "limitations": ["Nominal clearances and topological validity do not establish extraction force, abrasion, chemical compatibility or long-term paper/capsule behavior."], "required_capabilities": [],
    })

    watermark_checks = [
        check("asset-revision", full_metadata["asset_revision"] == micro_metadata["asset_revision"] == "MM-WM-001-R2", "Canonical R2 watermark assets are used"),
        check("identity", full_metadata["product_id"] == micro_metadata["product_id"] == PROJECT_ID and full_metadata["version"] == micro_metadata["version"] == REVISION, "Generated identities match product ID and revision"),
        check("host-tier", host_selector["selection"]["layout_tier"] == "full" and host_selector["selection"]["layout_priority"] == 1 and host_selector["selection"]["domain_visible"], "Host uses the highest-information Full tier at priority 1"),
        check("adapter-tier", adapter_selector["selection"]["layout_tier"] == "micro" and adapter_selector["selection"]["layout_priority"] == 3 and not adapter_selector["selection"]["domain_visible"], "Adapter band deterministically falls back to the unscaled Micro tier"),
        check("unscaled", host_selector["selection"]["uniform_scale"] == adapter_selector["selection"]["uniform_scale"] == 1.0, "Both selected tiers remain unscaled"),
        check("all-reusable-parts-marked", host_metrics["watermark_cut_volume_mm3"] > 0 and square_metrics["watermark_cut_volume_mm3"] > 0 and round_metrics["watermark_cut_volume_mm3"] > 0, "Host and both reusable adapter sources contain recessed identity geometry"),
        check("residual-walls", host_metrics["watermark_residual_wall_mm"] >= 0.8 and min(square_metrics["opposed_recess_residual_mm"], round_metrics["opposed_recess_residual_mm"]) >= 0.8, "Host and adapters retain the required residual wall"),
        check("selected-coupons", meshes["full-watermark-coupon"]["watertight"] and meshes["micro-watermark-coupon"]["watertight"], "Exact Full and Micro physical coupons are watertight and packaged"),
    ]
    write_json(VALIDATION / "watermark-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-watermark-integration", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in watermark_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml"), record(FULL_METADATA), record(MICRO_METADATA), record(HOST_SELECTOR), record(ADAPTER_SELECTOR), record(host_outputs[2]), record(square_outputs[2]), record(round_outputs[2]), record(full_coupon_path), record(micro_coupon_path)],
        "checks": watermark_checks, "metrics": {"host_selector": host_selector, "adapter_selector": adapter_selector, "host": host_metrics, "square_adapter": square_metrics, "round_adapter": round_metrics},
        "limitations": ["Digital identity and topology checks do not prove intended-process legibility; both selected-tier physical coupons remain mandatory before release."], "required_capabilities": [],
    })

    saved_pct = 100 * (baseline_metrics["cad_volume_mm3"] - host_metrics["cad_volume_mm3"]) / baseline_metrics["cad_volume_mm3"]
    opt_checks = [
        check("material-saving", saved_pct >= 20, "Open lattice saves at least 20% CAD volume versus the equally marked continuous-floor host", {"saved_percent": saved_pct}),
        check("protected-envelope", host_metrics["envelope_mm"] == baseline_metrics["envelope_mm"] == [214.0, 144.0, 16.0], "Optimization retains the complete host envelope"),
        check("protected-cells", host_metrics["derived"]["cell_width_mm"] == baseline_metrics["derived"]["cell_width_mm"] and host_metrics["derived"]["cell_depth_mm"] == baseline_metrics["derived"]["cell_depth_mm"], "Optimization retains all six cell dimensions"),
        check("support-rails-retained", p["host"]["support_top_z_mm"] == 7.5 and len(p["host"]["support_rail_centers_y_mm"]) == 2, "Optimization retains both support rails in every cell"),
    ]
    write_json(REPORTS / "optimization-comparison.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-optimization-comparison", "tool_version": REVISION,
        "status": "PASS" if all(row["status"] == "PASS" for row in opt_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(host_outputs[2])], "checks": opt_checks,
        "metrics": {"selected_host_volume_mm3": host_metrics["cad_volume_mm3"], "continuous_floor_host_volume_mm3": baseline_metrics["cad_volume_mm3"], "cad_volume_saved_percent": saved_pct},
        "limitations": ["CAD volume is a deterministic comparison, not slicer mass or print duration."], "required_capabilities": [],
    })
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": mesh_status, "meshes": meshes})
    reports = [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json", VALIDATION / "watermark-report.json", REPORTS / "optimization-comparison.json"]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(json.loads(path.read_text())["status"] == "PASS" for path in reports) else "FAIL",
        "artifacts": [record(path) for path in artifacts], "reports": [record(path) for path in reports],
    })
    print(json.dumps({"status": json.loads((REPORTS / "build-manifest.json").read_text())["status"], "square_kit_3mf": str(square_3mf.relative_to(ROOT)), "round_kit_3mf": str(round_3mf.relative_to(ROOT)), "gauge_3mf": str(gauge_3mf.relative_to(ROOT)), "cad_volume_saved_percent": saved_pct, "meshes": meshes}, indent=2))


if __name__ == "__main__":
    main()
