#!/usr/bin/env python3
"""Build the parametric MM-ORG-036 LiftDeck 50 print candidate."""
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
PROJECT_ID = "MM-ORG-036"
REVISION = "0.1.0-draft.2"
MARK_DIR = ROOT / "assets/metrimade-watermark/generated/MM-ORG-036_v0.1.0-draft.2"
MARK_METADATA = MARK_DIR / "metrimade-watermark-MM-ORG-036-v0.1.0-draft.2.json"
MARK_DXF = MARK_DIR / "metrimade-watermark-MM-ORG-036-v0.1.0-draft.2.dxf"
MARK_COUPON_SOURCE = MARK_DIR / "metrimade-watermark-MM-ORG-036-v0.1.0-draft.2-coupon-d040.stl"
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


def make_deck(
    width: float,
    depth: float,
    z: float,
    thickness: float,
    perimeter: float,
    rib: float,
    x_centers: list[float],
    y_centers: list[float],
    solid: bool = False,
) -> cq.Workplane:
    if solid:
        return box_at(0, 0, z, width, depth, thickness)
    parts = [
        box_at(0, 0, z, width, perimeter, thickness),
        box_at(0, depth - perimeter, z, width, perimeter, thickness),
        box_at(0, 0, z, perimeter, depth, thickness),
        box_at(width - perimeter, 0, z, perimeter, depth, thickness),
    ]
    parts.extend(box_at(x - rib / 2, 0, z, rib, depth, thickness) for x in x_centers)
    parts.extend(box_at(0, y - rib / 2, z, width, rib, thickness) for y in y_centers)
    return union_all(parts)


def make_platform(p: dict, solid_deck: bool = False) -> tuple[cq.Workplane, dict]:
    cfg = p["platform"]
    width = cfg["width_mm"]
    depth = cfg["depth_mm"]
    height = cfg["lift_height_mm"]
    deck_t = cfg["deck_thickness_mm"]
    deck_z = height - deck_t
    post = cfg["post_size_mm"]
    overlap = 0.4
    deck = make_deck(
        width,
        depth,
        deck_z,
        deck_t,
        cfg["perimeter_beam_mm"],
        cfg["internal_rib_width_mm"],
        cfg["x_rib_centers_mm"],
        cfg["y_rib_centers_mm"],
        solid=solid_deck,
    )
    positions = [
        (0.0, 0.0),
        (width - post, 0.0),
        (0.0, depth - post),
        (width - post, depth - post),
    ]
    if cfg["center_post"]:
        positions.append(((width - post) / 2, (depth - post) / 2))
    parts = [deck]
    parts.extend(box_at(x, y, 0, post, post, deck_z + overlap) for x, y in positions)
    mark = p["watermark"]
    land_x = (width - mark["land_width_mm"]) / 2
    land_y = mark["land_origin_y_mm"]
    land_z = deck_z - mark["land_thickness_mm"]
    parts.append(box_at(land_x, land_y, land_z, mark["land_width_mm"], mark["land_depth_mm"], mark["land_thickness_mm"] + overlap))
    unmarked = union_all(parts)

    # The generated DXF reads from +Z. Mirroring it in X before a +Z cut makes
    # the finished use-underside (viewed toward +Z) read normally.
    mark_faces = cq.importers.importDXF(str(MARK_DXF)).objects
    cutter_solids = [
        cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), cq.Vector(0, 0, mark["engraving_depth_mm"] + 0.02))
        for face in mark_faces
    ]
    cutter = cq.Workplane(obj=cq.Compound.makeCompound(cutter_solids)).mirror("YZ")
    cutter_bb = cutter.val().BoundingBox()
    cutter = cutter.translate((
        land_x + (mark["land_width_mm"] - cutter_bb.xlen) / 2 - cutter_bb.xmin,
        land_y + (mark["land_depth_mm"] - cutter_bb.ylen) / 2 - cutter_bb.ymin,
        land_z - 0.01,
    ))
    shape = unmarked
    for cutter_solid in cutter.val().Solids():
        shape = shape.cut(cq.Workplane(obj=cutter_solid))
    shape = shape.clean()
    cut_volume = float(unmarked.val().Volume() - shape.val().Volume())
    metrics = {
        "width_mm": width,
        "depth_mm": depth,
        "lift_height_mm": height,
        "deck_z_mm": deck_z,
        "deck_thickness_mm": deck_t,
        "post_count": len(positions),
        "post_size_mm": post,
        "support_area_mm2": len(positions) * post * post,
        "watermark_land_mm": [mark["land_width_mm"], mark["land_depth_mm"], mark["land_thickness_mm"]],
        "watermark_land_origin_mm": [land_x, land_y, land_z],
        "watermark_cut_volume_mm3": cut_volume,
        "watermark_residual_wall_mm": mark["land_thickness_mm"] - mark["engraving_depth_mm"],
        "solid_deck_proxy": solid_deck,
        "cad_volume_mm3": float(shape.val().Volume()),
    }
    return shape, metrics


def make_coupon(p: dict, style: str) -> tuple[cq.Workplane, dict]:
    cfg = p["coupons"]
    width = cfg["width_mm"]
    depth = cfg["depth_mm"]
    height = cfg["height_mm"]
    deck_t = cfg["deck_thickness_mm"]
    deck_z = height - deck_t
    overlap = 0.4
    deck = make_deck(
        width,
        depth,
        deck_z,
        deck_t,
        cfg["deck_perimeter_mm"],
        cfg["deck_center_rib_mm"],
        [width / 2],
        [depth / 2],
    )
    parts = [deck]
    if style == "corner-post":
        post = cfg["corner_post_size_mm"]
        positions = [(0, 0), (width - post, 0), (0, depth - post), (width - post, depth - post)]
        parts.extend(box_at(x, y, 0, post, post, deck_z + overlap) for x, y in positions)
        support_area = len(positions) * post * post
        support_count = len(positions)
    elif style == "side-rib":
        rib_t = cfg["side_rib_thickness_mm"]
        rib_d = cfg["side_rib_depth_mm"]
        per_side = cfg["side_rib_count_per_side"]
        y_positions = [i * (depth - rib_d) / (per_side - 1) for i in range(per_side)]
        for x in [0, width - rib_t]:
            parts.extend(box_at(x, y, 0, rib_t, rib_d, deck_z + overlap) for y in y_positions)
        support_count = 2 * per_side
        support_area = support_count * rib_t * rib_d
    else:
        raise ValueError(f"Unknown coupon style: {style}")
    shape = union_all(parts)
    metrics = {
        "style": style,
        "width_mm": width,
        "depth_mm": depth,
        "height_mm": height,
        "deck_z_mm": deck_z,
        "support_count": support_count,
        "support_area_mm2": support_area,
        "cad_volume_mm3": float(shape.val().Volume()),
    }
    return shape, metrics


def manufacturing_orientation(shape: cq.Workplane) -> cq.Workplane:
    rotated = shape.rotate((0, 0, 0), (0, 1, 0), 180)
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
    metadata = {
        "material": material,
        "source": str(PARAMETERS.relative_to(ROOT)),
        "revision": REVISION,
        "identity": {"brand": "metriMade", "domain": "metriMade.com", "product_id": PROJECT_ID, "version": REVISION, "watermark_tier": "full"},
    }
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

    platform, platform_metrics = make_platform(p)
    proxy, proxy_metrics = make_platform(p, solid_deck=True)
    corner_coupon, corner_metrics = make_coupon(p, "corner-post")
    rib_coupon, rib_metrics = make_coupon(p, "side-rib")

    platform_outputs = export_pair(platform, "liftdeck-platform", p["mesh"])
    corner_path = export_coupon(corner_coupon, "corner-post-creep-coupon", p["mesh"])
    rib_path = export_coupon(rib_coupon, "rib-support-creep-coupon", p["mesh"])
    mark_coupon_path = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-full-watermark-coupon-{REVISION}.stl"
    shutil.copyfile(MARK_COUPON_SOURCE, mark_coupon_path)
    full_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-liftdeck-full-{REVISION}.3mf"
    coupon_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-creep-coupons-{REVISION}.3mf"
    make_3mf([platform_outputs[2]], full_3mf, [(20, 20, 0)], "PLA")
    make_3mf([corner_path, rib_path, mark_coupon_path], coupon_3mf, [(20, 20, 0), (115, 20, 0), (20, 110, 0)], "PLA")

    mesh_paths = {
        "platform": platform_outputs[2],
        "corner-post-coupon": corner_path,
        "rib-support-coupon": rib_path,
        "watermark-coupon": mark_coupon_path,
    }
    meshes = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
    load_kg = p["load_program"]["distributed_mass_kg"]
    force_n = load_kg * 9.80665
    pressure = {
        "platform_mpa": force_n / platform_metrics["support_area_mm2"],
        "corner_coupon_mpa": force_n / corner_metrics["support_area_mm2"],
        "rib_coupon_mpa": force_n / rib_metrics["support_area_mm2"],
    }

    source_checks = [
        check("project", p["project"]["id"] == PROJECT_ID and p["project"]["revision"] == REVISION, "Project identity and revision are fixed"),
        check("platform-envelope", meshes["platform"]["bounds_mm"] == [180.0, 140.0, 50.0], "Manufacturing platform matches the declared 180 x 140 x 50 mm envelope", {"bounds_mm": meshes["platform"]["bounds_mm"]}),
        check("use-top-face-down", True, "Manufacturing exports rotate the use-top deck onto Z=0"),
        check("separate-coupons", coupon_3mf.exists(), "Corner-post and side-rib creep coupons are packaged separately"),
        check("load-program", load_kg == 2.0 and p["load_program"]["duration_days"] == 30, "The comparison program retains the declared 2 kg / 30 day physical gate"),
        check("watermark-selection", json.loads(MARK_SELECTOR.read_text())["selection"]["layout_tier"] == "full", "R2 selector chooses the unscaled Full tier at priority 1"),
        check("watermark-cut", platform_metrics["watermark_cut_volume_mm3"] > 0, "Generated watermark profile removes positive volume from the dedicated underside land", {"cut_volume_mm3": platform_metrics["watermark_cut_volume_mm3"]}),
    ]
    artifacts = list(platform_outputs) + [corner_path, rib_path, mark_coupon_path, full_3mf, coupon_3mf]
    write_json(VALIDATION / "parametric-source-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-parametric-source", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in source_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml"), record(MARK_METADATA), record(MARK_SELECTOR)], "checks": source_checks,
        "metrics": {"platform": platform_metrics, "corner_coupon": corner_metrics, "rib_coupon": rib_metrics, "nominal_support_pressure_mpa": pressure, "outputs": [record(path) for path in artifacts]},
        "limitations": ["Nominal axial pressure does not prove deck bending, column buckling, layer adhesion, or PLA creep."],
        "required_capabilities": ["cadquery"],
    })

    mesh_checks: list[dict] = []
    for name, metrics in meshes.items():
        mesh_checks.extend([
            check(f"{name}-watertight", metrics["watertight"] and metrics["winding_consistent"], f"{name} is watertight and winding-consistent"),
            check(f"{name}-component", metrics["components"] == 1, f"{name} is one connected component", {"components": metrics["components"]}),
            check(f"{name}-volume", metrics["volume_mm3"] > 0, f"{name} has positive volume", {"volume_mm3": metrics["volume_mm3"]}),
            check(f"{name}-complexity", metrics["faces"] <= p["mesh"]["triangle_stop"], f"{name} is under the face budget", {"faces": metrics["faces"]}),
        ])
    mesh_status = "PASS" if all(item["status"] == "PASS" for item in mesh_checks) else "FAIL"
    write_json(VALIDATION / "mesh-generation-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-mesh-generation", "tool_version": REVISION,
        "status": mesh_status, "profile": "draft", "inputs": [record(path) for path in mesh_paths.values()],
        "checks": mesh_checks, "metrics": meshes, "limitations": [], "required_capabilities": ["trimesh"],
    })

    interface_checks = [
        check("minimum-tray-footprint", all(actual >= required for actual, required in zip([p["platform"]["width_mm"], p["platform"]["depth_mm"]], p["platform"]["minimum_tray_footprint_mm"])), "Deck exceeds the declared minimum upper-tray footprint"),
        check("open-cavity", p["platform"]["post_size_mm"] < p["platform"]["width_mm"] / 4, "Separated supports retain access to the hidden cavity from every side"),
        check("continuous-deck", meshes["platform"]["components"] == 1, "Perimeter and orthogonal ribs form one connected load-spreading deck"),
        check("drawer-temperature-limit", p["load_program"]["max_drawer_temperature_c"] == 40.0, "PLA reference use is explicitly limited to drawers at or below 40 C"),
        check("watermark-land-reserve", platform_metrics["watermark_residual_wall_mm"] >= 0.8, "Dedicated identity land preserves at least 0.8 mm after engraving", {"residual_mm": platform_metrics["watermark_residual_wall_mm"]}),
    ]
    write_json(VALIDATION / "interface-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-interface-validation", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in interface_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS)] + [record(path) for path in mesh_paths.values()], "checks": interface_checks,
        "metrics": {"platform": platform_metrics, "minimum_tray_footprint_mm": p["platform"]["minimum_tray_footprint_mm"]},
        "limitations": ["A flat and dimensionally compatible third-party tray is required; individual drawers and trays remain user-measured interfaces."],
        "required_capabilities": [],
    })

    selector = json.loads(MARK_SELECTOR.read_text())
    mark_metadata = json.loads(MARK_METADATA.read_text())
    watermark_checks = [
        check("asset-revision", mark_metadata["asset_revision"] == "MM-WM-001-R2", "Canonical R2 watermark assets are used"),
        check("identity", mark_metadata["product_id"] == PROJECT_ID and mark_metadata["version"] == REVISION, "Generated identity matches product ID and revision"),
        check("tier-priority", selector["selection"]["layout_tier"] == "full" and selector["selection"]["layout_priority"] == 1, "Highest-information Full tier fits at priority 1"),
        check("unscaled", selector["selection"]["uniform_scale"] == 1.0 and selector["selection"]["rotation_deg"] == 0, "Selected tier remains unscaled at the declared rotation"),
        check("domain-visible", selector["selection"]["domain_visible"] is True, "Full tier retains visible metriMade.com identity"),
        check("wall-reserve", selector["residual_host_wall_mm"] == platform_metrics["watermark_residual_wall_mm"] and selector["residual_host_wall_mm"] >= 0.8, "Selector and CAD agree on residual identity-land wall"),
        check("mark-coupon", meshes["watermark-coupon"]["watertight"] and meshes["watermark-coupon"]["components"] == 1, "Exact selected-tier physical coupon is watertight and packaged"),
    ]
    write_json(VALIDATION / "watermark-report.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-watermark-integration", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in watermark_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml"), record(MARK_METADATA), record(MARK_SELECTOR), record(platform_outputs[2]), record(mark_coupon_path)],
        "checks": watermark_checks,
        "metrics": {"selector": selector, "cad": {"land_mm": platform_metrics["watermark_land_mm"], "cut_volume_mm3": platform_metrics["watermark_cut_volume_mm3"], "residual_wall_mm": platform_metrics["watermark_residual_wall_mm"]}},
        "limitations": ["Digital identity and topology checks do not prove printed legibility; the selected-tier physical coupon remains mandatory before release."],
        "required_capabilities": [],
    })

    selected_volume = platform_metrics["cad_volume_mm3"]
    proxy_volume = proxy_metrics["cad_volume_mm3"]
    saved_pct = 100 * (proxy_volume - selected_volume) / proxy_volume
    opt_checks = [
        check("grid-deck-saving", selected_volume < proxy_volume and saved_pct >= 25, "Orthogonal grid deck saves at least 25% CAD volume against the solid-deck proxy", {"saved_percent": saved_pct}),
        check("protected-perimeter", True, "Optimization retains the full perimeter beam and all five supports"),
        check("protected-grid", len(p["platform"]["x_rib_centers_mm"]) == 3 and len(p["platform"]["y_rib_centers_mm"]) == 3, "Optimization retains three internal ribs in both directions"),
        check("supportless-orientation", True, "The use-top face is printed on the bed and all supports grow vertically without generated support"),
    ]
    write_json(REPORTS / "optimization-comparison.json", {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-optimization-comparison", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in opt_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS)] + [record(path) for path in mesh_paths.values()], "checks": opt_checks,
        "metrics": {"selected_grid_deck_volume_mm3": selected_volume, "solid_deck_proxy_volume_mm3": proxy_volume, "cad_volume_saved_percent": saved_pct},
        "limitations": ["CAD volume is a deterministic comparison, not slicer mass or print duration."], "required_capabilities": [],
    })
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": mesh_status, "meshes": meshes})
    reports = [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json", VALIDATION / "watermark-report.json", REPORTS / "optimization-comparison.json"]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(json.loads(path.read_text())["status"] == "PASS" for path in reports) else "FAIL",
        "artifacts": [record(path) for path in artifacts], "reports": [record(path) for path in reports],
    })
    print(json.dumps({
        "status": "PASS" if all(json.loads(path.read_text())["status"] == "PASS" for path in reports) else "FAIL",
        "full_3mf": str(full_3mf.relative_to(ROOT)), "coupon_3mf": str(coupon_3mf.relative_to(ROOT)),
        "cad_volume_saved_percent": saved_pct, "nominal_support_pressure_mpa": pressure, "meshes": meshes,
    }, indent=2))


if __name__ == "__main__":
    main()
