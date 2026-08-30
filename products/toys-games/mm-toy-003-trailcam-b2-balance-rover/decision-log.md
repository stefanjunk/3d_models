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
