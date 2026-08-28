#!/usr/bin/env python3
"""Create the hash-bound digital print-candidate report for MM-ORG-028."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
REPORT_PATHS = [
    "validation/parametric-source-report.json", "validation/mesh-generation-report.json", "validation/interface-report.json",
    "reports/csv-import.json", "reports/live-batch-preview.json", "reports/nesting-layout.json", "validation/optimization-report.json",
    "validation/fdm-mesh-rack.json", "validation/fdm-mesh-index-divider-01-stamps.json", "validation/fdm-mesh-index-divider-02-dies.json",
    "validation/fdm-mesh-index-divider-03-alpha.json", "validation/fdm-mesh-index-divider-04-floral.json",
    "validation/fdm-mesh-lane-gap-gauge.json", "validation/fdm-mesh-divider-foot-key.json",
    "validation/fdm-3mf-rack-kit.json", "validation/fdm-3mf-divider-set.json",
    "validation/slicer-rack-020.json", "validation/slicer-dividers-020.json", "validation/approvals-through-slicer.json",
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


def gcode_metrics(report: dict) -> tuple[dict, list[str], bool]:
    gcode_reports = list(report.get("gcode_reports", {}).values())
    metrics = gcode_reports[0].get("metrics", {}) if len(gcode_reports) == 1 else {}
    warnings = list(metrics.get("warnings", [])) + [item.get("warning_message", "") for item in report.get("native_result", {}).get("sliced_plates", []) if item.get("warning_message", "").strip()]
    passed = len(gcode_reports) == 1 and gcode_reports[0].get("status") == "PASS"
    return metrics, warnings, passed


def main() -> None:
    paths = [ROOT / item for item in REPORT_PATHS]
    loaded = {item: json.loads((ROOT / item).read_text(encoding="utf-8")) for item in REPORT_PATHS}
    checks = [check(f"report:{item}", report.get("status") == "PASS", f"{item} reports PASS") for item, report in loaded.items()]
    rack_gcode, rack_warnings, rack_gcode_pass = gcode_metrics(loaded["validation/slicer-rack-020.json"])
    divider_gcode, divider_warnings, divider_gcode_pass = gcode_metrics(loaded["validation/slicer-dividers-020.json"])
    interface_metrics = loaded["validation/interface-report.json"]["metrics"]
    interfaces = interface_metrics["interfaces"]
    selected_dividers = [value for name, value in interfaces.items() if name.startswith("index-divider-")]
    csv_metrics = loaded["reports/csv-import.json"]["metrics"]
    proof_metrics = loaded["reports/live-batch-preview.json"]["metrics"]
    nesting = loaded["reports/nesting-layout.json"]
    optimization = loaded["validation/optimization-report.json"]["metrics"]
    checks.extend([
        check("two-gcode-reports", rack_gcode_pass and divider_gcode_pass, "Exactly one temporary G-code analysis per selected build plate reports PASS"),
        check("expected-heights", rack_gcode.get("layers_from_comments") == 225 and divider_gcode.get("layers_from_comments") == 54, "45.0 mm rack and 10.8 mm print-oriented dividers slice as 225 and 54 layers at 0.20 mm"),
        check("slicer-warnings", not rack_warnings and not divider_warnings, "Both selected exact slices contain no native or parser warnings", {"rack": rack_warnings, "dividers": divider_warnings}),
        check("one-tool", rack_gcode.get("tools_seen") == [0] and divider_gcode.get("tools_seen") == [0] and rack_gcode.get("tool_changes") == divider_gcode.get("tool_changes") == 0, "Both selected build plates use one tool and no tool changes"),
        check("filled-envelope-boundary", interfaces["rack"]["lane_count"] == 15 and interfaces["rack"]["lane_gap_mm"] == 11.2, "Rack retains fifteen nominal 11.2 mm lanes for the declared filled-envelope class"),
        check("nominal-fit", interface_metrics.get("nominal_total_clearance_mm") >= 0.4 - 1e-9 and interfaces["divider-foot-key"]["width_mm"] == 10.8, "Divider pads retain 0.40 mm total nominal lane clearance and the key reproduces pad width"),
        check("coupon-bracket", interfaces["lane-gap-gauge"]["candidate_slot_widths_mm"] == [10.9, 11.2, 11.5], "Coupon brackets and includes the production lane gap"),
        check("protected-frames", len(selected_dividers) == 4 and all(item["frame_width_mm"] >= 8 and item["center_rib_width_mm"] >= 12 and item["pad_count"] == 3 for item in selected_dividers), "Four selected dividers retain protected frames, center ribs and three aligned pads"),
        check("csv-batch", len(csv_metrics.get("labels", [])) == 4 and csv_metrics.get("labels") == interface_metrics.get("labels"), "CSV import and CAD retain the same four normalized labels and tab positions"),
        check("font-identity", csv_metrics.get("font_id") == proof_metrics.get("font_id") == interface_metrics.get("font_record", {}).get("font_id") == "MM-GRID-5X7-v1", "CSV import, exact proof and CAD retain repository-owned glyph identity"),
        check("exact-label-proof", proof_metrics.get("labels") == [item.get("normalized_label") for item in csv_metrics.get("labels", [])], "Exact SVG proof and imported batch retain identical normalized labels"),
        check("printable-pixels", proof_metrics.get("minimum_pixel_width_mm", 0) >= 0.8 and min(item.get("layout", {}).get("pixel_width_mm", 0) for item in selected_dividers) >= 0.8, "Exact proof and CAD exceed the 0.8 mm minimum glyph-pixel width"),
        check("two-plate-nesting", nesting["metrics"]["plate_count"] == 2 and nesting["metrics"]["object_count"] == 7 and all(item["status"] == "PASS" for item in nesting["checks"]), "Seven selected objects form two collision-free build plates"),
        check("optimization-selection", optimization.get("selected_variant") == "system-020" and optimization.get("feasible_variants") == 1 and optimization.get("pareto_variants") == ["system-020"], "Two-plate 0.20 mm system is the sole feasible Pareto variant"),
        check("physical-gates-deferred", True, "Real envelope fit, snagging, racking, loaded tip, corner lift and cycle tests remain user-owned"),
    ])
    output = {
        "schema_version": "1.0", "tool": "MM-ORG-028-finalize-digital-candidate", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": [record(path) for path in paths], "checks": checks,
        "metrics": {"labels": 4, "unique_selected_meshes": 7, "selected_objects": 7, "build_plates": 2, "plate_layers": {"rack-kit": rack_gcode.get("layers_from_comments"), "divider-set": divider_gcode.get("layers_from_comments")}, "slicer_estimate_seconds": rack_gcode.get("slicer_metadata_time_s", 0) + divider_gcode.get("slicer_metadata_time_s", 0), "extruded_volume_mm3": rack_gcode.get("extruded_volume_mm3", 0) + divider_gcode.get("extruded_volume_mm3", 0), "positive_extrusion_mm": rack_gcode.get("positive_extrusion_total_mm", 0) + divider_gcode.get("positive_extrusion_total_mm", 0), "peak_flow_mm3_s": max(rack_gcode.get("peak_flow_mm3_s", 0), divider_gcode.get("peak_flow_mm3_s", 0)), "tools_seen": [0], "font_id": proof_metrics.get("font_id"), "selected_variant": optimization.get("selected_variant"), "geometric_reduction_vs_proxy_percent": optimization.get("geometric_reduction_vs_proxy_percent"), "physical_validation": "DEFERRED", "release_state": "DRAFT_DIGITAL_PRINT_CANDIDATE"},
        "limitations": [
            "The nominal 11.2 mm lane is a digital candidate; print the gauge/key before the rack or divider set.",
            "Load filled protective envelopes/cases only; loose exposed dies, blades and unprotected stamps are excluded.",
            "The exact SVG proves CAD/source identity, not printed contrast, customer approval or content rights.",
            "Headless slicing does not replace final layer preview or a physical print.",
            "Envelope snagging/scuffing, loaded racking/tip, corner lift, 250 divider cycles and 500 retrieval cycles remain untested.",
            "Larger 6×7, 9.5×7 and 7×10 formats require a regenerated and revalidated parameter set.",
            "Commercial release remains a separate human gate. No G-code was retained and no printer action was performed.",
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
