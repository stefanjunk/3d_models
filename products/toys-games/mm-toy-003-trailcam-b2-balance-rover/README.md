# MM-TOY-003 — TrailCam B2 Balance FPV Rover

Portfolio record: `PORT-099`

Current revision: `0.1.0` — requirements, concept r1 and decomposition approved;
parametric candidate `0.1.0-parametric.2` passes its required source/geometry
and idealized-control checks but remains a non-manufacturing DRAFT

Lifecycle: `P1 Concept / digital proxy` — a deterministic CadQuery assembly,
provisional purchased-part proxies and an idealized control model exist. No
manufacturing candidate or physical balance evidence exists.

TrailCam B2 is a new product inspired by the open, ribbed, serviceable FPV
architecture of `MM-TOY-002`. It is not a two-wheel rendering of the four-wheel
TrailCam CF10. Its defining mechanism is a single geometric wheel axis with two
independently driven wheels and an electronic inverted-pendulum controller that
keeps the body upright and steers by differential wheel torque.

The proposed product retains a protected analog-FPV camera, separated radio and
video links, removable electronics trays, visible cable routing and the dark
printed frame/orange camera-guard design language. The four-wheel chassis,
suspension, steering linkage and axle drivetrain of `MM-TOY-002` are explicitly
outside this product.

## Controlled files

- `design-spec.yaml` — authoritative requirements candidate and workflow gates
- `docs/requirements-review-v0.1.0.md` — concise approval review and open choices
- `decision-log.md` — product identity, assumptions and blocked decisions
- `autonomy-policy.json` — guided workflow boundary; physical and release stages remain human-controlled
- `concepts/trailcam-b2-balance-concept-v0.1.0-r1.png` — approved appearance and architecture concept evidence
- `concepts/concept-review-v0.1.0.md` — requirement correspondence and disclosed visual limitations
- `concepts/imagegen-metadata-v0.1.0-r1.json` — built-in generation provenance, prompts and hashes
- `architecture/hybrid-design-plan-v0.1.0.json` — machine-readable component, interface, keep-out and validation contract
- `architecture/architecture-report-v0.1.0.md` — generated human-readable architecture report
- `architecture/control-architecture-v0.1.0.md` — balance loops, state machine, safety supervisor and test ladder
- `architecture/bom-candidates-v0.1.0.csv` — purchased-part candidates, authority and blocking evidence
- `reports/purchased-parts-research-v0.1.0.md` — manufacturer-backed component research and selection gaps
- `reports/preliminary-balance-sizing-v0.1.0.md` — wheel-speed and static torque sanity checks
- `docs/decomposition-review-v0.1.0.md` — concise human approval boundary for the next phase
- `cad/parameters.py` and `cad/build_rover.py` — axle-centered parametric source and deterministic DRAFT export generator
- `cad/validate_geometry.py` — geometry, envelope, landing and mass-property checks
- `control/plant_model.py` — nonlinear cart-pendulum proxy with sampled 250 Hz LQR validation
- `architecture/interface-contract-v0.1.0-parametric.2.json` — current proxy wheel, battery, camera and motor/bracket interface checks
- `previews/DRAFT-trailcam-b2-assembly-v0.1.0-parametric.2.png` and `.glb` — current non-manufacturing assembly visualization
- `reports/parametric-candidate-v0.1.0-parametric.2.md` — current model result and evidence
- `validation-project.json` — aggregate fail-closed validation contract
- `validation/` — generated structural and policy-validation evidence

## Current boundary

The current STEP/STL/GLB files are `DRAFT` digital proxies, not manufacturing
or print-release artifacts. The assembly has exactly two wheels on one common
axis and all 12 printed bodies fit the 220 × 220 × 250 mm compatibility target.
The idealized controller recovers from ±8° in simulation, but that result is
not firmware, hardware, failsafe or safety evidence.

Stefan selected Option A, so `ACC-MASS-001` remains a whole-assembly criterion.
The battery/cradle and electronics tiers were raised while preserving their
ordering and the 250 mm height limit. The complete provisional assembly is now
1877.15 g with COM `[1.69, 0.00, 71.23]` mm relative to the axle and passes the
70–110 mm vertical, 3 mm lateral and 12 mm longitudinal limits. The cradle
mounting slots provide 12.2 mm trim per side.

The provisional vertical COM clears the lower limit by only 1.23 mm. Exact
component masses and installed positions therefore remain an integration gate,
even though the current whole-assembly proxy passes.

Exact purchased components, an exact-clearance backend, certified mesh
self-intersection checking and complete Anycubic machine/process/filament
profiles are still required. No 3MF or G-code was generated.
