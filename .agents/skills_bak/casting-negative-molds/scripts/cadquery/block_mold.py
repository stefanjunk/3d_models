#!/usr/bin/env python3
"""Generate a two-part parametric block mold around a STEP solid or demo master.

This is a baseline generator, not an automatic demolding solver. The default
split is planar and must be replaced when the article has undercuts.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Iterable

import cadquery as cq


def bbox_dict(shape: cq.Shape) -> dict[str, float]:
    b = shape.BoundingBox()
    return {
        "xmin": b.xmin, "xmax": b.xmax, "xlen": b.xlen,
        "ymin": b.ymin, "ymax": b.ymax, "ylen": b.ylen,
        "zmin": b.zmin, "zmax": b.zmax, "zlen": b.zlen,
    }


def is_valid(shape: cq.Shape) -> bool:
    try:
        return bool(shape.isValid())
    except Exception:
        return not shape.isNull()


def union_shapes(shapes: Iterable[cq.Shape]) -> cq.Shape:
    values = list(shapes)
    if not values:
        raise ValueError("No solids were supplied.")
    result = values[0]
    for shape in values[1:]:
        result = result.fuse(shape)
    try:
        return result.clean()
    except Exception:
        return result


def load_step(path: Path) -> cq.Shape:
    wp = cq.importers.importStep(str(path))
    values = [shape for shape in wp.vals() if isinstance(shape, cq.Shape) and not shape.isNull()]
    if not values:
        raise ValueError("STEP import produced no usable shapes.")
    return union_shapes(values)


def demo_master(name: str, height: float) -> cq.Shape:
    if height <= 0:
        raise ValueError("Demo height must be positive.")

    if name == "roman-pillar":
        shaft_h = height * 0.64
        base_h = height * 0.18
        cap_h = height - shaft_h - base_h
        shaft_r = height * 0.095
        base_r = height * 0.15
        cap_r = height * 0.145
        base = cq.Solid.makeCylinder(base_r, base_h)
        base_ring = cq.Solid.makeCylinder(base_r * 1.08, base_h * 0.20, (0, 0, base_h * 0.80))
        shaft = cq.Solid.makeCone(shaft_r * 1.03, shaft_r * 0.94, shaft_h, (0, 0, base_h))
        neck = cq.Solid.makeCylinder(shaft_r * 1.08, cap_h * 0.16, (0, 0, base_h + shaft_h))
        capital = cq.Solid.makeCone(cap_r * 0.82, cap_r, cap_h * 0.62, (0, 0, base_h + shaft_h + cap_h * 0.12))
        abacus = cq.Workplane("XY").box(cap_r * 2.1, cap_r * 2.1, cap_h * 0.26, centered=(True, True, False)).translate((0, 0, height - cap_h * 0.26)).val()
        return union_shapes([base, base_ring, shaft, neck, capital, abacus])

    if name == "tile":
        side = height * 4.0
        thickness = max(4.0, height * 0.20)
        plate = cq.Workplane("XY").box(side, side, thickness, centered=(True, True, False)).val()
        center = cq.Solid.makeCylinder(side * 0.13, thickness * 0.35, (0, 0, thickness))
        petals: list[cq.Shape] = []
        for angle in range(0, 360, 30):
            petal = cq.Workplane("XY").ellipse(side * 0.18, side * 0.055).extrude(thickness * 0.22).translate((side * 0.19, 0, thickness)).val()
            petal = petal.rotate((0, 0, 0), (0, 0, 1), angle)
            petals.append(petal)
        return union_shapes([plate, center, *petals])

    if name == "bowl":
        bowl_h = height
        bottom_r = bowl_h * 0.38
        top_r = bowl_h * 0.78
        body = cq.Solid.makeCone(bottom_r, top_r, bowl_h * 0.88)
        foot = cq.Solid.makeCylinder(bottom_r * 0.72, bowl_h * 0.12, (0, 0, -bowl_h * 0.12))
        rim = cq.Solid.makeCylinder(top_r * 1.025, bowl_h * 0.06, (0, 0, bowl_h * 0.84))
        return union_shapes([body, foot, rim])

    if name == "rounded-box":
        x, y, z = height * 0.7, height * 0.5, height
        wp = cq.Workplane("XY").box(x, y, z)
        try:
            wp = wp.edges().fillet(min(x, y) * 0.08)
        except Exception:
            pass
        return wp.val()

    raise ValueError(f"Unknown demo master: {name}")


def center_and_scale(shape: cq.Shape, factors: tuple[float, float, float]) -> cq.Shape:
    if any(f <= 0 for f in factors):
        raise ValueError("Scale factors must be positive.")
    b = shape.BoundingBox()
    center = ((b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0, (b.zmin + b.zmax) / 2.0)
    centered = shape.translate(tuple(-v for v in center))
    matrix = cq.Matrix([
        [factors[0], 0.0, 0.0, 0.0],
        [0.0, factors[1], 0.0, 0.0],
        [0.0, 0.0, factors[2], 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ])
    return centered.transformGeometry(matrix)


def oversize_factors(shrink_pct: tuple[float, float, float]) -> tuple[float, float, float]:
    if any(s >= 100.0 for s in shrink_pct):
        raise ValueError("Shrinkage must be below 100 percent.")
    return tuple(1.0 / (1.0 - s / 100.0) for s in shrink_pct)


def make_block(master: cq.Shape, side: float, bottom: float, top: float) -> tuple[cq.Shape, dict[str, float]]:
    if min(side, bottom, top) <= 0:
        raise ValueError("Margins must be positive.")
    b = master.BoundingBox()
    dims = {
        "x": b.xlen + 2 * side,
        "y": b.ylen + 2 * side,
        "z": b.zlen + bottom + top,
        "zmin": b.zmin - bottom,
        "zmax": b.zmax + top,
    }
    block = cq.Solid.makeBox(dims["x"], dims["y"], dims["z"], (-dims["x"] / 2, -dims["y"] / 2, dims["zmin"]))
    return block, dims


def make_vertical_channel(master: cq.Shape, block_dims: dict[str, float], xy: tuple[float, float], bottom_radius: float, top_radius: float) -> cq.Shape:
    b = master.BoundingBox()
    start_z = b.zmax - min(1.0, max(0.2, b.zlen * 0.01))
    height = block_dims["zmax"] - start_z + 1.0
    if bottom_radius <= 0 or top_radius <= 0:
        raise ValueError("Channel radii must be positive.")
    return cq.Solid.makeCone(bottom_radius, top_radius, height, (xy[0], xy[1], start_z), (0, 0, 1))


def split_shape(shape: cq.Shape, dims: dict[str, float], axis: str) -> tuple[cq.Shape, cq.Shape]:
    pad = 2.0
    if axis == "X":
        clip_a = cq.Solid.makeBox(dims["x"] / 2 + pad, dims["y"] + 2 * pad, dims["z"] + 2 * pad,
                                  (-dims["x"] / 2 - pad, -dims["y"] / 2 - pad, dims["zmin"] - pad))
        clip_b = cq.Solid.makeBox(dims["x"] / 2 + pad, dims["y"] + 2 * pad, dims["z"] + 2 * pad,
                                  (0, -dims["y"] / 2 - pad, dims["zmin"] - pad))
    elif axis == "Y":
        clip_a = cq.Solid.makeBox(dims["x"] + 2 * pad, dims["y"] / 2 + pad, dims["z"] + 2 * pad,
                                  (-dims["x"] / 2 - pad, -dims["y"] / 2 - pad, dims["zmin"] - pad))
        clip_b = cq.Solid.makeBox(dims["x"] + 2 * pad, dims["y"] / 2 + pad, dims["z"] + 2 * pad,
                                  (-dims["x"] / 2 - pad, 0, dims["zmin"] - pad))
    else:
        raise ValueError("Only X and Y planar splits are implemented.")
    return shape.intersect(clip_a), shape.intersect(clip_b)


def key_positions(master: cq.Shape, dims: dict[str, float], axis: str, side_margin: float, radius: float) -> list[tuple[float, float, float]]:
    b = master.BoundingBox()
    z_low = max(dims["zmin"] + radius * 1.5, b.zmin + b.zlen * 0.20)
    z_high = min(dims["zmax"] - radius * 1.5, b.zmax - b.zlen * 0.20)
    if z_high <= z_low:
        z_low = dims["zmin"] + dims["z"] * 0.30
        z_high = dims["zmin"] + dims["z"] * 0.70

    offset = (b.ylen / 2 + side_margin * 0.55) if axis == "X" else (b.xlen / 2 + side_margin * 0.55)
    if axis == "X":
        return [(0.0, -offset, z_low), (0.0, offset, z_low), (0.0, -offset, z_high), (0.0, offset * 0.72, z_high)]
    return [(-offset, 0.0, z_low), (offset, 0.0, z_low), (-offset, 0.0, z_high), (offset * 0.72, 0.0, z_high)]


def add_keys(a: cq.Shape, b: cq.Shape, master: cq.Shape, dims: dict[str, float], axis: str,
             side_margin: float, radius: float, depth: float, clearance: float) -> tuple[cq.Shape, cq.Shape, list[list[float]]]:
    max_radius = side_margin * 0.30
    r = min(radius, max_radius)
    if r <= 0.5:
        raise ValueError("Side margin is too small for registration keys.")
    if depth <= 0 or clearance < 0:
        raise ValueError("Key depth must be positive and clearance non-negative.")
    positions = key_positions(master, dims, axis, side_margin, r)
    direction = (1, 0, 0) if axis == "X" else (0, 1, 0)
    overlap = 0.25

    for p in positions:
        start = list(p)
        start[0 if axis == "X" else 1] = -overlap
        male = cq.Solid.makeCone(r, r * 0.82, depth + overlap, tuple(start), direction)
        socket = cq.Solid.makeCone(r + clearance, r * 0.82 + clearance,
                                   depth + 2 * overlap, tuple(start), direction)
        a = a.fuse(male)
        b = b.cut(socket)
    return a, b, [list(p) for p in positions]


def export_shape(shape: cq.Shape, path: Path, tolerance: float, angular_tolerance: float) -> None:
    if shape.isNull() or not is_valid(shape):
        raise ValueError(f"Refusing to export invalid/null shape: {path.name}")
    if path.suffix.lower() in {".step", ".stp"}:
        cq.exporters.export(shape, str(path), exportType="STEP")
    elif path.suffix.lower() == ".stl":
        cq.exporters.export(shape, str(path), exportType="STL", tolerance=tolerance, angularTolerance=angular_tolerance)
    else:
        raise ValueError(f"Unsupported export extension: {path.suffix}")


def parse_vent(value: str) -> tuple[float, float]:
    try:
        x, y = value.split(",", 1)
        return float(x), float(y)
    except Exception as exc:
        raise argparse.ArgumentTypeError("Vent must be X,Y in millimetres") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", type=Path, help="Input STEP solid")
    src.add_argument("--demo", choices=("roman-pillar", "tile", "bowl", "rounded-box"))
    parser.add_argument("--height", type=float, default=80.0, help="Primary size for demo geometry")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--shrink", nargs=3, type=float, default=(0.0, 0.0, 0.0), metavar=("X_PCT", "Y_PCT", "Z_PCT"))
    parser.add_argument("--side-margin", type=float, default=12.0)
    parser.add_argument("--bottom-margin", type=float, default=10.0)
    parser.add_argument("--top-margin", type=float, default=18.0)
    parser.add_argument("--split-axis", choices=("X", "Y"), default="X")
    parser.add_argument("--sprue", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--sprue-bottom-radius", type=float, default=4.0)
    parser.add_argument("--sprue-top-radius", type=float, default=10.0)
    parser.add_argument("--vent", type=parse_vent, action="append", default=[], help="Add vertical vent at X,Y; repeat option")
    parser.add_argument("--vent-radius", type=float, default=1.2)
    parser.add_argument("--key-radius", type=float, default=4.0)
    parser.add_argument("--key-depth", type=float, default=3.0)
    parser.add_argument("--key-clearance", type=float, default=0.25)
    parser.add_argument("--stl-tolerance", type=float, default=0.05)
    parser.add_argument("--angular-tolerance", type=float, default=0.12)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        out = args.output_dir.expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)

        if args.input:
            source_path = args.input.expanduser().resolve()
            if not source_path.is_file():
                raise FileNotFoundError(source_path)
            source = load_step(source_path)
            source_label = str(source_path)
        else:
            source = demo_master(args.demo, args.height)
            source_label = f"demo:{args.demo}"

        factors = oversize_factors(tuple(args.shrink))
        master = center_and_scale(source, factors)
        if not is_valid(master):
            raise ValueError("Scaled master is invalid.")

        block, dims = make_block(master, args.side_margin, args.bottom_margin, args.top_margin)
        complete = block.cut(master)
        channels: list[dict[str, object]] = []
        if args.sprue:
            sprue = make_vertical_channel(master, dims, (0.0, 0.0), args.sprue_bottom_radius, args.sprue_top_radius)
            complete = complete.cut(sprue)
            channels.append({"type": "sprue", "xy": [0.0, 0.0], "radii": [args.sprue_bottom_radius, args.sprue_top_radius]})
        for xy in args.vent:
            vent = make_vertical_channel(master, dims, xy, args.vent_radius, args.vent_radius)
            complete = complete.cut(vent)
            channels.append({"type": "vent", "xy": list(xy), "radius": args.vent_radius})

        mold_a, mold_b = split_shape(complete, dims, args.split_axis)
        mold_a, mold_b, positions = add_keys(
            mold_a, mold_b, master, dims, args.split_axis, args.side_margin,
            args.key_radius, args.key_depth, args.key_clearance
        )
        try:
            mold_a, mold_b = mold_a.clean(), mold_b.clean()
        except Exception:
            pass

        for shape, stem in ((master, "master_adjusted"), (mold_a, "mold_A"), (mold_b, "mold_B")):
            export_shape(shape, out / f"{stem}.step", args.stl_tolerance, args.angular_tolerance)
            export_shape(shape, out / f"{stem}.stl", args.stl_tolerance, args.angular_tolerance)

        manifest = {
            "generator": "scripts/cadquery/block_mold.py",
            "source": source_label,
            "units": "mm",
            "demo_height_mm": args.height if args.demo else None,
            "shrinkage_percent_xyz": list(args.shrink),
            "oversize_scale_xyz": list(factors),
            "master_bbox": bbox_dict(master),
            "block": dims,
            "split_axis": args.split_axis,
            "margins_mm": {"side": args.side_margin, "bottom": args.bottom_margin, "top": args.top_margin},
            "keys": {
                "positions": positions,
                "radius_mm": min(args.key_radius, args.side_margin * 0.30),
                "depth_mm": args.key_depth,
                "clearance_mm": args.key_clearance,
                "warning": "Calibrate clearance on the actual printer and finish."
            },
            "channels": channels,
            "outputs": ["master_adjusted.step", "master_adjusted.stl", "mold_A.step", "mold_A.stl", "mold_B.step", "mold_B.stl"],
            "warnings": [
                "Planar split does not prove demoldability; check undercuts and swept removal.",
                "Automatic vent coordinates only create channels; verify that each reaches a real air pocket and the exterior.",
                "For conventional ceramic slip casting, use this output as a master/case route to an absorbent plaster working mold unless a porous process is explicitly validated."
            ]
        }
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output_dir": str(out), "mold_A_bbox": bbox_dict(mold_a), "mold_B_bbox": bbox_dict(mold_b)}, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
