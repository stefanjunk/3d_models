#!/usr/bin/env python3
"""Parametric honeycomb wall-display cell built with CadQuery.

The model is deliberately split into:
- a printed display cell;
- a small keyhole-fit coupon;
- purchased wall-specific screws/anchors.

No safe wall load is claimed by this example.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq


def regular_hex(radius: float) -> list[tuple[float, float]]:
    """Flat-top regular hexagon, counter-clockwise."""
    return [
        (radius * math.cos(math.radians(60 * i)), radius * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]


def keyhole_cutter(
    x: float,
    y: float,
    z_start: float,
    cut_depth: float,
    head_diameter: float,
    neck_width: float,
    slot_length: float,
) -> cq.Workplane:
    """Large lower entry plus narrow upward slot for a screw head."""
    head = (
        cq.Workplane("XY")
        .center(x, y)
        .circle(head_diameter / 2)
        .extrude(cut_depth)
        .translate((0, 0, z_start))
    )
    slot = (
        cq.Workplane("XY")
        .box(neck_width, slot_length, cut_depth, centered=(True, False, False))
        .translate((x, y, z_start))
    )
    top = (
        cq.Workplane("XY")
        .center(x, y + slot_length)
        .circle(neck_width / 2)
        .extrude(cut_depth)
        .translate((0, 0, z_start))
    )
    return head.union(slot).union(top)


def build_cell(params: dict[str, float]) -> cq.Workplane:
    radius = params["outer_radius"]
    depth = params["depth"]
    wall = params["wall"]
    back = params["back"]
    front_edge_radius = params["front_edge_radius"]

    # Reduce circumradius so the apothem difference equals the requested wall.
    inner_radius = radius - wall / math.cos(math.radians(30))
    if inner_radius <= 0:
        raise ValueError("wall is too large for outer_radius")
    if back <= 0 or back >= depth:
        raise ValueError("back must be positive and smaller than depth")

    outer = cq.Workplane("XY").polyline(regular_hex(radius)).close().extrude(depth)
    inner = (
        cq.Workplane("XY")
        .polyline(regular_hex(inner_radius))
        .close()
        .extrude(depth - back + 0.5)
        .translate((0, 0, back))
    )
    cell = outer.cut(inner)

    # Round only the front perimeter where it improves handling and appearance.
    try:
        cell = cell.edges(">Z").fillet(front_edge_radius)
    except Exception:
        # Keep the base geometry valid across CadQuery/OCC versions.
        pass

    # Two keyholes are placed in the upper half of the back panel.
    keyhole_y = radius * 0.34
    keyhole_x = radius * 0.38
    for x in (-keyhole_x, keyhole_x):
        cutter = keyhole_cutter(
            x=x,
            y=keyhole_y,
            z_start=-0.5,
            cut_depth=back + 1.0,
            head_diameter=params["screw_head_clearance"],
            neck_width=params["screw_neck_clearance"],
            slot_length=params["keyhole_slot_length"],
        )
        cell = cell.cut(cutter)

    # Optional local pads spread screw-head bearing into the back panel.
    pad_w = params["mount_pad_width"]
    pad_h = params["mount_pad_height"]
    pad_t = params["mount_pad_extra"]
    for x in (-keyhole_x, keyhole_x):
        pad = (
            cq.Workplane("XY")
            .center(x, keyhole_y + params["keyhole_slot_length"] / 2)
            .rect(pad_w, pad_h)
            .extrude(pad_t)
            .translate((0, 0, back))
        )
        cell = cell.union(pad)

    return cell


def build_keyhole_coupon(params: dict[str, float]) -> cq.Workplane:
    width, height = 44.0, 55.0
    thickness = params["back"] + params["mount_pad_extra"]
    plate = cq.Workplane("XY").box(width, height, thickness, centered=(True, True, False))
    cutter = keyhole_cutter(
        x=0,
        y=-8,
        z_start=-0.5,
        cut_depth=thickness + 1.0,
        head_diameter=params["screw_head_clearance"],
        neck_width=params["screw_neck_clearance"],
        slot_length=params["keyhole_slot_length"],
    )
    return plate.cut(cutter)


def export_shape(shape: cq.Workplane, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".step":
        cq.exporters.export(shape, str(path), exportType="STEP")
    elif suffix == ".stl":
        cq.exporters.export(shape, str(path), exportType="STL", tolerance=0.08, angularTolerance=0.12)
    else:
        raise ValueError(f"unsupported export: {path}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("generated"))
    p.add_argument("--outer-radius", type=float, default=84.0)
    p.add_argument("--depth", type=float, default=72.0)
    p.add_argument("--wall", type=float, default=8.0)
    p.add_argument("--back", type=float, default=4.8)
    p.add_argument("--front-edge-radius", type=float, default=2.0)
    p.add_argument("--screw-head-clearance", type=float, default=10.8)
    p.add_argument("--screw-neck-clearance", type=float, default=4.8)
    p.add_argument("--keyhole-slot-length", type=float, default=14.0)
    p.add_argument("--mount-pad-width", type=float, default=24.0)
    p.add_argument("--mount-pad-height", type=float, default=34.0)
    p.add_argument("--mount-pad-extra", type=float, default=1.8)
    args = p.parse_args()

    params = {
        "outer_radius": args.outer_radius,
        "depth": args.depth,
        "wall": args.wall,
        "back": args.back,
        "front_edge_radius": args.front_edge_radius,
        "screw_head_clearance": args.screw_head_clearance,
        "screw_neck_clearance": args.screw_neck_clearance,
        "keyhole_slot_length": args.keyhole_slot_length,
        "mount_pad_width": args.mount_pad_width,
        "mount_pad_height": args.mount_pad_height,
        "mount_pad_extra": args.mount_pad_extra,
    }

    cell = build_cell(params)
    coupon = build_keyhole_coupon(params)
    out = args.out
    export_shape(cell, out / "honeycomb-wall-shelf.step")
    export_shape(cell, out / "honeycomb-wall-shelf.stl")
    export_shape(coupon, out / "keyhole-fit-coupon.step")
    export_shape(coupon, out / "keyhole-fit-coupon.stl")

    bb = cell.val().BoundingBox()
    report = {
        "parameters": params,
        "cell_bounds_mm": [bb.xlen, bb.ylen, bb.zlen],
        "cell_volume_mm3": cell.val().Volume(),
        "warning": "No load rating. Match certified anchors/screws to the actual wall and proof-test the installation.",
    }
    (out / "build-metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
