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
