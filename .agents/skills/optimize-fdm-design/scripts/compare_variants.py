#!/usr/bin/env python3
"""Reject infeasible FDM variants and find the non-dominated objective set."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


OPS = {"<=", ">=", "<", ">", "==", "!="}


def compare(actual: Any, op: str, expected: Any, tolerance: float) -> bool:
    if op == "==":
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            return math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tolerance)
        return actual == expected
    if op == "!=":
        return not compare(actual, "==", expected, tolerance)
    if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
        return False
    if op == "<=":
        return actual <= expected + tolerance
    if op == ">=":
        return actual >= expected - tolerance
    if op == "<":
        return actual < expected
    if op == ">":
        return actual > expected
    raise ValueError(f"unsupported operator {op}")


def normalized(value: float, goal: str) -> float:
    return value if goal == "min" else -value


def dominates(a: dict[str, float], b: dict[str, float], objectives: list[dict[str, str]]) -> bool:
    av = [normalized(a[o["metric"]], o["goal"]) for o in objectives]
    bv = [normalized(b[o["metric"]], o["goal"]) for o in objectives]
    return all(x <= y for x, y in zip(av, bv)) and any(x < y for x, y in zip(av, bv))


def validate_payload(data: dict[str, Any]) -> None:
    required = {"baseline", "objectives", "constraints", "variants"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"missing top-level fields: {', '.join(missing)}")
    if not isinstance(data["variants"], list) or not data["variants"]:
        raise ValueError("variants must be a non-empty list")
    names = [v.get("name") for v in data["variants"]]
    if any(not isinstance(name, str) or not name for name in names):
        raise ValueError("every variant needs a non-empty string name")
    if len(set(names)) != len(names):
        raise ValueError("variant names must be unique")
    if data["baseline"] not in names:
        raise ValueError("baseline must name one variant")
    if not isinstance(data["objectives"], list) or not data["objectives"]:
        raise ValueError("objectives must be a non-empty list")
    for objective in data["objectives"]:
        if objective.get("goal") not in {"min", "max"} or not objective.get("metric"):
            raise ValueError("each objective needs metric and goal=min|max")
    for constraint in data["constraints"]:
        if not constraint.get("metric") or constraint.get("op") not in OPS or "value" not in constraint:
            raise ValueError("each constraint needs metric, op, and value")
    objective_metrics = [o["metric"] for o in data["objectives"]]
    for variant in data["variants"]:
        metrics = variant.get("metrics")
        if not isinstance(metrics, dict):
            raise ValueError(f"variant {variant['name']} needs a metrics object")
        for metric in objective_metrics:
            if not isinstance(metrics.get(metric), (int, float)):
                raise ValueError(f"variant {variant['name']} needs numeric objective {metric}")


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    validate_payload(data)
    variants = {v["name"]: v for v in data["variants"]}
    baseline_metrics = variants[data["baseline"]]["metrics"]
    results: list[dict[str, Any]] = []

    for variant in data["variants"]:
        metrics = variant["metrics"]
        failed = []
        for constraint in data["constraints"]:
            metric = constraint["metric"]
            tolerance = float(constraint.get("tolerance", 0.0))
            if metric not in metrics or not compare(metrics[metric], constraint["op"], constraint["value"], tolerance):
                failed.append({
                    "metric": metric,
                    "actual": metrics.get(metric),
                    "op": constraint["op"],
                    "required": constraint["value"],
                    "tolerance": tolerance,
                })
        deltas = {}
        for objective in data["objectives"]:
            metric = objective["metric"]
            value = float(metrics[metric])
            base = float(baseline_metrics[metric])
            deltas[metric] = {
                "absolute": value - base,
                "percent": None if base == 0 else 100.0 * (value - base) / abs(base),
            }
        results.append({
            "name": variant["name"],
            "feasible": not failed,
            "failed_constraints": failed,
            "objective_metrics": {o["metric"]: metrics[o["metric"]] for o in data["objectives"]},
            "delta_from_baseline": deltas,
            "notes": variant.get("notes", []),
            "pareto": False,
        })

    feasible_names = [r["name"] for r in results if r["feasible"]]
    pareto = []
    for name in feasible_names:
        metrics = variants[name]["metrics"]
        if not any(
            other != name and dominates(variants[other]["metrics"], metrics, data["objectives"])
            for other in feasible_names
        ):
            pareto.append(name)
    pareto_set = set(pareto)
    for result in results:
        result["pareto"] = result["name"] in pareto_set

    return {
        "baseline": data["baseline"],
        "objectives": data["objectives"],
        "constraints": data["constraints"],
        "results": results,
        "pareto_variants": pareto,
        "feasible_count": len(feasible_names),
        "interpretation": "Choose among feasible Pareto variants using explicit user priorities; no weighted score was invented.",
    }


def markdown(report: dict[str, Any]) -> str:
    metrics = [o["metric"] for o in report["objectives"]]
    headers = ["Variant", *metrics, "Feasible", "Pareto", "Failed constraints"]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for result in report["results"]:
        failures = ", ".join(f["metric"] for f in result["failed_constraints"]) or "—"
        values = [str(result["objective_metrics"][metric]) for metric in metrics]
        row = [result["name"], *values, "yes" if result["feasible"] else "no", "yes" if result["pareto"] else "no", failures]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("Pareto set: " + (", ".join(report["pareto_variants"]) or "none"))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-no-feasible", action="store_true")
    args = parser.parse_args()

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        report = analyze(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    encoded = markdown(report) if args.markdown else json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(encoded, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    return 2 if args.fail_no_feasible and report["feasible_count"] == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
