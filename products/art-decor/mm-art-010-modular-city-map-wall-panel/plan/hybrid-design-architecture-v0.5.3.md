# Hybrid design architecture — Berlin wall relief with complete water openings and S/U transit accent

- Project ID: `MM-ART-010`
- Claim: `new_design`
- Sources: concept_image, design_description, geospatial_vector
- Units: `mm`
- Master envelope: [0, 0, -18] → [600, 400, 6] (600 × 400 × 24 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: component, integration, manufacturing, physical, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-WATER-053 | critical | requested | Every retained mapped water area and river/canal/stream shall be a through-opening, except for an explicitly logged topology bridge needed to keep printed land connected. | source-to-mask accounting, Tegeler See regression and connected-component audit |
| REQ-COLOR-053 | critical | requested | Oak owns the base, Mint Green the middle relief, Midnight every street class including motorway/trunk, and Sky Blue S-Bahn/U-Bahn plus context boundary and site marker. | four-body ownership audit and exact target-slicer tool report |
| REQ-STRUCT-053 | critical | requested | Each 300 x 400 mm half shall remain one connected printable body and be independently supported at the wall; no rear grid or blanket rib network is allowed. | candidate comparison, topology audit, placement audit and physical handling/proof test |
| REQ-SCOPE-053 | critical | requested | Lighting remains an optional unsupplied add-on and the digital phase shall not upload or start a print. | BOM, keep-out and release review |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-DECOMP-053 | resolved | Approve water, transit, topology-bridge and four-color ownership. | The user approved concept v07 and the targeted bridge strategy before asking the design work to continue. | Retain the approval trace in design-spec.yaml and decomposition-review-0.5.3.md. |  |
| DEC-SOURCE-053 | provisional | Freeze same-date Berlin and Brandenburg extracts and bounded semantic derivatives. | Official 2026-08-30 Berlin and Brandenburg PBFs were reacquired; derivative extraction and coverage evidence are pending. | Record transport hashes, derived-layer hashes, projected coverage, counts and Tegeler See relation 451908. | component, integration, manufacturing, physical, release |
| DEC-STIFFNESS-053 | provisional | Select the least-material viable aperture reinforcement candidate. | Candidate B uses only mandatory 2.0 mm full-thickness topology bridges. Local rear ribs are conditional and currently disfavored because they conflict with rear-datum-down printing and halo lands. | Compare openings-only, topology-bridged and conditional local-rib candidates; then perform a physical handling and installed proof test. | physical, release |
| DEC-PROCESS-053 | provisional | Qualify final connector clearance, opacity, purge and wall-load behavior. | Prior digital geometry and exact Anycubic slicing exist, but no exact four-spool physical coupon or wall proof test exists. | Process-matched connector/light/color coupons and mass-based installed proof test. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| SOURCE_SET_053 | hybrid | mixed | owns immutable boundary, roads, water areas, water lines and S/U route relations | [0, 0, 0] → [600, 400, 0.01] (600 × 400 × 0.01 mm) | not applicable / semantic source | IF-SOURCE-RELIEF, IF-SOURCE-WATER |
| MAIN_RELIEF_SET_053 | parametric | mesh | owns backer, outer masks, seam split, sockets, four positive color bodies and print datum | [0, 0, 0] → [600, 400, 5.2] (600 × 400 × 5.2 mm) | PLA family / Oak, Mint Green, Midnight, Sky Blue | IF-SOURCE-RELIEF, IF-WATER-BACKER |
| WATER_APERTURE_TOOL_053 | negative/tooling | negative_volume | owns through-part negative water geometry, protected keep-outs and the minimum bridge set needed to prevent detached land | [0, 0, 0] → [600, 400, 3.01] (600 × 400 × 3.01 mm) | none; restored bridges inherit Oak base / negative geometry | IF-SOURCE-WATER, IF-WATER-BACKER |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-SOURCE-RELIEF | SOURCE_SET_053 ↔ MAIN_RELIEF_SET_053 | MAIN_RELIEF_SET_053 | relief_substrate | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-SEAM, KEEP-MOUNTS |
| IF-SOURCE-WATER | SOURCE_SET_053 ↔ WATER_APERTURE_TOOL_053 | WATER_APERTURE_TOOL_053 | other | 0 mm | 0 mm | 0 mm | 0 mm | KEEP-SEAM, KEEP-MOUNTS, KEEP-MARKER |
| IF-WATER-BACKER | WATER_APERTURE_TOOL_053 ↔ MAIN_RELIEF_SET_053 | WATER_APERTURE_TOOL_053 | other | 0 mm | 0 mm | 0 mm | 2 mm | KEEP-SEAM, KEEP-MOUNTS, KEEP-MARKER |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-SEAM` (aabb): center seam and connector protection proxy. [292, 0, 0] → [308, 400, 5.2]
- `KEEP-MOUNTS` (aabb): union planning proxy for local hanger and standoff lands; exact bodies remain mode-specific. [12, 12, -18] → [588, 388, 3]
- `KEEP-MARKER` (aabb): parameterized site-marker and attribution protection proxy. [170, 230, 0] → [260, 330, 5.2]

## Assembly sequence

1. Print and qualify the existing connector/interface coupon on the selected process.
2. Print the left and right four-body halves rear datum down.
3. Insert three one-way connectors and press the halves together once on a flat fixture.
4. Install one upper support per half plus lower standoffs; do not use the center seam as the gravity load path.
5. Optionally add customer lighting only inside the declared rear envelope.

## Validation gates

- `architecture` / `VAL-ARCH-053` — validate plan and review unique ownership Acceptance: no plan errors; water, bridge and four-color responsibilities have one owner
- `proxy` / `VAL-PROXY-053` — compare openings-only, topology-bridge and conditional-rib masks Acceptance: select the least-material candidate that leaves one connected backer per half and respects keep-outs
- `component` / `VAL-COMP-053` — source coverage, feature accounting, Tegeler See regression and mesh audit Acceptance: all required layers are non-empty, every water feature is accounted and every exported body is manifold
- `integration` / `VAL-INT-053` — interface, open-area, ligament, body-overlap and seam-continuity reports Acceptance: no unintended collision, no detached land, no tool-4 motorway layer and open area does not exceed 12 percent per half
- `manufacturing` / `VAL-MFG-053` — vendor-aware 3MF checks and exact slice-anycubic-next runs Acceptance: four aligned non-empty tools produce non-empty G-code within resource budgets
- `physical` / `VAL-PHYS-053` — process-matched connector/light coupon, handling test and installed mass-based proof test Acceptance: no crack, detached land, unacceptable flex, disengagement or permanent set; lighting remains optional

## Plan diagnostics

No errors or warnings.
