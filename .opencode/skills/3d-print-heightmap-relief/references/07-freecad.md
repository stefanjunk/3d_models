# 07 — FreeCAD workflow

## Recommended role

Use FreeCAD for:

- parametric Part/Part Design bases;
- STEP import/export;
- visual inspection and measurement;
- controlled conversion of a B-rep shape to mesh;
- Mesh workbench repair and mesh Boolean operations;
- manual placement when coordinate systems need inspection.

As with CadQuery, keep dense image relief as a mesh rather than converting every triangle into a Part face.

## Workflow A: Part base to mesh relief

1. Model or import the base as a Part/Part Design solid.
2. Save the editable FCStd and export STEP.
3. Tessellate the base with controlled linear/angular deflection.
4. Generate the relief patch externally.
5. Perform a mesh difference/union.
6. inspect and validate the result.
7. export STL or 3MF through the chosen downstream path.

The included macros:

- `templates/freecad/part_to_mesh_relief.FCMacro`
- `templates/freecad/mesh_relief_boolean.FCMacro`

## Tessellation

`MeshPart.meshFromShape` accepts shape, linear deflection, angular deflection, and a relative/absolute choice. Use absolute millimetre-scale deflection for reproducibility.

A very small linear deflection can create excessive triangles. Match it to visible curvature and relief mesh pitch.

## Mesh Boolean

FreeCAD’s Mesh module exposes mesh Boolean operations. API names can vary by release/build; the template uses difference/unite/intersect style methods and is intentionally short enough to adapt.

Before Boolean:

- both meshes should be closed;
- normals should be harmonized;
- duplicated points should be removed;
- cutter should overlap the surface;
- coordinate units and placement should match.

After Boolean, run the external validator as a second implementation check.

## Workflow B: GUI displacement

FreeCAD is not primarily a UV texture/displacement application. For arbitrary UV-mapped displacement, Blender is usually better. For simple planar relief, an imported height surface or mesh can be positioned and Booleaned in FreeCAD.

## Mesh-to-Part conversion warning

Converting a dense relief mesh to a Part shape can create a face per triangle. Refine operations may not merge arbitrary textured facets. The resulting shape can be very large and Boolean operations may become fragile.

Only convert when:

- the mesh is strongly decimated;
- a downstream Part-only operation is unavoidable;
- topology has been validated;
- the cost is understood.

## Placement

FreeCAD object Placement can translate/rotate the patch, but it is better to generate in final coordinates when possible. Store transformations in scripts, not only in a saved GUI state.

For inner surfaces, verify the cutter enters the wall, not the cavity. A constant-white test map makes this obvious.

## Repair

Useful checks in Mesh workbench or scripting include:

- duplicated points/facets;
- flipped normals;
- non-manifold edges;
- self-intersections;
- holes;
- connected components.

Do not automatically close large holes without understanding whether they are intended openings.

## Parametric update cycle

When base dimensions change:

1. regenerate STEP/base STL;
2. recompute physical image width and surface configuration;
3. regenerate the patch;
4. Boolean again;
5. revalidate.

Do not scale a finished textured STL nonuniformly as a substitute. That changes depth, feature width, and clearances.

## FreeCAD-specific issues

### Boolean command disabled or fails

Ensure objects are meshes, not a mixture of Part and Mesh. Convert the base once, then operate mesh-to-mesh.

### Result normals are inconsistent

Harmonize normals and validate winding. An STL viewer may shade a broken mesh plausibly.

### Mesh is too dense for the GUI

Use command-line macros, increase mesh pitch/deflection, split surface families, and avoid displaying all intermediate cutters simultaneously.

### FCStd becomes huge

Do not embed every high-resolution intermediate unless needed. Keep generated STL/report files alongside the project.

## Deliverables

- FCStd or parametric source;
- STEP base;
- tessellation macro/settings;
- relief config and height map;
- cutter STL;
- Boolean macro;
- final validated mesh.
