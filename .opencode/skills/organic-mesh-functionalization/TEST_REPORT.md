# Test report

Test environment date: 2026-08-09.

## Executed successfully

- Python syntax compilation for all bundled `.py` files.
- `inspect_mesh.py` on generated watertight STL meshes.
- `estimate_voxel_memory.py` on mesh-derived bounds.
- `validate_edit.py` on identical meshes and on an ROI-limited surface modification.
- `cadquery_primitives.py` for cylinder, tube, capsule, and rounded-box profiles.
- CadQuery dice-tower cutter and connected staircase exports.
- OpenSCAD dice-tower overlay through full STL render, followed by watertightness inspection.
- `tests/smoke_test.py` end-to-end for the installed Python/CadQuery toolchain.

## Not executed in this environment

- Blender headless script, because Blender is not installed in the runtime.
- FreeCAD macro, because FreeCADCmd is not installed in the runtime.

The Blender and FreeCAD files were syntax-reviewed and are deliberately version-aware templates. Run them first on trivial geometry with the exact installed application version before production data.
