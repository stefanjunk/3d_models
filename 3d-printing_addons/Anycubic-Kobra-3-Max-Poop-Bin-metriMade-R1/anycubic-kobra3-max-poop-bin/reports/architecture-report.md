# Hybrid design architecture — Original removable purge-waste bin for Anycubic Kobra 3 Max

- Project ID: `ANYCUBIC-K3MAX-POOP-BIN-R1`
- Claim: `new_design`
- Sources: design_description, measurements
- Units: `mm`
- Master envelope: [-84, -59, 0] → [84, 59, 152] (168 × 118 × 152 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: physical, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-001 | critical | requested | Catch purge waste without entering the printer motion envelope. | physical full-travel and three-cycle purge test |
| REQ-002 | critical | requested | Use an original design and no third-party model geometry. | provenance and package audit |
| REQ-003 | important | requested | Remain support-free with 0.4 mm nozzle PETG defaults. | slicer preview and prototype |
| REQ-004 | important | requested | Carry metriMade branding and literal metrimade.com text with up to four logo colors. | 3MF material/solid audit and appearance review |
| REQ-005 | critical | inferred | Unknown machine hole spacing shall be isolated from the large print through a low-cost fit gauge and adjustable bracket. | gauge fit and measured hole spacing |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-001 | open | Machine screw spacing and local keep-out | Official guide confirms screws and positioning holes but gives no spacing. | Printed gauge fit and physical measurement. | physical, release |
| DEC-002 | provisional | Replacement screw length | Official bundle lists M3x7; a 3.2 mm added plate suggests M3x10 as a starting point. | Verify thread engagement and no bottoming on the printer. | physical, release |
| DEC-003 | resolved | Balanced versus compact body | Balanced provides 1.86 l geometric capacity at about 263 g PETG and fits the official build area. | Slicer time/material comparison remains useful but does not change the selected geometry. |  |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| BIN | parametric | mesh | capture, store and permit clean removal of purge waste | [-84, -59, 0] → [84, 59, 152] (168 × 118 × 152 mm) | PETG / navy or user choice | IF-BRACKET-BIN, IF-BIN-BADGE |
| BRACKET | parametric | mesh | carry the removable bin from the purge-wiper sheet metal | [-34, 0, 0] → [34, 42, 14] (68 × 42 × 14 mm) | PETG / teal or body color | IF-HARDWARE-BRACKET, IF-BRACKET-BIN |
| GAUGE | parametric | mesh | low-material physical calibration before bracket production | [-34, -8, 0] → [34, 8, 1.2] (68 × 16 × 1.2 mm) | PETG / aqua or scrap color | IF-HARDWARE-BRACKET |
| BADGE | parametric | mesh | brand identity without weakening the catch wall | [-50, -22, 0] → [50, 22, 2] (100 × 44 × 2 mm) | same-family PETG or PLA / sand/navy/teal/aqua | IF-BIN-BADGE |
| HARDWARE | purchased | cots | purchased mounting hardware | [-3, -10, 0] → [3, 10, 10] (6 × 20 × 10 mm) | steel / hardware | IF-HARDWARE-BRACKET |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-HARDWARE-BRACKET | HARDWARE ↔ BRACKET | BRACKET | fastener | 0.5 mm | 0 mm | 0 mm | 0 mm | KEEP-MACHINE |
| IF-BRACKET-BIN | BRACKET ↔ BIN | BIN | keyed_insert | 0.6 mm | 0 mm | 0 mm | 3 mm | KEEP-PURGE-STREAM, KEEP-MACHINE |
| IF-BIN-BADGE | BIN ↔ BADGE | BIN | adhesive_backer | 0 mm | 0.2 mm | 0 mm | 2 mm | KEEP-MACHINE |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-MACHINE` (aabb): conservative planning proxy for toolhead, bed, cable, wiper and sheet-metal motion; replace through physical check. [-120, -90, 0] → [120, 90, 200]
- `KEEP-PURGE-STREAM` (aabb): planning proxy for fall path from purge chute into bin opening. [-30, 40, 110] → [30, 80, 190]

## Assembly sequence

1. Print and verify the machine-side fit gauge.
2. Print and install the bracket with verified M3 hardware.
3. Print the bin upright and engage both rim hooks.
4. Print one or two four-color badges and bond them to clean side faces.
5. Run full-motion and supervised purge tests before unattended use.

## Validation gates

- `architecture` / `VAL-ARCH` — validate hybrid plan and trace requirements to components and interfaces Acceptance: no unresolved references and one declared interface owner
- `proxy` / `VAL-PROXY` — review parameter envelopes and machine-side fit-gauge coverage Acceptance: all components remain independently replaceable and uncertainty is isolated in the gauge/bracket
- `component` / `VAL-COMP` — deterministic STL edge/topology/volume audit Acceptance: all solids closed, positive volume, no boundary/non-manifold/degenerate/duplicate faces
- `integration` / `VAL-INT` — validate hook spacing, continuous rim, M3 slot and common badge coordinate frame Acceptance: declared digital interfaces pass; physical machine-fit stays visible
- `manufacturing` / `VAL-3MF` — validate package XML, object/material references and triangle indices Acceptance: all structural checks pass and four badge materials exist
- `manufacturing` / `VAL-SLICE` — Anycubic Slicer Next preview and G-code analysis Acceptance: correct walls, no unsupported toolpaths, correct colors, safe purge estimate
- `physical` / `VAL-PHYSICAL` — fit gauge, full travel, retention and three supervised purge cycles Acceptance: all checklist items pass without interference or loosening

## Plan diagnostics

No errors or warnings.
