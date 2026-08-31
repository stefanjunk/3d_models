# Retrospective 3D-design preflight — Anycubic Kobra 3 Max Purge Catcher — Interface Neuentwurf

`Anycubic Kobra 3 Max Purge Catcher — Interface Neuentwurf | C3 (59.3/100) | R2 | K2 | Lane E | LOW_UNKNOWN`

## Decision

- Release: `HOLD`
- Lane: `E`
- Rationale: The installed third-party reference materially improves variant, side, orientation and two-screw-interface evidence, but it cannot supply clean-room geometry or commercial rights. R7 remains held until its own envelope, hardware and architecture are approved and physically checked.
- Purpose: Ein leichter Fangkopf fährt direkt mit dem Purge-Wiper entlang Z, fängt Filamentreste unmittelbar an der Quelle und lenkt sie ohne langen Kanal nach unten in einen stationären, entnehmbaren Sammelbehälter.

This focused retrospective reassessment includes the 31 August 2026 user fit
assessment and the audited BY-NC reference 3MF. Unknown facts were not
reconstructed or inferred as owned measurements.

## Complexity score rationale

| Dimension | Score | Evidence-based rationale |
|---|---:|---|
| REQ | 2 | A design specification or requirement record exists, but release criteria may still be incomplete. |
| CTX | 2 | The use context includes a host, environment, or user variant that must be confirmed. |
| PAR | 2 | The current evidence exposes approximately 0 distinct geometry-file stems; exports may duplicate physical parts. |
| INT | 3 | At least one functional host, human, medium, or assembly boundary governs success. |
| CPL | 2 | Changes can propagate across multiple parts, datums, or functional subsystems. |
| MOT | 2 | The accessory co-moves with the Purge-Wiper along the guided Z translation. |
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
| verification | R3 |

Blocking unknowns:

- clean-room machine envelope, screw hardware, tolerances and uncertainty beyond the independently measured 17 mm pitch
- architecture decision between a lightweight diverter with stationary storage and a directly mounted moving storage bin

## Criticality

`K2` — The product involves load, flow, motion, heat-adjacent use, or direct body contact and therefore requires controlled functional testing.

Credible effects: functional failure, leakage, obstruction, or detachment, minor injury or property damage.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
| `IF-EXT-GEO-CON-MIXED-001` | Printed product to intended host | E2 | K2 | PLANNED |

The JSON contract records the primary discovered boundary and the independently
measured 17 mm screw pitch. The installed reference supports the Kobra 3 Max
variant, physical side and direct mounting principle. It does not establish the
clean-room R7 envelope, fastener contract or tolerances, so G2 remains failed.

## Hard gates

| Gate | Status |
|---|---|
| G0 | PASS |
| G1 | PASS |
| G2 | FAIL |
| G3 | PASS |
| G4 | PASS |
| G5 | PASS |
| G6 | WARN |

## Warnings

- `CRITICAL_INTERFACE_UNKNOWN` (BLOCKER): The exact host variant and 17 mm screw pitch are supported, but the clean-room accessory still lacks a complete machine envelope, hardware contract, tolerances and physical coupon result.
- `THIRD_PARTY_BY_NC` (WARN): The strongest fit reference is marked BY-NC and may not be copied into a commercial R7 design; its exact license version is not embedded.
- `REFERENCE_PROFILE_MISMATCH` (WARN): The reference 3MF embeds a Bambu Lab P1S profile, not an Anycubic Kobra 3 Max manufacturing profile.

## Functional FMEA

| Failure | Local/final effect | Detection | Mitigation | Verification |
|---|---|---|---|---|
| Primary interface misses fit or functional intent | Loss of function; consequences listed under criticality | Variant measurement, coupon, and controlled prototype inspection | Confirm host/variant, tolerance, uncertainty, keep-outs, and stop conditions | Coupon/prototype test; expert review for K3/K4 |

## Next evidence

1. Build and fit a clean-room 17 mm hole-pattern plus conservative outline coupon from the user's own measurements and machine photos. Exit: The coupon fits the powered-off target machine, screw hardware and engagement are recorded, and no third-party contour or dimension is used.
2. Select the storage architecture before reopening concept approval. Exit: The owner explicitly approves either lightweight moving diversion with stationary storage or directly mounted moving storage, including the corresponding moving-mass and service constraints.
3. Verify the complete machine-motion and service envelope with the selected clean-room concept. Exit: Powered-off full-travel, tool-access and removal-sweep tests meet the documented clearance criteria.

## Traceability basis

- `design-spec.yaml`
- `WIPER-PHOTO-MEASUREMENTS-R7.yaml`
- `learning-trace-interface-r7.yaml`
- `REFERENCE-FIT-AUDIT-ANYCUBIC-POOP-CATCHER.md`
- `REFERENCE-FIT-AUDIT-ANYCUBIC-POOP-CATCHER.json`
- `research/third-party/printer-workshop/Anycubic_Kobra_3_Max_Poop_catcher.3mf`
- `REQUIREMENTS-PHASE-VALIDATION-R7.json`
- `CONCEPT-PHASE-VALIDATION-R7.json`
- `current/anycubic-kobra3max-purge-catcher-r7/README-DE.md`
- `current/anycubic-kobra3max-purge-catcher-r7/validation-project.lock.json`
- `current/anycubic-kobra3max-purge-catcher-r7/validation-project.json`
- `current/anycubic-kobra3max-purge-catcher-r7/reports/validation-project-report.json`
- `current/anycubic-kobra3max-purge-catcher-r7/reports/validation-project-lock-report.json`
