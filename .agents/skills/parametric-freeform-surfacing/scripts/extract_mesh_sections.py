#!/usr/bin/env python3
"""Optional Trimesh helper to extract semantic planar sections from a reference mesh."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from surface_geometry import curve_metrics, polyline_length, resample_polyline, write_csv_points, write_json


def parse_positions(text: str) -> list[float]:
    try:
        values = [float(value.strip()) for value in text.split(",") if value.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if not values:
        raise argparse.ArgumentTypeError("At least one section position is required")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract longest closed planar section loops from STL/OBJ/PLY/GLB reference meshes.")
    parser.add_argument("mesh", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--axis", choices=("x", "y", "z"), default="x")
    parser.add_argument("--positions", type=parse_positions, help="Comma-separated positions in model units")
    parser.add_argument("--count", type=int, help="Evenly distribute planes inside mesh bounds")
    parser.add_argument("--margin", type=float, default=0.02, help="Fractional bound margin for --count")
    parser.add_argument("--points", type=int, default=128)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        import trimesh
    except Exception as exc:
        raise SystemExit(f"Trimesh is not available; extraction status is NOT_RUN: {exc}")

    loaded = trimesh.load(args.mesh, force="mesh", process=False)
    if not isinstance(loaded, trimesh.Trimesh) or loaded.is_empty:
        raise SystemExit(f"Could not load a non-empty mesh from {args.mesh}")
    axis_index = {"x": 0, "y": 1, "z": 2}[args.axis]
    normal = np.zeros(3)
    normal[axis_index] = 1.0
    lower, upper = map(float, loaded.bounds[:, axis_index])
    if args.positions is not None and args.count is not None:
        raise SystemExit("Choose either --positions or --count")
    if args.positions is None:
        count = args.count or 8
        if count < 2:
            raise SystemExit("--count must be at least 2")
        span = upper - lower
        positions = np.linspace(lower + args.margin * span, upper - args.margin * span, count).tolist()
    else:
        positions = args.positions

    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    successes = 0
    for index, position in enumerate(positions):
        origin = np.zeros(3)
        origin[axis_index] = position
        section = loaded.section(plane_origin=origin, plane_normal=normal)
        record = {"index": index, "axis": args.axis, "position": position, "status": "NO_INTERSECTION"}
        if section is not None:
            loops = [np.asarray(loop, dtype=float) for loop in section.discrete if len(loop) >= 3]
            if loops:
                loop = max(loops, key=lambda points: polyline_length(points, closed=True))
                if np.linalg.norm(loop[0] - loop[-1]) < 1e-7:
                    loop = loop[:-1]
                sampled = resample_polyline(loop, count=args.points, closed=True)
                output_path = args.output / f"{index:03d}_{args.axis}_{position:+.4f}.csv"
                write_csv_points(output_path, sampled)
                record.update({
                    "status": "PASS",
                    "output": str(output_path),
                    "candidate_loop_count": len(loops),
                    "selected_loop_length": polyline_length(loop, closed=True),
                    "metrics": curve_metrics(sampled, closed=True),
                })
                successes += 1
        records.append(record)
    report = {
        "mesh": str(args.mesh),
        "mesh_bounds": loaded.bounds.tolist(),
        "axis": args.axis,
        "requested_sections": len(positions),
        "extracted_sections": successes,
        "records": records,
        "warning": "The longest loop is a heuristic. Review semantic correspondence, source units, topology, and internal shells before lofting.",
    }
    report_path = args.report or (args.output / "section-extraction.json")
    write_json(report_path, report)
    print(json.dumps({"report": str(report_path), "extracted": successes, "requested": len(positions)}, indent=2))
    return 0 if successes > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
