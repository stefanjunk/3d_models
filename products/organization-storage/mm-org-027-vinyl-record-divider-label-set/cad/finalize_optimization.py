#!/usr/bin/env python3
"""Bind the MM-ORG-027 optimization decision to exact slicer evidence."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[2]
COMPARE = REPOSITORY / ".agents/skills/optimize-fdm-design/scripts/compare_variants.py"
REVISION = "0.1.0-draft.1"
REPORTS = {
    "smooth-020": ROOT / "validation/slicer-selected-020.json",
    "smooth-028": ROOT / "validation/slicer-selected-028.json",
    "windowed-020": ROOT / "validation/slicer-windowed-020.json",
    "windowed-028": ROOT / "validation/slicer-windowed-028.json",
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
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def slicer_metrics(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    gcode_reports = list(report.get("gcode_reports", {}).values())
    if len(gcode_reports) != 1:
        raise ValueError(f"expected one G-code report in {path}")
    metrics = gcode_reports[0].get("metrics", {})
    native_warnings = [
        item.get("warning_message", "")
        for item in report.get("native_result", {}).get("sliced_plates", [])
        if item.get("warning_message", "").strip()
    ]
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
    engraving_depth = float(parameters["label_cap"]["engraving_depth_mm"])
    layer_heights = {"020": 0.20, "028": 0.28}
    continuous = {"smooth": 1, "windowed": 0}
    variants = []
    extracted = {}
    for name, report_path in REPORTS.items():
        geometry, process = name.split("-")
        current = slicer_metrics(report_path)
        current.update({
            "continuous_contact": continuous[geometry],
            "nominal_engraving_layers": engraving_depth / layer_heights[process],
        })
        extracted[name] = current
        variants.append({
            "name": name,
            "metrics": current,
            "notes": [
                "Exact Anycubic Kobra 3 Max PETG slice; no G-code retained.",
                "The continuous-contact constraint protects sleeve-facing geometry."
                if geometry == "smooth"
                else "Window edges remain rejected until snag, racking and flatness tests pass.",
            ],
        })

    payload = {
        "baseline": "smooth-020",
        "objectives": [
            {"metric": "print_time_s", "goal": "min"},
            {"metric": "extruded_volume_mm3", "goal": "min"},
        ],
        "constraints": [
            {"metric": "report_status", "op": "==", "value": 1},
            {"metric": "warning_count", "op": "==", "value": 0},
            {"metric": "tool_changes", "op": "==", "value": 0},
            {"metric": "continuous_contact", "op": "==", "value": 1},
            {"metric": "nominal_engraving_layers", "op": ">=", "value": 3.0, "tolerance": 1e-9},
        ],
        "variants": variants,
    }
    payload_path = ROOT / "reports/optimization-variants.json"
    comparison_path = ROOT / "reports/optimization-pareto.json"
    markdown_path = ROOT / "reports/optimization-pareto.md"
    payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(COMPARE), str(payload_path), "--output", str(comparison_path)], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, str(COMPARE), str(payload_path), "--markdown", "--output", str(markdown_path)], check=True, stdout=subprocess.DEVNULL)
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))

    baseline = extracted["smooth-020"]
    faster_layer = extracted["smooth-028"]
    checks = [
        *[
            check(f"slicer:{name}", values["report_status"] == 1, f"Exact slicer report {name} reports PASS")
            for name, values in extracted.items()
        ],
        check("all-slices-warning-free", all(item["warning_count"] == 0 for item in extracted.values()), "All four exact slices contain no parser or native object warnings"),
        check("all-slices-single-tool", all(item["tools_seen"] == [0] and item["tool_changes"] == 0 for item in extracted.values()), "All four exact slices use one tool with no tool changes"),
        check("baseline-protected-geometry", interface["metrics"]["interfaces"]["smooth-carrier"]["record_contact_surface"] == "continuous", "Selected carrier retains a continuous sleeve-facing surface"),
        check("windowed-rejected", interface["metrics"]["interfaces"]["windowed-carrier"]["record_contact_surface"] == "interrupted", "Windowed carrier is rejected without physical edge, racking and flatness evidence"),
        check("minimum-engraving-layers", (baseline["nominal_engraving_layers"] >= 3.0 or math.isclose(baseline["nominal_engraving_layers"], 3.0, abs_tol=1e-9)) and faster_layer["nominal_engraving_layers"] < 3.0, "0.20 mm retains three nominal engraving layers; 0.28 mm does not", {"smooth-020": baseline["nominal_engraving_layers"], "smooth-028": faster_layer["nominal_engraving_layers"]}),
        check("pareto-selection", comparison.get("pareto_variants") == ["smooth-020"] and comparison.get("feasible_count") == 1, "Smooth 0.20 mm is the only feasible Pareto variant"),
        check("exact-profile-counterfactual", faster_layer["print_time_s"] > baseline["print_time_s"] and faster_layer["extruded_volume_mm3"] > baseline["extruded_volume_mm3"], "The exact 0.28 mm profile is slower and uses more extrusion than the protected 0.20 mm baseline", {"time_delta_percent": 100.0 * (faster_layer["print_time_s"] - baseline["print_time_s"]) / baseline["print_time_s"], "volume_delta_percent": 100.0 * (faster_layer["extruded_volume_mm3"] - baseline["extruded_volume_mm3"]) / baseline["extruded_volume_mm3"]}),
        check("geometric-proxy", geometric.get("status") == "PASS" and geometric.get("selected", {}).get("reduction_percent", 0) > 0, "Selected two-part system reduces geometric volume versus the legacy full-panel proxy"),
    ]
    source_inputs = [parameters_path, interface_path, geometric_path, COMPARE, *REPORTS.values(), payload_path, comparison_path, markdown_path]
    report = {
        "schema_version": "1.0",
        "tool": "MM-ORG-027-finalize-optimization",
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [record(path) for path in source_inputs],
        "checks": checks,
        "metrics": {
            "selected_variant": "smooth-020",
            "feasible_variants": comparison.get("feasible_count"),
            "pareto_variants": comparison.get("pareto_variants", []),
            "selected_print_time_s": baseline["print_time_s"],
            "selected_extruded_volume_mm3": baseline["extruded_volume_mm3"],
            "selected_layers": baseline["layer_count"],
            "geometric_reduction_vs_legacy_percent": geometric["selected"]["reduction_percent"],
            "windowed_reduction_vs_selected_percent": geometric["windowed"]["reduction_percent_vs_selected"],
            "variant_metrics": extracted,
        },
        "limitations": [
            "Slicer extrusion and time are estimates, not measured print outcomes.",
            "Windowed carriers remain digital optimization variants only and are not manufacturing outputs.",
            "Continuous contact is a geometry constraint; sleeve snagging, flatness and racking remain physical gates.",
            "No G-code was retained and no printer upload or print-start action was performed.",
        ],
        "required_capabilities": [],
    }
    output = ROOT / "validation/optimization-report.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output), "metrics": report["metrics"]}, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
