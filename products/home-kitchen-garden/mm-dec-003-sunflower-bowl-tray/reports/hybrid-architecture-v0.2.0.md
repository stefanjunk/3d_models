# Hybrid design architecture — Sunflower Bowl / Tray v0.2.0

- Project ID: `MM-DEC-003`
- Claim: `step1x_regeneration_with_parametric_foot_only`
- Sources: concept_image, design_description
- Units: `mm`
- Master envelope: [-100, -100, 0] → [100, 100, 65] (200 × 200 × 65 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: physical, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-APPEAR-001 | important | requested | The visible body shall retain the selected soft sunflower petal and central seed-disc character. | top/front/isometric clay review |
| REQ-MFG-001 | critical | requested | The manufacturing derivative shall preserve the registered Step1X flower body and add only the owner-confirmed 80 × 6 mm disc foot as parametric geometry. | registration report, mesh audit and exact-profile slice |
| REQ-TRAY-001 | critical | requested | The central open tray depression shall remain free of generated closures and hidden pockets. | sections, top view and physical dry-item test |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-LEGACY-001 | resolved | Exclude all prior AI meshes and the old 3MF from the new derivative chain. | The files predate the Step1X cleanup and have no auditable run manifest. | New Step1X run at or after f00dd46. |  |
| DEC-PHYSICAL-001 | open | Qualify the final support footprint, petal-edge comfort and loaded tilt stability. | Only digital and nominal evidence exists. | Full prototype printed on the recorded process and measured physical test results. | physical, release |
| DEC-FOOT-001 | resolved | Add the real-print disc foot parametrically without repairing the Step1X body. | Owner instruction plus old Anycubic 3MF metadata establishing a nominal 80 × 6 mm disc. | Foot parameters, Boolean report and protected-region comparison. |  |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| SUNFLOWER_BODY | organic | mesh | visible one-piece flower form and tray massing | [-100, -100, 0] → [100, 100, 65] (200 × 200 × 65 mm) | SUNLU PETG Black digital baseline; final yellow material unresolved / single | IF-BODY-BED-DATUM |
| FOOT_DISC | parametric | brep | owner-confirmed positive foot geometry and final bed placement | [-40, -40, 0] → [40, 40, 6] (80 × 80 × 6 mm) | same PETG as the body / single | IF-BODY-BED-DATUM |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-BODY-BED-DATUM | SUNFLOWER_BODY ↔ FOOT_DISC | FOOT_DISC | other | 0 mm | 0 mm | 5.9 mm | 6.1 mm | KEEP-TRAY-DEPRESSION, KEEP-VISIBLE-UPPER |

## Organic/image-to-3D jobs

| Component | Mode | Views | Sacrificial band | Landmarks |
|---|---|---|---:|---:|
| SUNFLOWER_BODY | single_view_whole_object | front-right three-quarter, slightly elevated | 6.1 mm | 3 |

## Keep-outs

- `KEEP-TRAY-DEPRESSION` (aabb): conservative proxy for the open central tray depression; no base fill may close it. [-55, -55, 6.1] → [55, 55, 65]
- `KEEP-VISIBLE-UPPER` (aabb): protected visible upper region outside the underside edit band. [-100, -100, 6.1] → [100, 100, 65]

## Assembly sequence

1. Generate and preserve the raw Step1X geometry proposal.
2. Register uniformly to the 200 mm product envelope and convert +Y-up to +Z-up.
3. Do not repair, simplify or parametrically reconstruct the Step1X flower body.
4. Create the owner-confirmed 80 × 6 mm disc foot and Boolean-union only that foot.
5. Audit protected-region preservation and slice the single derived body; no physical assembly is required.

## Validation gates

- `architecture` / `VAL-ARCH-001` — run plan_hybrid_design.py and review authority/interface matrix Acceptance: one authority per dimension and no unresolved identifiers
- `proxy` / `VAL-PROXY-001` — compare the registered Step1X body and footed result outside the declared cylindrical foot ROI Acceptance: outside the foot ROI only the documented rigid 0.1 mm Z registration is measurable
- `component` / `VAL-COMP-001` — Step1X intake plus registered mesh audit and clay renders Acceptance: one coherent watertight component with accepted silhouette and open depression
- `integration` / `VAL-INT-001` — bounds, bed contact, sections and protected-region review Acceptance: only the underside edit band changes and the support plane is continuous
- `manufacturing` / `VAL-MFG-001` — Anycubic Slicer Next exact-profile run and layer review Acceptance: successful G-code with declared build-plate-only tree support, no floating-region warning and peak-flow analysis at or below 13.3 mm3/s
- `physical` / `VAL-PHY-001` — full prototype rocking, loaded tilt, dry-item handling and edge inspection Acceptance: all recorded physical criteria pass before print-candidate or release approval

## Plan diagnostics

No errors or warnings.
