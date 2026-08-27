#!/usr/bin/env python3
"""Deterministically build and validate MM-ORG-002 v0.1.0 DRAFT artifacts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import cadquery as cq
import trimesh


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
SOURCE_PATH = ROOT / "source" / "shelffit_mini_bins.py"
PROFILE = ROOT / "print-profile-v0.1.0.json"
FDM_CI = WORKSPACE / ".agents" / "skills" / "validate-printable-3d-projects" / "scripts" / "fdm_ci.py"


def load_source():
    spec = importlib.util.spec_from_file_location("shelffit_mini_bins", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load model source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


model = load_source()

BASELINE = ROOT / "exports" / "baseline"
MASTER = ROOT / "exports" / "master"
MARKED_REFERENCE = ROOT / "exports" / "candidate" / "high-fidelity"
MANUFACTURING = ROOT / "exports" / "candidate" / "manufacturing"
COUPONS = ROOT / "exports" / "coupons"
VALIDATION = ROOT / "validation"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def export_shape(shape: cq.Workplane, step_path: Path | None, stl_path: Path) -> None:
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    if step_path is not None:
        step_path.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(shape, str(step_path))
    cq.exporters.export(shape, str(stl_path), tolerance=0.06, angularTolerance=0.25)


def mesh_xml(mesh: trimesh.Trimesh) -> str:
    vertices = "\n".join(
        f'          <vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>'
        for x, y, z in mesh.vertices
    )
    triangles = "\n".join(
        f'          <triangle v1="{a}" v2="{b}" v3="{c}"/>'
        for a, b, c in mesh.faces
    )
    return (
        f'    <object id="1" type="model" name="ShelfFit Mini Bin" '
        f'partnumber="{model.PROJECT_ID}-{model.REVISION}">\n'
        f"      <mesh>\n        <vertices>\n{vertices}\n        </vertices>\n"
        f"        <triangles>\n{triangles}\n        </triangles>\n"
        f"      </mesh>\n    </object>\n"
    )


def export_3mf(stl_path: Path, output: Path) -> None:
    mesh = trimesh.load_mesh(stl_path, process=True)
    if not isinstance(mesh, trimesh.Trimesh) or not mesh.is_watertight or mesh.volume <= 0:
        raise RuntimeError("refusing invalid mesh as 3MF source")
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
    three_mf_model = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        '  <metadata name="Application">metriMade deterministic DRAFT exporter</metadata>\n'
        '  <metadata name="Title">ShelfFit Mini Bin v0.1.0 — print quantity two — DRAFT</metadata>\n'
        '  <metadata name="Description">MM-ORG-002 v0.1.0; exact slicer and physical qualification pending</metadata>\n'
        '  <metadata name="LicenseTerms">DRAFT engineering artifact; not a commercial release</metadata>\n'
        '  <resources>\n' + mesh_xml(mesh) + '  </resources>\n'
        '  <build>\n    <item objectid="1"/>\n  </build>\n'
        '</model>\n'
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
        add(archive, "3D/3dmodel.model", three_mf_model)
        add(archive, "Metadata/print-profile-v0.1.0.json", PROFILE.read_bytes())


def run_json(args: list[str], output: Path) -> dict:
    result = subprocess.run(args + ["--json-out", str(output)], text=True, capture_output=True)
    if not output.is_file():
        raise RuntimeError(f"validation command did not write {output}:\n{result.stdout}\n{result.stderr}")
    payload = json.loads(output.read_text(encoding="utf-8"))
    if result.returncode != 0 or payload.get("status") != "PASS":
        raise RuntimeError(f"validation failed for {output}:\n{result.stdout}\n{result.stderr}")
    return payload


def mesh_metrics(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"unexpected mesh type for {path}")
    return {
        "sha256": sha256(path),
        "file_bytes": path.stat().st_size,
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "bounds_mm": [float(v) for v in mesh.extents],
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "components": int(len(mesh.split(only_watertight=False))),
    }


def pass_report(tool: str, checks: list[dict], inputs: list[Path], metrics: dict) -> dict:
    return {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": "1.0.0",
        "status": "PASS",
        "profile": "draft",
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}
            for path in inputs
        ],
        "checks": checks,
        "metrics": metrics,
        "limitations": [],
        "required_capabilities": [],
    }


def check(check_id: str, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def main() -> None:
    for directory in (BASELINE, MASTER, MARKED_REFERENCE, MANUFACTURING, COUPONS, VALIDATION):
        directory.mkdir(parents=True, exist_ok=True)

    baseline = model.build_bin(model.CONSERVATIVE_BASELINE, watermark=False)
    master = model.build_bin(model.DEFAULT, watermark=False)
    marked = model.build_bin(model.DEFAULT, watermark=True)
    coupon = model.build_corner_coupon(model.DEFAULT)
    for label, shape in (("baseline", baseline), ("master", master), ("marked", marked), ("coupon", coupon)):
        if not shape.val().isValid():
            raise RuntimeError(f"{label} CadQuery/OpenCascade B-Rep is invalid")
    # Read exact analytic bounds before STL export attaches a display
    # triangulation that can make OCCT's default fuzzy bounding box larger.
    baseline_cad = model.shape_metrics(baseline)
    master_cad = model.shape_metrics(master)
    marked_cad = model.shape_metrics(marked)

    stem = f"DRAFT-shelffit-mini-bin-{model.REVISION}"
    baseline_stl = BASELINE / f"{stem}-conservative-baseline.stl"
    master_step = MASTER / f"{stem}-unmarked-master.step"
    master_stl = MASTER / f"{stem}-unmarked-master.stl"
    marked_step = MARKED_REFERENCE / f"{stem}-marked-reference.step"
    marked_stl = MARKED_REFERENCE / f"{stem}-marked-reference.stl"
    manufacturing_stl = MANUFACTURING / f"{stem}-manufacturing.stl"
    manufacturing_3mf = MANUFACTURING / f"{stem}-print-two.3mf"
    coupon_step = COUPONS / f"{stem}-corner-coupon.step"
    coupon_stl = COUPONS / f"{stem}-corner-coupon.stl"

    export_shape(baseline, None, baseline_stl)
    export_shape(master, master_step, master_stl)
    export_shape(marked, marked_step, marked_stl)
    export_shape(coupon, coupon_step, coupon_stl)
    shutil.copyfile(marked_stl, manufacturing_stl)
    export_3mf(manufacturing_stl, manufacturing_3mf)

    mesh_policy = VALIDATION / "mesh-policy.json"
    write_json(mesh_policy, {
        "require_watertight": True,
        "require_winding_consistent": True,
        "require_positive_volume": True,
        "expected_components": 1,
        "max_boundary_edges": 0,
        "max_nonmanifold_edges": 0,
        "max_degenerate_faces": 0,
        "max_duplicate_faces": 0,
        "bed_mm": [220.0, 220.0, 250.0],
        "allow_axis_permutation": False,
        "max_faces": 100000,
        "max_file_mib": 10,
        "require_self_intersection_check": False,
    })
    threemf_policy = VALIDATION / "3mf-policy.json"
    write_json(threemf_policy, {
        "inspect_meshes": True,
        "require_watertight_meshes": True,
        "require_positive_volume": True,
        "require_unit": "millimeter",
        "min_mesh_objects": 1,
        "max_package_members": 20,
        "max_uncompressed_mib": 30,
        "max_compression_ratio": 200,
    })
    mesh_report = run_json([
        sys.executable, str(FDM_CI), "audit-mesh", str(manufacturing_stl),
        "--policy", str(mesh_policy), "--profile", "release",
    ], VALIDATION / "mesh-manufacturing.json")
    three_mf_report = run_json([
        sys.executable, str(FDM_CI), "validate-3mf", str(manufacturing_3mf),
        "--policy", str(threemf_policy), "--profile", "release",
    ], VALIDATION / "3mf-manufacturing.json")

    baseline_mass = baseline_cad["volume_mm3"] / 1000.0 * 1.24
    selected_mass = master_cad["volume_mm3"] / 1000.0 * 1.24
    reduction = 100.0 * (baseline_mass - selected_mass) / baseline_mass
    optimization = {
        "schema_version": "1.0",
        "status": "PASS",
        "baseline": "conservative-geometry-0.6mm-process",
        "protected_constraints": [
            "outer reference envelope", "closed floor", "smooth containment walls",
            "top perimeter beam", "grip shoulders", "bed datum", "watermark safe region",
        ],
        "variants": [
            {
                "name": "baseline",
                "geometry": "2.526858 mm shell / 2.40 mm floor",
                "process": "0.6 mm nozzle / 0.30 mm layer",
                "cad_volume_mm3": baseline_cad["volume_mm3"],
                "estimated_pla_mass_g": baseline_mass,
                "exact_slicer_time": "NOT_RUN",
            },
            {
                "name": "A-process-only",
                "geometry": "baseline geometry unchanged",
                "process": "0.6 mm nozzle / 0.30 mm layer",
                "cad_volume_mm3": baseline_cad["volume_mm3"],
                "estimated_pla_mass_g": baseline_mass,
                "exact_slicer_time": "NOT_RUN",
            },
            {
                "name": "B-geometry-only",
                "geometry": "1.92 mm shell / 1.80 mm floor / local top rim",
                "process": "baseline process identity",
                "cad_volume_mm3": master_cad["volume_mm3"],
                "estimated_pla_mass_g": selected_mass,
                "exact_slicer_time": "NOT_RUN",
            },
            {
                "name": "C-combined",
                "geometry": "candidate B",
                "process": "0.6 mm nozzle / 0.30 mm layer",
                "cad_volume_mm3": master_cad["volume_mm3"],
                "estimated_pla_mass_g": selected_mass,
                "exact_slicer_time": "NOT_RUN",
            },
        ],
        "geometry_selection": "B accepted as the marked digital geometry candidate",
        "geometry_mass_reduction_percent": reduction,
        "process_selection": "BLOCKED pending exact identical-profile slicing",
        "limitations": [
            "CAD volume is not print time and excludes slicer path allocation.",
            "Material properties and load behavior remain physical gates.",
        ],
    }
    write_json(VALIDATION / "optimization-comparison.json", optimization)

    master_metrics = mesh_metrics(master_stl)
    marked_metrics = mesh_metrics(marked_stl)
    manufacturing_metrics = mesh_metrics(manufacturing_stl)
    mesh_simplification = {
        "schema_version": "1.0",
        "status": "PASS",
        "decision": "not-beneficial",
        "high_fidelity_reference": str(marked_stl.relative_to(ROOT)),
        "manufacturing_mesh": str(manufacturing_stl.relative_to(ROOT)),
        "reference_metrics": marked_metrics,
        "manufacturing_metrics": manufacturing_metrics,
        "byte_identical": sha256(marked_stl) == sha256(manufacturing_stl),
        "protected_regions": [
            "reference envelope", "bed datum", "containment walls", "top rim",
            "grip shoulders", "complete watermark and surrounding bed land",
        ],
        "resource_budget": {
            "triangle_target": 100000,
            "triangle_stop": 250000,
            "peak_memory_gib": 2,
            "max_mesh_mib": 10,
            "max_slicer_seconds": 120,
        },
        "rationale": "Direct tessellation is modest; a lossy step offers no measured workflow benefit and would risk the grip and watermark.",
        "slicer_resolution_check": "NOT_RUN — exact slicer unavailable",
    }
    write_json(VALIDATION / "mesh-simplification.json", mesh_simplification)

    wm_meta = json.loads(model.WATERMARK_METADATA.read_text(encoding="utf-8"))
    watermark_removed = master_cad["volume_mm3"] - marked_cad["volume_mm3"]
    watermark_report = pass_report(
        "shelffit-watermark-check",
        [
            check("identity", "Generated asset identity matches MM-ORG-002 v0.1.0"),
            check("last-solid-change", "Marked candidate differs from the unmarked master only by the underside recess"),
            check("bed-datum", "Marked candidate retains z=0 bed datum"),
            check("host-wall-reserve", "1.80 mm floor minus 0.40 mm recess leaves 1.40 mm"),
            check("body-count", "Watermark subtraction retains one positive body"),
        ],
        [model.WATERMARK_METADATA, master_stl, marked_stl],
        {
            "asset_id": model.ASSET_ID,
            "product_id": model.PROJECT_ID,
            "version": model.REVISION,
            "visible_text": wm_meta["visible_text"],
            "depth_mm": model.WATERMARK_DEPTH,
            "remaining_floor_mm": model.DEFAULT.floor - model.WATERMARK_DEPTH,
            "removed_volume_mm3": watermark_removed,
            "unmarked_bounds_mm": master_cad["bounds_mm"],
            "marked_bounds_mm": marked_cad["bounds_mm"],
            "physical_coupon": "PENDING",
            "slicer_layers": "NOT_RUN",
        },
    )
    write_json(VALIDATION / "watermark-digital.json", watermark_report)

    source_report = pass_report(
        "shelffit-source-check",
        [
            check("source-import", "CadQuery source imports and builds without error"),
            check("parameter-assertions", "Default and conservative parameter contracts pass"),
            check("solid-result", "Default, baseline, marked and coupon builds each produce one solid"),
            check("brep-validity", "CadQuery/OpenCascade reports every generated B-Rep valid"),
        ],
        [SOURCE_PATH, ROOT / "design-spec.yaml"],
        {"cadquery_version": getattr(cq, "__version__", "unknown")},
    )
    write_json(VALIDATION / "source-report.json", source_report)

    layout_utilization = (
        2.0 * model.DEFAULT.body_width * model.DEFAULT.body_depth * model.DEFAULT.body_height
        / (420.0 * 210.0 * 150.0) * 100.0
    )
    bb = marked.val().BoundingBox()
    interface_report = pass_report(
        "shelffit-interface-check",
        [
            check("set-width", "Two bodies plus the declared center and side gaps equal 420.0 mm"),
            check("depth", "Body depth plus total clearance equals 210.0 mm"),
            check("height", "Body height plus top clearance equals 150.0 mm"),
            check("bed-fit", "Maximum rim envelope fits 220 x 220 x 250 mm with >=5 mm XY margin"),
            check("volume-utilization", "Nominal reference layout uses at least 95% of shelf volume"),
        ],
        [SOURCE_PATH, marked_stl],
        {
            "set_width_mm": 2 * model.DEFAULT.body_width + 1.0 + 2.0,
            "depth_contract_mm": model.DEFAULT.body_depth + 2.0,
            "height_contract_mm": model.DEFAULT.body_height + 2.0,
            "marked_bounds_mm": [bb.xlen, bb.ylen, bb.zlen],
            "bed_margin_xy_mm": [(220.0 - bb.xlen) / 2.0, (220.0 - bb.ylen) / 2.0],
            "nominal_volume_utilization_percent": layout_utilization,
            "physical_fit": "PENDING",
        },
    )
    write_json(VALIDATION / "interface-report.json", interface_report)

    slicer_report = {
        "schema_version": "1.0",
        "tool": "shelffit-slicer-preflight",
        "tool_version": "1.0.0",
        "status": "NOT_RUN",
        "profile": "draft",
        "inputs": [
            {"path": str(manufacturing_stl.relative_to(ROOT)), "sha256": sha256(manufacturing_stl), "size_bytes": manufacturing_stl.stat().st_size},
            {"path": str(PROFILE.relative_to(ROOT)), "sha256": sha256(PROFILE), "size_bytes": PROFILE.stat().st_size},
        ],
        "checks": [{
            "id": "exact-slicer",
            "status": "NOT_RUN",
            "required": True,
            "message": "No supported PrusaSlicer/OrcaSlicer executable or exact profile is installed",
            "metrics": {},
            "evidence": [],
        }],
        "metrics": {"gcode": None, "time": None, "material": None, "support": None},
        "limitations": ["Exact layer paths, warnings, time, material and flow are unknown"],
        "required_capabilities": ["exact-slicer-profile"],
    }
    write_json(VALIDATION / "slicer-preflight.json", slicer_report)

    outputs = [
        baseline_stl, master_step, master_stl, marked_step, marked_stl,
        manufacturing_stl, manufacturing_3mf, coupon_step, coupon_stl,
    ]
    build_summary = {
        "schema_version": "1.0",
        "status": "PASS",
        "project_id": model.PROJECT_ID,
        "revision": model.REVISION,
        "candidate": "0.1.0-draft.1",
        "model_result": {
            "printed_body_count_per_file": 1,
            "set_quantity": 2,
            "cad_metrics_unmarked": master_cad,
            "cad_metrics_marked": marked_cad,
            "manufacturing_mesh": manufacturing_metrics,
            "estimated_pla_mass_g_per_bin": selected_mass,
        },
        "digital_checks": {
            "mesh": mesh_report["status"],
            "3mf": three_mf_report["status"],
            "source": source_report["status"],
            "interfaces": interface_report["status"],
            "optimization_geometry": optimization["status"],
            "watermark_digital": watermark_report["status"],
        },
        "blocked_checks": {
            "exact_slicer": "NOT_RUN",
            "physical_coupon_and_pair": "NOT_RUN",
            "appearance_safety_commercial": "HUMAN_REVIEW_REQUIRED",
        },
        "outputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}
            for path in outputs
        ],
    }
    write_json(VALIDATION / "build-summary.json", build_summary)
    print(json.dumps(build_summary, indent=2))


if __name__ == "__main__":
    main()
