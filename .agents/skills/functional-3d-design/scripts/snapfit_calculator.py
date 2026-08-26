#!/usr/bin/env python3
"""Preliminary rectangular cantilever snap-fit calculation in N/mm/MPa."""
from __future__ import annotations

import argparse
import json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--length", type=float, required=True, help="Free cantilever length mm")
    p.add_argument("--width", type=float, required=True, help="Beam width mm")
    p.add_argument("--thickness", type=float, required=True, help="Root thickness mm")
    p.add_argument("--deflection", type=float, required=True, help="Required tip deflection mm")
    p.add_argument("--modulus", type=float, required=True, help="Effective printed modulus MPa = N/mm^2")
    p.add_argument("--allowable-strain", type=float, required=True, help="Allowable design strain percent for target cycles/orientation")
    p.add_argument("--nozzle", type=float, default=0.4)
    p.add_argument("--layer", type=float, default=0.2)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    for name in ["length", "width", "thickness", "deflection", "modulus", "allowable_strain", "nozzle", "layer"]:
        if getattr(args, name) <= 0:
            raise SystemExit(f"{name} must be positive")

    L, b, t, y, E = args.length, args.width, args.thickness, args.deflection, args.modulus
    strain = 1.5 * t * y / (L * L)
    stress = E * strain
    force = E * b * (t ** 3) * y / (4 * (L ** 3))
    allowable = args.allowable_strain / 100.0
    safety_factor = allowable / strain if strain > 0 else float("inf")

    result = {
        "model": "small-deflection rectangular cantilever baseline",
        "tip_force_n": round(force, 3),
        "root_stress_mpa": round(stress, 3),
        "root_strain_percent": round(strain * 100, 3),
        "strain_safety_factor": round(safety_factor, 3),
        "root_radius_start_mm": round(max(0.5 * t, 2 * args.layer, args.nozzle), 3),
        "taper_tip_thickness_start_mm": round(0.5 * t, 3),
        "print_rules": [
            "Orient layers so the snap arm does not primarily peel between layers.",
            "Add a generous root fillet and avoid a notch at the fixed end.",
            "Taper thickness or width and add a hard stop to limit over-deflection.",
            "Print a coupon in the final orientation and cycle it to the target count/environment.",
        ],
        "passed_preliminary_strain": safety_factor >= 1.0,
        "warning": "Not valid for large deflection, tapered-beam force, creep/fatigue, anisotropic fracture, or safety certification. Use measured printed properties and physical coupons.",
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0 if result["passed_preliminary_strain"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
