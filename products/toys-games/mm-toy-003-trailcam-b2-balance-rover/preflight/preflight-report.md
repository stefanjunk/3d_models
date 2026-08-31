# Retrospective 3D-design preflight — Trailcam B2 Balance Fpv Rover

`Trailcam B2 Balance Fpv Rover | C3 (59.2/100) | R2 | K3 | Lane E | NOT_AUTONOMOUSLY_RELEASABLE`

## Decision

- Release: `HOLD`
- Lane: `E`
- Rationale: The retrospective preflight blocks release wherever interface evidence, the exact manufacturing profile, lifecycle controls, or measurable verification remains incomplete.
- Purpose: A two-wheel, single-axis FPV camera rover that actively balances its body as an inverted pendulum. Two independently driven coaxial wheels provide pitch stabilization, forward/reverse motion and differential yaw steering. A protected front camera, independent control/video links and serviceable electronics remain visually and functionally related to TrailCam CF10.

This is a retrospective backfill of the currently evidenced repository state.
Unknown facts were not reconstructed or inferred as measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
| REQ | 2 | A design specification or requirement record exists, but release criteria may still be incomplete. |
| CTX | 2 | The use context includes a host, environment, or user variant that must be confirmed. |
| PAR | 4 | The current evidence exposes approximately 74 distinct geometry-file stems; exports may duplicate physical parts. |
| INT | 2 | At least one functional host, human, medium, or assembly boundary governs success. |
| CPL | 2 | Changes can propagate across multiple parts, datums, or functional subsystems. |
| MOT | 3 | The purpose or evidence includes repeated motion, flexure, or a guided mechanism. |
| GEO | 2 | Geometry appears conventional or non-fit-critical, although exact dimensions were not re-derived. |
| PHY | 2 | Load, heat, airflow, water, fatigue, or another functional physical domain must be tested. |
| MAT | 2 | Material behavior, anisotropy, flexibility, surface process, or post-processing affects function. |
| EXT | 3 | Purchased hardware, printer equipment, electronics, or software participates in the system. |
| VER | 2 | Several fit, function, flow, load, motion, or process checks are required. |

## Readiness

| Component | Level |
|---|---|
| scope_variant | R3 |
| requirements | R3 |
| critical_interfaces | R2 |
| manufacturing_profile | R2 |
| verification | R3 |

Blocking unknowns:

- variant-confirmed critical interface dimensions, tolerances, and uncertainty
- complete printer/material/nozzle/orientation/process-profile set

## Criticality

`K3` — A human-load, powered vehicle, machine-adjacent, projectile, or wall-mounted interface can plausibly cause injury or significant property damage.

Credible effects: injury, damage to host equipment, loss of controlled function.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
| `IF-ENV-MEC-LOD-BODY-001` | Printed product to supervised use environment | E2 | K3 | PLANNED |

The JSON contract records the primary discovered boundary. Because the audit
does not prove complete interface discovery, G1/G2 remain conservative.

## Hard gates

| Gate | Status |
|---|---|
| G0 | PASS |
| G1 | PASS |
| G2 | FAIL |
| G3 | FAIL |
| G4 | PASS |
| G5 | WARN |
| G6 | PASS |

## Warnings

- `CRITICAL_INTERFACE_UNKNOWN` (BLOCKER): The primary functional interface lacks variant-confirmed dimensions, tolerance, and uncertainty evidence.
- `VERIFICATION_NOT_DEFINED` (BLOCKER): Printer, material, nozzle, orientation, and process profile are not documented as one complete exact set.
- `SAFETY_EXPERT_REQUIRED` (BLOCKER): K3 scope requires expert-in-the-loop review and controlled prototypes; autonomous release is prohibited.
- `AUTONOMOUS_RELEASE_PROHIBITED` (BLOCKER): The credible failure consequence exceeds autonomous release authority.
- `DYNAMIC_OR_FATIGUE_LOAD` (BLOCKER): Repeated motion, flexure, vibration, or dynamic contact needs cycle and failure testing.

## Functional FMEA

| Failure | Local/final effect | Detection | Mitigation | Verification |
|---|---|---|---|---|
| Primary interface misses fit or functional intent | Loss of function; consequences listed under criticality | Variant measurement, coupon, and controlled prototype inspection | Confirm host/variant, tolerance, uncertainty, keep-outs, and stop conditions | Coupon/prototype test; expert review for K3/K4 |

## Next evidence

1. Obtain an expert review of credible failure modes and the staged prototype plan. Exit: A named reviewer approves the test scope, controls, and stop conditions.
2. Confirm the exact product/host variant and complete the primary interface contract. Exit: Datums, nominal dimensions, tolerances, measurement uncertainty, keep-outs, and variant identity are recorded from traceable evidence.
3. Record the exact manufacturing profile. Exit: Printer, material, nozzle, orientation, and complete process profile are uniquely identified and source-linked.

## Traceability basis

- `design-spec.yaml`
- `README.md`
- `validation-project.json`
- `validation/procurement-bom-validation-v0.1.0-bom.1.json`
- `validation/hybrid-plan-validation-v0.1.0.json`
- `validation/v0.1.0-parametric.3/project-validation.json`
- `validation/v0.1.0-parametric.3/parameter-sweep.json`
- `validation/v0.1.0-parametric.3/mesh-DRAFT-upper-crossmember.json`
