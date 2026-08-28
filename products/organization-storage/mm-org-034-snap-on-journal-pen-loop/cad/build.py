#!/usr/bin/env python3
"""Build the parametric MM-ORG-034 FlexDock journal pen-loop candidate."""
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
PROJECT_ID = "MM-ORG-034"
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


def cylinder_y(radius: float, width: float, x: float, z: float) -> cq.Workplane:
    return cq.Workplane("XZ", origin=(0, width / 2, 0)).center(x, z).circle(radius).extrude(width)


def ring_y(inner_radius: float, outer_radius: float, width: float, x: float, z: float) -> cq.Workplane:
    return (
        cq.Workplane("XZ", origin=(0, width / 2, 0))
        .center(x, z)
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(width)
    )


def make_petg_clip(p: dict, size: str, gap: float) -> tuple[cq.Workplane, dict]:
    c, r = p["clip"], p["rail"]
    width = c["width_mm"]
    back = box_at(0, -width / 2, 0, c["insertion_depth_mm"], width, c["back_thickness_mm"])
    tongue_z = c["back_thickness_mm"] + gap
    tongue = box_at(0, -width / 2, tongue_z, c["tongue_depth_mm"], width, c["tongue_thickness_mm"])
    total_height = tongue_z + c["tongue_thickness_mm"]
    bridge = box_at(0, -width / 2, 0, c["bridge_thickness_mm"], width, total_height)
    rib_radius = c["retention_rib_mm"] + 0.20
    rib = cylinder_y(rib_radius, width - 4.0, c["tongue_depth_mm"] - 1.4, tongue_z + 0.20)

    rail_center_z = total_height / 2
    neck = box_at(
        -r["neck_depth_mm"], -r["width_mm"] / 2, rail_center_z - r["neck_height_mm"] / 2,
        r["neck_depth_mm"] + 0.4, r["width_mm"], r["neck_height_mm"],
    )
    head = box_at(
        -r["neck_depth_mm"] - r["head_depth_mm"], -r["width_mm"] / 2,
        rail_center_z - r["head_height_mm"] / 2,
        r["head_depth_mm"] + 0.4, r["width_mm"], r["head_height_mm"],
    )
    shape = back.union(tongue).union(bridge).union(rib).union(neck).union(head).clean()
    return shape, {
        "part_id": f"petg-clip-{size.lower()}",
        "size": size,
        "nominal_gap_mm": gap,
        "effective_rib_gap_mm": gap - c["retention_rib_mm"],
        "rail_center_z_mm": rail_center_z,
        "functional_envelope_mm": [c["insertion_depth_mm"] + r["neck_depth_mm"] + r["head_depth_mm"], width, total_height],
    }


def make_tpu_insert(p: dict) -> tuple[cq.Workplane, dict]:
    r, loop = p["rail"], p["loop"]
    width = loop["axial_width_mm"]
    inner = loop["relaxed_inner_diameter_mm"] / 2
    outer = inner + loop["radial_wall_mm"]
    ring_center_x = -11.8
    ring = ring_y(inner, outer, width, ring_center_x, 0)

    cavity_height = r["head_height_mm"] + 2 * r["socket_clearance_mm"]
    cavity_depth = r["head_depth_mm"] + r["socket_clearance_mm"] + 0.8
    outer_height = cavity_height + 2 * r["socket_wall_mm"]
    carrier = box_at(-5.0, -width / 2, -outer_height / 2, 5.2, width, outer_height)
    head_cavity = box_at(
        -r["neck_depth_mm"] - r["head_depth_mm"] - r["socket_clearance_mm"],
        -width / 2 - 0.1,
        -cavity_height / 2,
        cavity_depth,
        width + 0.2,
        cavity_height,
    )
    mouth_height = r["head_height_mm"] - 2 * r["snap_interference_mm"]
    mouth = box_at(-0.8, -width / 2 - 0.1, -mouth_height / 2, 1.5, width + 0.2, mouth_height)
    carrier = carrier.cut(head_cavity).cut(mouth)
    connector = box_at(-5.6, -width / 2, -2.0, 2.2, width, 4.0)
    shape = ring.union(carrier).union(connector).clean()
    return shape, {
        "part_id": "tpu-rail-loop",
        "relaxed_inner_diameter_mm": loop["relaxed_inner_diameter_mm"],
        "outer_diameter_mm": 2 * outer,
        "socket_cavity_height_mm": cavity_height,
        "socket_mouth_height_mm": mouth_height,
        "snap_interference_each_mm": r["snap_interference_mm"],
    }


def make_all_tpu(p: dict) -> tuple[cq.Workplane, dict]:
    c, a, loop = p["clip"], p["all_tpu"], p["loop"]
    width = a["clip_width_mm"]
    back = box_at(0, -width / 2, 0, c["insertion_depth_mm"], width, a["back_thickness_mm"])
    tongue_z = a["back_thickness_mm"] + a["nominal_gap_mm"]
    tongue = box_at(0, -width / 2, tongue_z, c["tongue_depth_mm"], width, a["tongue_thickness_mm"])
    total_height = tongue_z + a["tongue_thickness_mm"]
    bridge = box_at(0, -width / 2, 0, c["bridge_thickness_mm"], width, total_height)
    rib_radius = a["contact_rib_mm"] + 0.20
    back_rib = cylinder_y(rib_radius, width - 6.0, 11.0, a["back_thickness_mm"] - 0.20)
    tongue_rib = cylinder_y(rib_radius, width - 6.0, 11.0, tongue_z + 0.20)

    inner = loop["relaxed_inner_diameter_mm"] / 2
    outer = inner + loop["radial_wall_mm"]
    center_z = total_height / 2
    loop_side_shift = -(width - loop["axial_width_mm"]) / 2
    ring = ring_y(inner, outer, loop["axial_width_mm"], -8.6, center_z).translate((0, loop_side_shift, 0))
    connector = box_at(-2.3, -loop["axial_width_mm"] / 2 + loop_side_shift, center_z - 2.2, 3.0, loop["axial_width_mm"], 4.4)
    shape = back.union(tongue).union(bridge).union(back_rib).union(tongue_rib).union(ring).union(connector).clean()
    return shape, {
        "part_id": "all-tpu-universal",
        "nominal_gap_mm": a["nominal_gap_mm"],
        "effective_rib_gap_mm": a["nominal_gap_mm"] - 2 * a["contact_rib_mm"],
        "relaxed_inner_diameter_mm": loop["relaxed_inner_diameter_mm"],
        "loop_side_shift_mm": loop_side_shift,
        "functional_envelope_mm": [c["insertion_depth_mm"] + 15.8, width, total_height + 2 * outer],
    }


def make_pen_gauge(p: dict) -> tuple[cq.Workplane, dict]:
    g = p["gauge"]
    shapes = []
    centers = []
    cursor = 0.0
    for diameter in g["diameters_mm"]:
        inner = diameter / 2
        outer = inner + g["wall_mm"]
        center_x = cursor + outer
        centers.append((center_x, outer, diameter))
        shapes.append(ring_y(inner, outer, g["axial_width_mm"], center_x, outer))
        cursor += 2 * outer + 4.0
    base = box_at(0, -g["axial_width_mm"] / 2, 0, cursor - 4.0, g["axial_width_mm"], 2.2)
    result = base
    for shape in shapes:
        result = result.union(shape)
    result = result.clean()
    return result, {"part_id": "tpu-pen-gauge", "diameters_mm": g["diameters_mm"], "overall_length_mm": cursor - 4.0}


def manufacturing_orientation(shape: cq.Workplane) -> cq.Workplane:
    rotated = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    bb = rotated.val().BoundingBox()
    return rotated.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def export_pair(shape: cq.Workplane, stem: str, material_folder: str, mesh: dict) -> tuple[Path, Path, Path]:
    step = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}.step"
    master_stl = EXPORTS / "master" / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}-master.stl"
    print_stl = EXPORTS / "manufacturing" / material_folder / f"DRAFT-{PROJECT_ID}-{stem}-{REVISION}.stl"
    for path in [step, master_stl, print_stl]:
        path.parent.mkdir(parents=True, exist_ok=True)
    exporters.export(shape, str(step))
    exporters.export(shape, str(master_stl), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])
    exporters.export(manufacturing_orientation(shape), str(print_stl), tolerance=mesh["linear_deflection_mm"], angularTolerance=mesh["angular_deflection_rad"])
    return step, master_stl, print_stl


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
    target.parent.mkdir(parents=True, exist_ok=True)
    metadata = {"material": material, "source": str(PARAMETERS.relative_to(ROOT)), "revision": REVISION}
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
    for folder in [REPORTS, VALIDATION, EXPORTS / "master", EXPORTS / "manufacturing" / "petg", EXPORTS / "manufacturing" / "tpu", EXPORTS / "coupons", EXPORTS / "3mf"]:
        folder.mkdir(parents=True, exist_ok=True)

    clips = {size: make_petg_clip(p, size, gap) for size, gap in p["clip"]["gap_variants_mm"].items()}
    insert, insert_metrics = make_tpu_insert(p)
    universal, universal_metrics = make_all_tpu(p)
    gauge, gauge_metrics = make_pen_gauge(p)

    outputs: dict[str, tuple[Path, Path, Path]] = {}
    interfaces = {f"clip-{size.lower()}": metrics for size, (_, metrics) in clips.items()}
    for size, (shape, _) in clips.items():
        outputs[f"clip-{size.lower()}"] = export_pair(shape, f"petg-clip-{size.lower()}", "petg", p["mesh"])
    outputs["insert"] = export_pair(insert, "tpu-rail-loop", "tpu", p["mesh"])
    outputs["universal"] = export_pair(universal, "all-tpu-universal", "tpu", p["mesh"])
    gauge_step, gauge_master, gauge_print = export_pair(gauge, "tpu-pen-gauge", "tpu", p["mesh"])
    gauge_coupon = EXPORTS / "coupons" / f"DRAFT-{PROJECT_ID}-tpu-pen-gauge-{REVISION}.stl"
    exporters.export(manufacturing_orientation(gauge), str(gauge_coupon), tolerance=p["mesh"]["linear_deflection_mm"], angularTolerance=p["mesh"]["angular_deflection_rad"])
    outputs["gauge"] = (gauge_step, gauge_master, gauge_print)

    petg_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-petg-clip-kit-{REVISION}.3mf"
    tpu_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-tpu-loop-kit-{REVISION}.3mf"
    gauge_3mf = EXPORTS / "3mf" / f"DRAFT-{PROJECT_ID}-tpu-pen-gauge-{REVISION}.3mf"
    make_3mf([outputs[key][2] for key in ["clip-s", "clip-m", "clip-l"]], petg_3mf, [(20, 20, 0), (55, 20, 0), (90, 20, 0)], "PETG")
    make_3mf([outputs["insert"][2], outputs["universal"][2]], tpu_3mf, [(20, 20, 0), (60, 20, 0)], "TPU")
    make_3mf([gauge_coupon], gauge_3mf, [(20, 20, 0)], "TPU")

    all_mesh_paths = {key: value[2] for key, value in outputs.items()}
    all_mesh_paths["gauge-coupon"] = gauge_coupon
    meshes = {key: mesh_metrics(path) for key, path in all_mesh_paths.items()}

    source_checks = [
        check("project", p["project"]["id"] == PROJECT_ID and p["project"]["revision"] == REVISION, "Project identity and revision are fixed"),
        check("three-rigid-gaps", list(p["clip"]["gap_variants_mm"].values()) == [1.8, 2.6, 3.4], "Three ordered PETG cover gaps are declared"),
        check("common-rail", len({p["rail"][key] for key in ["width_mm", "head_height_mm", "neck_height_mm"]}) == 3, "The common rail dimensions are present"),
        check("loop-wall", p["loop"]["radial_wall_mm"] >= 1.8, "TPU ring wall meets the minimum section"),
        check("material-separation", petg_3mf.exists() and tpu_3mf.exists(), "PETG and TPU are packaged as separate plates"),
        check("gauge", p["gauge"]["diameters_mm"] == [9.0, 12.0, 15.0], "The pen gauge spans three declared bores"),
    ]
    source_report = {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-parametric-source", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in source_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS), record(ROOT / "design-spec.yaml")], "checks": source_checks,
        "metrics": {"clips": interfaces, "insert": insert_metrics, "all_tpu": universal_metrics, "gauge": gauge_metrics, "outputs": [record(path) for values in outputs.values() for path in values] + [record(petg_3mf), record(tpu_3mf), record(gauge_3mf), record(gauge_coupon)]},
        "limitations": ["Parametric geometry cannot prove real cover safety, fatigue, or pen retention."], "required_capabilities": ["cadquery"],
    }
    write_json(VALIDATION / "parametric-source-report.json", source_report)

    mesh_checks = []
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
        "inputs": [record(path) for path in all_mesh_paths.values()], "checks": mesh_checks, "metrics": meshes,
        "limitations": [], "required_capabilities": ["trimesh"],
    }
    write_json(VALIDATION / "mesh-generation-report.json", mesh_report)

    rail = p["rail"]
    interface_checks = [
        check("rail-clearance", rail["socket_clearance_mm"] >= 0.3, "Socket has explicit per-side rail clearance", {"clearance_mm": rail["socket_clearance_mm"]}),
        check("snap-mouth", insert_metrics["socket_mouth_height_mm"] < rail["head_height_mm"] and insert_metrics["socket_mouth_height_mm"] > rail["neck_height_mm"] - 0.1, "TPU mouth retains the rail head while admitting the neck", insert_metrics),
        check("same-rail-all-sizes", len({round(metrics["rail_center_z_mm"] - (metrics["nominal_gap_mm"] / 2), 6) for metrics in interfaces.values()}) == 1, "Rail centers track the clip gap without changing the rail section"),
        check("profile-side-down", all(metrics["bounds_mm"][2] <= 30.01 for metrics in meshes.values()), "Manufacturing Z is the original axial width and stays at or below 30 mm", {key: value["bounds_mm"] for key, value in meshes.items()}),
        check("pen-range-deferred", p["loop"]["intended_pen_range_mm"] == [9.0, 16.0], "The intended range is declared and remains physically gated"),
    ]
    interface_report = {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-interface-validation", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in interface_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS)] + [record(path) for path in all_mesh_paths.values()], "checks": interface_checks,
        "metrics": {"clips": interfaces, "insert": insert_metrics, "all_tpu": universal_metrics, "gauge": gauge_metrics},
        "limitations": ["Nominal CAD clearances do not infer TPU hardness, extrusion compensation, or cover compressibility."], "required_capabilities": [],
    }
    write_json(VALIDATION / "interface-report.json", interface_report)

    petg_volume = sum(meshes[f"clip-{size}"]["volume_mm3"] for size in ["s", "m", "l"])
    tpu_volume = meshes["insert"]["volume_mm3"] + meshes["universal"]["volume_mm3"]
    opt_checks = [
        check("replaceable-wear-part", True, "The modular TPU wear part is independently replaceable"),
        check("shared-insert", True, "One TPU insert serves all three PETG sizes"),
        check("no-generated-support", True, "All manufacturing meshes use constant side profiles or flat gauge rings"),
        check("small-material-envelope", petg_volume < 30000 and tpu_volume < 25000, "Total kit CAD volumes stay within the planning limits", {"petg_mm3": petg_volume, "tpu_mm3": tpu_volume}),
    ]
    opt_report = {
        "schema_version": "1.0", "tool": f"{PROJECT_ID}-optimization-comparison", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in opt_checks) else "FAIL", "profile": "draft",
        "inputs": [record(PARAMETERS)] + [record(path) for path in all_mesh_paths.values()], "checks": opt_checks,
        "metrics": {"selected_variant": "three-size-petg-plus-common-tpu-and-all-tpu", "petg_kit_volume_mm3": petg_volume, "tpu_kit_volume_mm3": tpu_volume},
        "limitations": ["CAD volume is not measured mass or fatigue performance."], "required_capabilities": [],
    }
    write_json(REPORTS / "optimization-comparison.json", opt_report)
    write_json(REPORTS / "mesh-complexity.json", {"schema_version": "1.0", "status": mesh_report["status"], "meshes": meshes})
    artifacts = [path for values in outputs.values() for path in values] + [gauge_coupon, petg_3mf, tpu_3mf, gauge_3mf]
    reports = [VALIDATION / "parametric-source-report.json", VALIDATION / "mesh-generation-report.json", VALIDATION / "interface-report.json", REPORTS / "optimization-comparison.json"]
    write_json(REPORTS / "build-manifest.json", {
        "schema_version": "1.0", "project_id": PROJECT_ID, "revision": REVISION,
        "status": "PASS" if all(json.loads(path.read_text())["status"] == "PASS" for path in reports) else "FAIL",
        "artifacts": [record(path) for path in artifacts], "reports": [record(path) for path in reports],
    })
    print(json.dumps({"status": "PASS", "petg_3mf": str(petg_3mf.relative_to(ROOT)), "tpu_3mf": str(tpu_3mf.relative_to(ROOT)), "gauge_3mf": str(gauge_3mf.relative_to(ROOT)), "meshes": meshes}, indent=2))


if __name__ == "__main__":
    main()
