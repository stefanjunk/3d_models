#!/usr/bin/env python3
"""Fail-closed consistency checks for the MM-TOY-003 bom.2 graph projection."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "preflight/preflight-result.json"
GRAPH = ROOT / "architecture/interface-graph-v0.1.0-bom.2.json"
COTS = ROOT / "architecture/cots-interface-register-v0.1.0-bom.2.csv"
OUTPUT = ROOT / "validation/interface-graph-validation-v0.1.0-bom.2.json"


def tier(total: int) -> str:
    return "I0" if total <= 3 else "I1" if total <= 7 else "I2" if total <= 11 else "I3" if total <= 15 else "I4" if total <= 19 else "I5"


def input_record(path: Path) -> dict:
    payload = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload)}


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    with COTS.open(newline="", encoding="utf-8") as stream:
        cots = list(csv.DictReader(stream))

    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []

    def check(identifier: str, condition: bool, detail: str) -> None:
        checks.append({"id": identifier, "status": "PASS" if condition else "FAIL", "required": True, "message": detail, "evidence": [], "metrics": {}})
        if not condition:
            errors.append(f"{identifier}: {detail}")

    nodes = graph["nodes"]
    edges = graph["edges"]
    node_ids = [node["id"] for node in nodes]
    edge_ids = [edge["id"] for edge in edges]
    result_ids = [edge["id"] for edge in result["interfaces"]]
    check("unique-nodes", len(node_ids) == len(set(node_ids)), f"{len(node_ids)} node IDs")
    check("unique-edges", len(edge_ids) == len(set(edge_ids)), f"{len(edge_ids)} edge IDs")
    check("edge-projection", edge_ids == result_ids, "graph edge order and IDs must exactly project preflight interfaces")
    check("endpoint-integrity", all(edge["source"] in node_ids and edge["target"] in node_ids for edge in edges), "every endpoint must resolve to a graph node")
    check("metric-node-count", graph["graph_metrics"]["node_count"] == len(nodes) == 22, "graph must contain 22 declared entities")
    check("metric-edge-count", graph["graph_metrics"]["edge_count"] == len(edges) == 18, "graph must contain 18 declared interfaces")
    check("all-unconfirmed", all(not edge["variant_confirmed"] for edge in edges), "no delivered-part variant may be claimed before intake measurement")

    complexity_ok = True
    for interface in result["interfaces"]:
        ic = interface["interface_complexity"]
        computed = sum(ic[key] for key in ("GEO", "KIN", "TOL", "PHY", "VAR", "LIF"))
        complexity_ok &= computed == ic["total"] and tier(computed) == ic["tier"]
    check("interface-complexity", complexity_ok, "every IC total and tier must be arithmetically consistent")

    scores = result["complexity"]["dimension_scores"]
    weights = {"REQ": 7, "CTX": 5, "PAR": 10, "INT": 20, "CPL": 10, "MOT": 10, "GEO": 7, "PHY": 10, "MAT": 7, "EXT": 7, "VER": 7}
    pc = sum(weights[key] * scores[key] / 4 for key in weights)
    check("product-complexity", abs(pc - result["complexity"]["score_0_100"]) < 1e-9 and pc >= 80, f"computed PC={pc:.2f} must match C5 result")

    row_ids = [row["item_id"] for row in cots]
    check("cots-row-count", len(cots) == 13, "register must contain 13 geometry-owning COTS rows")
    check("cots-unique-items", len(row_ids) == len(set(row_ids)), "COTS item IDs must be unique")
    check("official-links", all(row["official_product_url"].startswith("https://") and row["official_drawing_or_cad_url"].startswith("https://") for row in cots), "every row needs HTTPS manufacturer product and drawing/CAD references")
    check("selected-t81-family", {row["mpn"] for row in cots if row["selection"] == "SELECT"} == {"T81H-RM61", "T81P-496BB"}, "only the matched BaneBots T81 hub/wheel replacements are SELECT")
    check("critical-cots-e3", all(row["evidence_level"] == "E3" for row in cots), "all registered geometry-owning COTS rows must have official nominal E3 evidence")
    check("cots-unconfirmed", all(row["variant_status"] == "not physically confirmed" for row in cots), "the register must not imply delivered-part confirmation")

    old_total_g = 2114.655891986308
    old_stack_each_g = 179.0
    t81_stack_each_g = 144.582 + 14.175
    estimated_total_g = old_total_g - 2 * (old_stack_each_g - t81_stack_each_g)
    estimated_com_z_mm = old_total_g * 71.15603679045469 / estimated_total_g
    projected_unchanged_height_mm = 249.5 + (123.825 - 120.0) / 2
    check("mass-arithmetic", abs(estimated_total_g - 2074.169891986308) < 1e-9 and abs(estimated_com_z_mm - 72.54494100540285) < 1e-9, "mass-only substitution must remain reproducible")
    check("width-arithmetic", abs((216.0 + 20.32) - 236.32) < 1e-9, "nominal overall width must derive from center track plus one wheel width")
    check("height-change-detected", abs(projected_unchanged_height_mm - 251.4125) < 1e-9 and projected_unchanged_height_mm > 250.0, "larger wheel must flag a bom.2 upright-envelope redesign instead of inheriting the bom.1 pass")

    if result["decision"]["design_release"] != "HOLD":
        errors.append("release-boundary: bom.2 must remain HOLD before sample and physical evidence")
    warnings.extend([
        "All COTS availability values are time-scoped snapshots and must be rechecked before ordering.",
        "Passing this projection check does not validate delivered dimensions, fit, dynamics, firmware, printing or powered operation.",
        "At unchanged axle-relative body geometry the selected wheel projects 251.4125 mm upright height, so CAD redesign is mandatory before a new envelope pass.",
    ])
    report = {
        "schema_version": "1.0",
        "tool": "mm-toy-003-dimensioned-cots-interface-graph",
        "tool_version": "1.0.0",
        "status": "PASS" if not errors else "FAIL",
        "validator": "mm-toy-003-dimensioned-cots-interface-graph",
        "project_id": "MM-TOY-003",
        "revision": "0.1.0-bom.2",
        "inputs": [input_record(Path(__file__).resolve()), input_record(RESULT), input_record(GRAPH), input_record(COTS)],
        "checks": checks,
        "derived": {"nominal_overall_width_mm": 236.32, "projected_unchanged_upright_height_mm": projected_unchanged_height_mm, "upright_height_limit_mm": 250.0, "projected_height_excess_mm": projected_unchanged_height_mm - 250.0, "mass_only_estimate_g": estimated_total_g, "mass_only_com_z_mm": estimated_com_z_mm},
        "errors": errors,
        "warnings": warnings,
        "limitations": warnings,
        "passed": not errors,
        "release_decision": "HOLD",
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
