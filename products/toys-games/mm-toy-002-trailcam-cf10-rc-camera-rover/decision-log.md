# Decision log — MM-TOY-002

## 2026-08-29 — Product identity and migration

- Assigned product ID `MM-TOY-002` and portfolio record `PORT-096`.
- Created `products/toys-games/mm-toy-002-trailcam-cf10-rc-camera-rover/`.
- Moved the unchanged legacy PDF into `docs/legacy/`.
- Initially left `products/toys-games/bom_budget_de.csv` loose because its rows are for OpenQuad; the later integration moved it into `MM-DRN-001` and TrailCam references only the shared component decision.
- Classified the product as `P0 Idea`, because the PDF's claimed generator, parameters, ten STL files, validation outputs, BOM and license are absent.

## 2026-08-29 — Workflow boundary

- Selected the guided project policy. Requirements, concept, decomposition and print-candidate decisions remain human gates.
- Production CAD and manufacturing exports are blocked until current revision `0.3.0` requirements and the derived concept are explicitly approved.

## 2026-08-29 — Recommended redesign direction

- Preserve the balanced-hybrid architecture and the separation of RC control from video.
- Replace the upper-deck battery placement with the lowest approved COTS chassis battery position.
- Replace a primary bodypost load path with a measured frame/hardpoint adapter; bodyposts may remain locators for light covers.
- Add a replaceable camera guard, strain relief, protected cable routes and explicit motion keep-outs.
- Rebuild precise geometry in CadQuery so functional interfaces also have STEP outputs.
- Treat the report's 42.2% CAD-volume saving as an unreproducible historical observation until an exact baseline and slicer profile exist.

## 2026-08-29 — FPV correction and component-family direction

- Revised the pending requirements from `0.2.0` to `0.3.0`; no approved gate was invalidated because requirements were still pending.
- Made FPV camera operation an explicit core function rather than an optional payload.
- Selected the OpenQuad analog-FPV family as the provisional reference: RunCam Phoenix 2 SE V2, SpeedyBee TX800 and compatible 5.8 GHz goggles/display.
- Standardized on the EdgeTX/ExpressLRS 2.4 GHz LBT ecosystem, while keeping platform-specific interfaces: serial CRSF/twin-stick for OpenQuad and PWM/surface controls for TrailCam.
- Kept control and video independent. Loss of the video link must not interfere with propulsion failsafe or a commanded stop.
- Excluded submerged RF reuse for Tethys; its primary control/video link remains the Ethernet tether, with ELRS/Wi-Fi permitted only on an optional surface buoy.

## 2026-08-29 — Requirements approval and concept candidate

- Stefan approved requirements revision `0.3.0` with the response `freigegeben`.
- Requirements are approved; concept revision `0.3.0-r2` remains pending explicit approval.
- Selected the second concept because its lower open bridge reduces upper mass,
  improves service access and visibly separates the receiver and video transmitter.
- The image is appearance and architecture evidence only. Purchased components,
  antenna geometry and fasteners remain generic proxies pending exact hardware measurements.
- Production CAD remains blocked until concept and decomposition are explicitly approved.

## 2026-08-29 — Concept depiction correction (r3)

- User reported that the r2 main view showed only one axle / two wheels while the
  underside view showed four wheels. Confirmed as a generation artifact and internal
  inconsistency of `trailcam-cf10-fpv-concept-v0.3.0-r2.png`.
- Approved requirements remain unchanged: purchased 1:10 COTS crawler chassis with two
  axles and four wheels (reference candidate Tamiya CC-02). The correction changes only
  the depiction, not the requirements; the requirements gate stays approved at 0.3.0.
- The first r3 generation attempt failed with `401 token_expired` from the image
  service; the user chose re-authentication plus regeneration and re-authenticated.
- Generated `trailcam-cf10-fpv-concept-v0.3.0-r3.png` with r2 as style reference and an
  explicit two-axle / four-wheel constraint in every view. Main view now includes the
  far-side wheels; underside view shows four wheels and both axles with differentials;
  exploded payload view unchanged.
- Concept gate remains `pending`; r3 replaces r2 as the candidate for explicit human
  approval. r2 is retained as history. User correction recorded in
  `docs/user-correction-concept-wheels-2026-08-29.md` with an eval candidate via
  `3d-skill-maintainer`.

## 2026-08-29 — Concept approval (r3)

- Stefan approved concept revision 0.3.0-r3 with the response "freigegeben".
- Approval recorded in `design-spec.yaml` and `concepts/concept-review-v0.3.0.md`;
  r2 remains history only.
- The decomposition draft (`architecture/hybrid-design-plan-v0.3.0.json` plus
  `architecture/architecture-report-v0.3.0.md`) is now the next human gate.
  Production CAD, slicer work and exports remain blocked until the decomposition
  is explicitly approved.

## 2026-08-29 — Requirements change 0.4.0: self-made chassis

- Stefan requested during the decomposition gate: the chassis shall not be a
  purchased COTS assembly; it shall be 3D-printed or built from carbon-fiber tubes
  with printed connectors, holders, baskets and cases.
- This changes approved requirements (structural base, load path, BOM, risk
  exposure). Per workflow: requirements gate set to `changes-requested`, concept
  approval r3 invalidated, decomposition blocked, specification raised to 0.4.0.
- Engineering direction recommended for the review: carbon-fiber tubes with printed
  nodes over a fully printed chassis; drivetrain, steering and precision parts stay
  purchased; final route and drivetrain/suspension sourcing are the consequential
  open questions of the 0.4.0 requirements review.
- No new concept image is generated before the 0.4.0 requirements are approved.

## 2026-08-29 — 0.4.0 route decisions: fully printed chassis and printed suspension

- Stefan selected the fully printed chassis (not CF tubes with printed nodes) and
  printed suspension arms plus steering links (not donor or discrete COTS
  suspension), explicitly against the lead recommendation.
- The decisions are recorded as user-stated requirements. The lead concern
  (fatigue and impact in FDM parts) is converted into mandatory validation:
  load-aligned orientation, root radii, replaceable wear links, static/impact/
  fatigue coupons (2000 suspension bump cycles, 1000 steering full-travel cycles),
  frame torsion/proof load and explicit human physical-test approval before any
  driving test (AC-STRUCT-001).
- Fabrication preference changed to integrated-print; motor, ESC, servo, radio,
  camera/VTX, wheels/tires and small metal hardware remain purchased.
- Risk class remains normal-functional with an explicit boundary: printed steering
  and suspension parts are part of the control/motion path and require coupon
  qualification plus human physical approval before driving.

## 2026-08-29 — Requirements 0.4.0 approved

- Stefan approved requirements revision 0.4.0 with the response "freigegeben".
- The 0.3.0 approval is recorded as superseded; concept r3 remains invalidated.
- Next gate: a new concept image for revision 0.4.0 (fully printed chassis with
  printed suspension and steering), followed by decomposition re-approval.

## 2026-08-29 — 0.4.0 concept candidate (r2)

- Generated `trailcam-cf10-fpv-concept-v0.4.0-r1.png`; self-review found the
  assembled view omitted the electronics bridge with separated RX/VTX bays.
- Generated `trailcam-cf10-fpv-concept-v0.4.0-r2.png` with the bridge added;
  self-reviewed against `EVAL-visual-concept-wheel-axle-consistency-001`
  (four wheels / two axles consistent in all full-vehicle views) and module
  separation visibility. Both checks pass.
- Concept gate set to pending for 0.4.0 with `concepts/concept-review-v0.4.0.md`.

## 2026-08-29 — Concept 0.4.0 approved

- Stefan approved concept v0.4.0-r2 with the response "freigeben".
- Approval recorded in `design-spec.yaml` and `concepts/concept-review-v0.4.0.md`.
- Next gate: decomposition 0.4.0 (printed part families, purchased scope, open
  decisions on axle/diff, drivetrain set and frame datums).

## 2026-08-30 — Decomposition draft 0.4.0

- Built `architecture/hybrid-design-plan-v0.4.0.json` (bounded subagent draft
  under lead specification; lead-reviewed): 7 printed part families
  (CHASSIS_PRINTED, SUSPENSION_ARMS, STEERING_LINKS, AXLE_CARRIERS,
  ELECTRONICS_BRIDGE, CAMERA_GUARD, RF_MOUNT_SET) and 8 purchased components
  (camera, RX, VTX, drivetrain unit, servo, shocks, wheels, hardware).
- 16 interfaces with keep-out assignments; 7 keep-outs including new
  KEEP-STEERING; DEC-CHASSIS-001 removed, DEC-DATUM-001/DEC-AXLE-001/DEC-DRIVE-001
  added; VAL-PHY extended with AC-STRUCT-001.
- `plan_hybrid_design.py` validation: PASS, 0 errors / 0 warnings; release
  remains blocked behind component/integration/manufacturing/physical/proxy gates.
- Decomposition gate set to pending for explicit human approval.

## 2026-08-30 — Decomposition 0.4.0 approved

- Stefan approved the 0.4.0 decomposition with the response "freigegeben".
- All three upstream human gates (requirements, concept, decomposition) are now
  approved for revision 0.4.0.
- Next phase: freeze designed frame datums (DEC-DATUM-001) from sourced 1:10
  class-reference values, select drivetrain/axle candidates (DEC-AXLE-001,
  DEC-DRIVE-001), then start the parametric CadQuery source phase.

## 2026-08-30 — Frame datum freeze (DEC-DATUM-001)

- Sourced 1:10 class reference from Tamiya CC-02 product pages (58715: wheelbase
  252 mm, tread 164/167 mm, tires 33 x 90 mm, width 198-200 mm, length 390 mm;
  58736: wheelbase 242 mm, tread 160/163 mm; G500 variant wheelbase 267 mm).
- Frozen for CAD start: wheelbase 252 mm, tread 165 mm, tire diameter 90 mm
  (envelope 90-115 mm), overall width max 200 mm, length target 400 mm, ground
  clearance target 40 mm. Recorded in design-spec.yaml geometry.designed_datums.
- Datums are a class reference for the designed printed chassis; they are
  re-verified against the purchased wheels/tires before manufacturing.
- Suspension architecture remains printed independent wishbones per the approved
  0.4.0 concept (the CC-02 4-link rigid axle is reference only, not adopted).

## 2026-08-30 — Drivetrain decision (DEC-AXLE-001 / DEC-DRIVE-001)

- Stefan selected two purchased geared motors, one per axle, with no
  differential/transfer case (recommended option).
- Printed rigid axle housings/carriers carry the motor units; steering remains
  servo plus printed links per the approved 0.4.0 concept.
- Exact motor model/ratio and ESC count stay open until purchase; a 540/550-class
  planetary-geared motor envelope is used for CAD keep-outs and mounts.

## 2026-08-30 — CAD phase 1: CHASSIS_PRINTED v1 draft

- `cad/parameters.py` created as the shared parametric contract (frozen datums,
  provisional purchased envelopes, printed-structure rules).
- `cad/chassis.py` v1 built by a bounded cad-microtask under lead contract and
  lead-reviewed: single valid B-Rep solid, watertight single-body STL,
  396 x 160 x 52 mm, 507.9 cm3, all ten contract features present.
- Accepted as DRAFT; mass optimization (solid servo pedestal, rail cavities) is
  a later optimize-fdm-design candidate, teardrop bores are the v2 DFM candidate.

## 2026-08-30 — Suspension architecture decision (lead)

- The v1 chassis provides lower pivot clevises (z=6) and shock towers (z=45) but
  no upper wishbone pivots. Lead decision: suspension = printed lower wishbone
  arm plus upper coil-over shock acting as the upper link (no printed upper
  arm). This matches the approved concept, keeps fatigue parts minimal and uses
  the existing interface bores.
- Steering remains servo plus printed links to front axle-carrier steering arms.

## 2026-08-30 — Corner stack v2 (lead redesign after suspension v1 integration review)

- Suspension v1 exposed contract errors: shock eye coaxial with the tower bore
  (no stroke) and chassis corner bosses colliding with arm outer ends, carriers
  and the per-axle motor envelope.
- Lead decision corner stack v2: lower wishbone pivots move inboard to
  x=+/-86 (PIVOT_X_MM) at z=8 (PIVOT_Z_MM); chassis clevis inner boss y 55..63,
  4 mm gap y 63..67, outer boss y 67..75, base plate ending at y=75.
- Arm tang 3.6 mm in the gap with >=2 mm bore lip; legs route around the outer
  boss in plan; arm outer plate y 76..80 z 4.2..8.2 with two M3 holes.
- Carrier becomes a clevis over the arm outer plate (flanges z 0.5..4.0 and
  8.4..12.0), upright y 76..82, motor clamp bore 36.8 at (126, z=5) axis y,
  wheel shaft bore 5.0; no upper inward shock arm.
- Shock lower eye moves to the arm outer end (bore 3.2 along y at z ~ 14,
  y 75..81); shock upper eye remains the tower bore at z=45 -> inclined
  coil-over acting as upper link with real stroke.
- Acceptance now includes pairwise boolean-common collision checks between
  chassis, arms and carriers (zero overlap), plus re-run of all v1 checks.

## 2026-08-30 — CAD phase 2 integration gate BLOCKED; trailing-arm v2 rejected

- Deterministic STEP review confirms the v1 static collisions: each measured
  arm intersects the chassis by 434.408 mm3 and each measured front carrier by
  713.987 mm3. The exact report, input hashes and analytic v2 kinematics are in
  `validation/corner-stack-v1-integration-2026-08-30-r4.json`.
- Independent contract review found that the two preceding lead-only
  suspension decisions diverge from the human-approved 0.4.0 concept and
  decomposition. Those approved artifacts require upper and lower wishbones,
  upright pins/ball joints and a coil-over used only for spring/damping. The
  experimental lower/trailing arm instead uses the shock as an upper locating
  link; two vertical M3 carrier fasteners would also remove front steering.
- The experimental carrier motor clamp and chassis anti-rotation tabs conflict
  with the approved quantity/location of two chassis-fixed motor modules, one
  per axle, and imply four over-constrained carrier motor mounts. Exact motor,
  spool/output, articulated half-shaft, bearing, ball-joint, wheel and shock
  identities remain absent from the local parts store.
- The proposed 4.0 mm gap around a 3.6 mm tang and the proposed carrier flanges
  both give only 0.20 mm clearance per side, below the approved 0.25 mm. A 3.2
  mm pivot bore with the interface's 5.0 mm ligament requires a 13.2 mm local
  section and pivot z at least 10.85 mm above the proposed base, not z=8.0 mm.
- `PIVOT_X_MM=86` and `PIVOT_Z_MM=8` remain rejected experimental values; they
  are not production datums. The untracked v1 suspension source/exports are
  preserved as failure evidence and must not be described as a candidate.
- Requirements, concept and decomposition approvals remain valid because this
  decision returns implementation to their explicit double-wishbone contract.
  Production suspension CAD is BLOCKED pending confirmation of the compliant
  route and exact purchased interfaces.
- Recommended continuation: upper and lower printed wishbones with purchased
  ball-joint/kingpin hardware, shock attached only to the lower arm, and one
  chassis-fixed geared drive module per axle feeding a locked spool plus two
  purchased articulated half-shafts/CVDs. Rigid live axles or four wheel motors
  would reopen requirements, concept and decomposition approval.
- Captured the single-scope failure as `EXP-00038` and the targeted contract
  eval as `EVAL-interfaces-suspension-dof-contract-001`; neither is promoted.
