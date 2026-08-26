# Casting Negative Molds — OpenCode Skill

A production-oriented OpenCode Agent Skill for designing printable negative molds, masters, cases, and plaster working molds for porcelain, stoneware, gypsum, and plaster.

## Install

Project-local:

```bash
mkdir -p .opencode/skills
cp -R casting-negative-molds .opencode/skills/
```

User-global:

```bash
mkdir -p ~/.config/opencode/skills
cp -R casting-negative-molds ~/.config/opencode/skills/
```

OpenCode discovers the `SKILL.md` and loads the detailed references only when needed.

## Important process distinction

An ordinary sealed FDM/SLA negative is generally suitable as tooling or as a direct mold for compatible gypsum/plaster casts. Conventional ceramic slip casting normally needs an **absorbent plaster working mold**. The printed object is therefore commonly a positive master or a reusable case used to manufacture that plaster mold.

## Included

- Generic workflow and decision gates in `SKILL.md`
- Detailed references for process selection, demolding, mold architecture, memory/resolution, tools, validation, workshop practice, and food-contact ceramics
- Three worked examples and machine-readable example specifications
- Python utilities for mesh preflight, memory estimation, empirical shrinkage, height-map preparation, and mold planning
- Parametric CadQuery and OpenSCAD mold generators
- Blender and FreeCAD command-line baseline generators
- A CadQuery detail-transfer coupon
- Unit/smoke tests
- Build manifest and SHA-256 checksums

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/common/mold_planner.py assets/examples/roman-pillar.json --output plan.md
python scripts/common/shrinkage_calculator.py --final 300 72 72 --shrink 12.0 12.0 13.0
python scripts/common/memory_estimator.py --volume-mm 300 100 100 --voxel-mm 0.25
python scripts/common/mesh_preflight.py input.stl --json report.json
```

Generate the CadQuery demo mold:

```bash
python scripts/cadquery/block_mold.py --demo roman-pillar --output-dir build/cq-demo
```

Generate the OpenSCAD demo halves:

```bash
mkdir -p build/openscad
openscad -o build/openscad/mold_A.stl -D 'part="A"' scripts/openscad/negative_mold.scad
openscad -o build/openscad/mold_B.stl -D 'part="B"' scripts/openscad/negative_mold.scad
```

## Validation status in this package

The common Python utilities, CadQuery generators, and OpenSCAD mold variants were executed and smoke-tested in the package build environment on 2026-08-09. The included test suite passed 7 tests. Blender and FreeCAD scripts were syntax-checked, but their host applications were not installed in that environment, so geometry execution must be validated locally.

## Scope and responsibility

This package supplies engineering guidance and prototype generators. It does not replace material datasheets, kiln/body/glaze qualification, occupational-safety rules, or legal conformity testing for food-contact ware.
