"""
Drawer frame / housing.

Coordinate system (all centred on the frame body):
  X  – width   (left ↔ right)
  Y  – depth   (front ↔ back, positive = into the frame)
  Z  – height  (bottom ↔ top)

Front face is at Y = -frame_od/2  → open (no front wall).
Back wall occupies Y = [frame_od/2 - wall_t, frame_od/2].
"""

import cadquery as cq
from params import (
    wall_t, shelf_t, clearance,
    frame_iw, frame_id, frame_ih,
    frame_ow, frame_oh, frame_od,
    SLOTS,
)

# ── outer shell (box centred at origin) ─────────────────────────────────────
frame = cq.Workplane("XY").box(frame_ow, frame_od, frame_oh)

# ── subtract interior void (front is open; back wall remains) ────────────────
# Interior Y centre is shifted by wall_t/2 toward front so back wall stays.
interior = (
    cq.Workplane("XY")
    .center(0, -wall_t / 2)
    .box(frame_iw, frame_id, frame_ih)
)
frame = frame.cut(interior)

# ── add horizontal shelf dividers ────────────────────────────────────────────
# Walk slots bottom→top and insert a shelf after each (except the last).
z_bottom_inner = -frame_oh / 2 + wall_t   # absolute Z of inner bottom surface
z_cur = z_bottom_inner

for i, slot_h in enumerate(SLOTS[:-1]):
    z_cur += slot_h
    shelf_z_centre = z_cur + shelf_t / 2
    shelf = (
        cq.Workplane("XY")
        .center(0, -wall_t / 2)
        .box(frame_iw, frame_id, shelf_t)
        .translate((0, 0, shelf_z_centre))
    )
    frame = frame.union(shelf)
    z_cur += shelf_t

# ── optional: small finger notch on each slot opening ─────────────────────────
# Cuts a semicircle at the front-bottom edge of every slot so you can reach in.
notch_r  = 10.0
notch_d  =  6.0   # how deep the notch goes into the front face
z_cur    = z_bottom_inner

for slot_h in SLOTS:
    slot_z_centre = z_cur + slot_h / 2
    notch = (
        cq.Workplane("XZ")
        .center(0, slot_z_centre - slot_h / 2 + notch_r)
        .circle(notch_r)
        .extrude(notch_d)
        .translate((0, -frame_od / 2, 0))
    )
    frame = frame.cut(notch)
    z_cur += slot_h + shelf_t

if "show_object" in dir():
    show_object(frame, "frame", options={"alpha": 0.4, "color": "gray"})
