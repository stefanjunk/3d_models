# Retrospective 3D-design preflight — Metrimade Kobra 3 Max Printhead Cover – Eigenständiger Neuaufbau

`Metrimade Kobra 3 Max Printhead Cover – Eigenständiger Neuaufbau | C4 (64.2/100) | R2 | K3 | Lane E | NOT_AUTONOMOUSLY_RELEASABLE`

## Decision

- Release: `HOLD`
- Lane: `E`
- Rationale: The retrospective preflight blocks release wherever interface evidence, the exact manufacturing profile, lifecycle controls, or measurable verification remains incomplete.
- Purpose: Develop a printable protective fan cage or printhead cover for a Kobra 3 Max while preserving airflow, motion clearances, and service access.

This is a retrospective backfill of the currently evidenced repository state.
Unknown facts were not reconstructed or inferred as measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
| REQ | 2 | A design specification or requirement record exists, but release criteria may still be incomplete. |
| CTX | 2 | The use context includes a host, environment, or user variant that must be confirmed. |
| PAR | 3 | The current evidence exposes approximately 30 distinct geometry-file stems; exports may duplicate physical parts. |
| INT | 3 | At least one functional host, human, medium, or assembly boundary governs success. |
| CPL | 2 | Changes can propagate across multiple parts, datums, or functional subsystems. |
| MOT | 3 | The purpose or evidence includes repeated motion, flexure, or a guided mechanism. |
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

`K3` — A human-load, powered vehicle, machine-adjacent, projectile, or wall-mounted interface can plausibly cause injury or significant property damage.

Credible effects: injury, damage to host equipment, loss of controlled function.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
| `IF-ENV-FLU-FLW-VOLUME-001` | Printed product to process medium | E2 | K3 | PLANNED |

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
| G5 | WARN |
| G6 | PASS |

## Warnings

- `CRITICAL_INTERFACE_UNKNOWN` (BLOCKER): The primary functional interface lacks variant-confirmed dimensions, tolerance, and uncertainty evidence.
- `SAFETY_EXPERT_REQUIRED` (BLOCKER): K3 scope requires expert-in-the-loop review and controlled prototypes; autonomous release is prohibited.
- `AUTONOMOUS_RELEASE_PROHIBITED` (BLOCKER): The credible failure consequence exceeds autonomous release authority.
- `THERMAL_OR_FLOW_CRITICAL` (BLOCKER): Flow, drainage, humidity, heat, or airflow performance needs a controlled functional test.
- `DYNAMIC_OR_FATIGUE_LOAD` (BLOCKER): Repeated motion, flexure, vibration, or dynamic contact needs cycle and failure testing.

## Functional FMEA

| Failure | Local/final effect | Detection | Mitigation | Verification |
|---|---|---|---|---|
| Primary interface misses fit or functional intent | Loss of function; consequences listed under criticality | Variant measurement, coupon, and controlled prototype inspection | Confirm host/variant, tolerance, uncertainty, keep-outs, and stop conditions | Coupon/prototype test; expert review for K3/K4 |

## Next evidence

1. Obtain an expert review of credible failure modes and the staged prototype plan. Exit: A named reviewer approves the test scope, controls, and stop conditions.
2. Confirm the exact product/host variant and complete the primary interface contract. Exit: Datums, nominal dimensions, tolerances, measurement uncertainty, keep-outs, and variant identity are recorded from traceable evidence.
3. Define measurable acceptance criteria and a minimal coupon/prototype test. Exit: Each critical interface and credible failure mode has a method, threshold, and result-record location.

## Traceability basis

- `redesign-v2/design-spec.yaml`
- `printhead_cover_metrimade_D52_multicolor.3mf`
- `Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1(1)/README.md`
- `current/README.md`
- `Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1(1)/validation-project.json`
- `Anycubic_Kobra_3_Max_Metrimade_Fan_Cage_R1(1)/reports/validation-project-report.json`
- `current/validation-project.json`
- `current/reports/validation-project-report.json`
