# MM-TOY-003 — TrailCam B2 Balance FPV Rover

Portfolio record: `PORT-099`

Current revision: `0.1.0` — requirements and concept r1 approved; decomposition
candidate `0.1.0-decomposition.1` awaits explicit approval; production CAD remains blocked

Lifecycle: `P0 Idea` — controlled requirements, an approved concept and a
validated decomposition candidate exist; no approved decomposition, CAD,
manufacturing export or physical evidence exists

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
- `validation/` — generated structural and policy-validation evidence

## Current boundary

No CAD source, STL, STEP, 3MF or G-code may be created until decomposition
candidate `0.1.0-decomposition.1` is explicitly approved. The plan assigns all
critical geometry to parametric CAD or exact measured purchased parts; it uses
no image-to-3D geometry. Exact wheels/hubs, IMU carrier, power/current-sensing
architecture, mass properties and print profiles remain downstream blockers.
