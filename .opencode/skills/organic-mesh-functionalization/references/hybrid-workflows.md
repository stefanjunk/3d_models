# Hybrid workflows

## Precise insert into organic body

```text
Trimesh/Blender: inspect and fit datums
CadQuery: generate insert and seat cutter
CadQuery: export STEP + controlled STL
Manifold/Blender: subtract seat, optionally union insert
Trimesh: validate and compare protected surface
FreeCAD: assembly drawing/FEM if useful
```

## Local voxel transition

```text
full mesh -> crop ROI + margin
functional part -> mesh at suitable tolerance
both -> signed field/local voxel Boolean
marching cubes -> local fused result
stitch/Boolean with untouched source
protected-surface and seam validation
```

## Separate assembly

```text
organic shell with parametric pocket/flange
+ separate functional component
+ purchased screws/magnets/inserts if appropriate
```

This is often the safest and most maintainable result. Integrated printing is preferred only when it improves assembly, alignment, support strategy, weight, or cost without creating a single unserviceable failure point.

## Interface design

A good hybrid interface includes:

- a datum and anti-rotation feature;
- sufficient seating land;
- print-calibrated clearance;
- load path into thicker material;
- accessible assembly direction;
- tolerance for adhesive or insert installation;
- drain/vent path where enclosed;
- coupon geometry for testing before the full object.
