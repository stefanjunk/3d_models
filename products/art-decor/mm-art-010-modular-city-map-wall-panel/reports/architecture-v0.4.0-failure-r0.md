# Hybrid design architecture — Berlin wall relief with boundary-crop and context-outline modes

- Project ID: `MM-ART-010`
- Claim: `new_design`
- Sources: concept_image, design_description, measurements
- Units: `mm`
- Master envelope: [0, 0, -35] → [600, 400, 6] (600 × 400 × 41 mm)
- Plan integrity: FAIL (1 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, proxy, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-MODES | critical | requested | Generate one boundary_crop Berlin example whose positive bodies end at the administrative boundary and one context_outline example whose rectangular field includes Umland and marks Berlin. | mode manifest, outer-mask containment report, source-coverage report and matched renders |
| REQ-PANEL | critical | requested | Each one-off example shall use two permanent main prints, one vertical split, no rear grid and no replaceable section; 600 x 400 mm is fixed for context_outline and a maximum envelope for boundary_crop. | global bounds, positive-body count, Kobra bed-fit and assembly audit |
| REQ-MAP | critical | requested | Every mode shall use one immutable geospatial frame and split only after global scaling, semantic mapping, outer masking and protected-interface registration. | source manifest, transform record and cross-seam coordinate report |
| REQ-SOURCE | critical | requested | context_outline shall fail closed unless a new immutable Berlin/Brandenburg source covers the selected 12 percent default margin on every side. | projected source bounds contain selected context bounds for every required semantic layer |
| REQ-COLOR | important | requested | Each mode shall use at most four broad Urban Signal filament bodies without dithering; context_outline shall use Orange for the robust Berlin boundary relief. | named-body audit, minimum-feature audit, target-slicer tool routing and purge review |
| REQ-JOIN | critical | requested | Three concealed loose one-way printed connectors shall permanently join each pair of halves without glue, magnets, screws or a service interface. | mode-specific safe-land placement, interface sections, existing coupon series and physical one-time assembly test |
| REQ-MOUNT | critical | inferred | Two upper local hangers and two lower local standoffs shall lie inside each mode's retained safe body and establish the 18 mm wall plane without a rear frame. | eroded-mask containment, socket ligament report, wall-plane gauge and installed proof test |
| REQ-LIGHT | critical | requested | Both modes shall reserve optional customer-added rear halo lighting and protected true front-through paths while remaining complete when unlit. | mode-specific route/keep-out audit, aperture report, passive gauge and human lit/unlit review |
| REQ-SCOPE | critical | requested | LEDs, wiring, controller, power supply, diffuser, wall screws and wall anchors remain excluded; no electrical or universal wall-load claim is made. | BOM, installation boundary and release-package review |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-DECOMP-040 | open | Approve the revision 0.4.0 mode-aware component, source, interface, color and validation decomposition. | Requirements and concept v03 are human-approved; the guided policy keeps decomposition human-controlled. | Explicit approval of plan/hybrid-design-plan-v0.4.0.json or requested corrections. | proxy, component, integration, manufacturing, physical, release |
| DEC-SOURCE-040 | open | Freeze the expanded context_outline Berlin/Brandenburg source and derived layers. | The Berlin-only 0.3.0 PBF does not cover the approved 12 percent context margin. | Immutable transport source, hashes, projected bounds, extraction commands, layer counts and attribution notice. | component, integration, manufacturing, release |
| DEC-PLACEMENT-040 | provisional | Freeze mode-specific connector, hanger, standoff and LED-route placements. | Revision 0.3.0 interface shapes remain the shared authority, but their old placements cannot be assumed inside the irregular silhouette. | Inward-offset safe-region solve, ligament sections, symmetry/load-path review and collision-free proxy for both modes. | component, integration, manufacturing, physical, release |
| DEC-PERIMETER-040 | provisional | Freeze boundary_crop perimeter simplification and weak-peninsula policy. | The administrative boundary is appearance-authoritative, while sub-print notches and narrow necks can be mechanically fragile. | Physical-scale deviation report, minimum retained neck/edge-ligament audit and matched outline preview. | component, integration, manufacturing, release |
| DEC-APERTURE-040 | provisional | Freeze mode-specific light-through path sets and rear halo routes. | Both modes retain light preparation, but perimeter and interface keep-outs differ. | Aperture width/open-area/ligament reports, rear-route coverage and physical light gauge. | integration, manufacturing, physical, release |
| DEC-FILAMENT-040 | provisional | Freeze the four physical Urban Signal spools and directed transition purge matrix. | Semantic colors are approved; exact products, batches, measured swatches and opacity remain unrecorded. | Spool/batch records, swatches, opacity notes and exact-profile transition coupon. | manufacturing, physical, release |
| DEC-WALL-040 | open | Select wall-substrate-specific hardware outside the product package. | Wall substrate and anchors remain installer-specific. | Actual substrate, chosen hardware data and installer-owned proof test. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| MODE_OUTER_MASK_SET | parametric | mixed | owns display_mode enum, maximum frame, boundary silhouette, context rectangle, projected bounds and all derived clip bodies | [0, 0, 0] → [600, 400, 4.6] (600 × 400 × 4.6 mm) | not applicable / not applicable | IF-MASK-MAIN, IF-SOURCE-MASK |
| MAP_SOURCE_SET | hybrid | mixed | owns transport files, provenance, working-CRS derived layers and coverage evidence | invalid | not applicable / semantic source only | IF-SOURCE-MASK, IF-MAIN-MAP |
| MAIN_HALF_SET | parametric | mixed | rear datum, retained perimeter, structural base, derived sockets, local lands and split authority | [0, 0, 0] → [600, 400, 3] (600 × 400 × 3 mm) | same-family PLA candidate / Bone White base plus aligned top bands | IF-MASK-MAIN, IF-MAIN-MAP, IF-MAIN-INTERFACE, IF-MAIN-APERTURE, IF-MAIN-LIGHTING |
| MULTICOLOR_RELIEF_SET | hybrid | mesh | owns printable Bone White, Nardo Grey, Black and Orange relief regions in the selected global mode frame | [0, 0, 0] → [600, 400, 4.6] (600 × 400 × 4.6 mm) | four same-family matte PLA colors / Urban Signal | IF-MAIN-MAP |
| MODE_INTERFACE_SKELETON | parametric | brep | single owner for seam, connector, hanger, standoff and lighting-land placements constrained to retained safe regions | [0, 0, -18] → [600, 400, 3] (600 × 400 × 21 mm) | not applicable / concealed | IF-MAIN-INTERFACE, IF-SKELETON-CONNECTOR, IF-SKELETON-STANDOFF |
| SEAM_CONNECTOR_SET | parametric | brep | owns connector section, flexure dimensions and derived pocket-clearance bodies | [285, 35, 0.2] → [315, 365, 2.8] (30 × 330 × 2.6 mm) | same-family PLA candidate / concealed single color | IF-SKELETON-CONNECTOR, IF-COUPON-CONNECTOR |
| HANGER_STANDOFF_SET | parametric | brep | owns the isolated snap geometry and 18 mm wall-plane counterpart | [0, 0, -18] → [600, 400, 0] (600 × 400 × 18 mm) | same-family PLA candidate / concealed single color | IF-SKELETON-STANDOFF, IF-STANDOFF-WALL, IF-COUPON-STANDOFF |
| LIGHT_CUTTER_SET | negative/tooling | negative_volume | owns selected negative paths after perimeter and interface keep-outs | [0, 0, -0.5] → [600, 400, 5.5] (600 × 400 × 6 mm) | not applicable / negative light path | IF-MAIN-APERTURE |
| LIGHTING_ENVELOPES | negative/tooling | negative_volume | non-product authority for strip space, adhesive lands, cable routes, exits and ventilation | [0, 0, -17] → [600, 400, -3] (600 × 400 × 14 mm) | not applicable / not applicable | IF-MAIN-LIGHTING |
| WALL_HARDWARE_REFERENCE | purchased | cots | planning envelopes for excluded wall fasteners and tools | [0, 0, -35] → [600, 400, -12] (600 × 400 × 23 mm) | substrate-specific / not applicable | IF-STANDOFF-WALL |
| COUPON_SET | parametric | brep | selects process compensation and flexure behavior shared by both display modes | [0, 0, -18] → [184, 118, 3] (184 × 118 × 21 mm) | exact production PLA/nozzle/profile / single process-control color | IF-COUPON-CONNECTOR, IF-COUPON-STANDOFF |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-MASK-MAIN | MODE_OUTER_MASK_SET ↔ MAIN_HALF_SET | MODE_OUTER_MASK_SET | relief_substrate | 0 mm | 0 mm | 0 mm | 8 mm | KEEP-PERIMETER, KEEP-SEAM, KEEP-ATTRIBUTION, KEEP-WATERMARK |
| IF-SOURCE-MASK | MAP_SOURCE_SET ↔ MODE_OUTER_MASK_SET | MODE_OUTER_MASK_SET | other | 0 mm | 0 mm | 0 mm | 0 mm |  |
| IF-MAIN-MAP | MAIN_HALF_SET ↔ MULTICOLOR_RELIEF_SET | MAIN_HALF_SET | relief_substrate | 0 mm | 0 mm | 0 mm | 8 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-ATTRIBUTION, KEEP-WATERMARK |
| IF-MAIN-INTERFACE | MAIN_HALF_SET ↔ MODE_INTERFACE_SKELETON | MODE_INTERFACE_SKELETON | other | 0 mm | 0 mm | 0 mm | 16 mm | KEEP-PERIMETER, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-LED, KEEP-CABLE |
| IF-SKELETON-CONNECTOR | MODE_INTERFACE_SKELETON ↔ SEAM_CONNECTOR_SET | SEAM_CONNECTOR_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 16 mm | KEEP-SEAM, KEEP-CONNECTORS, KEEP-LED, KEEP-CABLE |
| IF-SKELETON-STANDOFF | MODE_INTERFACE_SKELETON ↔ HANGER_STANDOFF_SET | HANGER_STANDOFF_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 16 mm | KEEP-PERIMETER, KEEP-STANDOFFS, KEEP-LED, KEEP-CABLE, KEEP-WALLTOOLS |
| IF-MAIN-APERTURE | MAIN_HALF_SET ↔ LIGHT_CUTTER_SET | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 16 mm | KEEP-PERIMETER, KEEP-SEAM, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-ATTRIBUTION, KEEP-WATERMARK |
| IF-MAIN-LIGHTING | MAIN_HALF_SET ↔ LIGHTING_ENVELOPES | MAIN_HALF_SET | other | 0 mm | 0 mm | 0 mm | 16 mm | KEEP-PERIMETER, KEEP-LED, KEEP-CABLE, KEEP-CONNECTORS, KEEP-STANDOFFS, KEEP-WALLTOOLS |
| IF-STANDOFF-WALL | HANGER_STANDOFF_SET ↔ WALL_HARDWARE_REFERENCE | WALL_HARDWARE_REFERENCE | purchased_mate | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-WALLTOOLS, KEEP-LED, KEEP-CABLE |
| IF-COUPON-CONNECTOR | COUPON_SET ↔ SEAM_CONNECTOR_SET | SEAM_CONNECTOR_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm |  |
| IF-COUPON-STANDOFF | COUPON_SET ↔ HANGER_STANDOFF_SET | HANGER_STANDOFF_SET | keyed_insert | 0 mm | 0 mm | 0 mm | 12 mm |  |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-PERIMETER` (mesh): mode-specific inward safe-region erosion preserving printable outer edge and local interface ligaments.
- `KEEP-SEAM` (mesh): protected center band around visible split and three connector stations.
- `KEEP-CONNECTORS` (mesh): connector pockets, spring sweeps and insertion paths.
- `KEEP-STANDOFFS` (mesh): two upper and two lower socket/flexure regions per mode.
- `KEEP-LED` (mesh): 12 x 4 mm rear strip envelope and front-light approach volumes.
- `KEEP-CABLE` (mesh): 6 x 4 mm cable routes, bends and left/right/bottom exits.
- `KEEP-WALLTOOLS` (mesh): fastener head, shank, driver and approach volumes.
- `KEEP-ATTRIBUTION` (mesh): mode-specific retained rear OpenStreetMap attribution land.
- `KEEP-WATERMARK` (mesh): candidate mode-specific protected rear watermark host; final placement is later.

## Assembly sequence

1. Select one display_mode and load its immutable outer mask, source extent and interface-placement manifest.
2. Print and qualify the existing process-matched connector/standoff coupon on the exact production process.
3. Regenerate both main halves, rear sockets and cutters from the selected mode skeleton and the recorded winning compensation.
4. Insert three one-way connectors into the left half, align both halves on a flat fixture and press the right half home once.
5. Snap two upper hangers and two lower standoffs into the mode-specific rear sockets and verify the 18 mm wall plane.
6. Optionally add customer lighting only inside declared lands and routes, then install with substrate-appropriate customer-selected hardware.

## Validation gates

- `architecture` / `VAL-ARCH` — plan_hybrid_design.py plus linked-tree and unique-owner review Acceptance: both modes are allocated, every interface has one owner, no rear grid/magnet/glue/service interface exists and assembly remains feasible
- `proxy` / `VAL-SOURCE` — hash and projected-bounds audit for every source and derived semantic layer Acceptance: boundary_crop uses the frozen Berlin boundary and context_outline source bounds contain the approved 12 percent extent on all sides
- `proxy` / `VAL-PROXY` — assemble per-mode mask, two halves, interface kit, lighting and wall proxies Acceptance: each half fits 420 x 420 mm, all rear lands lie inside eroded retained bodies and no keep-out collision exists
- `component` / `VAL-COMP` — source manifests, mask containment, mesh audits and named-body inventory Acceptance: four watertight main composites and 16 aligned watertight color bodies exist; boundary crop has zero positive volume outside Berlin
- `integration` / `VAL-INT` — sections, clearance/ligament checks, motion sweeps and process-matched coupon Acceptance: shared interface shapes are correctly placed in both modes, one seam stays flush and lighting paths avoid all interfaces
- `manufacturing` / `VAL-MFG` — mesh/3MF audits and exact Anycubic Slicer Next runs with complete profiles in new output directories Acceptance: four target-project 3MFs import with geometry, retain four tools, do not auto-arrange, preserve intended paths and stay within budgets
- `physical` / `VAL-PHY` — coupon, representative seam, wall-plane/light gauge and completed-artwork proof/appearance tests Acceptance: one-time assembly passes without damage, artwork remains flat, wall proof passes and lit/unlit appearance is human-approved

## Plan diagnostics

### Errors

- Component MAP_SOURCE_SET: invalid envelope_mm
