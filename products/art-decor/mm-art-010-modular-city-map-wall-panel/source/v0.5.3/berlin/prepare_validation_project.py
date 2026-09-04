#!/usr/bin/env python3
"""Create the hash-bound revision 0.5.3 validation contract."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
CANDIDATE = "digital-candidate-r4"
ROOT = PRODUCT / "validation" / "v0.5.3" / "berlin" / CANDIDATE
EXPORT = PRODUCT / "exports" / "v0.5.3" / "berlin" / CANDIDATE
SOURCE = PRODUCT / "source-data" / "v0.5.3" / "berlin"
OUTPUT = ROOT / "validation-project-r2.json"
ATTESTATION = ROOT / "digital-source-build-attestation.json"


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
        "revision": "0.5.3",
        "sha256": sha256(path),
    }


def report_check(identifier: str, artifact_id: str, expected_inputs=None) -> dict:
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
    build_report = ROOT / "build-report.json"
    source_manifest = SOURCE / "source-manifest.json"
    if ATTESTATION.exists():
        raise SystemExit(f"refusing to overwrite existing attestation: {ATTESTATION}")
    build = json.loads(build_report.read_text())
    source = json.loads(source_manifest.read_text())
    attestation = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.3",
        "status": "PASS" if build.get("status") == source.get("status") == "PASS" else "FAIL",
        "input_hashes": {
            "build_report": sha256(build_report),
            "source_manifest": sha256(source_manifest),
        },
        "checks": {
            "build_report_passed": build.get("status") == "PASS",
            "source_manifest_passed": source.get("status") == "PASS",
            "tegeler_see_source_fixture_passed": source.get("named_regression_fixtures", {}).get("tegeler_see", {}).get("feature_count") == 1
            and source.get("named_regression_fixtures", {}).get("tegeler_see", {}).get("area_m2", 0) > 0,
        },
    }
    if not all(attestation["checks"].values()):
        raise ValueError(f"digital source/build attestation failed: {attestation['checks']}")
    ATTESTATION.write_text(json.dumps(attestation, indent=2) + "\n")
    runs = {
        "boundary-left": ("boundary-crop", "left", "r2"),
        "boundary-right": ("boundary-crop", "right", "r1"),
        "context-left": ("context-outline", "left", "r1"),
        "context-right": ("context-outline", "right", "r1"),
    }
    artifacts = [
        artifact("build-report", build_report, "report"),
        artifact("source-manifest", source_manifest, "report"),
        artifact("source-build-attestation", ATTESTATION, "report"),
    ]
    checks = [
        report_check(
            "source-build-status",
            "source-build-attestation",
            ["build-report", "source-manifest"],
        ),
    ]
    for short, (mode, half, run) in runs.items():
        prefix = f"berlin-{mode}-{half}"
        stem = f"{prefix}-oak-mint-midnight-sky-metrimade-water-transit-anycubic"
        mesh = EXPORT / mode / f"{prefix}-composite.stl"
        project = EXPORT / mode / f"{stem}.3mf"
        packaging = ROOT / "3mf" / f"{stem}-packaging.json"
        geometry = ROOT / "3mf" / f"{stem}-geometry-r2.json"
        adapter = ROOT / "anycubic-slices" / f"{mode}-{half}-{run}-adapter.json"
        review = ROOT / "anycubic-slices" / f"{mode}-{half}-{run}-review.json"
        gcode = ROOT / "anycubic-slices" / f"{mode}-{half}-{run}" / "plate_1.gcode"
        artifacts.extend(
            [
                artifact(f"{short}-mesh", mesh, "mesh"),
                artifact(f"{short}-3mf", project, "3mf"),
                artifact(f"{short}-packaging", packaging, "report"),
                artifact(f"{short}-geometry", geometry, "report"),
                artifact(f"{short}-adapter", adapter, "report"),
                artifact(f"{short}-gcode", gcode, "gcode"),
                artifact(f"{short}-review", review, "report"),
            ]
        )
        checks.extend(
            [
                {
                    "id": f"{short}-mesh-audit",
                    "type": "mesh",
                    "required": True,
                    "artifact": f"{short}-mesh",
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
                        "max_faces": 750000,
                        "max_file_mib": 75.0,
                    },
                },
                report_check(
                    f"{short}-3mf-geometry", f"{short}-geometry", [f"{short}-3mf", f"{short}-packaging"]
                ),
                report_check(
                    f"{short}-native-slice", f"{short}-review", [f"{short}-3mf", f"{short}-adapter", f"{short}-gcode"]
                ),
            ]
        )
    checks.extend(
        [
            {
                "id": "generic-anycubic-comment-parser",
                "type": "review",
                "required": False,
                "status": "REVIEW_REQUIRED",
                "criterion": "The generic parser double-counts supplemental Anycubic layer comments; canonical project-local reviews control the layer gate.",
            },
            {
                "id": "ace-purge-gui-review",
                "type": "review",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Human approves physical ACE slots, purge matrix, wipe tower, transition layers and seams.",
            },
            {
                "id": "bridge-handling-wall-proof",
                "type": "physical",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Printed topology bridges, two-half handling and the independently supported installed artwork pass the project proof-load procedure.",
            },
            {
                "id": "connector-light-appearance",
                "type": "physical",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Connector, halo gap, light-through appearance, opacity and unlit appearance pass physical review.",
            },
            {
                "id": "logo-recognition-coupon",
                "type": "physical",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "The inherited process-matched Oak/Sky Blue coupon is recognized at 2 m.",
            },
            {
                "id": "watermark-rights-release",
                "type": "review",
                "required": True,
                "status": "REVIEW_REQUIRED",
                "criterion": "Rear product watermark, logo/map rights, safety and commercial release receive approval.",
            },
        ]
    )
    project = {
        "schema_version": "1.0",
        "project": {
            "id": "MM-ART-010-berlin-water-transit",
            "revision": "0.5.3",
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
