# Prospective 3D-design preflight — Anycubic Kobra 3 Max Purge Catcher

`0.7.0-requirements.5 | C3 (52.5/100) | R2 | K2 | Lane E | LOW_UNKNOWN`

## Decision

- Release: `CONCEPT_ONLY`
- Architecture: one-piece, bottomless diverter, directly and permanently mounted through two holes with the existing Wiper screws
- Removed: adapter plate, clip, slider, latch, quick-release, floor, flap and moving storage volume
- Preserved: open honeycomb walls and a centred owned metriMade logo
- Rationale: the user has resolved the product architecture, so a non-dimensional clean-room concept may follow after explicit requirements approval. Production CAD remains blocked by the unknown screw contract and incomplete owned machine envelope.

The third-party 3MF is evidence-only. Its geometry, contours, dimensions,
images and project metadata are not design inputs.

## Complexity

| Dimension | Score | Rationale |
|---|---:|---|
| REQ | 2 | The requested architecture is explicit; requirements approval remains open. |
| CTX | 2 | The exact machine unit and surrounding envelope still require physical confirmation. |
| PAR | 1 | One printed production part plus inexpensive fit coupons are planned. |
| INT | 3 | Fastener, machine-envelope and purge-medium boundaries govern success. |
| CPL | 1 | The one-piece architecture removes intermediate attachment and storage subsystems. |
| MOT | 2 | The diverter co-moves with the guided Wiper along Z. |
| GEO | 2 | Conventional printable geometry, but several external datums and keep-outs are unresolved. |
| PHY | 3 | Screw clamping, vibration, warm purge impact and gravity diversion require physical tests. |
| MAT | 2 | Printed anisotropy and creep affect the direct screw zone. |
| EXT | 1 | Only the host and its two existing screws participate. |
| VER | 3 | Fit, engagement, motion, purge flow, mesh and slicer checks are required. |

## Readiness and blockers

| Component | Level |
|---|---|
| Scope and variant | R4 |
| Requirements | R3 |
| Critical interfaces | R2 |
| Manufacturing profile | R3 |
| Verification | R3 |

Blocking unknowns:

- screw thread or shaft diameter, head diameter, head height and current length under head
- required printed seating thickness and remaining thread engagement
- owned complete Wiper, bed, rollers, head, cable, tool-access and service envelope
- approved clean-room concept and physical bottomless purge trajectory

## Interface register

| Contract | Purpose | Evidence | Criticality | Status |
|---|---|---:|---:|---|
| `IF-EXT-GEO-FST-HLP-001` | Direct fixed two-screw Wiper mount | E2 | K2 | Coupon planned |
| `IF-INT-FLU-GDE-VOLUME-001` | Bottomless capture and gravity diversion | E1 | K2 | Prototype test planned |
| `IF-EXT-KIN-CLR-VOLUME-001` | Full moving machine keep-out envelope | E1 | K2 | Outline coupon and motion test planned |

The independently measured vertical screw pitch is 17 mm. That is the only
fastener geometry currently admitted as a measured design input. Hole diameter,
head seat and screw length are deliberately `UNKNOWN` until physically measured.

## Hard gates

| Gate | Status |
|---|---|
| G0 purpose | PASS |
| G1 entities | PASS |
| G2 critical interfaces | FAIL |
| G3 complexity | PASS |
| G4 criticality | PASS |
| G5 manufacturing context | PASS |
| G6 maintenance and service | PASS |

## Main failure modes

| Failure | Effect | Control |
|---|---|---|
| Hole, head seat or screw stack does not match | No fit, Wiper distortion, loosening or printed-zone fracture | Caliper measurement plus 17 mm hole-pattern/seating coupon |
| Added thickness reduces thread engagement | Unreliable original Wiper or accessory retention | Record screw and stack dimensions; verify replacement length if needed |
| Body enters an omitted machine envelope | Collision or damage | Owned outline coupon and powered-off full-travel/service sweep |
| Purge catches on internal, honeycomb or logo edges | Backlog or uncontrolled fall | Smooth bottomless section and nine supervised low/mid/high-Z purge cycles |

## Next evidence

1. Measure screw/shaft diameter, head diameter, head height, current length under head and seating stack; then fit an independently designed 17 mm hole-pattern and outline coupon.
2. Obtain explicit approval for `0.7.0-requirements.5`, then create a non-dimensional clean-room concept sheet showing the direct holes, bottomless section, open honeycomb walls and centred logo.
3. After concept approval, implement production CAD and verify the complete powered-off motion/service envelope and physical purge path before print-candidate release.

No CAD, manufacturing 3MF or slicer run is authorized by this preflight.
