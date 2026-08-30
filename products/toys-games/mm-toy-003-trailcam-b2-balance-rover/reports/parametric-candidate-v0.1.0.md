# Parametric candidate — 0.1.0-parametric.1

## Outcome

The approved two-wheel TrailCam architecture now has a deterministic DRAFT
CadQuery implementation and an idealized balance-controller model. It remains
blocked from parametric approval and manufacturing release.

## Assembly

- Exactly two provisional 120 × 40 mm wheels on the common Y axis
- Two independent coaxial encoder-gearmotor proxies
- Five-part open ribbed chassis plus battery cradle, control tray, camera guard,
  front/rear non-rolling landing parts and two antenna mounts
- Upright envelope: 179 mm long × 245 mm wide × 250 mm ground-to-top
- Nominal wheel/frame axial gap: 7.5 mm
- First landing contact: 22.88°; clearance at 12° pitch: 14.32 mm
- Every printed body fits the 220 × 220 × 250 mm compatibility target after its
  declared orientation

## Control model

The provisional nonlinear cart-pendulum proxy uses a 1 ms integration step,
250 Hz sampled LQR and actuator lag. Both ±8° release cases settle below 1° in
1.21 s, reach 0.183 m maximum translation and demand 7.93 N maximum command
against a 33.33 N transient proxy limit. Real motor curves, current/voltage
limits, encoder quantization, IMU noise/bias, timing jitter, tire compliance,
traction and faults are not modeled, so this cannot qualify firmware or safe
operation.

## Blocking decision: center-of-mass scope

The approved `ACC-MASS-001` currently applies the 70–110 mm height band to the
“assembled center of mass.” The provisional ledger gives:

| Scope | Mass | COM above axle | Result |
|---|---:|---:|---|
| Complete assembly proxy | 1875.65 g | 54.61 mm | FAIL |
| Reduced-order pendulum lump used by the provisional plant | 1210.65 g | 84.90 mm | PASS diagnostic |

One possible correction is to define the target band for an explicitly
registered reduced-order pendulum mass grouping, while retaining whole-system
mass and lateral/longitudinal balance checks separately. That grouping must be
approved and correlated with measured inertia; it is not a physical COM
substitute. If the current whole-system interpretation is intentional, the mass
stack must instead be redesigned and re-run. Ballast is not assumed.

## Evidence and limits

Geometry and control reports are fresh against their source hashes. Proxy
clearances exceed the declared minima but stay `REVIEW_REQUIRED` because only a
nearest-vertex fallback is available. Mesh topology checks pass for all 12
DRAFT bodies, while certified self-intersection remains `NOT_RUN`. Exact COTS
measurements and complete Anycubic profiles are absent, so no 3MF, G-code,
print-time or filament claims were produced.
