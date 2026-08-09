# Decorative dice tower functional core

This example assumes an external high-resolution decorative shell whose roughly cylindrical tower axis is Z and whose courtyard projects toward negative Y. The script generates only the parametric functional geometry:

- inner core cutter;
- roof entry cutter;
- courtyard exit cutter;
- alternating inclined baffle/stair insert.

The organic source is intentionally not included. Fit `core_radius`, `tower_height`, and transforms from cross-sections of the real mesh. Prototype the baffle insert separately before fusing it.

## Generate

```bash
python functional_parts.py --out generated
```

## Suggested integration

1. Validate and orient the source mesh.
2. Subtract `core-cutter.stl`, `entry-cutter.stl`, and `exit-cutter.stl` with Manifold3D or Blender Exact.
3. Keep `stair-insert.stl` separate, captured by ledges or an access roof during early tests.
4. Inspect cross-sections every 10–15 mm and perform repeated drop tests using the largest die.
