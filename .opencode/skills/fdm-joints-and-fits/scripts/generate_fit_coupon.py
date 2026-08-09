#!/usr/bin/env python3
"""Generate an original CadQuery bore-ladder coupon for process calibration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq


def parse_offsets(raw: str) -> list[float]:
    offsets = [float(value.strip()) for value in raw.split(",") if value.strip()]
    if len(offsets) < 3:
        raise ValueError("provide at least three offsets")
    if offsets != sorted(set(offsets)):
        raise ValueError("offsets must be unique and ascending")
    return offsets


def build_coupon(nominal: float, offsets: list[float]) -> cq.Workplane:
    hole_diameters = [nominal + offset for offset in offsets]
    if any(diameter <= 0 for diameter in hole_diameters):
        raise ValueError("all resulting hole diameters must be positive")
    pitch = max(12.0, nominal + 6.0)
    length = pitch * len(hole_diameters)
    width = max(18.0, nominal + 10.0)
    height = 8.0
    coupon = cq.Workplane("XY").box(length, width, height, centered=(True, True, False))
    x_start = -0.5 * pitch * (len(hole_diameters) - 1)
    for index, diameter in enumerate(hole_diameters):
        x = x_start + index * pitch
        cutter = cq.Workplane("XY").center(x, 0).circle(diameter / 2.0).extrude(height)
        coupon = coupon.cut(cutter)
    return coupon


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nominal", type=float, required=True)
    parser.add_argument("--offsets", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    if args.nominal <= 0:
        parser.error("nominal must be positive")
    try:
        offsets = parse_offsets(args.offsets)
        coupon = build_coupon(args.nominal, offsets)
    except ValueError as error:
        parser.error(str(error))

    output = Path(args.output)
    report_path = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(coupon, str(output))
    hole_diameters = [round(args.nominal + offset, 6) for offset in offsets]
    report = {
        "status": "COUPON_GENERATED",
        "nominal_mm": args.nominal,
        "offsets_mm": offsets,
        "hole_diameters_mm": hole_diameters,
        "required_measurements": [
            "printed_hole_diameter",
            "mating_part_diameter",
            "insertion_force",
            "retention_or_removal_force",
            "damage_and_relaxation",
        ],
        "limitations": "Compensation applies only to the tested process combination.",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
