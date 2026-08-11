#!/usr/bin/env python3
"""Generate a calibration checklist for a material/nozzle/design feature set."""
from __future__ import annotations

import argparse
import json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--material", default="petg")
    p.add_argument("--nozzle", type=float, default=0.6)
    p.add_argument("--features", nargs="*", default=["fits", "bridges", "walls"])
    args = p.parse_args()
    tasks = []
    mapping = {
        "fits": "Print hole/shaft and slot/tab ladder in final orientation; measure after cooling.",
        "bridges": "Print increasing bridge spans with final cooling/speed; record first unacceptable span.",
        "walls": "Print 1–5 line wall coupon; measure line width and bonding.",
        "snap-fit": "Print length/thickness/root-radius matrix and cycle to target count.",
        "insert": "Print boss/insert-hole matrix and test installation plus pull-out/torque.",
        "engraving": "Print depth/line-width tile at intended orientation and inspect readability.",
        "adhesive": "Print substrate strips; test surface prep and peel/shear after conditioning.",
        "overhang": "Print 30–70 degree overhang coupon using final cooling/material condition.",
    }
    for feature in args.features:
        tasks.append({"feature": feature, "task": mapping.get(feature, "Define a focused coupon and measurable pass/fail criterion.")})
    print(json.dumps({
        "material": args.material,
        "nozzle_mm": args.nozzle,
        "tasks": tasks,
        "record": ["printer", "slicer/profile hash", "filament product/batch/drying", "orientation", "layer/line width", "measurements", "photos", "pass/fail"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
