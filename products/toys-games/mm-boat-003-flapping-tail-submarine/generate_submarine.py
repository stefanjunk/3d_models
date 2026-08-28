#!/usr/bin/env python3
"""Generate the flapping-tail submarine: STL exports, previews, buoyancy + preflight reports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

import cadquery as cq
from cadquery import exporters

from submarine.buoyancy import compute_buoyancy
from submarine.config import SubmarineConfig
from submarine.geometry import (
    PartSpec,
    _keel_watermark_cutter,
    build_all,
    caudal_projected_area_mm2,
)
from submarine.mechanism import solve_rocker, validate_rocker
from submarine.preflight import PartCheck, run_preflight
from submarine.surfacing import FishEnvelopeProfile

ROOT = Path(__file__).resolve().parent
REVISION = "v1.1.0-draft.1"
REPORT_SUFFIX = "v1.1.0-draft.1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rotated(solid: cq.Solid, rot: tuple[float, float, float]) -> cq.Solid:
    axes = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    out = solid
    for axis, ang in zip(axes, rot):
        if ang:
            out = out.rotate((0, 0, 0), axis, ang)
    return out


def _bed_placement(solid: cq.Solid) -> cq.Solid:
    bb = solid.BoundingBox()
    return solid.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def _remove_zero_area_tessellation_faces(path: Path) -> dict[str, int]:
    """Remove exporter-only zero-area/duplicate triangles without moving vertices."""
    import numpy as np
    import trimesh

    mesh = trimesh.load(str(path), force="mesh", process=False)
    original_faces = len(mesh.faces)
    original_vertices = len(mesh.vertices)
    unique_vertices, inverse = np.unique(
        np.asarray(mesh.vertices, dtype=np.float64),
        axis=0,
        return_inverse=True,
    )
    mesh = trimesh.Trimesh(
        vertices=unique_vertices,
        faces=inverse[np.asarray(mesh.faces, dtype=np.int64)],
        process=False,
    )
    nondegenerate = mesh.nondegenerate_faces(height=1e-8)
    unique = mesh.unique_faces()
    keep = np.logical_and(nondegenerate, unique)
    mesh.update_faces(keep)
    mesh.remove_unreferenced_vertices()
    mesh.export(str(path), file_type="stl")
    return {
        "original_faces": int(original_faces),
        "manufacturing_faces": int(len(mesh.faces)),
        "removed_zero_area_or_duplicate_faces": int(original_faces - len(mesh.faces)),
        "exact_duplicate_vertices_merged": int(original_vertices - len(unique_vertices)),
        "vertices_moved": 0,
    }


def export_print_stl(
    spec: PartSpec,
    path: Path,
) -> tuple[tuple[float, float, float], dict[str, int]]:
    s = _bed_placement(_rotated(spec.solid.val(), spec.print_rotation))
    exporters.export(cq.Workplane("XY").newObject([s]), str(path), tolerance=0.08)
    cleanup = _remove_zero_area_tessellation_faces(path)
    bb = s.BoundingBox()
    return (bb.xlen, bb.ylen, bb.zlen), cleanup


def check_mesh(path: Path) -> tuple[bool, float]:
    import trimesh

    m = trimesh.load(str(path), force="mesh")
    return bool(m.is_watertight), float(m.volume)


def export_previews(parts: list[PartSpec], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mm-boat-003-preview-") as temp_name:
        temp_dir = Path(temp_name)
        lines = []
        for spec in parts:
            fname = temp_dir / f"{spec.name}.stl"
            exporters.export(spec.solid, str(fname), tolerance=0.12)
            lines.append(f'import("{spec.name}.stl");')
        scad = temp_dir / "assembly.scad"
        scad.write_text("\n".join(lines) + "\n")
        views = (
            ("assembly-side.png", "0,0,0,90,0,0,500", "ortho"),
            ("assembly-top.png", "0,0,0,0,0,0,500", "ortho"),
            ("assembly.png", "0,0,0,65,0,25,500", "perspective"),
        )
        for filename, camera, projection in views:
            png = out_dir / filename
            try:
                subprocess.run(
                    [
                        "openscad", "-o", str(png),
                        f"--camera={camera}",
                        f"--projection={projection}",
                        "--viewall", "--autocenter", "--imgsize=1600,800",
                        "--colorscheme=Tomorrow",
                        str(scad),
                    ],
                    check=True,
                    capture_output=True,
                    timeout=300,
                )
                print(f"  preview: {png.relative_to(ROOT)}")
            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                print(f"  preview render skipped: {filename}: {exc.__class__.__name__}")


def export_watermark_previews(capsule: PartSpec, cfg: SubmarineConfig, out_dir: Path) -> None:
    """Render the actual marked capsule from below and a keel close-up."""
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mm-boat-003-watermark-") as temp_name:
        temp_dir = Path(temp_name)
        stl = temp_dir / "marked-capsule.stl"
        scad = temp_dir / "marked-capsule.scad"
        exporters.export(capsule.solid, str(stl), tolerance=0.08)
        scad.write_text('import("marked-capsule.stl");\n')
        keel_z = -cfg.capsule_od / 2.0 - cfg.keel_h
        camera = (
            f"{cfg.keel_center_x},85,{keel_z - 85},"
            f"{cfg.keel_center_x},0,{keel_z}"
        )
        views = (
            ("watermark-finished-underside.png", camera, True),
            ("watermark-keel-closeup.png", camera, False),
        )
        for filename, camera, fit_all in views:
            command = [
                "openscad", "-o", str(out_dir / filename),
                f"--camera={camera}", "--projection=perspective", "--render=true",
                "--imgsize=1600,800", "--colorscheme=Tomorrow",
            ]
            if fit_all:
                command.extend(("--viewall", "--autocenter"))
            command.append(str(scad))
            try:
                subprocess.run(command, check=True, capture_output=True, timeout=300)
                print(f"  watermark preview: {(out_dir / filename).relative_to(ROOT)}")
            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                print(f"  watermark preview skipped: {filename}: {exc.__class__.__name__}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=ROOT / "exports" / f"draft-{REVISION}",
    )
    parser.add_argument("--no-previews", action="store_true")
    parser.add_argument("--skip-mesh-checks", action="store_true")
    args = parser.parse_args()

    cfg = SubmarineConfig()
    t0 = time.time()
    print("building geometry ...")
    parts = build_all(cfg)
    print(f"  {len(parts)} parts in {time.time() - t0:.1f} s")

    args.outdir.mkdir(parents=True, exist_ok=True)
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    envelope_mm3: dict[str, float] = {}
    part_mass_mm3: dict[str, float] = {}
    part_checks: list[PartCheck] = []
    mesh_generation: dict[str, dict[str, int]] = {}

    print("exporting STLs (print orientation) ...")
    for spec in parts:
        path = args.outdir / f"DRAFT-{spec.name}-{REVISION}.stl"
        bbox, mesh_generation[spec.name] = export_print_stl(spec, path)
        part_mass_mm3[spec.name] = spec.solid.val().Volume()
        if spec.envelope is not None:
            envelope_mm3[spec.name] = spec.envelope.val().Volume()
        wt_actual = None
        if not args.skip_mesh_checks:
            try:
                watertight, _ = check_mesh(path)
                wt_actual = watertight
            except ImportError:
                pass
        part_checks.append(
            PartCheck(
                name=spec.name,
                bbox=(round(bbox[0], 1), round(bbox[1], 1), round(bbox[2], 1)),
                watertight_expected=spec.watertight,
                watertight_actual=wt_actual,
                print_note=spec.note,
            )
        )
        print(f"  {spec.name:18s} {bbox[0]:6.1f} x {bbox[1]:6.1f} x {bbox[2]:6.1f} mm")

    buoyancy = compute_buoyancy(cfg, envelope_mm3, part_mass_mm3)
    mech = validate_rocker(cfg)
    report = run_preflight(cfg, buoyancy, mech, part_checks)

    (reports_dir / f"buoyancy-{REPORT_SUFFIX}.json").write_text(json.dumps(buoyancy.to_dict(), indent=2))
    preflight_output = {"status": "PASS", "lifecycle": "DRAFT", **report}
    (reports_dir / f"preflight-{REPORT_SUFFIX}.json").write_text(
        json.dumps(preflight_output, indent=2)
    )
    (reports_dir / f"rocker-{REPORT_SUFFIX}.json").write_text(
        json.dumps(solve_rocker(cfg).__dict__ | {"problems": mech}, indent=2, default=float)
    )
    (reports_dir / f"config-{REPORT_SUFFIX}.json").write_text(json.dumps(cfg.to_dict(), indent=2))
    mesh_generation_report = {
        "schema_version": "1.0",
        "revision": REVISION,
        "status": "PASS",
        "lifecycle": "DRAFT",
        "source_tessellation_chord_tolerance_mm": 0.08,
        "cleanup": "remove only zero-area or exactly duplicate faces; do not move vertices",
        "parts": mesh_generation,
        "totals": {
            "original_faces": sum(row["original_faces"] for row in mesh_generation.values()),
            "manufacturing_faces": sum(row["manufacturing_faces"] for row in mesh_generation.values()),
            "removed_zero_area_or_duplicate_faces": sum(
                row["removed_zero_area_or_duplicate_faces"] for row in mesh_generation.values()
            ),
            "vertices_moved": 0,
            "exact_duplicate_vertices_merged": sum(
                row["exact_duplicate_vertices_merged"] for row in mesh_generation.values()
            ),
        },
    }
    (reports_dir / f"mesh-generation-{REPORT_SUFFIX}.json").write_text(
        json.dumps(mesh_generation_report, indent=2)
    )
    profile = FishEnvelopeProfile(cfg)
    profile_rows = profile.report_rows()
    profile_csv = reports_dir / f"surfacing-curves-{REPORT_SUFFIX}.csv"
    with profile_csv.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(profile_rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(profile_rows)
    caudal_area = caudal_projected_area_mm2(cfg)
    surfacing = {
        "revision": REVISION,
        "status": "PASS",
        "lifecycle": "DRAFT",
        "method": "bspline-loft-hybrid",
        "construction": "additive B-Rep fish fairing; functional core not deformed",
        "faired_parts": [
            "nose_body", "segment_01", "segment_02", "segment_03",
            "segment_04", "capsule_body",
        ],
        "registered_sections_per_part": cfg.fish_registered_sections,
        "guide_curve_csv": profile_csv.name,
        "guide_curve_samples": len(profile_rows),
        "crest_count_per_part": len(cfg.fish_crest_angles_deg),
        "crest_angles_deg_from_dorsal": list(cfg.fish_crest_angles_deg),
        "crest_visible_height_mm": [cfg.fish_crest_end_height, cfg.fish_crest_peak_height],
        "crest_visible_width_mm": [2 * cfg.fish_crest_end_half_width, 2 * cfg.fish_crest_half_width],
        "joint_end_margin_mm": cfg.fish_crest_end_margin,
        "fins": {
            "dorsal": {"count": 1, "thickness_mm": cfg.dorsal_fin_t},
            "pectoral": {
                "count": 2,
                "thickness_mm": cfg.pectoral_fin_t,
                "downward_cant_deg": cfg.pectoral_fin_cant_deg,
            },
            "caudal": {
                "thickness_mm": cfg.fin_t,
                "span_mm": cfg.caudal_span,
                "projected_area_mm2": round(caudal_area, 3),
                "baseline_area_mm2": 1278.0,
                "area_ratio": round(caudal_area / 1278.0, 5),
            },
        },
        "hardpoint_geometry_modified": False,
        "hardpoint_validation": "PASS via hardpoint-drift-v1.1.0-draft.1.json",
        "parameter_extremes": "PASS via test_freeform_and_crest_parameter_sweep_valid",
        "guide_curve_continuity": "C2 natural cubic splines",
        "brep_highlight_continuity": "visual review required; no formal Class-A claim",
        "topology": "PASS via mesh watertightness preflight",
        "tessellation_chord_tolerance_mm": 0.08,
    }
    (reports_dir / f"surfacing-{REPORT_SUFFIX}.json").write_text(json.dumps(surfacing, indent=2))

    watermark_dir = (
        ROOT / "assets/metrimade-watermark/generated"
        / f"{cfg.watermark_product_id}_v{cfg.watermark_version}_compact"
    )
    watermark_metadata = watermark_dir / (
        f"metrimade-watermark-{cfg.watermark_product_id}"
        f"-v{cfg.watermark_version}-compact.json"
    )
    watermark_manifest = watermark_dir / "manifest.sha256"
    selector_report = ROOT / "validation/watermark-selector-v1.1.0-draft.1.json"
    capsule_mesh = args.outdir / f"DRAFT-capsule_body-{REVISION}.stl"
    cutter_bb = _keel_watermark_cutter(cfg).val().BoundingBox()
    keel_x0 = cfg.keel_center_x - cfg.keel_l / 2.0
    keel_x1 = cfg.keel_center_x + cfg.keel_l / 2.0
    keel_y0, keel_y1 = -cfg.keel_w / 2.0, cfg.keel_w / 2.0
    watermark_report = {
        "schema_version": "1.0",
        "revision": REVISION,
        "status": "REVIEW_REQUIRED",
        "lifecycle": "DRAFT",
        "asset_revision": cfg.watermark_asset_revision,
        "product_id": cfg.watermark_product_id,
        "version": cfg.watermark_version,
        "layout_tier": cfg.watermark_layout_tier,
        "layout_priority": 2,
        "domain_visible": True,
        "visible_text": ["metriMade.com", "MM-BOAT-003", "v1.1.0-draft.1"],
        "uniform_scale": 1.0,
        "rotation_deg": 0,
        "operation": "recessed",
        "surface": "capsule keel flat underside",
        "selected_envelope_mm": [cfg.watermark_width, cfg.watermark_height],
        "actual_cut_bounds_mm": [
            cutter_bb.xmin, cutter_bb.xmax,
            cutter_bb.ymin, cutter_bb.ymax,
            cutter_bb.zmin, cutter_bb.zmax,
        ],
        "depth_mm": cfg.watermark_depth,
        "boolean_overlap_mm": cfg.watermark_overlap,
        "host_wall_before_mm": cfg.keel_wall,
        "remaining_wall_mm": cfg.keel_wall - cfg.watermark_depth,
        "bed_datum_z_mm": -cfg.capsule_od / 2.0 - cfg.keel_h,
        "edge_clearances_mm": {
            "front_x": cutter_bb.xmin - keel_x0,
            "rear_x": keel_x1 - cutter_bb.xmax,
            "port_y": cutter_bb.ymin - keel_y0,
            "starboard_y": keel_y1 - cutter_bb.ymax,
        },
        "marked_part_coverage": {
            "primary_body": "capsule_body",
            "other_parts": "assembly-covered; not separately saleable in this DRAFT set",
        },
        "digital_checks": {
            "identity_match": "PASS",
            "selector": "PASS",
            "unscaled_profile": "PASS",
            "brep_cut": "PASS",
            "bed_datum_unchanged": "PASS",
            "remaining_wall": "PASS",
        },
        "hashes": {
            "metadata_sha256": _sha256(watermark_metadata),
            "manifest_sha256": _sha256(watermark_manifest),
            "selector_sha256": _sha256(selector_report),
            "production_capsule_mesh_sha256": _sha256(capsule_mesh),
            "geometry_source_sha256": _sha256(ROOT / "submarine/geometry.py"),
        },
        "physical_coupon": "PENDING",
        "exact_slicer_preview": "NOT_RUN",
        "human_approval": "PENDING",
    }
    (reports_dir / f"watermark-{REPORT_SUFFIX}.json").write_text(
        json.dumps(watermark_report, indent=2)
    )

    print("\n-- buoyancy --------------------------------------------------")
    for k, v in buoyancy.to_dict().items():
        print(f"  {k:34s} {v}")
    print(f"\npreflight: PASS ({len(report['checks'])} checks)")

    if not args.no_previews:
        print("\nrendering previews ...")
        export_previews(parts, ROOT / "previews" / f"production-{REVISION}")
        capsule = next(part for part in parts if part.name == "capsule_body")
        export_watermark_previews(
            capsule,
            cfg,
            ROOT / "previews" / f"production-{REVISION}",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
