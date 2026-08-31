# Retrospective 3D-design preflight — Mm Toy 001 Rubber Ball Toy Popper

`Mm Toy 001 Rubber Ball Toy Popper | C3 (52.8/100) | R1 | K3 | Lane E | NOT_AUTONOMOUSLY_RELEASABLE`

## Decision

- Release: `HOLD`
- Lane: `E`
- Rationale: The retrospective preflight blocks release wherever interface evidence, the exact manufacturing profile, lifecycle controls, or measurable verification remains incomplete.
- Purpose: Develop a supervised play mechanism that launches or pops a soft rubber ball; projectile energy and user safety remain unvalidated.

This is a retrospective backfill of the currently evidenced repository state.
Unknown facts were not reconstructed or inferred as measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
| REQ | 1 | Only product-level intent and artifact names are available; quantified requirements are incomplete. |
| CTX | 3 | The use context includes a host, environment, or user variant that must be confirmed. |
| PAR | 3 | The current evidence exposes approximately 11 distinct geometry-file stems; exports may duplicate physical parts. |
| INT | 3 | At least one functional host, human, medium, or assembly boundary governs success. |
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
| scope_variant | R2 |
| requirements | R1 |
| critical_interfaces | R1 |
| manufacturing_profile | R1 |
| verification | R1 |

Blocking unknowns:

- stable current product revision
- variant-confirmed critical interface dimensions, tolerances, and uncertainty
- complete printer/material/nozzle/orientation/process-profile set
- measurable acceptance criteria
- verification plan and physical result references

## Criticality

`K3` — A human-load, powered vehicle, machine-adjacent, projectile, or wall-mounted interface can plausibly cause injury or significant property damage.

Credible effects: injury, damage to host equipment, loss of controlled function.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
| `IF-HUM-HUM-USR-BODY-001` | Printed product to intended user/body | E1 | K3 | PLANNED |

The JSON contract records the primary discovered boundary. Because the audit
does not prove complete interface discovery, G1/G2 remain conservative.

## Hard gates

| Gate | Status |
|---|---|
| G0 | WARN |
| G1 | WARN |
| G2 | FAIL |
| G3 | FAIL |
| G4 | FAIL |
| G5 | WARN |
| G6 | PASS |

## Warnings

- `VARIANT_UNKNOWN` (WARN): No stable current product revision is evidenced at the product boundary.
- `CRITICAL_INTERFACE_UNKNOWN` (BLOCKER): The primary functional interface lacks variant-confirmed dimensions, tolerance, and uncertainty evidence.
- `VERIFICATION_NOT_DEFINED` (BLOCKER): Printer, material, nozzle, orientation, and process profile are not documented as one complete exact set.
- `SAFETY_EXPERT_REQUIRED` (BLOCKER): K3 scope requires expert-in-the-loop review and controlled prototypes; autonomous release is prohibited.
- `AUTONOMOUS_RELEASE_PROHIBITED` (BLOCKER): The credible failure consequence exceeds autonomous release authority.

## Functional FMEA

| Failure | Local/final effect | Detection | Mitigation | Verification |
|---|---|---|---|---|
| Primary interface misses fit or functional intent | Loss of function; consequences listed under criticality | Variant measurement, coupon, and controlled prototype inspection | Confirm host/variant, tolerance, uncertainty, keep-outs, and stop conditions | Coupon/prototype test; expert review for K3/K4 |

## Next evidence

1. Obtain an expert review of credible failure modes and the staged prototype plan. Exit: A named reviewer approves the test scope, controls, and stop conditions.
2. Confirm the exact product/host variant and complete the primary interface contract. Exit: Datums, nominal dimensions, tolerances, measurement uncertainty, keep-outs, and variant identity are recorded from traceable evidence.
3. Record the exact manufacturing profile. Exit: Printer, material, nozzle, orientation, and complete process profile are uniquely identified and source-linked.
4. Define measurable acceptance criteria and a minimal coupon/prototype test. Exit: Each critical interface and credible failure mode has a method, threshold, and result-record location.

## Traceability basis

- `rubber_ball_toy_popper/README.md`
- `toy-blaster-mechanisms-research-report.md`
- `rubber_ball_toy_popper/output/toy_popper_assembly_preview_NOT_FOR_PRINT.stl`
- `rubber_ball_toy_popper/output/toy_popper_sear.stl`
- `rubber_ball_toy_popper/output/toy_popper_safety_block.stl`
- `rubber_ball_toy_popper/output/toy_popper_rear_cap.stl`
- `rubber_ball_toy_popper/output/toy_popper_rail_lock_pin.stl`
- `rubber_ball_toy_popper/output/toy_popper_plunger.stl`
