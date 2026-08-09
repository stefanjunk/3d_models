#!/usr/bin/env python3
"""Generate a rounded compartment cavity, window cutter, and separate door."""
from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq


def rounded_box(x: float, y: float, z: float, r: float):
    return cq.Workplane("XY").box(x, y, z).edges("|Z").fillet(r)


def export(obj, path: Path, tol: float = 0.08) -> None:
    cq.exporters.export(obj, str(path.with_suffix(".step")))
    cq.exporters.export(obj, str(path.with_suffix(".stl")), tolerance=tol, angularTolerance=0.12)


def build(out: Path) -> None:
    cavity_w, cavity_l, cavity_d = 52.0, 60.0, 28.0
    corner = 7.0
    door_gap = 0.35
    door_t = 2.4
    rim = 3.0

    cavity = rounded_box(cavity_w, cavity_l, cavity_d, corner)
    window = rounded_box(cavity_w - 8, cavity_l - 10, cavity_d + 20, corner - 2)
    outer = rounded_box(cavity_w - 8 - 2 * door_gap, cavity_l - 10 - 2 * door_gap, door_t, corner - 2)
    inner_rebate = rounded_box(cavity_w - 8 - 2 * (door_gap + rim), cavity_l - 10 - 2 * (door_gap + rim), 1.0, max(1.0, corner - 4)).translate((0, 0, -1.2))
    door = outer.union(inner_rebate)

    out.mkdir(parents=True, exist_ok=True)
    export(cavity, out / "cavity-cutter")
    export(window, out / "window-cutter")
    export(door, out / "door")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("generated"))
    args = parser.parse_args()
    build(args.out)
