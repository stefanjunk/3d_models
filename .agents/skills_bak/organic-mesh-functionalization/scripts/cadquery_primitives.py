#!/usr/bin/env python3
"""Generate precise functional cutters/inserts from a small JSON schema using CadQuery."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import cadquery as cq
from cadquery import exporters


def rounded_box(x: float, y: float, z: float, radius: float) -> cq.Workplane:
    if radius <= 0:
        return cq.Workplane("XY").box(x, y, z, centered=(True, True, True))
    if 2 * radius >= min(x, y):
        raise ValueError("rounded_box radius must be less than half of X and Y")
    # A 2D rounded profile extruded to total height z is more robust to
    # tessellate than filleting every edge of a triangulated box.
    return (cq.Workplane("XY")
            .sketch().rect(x, y).vertices().fillet(radius).finalize()
            .extrude(z / 2, both=True)
            .clean())


def make_shape(spec: dict[str, Any]) -> cq.Workplane:
    kind = spec["type"].lower()
    if kind == "box":
        result = cq.Workplane("XY").box(*map(float, spec["size"]), centered=(True, True, True))
    elif kind == "rounded_box":
        result = rounded_box(*map(float, spec["size"]), float(spec.get("radius", 1.0)))
    elif kind == "cylinder":
        result = cq.Workplane("XY").circle(float(spec["radius"])).extrude(float(spec["height"]) / 2, both=True)
    elif kind == "tube":
        outer = float(spec["outer_radius"])
        inner = float(spec["inner_radius"])
        h = float(spec["height"])
        if not 0 < inner < outer:
            raise ValueError("tube requires 0 < inner_radius < outer_radius")
        result = cq.Workplane("XY").circle(outer).circle(inner).extrude(h / 2, both=True)
    elif kind == "capsule":
        length = float(spec["length"])
        radius = float(spec["radius"])
        depth = float(spec["depth"])
        if length < 2 * radius:
            raise ValueError("capsule length must be >= 2*radius")
        half = length / 2 - radius
        wire = (cq.Workplane("XY")
                .moveTo(-half, -radius)
                .lineTo(half, -radius)
                .threePointArc((half + radius, 0), (half, radius))
                .lineTo(-half, radius)
                .threePointArc((-half - radius, 0), (-half, -radius))
                .close())
        result = wire.extrude(depth / 2, both=True)
    else:
        raise ValueError(f"Unsupported type: {kind}")

    rot = spec.get("rotation_deg", [0, 0, 0])
    for axis, angle in zip(((1,0,0), (0,1,0), (0,0,1)), rot):
        if float(angle):
            result = result.rotate((0,0,0), axis, float(angle))
    loc = spec.get("location", [0, 0, 0])
    return result.translate(tuple(map(float, loc)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("config", type=Path)
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text())
    out = Path(cfg.get("output_dir", "generated-parts"))
    out.mkdir(parents=True, exist_ok=True)

    manifest = []
    for spec in cfg["parts"]:
        name = spec["name"]
        shape = make_shape(spec)
        step = out / f"{name}.step"
        stl = out / f"{name}.stl"
        exporters.export(shape, str(step))
        exporters.export(shape, str(stl), tolerance=float(spec.get("stl_tolerance", 0.05)))
        solid = shape.val()
        manifest.append({
            "name": name,
            "step": str(step),
            "stl": str(stl),
            "volume": float(solid.Volume()),
            "bounds": [solid.BoundingBox().xlen, solid.BoundingBox().ylen, solid.BoundingBox().zlen],
        })
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
