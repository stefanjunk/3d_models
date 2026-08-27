#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-011."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
REPORTS = [
    ROOT / "validation/parametric-source-report.json",
    ROOT / "validation/mesh-generation-report.json",
    ROOT / "validation/interface-report.json",
    ROOT / "validation/fdm-mesh-rack.json",
    ROOT / "validation/fdm-mesh-card.json",
    ROOT / "validation/fdm-3mf.json",
    ROOT / "validation/slicer-preflight-anycubic-kobra3max-pla.json",
    ROOT / "validation/approvals-through-slicer.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True,
            "message": message, "metrics": metrics or {}, "evidence": []}


def main() -> None:
    loaded = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in REPORTS}
    checks = [
        check(f"report:{name}", value.get("status") == "PASS", f"{name} reports PASS")
        for name, value in loaded.items()
    ]
    slicer = loaded["slicer-preflight-anycubic-kobra3max-pla.json"]
    native_warnings = [
        item.get("warning_message", "")
        for item in slicer.get("native_result", {}).get("sliced_plates", [])
        if item.get("warning_message", "").strip()
    ]
    gcode_reports = list(slicer.get("gcode_reports", {}).values())
    checks.extend([
        check("native-slicer-warnings", not native_warnings, "Native slicer returned no object warnings", {"warnings": native_warnings}),
        check("gcode-report", len(gcode_reports) == 1 and gcode_reports[0].get("status") == "PASS", "Exactly one G-code analysis reports PASS"),
        check("physical-gate-deferred", True, "Physical fit, abrasion, cycle and stability checks remain outside this digital candidate"),
        check("watermark-gate-deferred", True, "Final watermark and commercial release remain blocked"),
    ])
    metrics = gcode_reports[0].get("metrics", {}) if gcode_reports else {}
    output = {
        "schema_version": "1.0",
        "tool": "MM-ORG-011-finalize-digital-candidate",
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [input_record(path) for path in REPORTS],
        "checks": checks,
        "metrics": {
            "layers": metrics.get("layers_from_comments"),
            "slicer_estimate_seconds": metrics.get("slicer_metadata_time_s"),
            "extruded_volume_mm3": metrics.get("extruded_volume_mm3"),
            "positive_extrusion_mm": metrics.get("positive_extrusion_total_mm"),
            "peak_flow_mm3_s": metrics.get("peak_flow_mm3_s"),
            "tools_seen": metrics.get("tools_seen"),
            "physical_validation": "DEFERRED",
            "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE",
        },
        "limitations": [
            "The fifteen default hook profiles are dimensional simulations, not measured customer hooks.",
            "Headless slicing does not replace layer-preview inspection or a physical print.",
            "No printer upload or print-start action was performed.",
        ],
        "required_capabilities": [],
    }
    path = ROOT / "validation/print-candidate-report.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "output": str(path)}, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
