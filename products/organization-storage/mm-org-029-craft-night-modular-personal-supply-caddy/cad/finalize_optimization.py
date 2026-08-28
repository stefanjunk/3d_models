#!/usr/bin/env python3
"""Bind the MM-ORG-029 optimization decision to exact whole-system slices."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[2]
COMPARE = REPOSITORY / ".agents/skills/optimize-fdm-design/scripts/compare_variants.py"
REVISION = "0.1.0-draft.1"
REPORTS = {"system-020": ROOT / "validation/slicer-system-020.json", "system-028": ROOT / "validation/slicer-system-028.json"}


def sha256(target: Path) -> str:
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(target: Path) -> dict:
    try:
        display = str(target.relative_to(ROOT))
    except ValueError:
        display = str(target)
    return {"path": display, "sha256": sha256(target), "size_bytes": target.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def slicer_metrics(target: Path) -> dict:
    report = json.loads(target.read_text(encoding="utf-8"))
    gcode_reports = list(report.get("gcode_reports", {}).values())
    if len(gcode_reports) != 1:
        raise ValueError(f"expected one G-code report in {target}")
    metrics = gcode_reports[0].get("metrics", {})
    native_warnings = [item.get("warning_message", "") for item in report.get("native_result", {}).get("sliced_plates", []) if item.get("warning_message", "").strip()]
    return {
        "report_status": 1 if report.get("status") == "PASS" and gcode_reports[0].get("status") == "PASS" else 0,
        "layer_count": metrics.get("layers_from_comments"),
        "print_time_s": metrics.get("slicer_metadata_time_s"),
        "extruded_volume_mm3": metrics.get("extruded_volume_mm3"),
        "warning_count": len(metrics.get("warnings", [])) + len(native_warnings),
        "tool_changes": metrics.get("tool_changes"),
        "tools_seen": metrics.get("tools_seen", []),
        "peak_flow_mm3_s": metrics.get("peak_flow_mm3_s"),
    }


def main() -> None:
    parameters_path = ROOT / "config/model-parameters.json"
    interface_path = ROOT / "validation/interface-report.json"
    geometric_path = ROOT / "reports/optimization-geometric.json"
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))
    interface = json.loads(interface_path.read_text(encoding="utf-8"))
    geometric = json.loads(geometric_path.read_text(encoding="utf-8"))
    extracted = {name: slicer_metrics(target) for name, target in REPORTS.items()}
    engraving = parameters["nameplate"]["engraving_depth_mm"]
    variants = []
    for name, layer_height in (("system-020", 0.20), ("system-028", 0.28)):
        metrics = extracted[name]
        variants.append({"name": name, "metrics": {**metrics, "protected_shell": 1, "nominal_engraving_layers": engraving / layer_height}, "notes": ["Exact one-plate Kobra 3 Max PLA slice; no G-code retained."]})
    payload = {
        "baseline": "system-020",
        "objectives": [{"metric": "print_time_s", "goal": "min"}, {"metric": "extruded_volume_mm3", "goal": "min"}],
        "constraints": [
            {"metric": "report_status", "op": "==", "value": 1},
            {"metric": "warning_count", "op": "==", "value": 0},
            {"metric": "tool_changes", "op": "==", "value": 0},
            {"metric": "protected_shell", "op": "==", "value": 1},
            {"metric": "nominal_engraving_layers", "op": ">=", "value": 3.0, "tolerance": 1e-9}
        ],
        "variants": variants
    }
    payload_path = ROOT / "reports/optimization-variants.json"
    comparison_path = ROOT / "reports/optimization-pareto.json"
    markdown_path = ROOT / "reports/optimization-pareto.md"
    payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(COMPARE), str(payload_path), "--output", str(comparison_path)], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, str(COMPARE), str(payload_path), "--markdown", "--output", str(markdown_path)], check=True, stdout=subprocess.DEVNULL)
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    selected = variants[0]["metrics"]
    candidate = variants[1]["metrics"]
    interfaces = interface["metrics"]["interfaces"]
    checks = [
        *[check(f"slicer:{name}", values["report_status"] == 1, f"Exact slicer report {name} reports PASS") for name, values in extracted.items()],
        check("all-slices-warning-free", all(item["warning_count"] == 0 for item in extracted.values()), "Both exact slices contain no parser or native warnings"),
        check("all-slices-single-tool", all(item["tools_seen"] == [0] and item["tool_changes"] == 0 for item in extracted.values()), "Both exact slices use one tool with no tool changes"),
        check("protected-selected-shell", interfaces["personal-caddy"]["wall_mm"] >= 3 and interfaces["personal-caddy"]["base_mm"] >= 3, "Selected caddy retains protected 3 mm shell/base"),
        check("bed-built-keys", parameters["dock"]["key_origin_z_mm"] == 0, "Hub keys build from the print bed after the slicer-warning iteration"),
        check("light-variant-rejected", interfaces["light-personal-caddy-variant"]["wall_mm"] == 2.4 and geometric["light_variant"]["constraint"].startswith("REJECTED"), "Light caddy remains rejected without physical flex/drop/docking evidence"),
        check("minimum-engraving-layers", selected["nominal_engraving_layers"] >= 3.0 - 1e-9 and candidate["nominal_engraving_layers"] < 3.0, "0.20 mm retains three nominal engraving layers; 0.28 mm does not"),
        check("pareto-selection", comparison.get("pareto_variants") == ["system-020"] and comparison.get("feasible_count") == 1, "0.20 mm system is the sole feasible Pareto variant"),
        check("exact-profile-tradeoff", candidate["print_time_s"] < selected["print_time_s"] and candidate["extruded_volume_mm3"] > selected["extruded_volume_mm3"], "0.28 mm is faster but uses more estimated extrusion and fails the engraving gate", {"time_delta_percent": 100 * (candidate["print_time_s"] - selected["print_time_s"]) / selected["print_time_s"], "volume_delta_percent": 100 * (candidate["extruded_volume_mm3"] - selected["extruded_volume_mm3"]) / selected["extruded_volume_mm3"]}),
        check("geometric-proxy", geometric["selected"]["reduction_percent"] >= 70, "Selected system reduces geometric volume by at least 70% versus the solid-envelope proxy")
    ]
    source_inputs = [parameters_path, interface_path, geometric_path, COMPARE, *REPORTS.values(), payload_path, comparison_path, markdown_path]
    report = {"schema_version": "1.0", "tool": "MM-ORG-029-finalize-optimization", "tool_version": REVISION, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [record(target) for target in source_inputs], "checks": checks, "metrics": {"selected_variant": "system-020", "feasible_variants": comparison.get("feasible_count"), "pareto_variants": comparison.get("pareto_variants", []), "selected_print_time_s": selected["print_time_s"], "selected_extruded_volume_mm3": selected["extruded_volume_mm3"], "selected_layers": selected["layer_count"], "geometric_reduction_vs_proxy_percent": geometric["selected"]["reduction_percent"], "light_variant_reduction_vs_selected_caddy_percent": geometric["light_variant"]["reduction_percent_vs_selected_caddy"], "variant_metrics": {item["name"]: item["metrics"] for item in variants}}, "limitations": ["Slicer time and extrusion are estimates, not measured outcomes.", "The light caddy remains a non-manufacturing digital variant.", "Loaded stability, docking effort, flex, drop and wear remain physical gates.", "No G-code was retained and no printer action was performed."], "required_capabilities": []}
    target = ROOT / "validation/optimization-report.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "metrics": report["metrics"]}, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
