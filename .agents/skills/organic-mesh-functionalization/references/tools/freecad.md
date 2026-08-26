# FreeCAD guidance

## Best role

Use FreeCAD when:

- the functional geometry is STEP/B-Rep;
- interactive Part/Part Design editing is desired;
- mesh-to-shape conversion is limited to a moderate repaired mesh;
- technical drawings, assemblies, or FEM surrogates are required.

## Mesh conversion warning

`Part ShapeFromMesh` can make a shape from a mesh so that Part operations become available. A dense organic mesh may become one B-Rep face per triangle, producing a huge, fragile document. Test on a copy and inspect face count and save time before continuing.

For a high-resolution AI mesh, prefer:

1. repair/segment in Blender;
2. generate exact inserts in FreeCAD/CadQuery;
3. export insert as STEP and tessellated mesh;
4. combine in Blender/Manifold3D;
5. use FreeCAD only for simplified analysis or the exact parts.

## Moderate mesh workflow

1. Import mesh.
2. Analyze and repair in Mesh workbench.
3. Create shape from mesh with a documented sewing tolerance.
4. Convert to solid only if the shell is closed.
5. Refine/remove splitters cautiously.
6. Execute Part Boolean with valid solids.
7. Check geometry and export a checkpoint.

## FEM

Do not mesh the decorative high-poly object directly for engineering conclusions. Build a simplified solid representing wall thickness, interfaces, loads, and supports. FreeCAD FEM can prepare geometry, assign materials and constraints, generate a Netgen/Gmsh mesh, run external solvers, and post-process results.

For printed parts, calibrate material and orientation assumptions with coupons. Use nonlinear/contact models where large deformation or TPU is central.

## Python macro

`examples/freecad/mesh_cut_template.py` demonstrates a guarded mesh-to-shape conversion and a simple cylinder cut. It is a template, not a universal repair pipeline.
