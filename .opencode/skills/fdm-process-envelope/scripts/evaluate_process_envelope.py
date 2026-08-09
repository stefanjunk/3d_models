#!/usr/bin/env python3
"""Conservative generic FDM geometry-screen for commercial model claims."""

from __future__ import annotations

import argparse
import json


MATERIALS = {"PLA", "PETG", "ABS", "ASA", "TPU", "PA-CF"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nozzle", type=float, choices=(0.4, 0.6, 0.8), required=True)
    parser.add_argument("--material", choices=sorted(MATERIALS), required=True)
    parser.add_argument("--min-wall", type=float, required=True)
    parser.add_argument("--min-feature", type=float, required=True)
    parser.add_argument("--press-fit", action="store_true")
    parser.add_argument("--snap-fit", action="store_true")
    parser.add_argument("--flexure", action="store_true")
    parser.add_argument("--gear", action="store_true")
    parser.add_argument("--seal", action="store_true")
    args = parser.parse_args()

    if args.min_wall <= 0 or args.min_feature <= 0:
        parser.error("minimum dimensions must be positive")

    blockers: list[str] = []
    concerns: list[str] = []
    requirements: list[str] = []
    coupons: list[str] = []
    wall_multiple = args.min_wall / args.nozzle
    feature_multiple = args.min_feature / args.nozzle

    if wall_multiple < 2.0:
        blockers.append("minimum wall is below the conservative two-nozzle screen")
    elif wall_multiple < 3.0:
        concerns.append("minimum wall passes only the robust baseline, not the preferred three-nozzle target")
    if feature_multiple < 1.0:
        blockers.append("minimum open feature is narrower than the nozzle")

    for enabled, name in (
        (args.press_fit, "press_fit"),
        (args.snap_fit, "snap_fit"),
        (args.flexure, "flexure"),
        (args.gear, "gear"),
        (args.seal, "seal"),
    ):
        if enabled:
            coupons.append(name)

    if args.material in {"ABS", "ASA"}:
        requirements.extend(["enclosed_or_warp_controlled_process", "ventilation_review"])
    elif args.material == "TPU":
        requirements.extend(["declared_shore_hardness", "flexible_filament_process_qualification"])
    elif args.material == "PA-CF":
        requirements.extend(["hardened_nozzle", "filament_drying", "abrasive_material_process_qualification"])

    if blockers:
        status, code = "UNSUPPORTED", 2
    elif concerns or requirements or coupons:
        status, code = "CONDITIONAL", 1
    else:
        status, code = "SUPPORTED", 0

    report = {
        "status": status,
        "nozzle_mm": args.nozzle,
        "material": args.material,
        "wall_nozzle_multiple": round(wall_multiple, 3),
        "feature_nozzle_multiple": round(feature_multiple, 3),
        "blockers": blockers,
        "concerns": concerns,
        "requirements": requirements,
        "required_coupons": coupons,
        "scope": "generic geometry screen; customer printer and slicer remain unqualified",
    }
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
