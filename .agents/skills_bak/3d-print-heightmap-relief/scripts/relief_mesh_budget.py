#!/usr/bin/env python3
"""Budget relief triangles, mesh bytes, working memory, slicer time, and tolerance."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def positive(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a finite number greater than zero")
    return parsed


def pitch_pair(value: str) -> tuple[float, float]:
    raw = value.lower().replace("*", "x").split("x")
    if len(raw) == 1:
        p = positive(raw[0])
        return p, p
    if len(raw) != 2:
        raise argparse.ArgumentTypeError("pitch must be P or PxP, for example 0.30x0.20")
    return positive(raw[0]), positive(raw[1])


def gate(triangles: int, target: int, stop: int) -> str:
    if triangles > stop:
        return "STOP"
    if triangles > target:
        return "REVIEW"
    return "PASS"


def human_bytes(value: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    amount = float(value)
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            return f"{amount:.2f} {unit}"
        amount /= 1024.0
    raise AssertionError("unreachable")


def tolerance_plan(
    process: str,
    nozzle: float | None,
    depth: float | None,
    layer: float | None,
    pitch: tuple[float, float],
) -> dict:
    if process == "fdm":
        if nozzle is None or depth is None or layer is None:
            raise ValueError("FDM tolerance planning requires nozzle, layer height, and relief depth")
        limits = {
            "ten_percent_nozzle_mm": 0.10 * nozzle,
            "twenty_percent_layer_height_mm": 0.20 * layer,
            "twelve_and_half_percent_relief_depth_mm": 0.125 * depth,
            "portable_cap_mm": 0.05,
        }
        formula = "min(0.10*nozzle, 0.20*layer_height, 0.125*relief_depth, 0.05 mm)"
    else:
        limits = {
            "ten_percent_min_pitch_mm": 0.10 * min(pitch),
            "portable_cap_mm": 0.05,
        }
        if depth is not None:
            limits["eight_percent_relief_depth_mm"] = 0.08 * depth
        if layer is not None:
            limits["quarter_layer_height_mm"] = 0.25 * layer
        formula = "non-FDM fallback from physical pitch, layer height, depth, and 0.05 mm cap"
    start = min(limits.values())
    return {
        "formula": formula,
        "basis": limits,
        "starting_tolerance_mm": round(start, 6),
        "candidate_sweep_mm": [round(start * factor, 6) for factor in (0.5, 1.0, 1.5)],
        "note": "Candidate tolerances require geometric, relief-amplitude, wall, bed-contact, and slicer acceptance checks.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--area-mm2", required=True, type=positive, help="Actual displaced surface area")
    parser.add_argument("--pitch-mm", required=True, type=pitch_pair, help="X or XxY physical sample pitch")
    parser.add_argument("--process", choices=["fdm", "resin"], default="fdm")
    parser.add_argument("--nozzle-mm", type=positive, help="Required for the FDM automatic tolerance formula")
    parser.add_argument("--depth-mm", type=positive, help="Peak-to-valley relief depth")
    parser.add_argument("--layer-height-mm", type=positive)
    parser.add_argument("--base-triangles", type=int, default=0, help="Known non-relief triangles in the closed cutter/part")
    parser.add_argument("--actual-triangles", type=int, help="Optional measured final triangle count")
    parser.add_argument("--target-triangles", type=int, default=1_000_000)
    parser.add_argument("--stop-triangles", type=int, default=5_000_000)
    parser.add_argument("--memory-budget-gib", required=True, type=positive)
    parser.add_argument(
        "--working-bytes-per-triangle",
        type=positive,
        default=1024.0,
        help="Calibratable planning coefficient for kernel arrays/intermediates; not a universal constant",
    )
    parser.add_argument("--memory-headroom-pct", type=float, default=25.0)
    parser.add_argument("--max-mesh-mib", required=True, type=positive)
    parser.add_argument("--max-slicer-seconds", required=True, type=positive)
    parser.add_argument("--actual-peak-memory-gib", type=positive)
    parser.add_argument("--actual-file-bytes", type=int)
    parser.add_argument("--actual-slicer-seconds", type=positive)
    parser.add_argument("--output", type=Path, help="Write the same JSON report to a file")
    parser.add_argument("--fail-on-stop", action="store_true")
    parser.add_argument("--require-measured-release", action="store_true")
    args = parser.parse_args()

    for name in ("base_triangles", "target_triangles", "stop_triangles"):
        if getattr(args, name) < 0:
            parser.error(f"--{name.replace('_', '-')} cannot be negative")
    if args.target_triangles <= 0 or args.stop_triangles <= args.target_triangles:
        parser.error("require 0 < target-triangles < stop-triangles")
    if args.actual_triangles is not None and args.actual_triangles < 0:
        parser.error("--actual-triangles cannot be negative")
    if args.actual_file_bytes is not None and args.actual_file_bytes < 0:
        parser.error("--actual-file-bytes cannot be negative")
    if not 0 <= args.memory_headroom_pct < 100:
        parser.error("--memory-headroom-pct must be in [0, 100)")
    if args.process == "fdm" and any(value is None for value in (args.nozzle_mm, args.depth_mm, args.layer_height_mm)):
        parser.error("FDM planning requires --nozzle-mm, --depth-mm, and --layer-height-mm")

    px, py = args.pitch_mm
    cells = math.ceil(args.area_mm2 / (px * py))
    relief_triangles = 2 * cells
    estimated_total = relief_triangles + args.base_triangles
    assessed = args.actual_triangles if args.actual_triangles is not None else estimated_total
    estimated_stl_bytes = 84 + 50 * estimated_total
    actual_stl_bytes = 84 + 50 * args.actual_triangles if args.actual_triangles is not None else None
    triangle_status = gate(assessed, args.target_triangles, args.stop_triangles)
    estimated_peak_memory_bytes = math.ceil(estimated_total * args.working_bytes_per_triangle)
    estimated_peak_memory_gib = estimated_peak_memory_bytes / (1024 ** 3)
    usable_memory_gib = args.memory_budget_gib * (1.0 - args.memory_headroom_pct / 100.0)
    memory_status = "PASS" if estimated_peak_memory_gib <= usable_memory_gib else "STOP"
    file_limit_bytes = math.floor(args.max_mesh_mib * 1024 ** 2)
    file_status = "PASS" if estimated_stl_bytes <= file_limit_bytes else "STOP"
    planning_status = "STOP" if "STOP" in {triangle_status, memory_status, file_status} else triangle_status

    measured = {
        "peak_memory": "PENDING" if args.actual_peak_memory_gib is None else (
            "PASS" if args.actual_peak_memory_gib <= args.memory_budget_gib else "STOP"
        ),
        "file_size": "PENDING" if args.actual_file_bytes is None else (
            "PASS" if args.actual_file_bytes <= file_limit_bytes else "STOP"
        ),
        "slicer_time": "PENDING" if args.actual_slicer_seconds is None else (
            "PASS" if args.actual_slicer_seconds <= args.max_slicer_seconds else "STOP"
        ),
    }
    if "STOP" in measured.values() or planning_status == "STOP":
        release_status = "STOP"
    elif "PENDING" in measured.values():
        release_status = "PENDING"
    else:
        release_status = "PASS"

    report = {
        "input": {
            "displaced_area_mm2": args.area_mm2,
            "pitch_mm": [px, py],
            "depth_mm": args.depth_mm,
            "layer_height_mm": args.layer_height_mm,
            "base_triangles": args.base_triangles,
            "process": args.process,
            "nozzle_mm": args.nozzle_mm,
        },
        "uniform_grid_worst_case": {
            "cells": cells,
            "relief_triangles": relief_triangles,
            "estimated_total_triangles": estimated_total,
            "estimated_binary_stl_bytes": estimated_stl_bytes,
            "estimated_binary_stl_size": human_bytes(estimated_stl_bytes),
            "note": "Excludes Boolean splits and is not a final mesh prediction.",
        },
        "actual": None if all(value is None for value in (
            args.actual_triangles,
            args.actual_file_bytes,
            args.actual_peak_memory_gib,
            args.actual_slicer_seconds,
        )) else {
            "triangles": args.actual_triangles,
            "binary_stl_bytes_if_stl": actual_stl_bytes,
            "binary_stl_size_if_stl": None if actual_stl_bytes is None else human_bytes(actual_stl_bytes),
            "file_bytes": args.actual_file_bytes,
            "peak_memory_gib": args.actual_peak_memory_gib,
            "slicer_seconds": args.actual_slicer_seconds,
        },
        "policy": {
            "assessed_triangles": assessed,
            "target_triangles": args.target_triangles,
            "stop_triangles": args.stop_triangles,
            "triangle_status": triangle_status,
            "status": planning_status,
            "scope": "Conservative portable workflow policy, not a printer-resolution limit.",
        },
        "resource_budget": {
            "memory_budget_gib": args.memory_budget_gib,
            "memory_headroom_pct": args.memory_headroom_pct,
            "usable_memory_gib": usable_memory_gib,
            "working_bytes_per_triangle": args.working_bytes_per_triangle,
            "estimated_peak_memory_gib": estimated_peak_memory_gib,
            "memory_planning_status": memory_status,
            "max_mesh_mib": args.max_mesh_mib,
            "estimated_binary_stl_mib": estimated_stl_bytes / (1024 ** 2),
            "file_planning_status": file_status,
            "max_slicer_seconds": args.max_slicer_seconds,
            "measured_status": measured,
            "release_status": release_status,
            "note": "Calibrate working bytes per triangle with the chosen kernel; measured peak memory and exact-slicer time remain mandatory release evidence.",
        },
        "simplification": tolerance_plan(args.process, args.nozzle_mm, args.depth_mm, args.layer_height_mm, args.pitch_mm),
        "recommended_order": [
            "limit relief to applied/visible regions",
            "remove unintended flat background",
            "generate adaptively from physical error or curvature",
            "simplify the relief cutter with protected seams and interfaces",
            "boolean into the exact functional base",
            "measure the final mesh and benchmark the exact slicer",
        ],
    }

    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    if args.fail_on_stop and planning_status == "STOP":
        return 2
    if args.require_measured_release and release_status != "PASS":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
