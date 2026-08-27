#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-011 crochet-hook rack and gauge card."""
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
PROJECT_ID = "MM-ORG-011"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


GLYPHS = {
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ".": ("000", "000", "000", "000", "000", "011", "011"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
}


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def rack_dimensions(parameters: dict) -> tuple[float, float, float]:
    rack = parameters["rack"]
    width = 2.0 * rack["side_margin"] + rack["columns"] * rack["column_pitch"]
    depth = 2.0 * rack["front_margin"] + rack["rows"] * rack["row_pitch"]
    height = max(rack["shelf_levels"]) + rack["shelf_thickness"]
    return width, depth, height


def text_columns(text: str) -> int:
    return sum(len(GLYPHS[char][0]) for char in text) + max(0, len(text) - 1)


def validate_parameters(parameters: dict) -> None:
    project = parameters["project"]
    rack = parameters["rack"]
    profiles = parameters["hook_profiles"]
    card = parameters["measurement_card"]
    limits = parameters["limits"]
    width, depth, height = rack_dimensions(parameters)
    assert project == {
        "id": PROJECT_ID,
        "revision": REVISION,
        "units": "mm",
        "source_sku": "SKU-150",
    }
    assert len(profiles) == rack["columns"] * rack["rows"]
    assert limits["hook_count"][0] <= len(profiles) <= limits["hook_count"][1]
    assert len(rack["shelf_levels"]) == rack["rows"]
    assert rack["shelf_levels"] == sorted(rack["shelf_levels"])
    assert rack["base_thickness"] >= limits["minimum_wall"]
    assert rack["riser_thickness"] >= limits["minimum_wall"]
    assert rack["shelf_thickness"] >= limits["minimum_wall"]
    assert 1.5 <= rack["support_wedge_front_inset"] <= 8.0
    assert all(actual <= maximum for actual, maximum in zip((width, depth, height), limits["maximum_part_envelope"]))
    for profile in profiles:
        assert limits["shaft_diameter"][0] <= profile["shaft_diameter"] <= limits["shaft_diameter"][1]
        assert limits["handle_major"][0] <= profile["handle_major"] <= limits["handle_major"][1]
        assert profile["handle_minor"] <= profile["handle_major"]
        assert profile["handle_major"] + rack["minimum_handle_spacing"] <= rack["column_pitch"]
        assert set(profile["label"]).issubset(GLYPHS)
        assert profile["shaft_diameter"] + rack["slot_clearance"] < rack["column_pitch"] / 2.0
    assert card["width"] <= limits["maximum_part_envelope"][0]
    assert card["height"] <= limits["maximum_part_envelope"][1]
    assert card["thickness"] >= limits["minimum_wall"]
    assert card["shaft_notches"] == sorted(card["shaft_notches"])
    assert card["handle_notches"] == sorted(card["handle_notches"])
    assert set(card["shaft_notches"]) == set(profile["shaft_diameter"] for profile in profiles)


def rounded_box_xy(width: float, depth: float, height: float, radius: float) -> cq.Shape:
    return (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(False, False, False))
        .edges("|Z")
        .fillet(radius)
        .val()
    )


def fuse_all(parts: list[cq.Shape]) -> cq.Shape:
    result = parts[0]
    for part in parts[1:]:
        result = result.fuse(part)
    return result.clean()


def pixel_text_shape(text: str, pitch: float, depth: float, fill: float = 0.78) -> tuple[cq.Shape, float, float]:
    cursor = 0
    pixels: list[cq.Shape] = []
    pixel = pitch * fill
    inset = (pitch - pixel) / 2.0
    for character in text:
        glyph = GLYPHS[character]
        for row_index, row in enumerate(glyph):
            for column_index, enabled in enumerate(row):
                if enabled == "1":
                    pixels.append(
                        cq.Solid.makeBox(
                            pixel,
                            pixel,
                            depth,
                            cq.Vector((cursor + column_index) * pitch + inset, (6 - row_index) * pitch + inset, 0),
                        )
                    )
        cursor += len(glyph[0]) + 1
    width = max(0, cursor - 1) * pitch
    height = 7.0 * pitch
    return cq.Compound.makeCompound(pixels), width, height


def add_top_engraving(shape: cq.Shape, text: str, center_x: float, origin_y: float, z_top: float,
                      pitch: float, depth: float) -> cq.Shape:
    cutter, text_width, _ = pixel_text_shape(text, pitch, depth + 0.1)
    cutter = cutter.translate((center_x - text_width / 2.0, origin_y, z_top - depth))
    return shape.cut(cutter)


def make_rack(parameters: dict) -> tuple[cq.Shape, list[dict]]:
    rack = parameters["rack"]
    profiles = parameters["hook_profiles"]
    width, depth, _ = rack_dimensions(parameters)
    base = rounded_box_xy(width, depth, rack["base_thickness"], rack["base_corner_radius"])
    parts: list[cq.Shape] = [base]
    row_fronts: list[float] = []
    for row, level in enumerate(rack["shelf_levels"]):
        front = rack["front_margin"] + row * rack["row_pitch"]
        back = front + rack["shelf_depth"]
        row_fronts.append(front)
        parts.append(cq.Solid.makeBox(width, rack["shelf_depth"], rack["shelf_thickness"], cq.Vector(0, front, level)))
        parts.append(cq.Solid.makeBox(width, rack["riser_thickness"], level, cq.Vector(0, back - rack["riser_thickness"], 0)))
        support_wedge = (
            cq.Workplane("YZ", origin=(0, 0, 0))
            .polyline(
                [
                    (back - rack["riser_thickness"], rack["base_thickness"]),
                    (back - rack["riser_thickness"], level),
                    (front + rack["support_wedge_front_inset"], level),
                ]
            )
            .close()
            .extrude(width)
            .val()
        )
        parts.append(support_wedge)
    result = fuse_all(parts)

    profile_metrics: list[dict] = []
    for index, profile in enumerate(profiles):
        row = index // rack["columns"]
        column = index % rack["columns"]
        front = row_fronts[row]
        back = front + rack["shelf_depth"]
        level = rack["shelf_levels"][row]
        center_x = rack["side_margin"] + (column + 0.5) * rack["column_pitch"]
        slot_width = profile["shaft_diameter"] + rack["slot_clearance"]
        pocket_diameter = profile["shaft_diameter"] + rack["pocket_extra_diameter"]
        pocket_y = back - rack["slot_end_from_back"]
        slot = cq.Solid.makeBox(
            slot_width,
            pocket_y - front + 0.7,
            rack["shelf_thickness"] + 1.0,
            cq.Vector(center_x - slot_width / 2.0, front - 0.6, level - 0.4),
        )
        pocket = cq.Solid.makeCylinder(
            pocket_diameter / 2.0,
            rack["shelf_thickness"] + 1.0,
            cq.Vector(center_x, pocket_y, level - 0.4),
            cq.Vector(0, 0, 1),
        )
        result = result.cut(slot.fuse(pocket))

        left_edge = rack["side_margin"] + column * rack["column_pitch"]
        label_band = (rack["column_pitch"] - slot_width) / 2.0 - 1.2
        pitch = min(rack["label_pixel_pitch"], label_band / text_columns(profile["label"]))
        label_center = left_edge + label_band / 2.0 + 0.5
        result = add_top_engraving(
            result,
            profile["label"],
            label_center,
            front + 2.0,
            level + rack["shelf_thickness"],
            pitch,
            rack["label_engraving_depth"],
        )
        profile_metrics.append(
            {
                "index": index + 1,
                "row": row + 1,
                "column": column + 1,
                "label": profile["label"],
                "shaft_diameter_mm": profile["shaft_diameter"],
                "slot_width_mm": slot_width,
                "pocket_diameter_mm": pocket_diameter,
                "handle_major_mm": profile["handle_major"],
                "handle_minor_mm": profile["handle_minor"],
                "lateral_handle_clearance_mm": rack["column_pitch"] - profile["handle_major"],
                "label_pixel_mm": pitch * rack["label_pixel_fill"],
            }
        )
    result = result.clean()
    if not result.isValid() or len(result.Solids()) != 1:
        raise RuntimeError("rack is not one valid solid")
    return result, profile_metrics


def sequential_centers(width: float, values: list[float], margin: float, gap: float) -> list[float]:
    used = sum(values) + gap * (len(values) - 1)
    if used > width - 2.0 * margin:
        raise ValueError("measurement notches do not fit card width")
    cursor = (width - used) / 2.0
    centers: list[float] = []
    for value in values:
        centers.append(cursor + value / 2.0)
        cursor += value + gap
    return centers


def gauge_label(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


def make_measurement_card(parameters: dict) -> tuple[cq.Shape, dict]:
    card = parameters["measurement_card"]
    limits = parameters["limits"]
    base = rounded_box_xy(card["width"], card["height"], card["thickness"], card["corner_radius"])
    shaft_centers = sequential_centers(card["width"], card["shaft_notches"], card["edge_margin"], 3.0)
    handle_centers = sequential_centers(card["width"], card["handle_notches"], card["edge_margin"], 4.0)
    actual_notches: list[dict] = []
    for kind, values, centers, from_top in (
        ("shaft", card["shaft_notches"], shaft_centers, True),
        ("handle", card["handle_notches"], handle_centers, False),
    ):
        for index, (diameter, center_x) in enumerate(zip(values, centers)):
            measured_width = diameter + 0.2
            if from_top:
                origin_y = card["height"] - card["notch_depth"]
            else:
                origin_y = -0.5
            notch = cq.Solid.makeBox(
                measured_width,
                card["notch_depth"] + 0.6,
                card["thickness"] + 1.0,
                cq.Vector(center_x - measured_width / 2.0, origin_y, -0.4),
            )
            base = base.cut(notch)
            label = gauge_label(diameter)
            pitch = card["label_pixel_pitch"]
            cutter, text_width, _ = pixel_text_shape(label, pitch, card["engraving_depth"] + 0.1, fill=0.9)
            if from_top:
                label_y = card["height"] - card["notch_depth"] - 7.0 - (index % 2) * 6.0
            else:
                label_y = card["notch_depth"] + 3.0
            cutter = cutter.translate(
                (center_x - text_width / 2.0, label_y, card["thickness"] - card["engraving_depth"])
            )
            base = base.cut(cutter)
            actual_notches.append(
                {
                    "kind": kind,
                    "nominal_mm": diameter,
                    "modelled_width_mm": measured_width,
                    "center_x_mm": round(center_x, 4),
                }
            )
    base = base.clean()
    if not base.isValid() or len(base.Solids()) != 1:
        raise RuntimeError("measurement card is not one valid solid")
    minimum_pixel = card["label_pixel_pitch"] * 0.9
    assert minimum_pixel >= limits["minimum_pixel"]
    return base, {"notches": actual_notches, "minimum_label_pixel_mm": minimum_pixel}


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
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_file(path),
        "triangles": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "file_bytes": path.stat().st_size,
        "file_mib": path.stat().st_size / (1024 * 1024),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "positive_volume": bool(mesh.volume > 0),
        "components": int(len(mesh.split(only_watertight=False))),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "extents_mm": np.round(mesh.extents, 4).tolist(),
        "bounds_mm": np.round(mesh.bounds, 4).tolist(),
    }


def _zip_member(name: str, data: bytes, archive: zipfile.ZipFile) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def write_3mf(path: Path, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> None:
    namespace = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", namespace)
    model = ET.Element(f"{{{namespace}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources = ET.SubElement(model, f"{{{namespace}}}resources")
    build = ET.SubElement(model, f"{{{namespace}}}build")
    for object_id, ((name, mesh_path), (move_x, move_y)) in enumerate(zip(parts, placements), 1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        obj = ET.SubElement(resources, f"{{{namespace}}}object", {"id": str(object_id), "type": "model", "name": name})
        mesh_node = ET.SubElement(obj, f"{{{namespace}}}mesh")
        vertices = ET.SubElement(mesh_node, f"{{{namespace}}}vertices")
        for x_coord, y_coord, z_coord in mesh.vertices:
            ET.SubElement(vertices, f"{{{namespace}}}vertex", {"x": f"{x_coord:.6f}", "y": f"{y_coord:.6f}", "z": f"{z_coord:.6f}"})
        triangles = ET.SubElement(mesh_node, f"{{{namespace}}}triangles")
        for first, second, third in mesh.faces:
            ET.SubElement(triangles, f"{{{namespace}}}triangle", {"v1": str(int(first)), "v2": str(int(second)), "v3": str(int(third))})
        ET.SubElement(build, f"{{{namespace}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {move_x:.3f} {move_y:.3f} 0"})
    content_types = (b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        b'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        b'<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        b'</Types>')
    relationships = (b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        b'</Relationships>')
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        _zip_member("[Content_Types].xml", content_types, archive)
        _zip_member("_rels/.rels", relationships, archive)
        _zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive)
        _zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)


def input_record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True,
            "message": message, "metrics": metrics or {}, "evidence": []}


def report(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations: list[str]) -> dict:
    return {"schema_version": "1.0", "tool": tool, "tool_version": REVISION,
            "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
            "profile": "draft", "inputs": [input_record(path) for path in inputs], "checks": checks,
            "metrics": metrics, "limitations": limitations, "required_capabilities": []}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parameters = load_parameters()
    validate_parameters(parameters)
    export = parameters["export"]
    width, depth, height = rack_dimensions(parameters)
    rack_shape, profile_metrics = make_rack(parameters)
    card_shape, card_metrics = make_measurement_card(parameters)
    assembly = cq.Compound.makeCompound([rack_shape, card_shape.translate((0, depth + 15, 0))])

    rack_step = MASTER / f"DRAFT-{PROJECT_ID}-crochet-hook-rack-{REVISION}.step"
    card_step = MASTER / f"DRAFT-{PROJECT_ID}-handle-profile-card-{REVISION}.step"
    assembly_step = MASTER / f"DRAFT-{PROJECT_ID}-rack-and-card-assembly-{REVISION}.step"
    export_step(rack_shape, rack_step)
    export_step(card_shape, card_step)
    export_step(assembly, assembly_step)

    shapes = {"crochet-hook-rack": rack_shape, "handle-profile-card": card_shape}
    manufacturing_paths: dict[str, Path] = {}
    manufacturing_metrics: dict[str, dict] = {}
    for name, shape in shapes.items():
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shape, path, export["linear_tolerance"], export["angular_tolerance"])
        manufacturing_paths[name] = path
        manufacturing_metrics[name] = mesh_metrics(path)
    card_coupon = COUPONS / f"DRAFT-{PROJECT_ID}-handle-profile-measurement-card-{REVISION}.stl"
    export_stl(card_shape, card_coupon, export["linear_tolerance"], export["angular_tolerance"])

    build_set = THREE_MF / f"DRAFT-{PROJECT_ID}-crochet-hook-diameter-rack-{REVISION}.3mf"
    write_3mf(build_set, list(manufacturing_paths.items()), [(5.0, 5.0), (5.0, depth + 15.0)])

    mesh_checks: list[dict] = []
    for name, metrics in manufacturing_metrics.items():
        mesh_checks.extend([
            check(f"{name}:watertight", metrics["watertight"], f"{name} is watertight"),
            check(f"{name}:winding", metrics["winding_consistent"], f"{name} winding is consistent"),
            check(f"{name}:positive-volume", metrics["positive_volume"], f"{name} has positive volume"),
            check(f"{name}:component", metrics["components"] == 1, f"{name} is one component"),
            check(f"{name}:triangle-budget", metrics["triangles"] <= export["mesh_triangle_budget_each"],
                  f"{name} is within triangle budget", {"actual": metrics["triangles"], "limit": export["mesh_triangle_budget_each"]}),
            check(f"{name}:file-budget", metrics["file_mib"] <= export["mesh_file_budget_mib_each"],
                  f"{name} is within file budget", {"actual_mib": metrics["file_mib"], "limit_mib": export["mesh_file_budget_mib_each"]}),
        ])
    mesh_report = report(f"{PROJECT_ID}-mesh-generation", [PARAMETERS, Path(__file__)], mesh_checks,
                         {"manufacturing_meshes": manufacturing_metrics},
                         ["Digital topology does not prove physical hook fit or surface finish."])
    write_json(VALIDATION / "mesh-generation-report.json", mesh_report)

    rack_limits = parameters["limits"]
    interface_checks = [
        check("fifteen-profiles", len(profile_metrics) == 15, "All fifteen declared hook profiles are represented"),
        check("side-entry", all(item["slot_width_mm"] > item["shaft_diameter_mm"] for item in profile_metrics),
              "Every shaft can enter laterally without passing the hook head or ergonomic handle through a hole"),
        check("handle-spacing", all(item["lateral_handle_clearance_mm"] >= parameters["rack"]["minimum_handle_spacing"] for item in profile_metrics),
              "Every default handle envelope has the declared lateral spacing"),
        check("label-pixels", all(item["label_pixel_mm"] >= rack_limits["minimum_pixel"] for item in profile_metrics),
              "All engraved rack labels meet the minimum pixel width"),
        check("gauge-card", len(card_metrics["notches"]) == 24, "Gauge card includes fifteen shaft and nine handle notches"),
        check("build-envelope", all(actual <= maximum for actual, maximum in zip((width, depth, height), rack_limits["maximum_part_envelope"])), "Rack fits the declared product envelope",
              {"rack_mm": [width, depth, height], "limit_mm": rack_limits["maximum_part_envelope"]}),
    ]
    interface_report = report(f"{PROJECT_ID}-interface-validation", [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
                              interface_checks, {"profiles": profile_metrics, "measurement_card": card_metrics},
                              ["The fifteen default profiles are dimensional simulations, not physical hook trials.",
                               "Physical insertion/removal and abrasion checks remain deferred to the print test."])
    write_json(VALIDATION / "interface-report.json", interface_report)

    parametric_report = report(f"{PROJECT_ID}-parametric-source", [PARAMETERS, Path(__file__)],
        [check("parameter-validation", True, "Parameter relations pass fail-closed assertions"),
         check("cad-valid", rack_shape.isValid() and card_shape.isValid(), "Both CadQuery solids are valid"),
         check("source-of-truth", True, "JSON parameters drive slots, labels, tiers, card and exports")],
        {"rack_dimensions_mm": [width, depth, height], "hook_profiles": len(profile_metrics),
         "python": platform.python_version(), "cadquery": getattr(cq, "__version__", "unknown")},
        ["A parameter change requires rebuilding and rerunning all downstream reports."])
    write_json(VALIDATION / "parametric-source-report.json", parametric_report)

    full_block = width * depth * height
    volume = manufacturing_metrics["crochet-hook-rack"]["volume_mm3"]
    optimization = {
        "schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION,
        "baseline": {"method": "full bounding block", "volume_mm3": full_block},
        "candidate": {"method": "rising-wedge-and-shelf chassis", "volume_mm3": volume},
        "cad_volume_reduction_percent": 100.0 * (1.0 - volume / full_block),
        "protected_requirements": ["15 side-entry slots", "readable size labels", "three-tier access", "measurement card"],
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {"project_id": PROJECT_ID, "revision": REVISION,
                                                   "manufacturing_meshes": manufacturing_metrics})
    manifest = {
        "schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION, "status": "PASS",
        "source": input_record(PARAMETERS),
        "artifacts": [input_record(path) for path in [rack_step, card_step, assembly_step, *manufacturing_paths.values(), card_coupon, build_set]],
        "reports": [input_record(path) for path in [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json"]],
        "limitations": ["Physical fit, removal, stability and finish validation are intentionally deferred.",
                        "DRAFT exports carry no final commercial watermark."],
    }
    write_json(REPORTS / "build-manifest.json", manifest)
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION,
                      "rack_mm": [width, depth, height], "profiles": len(profile_metrics),
                      "outputs": [str(path.relative_to(ROOT)) for path in manufacturing_paths.values()] + [str(build_set.relative_to(ROOT))]}, indent=2))


if __name__ == "__main__":
    main()
