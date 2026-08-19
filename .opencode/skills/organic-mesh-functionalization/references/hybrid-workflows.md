# Recommended hybrid workflows

## Default production route

```text
AI mesh
→ Trimesh baseline report
→ Blender cleanup/segmentation and proxy
→ CadQuery functional cutters/inserts
→ Blender Exact/Manifold or Manifold3D combination
→ Trimesh preservation/topology validation
→ slicer validation
→ interface coupon
→ full print
```

This route keeps organic detail in a mesh-native tool and dimensional interfaces in a CAD kernel.

## Dirty mesh route

```text
AI mesh
→ isolate ROI
→ Blender/OpenVDB voxel reconstruction
→ preservation seam with original exterior
→ CadQuery insert
→ mesh union
→ distance heat map and topology checks
```

## Constant-wall hollowing route

```text
validated outer mesh
→ sparse/narrow-band SDF
→ inward level-set offset
→ subtract inner volume
→ add drain/access openings
→ marching cubes / volume-to-mesh
→ topology and thickness validation
```

## Full replacement route

```text
AI mesh as reference
→ landmarks and section extraction
→ parametric replacement body
→ retain selected decorative shell/skirt only
→ design seam/flange
→ combine or print as assembly
```

## Why not one tool?

- Blender understands and edits organic topology but is not the best source of exact mechanical interfaces.
- CadQuery/FreeCAD create exact geometry but do not benefit from converting millions of mesh triangles into CAD faces.
- OpenSCAD is reproducible but weak at repair and organic fitting.
- SDF/voxel methods are robust for topology but discretize detail and can consume large memory.
- Trimesh is excellent for automation and validation but is not a full interactive modeler.

## Authoritative sources

Keep the organic archive mesh and parametric CAD scripts as separate authorities. The final STL/3MF is a derived manufacturing artifact, not the sole editable source.
