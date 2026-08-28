#!/usr/bin/env python3
"""Build the parametric MM-ORG-032 PairPin 8 candidate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import zipfile
import xml.etree.ElementTree as ET

import cadquery as cq
import numpy as np
import trimesh
from cadquery import exporters

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
REPORTS, VALIDATION, EXPORTS = ROOT / "reports", ROOT / "validation", ROOT / "exports"
PROJECT_ID, REVISION = "MM-ORG-032", "0.1.0-draft.1"


def sha256(target: Path) -> str:
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(target: Path) -> dict:
    try:
        display = str(target.relative_to(ROOT))
    except ValueError:
        display = str(target)
    return {"path": display, "sha256": sha256(target), "size_bytes": target.stat().st_size}


def write_json(target: Path, value: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def rounded_cylinder(diameter: float, height: float, top_fillet: float, x: float, y: float, z: float) -> cq.Workplane:
    part = cq.Workplane("XY").center(x, y).circle(diameter / 2).extrude(height).translate((0, 0, z))
    return part.edges(">Z").fillet(top_fillet)


def make_rack(parameters: dict, light: bool = False) -> tuple[cq.Workplane, dict]:
    rack, fit = parameters["rack"], parameters["fit"]
    base = rack["light_base_mm"] if light else rack["base_mm"]
    shape = cq.Workplane("XY").box(rack["width_mm"], rack["depth_mm"], base, centered=(False, False, False)).edges("|Z").fillet(rack["corner_radius_mm"])
    stations = []
    for row, spool_y, bobbin_y in [
        ("front", rack["front_spool_y_mm"], rack["front_bobbin_y_mm"]),
        ("rear", rack["rear_spool_y_mm"], rack["rear_bobbin_y_mm"]),
    ]:
        for column, x in enumerate(rack["column_centers_x_mm"], 1):
            spool_collar = rounded_cylinder(rack["spool_collar_diameter_mm"], rack["spool_collar_height_mm"], rack["collar_top_fillet_mm"], x, spool_y, base)
            spool_post = rounded_cylinder(rack["selected_spool_post_diameter_mm"], rack["spool_post_height_mm"], rack["post_tip_fillet_mm"], x, spool_y, base)
            bobbin_collar = rounded_cylinder(rack["bobbin_collar_diameter_mm"], rack["bobbin_collar_height_mm"], rack["collar_top_fillet_mm"], x, bobbin_y, base)
            bobbin_post = rounded_cylinder(rack["selected_bobbin_post_diameter_mm"], rack["bobbin_post_height_mm"], rack["bobbin_tip_fillet_mm"], x, bobbin_y, base)
            shape = shape.union(spool_collar).union(spool_post).union(bobbin_collar).union(bobbin_post)
            stations.append({"pair_id": f"{row}-{column}", "column": column, "x_mm": x, "spool_y_mm": spool_y, "bobbin_y_mm": bobbin_y})
    shape = shape.clean()
    gaps = {
        "spool_to_bobbin_same_pair_mm": abs(rack["front_bobbin_y_mm"] - rack["front_spool_y_mm"]) - (fit["maximum_spool_diameter_mm"] + fit["maximum_bobbin_diameter_mm"]) / 2,
        "bobbin_between_rows_mm": abs(rack["rear_bobbin_y_mm"] - rack["front_bobbin_y_mm"]) - fit["maximum_bobbin_diameter_mm"],
        "spool_between_columns_mm": rack["column_pitch_mm"] - fit["maximum_spool_diameter_mm"],
    }
    return shape, {"part_id": "light-rack" if light else "rack", "outer_bounds_mm": [rack["width_mm"], rack["depth_mm"], base + rack["spool_post_height_mm"]], "pair_count": len(stations), "stations": stations, "spool_post_diameter_mm": rack["selected_spool_post_diameter_mm"], "bobbin_post_diameter_mm": rack["selected_bobbin_post_diameter_mm"], "spool_tip_fillet_mm": rack["post_tip_fillet_mm"], "bobbin_tip_fillet_mm": rack["bobbin_tip_fillet_mm"], "collar_top_fillet_mm": rack["collar_top_fillet_mm"], "base_mm": base, "stored_envelope_gaps_mm": gaps, "label_datums": [{"column": index + 1, "width_mm": rack["label_datum_width_mm"], "height_mm": rack["label_datum_height_mm"]} for index in range(rack["columns"])], "print_orientation": "base_down", "support_required": False, "light_variant": light, "external_assets": []}


def make_pin_gauge(parameters: dict, family: str) -> tuple[cq.Workplane, dict]:
    fit, coupon = parameters["fit"], parameters["coupon"]
    candidates = fit["spool_post_diameter_candidates_mm"] if family == "spool" else fit["bobbin_post_diameter_candidates_mm"]
    selected = fit["selected_spool_post_diameter_mm"] if family == "spool" else fit["selected_bobbin_post_diameter_mm"]
    shape = cq.Workplane("XY").box(coupon["base_width_mm"], coupon["base_depth_mm"], coupon["base_mm"], centered=(False, False, False)).edges("|Z").fillet(2.0)
    for x, diameter in zip(coupon["center_x_mm"], candidates):
        collar = rounded_cylinder(diameter + 5.0, 1.8, 0.6, x, coupon["base_depth_mm"] / 2, coupon["base_mm"])
        pin = rounded_cylinder(diameter, coupon["pin_height_mm"], min(coupon["tip_fillet_mm"], diameter / 2 - 0.2), x, coupon["base_depth_mm"] / 2, coupon["base_mm"])
        shape = shape.union(collar).union(pin)
    shape = shape.clean()
    return shape, {"part_id": f"{family}-post-gauge", "candidate_diameters_mm": candidates, "selected_diameter_mm": selected, "station_order": "left_to_right_ascending", "outer_bounds_mm": [coupon["base_width_mm"], coupon["base_depth_mm"], coupon["base_mm"] + coupon["pin_height_mm"]], "tip_fillet_mm": coupon["tip_fillet_mm"], "print_orientation": "base_down", "external_assets": []}


def export_step(shape: cq.Workplane | cq.Compound, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(target), exportType="STEP")


def export_stl(shape: cq.Workplane, target: Path, linear: float, angular: float) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(target), exportType="STL", tolerance=linear, angularTolerance=angular)
    mesh = trimesh.load_mesh(target, force="mesh", process=True)
    mesh.remove_unreferenced_vertices(); mesh.merge_vertices(); mesh.fix_normals()
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise RuntimeError(f"Invalid mesh: {target}")
    mesh.export(target, file_type="stl")


def mesh_metrics(target: Path) -> dict:
    mesh = trimesh.load_mesh(target, force="mesh", process=True)
    return {"path": str(target.relative_to(ROOT)), "sha256": sha256(target), "triangles": int(len(mesh.faces)), "vertices": int(len(mesh.vertices)), "file_bytes": target.stat().st_size, "file_mib": target.stat().st_size / (1024 * 1024), "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent), "positive_volume": bool(mesh.is_volume and mesh.volume > 0), "components": int(len(mesh.split(only_watertight=False))), "volume_mm3": float(mesh.volume), "surface_area_mm2": float(mesh.area), "extents_mm": np.round(mesh.extents, 4).tolist(), "bounds_mm": np.round(mesh.bounds, 4).tolist()}


def zip_member(name: str, data: bytes, archive: zipfile.ZipFile) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; archive.writestr(info, data)


def write_3mf(target: Path, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"; ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"}); resources = ET.SubElement(model, f"{{{ns}}}resources"); build = ET.SubElement(model, f"{{{ns}}}build")
    for object_id, ((name, mesh_path), (mx, my)) in enumerate(zip(parts, placements), 1):
        mesh = trimesh.load_mesh(mesh_path, force="mesh", process=True); obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(object_id), "type": "model", "name": name}); mesh_node = ET.SubElement(obj, f"{{{ns}}}mesh"); vertices = ET.SubElement(mesh_node, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices: ET.SubElement(vertices, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        triangles = ET.SubElement(mesh_node, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces: ET.SubElement(triangles, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {mx:.3f} {my:.3f} 0"})
    types = b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        zip_member("[Content_Types].xml", types, archive); zip_member("_rels/.rels", rels, archive); zip_member("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True), archive); zip_member("Metadata/model-parameters.json", PARAMETERS.read_bytes(), archive)


def nesting_report(parameters: dict, parts: list[tuple[str, Path]], placements: list[tuple[float, float]]) -> dict:
    gap, margin, bed = parameters["nesting"]["minimum_object_gap_mm"], parameters["nesting"]["bed_margin_mm"], parameters["printer"]["build_volume_mm"]
    items = []
    for (name, target), (mx, my) in zip(parts, placements):
        bounds = trimesh.load_mesh(target, force="mesh", process=True).bounds; items.append({"name": name, "x0": float(bounds[0][0] + mx), "y0": float(bounds[0][1] + my), "x1": float(bounds[1][0] + mx), "y1": float(bounds[1][1] + my)})
    collisions = []
    for index, a in enumerate(items):
        for b in items[index + 1:]:
            separated = a["x1"] + gap <= b["x0"] or b["x1"] + gap <= a["x0"] or a["y1"] + gap <= b["y0"] or b["y1"] + gap <= a["y0"]
            if not separated: collisions.append([a["name"], b["name"]])
    within = all(item["x0"] >= margin and item["y0"] >= margin and item["x1"] <= bed[0] - margin and item["y1"] <= bed[1] - margin for item in items)
    checks = [check("non-overlap", not collisions, "Three objects retain the configured gap", {"collisions": collisions}), check("bed-bounds", within, "Layout respects conservative bed margins")]
    return {"schema_version": "1.0", "tool": "MM-ORG-032-nesting-layout", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [], "checks": checks, "metrics": {"plate_count": 1, "object_count": len(items), "minimum_gap_mm": gap, "objects": items}, "limitations": ["Exact destination profile remains authoritative."], "required_capabilities": []}


def virtual_loaded_assembly(parameters: dict, rack_shape: cq.Workplane) -> cq.Compound:
    rack, fit = parameters["rack"], parameters["fit"]
    solids = [rack_shape.val()]
    for spool_y, bobbin_y in [(rack["front_spool_y_mm"], rack["front_bobbin_y_mm"]), (rack["rear_spool_y_mm"], rack["rear_bobbin_y_mm"])]:
        for x in rack["column_centers_x_mm"]:
            spool = cq.Workplane("XY").center(x, spool_y).circle(fit["maximum_spool_diameter_mm"] / 2).extrude(fit["maximum_spool_height_mm"]).translate((0, 0, rack["base_mm"] + rack["spool_collar_height_mm"]))
            bobbin = cq.Workplane("XY").center(x, bobbin_y).circle(fit["maximum_bobbin_diameter_mm"] / 2).extrude(fit["maximum_bobbin_height_mm"]).translate((0, 0, rack["base_mm"] + rack["bobbin_collar_height_mm"]))
            solids.extend([spool.val(), bobbin.val()])
    return cq.Compound.makeCompound(solids)


def main() -> None:
    parameters = json.loads(PARAMETERS.read_text()); REPORTS.mkdir(exist_ok=True); VALIDATION.mkdir(exist_ok=True)
    source_inputs = [PARAMETERS, ROOT / "cad/build.py"]; inputs = [record(path) for path in source_inputs]
    rack_p, fit, mesh_p = parameters["rack"], parameters["fit"], parameters["mesh"]
    rack_shape, rack_i = make_rack(parameters); light_shape, light_i = make_rack(parameters, light=True); spool_gauge, spool_i = make_pin_gauge(parameters, "spool"); bobbin_gauge, bobbin_i = make_pin_gauge(parameters, "bobbin")
    shapes = {"rack": rack_shape, "spool-post-gauge": spool_gauge, "bobbin-post-gauge": bobbin_gauge}; all_shapes = [*shapes.values(), light_shape]
    if not all(shape.val().isValid() and len(shape.solids().vals()) == 1 for shape in all_shapes): raise RuntimeError("Invalid or multi-solid B-Rep")
    checks = [check("identity", parameters["project"]["id"] == PROJECT_ID, "Project identity matches"), check("pair-count", rack_i["pair_count"] == 8, "Eight pair stations exist"), check("envelope", rack_p["width_mm"] <= 220 and rack_p["depth_mm"] <= 160 and rack_i["outer_bounds_mm"][2] <= 180, "Rack fits portfolio envelope"), check("pin-candidates", len(fit["spool_post_diameter_candidates_mm"]) == len(fit["bobbin_post_diameter_candidates_mm"]) == 4, "Two four-pin sweeps exist"), check("selected-pins", rack_i["spool_post_diameter_mm"] == fit["selected_spool_post_diameter_mm"] and rack_i["bobbin_post_diameter_mm"] == fit["selected_bobbin_post_diameter_mm"], "Rack and fit source share selected pins"), check("thread-contact", rack_i["spool_tip_fillet_mm"] >= 1.5 and rack_i["bobbin_tip_fillet_mm"] >= 1.3 and rack_i["collar_top_fillet_mm"] >= 0.8, "Thread-contact transitions retain declared fillets"), check("content", parameters["physical_contract"]["contents"] == "adult_sewing_thread_spools_and_matching_machine_bobbins_only", "Adult sewing-storage boundary is explicit")]
    step_paths, stl_paths = {}, {}
    for name, shape in shapes.items():
        step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"; folder = "manufacturing" if name == "rack" else "coupons"; stl = EXPORTS / folder / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"; export_step(shape, step); export_stl(shape, stl, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"]); step_paths[name], stl_paths[name] = step, stl
    light_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-light-rack-{REVISION}.step"; light_stl = EXPORTS / "variants" / f"DRAFT-{PROJECT_ID}-light-rack-{REVISION}.stl"; export_step(light_shape, light_step); export_stl(light_shape, light_stl, mesh_p["linear_deflection_mm"], mesh_p["angular_deflection_rad"]); step_paths["light-rack"], stl_paths["light-rack"] = light_step, light_stl
    virtual_step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-virtual-loaded-eight-pairs-{REVISION}.step"; export_step(virtual_loaded_assembly(parameters, rack_shape), virtual_step)
    order = ["rack", "spool-post-gauge", "bobbin-post-gauge"]; parts = [(name, stl_paths[name]) for name in order]; placements = [tuple(parameters["nesting"]["origins_mm"][name]) for name in order]
    nesting = nesting_report(parameters, parts, placements); nesting["inputs"] = inputs; write_json(REPORTS / "nesting-layout.json", nesting)
    if nesting["status"] != "PASS": raise RuntimeError("Nesting failed")
    selected_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-pairpin-eight-{REVISION}.3mf"; write_3mf(selected_3mf, parts, placements)
    metrics = {name: mesh_metrics(path) for name, path in stl_paths.items()}; baseline = rack_p["width_mm"] * rack_p["depth_mm"] * (rack_p["base_mm"] + rack_p["spool_post_height_mm"]); selected = metrics["rack"]["volume_mm3"]
    geometric = {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "baseline": {"id": "solid-rack-envelope", "volume_mm3": baseline}, "selected": {"id": "thin-base-rounded-pair-post-rack", "volume_mm3": selected, "reduction_percent": 100 * (1 - selected / baseline)}, "light_variant": {"id": "2.4-mm-base-same-fit-pins", "volume_mm3": metrics["light-rack"]["volume_mm3"], "reduction_percent_vs_selected_rack": 100 * (1 - metrics["light-rack"]["volume_mm3"] / selected), "constraint": "REJECTED_PENDING_LOADED_TIP_DROP_AND_CYCLE_EVIDENCE"}, "process_comparison": "PENDING_EXACT_SLICES"}; write_json(REPORTS / "optimization-geometric.json", geometric)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": "PASS", "meshes": metrics, "simplification": "NOT_BENEFICIAL", "reason": "Filleted contact geometry and calibrated pin diameters are functional; all meshes remain below budget."})
    parametric_checks = checks + [check("cad-valid", all(shape.val().isValid() for shape in all_shapes), "All B-Reps are valid"), check("single-solids", all(len(shape.solids().vals()) == 1 for shape in all_shapes), "Every unique printable deliverable is one solid")]
    parametric = {"schema_version": "1.0", "tool": "MM-ORG-032-parametric-source", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in parametric_checks) else "FAIL", "profile": "draft", "inputs": inputs, "checks": parametric_checks, "metrics": {"python": sys.version.split()[0], "cadquery": cq.__version__, "unique_parts": ["rack", "spool-post-gauge", "bobbin-post-gauge", "light-rack"]}, "limitations": ["Digital fillets and gaps do not prove real thread snag resistance or stored-item stability."], "required_capabilities": ["cad"]}; write_json(VALIDATION / "parametric-source-report.json", parametric)
    mesh_checks = [check("mesh-count", len(metrics) == 4, "Three selected meshes plus one light variant generated"), check("mesh-validity", all(item["watertight"] and item["winding_consistent"] and item["components"] == 1 and item["positive_volume"] for item in metrics.values()), "Every mesh is one watertight positive volume"), check("mesh-budget", all(item["triangles"] <= mesh_p["triangle_stop"] and item["file_mib"] <= mesh_p["max_mesh_mib"] for item in metrics.values()), "Every mesh stays below budget")]
    meshgen = {"schema_version": "1.0", "tool": "MM-ORG-032-mesh-generation", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in mesh_checks) else "FAIL", "profile": "draft", "inputs": inputs, "checks": mesh_checks, "metrics": {"meshes": metrics, "selected_3mf": record(selected_3mf)}, "limitations": ["STL units rely on project millimetre contract."], "required_capabilities": ["mesh"]}; write_json(VALIDATION / "mesh-generation-report.json", meshgen)
    minimum_gap = min(rack_i["stored_envelope_gaps_mm"].values())
    interface_checks = [check("eight-pairs", rack_i["pair_count"] == 8 and len(rack_i["stations"]) == 8, "Eight spool/bobbin pair identities share X centerlines"), check("envelope-gap", minimum_gap >= fit["minimum_neighbor_gap_mm"], "Stored planning envelopes retain minimum gap", {"minimum_gap_mm": minimum_gap}), check("spool-gauge", spool_i["candidate_diameters_mm"] == [4, 4.5, 5, 5.5] and spool_i["selected_diameter_mm"] == 5, "Spool gauge brackets selected pin"), check("bobbin-gauge", bobbin_i["candidate_diameters_mm"] == [3.5, 4, 4.5, 5] and bobbin_i["selected_diameter_mm"] == 4.5, "Bobbin gauge brackets selected pin"), check("fillets", rack_i["spool_tip_fillet_mm"] == 1.6 and rack_i["bobbin_tip_fillet_mm"] == 1.4 and rack_i["collar_top_fillet_mm"] == 0.8, "All declared thread-contact transitions retain fillets"), check("labels", len(rack_i["label_datums"]) == 4 and all(item["width_mm"] == 42 for item in rack_i["label_datums"]), "Four flat label datums are declared"), check("light-fit", light_i["spool_post_diameter_mm"] == rack_i["spool_post_diameter_mm"] and light_i["bobbin_post_diameter_mm"] == rack_i["bobbin_post_diameter_mm"], "Light variant does not alter fit pins")]
    interfaces = {"rack": rack_i, "spool-post-gauge": spool_i, "bobbin-post-gauge": bobbin_i, "light-rack": light_i}
    interface = {"schema_version": "1.0", "tool": "MM-ORG-032-interface-validation", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in interface_checks) else "FAIL", "profile": "draft", "inputs": inputs, "checks": interface_checks, "metrics": {"interfaces": interfaces, "minimum_stored_envelope_gap_mm": minimum_gap, "stored_envelopes_mm": {"spool": [fit["maximum_spool_diameter_mm"], fit["maximum_spool_height_mm"]], "bobbin": [fit["maximum_bobbin_diameter_mm"], fit["maximum_bobbin_height_mm"]]}}, "limitations": ["Real bores, bobbin machine compatibility, thread snag and loaded stability require physical checks."], "required_capabilities": []}; write_json(VALIDATION / "interface-report.json", interface)
    outputs = [*step_paths.values(), virtual_step, *stl_paths.values(), selected_3mf, REPORTS / "nesting-layout.json", REPORTS / "optimization-geometric.json", REPORTS / "mesh-complexity.json", VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json"]
    write_json(REPORTS / "build-manifest.json", {"schema_version": "1.0", "project": PROJECT_ID, "revision": REVISION, "status": "PASS", "source_inputs": inputs, "outputs": [record(path) for path in outputs], "manufacturing_outputs": [str(stl_paths[name].relative_to(ROOT)) for name in order] + [str(selected_3mf.relative_to(ROOT))], "optimization_variants": [str(light_step.relative_to(ROOT)), str(light_stl.relative_to(ROOT))]})
    if any(report["status"] != "PASS" for report in [nesting, parametric, meshgen, interface]): raise RuntimeError("One or more reports failed")
    print(json.dumps({"status": "PASS", "project": PROJECT_ID, "unique_meshes": len(metrics), "selected_objects": len(parts), "geometric_reduction_percent": geometric["selected"]["reduction_percent"]}, indent=2))


if __name__ == "__main__": main()
