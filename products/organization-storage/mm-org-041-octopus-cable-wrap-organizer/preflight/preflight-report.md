# MM-ORG-041 preflight report

**Scorecard:** Octopus cable wrap organizer | C2 (34.75/100) | R2 | K1 | Lane C | LOW_UNKNOWN
**Assessment:** PREFLIGHT-MM-ORG-041-001 v0.1.0, PROSPECTIVE, 2026-09-04
**Design release:** GO_WITH_CONTROLS

## 1. Decision and reasoning

Design work may proceed under controls. C2 complexity with K1 criticality places the
product in Lane C (iterative engineering). Readiness stops at **R2** because the
cable-retention contract rests on a *declared design range* rather than measured cable
diameters — that is the weakest evidence link and it caps the whole project.

Controls attached to the release:

1. The generated mesh is labelled a **proposal**, never a measured reconstruction.
2. Every functional dimension is re-created parametrically after generation.
3. No fit, retention, comfort, stability or compatibility wording may be published
   before the coupon and physical tests pass.
4. Commercial release stays blocked independently by the Step1X-3D licence conflict.

## 2. Interface register

| ID | Contract | Evidence | IC / tier | Note |
|---|---|---|---|---|
| IF-EXT-GEO-RET-SLOT-001 | slack cable to open tentacle channel | **E1** | 10 / I2 | weakest link; caps readiness at R2 |
| IF-EXT-MEC-SUP-PLN-001 | base to desk support plane | E1 | 5 / I1 | mass and CoG unknown |
| IF-HUM-GEO-CON-FREEFORM-001 | adult hand to generated surface and lips | E1 | 6 / I1 | min wall derived from process baseline |
| IF-INT-GEO-CON-BODY-001 | generated shell to CAD-owned Boolean band | E2 | 6 / I1 | mesh becomes directly inspectable |

## 3. Missing and uncertain data

- Cable outer diameter, jacket hardness and retention force: **UNKNOWN**.
- Hidden geometry and internal volume: synthesized from one image.
- As-built mass, centre of gravity, footprint area, desk friction: **UNKNOWN**.
- Cycle life of the compliant pinch lips in PETG: **UNKNOWN**.
- Step1X-3D EU licence position: **BLOCK**.

## 4. Hard gates

| Gate | Result | Basis |
|---|---|---|
| G0 scope/variant/use | PASS | function, exclusions, users, environment and lifecycle fixed |
| G1 entities/interfaces | PASS | 6 entities, 4 contracts, internal authority boundary named |
| G2 critical evidence | **WARN** | cable interface is E1 from a declared range; no cable measured |
| G3 process profile | PASS | hashed Kobra 3 Max / SUNLU PETG Black / 0.4 mm / 0.20 mm baseline pinned |
| G4 acceptance/methods | PASS | six acceptance criteria with named methods |
| G5 criticality | PASS | K1 permits the autonomous design workflow |
| G6 assembly/service/lifecycle | PASS | single part, no assembly or service path needed |

G2 is deliberately WARN rather than PASS. The product owner auto-approved the workflow
gates, which authorizes *proceeding*; it does not create measurement evidence.

## 5. Minimum next evidence

Measure the outer diameter of at least five real target cables and replace the declared
range with a variant-confirmed contract.
**Exit criterion:** IF-EXT-GEO-RET-SLOT-001 reaches E3 with recorded nominals, tolerance
and a control dimension; `critical_interfaces` rises to R3 and G2 can become PASS.

## 6. Recommended design and test path

1. Own imagegen reference → Step1X-3D **sacrificial preform** (massing and surface only).
2. Mesh repair to a watertight manifold solid; audit before any Boolean.
3. Deliberate millimetre scaling and registration; record the matrix.
4. Parametric channel Boolean inside the editable seam band only.
5. Minimum-wall, thin-protrusion, floater and envelope audits.
6. Smallest-feature channel coupon → measured cables → retention and 100-cycle tests.
7. Full body prototype → stability, edge comfort, appearance.
8. Only then: watermark placement, then commercial gates.

## 7. Warnings

`HIDDEN_GEOMETRY` (WARN) · `CRITICAL_INTERFACE_UNKNOWN` (WARN) ·
`VERIFICATION_NOT_DEFINED` (INFO) · `GENERATIVE_TOOL_LICENCE_BLOCK` (**BLOCKER**)
