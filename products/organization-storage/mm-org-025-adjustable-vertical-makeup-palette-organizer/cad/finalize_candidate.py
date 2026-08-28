#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-025."""
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
    "validation/fdm-mesh-palette-grid-base.json",
    "validation/fdm-mesh-removable-divider.json",
    "validation/fdm-mesh-slot-gauge.json",
    "validation/fdm-mesh-divider-fit-key.json",
    "validation/fdm-3mf.json",
    "validation/slicer-anycubic-next.json",
    "validation/approvals-through-slicer.json",
    "reports/photo-capture-example-output.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def main() -> None:
    reports = [ROOT / item for item in REPORT_PATHS]
    loaded = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in reports}
    checks = [check(f"report:{name}", value.get("status") == "PASS", f"{name} reports PASS") for name, value in loaded.items()]
    slicer = loaded["slicer-anycubic-next.json"]
    gcode_reports = list(slicer.get("gcode_reports", {}).values())
    metrics = gcode_reports[0].get("metrics", {}) if len(gcode_reports) == 1 else {}
    warnings = [
        item.get("warning_message", "")
        for item in slicer.get("native_result", {}).get("sliced_plates", [])
        if item.get("warning_message", "").strip()
    ]
    interfaces = loaded["interface-report.json"].get("metrics", {}).get("interfaces", {})
    base = interfaces.get("palette-grid-base", {})
    divider = interfaces.get("removable-divider", {})
    gauge = interfaces.get("slot-gauge", {})
    key = interfaces.get("divider-fit-key", {})
    capture = loaded["photo-capture-example-output.json"]
    checks.extend([
        check("gcode-report", len(gcode_reports) == 1 and gcode_reports[0].get("status") == "PASS", "Exactly one temporary G-code analysis reports PASS"),
        check("expected-height", metrics.get("layers_from_comments") == 50, "10 mm maximum print height slices as 50 layers at 0.20 mm"),
        check("native-slicer-warnings", not warnings, "Native slicer returned no object warnings", {"warnings": warnings}),
        check("one-tool", metrics.get("tools_seen") == [0] and metrics.get("tool_changes") == 0, "One tool and no tool changes"),
        check("grid-contract", len(base.get("slot_positions_x_mm", [])) == 16 and base.get("default_divider_indices") == [0, 2, 4, 6, 8, 11, 15], "Sixteen stations and default seven-divider layout remain exact"),
        check("protected-slot", base.get("slot_width_mm") == 2.9 and divider.get("tongue_thickness_mm") == 2.4, "Production slot and divider tongue retain 0.5 mm total clearance"),
        check("coupon-bracket", gauge.get("candidate_slot_widths_mm") == [2.7, 2.9, 3.1] and key.get("tongue_thickness_mm") == divider.get("tongue_thickness_mm"), "Coupon brackets production and reproduces the real tongue"),
        check("default-compartments", base.get("default_compartment_clear_mm") == [20.6, 20.6, 20.6, 20.6, 32.1, 43.6], "Six default clear compartments remain exact"),
        check("photo-capture", capture.get("closed_face_width_mm") == 130.0 and capture.get("closed_face_height_mm") == 71.0 and capture.get("closed_thickness_mm") == 15.2, "Calibration example reproduces the expected measured dimensions"),
        check("physical-gates-deferred", True, "Fit, tip, abrasion, retrieval and 500-cycle tests remain user-owned"),
    ])
    output = {
        "schema_version": "1.0",
        "tool": "MM-ORG-025-finalize-digital-candidate",
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [record(path) for path in reports],
        "checks": checks,
        "metrics": {
            "build_sets": 1,
            "unique_meshes": 4,
            "objects": 10,
            "layers": metrics.get("layers_from_comments"),
            "slicer_estimate_seconds": metrics.get("slicer_metadata_time_s"),
            "extruded_volume_mm3": metrics.get("extruded_volume_mm3"),
            "positive_extrusion_mm": metrics.get("positive_extrusion_total_mm"),
            "peak_flow_mm3_s": metrics.get("peak_flow_mm3_s"),
            "tools_seen": metrics.get("tools_seen", []),
            "physical_validation": "DEFERRED",
            "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE",
        },
        "limitations": [
            "The nominal 2.9 mm slot is a digital candidate; the included coupon must select the real printer/material fit.",
            "A calibrated overhead photo measures the closed face plane only; maximum closed thickness requires calipers.",
            "Headless slicing does not replace final layer preview or a physical print.",
            "Divider retention, 500-cycle wear, palette-case marking, retrieval comfort and loaded tip stability remain untested.",
            "The organizer has no universal-fit, hygiene, sanitation, heat-resistance or scratch-resistance claim.",
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
