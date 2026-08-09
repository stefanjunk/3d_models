# Validation status

Validation date: 2026-08-09.

## Executed

- Python core image/mapping/geometry pipeline.
- 16-bit grayscale round trip.
- Plane, cylinder, cone/frustum, rounded rectangle wall, polygon wall, sphere band, torus, polygon-ring sectors, and arbitrary NPZ grid.
- CadQuery STL export.
- OpenSCAD mesh Boolean fallback.
- JSON Schema validation for every bundled example config.
- Static compilation of every Python script and FreeCAD macro.
- `build_examples.py` command-line smoke test.

## Full draft builds

| Example | Final triangles | Bodies | Watertight | Non-manifold edges |
|---|---:|---:|---|---:|
| Unicorn cylindrical gift box | 6,542 | 1 | yes | 0 |
| Carbon rounded organizer | 71,144 | 1 | yes | 0 |
| Wood honeycomb shelf | 27,856 | 1 | yes | 0 |

Each result was regenerated from its current CadQuery base and current relief config, then subtracted with OpenSCAD.

## Detailed cutter builds

| Cutter | Triangles | Bodies | Watertight |
|---|---:|---:|---|
| Unicorn cylinder | 874,872 | 1 | yes |
| Carbon rounded organizer | 1,098,656 | 1 | yes |
| Honeycomb outer wall | 528,000 | 1 | yes |
| Honeycomb inner wall | 448,800 | 1 | yes |
| Honeycomb front ring | 108,720 | 6 | yes |
| Honeycomb back ring | 108,720 | 6 | yes |

The six ring bodies are intentional separated sectors. They are used together as Boolean tools; the final shelf is one body.

## Not runtime-executed in this environment

- Blender was unavailable; the Blender template was statically compiled.
- FreeCADCmd was unavailable; the macros were statically compiled.
- `manifold3d` was unavailable; the tested fallback was OpenSCAD.

See `validation-summary.json` for structured details and exact package versions.
