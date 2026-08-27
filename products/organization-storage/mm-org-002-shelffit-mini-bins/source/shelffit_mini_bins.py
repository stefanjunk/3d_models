#!/usr/bin/env python3
"""Parametric CadQuery source for MM-ORG-002 ShelfFit Mini Bins v0.1.0.

The source produces one support-free open-top body. The reference set uses two
identical prints. The canonical metriMade watermark is optional so the same
source can produce an unmarked engineering master and a marked DRAFT candidate.
All dimensions are millimetres and z=0 is the immutable print-bed datum.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache
import json
from pathlib import Path

import cadquery as cq


PROJECT_ID = "MM-ORG-002"
REVISION = "0.1.0"
ASSET_ID = "MM-WM-001-R1"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
WATERMARK_DIR = (
    PROJECT_ROOT
    / "assets"
    / "metrimade-watermark"
    / "generated"
    / f"{PROJECT_ID}_v{REVISION}"
)
WATERMARK_DXF = WATERMARK_DIR / f"metrimade-watermark-{PROJECT_ID}-v{REVISION}.dxf"
WATERMARK_METADATA = WATERMARK_DIR / f"metrimade-watermark-{PROJECT_ID}-v{REVISION}.json"
WATERMARK_DEPTH = 0.40
BOOLEAN_OVERLAP = 0.01


@dataclass(frozen=True)
class BinParameters:
    body_width: float = 208.5
    body_depth: float = 208.0
    body_height: float = 148.0
    wall: float = 1.92
    floor: float = 1.80
    outer_corner_radius: float = 8.0
    top_rim_height: float = 3.60
    top_rim_overhang_each_side: float = 0.75
    grip_radius: float = 24.0
    grip_center_z: float = 148.0

    @property
    def inner_width(self) -> float:
        return self.body_width - 2.0 * self.wall

    @property
    def inner_depth(self) -> float:
        return self.body_depth - 2.0 * self.wall

    @property
    def inner_corner_radius(self) -> float:
        return self.outer_corner_radius - self.wall

    @property
    def rim_width(self) -> float:
        return self.body_width + 2.0 * self.top_rim_overhang_each_side

    @property
    def rim_depth(self) -> float:
        return self.body_depth + 2.0 * self.top_rim_overhang_each_side

    @property
    def rim_corner_radius(self) -> float:
        return self.outer_corner_radius + self.top_rim_overhang_each_side

    def validate(self) -> None:
        assert 0.0 < self.wall < 0.1 * min(self.body_width, self.body_depth)
        assert self.floor >= 1.2
        assert self.floor - WATERMARK_DEPTH >= 0.8
        assert self.body_height > self.floor + self.top_rim_height
        assert self.inner_width > 0 and self.inner_depth > 0
        assert self.inner_corner_radius > 0
        assert self.rim_width <= 210.0 + 1e-9
        assert self.rim_depth <= 210.0 + 1e-9
        assert self.body_height <= 250.0
        assert self.grip_center_z == self.body_height
        assert self.grip_radius >= 18.0
        assert 2.0 * self.grip_radius < self.body_width - 4.0 * self.wall


DEFAULT = BinParameters()
CONSERVATIVE_BASELINE = replace(DEFAULT, wall=2.526858347, floor=2.40)


def _rounded_prism(width: float, depth: float, radius: float,
                   height: float, z0: float = 0.0) -> cq.Workplane:
    if min(width, depth, height) <= 0:
        raise ValueError("rounded prism dimensions must be positive")
    if not 0 < radius < 0.5 * min(width, depth):
        raise ValueError("rounded prism radius is outside the valid range")
    sketch = cq.Sketch().rect(width, depth).vertices().fillet(radius)
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .placeSketch(sketch)
        .extrude(height)
    )


def _body_without_grip(p: BinParameters) -> cq.Workplane:
    outer = _rounded_prism(
        p.body_width, p.body_depth, p.outer_corner_radius, p.body_height
    )
    cavity = _rounded_prism(
        p.inner_width,
        p.inner_depth,
        p.inner_corner_radius,
        p.body_height - p.floor + BOOLEAN_OVERLAP,
        z0=p.floor,
    )
    shell = outer.cut(cavity)

    rim_z = p.body_height - p.top_rim_height
    rim_outer = _rounded_prism(
        p.rim_width,
        p.rim_depth,
        p.rim_corner_radius,
        p.top_rim_height,
        z0=rim_z,
    )
    rim_cavity = _rounded_prism(
        p.inner_width,
        p.inner_depth,
        p.inner_corner_radius,
        p.top_rim_height + 2.0 * BOOLEAN_OVERLAP,
        z0=rim_z - BOOLEAN_OVERLAP,
    )
    return shell.union(rim_outer.cut(rim_cavity))


def _grip_cutter(p: BinParameters) -> cq.Workplane:
    start_y = -p.rim_depth / 2.0 - BOOLEAN_OVERLAP
    cutter_depth = (
        p.top_rim_overhang_each_side
        + p.wall
        + 2.0 * BOOLEAN_OVERLAP
    )
    cylinder = cq.Solid.makeCylinder(
        p.grip_radius,
        cutter_depth,
        cq.Vector(0.0, start_y, p.grip_center_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    return cq.Workplane("XY").newObject([cylinder])


@lru_cache(maxsize=1)
def watermark_cutter_centered() -> cq.Shape:
    """Return the exact generated DXF as an underside-reading cutter."""
    if not WATERMARK_DXF.is_file() or not WATERMARK_METADATA.is_file():
        raise FileNotFoundError("generated metriMade watermark profile is missing")
    metadata = json.loads(WATERMARK_METADATA.read_text(encoding="utf-8"))
    identity = (
        metadata.get("asset_revision"),
        metadata.get("product_id"),
        metadata.get("version"),
    )
    if identity != (ASSET_ID, PROJECT_ID, REVISION):
        raise ValueError(f"watermark identity mismatch: {identity}")
    imported = cq.importers.importDXF(str(WATERMARK_DXF))
    solids = imported.extrude(
        WATERMARK_DEPTH + BOOLEAN_OVERLAP, combine=False
    ).solids().vals()
    expected_bodies = int(metadata["digital_validation"]["cutter"]["body_count"])
    if len(solids) != expected_bodies:
        raise AssertionError(
            f"expected {expected_bodies} watermark solids, got {len(solids)}"
        )
    compound = cq.Compound.makeCompound(solids).mirror("YZ")
    bb = compound.BoundingBox()
    compound = compound.translate(
        (
            -(bb.xmin + bb.xmax) / 2.0,
            -(bb.ymin + bb.ymax) / 2.0,
            -BOOLEAN_OVERLAP,
        )
    )
    bb = compound.BoundingBox()
    expected = metadata["digital_validation"]["cutter"]["extents_mm"]
    if abs(bb.xlen - float(expected[0])) > 0.02 or abs(bb.ylen - float(expected[1])) > 0.02:
        raise AssertionError(
            f"unexpected watermark envelope {bb.xlen:.6f} x {bb.ylen:.6f}"
        )
    expected_area = float(metadata["digital_validation"]["cutter"]["volume_mm3"]) / WATERMARK_DEPTH
    actual_area = compound.Volume() / (WATERMARK_DEPTH + BOOLEAN_OVERLAP)
    if abs(actual_area - expected_area) > 0.05:
        raise AssertionError("DXF cutter section differs from generated metadata")
    return compound


def apply_watermark(part: cq.Workplane, p: BinParameters) -> cq.Workplane:
    cutter = watermark_cutter_centered()
    cutter_bb = cutter.BoundingBox()
    safe_width = p.body_width - 24.0
    safe_depth = p.body_depth - 24.0
    if cutter_bb.xlen > safe_width or cutter_bb.ylen > safe_depth:
        raise AssertionError("watermark does not fit the protected underside region")
    result = part.cut(cq.Workplane("XY").newObject([cutter]))
    solids = result.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError("watermark cut broke the primary body")
    bb = solids[0].BoundingBox()
    if abs(bb.zmin) > 1e-6:
        raise AssertionError(f"watermark changed bed datum to {bb.zmin}")
    return result


def build_bin(p: BinParameters = DEFAULT, watermark: bool = False) -> cq.Workplane:
    p.validate()
    body = _body_without_grip(p).cut(_grip_cutter(p))
    solids = body.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError("base construction did not produce one valid solid")
    if watermark:
        body = apply_watermark(body, p)
    return body


def build_corner_coupon(p: BinParameters = DEFAULT) -> cq.Workplane:
    """Small process coupon retaining the front-left floor/wall corner."""
    master = build_bin(p, watermark=False)
    sample = (
        cq.Workplane("XY")
        .box(42.0, 42.0, 16.0, centered=(False, False, False))
        .translate((-p.rim_width / 2.0, -p.rim_depth / 2.0, 0.0))
    )
    coupon = master.intersect(sample)
    solids = coupon.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError("corner coupon is not one valid solid")
    return coupon


def shape_metrics(part: cq.Workplane) -> dict[str, float | list[float] | int]:
    solids = part.solids().vals()
    if len(solids) != 1:
        raise AssertionError(f"expected one solid, got {len(solids)}")
    solid = solids[0]
    bb = solid.BoundingBox()
    return {
        "body_count": len(solids),
        "bounds_mm": [bb.xlen, bb.ylen, bb.zlen],
        "z_min_mm": bb.zmin,
        "z_max_mm": bb.zmax,
        "volume_mm3": solid.Volume(),
        "surface_area_mm2": solid.Area(),
    }


if __name__ == "__main__":
    metrics = shape_metrics(build_bin(DEFAULT, watermark=False))
    print(json.dumps(metrics, indent=2))

