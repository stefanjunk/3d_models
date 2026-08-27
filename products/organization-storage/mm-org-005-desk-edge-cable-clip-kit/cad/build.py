#!/usr/bin/env python3
"""Parametric desk-edge cable clip generator for MM-ORG-005."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = ROOT / "config" / "model-parameters.json"
MASTER = ROOT / "exports" / "master"
MANUFACTURING = ROOT / "exports" / "manufacturing"
COUPONS = ROOT / "exports" / "coupons"
THREE_MF = ROOT / "exports" / "3mf"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"
PROJECT_ID = "MM-ORG-005"
REVISION = "0.1.0-draft.1"


def load_params() -> dict:
    return json.loads(PARAMS.read_text(encoding="utf-8"))


def custom_variant(p: dict, desk: float, cable: float) -> dict:
    limits = p["input_limits"]
    if not limits["desk_min"] <= desk <= limits["desk_max"]:
        raise ValueError(f"desk thickness must be {limits['desk_min']}..{limits['desk_max']} mm")
    if not limits["cable_min"] <= cable <= limits["cable_max"]:
        raise ValueError(f"cable diameter must be {limits['cable_min']}..{limits['cable_max']} mm")
    jaw = min(desk - p["clamp"]["preload_default"], p["clamp"]["maximum_jaw"])
    return {"target_desk": desk, "jaw_gap": jaw, "cable_diameter": cable}


def validate_parameters(p: dict) -> None:
    assert p["project"]["id"] == PROJECT_ID and p["project"]["revision"] == REVISION
    c = p["clamp"]
    k = p["cable_keeper"]
    assert c["flexure_root"] >= 2.4 and c["flexure_tip"] >= 1.8
    assert c["fixed_arm"] >= 2.0 and c["insertion_depth"] >= 30.0
    assert c["flexure_root"] > c["flexure_tip"]
    assert math.isclose(k["radial_clearance"], 0.35, abs_tol=1e-9)
    assert 0.55 <= k["entry_ratio"] <= 0.80
    limits = p["input_limits"]
    assert custom_variant(p, limits["desk_min"], limits["cable_min"])["jaw_gap"] > 0
    assert custom_variant(p, limits["desk_max"], limits["cable_max"])["jaw_gap"] <= c["maximum_jaw"]
    for variant in p["variants"].values():
        assert limits["desk_min"] <= variant["target_desk"] <= limits["desk_max"]
        assert limits["cable_min"] <= variant["cable_diameter"] <= limits["cable_max"]
        assert variant["jaw_gap"] < variant["target_desk"]


def prism_xz(points: list[tuple[float, float]], width: float) -> cq.Shape:
    vectors = [cq.Vector(x, -width / 2.0, z) for x, z in points]
    vectors.append(vectors[0])
    wire = cq.Wire.makePolygon(vectors)
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0.0, width, 0.0))


def box_at(x: float, y: float, z: float, sx: float, sy: float, sz: float) -> cq.Shape:
    return cq.Solid.makeBox(sx, sy, sz, cq.Vector(x, y, z))


def cylinder_y(radius: float, width: float, x: float, z: float) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, width, cq.Vector(x, -width / 2.0, z), cq.Vector(0.0, 1.0, 0.0))


def make_clip(variant: dict, p: dict, *, width: float | None = None, baseline: bool = False) -> cq.Shape:
    c = p["clamp"]
    k = p["cable_keeper"]
    actual_width = float(width if width is not None else c["clip_width"])
    depth = c["insertion_depth"]
    jaw = variant["jaw_gap"]
    fixed = 3.0 if baseline else c["fixed_arm"]
    root = 3.0 if baseline else c["flexure_root"]
    tip = 3.0 if baseline else c["flexure_tip"]

    spine = box_at(0.0, -actual_width / 2.0, -root, c["front_spine"], actual_width, jaw + fixed + root)
    upper_points = [
        (0.0, jaw),
        (depth - c["tip_ramp_length"], jaw),
        (depth, jaw + c["tip_ramp_rise"]),
        (depth, jaw + fixed),
        (0.0, jaw + fixed),
    ]
    upper = prism_xz(upper_points, actual_width)
    lower_points = [(0.0, 0.0), (depth, 0.0), (depth, -tip), (0.0, -root)]
    lower = prism_xz(lower_points, actual_width)
    grip = cylinder_y(c["grip_pad_radius"], actual_width, depth - 2.2, 0.0)

    cable = variant["cable_diameter"]
    bore_r = cable / 2.0 + k["radial_clearance"]
    outer_r = bore_r + k["ring_wall"]
    ring_x = -outer_r + k["root_overlap"]
    ring_z = jaw / 2.0
    ring = cylinder_y(outer_r, actual_width, ring_x, ring_z).cut(cylinder_y(bore_r, actual_width + 0.2, ring_x, ring_z))
    slit = cable * k["entry_ratio"]
    slit_box = box_at(
        ring_x - outer_r - 0.2,
        -actual_width / 2.0 - 0.1,
        ring_z - slit / 2.0,
        outer_r + 0.35,
        actual_width + 0.2,
        slit,
    )
    ring = ring.cut(slit_box)
    shape = spine.fuse(upper).fuse(lower).fuse(grip).fuse(ring)
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError("Invalid clip B-Rep")
    return shape


def print_orientation(shape: cq.Shape) -> cq.Shape:
    rotated = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90.0)
    box = rotated.BoundingBox()
    return rotated.translate(cq.Vector(-box.xmin, -box.ymin, -box.zmin))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def export_shape(shape: cq.Shape, path: Path, p: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".step":
        cq.exporters.export(shape, str(path), exportType="STEP")
    else:
        cq.exporters.export(shape, str(path), tolerance=p["export"]["chordal_tolerance"], angularTolerance=p["export"]["angular_tolerance"])


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    return {
        "path": str(path.relative_to(ROOT)), "sha256": sha256(path), "file_bytes": path.stat().st_size,
        "vertices": int(len(mesh.vertices)), "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
        "positive_volume": bool(mesh.volume > 0), "components": int(len(mesh.split(only_watertight=False))),
        "volume_mm3": float(mesh.volume), "extents_mm": np.round(mesh.extents, 5).tolist(),
    }


def check(cid: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": cid, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def report(tool: str, inputs: list[Path], checks: list[dict], metrics: dict, limitations: list[str]) -> dict:
    return {
        "schema_version": "1.0", "tool": tool, "tool_version": REVISION,
        "status": "PASS" if all(x["status"] == "PASS" for x in checks) else "FAIL", "profile": "draft",
        "inputs": [{"path": str(x.relative_to(ROOT)), "sha256": sha256(x), "size_bytes": x.stat().st_size} for x in inputs],
        "checks": checks, "metrics": metrics, "limitations": limitations, "required_capabilities": [],
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def add_zip_member(archive: zipfile.ZipFile, name: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o100644 << 16
    archive.writestr(info, payload)


def mesh_for_3mf(shape: cq.Shape, p: dict) -> trimesh.Trimesh:
    vertices, faces = shape.tessellate(p["export"]["chordal_tolerance"], p["export"]["angular_tolerance"])
    mesh = trimesh.Trimesh(np.asarray([[v.x, v.y, v.z] for v in vertices]), np.asarray(faces), process=True, validate=True)
    mesh.merge_vertices(); mesh.remove_unreferenced_vertices()
    if not mesh.is_watertight or mesh.volume <= 0: raise RuntimeError("Invalid 3MF mesh")
    return mesh


def write_3mf(path: Path, shapes: list[tuple[str, cq.Shape]], p: dict) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"; ET.register_namespace("", ns)
    model = ET.Element(f"{{{ns}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    for key, value in (("Title", "DRAFT MM-ORG-005 Desk-edge Cable Clip Kit"), ("Designer", "metriMade / autonomous CAD workflow"), ("Description", "Three side-oriented PETG clip variants; unsliced inventory strip."), ("LicenseTerms", "DRAFT engineering artifact; not a commercial release")):
        n = ET.SubElement(model, f"{{{ns}}}metadata", {"name": key}); n.text = value
    resources = ET.SubElement(model, f"{{{ns}}}resources"); build = ET.SubElement(model, f"{{{ns}}}build")
    cursor = 0.0
    for oid, (name, shape) in enumerate(shapes, 1):
        mesh = mesh_for_3mf(shape, p)
        obj = ET.SubElement(resources, f"{{{ns}}}object", {"id": str(oid), "type": "model", "name": name, "partnumber": f"{PROJECT_ID}-{REVISION}-{name}"})
        mn = ET.SubElement(obj, f"{{{ns}}}mesh"); vn = ET.SubElement(mn, f"{{{ns}}}vertices")
        for x, y, z in mesh.vertices: ET.SubElement(vn, f"{{{ns}}}vertex", {"x": f"{x:.6f}", "y": f"{y:.6f}", "z": f"{z:.6f}"})
        tn = ET.SubElement(mn, f"{{{ns}}}triangles")
        for a, b, c in mesh.faces: ET.SubElement(tn, f"{{{ns}}}triangle", {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c))})
        ET.SubElement(build, f"{{{ns}}}item", {"objectid": str(oid), "transform": f"1 0 0 0 1 0 0 0 1 {cursor:.3f} 0 0"})
        cursor += shape.BoundingBox().xlen + 8.0
    model_bytes = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        add_zip_member(z, "[Content_Types].xml", types); add_zip_member(z, "_rels/.rels", rels); add_zip_member(z, "3D/3dmodel.model", model_bytes); add_zip_member(z, "Metadata/model-parameters.json", PARAMS.read_bytes())


def build_default() -> None:
    p = load_params(); validate_parameters(p); source = Path(__file__).resolve(); envelope = p["manufacturing_envelope"]
    clip_shapes: dict[str, cq.Shape] = {}; meshes: dict[str, dict] = {}; coupon_meshes: dict[str, dict] = {}
    for name, variant in p["variants"].items():
        native = make_clip(variant, p); printed = print_orientation(native); clip_shapes[name] = printed
        step = MASTER / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.step"; stl = MANUFACTURING / f"DRAFT-{PROJECT_ID}-{name}-{REVISION}.stl"
        export_shape(native, step, p); export_shape(printed, stl, p); meshes[name] = mesh_metrics(stl)
        coupon = print_orientation(make_clip(variant, p, width=p["clamp"]["coupon_width"]))
        coupon_path = COUPONS / f"DRAFT-{PROJECT_ID}-{name}-coupon-{REVISION}.stl"; export_shape(coupon, coupon_path, p); coupon_meshes[name] = mesh_metrics(coupon_path)
    print_set = THREE_MF / f"DRAFT-{PROJECT_ID}-desk-edge-cable-clip-kit-{REVISION}.3mf"
    write_3mf(print_set, list(clip_shapes.items()), p)
    assembly = cq.Compound.makeCompound([shape.translate(cq.Vector(0, idx * 28.0, 0)) for idx, shape in enumerate(clip_shapes.values())])
    preview = MASTER / f"DRAFT-{PROJECT_ID}-kit-preview-{REVISION}.stl"; export_shape(assembly, preview, p)

    all_meshes = {**meshes, **{f"coupon_{k}": v for k, v in coupon_meshes.items()}}
    mesh_checks = []
    for name, m in all_meshes.items():
        mesh_checks += [check(f"{name}-watertight", m["watertight"], f"{name} is watertight"), check(f"{name}-winding", m["winding_consistent"], f"{name} has consistent winding"), check(f"{name}-volume", m["positive_volume"], f"{name} has positive volume"), check(f"{name}-component", m["components"] == 1, f"{name} is one component"), check(f"{name}-envelope", all(a <= b + 0.05 for a, b in zip(m["extents_mm"], envelope)), f"{name} fits 80 x 25 x 20 mm", {"extents_mm": m["extents_mm"]})]
    mesh_report = report(f"{PROJECT_ID}-mesh-generation", [PARAMS, source], mesh_checks, {"meshes": all_meshes}, ["Mesh checks do not prove PETG fatigue, force, pinch or marking behavior."])
    write_json(VALIDATION / "mesh-generation-report.json", mesh_report)
    interface_report = report(f"{PROJECT_ID}-interface-validation", [PARAMS, source], [
        check("radial-clearance", math.isclose(p["cable_keeper"]["radial_clearance"], 0.35, abs_tol=1e-9), "Cable radial clearance is 0.35 mm"),
        check("flexure-root", p["clamp"]["flexure_root"] >= 2.4, "Flexure root is at least 2.4 mm"),
        check("flexure-tip", p["clamp"]["flexure_tip"] >= 1.8, "Flexure tip is at least 1.8 mm"),
        check("coupon-set", len(coupon_meshes) == 3, "Three low-material fit coupons exist"),
    ], {"desk_targets_mm": [v["target_desk"] for v in p["variants"].values()], "cable_diameters_mm": [v["cable_diameter"] for v in p["variants"].values()], "physical_fit": "NOT_RUN"}, ["Nominal geometry does not establish insertion force, fatigue, cable pinch or non-marking behavior."])
    write_json(VALIDATION / "interface-report.json", interface_report)
    source_report = report(f"{PROJECT_ID}-parametric-source", [PARAMS, source, ROOT / "design-spec.yaml", ROOT / "protected-geometry-map.md"], [
        check("parameter-contract", True, "Default and min/max input assertions pass"), check("part-count", len(meshes) == 3, "Three default production clips are generated"), check("mesh-stage", mesh_report["status"] == "PASS", "All mesh checks pass"), check("interface-stage", interface_report["status"] == "PASS", "All nominal interface checks pass"), check("print-set", print_set.is_file(), "DRAFT 3MF exists")
    ], {"production_parts": list(meshes), "print_set": str(print_set.relative_to(ROOT))}, ["Exact slicer and physical validation are deferred."])
    write_json(VALIDATION / "parametric-source-report.json", source_report)
    baseline_volume = sum(make_clip(v, p, baseline=True).Volume() for v in p["variants"].values()); selected_volume = sum(m["volume_mm3"] for m in meshes.values())
    optimization = report(f"{PROJECT_ID}-optimization-comparison", [PARAMS, source, ROOT / "protected-geometry-map.md"], [check("protected-map", True, "Protected geometry map exists"), check("selected-volume", selected_volume < baseline_volume, "Tapered C-ring candidate uses less CAD volume than 3 mm U baseline"), check("part-envelope", all(all(a <= b + 0.05 for a, b in zip(m["extents_mm"], envelope)) for m in meshes.values()), "Selected production clips fit the research envelope")], {"baseline_cad_volume_mm3": baseline_volume, "selected_cad_volume_mm3": selected_volume, "cad_volume_reduction_percent": 100 * (baseline_volume-selected_volume)/baseline_volume, "exact_slicer_metrics": "NOT_RUN", "selection": "B tapered leaf plus C-ring"}, ["CAD volume is not deposited material; exact A/B/C slicing and fatigue tests are deferred."])
    write_json(REPORTS / "optimization-comparison.json", optimization)
    manifest = {"project_id": PROJECT_ID, "revision": REVISION, "status": "DRAFT", "parameters_sha256": sha256(PARAMS), "source_sha256": sha256(source), "parts": meshes, "coupons": coupon_meshes, "print_set": str(print_set.relative_to(ROOT)), "print_set_sha256": sha256(print_set), "physical_validation": "DEFERRED"}
    write_json(REPORTS / "build-manifest.json", manifest)
    if any(r["status"] != "PASS" for r in (mesh_report, interface_report, source_report, optimization)): raise RuntimeError("Digital check failed")
    print(json.dumps({"status": "PASS", "parts": list(meshes), "print_set": str(print_set)}, indent=2))


def build_custom(desk: float, cable: float, count: int, name: str) -> None:
    p = load_params(); validate_parameters(p)
    limits = p["input_limits"]
    if not limits["count_min"] <= count <= limits["count_max"]: raise ValueError(f"count must be {limits['count_min']}..{limits['count_max']}")
    variant = custom_variant(p, desk, cable); native = make_clip(variant, p); printed = print_orientation(native)
    slug = name.replace(" ", "-").lower(); step = MASTER / f"CUSTOM-{PROJECT_ID}-{slug}.step"; stl = MANUFACTURING / f"CUSTOM-{PROJECT_ID}-{slug}.stl"
    export_shape(native, step, p); export_shape(printed, stl, p)
    order = {"project_id": PROJECT_ID, "name": name, "desk_mm": desk, "cable_mm": cable, "count": count, "jaw_gap_mm": variant["jaw_gap"], "step": str(step.relative_to(ROOT)), "stl": str(stl.relative_to(ROOT)), "physical_fit": "NOT_RUN"}
    write_json(REPORTS / f"CUSTOM-{PROJECT_ID}-{slug}-order.json", order); print(json.dumps(order, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--desk-mm", type=float); parser.add_argument("--cable-mm", type=float); parser.add_argument("--count", type=int, default=1); parser.add_argument("--name", default="custom")
    args = parser.parse_args()
    if args.desk_mm is None and args.cable_mm is None: build_default()
    elif args.desk_mm is not None and args.cable_mm is not None: build_custom(args.desk_mm, args.cable_mm, args.count, args.name)
    else: parser.error("--desk-mm and --cable-mm must be supplied together")


if __name__ == "__main__": main()
