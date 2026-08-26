#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    require(isinstance(data, dict), "Root must be a mapping", errors)
    if not isinstance(data, dict):
        return errors
    required = {"schema_version", "project", "intent", "semantic_parameters", "hardpoints", "surface_strategy", "fdm", "acceptance", "outputs"}
    for key in sorted(required - set(data)):
        errors.append(f"Missing top-level key: {key}")
    project = data.get("project", {})
    require(project.get("units") == "mm", "project.units must be mm", errors)
    require(bool(project.get("name")), "project.name is required", errors)
    params = data.get("semantic_parameters", [])
    require(isinstance(params, list), "semantic_parameters must be a list", errors)
    names: set[str] = set()
    if isinstance(params, list):
        for index, item in enumerate(params):
            require(isinstance(item, dict), f"semantic_parameters[{index}] must be a mapping", errors)
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            require(isinstance(name, str) and bool(name), f"semantic_parameters[{index}].name is required", errors)
            if isinstance(name, str):
                require(name not in names, f"Duplicate semantic parameter: {name}", errors)
                names.add(name)
            value = item.get("value")
            require(isinstance(value, (int, float)), f"semantic_parameters[{index}].value must be numeric", errors)
            minimum, maximum = item.get("min"), item.get("max")
            if isinstance(value, (int, float)) and isinstance(minimum, (int, float)):
                require(value >= minimum, f"{name}: value is below min", errors)
            if isinstance(value, (int, float)) and isinstance(maximum, (int, float)):
                require(value <= maximum, f"{name}: value is above max", errors)
            if isinstance(minimum, (int, float)) and isinstance(maximum, (int, float)):
                require(minimum <= maximum, f"{name}: min exceeds max", errors)
    hardpoints = data.get("hardpoints", {})
    require(isinstance(hardpoints.get("tolerance_mm"), (int, float)) and hardpoints.get("tolerance_mm", -1) >= 0, "hardpoints.tolerance_mm must be non-negative", errors)
    strategy = data.get("surface_strategy", {})
    require(strategy.get("primary") in {"bspline-loft", "nurbs-network", "subd", "ffd", "morph", "sdf-local", "hybrid"}, "surface_strategy.primary is invalid", errors)
    require(strategy.get("continuity_default") in {"G0", "G1", "G2", "G3", "intentional-sharp"}, "surface_strategy.continuity_default is invalid", errors)
    fdm = data.get("fdm", {})
    build = fdm.get("printer_build_volume_mm")
    require(isinstance(build, list) and len(build) == 3 and all(isinstance(x, (int, float)) and x > 0 for x in build), "fdm.printer_build_volume_mm must contain three positive numbers", errors)
    nozzle = fdm.get("nozzle_mm")
    require(isinstance(nozzle, (int, float)) and nozzle > 0, "fdm.nozzle_mm must be positive", errors)
    wall = fdm.get("minimum_wall_mm")
    require(isinstance(wall, (int, float)) and wall > 0, "fdm.minimum_wall_mm must be positive", errors)
    heights = fdm.get("layer_height_range_mm")
    require(isinstance(heights, list) and len(heights) == 2 and all(isinstance(x, (int, float)) and x > 0 for x in heights), "fdm.layer_height_range_mm must contain two positive numbers", errors)
    if isinstance(heights, list) and len(heights) == 2 and all(isinstance(x, (int, float)) for x in heights):
        require(heights[0] <= heights[1], "layer height range is reversed", errors)
        if isinstance(nozzle, (int, float)) and nozzle > 0:
            require(heights[1] <= 0.8 * nozzle + 1e-12, "maximum layer height exceeds 80% of nozzle diameter", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a surfacing-spec YAML file with core portable checks.")
    parser.add_argument("spec", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    data = yaml.safe_load(args.spec.read_text(encoding="utf-8"))
    errors = validate(data)
    report = {"spec": str(args.spec), "valid": not errors, "errors": errors}
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
