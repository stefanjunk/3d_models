#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
COMPARE = REPO / ".agents/skills/optimize-fdm-design/scripts/compare_variants.py"
REV = "0.1.0-draft.1"
REPORTS = {"system-020": ROOT / "validation/slicer-system-020.json", "system-028": ROOT / "validation/slicer-system-028.json"}


def sha(target: Path) -> str:
    return hashlib.sha256(target.read_bytes()).hexdigest()


def record(target: Path) -> dict:
    try:
        display = str(target.relative_to(ROOT))
    except ValueError:
        display = str(target)
    return {"path": display, "sha256": sha(target), "size_bytes": target.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def slicer_metrics(target: Path) -> dict:
    report = json.loads(target.read_text())
    gcode = list(report["gcode_reports"].values())[0]
    metrics = gcode["metrics"]
    native = [item["warning_message"] for item in report["native_result"]["sliced_plates"] if item.get("warning_message", "").strip()]
    return {"report_status": 1 if report["status"] == gcode["status"] == "PASS" else 0, "layer_count": metrics["layers_from_comments"], "print_time_s": metrics["slicer_metadata_time_s"], "extruded_volume_mm3": metrics["extruded_volume_mm3"], "warning_count": len(metrics["warnings"]) + len(native), "tool_changes": metrics["tool_changes"], "tools_seen": metrics["tools_seen"]}


def main() -> None:
    extracted = {name: slicer_metrics(path) for name, path in REPORTS.items()}
    variants = [{"name": name, "metrics": {**metrics, "protected_interfaces": 1}, "notes": ["Exact whole-plate Kobra 3 Max PLA slice; no G-code retained."]} for name, metrics in extracted.items()]
    payload = {"baseline": "system-020", "objectives": [{"metric": "print_time_s", "goal": "min"}, {"metric": "extruded_volume_mm3", "goal": "min"}], "constraints": [{"metric": "report_status", "op": "==", "value": 1}, {"metric": "warning_count", "op": "==", "value": 0}, {"metric": "tool_changes", "op": "==", "value": 0}, {"metric": "protected_interfaces", "op": "==", "value": 1}], "variants": variants}
    variants_path = ROOT / "reports/optimization-variants.json"
    pareto_path = ROOT / "reports/optimization-pareto.json"
    markdown_path = ROOT / "reports/optimization-pareto.md"
    variants_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    subprocess.run([sys.executable, str(COMPARE), str(variants_path), "--output", str(pareto_path)], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, str(COMPARE), str(variants_path), "--markdown", "--output", str(markdown_path)], check=True, stdout=subprocess.DEVNULL)
    comparison = json.loads(pareto_path.read_text())
    selected, baseline = extracted["system-028"], extracted["system-020"]
    time_delta = 100 * (selected["print_time_s"] - baseline["print_time_s"]) / baseline["print_time_s"]
    volume_delta = 100 * (selected["extruded_volume_mm3"] - baseline["extruded_volume_mm3"]) / baseline["extruded_volume_mm3"]
    geometric = json.loads((ROOT / "reports/optimization-geometric.json").read_text())
    interface = json.loads((ROOT / "validation/interface-report.json").read_text())["metrics"]["interfaces"]["dock"]
    checks = [
        *[check(f"slicer:{name}", metrics["report_status"] == 1, f"{name} reports PASS") for name, metrics in extracted.items()],
        check("warning-free", all(metrics["warning_count"] == 0 for metrics in extracted.values()), "Both slices contain no native/parser warnings"),
        check("single-tool", all(metrics["tools_seen"] == [0] and metrics["tool_changes"] == 0 for metrics in extracted.values()), "Both use one tool"),
        check("pareto", set(comparison["pareto_variants"]) == {"system-020", "system-028"}, "Both time/material tradeoff variants are Pareto-efficient"),
        check("time-priority-selection", time_delta < 0 and volume_delta <= 12, "0.28 mm saves time while reported extrusion growth stays within 12%", {"time_delta_percent": time_delta, "volume_delta_percent": volume_delta}),
        check("protected-interfaces", interface["base_mm"] >= 3 and interface["wall_mm"] >= 3 and interface["device_slot_at_shoe_mm"] == 13 and interface["book_slot_mm"] == 31, "Selected structural and fit interfaces remain protected"),
        check("light-rejected", geometric["light_variant"]["constraint"].startswith("REJECTED"), "Light dock remains rejected"),
        check("geometric", geometric["selected"]["reduction_percent"] >= 90, "Sparse dock reduces solid-envelope proxy by at least 90%"),
    ]
    sources = [ROOT / "config/model-parameters.json", ROOT / "validation/interface-report.json", ROOT / "reports/optimization-geometric.json", COMPARE, *REPORTS.values(), variants_path, pareto_path, markdown_path]
    report = {"schema_version": "1.0", "tool": "MM-ORG-031-finalize-optimization", "tool_version": REV, "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [record(path) for path in sources], "checks": checks, "metrics": {"selected_variant": "system-028", "selection_policy": "time_priority_with_max_12_percent_reported_extrusion_growth", "feasible_variants": comparison["feasible_count"], "pareto_variants": comparison["pareto_variants"], "selected_print_time_s": selected["print_time_s"], "selected_extruded_volume_mm3": selected["extruded_volume_mm3"], "selected_layers": selected["layer_count"], "time_delta_percent_vs_020": time_delta, "volume_delta_percent_vs_020": volume_delta, "geometric_reduction_vs_proxy_percent": geometric["selected"]["reduction_percent"], "light_variant_reduction_percent": geometric["light_variant"]["reduction_percent_vs_selected_dock"], "variant_metrics": extracted}, "limitations": ["Slicer estimates are not measured outcomes.", "Physical case/book fit, connector access, tip, drop and cycles are deferred.", "No G-code was retained."], "required_capabilities": []}
    target = ROOT / "validation/optimization-report.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "metrics": report["metrics"]}, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
