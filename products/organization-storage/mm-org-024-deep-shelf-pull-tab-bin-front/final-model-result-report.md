# Final model result — MM-ORG-024

Status: **PASS — draft digital print candidate**

Source: SKU-118, opportunity score 88.8

Revision: `0.1.0-draft.1`

## Delivered geometry

| Artifact | Functional interface | Envelope (mm) | Topology |
|---|---:|---:|---|
| pull/label face | 76.2 × 20 mm label; two locked clip centers | 120 × 48 × 15 | one watertight positive-volume component |
| thin clip | 2.2 mm gap for 1.92 mm host candidate | 10.9 × 22 × 6.2 | one watertight positive-volume component |
| ShelfFit clip | 2.9 mm gap for 2.67 mm front-rim candidate | 11.6 × 22 × 6.2 | one watertight positive-volume component |
| thick clip | 3.6 mm gap for 3.3 mm host candidate | 12.3 × 22 × 6.2 | one watertight positive-volume component |
| gap gauge | all three protected clip gaps | 76 × 32 × 3 | one watertight positive-volume component |
| key-slot coupon | exact face key slot | 32 × 22 × 3 | one watertight positive-volume component |

The face uses an exposed top-entry paper-label pocket, two mirrored insert-then-inward-slide key slots and a solid support-conscious lower pull wedge. Each U-clip prints broad-profile-down and carries one/two/three-hole identity coding. STEP masters, manufacturing STL files and a six-object 3MF are included.

## Digital evidence

- 13 deterministic parameter and regression tests passed.
- All six independent mesh audits passed with zero boundary, nonmanifold, degenerate and duplicate faces.
- 3MF validation passed: millimetres, six watertight positive-volume mesh objects and no structural warnings.
- Exact Anycubic Slicer Next 1.3.9.4 preflight passed with Kobra 3 Max / 0.4 mm / 0.20 mm Standard / Anycubic PETG profiles.
- Slicer result: 75 layers, one tool, zero tool changes, no native object warnings, 4,535 s estimate and 22,997.1 mm³ extrusion estimate.
- Required aggregate project gates are PASS. The sole optional physical gate is `REVIEW_REQUIRED` by user instruction.
- Unique-part candidate volume is 39,512.1 mm³ versus 100,554.7 mm³ for six solid envelope blocks (60.7% geometric reduction; the solid baseline was not sliced).

## Deferred validation

Before treating the draft as physically validated, measure and select a gauge gap, run 50 key/coupon cycles, inspect the installed clip and host after 24 hours, perform 500 controlled horizontal pulls with 0.75 kg distributed test contents, and complete 100 paper-label changes according to `tests/physical-test-plan.md`. No G-code was retained, uploaded or started.

The accessory is not a carry handle. Lifting, carrying, load-rating, universal-fit, child-use, food-contact, dust-protection and moisture-protection claims remain excluded. Commercial release remains blocked.
