"""
Screw organiser insert – three labelled zones for M2 / M3 / M4 screws.

The insert is divided into 3 equal bands along Y.
Each band has a grid of cylindrical pockets sized for its screw class.
Thin ridges between bands serve as dividers.
"""

import cadquery as cq
from params import drawer_w, drawer_d, drawer_wt, slot_h_std, clearance

insert_w = drawer_w  - 2 * drawer_wt - 0.4
insert_d = drawer_d  - drawer_wt - 0.4
insert_h = slot_h_std - drawer_wt - 2.0

ridge_t  = 2.0   # thickness of zone-divider ridges

# ── screw pocket parameters [M2, M3, M4] ─────────────────────────────────────
ZONES = [
    dict(label="M2", hole_d=2.6, pitch=6.0,  depth=14.0),
    dict(label="M3", hole_d=3.6, pitch=7.5,  depth=18.0),
    dict(label="M4", hole_d=4.6, pitch=9.0,  depth=22.0),
]

zone_d = (insert_d - 2 * ridge_t) / 3   # usable depth per zone

insert = (
    cq.Workplane("XY")
    .box(insert_w, insert_d, insert_h, centered=(True, True, False))
)

# ── punch pockets zone by zone ────────────────────────────────────────────────
# Y goes from -insert_d/2 (front) to +insert_d/2 (back)
y_start = -insert_d / 2

for i, z in enumerate(ZONES):
    # zone occupies y_start → y_start + zone_d (then a ridge)
    zone_y_centre = y_start + zone_d / 2
    pitch   = z["pitch"]
    hole_r  = z["hole_d"] / 2
    depth   = min(z["depth"], insert_h - 1.0)   # never punch through

    cols = int(insert_w // pitch)
    rows = int(zone_d   // pitch)
    x0   = -(cols - 1) * pitch / 2
    y0   =  zone_y_centre - (rows - 1) * pitch / 2

    for row in range(rows):
        for col in range(cols):
            px = x0 + col * pitch
            py = y0 + row * pitch
            insert = insert.cut(
                cq.Workplane("XY")
                .cylinder(depth, hole_r)
                .translate((px, py, insert_h - depth))
            )

    y_start += zone_d + ridge_t

# chamfer top
insert = insert.edges(">Z").chamfer(0.8)

if "show_object" in dir():
    show_object(insert, "screw insert", options={"color": "yellowgreen"})
