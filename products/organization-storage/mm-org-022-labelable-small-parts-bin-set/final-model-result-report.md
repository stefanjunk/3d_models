# Final model result — MM-ORG-022

Status: **PASS — draft digital print candidate**

Source: SKU-023, opportunity score 88.8

Revision: `0.1.0-draft.1`

## Delivered geometry

| Artifact | Functional size | Envelope (mm) | Topology |
|---|---:|---:|---|
| narrow bin | 45 mm row unit | 45 × 76.5 × 36 | one watertight positive-volume component |
| medium bin | 67.5 mm row unit | 67.5 × 76.5 × 36 | one watertight positive-volume component |
| wide bin | 90 mm row unit | 90 × 76.5 × 36 | one watertight positive-volume component |
| matrix frame | two 180 × 75 mm rows | 186 × 156 × 4 | one watertight positive-volume component |
| label-slot gauge | 0.5 / 0.7 / 0.9 mm | 72 × 22 × 16 | one watertight positive-volume component |

Every bin has a 1.8 mm continuous shell, 12 mm front grip radius, 13 × 7 mm interior pickup ramp, top-loading paper-label rails and underside hole coding. Electronics and sewing presets both tile the protected 180 mm row exactly. STEP masters, manufacturing STL files and a five-object 3MF are included.

## Digital evidence

- 12 deterministic parameter and regression tests passed.
- All five independent mesh audits passed with zero boundary, nonmanifold, degenerate and duplicate faces.
- 3MF validation passed: millimetres, five watertight positive-volume mesh objects and no structural warnings.
- Exact Anycubic Slicer Next 1.3.9.4 preflight passed with Kobra 3 Max / 0.4 mm / 0.20 mm Standard / Anycubic PLA profiles.
- Slicer result: 180 layers, one tool, zero tool changes, no native object warnings, 11,419 s estimate and 87,421.1 mm³ extrusion estimate.
- Required aggregate project gates are PASS. The sole optional physical gate is `REVIEW_REQUIRED` by user instruction.
- Unique-part candidate volume is 99,527.9 mm³ versus 699,093.0 mm³ for five solid envelope blocks (85.8% geometric reduction; the solid baseline was not sliced).

## Deferred validation

Before treating the draft as physically validated, follow `tests/physical-test-plan.md`: choose label clearance with the coupon, verify actual drawer/frame fit, pilot unpowered electronics and adult sewing notions, check edge comfort, complete 100 bin and label cycles, and run the bounded 0.25 kg/24 h check. No G-code was retained, uploaded or started.

Commercial release, child use, battery/energized-part storage, ESD, transport, spill and named-system compatibility remain blocked.
