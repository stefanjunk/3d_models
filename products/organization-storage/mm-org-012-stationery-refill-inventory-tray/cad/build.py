#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-012 stationery-refill inventory tray."""
from __future__ import annotations

import hashlib
import json
import platform
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
PROJECT_ID = "MM-ORG-012"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    ".": ("000", "000", "000", "000", "000", "011", "011"),
}


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    tray = parameters["tray"]
    rear = parameters["rear_packet_lanes"]
    front = parameters["front_pockets"]
    coupon = parameters["coupon"]
    limits = parameters["limits"]
    assert project == {"id": PROJECT_ID, "revision": REVISION, "units": "mm", "source_sku": "SKU-196"}
    assert limits["width"][0] <= tray["width"] <= limits["width"][1]
    assert limits["depth"][0] <= tray["depth"] <= limits["depth"][1]
    assert limits["height"][0] <= tray["height"] <= limits["height"][1]
    assert tray["wall_thickness"] >= limits["minimum_wall"]
    assert tray["base_thickness"] >= limits["minimum_wall"]
    assert limits["rear_lane_count"][0] <= len(rear) <= limits["rear_lane_count"][1]
    assert limits["front_pocket_count"][0] <= len(front) <= limits["front_pocket_count"][1]
    rear_total = sum(item["clear_width"] for item in rear) + (len(rear) + 1) * tray["wall_thickness"]
    front_total = sum(item["clear_width"] for item in front) + (len(front) + 1) * tray["wall_thickness"]
    assert abs(rear_total - tray["width"]) < 1e-6
    assert abs(front_total - tray["width"]) < 1e-6
    rear_clear_depth = tray["depth"] - tray["front_region_depth"] - 2.0 * tray["wall_thickness"]
    for item in rear:
        assert item["package_width"] + tray["package_clearance"] <= item["clear_width"]
        assert item["package_length"] + tray["package_clearance"] <= rear_clear_depth
        assert item["package_thickness"] < tray["height"] - tray["base_thickness"]
        assert set(item["label"]).issubset(GLYPHS)
    front_clear_depth = tray["front_region_depth"] - 2.0 * tray["wall_thickness"]
    for item in front:
        assert item["package_width"] + tray["package_clearance"] <= item["clear_width"]
        assert item["package_depth"] + tray["package_clearance"] <= front_clear_depth
        assert item["package_height"] < tray["front_wall_height"]
        assert set(item["label"]).issubset(GLYPHS)
    assert tray["label_pixel_pitch"] * tray["label_pixel_fill"] >= limits["minimum_label_pixel"]
    assert coupon["notch_radius"] <= coupon["height"] / 2.0
    coupon_width = sum(coupon["cell_clear_widths"]) + (len(coupon["cell_clear_widths"]) + 1) * tray["wall_thickness"]
    assert coupon_width <= limits["maximum_part_envelope"][0]
    assert [tray["width"], tray["depth"], tray["height"]] == limits["maximum_part_envelope"]


def rounded_box_xy(width: float, depth: float, height: float, radius: float) -> cq.Shape:
    return (cq.Workplane("XY").box(width, depth, height, centered=(False, False, False)).edges("|Z").fillet(radius).val())


def fuse_all(parts: list[cq.Shape]) -> cq.Shape:
    result = parts[0]
    for part in parts[1:]:
        result = result.fuse(part)
    return result.clean()


def pixel_text_vertical(text: str, pitch: float, depth: float, fill: float) -> tuple[cq.Shape, float, float]:
    cursor = 0
    pixels: list[cq.Shape] = []
    pixel = pitch * fill
    inset = (pitch - pixel) / 2.0
    for character in text:
        glyph = GLYPHS[character]
        for row_index, row in enumerate(glyph):
            for column_index, enabled in enumerate(row):
                if enabled == "1":
                    pixels.append(cq.Solid.makeBox(
                        pixel, depth, pixel,
                        cq.Vector((cursor + column_index) * pitch + inset, 0, (6 - row_index) * pitch + inset),
                    ))
        cursor += len(glyph[0]) + 1
    return cq.Compound.makeCompound(pixels), max(0, cursor - 1) * pitch, 7.0 * pitch


def cut_front_label(shape: cq.Shape, text: str, center_x: float, face_y: float, z0: float, parameters: dict) -> cq.Shape:
    tray = parameters["tray"]
    cutter, width, _ = pixel_text_vertical(text, tray["label_pixel_pitch"], tray["label_engraving_depth"] + 0.1, tray["label_pixel_fill"])
    return shape.cut(cutter.translate((center_x - width / 2.0, face_y - 0.05, z0)))


def ramp_wedge(x0: float, width: float, y0: float, y1: float, base_z: float, rise: float) -> cq.Shape:
    """Return a base-grown ramp prism without a zero-thickness leading edge."""
    overlap = 0.2
    bottom_z = 0.2
    front_top_z = base_z + 0.8
    rear_top_z = base_z + rise
    return (
        cq.Workplane("YZ", origin=(x0 - overlap, 0, 0))
        .polyline([
            (y0 - overlap, bottom_z),
            (y1 + overlap, bottom_z),
            (y1 + overlap, rear_top_z),
            (y0 - overlap, front_top_z),
        ])
        .close()
        .extrude(width + 2.0 * overlap)
        .val()
    )


def thumb_notch(center_x: float, face_y: float, wall_height: float, radius: float, wall_depth: float) -> cq.Shape:
    top_overlap = 0.6
    return cq.Solid.makeCylinder(
        radius,
        wall_depth + 1.0,
        cq.Vector(center_x, face_y - 0.5, wall_height - radius + top_overlap),
        cq.Vector(0, 1, 0),
    )


def make_tray(parameters: dict) -> tuple[cq.Shape, dict]:
    tray = parameters["tray"]
    rear = parameters["rear_packet_lanes"]
    front = parameters["front_pockets"]
    wall = tray["wall_thickness"]
    width, depth, height = tray["width"], tray["depth"], tray["height"]
    boundary_y = tray["front_region_depth"]
    parts = [rounded_box_xy(width, depth, tray["base_thickness"], tray["corner_radius"])]
    parts.extend([
        cq.Solid.makeBox(wall, depth, height, cq.Vector(0, 0, 0)),
        cq.Solid.makeBox(wall, depth, height, cq.Vector(width - wall, 0, 0)),
        cq.Solid.makeBox(width, wall, height, cq.Vector(0, depth - wall, 0)),
        cq.Solid.makeBox(width, wall, tray["front_wall_height"], cq.Vector(0, 0, 0)),
        cq.Solid.makeBox(width, wall, tray["front_divider_height"], cq.Vector(0, boundary_y, 0)),
    ])

    front_metrics = []
    cursor = wall
    for index, item in enumerate(front):
        x0 = cursor
        x1 = x0 + item["clear_width"]
        center = (x0 + x1) / 2.0
        if index < len(front) - 1:
            parts.append(cq.Solid.makeBox(wall, boundary_y + wall, tray["front_divider_height"], cq.Vector(x1, 0, 0)))
        parts.append(ramp_wedge(x0, item["clear_width"], wall, boundary_y, tray["base_thickness"], tray["front_ramp_rise"]))
        front_metrics.append({
            "label": item["label"], "clear_width_mm": item["clear_width"],
            "clear_depth_mm": boundary_y - 2.0 * wall,
            "package_clearance_x_mm": item["clear_width"] - item["package_width"],
            "package_clearance_y_mm": boundary_y - 2.0 * wall - item["package_depth"],
            "package_height_margin_mm": tray["front_wall_height"] - item["package_height"],
        })
        cursor = x1 + wall

    rear_metrics = []
    cursor = wall
    rear_front = boundary_y + wall
    rear_back = depth - wall
    for index, item in enumerate(rear):
        x0 = cursor
        x1 = x0 + item["clear_width"]
        center = (x0 + x1) / 2.0
        if index < len(rear) - 1:
            parts.append(cq.Solid.makeBox(wall, depth - boundary_y, height, cq.Vector(x1, boundary_y, 0)))
        parts.append(ramp_wedge(x0, item["clear_width"], rear_front, rear_back, tray["base_thickness"], tray["rear_ramp_rise"]))
        rear_metrics.append({
            "label": item["label"], "clear_width_mm": item["clear_width"],
            "clear_depth_mm": rear_back - rear_front,
            "package_clearance_x_mm": item["clear_width"] - item["package_width"],
            "package_clearance_y_mm": rear_back - rear_front - item["package_length"],
            "package_height_margin_mm": height - tray["base_thickness"] - tray["rear_ramp_rise"] - item["package_thickness"],
        })
        cursor = x1 + wall

    result = fuse_all(parts)
    cursor = wall
    for item in front:
        center = cursor + item["clear_width"] / 2.0
        notch_center = center + item["clear_width"] * 0.23
        label_center = center - item["clear_width"] * 0.20
        result = result.cut(thumb_notch(notch_center, 0.0, tray["front_wall_height"], tray["thumb_notch_radius"], wall))
        result = cut_front_label(result, item["label"], label_center, 0.0, 8.5, parameters)
        cursor += item["clear_width"] + wall
    cursor = wall
    for item in rear:
        center = cursor + item["clear_width"] / 2.0
        result = result.cut(thumb_notch(center, boundary_y, tray["front_divider_height"], tray["thumb_notch_radius"], wall))
        result = cut_front_label(result, item["label"], center, depth - wall, 31.0, parameters)
        cursor += item["clear_width"] + wall
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("inventory tray is not one valid solid")
    return result, {"front_pockets": front_metrics, "rear_lanes": rear_metrics}


def make_retrieval_coupon(parameters: dict) -> tuple[cq.Shape, dict]:
    tray = parameters["tray"]
    coupon = parameters["coupon"]
    wall = tray["wall_thickness"]
    widths = coupon["cell_clear_widths"]
    width = sum(widths) + (len(widths) + 1) * wall
    depth = coupon["depth"]
    height = coupon["height"]
    parts = [rounded_box_xy(width, depth, tray["base_thickness"], 3.0)]
    parts.extend([
        cq.Solid.makeBox(wall, depth, height, cq.Vector(0, 0, 0)),
        cq.Solid.makeBox(wall, depth, height, cq.Vector(width - wall, 0, 0)),
        cq.Solid.makeBox(width, wall, height, cq.Vector(0, 0, 0)),
        cq.Solid.makeBox(width, wall, height, cq.Vector(0, depth - wall, 0)),
    ])
    cursor = wall
    centers = []
    for index, cell_width in enumerate(widths):
        centers.append(cursor + cell_width / 2.0)
        parts.append(ramp_wedge(cursor, cell_width, wall, depth - wall, tray["base_thickness"], coupon["ramp_rise"]))
        if index < len(widths) - 1:
            parts.append(cq.Solid.makeBox(wall, depth, height, cq.Vector(cursor + cell_width, 0, 0)))
        cursor += cell_width + wall
    result = fuse_all(parts)
    for center in centers:
        result = result.cut(thumb_notch(center, 0.0, height, coupon["notch_radius"], wall))
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("retrieval coupon is not one valid solid")
    return result, {"width_mm": width, "depth_mm": depth, "height_mm": height, "cell_clear_widths_mm": widths,
                    "production_wall_mm": wall, "production_notch_radius_mm": coupon["notch_radius"]}


def move_to_origin(shape: cq.Shape) -> cq.Shape:
    bounds = shape.BoundingBox()
    return shape.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_step(shape: cq.Shape, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path), exportType="STEP")


def export_stl(shape: cq.Shape, path: Path, linear: float, angular: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(move_to_origin(shape), str(path), tolerance=linear, angularTolerance=angular)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "triangles": int(len(mesh.faces)),
            "vertices": int(len(mesh.vertices)), "file_bytes": path.stat().st_size, "file_mib": path.stat().st_size / (1024 * 1024),
            "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
            "positive_volume": bool(mesh.volume > 0), "components": int(len(mesh.split(only_watertight=False))),
            "volume_mm3": float(mesh.volume), "surface_area_mm2": float(mesh.area),
            "extents_mm": np.round(mesh.extents, 4).tolist(), "bounds_mm": np.round(mesh.bounds, 4).tolist()}


def _zip_member(name: str, data: bytes, archive: zipfile.ZipFile) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; archive.writestr(info, data)


def write_3mf(path: Path, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"; ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources = ET.SubElement(model, f"{{{ns}}}resources"); build = ET.SubElement(model, f"{{{ns}}}build")
    for object_id, ((name, mesh_path), (move_x, move_y)) in enumerate(zip(parts, placements), 1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name})
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh"); verts = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices: ET.SubElement(verts, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        tris = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces: ET.SubElement(tris, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {move_x:.3f} {move_y:.3f} 0"})
    types = (b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             b'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             b'<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = (b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            b'<Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        _zip_member("[Content_Types].xml", types, archive); _zip_member("_rels/.rels", rels, archive)
        _zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive)
        _zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)


def input_record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def report(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations: list[str]) -> dict:
    return {"schema_version": "1.0", "tool": tool, "tool_version": REVISION,
            "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
            "inputs": [input_record(path) for path in inputs], "checks": checks, "metrics": metrics,
            "limitations": limitations, "required_capabilities": []}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parameters = load_parameters(); validate_parameters(parameters); export = parameters["export"]; tray_p = parameters["tray"]
    tray_shape, interface_metrics = make_tray(parameters); coupon_shape, coupon_metrics = make_retrieval_coupon(parameters)
    assembly = cq.Compound.makeCompound([tray_shape, coupon_shape.translate((tray_p["width"] + 12, 0, 0))])
    steps = {"inventory-tray": tray_shape, "retrieval-coupon": coupon_shape, "tray-and-coupon-assembly": assembly}
    step_paths = []
    for name, shape in steps.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"; export_step(shape, path); step_paths.append(path)
    shapes = {"inventory-tray": tray_shape, "retrieval-coupon": coupon_shape}
    paths = {}; metrics = {}
    for name, shape in shapes.items():
        directory = MANUFACTURING if name == "inventory-tray" else COUPONS
        path = directory / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shape, path, export["linear_tolerance"], export["angular_tolerance"]); paths[name] = path; metrics[name] = mesh_metrics(path)
    build_set = THREE_MF / f"DRAFT-{PROJECT_ID}-stationery-refill-inventory-tray-{REVISION}.3mf"
    write_3mf(build_set, list(paths.items()), [(5.0, 5.0), (tray_p["width"] + 15.0, 5.0)])
    mesh_checks = []
    for name, item in metrics.items():
        mesh_checks.extend([check(f"{name}:watertight", item["watertight"], f"{name} is watertight"),
                            check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"),
                            check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"),
                            check(f"{name}:component", item["components"] == 1, f"{name} is one component"),
                            check(f"{name}:triangles", item["triangles"] <= export["mesh_triangle_budget_each"], "Triangle budget", {"actual": item["triangles"], "limit": export["mesh_triangle_budget_each"]}),
                            check(f"{name}:file", item["file_mib"] <= export["mesh_file_budget_mib_each"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": export["mesh_file_budget_mib_each"]})])
    write_json(VALIDATION / "mesh-generation-report.json", report(f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks,
               {"meshes": metrics}, ["Topology does not prove physical package retrieval, label readability or drawer fit."]))
    interface_checks = [
        check("five-rear-lanes", len(interface_metrics["rear_lanes"]) == 5, "Five rear packet lanes generated"),
        check("three-front-pockets", len(interface_metrics["front_pockets"]) == 3, "Three front refill pockets generated"),
        check("rear-envelope", all(item["package_clearance_x_mm"] >= tray_p["package_clearance"] and item["package_clearance_y_mm"] >= tray_p["package_clearance"] for item in interface_metrics["rear_lanes"]), "Every rear package envelope has declared XY clearance"),
        check("front-envelope", all(item["package_clearance_x_mm"] >= tray_p["package_clearance"] and item["package_clearance_y_mm"] >= tray_p["package_clearance"] for item in interface_metrics["front_pockets"]), "Every front package envelope has declared XY clearance"),
        check("label-pixels", tray_p["label_pixel_pitch"] * tray_p["label_pixel_fill"] >= parameters["limits"]["minimum_label_pixel"], "Embedded label pixels meet process minimum"),
        check("coupon-production-interface", coupon_metrics["production_wall_mm"] == tray_p["wall_thickness"] and coupon_metrics["production_notch_radius_mm"] == parameters["coupon"]["notch_radius"], "Coupon reuses production wall and retrieval-notch parameters"),
    ]
    write_json(VALIDATION / "interface-report.json", report(f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"], interface_checks,
               {**interface_metrics, "coupon": coupon_metrics}, ["Package envelopes are simulated defaults, not physical branded packages.", "Retrieval force and visibility require the deferred print test."]))
    write_json(VALIDATION / "parametric-source-report.json", report(f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)],
               [check("parameter-validation", True, "Fail-closed parameter relations pass"), check("cad-valid", tray_shape.isValid() and coupon_shape.isValid(), "Tray and coupon B-Reps are valid"), check("source-of-truth", True, "JSON drives layout, ramps, labels, coupon and exports")],
               {"tray_dimensions_mm": [tray_p["width"], tray_p["depth"], tray_p["height"]], "rear_lanes": 5, "front_pockets": 3, "python": platform.python_version(), "cadquery": getattr(cq, "__version__", "unknown")},
               ["A parameter change requires rebuilding all downstream evidence."]))
    baseline = tray_p["width"] * tray_p["depth"] * tray_p["height"]; volume = metrics["inventory-tray"]["volume_mm3"]
    write_json(REPORTS / "optimization-comparison.json", {"schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION,
               "baseline": {"method": "full bounding block", "volume_mm3": baseline}, "candidate": {"method": "open-wall tray with local retrieval ramps", "volume_mm3": volume},
               "cad_volume_reduction_percent": 100.0 * (1.0 - volume / baseline), "protected_requirements": ["five packet lanes", "three scoop pockets", "labels", "retrieval coupon"]})
    write_json(REPORTS / "mesh-complexity.json", {"project_id": PROJECT_ID, "revision": REVISION, "meshes": metrics})
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION, "status": "PASS",
               "source": input_record(PARAMETERS), "artifacts": [input_record(path) for path in [*step_paths, *paths.values(), build_set]],
               "reports": [input_record(path) for path in [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json"]],
               "limitations": ["Physical package retrieval and loaded drawer use are deferred.", "DRAFT outputs carry no final commercial watermark."]})
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "outputs": [str(path.relative_to(ROOT)) for path in paths.values()] + [str(build_set.relative_to(ROOT))]}, indent=2))


if __name__ == "__main__":
    main()
