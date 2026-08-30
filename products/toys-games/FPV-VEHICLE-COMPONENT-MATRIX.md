# FPV vehicle component matrix

This requirements-level matrix coordinates `MM-DRN-001`, `MM-TOY-002`,
`MM-TOY-003` and `MM-ROV-001`. It identifies a shared operator ecosystem without
claiming that vehicle-rated power, control or pressure components are
interchangeable.

| Capability | OpenQuad CF5 | TrailCam CF10 | TrailCam B2 Balance | Tethys Mini ROV | Reuse decision |
|---|---|---|---|---|---|
| Operator firmware/ecosystem | EdgeTX + ExpressLRS 2.4 GHz LBT | EdgeTX + ExpressLRS 2.4 GHz LBT | EdgeTX + ExpressLRS 2.4 GHz LBT candidate | Direct tether first; ELRS only on optional surface buoy | Shared protocol knowledge and configuration practice |
| Vehicle receiver | RadioMaster RP1 V2, serial CRSF | RadioMaster ER5C PWM candidate | Surface PWM or serial receiver feeding a separate balance controller | Ethernet to Pi/Pico; optional buoy receiver | Platform-specific electrical interface |
| Transmitter ergonomics | RadioMaster Pocket M2, twin-stick | RadioMaster MT12 ELRS recommended, steering wheel/trigger | MT12 or Pocket; controller consumes bounded speed/yaw commands | Laptop/gamepad; optional buoy may accept ELRS | Same RF family where useful, not one mandatory controller |
| Camera | RunCam Phoenix 2 SE V2 analog | RunCam Phoenix 2 SE V2 analog | RunCam Phoenix 2 SE V2 family candidate | Raspberry Pi Camera Module 3 Wide | Exact reuse for air/ground only after measured revision freeze |
| Video transport | SpeedyBee TX800 5.8 GHz analog | SpeedyBee TX800 5.8 GHz analog | SpeedyBee TX800 family candidate | Ethernet tether; optional Wi-Fi above water | Exact reuse for air/ground only; no submerged 5.8 GHz |
| Video receiver | 5.8 GHz analog goggles/display | Same goggles/display family | Same goggles/display family | Laptop/topside station | Workshop reuse for air/ground |
| Power | 4S flight LiPo and 4-in-1 flight ESC | 2S crawler battery/ESC plus verified payload BEC | Battery and dual motor driver sized for balance transients; exact voltage unresolved | 3S onboard LiPo, fused distribution and three reversible ESCs | No default battery, ESC or motor-driver interchangeability |
| Primary control | Flight controller owns stabilization and mixing | Receiver/ESC/servo own surface driving | Dedicated real-time controller owns IMU/encoder balance and differential torque | Tethered compute plus thruster control | Firmware and control laws remain platform-specific |
| Antenna rule | Clear of carbon and high-current wiring | Clear of rails, motor and steering wiring | Clear of motor leads, driver switching loops and moving/landing envelopes | RF antennas stay above water | Shared keep-out method, platform-specific placement |
| Bench safety | Smoke stopper, current limit, legal RF settings | Smoke stopper, steering-stall/BEC test, legal RF settings | Restrained rig, deliberate arm, current limit, tip disarm and fault injection | Propeller-off failsafe, leak/vacuum/tether tests | Shared documentation pattern, different gates |

## Interface authority

- Purchased-component authority owns the exact radio, camera, VTX, antenna,
  connector, battery, ESC, pressure-body and thruster envelopes.
- Parametric CAD owns mounts, guards, trays, strain relief and service access.
- Assembly authority owns datums, keep-outs, transforms and cable routing.
- Firmware authority owns channel mapping, mixing and failsafe behavior; printed
  geometry must never be used as evidence that a control system is safe.

## Required exceptions

- OpenQuad uses a serial CRSF receiver and twin-stick flight controls.
- TrailCam uses a surface PWM receiver and should use surface-radio ergonomics.
- TrailCam B2 routes remote commands through a dedicated balance controller;
  receiver output must never drive motor PWM directly.
- Tethys uses the Ethernet tether for submerged control and video. A Wi-Fi or
  ELRS bridge is permitted only on an optional buoy above the waterline.
- Every platform needs its own voltage, current, cooling, connector, legal RF,
  interference and failsafe verification before operation.

Status: requirements draft; component dimensions and exact revisions remain to
be measured before any new production CAD.
