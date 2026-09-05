"""MM-ORG-042 DIN A6 postcard archive divider set - parametric source.

Generates the lane block and the fit coupon that the calibration gate requires.
Every fit-relevant dimension comes from parameters/divider.json; nothing is hard coded.
The lane clearance is UNQUALIFIED on this process and is a placeholder until a coupon
qualifies xy_clearance_sliding for Anycubic Kobra 3 Max / SUNLU PETG / 0.4 mm.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
P = json.loads((PROD / "parameters" / "divider.json").read_text(encoding="utf-8"))

MEDIA_W = P["media"]["width_mm"]
CLR = P["lane_clearance_mm"]["value"]
N = P["lane_count"]
PITCH = P["lane_pitch_mm"]
WALL = P["wall_mm"]
FLOOR = P["floor_mm"]
DEPTH = P["lane_depth_mm"]
TAB_H = P["tab_height_mm"]
TAB_W = P["tab_width_mm"]
TAB_T = P["tab_thickness_mm"]
FILLET = P["edge_fillet_mm"]
MIN_WALL = P["minimum_wall_mm"]
ENV = P["envelope_ceiling_mm"]

LANE_LEN = MEDIA_W + CLR              # clear length along the card's 105 mm edge
OUTER_LEN = LANE_LEN + 2 * WALL
OUTER_W = N * PITCH + WALL
OUTER_H = FLOOR + DEPTH


def _check() -> None:
    if WALL < MIN_WALL:
        raise ValueError(f"wall {WALL} below minimum wall {MIN_WALL}")
    if TAB_T < MIN_WALL:
        raise ValueError(f"tab thickness {TAB_T} below minimum wall {MIN_WALL}")
    if PITCH - WALL <= 0:
        raise ValueError("lane pitch must exceed the wall thickness")
    got = [OUTER_W, OUTER_LEN, OUTER_H + TAB_H]
    if any(g > e + 1e-6 for g, e in zip(got, ENV)):
        raise ValueError(f"generated envelope {got} exceeds ceiling {ENV}")


def block() -> cq.Workplane:
    """Open-top lane block: open top, one open long side, flat underside."""
    _check()
    body = cq.Workplane("XY").box(OUTER_W, OUTER_LEN, OUTER_H, centered=(True, True, False))
    # cut each lane from above; the front long side is opened afterwards
    for i in range(N):
        x = -OUTER_W / 2 + WALL + PITCH * i + (PITCH - WALL) / 2
        body = body.cut(
            cq.Workplane("XY").box(PITCH - WALL, LANE_LEN, DEPTH, centered=(True, True, False))
            .translate((x, 0, FLOOR))
        )
    # open one long side so the media is visible and reachable edge-on
    body = body.cut(
        cq.Workplane("XY").box(OUTER_W + 2, WALL + 0.2, DEPTH, centered=(True, True, False))
        .translate((0, -OUTER_LEN / 2 + WALL / 2 - 0.1, FLOOR))
    )
    # index tabs standing on the rear wall, one per lane, blank faces
    for i in range(N):
        x = -OUTER_W / 2 + WALL + PITCH * i + (PITCH - WALL) / 2
        body = body.union(
            cq.Workplane("XY").box(TAB_W, TAB_T, TAB_H, centered=(True, True, False))
            .translate((x, OUTER_LEN / 2 - WALL / 2, OUTER_H))
        )
    return body.edges("|Z").fillet(FILLET)


def coupon() -> cq.Workplane:
    """fit-coupon-xy-series: five short lanes at the candidate clearances."""
    series = P["lane_clearance_mm"]["coupon_series_mm"]
    depth, length = 14.0, 26.0
    w = len(series) * PITCH + WALL
    c = cq.Workplane("XY").box(w, MEDIA_W + max(series) + 2 * WALL, FLOOR + depth,
                               centered=(True, True, False))
    for i, s in enumerate(series):
        x = -w / 2 + WALL + PITCH * i + (PITCH - WALL) / 2
        c = c.cut(cq.Workplane("XY").box(PITCH - WALL, MEDIA_W + s, depth, centered=(True, True, False))
                  .translate((x, 0, FLOOR)))
    return c.edges("|Z").fillet(FILLET)


def main() -> int:
    out = PROD / "source" / "generated"
    out.mkdir(parents=True, exist_ok=True)
    for name, solid in (("divider-block", block()), ("fit-coupon-xy-series", coupon())):
        cq.exporters.export(solid, str(out / f"{name}.step"))
        cq.exporters.export(solid, str(out / f"{name}.stl"),
                            opt={"tolerance": 0.01, "angularTolerance": 0.1})
        bb = solid.val().BoundingBox()
        print(f"{name}: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm")
    print(f"lane clear length {LANE_LEN:.2f} mm = A6 {MEDIA_W} + clearance {CLR} (UNQUALIFIED)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
