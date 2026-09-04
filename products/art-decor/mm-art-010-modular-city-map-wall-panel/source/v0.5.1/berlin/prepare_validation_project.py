#!/usr/bin/env python3
"""Create the hash-bound revision 0.5.1 validation contract."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
CANDIDATE = "digital-candidate-r4"
ROOT = PRODUCT / "validation" / "v0.5.1" / "berlin" / CANDIDATE
COUPON = PRODUCT / "validation" / "v0.5.1" / "berlin" / "logo-coupon-r1"
OUTPUT = ROOT / "validation-project.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact(identifier: str, path: Path, kind: str) -> dict:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"missing or empty validation artifact: {path}")
    return {
        "id": identifier,
        "path": os.path.relpath(path, ROOT),
        "kind": kind,
        "revision": "0.5.1",
        "sha256": sha256(path),
    }


def mesh_check(identifier: str, artifact_id: str, max_faces: int = 750000) -> dict:
    return {
        "id": identifier,
        "type": "mesh",
        "required": True,
        "artifact": artifact_id,
        "policy": {
            "require_watertight": True,
            "require_winding_consistent": True,
            "require_positive_volume": True,
            "expected_components": 1,
            "max_boundary_edges": 0,
            "max_nonmanifold_edges": 0,
            "max_degenerate_faces": 0,
            "max_duplicate_faces": 0,
            "bed_mm": [420.0, 420.0, 500.0],
            "allow_axis_permutation": False,
            "max_faces": max_faces,
            "max_file_mib": 75.0,
        },
    }


def report_check(identifier: str, artifact_id: str, expected_inputs: list[str] | None = None) -> dict:
    return {
        "id": identifier,
        "type": "external_report",
        "required": True,
        "artifact": artifact_id,
        "expected_inputs": expected_inputs or [],
    }


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite existing contract: {OUTPUT}")
    export = PRODUCT / "exports" / "v0.5.1" / "berlin" / CANDIDATE
    coupon_export = PRODUCT / "exports" / "v0.5.1" / "berlin" / "logo-coupon-r1"
    modes = {
        "boundary-left": ("boundary-crop", "left", "r1"),
        "boundary-right": ("boundary-crop", "right", "r1"),
        "context-left": ("context-outline", "left", "r2"),
        "context-right": ("context-outline", "right", "r1"),
    }
    artifacts: list[dict] = []
    checks: list[dict] = []
    for short, (mode, half, run) in modes.items():
        prefix = f"berlin-{mode}-{half}"
        mesh = export / mode / f"{prefix}-composite.stl"
        project = export / mode / f"{prefix}-oak-mint-midnight-sky-metrimade-anycubic.3mf"
        geometry = ROOT / "3mf" / f"{prefix}-geometry.json"
        adapter = ROOT / "anycubic-slices" / f"{short.replace('boundary-', 'boundary-crop-').replace('context-', 'context-outline-')}-{run}-adapter.json"
        review = ROOT / "anycubic-slices" / f"{short.replace('boundary-', 'boundary-crop-').replace('context-', 'context-outline-')}-{run}-review.json"
        gcode = ROOT / "anycubic-slices" / f"{short.replace('boundary-', 'boundary-crop-').replace('context-', 'context-outline-')}-{run}" / "plate_1.gcode"
        artifacts.extend(
            [
                artifact(f"{short}-mesh", mesh, "mesh"),
                artifact(f"{short}-3mf", project, "3mf"),
                artifact(f"{short}-geometry", geometry, "report"),
                artifact(f"{short}-adapter", adapter, "report"),
                artifact(f"{short}-gcode", gcode, "gcode"),
                artifact(f"{short}-review", review, "report"),
            ]
        )
        checks.append(mesh_check(f"{short}-mesh-audit", f"{short}-mesh"))
        checks.append(report_check(f"{short}-3mf-geometry", f"{short}-geometry"))
        checks.append(
            report_check(
                f"{short}-native-slice",
                f"{short}-review",
                [f"{short}-3mf", f"{short}-adapter", f"{short}-gcode"],
            )
        )

    artifacts.extend(
        [
            artifact("build-report", ROOT / "build-report.json", "report"),
            artifact("coupon-mesh", coupon_export / "metrimade-logo-coupon-composite.stl", "mesh"),
            artifact("coupon-3mf", coupon_export / "metrimade-logo-coupon-oak-sky-anycubic.3mf", "3mf"),
            artifact("coupon-build", COUPON / "build-report.json", "report"),
            artifact("coupon-geometry", COUPON / "3mf-geometry.json", "report"),
            artifact("coupon-adapter", COUPON / "anycubic-slices" / "coupon-r2-adapter.json", "report"),
            artifact("coupon-gcode", COUPON / "anycubic-slices" / "coupon-r2" / "plate_1.gcode", "gcode"),
            artifact("coupon-review", COUPON / "anycubic-slices" / "coupon-r2-review.json", "report"),
        ]
    )
    checks.extend(
        [
            mesh_check("coupon-mesh-audit", "coupon-mesh", max_faces=100000),
            report_check("build-report-status", "build-report"),
            report_check("coupon-build-status", "coupon-build"),
            report_check("coupon-3mf-geometry", "coupon-geometry"),
            report_check(
                "coupon-native-slice",
                "coupon-review",
                ["coupon-3mf", "coupon-adapter", "coupon-gcode"],
            ),
            {
                "id": "generic-anycubic-comment-parser",
                "type": "review",
                "required": False,
                "status": "REVIEW_REQUIRED",
                "criterion": "Canonical layer markers control the gate because the generic parser also counts Anycubic supplemental layer comments.",
            },
            {
                "id": "context-left-runtime",
                "type": "review",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Accept or optimize context-outline left native slicing, which timed out at 900 seconds and completed only in the controlled 1800 second retry.",
            },
            {
                "id": "context-left-floating-regions-gui",
                "type": "review",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Human inspects the context-outline left layer preview and confirms that the native floating-regions warning corresponds only to intentionally stacked color volumes and requires no supports.",
            },
            {
                "id": "ace-purge-gui-review",
                "type": "review",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Human approves exact four-spool ACE mapping, purge matrix, wipe tower, transition layers and seams in Anycubic Slicer Next.",
            },
            {
                "id": "logo-recognition-coupon",
                "type": "physical",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "The Oak/Sky Blue coupon is printed and the metriMade logo is recognized at 2.0 m under ordinary indoor lighting.",
            },
            {
                "id": "connector-light-wall-proof",
                "type": "physical",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Connector, mount, optional-light envelope and permanently assembled wall proof pass their project criteria.",
            },
            {
                "id": "watermark-rights-release",
                "type": "review",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Rear release watermark, brand/map rights, safety and commercial release are separately approved.",
            },
        ]
    )
    project = {
        "schema_version": "1.0",
        "project": {
            "id": "MM-ART-010-berlin-metrimade-marker",
            "revision": "0.5.1",
            "units": "mm",
            "risk_class": "decorative",
            "build_volume_mm": [420.0, 420.0, 500.0],
        },
        "artifacts": artifacts,
        "checks": checks,
        "release": {"required_approvals": [], "approvals": {}},
    }
    OUTPUT.write_text(json.dumps(project, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "output": str(OUTPUT), "artifacts": len(artifacts), "checks": len(checks)}))


if __name__ == "__main__":
    main()
