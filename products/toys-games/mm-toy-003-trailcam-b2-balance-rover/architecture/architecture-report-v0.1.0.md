# Hybrid design architecture — TrailCam B2 Balance FPV Rover

- Project ID: `MM-TOY-003`
- Claim: `new_design`
- Sources: design_description, approved_concept_image, supplier_data
- Units: `mm`
- Master envelope: [-95, -130, -60] → [95, 130, 190] (190 × 260 × 250 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, proxy, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-ARCH-001 | critical | approved | The product shall have exactly two independently driven wheels on one common geometric axis and no caster, suspension, steering linkage or second axle. | component count, datum and assembly-envelope checks |
| REQ-CTRL-001 | critical | approved | The body shall use IMU and wheel-encoder feedback in a bounded active balance controller; direct RC-to-motor PWM is prohibited. | control architecture review, deterministic simulation, HIL and restrained physical tests |
| REQ-GEO-001 | critical | approved | The assembled design shall remain within 260 mm width, 190 mm length and 250 mm upright height with 110 to 130 mm wheels. | exact CAD bounds and purchased-part envelope audit |
| REQ-MASS-001 | critical | approved | The target mass is 1800 g, maximum design mass 2200 g, with center of mass 70 to 110 mm above the axle, lateral offset at most 3 mm and longitudinal trim of plus or minus 12 mm. | CAD mass-property estimate followed by component weighing and assembled balance measurement |
| REQ-LAND-001 | critical | approved | Non-rolling replaceable landing protection shall remain clear in normal balance motion and contact no earlier than 22 degrees body tilt. | exact pitch sweep and restrained tip test |
| REQ-DRIVE-001 | critical | approved_target | Each wheel channel shall target 100 to 150 rpm, at least 0.35 Nm continuous output torque and a current-limited transient target of 1.0 Nm. | supplier-curve review and restrained drivetrain dynamometer test |
| REQ-FPV-001 | important | approved | The protected fixed-tilt analog FPV camera and ELRS control receiver shall use independent video and control paths. | wiring review, camera field-of-view check and independent link-loss tests |
| REQ-MFG-001 | critical | approved | Critical geometry shall be parametric B-Rep; purchased components own their exact mating geometry; concept pixels are not dimensional authority. | source audit, interface-owner audit and CAD regression tests |
| REQ-SAFE-001 | critical | approved | Arming, watchdog, stale-data detection, bounded commands, overcurrent and undervoltage handling, tip disarm and deliberate re-arm shall be verified before free balancing. | fault-injection matrix, HIL and restrained physical test ladder |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-DECOMP-001 | open | Approve this functional decomposition, interface ownership and validation routing before production CAD. | Requirements and concept revision 0.1.0-r1 are approved; this plan is the first controlled decomposition candidate. | Explicit human approval of the decomposition candidate. | proxy, component, integration, manufacturing, physical, release |
| DEC-PROCESS-001 | open | Freeze the Anycubic printer, PETG product, drying state, orientation and complete machine/process/filament JSON profile set. | A 0.6 mm nozzle and 0.24 mm layers are planning assumptions only. | Named installed profiles and process-matched fit coupons. | manufacturing, physical, release |
| DEC-MOTOR-001 | provisional | Qualify the two motor and encoder assemblies. | Pololu item 4755, 100:1 37D 12 V encoder gearmotor, matches the 100 rpm speed class and offers a measured supplier envelope. | Two purchased samples, shaft runout and encoder polarity checks, torque/current/thermal characterization and exact mass. | component, integration, physical, release |
| DEC-WHEEL-001 | open | Select the exact 120 mm class wheels and metal 6 mm D-shaft to wheel-hub system. | Only a 120 x 40 mm planning envelope and 205 mm wheel-center track are frozen. | Supplier drawing plus two measured wheel and hub samples, retention method, mass and inertia. | component, integration, manufacturing, physical, release |
| DEC-CONTROL-001 | provisional | Freeze the exact controller, IMU carrier, motor driver, current sensing, regulated supplies, fuse and disconnect. | Teensy 4.1, ICM-42688-P-class SPI IMU and Cytron MDD10A are candidates; MDD10A has no intrinsic current telemetry and therefore needs qualified external sensing or replacement. | Purchased and measured boards, current-sensor choice, timing and noise tests, thermal/fault behavior and complete power schematic. | component, integration, physical, release |
| DEC-POWER-001 | open | Freeze battery voltage, capacity, connector, BEC, fusing, regeneration and emergency-disconnect behavior. | A centered 3S LiPo-class pack is a packaging assumption; opening the circuit during regenerative braking is an unresolved hazard. | Power budget, measured pack, safe disconnect architecture, transient test and runtime evidence. | component, integration, physical, release |
| DEC-MASS-001 | provisional | Close the mass and center-of-mass budget. | Target geometry provides a sliding battery trim but supplier and printed masses are incomplete. | Mass ledger, CAD properties using qualified densities, physical weighing and hang/balance measurement. | integration, physical, release |
| DEC-SAFETY-001 | open | Approve the restrained tuning rig, exclusion zone, fault matrix and staged energy limits. | The design specification defines the test ladder but no rig or physical procedure is approved. | Human-reviewed test plan, rig inspection and witnessed staged results. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| CHASSIS_SET | parametric | brep | primary structural, axle, landing, battery, electronics and appearance datum authority | [-90, -75, -45] → [90, 75, 185] (180 × 150 × 230 mm) | PETG candidate / anthracite structure | IF-CHASSIS-BRACKETS, IF-CHASSIS-CRADLE, IF-CHASSIS-TRAY, IF-CHASSIS-GUARD, IF-CHASSIS-VTX, IF-CHASSIS-RX, IF-CHASSIS-LANDING, IF-CHASSIS-ANTENNAS, IF-CHASSIS-HARDWARE |
| MOTOR_BRACKET_SET | purchased | cots | supplier-owned transition from printed chassis to 37D motors | [-25, -98, -25] → [25, 98, 25] (50 × 196 × 50 mm) | machined aluminium / metal hardware | IF-CHASSIS-BRACKETS, IF-BRACKETS-DRIVE |
| DRIVE_SET | purchased | cots | independent left and right balance and yaw actuation | [-20, -106, -20] → [20, 106, 20] (40 × 212 × 40 mm) | supplier assembly / drive hardware | IF-BRACKETS-DRIVE, IF-DRIVE-WHEELS, IF-ELEC-CONTROL-DRIVE |
| HUB_WHEEL_SET | purchased | cots | ground contact, motor-shaft retention and passive tire compliance | [-60, -126, -60] → [60, 126, 60] (120 × 252 × 120 mm) | rubber or foam tires with metal hubs / black wheels | IF-DRIVE-WHEELS |
| BATTERY_CRADLE | parametric | brep | centered restraint and longitudinal center-of-mass trim | [-55, -50, 20] → [55, 50, 105] (110 × 100 × 85 mm) | PETG candidate plus purchased strap / anthracite structure | IF-CHASSIS-CRADLE, IF-CRADLE-BATTERY |
| BATTERY_COTS | purchased | cots | energy source, fuse, regulated supplies and reachable disconnect | [-48, -42, 32] → [48, 42, 98] (96 × 84 × 66 mm) | supplier battery and power hardware / power module | IF-CRADLE-BATTERY, IF-ELEC-BATTERY-CONTROL |
| CONTROL_TRAY | parametric | brep | rigid electronics datum and serviceable harness-routing authority | [-52, -55, 88] → [52, 55, 153] (104 × 110 × 65 mm) | PETG candidate / anthracite structure | IF-CHASSIS-TRAY, IF-TRAY-CONTROL |
| CONTROL_STACK_COTS | purchased | cots | deterministic sensing, safety supervision and two-channel motor actuation | [-47, -48, 95] → [47, 48, 148] (94 × 96 × 53 mm) | supplier electronics / electronics | IF-TRAY-CONTROL, IF-ELEC-BATTERY-CONTROL, IF-ELEC-CONTROL-DRIVE, IF-ELEC-RX-CONTROL, IF-ELEC-CONTROL-VTX |
| CAMERA_GUARD | parametric | brep | protect camera and express the approved orange TrailCam accent | [45, -30, 108] → [94, 30, 165] (49 × 60 × 57 mm) | orange PETG candidate / orange protection | IF-CHASSIS-GUARD, IF-GUARD-CAMERA |
| CAMERA_COTS | purchased | cots | forward visual sensing for the operator | [62, -10, 124] → [87, 10, 147] (25 × 20 × 23 mm) | supplier electronics / camera | IF-GUARD-CAMERA, IF-ELEC-CAMERA-VTX |
| VTX_COTS | purchased | cots | independent 5.8 GHz video link | [-42, 10, 125] → [-8, 44, 145] (34 × 34 × 20 mm) | supplier electronics / video module | IF-CHASSIS-VTX, IF-ANTENNAS-VTX, IF-ELEC-CAMERA-VTX, IF-ELEC-CONTROL-VTX |
| RX_COTS | purchased | cots | independent bounded control-command and failsafe input | [-43, -44, 125] → [1, -12, 149] (44 × 32 × 24 mm) | supplier electronics / radio module | IF-CHASSIS-RX, IF-ANTENNAS-RX, IF-ELEC-RX-CONTROL |
| LANDING_SET | parametric | brep | non-rolling low-energy resting and tip-impact surfaces | [-95, -70, -56] → [95, 70, -24] (190 × 140 × 32 mm) | orange PETG candidate; TPU contact pads optional after test / orange protection | IF-CHASSIS-LANDING |
| ANTENNA_SET | hybrid | mixed | RF positioning, connector strain relief and active-region keep-out | [-32, -62, 132] → [32, 62, 190] (64 × 124 × 58 mm) | PETG/TPU candidate and supplier RF parts / orange or black mounts | IF-CHASSIS-ANTENNAS, IF-ANTENNAS-VTX, IF-ANTENNAS-RX |
| HARDWARE_KIT | purchased | cots | serviceable structural joining and retention | [-90, -78, -50] → [90, 78, 180] (180 × 156 × 230 mm) | steel fasteners, metal nuts and straps / hardware | IF-CHASSIS-HARDWARE |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-CHASSIS-BRACKETS | CHASSIS_SET ↔ MOTOR_BRACKET_SET | MOTOR_BRACKET_SET | fastener | 0.3 mm | 0 mm | 0 mm | 0 mm | KO-WHEEL-LEFT, KO-WHEEL-RIGHT, KO-SHAFTS, KO-TOOL |
| IF-BRACKETS-DRIVE | MOTOR_BRACKET_SET ↔ DRIVE_SET | DRIVE_SET | purchased_mate | 0 mm | 0 mm | 0 mm | 0 mm | KO-SHAFTS, KO-CABLES |
| IF-DRIVE-WHEELS | DRIVE_SET ↔ HUB_WHEEL_SET | HUB_WHEEL_SET | purchased_mate | 0 mm | 0 mm | 0 mm | 0 mm | KO-WHEEL-LEFT, KO-WHEEL-RIGHT, KO-SHAFTS, KO-PINCH |
| IF-CHASSIS-CRADLE | CHASSIS_SET ↔ BATTERY_CRADLE | CHASSIS_SET | fastener | 0.4 mm | 0 mm | 0 mm | 0 mm | KO-BATTERY-REMOVAL, KO-CABLES, KO-GROUND-SWEEP |
| IF-CRADLE-BATTERY | BATTERY_CRADLE ↔ BATTERY_COTS | BATTERY_COTS | flexible_flange | 1.35 mm | 0 mm | 0 mm | 0 mm | KO-BATTERY-REMOVAL, KO-CABLES |
| IF-CHASSIS-TRAY | CHASSIS_SET ↔ CONTROL_TRAY | CHASSIS_SET | fastener | 0.3 mm | 0 mm | 0 mm | 0 mm | KO-ELECTRONICS, KO-CABLES, KO-TOOL |
| IF-TRAY-CONTROL | CONTROL_TRAY ↔ CONTROL_STACK_COTS | CONTROL_STACK_COTS | fastener | 0.4 mm | 0 mm | 0 mm | 0 mm | KO-ELECTRONICS, KO-CABLES, KO-TOOL |
| IF-CHASSIS-GUARD | CHASSIS_SET ↔ CAMERA_GUARD | CHASSIS_SET | fastener | 0.4 mm | 0 mm | 0 mm | 0 mm | KO-CAMERA-FOV, KO-GROUND-SWEEP, KO-TOOL |
| IF-GUARD-CAMERA | CAMERA_GUARD ↔ CAMERA_COTS | CAMERA_COTS | fastener | 0.35 mm | 0 mm | 0 mm | 0 mm | KO-CAMERA-FOV, KO-CABLES |
| IF-CHASSIS-VTX | CHASSIS_SET ↔ VTX_COTS | VTX_COTS | fastener | 0.4 mm | 0 mm | 0 mm | 0 mm | KO-ELECTRONICS, KO-RF, KO-CABLES |
| IF-CHASSIS-RX | CHASSIS_SET ↔ RX_COTS | RX_COTS | flexible_flange | 0.5 mm | 0 mm | 0 mm | 0 mm | KO-ELECTRONICS, KO-RF, KO-CABLES |
| IF-CHASSIS-LANDING | CHASSIS_SET ↔ LANDING_SET | CHASSIS_SET | fastener | 0.3 mm | 0 mm | 0 mm | 0 mm | KO-GROUND-SWEEP, KO-WHEEL-LEFT, KO-WHEEL-RIGHT, KO-PINCH |
| IF-CHASSIS-ANTENNAS | CHASSIS_SET ↔ ANTENNA_SET | CHASSIS_SET | flexible_flange | 0.5 mm | 0 mm | 0 mm | 0 mm | KO-RF, KO-GROUND-SWEEP, KO-CABLES |
| IF-ANTENNAS-VTX | ANTENNA_SET ↔ VTX_COTS | VTX_COTS | purchased_mate | 0 mm | 0 mm | 0 mm | 0 mm | KO-RF, KO-CABLES |
| IF-ANTENNAS-RX | ANTENNA_SET ↔ RX_COTS | RX_COTS | purchased_mate | 0 mm | 0 mm | 0 mm | 0 mm | KO-RF, KO-CABLES |
| IF-CHASSIS-HARDWARE | CHASSIS_SET ↔ HARDWARE_KIT | HARDWARE_KIT | fastener | 0.3 mm | 0 mm | 0 mm | 0 mm | KO-TOOL, KO-CABLES |
| IF-ELEC-BATTERY-CONTROL | BATTERY_COTS ↔ CONTROL_STACK_COTS | BATTERY_COTS | other | 0 mm | 0 mm | 0 mm | 0 mm | KO-BATTERY-REMOVAL, KO-CABLES, KO-ELECTRONICS |
| IF-ELEC-CONTROL-DRIVE | CONTROL_STACK_COTS ↔ DRIVE_SET | CONTROL_STACK_COTS | other | 0 mm | 0 mm | 0 mm | 0 mm | KO-CABLES, KO-WHEEL-LEFT, KO-WHEEL-RIGHT |
| IF-ELEC-CAMERA-VTX | CAMERA_COTS ↔ VTX_COTS | VTX_COTS | other | 0 mm | 0 mm | 0 mm | 0 mm | KO-CABLES, KO-RF, KO-CAMERA-FOV |
| IF-ELEC-RX-CONTROL | RX_COTS ↔ CONTROL_STACK_COTS | CONTROL_STACK_COTS | other | 0 mm | 0 mm | 0 mm | 0 mm | KO-CABLES, KO-RF |
| IF-ELEC-CONTROL-VTX | CONTROL_STACK_COTS ↔ VTX_COTS | CONTROL_STACK_COTS | other | 0 mm | 0 mm | 0 mm | 0 mm | KO-CABLES, KO-ELECTRONICS, KO-RF |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KO-WHEEL-LEFT` (cylinder): exact left wheel and tire rotation plus radial growth.
- `KO-WHEEL-RIGHT` (cylinder): exact right wheel and tire rotation plus radial growth.
- `KO-SHAFTS` (swept_volume): motor output shaft, hub retention and tool envelope on the common axle.
- `KO-GROUND-SWEEP` (swept_volume): body, camera and antenna pitch sweep from minus 35 to plus 35 degrees over the ground plane; landing contacts are evaluated separately.
- `KO-BATTERY-REMOVAL` (aabb): battery, strap and connector removal corridor. [-70, -58, 20] → [70, 58, 125]
- `KO-ELECTRONICS` (aabb): board cooling, connector and probe-access volume. [-55, -58, 88] → [55, 58, 160]
- `KO-CAMERA-FOV` (swept_volume): camera lens, full field of view and service corridor.
- `KO-RF` (swept_volume): VTX and receiver antenna active regions, separation and connector bend radii.
- `KO-CABLES` (swept_volume): power, motor, encoder, sensor, video and RF harness corridors with separation and bend radii.
- `KO-PINCH` (swept_volume): human finger exclusion and moving wheel-to-frame pinch clearance.
- `KO-TOOL` (aabb): representative driver and nut-tool access through the central service zone. [-94, -90, -50] → [94, 90, 188]

## Assembly sequence

1. Join the printed chassis set with measured metal through-fasteners and verify the axle datum.
2. Install the purchased motor brackets and encoder gearmotors without wheels.
3. Install the battery cradle, control tray and the measured electronics stack with the IMU on its rigid datum.
4. Route fused battery power, motor leads, encoder leads and signal harnesses through their separated cable corridors.
5. Install camera guard, camera, VTX, receiver and antenna mounts while preserving optical, RF and cooling keep-outs.
6. Install the non-rolling landing set and verify the exact pitch-contact sweep before powered tests.
7. Install measured metal hubs and wheels; verify coaxiality, retention, rotation and pinch clearances.
8. Measure total mass and center of mass, trim the battery position and repeat the pitch/contact sweep.
9. Perform unpowered, wheels-off-ground, restrained, tethered and only then free-balance validation stages.

## Validation gates

- `architecture` / `VAL-ARCH-001` — hybrid-plan schema, cross-reference and decision-gate validation plus human review Acceptance: zero validation errors, no unowned component/interface and explicit decomposition approval
- `proxy` / `VAL-PROXY-001` — low-detail parametric envelope assembly, wheel/ground sweeps and mass-ledger estimate Acceptance: exactly two wheels/one axis, master envelope pass, no critical keep-out collision and plausible trim range
- `component` / `VAL-COMP-001` — measured supplier-part audit and process-matched printed interface coupons Acceptance: all candidate parts identified and measured; every mechanical interface coupon passes before full parts
- `integration` / `VAL-INT-001` — exact assembly collision, accessibility, mass-properties, pitch-contact, harness and control-model regression tests Acceptance: all deterministic gates pass with evidence; unresolved mass, power, driver or wheel decisions are closed
- `manufacturing` / `VAL-MFG-001` — fresh Anycubic Slicer Next headless run using complete explicit machine/process/filament JSON profiles and artifact audit Acceptance: adapter PASS, readable G-code and report, support/seam/layer human review and no stale exports
- `physical` / `VAL-PHYS-001` — unpowered inspection followed by wheels-off-ground, restrained, tethered and supervised free-balance test ladder with fault injection Acceptance: human-approved plan and rig; dimensional, thermal, control, failsafe, landing and service targets pass without uncontrolled motion

## Plan diagnostics

No errors or warnings.
