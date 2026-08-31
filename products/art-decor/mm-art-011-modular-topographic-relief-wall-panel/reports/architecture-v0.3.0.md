# Hybrid design architecture — Permanent one-off Harz and Rhenish topographic wall relief pilots

- Project ID: `MM-ART-011`
- Claim: `new_design`
- Sources: concept_image, design_description, measurements
- Units: `mm`
- Master envelope: [0, 0, -35] → [600, 400, 12] (600 × 400 × 47 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, proxy, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-PANEL | critical | requested | Each unique 600 x 400 mm pilot shall be manufactured as two permanent 300 x 400 mm main halves with one vertical seam and no rear grid. | global bounds, Kobra 3 Max bed-fit report, component audit and assembled flatness test |
| REQ-HEIGHT | critical | requested | Each pilot shall preserve one immutable 16-bit global height master, physical aspect ratio and one elevation-to-model-Z transform; halves shall never be normalized independently. | source manifest, aspect/scale report, center-seam height comparison and 16-bit master hash |
| REQ-PILOTS | critical | requested | The family shall produce separate permanent one-off Harz and Rheinisches Braunkohlerevier pilots from frozen official elevation acquisitions. | pilot-specific source manifests, extents, previews and rebuild jobs |
| REQ-COLOR | important | requested | Each continuous terrain surface shall use four broad abstract altitude colors through exactly three global layer changes, without dithering or realistic land-cover claims. | global threshold report, 3MF validation and exact-slicer tool/change/purge report |
| REQ-JOIN | critical | requested | Exactly three concealed loose printed one-way spring/tenon connectors and discrete locating lands shall join each pilot without glue, magnets, screws or a replaceable service interface. | interface ownership audit, strain calculation, shared process-matched coupon and one-time assembly test per pilot |
| REQ-MOUNT | critical | inferred | Each pilot shall use two upper local hanger parts and two lower local standoffs snapped into isolated rear sockets to create an 18 mm wall gap without a rear frame. | proxy load-path review, same-process snap coupon, wall-plane gauge and mass-based proof test |
| REQ-LIGHT | critical | requested | Each unlit pilot shall remain complete while reserving optional customer lighting envelopes for an indirect halo and selected true front-through terrain paths. | keep-out collision audit, aperture report, lighting gauge and human lit/unlit appearance review |
| REQ-SCOPE | critical | requested | LEDs, wiring, power supply, controller, diffuser, wall hardware and electrical work are excluded; the terrain is decorative and makes no survey, mining-safety, navigation or universal wall-load claim. | BOM, data disclaimer, installation boundary and release-package review |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-DECOMP-001 | open | Approve the revision 0.3.0 component, interface, manufacturing and coupon decomposition for both pilots. | Requirements and concept v02 are approved; the guided autonomy policy assigns decomposition approval to Stefan. | Explicit approval of plan/hybrid-design-plan-v0.3.0.json or requested corrections. | proxy, component, integration, manufacturing, physical, release |
| DEC-CONNECTOR-001 | provisional | Freeze shared connector spring dimensions, root radius, allowed strain, pocket compensation and one-time retention behavior. | Topology, quantity per pilot and 0.15/0.25/0.35/0.45 mm per-side process-coupon series are approved; no physical result exists. | Material-specific strain calculation followed by the shared same-process coupon and a representative seam test. | integration, manufacturing, physical, release |
| DEC-HANGER-001 | provisional | Freeze shared local hanger/standoff snap geometry and pilot-specific installed proof-load acceptance. | Two upper load points plus two lower plane-setting points per pilot are the minimal balanced candidate; no wall substrate or physical snap evidence exists. | Same-process snap coupon, each completed artwork mass, actual wall substrate/hardware and installer-owned proof-test plan. | physical, release |
| DEC-HARZ-DATA-001 | open | Freeze Copernicus GLO-30 source tiles, extent, vertical reference, licence evidence and hashes for Harz. | Copernicus GLO-30 is the approved cross-state official-data route and the target crop contains the Harz massif and Brocken. | Immutable local DEM set, acquisition manifest, CRS/vertical reference, hashes and attribution notice. | component, integration, manufacturing, release |
| DEC-RHENISH-DATA-001 | open | Freeze current GeoBasis NRW DGM1 tiles, extent, acquisition state, licence evidence and hashes for the Rhenish pilot. | Current DGM1 is preferred because open-cast terrain changes materially; the target crop covers Garzweiler, Hambach and Inden. | Immutable local DGM1 set, acquisition state, CRS/vertical reference, hashes and reviewed Data Licence Germany attribution. | component, integration, manufacturing, release |
| DEC-Z-SCALE-001 | provisional | Freeze each pilot's vertical exaggeration and three global color-change heights. | Relief depth is capped at 7 mm; continuous 16-bit geometry and broad global bands are approved, but source distributions are not yet available. | Global elevation distributions, scale/threshold report, relief previews and human appearance review. | integration, manufacturing, physical, release |
| DEC-APERTURE-001 | provisional | Freeze each pilot's selected light-through path set. | Concept v02 approves sparse Harz valley/contour and Rhenish mine-bench/infrastructure paths; final geometry depends on the frozen masters. | Pilot-specific aperture previews, minimum-width/ligament reports and physical light-envelope coupon. | component, integration, manufacturing, physical, release |
| DEC-FILAMENT-001 | provisional | Freeze physical Harz and Rhenish palette spools and transition purge matrices. | Both abstract palettes are approved; supplier products, batches, measured swatches and opacity are not recorded. | Spool/batch identities, swatches, opacity notes and exact-profile directed transition coupon. | manufacturing, physical, release |
| DEC-WALL-001 | open | Select wall-substrate-specific anchors outside each product package. | The products provide local hanger geometry only; wall substrate and fasteners are customer/installer-specific. | Actual wall substrate, chosen hardware data and installed proof test by the responsible installer for each pilot. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| MAIN_HALF_SET | parametric | brep | rear datum, outer boundary, center locating lands, connector pockets, standoff sockets, LED lands and minimum-wall authority for both pilots | [0, 0, 0] → [600, 400, 3] (600 × 400 × 3 mm) | same-family PLA candidate / pilot-specific lowest altitude band | IF-MAIN-HARZ, IF-MAIN-RHENISH, IF-MAIN-CONNECTOR, IF-MAIN-STANDOFF, IF-MAIN-HARZ-APERTURE, IF-MAIN-RHENISH-APERTURE, IF-MAIN-LIGHTING, IF-COUPON-MAIN |
| HARZ_HEIGHTFIELD | hybrid | heightmap | continuous global surface, elevation transform, seam height and abstract altitude-band authority for the Harz pilot | [0, 0, 3] → [600, 400, 10] (600 × 400 × 7 mm) | Dark Green, Chocolate Brown, Caramel and Bone White same-family matte PLA / Harz Moss Stone global altitude bands | IF-MAIN-HARZ |
| RHENISH_HEIGHTFIELD | hybrid | heightmap | continuous global surface, elevation transform, seam height and abstract altitude-band authority for the Rhenish pilot | [0, 0, 3] → [600, 400, 10] (600 × 400 × 7 mm) | Black, Chocolate Brown, Desert Tan and Orange same-family matte PLA / Rhenish Industrial Earth global altitude bands | IF-MAIN-RHENISH |
| SEAM_CONNECTOR_SET | parametric | brep | concealed one-time retention and connector clearance authority shared by both pilots | [285, 40, 0.2] → [315, 360, 2.8] (30 × 320 × 2.6 mm) | one shared exact PLA product/profile pending / concealed single color | IF-MAIN-CONNECTOR, IF-COUPON-CONNECTOR |
| HANGER_STANDOFF_SET | parametric | brep | isolated rear wall interface and 18 mm wall-plane authority without a rear frame | [90, 35, -18] → [510, 365, 0] (420 × 330 × 18 mm) | one shared exact PLA product/profile pending / concealed single color | IF-MAIN-STANDOFF, IF-STANDOFF-WALL, IF-COUPON-STANDOFF |
| HARZ_LIGHT_CUTTERS | negative/tooling | negative_volume | controlled negative geometry derived from sparse simplified valleys or contours | [0, 0, -0.5] → [600, 400, 10.5] (600 × 400 × 11 mm) | not applicable / negative light path | IF-MAIN-HARZ-APERTURE |
| RHENISH_LIGHT_CUTTERS | negative/tooling | negative_volume | controlled negative geometry derived from selected mine benches or infrastructure traces | [0, 0, -0.5] → [600, 400, 10.5] (600 × 400 × 11 mm) | not applicable / negative light path | IF-MAIN-RHENISH-APERTURE |
| LIGHTING_ENVELOPES | negative/tooling | negative_volume | non-product authority for rear strip, adhesive lands, cable routes, bend access and diffuser lands | [8, 8, -17] → [592, 392, -3] (584 × 384 × 14 mm) | customer-supplied lighting excluded / not applicable | IF-MAIN-LIGHTING |
| WALL_HARDWARE_REFERENCE | purchased | cots | planning envelopes for fastener heads, shanks and installation tools only | [90, 300, -35] → [510, 380, -12] (420 × 80 × 23 mm) | substrate-specific / not applicable | IF-STANDOFF-WALL |
| COUPON_SET | parametric | brep | process-matched selection of pocket compensation, locating-land gap and flexure behavior before full-size source generation | [0, 0, -18] → [180, 120, -5] (180 × 120 × 13 mm) | exact production connector/standoff PLA, nozzle and profile / single process-control color | IF-COUPON-CONNECTOR, IF-COUPON-STANDOFF, IF-COUPON-MAIN |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-MAIN-HARZ | MAIN_HALF_SET ↔ HARZ_HEIGHTFIELD | MAIN_HALF_SET | relief_substrate | 0 mm | 0 mm | 0 mm | 8 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-DATA-NOTE, KEEP-WATERMARK |
| IF-MAIN-RHENISH | MAIN_HALF_SET ↔ RHENISH_HEIGHTFIELD | MAIN_HALF_SET | relief_substrate | 0 mm | 0 mm | 0 mm | 8 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-DATA-NOTE, KEEP-WATERMARK |
| IF-MAIN-CONNECTOR | MAIN_HALF_SET ↔ SEAM_CONNECTOR_SET | SEAM_CONNECTOR_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-LED, KEEP-CABLE |
| IF-MAIN-STANDOFF | MAIN_HALF_SET ↔ HANGER_STANDOFF_SET | HANGER_STANDOFF_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-STANDOFFS, KEEP-LED, KEEP-CABLE, KEEP-WALLTOOLS |
| IF-MAIN-HARZ-APERTURE | MAIN_HALF_SET ↔ HARZ_LIGHT_CUTTERS | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-DATA-NOTE, KEEP-WATERMARK |
| IF-MAIN-RHENISH-APERTURE | MAIN_HALF_SET ↔ RHENISH_LIGHT_CUTTERS | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-DATA-NOTE, KEEP-WATERMARK |
| IF-MAIN-LIGHTING | MAIN_HALF_SET ↔ LIGHTING_ENVELOPES | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-LED, KEEP-CABLE, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-WALLTOOLS |
| IF-STANDOFF-WALL | HANGER_STANDOFF_SET ↔ WALL_HARDWARE_REFERENCE | WALL_HARDWARE_REFERENCE | purchased_mate | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-WALLTOOLS, KEEP-LED, KEEP-CABLE |
| IF-COUPON-CONNECTOR | COUPON_SET ↔ SEAM_CONNECTOR_SET | SEAM_CONNECTOR_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm |  |
| IF-COUPON-STANDOFF | COUPON_SET ↔ HANGER_STANDOFF_SET | HANGER_STANDOFF_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm |  |
| IF-COUPON-MAIN | COUPON_SET ↔ MAIN_HALF_SET | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 12 mm |  |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-SEAM` (mesh): 12 mm protected center band around locating lands and continuous terrain samples.
- `KEEP-CONNECTORS` (mesh): protected volumes around three connector pockets, spring sweeps and insertion paths per pilot.
- `KEEP-STANDOFFS` (mesh): protected volumes around two upper hanger and two lower standoff sockets and flexure sweeps per pilot.
- `KEEP-LED` (mesh): 12 x 4 mm rear strip envelope and local front-light approach volumes inside the 18 mm cavity.
- `KEEP-CABLE` (mesh): 6 x 4 mm minimum cable paths, bend access and left/right/bottom exits.
- `KEEP-WALLTOOLS` (mesh): wall-fastener head, shank, driver and installation approach volumes.
- `KEEP-DATA-NOTE` (aabb): protected rear source attribution and decorative-data disclaimer zone. [8, 8, 0] → [260, 30, 3]
- `KEEP-WATERMARK` (aabb): candidate protected rear watermark host; final placement remains a later approval gate. [380, 8, 0] → [592, 30, 3]

## Assembly sequence

1. Freeze and hash the official source acquisition for the selected pilot, create one 16-bit global master and approve its extent/vertical interpretation.
2. Print the shared off-product connector and standoff coupon with the exact production printer, nozzle, material, orientation and profile.
3. Select and record the passing pocket compensation and flexure candidate; regenerate all mating bodies from the shared interface kit.
4. Insert three selected one-way connectors into the left main half, align both halves on a flat fixture and press the right half home once.
5. Snap two upper hanger parts and two lower standoffs into the isolated rear sockets and verify the 18 mm wall plane.
6. Optionally add customer lighting only inside the declared rear lands, strip keep-outs and cable routes, then install with substrate-appropriate wall hardware.

## Validation gates

- `architecture` / `VAL-ARCH` — plan_hybrid_design.py plus manual linked-tree and interface-owner review Acceptance: all critical requirements allocated, no grid/magnet/glue/service interface present, every interface has one owner and each pilot assembly sequence is feasible
- `proxy` / `VAL-PROXY` — assemble two-half, connector, standoff, lighting and wall-hardware proxies in the global frame Acceptance: 600 x 400 mm assembly per pilot, each main half fits 420 x 420 mm, 18 mm wall plane is defined and no functional keep-out collision exists
- `component` / `VAL-COMP` — source manifests, 16-bit master audits, parametric assertions and pilot-specific body inventories Acceptance: two immutable global masters, four total main halves, six connectors, eight standoff parts and continuous seam-locked terrain with three global thresholds per pilot
- `integration` / `VAL-INT` — strain calculations, two-axis sections, gap/ligament checks, seam height comparisons, motion sweeps and shared process-matched coupon Acceptance: coupon-selected compensation, no damaged flexures, flush single seam, continuous terrain, protected lighting paths and no hidden islands
- `manufacturing` / `VAL-MFG` — reference/manufacturing mesh comparison, 3MF audits and exact Anycubic Slicer Next runs with complete profiles Acceptance: mesh budgets pass, no auto-arrangement, exactly three color changes per pilot, no first-layer island, all intended terrain/apertures survive and reports are hash-bound
- `physical` / `VAL-PHY` — shared interface coupon, pilot relief/color coupons, representative seams, wall-plane/light gauge and completed-artwork proof/appearance tests Acceptance: one-time assembly passes without crack/whitening, each artwork remains flat and terrain-continuous, wall interface passes installer-owned proof test and lit/unlit appearance is approved

## Plan diagnostics

No errors or warnings.
