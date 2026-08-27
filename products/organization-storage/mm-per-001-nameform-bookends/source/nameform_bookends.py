#!/usr/bin/env python3
"""NameForm Bookends — MM-PER-001 — parametric source (CadQuery).

Spec revision 0.2.0 (design-spec.yaml is the source of truth for requirements;
this file is the source of truth for geometry). Font: DejaVu Sans Bold (SIL OFL 1.1).

Coordinate system (mm):
    X  word direction, symmetric about 0
    Y  depth; +Y = front / word face / viewer side, -Y = book side
    Z  up; underside (bed datum) at z = 0

Layout (derived from spec 0.2.0 / decision log D2, D6..D8):
    base slab   x in [-BASE_W/2, BASE_W/2],
                y in [BOOK_FACE_Y - BALLAST, LETTER_FRONT],  z in [0, BASE_H]
    letter      centered in x,
                y in [LETTER_FRONT - LETTER_DEPTH, LETTER_FRONT],
                z in [BASE_H, BASE_H + CAP]
    stop panel  full base width, y in [-PANEL_T, 0], z in [BASE_H, BASE_H + CAP]
    book face   at y = -PANEL_T (books stand on the -Y side, lean against it)

Letter orientation (decision D13): the readable face points +Y (front viewer).
Constructed as: text in XY plane (readable from +Z) -> extrude +Z -> mirror in
X -> rotate +90 deg about X. Verified: for the front viewer (at +Y) the word
reads left-to-right with letter tops up (no mirroring); the SCAD revision 0.1.0
presented a mirrored word (latent, hidden by the symmetric hero letter M).

Watermark (decision D14, gate evidence in validation/watermark.json):
JSI-WM-001-R1 standard lockup, X-mirrored so it reads normally when the
finished underside is viewed from outside with the part's front toward the
viewer, recessed WM_DEPTH into the underside, centered in x and y.

Stability: books (2.0 kg, CM 25 mm beyond book face) push +Y; the part tips
about the front bottom edge (y = +LETTER_FRONT). BALLAST is the free parameter
the build loop raises until SF >= 1.55 (spec: SF >= 1.5 minimum).

CLI:
    python3 source/nameform_bookends.py --word M --ballast 100 \
        [--watermark] --out-dir ../exports/...
Exports STEP (editable master) + STL (manufacturing) of the single part.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cadquery as cq
import ezdxf
import numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec

# ---------------------------------------------------------------------------
# Font and asset
# ---------------------------------------------------------------------------
FONT_PATH = "/usr/share/fonts/truetype/DejaVuSans-Bold.ttf"
# Canonical production asset JSI-WM-001-R1 (standard lockup), copied byte-identical
# from the skill's assets/just-innovation-watermark/ (sha256 recorded in
# validation/watermark.json). Do not recreate with a font (release gate).
DEFAULT_WM_DXF = str(Path(__file__).resolve().parent / "watermark" / "just-innovation-standard.dxf")

# ---------------------------------------------------------------------------
# Fixed design parameters (spec 0.2.0) — millimetres
# ---------------------------------------------------------------------------
BASE_H = 20.0            # base slab height (ballast)
LETTER_DEPTH = 50.0      # letter extrusion, front-to-back
PANEL_T = 4.0            # stop panel thickness
PANEL_OVERLAP = 2.0      # letter/panel bonding overlap
CHAMFER = 2.0            # base vertical corner chamfer (hazard mitigation)
WIDTH_MARGIN = 24.0      # word width + margin = base width
WIDTH_MAX = 216.0        # bed-safe width (220 bed - 4)
DEPTH_MAX = 216.0        # bed-safe depth
HEIGHT_MAX = 240.0       # bed-safe height (250 - 10)
CAP_MIN = 40.0           # practical personalization tier
CAP_MAX = 180.0
WIDTH_BUDGET = WIDTH_MAX - WIDTH_MARGIN

# anti-slip dimples (underside)
DIMPLE_PITCH = 6.0
DIMPLE_SIZE = 3.0
DIMPLE_DEPTH = 0.4
# watermark recess
WM_DEPTH = 0.4
BOOL_OVERLAP = 0.1       # boolean overlap below/above datum for robust cuts

# derived (fixed)
LETTER_FRONT = LETTER_DEPTH - PANEL_T + PANEL_OVERLAP   # 48 mm front face
BOOK_FACE_Y = -PANEL_T                                   # -4 mm book face


# ---------------------------------------------------------------------------
# Constraints (fail fast before expensive geometry)
# ---------------------------------------------------------------------------
def assert_layout(word: str, size: float, cap: float, word_w: float, ballast: float) -> None:
    import re
    if not re.fullmatch(r"[A-Z]{1,10}", word):
        raise ValueError(f"WORD must be 1-10 uppercase A-Z, got {word!r}")
    base_w = word_w + WIDTH_MARGIN
    base_depth = LETTER_FRONT - (BOOK_FACE_Y - ballast)
    checks = [
        (base_w <= WIDTH_MAX + 1e-9, f"base width {base_w:.2f} > {WIDTH_MAX} (word too long)"),
        (base_depth <= DEPTH_MAX + 1e-9, f"base depth {base_depth:.2f} > {DEPTH_MAX}"),
        (BASE_H + cap <= HEIGHT_MAX + 1e-9, f"height {BASE_H + cap:.2f} > {HEIGHT_MAX}"),
        (cap >= CAP_MIN - 1e-9, f"cap {cap:.2f} below tier minimum {CAP_MIN}"),
        (cap <= CAP_MAX + 1e-9, f"cap {cap:.2f} above maximum {CAP_MAX}"),
        (LETTER_DEPTH >= 40.0, "letter depth below 40 mm minimum"),
        (ballast >= CAP_MIN - 1e-9, f"ballast {ballast:.2f} below practical minimum {CAP_MIN}"),
    ]
    for ok, msg in checks:
        if not ok:
            raise AssertionError(msg)


# ---------------------------------------------------------------------------
# Letter (word) solid
# ---------------------------------------------------------------------------
def letter_solid(word: str, size: float) -> cq.Workplane:
    """Bold word, readable from the front (+Y), resting at z=0..CAP, y back at
    LETTER_FRONT-LETTER_DEPTH. See module docstring for the orientation proof."""
    wp = cq.Workplane("XY").text(
        word, size, 0,
        fontPath=FONT_PATH,
        halign="center", valign="bottom",
        combine=False, clean=False,
    )
    wp = wp.extrude(LETTER_DEPTH, combine=False)
    wp = wp.mirror((1, 0, 0))                      # readable face -> -Z side
    wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)       # caps up, readable face -> +Y
    wp = wp.translate((0, LETTER_FRONT, BASE_H))   # onto base top, back 2 mm into panel
    bb = wp.val().BoundingBox()
    # placement invariants (catch font/transform regressions immediately)
    assert abs(bb.ymin - (LETTER_FRONT - LETTER_DEPTH)) < 1e-6, f"letter y {bb.ymin}"
    assert abs(bb.ymax - LETTER_FRONT) < 1e-6, f"letter front {bb.ymax}"
    assert abs(bb.zmin - BASE_H) < 1e-6, f"letter base {bb.zmin}"
    assert abs(bb.zmax - (BASE_H + (bb.zmax - bb.zmin))) < 1e-9
    return wp


# ---------------------------------------------------------------------------
# Underside features: anti-slip dimples + watermark
# ---------------------------------------------------------------------------
def _shoelace2(pts2d):
    s = 0.0
    n = len(pts2d)
    for i in range(n):
        x1, y1 = pts2d[i]
        x2, y2 = pts2d[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return s / 2


def _wire_of(pts2d, want_ccw: bool, scale: float = 1.0,
             rotation_deg: float = 0.0, center: tuple = (0.0, 0.0)) -> cq.Wire:
    rad = np.deg2rad(rotation_deg)
    cr, sr = np.cos(rad), np.sin(rad)
    out = []
    for x, y in pts2d:
        x, y = x * scale, y * scale
        dx, dy = x - center[0], y - center[1]
        x = center[0] + dx * cr - dy * sr
        y = center[1] + dx * sr + dy * cr
        out.append((-x, y))                      # X-mirror (readable from underside)
    src = out
    if (_shoelace2(src) > 0) != want_ccw:
        src = src[::-1]
    if src[0] != src[-1]:
        src = src + [src[0]]
    return cq.Wire.makePolygon([(x, y, 0.0) for x, y in src])


def _prism(face: cq.Face, depth: float) -> cq.Solid:
    p = BRepPrimAPI_MakePrism(face.wrapped, gp_Vec(0.0, 0.0, depth), depth, True)
    return cq.Solid(p.Shape())


def watermark_cutter(dxf_path: str, depth: float, scale: float = 1.0,
                     rotation_deg: float = 0.0) -> cq.Shape:
    """Closed DXF polylines (asset JSI-WM-001-R1) -> X-mirrored solids,
    z in [0, depth]. Holes are detected by centroid containment.
    `scale`/`rotation_deg` are the selector's uniform scale and rotation
    (release gate: apply the selector's selection, never shrink the mark)."""
    doc = ezdxf.readfile(dxf_path)
    polys = []
    for e in doc.modelspace():
        if e.dxftype() == "POLYLINE":
            polys.append([(v.dxf.location.x, v.dxf.location.y) for v in e.vertices])
        elif e.dxftype() == "LWPOLYLINE":
            polys.append(list(e.get_points(format="xy")))
    if not polys:
        raise ValueError(f"no closed polylines in {dxf_path}")

    import shapely
    sp = []
    for p in polys:
        poly = shapely.Polygon([(-x, y) for x, y in p])
        if not poly.is_valid:
            poly = poly.buffer(0)
        sp.append(poly)
    holes: dict[int, list[int]] = {}
    for i in range(len(sp)):
        for j in range(len(sp)):
            if i != j and sp[j].area > sp[i].area and sp[j].contains(sp[i].representative_point()):
                holes.setdefault(j, []).append(i)
    hole_idx = {i for hs in holes.values() for i in hs}

    all_x = [x for p in polys for x, _ in p]
    all_y = [y for p in polys for _, y in p]
    center = ((min(all_x) + max(all_x)) / 2.0, (min(all_y) + max(all_y)) / 2.0)

    solids = []
    for j in range(len(polys)):
        if j in hole_idx:
            continue
        outer = _wire_of(polys[j], True, scale, rotation_deg, center)
        hs = [_wire_of(polys[i], False, scale, rotation_deg, center)
              for i in holes.get(j, [])]
        solids.append(_prism(cq.Face.makeFromWires(outer, hs), depth))
    comp = cq.Compound.makeCompound(solids)
    bb = comp.BoundingBox()
    if bb.zmin < -1e-9 or bb.zmax > depth + 1e-6:
        raise AssertionError(f"watermark cutter out of z-range: {bb.zmin}..{bb.zmax}")
    # re-center on the mark's own center (the asset origin is not centered)
    comp = comp.translate((-(bb.xmin + bb.xmax) / 2.0, -(bb.ymin + bb.ymax) / 2.0, 0.0))
    return comp


def dimples_cutter(base_w: float, base_back: float, wm_cx: float, wm_cy: float,
                   wm_half_w: float = 20.0, wm_half_h: float = 12.0) -> cq.Shape:
    """Anti-slip dimple grid on the underside, excluding a zone around the
    watermark (keeps the mark free of deliberate texture). Zone half-extents
    must cover the scaled mark half-extents + 2 mm clearance."""
    wm_x0, wm_x1 = wm_cx - wm_half_w, wm_cx + wm_half_w
    wm_y0, wm_y1 = wm_cy - wm_half_h, wm_cy + wm_half_h
    h = DIMPLE_DEPTH + BOOL_OVERLAP
    cubes = []
    x = DIMPLE_PITCH / 2
    while x <= base_w / 2 - 1.0 + 1e-9:
        y = base_back + DIMPLE_PITCH / 2
        while y <= LETTER_FRONT - DIMPLE_PITCH / 2 + 1e-9:
            if not (wm_x0 <= x <= wm_x1 and wm_y0 <= y <= wm_y1):
                c = (cq.Workplane("XY")
                     .box(DIMPLE_SIZE, DIMPLE_SIZE, h, centered=(True, True, False))
                     .translate((x, y, -BOOL_OVERLAP)).val())
                cubes.append(c)
            y += DIMPLE_PITCH
        x += DIMPLE_PITCH
    if not cubes:
        raise AssertionError("dimple grid empty — layout too small")
    return cq.Compound.makeCompound(cubes)


# ---------------------------------------------------------------------------
# Full part
# ---------------------------------------------------------------------------
def build(
    word: str,
    size: float,
    cap: float,
    word_w: float,
    ballast: float,
    watermark: bool = False,
    wm_dxf: str = DEFAULT_WM_DXF,
    wm_scale: float = 1.0,
    wm_rotation_deg: float = 0.0,
) -> cq.Workplane:
    """Single solid bookend. `watermark=True` applies the LAST solid change
    (JuSt Innovation recess) — master exports use watermark=False.
    `wm_scale`/`wm_rotation_deg` are the selector's selection (release gate)."""
    assert_layout(word, size, cap, word_w, ballast)

    base_w = word_w + WIDTH_MARGIN
    base_back = BOOK_FACE_Y - ballast
    base_depth = LETTER_FRONT - base_back
    base_cy = (base_back + LETTER_FRONT) / 2.0

    base = (cq.Workplane("XY")
            .box(base_w, base_depth, BASE_H, centered=(True, True, False))
            .translate((0, base_cy, 0))
            .edges("|Z").chamfer(CHAMFER))

    panel = (cq.Workplane("XY")
             .box(base_w, PANEL_T, cap, centered=(True, True, False))
             .translate((0, -PANEL_T / 2.0, BASE_H)))

    letter = letter_solid(word, size)

    part = base.union(panel)
    part = part.union(letter)

    wm_cy = base_cy  # watermark centered on the underside
    # one scaled cutter for both the dimple exclusion zone and the final cut;
    # built at depth+overlap so the recess cuts exactly WM_DEPTH into the
    # underside while the boolean overlap stays below the bed datum
    wm = watermark_cutter(wm_dxf, WM_DEPTH + BOOL_OVERLAP, wm_scale, wm_rotation_deg)
    ebb = wm.BoundingBox()
    wm_half_w = (ebb.xmax - ebb.xmin) / 2.0
    wm_half_h = (ebb.ymax - ebb.ymin) / 2.0
    part = part.cut(dimples_cutter(base_w, base_back, 0.0, wm_cy,
                                   wm_half_w + 2.0, wm_half_h + 2.0))

    if watermark:
        margin_x = base_w / 2.0 - wm_half_w
        margin_y = min(wm_cy - wm_half_h - base_back, LETTER_FRONT - (wm_cy + wm_half_h))
        if margin_x < 5.0 or margin_y < 5.0:
            raise AssertionError(f"watermark clearance too small: x={margin_x:.2f} y={margin_y:.2f}")
        part = part.cut(wm.translate((0.0, wm_cy, -BOOL_OVERLAP)))

    v = part.val()
    assert not v.isNull() and len(part.solids().vals()) == 1, "expected exactly one solid"
    return part


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
STL_TOLERANCE = 0.05       # chordal mm (recorded in build-summary)
STL_ANGULAR_TOLERANCE = 0.5  # rad

def export_stl(part: cq.Workplane, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(part, str(path), tolerance=STL_TOLERANCE,
                        angularTolerance=STL_ANGULAR_TOLERANCE)


def export_step(part: cq.Workplane, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(part, str(path))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--word", required=True)
    ap.add_argument("--size", type=float, required=True)
    ap.add_argument("--cap", type=float, required=True)
    ap.add_argument("--word-width", type=float, required=True)
    ap.add_argument("--ballast", type=float, default=100.0)
    ap.add_argument("--watermark", action="store_true")
    ap.add_argument("--wm-dxf", default=DEFAULT_WM_DXF)
    ap.add_argument("--out-stl", required=True)
    ap.add_argument("--out-step", required=True)
    a = ap.parse_args()

    part = build(a.word, a.size, a.cap, a.word_width, a.ballast, a.watermark, a.wm_dxf)
    export_stl(part, Path(a.out_stl))
    export_step(part, Path(a.out_step))
    v = part.val()
    bb = v.BoundingBox()
    print(f"part: {v.Volume()/1000.0:.2f} cm3  "
          f"bbox x[{bb.xmin:.2f},{bb.xmax:.2f}] y[{bb.ymin:.2f},{bb.ymax:.2f}] "
          f"z[{bb.zmin:.2f},{bb.zmax:.2f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
