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
| REQ-STRUCT-001 | critical | requested | Primary payload loads shall pass through measured chassis hardpoints, adapter nodes and two rails; bodyposts may locate only a light cover. | datum inspection, load-path section review, clamp-slip test and proof-load test |
| REQ-MASS-001 | critical | requested | The traction battery shall remain in the lowest approved purchased-chassis position and the upper electronics bridge shall be open, ribbed and serviceable. | assembly proxy, center-of-mass comparison and service-access review |
| REQ-KEEP-001 | critical | requested | No payload component, cable or fastener may enter steering, suspension, wheel, driveshaft, motor, battery-access, disconnect, camera-view or RF-active keep-outs. | exact CAD collision and swept-volume checks plus full-travel physical inspection |
| REQ-MFG-001 | important | recommended | Printed functional components shall be deterministic CadQuery B-Rep solids with STEP, watertight STL and 3MF handoff outputs after concept and decomposition approval. | source regeneration, solid audit, mesh validation and exact slicer preflight |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-CONCEPT-001 | open | Approve concept revision 0.3.0-r2 and this functional decomposition before production CAD. | Requirements revision 0.3.0 is approved; the selected concept and decomposition are awaiting explicit human approval. | User approval or corrections naming concept revision 0.3.0-r2 and the decomposition direction. | proxy, component, integration, manufacturing, physical, release |
| DEC-CHASSIS-001 | open | Freeze the exact 1:10 crawler chassis revision and measured hardpoint/motion contract. | Tamiya CC-02 is only the recommended first reference; legacy dimensions are not verified. | Named chassis kit/revision, calibrated measurements, hardpoint table, motion sweeps and battery/disconnect envelope. | proxy, component, integration, manufacturing, physical, release |
| DEC-COTS-001 | provisional | Freeze measured camera, VTX, receiver, antenna, connector, cable and fastener envelopes. | RunCam Phoenix 2 SE V2, SpeedyBee TX800 and RadioMaster ER5C are platform-family candidates, not measured CAD authorities. | Exact purchased revisions, supplier drawings, calibrated samples, connector exits, bend radii and antenna active-element boundaries. | proxy, component, integration, physical, release |
| DEC-LOAD-001 | provisional | Approve payload mass, proof load and impact severity. | Planning values are 500 g service payload, 1000 g static proof load and supervised operation at or below 5 km/h. | Weighed electronics assembly, approved test fixture and test acceptance confirmation. | component, integration, physical, release |
| DEC-PROCESS-001 | provisional | Freeze printer, PETG product, material condition, orientation and Anycubic process profile. | Kobra 3 Max, 0.6 mm nozzle, 0.66 mm line width and 0.24 mm layers are planning assumptions. | Complete exact machine/process/filament JSON profiles and process-matched coupon results. | manufacturing, physical, release |
| DEC-RADIO-001 | open | Select RadioMaster MT12 ELRS or protocol-family-compatible Pocket transmitter ergonomics. | MT12 is recommended for surface controls; Pocket preserves more operator familiarity with OpenQuad. | Operator choice plus bound-receiver, channel-map and failsafe evidence. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| CHASSIS_COTS | purchased | cots | authoritative drivetrain, suspension, battery, frame and primary mounting datums | [-250, -170, -100] → [250, 170, 105] (500 × 340 × 205 mm) | supplier assembly / chassis | IF-CHASSIS-ADAPTERS |
| ADAPTER_SET | parametric | brep | primary printed load path between chassis hardpoints and purchased rails | [-180, -70, 5] → [180, 70, 55] (360 × 140 × 50 mm) | PETG pending process approval / structural | IF-CHASSIS-ADAPTERS, IF-ADAPTERS-RAILS, IF-ADAPTERS-HARDWARE |
| RAILS_COTS | purchased | cots | lightweight structural span and bridge datum | [-195, -47, 35] → [195, 47, 45] (390 × 94 × 10 mm) | square tube; exact material pending / rail | IF-ADAPTERS-RAILS, IF-RAILS-BRIDGE |
| ELECTRONICS_BRIDGE | parametric | brep | serviceable printed platform with edge beams, radiused windows and local mounting pads | [-110, -60, 42] → [130, 60, 90] (240 × 120 × 48 mm) | PETG pending process approval / structural | IF-RAILS-BRIDGE, IF-BRIDGE-CAMERA-GUARD, IF-BRIDGE-RF-MOUNTS |
| CAMERA_GUARD | parametric | brep | precise camera interface, fixed tilt and sacrificial frontal protection | [105, -30, 35] → [155, 30, 95] (50 × 60 × 60 mm) | PETG pending impact coupon / orange service/protection accent | IF-BRIDGE-CAMERA-GUARD, IF-CAMERA-GUARD-CAMERA |
| CAMERA_COTS | purchased | cots | purchased optical and mounting-envelope authority | [118, -9.5, 52] → [140, 9.5, 71] (22 × 19 × 19 mm) | supplier assembly / camera | IF-CAMERA-GUARD-CAMERA |
| RF_MOUNT_SET | parametric | brep | printed retention, cooling clearance, cable strain relief and RF keep-out enforcement | [-85, -58, 48] → [70, 58, 120] (155 × 116 × 72 mm) | PETG pending thermal and fit coupons / structural with orange service tabs | IF-BRIDGE-RF-MOUNTS, IF-RF-MOUNTS-RX, IF-RF-MOUNTS-VTX |
| RX_COTS | purchased | cots | purchased rover control interface and antenna authority | [-65, -48, 52] → [-25, -15, 78] (40 × 33 × 26 mm) | supplier assembly / receiver | IF-RF-MOUNTS-RX |
| VTX_COTS | purchased | cots | purchased video transmitter, thermal and antenna-connector authority | [5, 15, 52] → [40, 50, 80] (35 × 35 × 28 mm) | supplier assembly / video transmitter | IF-RF-MOUNTS-VTX |
| HARDWARE_KIT | purchased | cots | primary bolted-joint and tool-envelope authority | [-185, -75, 0] → [185, 75, 90] (370 × 150 × 90 mm) | metal to approved specification / hardware | IF-ADAPTERS-HARDWARE |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-CHASSIS-ADAPTERS | CHASSIS_COTS ↔ ADAPTER_SET | CHASSIS_COTS | purchased_mate | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION, KEEP-BATTERY-ACCESS, KEEP-DISCONNECT |
| IF-ADAPTERS-RAILS | ADAPTER_SET ↔ RAILS_COTS | RAILS_COTS | fastener | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION, KEEP-BATTERY-ACCESS |
| IF-RAILS-BRIDGE | RAILS_COTS ↔ ELECTRONICS_BRIDGE | RAILS_COTS | fastener | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION, KEEP-BATTERY-ACCESS, KEEP-DISCONNECT |
| IF-BRIDGE-CAMERA-GUARD | ELECTRONICS_BRIDGE ↔ CAMERA_GUARD | ELECTRONICS_BRIDGE | fastener | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-CAMERA-FOV, KEEP-MOTION |
| IF-CAMERA-GUARD-CAMERA | CAMERA_GUARD ↔ CAMERA_COTS | CAMERA_COTS | purchased_mate | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-CAMERA-FOV |
| IF-BRIDGE-RF-MOUNTS | ELECTRONICS_BRIDGE ↔ RF_MOUNT_SET | ELECTRONICS_BRIDGE | fastener | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-RF-ACTIVE, KEEP-DISCONNECT, KEEP-CABLES |
| IF-RF-MOUNTS-RX | RF_MOUNT_SET ↔ RX_COTS | RX_COTS | purchased_mate | 0.4 mm | 0 mm | 0 mm | 0 mm | KEEP-RF-ACTIVE, KEEP-CABLES |
| IF-RF-MOUNTS-VTX | RF_MOUNT_SET ↔ VTX_COTS | VTX_COTS | purchased_mate | 0.4 mm | 0 mm | 0 mm | 0 mm | KEEP-RF-ACTIVE, KEEP-CABLES |
| IF-ADAPTERS-HARDWARE | ADAPTER_SET ↔ HARDWARE_KIT | HARDWARE_KIT | purchased_mate | 0.3 mm | 0 mm | 0 mm | 0 mm | KEEP-MOTION, KEEP-BATTERY-ACCESS, KEEP-DISCONNECT |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-MOTION` (swept_volume): steering, suspension, wheels, driveshaft and motor motion across full travel.
- `KEEP-BATTERY-ACCESS` (aabb): traction-battery installation and removal corridor; provisional proxy only. [-125, -80, -20] → [90, 80, 70]
- `KEEP-DISCONNECT` (aabb): visible emergency battery-disconnect hand and cable path; provisional proxy only. [-75, -120, 0] → [40, 0, 100]
- `KEEP-CAMERA-FOV` (swept_volume): camera optical field including lens protection margin at approved fixed tilt.
- `KEEP-RF-ACTIVE` (swept_volume): 2.4 GHz receiver and 5.8 GHz video antenna active-element clearance, separation and rollover envelope.
- `KEEP-CABLES` (swept_volume): power, video, PWM and antenna cable bend radii, connector insertion and strain-relief paths.

## Assembly sequence

1. Measure and freeze the exact purchased chassis, hardpoints, rail section, motion envelopes and battery/disconnect access.
2. Attach ADAPTER_SET to CHASSIS_COTS with HARDWARE_KIT and verify full suspension/steering travel.
3. Capture the two RAILS_COTS in split clamps without drilling the rails.
4. Fasten ELECTRONICS_BRIDGE to the rails and verify load path, tool access and battery removal.
5. Install CAMERA_COTS in CAMERA_GUARD, then install the guarded module at the front bridge interface.
6. Install RX_COTS and VTX_COTS in their separated RF_MOUNT_SET bodies with cable strain relief and antenna keep-outs.
7. Complete electrical, failsafe, thermal, RF, load and low-speed driving checks before FPV operation.

## Validation gates

- `architecture` / `VAL-ARCH` — review function, load path, RF separation, ownership and service sequence Acceptance: purchased chassis owns motion and battery; adapters/rails own primary load; bridge and guards remain serviceable; control and video remain independent
- `proxy` / `VAL-PROXY` — assemble measured chassis, rail, electronics, fastener, cable and swept-volume proxies Acceptance: all datums are frozen and no component enters motion, battery, disconnect, view, RF or cable keep-outs
- `component` / `VAL-COMP` — deterministic CadQuery solid audit, interface sections, minimum-wall review and STL round trip Acceptance: every printed body is a positive B-Rep solid with matching STEP and watertight single-component STL
- `integration` / `VAL-INT` — exact assembly collision, tool access, clamp/fastener, cable and service-removal checks Acceptance: all interface contracts pass and camera/RX/VTX can be serviced without disturbing drivetrain or battery
- `manufacturing` / `VAL-MFG` — slice every printed part with complete explicit Anycubic machine, process and filament JSON profiles Acceptance: all parts fit the bed in approved orientation and required slicer/G-code checks have no FAIL, NOT_RUN or unresolved REVIEW_REQUIRED result
- `physical` / `VAL-PHY` — fit coupons, 50 N clamp-slip, 500 g deflection, 1000 g proof-load, camera impact, thermal, failsafe, range, braking and supervised 5 km/h driving tests Acceptance: all numeric design-spec acceptance limits pass with recorded measurements and no unsafe control/video coupling

## Plan diagnostics

No errors or warnings.
