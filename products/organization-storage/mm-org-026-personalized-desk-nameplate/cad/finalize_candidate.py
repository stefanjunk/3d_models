#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-026."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
REPORT_PATHS = [
    "validation/parametric-source-report.json",
    "validation/mesh-generation-report.json",
    "validation/interface-report.json",
    "validation/fdm-mesh-personalized-insert.json",
    "validation/fdm-mesh-angled-end-stand.json",
    "validation/fdm-mesh-angled-slot-gauge.json",
    "validation/fdm-mesh-insert-fit-key.json",
    "validation/fdm-3mf.json",
    "validation/slicer-anycubic-next.json",
    "validation/approvals-through-slicer.json",
    "reports/live-text-preview.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def main() -> None:
    reports = [ROOT / item for item in REPORT_PATHS]
    loaded = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in reports}
    checks = [
        check(f"report:{name}", value.get("status") == "PASS", f"{name} reports PASS")
        for name, value in loaded.items()
    ]
    slicer = loaded["slicer-anycubic-next.json"]
    gcode_reports = list(slicer.get("gcode_reports", {}).values())
    metrics = gcode_reports[0].get("metrics", {}) if len(gcode_reports) == 1 else {}
    warnings = [
        item.get("warning_message", "")
        for item in slicer.get("native_result", {}).get("sliced_plates", [])
        if item.get("warning_message", "").strip()
    ]
    interfaces = loaded["interface-report.json"].get("metrics", {}).get("interfaces", {})
    insert = interfaces.get("personalized-insert", {})
    stand = interfaces.get("angled-end-stand", {})
    gauge = interfaces.get("angled-slot-gauge", {})
    key = interfaces.get("insert-fit-key", {})
    proof = loaded["live-text-preview.json"].get("metrics", {})
    checks.extend([
        check("gcode-report", len(gcode_reports) == 1 and gcode_reports[0].get("status") == "PASS", "Exactly one temporary G-code analysis reports PASS"),
        check("expected-height", metrics.get("layers_from_comments") == 100, "20 mm maximum print height slices as 100 layers at 0.20 mm"),
        check("native-slicer-warnings", not warnings, "Native slicer returned no object warnings", {"warnings": warnings}),
        check("one-tool", metrics.get("tools_seen") == [0] and metrics.get("tool_changes") == 0, "One tool and no tool changes"),
        check("protected-slot", stand.get("slot_width_mm") == 3.4 and insert.get("outer_dimensions_mm", [None, None, None])[2] == 3.0, "Production slot and insert retain 0.4 mm total clearance"),
        check("coupon-bracket", gauge.get("candidate_slot_widths_mm") == [3.2, 3.4, 3.6] and key.get("thickness_mm") == 3.0, "Coupon brackets production and reproduces the real insert thickness"),
        check("font-identity", insert.get("font_id") == proof.get("font_id") == "MM-GRID-5X7-v1", "CAD and exact live proof retain the repository-owned glyph identity"),
        check("proof-text", insert.get("normalized_name") == proof.get("normalized_name") and insert.get("normalized_title") == proof.get("normalized_title"), "CAD and exact live proof retain identical normalized text"),
        check("minimum-pixels", min(proof.get("name_layout", {}).get("pixel_width_mm", 0), proof.get("title_layout", {}).get("pixel_width_mm", 0)) >= 0.8, "Both text lines retain the 0.8 mm printable minimum pixel width"),
        check("privacy-contract", proof.get("privacy") == "do_not_retain_customer_names_outside_order_and_proof_records", "Proof report retains the privacy-minimizing customer-data contract"),
        check("physical-gates-deferred", True, "Fit, tip, legibility, abrasion and cycle tests remain user-owned"),
    ])
    output = {
        "schema_version": "1.0",
        "tool": "MM-ORG-026-finalize-digital-candidate",
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [record(path) for path in reports],
        "checks": checks,
        "metrics": {
            "build_sets": 1,
            "unique_meshes": 4,
            "objects": 5,
            "layers": metrics.get("layers_from_comments"),
            "slicer_estimate_seconds": metrics.get("slicer_metadata_time_s"),
            "extruded_volume_mm3": metrics.get("extruded_volume_mm3"),
            "positive_extrusion_mm": metrics.get("positive_extrusion_total_mm"),
            "peak_flow_mm3_s": metrics.get("peak_flow_mm3_s"),
            "tools_seen": metrics.get("tools_seen", []),
            "font_id": proof.get("font_id"),
            "physical_validation": "DEFERRED",
            "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE",
        },
        "limitations": [
            "The nominal 3.4 mm stand slot is a digital candidate; the included coupon must select the real printer/material fit.",
            "The SVG is an exact text-layout proof, not evidence of engraved contrast or customer approval.",
            "Headless slicing does not replace final layer preview or a physical print.",
            "Text legibility, stand retention, tip resistance, desk marking, 250 insert cycles and long-term creep remain untested.",
            "The product has no affiliation, accessibility, outdoor, heat-resistance or scratch-resistance claim.",
            "Commercial release and customer-specific proof approval remain separate human gates.",
            "No G-code was retained and no printer upload or print-start action was performed.",
        ],
        "required_capabilities": [],
    }
    path = ROOT / "validation/print-candidate-report.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "output": str(path), "metrics": output["metrics"]}, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
