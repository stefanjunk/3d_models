#!/usr/bin/env python3
"""Calculate basic standard spur-gear pair dimensions and printability warnings."""
from __future__ import annotations

import argparse
import json
import math


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--module", type=float, required=True)
    p.add_argument("--teeth1", type=int, required=True)
    p.add_argument("--teeth2", type=int, required=True)
    p.add_argument("--pressure-angle", type=float, default=20.0)
    p.add_argument("--nozzle", type=float, default=0.4)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.module <= 0 or args.teeth1 < 5 or args.teeth2 < 5 or args.nozzle <= 0:
        raise SystemExit("module/nozzle must be positive and each tooth count at least 5")

    m, z1, z2 = args.module, args.teeth1, args.teeth2
    pitch1, pitch2 = m * z1, m * z2
    center = (pitch1 + pitch2) / 2
    circular_pitch = math.pi * m
    ratio = z2 / z1
    outside1, outside2 = m * (z1 + 2), m * (z2 + 2)
    root1, root2 = max(0, m * (z1 - 2.5)), max(0, m * (z2 - 2.5))
    module_ratio = m / args.nozzle

    warnings = []
    if module_ratio < 2:
        warnings.append("Module is below two nozzle diameters: fine teeth are high-risk for FDM durability and accuracy.")
    elif module_ratio < 3:
        warnings.append("Prototype range: print a gear-pair coupon and tune backlash/center distance.")
    else:
        warnings.append("Geometric resolution is a more robust starting range, but load/speed/wear still require engineering tests.")
    if min(z1, z2) < 17 and abs(args.pressure_angle - 20) < 1e-6:
        warnings.append("Low tooth count may require profile shift to avoid undercut; use a proper gear library/calculation.")

    result = {
        "module_mm": m,
        "pressure_angle_deg": args.pressure_angle,
        "teeth": [z1, z2],
        "ratio_driven_over_driver": round(ratio, 6),
        "pitch_diameters_mm": [round(pitch1, 4), round(pitch2, 4)],
        "outside_diameters_mm": [round(outside1, 4), round(outside2, 4)],
        "approx_root_diameters_mm": [round(root1, 4), round(root2, 4)],
        "standard_center_distance_mm": round(center, 4),
        "circular_pitch_mm": round(circular_pitch, 4),
        "module_to_nozzle_ratio": round(module_ratio, 3),
        "warnings": warnings,
        "libraries": ["cq_gears", "BOSL2 gears.scad", "FreeCAD Gears"],
        "note": "Backlash, face width, material, torque, speed, lubrication, shaft/bearing stiffness, and profile shift are not sized here.",
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
