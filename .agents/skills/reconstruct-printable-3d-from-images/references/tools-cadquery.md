# CadQuery route

Use CadQuery for scripted, dimensioned reconstruction of functional or product-like objects. Build a BRep master from traced profiles, measured sections, and explicit parameters; use a mesh tool for organic surfaces that cannot be represented economically as lofts/sweeps.

## Contents

1. [Input preparation](#input-preparation)
2. [Import and reconstruct](#import-and-reconstruct)
3. [Evidence-backed script structure](#evidence-backed-script-structure)
4. [Curves, lofts, and fillets](#curves-lofts-and-fillets)
5. [Functional features](#functional-features)
6. [Validation in code](#validation-in-code)
7. [Export and tessellation](#export-and-tessellation)
8. [Performance](#performance)

## Input preparation

CadQuery is not an image-analysis tool. Convert source evidence into:

- dimensions and datums;
- DXF profiles with known units;
- ordered section points or radii;
- paths for sweeps;
- optional simplified mesh proxies used outside the BRep master.

Trace profiles in a vector editor. Close loops, remove duplicates, keep holes on separate layers, and reduce control points within tolerance.

## Import and reconstruct

Import DXF with explicit layer control and merge tolerance:

```python
import cadquery as cq

profile = (
    cq.importers.importDXF(
        "front-profile.dxf",
        tol=1e-4,
        include=["OUTER", "HOLES"],
    )
    .wires()
    .toPending()
)
body = profile.extrude(18.0, both=True)
```

Use the simplest valid construction:

- `extrude()` for prismatic evidence;
- `revolve()` for rotational profiles;
- `loft()` for measured cross-sections;
- `sweep()` for handles, tubes, and guided transitions;
- `shell()` or offset logic for controlled wall thickness;
- union/cut/intersect for openings and manufacturing splits.

For multi-view work, parameterize section widths/depths at shared Z stations. Fit those sections to front/side silhouettes rather than extruding one view and guessing the other.

## Evidence-backed script structure

```python
from dataclasses import dataclass
import cadquery as cq

@dataclass(frozen=True)
class Params:
    height: float = 120.0          # measured
    width: float = 74.0            # measured
    depth: float = 36.0            # inferred; variant candidate
    wall: float = 1.6              # print requirement
    interface_clearance: float = 0.25

def build(p: Params) -> cq.Workplane:
    assert p.wall > 0
    outer = cq.Workplane("XY").box(p.width, p.depth, p.height)
    inner = (
        cq.Workplane("XY")
        .box(p.width - 2 * p.wall, p.depth - 2 * p.wall, p.height)
        .translate((0, 0, p.wall))
    )
    return outer.cut(inner)
```

Annotate values as measured/requested/inferred in comments or load them from the reconstruction brief. Keep printer compensation separate from nominal geometry where practical.

## Curves, lofts, and fillets

- Use few, meaningful section stations first; add stations only where comparison exposes shape error.
- Keep corresponding vertices/wire orientation consistent across loft sections.
- Prefer analytic arcs/lines to dense traced splines for manufactured objects.
- Apply fillets late and incrementally. Large batches of fillets can fail without revealing which edge caused the problem.
- Preserve the unfilleted intermediate for debugging and dimensional checks.
- Validate thin or near-tangent geometry after every Boolean.

Use a surface/mesh workflow instead when an organic scan would require hundreds of irregular sections. A triangle-to-BRep conversion is usually the wrong bridge.

## Functional features

Reconstruct appearance only after locking:

- mating datums and envelopes;
- insertion path and assembly access;
- clearances and press/snap behavior;
- load path and minimum walls;
- drainage, fastening, cable bend radius, or contact surfaces;
- print orientation and support access.

Use parameters for every interface. Generate fit coupons from the same parameters so compensation remains traceable.

## Validation in code

Check shape validity and dimensions before export:

```python
shape = build(Params()).val()
assert shape.isValid(), "OCCT reports an invalid shape"

bb = shape.BoundingBox()
print({
    "x_mm": bb.xlen,
    "y_mm": bb.ylen,
    "z_mm": bb.zlen,
    "volume_mm3": shape.Volume(),
})
```

Add project-specific asserts for overall dimensions, minimum opening, part count, and expected volume range. Render or export canonical views and compare them to source imagery; BRep validity does not prove visual fidelity.

## Export and tessellation

Keep STEP as the editable/interchange solid when possible. Export print meshes with tolerance based on physical resolution:

```python
from cadquery import exporters

result = build(Params())
exporters.export(result, "model.step")
exporters.export(
    result,
    "model.stl",
    tolerance=0.05,
    angularTolerance=0.1,
    opt={"relative": False},
)
```

Confirm the exact CadQuery version's exporter signature. The official documentation warns that overly small linear/angular tolerances create large meshes and overly large tolerances lose detail. Test several values and compare surface/silhouette change. Do not copy the example tolerance blindly.

Current CadQuery documentation notes that AMF/3MF exporter parameters do not include color/material assignments. Use an assembly or downstream 3MF workflow and verify the result when color matters.

## Performance

- Keep computation in BRep form until final tessellation.
- Avoid dense splines and repeated global fillets.
- Cache or export stable subcomponents during iteration.
- Use binary STL rather than ASCII for large meshes.
- Use coarse tessellation for view matching, final tessellation after acceptance.
- Keep high-resolution organic meshes out of OCCT unless simplified to a manageable proxy.

Use OpenSCAD for simpler highly configurable CSG, FreeCAD for interactive constrained editing, and Blender for organic mesh/sculpt/texture tasks.
