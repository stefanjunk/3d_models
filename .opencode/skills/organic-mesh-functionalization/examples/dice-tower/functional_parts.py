#!/usr/bin/env python3
"""Generate parametric dice-tower cutters and an alternating inclined baffle insert."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import cadquery as cq


def export(obj, stem: Path, mesh_tol: float = 0.08) -> None:
    cq.exporters.export(obj, str(stem.with_suffix(".step")))
    cq.exporters.export(obj, str(stem.with_suffix(".stl")), tolerance=mesh_tol, angularTolerance=0.12)


def build(out: Path) -> None:
    tower_height = 140.0
    core_radius = 33.0
    overshoot = 1.0
    die_size = 22.0
    path_clearance = 4.0

    core = cq.Workplane("XY").circle(core_radius).extrude(tower_height + 2 * overshoot).translate((0, 0, -overshoot))
    entry = cq.Workplane("XY").circle((die_size + path_clearance) / 2).extrude(12).translate((0, 0, tower_height - 4))
    exit_cut = (
        cq.Workplane("XZ")
        .rect(die_size + 2 * path_clearance, die_size + path_clearance)
        .extrude(core_radius + 14, both=True)
        .translate((0, -core_radius, 18))
    )

    baffle_count = 6
    baffle_width = 2 * core_radius - 8
    baffle_depth = core_radius * 1.25
    baffle_thickness = 2.4
    tilt_deg = 18.0
    z0 = 30.0
    dz = 16.0
    parts = []
    for i in range(baffle_count):
        slab = cq.Workplane("XY").box(baffle_width, baffle_depth, baffle_thickness)
        slab = slab.rotate((-50, 0, 0), (50, 0, 0), tilt_deg if i % 2 == 0 else -tilt_deg)
        slab = slab.rotate((0, 0, 0), (0, 0, 1), 0 if i % 2 == 0 else 180)
        slab = slab.translate((0, 0, z0 + i * dz))
        parts.append(slab)
    spine = cq.Workplane("XY").box(3.0, 3.0, dz * (baffle_count - 1) + 8).translate((core_radius - 5, 0, z0 + dz * (baffle_count - 1) / 2))
    insert = spine
    for slab in parts:
        insert = insert.union(slab)

    out.mkdir(parents=True, exist_ok=True)
    export(core, out / "core-cutter")
    export(entry, out / "entry-cutter")
    export(exit_cut, out / "exit-cutter")
    export(insert, out / "stair-insert")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("generated"))
    args = parser.parse_args()
    build(args.out)
