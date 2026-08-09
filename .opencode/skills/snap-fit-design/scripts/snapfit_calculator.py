#!/usr/bin/env python3
"""First-pass cantilever snap-fit strain screen."""

from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--material", required=True)
    parser.add_argument("--length", type=float, required=True)
    parser.add_argument("--root-thickness", type=float, required=True)
    parser.add_argument("--tip-thickness", type=float, required=True)
    parser.add_argument("--width", type=float, required=True)
    parser.add_argument("--deflection", type=float, required=True)
    parser.add_argument("--root-radius", type=float, required=True)
    parser.add_argument("--cycles", type=int, required=True)
    parser.add_argument("--allowable-strain", type=float, required=True)
    args = parser.parse_args()

    values = (
        args.length,
        args.root_thickness,
        args.tip_thickness,
        args.width,
        args.deflection,
        args.root_radius,
    )
    if any(value <= 0 for value in values) or args.cycles < 1 or args.allowable_strain <= 0:
        parser.error("dimensions must be positive and cycles must be at least one")

    blockers: list[str] = []
    if args.tip_thickness > args.root_thickness:
        blockers.append("tip thickness exceeds root thickness; taper direction is unfavorable")
    if args.root_radius < 0.5 * args.root_thickness:
        blockers.append("root radius is below 0.5 times root thickness")
    if args.width < 5.0:
        blockers.append("beam width is below the conservative 5 mm starting point")

    strain = 1.5 * args.deflection * args.root_thickness / args.length**2
    if strain > args.allowable_strain:
        blockers.append("predicted strain exceeds declared allowable strain")
    status = "REDESIGN_REQUIRED" if blockers else "COUPON_REQUIRED"
    report = {
        "status": status,
        "material": args.material,
        "predicted_root_strain": round(strain, 6),
        "predicted_root_strain_percent": round(100.0 * strain, 4),
        "cycles": args.cycles,
        "declared_allowable_strain": args.allowable_strain,
        "strain_utilization": round(strain / args.allowable_strain, 4),
        "blockers": blockers,
        "required_tests": ["assembly_force", "retention_force", "permanent_set", "creep", "cycle_life"],
        "limitations": [
            "simplified rectangular cantilever equation",
            "does not include printed anisotropy or process defects",
            "allowable strain must come from an authoritative material/process basis",
            "does not establish fatigue life or safety factor",
        ],
    }
    print(json.dumps(report, indent=2))
    return 2 if blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
