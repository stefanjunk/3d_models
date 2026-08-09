# FreeCAD-specific workflow

## Strengths

- interactive measurement and placement;
- Mesh Workbench evaluation/repair/decimation/remesh;
- Part/Part Design for STEP functional parts;
- assembly context and drawings;
- Python console/macros;
- FEM on simplified, meaningful solids.

## Mesh-to-shape caution

`Shape From Mesh` creates Part geometry from mesh facets. On a dense mesh this can produce a huge face-per-triangle shape that is slow and fragile for Boolean operations. Repair and reduce the mesh first, and only convert when the face count and need justify it.

## Recommended hybrid

1. import organic mesh as Mesh object;
2. inspect/repair or create a reduced proxy;
3. import/generate functional STEP solid;
4. position with measured Placement/transforms;
5. use FreeCAD for assembly review and dimensions;
6. perform final mesh Boolean in a mesh-appropriate engine when conversion is impractical;
7. use FEM only on a simplified structural representation with defensible material/boundary assumptions.

## BooleanFragments and Slice

These Part tools are useful on valid B-Rep solids to preserve and inspect all fragments before deciding which pieces to keep. They are not a remedy for invalid dense triangle meshes.
