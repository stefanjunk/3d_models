"""
Nozzle organiser insert for a standard-height drawer.

Stores M6 printer nozzles (brass/steel V6-style) upright, tip-down.
Each pocket has a narrow lower hole (lets the tip sit) + wider upper bore
(fits the hex body). Fits inside a std drawer.
"""

import cadquery as cq
from params import drawer_w, drawer_d, drawer_wt, slot_h_std, clearance

# ── insert block dimensions ─────────────────────────────────────────────────
insert_w = drawer_w  - 2 * drawer_wt - 0.4   # snug in drawer
insert_d = drawer_d  - drawer_wt - 0.4
insert_h = slot_h_std - drawer_wt - 4.0       # leaves head-room to grab nozzles

# ── pocket geometry (V6-style nozzle) ────────────────────────────────────────
tip_d    =  4.5    # lower bore Ø  (tip + small clearance)
tip_h    =  8.0    # depth of lower bore
body_d   =  8.0    # upper bore Ø  (hex body ~7.0 AF, +clearance)
body_h   =  8.0    # depth of upper bore
pitch_x  = 14.0   # column pitch
pitch_y  = 14.0   # row pitch

cols = int(insert_w // pitch_x)
rows = int(insert_d // pitch_y)

# centre grid inside insert
x0 = -(cols - 1) * pitch_x / 2
y0 =  (rows - 1) * pitch_y / 2

insert = (
    cq.Workplane("XY")
    .box(insert_w, insert_d, insert_h, centered=(True, True, False))
)

# build pocket tool: wide bore on top, narrow bore below
pocket = (
    cq.Workplane("XY")
    .cylinder(body_h, body_d / 2)
    .faces(">Z")
    .workplane()
    .circle(body_d / 2)
    .workplane(offset=body_h)   # dummy — use translate below
)
# Use direct cut approach: two nested cylinders
wide_cut  = cq.Workplane("XY").cylinder(body_h, body_d / 2)
narrow_cut = (
    cq.Workplane("XY")
    .cylinder(tip_h, tip_d / 2)
    .translate((0, 0, body_h))
)
pocket_tool = wide_cut.union(narrow_cut)

# punch pockets at each grid position
for row in range(rows):
    for col in range(cols):
        px = x0 + col * pitch_x
        py = y0 - row * pitch_y
        insert = insert.cut(
            pocket_tool.translate((px, py, 0))
        )

# chamfer top rim of insert for easier placement
insert = insert.edges(">Z").chamfer(1.0)

if "show_object" in dir():
    show_object(insert, "nozzle insert", options={"color": "orange"})
