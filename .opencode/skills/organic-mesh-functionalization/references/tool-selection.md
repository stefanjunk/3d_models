# Tool selection for organic mesh functionalization

Choose the representation of the **operation**, not only the representation of the input.

## Decision table

| Situation | Primary tool | Why | Avoid |
|---|---|---|---|
| Dense STL/OBJ/GLB, visual segmentation, local organic edits | Blender | Native mesh editing, modifiers, Voxel Remesh, Shrinkwrap, scripting | Face-per-triangle B-Rep conversion |
| Clean closed mesh plus simple cylinder/box/hole | OpenSCAD | Small deterministic CSG script and CLI export | Repairing invalid input in OpenSCAD |
| Precise stairs, hinges, doors, inserts, flanges, seats | CadQuery | Parametric B-Rep, STEP master, exact dimensions | Importing dense STL as the design master |
| Interactive measurement, STEP assembly, mesh diagnostics, FEM | FreeCAD | Mesh/Part/FEM workbenches and visual placement | Huge mesh-to-shape conversion without reduction |
| Headless closed-mesh Boolean and reports | Trimesh + Manifold3D | Deterministic scripting and guaranteed-manifold engine for valid inputs | Treating repair as automatically dimension-preserving |
| Bad topology, complex hollowing, uniform offsets, blended fusion | Blender Voxel Remesh or SDF | Reconstructs volume robustly | Global high-resolution voxelization by default |

## Recommended routing questions

1. Is the source a triangle mesh or STEP/B-Rep?
2. Is the source a valid closed volume?
3. Must fine exterior detail be preserved exactly, approximately, or only visually?
4. Is the operation a primitive CSG, precise mechanical feature, conformal surface, or organic replacement?
5. Can the new functional part remain separate?
6. Is STEP editability required for the new component?
7. Is the intended operation local enough to crop?
8. What maximum memory and runtime are acceptable?
9. What evidence will prove that protected geometry did not change?

## Default hybrid route

```text
high-resolution organic mesh
  -> Trimesh baseline report
  -> Blender proxy and ROI segmentation
  -> CadQuery/OpenSCAD functional part
  -> STEP retained as master
  -> controlled STL/3MF tessellation
  -> Manifold3D or Blender Exact integration
  -> Trimesh validation + section review
  -> slicer + physical coupon
```

Keep the functional part as a separate assembly during early iterations. Fuse it only when integrated printing is an explicit benefit and the union can be verified.
