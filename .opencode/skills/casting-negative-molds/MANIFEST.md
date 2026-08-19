# Package manifest

## Identity

- Package: `casting-negative-molds`
- Version: `1.0.0`
- Date: `2026-08-09`
- Entry point: `SKILL.md`
- License: MIT
- Intended host: OpenCode Agent Skills

## Contents

| Path | Purpose |
|---|---|
| `SKILL.md` | Concise routing logic, mandatory engineering workflow, stop conditions, and reference map |
| `README.md` | Installation, quick-start commands, package scope, and validation status |
| `references/` | Process, demolding, architectures, memory/resolution, workshop practice, tool workflows, validation, food contact, examples, and research sources |
| `assets/mold-spec.schema.json` | JSON Schema for machine-readable casting/mold specifications |
| `assets/examples/` | Roman pillar, sunflower tile, and food-serving bowl specifications |
| `scripts/common/` | Mesh preflight, memory estimation, shrinkage compensation, height-map preparation, and plan generation |
| `scripts/cadquery/` | Parametric split block-mold/case generator and detail-transfer coupon |
| `scripts/openscad/` | Parametric block, hollow-block, conformal-shell, and ribbed-shell mold variants |
| `scripts/blender/` | Blender batch baseline for mesh cleanup, booleans, split parts, keys, sprue, and export |
| `scripts/freecad/` | FreeCAD command-line baseline for imported solids, block subtraction, splitting, keys, sprue, and export |
| `tests/` | Seven automated tests plus a cross-tool smoke-test script |
| `checksums.sha256` | SHA-256 checksums for package files, generated during packaging |

## Executed validation

Validation was executed in the package build environment on `2026-08-09`.

| Component | Result | Environment or note |
|---|---|---|
| Python syntax | Passed | Python 3.13.5 |
| Automated tests | **7 passed** | `python -m pytest -q tests` |
| Example JSON Schema validation | Passed | all three example specifications |
| Internal relative Markdown links | Passed | no missing or escaping targets |
| Common Python utilities | Executed | NumPy 2.3.5, Pillow 12.3.0, trimesh 4.11.1 |
| CadQuery generators | Executed | CadQuery 2.8.0; STEP/STL output generated |
| CadQuery mold mesh preflight | Passed | one component, watertight, zero boundary and non-manifold edges |
| OpenSCAD generator | Executed | OpenSCAD 2021.01; block/hollow/conformal variants exercised during development and hollow variant in final smoke test |
| OpenSCAD mold mesh preflight | Passed | one component, watertight, zero boundary and non-manifold edges |
| Blender generator | Static only | Python syntax checked; Blender host was not installed in the build environment |
| FreeCAD generator | Static only | Python syntax checked; FreeCAD host was not installed in the build environment |

Reproduce the main validation with:

```bash
bash tests/smoke_test.sh
```

## Important scope boundaries

- Draft-angle output from a mesh screen is indicative; collision-based extraction tests on every mold section remain mandatory.
- Printer resolution, plaster ratios, ceramic shrinkage, release systems, glaze/firing schedules, and dishwasher performance are process-specific and require physical coupons.
- A dense sealed print is not automatically a conventional ceramic slip-casting working mold; the workflow normally uses an absorbent plaster mold unless a validated porous-tool process is deliberately selected.
- Food-contact suitability is a property of the finished fired body/glaze/decoration/firing system under its actual use conditions and is not established by this package.
