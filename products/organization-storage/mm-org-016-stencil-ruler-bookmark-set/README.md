# MM-ORG-016 Stencil-ruler bookmark set

Fully parametric clip-free journal tool set derived from SKU-026. It contains independent native 5 mm and 4 mm layout plates, a twelve-shape `Signal-12` plate and an optional minimum-feature coupon. All geometry is built from project-owned analytic primitives without fonts or external art.

## Primary files

- Edit `config/model-parameters.json`.
- Regenerate STEP, STL, 3MF and reports with `python cad/build.py`.
- Run the twelve deterministic tests with `python -m pytest -q tests/test_parameters.py`.
- Slice `exports/3mf/DRAFT-MM-ORG-016-stencil-ruler-bookmark-set-0.1.0-draft.1.3mf` or use the individual production STL files.
- Print and qualify the coupon before the three production plates.

## Digital candidate status

- Three plates: each 142 × 40 × 0.8 mm, watertight and independently audited.
- Coupon: 90 × 32 × 0.8 mm with 0.8–1.6 mm slots and holes, watertight and independently audited.
- Exact Anycubic Slicer Next preflight: PASS, four layers, 3,262 s estimate, one tool and no native object warnings.
- Aggregate draft validation: PASS; physical edge, paper, ink, trace, flex and cycle tests remain deliberately deferred.

See `final-model-result-report.md` for exact hashes and evidence boundaries.

All outputs remain `DRAFT`. The design is not a calibrated ruler, child product, cutting tool or validated universal pen/paper accessory. Physical edge, paper, ink, flex and cycle validation remains deferred.
