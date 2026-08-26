#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from surface_geometry import (
    curve_metrics,
    fairing_displacement,
    fourier_smooth_closed,
    read_csv_points,
    regularized_smooth,
    resample_polyline,
    write_csv_points,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fair a 2D/3D guide curve and report geometric screening metrics.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--method", choices=("regularized", "fourier"), default="regularized")
    parser.add_argument("--strength", type=float, default=10.0, help="Regularization strength for second differences")
    parser.add_argument("--harmonics", type=int, default=8, help="Retained positive Fourier harmonics")
    parser.add_argument("--count", type=int, help="Output point count; defaults to input count")
    parser.add_argument("--closed", action="store_true")
    parser.add_argument("--preserve-ends", action="store_true")
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    original = read_csv_points(args.input)
    count = args.count or len(original)
    sampled = resample_polyline(original, count=count, closed=args.closed)
    if args.method == "regularized":
        faired = regularized_smooth(
            sampled,
            strength=args.strength,
            closed=args.closed,
            preserve_ends=args.preserve_ends or not args.closed,
        )
    else:
        if not args.closed:
            raise SystemExit("Fourier fairing requires --closed")
        faired = fourier_smooth_closed(sampled, harmonics=args.harmonics, output_count=count)
    write_csv_points(args.output, faired)
    report = {
        "input": str(args.input),
        "output": str(args.output),
        "method": args.method,
        "closed": args.closed,
        "before": curve_metrics(sampled, closed=args.closed),
        "after": curve_metrics(faired, closed=args.closed),
        "displacement": fairing_displacement(sampled, faired, closed=args.closed),
    }
    if args.report:
        write_json(args.report, report)
    print(f"Wrote {args.output}")
    if args.report:
        print(f"Wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
