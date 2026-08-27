# Hybrid design architecture — Premium Parametric Over-Toilet Shelf

- Project ID: `PREMIUM_OVER_TOILET_SHELF_R02`
- Claim: `new_design`
- Sources: concept_image, design_description, measurements
- Units: `mm`
- Master envelope: [-340, -80, 0] → [340, 300, 1650] (680 × 380 × 1650 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-R02-ENVELOPE | critical | requested | The selected default architecture is 680 mm wide, 300 mm deep, and 1650 mm high within the recorded master envelope. | parametric bounds check; site-fit evidence remains open |
| REQ-R02-FRAME | critical | requested | The floor-standing load path uses two 20 mm thick by 240 mm deep side frames, seven printable segments per side locked with M4 hardware, and four PETG feet with replaceable TPU pads. | future source inspection, interface coupons, assembly review, and physical tests |
| REQ-R02-SHELVES | critical | requested | The 620 mm clear shelves have top datums at Z=1050 mm and Z=1400 mm; each shelf is 32 mm high with two 14 x 32 mm edge beams, three tiles, and underside joiners. | future parametric section check plus creep, proof, and cycle tests |
| REQ-R02-MODULES | critical | requested | Modules use a six-column grid; any wider-than-245 mm three-column module is split at its centerline and joined with test-required M3 seam hardware. | revision-bound configuration and drawer swept-volume digital checks pass; exact M3 seam coupon remains pending |
| REQ-R02-WALL | critical | requested | Two rear height-adjustable wall-restraint spacers are required in total, one per side, using adjacent 50 mm frame holes and purchased substrate-specific wall anchors. | site substrate identification, supplier anchor review, installation check, and guarded anti-tip test |
| REQ-R02-DECOR | important | requested | Fascias and the header remain replaceable, and any optional continuous-tone image relief is localized to a replaceable heightmap-controlled insert outside protected functional geometry. | future interface review, relief metadata check, coupon, and exact slicer review |
| REQ-R02-HARDWARE | critical | requested | M4, M5, M3, and wall anchoring hardware are purchased parts; supplier or measured geometry owns purchased mating details. | exact purchased-part identification, measurement, and coupon evidence |
| REQ-R02-EVIDENCE | critical | inferred | Architecture integrity may be checked now, but manufacturing, physical, and release acceptance remain blocked pending the recorded evidence decisions. | decision-log blocker review |
| REQ-R02-LEGACY | important | inferred | Revision 0.1 output evidence is retained as informative legacy evidence and is not current approval evidence for revision 0.2.0. | no revision 0.1 evidence is deleted or promoted by this architecture edit |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-R02-PROCESS | provisional | Confirm the target FDM process and dimensional compensation | Approved PETG, 0.6 mm nozzle, 0.68 mm line width, and 0.30 mm structural layer target on a universal 256 mm class printer. | Exact printer, filament, profile identity, drying state, and process-matched interface coupons. | component, integration, manufacturing, physical, release |
| DEC-R02-WALL-ANCHOR | open | Select and verify substrate-specific wall anchors | The architecture requires two rear restraints, but anchor capacity belongs to the measured wall substrate and purchased anchor system. | Site substrate identification, exact anchor and screw supplier data, installation method, edge-distance review, and guarded pull/anti-tip test. | integration, manufacturing, physical, release |
| DEC-R02-MODULE-SEAM | provisional | Qualify the M3 center seam for wide three-column modules | Modules wider than 245 mm split at center; geometry revision r0.2.0-draft.2 seats each removable 3 mm plate directly on two 6 mm boss tops with zero modeled gap and open coaxial M3 axes. | Exact M3 insert or captive-nut selection, seam geometry, process coupon, tool access, assembly-cycle, and module-load checks. | component, integration, manufacturing, physical, release |
| DEC-R02-SHELF-LOAD | provisional | Verify shelf creep, service load, proof load, and cycle behavior | The selected 32 mm shelf architecture and two 14 x 32 mm edge beams have only preliminary analytical support. | Production-process shelf assembly tests for creep, service deflection, proof load, residual set, seam behavior, and load cycles. | physical, release |
| DEC-R02-SITE-FIT | open | Confirm toilet, service, baseboard, pipe, wall-gap, and floor fit | The default envelope is approved, but each installation requires measured keep-outs and floor contacts. | Measured site envelope, toilet and lid service path, flush controls, pipes, baseboard, wall gap, floor flatness, and installation mockup. | integration, manufacturing, physical, release |
| DEC-R02-EXACT-SLICER | open | Run the exact target slicer review | No revision 0.2.0 manufacturing geometry or exact-profile slicer evidence is approved. | Exact target profile import and toolpath review for bed fit, thin walls, supports, seams, hardware features, and optional relief budget. | manufacturing, release |
| DEC-R02-OPTIMIZATION | open | Complete print-time, material, and manufacturing-mesh optimization evidence | No stable revision 0.2.0 production geometry, exact slicer baseline, comparison, or selected mesh policy exists. | Protected-region baseline, process/geometry comparison, selected or no-change decision, mesh policy, and independent slicer-resolution evidence. | manufacturing, release |
| DEC-R02-WATERMARK | open | Integrate and approve the JuSt Innovation watermark on current production geometry | The specification requires JSI-WM-001-R1 as the last planned solid-geometry feature; no revision 0.2.0 placement or validation evidence exists. | Current-geometry placement, protected-wall review, readable underside preview, manufacturing validation, and explicit final approval. | release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| FRAME | parametric | brep | Primary floor-standing vertical load path, bracket grid, and wall-restraint transfer path | [-330, 0, 0] → [330, 240, 1650] (660 × 240 × 1650 mm) | PETG / structural | IF-SEGMENT-SEAM, IF-FEET-FRAME, IF-BRACKET-FRAME, IF-WALL-RESTRAINT-FRAME |
| FLOOR_FEET | parametric | brep | Transfer side-frame loads to four floor contacts without using the toilet as a load path | [-340, 0, 0] → [340, 300, 16] (680 × 300 × 16 mm) | PETG feet with TPU pads / structural and floor-contact | IF-FEET-FRAME |
| SHELF_SYSTEM | parametric | brep | Provide two 620 mm clear storage planes and carry module loads into brackets | [-310, 0, 1018] → [310, 240, 1400] (620 × 240 × 382 mm) | PETG / structural | IF-SHELF-BRACKET, IF-TILE-SEAM, IF-MODULE-GRID, IF-DRAWER-TRAVEL, IF-DECOR-FASCIA, IF-DECOR-HEADER |
| SHELF_BRACKETS | parametric | brep | Transfer shelf shear and front-edge moment into the side frames | [-330, 0, 1018] → [330, 240, 1400] (660 × 240 × 382 mm) | PETG / structural | IF-BRACKET-FRAME, IF-SHELF-BRACKET |
| MODULES | parametric | brep | Provide removable bins, trays, drawers, open areas, dividers, and hangers | [-310, 0, 1050] → [310, 240, 1650] (620 × 240 × 600 mm) | PETG / module | IF-MODULE-GRID, IF-MODULE-SEAM, IF-DRAWER-TRAVEL |
| DECOR_SKINS | parametric | brep | Carry nonstructural finish, text, and optional localized image-relief presentation | [-310, 0, 1018] → [310, 240, 1650] (620 × 240 × 632 mm) | PETG or nonstructural decorative material allowed by the approved specification / accent | IF-DECOR-FASCIA, IF-DECOR-HEADER, IF-IMAGE-RELIEF |
| IMAGE_RELIEF | hybrid | heightmap | Provide optional image engraving or embossing only on a replaceable decorative insert | [-90, 0, 1400] → [90, 240, 1650] (180 × 240 × 250 mm) | nonstructural replaceable PETG or approved decorative material / accent | IF-IMAGE-RELIEF |
| WALL_RESTRAINT | parametric | brep | Bridge the rear wall gap and transfer horizontal anti-tip restraint from each side frame to purchased wall anchors | [-340, -80, 1230] → [340, 0, 1580] (680 × 80 × 350 mm) | PETG spacers / structural | IF-WALL-RESTRAINT-FRAME, IF-WALL-ANCHOR |
| HARDWARE | purchased | cots | Provide serviceable clamping and substrate-specific wall anchoring under supplier or measured authority | [-340, -80, 0] → [340, 300, 1650] (680 × 380 × 1650 mm) | supplier-specified hardware materials / hardware | IF-SEGMENT-SEAM, IF-BRACKET-FRAME, IF-SHELF-BRACKET, IF-TILE-SEAM, IF-MODULE-SEAM, IF-WALL-ANCHOR |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-SEGMENT-SEAM | FRAME ↔ HARDWARE | FRAME | fastener | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-SEGMENT-SEAMS, KEEP-TOOL-ACCESS |
| IF-FEET-FRAME | FLOOR_FEET ↔ FRAME | FLOOR_FEET | keyed_insert | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-FLOOR-CONTACTS, KEEP-BASEBOARD, KEEP-TOOL-ACCESS |
| IF-BRACKET-FRAME | SHELF_BRACKETS ↔ FRAME | FRAME | fastener | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-BRACKET-GRID, KEEP-TOOL-ACCESS |
| IF-SHELF-BRACKET | SHELF_SYSTEM ↔ SHELF_BRACKETS | SHELF_SYSTEM | fastener | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-SHELF-TOP, KEEP-TOOL-ACCESS |
| IF-TILE-SEAM | SHELF_SYSTEM ↔ HARDWARE | SHELF_SYSTEM | fastener | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-TILE-SEAMS, KEEP-SHELF-TOP, KEEP-TOOL-ACCESS |
| IF-MODULE-GRID | SHELF_SYSTEM ↔ MODULES | SHELF_SYSTEM | other | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-MODULE-GRID, KEEP-SHELF-TOP, KEEP-DRAWER-TRAVEL |
| IF-MODULE-SEAM | MODULES ↔ HARDWARE | MODULES | fastener | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-MODULE-SEAMS, KEEP-DRAWER-TRAVEL, KEEP-TOOL-ACCESS |
| IF-DRAWER-TRAVEL | MODULES ↔ SHELF_SYSTEM | MODULES | other | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-DRAWER-TRAVEL, KEEP-MODULE-GRID, KEEP-TOILET-SERVICE |
| IF-DECOR-FASCIA | DECOR_SKINS ↔ SHELF_SYSTEM | SHELF_SYSTEM | keyed_insert | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-DECOR-HEADER, KEEP-SHELF-TOP, KEEP-TOOL-ACCESS |
| IF-DECOR-HEADER | DECOR_SKINS ↔ SHELF_SYSTEM | SHELF_SYSTEM | keyed_insert | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-DECOR-HEADER, KEEP-WALL-RESTRAINT, KEEP-TOOL-ACCESS |
| IF-IMAGE-RELIEF | IMAGE_RELIEF ↔ DECOR_SKINS | DECOR_SKINS | relief_substrate | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-DECOR-HEADER, KEEP-SHELF-TOP, KEEP-TOOL-ACCESS |
| IF-WALL-RESTRAINT-FRAME | WALL_RESTRAINT ↔ FRAME | FRAME | fastener | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-WALL-RESTRAINT, KEEP-TOOL-ACCESS, KEEP-TOILET-SERVICE, KEEP-BASEBOARD |
| IF-WALL-ANCHOR | WALL_RESTRAINT ↔ HARDWARE | HARDWARE | purchased_mate | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-WALL-RESTRAINT, KEEP-TOOL-ACCESS, KEEP-TOILET-SERVICE, KEEP-BASEBOARD |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-SEGMENT-SEAMS` (aabb): Reserve every frame segment seam, M4 lock path, registration feature, and seam-adjacent load path from decoration or unrelated geometry.. [-330, 0, 0] → [330, 240, 1650]
- `KEEP-FLOOR-CONTACTS` (aabb): Reserve four PETG foot contacts and replaceable TPU pad faces as uninterrupted floor-bearing regions.. [-340, 0, 0] → [340, 300, 18]
- `KEEP-BRACKET-GRID` (aabb): Protect frame grid holes, bracket bearing faces, and shelf bracket fastener paths.. [-330, 0, 950] → [330, 240, 1400]
- `KEEP-TILE-SEAMS` (aabb): Protect all three-tile shelf seams, underside joiners, M4 hardware, and seam load-transfer regions.. [-310, 0, 1018] → [310, 240, 1400]
- `KEEP-MODULE-GRID` (aabb): Protect the six-column seating grid and module locating surfaces on both shelves.. [-310, 0, 1050] → [310, 240, 1504]
- `KEEP-MODULE-SEAMS` (aabb): Protect center seams, M3 fastener paths, bearing regions, and tool access in qualifying wide three-column modules.. [-310, 0, 1050] → [310, 240, 1154]
- `KEEP-DRAWER-TRAVEL` (swept_volume): Reserve the full configured drawer insertion, operation, and removal path from shelf, decor, seam hardware, toilet, and adjacent-module collision..
- `KEEP-DECOR-HEADER` (aabb): Constrain replaceable fascia, header, and optional localized heightmap work to nonstructural decorative host regions.. [-310, 0, 1018] → [310, 245, 1650]
- `KEEP-WALL-RESTRAINT` (aabb): Protect the two rear spacer locations, adjacent 50 mm frame holes, wall-fastener axes, bearing faces, and installer access.. [-340, -80, 1230] → [340, 20, 1580]
- `KEEP-TOILET-SERVICE` (aabb): Keep the toilet, cistern, lid/service path, flush controls, pipes, and required user access collision-free.. [-280, 0, 0] → [280, 300, 950]
- `KEEP-BASEBOARD` (aabb): Keep frame, feet, wall restraint, tools, and service paths clear of the measured baseboard and rear-wall obstructions.. [-340, -20, 0] → [340, 20, 100]
- `KEEP-TOOL-ACCESS` (aabb): Reserve installation, tightening, inspection, and removal access for M4, M5, M3, and wall hardware.. [-340, -80, 0] → [340, 300, 1650]
- `KEEP-SHELF-TOP` (aabb): Protect both shelf top datums, module seating faces, and cleanable storage surfaces from seams, decoration, and uncontrolled texture.. [-310, 0, 1048] → [310, 240, 1402]

## Assembly sequence

1. Confirm the measured site, wall substrate, purchased hardware, and process-matched coupons before production assembly.
2. Assemble seven M4-locked frame segments per side and engage each side frame with its two PETG feet and TPU floor pads.
3. Install shelf brackets at the selected frame positions for shelf top datums Z=1050 mm and Z=1400 mm.
4. Assemble three tiles and underside joiners for each shelf, then fasten each shelf to its brackets.
5. Install six-column modules; center-split any wider-than-245 mm three-column module and use only coupon-qualified M3 seam hardware.
6. Install the replaceable fascias, header, and optional localized heightmap insert without entering protected geometry.
7. Install one rear wall-restraint spacer per side on adjacent 50 mm holes with substrate-specific purchased wall anchors before loading.
8. Do not treat the assembly as manufacturing-, physical-, load-, or release-accepted until all open blockers are closed.

## Validation gates

- `architecture` / `VAL-R02-ARCHITECTURE` — Run plan_hybrid_design.py against design-plan.json using the supplied acceptance command. Acceptance: Command exits 0 and reports plan integrity PASS with unique IDs, valid references, exact interface ownership, valid transforms, and component envelopes inside the master envelope.
- `proxy` / `VAL-R02-PROXY` — Review the revision-bound CAD assembly preview and build manifest for frame, feet, shelves, brackets, modules, decor, wall restraint, and configured keep-outs; measured site keep-outs remain pending. Acceptance: All selected architecture facts and assembly paths are represented without treating the proxy as engineering evidence.
- `component` / `VAL-R02-COMPONENT` — Run unit, source, STEP/STL topology, body-count, bounds, bed-fit, and hash checks on the revision-bound DRAFT; process-matched coupons and purchased-part qualification remain pending. Acceptance: Each component meets its recorded count, bounds, material authority, interface ownership, and coupon criteria.
- `integration` / `VAL-R02-INTEGRATION` — Run the revision-bound digital integration checks for assembly identity, collision proxies, hardware axes/stacks, seam seating, drawer travel, module stops, floor contacts, header capture, and wall-restraint geometry; measured site fit and exact tool/hardware access remain pending. Acceptance: No unintended collision or protected-region intrusion and all serviceable assembly paths remain accessible.
- `manufacturing` / `VAL-R02-MANUFACTURING` — Run digital mesh and configured bed-fit checks now, then complete exact target slicer, support, thin-wall, 3MF, time/material, mesh-policy, and optimization review on the unchanged DRAFT candidate. Acceptance: All manufacturing blockers are evidenced and closed before any manufacturing acceptance claim.
- `physical` / `VAL-R02-PHYSICAL` — Future process coupons, shelf creep/service/proof/cycle tests, drawer cycle test, floor/site mockup, and substrate-specific guarded anti-tip test; not performed by this edit. Acceptance: All approved physical criteria pass on production-process parts at the measured installation before any load or release claim.

## Plan diagnostics

No errors or warnings.
