# MM-TOY-003 — TrailCam B2 Balance FPV Rover

Portfolio record: `PORT-099`

Current revision: `0.1.0` — requirements, concept r1 and decomposition approved;
component-driven candidate `0.1.0-parametric.3` passes its required B-Rep
geometry, parameter-sweep and idealized-control checks but remains a
non-manufacturing DRAFT

Procurement candidate: `0.1.0-bom.1` — real manufacturer parts and current
purchase sources are selected for samples and bench work; the CAD now follows
those declared envelopes, while exact delivered-part measurements and
process-matched coupon results remain required

Lifecycle: `P2 component-driven DRAFT` — a deterministic CadQuery assembly,
19 separate rover parts, six fit coupons, purchased-part registration proxies
and an idealized control model exist. No print release or physical balance
evidence exists.

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
- `architecture/bom-procurement-v0.1.0-bom.1.csv` — selected real parts, quantities, current suppliers, prices, masses and procurement gates
- `reports/purchased-parts-research-v0.1.0.md` — manufacturer-backed component research and selection gaps
- `reports/procurement-bom-v0.1.0-bom.1.md` — coherent drive/control/power/FPV selection, cost, mass impact and order/test sequence
- `validation/procurement-bom-validation-v0.1.0-bom.1.json` — deterministic row, cost, mass and reference checks plus open physical gates
- `reports/preliminary-balance-sizing-v0.1.0.md` — wheel-speed and static torque sanity checks
- `docs/decomposition-review-v0.1.0.md` — concise human approval boundary for the next phase
- `cad/component_parameters.py` and `cad/build_component_rover.py` — BOM-driven dimensions and deterministic 19-part DRAFT export generator
- `cad/validate_component_geometry.py` and `cad/sweep_component_contract.py` — B-Rep, envelope, mass/COM and declared-size-range checks
- `cad/build_fit_coupons.py` — six process-matched sample-fit coupons
- `control/plant_model_component.py` — component-correlated nonlinear balance plausibility model at 250 Hz
- `architecture/printed-parts-bom-v0.1.0-parametric.3.csv` — 19 rover parts plus six mandatory coupons
- `architecture/interface-contract-v0.1.0-parametric.3.json` — current wheel, battery, camera and motor/bracket checks
- `previews/DRAFT-trailcam-b2-assembly-v0.1.0-parametric.3.png` and `.glb` — current non-manufacturing assembly visualization
- `docs/assembly-v0.1.0-parametric.3.md` — intake, coupon, assembly and restrained-test order
- `reports/component-driven-candidate-v0.1.0-parametric.3.md` — current model result, evidence and release boundary
- `reports/optimization-gate-v0.1.0-parametric.3.md` — protected geometry, mesh-efficiency evidence and open slicer baseline
- `validation-project.json` — aggregate fail-closed validation contract
- `validation/` — generated structural and policy-validation evidence

## Current boundary

The current STEP/STL/GLB files are `DRAFT`, not print-release artifacts. The
assembly has exactly two 120 × 42 mm wheel envelopes on one common axis and all
19 rover parts fit the 220 × 220 × 250 mm target in their documented
orientations. The overall DRAFT envelope is 183 × 258 × 249.5 mm.

The component-driven mass ledger includes the real BOM estimates, conservative
solid-PETG part volumes and a 120 g calculation ballast. It totals 2114.66 g
with COM `[0.31, -0.75, 71.16]` mm relative to the axle and therefore passes the
approved complete-assembly bounds digitally. The cassette can hold up to 180 g,
but its installed mass must be derived from the weighed rover; 180 g is not an
automatic installation instruction.

Nominal CAD clearances are 6.0 mm from the 42 mm tire to printed structure,
1.0 mm per side around the declared battery envelope and 1.0 mm around the
19 mm camera body. Six coupons own the physical fit decision. The idealized
controller recovers from ±8° in simulation, but that result is not firmware,
hardware, failsafe or safety evidence.

Mesh topology, volume, complexity and bed fit pass without a reported failure.
Certified self-intersection remains `NOT_RUN`; exact delivered parts and coupon
results remain `REVIEW_REQUIRED`. Complete Anycubic machine/process/filament
profiles are absent, so no 3MF, G-code, print-time or filament claim was
generated. Watermark, printing, powered test and release remain separate human
gates.
