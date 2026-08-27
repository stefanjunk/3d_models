#!/usr/bin/env python3
"""Fail-closed check for exact filament identity and label temperature bounds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def evaluate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    product = data.get("product", {})
    label = data.get("label_temperature_c", {})
    proposals = data.get("proposals", [])

    identity = " ".join(
        str(product.get(key, "")) for key in ("manufacturer", "name", "variant", "color")
    ).casefold()
    for marker in product.get("excluded_markers", []):
        if str(marker).casefold() in identity:
            errors.append(f"product identity contains excluded marker: {marker}")

    try:
        lower = float(label["min"])
        upper = float(label["max"])
    except (KeyError, TypeError, ValueError):
        return errors + ["label_temperature_c.min/max must be numeric"]
    if lower >= upper:
        errors.append("label temperature minimum must be lower than maximum")

    required = {
        (0.4, "brass"),
        (0.4, "stainless-steel"),
        (0.4, "hardened-steel"),
        (0.8, "brass"),
        (0.8, "stainless-steel"),
        (0.8, "hardened-steel"),
    }
    seen: set[tuple[float, str]] = set()
    for index, proposal in enumerate(proposals):
        try:
            diameter = float(proposal["nozzle_diameter_mm"])
            material = str(proposal["nozzle_material"]).casefold()
            temperature = float(proposal["temperature_c"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"proposal {index} has incomplete or invalid fields")
            continue
        seen.add((diameter, material))
        if not lower <= temperature <= upper:
            errors.append(
                f"proposal {index} temperature {temperature:g} °C is outside "
                f"the exact label range {lower:g}-{upper:g} °C"
            )
    missing = sorted(required - seen)
    if missing:
        errors.append(f"missing required diameter/material proposals: {missing}")
    if data.get("thermal_shortfall_action") != "reduce-flow-and-validate":
        errors.append("thermal shortfall must reduce flow and require validation")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    with args.fixture.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    errors = evaluate(data)
    result = {"fixture": str(args.fixture), "status": "fail" if errors else "pass", "errors": errors}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
