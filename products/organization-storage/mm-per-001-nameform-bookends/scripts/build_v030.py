#!/usr/bin/env python3
"""Build and digitally validate the unmarked MM-PER-001 0.3.0 master pair.

This script intentionally emits DRAFT artifacts. The product watermark is a
later phase and the exact-slicer/physical gates remain explicit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/nameform-matplotlib")

import cadquery as cq
import matplotlib
import shapely
import trimesh

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "v0.3.0"
sys.path.insert(0, str(SRC))
import nameform_bookends as nb  # noqa: E402

OUT_MASTER = ROOT / "exports" / "v0.3.0" / "master"
OUT_DRAFT = ROOT / "exports" / "v0.3.0" / "draft"
VAL = ROOT / "validation" / "v0.3.0"
PROFILE = ROOT / "print-profile-v0.3.0.json"
FDM_CI = ROOT.parents[1] / ".agents" / "skills" / "validate-printable-3d-projects" / "scripts" / "fdm_ci.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def analyze_mesh(path: Path) -> dict:
    mesh = trimesh.load_mesh(path, process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"expected one mesh in {path}")
    processed = mesh.copy()
    processed.process(validate=True)
    bounds = processed.bounds
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "vertices": int(len(processed.vertices)),
        "faces": int(len(processed.faces)),
        "watertight": bool(processed.is_watertight),
        "winding_consistent": bool(processed.is_winding_consistent),
        "positive_volume": bool(processed.volume > 0),
        "body_count": len(processed.split(only_watertight=False)),
        "bounds_mm": bounds.tolist(),
        "extents_mm": (bounds[1] - bounds[0]).tolist(),
        "volume_cm3": float(processed.volume / 1000.0),
        "mass_g_at_1_24": float(processed.volume / 1000.0 * 1.24),
        "center_mass_mm": processed.center_mass.tolist(),
    }


def mesh_xml(mesh: trimesh.Trimesh, side: str, text: str) -> str:
    vertices = "\n".join(
        f'          <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>'
        for x, y, z in mesh.vertices
    )
    triangles = "\n".join(
        f'          <triangle v1="{a}" v2="{b}" v3="{c}"/>'
        for a, b, c in mesh.faces
    )
    return (
        f'    <object id="1" type="model" name="NameForm {side} {text}" '
        f'partnumber="{nb.PRODUCT_ID}-{nb.REVISION}-{side}">\n'
        f"      <mesh>\n        <vertices>\n{vertices}\n        </vertices>\n"
        f"        <triangles>\n{triangles}\n        </triangles>\n"
        f"      </mesh>\n    </object>\n"
    )


def export_3mf(stl: Path, out: Path, side: str, text: str) -> None:
    mesh = trimesh.load_mesh(stl, process=True)
    if not mesh.is_watertight or mesh.volume <= 0:
        raise RuntimeError(f"refusing invalid 3MF source mesh: {stl}")
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
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        '  <metadata name="Application">metriMade deterministic draft exporter</metadata>\n'
        f'  <metadata name="Title">NameForm {side} — {text} — DRAFT</metadata>\n'
        f'  <metadata name="Description">{nb.PRODUCT_ID} v{nb.REVISION}; print separately; profile {PROFILE.name}</metadata>\n'
        '  <metadata name="LicenseTerms">DRAFT engineering artifact; not a final commercial package</metadata>\n'
        '  <resources>\n' + mesh_xml(mesh, side, text) + '  </resources>\n'
        '  <build>\n    <item objectid="1"/>\n  </build>\n'
        '</model>\n'
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    def add_bytes(archive: zipfile.ZipFile, name: str, data: str | bytes) -> None:
        info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, data.encode("utf-8") if isinstance(data, str) else data)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        add_bytes(archive, "[Content_Types].xml", content_types)
        add_bytes(archive, "_rels/.rels", rels)
        add_bytes(archive, "3D/3dmodel.model", model)
        add_bytes(archive, "Metadata/print-profile-v0.3.0.json", PROFILE.read_bytes())


def validate_3mf_locally(path: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(FDM_CI), "validate-3mf", str(path), "--profile", "release"],
        check=False, text=True, capture_output=True,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(result.stdout + result.stderr) from exc
    if result.returncode != 0 or payload.get("status") != "PASS":
        raise RuntimeError(f"3MF validation failed for {path}:\n{result.stdout}\n{result.stderr}")
    return payload


def text_sweep() -> dict:
    values = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + list("ÄÖÜẞ")
    cases = [
        {"name": value, "mode": "split-name"} for value in values
    ] + [
        {"name": "STEFAN", "mode": "split-name"},
        {"name": "SOPHIA", "mode": "split-name"},
        {"name": "ALEXANDER", "mode": "split-name"},
        {"name": "MAXIMILIAN", "mode": "split-name"},
        {"name": "MÄX", "mode": "split-name"},
        {"name": "O-P", "mode": "split-name"},
        {"name": "STEFAN", "mode": "whole-name-each-side"},
        {"left": "BÜ", "right": "Qß", "mode": "explicit-pair"},
    ]
    outcomes = []
    for case in cases:
        try:
            if case["mode"] == "explicit-pair":
                plan = nb.pair_text(left_text=case["left"], right_text=case["right"])
            else:
                plan = nb.pair_text(case["name"], same_on_both=case["mode"] == "whole-name-each-side")
            # Exercise contour parity for every supported glyph. Run complete
            # body Booleans for counter/baseline edge cases and all name modes.
            left_text_shape = nb.text_solid(plan.left, plan.scale,
                                            -nb.WING_W / 2.0, plan.baseline_z)
            right_text_shape = nb.text_solid(plan.right, plan.scale,
                                             nb.WING_W / 2.0, plan.baseline_z)
            full_build = (
                case.get("name") in set("BCDJOQRSUÄÖÜẞ")
                or len(case.get("name", "")) > 1
                or case["mode"] != "split-name"
            )
            if full_build:
                left = nb.build_side("left", plan.left, plan)
                right = nb.build_side("right", plan.right, plan)
                left_volume = left.val().Volume()
                right_volume = right.val().Volume()
            else:
                left_volume = left_text_shape.Volume()
                right_volume = right_text_shape.Volume()
            outcomes.append({"case": case, "status": "PASS", "left": plan.left,
                             "right": plan.right, "scale": plan.scale,
                             "full_body_build": full_build,
                             "left_volume_mm3": left_volume,
                             "right_volume_mm3": right_volume})
        except Exception as exc:
            outcomes.append({"case": case, "status": "FAIL",
                             "error": f"{type(exc).__name__}: {exc}"})
    failed = [item for item in outcomes if item["status"] != "PASS"]
    return {
        "status": "PASS" if not failed else "FAIL",
        "case_count": len(outcomes),
        "passed": len(outcomes) - len(failed),
        "failed": len(failed),
        "cases": outcomes,
    }


def stiffness_report() -> dict:
    # Conservative strip/beam comparison for normal load on the side blade.
    # The front wing and horizontal plate action are ignored; four continuous
    # vertical ribs are included by transformed rectangle areas.
    e_mpa = 3000.0
    force_n = 5.0
    length = nb.TOTAL_H
    skin_area = nb.SIDE_DEPTH * nb.PLATE_T
    rib_area = nb.RIB_T * nb.RIB_PROJECTION
    rib_count = 4
    rib_center = nb.PLATE_T / 2.0 + nb.RIB_PROJECTION / 2.0
    total_area = skin_area + rib_count * rib_area
    neutral = rib_count * rib_area * rib_center / total_area
    i_skin = nb.SIDE_DEPTH * nb.PLATE_T ** 3 / 12.0 + skin_area * neutral ** 2
    i_rib_local = nb.RIB_T * nb.RIB_PROJECTION ** 3 / 12.0
    i_ribs = rib_count * (i_rib_local + rib_area * (rib_center - neutral) ** 2)
    inertia = i_skin + i_ribs
    deflection = force_n * length ** 3 / (3.0 * e_mpa * inertia)
    max_distance = nb.PLATE_T / 2.0 + nb.RIB_PROJECTION - neutral
    stress = force_n * length * max_distance / inertia
    return {
        "status": "PASS",
        "model": "conservative vertical cantilever section; ignores stiffening from front wing and plate action",
        "elastic_modulus_mpa_assumed": e_mpa,
        "proof_force_n": force_n,
        "load_height_mm": length,
        "second_moment_mm4": inertia,
        "tip_deflection_mm": deflection,
        "max_bending_stress_mpa": stress,
        "comparison_limits": {"tip_deflection_mm_max": 2.0, "stress_mpa_max": 15.0},
        "limitations": [
            "Isotropic linear PLA comparison only; not a printed-material allowable",
            "Layer adhesion, creep, impacts, shelf friction, and book contact require physical tests"
        ],
        "pass": bool(deflection <= 2.0 and stress <= 15.0),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="STEFAN")
    args = parser.parse_args()
    start = time.time()
    OUT_MASTER.mkdir(parents=True, exist_ok=True)
    OUT_DRAFT.mkdir(parents=True, exist_ok=True)
    VAL.mkdir(parents=True, exist_ok=True)

    left, right, plan = nb.build_pair(args.name)
    stem = f"nameform-{plan.left}-{plan.right}"
    paths = {}
    for side, part in (("left", left), ("right", right)):
        step = OUT_MASTER / f"{stem}-{side}-master.step"
        stl = OUT_MASTER / f"{stem}-{side}-master.stl"
        threemf = OUT_DRAFT / f"DRAFT-{stem}-{side}.3mf"
        nb.export_step(part, step)
        nb.export_stl(part, stl)
        export_3mf(stl, threemf, side, plan.left if side == "left" else plan.right)
        paths[side] = {"step": step, "stl": stl, "3mf": threemf}
    assembly = OUT_MASTER / f"{stem}-assembly-master.step"
    nb.export_assembly(left, right, 240.0, assembly)

    geometry = {
        "status": "PASS",
        "product_id": nb.PRODUCT_ID,
        "revision": nb.REVISION,
        "candidate": "unmarked master — DRAFT",
        "text": {"left": plan.left, "right": plan.right, "mode": plan.mode,
                 "scale": plan.scale, "baseline_z": plan.baseline_z},
        "left": analyze_mesh(paths["left"]["stl"]),
        "right": analyze_mesh(paths["right"]["stl"]),
    }
    required = []
    for side in ("left", "right"):
        item = geometry[side]
        required.extend([item["watertight"], item["winding_consistent"],
                         item["positive_volume"], item["body_count"] == 1,
                         item["extents_mm"][0] <= 200.0,
                         item["extents_mm"][1] <= 120.0,
                         item["extents_mm"][2] <= 165.0])
    geometry["status"] = "PASS" if all(required) else "FAIL"
    geometry["pair_mass_g_at_1_24"] = (
        geometry["left"]["mass_g_at_1_24"] + geometry["right"]["mass_g_at_1_24"]
    )
    geometry["historical_pair_mass_g_at_1_24"] = 3682.4
    geometry["mass_reduction_percent_vs_0.2.0"] = (
        100.0 * (1.0 - geometry["pair_mass_g_at_1_24"] / 3682.4)
    )
    write_json(VAL / "geometry-master.json", geometry)

    sweep = text_sweep()
    write_json(VAL / "text-sweep.json", sweep)
    stiffness = stiffness_report()
    write_json(VAL / "stiffness-comparison.json", stiffness)
    threemf_reports = {
        side: validate_3mf_locally(paths[side]["3mf"]) for side in ("left", "right")
    }
    write_json(VAL / "3mf-master.json", {"status": "PASS", "reports": threemf_reports})

    artifacts = [
        paths[side][kind] for side in ("left", "right") for kind in ("step", "stl", "3mf")
    ] + [assembly, PROFILE, SRC / "nameform_bookends.py", nb.FONT_PATH, nb.FONT_LICENSE]
    summary = {
        "status": "PASS" if all([
            geometry["status"] == "PASS", sweep["status"] == "PASS",
            stiffness["pass"], all(r["status"] == "PASS" for r in threemf_reports.values()),
        ]) else "FAIL",
        "product_id": nb.PRODUCT_ID,
        "revision": nb.REVISION,
        "candidate": "unmarked master — DRAFT",
        "build_seconds": round(time.time() - start, 1),
        "environment": {
            "python": platform.python_version(),
            "cadquery": cq.__version__,
            "trimesh": trimesh.__version__,
            "shapely": shapely.__version__,
            "matplotlib": matplotlib.__version__,
            "platform": platform.platform(),
        },
        "artifacts": {
            str(path.relative_to(ROOT)): {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in artifacts
        },
        "checks": {
            "geometry": geometry["status"],
            "text_sweep": sweep["status"],
            "stiffness_comparison": "PASS" if stiffness["pass"] else "FAIL",
            "3mf_structure": "PASS" if all(r["status"] == "PASS" for r in threemf_reports.values()) else "FAIL",
            "exact_slicer": "NOT_RUN — no supported slicer executable on build host",
            "physical": "NOT_RUN — human boundary",
            "watermark": "NOT_RUN — intentionally deferred until the last solid change",
        },
    }
    write_json(VAL / "build-summary-master.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
