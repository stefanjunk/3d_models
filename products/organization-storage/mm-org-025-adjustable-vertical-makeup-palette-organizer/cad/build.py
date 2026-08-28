#!/usr/bin/env python3
"""Build the fully parametric MM-ORG-025 PaletteGrid family."""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
PROJECT_ID = "MM-ORG-025"
REVISION = "0.1.0-draft.1"
MASTER = ROOT / "exports/master"
MANUFACTURING = ROOT / "exports/manufacturing"
COUPONS = ROOT / "exports/coupons"
THREE_MF = ROOT / "exports/3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


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


def rounded_plate(width: float, depth: float, thickness: float, radius: float) -> cq.Shape:
    return (
        cq.Workplane("XY")
        .box(width, depth, thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(radius)
        .val()
    )


def slot_positions(parameters: dict) -> list[float]:
    base = parameters["base"]
    return [(index - (base["slot_count"] - 1) / 2.0) * base["slot_pitch_mm"] for index in range(base["slot_count"])]


def compartment_clearances(parameters: dict) -> list[float]:
    divider = parameters["divider"]
    pitch = parameters["base"]["slot_pitch_mm"]
    indices = divider["default_slot_indices"]
    return [round((right - left) * pitch - divider["thickness_mm"], 3) for left, right in zip(indices, indices[1:])]


def make_base(parameters: dict) -> tuple[cq.Shape, dict]:
    base = parameters["base"]
    width = base["width_mm"]
    depth = base["depth_mm"]
    height = base["rail_height_mm"]
    rail_y = depth / 2.0 - base["rail_depth_mm"] / 2.0
    front = rounded_plate(width, base["rail_depth_mm"], height, base["corner_radius_mm"]).translate((0.0, -rail_y, 0.0))
    rear = rounded_plate(width, base["rail_depth_mm"], height, base["corner_radius_mm"]).translate((0.0, rail_y, 0.0))
    middle = rounded_plate(width, base["middle_rail_depth_mm"], height, base["corner_radius_mm"])
    side_x = width / 2.0 - base["side_rail_width_mm"] / 2.0
    left = rounded_plate(base["side_rail_width_mm"], depth, base["side_rail_height_mm"], 1.5).translate((-side_x, 0.0, 0.0))
    right = left.translate((2.0 * side_x, 0.0, 0.0))
    shape = front.fuse(rear).fuse(middle).fuse(left).fuse(right)
    for x in slot_positions(parameters):
        for y in (-rail_y, rail_y):
            cutter = (
                cq.Workplane("XY")
                .box(base["slot_width_mm"], base["slot_length_mm"], height + 2.0, centered=(True, True, False))
                .translate((x, y, -1.0))
                .val()
            )
            shape = shape.cut(cutter)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("base is not one valid solid")
    bounds = shape.BoundingBox()
    return shape, {
        "part_id": "palette-grid-base",
        "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
        "slot_positions_x_mm": slot_positions(parameters),
        "slot_width_mm": base["slot_width_mm"],
        "slot_length_mm": base["slot_length_mm"],
        "default_divider_indices": parameters["divider"]["default_slot_indices"],
        "default_compartment_clear_mm": compartment_clearances(parameters),
        "print_orientation": "rails_on_bed",
        "external_assets": [],
    }


def make_divider(parameters: dict) -> tuple[cq.Shape, dict]:
    divider = parameters["divider"]
    panel = rounded_plate(
        divider["panel_depth_mm"],
        divider["panel_height_mm"],
        divider["thickness_mm"],
        divider["edge_radius_mm"],
    ).translate((0.0, divider["foot_depth_mm"] + divider["panel_height_mm"] / 2.0, 0.0))
    window = rounded_plate(
        divider["window_depth_mm"],
        divider["window_height_mm"],
        divider["thickness_mm"] + 2.0,
        divider["window_radius_mm"],
    ).translate((0.0, divider["foot_depth_mm"] + divider["panel_height_mm"] / 2.0, -1.0))
    shape = panel.cut(window)
    for x in (-divider["foot_center_y_mm"], divider["foot_center_y_mm"]):
        foot = (
            cq.Workplane("XY")
            .box(divider["foot_length_mm"], divider["foot_depth_mm"], divider["thickness_mm"], centered=(True, True, False))
            .translate((x, divider["foot_depth_mm"] / 2.0, 0.0))
            .val()
        )
        shape = shape.fuse(foot)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("divider is not one valid solid")
    bounds = shape.BoundingBox()
    return shape, {
        "part_id": "removable-divider",
        "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
        "tongue_thickness_mm": divider["thickness_mm"],
        "tongue_length_mm": divider["foot_length_mm"],
        "tongue_depth_mm": divider["foot_depth_mm"],
        "installed_height_above_base_mm": divider["panel_height_mm"],
        "print_orientation": "broad_face_down",
        "external_assets": [],
    }


def make_slot_gauge(parameters: dict) -> tuple[cq.Shape, dict]:
    coupon = parameters["coupon"]
    shape = rounded_plate(coupon["gauge_width_mm"], coupon["gauge_depth_mm"], coupon["gauge_height_mm"], 2.0)
    for station, (x, width) in enumerate(zip(coupon["station_centers_x_mm"], coupon["candidate_slot_widths_mm"]), 1):
        cutter = (
            cq.Workplane("XY")
            .box(width, parameters["base"]["slot_length_mm"], coupon["gauge_height_mm"] + 2.0, centered=(True, True, False))
            .translate((x, 0.0, -1.0))
            .val()
        )
        shape = shape.cut(cutter)
        for hole_index in range(station):
            hole_x = x + (hole_index - (station - 1) / 2.0) * 2.4
            hole = cq.Solid.makeCylinder(0.65, coupon["gauge_height_mm"] + 2.0, cq.Vector(hole_x, -7.0, -1.0), cq.Vector(0.0, 0.0, 1.0))
            shape = shape.cut(hole)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("slot gauge is not one valid solid")
    return shape, {
        "part_id": "slot-gauge",
        "candidate_slot_widths_mm": coupon["candidate_slot_widths_mm"],
        "station_centers_x_mm": coupon["station_centers_x_mm"],
        "slot_length_mm": parameters["base"]["slot_length_mm"],
        "outer_dimensions_mm": [coupon["gauge_width_mm"], coupon["gauge_depth_mm"], coupon["gauge_height_mm"]],
        "print_orientation": "broad_face_down",
        "external_assets": [],
    }


def make_fit_key(parameters: dict) -> tuple[cq.Shape, dict]:
    divider = parameters["divider"]
    coupon = parameters["coupon"]
    thickness = divider["thickness_mm"]
    grip = rounded_plate(coupon["key_grip_width_mm"], coupon["key_grip_height_mm"], thickness, 3.0).translate((0.0, divider["foot_depth_mm"] + coupon["key_grip_height_mm"] / 2.0, 0.0))
    tongue = (
        cq.Workplane("XY")
        .box(divider["foot_length_mm"], divider["foot_depth_mm"], thickness, centered=(True, True, False))
        .translate((0.0, divider["foot_depth_mm"] / 2.0, 0.0))
        .val()
    )
    shape = grip.fuse(tongue).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("fit key is not one valid solid")
    bounds = shape.BoundingBox()
    return shape, {
        "part_id": "divider-fit-key",
        "tongue_thickness_mm": thickness,
        "tongue_length_mm": divider["foot_length_mm"],
        "tongue_depth_mm": divider["foot_depth_mm"],
        "outer_dimensions_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
        "print_orientation": "broad_face_down",
        "external_assets": [],
    }


def validate_parameters(parameters: dict) -> None:
    base = parameters["base"]
    divider = parameters["divider"]
    contract = parameters["workflow_contract"]
    positions = slot_positions(parameters)
    clears = compartment_clearances(parameters)
    assert parameters["project"]["id"] == PROJECT_ID
    assert base["slot_count"] == 16 and len(positions) == 16
    assert np.allclose(np.diff(positions), base["slot_pitch_mm"])
    assert base["width_mm"] / 2.0 - max(abs(item) for item in positions) >= 8.0
    assert np.isclose(base["slot_width_mm"] - divider["thickness_mm"], 0.5)
    assert np.isclose(base["slot_length_mm"] - divider["foot_length_mm"], 0.6)
    assert divider["default_slot_indices"] == [0, 2, 4, 6, 8, 11, 15]
    assert np.allclose(clears, [20.6, 20.6, 20.6, 20.6, 32.1, 43.6])
    assert np.allclose([item - divider["minimum_palette_clearance_mm"] for item in clears], contract["default_supported_palette_thicknesses_mm"])
    assert base["width_mm"] <= 225.0 and base["depth_mm"] <= 110.0
    assert base["rail_height_mm"] + divider["panel_height_mm"] <= 135.0
    assert np.isclose(base["rail_height_mm"] / parameters["printer"]["layer_height_mm"], 50.0)
    assert np.isclose(divider["thickness_mm"] / parameters["printer"]["layer_height_mm"], 12.0)
    assert contract["claim"] == "dry_countertop_storage_only_no_universal_fit_or_hygiene_claim"


def move_to_origin(shape: cq.Shape) -> cq.Shape:
    bounds = shape.BoundingBox()
    return shape.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def export_step(shape: cq.Shape, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path), exportType="STEP")


def export_stl(shape: cq.Shape, path: Path, linear: float, angular: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(move_to_origin(shape), str(path), tolerance=linear, angularTolerance=angular)
    mesh = trimesh.load_mesh(path, force="mesh", process=False)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    mesh.process(validate=True)
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise RuntimeError(f"cleaned STL is not a valid volume: {path.name}")
    mesh.export(path, file_type="stl")


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
        "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
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
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources = ET.SubElement(model, f"{{{ns}}}resources")
    build = ET.SubElement(model, f"{{{ns}}}build")
    for object_id, ((name, mesh_path), (move_x, move_y)) in enumerate(zip(parts, placements), 1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name})
        mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh")
        vertices = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces:
            ET.SubElement(triangles, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {move_x:.3f} {move_y:.3f} 0"})
    types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        _zip_member("[Content_Types].xml", types, archive)
        _zip_member("_rels/.rels", rels, archive)
        _zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive)
        _zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)


def main() -> None:
    parameters = load_parameters()
    validate_parameters(parameters)
    mesh_p = parameters["mesh"]
    shapes: dict[str, cq.Shape] = {}
    interfaces: dict[str, dict] = {}
    shapes["palette-grid-base"], interfaces["palette-grid-base"] = make_base(parameters)
    shapes["removable-divider"], interfaces["removable-divider"] = make_divider(parameters)
    shapes["slot-gauge"], interfaces["slot-gauge"] = make_slot_gauge(parameters)
    shapes["divider-fit-key"], interfaces["divider-fit-key"] = make_fit_key(parameters)

    step_paths = []
    for name, shape in shapes.items():
        path = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"
        export_step(shape, path)
        step_paths.append(path)
    exploded = cq.Compound.makeCompound(
        [
            shapes["palette-grid-base"],
            shapes["removable-divider"].translate((0.0, 125.0, 0.0)),
            shapes["slot-gauge"].translate((125.0, 125.0, 0.0)),
            shapes["divider-fit-key"].translate((175.0, 125.0, 0.0)),
        ]
    )
    exploded_path = MASTER / f"DRAFT-{PROJECT_ID}-virtual-set-{REVISION}.step"
    export_step(exploded, exploded_path)
    step_paths.append(exploded_path)

    mesh_paths: dict[str, Path] = {}
    for name in ("palette-grid-base", "removable-divider"):
        path = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path
    for name in ("slot-gauge", "divider-fit-key"):
        path = COUPONS / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_stl(shapes[name], path, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"])
        mesh_paths[name] = path

    package_path = THREE_MF / f"DRAFT-{PROJECT_ID}-adjustable-vertical-makeup-palette-organizer-{REVISION}.3mf"
    parts = [("palette-grid-base", mesh_paths["palette-grid-base"])]
    parts.extend((f"removable-divider-{index:02d}", mesh_paths["removable-divider"]) for index in range(1, 8))
    parts.extend([("slot-gauge", mesh_paths["slot-gauge"]), ("divider-fit-key", mesh_paths["divider-fit-key"])])
    placements = [(10.0, 10.0), (10.0, 130.0), (115.0, 130.0), (220.0, 130.0), (10.0, 205.0), (115.0, 205.0), (220.0, 205.0), (10.0, 280.0), (220.0, 10.0), (280.0, 10.0)]
    write_3mf(package_path, parts, placements)

    metrics = {name: mesh_metrics(path) for name, path in mesh_paths.items()}
    mesh_checks = []
    for name, item in metrics.items():
        mesh_checks.extend([
            check(f"{name}:watertight", item["watertight"], f"{name} is watertight"),
            check(f"{name}:winding", item["winding_consistent"], f"{name} winding is consistent"),
            check(f"{name}:volume", item["positive_volume"], f"{name} has positive volume"),
            check(f"{name}:component", item["components"] == 1, f"{name} is one component"),
            check(f"{name}:triangles", item["triangles"] <= mesh_p["triangle_stop"], "Triangle budget", {"actual": item["triangles"], "limit": mesh_p["triangle_stop"]}),
            check(f"{name}:file", item["file_mib"] <= mesh_p["max_mesh_mib"], "File budget", {"actual_mib": item["file_mib"], "limit_mib": mesh_p["max_mesh_mib"]}),
        ])

    parametric_checks = [
        check("parameter-validation", True, "Fail-closed parameter relations pass"),
        check("cad-valid", all(shape.isValid() for shape in shapes.values()), "All four B-Reps are valid"),
        check("single-solids", all(len(shape.Solids()) == 1 for shape in shapes.values()), "Every unique deliverable is one B-Rep solid"),
        check("slot-array", len(interfaces["palette-grid-base"]["slot_positions_x_mm"]) == 16, "Sixteen exact grid positions are generated"),
        check("no-external-assets", not any(item.get("external_assets") for item in interfaces.values()), "No external font, vector or mesh asset is used"),
    ]
    write_json(VALIDATION / "parametric-source-report.json", report(
        f"{PROJECT_ID}-parametric-source",
        [PARAMETERS, Path(__file__)],
        parametric_checks,
        {"python": platform.python_version(), "cadquery": cq.__version__, "unique_parts": list(shapes), "print_objects": [name for name, _ in parts]},
        ["Any parameter change requires regeneration of downstream evidence."],
    ))
    write_json(VALIDATION / "mesh-generation-report.json", report(
        f"{PROJECT_ID}-mesh-generation",
        [PARAMETERS, Path(__file__)],
        mesh_checks,
        {"meshes": metrics},
        ["Topology does not prove real PETG divider fit, palette abrasion, retrieval or loaded stability."],
    ))

    base_i = interfaces["palette-grid-base"]
    divider_i = interfaces["removable-divider"]
    gauge_i = interfaces["slot-gauge"]
    key_i = interfaces["divider-fit-key"]
    interface_checks = [
        check("slot-pitch", np.allclose(np.diff(base_i["slot_positions_x_mm"]), [11.5] * 15), "All grid stations use 11.5 mm pitch"),
        check("slot-clearance", np.isclose(base_i["slot_width_mm"] - divider_i["tongue_thickness_mm"], 0.5), "Default slot has 0.5 mm total tongue clearance"),
        check("length-clearance", np.isclose(base_i["slot_length_mm"] - divider_i["tongue_length_mm"], 0.6), "Default slot has 0.6 mm total tongue-length clearance"),
        check("gauge-brackets-default", gauge_i["candidate_slot_widths_mm"] == [2.7, 2.9, 3.1] and base_i["slot_width_mm"] == 2.9, "Gauge brackets the default slot by plus/minus 0.2 mm"),
        check("fit-key-matches-divider", key_i["tongue_thickness_mm"] == divider_i["tongue_thickness_mm"] and key_i["tongue_length_mm"] == divider_i["tongue_length_mm"], "Fit key reproduces divider tongue section"),
        check("default-layout", base_i["default_divider_indices"] == [0, 2, 4, 6, 8, 11, 15], "Default seven-divider layout is exact"),
        check("compartment-series", np.allclose(base_i["default_compartment_clear_mm"], [20.6, 20.6, 20.6, 20.6, 32.1, 43.6]), "Six default clear compartments are exact"),
        check("palette-margin", np.allclose(np.subtract(base_i["default_compartment_clear_mm"], 1.0), parameters["workflow_contract"]["default_supported_palette_thicknesses_mm"]), "Every declared palette thickness keeps 1.0 mm retrieval clearance"),
        check("portfolio-envelope", base_i["outer_dimensions_mm"][0] <= 225.0 and base_i["outer_dimensions_mm"][1] <= 110.0 and parameters["base"]["rail_height_mm"] + divider_i["installed_height_above_base_mm"] <= 135.0, "Assembly fits the researched 225 x 110 x 135 mm envelope"),
        check("support-conscious", all(item["print_orientation"] in {"rails_on_bed", "broad_face_down"} for item in interfaces.values()), "All unique parts have support-free declared orientations"),
        check("claim-boundary", parameters["workflow_contract"]["claim"] == "dry_countertop_storage_only_no_universal_fit_or_hygiene_claim", "Dry-storage claim boundary is explicit"),
    ]
    write_json(VALIDATION / "interface-report.json", report(
        f"{PROJECT_ID}-interface-validation",
        [PARAMETERS, Path(__file__), ROOT / "design-spec.yaml"],
        interface_checks,
        {"interfaces": interfaces, "workflow_contract": parameters["workflow_contract"]},
        ["Analytic clearances cannot establish insert force, wear, palette surface marking or tip resistance."],
    ))

    baseline_volume = float(np.prod(base_i["outer_dimensions_mm"]))
    baseline_volume += 7.0 * float(np.prod(divider_i["outer_dimensions_mm"]))
    baseline_volume += float(np.prod(gauge_i["outer_dimensions_mm"])) + float(np.prod(key_i["outer_dimensions_mm"]))
    candidate_volume = float(shapes["palette-grid-base"].Volume()) + 7.0 * float(shapes["removable-divider"].Volume()) + float(shapes["slot-gauge"].Volume()) + float(shapes["divider-fit-key"].Volume())
    reduction = 100.0 * (1.0 - candidate_volume / baseline_volume)
    optimization = {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "baseline": {"description": "solid bounding-envelope blocks for one base, seven dividers and two coupons", "volume_mm3": baseline_volume},
        "candidate": {"description": "three support rails, low side ties, windowed dividers and compact coupons", "volume_mm3": candidate_volume},
        "volume_reduction_percent": reduction, "selection_threshold_percent": 35.0,
        "status": "PASS" if reduction >= 35.0 else "FAIL", "exact_profile_ab_comparison": "PENDING_REFERENCE_SLICE"
    }
    write_json(REPORTS / "optimization-comparison.json", optimization)
    write_json(REPORTS / "mesh-complexity.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()) else "FAIL",
        "meshes": metrics, "simplification": "NOT_BENEFICIAL",
        "reason": "Slot edges, tongue sections and rounded palette contact frames are under budget; decimation risks the protected interface."
    })
    outputs = [*step_paths, *mesh_paths.values(), package_path]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS",
        "source_inputs": [input_record(PARAMETERS), input_record(Path(__file__))],
        "outputs": [input_record(path) for path in outputs],
        "manufacturing_outputs": [str(path.relative_to(ROOT)) for path in [*mesh_paths.values(), package_path]],
    })
    gate_reports = [json.loads((VALIDATION / name).read_text()) for name in ("parametric-source-report.json", "mesh-generation-report.json", "interface-report.json")]
    if any(value["status"] != "PASS" for value in [*gate_reports, optimization]):
        raise SystemExit("one or more build reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "revision": REVISION, "unique_meshes": len(mesh_paths), "objects": len(parts), "3mf": str(package_path.relative_to(ROOT)), "volume_reduction_percent": reduction}, indent=2))


if __name__ == "__main__":
    main()
