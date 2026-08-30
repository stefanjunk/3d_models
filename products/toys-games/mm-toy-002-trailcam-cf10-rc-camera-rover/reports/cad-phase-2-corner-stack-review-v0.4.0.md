# CAD phase 2 integration review — MM-TOY-002 v0.4.0

Date: 2026-08-30
Decision: **BLOCKED**
Scope: existing `CHASSIS_PRINTED` v1, experimental suspension/carrier v1 and the documented corner-stack-v2 proposal

## Outcome

The current suspension/carrier work is not a functional continuation of the
approved design and must not be promoted to a print candidate.  The exact v1
STEP baseline contains static chassis collisions.  The proposed v2 removes the
approved upper wishbone, uses the coil-over shock as a locating member, fixes
the front carrier with two vertical screws so it cannot steer, and places a
motor clamp on every moving carrier although the approved decomposition assigns
one chassis-fixed motor module to each axle.

The approved revision remains `0.4.0`.  No approved user requirement changed;
the rejected source diverged from the approved double-wishbone/ball-joint
contract.  The permitted next CAD route is therefore to return to that contract,
not to approve the experimental lower-arm/trailing-arm geometry by inertia.

## Reproducible baseline evidence

Command:

```bash
python cad/validate_corner_stack.py \
  --output validation/corner-stack-v1-integration-2026-08-30-r4.json
```

The command deliberately returns exit code `1` because the integration gate
fails.  The JSON report records input hashes and refuses to overwrite an
existing evidence file.

| Check | Result | Measured evidence |
|---|---|---|
| Approved architecture match | FAIL | Approved `SUSPENSION_ARMS` is double-wishbone with pins/ball joints; experimental source names the shock as the upper link and adds a carrier motor clamp/chassis tabs |
| Neutral chassis/left arm | FAIL | Boolean common `434.408 mm³` |
| Neutral chassis/right arm | FAIL | Boolean common `434.408 mm³` |
| Neutral chassis/left front carrier | FAIL | Boolean common `713.987 mm³` |
| Neutral chassis/right front carrier | FAIL | Boolean common `713.987 mm³` |
| Provisional 36.8 × 80 mm motor keep-out/chassis | FAIL | Boolean common `23,788.644 mm³`; proxy only, not supplier geometry |
| Rejected pivot plate/90 mm wheel cylinder | FAIL | Boolean common `535.859 mm³` |
| Rejected pivot plate/115 mm wheel cylinder | FAIL | Boolean common `720.000 mm³` |
| Tang and carrier-flange clearance | FAIL | `0.20 mm/side`, contract requires `0.25 mm/side` |
| Pivot ligament | FAIL | Ø3.2 bore plus 5.0 mm ligament requires Ø13.2 local section and pivot `z >= 10.85 mm` above the proposed base; proposal uses `z=8.0 mm` |
| Purchased component authority | REVIEW_REQUIRED | Exact motor, locked axle output/spool, half-shafts/CVDs, ball joints, bearing/hub, wheel and shock remain unselected/unmeasured |

The full-cylinder wheel and motor solids are deliberately conservative keep-out
proxies.  Exact purchased geometry may replace them only after part identity and
measurements are recorded; a likely rim cavity is not evidence of clearance.

All six experimental STL files separately pass the basic topology gate
(watertight, consistently wound, positive volume, one body).  Their reports are
under `validation/corner-stack-v1-mesh-audit-2026-08-30/`.  This confirms only
that each isolated mesh is closed; it does not offset the failed mechanism,
clearance or assembly checks.

The updated `design-spec.yaml` passes the Functional-3D specification validator.
Its remaining warnings are intentional DRAFT gates: final watermark approval,
exact slicer optimization evidence and manufacturing-mesh policy are pending.

## Why the experimental architecture fails

1. The approved concept and decomposition require printed upper and lower
   wishbones at all four corners.  `SHOCK_SET` is assigned spring and damping
   functions, not wheel-location or camber-control functions.
2. A carrier clevis bolted through two vertical M3 holes to one rigid arm plate
   removes the front upright's steering degree of freedom.  An articulated
   upright needs the approved ball-joint/kingpin interfaces and a separate tie
   rod.
3. A motor clamp and chassis anti-rotation tabs on every carrier both
   over-constrain suspension motion and imply four motor locations.  The
   approved two-motor decision instead needs one chassis-fixed drive module per
   axle and articulated shafts to the moving uprights.
4. The rejected trailing-arm proposal needs roughly `-22.37°` to `+21.70°`
   rotation for a ±15 mm wheel-center sweep.  Its lower shock-eye center moves
   from `z=-1.68 mm` to `z=28.36 mm`, while the provisional eye distance changes
   from `53.93 mm` to `32.11 mm`.  No purchased shock or joint-angle evidence
   supports that range.
5. With the nominal 90 mm tire, wheel-center `z=5 mm` correctly touches the
   declared ground plane at `z=-40 mm`.  A 115 mm tire at the same axle height
   penetrates that plane by `12.5 mm`; the 90–115 mm envelope therefore cannot
   share one frozen axle-height/ground-clearance claim.

## Purchased-part search

The repository-local functional parts store contains no qualified motor, wheel,
servo, bearing, shaft, ball-joint, CVD or shock entry for this rover.  The only
project values are provisional envelopes.  Existing M3/5 mm sample interfaces
are unqualified digital examples and cannot establish this vehicle's fit or
load capability.

## Recommended continuation contract

The least disruptive route is:

- retain the approved double-wishbone layout;
- use purchased ball joints or kingpin hardware at the upright, with the shock
  attached only between the chassis tower and lower wishbone;
- use one chassis-fixed geared drive module per axle, a locked output/spool and
  two purchased articulated half-shafts/CVDs to bearing-supported uprights;
- model only keep-outs until exact motor, output, CVD plunge/angle, bearing,
  wheel offset, ball-joint and shock dimensions are selected and measured;
- validate neutral, bump, droop, diagonal articulation and front steering at
  both locks, including fasteners, tool paths, tires, shocks and driveshafts.

A rigid live-axle/4-link route could use one motor per axle more simply, and four
independent wheel motors could preserve independent suspension, but either
choice changes the approved concept or two-motor requirement and therefore
reopens requirements, concept and decomposition approval.

## Manufacturing, optimization and release state

- No replacement CAD, STEP, STL, 3MF or G-code was generated in this review.
- Exact Anycubic machine/process/filament JSON profiles are absent, so slicing
  remains fail-closed.
- Structural lightweighting is not attempted: steering and suspension are
  vehicle-control parts, and the current baseline has neither a valid load path
  nor physical qualification.
- Physical fit, fatigue, steering, braking, failsafe and driving gates remain
  human-controlled and not run.
- The `metriMade.com` mark remains deferred until a stable, verified production
  body exists; it is not inserted into rejected DRAFT geometry.

## Next human decision

Approve the recommended double-wishbone plus chassis-fixed one-motor-per-axle
route and permit exact component research/selection, or request a requirements
revision for rigid axles or four wheel motors.  Production suspension CAD stays
blocked until that decision and the purchased interface identities exist.
