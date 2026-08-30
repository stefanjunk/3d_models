# Hybrid design architecture — TrailCam CF10 low-profile FPV rover functional redesign

- Project ID: `MM-TOY-002`
- Claim: `functional_redesign`
- Sources: design_description, concept_image, measurements
- Units: `mm`
- Master envelope: [-250, -170, -100] → [250, 170, 180] (500 × 340 × 280 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, proxy, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-FPV-001 | critical | requested | The rover shall provide a forward analog-FPV view through a guarded RunCam Phoenix 2 SE V2-class camera and a separately mounted SpeedyBee TX800-class VTX. | measured COTS envelopes, field-of-view collision test, power/thermal bench test and supervised video-under-load test |
| REQ-RC-001 | critical | requested | Control shall use the EdgeTX/ExpressLRS 2.4 GHz LBT family through a rover-specific PWM receiver, independent of the analog video link. | wiring review, failsafe test with total video loss, stall/brownout test and controlled range test |
| REQ-STRUCT-001 | critical | requested | Primary vehicle and payload loads shall pass through designed printed frame datums and printed nodes; bodyposts may locate only a light cover. | datum inspection, load-path section review, static/impact/fatigue coupon qualification and proof-load test |
| REQ-MASS-001 | critical | requested | The traction battery shall remain in the lowest designed printed-tray position and the upper electronics bridge shall be open, ribbed and serviceable. | assembly proxy, center-of-mass comparison and service-access review |
| REQ-KEEP-001 | critical | requested | No payload component, cable or fastener may enter steering, suspension, wheel, driveshaft, motor, battery-access, disconnect, camera-view or RF-active keep-outs. | exact CAD collision and swept-volume checks plus full-travel physical inspection |
| REQ-MFG-001 | important | recommended | Printed functional components shall be deterministic CadQuery B-Rep solids with STEP, watertight STL and 3MF handoff outputs after concept and decomposition approval. | source regeneration, solid audit, mesh validation and exact slicer preflight |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-CONCEPT-001 | resolved | Approve concept revision 0.4.0-r2 and this functional decomposition before production CAD. | Concept 0.4.0-r2 approved by Stefan on 2026-08-29; the 0.3.0-r3 approval is invalidated by the chassis-route change recorded in design-spec.yaml revision 0.4.0. | None; approval recorded in design-spec.yaml revision 0.4.0 workflow.concept_approval. |  |
| DEC-DATUM-001 | open | Freeze the designed frame datums (wheelbase, track, ground clearance) from the 1:10 class reference, with Tamiya CC-02 as geometry reference only. | User decision 2026-08-29 removes any COTS/donor chassis; the fully printed chassis takes over frame, suspension and steering, but class-reference values are not yet sourced. | Sourced 1:10 class-reference values and a frozen parameter table before production CAD. | proxy, component, integration, manufacturing, physical, release |
| DEC-AXLE-001 | resolved | Select the axle/differential approach: purchased gearbox/diff unit preferred; printed low-speed gears/axles only with explicit strain justification and bench tests. | User decision 2026-08-30: two purchased geared motors, one per axle; no differential/transfer case; printed rigid axle housings/carriers. Printed gears/axles remain prohibited without strain justification and bench tests. | Named geared motor model with measured mounting envelope before manufacturing. |  |
| DEC-DRIVE-001 | provisional | Freeze the exact drivetrain set (motor class, ratio, servo size) and wheel/tire size for the printed chassis. | Architecture frozen 2026-08-30: two 540/550-class planetary geared motors (one per axle), steering via servo plus printed links; exact motor model/ratio, ESC count and wheel/tire purchase remain open. | Named motor/ratio, ESC count, servo size and wheel/tire selection with measured envelopes. | component, integration, manufacturing, physical, release |
| DEC-COTS-001 | provisional | Freeze measured camera, VTX, receiver, antenna, connector, cable and fastener envelopes. | RunCam Phoenix 2 SE V2, SpeedyBee TX800 and RadioMaster ER5C are platform-family candidates, not measured CAD authorities. | Exact purchased revisions, supplier drawings, calibrated samples, connector exits, bend radii and antenna active-element boundaries. | proxy, component, integration, physical, release |
| DEC-LOAD-001 | provisional | Approve payload mass, proof load and impact severity. | Planning values are 500 g service payload, 1000 g static proof load and supervised operation at or below 5 km/h. | Weighed electronics assembly, approved test fixture and test acceptance confirmation. | component, integration, physical, release |
| DEC-PROCESS-001 | provisional | Freeze printer, PETG product, material condition, orientation and Anycubic process profile. | Kobra 3 Max, 0.6 mm nozzle, 0.66 mm line width and 0.24 mm layers are planning assumptions. | Complete exact machine/process/filament JSON profiles and process-matched coupon results. | manufacturing, physical, release |
| DEC-RADIO-001 | open | Select RadioMaster MT12 ELRS or protocol-family-compatible Pocket transmitter ergonomics. | MT12 is recommended for surface controls; Pocket preserves more operator familiarity with OpenQuad. | Operator choice plus bound-receiver, channel-map and failsafe evidence. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| CHASSIS_PRINTED | parametric | brep | printed frame with ribbed side rails, skid plate, integrated battery tray, suspension pivot bosses, servo and drivetrain mounts and bridge mounts; envelope is provisional until DEC-DATUM-001 freezes the designed frame datums | [-210, -110, -60] → [210, 110, 0] (420 × 220 × 60 mm) | PETG pending process approval / structural | IF-CHASSIS-SUSP, IF-CHASSIS-STEERING, IF-CHASSIS-SERVO, IF-CHASSIS-DRIVE, IF-CHASSIS-BRIDGE, IF-CHASSIS-HARDWARE, IF-CHASSIS-SHOCKS |
| SUSPENSION_ARMS | parametric | brep | replaceable printed wishbone arms at all four corners with load-aligned print orientation and generous root radii per AC-STRUCT-001 | [-230, -160, -95] → [230, 160, -25] (460 × 320 × 70 mm) | PETG pending fatigue coupon / structural with orange replaceable-wear accent | IF-CHASSIS-SUSP, IF-SUSP-CARRIERS, IF-SUSP-SHOCKS |
| STEERING_LINKS | parametric | brep | replaceable printed steering links with load-aligned print orientation and generous root radii per AC-STRUCT-001 | [80, -140, -80] → [230, 140, -30] (150 × 280 × 50 mm) | PETG pending fatigue coupon / structural with orange replaceable-wear accent | IF-CHASSIS-STEERING |
| AXLE_CARRIERS | parametric | brep | printed uprights/axle carriers; drivetrain interface mates a purchased or printed axle per DEC-AXLE-001 | [-230, -165, -90] → [230, 165, 0] (460 × 330 × 90 mm) | PETG pending process approval / structural | IF-SUSP-CARRIERS, IF-CARRIERS-WHEELS, IF-DRIVE-CARRIERS |
| ELECTRONICS_BRIDGE | parametric | brep | serviceable printed platform with edge beams, radiused windows and local mounting pads; mounts to CHASSIS_PRINTED bridge mounts | [-110, -60, 42] → [130, 60, 90] (240 × 120 × 48 mm) | PETG pending process approval / structural | IF-CHASSIS-BRIDGE, IF-BRIDGE-CAMERA-GUARD, IF-BRIDGE-RF-MOUNTS |
| CAMERA_GUARD | parametric | brep | precise camera interface, fixed tilt and sacrificial frontal protection | [105, -30, 35] → [155, 30, 95] (50 × 60 × 60 mm) | PETG pending impact coupon / orange service/protection accent | IF-BRIDGE-CAMERA-GUARD, IF-CAMERA-GUARD-CAMERA |
| CAMERA_COTS | purchased | cots | purchased optical and mounting-envelope authority | [118, -9.5, 52] → [140, 9.5, 71] (22 × 19 × 19 mm) | supplier assembly / camera | IF-CAMERA-GUARD-CAMERA |
| RF_MOUNT_SET | parametric | brep | printed retention, cooling clearance, cable strain relief and RF keep-out enforcement | [-85, -58, 48] → [70, 58, 120] (155 × 116 × 72 mm) | PETG pending thermal and fit coupons / structural with orange service tabs | IF-BRIDGE-RF-MOUNTS, IF-RF-MOUNTS-RX, IF-RF-MOUNTS-VTX |
| RX_COTS | purchased | cots | purchased rover control interface and antenna authority | [-65, -48, 52] → [-25, -15, 78] (40 × 33 × 26 mm) | supplier assembly / receiver | IF-RF-MOUNTS-RX |
| VTX_COTS | purchased | cots | purchased video transmitter, thermal and antenna-connector authority | [5, 15, 52] → [40, 50, 80] (35 × 35 × 28 mm) | supplier assembly / video transmitter | IF-RF-MOUNTS-VTX |
| DRIVETRAIN_COTS | purchased | cots | purchased drivetrain authority: two geared motor units (one per axle) without differential/transfer case per user decision 2026-08-30; printed rigid axle housings/carriers mate the motor gearboxes | [-120, -110, -75] → [120, 110, -5] (240 × 220 × 70 mm) | supplier assembly / drivetrain | IF-CHASSIS-DRIVE, IF-DRIVE-CARRIERS |
| SERVO_COTS | purchased | cots | purchased steering authority; standard 1:10 steering servo class with exact size per DEC-DRIVE-001 | [100, -15, -55] → [145, 15, -15] (45 × 30 × 40 mm) | supplier assembly / servo | IF-CHASSIS-SERVO |
| SHOCK_SET | purchased | cots | purchased coil-over shock candidate set; printed shock bodies are only a later coupon-gated option | [-230, -160, -90] → [230, 160, 5] (460 × 320 × 95 mm) | supplier assembly / shocks | IF-CHASSIS-SHOCKS, IF-SUSP-SHOCKS |
| WHEELS_COTS | purchased | cots | purchased traction and rolling-envelope authority | [-235, -170, -100] → [235, 170, 10] (470 × 340 × 110 mm) | supplier tire and rim / wheels | IF-CARRIERS-WHEELS |
| HARDWARE_KIT | purchased | cots | primary bolted-joint and tool-envelope authority | [-185, -75, 0] → [185, 75, 90] (370 × 150 × 90 mm) | metal to approved specification / hardware | IF-CHASSIS-HARDWARE |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-CHASSIS-SUSP | CHASSIS_PRINTED ↔ SUSPENSION_ARMS | CHASSIS_PRINTED | fastener | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION, KEEP-BATTERY-ACCESS |
| IF-SUSP-CARRIERS | SUSPENSION_ARMS ↔ AXLE_CARRIERS | SUSPENSION_ARMS | fastener | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION |
| IF-CARRIERS-WHEELS | AXLE_CARRIERS ↔ WHEELS_COTS | WHEELS_COTS | purchased_mate | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION |
| IF-CHASSIS-STEERING | CHASSIS_PRINTED ↔ STEERING_LINKS | CHASSIS_PRINTED | fastener | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-STEERING, KEEP-MOTION |
| IF-CHASSIS-SERVO | CHASSIS_PRINTED ↔ SERVO_COTS | SERVO_COTS | purchased_mate | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-STEERING, KEEP-BATTERY-ACCESS |
| IF-CHASSIS-DRIVE | CHASSIS_PRINTED ↔ DRIVETRAIN_COTS | DRIVETRAIN_COTS | purchased_mate | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION, KEEP-BATTERY-ACCESS |
| IF-DRIVE-CARRIERS | DRIVETRAIN_COTS ↔ AXLE_CARRIERS | DRIVETRAIN_COTS | purchased_mate | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION |
| IF-CHASSIS-BRIDGE | CHASSIS_PRINTED ↔ ELECTRONICS_BRIDGE | CHASSIS_PRINTED | fastener | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION, KEEP-BATTERY-ACCESS, KEEP-DISCONNECT |
| IF-BRIDGE-CAMERA-GUARD | ELECTRONICS_BRIDGE ↔ CAMERA_GUARD | ELECTRONICS_BRIDGE | fastener | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-CAMERA-FOV, KEEP-MOTION |
| IF-CAMERA-GUARD-CAMERA | CAMERA_GUARD ↔ CAMERA_COTS | CAMERA_COTS | purchased_mate | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-CAMERA-FOV |
| IF-BRIDGE-RF-MOUNTS | ELECTRONICS_BRIDGE ↔ RF_MOUNT_SET | ELECTRONICS_BRIDGE | fastener | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-RF-ACTIVE, KEEP-DISCONNECT, KEEP-CABLES |
| IF-RF-MOUNTS-RX | RF_MOUNT_SET ↔ RX_COTS | RX_COTS | purchased_mate | 0.4 mm | 0 mm | 0 mm | 0 mm | KEEP-RF-ACTIVE, KEEP-CABLES |
| IF-RF-MOUNTS-VTX | RF_MOUNT_SET ↔ VTX_COTS | VTX_COTS | purchased_mate | 0.4 mm | 0 mm | 0 mm | 0 mm | KEEP-RF-ACTIVE, KEEP-CABLES |
| IF-CHASSIS-HARDWARE | CHASSIS_PRINTED ↔ HARDWARE_KIT | HARDWARE_KIT | purchased_mate | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION, KEEP-BATTERY-ACCESS, KEEP-DISCONNECT |
| IF-CHASSIS-SHOCKS | CHASSIS_PRINTED ↔ SHOCK_SET | SHOCK_SET | purchased_mate | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION |
| IF-SUSP-SHOCKS | SUSPENSION_ARMS ↔ SHOCK_SET | SHOCK_SET | purchased_mate | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-MOTION` (swept_volume): steering, suspension, wheels, driveshaft and motor motion across full travel.
- `KEEP-BATTERY-ACCESS` (aabb): traction-battery installation and removal corridor in the designed printed tray; provisional proxy only. [-125, -80, -20] → [90, 80, 70]
- `KEEP-DISCONNECT` (aabb): visible emergency battery-disconnect hand and cable path; provisional proxy only. [-75, -120, 0] → [40, 0, 100]
- `KEEP-CAMERA-FOV` (swept_volume): camera optical field including lens protection margin at approved fixed tilt.
- `KEEP-RF-ACTIVE` (swept_volume): 2.4 GHz receiver and 5.8 GHz video antenna active-element clearance, separation and rollover envelope.
- `KEEP-CABLES` (swept_volume): power, video, PWM and antenna cable bend radii, connector insertion and strain-relief paths.
- `KEEP-STEERING` (swept_volume): steering link and servo horn travel across full lock.

## Assembly sequence

1. Print CHASSIS_PRINTED and qualify frame, arm and link coupons per AC-STRUCT-001 before vehicle assembly.
2. Assemble SUSPENSION_ARMS and AXLE_CARRIERS to the chassis pivot bosses with HARDWARE_KIT pivot pins and verify full suspension travel.
3. Install DRIVETRAIN_COTS and SERVO_COTS in their printed mounts, connect STEERING_LINKS and verify full steering travel against KEEP-STEERING.
4. Mount WHEELS_COTS and SHOCK_SET and verify the motion envelopes against KEEP-MOTION.
5. Fasten ELECTRONICS_BRIDGE to the chassis bridge mounts and verify load path, tool access and printed battery-tray removal.
6. Install CAMERA_COTS in CAMERA_GUARD, then install the guarded module at the front bridge interface.
7. Install RX_COTS and VTX_COTS in their separated RF_MOUNT_SET bodies with cable strain relief and antenna keep-outs.
8. Complete electrical, failsafe, thermal, RF, load and low-speed driving checks with human physical approval before FPV operation.

## Validation gates

- `architecture` / `VAL-ARCH` — review function, load path, RF separation, ownership and service sequence Acceptance: printed frame owns motion, battery and primary load; bridge and guards remain serviceable; control and video remain independent
- `proxy` / `VAL-PROXY` — assemble frame, suspension, steering, drivetrain, servo, electronics, fastener, cable and swept-volume proxies Acceptance: all datums are frozen per DEC-DATUM-001 and no component enters motion, steering, battery, disconnect, view, RF or cable keep-outs
- `component` / `VAL-COMP` — deterministic CadQuery solid audit, interface sections, minimum-wall review and STL round trip Acceptance: every printed body is a positive B-Rep solid with matching STEP and watertight single-component STL
- `integration` / `VAL-INT` — exact assembly collision, tool access, fastener, cable and service-removal checks Acceptance: all interface contracts pass and camera/RX/VTX can be serviced without disturbing drivetrain or battery
- `manufacturing` / `VAL-MFG` — slice every printed part with complete explicit Anycubic machine, process and filament JSON profiles Acceptance: all parts fit the bed in approved orientation and required slicer/G-code checks have no FAIL, NOT_RUN or unresolved REVIEW_REQUIRED result
- `physical` / `VAL-PHY` — fit, static/impact/fatigue coupons, 50 N clamp-slip, 500 g deflection, 1000 g proof-load, frame torsion, camera impact, thermal, failsafe, range, braking and supervised 5 km/h driving tests Acceptance: all numeric design-spec acceptance limits pass with recorded measurements, AC-STRUCT-001 passes (2000 suspension bump cycles, 1000 steering full-travel cycles, frame torsion and proof load) and human physical approval is recorded before any driving test

## Plan diagnostics

No errors or warnings.
