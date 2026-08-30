# MM-TOY-003 — TrailCam B2 Balance FPV Rover

Portfolio record: `PORT-099`

Current revision: `0.1.0` — requirements approved; concept candidate r1 awaits
explicit approval; decomposition and production CAD remain blocked

Lifecycle: `P0 Idea` — controlled requirements and a concept image exist; no
approved decomposition, CAD, manufacturing export or physical evidence exists

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
- `concepts/trailcam-b2-balance-concept-v0.1.0-r1.png` — current concept candidate for human approval
- `concepts/concept-review-v0.1.0.md` — requirement correspondence and disclosed visual limitations
- `concepts/imagegen-metadata-v0.1.0-r1.json` — built-in generation provenance, prompts and hashes
- `validation/` — generated structural and policy-validation evidence

## Current boundary

No CAD source, STL, STEP, 3MF or G-code may be created until concept r1 is
explicitly approved. The concept sheet shows the upright rover, common wheel
axis, mass placement, camera protection, electronics access and non-rolling
landing protection. Exact dimensions, center of mass and skid clearance remain
owned by `design-spec.yaml` and later deterministic CAD checks.
