"""CadQuery template: create exact functional geometry and controlled mesh handoff."""
from pathlib import Path
import cadquery as cq

OUT = Path("exports")
OUT.mkdir(exist_ok=True)

width = 40.0
depth = 30.0
height = 10.0
radius = 3.0

part = cq.Workplane("XY").box(width, depth, height).edges("|Z").fillet(radius)

cq.exporters.export(part, str(OUT / "functional-part.step"))
cq.exporters.export(
    part,
    str(OUT / "functional-part.stl"),
    tolerance=0.08,
    angularTolerance=0.12,
)
