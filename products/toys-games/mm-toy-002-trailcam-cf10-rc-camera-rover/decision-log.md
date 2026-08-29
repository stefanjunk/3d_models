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
