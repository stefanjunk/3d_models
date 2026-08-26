# Dice tower example

This example separates the decorated shell from precise functional bodies.

1. Fit `tower_axis`, `inner_radius`, and `usable_height` from source cross-sections.
2. Generate `interior-cutter`, `top-opening`, `bottom-opening`, and `stair-insert` with `cadquery_dice_parts.py`.
3. Update `blender-operations.json` with the generated paths and source mesh.
4. Run the Blender pipeline.
5. Validate exterior preservation with `edit-roi.json` and test the die path physically.

The sample dimensions are placeholders and must not be applied to an unmeasured mesh.
