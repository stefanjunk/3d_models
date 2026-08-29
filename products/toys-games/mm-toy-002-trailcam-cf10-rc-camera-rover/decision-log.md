# Decision log — MM-TOY-002

## 2026-08-29 — Product identity and migration

- Assigned product ID `MM-TOY-002` and portfolio record `PORT-096`.
- Created `products/toys-games/mm-toy-002-trailcam-cf10-rc-camera-rover/`.
- Moved the unchanged legacy PDF into `docs/legacy/`.
- Did not move `products/toys-games/bom_budget_de.csv`: its component rows are for the OpenQuad aircraft, not TrailCam.
- Classified the product as `P0 Idea`, because the PDF's claimed generator, parameters, ten STL files, validation outputs, BOM and license are absent.

## 2026-08-29 — Workflow boundary

- Selected the guided project policy. Requirements, concept, decomposition and print-candidate decisions remain human gates.
- Production CAD and manufacturing exports are blocked until revision `0.2.0` requirements and the derived concept are explicitly approved.

## 2026-08-29 — Recommended redesign direction

- Preserve the balanced-hybrid architecture and the separation of RC control from video.
- Replace the upper-deck battery placement with the lowest approved COTS chassis battery position.
- Replace a primary bodypost load path with a measured frame/hardpoint adapter; bodyposts may remain locators for light covers.
- Add a replaceable camera guard, strain relief, protected cable routes and explicit motion keep-outs.
- Rebuild precise geometry in CadQuery so functional interfaces also have STEP outputs.
- Treat the report's 42.2% CAD-volume saving as an unreproducible historical observation until an exact baseline and slicer profile exist.
