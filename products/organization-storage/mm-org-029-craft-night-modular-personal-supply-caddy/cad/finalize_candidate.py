#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-029."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
REPORT_PATHS = [
    "validation/parametric-source-report.json", "validation/mesh-generation-report.json", "validation/interface-report.json",
    "reports/csv-import.json", "reports/live-batch-preview.json", "reports/nesting-layout.json", "validation/optimization-report.json",
    "validation/fdm-mesh-personal-caddy.json", "validation/fdm-mesh-shared-center-hub.json",
    "validation/fdm-mesh-nameplate-01-alex.json", "validation/fdm-mesh-nameplate-02-blair.json",
    "validation/fdm-mesh-nameplate-03-casey.json", "validation/fdm-mesh-nameplate-04-devin.json",
    "validation/fdm-mesh-dock-clearance-gauge.json", "validation/fdm-mesh-dock-interface-key.json",
    "validation/fdm-3mf-four-caddy-system.json", "validation/slicer-system-020.json", "validation/approvals-through-slicer.json"
]


def sha256(target: Path) -> str:
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(target: Path) -> dict:
    return {"path": str(target.relative_to(ROOT)), "sha256": sha256(target), "size_bytes": target.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def main() -> None:
    paths = [ROOT / item for item in REPORT_PATHS]
    loaded = {item: json.loads((ROOT / item).read_text(encoding="utf-8")) for item in REPORT_PATHS}
    checks = [check(f"report:{item}", report.get("status") == "PASS", f"{item} reports PASS") for item, report in loaded.items()]
    slicer = loaded["validation/slicer-system-020.json"]
    gcode_reports = list(slicer.get("gcode_reports", {}).values())
    gcode = gcode_reports[0].get("metrics", {}) if len(gcode_reports) == 1 else {}
    native_warnings = [item.get("warning_message", "") for item in slicer.get("native_result", {}).get("sliced_plates", []) if item.get("warning_message", "").strip()]
    interface = loaded["validation/interface-report.json"]["metrics"]
    csv_metrics = loaded["reports/csv-import.json"]["metrics"]
    proof = loaded["reports/live-batch-preview.json"]["metrics"]
    nesting = loaded["reports/nesting-layout.json"]
    optimization = loaded["validation/optimization-report.json"]["metrics"]
    checks.extend([
        check("one-gcode-report", len(gcode_reports) == 1 and gcode_reports[0].get("status") == "PASS", "Exactly one temporary G-code analysis reports PASS"),
        check("expected-height", gcode.get("layers_from_comments") == 325, "65 mm caddies slice as 325 layers at 0.20 mm"),
        check("slicer-warnings", not gcode.get("warnings", []) and not native_warnings, "Selected exact slice has no parser or native warnings"),
        check("one-tool", gcode.get("tools_seen") == [0] and gcode.get("tool_changes") == 0, "Selected plate uses one tool and no tool changes"),
        check("four-docked-caddies", interface["interfaces"]["shared-center-hub"]["dock_count"] == 4, "Hub retains four identical dock keys"),
        check("nominal-fit", interface["nominal_total_clearance_mm"] == 0.4 and interface["interfaces"]["dock-clearance-gauge"]["candidate_total_clearances_mm"] == [0.2, 0.4, 0.6], "Production dock clearance is bracketed by its fail-first coupon"),
        check("bed-built-keys", interface["interfaces"]["shared-center-hub"]["key"]["height_mm"] == 25, "Revised 25 mm hub keys are retained in the warning-free candidate"),
        check("four-nameplates", len(interface["names"]) == 4 and proof["names"] == [item["normalized_name"] for item in csv_metrics["names"]], "CSV, exact proof and CAD retain the same four names"),
        check("font-identity", csv_metrics["font_id"] == proof["font_id"] == interface["font_record"]["font_id"] == "MM-GRID-5X7-v1", "CSV import, proof and CAD retain repository-owned glyph identity"),
        check("one-plate-nesting", nesting["metrics"]["plate_count"] == 1 and nesting["metrics"]["object_count"] == 11 and all(item["status"] == "PASS" for item in nesting["checks"]), "Eleven selected objects form one collision-free build plate"),
        check("optimization-selection", optimization["selected_variant"] == "system-020" and optimization["feasible_variants"] == 1 and optimization["pareto_variants"] == ["system-020"], "0.20 mm system is the sole feasible Pareto variant"),
        check("physical-gates-deferred", True, "Printed coupon, load, tip, drop, flex, plate fit and cycle tests remain user-owned")
    ])
    output = {"schema_version": "1.0", "tool": "MM-ORG-029-finalize-digital-candidate", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [record(target) for target in paths], "checks": checks, "metrics": {"names": 4, "unique_selected_meshes": 8, "selected_objects": 11, "build_plates": 1, "layers": gcode.get("layers_from_comments"), "slicer_estimate_seconds": gcode.get("slicer_metadata_time_s"), "extruded_volume_mm3": gcode.get("extruded_volume_mm3"), "positive_extrusion_mm": gcode.get("positive_extrusion_total_mm"), "peak_flow_mm3_s": gcode.get("peak_flow_mm3_s"), "tools_seen": [0], "font_id": proof["font_id"], "selected_variant": optimization["selected_variant"], "geometric_reduction_vs_proxy_percent": optimization["geometric_reduction_vs_proxy_percent"], "physical_validation": "DEFERRED", "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE"}, "limitations": ["Print the dock gauge/key and choose the working clearance before committing to the full system.", "Dry indoor adult craft supplies only; hot tools, solvents, liquids, food contact and unsupervised child use are excluded.", "The exact SVG proves CAD/source identity, not customer approval or printed contrast.", "Headless slicing does not replace final layer preview or a physical print.", "Docking effort, 250 cycles, 750 g load per caddy, loaded tip, corner lift, flex and drop remain untested.", "Commercial release remains a separate human gate. No G-code was retained and no printer action was performed."], "required_capabilities": []}
    target = ROOT / "validation/print-candidate-report.json"
    target.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "metrics": output["metrics"]}, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
