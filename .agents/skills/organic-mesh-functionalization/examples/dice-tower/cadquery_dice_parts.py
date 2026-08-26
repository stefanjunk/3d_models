#!/usr/bin/env python3
from pathlib import Path
import cadquery as cq
from cadquery import exporters

OUT = Path("generated")
OUT.mkdir(exist_ok=True)

# Replace with measured values in millimeters.
inner_radius = 28.0
usable_height = 105.0
wall_clearance = 0.4
portal_width = 25.0
portal_height = 24.0
step_count = 7
step_rise = 12.0
step_run = 15.0
step_width = 45.0
step_thickness = 3.0

interior = cq.Workplane("XY").circle(inner_radius).extrude(usable_height / 2, both=True)
top_opening = cq.Workplane("XY").box(portal_width, portal_width, 20, centered=(True, True, True)).translate((0, 0, usable_height / 2))
bottom_opening = cq.Workplane("XZ").box(portal_width, 30, portal_height, centered=(True, True, True)).translate((0, inner_radius, -usable_height / 2 + portal_height / 2))

stairs = None
for i in range(step_count):
    z = -usable_height / 2 + 12 + i * step_rise
    y = inner_radius - 8 - i * step_run * 0.12
    step = cq.Workplane("XY").box(step_width, step_run, step_thickness, centered=(True, True, True)).translate((0, y, z))
    # A narrow side riser connects each tread to the previous one while
    # leaving most of the dice path open. Replace with a measured stringer
    # or wall attachment for the actual tower.
    if i > 0:
        riser = (cq.Workplane("XY")
                 .box(4.0, step_run, step_rise + step_thickness, centered=(True, True, True))
                 .translate((-step_width / 2 + 2.0, y, z - step_rise / 2)))
        step = step.union(riser)
    stairs = step if stairs is None else stairs.union(step)
stairs = stairs.clean()

for name, shape in {
    "interior-cutter": interior,
    "top-opening": top_opening,
    "bottom-opening": bottom_opening,
    "stair-insert": stairs,
}.items():
    exporters.export(shape, str(OUT / f"{name}.step"))
    exporters.export(shape, str(OUT / f"{name}.stl"), tolerance=0.05)
