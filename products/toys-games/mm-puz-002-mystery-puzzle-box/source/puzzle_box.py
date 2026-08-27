#!/usr/bin/env python3
"""Parametric CAD for MM-PUZ-002 Mystery Puzzle Box v1.2.0.

The exact exterior, cavity, lid skirt, three face apertures, local latch ledges,
generic slider, return leaf and compact vector texture are generated with
CadQuery. The current design is a DRAFT digital candidate: actual spring force,
friction, latch reliability and visual camouflage remain physical gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path

import cadquery as cq


PROJECT_ID = "MM-PUZ-002"
REVISION = "1.2.0"
CANDIDATE = "1.2.0-draft.1"
ASSET_ID = "MM-WM-001-R1"
ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WM_DIR = ROOT / "assets" / "metrimade-watermark" / "generated" / f"{PROJECT_ID}_v{REVISION}"
WM_DXF = WM_DIR / f"metrimade-watermark-{PROJECT_ID}-v{REVISION}.dxf"
WM_METADATA = WM_DIR / f"metrimade-watermark-{PROJECT_ID}-v{REVISION}.json"
WM_DEPTH = 0.4
OVERLAP = 0.01


@dataclass(frozen=True)
class Parameters:
    length: float = 250.0
    depth: float = 75.0
    total_height: float = 75.0
    body_height: float = 65.0
    wall: float = 2.5
    floor: float = 3.0
    outer_radius: float = 4.0
    lid_top: float = 3.0
    lid_skirt_overlap: float = 7.0
    lid_skirt_wall: float = 2.5
    lid_radial_clearance: float = 0.35
    slider_clearance: float = 0.30
    button_travel: float = 1.50
    button_center_z: float = 55.0
    texture_depth: float = 0.60
    texture_slit_depth: float = 0.30

    @property
    def inner_length(self) -> float:
        return self.length - 2.0 * self.wall

    @property
    def inner_depth(self) -> float:
        return self.depth - 2.0 * self.wall

    @property
    def inner_radius(self) -> float:
        return self.outer_radius - self.wall

    @property
    def lid_bottom(self) -> float:
        return self.body_height - self.lid_skirt_overlap

    @property
    def skirt_outer_length(self) -> float:
        return self.inner_length - 2.0 * self.lid_radial_clearance

    @property
    def skirt_outer_depth(self) -> float:
        return self.inner_depth - 2.0 * self.lid_radial_clearance

    def validate(self) -> None:
        assert self.total_height == 75.0
        assert self.body_height + (self.total_height - self.body_height) == self.total_height
        assert self.wall >= 2.4 and self.floor >= 3.0
        assert self.floor - WM_DEPTH >= 0.8
        assert self.inner_radius > 0
        assert self.lid_radial_clearance >= 0.25
        assert self.slider_clearance >= 0.25
        assert self.button_travel == 1.5
        assert self.texture_depth <= self.wall - 1.2


DEFAULT = Parameters()


def _rounded_prism(width: float, depth: float, radius: float,
                   height: float, z0: float = 0.0) -> cq.Workplane:
    sketch = cq.Sketch().rect(width, depth).vertices().fillet(radius)
    return cq.Workplane("XY").workplane(offset=z0).placeSketch(sketch).extrude(height)


def _box(dx: float, dy: float, dz: float, center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").box(dx, dy, dz).translate(center)


@lru_cache(maxsize=12)
def motif(size: float, depth: float, slit_depth: float) -> cq.Shape:
    """Question mark plus rounded perimeter slit, both starting at z=0."""
    q = (
        cq.Workplane("XY")
        .text("?", size, depth, combine=False, clean=True,
              font="DejaVu Sans", fontPath=FONT_PATH, kind="bold")
    )
    width = 0.82 * size
    height = 1.18 * size
    radius = min(1.5, 0.16 * size)
    slit = 0.45
    outer = _rounded_prism(width, height, radius, slit_depth)
    inner = _rounded_prism(
        width - 2.0 * slit,
        height - 2.0 * slit,
        max(0.3, radius - slit),
        slit_depth + OVERLAP,
        z0=-OVERLAP,
    )
    ring = outer.cut(inner)
    solids = q.solids().vals() + ring.solids().vals()
    return cq.Compound.makeCompound(solids)


def _transformed_motif(surface: str, u: float, v: float, size: float,
                       angle: float, p: Parameters) -> cq.Shape:
    shape = motif(size, p.texture_depth, p.texture_slit_depth)
    shape = shape.rotate((0, 0, 0), (0, 0, 1), angle)
    if surface == "front":
        return shape.rotate((0, 0, 0), (1, 0, 0), -90).translate((u, -p.depth / 2.0 - OVERLAP, v))
    if surface == "rear":
        return shape.rotate((0, 0, 0), (1, 0, 0), 90).translate((u, p.depth / 2.0 + OVERLAP, v))
    if surface == "left":
        return shape.rotate((0, 0, 0), (0, 1, 0), 90).translate((-p.length / 2.0 - OVERLAP, u, v))
    if surface == "right":
        return shape.rotate((0, 0, 0), (0, 1, 0), -90).translate((p.length / 2.0 + OVERLAP, u, v))
    if surface == "top":
        return shape.rotate((0, 0, 0), (1, 0, 0), 180).translate((u, v, p.total_height + OVERLAP))
    raise ValueError(f"unknown texture surface: {surface}")


def _body_texture_cutters(p: Parameters) -> cq.Workplane:
    placements: list[tuple[str, float, float, float, float]] = []
    row_a = [-105, -70, -35, 0, 35, 70, 105]
    row_b = [-98, -58, -18, 22, 62, 102]
    for surface in ("front", "rear"):
        for idx, x in enumerate(row_a):
            placements.append((surface, x, 17.0, (8.0, 11.0, 15.0)[idx % 3], (-12, 0, 12)[idx % 3]))
        for idx, x in enumerate(row_b):
            placements.append((surface, x, 39.5, (11.0, 15.0, 8.0)[idx % 3], (10, -8, 5)[idx % 3]))
    for surface in ("left", "right"):
        for idx, y in enumerate((-23.0, 0.0, 23.0)):
            placements.append((surface, y, 17.0, (8.0, 11.0, 8.0)[idx], (-10, 0, 10)[idx]))
            placements.append((surface, y, 39.5, (11.0, 15.0, 11.0)[idx], (8, -8, 0)[idx]))
    shapes = [_transformed_motif(*placement, p) for placement in placements]
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(shapes)])


def _lid_texture_cutters(p: Parameters) -> cq.Workplane:
    shapes: list[cq.Shape] = []
    xs = (-100.0, -60.0, -20.0, 20.0, 60.0, 100.0)
    for row, y in enumerate((-24.0, 0.0, 24.0)):
        for idx, x in enumerate(xs):
            size = (8.0, 11.0, 15.0)[(idx + row) % 3]
            angle = (-12.0, 0.0, 12.0)[(2 * idx + row) % 3]
            shapes.append(_transformed_motif("top", x, y, size, angle, p))
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(shapes)])


def _front_guide(p: Parameters, x: float, front: bool) -> tuple[cq.Workplane, cq.Workplane]:
    sy = -1.0 if front else 1.0
    wall_y = sy * (p.depth / 2.0 - p.wall / 2.0)
    opening = _box(12.0 + 2 * p.slider_clearance, p.wall + 2 * OVERLAP,
                   14.0 + 2 * p.slider_clearance, (x, wall_y, p.button_center_z))
    guide_y = sy * (p.depth / 2.0 - p.wall - 4.0)
    # The rails stop 0.30 mm below the lid skirt.  The wider rail envelope
    # retains 1.70 mm on either side of the 16.60 mm slider pocket.
    guide = _box(20.0, 8.0, 12.6, (x, guide_y, 51.4))
    pocket = _box(16.0 + 2 * p.slider_clearance, 10.0, 18.0,
                  (x, guide_y, 53.0))
    return guide, opening.union(pocket)


def _left_guide(p: Parameters, y: float) -> tuple[cq.Workplane, cq.Workplane]:
    wall_x = -p.length / 2.0 + p.wall / 2.0
    opening = _box(p.wall + 2 * OVERLAP, 12.0 + 2 * p.slider_clearance,
                   14.0 + 2 * p.slider_clearance, (wall_x, y, p.button_center_z))
    guide_x = -p.length / 2.0 + p.wall + 4.0
    guide = _box(8.0, 20.0, 12.6, (guide_x, y, 51.4))
    pocket = _box(10.0, 16.0 + 2 * p.slider_clearance, 18.0,
                  (guide_x, y, 53.0))
    return guide, opening.union(pocket)


def build_body(p: Parameters = DEFAULT, watermark: bool = False,
               textured: bool = True) -> cq.Workplane:
    p.validate()
    outer = _rounded_prism(p.length, p.depth, p.outer_radius, p.body_height)
    cavity = _rounded_prism(
        p.inner_length, p.inner_depth, p.inner_radius,
        p.body_height - p.floor + OVERLAP, z0=p.floor,
    )
    body = outer.cut(cavity)
    cutters: list[cq.Workplane] = []
    for x, front in ((-60.0, True), (60.0, False)):
        guide, cutter = _front_guide(p, x, front)
        body = body.union(guide)
        cutters.append(cutter)
    guide, cutter = _left_guide(p, 0.0)
    body = body.union(guide)
    cutters.append(cutter)
    for cutter in cutters:
        body = body.cut(cutter)
    if textured:
        body = body.cut(_body_texture_cutters(p))
    if watermark:
        body = apply_watermark(body, p)
    solids = body.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError(f"body should be one solid, got {len(solids)}")
    return body


def build_lid(p: Parameters = DEFAULT, textured: bool = True) -> cq.Workplane:
    p.validate()
    cap_outer = _rounded_prism(
        p.length, p.depth, p.outer_radius,
        p.total_height - p.body_height, z0=p.body_height,
    )
    skirt_height = p.total_height - p.lid_top - p.lid_bottom
    skirt_outer = _rounded_prism(
        p.skirt_outer_length, p.skirt_outer_depth,
        max(0.8, p.inner_radius - p.lid_radial_clearance),
        skirt_height, z0=p.lid_bottom,
    )
    skirt_inner = _rounded_prism(
        p.skirt_outer_length - 2 * p.lid_skirt_wall,
        p.skirt_outer_depth - 2 * p.lid_skirt_wall,
        max(0.4, p.inner_radius - p.lid_radial_clearance - p.lid_skirt_wall),
        skirt_height + 2 * OVERLAP,
        z0=p.lid_bottom - OVERLAP,
    )
    # Hollow the underside of the 10 mm external cap so the visible side band
    # stays flush with the body while only the top 3 mm remains solid.
    cap_inner = _rounded_prism(
        p.skirt_outer_length - 2 * p.lid_skirt_wall,
        p.skirt_outer_depth - 2 * p.lid_skirt_wall,
        max(0.4, p.inner_radius - p.lid_radial_clearance - p.lid_skirt_wall),
        p.total_height - p.lid_top - p.body_height + OVERLAP,
        z0=p.body_height - OVERLAP,
    )
    lid = cap_outer.cut(cap_inner).union(skirt_outer.cut(skirt_inner))
    # Local ledges protrude inward from the front, rear and left skirt walls.
    lid = lid.union(_box(16.0, 3.65, 2.0, (-60.0, -30.325, 60.5)))
    lid = lid.union(_box(16.0, 3.65, 2.0, (60.0, 30.325, 60.5)))
    lid = lid.union(_box(3.65, 16.0, 2.0, (-117.825, 0.0, 60.5)))
    if textured:
        lid = lid.cut(_lid_texture_cutters(p))
    solids = lid.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError(f"lid should be one solid, got {len(solids)}")
    return lid


def build_slider() -> cq.Workplane:
    """Generic slider in local coordinates; +X is the inward press direction."""
    # The 1.20 mm cap stays 0.15 mm clear of the lid skirt at full travel.
    cap = cq.Workplane("XY").box(1.2, 12.0, 14.0, centered=(False, True, True))
    shoulder = (
        cq.Workplane("XY").box(2.4, 16.0, 10.0, centered=(False, True, True))
        .translate((1.1, 0.0, -2.3))
    )
    shaft = (
        cq.Workplane("XY").box(6.8, 5.0, 5.0, centered=(False, True, True))
        .translate((3.4, 0.0, 0.0))
    )
    hook = (
        cq.Workplane("XY").box(1.8, 5.0, 4.2, centered=(False, True, False))
        .translate((8.4, 0.0, 2.2))
    )
    slider = cap.union(shoulder).union(shaft).union(hook)
    mark = (
        cq.Workplane("YZ", origin=(-OVERLAP, 0.0, 0.0))
        .text("?", 8.0, 0.45, combine=False, clean=True,
              font="DejaVu Sans", fontPath=FONT_PATH, kind="bold")
    )
    slider = slider.cut(mark)
    solids = slider.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError("slider should be one solid")
    return slider


def build_return_leaf() -> cq.Workplane:
    base = cq.Workplane("XY").box(5.0, 8.0, 3.0, centered=(False, True, False))
    beam = (
        cq.Workplane("XY").box(20.0, 6.0, 1.2, centered=(False, True, False))
        .translate((4.5, 0.0, 0.9))
    )
    leaf = base.union(beam)
    solids = leaf.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError("return leaf should be one solid")
    return leaf


def slider_print_orientation() -> cq.Workplane:
    slider = build_slider().rotate((0, 0, 0), (0, 1, 0), -90)
    bb = slider.val().BoundingBox()
    return slider.translate((0.0, 0.0, -bb.zmin))


def lid_print_orientation(p: Parameters = DEFAULT) -> cq.Workplane:
    lid = build_lid(p, textured=True).rotate((0, 0, 0), (0, 1, 0), 180)
    bb = lid.val().BoundingBox()
    return lid.translate((0.0, 0.0, -bb.zmin))


def assembly_sliders(p: Parameters = DEFAULT) -> dict[str, cq.Workplane]:
    local = build_slider()
    return {
        "front": local.rotate((0, 0, 0), (0, 0, 1), 90).translate((-60.0, -p.depth / 2.0, p.button_center_z)),
        "rear": local.rotate((0, 0, 0), (0, 0, 1), -90).translate((60.0, p.depth / 2.0, p.button_center_z)),
        "left": local.translate((-p.length / 2.0, 0.0, p.button_center_z)),
    }


@lru_cache(maxsize=1)
def watermark_cutter() -> cq.Shape:
    if not WM_DXF.is_file() or not WM_METADATA.is_file():
        raise FileNotFoundError("generated metriMade watermark is missing")
    metadata = json.loads(WM_METADATA.read_text(encoding="utf-8"))
    if (metadata.get("asset_revision"), metadata.get("product_id"), metadata.get("version")) != (
        ASSET_ID, PROJECT_ID, REVISION
    ):
        raise ValueError("watermark identity mismatch")
    solids = (
        cq.importers.importDXF(str(WM_DXF))
        .extrude(WM_DEPTH + OVERLAP, combine=False)
        .solids().vals()
    )
    expected_bodies = int(metadata["digital_validation"]["cutter"]["body_count"])
    if len(solids) != expected_bodies:
        raise AssertionError(f"expected {expected_bodies} watermark solids, got {len(solids)}")
    compound = cq.Compound.makeCompound(solids).mirror("YZ")
    bb = compound.BoundingBox()
    return compound.translate((-(bb.xmin + bb.xmax) / 2.0,
                               -(bb.ymin + bb.ymax) / 2.0,
                               -OVERLAP))


def apply_watermark(body: cq.Workplane, p: Parameters) -> cq.Workplane:
    cutter = watermark_cutter()
    bb = cutter.BoundingBox()
    if bb.xlen > 210.0 or bb.ylen > 52.0:
        raise AssertionError("watermark exceeds selected underside region")
    result = body.cut(cq.Workplane("XY").newObject([cutter]))
    solids = result.solids().vals()
    if len(solids) != 1 or abs(solids[0].BoundingBox().zmin) > 1e-6:
        raise AssertionError("watermark damaged body or bed datum")
    return result


def metrics(shape: cq.Workplane) -> dict:
    solids = shape.solids().vals()
    if len(solids) != 1:
        raise AssertionError(f"expected one solid, got {len(solids)}")
    solid = solids[0]
    bb = solid.BoundingBox()
    return {
        "body_count": 1,
        "bounds_mm": [bb.xlen, bb.ylen, bb.zlen],
        "min_mm": [bb.xmin, bb.ymin, bb.zmin],
        "max_mm": [bb.xmax, bb.ymax, bb.zmax],
        "volume_mm3": solid.Volume(),
        "surface_area_mm2": solid.Area(),
        "brep_valid": bool(solid.isValid()),
    }


if __name__ == "__main__":
    parts = {
        "body": build_body(DEFAULT, watermark=True, textured=True),
        "lid": build_lid(DEFAULT, textured=True),
        "slider": build_slider(),
        "leaf": build_return_leaf(),
    }
    print(json.dumps({name: metrics(shape) for name, shape in parts.items()}, indent=2))
