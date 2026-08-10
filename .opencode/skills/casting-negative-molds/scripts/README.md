# Script index

## Common utilities

- `common/mesh_preflight.py` — manifold/topology, dimensions, components, quality, and draft-screen report
- `common/memory_estimator.py` — voxel-grid and height-field mesh planning
- `common/shrinkage_calculator.py` — anisotropic oversize from percentages or measured coupons
- Height-map preprocessing is owned by
  `../../3d-print-heightmap-relief/scripts/prepare_heightmap.py`.
- `common/mold_planner.py` — deterministic Markdown plan from `assets/mold-spec.schema.json`

## Generators

- `cadquery/block_mold.py` — tested STEP/demo two-part block mold with keys, sprue, vents, STEP/STL exports, and manifest
- `cadquery/detail_coupon.py` — tested planar or curved feature-transfer coupon and direct negative tray
- `openscad/negative_mold.scad` — tested block, hollow-block, conformal-shell, and ribbed-shell baseline
- `blender/negative_mold.py` — batch baseline for organic meshes; requires Blender host
- `freecad/negative_mold.py` — Part/mesh baseline; requires FreeCADCmd host

## Testing

```bash
bash tests/smoke_test.sh
```

The smoke test executes common tools, CadQuery, and OpenSCAD when installed. Blender and FreeCAD scripts are syntax-checked by normal Python compilation but need their host application for geometry execution.
