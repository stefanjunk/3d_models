#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-018."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
REPORT_PATHS = [
    "validation/parametric-source-report.json", "validation/mesh-generation-report.json", "validation/interface-report.json",
    "validation/fdm-mesh-radius-r02.json", "validation/fdm-mesh-radius-r04.json", "validation/fdm-mesh-radius-r06.json",
    "validation/fdm-mesh-radius-r08.json", "validation/fdm-mesh-radius-r10.json", "validation/fdm-mesh-radius-r12.json",
    "validation/fdm-mesh-height-card.json", "validation/fdm-mesh-clearance-comb.json", "validation/fdm-mesh-calibration-frame.json",
    "validation/fdm-3mf.json", "validation/slicer-anycubic-next.json", "validation/approvals-through-slicer.json",
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
    warnings = [item.get("warning_message", "") for item in slicer.get("native_result", {}).get("sliced_plates", []) if item.get("warning_message", "").strip()]
    checks.extend([
        check("gcode-report", len(gcode_reports) == 1 and gcode_reports[0].get("status") == "PASS", "Exactly one temporary G-code analysis reports PASS"),
        check("fifteen-layers", metrics.get("layers_from_comments") == 15, "3.0 mm tools slice as fifteen 0.20 mm layers"),
        check("native-slicer-warnings", not warnings, "Native slicer returned no object warnings", {"warnings": warnings}),
        check("one-tool", metrics.get("tools_seen") == [0] and metrics.get("tool_changes") == 0, "One tool and no tool changes"),
        check("accuracy-gate-deferred", True, "Printed dimensions and ten-drawer user error remain outside this digital candidate"),
        check("watermark-gate-deferred", True, "Final watermark, accuracy claims and commercial release remain blocked"),
    ])
    output = {
        "schema_version": "1.0", "tool": "MM-ORG-018-finalize-digital-candidate", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": [record(path) for path in reports], "checks": checks,
        "metrics": {
            "build_sets": 1, "unique_meshes": 9, "objects": 10, "layers": metrics.get("layers_from_comments"),
            "slicer_estimate_seconds": metrics.get("slicer_metadata_time_s"), "extruded_volume_mm3": metrics.get("extruded_volume_mm3"),
            "positive_extrusion_mm": metrics.get("positive_extrusion_total_mm"), "peak_flow_mm3_s": metrics.get("peak_flow_mm3_s"),
            "tools_seen": metrics.get("tools_seen", []), "physical_validation": "DEFERRED", "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE",
        },
        "limitations": [
            "Nominal increments and analytic CAD dimensions are not printed accuracy results.",
            "Headless slicing does not replace layer preview, caliper comparison or a physical print.",
            "The ten-drawer mean-user-error target has not been measured.",
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
