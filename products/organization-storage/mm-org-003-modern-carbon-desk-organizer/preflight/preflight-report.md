# Corrective 3D-design preflight — Modern Carbon Desk Organizer Compact

`Modern Carbon Desk Organizer Compact | C3 (46.0/100) | R2 | K1 | Lane C | LOW_UNKNOWN`

## Decision

- Digital design: `GO_WITH_CONTROLS`
- Workflow: Lane C, iterative engineering
- Physical fit, slicing, appearance and release: blocked until exact-process evidence exists
- Assessment: `PREFLIGHT-MM-ORG-003-002`, revision `0.2.0`, product revision `2.0.0-draft.2`

The owner correction makes the desired product state clear and the repository contains exact parametric geometry. Readiness remains R2 because the printer, filament product, complete slicer profile and physical results are unknown.

## Main complexity drivers

| Driver | Score | Reason |
|---|---:|---|
| INT | 3 | Long sliding drawers, four stack locators, containment corners and appearance keep-outs interact. |
| PAR | 3 | One source controls five printable artifacts and derived STEP/STL/3MF evidence. |
| VER | 3 | Geometry, motion, fit, texture, slicing and physical use require separate gates. |

## Interface register

| Contract | Purpose | Evidence | Criticality | Status |
|---|---|---:|---:|---|
| `IF-INT-KIN-SLD-SLOT-001` | drawer travel in housing | E3 digital | K1 | CAD pass; physical coupon planned |
| `IF-INT-GEO-LOC-SLOT-002` | sorter registration | E3 digital | K1 | CAD pass; physical seating planned |
| `IF-INT-GEO-CON-BODY-003` | closed housing/sorter corners | E2 before correction | K1 | corrected verification planned at preflight time |
| `IF-HUM-OPT-VIS-FREEFORM-004` | rounded front and carbon look | E2 | K0 | digital correction allowed; human coupon gate retained |

## Hard gates

| Gate | Status | Meaning |
|---|---|---|
| G0 | PASS | scope and correction are explicit |
| G1 | PASS | parts, user, environment and four interfaces are identified |
| G2 | WARN | digital geometry exists; physical fit/appearance evidence does not |
| G3 | WARN | target printer class/nozzle/orientation exist; exact machine/material/profile do not |
| G4 | PASS | corner, motion, stack, mesh, 3MF, fit-coupon and texture-coupon criteria are measurable |
| G5 | PASS | K1 permits iterative digital work |
| G6 | PASS | assembly, cleaning, removal and service are represented |

## Required next evidence

1. Correct and verify the final STEP/STL geometry. Exit: corner probes, full-travel intersections, stack intersection, protected regions and mesh checks pass.
2. Qualify XY sliding clearance for the exact process. Exit: a measured coupon selects the value and the unchanged full-length drawer repeats it.
3. Run exact-profile slicing. Exit: isolated slicer evidence records binary/profile/input/G-code hashes and manual layer, seam and support review.
4. Approve physical appearance. Exit: the vertical-wall 2.4/3.2/4.0 mm coupon is reviewed at desk distance under three fixed light angles.

The schema-valid authority is `preflight-result.json`; this report is its readable projection.
