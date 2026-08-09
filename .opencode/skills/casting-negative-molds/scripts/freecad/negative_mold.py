#!/usr/bin/env python3
"""FreeCADCmd baseline for a two-part block negative mold.

Examples:
  FreeCADCmd negative_mold.py -- --input master.step --output-dir build
  FreeCADCmd negative_mold.py -- --demo roman-pillar --height 80 --output-dir build

The planar split is a starting point and does not solve undercuts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

import FreeCAD as App
import Part


def argv_after_separator() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]


def union_shapes(shapes: Iterable[Part.Shape]) -> Part.Shape:
    values = list(shapes)
    if not values:
        raise ValueError("No shapes to fuse.")
    result = values[0]
    for shape in values[1:]:
        result = result.fuse(shape)
    try:
        return result.removeSplitter()
    except Exception:
        return result


def load_shape(path: Path, mesh_tolerance: float) -> Part.Shape:
    ext = path.suffix.lower()
    if ext in {".step", ".stp"}:
        shape = Part.read(str(path))
    elif ext == ".stl":
        import Mesh
        mesh = Mesh.Mesh(str(path))
        shape = Part.Shape()
        shape.makeShapeFromMesh(mesh.Topology, mesh_tolerance)
        shells = []
        try:
            shells = shape.Shells
        except Exception:
            pass
        if len(shells) == 1:
            shape = Part.makeSolid(shells[0])
        elif shape.ShapeType == "Shell":
            shape = Part.makeSolid(shape)
        else:
            raise ValueError("Mesh-to-solid did not produce one closed shell; repair/decimate the mesh first.")
    else:
        raise ValueError("FreeCAD baseline accepts STEP/STP or STL.")
    if shape.isNull():
        raise ValueError("Import produced a null shape.")
    return shape


def demo_master(name: str, height: float) -> Part.Shape:
    if name == "roman-pillar":
        shaft_h, base_h = height * 0.64, height * 0.18
        cap_h = height - shaft_h - base_h
        shaft_r, base_r, cap_r = height * 0.095, height * 0.15, height * 0.145
        shapes = [
            Part.makeCylinder(base_r, base_h),
            Part.makeCylinder(base_r * 1.08, base_h * 0.20, App.Vector(0, 0, base_h * 0.80)),
            Part.makeCone(shaft_r * 1.03, shaft_r * 0.94, shaft_h, App.Vector(0, 0, base_h)),
            Part.makeCylinder(shaft_r * 1.08, cap_h * 0.16, App.Vector(0, 0, base_h + shaft_h)),
            Part.makeCone(cap_r * 0.82, cap_r, cap_h * 0.62, App.Vector(0, 0, base_h + shaft_h + cap_h * 0.12)),
            Part.makeBox(cap_r * 2.1, cap_r * 2.1, cap_h * 0.26,
                         App.Vector(-cap_r * 1.05, -cap_r * 1.05, height - cap_h * 0.26))
        ]
        return union_shapes(shapes)
    if name == "rounded-box":
        return Part.makeBox(height * 0.7, height * 0.5, height, App.Vector(-height * 0.35, -height * 0.25, -height * 0.5))
    if name == "bowl":
        bottom_r, top_r = height * 0.38, height * 0.78
        return union_shapes([
            Part.makeCone(bottom_r, top_r, height * 0.88),
            Part.makeCylinder(bottom_r * 0.72, height * 0.12, App.Vector(0, 0, -height * 0.12)),
            Part.makeCylinder(top_r * 1.025, height * 0.06, App.Vector(0, 0, height * 0.84))
        ])
    raise ValueError(f"Unknown demo: {name}")


def center_and_scale(shape: Part.Shape, shrink: tuple[float, float, float]) -> tuple[Part.Shape, tuple[float, float, float]]:
    if any(s >= 100 for s in shrink):
        raise ValueError("Shrinkage must be below 100 percent.")
    factors = tuple(1.0 / (1.0 - s / 100.0) for s in shrink)
    b = shape.BoundBox
    centered = shape.copy()
    centered.translate(App.Vector(-b.Center.x, -b.Center.y, -b.Center.z))
    matrix = App.Matrix()
    matrix.A11, matrix.A22, matrix.A33 = factors
    scaled = centered.transformGeometry(matrix)
    return scaled, factors


def bbox(shape: Part.Shape) -> dict[str, float]:
    b = shape.BoundBox
    return {"xmin": b.XMin, "xmax": b.XMax, "xlen": b.XLength,
            "ymin": b.YMin, "ymax": b.YMax, "ylen": b.YLength,
            "zmin": b.ZMin, "zmax": b.ZMax, "zlen": b.ZLength}


def make_block(master: Part.Shape, side: float, bottom: float, top: float) -> tuple[Part.Shape, dict[str, float]]:
    b = master.BoundBox
    dims = {"x": b.XLength + 2 * side, "y": b.YLength + 2 * side,
            "z": b.ZLength + bottom + top, "zmin": b.ZMin - bottom, "zmax": b.ZMax + top}
    block = Part.makeBox(dims["x"], dims["y"], dims["z"], App.Vector(-dims["x"] / 2, -dims["y"] / 2, dims["zmin"]))
    return block.cut(master), dims


def channel(master: Part.Shape, dims: dict[str, float], xy: tuple[float, float], r1: float, r2: float) -> Part.Shape:
    b = master.BoundBox
    start = b.ZMax - min(1.0, max(0.2, b.ZLength * 0.01))
    height = dims["zmax"] - start + 1.0
    if abs(r1 - r2) < 1e-9:
        return Part.makeCylinder(r1, height, App.Vector(xy[0], xy[1], start))
    return Part.makeCone(r1, r2, height, App.Vector(xy[0], xy[1], start))


def split_shape(shape: Part.Shape, dims: dict[str, float], axis: str) -> tuple[Part.Shape, Part.Shape]:
    pad = 2.0
    if axis == "X":
        clip_a = Part.makeBox(dims["x"] / 2 + pad, dims["y"] + 2 * pad, dims["z"] + 2 * pad,
                              App.Vector(-dims["x"] / 2 - pad, -dims["y"] / 2 - pad, dims["zmin"] - pad))
        clip_b = Part.makeBox(dims["x"] / 2 + pad, dims["y"] + 2 * pad, dims["z"] + 2 * pad,
                              App.Vector(0, -dims["y"] / 2 - pad, dims["zmin"] - pad))
    else:
        clip_a = Part.makeBox(dims["x"] + 2 * pad, dims["y"] / 2 + pad, dims["z"] + 2 * pad,
                              App.Vector(-dims["x"] / 2 - pad, -dims["y"] / 2 - pad, dims["zmin"] - pad))
        clip_b = Part.makeBox(dims["x"] + 2 * pad, dims["y"] / 2 + pad, dims["z"] + 2 * pad,
                              App.Vector(-dims["x"] / 2 - pad, 0, dims["zmin"] - pad))
    return shape.common(clip_a), shape.common(clip_b)


def add_keys(a: Part.Shape, b: Part.Shape, master: Part.Shape, dims: dict[str, float], axis: str,
             side: float, radius: float, depth: float, clearance: float) -> tuple[Part.Shape, Part.Shape, list[list[float]]]:
    mb = master.BoundBox
    r = min(radius, side * 0.30)
    z1 = max(dims["zmin"] + r * 1.6, mb.ZMin + mb.ZLength * 0.20)
    z2 = min(dims["zmax"] - r * 1.6, mb.ZMax - mb.ZLength * 0.20)
    offset = (mb.YLength / 2 + side * 0.55) if axis == "X" else (mb.XLength / 2 + side * 0.55)
    positions = ([[0, -offset, z1], [0, offset, z1], [0, -offset, z2], [0, offset * 0.72, z2]]
                 if axis == "X" else
                 [[-offset, 0, z1], [offset, 0, z1], [-offset, 0, z2], [offset * 0.72, 0, z2]])
    direction = App.Vector(1, 0, 0) if axis == "X" else App.Vector(0, 1, 0)
    overlap = 0.25
    for p in positions:
        start = App.Vector(*p)
        if axis == "X":
            start.x = -overlap
        else:
            start.y = -overlap
        male = Part.makeCone(r, r * 0.82, depth + overlap, start, direction)
        socket = Part.makeCone(r + clearance, r * 0.82 + clearance, depth + 2 * overlap, start, direction)
        a = a.fuse(male)
        b = b.cut(socket)
    return a, b, positions


def export_shape(shape: Part.Shape, path: Path, linear_deflection: float) -> None:
    if shape.isNull() or not shape.isValid():
        raise ValueError(f"Invalid/null shape: {path.name}")
    if path.suffix.lower() in {".step", ".stp"}:
        shape.exportStep(str(path))
    elif path.suffix.lower() == ".stl":
        shape.exportStl(str(path), linear_deflection)
    else:
        raise ValueError(f"Unsupported export extension: {path.suffix}")


def parse_vent(value: str) -> tuple[float, float]:
    try:
        x, y = value.split(",", 1)
        return float(x), float(y)
    except Exception as exc:
        raise argparse.ArgumentTypeError("Vent must be X,Y") from exc


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--demo", choices=("roman-pillar", "rounded-box", "bowl"))
    parser.add_argument("--height", type=float, default=80.0)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--mesh-tolerance", type=float, default=0.10)
    parser.add_argument("--shrink", nargs=3, type=float, default=(0.0, 0.0, 0.0))
    parser.add_argument("--side-margin", type=float, default=12.0)
    parser.add_argument("--bottom-margin", type=float, default=10.0)
    parser.add_argument("--top-margin", type=float, default=18.0)
    parser.add_argument("--split-axis", choices=("X", "Y"), default="X")
    parser.add_argument("--sprue", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--sprue-bottom-radius", type=float, default=4.0)
    parser.add_argument("--sprue-top-radius", type=float, default=10.0)
    parser.add_argument("--vent", type=parse_vent, action="append", default=[])
    parser.add_argument("--vent-radius", type=float, default=1.2)
    parser.add_argument("--key-radius", type=float, default=4.0)
    parser.add_argument("--key-depth", type=float, default=3.0)
    parser.add_argument("--key-clearance", type=float, default=0.25)
    parser.add_argument("--stl-deflection", type=float, default=0.05)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(argv_after_separator())
    try:
        out = args.output_dir.expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        if args.input:
            source_path = args.input.expanduser().resolve()
            if not source_path.is_file():
                raise FileNotFoundError(source_path)
            source = load_shape(source_path, args.mesh_tolerance)
            source_label = str(source_path)
        else:
            source = demo_master(args.demo, args.height)
            source_label = f"demo:{args.demo}"
        master, factors = center_and_scale(source, tuple(args.shrink))
        complete, dims = make_block(master, args.side_margin, args.bottom_margin, args.top_margin)
        channels = []
        if args.sprue:
            complete = complete.cut(channel(master, dims, (0, 0), args.sprue_bottom_radius, args.sprue_top_radius))
            channels.append({"type": "sprue", "xy": [0, 0]})
        for xy in args.vent:
            complete = complete.cut(channel(master, dims, xy, args.vent_radius, args.vent_radius))
            channels.append({"type": "vent", "xy": list(xy)})
        a, b = split_shape(complete, dims, args.split_axis)
        a, b, positions = add_keys(a, b, master, dims, args.split_axis, args.side_margin,
                                   args.key_radius, args.key_depth, args.key_clearance)
        for shape, stem in ((master, "master_adjusted"), (a, "mold_A"), (b, "mold_B")):
            export_shape(shape, out / f"{stem}.step", args.stl_deflection)
            export_shape(shape, out / f"{stem}.stl", args.stl_deflection)
        manifest = {
            "generator": "scripts/freecad/negative_mold.py",
            "freecad_version": App.Version(),
            "source": source_label,
            "units": "mm",
            "shrinkage_percent_xyz": list(args.shrink),
            "scale_xyz": list(factors),
            "master_bbox": bbox(master),
            "block": dims,
            "split_axis": args.split_axis,
            "keys": {"positions": positions, "clearance_mm": args.key_clearance},
            "channels": channels,
            "warnings": [
                "Mesh-to-BREP conversion can be extremely heavy; decimate and repair dense STL first.",
                "Planar split does not prove demoldability.",
                "Use printed tooling as a master/case for an absorbent plaster working mold in conventional ceramic slip casting."
            ]
        }
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output_dir": str(out), "mold_A_valid": a.isValid(), "mold_B_valid": b.isValid()}, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
