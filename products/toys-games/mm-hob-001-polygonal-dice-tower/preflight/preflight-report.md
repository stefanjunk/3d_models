# Retrospective 3D-design preflight — Polygonal Dice Tower

`Polygonal Dice Tower | C3 (46.5/100) | R2 | K1 | Lane E | LOW_UNKNOWN`

## Decision

- Release: `HOLD`
- Lane: `E`
- Rationale: The retrospective preflight blocks release wherever interface evidence, the exact manufacturing profile, lifecycle controls, or measurable verification remains incomplete.
- Purpose: Guide tabletop dice through a printable polygonal tower and deliver randomized rolls into a controlled collection area.

This is a retrospective backfill of the currently evidenced repository state.
Unknown facts were not reconstructed or inferred as measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
| REQ | 1 | A design specification or requirement record exists, but release criteria may still be incomplete. |
| CTX | 2 | The use context includes a host, environment, or user variant that must be confirmed. |
| PAR | 3 | The current evidence exposes approximately 16 distinct geometry-file stems; exports may duplicate physical parts. |
| INT | 2 | At least one functional host, human, medium, or assembly boundary governs success. |
| CPL | 1 | The available architecture appears locally coupled or monolithic. |
| MOT | 2 | The purpose or evidence includes repeated motion, flexure, or a guided mechanism. |
| GEO | 2 | Geometry appears conventional or non-fit-critical, although exact dimensions were not re-derived. |
| PHY | 2 | Load, heat, airflow, water, fatigue, or another functional physical domain must be tested. |
| MAT | 2 | Material behavior, anisotropy, flexibility, surface process, or post-processing affects function. |
| EXT | 1 | Little or no external-component integration is evidenced. |
| VER | 2 | Several fit, function, flow, load, motion, or process checks are required. |

## Readiness

| Component | Level |
|---|---|
| scope_variant | R3 |
| requirements | R2 |
| critical_interfaces | R2 |
| manufacturing_profile | R2 |
| verification | R2 |

Blocking unknowns:

- variant-confirmed critical interface dimensions, tolerances, and uncertainty
- complete printer/material/nozzle/orientation/process-profile set
- measurable acceptance criteria
- verification plan and physical result references

## Criticality

`K1` — Failure is expected to cause inconvenience, fit loss, or limited property impact without credible high energy in the documented scope.

Credible effects: loss of intended function, minor item or surface damage.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
| `IF-ENV-MEC-LOD-BODY-001` | Printed product to supervised use environment | E2 | K1 | PLANNED |

The JSON contract records the primary discovered boundary. Because the audit
does not prove complete interface discovery, G1/G2 remain conservative.

## Hard gates

| Gate | Status |
|---|---|
| G0 | PASS |
| G1 | PASS |
| G2 | WARN |
| G3 | FAIL |
| G4 | FAIL |
| G5 | PASS |
| G6 | PASS |

## Warnings

- `CRITICAL_INTERFACE_UNKNOWN` (BLOCKER): The primary functional interface lacks variant-confirmed dimensions, tolerance, and uncertainty evidence.
- `VERIFICATION_NOT_DEFINED` (BLOCKER): Printer, material, nozzle, orientation, and process profile are not documented as one complete exact set.

## Next evidence

1. Confirm the exact product/host variant and complete the primary interface contract. Exit: Datums, nominal dimensions, tolerances, measurement uncertainty, keep-outs, and variant identity are recorded from traceable evidence.
2. Record the exact manufacturing profile. Exit: Printer, material, nozzle, orientation, and complete process profile are uniquely identified and source-linked.
3. Define measurable acceptance criteria and a minimal coupon/prototype test. Exit: Each critical interface and credible failure mode has a method, threshold, and result-record location.

## Traceability basis

- `unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1/dice_tower_project/release-0.1.2-g1/design-spec.yaml`
- `unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1/dice_tower_project/release-0.1.2-g1/README.md`
- `unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1/dice_tower_project/release-0.1.2-g1/reports/watermark-validation-0.1.2-g1.json`
- `unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1/dice_tower_project/release-0.1.2-g1/reports/geometry-validation-0.1.2-g1.json`
- `unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1/dice_tower_project/release-0.1.2-g1/source/polygonal-source-working-mm-0.1.2-g1.stl`
- `unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1/dice_tower_project/release-0.1.2-g1/result/polygonal-dice-tower-FINAL-0.1.2-g1.stl`
- `unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1/dice_tower_project/release-0.1.2-g1/inserts/sloped-floor-insert-0.1.2-g1.stl`
- `unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1/dice_tower_project/release-0.1.2-g1/inserts/rear-upper-entry-channel-liner-0.1.2-g1.stl`
