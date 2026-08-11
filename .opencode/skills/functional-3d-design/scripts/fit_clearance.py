#!/usr/bin/env python3
"""Suggest a starting FDM fit clearance and coupon range."""
from __future__ import annotations

import argparse
import json

BASE_PER_SIDE = {
    "press": -0.03,
    "snug": 0.10,
    "slide": 0.20,
    "running": 0.30,
    "print-in-place": 0.35,
}

MATERIAL_ADJUST = {
    "pla": 0.00,
    "pla-plus": 0.00,
    "petg": 0.03,
    "abs": 0.05,
    "asa": 0.05,
    "pa6": 0.06,
    "pa12": 0.05,
    "copa": 0.05,
    "tpu-95a": 0.12,
    "tpu-soft": 0.20,
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--nominal", type=float, required=True, help="Nominal shaft/pin size mm")
    p.add_argument("--fit", choices=BASE_PER_SIDE, default="slide")
    p.add_argument("--nozzle", type=float, default=0.4)
    p.add_argument("--material", default="pla")
    p.add_argument("--measured-hole-error", type=float, default=0.0, help="Measured minus modeled hole diameter; negative means undersized")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.nominal <= 0 or args.nozzle <= 0:
        raise SystemExit("nominal and nozzle must be positive")

    scale = args.nozzle / 0.4
    per_side = BASE_PER_SIDE[args.fit] * scale + MATERIAL_ADJUST.get(args.material, 0.03)
    total_clearance = 2 * per_side
    # If holes print undersized (negative error), subtracting the error increases the modeled hole.
    modeled_hole = args.nominal + total_clearance - args.measured_hole_error
    coupon_offsets = [round(per_side + delta, 3) for delta in (-0.10, -0.05, 0.0, 0.05, 0.10)]

    result = {
        "nominal_mm": args.nominal,
        "fit": args.fit,
        "starting_clearance_per_side_mm": round(per_side, 3),
        "starting_total_diametral_clearance_mm": round(total_clearance, 3),
        "modeled_hole_diameter_mm_if_shaft_is_nominal": round(modeled_hole, 3),
        "coupon_per_side_offsets_mm": coupon_offsets,
        "warning": "Starting values only. Horizontal/vertical holes, first layer, material, line width, speed, and printer calibration change the result. Print a coupon in the final orientation.",
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
