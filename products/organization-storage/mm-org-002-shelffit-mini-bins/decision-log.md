# Decision log — MM-ORG-002 ShelfFit Mini Bins

| ID | Decision | Choice | Rationale / trade-off |
|---|---|---|---|
| D1 | Product selection | `MM-ORG-002`, the first portfolio row with `No CAD` | It is `P0 NOW`, initial-launch SKU 3 and the only audited product without any model artifact. |
| D2 | Autonomy | `autonomous-to-print-candidate`, authorized by Stefan | Permits local requirements, concept, source, mesh and deterministic evidence; physical, appearance, safety and commercial gates remain human. |
| D3 | First revision scope | Open-top, non-stacking, one-piece bin printed twice | Matches the portfolio's low-risk/non-stacking boundary; omits lids, snaps and stack-load claims that would add interfaces and physical evidence. |
| D4 | Fixed reference shelf | 420 × 210 × 150 mm internal; two bins across | Produces 208.5 × 208 × 148 mm bodies that fit a common 220 mm bed and demonstrate the exact-fit calculation. Real shelf measurements remain required. |
| D5 | Clearance | 1 mm at each shelf side, 1 mm between bins, 2 mm total in depth and 2 mm above | Achieves 97.3% nominal volume utilization. It is intentionally provisional because process and shelf tolerance are not yet measured. |
| D6 | Functional geometry | Smooth closed shell, local top perimeter beam, centered semicircular grip | Continuous, cleanable and support-free; avoids many decorative cells or a separate texture panel in the first revision. |
| D7 | Process route | CadQuery, STEP master, STL/3MF manufacturing candidates | Precise envelope and shell dimensions are central; the workspace already has CadQuery, Trimesh, OpenSCAD, Blender and FreeCAD. |
| D8 | Nominal extrusion sections | 1.92 mm wall, 1.8 mm floor, 0.6 mm nozzle, 0.68 mm line, 0.30 mm layer | Targets three continuous wall paths and six floor layers; exact Arachne/toolpath behavior still needs a real slicer profile. |
| D9 | Material | Matte PLA candidate; exact product unresolved | Appropriate for indoor organizer prototyping, but no material/service claim is made without the actual supplier profile and tests. |
| D10 | Optimization | Compare conservative shell, process-only, geometry-only and combined candidates | CAD volume is useful for geometry direction; print-time/material selection is not claimed until exact slicer metrics exist. |
| D11 | Texture and labels | Deferred | A smooth first revision reduces mesh/toolpath and cleaning risk. Fluted panels and labels remain appearance-led derivatives after the fit/load baseline is qualified. |
| D12 | Watermark | Canonical `MM-WM-001-R1`, `MM-ORG-002 · v0.1.0`, recessed 0.4 mm in the underside | Required last solid-geometry change; floor reserve and finished-underside reading direction will be checked digitally, while the process coupon remains human. |
| D13 | Release meaning | DRAFT digital candidate only | A model can exist at `P2` while exact slicing, physical fit/load/cycles, appearance, safety, rights and commercial release remain blocked. |
| D14 | Concept | New concept sheet at `concept/shelffit-mini-bins-v0.1.0-concept.png` | Shows the exact v0.1.0 scope: two identical open-top smooth bins, no lid/stacking/label/texture. Dimensional details remain authoritative only in the specification. |
| D15 | Concept gate | `AUTO_APPROVED` under the project autonomy policy | The image matches the normalized revision with no conflicting feature; production CAD may begin while physical and commercial gates remain human. |
