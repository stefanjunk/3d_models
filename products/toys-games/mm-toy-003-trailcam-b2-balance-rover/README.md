# MM-TOY-003 — TrailCam B2 Balance FPV Rover

Portfolio record: `PORT-099`

Current revision: `0.1.0` — requirements, concept r1 and decomposition approved;
parametric candidate `0.1.0-parametric.1` is a blocked DRAFT

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
- `architecture/interface-contract-v0.1.0-parametric.1.json` — proxy wheel, battery, camera and motor/bracket interface checks
- `previews/DRAFT-trailcam-b2-assembly.png` and `.glb` — non-manufacturing assembly visualization
- `reports/parametric-candidate-v0.1.0.md` — concise result and open decision
- `validation-project.json` — aggregate fail-closed validation contract
- `validation/` — generated structural and policy-validation evidence

## Current boundary

The current STEP/STL/GLB files are `DRAFT` digital proxies, not manufacturing
or print-release artifacts. The assembly has exactly two wheels on one common
axis and all 12 printed bodies fit the 220 × 220 × 250 mm compatibility target.
The idealized controller recovers from ±8° in simulation, but that result is
not firmware, hardware, failsafe or safety evidence.

Parametric approval is blocked by the scope of `ACC-MASS-001`: the provisional
whole-system center of mass is 54.61 mm above the axle, while the actively
modeled reduced-order pendulum lump—excluding the provisional axle-grouped
wheels, hubs, motors and brackets—is 84.90 mm above it. That grouping is a
control-model diagnostic, not physical mass-property authority. Exact purchased
components, an exact-clearance backend, certified mesh self-intersection
checking and complete Anycubic machine/process/filament profiles are also still
required. No 3MF or G-code was generated.
