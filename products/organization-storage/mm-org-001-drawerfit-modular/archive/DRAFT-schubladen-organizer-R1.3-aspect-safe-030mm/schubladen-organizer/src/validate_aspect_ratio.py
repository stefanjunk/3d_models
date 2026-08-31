#!/usr/bin/env python3
"""Hard gate for physical aspect metadata before geometry generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail when a prepared relief violates its physical aspect invariant."
    )
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--tolerance-pct", type=float)
    args = parser.parse_args()
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    validation = metadata.get("aspect_validation")
    if not isinstance(validation, dict):
        raise SystemExit("aspect_validation metadata is missing; geometry generation is blocked")
    error = float(validation.get("error_pct", float("inf")))
    tolerance = (
        float(args.tolerance_pct)
        if args.tolerance_pct is not None
        else float(validation.get("tolerance_pct", 0.0))
    )
    recorded_pass = validation.get("passed") is True
    passed = recorded_pass and error <= tolerance
    result = {
        "physical_aspect_error_pct": error,
        "tolerance_pct": tolerance,
        "aspect_policy": validation.get("aspect_policy"),
        "allow_aspect_distortion": validation.get("allow_aspect_distortion"),
        "passed": passed,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
