# Hybrid design architecture — Modular Harz and Rhenish lignite district topographic relief wall panels

- Project ID: `MM-ART-011`
- Claim: `new_design`
- Sources: concept_image, design_description, measurements
- Units: `mm`
- Master envelope: [0, 0, -30] → [600, 400, 12] (600 × 400 × 42 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, proxy, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-MODULES | critical | requested | Each 600 x 400 mm pilot shall consist of six individually printable 200 mm-pitch tiles on the shared segmented rear-grid family. | global-frame bounds, bed-fit checks, assembled seam report and physical 3 x 2 alignment test |
| REQ-HEIGHT | critical | requested | Each pilot shall preserve one immutable 16-bit global terrain master, physical aspect ratio and seam coordinates; no tile may be independently normalized. | source manifests, aspect report, global scaling report and matched seam-height comparison |
| REQ-PILOTS | critical | requested | The product family shall provide separate Harz and Rheinisches Braunkohlerevier pilots from official terrain sources. | dataset manifests, named pilot rebuild jobs and rendered extent review |
| REQ-COLOR | important | requested | Each relief shall use no more than four broad Z-based color bands in its approved abstract palette without dithering or a realistic land-cover claim. | global layer-change manifest, exact-slicer tool/change report and physical band/purge coupon |
| REQ-LIGHT | critical | requested | The printed product shall work unlit while reserving an 18 mm halo cavity, generic LED routes and protected true through-openings derived from terrain semantics. | keep-out collision checks, aperture geometry report, light gauge and physical illuminated coupon |
| REQ-SERVICE | important | requested | Each terrain tile shall be replaceable without disturbing the wall-mounted rear grid and shall survive 25 removal/reinstall cycles in the declared test. | interface coupon followed by repeated tile service-cycle test |
| REQ-SCOPE | critical | requested | LEDs, electrical parts and wall anchors are excluded and no surveying, mining-safety, structural wall-anchor or electrical-safety claim shall be made. | BOM, instructions, risk register and release-package review |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-DECOMP-001 | open | Approve this component, interface and manufacturing decomposition. | Concept v01 is approved; the guided autonomy policy assigns decomposition approval to the human owner. | Explicit approval of plan/hybrid-design-plan.json or requested corrections. | proxy, component, integration, manufacturing, physical, release |
| DEC-RETENTION-001 | provisional | Freeze the shared magnetic tile-retention hardware and pocket compensation. | Recommended architecture reuses MM-ART-010 gravity shoulders and three datum pads plus four captive 6 x 2 mm magnets and steel counterparts per tile. | Exact magnet/steel part records, pull-off target, same-process pocket coupon and captive-retention test. | integration, physical, release |
| DEC-HARZ-DATA-001 | open | Freeze Copernicus GLO-30 source tiles, extent, vertical datum, licence evidence and hashes for Harz. | Copernicus GLO-30 is the approved official cross-state route; production download starts after decomposition approval. | Immutable local DEM set, product metadata, acquisition/download manifest, CRS/vertical reference, hashes and attribution notice. | component, integration, manufacturing, release |
| DEC-RHENISH-DATA-001 | open | Freeze the current official GeoBasis NRW DGM1 tile set, acquisition state, licence evidence and hashes for the Rhenish pilot. | Current DGM1 is preferred because open-cast mine terrain changes materially over time. | Immutable local DGM1 set, exact extent/acquisition metadata, CRS/vertical reference, hashes and reviewed Data Licence Germany attribution. | component, integration, manufacturing, release |
| DEC-Z-SCALE-001 | provisional | Freeze vertical exaggeration and three global color thresholds for each pilot. | Relief depth is capped at 7 mm; broad global quantiles are recommended as starting thresholds, then adjusted only to preserve a documented major summit or mine-bench break. | Global elevation distributions, relief preview, threshold report, common Z heights across all six tiles and human appearance review. | integration, manufacturing, physical, release |
| DEC-FILAMENT-001 | provisional | Freeze actual Harz and Rhenish palette spools and transition purge matrices. | Retail Anycubic PLA Matte names and display colors are selected; batch identity and measured swatches are not yet available. | Spool/batch identities, physical swatches, opacity notes and exact-profile transition coupon. | manufacturing, physical, release |
| DEC-WALL-001 | open | Select wall-substrate-specific anchors outside the product package. | The printed grid will expose generic mounting slots but cannot determine the customer's wall substrate. | Actual wall substrate, chosen anchor data and installed proof test by the responsible installer. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| REAR_GRID | parametric | brep | global pitch, wall plane, load shoulder, tile datums, retention pockets, lighting routes and cable exits | [0, 0, -18] → [600, 400, 0] (600 × 400 × 18 mm) | PETG candidate / rear grid | IF-GRID-TILE, IF-GRID-LIGHTING, IF-GRID-RETENTION, IF-GRID-WALL |
| TERRAIN_TILE_SET | parametric | brep | print-bed face, minimum wall, outer frame, seam boundary and rear interface authority | [0, 0, 0] → [600, 400, 3] (600 × 400 × 3 mm) | Anycubic PLA Matte / lowest elevation palette color | IF-GRID-TILE, IF-TILE-HARZ, IF-TILE-RHENISH, IF-TILE-HARZ-LIGHT, IF-TILE-RHENISH-LIGHT |
| HARZ_HEIGHTFIELD | hybrid | heightmap | Harz terrain geometry, aspect, global vertical scale and Z-band authority | [0, 0, 3] → [600, 400, 10] (600 × 400 × 7 mm) | Dark Green, Chocolate Brown, Caramel and Bone White PLA Matte / Harz Moss and Stone Z bands | IF-TILE-HARZ |
| RHENISH_HEIGHTFIELD | hybrid | heightmap | current mine-region terrain geometry, aspect, global vertical scale and Z-band authority | [0, 0, 3] → [600, 400, 10] (600 × 400 × 7 mm) | Black, Chocolate Brown, Desert Tan and Orange PLA Matte / Rhenish Industrial Earth Z bands | IF-TILE-RHENISH |
| HARZ_LIGHT_CUTTERS | negative/tooling | negative_volume | controlled negative geometry for front-through illumination | [0, 0, -0.5] → [600, 400, 10.5] (600 × 400 × 11 mm) | not applicable / negative Harz light path | IF-TILE-HARZ-LIGHT |
| RHENISH_LIGHT_CUTTERS | negative/tooling | negative_volume | controlled negative geometry for front-through illumination | [0, 0, -0.5] → [600, 400, 10.5] (600 × 400 × 11 mm) | not applicable / negative Rhenish light path | IF-TILE-RHENISH-LIGHT |
| LIGHTING_ENVELOPES | negative/tooling | negative_volume | non-product keep-out authority for halo strip, front-light strip, cable and diffuser | [0, 0, -17] → [600, 400, -3] (600 × 400 × 14 mm) | customer-supplied lighting; printed clips match rear-grid material / not applicable | IF-GRID-LIGHTING |
| TILE_RETENTION_HARDWARE | purchased | cots | normal retention only; gravity shoulders carry tile self-weight | [0, 0, -4] → [600, 400, 1] (600 × 400 × 5 mm) | neodymium magnets plus steel counterparts, exact grade pending / hidden hardware | IF-GRID-RETENTION |
| WALL_HARDWARE_REFERENCE | purchased | cots | generic hole, head and tool-access envelope only; not supplied or rated | [0, 0, -30] → [600, 400, -8] (600 × 400 × 22 mm) | substrate-specific / not applicable | IF-GRID-WALL |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-GRID-TILE | REAR_GRID ↔ TERRAIN_TILE_SET | REAR_GRID | other | 0.3 mm | 0 mm | 0 mm | 8 mm | KEEP-SEAMS, KEEP-DATUMS, KEEP-LED-HALO, KEEP-LED-FRONT |
| IF-TILE-HARZ | TERRAIN_TILE_SET ↔ HARZ_HEIGHTFIELD | TERRAIN_TILE_SET | relief_substrate | 0 mm | 0 mm | 0.2 mm | 8 mm | KEEP-SEAMS, KEEP-DATUMS, KEEP-ATTRIBUTION |
| IF-TILE-RHENISH | TERRAIN_TILE_SET ↔ RHENISH_HEIGHTFIELD | TERRAIN_TILE_SET | relief_substrate | 0 mm | 0 mm | 0.2 mm | 8 mm | KEEP-SEAMS, KEEP-DATUMS, KEEP-ATTRIBUTION |
| IF-TILE-HARZ-LIGHT | TERRAIN_TILE_SET ↔ HARZ_LIGHT_CUTTERS | TERRAIN_TILE_SET | other | 0 mm | 0 mm | 0.5 mm | 8 mm | KEEP-SEAMS, KEEP-DATUMS, KEEP-ATTRIBUTION |
| IF-TILE-RHENISH-LIGHT | TERRAIN_TILE_SET ↔ RHENISH_LIGHT_CUTTERS | TERRAIN_TILE_SET | other | 0 mm | 0 mm | 0.5 mm | 8 mm | KEEP-SEAMS, KEEP-DATUMS, KEEP-ATTRIBUTION |
| IF-GRID-LIGHTING | REAR_GRID ↔ LIGHTING_ENVELOPES | REAR_GRID | other | 1.4 mm | 0.3 mm | 0 mm | 8 mm | KEEP-DATUMS, KEEP-LED-HALO, KEEP-LED-FRONT, KEEP-WALL-TOOLS |
| IF-GRID-RETENTION | REAR_GRID ↔ TILE_RETENTION_HARDWARE | TILE_RETENTION_HARDWARE | purchased_mate | 0.25 mm | 0.1 mm | 0 mm | 0 mm | KEEP-DATUMS, KEEP-LED-HALO, KEEP-LED-FRONT |
| IF-GRID-WALL | REAR_GRID ↔ WALL_HARDWARE_REFERENCE | WALL_HARDWARE_REFERENCE | purchased_mate | 1.15 mm | 0 mm | 0 mm | 0 mm | KEEP-WALL-TOOLS, KEEP-LED-HALO |

## Organic/image-to-3D jobs

| Component | Mode | Views | Sacrificial band | Landmarks |
|---|---|---|---:|---:|
| HARZ_HEIGHTFIELD | relief_heightmap | source/harz/copernicus-dem-master.tif, build/harz/harz-master-16bit.preview.png | 8 mm | 3 |
| RHENISH_HEIGHTFIELD | relief_heightmap | source/rhenish/geobasis-nrw-dgm1-master.tif, build/rhenish/rhenish-master-16bit.preview.png | 8 mm | 3 |

## Keep-outs

- `KEEP-SEAMS` (mesh): 8 mm protected bands around all internal tile seams; exact cross-shaped body is generated parametrically.
- `KEEP-DATUMS` (mesh): 12 mm protected volumes around tile datums, gravity shoulders, magnet pockets and rear-grid joins.
- `KEEP-LED-HALO` (mesh): 12 x 4 mm perimeter halo-strip and bend-radius envelope inside the 18 mm wall cavity.
- `KEEP-LED-FRONT` (mesh): selected straight 12 x 4 mm strip lands and diffuser access behind light-opening clusters.
- `KEEP-WALL-TOOLS` (mesh): wall-fastener head, driver and installation approach volumes.
- `KEEP-ATTRIBUTION` (aabb): protected lower rear attribution and future watermark zone. [8, 8, 0] → [192, 28, 3]

## Assembly sequence

1. Join and square the six shared-family REAR_GRID segments in the global 3 x 2 frame.
2. Install customer-selected wall anchors through the documented generic mounting slots after substrate-specific review.
3. Optionally install customer lighting into the halo and front-light envelopes, route the cable through one selected exit and add diffuser film if desired.
4. Choose one complete six-tile pilot set and place every TERRAIN_TILE_SET member on its gravity shoulder and datum pads; never mix tile positions or pilot masters.
5. Verify 0.25 mm target seams, terrain continuity, common color-change heights, tile retention and unobstructed intended light openings.

## Validation gates

- `architecture` / `VAL-ARCH` — plan_hybrid_design.py plus manual functional/physical/appearance tree review Acceptance: all critical requirements allocated, every interface has one owner and neither DEM nor lighting data owns a structural mating surface
- `proxy` / `VAL-PROXY` — assemble six tile, rear-grid, keep-out and hardware-envelope proxies for both pilots Acceptance: 600 x 400 mm assembly, individual 220 x 220 mm bed fit, feasible install/service sequence and no keep-out collision
- `component` / `VAL-COMP` — source manifests, relief-job aspect checks, mesh budgets and parametric source assertions Acceptance: one 16-bit global master per pilot, exact aspect and all expected seam-locked bodies
- `integration` / `VAL-INT` — exact sections, overlap/gap checks, seam-height comparison and retention/light collision checks Acceptance: all interface dimensions, walls, ligaments, seams, major terrain breaks and service paths pass
- `manufacturing` / `VAL-MFG` — reference/manufacturing mesh comparison, 3MF audits and exact Anycubic Slicer Next run with complete profiles Acceptance: common pilot Z changes, four-color maximum, intended openings stay open, no missing peaks/benches or first-layer islands and resource budgets pass
- `physical` / `VAL-PHY` — seam/retention coupon, relief/color/light coupon, one representative tile per pilot and full 3 x 2 assembly Acceptance: selected fit, 25 service cycles, stable unlit assembly and human-approved relief, seams, palettes and lighting

## Plan diagnostics

No errors or warnings.
