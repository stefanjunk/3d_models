#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-024."""
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
    "validation/fdm-mesh-pull-label-face.json",
    "validation/fdm-mesh-clip-thin.json",
    "validation/fdm-mesh-clip-shelffit.json",
    "validation/fdm-mesh-clip-thick.json",
    "validation/fdm-mesh-gap-gauge.json",
    "validation/fdm-mesh-key-slot-coupon.json",
    "validation/fdm-3mf.json",
    "validation/slicer-anycubic-next.json",
    "validation/approvals-through-slicer.json",
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
    clip_gaps = [interfaces.get(f"clip-{name}", {}).get("gap_mm") for name in ("thin", "shelffit", "thick")]
    gauge_gaps = interfaces.get("gap-gauge", {}).get("gaps_mm")
    face = interfaces.get("pull-label-face", {})
    key_coupon = interfaces.get("key-slot-coupon", {})

    checks.extend(
        [
            check("gcode-report", len(gcode_reports) == 1 and gcode_reports[0].get("status") == "PASS", "Exactly one temporary G-code analysis reports PASS"),
            check("expected-height", metrics.get("layers_from_comments") == 75, "15 mm pull-face height slices as 75 layers at 0.20 mm"),
            check("native-slicer-warnings", not warnings, "Native slicer returned no object warnings", {"warnings": warnings}),
            check("one-tool", metrics.get("tools_seen") == [0] and metrics.get("tool_changes") == 0, "One tool and no tool changes"),
            check("clip-gap-series", clip_gaps == [2.2, 2.9, 3.6], "Protected clip gap series remains exact", {"gap_mm": clip_gaps}),
            check("gauge-series", gauge_gaps == clip_gaps, "Gap gauge reproduces all three clip gaps"),
            check("key-coupon", key_coupon.get("key_slot_mm") == face.get("key_slot_mm"), "Key-slot coupon reproduces the face slot"),
            check("label-interface", face.get("label_insert_mm") == [76.2, 20.0], "Nominal exposed paper-label interface remains 76.2 x 20 mm"),
            check("physical-gates-deferred", True, "Gap fit, key retention, creep, marking, label and 500-cycle slide tests remain user-owned"),
        ]
    )
    output = {
        "schema_version": "1.0",
        "tool": "MM-ORG-024-finalize-digital-candidate",
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [record(path) for path in reports],
        "checks": checks,
        "metrics": {
            "build_sets": 1,
            "unique_meshes": 6,
            "objects": 6,
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
            "The three gaps are measured candidates, not a universal-fit claim.",
            "The low-profile tab is only for light horizontal sliding; lifting, carrying and load-rating claims are prohibited.",
            "Headless slicing does not replace final layer preview or a physical print.",
            "PETG preload, key retention, clip fatigue, creep, host marking and label retention remain untested.",
            "The 0.75 kg contents mass and 500 pulls are test targets, not a qualified rating.",
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
