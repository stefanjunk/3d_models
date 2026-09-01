# Retrospective 3D-design preflight — Anycubic Kobra 3 Max Purge Catcher — Interface Neuentwurf

`Anycubic Kobra 3 Max Purge Catcher — Interface Neuentwurf | C3 (56.8/100) | R2 | K2 | Lane E | LOW_UNKNOWN`

## Decision

- Release: `HOLD`
- Lane: `E`
- Rationale: The retrospective preflight blocks release wherever interface evidence, the exact manufacturing profile, lifecycle controls, or measurable verification remains incomplete.
- Purpose: Ein einteiliger, bodenloser Umlenker ist mit den beiden vorhandenen Wiper-Schrauben fest am bewegten Purge-Wiper verschraubt, fängt Filamentreste unmittelbar an der Quelle und lässt sie durch einen freien unteren Auslass nach unten fallen.

This is a retrospective backfill of the currently evidenced repository state.
Unknown facts were not reconstructed or inferred as measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
| REQ | 2 | A design specification or requirement record exists, but release criteria may still be incomplete. |
| CTX | 2 | The use context includes a host, environment, or user variant that must be confirmed. |
| PAR | 2 | The current evidence exposes approximately 0 distinct geometry-file stems; exports may duplicate physical parts. |
| INT | 3 | At least one functional host, human, medium, or assembly boundary governs success. |
| CPL | 2 | Changes can propagate across multiple parts, datums, or functional subsystems. |
| MOT | 1 | The primary product state is static apart from assembly handling. |
| GEO | 2 | Geometry appears conventional or non-fit-critical, although exact dimensions were not re-derived. |
| PHY | 3 | Load, heat, airflow, water, fatigue, or another functional physical domain must be tested. |
| MAT | 2 | Material behavior, anisotropy, flexibility, surface process, or post-processing affects function. |
| EXT | 2 | Purchased hardware, printer equipment, electronics, or software participates in the system. |
| VER | 3 | Several fit, function, flow, load, motion, or process checks are required. |

## Readiness

| Component | Level |
|---|---|
| scope_variant | R3 |
| requirements | R2 |
| critical_interfaces | R2 |
| manufacturing_profile | R3 |
| verification | R2 |

Blocking unknowns:

- variant-confirmed critical interface dimensions, tolerances, and uncertainty
- measurable acceptance criteria

## Criticality

`K2` — The product involves load, flow, motion, heat-adjacent use, or direct body contact and therefore requires controlled functional testing.

Credible effects: functional failure, leakage, obstruction, or detachment, minor injury or property damage.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
| `IF-EXT-GEO-CON-MIXED-001` | Printed product to intended host | E2 | K2 | PLANNED |

The JSON contract records the primary discovered boundary. Because the audit
does not prove complete interface discovery, G1/G2 remain conservative.

## Hard gates

| Gate | Status |
|---|---|
| G0 | PASS |
| G1 | PASS |
| G2 | FAIL |
| G3 | PASS |
| G4 | WARN |
| G5 | PASS |
| G6 | PASS |

## Warnings

- `CRITICAL_INTERFACE_UNKNOWN` (BLOCKER): The primary functional interface lacks variant-confirmed dimensions, tolerance, and uncertainty evidence.

## Functional FMEA

| Failure | Local/final effect | Detection | Mitigation | Verification |
|---|---|---|---|---|
| Primary interface misses fit or functional intent | Loss of function; consequences listed under criticality | Variant measurement, coupon, and controlled prototype inspection | Confirm host/variant, tolerance, uncertainty, keep-outs, and stop conditions | Coupon/prototype test; expert review for K3/K4 |

## Next evidence

1. Confirm the exact product/host variant and complete the primary interface contract. Exit: Datums, nominal dimensions, tolerances, measurement uncertainty, keep-outs, and variant identity are recorded from traceable evidence.
2. Define measurable acceptance criteria and a minimal coupon/prototype test. Exit: Each critical interface and credible failure mode has a method, threshold, and result-record location.

## Traceability basis

- `design-spec.yaml`
- `REQUIREMENTS-PHASE-VALIDATION-R7.json`
- `COUPON-C01-VALIDATION-R7.json`
- `CONCEPT-PHASE-VALIDATION-R7.json`
- `REQUIREMENTS-REVIEW-R7-0.7.0-requirements.5.md`
- `current/r7-interface-measurement-coupon-c01/README-DE.md`
- `current/anycubic-kobra3max-purge-catcher-r7/README-DE.md`
- `current/anycubic-kobra3max-purge-catcher-r7/validation-project.lock.json`
