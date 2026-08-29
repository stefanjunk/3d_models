#!/usr/bin/env python3
"""Check key OpenSCAD parameters against the engineering calculation model."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAD = ROOT / "CAD" / "openquad_cf5.scad"
VALIDATOR = ROOT / "analysis" / "validate_design.py"
OUT = ROOT / "output" / "scad_sync_report.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("openquad_validate", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load validate_design.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_assignment(source: str, name: str) -> float:
    match = re.search(rf"(?m)^\s*{re.escape(name)}\s*=\s*(-?\d+(?:\.\d+)?)\s*;", source)
    if not match:
        raise ValueError(f"Direct numeric assignment not found: {name}")
    return float(match.group(1))


def delimiter_check(source: str) -> dict:
    # Strip line comments and quoted strings before balancing delimiters.
    stripped = re.sub(r"//.*", "", source)
    stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', stripped)
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[tuple[str, int]] = []
    for index, char in enumerate(stripped):
        if char in "([{":
            stack.append((char, index))
        elif char in ")]}":
            if not stack or stack[-1][0] != pairs[char]:
                return {"pass": False, "error": f"Unexpected {char} at character {index}"}
            stack.pop()
    if stack:
        char, index = stack[-1]
        return {"pass": False, "error": f"Unclosed {char} from character {index}"}
    return {"pass": True, "error": None}


def main() -> int:
    model = load_validator()
    source = SCAD.read_text(encoding="utf-8")
    expected = {
        "wheelbase": model.WHEELBASE_MM,
        "prop_diameter": model.PROP_DIAMETER_MM,
        "arm_outer": model.ARM_OUTER_MM,
        "arm_inner": model.ARM_INNER_MM,
        "arm_inner_radius": model.ARM_INNER_RADIUS_MM,
        "hub_size": model.HUB_SIZE_MM,
        "deck_length": model.DECK_LENGTH_MM,
        "deck_width": model.DECK_WIDTH_MM,
        "deck_standoff_height": model.DECK_HEIGHT_MM - 16.0,
        "motor_pattern": 16.0,
        "saddle_length": model.SADDLE_OVERLAP_MM,
        "saddle_width": model.SADDLE_WIDTH_MM,
        "fc_hole_spacing": model.FC_HOLE_SPACING_MM,
    }
    values = {}
    checks = []
    for name, exp in expected.items():
        actual = parse_assignment(source, name)
        passed = abs(actual - exp) < 1e-9
        values[name] = actual
        checks.append({"parameter": name, "scad": actual, "analysis": exp, "pass": passed})
    delimiters = delimiter_check(source)
    result = {
        "status": "TEXTUAL_SANITY_ONLY_NOT_AN_OPENSCAD_RENDER",
        "parameter_checks": checks,
        "delimiter_check": delimiters,
        "pass": all(c["pass"] for c in checks) and delimiters["pass"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
