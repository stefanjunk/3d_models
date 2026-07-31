"""
Parametric drawer body.

Usage:
    from drawer import make_drawer
    d = make_drawer(slot_h)   # pass the slot height this drawer lives in

The returned solid's front face is at Y=0 (the frame's open face).
The body extends in the +Y direction into the frame.
"""

import cadquery as cq
from params import (
    wall_t, shelf_t, clearance,
    frame_iw, frame_id, frame_ow, frame_od,
    drawer_w, drawer_d, drawer_wt,
    handle_h, handle_w, handle_d, fp_thick,
    slot_h_std, slot_h_tall,
)


def make_drawer(slot_h: float) -> cq.Workplane:
    """Return a drawer sized for *slot_h* (interior slot height)."""

    body_h = slot_h - 2 * clearance   # outer height of sliding body
    inner_w = drawer_w - 2 * drawer_wt
    inner_d = drawer_d - drawer_wt     # open at front
    inner_h = body_h  - drawer_wt     # open at top

    # ── tray body (closed bottom, 3 walls, open top + open front) ───────────
    body = (
        cq.Workplane("XY")
        .box(drawer_w, drawer_d, body_h, centered=(True, False, False))
    )
    # hollow out (leave bottom floor + side walls + back wall)
    body = body.cut(
        cq.Workplane("XY")
        .box(inner_w, inner_d, inner_h + 1,   # +1 so cut exits top face
             centered=(True, False, False))
        .translate((0, drawer_wt, drawer_wt))
    )

    # ── front panel (sits at Y=0, wider than body to act as drawer stop) ─────
    fp_w = frame_ow + 2.0           # 2 mm wider than frame on each side
    fp_h = body_h + 2 * clearance   # flush with slot including clearance gaps

    front_panel = (
        cq.Workplane("XY")
        .box(fp_w, fp_thick, fp_h, centered=(True, False, False))
        .translate((0, -fp_thick, 0))
    )

    # ── handle (D-pull centred on front panel) ────────────────────────────────
    handle = (
        cq.Workplane("XY")
        .box(handle_w, handle_d, handle_h, centered=(True, False, False))
        .translate((0, -fp_thick - handle_d, (fp_h - handle_h) / 2))
    )
    # round the front corners of the handle
    handle = (
        handle
        .edges("|Z and >Y")
        .fillet(3.0)
        .edges(">Y and |X")
        .fillet(2.0)
    )

    return body.union(front_panel).union(handle)


# Pre-built instances for import
drawer_std  = make_drawer(slot_h_std)
drawer_tall = make_drawer(slot_h_tall)

if "show_object" in dir():
    show_object(drawer_std,  "drawer_std",  options={"color": "dodgerblue"})
    show_object(drawer_tall, "drawer_tall", options={"color": "steelblue"})
