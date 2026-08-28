#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = "0.1.0-draft.1"
PATHS = [
    "validation/parametric-source-report.json",
    "validation/mesh-generation-report.json",
    "validation/interface-report.json",
    "reports/nesting-layout.json",
    "validation/optimization-report.json",
    "validation/fdm-mesh-dock.json",
    "validation/fdm-mesh-device-fit-gauge.json",
    "validation/fdm-mesh-device-key-comb.json",
    "validation/fdm-mesh-book-fit-gauge.json",
    "validation/fdm-mesh-book-key-comb.json",
    "validation/fdm-3mf-pageharbor-duo-five.json",
    "validation/slicer-system-028.json",
    "validation/approvals-through-slicer.json",
]


def sha(target: Path) -> str:
    return hashlib.sha256(target.read_bytes()).hexdigest()


def record(target: Path) -> dict:
    return {"path": str(target.relative_to(ROOT)), "sha256": sha(target), "size_bytes": target.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def main() -> None:
    loaded = {path: json.loads((ROOT / path).read_text()) for path in PATHS}
    checks = [check(f"report:{path}", report["status"] == "PASS", f"{path} reports PASS") for path, report in loaded.items()]
    slicer = loaded["validation/slicer-system-028.json"]
    gcode = list(slicer["gcode_reports"].values())[0]["metrics"]
    native = [item["warning_message"] for item in slicer["native_result"]["sliced_plates"] if item.get("warning_message", "").strip()]
    interface = loaded["validation/interface-report.json"]["metrics"]["interfaces"]
    nesting = loaded["reports/nesting-layout.json"]["metrics"]
    optimization = loaded["validation/optimization-report.json"]["metrics"]
    checks += [
        check("one-gcode", len(slicer["gcode_reports"]) == 1, "One temporary G-code analysis reports PASS"),
        check("height", gcode["layers_from_comments"] == 357, "100 mm dock slices as 357 layers at 0.28 mm"),
        check("warnings", not gcode["warnings"] and not native, "Selected slice is warning-free"),
        check("one-tool", gcode["tools_seen"] == [0] and gcode["tool_changes"] == 0, "Selected plate uses one tool"),
        check("device-gauge", interface["device-fit-gauge"]["slot_widths_mm"] == [9, 11, 13, 15, 17], "Five device fit stations are retained"),
        check("book-gauge", interface["book-fit-gauge"]["slot_widths_mm"] == [19, 31, 43], "Three book fit stations are retained"),
        check("connector", interface["dock"]["connector_keepout_width_mm"] == 40 and interface["dock"]["connector_vertical_clearance_mm"] == 11, "Connector access keepout is retained"),
        check("nesting", nesting["plate_count"] == 1 and nesting["object_count"] == 5, "Five objects form one plate"),
        check("optimization", optimization["selected_variant"] == "system-028" and set(optimization["pareto_variants"]) == {"system-020", "system-028"}, "Selected 0.28 mm is an explicit Pareto time-priority choice"),
        check("physical-deferred", True, "Case/book fit, connector access, tip, drop and cycles remain user-owned"),
    ]
    report = {"schema_version": "1.0", "tool": "MM-ORG-031-finalize-digital-candidate", "tool_version": REV, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [record(ROOT / path) for path in PATHS], "checks": checks, "metrics": {"device_fit_stations": 5, "book_fit_stations": 3, "unique_selected_meshes": 5, "selected_objects": 5, "build_plates": 1, "layers": gcode["layers_from_comments"], "slicer_estimate_seconds": gcode["slicer_metadata_time_s"], "extruded_volume_mm3": gcode["extruded_volume_mm3"], "selected_variant": optimization["selected_variant"], "geometric_reduction_vs_proxy_percent": optimization["geometric_reduction_vs_proxy_percent"], "physical_validation": "DEFERRED", "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE"}, "limitations": ["Print both fit-gauge/key-comb pairs before the full dock.", "Measure the cased device, closed book and connector access; rebuild if needed.", "Passive dry indoor storage only; no charging, thermal, universal-fit, load, impact, cycle or child-safety claim.", "No G-code was retained and no printer action occurred."], "required_capabilities": []}
    target = ROOT / "validation/print-candidate-report.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "metrics": report["metrics"]}, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
