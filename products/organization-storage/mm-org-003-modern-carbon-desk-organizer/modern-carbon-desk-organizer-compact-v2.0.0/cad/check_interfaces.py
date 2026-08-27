#!/usr/bin/env python3
"""Deterministic source-level interface contract for MM-ORG-003 compact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = ROOT / "model-parameters.json"
SOURCE = ROOT / "cad" / "build_compact_organizer.py"
ASSEMBLY_REPORT = ROOT / "validation" / "parametric-source-report.json"
OUTPUT = ROOT / "validation" / "interface-report.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def close(actual: float, expected: float, tolerance: float = 1e-6) -> bool:
    return abs(actual - expected) <= tolerance


def check(check_id: str, passed: bool, message: str, metrics: dict) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics,
        "evidence": [],
    }


def main() -> None:
    p = json.loads(PARAMS.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY_REPORT.read_text(encoding="utf-8"))
    housing = p["housing"]
    drawer = p["drawer"]
    sorter = p["sorter"]
    stack = p["stack_interface"]

    cavity_width = housing["width"] - 2.0 * housing["side_wall"]
    side_clearance = (cavity_width - drawer["body_width"]) / 2.0
    cavity_depth = housing["depth"] - housing["rear_wall"]
    drawer_depth_stack = drawer["front_depth"] + drawer["body_depth"] + drawer["rear_clearance"]
    vertical_clearance = housing["opening_height"] - drawer["body_height"]
    stack_clearance_each = (stack["socket_size"] - stack["peg_size"]) / 2.0
    insertion_reserve = stack["socket_depth"] - stack["peg_height"]
    cell_width = (sorter["width"] - 2.0 * sorter["outer_wall"] - (sorter["columns"] - 1) * sorter["divider_wall"]) / sorter["columns"]
    cell_depth = (sorter["depth"] - 2.0 * sorter["outer_wall"] - (sorter["rows"] - 1) * sorter["divider_wall"]) / sorter["rows"]
    assembly_extents = assembly["metrics"]["assembly_extents_mm"]

    checks = [
        check("drawer-side-clearance", close(side_clearance, drawer["side_clearance_each"]), "Drawer has the declared 0.45 mm clearance on each side.", {"actual_mm": side_clearance, "required_mm": drawer["side_clearance_each"]}),
        check("drawer-depth-stack", close(drawer_depth_stack, cavity_depth), "Drawer front, body and rear reserve close the housing cavity depth exactly.", {"drawer_stack_mm": drawer_depth_stack, "cavity_mm": cavity_depth}),
        check("drawer-top-clearance", close(vertical_clearance, drawer["top_clearance"]), "Each drawer opening provides the declared 3.0 mm vertical clearance.", {"actual_mm": vertical_clearance, "required_mm": drawer["top_clearance"]}),
        check("stack-lateral-clearance", close(stack_clearance_each, 0.35), "Each tapered sorter peg has 0.35 mm nominal lateral socket clearance per side.", {"clearance_each_mm": stack_clearance_each}),
        check("stack-depth-reserve", insertion_reserve >= 0.2, "Socket depth exceeds peg height and avoids bottoming out.", {"reserve_mm": insertion_reserve}),
        check("sorter-grid", sorter["rows"] == 3 and sorter["columns"] == 2 and cell_width > 90.0 and cell_depth > 59.0, "Sorter resolves to six usable 2 x 3 cells.", {"cell_width_mm": cell_width, "cell_depth_mm": cell_depth, "cell_count": sorter["rows"] * sorter["columns"]}),
        check("assembly-envelope", all(close(a, b, 0.05) for a, b in zip(assembly_extents, [210.0, 190.0, 173.0])), "Assembled envelope remains 210 x 190 x 173 mm.", {"extents_mm": assembly_extents}),
    ]
    payload = {
        "schema_version": "1.0",
        "tool": "MM-ORG-003-interface-contract",
        "tool_version": "2.0.0",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}
            for path in (PARAMS, SOURCE, ASSEMBLY_REPORT)
        ],
        "checks": checks,
        "metrics": {
            "interface_policy": "nominal CAD clearances; validate coupons before full print",
            "drawer_side_clearance_each_mm": side_clearance,
            "stack_clearance_each_mm": stack_clearance_each,
            "sorter_cell_size_mm": [cell_width, cell_depth],
        },
        "limitations": [
            "Nominal CAD clearances do not replace printer/material-specific fit coupon results.",
            "Physical drawer cycling, stack retention and anti-tip behavior are deferred by the user.",
        ],
        "required_capabilities": [],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report": str(OUTPUT)}, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
