"""Deterministic declared-envelope and trim sweep for parametric.3."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import component_parameters as P

GEOMETRY_REPORT = ROOT / "validation" / f"v{P.CANDIDATE}" / "geometry-validation.json"
OUT = ROOT / "validation" / f"v{P.CANDIDATE}" / "parameter-sweep.json"


def record(path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }


def main() -> int:
    geometry = json.loads(GEOMETRY_REPORT.read_text(encoding="utf-8"))
    no_trim = geometry["mass_properties_without_trim"]
    base_mass = float(no_trim["total_mass_g"])
    base_com = [float(value) for value in no_trim["center_of_mass_mm"]]
    base_moments = [base_mass * value for value in base_com]

    wheel_cases = []
    for width, supported in ((42.0, True), (44.0, True), (46.0, False)):
        overall = P.WHEEL_TRACK_MM + width
        clearance = P.WHEEL_CENTER_Y_MM - width / 2.0 - P.MOTOR_POD_OUTER_Y_MM
        passed = overall <= P.OVERALL_WIDTH_MAX_MM and clearance >= 5.0
        wheel_cases.append(
            {
                "tire_width_mm": width,
                "supported": supported,
                "overall_width_mm": overall,
                "wheel_to_printed_clearance_mm": clearance,
                "status": "PASS" if passed else "OUT_OF_CONTRACT",
            }
        )

    battery_cases = []
    for growth in (0.0, 1.0, 2.0):
        size = [value + growth for value in P.BATTERY_SIZE_MM_PROVISIONAL]
        clearances = [
            (inner - actual) / 2.0
            for inner, actual in zip(P.BATTERY_INNER_MM, size)
        ]
        supported = growth <= 1.0
        passed = min(clearances) >= 0.5
        battery_cases.append(
            {
                "overall_growth_each_dimension_mm": growth,
                "size_mm": size,
                "supported": supported,
                "clearance_each_side_mm": clearances,
                "status": "PASS" if passed else "OUT_OF_CONTRACT",
            }
        )

    ballast_cases = []
    for ballast in (100.0, 120.0, 180.0):
        total = base_mass + ballast
        com = [
            (base_moments[index] + ballast * value) / total
            for index, value in enumerate((0.0, 0.0, 181.0))
        ]
        passed = total <= 2200.0 and 70.0 <= com[2] <= 110.0
        ballast_cases.append(
            {
                "ballast_g": ballast,
                "total_mass_g": total,
                "center_of_mass_mm": com,
                "status": "PASS" if passed else "FAIL",
            }
        )

    supported_pass = (
        all(case["status"] == "PASS" for case in wheel_cases if case["supported"])
        and all(case["status"] == "PASS" for case in battery_cases if case["supported"])
        and all(case["status"] == "PASS" for case in ballast_cases)
    )
    report = {
        "schema_version": "1.0",
        "tool": "MM-TOY-003 component contract sweep",
        "tool_version": "0.1.0",
        "candidate": P.CANDIDATE,
        "status": "PASS" if supported_pass else "FAIL",
        "inputs": [record(Path(__file__).resolve()), record(HERE / "component_parameters.py"), record(GEOMETRY_REPORT)],
        "supported_ranges": {
            "tire_width_mm": [42.0, 44.0],
            "battery_overall_growth_each_dimension_mm": [0.0, 1.0],
            "calculation_ballast_g": [100.0, 180.0],
        },
        "wheel_cases": wheel_cases,
        "battery_cases": battery_cases,
        "ballast_cases": ballast_cases,
        "boundary_findings": [
            "A 46 mm tire width exceeds both the 260 mm overall-width contract and 5 mm printed clearance; it is intentionally outside the supported range.",
            "Battery growth above 1 mm per complete dimension leaves less than the 0.5 mm coupon starting clearance.",
            "Metal-bracket-to-tire clearance is not accepted by this sweep because rim hex depth, sidewall overhang and the delivered bracket stack remain unmeasured.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "wheel_cases": wheel_cases, "battery_cases": battery_cases, "ballast_cases": ballast_cases}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
