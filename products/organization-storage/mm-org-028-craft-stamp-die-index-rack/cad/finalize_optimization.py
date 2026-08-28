#!/usr/bin/env python3
"""Bind the MM-ORG-028 system optimization decision to exact two-plate slices."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[2]
COMPARE = REPOSITORY / ".agents/skills/optimize-fdm-design/scripts/compare_variants.py"
REVISION = "0.1.0-draft.1"
REPORTS = {
    "rack-020": ROOT / "validation/slicer-rack-020.json",
    "dividers-020": ROOT / "validation/slicer-dividers-020.json",
    "rack-028": ROOT / "validation/slicer-rack-028.json",
    "dividers-028": ROOT / "validation/slicer-dividers-028.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    try:
        display = str(path.relative_to(ROOT))
    except ValueError:
        display = str(path)
    return {"path": display, "sha256": sha256(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def slicer_metrics(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    gcode_reports = list(report.get("gcode_reports", {}).values())
    if len(gcode_reports) != 1:
        raise ValueError(f"expected one G-code report in {path}")
    metrics = gcode_reports[0].get("metrics", {})
    native_warnings = [item.get("warning_message", "") for item in report.get("native_result", {}).get("sliced_plates", []) if item.get("warning_message", "").strip()]
    return {
        "report_status": 1 if report.get("status") == "PASS" and gcode_reports[0].get("status") == "PASS" else 0,
        "layer_count": metrics.get("layers_from_comments"),
        "print_time_s": metrics.get("slicer_metadata_time_s"),
        "extruded_volume_mm3": metrics.get("extruded_volume_mm3"),
        "tool_changes": metrics.get("tool_changes"),
        "warning_count": len(metrics.get("warnings", [])) + len(native_warnings),
        "tools_seen": metrics.get("tools_seen", []),
    }


def main() -> None:
    parameters_path = ROOT / "config/model-parameters.json"
    interface_path = ROOT / "validation/interface-report.json"
    geometric_path = ROOT / "reports/optimization-geometric.json"
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))
    interface = json.loads(interface_path.read_text(encoding="utf-8"))
    geometric = json.loads(geometric_path.read_text(encoding="utf-8"))
    extracted = {name: slicer_metrics(path) for name, path in REPORTS.items()}
    engraving_depth = parameters["divider"]["engraving_depth_mm"]
    systems = []
    for process, layer_height in (("020", 0.20), ("028", 0.28)):
        rack = extracted[f"rack-{process}"]
        dividers = extracted[f"dividers-{process}"]
        systems.append({
            "name": f"system-{process}",
            "metrics": {
                "report_status": min(rack["report_status"], dividers["report_status"]),
                "print_time_s": rack["print_time_s"] + dividers["print_time_s"],
                "extruded_volume_mm3": rack["extruded_volume_mm3"] + dividers["extruded_volume_mm3"],
                "warning_count": rack["warning_count"] + dividers["warning_count"],
                "tool_changes": rack["tool_changes"] + dividers["tool_changes"],
                "protected_frame": 1,
                "nominal_engraving_layers": engraving_depth / layer_height,
            },
            "notes": ["Exact rack-kit and divider-set Anycubic PLA slices; no G-code retained."],
        })
    payload = {
        "baseline": "system-020",
        "objectives": [{"metric": "print_time_s", "goal": "min"}, {"metric": "extruded_volume_mm3", "goal": "min"}],
        "constraints": [
            {"metric": "report_status", "op": "==", "value": 1},
            {"metric": "warning_count", "op": "==", "value": 0},
            {"metric": "tool_changes", "op": "==", "value": 0},
            {"metric": "protected_frame", "op": "==", "value": 1},
            {"metric": "nominal_engraving_layers", "op": ">=", "value": 3.0, "tolerance": 1e-9},
        ],
        "variants": systems,
    }
    payload_path = ROOT / "reports/optimization-variants.json"
    comparison_path = ROOT / "reports/optimization-pareto.json"
    markdown_path = ROOT / "reports/optimization-pareto.md"
    payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(COMPARE), str(payload_path), "--output", str(comparison_path)], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, str(COMPARE), str(payload_path), "--markdown", "--output", str(markdown_path)], check=True, stdout=subprocess.DEVNULL)
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    selected = systems[0]["metrics"]
    candidate = systems[1]["metrics"]
    interfaces = interface["metrics"]["interfaces"]
    selected_dividers = [value for name, value in interfaces.items() if name.startswith("index-divider-")]
    light = interfaces["light-index-divider-variant"]
    checks = [
        *[check(f"slicer:{name}", values["report_status"] == 1, f"Exact slicer report {name} reports PASS") for name, values in extracted.items()],
        check("all-slices-warning-free", all(item["warning_count"] == 0 for item in extracted.values()), "All four exact slices contain no parser or native object warnings"),
        check("all-slices-single-tool", all(item["tools_seen"] == [0] and item["tool_changes"] == 0 for item in extracted.values()), "All four exact slices use one tool with no tool changes"),
        check("protected-selected-frame", all(item["frame_width_mm"] >= 8 and item["center_rib_width_mm"] >= 12 for item in selected_dividers), "Selected dividers retain protected 8 mm frames and 12 mm center ribs"),
        check("light-variant-rejected", light["frame_width_mm"] == 6 and light["center_rib_width_mm"] == 8 and geometric["light_variant"]["constraint"].startswith("REJECTED"), "Light frame remains rejected without loaded racking and snag evidence"),
        check("minimum-engraving-layers", selected["nominal_engraving_layers"] >= 3.0 - 1e-9 and candidate["nominal_engraving_layers"] < 3.0, "0.20 mm retains three nominal engraving layers; 0.28 mm does not"),
        check("pareto-selection", comparison.get("pareto_variants") == ["system-020"] and comparison.get("feasible_count") == 1, "Two-plate 0.20 mm system is the sole feasible Pareto variant"),
        check("exact-profile-tradeoff", candidate["print_time_s"] < selected["print_time_s"] and candidate["extruded_volume_mm3"] > selected["extruded_volume_mm3"], "0.28 mm is faster but uses more estimated extrusion and fails the engraving-layer gate", {"time_delta_percent": 100 * (candidate["print_time_s"] - selected["print_time_s"]) / selected["print_time_s"], "volume_delta_percent": 100 * (candidate["extruded_volume_mm3"] - selected["extruded_volume_mm3"]) / selected["extruded_volume_mm3"]}),
        check("geometric-proxy", geometric.get("status") == "PASS" and geometric["selected"]["reduction_percent"] >= 50, "Selected system reduces geometric volume by at least 50% versus full tray/full dividers proxy"),
    ]
    source_inputs = [parameters_path, interface_path, geometric_path, COMPARE, *REPORTS.values(), payload_path, comparison_path, markdown_path]
    report = {
        "schema_version": "1.0", "tool": "MM-ORG-028-finalize-optimization", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": [record(path) for path in source_inputs], "checks": checks,
        "metrics": {"selected_variant": "system-020", "feasible_variants": comparison.get("feasible_count"), "pareto_variants": comparison.get("pareto_variants", []), "selected_print_time_s": selected["print_time_s"], "selected_extruded_volume_mm3": selected["extruded_volume_mm3"], "selected_plate_layers": {"rack-kit": extracted["rack-020"]["layer_count"], "divider-set": extracted["dividers-020"]["layer_count"]}, "geometric_reduction_vs_proxy_percent": geometric["selected"]["reduction_percent"], "light_variant_reduction_vs_selected_divider_percent": geometric["light_variant"]["reduction_percent_vs_mean_selected_divider"], "system_metrics": {item["name"]: item["metrics"] for item in systems}, "plate_metrics": extracted},
        "limitations": ["Slicer time and extrusion are estimates, not measured outcomes.", "The light divider remains a digital non-manufacturing variant.", "Racking, snagging, loaded tip and real envelope fit remain physical gates.", "No G-code was retained and no printer action was performed."],
        "required_capabilities": [],
    }
    output = ROOT / "validation/optimization-report.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output), "metrics": report["metrics"]}, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
