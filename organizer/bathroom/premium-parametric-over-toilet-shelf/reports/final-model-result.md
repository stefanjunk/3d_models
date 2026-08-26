# Draft model result — geometry revision r0.2.0-draft.2

The approved revision 0.2.0 over-toilet shelf remains a digitally validated structural DRAFT. Geometry revision `r0.2.0-draft.2` corrects the center-split module seams so all six M3 joiner plates sit directly on their boss tops; manufacturing, physical, load, anti-tip and final-release acceptance are still blocked.

![Revision-bound CAD QA preview](../output/rev-0.2.0-draft/preview/premium_over_toilet_shelf_preview.png)

## Model result

- Floor-standing 680 × 300 × 1650 mm default configuration, with 20 mm rear wall gap and 320 mm installed depth from wall plane to front edge.
- Four load-spreading floor feet with replaceable TPU pads; no load path through the toilet or cistern.
- Two 620 × 240 mm shelf levels with top datums at 1050 and 1400 mm, three tiles per level, continuous edge beams, ribs and bolted underside seam plates.
- Seven printable side-frame segments per side, adjustable shelf brackets and two mandatory height-adjustable rear wall-restraint spacers.
- Six-column removable module system with a center-split drawer housing, drawer and bin. Geometry revision `r0.2.0-draft.2` parameterizes the M3 plate/boss geometry and enforces a 0.0 mm modeled contact gap at all six plate stations.
- Replaceable fascias and header insert keep decoration outside the protected load, fit, seating and service geometry.

## Verification and print readiness

- Requirements and concept gates: approved for specification revision 0.2.0.
- Source tests: 11/11 PASS.
- Architecture/specification checks: PASS with zero schema/plan errors; open release warnings remain explicit.
- Export validation: 42/42 unique printable STEP/STL files PASS watertightness, winding, positive-volume, component-count and configured 256 × 256 × 300 mm bed-fit checks.
- Assembly/integration: PASS for 63 named bodies. All six M3 plates report 0.0 mm boss-contact gap and two open coaxial plate/boss axes per station.
- Mesh burden: 113,692 triangles and 5.425 MiB across unique manufacturing STLs; lossy simplification remains not beneficial for the ordinary CAD meshes.
- Provisional process: PETG, 0.6 mm nozzle, 0.68 mm line width and 0.30 mm structural layers. This is not manufacturing evidence without the exact printer, filament and slicer profile.
- No revision-bound reviewed 3MF or exact toolpath evidence exists. `manufacturing_status` therefore remains `BLOCKED` even though the digital geometry report passes.

## Deliverables

- Editable parametric source: `src/over_toilet_shelf.py`, driven by `parameters.json` and the approved `design-spec.yaml`.
- Revision-bound STEP: `output/rev-0.2.0-draft/step/`.
- Revision-bound STL: `output/rev-0.2.0-draft/stl/`.
- Assembly STEP/STL and preview: `output/rev-0.2.0-draft/preview/`.
- Build manifest and per-part inventory: `output/rev-0.2.0-draft/reports/build_manifest.json` and `print_parts.csv`.
- Geometry/integration evidence: `output/rev-0.2.0-draft/reports/validation_report.json` and `validation_report.md`.
- BOM, printing/assembly instructions, architecture, optimization/mesh review and physical test plan remain in the project root and `reports/`.
- `output/rev-0.2.0-draft/3mf/` is intentionally empty until an exact target-profile slicer project is reviewed.

## Open items and limitations

- Confirm the measured site envelope, toilet/lid/service path, baseboard, pipes, flush control, wall gap, floor flatness and substrate.
- Select the exact printer, PETG product/profile and purchased M3/M4/M5 hardware; select substrate-specific wall anchors.
- Slice every part with the exact profile, archive the reviewed 3MF and check walls, supports, seams, bridge/tool access, flow, time and material.
- Print and qualify the clearance, M3 seam and PETG/TPU floor-interface coupons before full-size parts.
- Complete site-fit, 4 kg/24 h creep, 8 kg/1 h proof, 1000 shelf cycles, 5000 drawer cycles and guarded 100 N anti-tip tests. The 4 kg value remains a test target, not a released rating.
- Complete the optimization/slicer-resolution evidence before selecting a production mesh/process candidate.

## Kennzeichnung

- JuSt Innovation `JSI-WM-001-R1`: not yet integrated or approved; this intentionally remains a final-release blocker.

Next model action: confirm site measurements, printer/material/profile and exact hardware, then create the reviewed 3MF and print the three qualification coupons before committing to the full assembly.
