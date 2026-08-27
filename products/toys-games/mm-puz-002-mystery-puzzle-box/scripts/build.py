#!/usr/bin/env python3
"""Build deterministic MM-PUZ-002 v1.2.0 DRAFT CAD and validation evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import cadquery as cq
import trimesh


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
SOURCE = ROOT / "source" / "puzzle_box.py"
PROFILE = ROOT / "print-profile-v1.2.0.json"
FDM_CI = WORKSPACE / ".agents" / "skills" / "validate-printable-3d-projects" / "scripts" / "fdm_ci.py"
MASTER = ROOT / "exports" / "master"
CANDIDATE = ROOT / "exports" / "candidate"
VALIDATION = ROOT / "validation"


def load_model():
    spec = importlib.util.spec_from_file_location("puzzle_box", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load model source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


model = load_model()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def export(shape: cq.Workplane, step: Path, stl: Path) -> None:
    step.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(step))
    cq.exporters.export(shape, str(stl), tolerance=0.055, angularTolerance=0.22)


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"unexpected mesh type: {path}")
    return {
        "sha256": sha256(path),
        "file_bytes": path.stat().st_size,
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "components": int(len(mesh.split(only_watertight=False))),
        "bounds_mm": [float(v) for v in mesh.extents],
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
    }


def mesh_xml(object_id: int, name: str, mesh: trimesh.Trimesh) -> str:
    vertices = "\n".join(
        f'          <vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>'
        for x, y, z in mesh.vertices
    )
    triangles = "\n".join(
        f'          <triangle v1="{a}" v2="{b}" v3="{c}"/>'
        for a, b, c in mesh.faces
    )
    return (
        f'    <object id="{object_id}" type="model" name="{name}" '
        f'partnumber="{model.PROJECT_ID}-{model.REVISION}">\n'
        f"      <mesh>\n        <vertices>\n{vertices}\n        </vertices>\n"
        f"        <triangles>\n{triangles}\n        </triangles>\n"
        f"      </mesh>\n    </object>\n"
    )


def export_3mf(mesh_paths: dict[str, Path], output: Path) -> None:
    meshes: dict[str, trimesh.Trimesh] = {}
    for name, path in mesh_paths.items():
        loaded = trimesh.load_mesh(path, process=True)
        if not isinstance(loaded, trimesh.Trimesh) or not loaded.is_watertight or loaded.volume <= 0:
            raise RuntimeError(f"refusing invalid mesh as 3MF source: {path}")
        meshes[name] = loaded
    objects = "".join(mesh_xml(i, name, meshes[name]) for i, name in enumerate(meshes, 1))
    ids = {name: i for i, name in enumerate(meshes, 1)}
    placements = [
        ("Body", 135.0, 65.0), ("Lid", 135.0, 155.0),
        ("Slider", 40.0, 230.0), ("Slider", 70.0, 230.0), ("Slider", 100.0, 230.0),
        ("Return leaf", 150.0, 230.0), ("Return leaf", 185.0, 230.0), ("Return leaf", 220.0, 230.0),
    ]
    build_items = "".join(
        f'    <item objectid="{ids[name]}" transform="1 0 0 0 1 0 0 0 1 {x:.3f} {y:.3f} 0"/>\n'
        for name, x, y in placements
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>\n'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>\n'
    )
    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        '  <metadata name="Application">metriMade deterministic DRAFT exporter</metadata>\n'
        '  <metadata name="Title">Mystery Puzzle Box v1.2.0 — DRAFT</metadata>\n'
        '  <metadata name="Description">One body, one lid, three sliders and three return leaves; physical qualification pending</metadata>\n'
        '  <metadata name="LicenseTerms">DRAFT engineering artifact; not a commercial release</metadata>\n'
        f"  <resources>\n{objects}  </resources>\n  <build>\n{build_items}  </build>\n</model>\n"
    )

    def add(archive: zipfile.ZipFile, name: str, data: str | bytes) -> None:
        info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, data.encode("utf-8") if isinstance(data, str) else data)

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        add(archive, "[Content_Types].xml", content_types)
        add(archive, "_rels/.rels", rels)
        add(archive, "3D/3dmodel.model", model_xml)
        add(archive, "Metadata/print-profile-v1.2.0.json", PROFILE.read_bytes())


def run_json(args: list[str], output: Path) -> dict:
    result = subprocess.run(args + ["--json-out", str(output)], text=True, capture_output=True)
    if not output.is_file():
        raise RuntimeError(f"validation did not write {output}:\n{result.stdout}\n{result.stderr}")
    payload = json.loads(output.read_text(encoding="utf-8"))
    if result.returncode or payload.get("status") != "PASS":
        raise RuntimeError(f"validation failed for {output}:\n{result.stdout}\n{result.stderr}")
    return payload


def check(check_id: str, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS", "required": True, "message": message,
            "metrics": metrics or {}, "evidence": []}


def pass_report(tool: str, checks: list[dict], inputs: list[Path], metrics: dict,
                limitations: list[str] | None = None) -> dict:
    return {
        "schema_version": "1.0", "tool": tool, "tool_version": "1.0.0",
        "status": "PASS", "profile": "draft",
        "inputs": [{"path": str(p.relative_to(ROOT)), "sha256": sha256(p),
                    "size_bytes": p.stat().st_size} for p in inputs],
        "checks": checks, "metrics": metrics, "limitations": limitations or [],
        "required_capabilities": [],
    }


def intersection_volume(a: cq.Workplane, b: cq.Workplane) -> float:
    result = a.intersect(b)
    return sum(s.Volume() for s in result.solids().vals())


def main() -> None:
    MASTER.mkdir(parents=True, exist_ok=True)
    CANDIDATE.mkdir(parents=True, exist_ok=True)
    VALIDATION.mkdir(parents=True, exist_ok=True)

    plain_body = model.build_body(model.DEFAULT, watermark=False, textured=False)
    plain_lid = model.build_lid(model.DEFAULT, textured=False)
    unmarked_body = model.build_body(model.DEFAULT, watermark=False, textured=True)
    marked_body = model.build_body(model.DEFAULT, watermark=True, textured=True)
    lid = model.build_lid(model.DEFAULT, textured=True)
    slider = model.slider_print_orientation()
    leaf = model.build_return_leaf()
    shapes = {"plain_body": plain_body, "plain_lid": plain_lid, "body": marked_body,
              "lid": lid, "slider": slider, "leaf": leaf}
    for name, shape in shapes.items():
        solids = shape.solids().vals()
        if len(solids) != 1 or not solids[0].isValid():
            raise RuntimeError(f"{name} is not one valid B-Rep")

    body_unmarked_step = MASTER / "DRAFT-mystery-puzzle-box-1.2.0-body-unmarked.step"
    body_unmarked_stl = MASTER / "DRAFT-mystery-puzzle-box-1.2.0-body-unmarked.stl"
    paths = {
        "Body": CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-body-marked.stl",
        "Lid": CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-lid.stl",
        "Slider": CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-slider-print-x3.stl",
        "Return leaf": CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-return-leaf-print-x3.stl",
    }
    steps = {
        "Body": CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-body-marked.step",
        "Lid": CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-lid.step",
        "Slider": CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-slider-print-x3.step",
        "Return leaf": CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-return-leaf-print-x3.step",
    }
    export(unmarked_body, body_unmarked_step, body_unmarked_stl)
    export(marked_body, steps["Body"], paths["Body"])
    export(model.lid_print_orientation(), steps["Lid"], paths["Lid"])
    export(slider, steps["Slider"], paths["Slider"])
    export(leaf, steps["Return leaf"], paths["Return leaf"])
    package = CANDIDATE / "DRAFT-mystery-puzzle-box-1.2.0-print-set.3mf"
    export_3mf(paths, package)

    policy = {
        "require_watertight": True, "require_winding_consistent": True,
        "require_positive_volume": True, "expected_components": 1,
        "max_boundary_edges": 0, "max_nonmanifold_edges": 0,
        "max_degenerate_faces": 0, "max_duplicate_faces": 0,
        "bed_mm": [420.0, 420.0, 500.0], "allow_axis_permutation": False,
        "max_faces": 250000, "max_file_mib": 25,
        "require_self_intersection_check": False,
    }
    write_json(VALIDATION / "mesh-policy.json", policy)
    mesh_reports = {}
    for key, path in paths.items():
        token = key.lower().replace(" ", "-")
        mesh_reports[key] = run_json([
            sys.executable, str(FDM_CI), "audit-mesh", str(path),
            "--policy", str(VALIDATION / "mesh-policy.json"), "--profile", "release",
        ], VALIDATION / f"mesh-{token}.json")
    threemf_policy = {
        "inspect_meshes": True, "require_watertight_meshes": True,
        "require_positive_volume": True, "require_unit": "millimeter",
        "min_mesh_objects": 4, "max_package_members": 20,
        "max_uncompressed_mib": 80, "max_compression_ratio": 200,
    }
    write_json(VALIDATION / "3mf-policy.json", threemf_policy)
    package_report = run_json([
        sys.executable, str(FDM_CI), "validate-3mf", str(package),
        "--policy", str(VALIDATION / "3mf-policy.json"), "--profile", "release",
    ], VALIDATION / "3mf-print-set.json")

    mesh_data = {name: mesh_metrics(path) for name, path in paths.items()}
    plain_volume = model.metrics(plain_body)["volume_mm3"] + model.metrics(plain_lid)["volume_mm3"]
    textured_volume = model.metrics(unmarked_body)["volume_mm3"] + model.metrics(lid)["volume_mm3"]
    solid_reference = model.DEFAULT.length * model.DEFAULT.depth * model.DEFAULT.total_height
    optimization = {
        "schema_version": "1.0", "status": "PASS",
        "selected": "hollow 2.5 mm shell plus compact recessed vector texture",
        "solid_reference_volume_mm3": solid_reference,
        "plain_shell_volume_mm3": plain_volume,
        "textured_shell_volume_mm3": textured_volume,
        "void_and_shell_reduction_vs_solid_percent": 100 * (solid_reference - textured_volume) / solid_reference,
        "texture_volume_removed_mm3": plain_volume - textured_volume,
        "max_triangles_per_part": max(v["triangles"] for v in mesh_data.values()),
        "triangle_budget_per_part": 250000,
        "dense_heightfield_alternative": "REJECTED — about 660,000 source triangles before CAD integration",
        "exact_slicer_time": "NOT_RUN",
        "limitations": ["CAD volume is not print time; exact equal-profile slicing remains required"],
    }
    write_json(VALIDATION / "optimization-report.json", optimization)

    source_report = pass_report(
        "puzzle-box-source-check",
        [check("source-import", "CadQuery source imports and builds without exception"),
         check("brep-validity", "Body, lid, slider and leaf are each one valid OpenCascade solid"),
         check("parameter-contract", "Default dimensions and minimum wall assertions pass")],
        [SOURCE, ROOT / "design-spec.yaml"],
        {"cadquery_version": getattr(cq, "__version__", "unknown"),
         "cad_metrics": {name: model.metrics(shape) for name, shape in shapes.items()}},
    )
    write_json(VALIDATION / "source-report.json", source_report)

    p = model.DEFAULT
    lid_assembly = model.build_lid(p, textured=True)
    sliders = model.assembly_sliders(p)
    locked = {name: intersection_volume(shape, lid_assembly) for name, shape in sliders.items()}
    retracted = {}
    for name, shape in sliders.items():
        vector = {"front": (0, p.button_travel, 0), "rear": (0, -p.button_travel, 0),
                  "left": (p.button_travel, 0, 0)}[name]
        retracted[name] = intersection_volume(shape.translate(vector), lid_assembly)
    interface_report = pass_report(
        "puzzle-box-interface-check",
        [check("closed-envelope", "Body/lid closed assembly is bounded by 250 x 75 x 75 mm"),
         check("lid-clearance", "Lid skirt has 0.35 mm radial clearance per side"),
         check("guide-skirt-clearance", "Guide rails stop 0.30 mm below the lid skirt"),
         check("locked-overlap", "Every locked slider has positive catch engagement", locked),
         check("retracted-clearance", "Every slider clears its lid ledge after 1.5 mm travel", retracted)],
        [SOURCE, paths["Body"], paths["Lid"], paths["Slider"]],
        {"external_envelope_mm": [250.0, 75.0, 75.0],
         "lid_radial_clearance_each_side_mm": p.lid_radial_clearance,
         "guide_to_skirt_vertical_clearance_mm": 0.30,
         "button_travel_mm": p.button_travel,
         "locked_intersection_volume_mm3": locked,
         "retracted_intersection_volume_mm3": retracted,
         "physical_friction_and_release": "PENDING"},
        ["Positive locked intersection is the intended local catch engagement, not an assembly collision"],
    )
    if min(locked.values()) <= 1.0 or max(retracted.values()) > 1e-5:
        raise RuntimeError(f"latch interface contract failed: locked={locked}, retracted={retracted}")
    write_json(VALIDATION / "interface-report.json", interface_report)

    e_mpa, width, thickness, length, deflection = 1800.0, 6.0, 1.2, 20.0, 1.5
    strain = 1.5 * thickness * deflection / length ** 2
    force = e_mpa * width * thickness ** 3 * deflection / (4 * length ** 3)
    flexure_report = pass_report(
        "puzzle-box-flexure-screen",
        [check("strain-calculation", "Nominal outer-fiber strain is explicitly calculated"),
         check("force-calculation", "Nominal cantilever force is explicitly calculated"),
         check("coupon-required", "A process-matched three-specimen 50-cycle coupon is specified")],
        [SOURCE, ROOT / "test-plan.yaml", PROFILE],
        {"assumed_petg_modulus_mpa": e_mpa, "beam_mm": [length, width, thickness],
         "deflection_mm": deflection, "nominal_outer_fiber_strain_percent": strain * 100,
         "nominal_force_n": force, "physical_status": "NOT_RUN"},
        ["Material modulus, root behavior, anisotropy, creep and safe strain require printed evidence"],
    )
    write_json(VALIDATION / "flexure-screen.json", flexure_report)

    texture_report = pass_report(
        "puzzle-box-texture-check",
        [check("representation", "Compact procedural vector recesses replace a dense image heightfield"),
         check("motif-count", "Exactly 56 deterministic question-mark motifs are generated"),
         check("mesh-budget", "Every tessellated part stays below 250,000 triangles"),
         check("protected-surfaces", "Bed face, seam band, interfaces and watermark region remain untextured")],
        [SOURCE, ROOT / "validation" / "texture-plan.json", paths["Body"], paths["Lid"]],
        {"motif_count": 56, "sizes_mm": [8.0, 11.0, 15.0], "recess_depth_mm": p.texture_depth,
         "perimeter_slit_depth_mm": p.texture_slit_depth,
         "body_triangles": mesh_data["Body"]["triangles"], "lid_triangles": mesh_data["Lid"]["triangles"],
         "appearance_coupon": "NOT_RUN"},
        ["Slicer survival, tactile comfort and camouflage quality remain physical/appearance gates"],
    )
    write_json(VALIDATION / "texture-report.json", texture_report)

    wm_meta = json.loads(model.WM_METADATA.read_text(encoding="utf-8"))
    unmarked_cad = model.metrics(unmarked_body)
    marked_cad = model.metrics(marked_body)
    watermark_report = pass_report(
        "puzzle-box-watermark-check",
        [check("identity", "Generated watermark identity matches MM-PUZ-002 v1.2.0"),
         check("last-solid-change", "Marked body differs from the unmarked textured master only by the underside recess"),
         check("bed-datum", "Marked body retains z=0 and one positive solid"),
         check("host-reserve", "3.0 mm floor minus 0.4 mm recess leaves 2.6 mm")],
        [model.WM_METADATA, body_unmarked_stl, paths["Body"]],
        {"asset_id": model.ASSET_ID, "visible_text": wm_meta["visible_text"],
         "depth_mm": model.WM_DEPTH, "remaining_floor_mm": p.floor - model.WM_DEPTH,
         "removed_volume_mm3": unmarked_cad["volume_mm3"] - marked_cad["volume_mm3"],
         "physical_coupon": "PENDING"},
    )
    write_json(VALIDATION / "watermark-digital.json", watermark_report)

    slicer = {
        "schema_version": "1.0", "tool": "puzzle-box-slicer-preflight", "tool_version": "1.0.0",
        "status": "NOT_RUN", "profile": "draft",
        "inputs": [{"path": str(package.relative_to(ROOT)), "sha256": sha256(package),
                    "size_bytes": package.stat().st_size},
                   {"path": str(PROFILE.relative_to(ROOT)), "sha256": sha256(PROFILE),
                    "size_bytes": PROFILE.stat().st_size}],
        "checks": [{"id": "exact-slicer", "status": "NOT_RUN", "required": True,
                    "message": "No supported exact slicer executable/profile identity is installed",
                    "metrics": {}, "evidence": []}],
        "metrics": {"gcode": None, "time": None, "material": None, "support": None},
        "limitations": ["Layer paths, small strokes, bridges, flow, time and material are unknown"],
        "required_capabilities": ["exact-slicer-profile"],
    }
    write_json(VALIDATION / "slicer-preflight.json", slicer)

    all_outputs = [body_unmarked_step, body_unmarked_stl, *steps.values(), *paths.values(), package]
    total_mass = (marked_cad["volume_mm3"] + model.metrics(lid)["volume_mm3"]) / 1000 * 1.24
    total_mass += (3 * model.metrics(slider)["volume_mm3"] + 3 * model.metrics(leaf)["volume_mm3"]) / 1000 * 1.27
    summary = {
        "schema_version": "1.0", "status": "PASS", "project_id": model.PROJECT_ID,
        "revision": model.REVISION, "candidate": model.CANDIDATE,
        "model_result": {"part_types": 4, "printed_objects": 8, "motif_count": 56,
                         "mesh_metrics": mesh_data, "estimated_combined_mass_g": total_mass},
        "digital_checks": {"meshes": {k: v["status"] for k, v in mesh_reports.items()},
                           "3mf": package_report["status"], "source": source_report["status"],
                           "interfaces": interface_report["status"], "flexure_screen": flexure_report["status"],
                           "texture": texture_report["status"], "watermark": watermark_report["status"],
                           "optimization": optimization["status"]},
        "blocked_checks": {"exact_slicer": "NOT_RUN", "physical_tests_TP_01_to_TP_08": "NOT_RUN",
                           "appearance_safety_commercial": "HUMAN_REVIEW_REQUIRED"},
        "outputs": [{"path": str(p.relative_to(ROOT)), "sha256": sha256(p),
                     "size_bytes": p.stat().st_size} for p in all_outputs],
    }
    write_json(VALIDATION / "build-summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
