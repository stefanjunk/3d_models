# CadQuery-specific workflow

CadQuery is the preferred generator for precise functional components, not the primary editor of dense organic triangle meshes.

## Keep a B-Rep master

Create stairs, door frames, hinge knuckles, latch seats, sole structures, flanges, screw bosses, and alignment features as parameterized CadQuery solids. Export:

- STEP as the editable/inspection master;
- STL/3MF at a documented tessellation tolerance for mesh handoff.

## Handoff pattern

```python
import cadquery as cq

part = (
    cq.Workplane("XY")
    .box(40, 30, 10)
    .edges("|Z")
    .fillet(3)
)

cq.exporters.export(part, "functional-part.step")
cq.exporters.export(part, "functional-part.stl", tolerance=0.08, angularTolerance=0.12)
```

Use a tessellation tolerance related to print/detail requirements. Extremely low tolerance creates unnecessarily large meshes and can increase Boolean cost.

## Dense mesh rule

CadQuery officially imports CAD-oriented formats such as STEP and DXF, while STL/3MF are export-oriented mesh formats. Do not convert a dense organic mesh into thousands or millions of B-Rep planar faces simply to perform one cut. Instead:

1. measure/fit the organic mesh externally;
2. generate the exact functional geometry in CadQuery;
3. tessellate the functional body;
4. integrate at the mesh stage;
5. retain the STEP and parameters separately.

## Assembly-first option

For prototypes, leave the organic body and CadQuery part separate. Add deliberate seats, fasteners, adhesive lands, clips, or capture geometry. This avoids a risky union and allows material/orientation changes.
