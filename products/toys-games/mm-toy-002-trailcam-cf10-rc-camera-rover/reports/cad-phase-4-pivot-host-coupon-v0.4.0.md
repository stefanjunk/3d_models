# CAD phase 4 — double-wishbone v2 pivot-host coupons

Date: 2026-08-30

Candidate: `0.4.0-draft.3`

Decision: `DRAFT_COUPON_ONLY`
Product release: `BLOCKED`

## Result

Separate front and rear chassis-side interface/process coupons now implement
the longitudinal x-axis lower and upper wishbone clevis topology required by
the approved v2 kinematic contract. The coupons do not modify or validate the
historical chassis v1 and are not installable vehicle parts.

The isolated coupon scope passes:

- one valid B-Rep solid and one watertight, consistently wound STL body for
  each front/rear variant;
- source-to-STEP relative volume error below `5e-15` and STL tessellation
  volume error about `6.01e-5`;
- 0.25 mm nominal radial M3 clearance, 5.05 mm boss ligament, 0.30 mm axial
  eye clearance per side and 0.30 mm radial eye-pocket clearance;
- positive volumetric attachment of every lower boss and upper tower web to
  the rail;
- zero final B-Rep overlap for all eight represented arm eyes;
- zero coupon/tire-envelope overlap in 924 Boolean checks using solid 90 mm
  and 115 mm tire envelopes across the declared motion matrices.

## Design correction retained as evidence

An unrelieved lower eye intersects the hollow rail by 136.438 mm3. Dedicated
13.4 mm pockets therefore remove the rail material inside each 6.6 mm clevis
gap without moving the approved kinematic axes.

Nominal clevis and eye clearance alone does not make the arm route valid. A
trimmed 6 mm diameter straight arm-neck proxy intersects the coupon by up to
46.276 mm3. The geometry is intentionally not hidden or tuned into a paper
pass. Final wishbones need a dog-leg or tapered neck and a new full-travel
collision sweep before any arm STL is generated.

## Deliberate exclusions and gates

- No shock host: its position depends on the final lower-arm path and a
  measured shock body, eye, stroke and articulation envelope.
- No arm, upright, hub, bearing, ball-joint or CVD fit claim.
- The 3.5 mm circular x-axis holes are ream-after-print candidates. A physical
  coupon must decide circular versus teardrop pilot geometry and verify M3 fit.
- No exact Anycubic slice was run because a complete approved explicit
  machine/process/filament JSON profile set is absent.
- No physical, load, impact, fatigue or vehicle-safety claim is made.
- Watermarking remains deferred until the last solid-geometry change of a
  stable product candidate.

## Evidence

- Generator: `cad/double_wishbone_v2_pivot_host_coupon.py`
- Validator: `cad/validate_double_wishbone_v2_pivot_host_coupon.py`
- Artifacts: `cad/exports/v0.4.0-draft.3-pivot-host-coupon/`
- Main report: `validation/double-wishbone-v2-pivot-host-coupon-2026-08-30.json`
- Mesh audits: `validation/dwv2-pivot-host-mesh-audit-2026-08-30/`

## Next permitted geometry phase

Create a separate left-side arm-neck routing study that preserves the approved
inboard axes and eye envelopes, uses the complete ±10 mm travel sweep, and
fails closed on host, tire, halfshaft and shock keep-outs. Do not merge these
coupons into chassis v1 or freeze shock/COTS interfaces without measurements.
