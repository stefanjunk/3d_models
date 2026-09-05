"""MM-ORG-043 Euro circulation-coin pocket-emptying tray - parametric source.

Recess diameters follow the EU-fixed coin nominals plus one named clearance.
That clearance is UNQUALIFIED on this process and is bounded below 0.50 mm because the
smallest step in the coin set is 1.00 mm (2c 18.75 to 10c 19.75). Exceeding half that
step lets a 2c coin enter the 10c recess and sorting fails silently.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
P = json.loads((PROD / "parameters" / "tray.json").read_text(encoding="utf-8"))

COINS = P["coins"]
CLR = P["recess_clearance_mm"]["value"]
BOUND = P["recess_clearance_mm"]["upper_bound_mm"]
NPR = P["coins_per_recess"]
EXTRA = P["recess_extra_depth_mm"]
NW, ND = P["notch_width_mm"], P["notch_depth_mm"]
COLS, ROWS = P["cols"], P["rows"]
PX, PY = P["cell_pitch_x_mm"], P["cell_pitch_y_mm"]
WALL = P["wall_mm"]
RIM = P["rim_mm"]
UNDER = P["under_floor_mm"]
RIM_ABOVE = P["rim_above_field_mm"]
SD, SR = P["slope_depth_mm"], P["slope_rise_mm"]
FIL, MINW = P["edge_fillet_mm"], P["minimum_wall_mm"]
ENV = P["envelope_ceiling_mm"]

FIELD_X = COLS * PX
FIELD_Y = ROWS * PY
OUTER_X = FIELD_X + 2 * RIM
OUTER_Y = FIELD_Y + SD + 2 * RIM
DEPTHS = {c["id"]: c["edge_mm"] * NPR + EXTRA for c in COINS}
SLAB_Z = max(DEPTHS.values()) + UNDER          # slab must carry the deepest recess
OUTER_Z = SLAB_Z + RIM_ABOVE


def _check() -> None:
    if CLR > BOUND:
        raise ValueError(f"recess clearance {CLR} exceeds the separation bound {BOUND}")
    ds = sorted(c["diameter_mm"] for c in COINS)
    step = min(b - a for a, b in zip(ds, ds[1:]))
    if CLR >= step / 2:
        raise ValueError(f"clearance {CLR} >= half the smallest diameter step {step}")
    biggest = max(c["diameter_mm"] for c in COINS) + CLR
    if PX - biggest < MINW or PY - biggest < MINW:
        raise ValueError(f"cell pitch leaves less than {MINW} mm between recesses")
    if RIM < MINW or UNDER < MINW:
        raise ValueError("rim or under-floor below the minimum wall")


def _assert_envelope(solid, name: str) -> None:
    """Check the ACTUAL bounding box, never only the intended dimensions."""
    bb = solid.val().BoundingBox()
    got = [bb.xlen, bb.ylen, bb.zlen]
    if any(g > e + 1e-6 for g, e in zip(got, ENV)):
        raise ValueError(f"{name} actual bounding box {[round(g,2) for g in got]} exceeds ceiling {ENV}")


def tray() -> cq.Workplane:
    _check()
    body = cq.Workplane("XY").box(OUTER_X, OUTER_Y, SLAB_Z, centered=(True, True, False))
    # perimeter rim standing above the slab
    body = body.union(
        cq.Workplane("XY").box(OUTER_X, OUTER_Y, RIM_ABOVE, centered=(True, True, False))
        .translate((0, 0, SLAB_Z))
        .cut(cq.Workplane("XY").box(OUTER_X - 2 * RIM, OUTER_Y - 2 * RIM, RIM_ABOVE,
                                    centered=(True, True, False)).translate((0, 0, SLAB_Z))))
    # rear entry ramp: profile in YZ, extruded along X so it cannot grow the Y envelope
    y0 = -OUTER_Y / 2 + RIM + FIELD_Y
    ramp = (cq.Workplane("YZ")
            .polyline([(y0, SLAB_Z), (y0 + SD, SLAB_Z), (y0 + SD, SLAB_Z + SR)]).close()
            .extrude(OUTER_X - 2 * RIM)
            .translate((-(OUTER_X - 2 * RIM) / 2, 0, 0)))
    body = body.union(ramp)
    # recesses cut down from the slab top, ordered by diameter
    for i, coin in enumerate(sorted(COINS, key=lambda c: c["diameter_mm"])):
        col, row = i % COLS, i // COLS
        x = -FIELD_X / 2 + PX / 2 + col * PX
        y = -OUTER_Y / 2 + RIM + PY / 2 + row * PY
        d = coin["diameter_mm"] + CLR
        depth = DEPTHS[coin["id"]]
        body = body.cut(cq.Workplane("XY").circle(d / 2).extrude(depth)
                        .translate((x, y, SLAB_Z - depth)))
        body = body.cut(cq.Workplane("XY").box(NW, ND * 2, depth, centered=(True, True, False))
                        .translate((x, y - d / 2, SLAB_Z - depth)))
    body = body.edges("|Z").fillet(FIL)
    _assert_envelope(body, "coin-tray")
    return body


def coupon() -> cq.Workplane:
    """hole-gauge-vertical: the 2c/10c separation pair at each candidate clearance."""
    series = P["recess_clearance_mm"]["coupon_series_mm"]
    pair = [c for c in COINS if c["id"] in ("2c", "10c")]
    px, py = 26.0, 26.0
    w, h = len(series) * px + 2 * RIM, 2 * py + 2 * RIM
    c = cq.Workplane("XY").box(w, h, UNDER + 8.0, centered=(True, True, False))
    for i, s in enumerate(series):
        for j, coin in enumerate(sorted(pair, key=lambda k: k["diameter_mm"])):
            x = -w / 2 + RIM + px / 2 + i * px
            y = -h / 2 + RIM + py / 2 + j * py
            c = c.cut(cq.Workplane("XY").circle((coin["diameter_mm"] + s) / 2)
                      .extrude(8.0).translate((x, y, UNDER)))
    return c.edges("|Z").fillet(FIL)


def main() -> int:
    out = PROD / "source" / "generated"
    out.mkdir(parents=True, exist_ok=True)
    for name, solid in (("coin-tray", tray()), ("hole-gauge-vertical", coupon())):
        cq.exporters.export(solid, str(out / f"{name}.step"))
        cq.exporters.export(solid, str(out / f"{name}.stl"),
                            opt={"tolerance": 0.01, "angularTolerance": 0.1})
        bb = solid.val().BoundingBox()
        print(f"{name}: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm")
    ds = sorted(c["diameter_mm"] for c in COINS)
    print(f"clearance {CLR} mm (UNQUALIFIED) | smallest coin step {min(b-a for a,b in zip(ds,ds[1:])):.2f} mm | bound {BOUND} mm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
