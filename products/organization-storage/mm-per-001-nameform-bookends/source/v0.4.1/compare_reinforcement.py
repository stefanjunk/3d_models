#!/usr/bin/env python3
"""Compare the reinforced MARITA draft with the printed v0.4.0 baseline."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


CONSTANTS = ("GLYPH_DEPTH", "CONNECTOR_T", "CONNECTOR_OVERLAP", "BRIDGE_WIDTH")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_record(path: Path) -> dict:
    return {"path": str(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def numeric_expression(node: ast.expr, values: dict[str, float]) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        left = numeric_expression(node.left, values)
        right = numeric_expression(node.right, values)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        return left / right
    raise ValueError(f"unsupported constant expression: {ast.dump(node)}")


def constants(path: Path) -> dict[str, float]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: dict[str, float] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name):
            try:
                values[target.id] = numeric_expression(node.value, values)
            except ValueError:
                continue
    missing = sorted(set(CONSTANTS) - values.keys())
    if missing:
        raise ValueError(f"missing literal constants in {path}: {', '.join(missing)}")
    return {name: values[name] for name in CONSTANTS}


def slice_metrics(report: dict) -> dict:
    metrics = report["gcode_reports"]["plate_1.gcode"]["metrics"]
    return {
        "time_s": metrics["slicer_metadata_time_s"],
        "filament_mm": metrics["positive_extrusion_total_mm"],
        "layers": metrics["layers_declared"],
    }


def percent_change(old: float, new: float) -> float:
    return 100.0 * (new - old) / old


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-source", type=Path, required=True)
    parser.add_argument("--candidate-source", type=Path, required=True)
    parser.add_argument("--baseline-generation", type=Path, required=True)
    parser.add_argument("--candidate-generation", type=Path, required=True)
    parser.add_argument("--baseline-left-slice", type=Path, required=True)
    parser.add_argument("--baseline-right-slice", type=Path, required=True)
    parser.add_argument("--candidate-left-slice", type=Path, required=True)
    parser.add_argument("--candidate-right-slice", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    if args.json_out.exists():
        raise FileExistsError(f"refusing to overwrite evidence: {args.json_out}")

    input_paths = [
        Path(__file__),
        args.baseline_source,
        args.candidate_source,
        args.baseline_generation,
        args.candidate_generation,
        args.baseline_left_slice,
        args.baseline_right_slice,
        args.candidate_left_slice,
        args.candidate_right_slice,
    ]
    old_constants = constants(args.baseline_source)
    new_constants = constants(args.candidate_source)
    old_generation = read_json(args.baseline_generation)
    new_generation = read_json(args.candidate_generation)
    old_slices = {
        "MA": slice_metrics(read_json(args.baseline_left_slice)),
        "RITA": slice_metrics(read_json(args.baseline_right_slice)),
    }
    new_slices = {
        "MA": slice_metrics(read_json(args.candidate_left_slice)),
        "RITA": slice_metrics(read_json(args.candidate_right_slice)),
    }

    checks = {
        "glyph_depth_exact_12_mm": new_constants["GLYPH_DEPTH"] == 12.0,
        "connector_thickness_exact_4_mm": new_constants["CONNECTOR_T"] == 4.0,
        "positive_overlap_exact_2_mm": new_constants["CONNECTOR_OVERLAP"] == 2.0,
        "bridge_width_minimum_12_mm": new_constants["BRIDGE_WIDTH"] >= 12.0,
        "candidate_generation_pass": new_generation["status"] == "PASS",
        "candidate_c_contract_preserved": new_generation["checks"]["candidate_c_exact_contract"],
        "layer_count_preserved": all(old_slices[p]["layers"] == new_slices[p]["layers"] == 1333 for p in old_slices),
    }
    parts = {}
    for part, side in (("MA", "left"), ("RITA", "right")):
        old_part = old_generation[side]
        new_part = new_generation[side]
        old_relief = old_part["candidate"]["texture"]["active_relief_robust_span_mm"]
        new_relief = new_part["candidate"]["texture"]["active_relief_robust_span_mm"]
        parts[part] = {
            "engineering_volume_mm3": {
                "baseline": old_part["engineering"]["volume_mm3"],
                "candidate": new_part["engineering"]["volume_mm3"],
                "change_percent": percent_change(old_part["engineering"]["volume_mm3"], new_part["engineering"]["volume_mm3"]),
            },
            "active_relief_robust_span_mm": {
                "baseline": old_relief,
                "candidate": new_relief,
                "absolute_change_mm": new_relief - old_relief,
            },
            "slice": {
                "baseline": old_slices[part],
                "candidate": new_slices[part],
                "time_change_percent": percent_change(old_slices[part]["time_s"], new_slices[part]["time_s"]),
                "filament_change_percent": percent_change(old_slices[part]["filament_mm"], new_slices[part]["filament_mm"]),
            },
        }

    payload = {
        "schema_version": "1.0",
        "tool": "NameForm reinforcement comparison",
        "tool_version": "0.4.1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": [input_record(path) for path in input_paths],
        "checks": checks,
        "structural_proxy": {
            "baseline": old_constants,
            "candidate": new_constants,
            "ratios": {
                "glyph_depth": new_constants["GLYPH_DEPTH"] / old_constants["GLYPH_DEPTH"],
                "connector_thickness": new_constants["CONNECTOR_T"] / old_constants["CONNECTOR_T"],
                "positive_overlap": new_constants["CONNECTOR_OVERLAP"] / old_constants["CONNECTOR_OVERLAP"],
                "bridge_width": new_constants["BRIDGE_WIDTH"] / old_constants["BRIDGE_WIDTH"],
                "gross_bridge_section": (new_constants["CONNECTOR_T"] * new_constants["BRIDGE_WIDTH"]) / (old_constants["CONNECTOR_T"] * old_constants["BRIDGE_WIDTH"]),
            },
            "limitation": "Nominal section ratios are deterministic geometry proxies, not measured stiffness or strength.",
        },
        "parts": parts,
        "decision": "RETAIN_REINFORCED_BASELINE_PENDING_PHYSICAL_TEST",
        "limitations": [
            "The comparison does not prove connector strength or fatigue resistance.",
            "The exact slicer reports still require human layer and seam review.",
            "No printer upload or print start was performed.",
        ],
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
