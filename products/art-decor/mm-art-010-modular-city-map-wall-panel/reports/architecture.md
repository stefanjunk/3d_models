# Hybrid design architecture — Modular Berlin city-map wall panel

- Project ID: `MM-ART-010`
- Claim: `new_design`
- Sources: concept_image, design_description, measurements
- Units: `mm`
- Master envelope: [0, 0, -30] → [600, 400, 5.5] (600 × 400 × 35.5 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, proxy, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-MODULES | critical | requested | The 600 x 400 mm artwork shall consist of six individually printable 200 mm-pitch tiles on a segmented rear grid. | global-frame bounds, bed-fit checks, assembled seam report and physical 3 x 2 alignment test |
| REQ-MAP | critical | requested | One immutable Berlin vector master shall own map position and cross-seam feature continuity; tiles shall never be scaled or normalized independently. | source hash, global clipping audit and matched seam-coordinate report |
| REQ-COLOR | important | requested | The artwork shall use no more than four broad explicit color regions in the approved Urban Signal palette without dithering. | named color-body audit, portable 3MF validation and exact-slicer tool/change/purge report |
| REQ-LIGHT | critical | requested | The printed product shall work unlit while reserving an 18 mm halo cavity, generic LED routes and protected true through-openings for customer-added lighting. | keep-out collision checks, aperture geometry report, light gauge and physical illuminated coupon |
| REQ-SERVICE | important | requested | Each art tile shall be replaceable without disturbing the wall-mounted rear grid and shall survive 25 removal/reinstall cycles in the declared test. | interface coupon followed by repeated tile service-cycle test |
| REQ-SCOPE | critical | requested | LEDs, electrical parts and wall anchors are excluded and no structural wall-anchor compatibility or electrical-safety claim shall be made. | BOM, instructions, risk register and release-package review |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-DECOMP-001 | open | Approve this component, interface and manufacturing decomposition. | Concept v01 is approved; the guided autonomy policy assigns decomposition approval to the human owner. | Explicit approval of plan/hybrid-design-plan.json or requested corrections. | proxy, component, integration, manufacturing, physical, release |
| DEC-RETENTION-001 | provisional | Freeze the exact magnetic tile-retention hardware and pocket compensation. | Recommended architecture uses gravity shoulders and three datum pads for load/alignment plus four captive 6 x 2 mm magnets and steel counterparts per tile for normal retention. | Exact magnet/steel part records, pull-off target, same-process pocket coupon and captive-retention test. | integration, physical, release |
| DEC-SOURCE-001 | open | Freeze the Berlin OpenStreetMap extraction extent, timestamp, hashes and attribution treatment. | Official OpenStreetMap data is the approved route, but production source download starts after decomposition approval. | Immutable local vector snapshot, extraction manifest, hashes and reviewed ODbL notice. | component, integration, manufacturing, release |
| DEC-FILAMENT-001 | provisional | Freeze actual Urban Signal filament spools and transition purge matrix. | Retail Anycubic PLA Matte names and display colors are selected; batch identity and measured swatches are not yet available. | Spool/batch identities, physical swatches, opacity notes and exact-profile transition coupon. | manufacturing, physical, release |
| DEC-WALL-001 | open | Select wall-substrate-specific anchors outside the product package. | The printed grid will expose generic mounting slots but cannot determine the customer's wall substrate. | Actual wall substrate, chosen anchor data and installed proof test by the responsible installer. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| REAR_GRID | parametric | brep | global pitch, wall plane, load shoulder, tile datums, retention pockets, lighting routes and cable exits | [0, 0, -18] → [600, 400, 0] (600 × 400 × 18 mm) | PETG candidate / rear grid | IF-GRID-TILE, IF-GRID-LIGHTING, IF-GRID-RETENTION, IF-GRID-WALL |
| ART_TILE_SET | parametric | brep | print-bed face, minimum wall, outer frame, seam boundary and rear interface authority | [0, 0, 0] → [600, 400, 3] (600 × 400 × 3 mm) | Anycubic PLA Matte / Bone White base | IF-GRID-TILE, IF-TILE-MAP, IF-TILE-APERTURES |
| BERLIN_VECTOR_FIELD | hybrid | mixed | appearance, four-color semantics and cross-seam map continuity | [0, 0, 3] → [600, 400, 5] (600 × 400 × 2 mm) | four Anycubic PLA Matte colors / Urban Signal semantic fields | IF-TILE-MAP |
| LIGHT_CUTTER_SET | negative/tooling | negative_volume | controlled negative geometry for front-through illumination | [0, 0, -0.5] → [600, 400, 5.5] (600 × 400 × 6 mm) | not applicable / negative light path | IF-TILE-APERTURES |
| LIGHTING_ENVELOPES | negative/tooling | negative_volume | non-product keep-out authority for halo strip, front-light strip, cable and diffuser | [0, 0, -17] → [600, 400, -3] (600 × 400 × 14 mm) | customer-supplied lighting; printed clips match rear-grid material / not applicable | IF-GRID-LIGHTING |
| TILE_RETENTION_HARDWARE | purchased | cots | normal retention only; gravity shoulders carry tile self-weight | [0, 0, -4] → [600, 400, 1] (600 × 400 × 5 mm) | neodymium magnets plus steel counterparts, exact grade pending / hidden hardware | IF-GRID-RETENTION |
| WALL_HARDWARE_REFERENCE | purchased | cots | generic hole, head and tool-access envelope only; not supplied or rated | [0, 0, -30] → [600, 400, -8] (600 × 400 × 22 mm) | substrate-specific / not applicable | IF-GRID-WALL |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-GRID-TILE | REAR_GRID ↔ ART_TILE_SET | REAR_GRID | other | 0.3 mm | 0 mm | 0 mm | 8 mm | KEEP-SEAMS, KEEP-DATUMS, KEEP-LED-HALO, KEEP-LED-FRONT |
| IF-TILE-MAP | ART_TILE_SET ↔ BERLIN_VECTOR_FIELD | ART_TILE_SET | relief_substrate | 0 mm | 0 mm | 0 mm | 2 mm | KEEP-SEAMS, KEEP-DATUMS, KEEP-ATTRIBUTION |
| IF-TILE-APERTURES | ART_TILE_SET ↔ LIGHT_CUTTER_SET | ART_TILE_SET | other | 0 mm | 0 mm | 0.5 mm | 8 mm | KEEP-SEAMS, KEEP-DATUMS, KEEP-ATTRIBUTION |
| IF-GRID-LIGHTING | REAR_GRID ↔ LIGHTING_ENVELOPES | REAR_GRID | other | 1.4 mm | 0.3 mm | 0 mm | 8 mm | KEEP-DATUMS, KEEP-LED-HALO, KEEP-LED-FRONT, KEEP-WALL-TOOLS |
| IF-GRID-RETENTION | REAR_GRID ↔ TILE_RETENTION_HARDWARE | TILE_RETENTION_HARDWARE | purchased_mate | 0.25 mm | 0.1 mm | 0 mm | 0 mm | KEEP-DATUMS, KEEP-LED-HALO, KEEP-LED-FRONT |
| IF-GRID-WALL | REAR_GRID ↔ WALL_HARDWARE_REFERENCE | WALL_HARDWARE_REFERENCE | purchased_mate | 1.15 mm | 0 mm | 0 mm | 0 mm | KEEP-WALL-TOOLS, KEEP-LED-HALO |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-SEAMS` (mesh): 8 mm protected bands around all internal tile seams; exact cross-shaped body is generated parametrically.
- `KEEP-DATUMS` (mesh): 12 mm protected volumes around tile datums, gravity shoulders, magnet pockets and rear-grid joins.
- `KEEP-LED-HALO` (mesh): 12 x 4 mm perimeter halo-strip and bend-radius envelope inside the 18 mm wall cavity.
- `KEEP-LED-FRONT` (mesh): selected straight 12 x 4 mm strip lands and diffuser access behind light-opening clusters.
- `KEEP-WALL-TOOLS` (mesh): wall-fastener head, driver and installation approach volumes.
- `KEEP-ATTRIBUTION` (aabb): protected lower rear attribution and future watermark zone. [8, 8, 0] → [192, 28, 3]

## Assembly sequence

1. Join and square the six REAR_GRID segments in the global 3 x 2 frame.
2. Install customer-selected wall anchors through the documented generic mounting slots after substrate-specific review.
3. Optionally install customer lighting into the halo and front-light envelopes, route the cable through one selected exit and add diffuser film if desired.
4. Place each ART_TILE_SET member on its gravity shoulder and datum pads; retention hardware supplies only normal holding force.
5. Verify 0.25 mm target seams, cross-seam map continuity, tile retention and unobstructed intended light openings.

## Validation gates

- `architecture` / `VAL-ARCH` — plan_hybrid_design.py plus manual functional/physical/appearance tree review Acceptance: all critical requirements allocated, every interface has one owner and no lighting or map data owns a structural mating surface
- `proxy` / `VAL-PROXY` — assemble six tile, rear-grid, keep-out and hardware-envelope proxies Acceptance: 600 x 400 mm assembly, individual 220 x 220 mm bed fit, feasible install/service sequence and no keep-out collision
- `component` / `VAL-COMP` — source manifests, vector simplification audit and parametric source assertions Acceptance: one global Berlin frame, printable features and all expected tile/color/cutter bodies
- `integration` / `VAL-INT` — exact sections, overlap/gap checks, seam-coordinate comparison and retention/light collision checks Acceptance: all interface dimensions, ligaments, seams and service paths pass
- `manufacturing` / `VAL-MFG` — mesh/3MF audits and exact Anycubic Slicer Next run with complete profiles Acceptance: expected bodies/tools, four-color maximum, intended openings stay open, no first-layer islands and resource budgets pass
- `physical` / `VAL-PHY` — seam/retention coupon, lighting gauge, one representative tile and full 3 x 2 assembly Acceptance: selected fit, 25 service cycles, stable unlit assembly and human-approved lit/unlit appearance

## Plan diagnostics

No errors or warnings.
