# Modifying existing organic models

## Default stack

```text
Blender or Blender Python
  -> visual inspection, cleanup, remesh, sculpt, cavity/cutter boolean
Trimesh
  -> independent bounds/body/topology/volume validation
Manifold3D (optional)
  -> robust boolean operations on already valid manifold meshes
NumPy/SDF/scikit-image (optional)
  -> equal-offset hollowing, field-driven cavities, dense texture/cells
CadQuery (hybrid)
  -> exact battery boxes, fastener interfaces, bearing seats, flanges
```

## Add a defined cavity

1. preserve the original mesh;
2. apply units/transforms;
3. inspect nonmanifold/self-intersection/internal shells;
4. remesh only if needed and document voxel size;
5. create a parameterized cutter with access/opening and minimum-wall envelope;
6. boolean difference;
7. inspect thin regions and trapped volumes;
8. validate and slice the exported result.

## Hollow an organic body

- `Solidify` is suitable for reasonably clean surfaces where offsets do not self-intersect.
- Scaling a duplicate inward does **not** create equal wall thickness except for special shapes.
- SDF/voxel offsets are robust for complex topology but resolution-limited and memory-intensive.
- Add drain/vent/inspection openings where trapped material or inaccessible support would result.

## Hybrid precision interface

Generate the exact connector/battery/fastener cutter in CadQuery, export it as STEP/STL, and use it in Blender as a boolean cutter. Preserve the cutter parameters and coordinate convention so the organic body can be regenerated.
