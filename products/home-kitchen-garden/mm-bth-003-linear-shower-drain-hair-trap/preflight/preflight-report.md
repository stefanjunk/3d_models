# Retrospective 3D-design preflight — Linear Shower Drain Hair Trap

`Linear Shower Drain Hair Trap | C3 (44.2/100) | R2 | K2 | Lane E | LOW_UNKNOWN`

## Decision

- Release: `HOLD`
- Lane: `E`
- Rationale: The retrospective preflight blocks release wherever interface evidence, the exact manufacturing profile, lifecycle controls, or measurable verification remains incomplete.
- Purpose: Develop a removable segmented insert that retains hair in a linear shower drain while preserving drainage and cleanability.

This is a retrospective backfill of the currently evidenced repository state.
Unknown facts were not reconstructed or inferred as measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
| REQ | 1 | A design specification or requirement record exists, but release criteria may still be incomplete. |
| CTX | 3 | The use context includes a host, environment, or user variant that must be confirmed. |
| PAR | 3 | The current evidence exposes approximately 32 distinct geometry-file stems; exports may duplicate physical parts. |
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
| `IF-ENV-FLU-FLW-VOLUME-001` | Printed product to process medium | E2 | K2 | PLANNED |

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
- `THERMAL_OR_FLOW_CRITICAL` (WARN): Flow, drainage, humidity, heat, or airflow performance needs a controlled functional test.

## Functional FMEA

| Failure | Local/final effect | Detection | Mitigation | Verification |
|---|---|---|---|---|
| Primary interface misses fit or functional intent | Loss of function; consequences listed under criticality | Variant measurement, coupon, and controlled prototype inspection | Confirm host/variant, tolerance, uncertainty, keep-outs, and stop conditions | Coupon/prototype test; expert review for K3/K4 |

## Next evidence

1. Confirm the exact product/host variant and complete the primary interface contract. Exit: Datums, nominal dimensions, tolerances, measurement uncertainty, keep-outs, and variant identity are recorded from traceable evidence.
2. Define measurable acceptance criteria and a minimal coupon/prototype test. Exit: Each critical interface and credible failure mode has a method, threshold, and result-record location.

## Traceability basis

- `abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21/design-spec.yaml`
- `abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21/assets/metrimade-watermark/design-spec.yaml`
- `abflusssieb/shower_drain_hairtrap_945x65_funnel_edge_v1_3/shower_drain_hairtrap_945x65_funnel_edge/README.md`
- `abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21/README.md`
- `abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21/profiles/anycubic-slicer-next/README.md`
- `abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21/assets/metrimade-watermark/README.md`
- `abflusssieb/shower_drain_hairtrap_v3_loose_segments_945x65x21/validation-project.json`
- `abflusssieb/shower_drain_hairtrap_945x65_funnel_edge_v1_3/shower_drain_hairtrap_945x65_funnel_edge/functional_test_tile_80mm.stl`
