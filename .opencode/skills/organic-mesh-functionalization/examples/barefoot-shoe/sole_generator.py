#!/usr/bin/env python3
"""Generate a simple parameterized zero-drop barefoot sole and removal cutter."""
from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq


def footprint_points(length: float, heel: float, waist: float, ball: float, toe: float):
    # Left sole: positive X is medial/great-toe side.
    stations = [
        (0.03, heel * 0.70, 0.00),
        (0.12, heel, 0.00),
        (0.34, waist, -0.03 * waist),
        (0.68, ball, 0.00),
        (0.84, toe, 0.03 * toe),
        (0.96, toe * 0.70, 0.06 * toe),
    ]
    right = [(shift + width / 2, y * length) for y, width, shift in stations]
    left = [(shift - width / 2, y * length) for y, width, shift in reversed(stations)]
    return right + left


def build(out: Path) -> None:
    length = 270.0
    heel_width = 68.0
    waist_width = 72.0
    ball_width = 104.0
    toe_width = 110.0
    sole_thickness = 5.0
    points = footprint_points(length, heel_width, waist_width, ball_width, toe_width)

    sole = cq.Workplane("XY").polyline(points).close().extrude(sole_thickness)
    # Gentle edge round. Leave failure visible if parameters make it impossible.
    sole = sole.edges("|Z").fillet(2.0)

    # Broad removal cutter: actual curved sole/upper interface should be authored in Blender.
    upper_cutter = cq.Workplane("XY").box(toe_width + 35, length + 30, 90).translate((0, length / 2, sole_thickness + 45))

    out.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(sole, str(out / "replacement-sole.step"))
    cq.exporters.export(sole, str(out / "replacement-sole.stl"), tolerance=0.08, angularTolerance=0.12)
    cq.exporters.export(upper_cutter, str(out / "upper-removal-envelope.step"))
    cq.exporters.export(upper_cutter, str(out / "upper-removal-envelope.stl"), tolerance=0.10, angularTolerance=0.15)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("generated"))
    args = parser.parse_args()
    build(args.out)
