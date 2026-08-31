# Hybrid design architecture — Permanent one-off Berlin city-map wall relief

- Project ID: `MM-ART-010`
- Claim: `new_design`
- Sources: concept_image, design_description, measurements
- Units: `mm`
- Master envelope: [0, 0, -35] → [600, 400, 6] (600 × 400 × 41 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, proxy, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-PANEL | critical | requested | The unique 600 x 400 mm Berlin artwork shall be manufactured as two permanent 300 x 400 mm main halves with one vertical center seam and no rear grid. | global bounds, Kobra 3 Max bed-fit report, component audit and assembled flatness test |
| REQ-MAP | critical | requested | One immutable OpenStreetMap-derived Berlin master shall own map registration and feature continuity across the single seam; halves shall never be normalized independently. | source manifest, global clipping audit and matched seam-coordinate report |
| REQ-COLOR | important | requested | The visible relief shall use at most four broad Urban Signal color bodies without dithering or a realistic map-color claim. | named-body audit, portable 3MF validation and exact-slicer tool/change/purge report |
| REQ-JOIN | critical | requested | Exactly three concealed loose printed one-way spring/tenon connectors and discrete locating lands shall join the halves without glue, magnets, screws or a replaceable service interface. | interface ownership audit, strain calculation, process-matched coupon and one-time assembly test |
| REQ-MOUNT | critical | inferred | Two upper local hanger parts and two lower local standoffs shall snap into isolated rear sockets and create an 18 mm wall gap without a rear frame. | proxy load-path review, same-process snap coupon, wall-plane gauge and mass-based proof test |
| REQ-LIGHT | critical | requested | The unlit product shall remain complete while reserving optional customer lighting envelopes for an indirect halo and selected true front-through paths. | keep-out collision audit, aperture report, lighting gauge and human lit/unlit appearance review |
| REQ-SCOPE | critical | requested | LEDs, wiring, power supply, controller, diffuser, wall screws and wall anchors are excluded; no electrical-safety or universal wall-load claim shall be made. | BOM, installation boundary and release-package review |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-DECOMP-001 | open | Approve the revision 0.3.0 component, interface, manufacturing and coupon decomposition. | Requirements and concept v02 are approved; the guided autonomy policy assigns decomposition approval to Stefan. | Explicit approval of plan/hybrid-design-plan-v0.3.0.json or requested corrections. | proxy, component, integration, manufacturing, physical, release |
| DEC-CONNECTOR-001 | provisional | Freeze connector spring dimensions, root radius, allowed strain, pocket compensation and one-time retention behavior. | Topology, quantity and 0.15/0.25/0.35/0.45 mm per-side process-coupon series are approved; no physical material/profile result exists. | Material-specific strain calculation followed by same-process coupon inspection for insertion, whitening/cracks, flushness and destructive pull behavior. | integration, manufacturing, physical, release |
| DEC-HANGER-001 | provisional | Freeze the local hanger/standoff snap geometry and installed proof-load acceptance value. | Two upper load points plus two lower plane-setting points are the minimal balanced candidate; no wall substrate or physical snap evidence is available. | Same-process snap coupon, completed-artwork mass, actual wall substrate/hardware and installer-owned proof-test plan. | physical, release |
| DEC-SOURCE-001 | open | Freeze the Berlin OpenStreetMap extraction extent, timestamp, hashes and attribution treatment. | The approved route is an immutable OSM snapshot clipped once in the global artwork frame. | Local source snapshot, extraction manifest, hashes and reviewed ODbL attribution notice. | component, integration, manufacturing, release |
| DEC-APERTURE-001 | provisional | Freeze the final selected light-through path set. | Concept v02 approves sparse luminous paths; final geometry depends on the frozen Berlin vector master and declared keep-outs. | Aperture preview, minimum-width/ligament report and physical light-envelope coupon. | component, integration, manufacturing, physical, release |
| DEC-FILAMENT-001 | provisional | Freeze the four physical Urban Signal filament spools and transition purge matrix. | Palette names are approved; supplier products, batches, measured swatches and opacity are not recorded. | Spool/batch identities, swatches, opacity notes and exact-profile directed transition coupon. | manufacturing, physical, release |
| DEC-WALL-001 | open | Select wall-substrate-specific anchors outside the product package. | The product provides only local hanger geometry; wall substrate and fasteners are customer/installer-specific. | Actual wall substrate, chosen hardware data and installed proof test by the responsible installer. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| MAIN_HALF_SET | parametric | brep | rear datum, outer boundary, center locating lands, connector pockets, standoff sockets, LED lands and minimum-wall authority | [0, 0, 0] → [600, 400, 3] (600 × 400 × 3 mm) | same-family PLA candidate / Bone White base | IF-MAIN-MAP, IF-MAIN-CONNECTOR, IF-MAIN-STANDOFF, IF-MAIN-APERTURE, IF-MAIN-LIGHTING, IF-COUPON-MAIN |
| BERLIN_VECTOR_FIELD | hybrid | mixed | map registration, visible relief, broad semantic colors and cross-seam continuity | [0, 0, 3] → [600, 400, 5] (600 × 400 × 2 mm) | four same-family matte PLA colors / Urban Signal: Bone White, Nardo Grey, Black, Orange | IF-MAIN-MAP |
| SEAM_CONNECTOR_SET | parametric | brep | concealed one-time retention and connector clearance authority | [285, 40, 0.2] → [315, 360, 2.8] (30 × 320 × 2.6 mm) | same-family PLA candidate; exact product pending / concealed single color | IF-MAIN-CONNECTOR, IF-COUPON-CONNECTOR |
| HANGER_STANDOFF_SET | parametric | brep | isolated rear wall interface and 18 mm wall-plane authority without a rear frame | [90, 35, -18] → [510, 365, 0] (420 × 330 × 18 mm) | same-family PLA candidate; exact product pending / concealed single color | IF-MAIN-STANDOFF, IF-STANDOFF-WALL, IF-COUPON-STANDOFF |
| LIGHT_CUTTER_SET | negative/tooling | negative_volume | controlled negative geometry derived from sparse simplified map paths | [0, 0, -0.5] → [600, 400, 5.5] (600 × 400 × 6 mm) | not applicable / negative light path | IF-MAIN-APERTURE |
| LIGHTING_ENVELOPES | negative/tooling | negative_volume | non-product authority for rear strip, adhesive lands, cable routes, bend access and diffuser lands | [8, 8, -17] → [592, 392, -3] (584 × 384 × 14 mm) | customer-supplied lighting excluded / not applicable | IF-MAIN-LIGHTING |
| WALL_HARDWARE_REFERENCE | purchased | cots | planning envelopes for fastener head, shank and installation tool only | [90, 300, -35] → [510, 380, -12] (420 × 80 × 23 mm) | substrate-specific / not applicable | IF-STANDOFF-WALL |
| COUPON_SET | parametric | brep | process-matched selection of pocket compensation, locating-land gap and flexure behavior before full-size source generation | [0, 0, -18] → [180, 120, -5] (180 × 120 × 13 mm) | exact production PLA, nozzle and profile / single process-control color | IF-COUPON-CONNECTOR, IF-COUPON-STANDOFF, IF-COUPON-MAIN |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-MAIN-MAP | MAIN_HALF_SET ↔ BERLIN_VECTOR_FIELD | MAIN_HALF_SET | relief_substrate | 0 mm | 0 mm | 0 mm | 8 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-ATTRIBUTION, KEEP-WATERMARK |
| IF-MAIN-CONNECTOR | MAIN_HALF_SET ↔ SEAM_CONNECTOR_SET | SEAM_CONNECTOR_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-LED, KEEP-CABLE |
| IF-MAIN-STANDOFF | MAIN_HALF_SET ↔ HANGER_STANDOFF_SET | HANGER_STANDOFF_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-STANDOFFS, KEEP-LED, KEEP-CABLE, KEEP-WALLTOOLS |
| IF-MAIN-APERTURE | MAIN_HALF_SET ↔ LIGHT_CUTTER_SET | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-ATTRIBUTION, KEEP-WATERMARK |
| IF-MAIN-LIGHTING | MAIN_HALF_SET ↔ LIGHTING_ENVELOPES | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 12 mm | KEEP-LED, KEEP-CABLE, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-WALLTOOLS |
| IF-STANDOFF-WALL | HANGER_STANDOFF_SET ↔ WALL_HARDWARE_REFERENCE | WALL_HARDWARE_REFERENCE | purchased_mate | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-WALLTOOLS, KEEP-LED, KEEP-CABLE |
| IF-COUPON-CONNECTOR | COUPON_SET ↔ SEAM_CONNECTOR_SET | SEAM_CONNECTOR_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm |  |
| IF-COUPON-STANDOFF | COUPON_SET ↔ HANGER_STANDOFF_SET | HANGER_STANDOFF_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm |  |
| IF-COUPON-MAIN | COUPON_SET ↔ MAIN_HALF_SET | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 12 mm |  |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-SEAM` (mesh): 12 mm protected center band around locating lands and visible cross-seam features.
- `KEEP-CONNECTORS` (mesh): protected volumes around three connector pockets, spring sweeps and insertion paths.
- `KEEP-STANDOFFS` (mesh): protected volumes around two upper hanger and two lower standoff sockets and flexure sweeps.
- `KEEP-LED` (mesh): 12 x 4 mm rear strip envelope and local front-light approach volumes inside the 18 mm cavity.
- `KEEP-CABLE` (mesh): 6 x 4 mm minimum cable paths, bend access and left/right/bottom exits.
- `KEEP-WALLTOOLS` (mesh): wall-fastener head, shank, driver and installation approach volumes.
- `KEEP-ATTRIBUTION` (aabb): protected rear OpenStreetMap attribution zone. [8, 8, 0] → [220, 30, 3]
- `KEEP-WATERMARK` (aabb): candidate protected rear watermark host; final placement remains a later approval gate. [380, 8, 0] → [592, 30, 3]

## Assembly sequence

1. Print the off-product connector and standoff coupon with the exact production printer, nozzle, material, orientation and profile.
2. Select and record the passing pocket compensation and flexure candidate; regenerate all mating bodies from the shared interface kit.
3. Insert the three selected one-way connectors into the left main half, align both halves on a flat fixture and press the right half home once.
4. Snap two upper hanger parts and two lower standoffs into the isolated rear sockets and verify the 18 mm wall plane.
5. Optionally add customer lighting only inside the declared rear adhesive lands, strip keep-outs and cable routes.
6. Install the completed one-piece artwork with substrate-appropriate customer-selected wall hardware and perform the declared proof test.

## Validation gates

- `architecture` / `VAL-ARCH` — plan_hybrid_design.py plus manual linked-tree and interface-owner review Acceptance: all critical requirements allocated, no grid/magnet/glue/service interface present, every interface has one owner and the assembly sequence is feasible
- `proxy` / `VAL-PROXY` — assemble two half, connector, standoff, lighting and wall-hardware proxies in the global frame Acceptance: 600 x 400 mm assembly, each main half fits 420 x 420 mm, 18 mm wall plane is defined and no functional keep-out collision exists
- `component` / `VAL-COMP` — source manifests, parametric assertions, vector simplification audit and named-body inventory Acceptance: one immutable Berlin frame, exactly two main halves, three connectors, four standoff parts and eight aligned color bodies with printable features
- `integration` / `VAL-INT` — strain calculations, two-axis sections, gap/overlap/ligament checks, motion sweeps and process-matched coupon Acceptance: coupon-selected compensation, no damaged flexures, flush single seam, protected lighting paths and no hidden islands
- `manufacturing` / `VAL-MFG` — mesh/3MF audits and exact Anycubic Slicer Next runs with complete machine/process/filament profiles Acceptance: expected bodies/tools, maximum four colors, no auto-arrangement, no first-layer island, all intended apertures survive and budgets pass
- `physical` / `VAL-PHY` — coupon, representative seam, wall-plane/light gauge and completed-artwork proof/appearance tests Acceptance: one-time assembly passes without crack/whitening, artwork remains flat and aligned, wall interface passes installer-owned proof test and lit/unlit appearance is approved

## Plan diagnostics

No errors or warnings.
