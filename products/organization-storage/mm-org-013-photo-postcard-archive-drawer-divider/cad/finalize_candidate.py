#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-013."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
BASE_REPORTS = [
    "validation/parametric-source-report.json",
    "validation/mesh-generation-report.json",
    "validation/interface-report.json",
]
MESH_REPORTS = [
    "validation/fdm-mesh-frame.json",
    *[f"validation/fdm-mesh-divider-{label}.json" for label in ("1900", "1980", "2000", "2010", "2020", "2025")],
    "validation/fdm-mesh-gauge-10x15.json",
    "validation/fdm-mesh-gauge-a6.json",
    "validation/fdm-mesh-gauge-13x18.json",
]
PACKAGE_REPORTS = [
    "validation/fdm-3mf-primary.json",
    "validation/fdm-3mf-secondary.json",
    "validation/fdm-3mf-gauges.json",
]
SLICER_REPORTS = [
    "validation/slicer-primary-anycubic-next.json",
    "validation/slicer-secondary-anycubic-next.json",
    "validation/slicer-gauges-anycubic-next.json",
]
REPORTS = [ROOT / item for item in BASE_REPORTS + MESH_REPORTS + PACKAGE_REPORTS + SLICER_REPORTS] + [
    ROOT / "validation/approvals-through-slicer.json"
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
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def main() -> None:
    loaded = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in REPORTS}
    checks = [
        check(f"report:{name}", value.get("status") == "PASS", f"{name} reports PASS")
        for name, value in loaded.items()
    ]

    plate_metrics = []
    native_warnings = []
    for report_name in (Path(item).name for item in SLICER_REPORTS):
        slicer = loaded[report_name]
        native_warnings.extend(
            item.get("warning_message", "")
            for item in slicer.get("native_result", {}).get("sliced_plates", [])
            if item.get("warning_message", "").strip()
        )
        gcode_reports = list(slicer.get("gcode_reports", {}).values())
        valid = len(gcode_reports) == 1 and gcode_reports[0].get("status") == "PASS"
        checks.append(check(f"gcode-report:{report_name}", valid, f"Exactly one G-code analysis in {report_name} reports PASS"))
        if gcode_reports:
            plate_metrics.append(gcode_reports[0].get("metrics", {}))

    checks.extend(
        [
            check("native-slicer-warnings", not native_warnings, "All three native slicer runs returned no object warnings", {"warnings": native_warnings}),
            check("physical-gate-deferred", True, "Media fit, snagging, visibility, closure and cycle checks remain outside this digital candidate"),
            check("watermark-gate-deferred", True, "Final watermark and commercial release remain blocked"),
        ]
    )
    output = {
        "schema_version": "1.0",
        "tool": "MM-ORG-013-finalize-digital-candidate",
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [input_record(path) for path in REPORTS],
        "checks": checks,
        "metrics": {
            "build_sets": len(plate_metrics),
            "layers_by_build_set": [item.get("layers_from_comments") for item in plate_metrics],
            "slicer_estimate_seconds_total": sum(item.get("slicer_metadata_time_s", 0) for item in plate_metrics),
            "extruded_volume_mm3_total": sum(item.get("extruded_volume_mm3", 0) for item in plate_metrics),
            "positive_extrusion_mm_total": sum(item.get("positive_extrusion_total_mm", 0) for item in plate_metrics),
            "peak_flow_mm3_s_max": max((item.get("peak_flow_mm3_s", 0) for item in plate_metrics), default=0),
            "tools_seen": sorted({tool for item in plate_metrics for tool in item.get("tools_seen", [])}),
            "physical_validation": "DEFERRED",
            "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE",
        },
        "limitations": [
            "Default drawer and sleeved-media dimensions are assumptions until measured on the target collection.",
            "Headless slicing does not replace layer-preview inspection or a physical print.",
            "Printed polymer is not claimed as a photo-safe primary archival enclosure.",
            "No printer upload or print-start action was performed.",
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
