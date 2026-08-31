# Retrospective 3D-design preflight — Unregistered Aroma Diffuser

`Unregistered Aroma Diffuser | C2 (39.2/100) | R0 | K2 | Lane E | LOW_UNKNOWN`

## Decision

- Release: `HOLD`
- Lane: `E`
- Rationale: The retrospective preflight blocks release wherever interface evidence, the exact manufacturing profile, lifecycle controls, or measurable verification remains incomplete.
- Purpose: Document and develop a printable aroma-diffuser concept; the fragrance medium, heat source, and safe operating method are not yet defined.

This is a retrospective backfill of the currently evidenced repository state.
Unknown facts were not reconstructed or inferred as measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
| REQ | 1 | Only product-level intent and artifact names are available; quantified requirements are incomplete. |
| CTX | 3 | The use context includes a host, environment, or user variant that must be confirmed. |
| PAR | 1 | The current evidence exposes approximately 0 distinct geometry-file stems; exports may duplicate physical parts. |
| INT | 3 | At least one functional host, human, medium, or assembly boundary governs success. |
| CPL | 0 | The available architecture appears locally coupled or monolithic. |
| MOT | 0 | The primary product state is static apart from assembly handling. |
| GEO | 1 | Geometry appears conventional or non-fit-critical, although exact dimensions were not re-derived. |
| PHY | 3 | Load, heat, airflow, water, fatigue, or another functional physical domain must be tested. |
| MAT | 1 | A conventional single-material FDM route is sufficient at the documented level. |
| EXT | 0 | Little or no external-component integration is evidenced. |
| VER | 3 | Several fit, function, flow, load, motion, or process checks are required. |

## Readiness

| Component | Level |
|---|---|
| scope_variant | R1 |
| requirements | R1 |
| critical_interfaces | R1 |
| manufacturing_profile | R0 |
| verification | R0 |

Blocking unknowns:

- stable current product revision
- variant-confirmed critical interface dimensions, tolerances, and uncertainty
- complete printer/material/nozzle/orientation/process-profile set
- measurable acceptance criteria
- verification plan and physical result references

## Criticality

`K2` — The product involves load, flow, motion, heat-adjacent use, or direct body contact and therefore requires controlled functional testing.

Credible effects: functional failure, leakage, obstruction, or detachment, minor injury or property damage.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
| `IF-HUM-HUM-USR-BODY-001` | Printed product to intended user/body | E0 | K2 | PLANNED |

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
| G5 | PASS |
| G6 | WARN |

## Warnings

- `VARIANT_UNKNOWN` (WARN): No stable current product revision is evidenced at the product boundary.
- `CRITICAL_INTERFACE_UNKNOWN` (BLOCKER): The primary functional interface lacks variant-confirmed dimensions, tolerance, and uncertainty evidence.
- `VERIFICATION_NOT_DEFINED` (BLOCKER): Printer, material, nozzle, orientation, and process profile are not documented as one complete exact set.
- `THERMAL_OR_FLOW_CRITICAL` (WARN): Flow, drainage, humidity, heat, or airflow performance needs a controlled functional test.

## Functional FMEA

| Failure | Local/final effect | Detection | Mitigation | Verification |
|---|---|---|---|---|
| Primary interface misses fit or functional intent | Loss of function; consequences listed under criticality | Variant measurement, coupon, and controlled prototype inspection | Confirm host/variant, tolerance, uncertainty, keep-outs, and stop conditions | Coupon/prototype test; expert review for K3/K4 |

## Next evidence

1. Confirm the exact product/host variant and complete the primary interface contract. Exit: Datums, nominal dimensions, tolerances, measurement uncertainty, keep-outs, and variant identity are recorded from traceable evidence.
2. Record the exact manufacturing profile. Exit: Printer, material, nozzle, orientation, and complete process profile are uniquely identified and source-linked.
3. Define measurable acceptance criteria and a minimal coupon/prototype test. Exit: Each critical interface and credible failure mode has a method, threshold, and result-record location.

## Traceability basis

- `.`
