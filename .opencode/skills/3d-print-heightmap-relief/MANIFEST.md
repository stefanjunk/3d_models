# Package manifest

## OpenCode entry point

- `.opencode/skills/3d-print-heightmap-relief/SKILL.md`

## Engineering references

- `00-workflow.md`
- `01-heightmap-fundamentals.md`
- `02-image-requirements-preprocessing.md`
- `03-resolution-memory-printability.md`
- `04-surface-mapping.md`
- `05-openscad.md`
- `06-cadquery.md`
- `07-freecad.md`
- `08-blender.md`
- `09-validation-troubleshooting.md`
- `10-examples.md`
- `11-relief-config-reference.md`
- `sources.md`

## Executable utilities

- image loading/preprocessing;
- physical/print/memory analysis;
- closed relief generation;
- Boolean dispatch;
- mesh validation;
- procedural example images;
- mapping test image;
- example build orchestration;
- self-test.

## Templates

- OpenSCAD flat native height surface and imported patch Boolean;
- CadQuery parametric-base workflow and coarse native pixel relief;
- FreeCAD Part tessellation and mesh Boolean macros;
- Blender UV displacement and STL export.

## Examples

1. Unicorn cylinder gift box.
2. Carbon-fibre rounded desk organizer.
3. Wood-textured honeycomb wall shelf.

Each example contains source art, prepared draft/print maps, JSON configs, CadQuery source, OpenSCAD wrapper, and documentation.

## Verification artifacts

- `tests/self-test-report.json`
- `tests/validation-summary.json`
- `schemas/relief-config.schema.json`

Large transient STL/STEP build products are intentionally not bundled. They are reproducible through `scripts/build_examples.py`.
