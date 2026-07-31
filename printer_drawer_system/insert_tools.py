"""
Tool organiser insert for the tall drawer.

Left half  – 6 upright slots for small screwdrivers (handle Ø ≤ 25 mm).
Right half – grid of hex-bit pockets (1/4" = 6.35 mm shank) + tweezers slot.
"""

import cadquery as cq
from params import drawer_w, drawer_d, drawer_wt, slot_h_tall, clearance

insert_w  = drawer_w - 2 * drawer_wt - 0.4
insert_d  = drawer_d - drawer_wt - 0.4
insert_h  = slot_h_tall - drawer_wt - 2.0

divider_x = 2.0   # central divider wall between halves

# ─── base block ──────────────────────────────────────────────────────────────
insert = (
    cq.Workplane("XY")
    .box(insert_w, insert_d, insert_h, centered=(True, True, False))
)

# ═══════════════════════════════════════════════════════════════════════════════
# LEFT HALF – screwdriver slots
# ═══════════════════════════════════════════════════════════════════════════════
sd_cols  = 3       # columns of screwdriver holes
sd_rows  = 2       # rows
sd_d     = 26.0    # pocket diameter (fits handle up to ~25 mm)
sd_depth = insert_h - 4.0   # almost full depth
sd_pitch_x = (insert_w / 2 - divider_x / 2 - 4.0) / sd_cols   # auto-fit pitch
sd_pitch_y = (insert_d - 4.0) / sd_rows

left_cx  = -(insert_w / 4 + divider_x / 4)   # centre X of left zone
y_base   = -(insert_d / 2) + sd_pitch_y / 2 + 2.0

for row in range(sd_rows):
    for col in range(sd_cols):
        px = left_cx + (col - (sd_cols - 1) / 2) * sd_pitch_x
        py = y_base + row * sd_pitch_y
        insert = insert.cut(
            cq.Workplane("XY")
            .cylinder(sd_depth, sd_d / 2)
            .translate((px, py, insert_h - sd_depth))
        )

# ═══════════════════════════════════════════════════════════════════════════════
# RIGHT HALF – 1/4" hex bit pockets + tweezers slot
# ═══════════════════════════════════════════════════════════════════════════════
bit_d      =  7.2    # Ø for 1/4" hex bit (6.35 mm across flats + clearance)
bit_depth  = 28.0
bit_pitch  = 11.0
right_cx   =  insert_w / 4 + divider_x / 4   # centre X of right zone
right_w    =  insert_w / 2 - divider_x / 2

bit_cols   = int(right_w    // bit_pitch)
bit_rows   = int((insert_d - 20.0) // bit_pitch)   # leave room for tweezers

bx0 = right_cx - (bit_cols - 1) * bit_pitch / 2
by0 = -(insert_d / 2) + bit_pitch / 2 + 2.0

for row in range(bit_rows):
    for col in range(bit_cols):
        px = bx0 + col * bit_pitch
        py = by0 + row * bit_pitch
        insert = insert.cut(
            cq.Workplane("XY")
            .cylinder(bit_depth, bit_d / 2)
            .translate((px, py, insert_h - bit_depth))
        )

# tweezers / thin-tool slot at back of right zone
tw_w  = right_w - 4.0
tw_d  =  8.0
tw_h  = insert_h - 2.0
tw_cx = right_cx
tw_cy = insert_d / 2 - tw_d / 2 - 2.0
insert = insert.cut(
    cq.Workplane("XY")
    .box(tw_w, tw_d, tw_h, centered=(True, True, False))
    .translate((tw_cx, tw_cy, 2.0))
)

insert = insert.edges(">Z").chamfer(0.8)

if "show_object" in dir():
    show_object(insert, "tool insert", options={"color": "tomato"})
