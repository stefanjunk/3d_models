#!/usr/bin/env python3
"""Perform structural checks on a design-spec YAML/JSON file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import load_structured

REQUIRED_TOP = ["project", "function", "risk", "fabrication", "printer", "manufacturing", "acceptance"]
VALID_RISK = {"decorative", "normal-functional", "structural", "safety-critical"}
VALID_MODE = {"integrated-print", "balanced-hybrid", "standard-hardware"}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("spec")
    p.add_argument("--json-out")
    args = p.parse_args()

    data = load_structured(args.spec)
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing top-level field: {key}")

    risk = data.get("risk", {}).get("class") if isinstance(data.get("risk"), dict) else None
    if risk not in VALID_RISK:
        errors.append(f"risk.class must be one of {sorted(VALID_RISK)}")

    mode = data.get("fabrication", {}).get("preference") if isinstance(data.get("fabrication"), dict) else None
    if mode not in VALID_MODE:
        errors.append(f"fabrication.preference must be one of {sorted(VALID_MODE)}")

    nozzle = data.get("manufacturing", {}).get("nozzle_mm") if isinstance(data.get("manufacturing"), dict) else None
    if nozzle is None or not isinstance(nozzle, (int, float)) or nozzle <= 0:
        errors.append("manufacturing.nozzle_mm must be positive")
    elif nozzle not in (0.4, 0.6, 0.8):
        warnings.append("nonstandard nozzle: ensure an explicit profile and feature calibration")

    build = data.get("printer", {}).get("build_volume_mm") if isinstance(data.get("printer"), dict) else None
    if not isinstance(build, list) or len(build) != 3 or not all(isinstance(v, (int, float)) and v > 0 for v in build):
        errors.append("printer.build_volume_mm must contain three positive numbers")

    acceptance = data.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        errors.append("acceptance must be a nonempty list")
    elif not all(isinstance(item, dict) and item.get("id") and item.get("criterion") for item in acceptance):
        errors.append("every acceptance entry needs id and criterion")

    if risk in {"structural", "safety-critical"}:
        loads = data.get("loads")
        if not loads:
            errors.append("structural/safety-critical design requires loads")
        if not data.get("test_plan"):
            warnings.append("structural/safety-critical design should link a test_plan")

    report = {"spec": str(Path(args.spec).resolve()), "errors": errors, "warnings": warnings, "passed": not errors}
    text = json.dumps(report, indent=2)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
