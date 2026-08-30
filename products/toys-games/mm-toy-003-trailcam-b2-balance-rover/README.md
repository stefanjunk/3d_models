# MM-TOY-003 — TrailCam B2 Balance FPV Rover

Portfolio record: `PORT-099`

Current revision: `0.1.0` — requirements candidate; concept, decomposition and
production CAD are blocked pending explicit requirements approval

Lifecycle: `P0 Idea` — controlled product contract exists; no concept image,
CAD, manufacturing export or physical evidence exists yet

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
- `validation/` — generated structural and policy-validation evidence

## Current boundary

No concept image, CAD source, STL, STEP, 3MF or G-code may be created until the
requirements gate is explicitly approved. After approval, the next artifact is
a concept sheet showing the upright rover, the common wheel axis, internal
mass placement, camera protection, electronics access and non-rolling landing
protection.
