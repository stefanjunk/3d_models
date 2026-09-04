#!/usr/bin/env python3
"""Generate the concise, hash-bound revision 0.5.1 candidate summaries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
REPO = PRODUCT.parents[2]
CANDIDATE = "digital-candidate-r4"
VALIDATION = PRODUCT / "validation" / "v0.5.1" / "berlin" / CANDIDATE
EXPORT = PRODUCT / "exports" / "v0.5.1" / "berlin" / CANDIDATE
COUPON_VALIDATION = PRODUCT / "validation" / "v0.5.1" / "berlin" / "logo-coupon-r1"
COUPON_EXPORT = PRODUCT / "exports" / "v0.5.1" / "berlin" / "logo-coupon-r1"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(PRODUCT))


def project_entry(mode: str, half: str, run: str) -> tuple[dict, dict]:
    prefix = f"berlin-{mode}-{half}"
    project = EXPORT / mode / f"{prefix}-oak-mint-midnight-sky-metrimade-anycubic.3mf"
    geometry_path = VALIDATION / "3mf" / f"{prefix}-geometry.json"
    review_path = VALIDATION / "anycubic-slices" / f"{mode}-{half}-{run}-review.json"
    geometry = read_json(geometry_path)
    review = read_json(review_path)
    assert geometry["status"] == "PASS"
    assert review["status"] == "PASS"
    entry = {
        "path": rel(project),
        "sha256": sha256(project),
        "components": geometry["totals"]["components"],
        "triangles": geometry["totals"]["triangles"],
        "volume_mm3": round(geometry["totals"]["volume_mm3"], 4),
    }
    metrics = review["metrics"]
    slice_entry = {
        "layers": metrics["canonical_layer_change_markers"],
        "max_z_mm": metrics["canonical_maximum_z_mm"],
        "tools": metrics["tools_seen"],
        "tool_changes": metrics["tool_changes"],
        "status": "PASS_WITH_PERFORMANCE_AND_GUI_REVIEW"
        if mode == "context-outline" and half == "left"
        else "PASS",
    }
    return entry, slice_entry


def main() -> None:
    build = read_json(VALIDATION / "build-report.json")
    aggregate = read_json(VALIDATION / "validation-summary-draft.json")
    assert build["status"] == "PASS"
    assert aggregate["status"] == "REVIEW_REQUIRED"
    modes = {
        "boundary_crop": ("boundary-crop", "r1", "r1"),
        "context_outline": ("context-outline", "r2", "r1"),
    }
    examples: dict[str, dict] = {}
    for public_mode, (path_mode, left_run, right_run) in modes.items():
        left_3mf, left_slice = project_entry(path_mode, "left", left_run)
        right_3mf, right_slice = project_entry(path_mode, "right", right_run)
        examples[public_mode] = {
            "left_3mf": left_3mf,
            "right_3mf": right_3mf,
            "left_slice": left_slice,
            "right_slice": right_slice,
        }

    coupon_project = COUPON_EXPORT / "metrimade-logo-coupon-oak-sky-anycubic.3mf"
    coupon_geometry = read_json(COUPON_VALIDATION / "3mf-geometry.json")
    coupon_review = read_json(COUPON_VALIDATION / "anycubic-slices" / "coupon-r2-review.json")
    coupon_build = read_json(COUPON_VALIDATION / "build-report.json")
    assert coupon_geometry["status"] == coupon_review["status"] == coupon_build["status"] == "PASS"

    marker = build["site_marker"]
    mode_markers = build["modes"]
    summary = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.1",
        "candidate": CANDIDATE,
        "status": "DRAFT_DIGITAL_PASS_REVIEW_REQUIRED",
        "selected_palette": build["selected_palette"],
        "site_marker": {
            "address": marker["address"],
            "coordinate_epsg25833": marker["coordinate_epsg25833"],
            "artwork_id": marker["artwork_id"],
            "artwork": marker["artwork"],
            "artwork_sha256": marker["artwork_sha256"],
            "size_mm": marker["renderer"]["physical_size_mm"],
            "relief_height_mm": 0.6,
            "semantic_tool": marker["semantic_tool"],
            "placement": {
                name: data["site_marker"]["center_mm"] for name, data in mode_markers.items()
            },
            "minimum_aperture_clearance_mm": min(
                data["site_marker"]["aperture_keepout"]["measured_clearance_mm"]
                for data in mode_markers.values()
            ),
            "recognition_distance_target_mm": marker["recognition_distance_target_mm"],
            "physical_recognition": "NOT_RUN",
        },
        "examples": examples,
        "logo_coupon": {
            "path": rel(coupon_project),
            "sha256": sha256(coupon_project),
            "size_mm": [84.0, 88.0, 3.0],
            "logo_size_mm": marker["renderer"]["physical_size_mm"],
            "relief_height_mm": 0.6,
            "semantic_tools": [1, 4],
            "components": coupon_geometry["totals"]["components"],
            "triangles": coupon_geometry["totals"]["triangles"],
            "slice": {
                "layers": coupon_review["metrics"]["canonical_layer_change_markers"],
                "max_z_mm": coupon_review["metrics"]["canonical_maximum_z_mm"],
                "tools": coupon_review["metrics"]["tools_seen"],
                "tool_changes": coupon_review["metrics"]["tool_changes"],
                "status": coupon_review["status"],
            },
            "physical_recognition": "NOT_RUN",
        },
        "digital_gates": [
            {"id": "geometry-build", "status": "PASS", "evidence": rel(VALIDATION / "build-report.json")},
            {"id": "composite-mesh-audits", "status": "PASS", "evidence": rel(VALIDATION / "mesh-audits")},
            {"id": "vendor-aware-3mf-geometry", "status": "PASS", "evidence": rel(VALIDATION / "3mf"), "details": "Every project resolves non-empty named source meshes and the intended semantic tool assignments."},
            {"id": "native-anycubic-import-slice", "status": "PASS", "evidence": rel(VALIDATION / "anycubic-slices"), "details": "All four projects produced non-empty exact G-code with canonical layers and tools 0-3; the coupon used tools 0 and 3."},
            {"id": "aggregate-draft-validation", "status": "REVIEW_REQUIRED", "evidence": rel(VALIDATION / "validation-summary-draft.json"), "details": "All 49 deterministic checks pass; seven human/physical checks remain review-required."},
            {"id": "context-left-runtime", "status": "REVIEW_REQUIRED", "evidence": rel(VALIDATION / "anycubic-slices" / "context-outline-left-r2-adapter.json"), "details": "The first 900 second run timed out; the controlled 1800 second retry completed natively."},
            {"id": "context-left-floating-regions", "status": "REVIEW_REQUIRED", "evidence": rel(VALIDATION / "anycubic-slices" / "context-outline-left-r2-adapter.json"), "details": "Anycubic emitted a floating-regions warning; a human must inspect the layer preview before deciding whether support is needed."},
            {"id": "generic-anycubic-comment-parser", "status": "LIMITATION_NOT_PRODUCT_FAILURE", "evidence": rel(VALIDATION / "validation-summary-draft.json"), "details": "The generic parser also counts supplemental Anycubic layer comments; the native header, summary and canonical markers agree."},
        ],
        "open_human_gates": [
            "Print the Oak/Sky Blue coupon and recognize the intended metriMade logo at 2.0 m under ordinary indoor lighting.",
            "Inspect context-outline left in the Anycubic GUI and resolve the floating-regions warning.",
            "Confirm exact physical spool batches, conditioning and four ACE slot assignments.",
            "Approve wipe tower, purge behavior, transition layers and seams.",
            "Print and qualify connector/socket and passive light/opacity coupons, then assemble and wall-proof the selected artwork.",
            "Approve rear watermark, brand/map rights, safety and commercial release.",
        ],
        "prohibited_actions_not_performed": ["printer upload", "print start"],
    }
    (VALIDATION / "digital-candidate-summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    rows = []
    for public_mode in ("boundary_crop", "context_outline"):
        item = examples[public_mode]
        for half in ("left", "right"):
            project = item[f"{half}_3mf"]
            sliced = item[f"{half}_slice"]
            result = "Pass"
            if sliced["status"] != "PASS":
                result = "Pass; Laufzeit- und GUI-Prüfung offen"
            rows.append(
                f"| `{public_mode}` {half} | {project['triangles']:,} | {sliced['layers']} | {sliced['tool_changes']} | {result} |"
            )
    markdown = f"""# MM-ART-010 Berlin — DRAFT {CANDIDATE}

Alle vier nativen Anycubic-Projektdateien enthalten vier nichtleere Werkzeugkörper und wurden in Anycubic Slicer Next nativ gesliced. Das schließt insbesondere den früher gemeldeten Geometrieverlust der rechten 3MF-Datei. Ein Druck oder eine kommerzielle Freigabe wird damit nicht autorisiert.

| Modus / Hälfte | 3MF-Dreiecke | Native Layer | Werkzeugwechsel | Ergebnis |
|---|---:|---:|---:|---|
{chr(10).join(rows)}

Die linken Hälften tragen das kanonische, gestapelte metriMade-Logo mit 54. × 57.176 mm am eingefrorenen Adresspunkt. Es liegt 0.6 mm erhaben in Sky Blue/Werkzeug 4 und hält mindestens 12.253 mm Abstand zu einer Lichtöffnung. Karten-, Teilungs-, Steckverbinder- und Lichtgeometrie wurden gegenüber der freigegebenen Basis nicht neu gestaltet.

Der separate 84 × 88 mm Coupon enthält die Originalgröße des Logos in Oak/Sky Blue, zwei nichtleere Körper auf den semantischen Werkzeugen 1 und 4 und wurde mit 15 Layern nativ gesliced. Die Erkennbarkeit aus 2 m ist noch **nicht** physisch geprüft.

Alle 49 deterministischen Prüfungen im hashgebundenen Entwurfsvertrag bestehen. Sieben Prüfungen bleiben `REVIEW_REQUIRED`: 2-m-Erkennung, ACE/Purge, die Anycubic-Warnung zu schwebenden Bereichen beim linken Umlandteil, dessen längere Slice-Laufzeit, Steckverbinder/Licht/Wandnachweis sowie Wasserzeichen/Rechte/Freigabe. Beim linken Umlandteil beendete erst der kontrollierte 1800-s-Wiederholungslauf den nativen Slice; die erste 900-s-Ausführung lief ins Zeitlimit.
"""
    (VALIDATION / "digital-candidate-summary.md").write_text(markdown)

    r1 = read_json(PRODUCT / "validation" / "v0.5.1" / "berlin" / "digital-candidate-r1" / "build-report.json")
    r3 = read_json(PRODUCT / "validation" / "v0.5.1" / "berlin" / "triangulation-diagnostic-r3" / "audit.json")
    repair = read_json(PRODUCT / "validation" / "v0.5.1" / "berlin" / "triangulation-diagnostic-r3" / "micro-repair-report.json")
    iteration = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.1",
        "iterations": [
            {"candidate": "digital-candidate-r1", "status": "REJECTED", "evidence_sha256": sha256(PRODUCT / "validation" / "v0.5.1" / "berlin" / "digital-candidate-r1" / "build-report.json"), "reason": "Boundary-crop left had one numerical degenerate face although it remained watertight, positive and single-component.", "degenerate_faces": r1["modes"]["boundary_crop"]["halves"]["left"]["composite"]["degenerate_faces"]},
            {"candidate": "digital-candidate-r2", "status": "REJECTED", "reason": "Aggressive dissolve cleanup split the boundary-left composite into two positive watertight components; no production artifact was accepted."},
            {"candidate": "triangulation-diagnostic-r3", "status": "REJECTED", "evidence_sha256": sha256(PRODUCT / "validation" / "v0.5.1" / "berlin" / "triangulation-diagnostic-r3" / "audit.json"), "reason": "EAR_CLIP triangulation increased the numerical degenerates and was rejected.", "degenerate_faces": r3["metrics"]["exact_coordinate_welded"]["degenerate_faces"]},
            {"candidate": CANDIDATE, "status": "DRAFT_DIGITAL_PASS_REVIEW_REQUIRED", "reason": "A deterministic topology-preserving one-ULP repair removed the single numerical degeneracy without changing face count, bounds, topology or meaningful volume.", "repair": repair["trace"]},
        ],
    }
    iteration_path = PRODUCT / "validation" / "v0.5.1" / "berlin" / "build-iteration-summary.json"
    iteration_path.write_text(json.dumps(iteration, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "summary": rel(VALIDATION / "digital-candidate-summary.json"), "iterations": rel(iteration_path)}))


if __name__ == "__main__":
    main()
