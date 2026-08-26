# Print and integration

Start with 0.4 mm nozzle, 0.2 mm layers, four perimeters, and 25% infill. Increase perimeters before increasing infill for pins, hooks, bosses, and gears. Use PETG/PA/PP for cyclic flexures and snaps.

Keep each sample's print orientation during calibration. When integrating it into a product, re-evaluate layer direction relative to the load. Never scale hardware pockets or clearances uniformly. Rebuild interface dimensions parametrically.

Use `print_plate.stl` for physical calibration and `parts/part_XX.stl` for component import. The individual part files are translated to their local origin; `components.json` records the original print-plate transformation.
