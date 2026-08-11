#!/usr/bin/env python3
"""Calculate mold/master oversize from measured linear shrinkage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def shrink_from_coupon(before: tuple[float, float, float], after: tuple[float, float, float]) -> tuple[float, float, float]:
    if any(v <= 0 for v in before + after):
        raise ValueError("Coupon dimensions must be positive.")
    return tuple((b - a) / b * 100.0 for b, a in zip(before, after, strict=True))


def calculate(final: tuple[float, float, float], shrink_pct: tuple[float, float, float]) -> dict[str, Any]:
    if any(v <= 0 for v in final):
        raise ValueError("Final dimensions must be positive.")
    if any(s >= 100.0 for s in shrink_pct):
        raise ValueError("Shrinkage must be below 100 percent.")
    factors = tuple(1.0 / (1.0 - s / 100.0) for s in shrink_pct)
    tool = tuple(f * d for f, d in zip(factors, final, strict=True))
    return {
        "final_dimensions_mm": list(final),
        "shrinkage_percent_xyz": list(shrink_pct),
        "oversize_scale_xyz": list(factors),
        "tool_or_green_dimensions_mm": list(tool),
        "formula": "tool_dimension = final_dimension / (1 - shrink_fraction)",
        "warning": "Use measured values for the exact body, preparation, drying, firing, orientation, and glaze route."
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final", nargs=3, required=True, type=float, metavar=("X", "Y", "Z"), help="Desired final dimensions in mm")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--shrink", nargs=3, type=float, metavar=("X_PCT", "Y_PCT", "Z_PCT"), help="Measured linear shrinkage percent")
    group.add_argument("--coupon-before", nargs=3, type=float, metavar=("X", "Y", "Z"), help="Coupon dimensions before shrinkage; requires --coupon-after")
    parser.add_argument("--coupon-after", nargs=3, type=float, metavar=("X", "Y", "Z"), help="Coupon dimensions after shrinkage")
    parser.add_argument("--json", dest="json_path", type=Path, help="Write JSON result")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        final = tuple(args.final)
        if args.shrink is not None:
            shrink = tuple(args.shrink)
            source = "provided_percent"
        else:
            if args.coupon_after is None:
                raise ValueError("--coupon-before requires --coupon-after.")
            shrink = shrink_from_coupon(tuple(args.coupon_before), tuple(args.coupon_after))
            source = "measured_coupon"
        result = calculate(final, shrink)
        result["shrinkage_source"] = source
        if args.coupon_before is not None:
            result["coupon_before_mm"] = list(args.coupon_before)
            result["coupon_after_mm"] = list(args.coupon_after)

        text = json.dumps(result, indent=2)
        print(text)
        if args.json_path:
            path = args.json_path.expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text + "\n", encoding="utf-8")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
