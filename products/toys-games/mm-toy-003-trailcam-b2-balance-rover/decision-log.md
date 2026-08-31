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

## 2026-08-30 — Decomposition approval

- Stefan approved `0.1.0-decomposition.1` with the response `freigegeben`.
- Froze the component authority, axle-centered coordinate frame, interface
  ownership, keep-outs, provisional COTS routing, control decomposition and
  fail-closed test ladder as the basis for deterministic proxy/CAD work.
- Opened the agent-controlled `parametric-source` stage under the guided
  autonomy policy. Exact purchased-part interfaces, slicer profiles, powered
  tests, watermark and release gates remain blocked by their recorded evidence.

## 2026-08-30 — Parametric candidate 0.1.0-parametric.1

- Created an axle-centered CadQuery assembly with exactly two 120 mm wheel
  proxies, two independent coaxial motor proxies, five structural chassis
  bodies and seven removable printed modules. All 12 printed bodies remain
  individually orientable within 220 × 220 × 250 mm.
- Exported editable STEP masters and explicitly labeled `DRAFT` STL validation
  meshes. The assembly view is also available as a DRAFT GLB/PNG preview; none
  of these files is a print release.
- Verified the 179 × 245 × 250 mm upright envelope, 7.5 mm nominal wheel/body
  gap, 22.88° first landing contact and 14.32 mm landing clearance at 12° pitch.
- Added a nonlinear inverted-pendulum proxy and sampled 250 Hz LQR. Its
  provisional ±8° cases settle below 1° in 1.21 s and stay within the declared
  transient-force/corridor limits. This is model evidence only, not firmware or
  hardware safety evidence.
- Kept the parameter-source stage blocked because `ACC-MASS-001` currently says
  “assembled center of mass.” The provisional whole assembly is 1875.65 g with
  COM 54.61 mm above the axle and fails the 70–110 mm band. The reduced-order
  pendulum lump used by the provisional plant, excluding the axle-grouped
  wheels, hubs, motors and brackets, is 1210.65 g with COM 84.90 mm and passes
  that band diagnostically. This grouping is not physical mass-property
  authority. The approved requirement must be clarified or the mass layout
  deliberately changed; it was not silently reinterpreted.
- Required proxy clearances exceed their thresholds, but the available
  nearest-vertex method is diagnostic only and therefore remains
  `REVIEW_REQUIRED`. Exact Manifold motor/bracket overlap checks pass.
- All DRAFT part meshes are watertight, consistently wound, positive-volume
  single components within size/face budgets. Release remains blocked because
  no certified self-intersection backend is configured.
- Did not apply speculative lightweighting. The optimization workflow requires
  a complete exact Anycubic machine/process/filament profile and a reproducible
  slicer baseline; those inputs are not yet available. No 3MF or G-code was
  generated.

## 2026-08-30 — Option A and parametric candidate 0.1.0-parametric.2

- Stefan selected Option A. `ACC-MASS-001` therefore remains unchanged and
  applies to the complete assembled rover proxy; the prior reduced-order mass
  grouping remains diagnostic only.
- Raised the battery center from 94 to 136 mm, its cradle and crossmember by
  42 mm, and the control tray/board stack into the protected upper frame. The
  battery remains below the electronics as shown by the approved concept.
- Extended the ribbed side-frame shoulders and roof without exceeding the
  original 250 mm ground-to-top envelope. Shifted the front camera/guard 8 mm
  forward to keep a non-interpenetrating mounting boundary around the raised
  upper crossmember.
- The revised complete proxy is 1877.15 g with COM `[1.69, 0.00, 71.23]` mm.
  It passes maximum mass, 70–110 mm vertical COM, 3 mm lateral offset and the
  centered longitudinal bound. Cradle slots provide 12.2 mm motion per side
  after the M3 shank allowance, satisfying the ±12 mm trim provision.
- The vertical result has only 1.23 mm margin above the lower band. It is a
  proxy PASS, not robustness evidence; exact installed masses and positions
  must be measured before integration approval.
- Correlated the nonlinear plant to the revised proxy: total-mass error is
  0.684% and gravitational-first-moment error is 0.275%. Both ±8° idealized
  release cases settle below 1° in 1.22 s and remain inside command/corridor
  limits.
- Kept the outputs as DRAFT. Exact COTS measurements, exact interface-distance
  validation, certified self-intersection checks, complete Anycubic profiles,
  coupons and all physical/powered tests remain release blockers.
- Aggregate draft validation is `NOT_RUN`, because those required mesh/profile
  capabilities and human physical evidence are intentionally fail-closed.

## 2026-08-30 — Real-parts procurement candidate 0.1.0-bom.1

- Replaced open or family-level component placeholders with a real procurement
  chain and current sources: Pololu 4755 motors, 1995 brackets and 2686 wheel
  adapters; INJORA CRAW18003 rims and CRAW20161023 tires; Gens ace
  GEA503S60X6GT battery; Teensy 4.1; Adafruit 4502 IMU; RadioMaster RP3 V2;
  RunCam Phoenix 2 SE V2; SpeedyBee TX800; and explicit fuse/BEC/disconnect
  components.
- Replaced the provisional Cytron MDD10A choice with Pololu item 2507 Dual
  VNH5019. The selected board exposes per-channel current sense and EN/DIAG and
  better matches the approved fault-monitoring contract. Current calibration,
  regeneration and thermal behavior remain restrained-bench gates.
- Replaced the ER5C PWM receiver candidate with the smaller RP3 V2 EU-LBT
  diversity receiver using CRSF UART so link health and stale-frame behavior
  can be supervised explicitly.
- Selected a 5000 mAh 3S XT60 pack rather than a light 2200 mAh shorty. Its
  153 mm retailer-declared length requires a new cradle, but its 359 g estimated
  mass preserves useful elevated pendulum mass and provides more credible
  runtime headroom.
- Recorded a current rover-parts estimate of 571.67 EUR before shipping;
  transmitter, transmitter cells and charger bring the estimate to 706.86 EUR.
  A new analog FPV viewer is optional and raises the example total to 945.86 EUR.
- The selected wheel/rim/adapter pair is about 358 g instead of the 210 g proxy,
  while the real upper control stack is substantially lighter than its 150 g
  proxy. The unchanged assembly is therefore estimated near 1.95 kg and 60 mm
  vertical COM before trim, which fails the approved 70–110 mm band.
- Added a real 300 g steel-segment trim product to the procurement list, but did
  not freeze the installed amount. Approximately 180 g at z about 186 mm gives
  a calculation point near 2.13 kg and 70.8 mm; the actual 150–250 g expected
  range must be set from measured printed and purchased parts inside a closed,
  mechanically retained cassette. Adhesive alone is not structural retention.
- Kept all geometry and operation blocked. Delivered-part intake, a new
  component-driven CAD revision, repeated whole-system mass properties and the
  existing restrained electrical/control test ladder are still required.

## 2026-08-30 — Component-driven print parts 0.1.0-parametric.3

- Treated Stefan's instruction to create the print components for BOM
  `0.1.0-bom.1` as authorization for the already approved parametric-source
  phase, without expanding authority to printing or powered operation.
- Replaced the 12-part planning proxy with 19 serviceable printed rover parts:
  two side frames, axle member, two bracket pods, three upper crossmembers,
  battery cradle, electronics deck, IMU datum, power panel, camera guard, two
  landing parts, two antenna guides and a bolted ballast cassette/lid.
- Registered manufacturer- or retailer-declared envelopes for Pololu
  4755/1995/2686 and 2507, INJORA 120 × 42 mm wheel stack, Gens ace
  153 × 44 × 25 mm battery, Teensy 4.1, Adafruit 4502, TX800, RP3, RunCam,
  XT60E-M and fuse holder. Delivered samples remain interface authority.
- Set the wheel track to 216 mm. The nominal 42 mm tire retains 6.0 mm to the
  nearest printed structure; a declared 44 mm case retains 5.0 mm, while 46 mm
  is explicitly outside the contract.
- Sized the battery cradle for 1.0 mm nominal clearance per side and at least
  ±12 mm longitudinal trim. Added six process-matched coupons for the highest
  uncertainty sample interfaces instead of freezing retailer dimensions as
  production truth.
- Added a mechanically bolted 180 g-capacity ballast cassette. The current
  complete digital ledger uses only 120 g and totals 2114.66 g with COM
  `[0.31, -0.75, 71.16]` mm; installed mass remains measurement-owned.
- Verified 19 valid B-Rep solids, one-axis/two-wheel architecture, envelope,
  bed fit, clearances, mass/COM and ±8° control plausibility. The 25 STL files
  have no topology failure; certified self-intersection remains `NOT_RUN`.
- Chose direct analytic B-Rep tessellation without decimation because the 19
  rover meshes total only 68,582 triangles and protected fit surfaces would be
  exposed to unnecessary approximation.
- Kept the aggregate result at DRAFT/`NOT_RUN`: exact sample intake, physical
  coupon fit, certified self-intersection, complete Anycubic profiles, 3MF/
  G-code, watermark regression and all powered tests remain open gates.

## 2026-08-31 — Preflight and dimensioned COTS candidate 0.1.0-bom.2

- Replaced the generic retrospective preflight with a schema-valid system
  assessment covering 22 entities and 18 mechanical, electrical, data,
  optical, human and environmental interfaces.
- Rated the intrinsically coupled active-balance product `C5` at 91.75/100,
  readiness `R2`, criticality `K3`, Lane `E` and release `HOLD`. The exact
  Anycubic profile set and all physical/dynamic evidence remain absent.
- Raised critical hardpoint capture from R2 to nominal R3 by registering exact
  manufacturer parts and official drawings or linked CAD, without treating
  supplier nominal data as delivered-part tolerance authority.
- Selected the BaneBots `T81H-RM61` 6 mm hub and `T81P-496BB` 123.825 x
  20.32 mm wheel as the `bom.2` replacement for the cross-brand Pololu 2686 /
  INJORA beadlock stack. The matched family has a direct hub/wheel contract,
  linked hub STEP and currently stated manufacturer lead time.
- Retained Pololu 4755 motors and 1995 brackets, Pololu 2507 driver and 2851
  regulator, Teensy 4.1, Adafruit 4502, RP3 V2, RunCam Phoenix 2 SE V2, TX800,
  Gens ace battery and Littelfuse holder with explicit evidence and sample
  gates. The battery availability statement is contradictory and must be
  rechecked before ordering.
- Calculated only a non-authoritative mass substitution: the matched T81
  wheel/hub stack reduces the prior ledger about 40.49 g total, suggesting
  2074.17 g and z-COM 72.54 mm if every other input remains unchanged.
- Recorded the envelope consequence instead of inheriting the old pass: the
  larger wheel projects the unchanged 249.5 mm body to 251.41 mm upright
  height, so the next CAD must recover at least 1.41 mm below the 250 mm limit.
- Marked `0.1.0-parametric.3` as passed historical `bom.1` evidence but stale
  for `bom.2`. No CAD mesh, 3MF, G-code, print or powered test was produced in
  this phase.
