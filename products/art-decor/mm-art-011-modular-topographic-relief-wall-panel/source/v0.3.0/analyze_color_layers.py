#!/usr/bin/env python3
"""Analyze layer-only color changes from the authoritative terrain band solids."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[1]


def analyze(pilot: str) -> dict:
    report_path = PRODUCT / "validation" / "v0.3.0" / pilot / f"{pilot}-build-report.json"
    report = json.loads(report_path.read_text())
    layer_height = float(report["color"]["layer_height_mm"])
    halves = {}
    overall_pass = True
    for half, half_report in report["halves"].items():
        ordered = list(half_report["colors"].items())
        maximum_z = float(half_report["composite"]["bounds_mm"][1][2])
        layer_count = int(math.ceil(maximum_z / layer_height))
        previous = None
        transitions = []
        active_histogram: dict[str, int] = {}
        multiple = 0
        uncovered = 0
        for layer in range(layer_count):
            z = (layer + 0.5) * layer_height
            active = [
                color_id
                for color_id, color in ordered
                if float(color["bounds_mm"][0][2]) - 1e-7 <= z <= float(color["bounds_mm"][1][2]) + 1e-7
            ]
            active_histogram[str(len(active))] = active_histogram.get(str(len(active)), 0) + 1
            if len(active) > 1:
                multiple += 1
            if not active:
                uncovered += 1
                continue
            current = active[0]
            if previous is not None and current != previous:
                transitions.append({"layer": layer, "z_center_mm": z, "from": previous, "to": current})
            previous = current
        half_pass = len(ordered) == 4 and len(transitions) == 3 and multiple == 0 and uncovered == 0
        overall_pass &= half_pass
        halves[half] = {
            "status": "PASS" if half_pass else "FAIL",
            "layer_count": layer_count,
            "active_color_count_histogram": active_histogram,
            "layers_with_multiple_colors": multiple,
            "uncovered_layers": uncovered,
            "estimated_transition_count": len(transitions),
            "transitions": transitions,
            "directed_purge_mm3": None,
        }
    return {
        "schema_version": "1.0",
        "project": "MM-ART-011",
        "revision": "0.3.0",
        "pilot": pilot,
        "status": "PASS" if overall_pass else "FAIL",
        "method": "Exact Z-occupancy of the four exported color solids at 0.2 mm layer centers; no slicer path-order claim.",
        "purge_matrix_status": "NOT_MEASURED; final ACE purge tower remains a human destination-slicer gate",
        "halves": halves,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", choices=("harz", "rhenish"), required=True)
    args = parser.parse_args()
    result = analyze(args.pilot)
    output = PRODUCT / "validation" / "v0.3.0" / args.pilot / f"{args.pilot}-color-layer-analysis.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "output": str(output)}))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
