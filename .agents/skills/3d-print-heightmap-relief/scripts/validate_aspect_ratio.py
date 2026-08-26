#!/usr/bin/env python3
from __future__ import annotations

import argparse
from _relief_utils import read_json


def main() -> int:
    p = argparse.ArgumentParser(description="Fail if a prepared heightmap violates its physical aspect invariant.")
    p.add_argument("metadata_json")
    p.add_argument("--tolerance-pct", type=float)
    args = p.parse_args()
    meta = read_json(args.metadata_json)
    av = meta.get("aspect_validation") or {}
    error = float(av.get("error_pct", float("inf")))
    tolerance = args.tolerance_pct if args.tolerance_pct is not None else float(av.get("tolerance_pct", 1.0))
    passed = error <= tolerance
    print(f"physical aspect error: {error:.6f}%")
    print(f"tolerance: {tolerance:.6f}%")
    print(f"passed: {passed}")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
