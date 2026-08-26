#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from surface_geometry import curve_metrics, read_csv_points, resample_polyline, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze discrete curvature/fairness indicators for a guide curve.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--closed", action="store_true")
    parser.add_argument("--count", type=int, default=256)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    points = read_csv_points(args.input)
    sampled = resample_polyline(points, count=args.count, closed=args.closed)
    report = {"input": str(args.input), **curve_metrics(sampled, closed=args.closed)}
    if args.report:
        write_json(args.report, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
