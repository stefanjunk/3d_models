# Decision log — MM-TOY-003

## 2026-08-30 — Product creation and requirements candidate 0.1.0

- Assigned product ID `MM-TOY-003`, portfolio record `PORT-099` and product
  folder `products/toys-games/mm-toy-003-trailcam-b2-balance-rover/`.
- Classified the request as a new design inspired by `MM-TOY-002`, not as a
  revision or reduced-wheel rendering of that product.
- Preserved the TrailCam design language, protected FPV camera, independent
  control/video paths and serviceable electronics as inferred intent.
- Replaced the four-wheel/suspension/steering architecture with one geometric
  wheel axis, two independently driven encoder wheels and active inverted-
  pendulum stabilization. A continuous mechanical axle is not required and
  would obstruct the differential-torque steering strategy.
- Selected `balanced-hybrid` because the user did not choose a fabrication
  preference: print the custom structure and protection; buy precision, wear,
  electrical and control components.
- Recommended a 120 mm wheel baseline, 2.5 km/h software speed limit, firm
  mostly level ground and a center of mass 70–110 mm above the wheel axis.
- Recommended non-rolling sacrificial landing skids/hoops. They are not wheels,
  remain clear in the normal balance range and protect the camera, battery and
  electronics after disarm or tip-over.
- Kept exact motor, encoder, controller, IMU, driver, battery, hub, wheel and
  electronics revisions provisional. Purchased-part measurements must become
  authoritative before production interfaces are modeled.
- Marked the requirements gate `pending` and concept/CAD work `blocked` until
  Stefan explicitly approves or corrects revision 0.1.0.
- Chose the guided autonomy policy as a conservative workflow assumption: human
  approval owns requirements, concept, print candidate and all physical/release
  stages; deterministic agent checks may own intermediate digital stages.

## 2026-08-30 — Requirements approval

- Stefan approved requirements revision `0.1.0` with the response
  `freigegeben`.
- Accepted the recommended firm-ground first prototype, retained independent
  ELRS/analog-FPV links and allowed non-rolling landing skids/hoops.
- Set the concept gate to `pending`. Production CAD and manufacturing exports
  remain blocked until a concept image for this exact specification revision is
  explicitly approved.

## 2026-08-30 — Concept candidate 0.1.0-r1

- Used the built-in image-generation path with the approved requirements and
  `MM-TOY-002` concept v0.4.0-r2 as a style/material reference only.
- Rejected the first internal output as a final candidate because the tower was
  visually too tall and the lower landing member appeared ground-contacting.
- Iterated the proportions and landing protection, then replaced the upper-right
  front view with a true side/cutaway view needed to assess the wheel axis,
  mass stack, camera direction and pitch-direction protection.
- Selected `concepts/trailcam-b2-balance-concept-v0.1.0-r1.png`, SHA-256
  `7eff5b88a5e3085398d82c96724dd4f9a6099a48725998b7170a466823ba29a8`.
- Self-review confirms exactly two wheels, one axis, two motor pods, no caster,
  no suspension, protected FPV, battery above axle and an exploded component
  arrangement. Exact dimensions and visible skid clearance remain non-authoritative.
- Concept approval remains `pending`; no production CAD is authorized yet.

## 2026-08-30 — Concept approval

- Stefan approved concept `0.1.0-r1` with the response `freigegeben`.
- Froze the concept-level architecture and appearance direction: two coaxial
  independently driven wheels, compact upright ribbed core, battery above the
  axis, protected front camera, separated antennas and non-rolling landing
  protection.
- Opened the decomposition gate. Production CAD remains blocked until the
  component authority, interface graph, keep-outs, control architecture,
  purchased-part candidates and assembly sequence are explicitly approved.

## 2026-08-30 — Decomposition candidate 0.1.0-decomposition.1

- Routed all custom functional geometry to parametric B-Rep and all exact motor,
  wheel, hub, electronics, battery, RF and fastener geometry to purchased-part
  records. No organic or image-to-3D component is required; concept r1 remains
  appearance evidence only.
- Established the axle-centered right-handed frame, 15 component groups, 21
  owned interfaces and 11 functional keep-outs. The generated plan validation
  passes with zero errors and zero warnings.
- Selected Pololu item 4755 encoder gearmotors and item 1995 metal brackets as
  provisional candidates because their official speed class and interface data
  suit the architecture. Exact wheels and metal hubs remain open and block exact
  drive-interface CAD.
- Selected Teensy 4.1, an ICM-42688-P-class SPI IMU, Cytron MDD10A, RunCam
  Phoenix 2 SE V2, SpeedyBee TX800 and RadioMaster ER5C as research candidates,
  not qualified inventory. Exact delivered parts must be measured.
- Recorded that the MDD10A does not satisfy current telemetry/fault reporting by
  itself. External current sensing and a fail-safe enable path must be qualified,
  or the driver must be replaced.
- Recorded regeneration versus emergency-disconnect behavior as a power hazard;
  battery, BEC, fuse, sensing and disconnect topology remain powered-test
  blockers.
- Defined cascaded velocity, pitch/rate and yaw control, a supervisory state
  machine, independent video/control paths and a fail-closed test ladder from
  simulation through restrained and supervised physical operation.
- Preliminary checks give 2.26 km/h at 100 rpm with a 120 mm wheel and static
  per-wheel gravity torque of 0.165 Nm at the target case or 0.247 Nm at the
  conservative mass/COM envelope. These are sizing checks, not stability or
  continuous-motor qualification.
- Set decomposition approval to `pending`. Production CAD and all powered tests
  remain blocked until Stefan explicitly approves this candidate.
