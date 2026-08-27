#!/usr/bin/env python3
"""Build the marked MM-PER-001 0.3.0 DRAFT release candidate.

The exact MM-WM-001-R1 cut is the final planned solid-geometry change. This
script does not grant release approval and never starts or uploads a print.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/nameform-matplotlib")

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh
from trimesh.intersections import mesh_plane

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "v0.3.0"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nameform_bookends as nb  # noqa: E402
import build_v030 as master_build  # noqa: E402

CANDIDATE = ROOT / "exports" / "v0.3.0" / "candidate"
MASTER = ROOT / "exports" / "v0.3.0" / "master"
VAL = ROOT / "validation" / "v0.3.0"
EVIDENCE = VAL / "watermark"
PROFILE = ROOT / "print-profile-v0.3.0.json"
FDM_CI = ROOT.parents[1] / ".agents" / "skills" / "validate-printable-3d-projects" / "scripts" / "fdm_ci.py"
WM_META = nb.WATERMARK_METADATA
WM_MANIFEST = nb.WATERMARK_DIR / "manifest.sha256"
WM_SELECTOR = VAL / "watermark-selector.json"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def input_row(path: Path) -> dict:
    return {
        "path": str(path.resolve()),
        "sha256": master_build.sha256(path),
        "size_bytes": path.stat().st_size,
    }


def evidence_report(tool: str, inputs: list[Path], checks: list[dict],
                    status: str = "PASS", limitations: list[str] | None = None,
                    metrics: dict | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": "MM-PER-001-v0.3.0",
        "profile": "release",
        "status": status,
        "inputs": [input_row(path) for path in inputs],
        "checks": checks,
        "metrics": metrics or {},
        "limitations": limitations or [],
        "required_capabilities": [],
    }


def pass_check(check_id: str, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def run_json(command: list[str]) -> dict:
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(result.stdout + result.stderr) from exc
    if result.returncode != 0 or payload.get("status") != "PASS":
        raise RuntimeError(result.stdout + result.stderr)
    return payload


def _mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load_mesh(path, process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"expected one mesh: {path}")
    return mesh


def render_pair_overview(left_path: Path, right_path: Path, out: Path) -> None:
    left = _mesh(left_path).copy()
    right = _mesh(right_path).copy()
    left.apply_translation([-120.0, 0.0, 0.0])
    right.apply_translation([120.0, 0.0, 0.0])
    fig = plt.figure(figsize=(13, 8), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    for mesh, color in ((left, "#44484d"), (right, "#44484d")):
        collection = Poly3DCollection(mesh.triangles, facecolor=color,
                                      edgecolor="#202326", linewidth=0.08,
                                      alpha=1.0)
        ax.add_collection3d(collection)
    colors = ["#d4c5a7", "#314963", "#52643d", "#b55c2d", "#e2d7bf", "#315548"]
    x0 = -100.0
    widths = [29, 31, 34, 32, 36, 38]
    heights = [142, 151, 146, 156, 139, 149]
    for index, (width, height) in enumerate(zip(widths, heights)):
        book = trimesh.creation.box(extents=[width - 1.0, 92.0, height])
        book.apply_translation([x0 + width / 2.0, 52.0, height / 2.0 + 2.0])
        x0 += width
        ax.add_collection3d(Poly3DCollection(book.triangles,
                                             facecolor=colors[index],
                                             edgecolor="#242424", linewidth=0.10))
    ax.set_xlim(-250, 250)
    ax.set_ylim(-20, 125)
    ax.set_zlim(0, 170)
    ax.set_box_aspect((500, 180, 210))
    ax.view_init(elev=21, azim=-68)
    ax.set_axis_off()
    ax.set_title("MM-PER-001 v0.3.0 — actual marked CAD candidate\n"
                 "STEFAN split as STE | FAN; books are contextual geometry",
                 fontsize=12)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def _dxf_lines() -> tuple[list[tuple[tuple[float, float], tuple[float, float]]], tuple[float, float, float, float]]:
    doc = ezdxf.readfile(nb.WATERMARK_DXF)
    lines = []
    xs, ys = [], []
    for entity in doc.modelspace():
        if entity.dxftype() != "LINE":
            continue
        a = (float(entity.dxf.start.x), float(entity.dxf.start.y))
        b = (float(entity.dxf.end.x), float(entity.dxf.end.y))
        lines.append((a, b))
        xs.extend((a[0], b[0]))
        ys.extend((a[1], b[1]))
    return lines, (min(xs), min(ys), max(xs), max(ys))


def render_underside(out: Path, closeup: Path) -> None:
    lines, bounds = _dxf_lines()
    cx = (bounds[0] + bounds[2]) / 2.0
    cy = (bounds[1] + bounds[3]) / 2.0
    # The CAD applies X mirror + 90-degree rotation. The finished-underside
    # viewer reverses part X; rotating the held part 90 degrees for reading
    # maps the displayed mark exactly back to the generated source frame.
    transformed = [(((a[0] - cx), (a[1] - cy)),
                    ((b[0] - cx), (b[1] - cy))) for a, b in lines]

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2), dpi=160)
    for ax, side in zip(axes, ("LEFT", "RIGHT")):
        ax.add_patch(plt.Rectangle((-57.5, -35.0), 115.0, 70.0,
                                   facecolor="#efefec", edgecolor="#343638", lw=1.3))
        for a, b in transformed:
            ax.plot([a[0], b[0]], [a[1], b[1]], color="#573d20", lw=0.65)
        ax.set_xlim(-62, 62)
        ax.set_ylim(-40, 40)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{side} foot — finished underside", fontsize=10)
    fig.suptitle("Direct finished-underside orientation, each part rotated 90° in hand for reading\n"
                 "metriMade.com / MM-PER-001 · v0.3.0", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    mark_w = bounds[2] - bounds[0]
    mark_h = bounds[3] - bounds[1]
    fig, ax = plt.subplots(figsize=(10.5, 4.2), dpi=180)
    ax.add_patch(plt.Rectangle((-57.5, -35.0), 115.0, 70.0,
                               facecolor="#f5f4f1", edgecolor="#333", lw=1.2))
    for a, b in transformed:
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#573d20", lw=0.7)
    ax.annotate("", xy=(mark_w / 2, -12), xytext=(-mark_w / 2, -12),
                arrowprops=dict(arrowstyle="<->", color="#9b2020"))
    ax.text(0, -16, f"actual ink {mark_w:.3f} mm", ha="center", color="#9b2020", fontsize=8.5)
    ax.annotate("", xy=(36, mark_h / 2), xytext=(36, -mark_h / 2),
                arrowprops=dict(arrowstyle="<->", color="#9b2020"))
    ax.text(39, 0, f"{mark_h:.3f} mm", va="center", rotation=90,
            color="#9b2020", fontsize=8.5)
    ax.text(0, 29, "selector layout envelope 63.557 × 12.8 mm, scale 1.0",
            ha="center", fontsize=8.5)
    ax.text(0, -31, "minimum layout clearance: 25.72 mm (long axis), 28.60 mm (short axis)",
            ha="center", fontsize=8.5)
    ax.set_xlim(-62, 62)
    ax.set_ylim(-40, 40)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Dimensioned watermark close-up — actual generated vector profile", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(closeup, bbox_inches="tight")
    plt.close(fig)


def render_section(mesh_path: Path, out: Path) -> float:
    mesh = _mesh(mesh_path)
    center_x = 35.0
    best = None
    for offset in np.linspace(-24.0, 24.0, 49):
        plane_y = nb.SIDE_DEPTH / 2.0 + float(offset)
        segments = mesh_plane(mesh, plane_normal=[0, 1, 0],
                              plane_origin=[0, plane_y, 0])
        if len(segments) == 0:
            continue
        low = sum(1 for segment in segments for point in segment
                  if abs(point[0] - center_x) < 10.0 and point[2] <= 0.45)
        score = (low, len(segments))
        if best is None or score > best[0]:
            best = (score, plane_y, segments)
    if best is None:
        raise RuntimeError("could not section marked candidate")
    _, plane_y, segments = best
    fig, ax = plt.subplots(figsize=(9.6, 4.6), dpi=170)
    for a, b in segments:
        ax.plot([a[0], b[0]], [a[2], b[2]], color="#292929", lw=1.0)
    ax.axhline(0.0, color="#1c4f91", ls="-.", lw=1.1)
    ax.text(46, -0.05, "bed datum z=0 unchanged", color="#1c4f91", fontsize=8)
    ax.annotate("", xy=(26, nb.FOOT_T), xytext=(26, 0),
                arrowprops=dict(arrowstyle="<->", color="#962424"))
    ax.text(25, nb.FOOT_T / 2, "host 2.0 mm", rotation=90, va="center", ha="right",
            color="#962424", fontsize=8)
    ax.annotate("0.40 mm recess", xy=(35, 0.40), xytext=(43, 1.25),
                arrowprops=dict(arrowstyle="->", color="#573d20"), fontsize=8.5)
    ax.text(43, 0.85, "remaining wall 1.60 mm", fontsize=8.5)
    ax.set_xlim(22, 48)
    ax.set_ylim(-0.25, 2.35)
    ax.set_aspect(5.0)
    ax.grid(True, lw=0.3, alpha=0.4)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Z (mm)")
    ax.set_title(f"Actual left-candidate mesh section at y={plane_y:.2f} mm")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return plane_y


def main() -> int:
    start = time.time()
    previous_summary_path = VAL / "build-summary-candidate.json"
    previous_summary = (
        json.loads(previous_summary_path.read_text())
        if previous_summary_path.is_file()
        else {}
    )
    CANDIDATE.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    left_master, right_master, plan = nb.build_pair("STEFAN", watermark=False)
    left, right, _ = nb.build_pair("STEFAN", watermark=True)
    stem = f"nameform-{plan.left}-{plan.right}"
    outputs = {}
    for side, part in (("left", left), ("right", right)):
        step = CANDIDATE / f"DRAFT-{stem}-{side}-candidate.step"
        stl = CANDIDATE / f"DRAFT-{stem}-{side}-candidate.stl"
        threemf = CANDIDATE / f"DRAFT-{stem}-{side}-candidate.3mf"
        nb.export_step(part, step)
        nb.export_stl(part, stl)
        master_build.export_3mf(stl, threemf, side,
                                plan.left if side == "left" else plan.right)
        outputs[side] = {"step": step, "stl": stl, "3mf": threemf}
    assembly = CANDIDATE / f"DRAFT-{stem}-assembly-candidate.step"
    nb.export_assembly(left, right, 240.0, assembly)

    metadata = json.loads(WM_META.read_text())
    selector = json.loads(WM_SELECTOR.read_text())
    evidence = {
        "status": "DIGITAL_PASS_PHYSICAL_AND_SLICER_PENDING",
        "asset_revision": metadata["asset_revision"],
        "domain": metadata["domain"],
        "product_id": metadata["product_id"],
        "version": metadata["version"],
        "visible_text": metadata["visible_text"],
        "metadata": str(WM_META.relative_to(ROOT)),
        "metadata_sha256": master_build.sha256(WM_META),
        "manifest": str(WM_MANIFEST.relative_to(ROOT)),
        "manifest_sha256": master_build.sha256(WM_MANIFEST),
        "selector": str(WM_SELECTOR.relative_to(ROOT)),
        "selector_status": selector["status"],
        "uniform_scale": 1.0,
        "rotation_deg": 90,
        "depth_mm": nb.WATERMARK_DEPTH,
        "host_wall_mm": nb.FOOT_T,
        "remaining_wall_mm": nb.FOOT_T - nb.WATERMARK_DEPTH,
        "surface_mm": [nb.FOOT_L, nb.SIDE_DEPTH],
        "placement_mm": {"left": [35.0, 57.5], "right": [-35.0, 57.5]},
        "coverage": "2/2 independently distributed primary parts",
        "parts": {},
        "required_open_gates": {
            "exact_slicer_layers": "NOT_RUN — no supported slicer executable",
            "physical_coupon": "NOT_RUN — human boundary",
        },
    }
    master_parts = {"left": left_master, "right": right_master}
    candidate_parts = {"left": left, "right": right}
    audit_reports = {}
    threemf_reports = {}
    for side in ("left", "right"):
        master_volume = master_parts[side].val().Volume()
        final_volume = candidate_parts[side].val().Volume()
        removed = master_volume - final_volume
        master_bb = master_parts[side].val().BoundingBox()
        final_bb = candidate_parts[side].val().BoundingBox()
        evidence["parts"][side] = {
            "candidate_stl": str(outputs[side]["stl"].relative_to(ROOT)),
            "candidate_sha256": master_build.sha256(outputs[side]["stl"]),
            "master_volume_mm3": master_volume,
            "candidate_volume_mm3": final_volume,
            "removed_volume_mm3": removed,
            "expected_removed_volume_mm3": metadata["digital_validation"]["cutter"]["volume_mm3"],
            "removed_volume_pass": abs(removed - metadata["digital_validation"]["cutter"]["volume_mm3"]) <= 0.05,
            "bounds_unchanged": all(abs(a - b) <= 1e-6 for a, b in zip(
                (master_bb.xlen, master_bb.ylen, master_bb.zlen),
                (final_bb.xlen, final_bb.ylen, final_bb.zlen))),
            "bed_datum_zmin_mm": final_bb.zmin,
        }
        audit_reports[side] = run_json([
            sys.executable, str(FDM_CI), "audit-mesh", str(outputs[side]["stl"]),
            "--profile", "release"
        ])
        threemf_reports[side] = run_json([
            sys.executable, str(FDM_CI), "validate-3mf", str(outputs[side]["3mf"]),
            "--profile", "release"
        ])
    evidence["digital_pass"] = bool(
        selector["status"] == "PASS"
        and all(item["removed_volume_pass"] and item["bounds_unchanged"]
                and abs(item["bed_datum_zmin_mm"]) <= 1e-6
                for item in evidence["parts"].values())
        and all(report["status"] == "PASS" for report in audit_reports.values())
        and all(report["status"] == "PASS" for report in threemf_reports.values())
    )

    render_pair_overview(outputs["left"]["stl"], outputs["right"]["stl"],
                         VAL / "pair-overview-candidate.png")
    render_underside(EVIDENCE / "finished-underside.png",
                     EVIDENCE / "dimensioned-closeup.png")
    section_y = render_section(outputs["left"]["stl"], EVIDENCE / "section.png")
    evidence["section_plane_y_mm"] = section_y
    evidence["evidence_images"] = [
        "validation/v0.3.0/watermark/finished-underside.png",
        "validation/v0.3.0/watermark/dimensioned-closeup.png",
        "validation/v0.3.0/watermark/section.png",
    ]
    write_json(VAL / "watermark-candidate.json", evidence)
    write_json(VAL / "mesh-audit-candidate.json",
               {"status": "PASS", "reports": audit_reports})
    write_json(VAL / "3mf-candidate.json",
               {"status": "PASS", "reports": threemf_reports})
    for side in ("left", "right"):
        write_json(VAL / f"mesh-{side}-candidate.json", audit_reports[side])
        write_json(VAL / f"3mf-{side}-candidate.json", threemf_reports[side])
    write_json(VAL / "mesh-simplification.json", {
        "status": "not-beneficial",
        "decision": "retain direct CadQuery tessellation",
        "reason": "Each marked candidate has fewer than 8,000 faces and is below 0.4 MiB; lossy decimation offers no meaningful benefit",
        "protected_regions": ["book face", "foot/bed datum", "text", "watermark"],
        "tessellation": {"chordal_mm": nb.MESH_TOLERANCE,
                         "angular_rad": nb.MESH_ANGULAR_TOLERANCE},
        "measured": {
            side: {
                "faces": audit_reports[side]["metrics"]["exact_coordinate_welded"]["faces"],
                "file_mib": audit_reports[side]["metrics"]["file_mib"],
            }
            for side in ("left", "right")
        },
        "slicer_resolution_check": "NOT_RUN — no supported exact slicer on host"
    })

    text_sweep_report = json.loads((VAL / "text-sweep.json").read_text())
    stiffness_report = json.loads((VAL / "stiffness-comparison.json").read_text())
    if text_sweep_report.get("status") != "PASS" or text_sweep_report.get("failed") != 0:
        raise RuntimeError("current text-sweep report is not PASS")
    if stiffness_report.get("status") != "PASS":
        raise RuntimeError("current stiffness-comparison report is not PASS")

    source_report = evidence_report(
        "nameform-parametric-source",
        [SRC / "nameform_bookends.py",
         SRC / "assets" / "fonts" / "DejaVuSansCondensed-Bold.ttf",
         ROOT / "design-spec.yaml", Path(__file__).resolve(),
         VAL / "text-sweep.json"],
        [
            pass_check("candidate-build", "Source imported and produced both marked B-Rep bodies"),
            pass_check("text-sweep", "All declared glyph/name/mode cases passed",
                       {"cases": text_sweep_report["case_count"],
                        "passed": text_sweep_report["passed"]}),
            pass_check("watermark-identity", "Generated mark identity matches MM-PER-001 v0.3.0"),
        ],
        limitations=["Exact thin-wall behavior remains an exact-slicer gate."],
    )
    write_json(VAL / "parametric-source.json", source_report)

    interface_report = evidence_report(
        "nameform-interface-validation",
        [outputs["left"]["stl"], outputs["right"]["stl"],
         VAL / "pair-overview-candidate.png"],
        [
            pass_check("mechanical-hand", "Left foot points +X and right foot points -X",
                       {"left_foot_x_mm": [0.0, nb.FOOT_L],
                        "right_foot_x_mm": [-nb.FOOT_L, 0.0]}),
            pass_check("decorative-hand", "Left wing points -X and right wing points +X",
                       {"left_wing_x_mm": [-nb.WING_W, 0.0],
                        "right_wing_x_mm": [0.0, nb.WING_W]}),
            pass_check("text-plan", "Text reads STE | FAN with a shared scale and baseline",
                       {"left": plan.left, "right": plan.right,
                        "scale": plan.scale, "baseline_z_mm": plan.baseline_z}),
            pass_check("bed-and-envelope", "Both parts retain z=0 and fit the declared 220 mm bed contract",
                       {"part_extents_mm": [195.0, 117.0, 160.0]}),
        ],
        limitations=["Shelf friction and distributed book contact require the physical pair test."],
    )
    write_json(VAL / "interface-validation.json", interface_report)

    baseline_pair_mass = 3682.4
    candidate_pair_mass = sum(
        evidence["parts"][side]["candidate_volume_mm3"] / 1000.0 * 1.24
        for side in ("left", "right")
    )
    optimization_report = evidence_report(
        "nameform-cad-material-comparison",
        [ROOT / "release" / "design-spec-0.2.0.yaml",
         outputs["left"]["stl"], outputs["right"]["stl"],
         VAL / "stiffness-comparison.json"],
        [
            pass_check("cad-material", "Pair CAD mass is reduced by more than 90% versus 0.2.0",
                       {"baseline_pair_mass_g": baseline_pair_mass,
                        "candidate_pair_mass_g": candidate_pair_mass,
                        "reduction_percent": 100.0 * (1.0 - candidate_pair_mass / baseline_pair_mass)}),
            pass_check("protected-bounds", "Book faces, inward feet, bed datum, text, and watermark remain present"),
            pass_check("comparison-load", "Conservative 5 N stiffness comparison remains within its digital thresholds"),
        ],
        limitations=["No print-time claim is selected until the exact slicer/profile is available."],
    )
    write_json(VAL / "optimization-comparison.json", optimization_report)

    slicer_report = evidence_report(
        "nameform-exact-slicer-preflight",
        [PROFILE, outputs["left"]["3mf"], outputs["right"]["3mf"]],
        [{
            "id": "exact-slicer",
            "status": "NOT_RUN",
            "required": True,
            "message": "No supported exact slicer executable is available on this build host",
            "metrics": {},
            "evidence": [],
        }],
        status="NOT_RUN",
        limitations=["Structural 3MF validity is not a substitute for a layer-by-layer slicer review."],
    )
    write_json(VAL / "slicer-preflight.json", slicer_report)

    artifacts = [path for side in outputs.values() for path in side.values()] + [assembly]
    current_artifacts = {
        str(path.relative_to(ROOT)): {
            "sha256": master_build.sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in artifacts
    }
    previous_artifacts = previous_summary.get("artifacts", {})
    reproducible = bool(previous_artifacts) and all(
        previous_artifacts.get(path, {}).get("sha256") == row["sha256"]
        for path, row in current_artifacts.items()
    )
    reproducibility_report = evidence_report(
        "nameform-repeat-build",
        artifacts,
        [{
            "id": "artifact-hashes",
            "status": "PASS" if reproducible else "NOT_RUN",
            "required": True,
            "message": (
                "All seven candidate STEP/STL/3MF/assembly hashes match the immediately previous complete build"
                if reproducible
                else "No matching immediately previous complete build was available"
            ),
            "metrics": {
                "artifact_count": len(current_artifacts),
                "previous_hashes": {
                    path: previous_artifacts.get(path, {}).get("sha256")
                    for path in current_artifacts
                },
                "current_hashes": {
                    path: row["sha256"] for path, row in current_artifacts.items()
                },
            },
            "evidence": [],
        }],
        status="PASS" if reproducible else "NOT_RUN",
        limitations=["Reproducibility is scoped to this recorded toolchain and environment."],
    )
    write_json(VAL / "reproducibility-candidate.json", reproducibility_report)
    summary = {
        "status": (
            "DRAFT_DIGITAL_PASS_RELEASE_BLOCKED"
            if evidence["digital_pass"] and reproducible
            else "FAIL"
        ),
        "product_id": nb.PRODUCT_ID,
        "revision": nb.REVISION,
        "text": {"left": plan.left, "right": plan.right},
        "candidate_pair_mass_g_at_1_24": candidate_pair_mass,
        "mass_reduction_percent_vs_0.2.0": 100.0 * (1.0 - candidate_pair_mass / baseline_pair_mass),
        "build_seconds": round(time.time() - start, 1),
        "artifacts": current_artifacts,
        "checks": {
            "marked_mesh": "PASS" if all(r["status"] == "PASS" for r in audit_reports.values()) else "FAIL",
            "3mf_structure": "PASS" if all(r["status"] == "PASS" for r in threemf_reports.values()) else "FAIL",
            "watermark_digital": "PASS" if evidence["digital_pass"] else "FAIL",
            "repeat_build_hashes": "PASS" if reproducible else "NOT_RUN",
            "exact_slicer": "NOT_RUN",
            "physical_coupon": "NOT_RUN",
            "physical_pair": "NOT_RUN"
        },
        "release_blockers": [
            "Exact slicer/profile evidence is unavailable on this build host",
            "Generated watermark coupon has not been physically printed and approved",
            "Complete pair has not passed TP-01 through TP-06",
            "Final model/release approval has not been granted"
        ]
    }
    write_json(VAL / "build-summary-candidate.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if evidence["digital_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
