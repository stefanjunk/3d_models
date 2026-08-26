#!/usr/bin/env python3
"""Optional SciPy B-spline fitting helper.

The portable core does not require SciPy.  When SciPy is available this script
fits an actual parametric BSpline and exports both sampled points and a JSON
record of degree, knots, coefficients, fit error, and fairness screening.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from surface_geometry import curve_metrics, read_csv_points, resample_polyline, write_csv_points, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit a SciPy parametric B-spline to 2D/3D samples.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--degree", type=int, default=3)
    parser.add_argument("--smoothing", type=float, default=1.0, help="Upper bound for weighted squared residual")
    parser.add_argument("--samples", type=int, default=256)
    parser.add_argument("--closed", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        from scipy.interpolate import make_splprep
    except Exception as exc:
        raise SystemExit(f"SciPy with make_splprep is required: {exc}")

    original = read_csv_points(args.input)
    fitting = original
    bc_type = None
    if args.closed:
        fitting = resample_polyline(original, max(len(original), args.degree + 4), closed=True)
        fitting = np.vstack([fitting, fitting[0]])
        bc_type = "periodic"
    spline, parameters = make_splprep(
        fitting.T,
        k=args.degree,
        s=args.smoothing,
        bc_type=bc_type,
    )
    sample_u = np.linspace(float(parameters[0]), float(parameters[-1]), args.samples, endpoint=not args.closed)
    sampled = np.asarray(spline(sample_u)).T
    write_csv_points(args.output, sampled)
    fitted_at_input = np.asarray(spline(parameters)).T
    residual = np.linalg.norm(fitted_at_input - fitting, axis=1)
    report = {
        "input": str(args.input),
        "output": str(args.output),
        "degree": int(spline.k),
        "closed": args.closed,
        "smoothing": args.smoothing,
        "knots": np.asarray(spline.t).tolist(),
        "coefficients": np.asarray(spline.c).tolist(),
        "input_point_count": int(len(original)),
        "coefficient_count": int(len(spline.c)),
        "fit_rms_mm": float(np.sqrt(np.mean(residual**2))),
        "fit_max_mm": float(residual.max()),
        "sampled_curve": curve_metrics(sampled, closed=args.closed),
    }
    if args.report:
        write_json(args.report, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
