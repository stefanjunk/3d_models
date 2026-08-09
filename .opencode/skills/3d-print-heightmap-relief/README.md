# OpenCode skill: 3D-print height-map relief

This package converts images into controlled embossing or engraving on printable objects. It combines a tool-neutral image and geometry pipeline with practical integrations for OpenSCAD, CadQuery, FreeCAD, and Blender.

## What is included

- An OpenCode skill at `.opencode/skills/3d-print-heightmap-relief/SKILL.md`.
- 12 focused engineering references.
- 16-bit-aware image preprocessing, physical-scale analysis, mapping, closed relief-patch generation, mesh Boolean, and validation scripts.
- Surface generators for flat planes, cylinders, cones/frustums, rounded rectangular walls, polygon walls, spheres, toruses, polygon-ring faces, and arbitrary sampled grids.
- Tool templates for OpenSCAD, CadQuery, FreeCAD, and Blender.
- Three complete example projects:
  1. a unicorn engraving wrapped around a cylindrical gift box;
  2. carbon-fibre texture around a rounded desk organizer;
  3. consistently oriented wood texture on every surface family of a honeycomb wall shelf.
- Procedural, redistributable example source images and draft/print prepared height maps.
- A JSON Schema, self-test, and validated draft-build report.

## Repository layout

```text
.opencode/skills/3d-print-heightmap-relief/
├── SKILL.md
├── references/
├── scripts/
├── schemas/
├── templates/
├── examples/
└── tests/
```

## Fast start

Copy the `.opencode` directory into the root of an OpenCode project, install the Python requirements, and run:

```bash
python .opencode/skills/3d-print-heightmap-relief/scripts/self_test.py
```

Then load the `3d-print-heightmap-relief` skill in OpenCode or ask the agent to design image relief for a printable object.

See `INSTALL.md` and the skill’s `references/00-workflow.md`.
