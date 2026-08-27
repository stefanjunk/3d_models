# Decision Log

## DEC-001 — Legacy package status

- Status: proposed for requirements approval in revision 3.0.0.
- Decision: treat the existing v2.0.0 hybrid package and its GLB-derived exports as informative legacy evidence only.
- Basis: no project-level requirements/concept approval record exists, the slicer gate is pending, and physical FIFO, interface and wall-mount tests are unavailable.
- Consequence: do not label existing exports as a current approved release.

## DEC-002 — Representation route

- Status: proposed for requirements approval in revision 3.0.0.
- Decision: prohibit image-to-3D geometry in the production model; use an exact parametric functional core plus deterministic spline/vector wave and kintsugi geometry.
- Basis: the visual identity is describable with sparse curves, while the seven legacy GLBs are non-watertight, normalized and converted through lossy projected relief fields.
- Trade-off: the result will be a controlled interpretation of the concept rather than a vertex-level reproduction of the GLB surfaces.

## DEC-003 — Structural simplification

- Status: approved by Stefan for revision 3.0.0 on 2026-08-21.
- Decision: use three structural modules with at most two roll positions per module instead of six body pieces and five structural interfaces.
- Basis: a two-roll module is approximately 248 mm high using the current 124 mm pitch and remains within the provisional printer envelope.
- Trade-off: larger individual prints, but fewer joints, pins, seams and wall-alignment operations.

## DEC-004 — Decorative system

- Status: approved by Stefan for revision 3.0.0 on 2026-08-21.
- Decision: use shallow procedural side waves, a buffered cubic-spline kintsugi network and material/finish for microtexture. Keep decorative bodies outside all mounting, FIFO and joint keep-outs.
- Basis: this preserves the ivory/wave/gold identity with substantially lower mesh and slicer complexity.

## DEC-005 — Optional scent tray

- Status: approved by Stefan for revision 3.0.0 on 2026-08-21.
- Decision: make the tray removable and optional, limited to dry solid scent stones; exclude flame and direct liquid oils.
- Basis: the tray adds cantilever loading, supports, cleaning and misuse risks without affecting the FIFO function.

## DEC-006 — Workflow gate

- Status: requirements approved by Stefan for revision 3.0.0 on 2026-08-21; concept approval pending.
- Decision: the existing concept image remains visual reference only. A new concept sheet must be bound to the approved revision 3.0.0.
- Consequence: concept-generation work is allowed; production geometry and manufacturing exports remain blocked until explicit concept approval.

## DEC-007 — Requirements approval

- Status: approved by Stefan on 2026-08-21.
- Decision: approve `design-spec.yaml` revision 3.0.0 including the recommended defaults for five-roll capacity, drilled substrate-specific mounting and an optional removable scent tray.
- Consequence: concept Gate 0B is pending for the same specification revision.

## DEC-008 — Concept candidate revision 3.0.0

- Status: approved by Stefan on 2026-08-21.
- Asset: `concept/zen_kintsugi_wave_fifo_r3.0.0_concept.png`.
- Depicted: five-roll top-load/bottom-output FIFO, exactly three structural modules and two seams, one procedural decorative skin per module, sparse gold spline inlays, four distributed rear mounting zones, open crown and optional removable dry-scent tray.
- Presentation boundary: the overview establishes appearance; the adjacent diagrams establish functional allocation. Dimensions, tolerances, wall-anchor capacity and printability remain authoritative only in `design-spec.yaml` and later validation evidence.
- Consequence: production CAD and draft validation exports may proceed. Final release remains blocked by engineering, manufacturing, physical-test and watermark gates.

## DEC-009 — Concept approval

- Status: approved by Stefan on 2026-08-21.
- Decision: approve `concept/zen_kintsugi_wave_fifo_r3.0.0_concept.png` for specification revision 3.0.0.
- Approved visible architecture: five-roll top-load/bottom-output FIFO; three structural modules with two seams; procedural removable skins and gold inlays; four rear mounting zones; open crown; optional removable scent tray.
- Consequence: begin the fully parametric non-image-to-3D production model. The concept image remains non-dimensional; `design-spec.yaml` owns dimensions and acceptance criteria.

## DEC-010 — Production tool route

- Status: selected for the draft production candidate.
- Decision: use CadQuery/OpenCascade for exact functional solids and STEP export; use sparse SciPy/Shapely spline ribbons only to define deterministic decorative profiles before conversion to CadQuery solids.
- Basis: the installed environment provides CadQuery 2.8.0. This route preserves B-Rep interfaces without importing any GLB or dense image-derived mesh.

## DEC-011 — Module joint starting concept

- Status: preliminary; coupon and tool-access verification required.
- Decision: four M5 vertical through-bolts plus shallow coaxial printed alignment bosses per seam, eight bolt sets total.
- Basis: local serviceability and no full-height tolerance accumulation. Alignment bosses are not credited as structural fasteners.
- Rejected starting alternative: two full-height threaded rods, because they complicate servicing and accumulate three-module alignment error.

## DEC-012 — Print-versus-buy

- Status: selected for the draft candidate.
- Decision: print the custom FIFO body, skins, inlays, optional crown/tray and coupons; buy wall anchors, wall screws, M5 seam hardware and M3 skin fasteners/inserts.
- Basis: custom geometry benefits from printing; threads, clamping and substrate-specific anchoring benefit from standard metal hardware.

## DEC-013 — Candidate-01 rigid-gauge collision correction

- Status: implemented as draft geometry `r3.0.0-candidate-02`; digital regression required.
- Finding: the approved 122 x 107 mm rigid roll gauges intersected candidate-01 at the lower output nose and at the lower and upper wall-mount bosses. The bosses extended to Y=8.0 mm while the gauge began at Y=6.4 mm; the nose occupied Y=109.4..116.4 mm while the parked gauge extended to Y=113.4 mm.
- Decision: preserve the approved three-module/four-zone architecture and 8 mm mount-boss depth. Move the shaft 2.0 mm forward by increasing rear clearance to 5.0 mm, increase shaft-clear depth and total depth by the same amount, and start the output nose 0.3 mm beyond the parked gauge front face.
- Envelope check: the revised 123.9 mm body depth remains below the approved 130 mm maximum. No requirement or approved concept feature changes.
- Validation follow-up: reduce the removable-skin assembly standoff from 0.20 to 0.05 mm so the joint-pad-to-proud-inlay base width is 150.0 mm rather than 150.15 mm.
- Consequence: increment the production geometry revision and require zero positive-volume intersection at all five nominal gauge positions before accepting the draft candidate for further validation. Wall-anchor selection, proof testing, nose-removal behavior and the full physical FIFO cycle remain release blockers.

## DEC-014 — Draft manufacturing-mesh policy

- Status: `not-beneficial` for lossy simplification on candidate-02; exact-slicer resolution remains pending.
- Decision: keep exact CadQuery/STEP geometry as authority and manufacture from the directly tessellated DRAFT STL/3MF meshes at 0.10 mm chordal and 0.15 rad angular tolerance. Do not add a decimation step.
- Evidence: all 15 draft STLs are watertight, positive-volume, single-component meshes. The largest is 11,792 triangles / 589,684 bytes; the complete set is 60,150 triangles / 3,008,760 bytes.
- Basis: the meshes are already modest and derive directly from analytic B-Reps; decimation would expose wall mounts, joints, bed planes, inlay boundaries and shallow decorative relief to unnecessary geometric risk.
- Limitation: no exact target-slicer import, layer or toolpath comparison is available, so `slicer_resolution_check` remains pending and release-blocking.

## DEC-015 — Procedural crown envelope

- Status: implemented and digitally checked in candidate-02.
- Finding: the cubic-spline interpolation and 8 mm ribbon buffer extended the optional crown 3.69 mm above its nominal 40 mm semantic height.
- Decision: clip the deterministic crown ribbons to the declared width-by-height profile envelope before B-Rep extrusion. Keep the separate 8 mm assembly tabs below the visible crown datum.
- Consequence: the crown's visible top is bounded by `total_body_height_mm + optional_crown_height_mm`; appearance remains consistent with the approved open-wave crown concept.
