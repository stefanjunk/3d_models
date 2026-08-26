# FreeCAD route

Use FreeCAD when interactive image tracing, constrained sketches, Part Design solids, datum-driven editing, and print preparation are preferable to code-only CAD. Verify command names against the installed FreeCAD version because workbench organization changes.

## Contents

1. [Set up evidence planes](#set-up-evidence-planes)
2. [Trace constrained sketches](#trace-constrained-sketches)
3. [Build the solid](#build-the-solid)
4. [Use a scan or AI mesh](#use-a-scan-or-ai-mesh)
5. [Appearance and color](#appearance-and-color)
6. [Validation](#validation)
7. [Performance](#performance)

## Set up evidence planes

1. Create a new document and set units to millimeters.
2. Import each source image as an image plane or equivalent reference object.
3. Place front/side/top images on mutually perpendicular datum planes.
4. Scale each plane from the same known physical dimension.
5. Align common landmarks to the same origin and axes.
6. Reduce opacity and lock/freeze placement where supported.

Use the Image scaling command or set the image plane's physical size/placement directly, depending on version. Confirm scale with a Draft/Sketcher dimension; do not trust screen pixels.

Correct perspective outside FreeCAD only when a planar calibration justifies it. If the source is perspective, use it for visual reference rather than tracing every edge as a true orthographic dimension.

## Trace constrained sketches

Create one sketch per meaningful profile or section:

- use construction geometry for centerlines and datums;
- constrain symmetry, coincidence, tangent, horizontal/vertical, and known dimensions;
- use arcs and conics for manufactured curves;
- use B-splines sparingly for freeform silhouettes;
- keep the sketch fully or intentionally constrained;
- name dimensional constraints by requirement ID where practical.

Avoid tracing thousands of bitmap edge points. Fit a smaller curve set and check maximum deviation at important landmarks.

For conflicting views, create separate sketches and section stations. Do not deform a front sketch to solve a side-view problem.

## Build the solid

Use Part Design or Part operations according to topology:

- Pad for extruded profiles;
- Revolution for axisymmetric profiles;
- Additive/subtractive loft for changing sections;
- Additive/subtractive pipe for swept paths;
- Pocket/hole for openings;
- Thickness or controlled inner features for shells;
- datum planes and shape binders for stable cross-body references;
- Boolean bodies for manufacturing splits or inserts.

Model dimensions and interfaces before ornament. Add fillets/chamfers late; reference stable geometry rather than transient edge numbers when possible to reduce topological naming failures.

## Use a scan or AI mesh

Import the mesh as reference or a limited Boolean operand only after repair and reduction.

Recommended hybrid sequence:

1. inspect and repair the mesh in Blender/MeshLab;
2. create a decimated proxy for FreeCAD placement;
3. fit datum planes/cylinders/sections to relevant regions;
4. model functional features as BRep solids;
5. export aligned CAD solids and combine with the detailed mesh in a mesh-aware tool if the final Boolean is too heavy in FreeCAD.

Avoid converting every triangle into a BRep face. Use “Create shape from mesh” only for manageable, purposeful meshes and verify the resulting solid. Dense scans can create huge documents and fragile operations.

## Appearance and color

Use object/view colors for organization and preview. FreeCAD is not the strongest UV/PBR texture-authoring route. For photo textures, matched lighting, or texture projection, move to Blender.

For multi-material printing:

- retain separate bodies with exact alignment;
- export a format/workflow supported by the slicer;
- verify material/body assignments after import;
- do not assume STL preserves colors.

## Validation

### Geometry

- use Measure and constraint values for all critical dimensions;
- run Part CheckGeometry on solids;
- inspect section cuts through thin walls and interfaces;
- verify body count and Boolean result;
- compare front/side/top screenshots or renders from matched cameras;
- keep a spreadsheet or named constraints tied to the requirement ledger.

### Mesh

Use the Mesh workbench/evaluation tools available in the installed version to check and repair:

- duplicated points/facets;
- non-manifold edges;
- holes;
- self-intersections;
- orientation;
- degenerate facets.

Treat automatic repair as a proposed change. Compare bounding box, volume, silhouettes, and critical sections before accepting it.

### Export

Keep FCStd and STEP masters. Create the print mesh with a linear deflection and angular deflection derived from printer capability and curvature. Inspect mesh statistics; a tiny deflection on a large curved object can create unnecessary millions of triangles.

Re-import the exported mesh into a clean document or run `scripts/mesh_audit.py` to catch unit or tessellation surprises. Then slice at the exact print profile.

## Performance

- Hide image planes and meshes not used by the active operation.
- Use low-resolution mesh proxies.
- Split independent bodies and suppress expensive features during blockout.
- Delay fine fillets, textures, and final tessellation.
- Prefer parametric sketches/solids over dense traced point sets.
- Save checkpoints before mesh conversion, Boolean, thickness, or large fillet operations.

Use CadQuery for repeatable scripted generation/testing, OpenSCAD for compact CSG families, and Blender for organic/texture-heavy reconstruction.
