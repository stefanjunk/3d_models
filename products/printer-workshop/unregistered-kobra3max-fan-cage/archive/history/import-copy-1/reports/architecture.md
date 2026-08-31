# Hybrid design architecture — Original reversible fan cage with Metrimade camera branding

- Project ID: `kobra3max-metrimade-fan-cage`
- Claim: `functional_redesign`
- Sources: product_photo, design_description, owner_supplied_vector
- Units: `mm`
- Master envelope: [-31, -34.2, 0] → [31, 31, 6.6] (62 × 65.2 × 6.6 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: manufacturing, physical, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-MOUNT | critical | requested | Mount reversibly on the raised circular front bezel without modifying factory screws or shell. | process-matched D50/D52/D54 fit coupon and physical installation test |
| REQ-AIR | critical | assumed | Retain at least 60 percent projected open area across an assumed 40 mm intake disc and avoid any inward fan-blade intrusion. | deterministic projected-area calculation followed by fan-noise and thermal observation |
| REQ-BRAND | important | requested | Use the supplied four-color M as an air-permeable grille and place its outlined wordmark on a closed plate above the fan intake. | front render and real camera test video |
| REQ-PRINT | critical | requested | Print support-free with a 0.4 mm nozzle and preserve explicit aligned color bodies in 3MF. | mesh/3MF checks and destination-slicer layer review |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-BEZEL-D | provisional | Select exact raised-bezel target diameter. | Official uncalibrated photos suggest a range around 50-54 mm; D52 is the digital start candidate. | User caliper measurement and matching fit-coupon result. | physical, release |
| DEC-LOGO | resolved | Select authoritative camera-facing Metrimade artwork. | Project owner supplied metrimade-lockup-horizontal-color.svg with outlined wordmark and four colors. | Physical filament swatches remain a separate appearance gate. |  |
| DEC-SLICER | open | Approve exact Anycubic Slicer Next import, slot map, layer paths, and purge behavior. | Portable 3MF is generated, but the target slicer is unavailable in this environment. | Saved slicer project and reviewed preview. | manufacturing, physical, release |
| DEC-LABEL-CLEARANCE | provisional | Verify clearance of the closed upper wordmark plate against the printer front shell. | The plate is tangent to the top of the 62 mm cage and remains outside the assumed fan intake, but the shell surface is not dimensioned. | Physical D50/D52/D54 fit coupon plus paper/cardboard 54 by 8.8 mm clearance check or full prototype. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| CAGE_CORE | parametric | mesh | protect fan opening, carry branding, and provide reversible retention | [-31, -34.2, 0] → [31, 31, 6.6] (62 × 65.2 × 6.6 mm) | PETG / body_navy | IF-CAGE-BEZEL, IF-CAGE-INLAYS |
| COLOR_INLAYS | parametric | mesh | camera-facing brand identity only | [-27, -34.1, 0] → [27, 15, 0.6] (54 × 49.1 × 0.6 mm) | same-family PETG / body_navy, brand_teal, brand_aqua, brand_sand | IF-CAGE-INLAYS |
| PRINTER_BEZEL | purchased | cots | factory mounting datum and nominal interface owner | [-27, -27, 2.2] → [27, 27, 6.6] (54 × 54 × 4.4 mm) | unknown factory polymer / factory black | IF-CAGE-BEZEL |

## Interfaces

| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |
|---|---|---|---|---:|---:|---:|---:|---|
| IF-CAGE-BEZEL | CAGE_CORE ↔ PRINTER_BEZEL | PRINTER_BEZEL | purchased_mate | 0.25 mm | 0 mm | 0 mm | 0 mm | KEEP-FAN, KEEP-DUCT |
| IF-CAGE-INLAYS | CAGE_CORE ↔ COLOR_INLAYS | CAGE_CORE | other | 0 mm | 0 mm | 0 mm | 0.2 mm |  |

## Organic/image-to-3D jobs

No image-to-3D jobs are defined.

## Keep-outs

- `KEEP-FAN` (cylinder): no geometry may protrude rearward inside the existing intake/blade volume.
- `KEEP-DUCT` (aabb): avoid the lower front-shell duct/opening area. [-10, 25, 2.2] → [10, 40, 8]

## Assembly sequence

1. Measure the raised factory bezel and print the nearest fit coupon.
2. Print the matching cage visible face down with no supports.
3. Power off and cool the printer, then press the cage evenly onto the bezel.
4. Run staged fan, thermal, vibration, and camera checks before routine use.

## Validation gates

- `architecture` / `VAL-ARCH` — validate hybrid design plan and unique interface ownership Acceptance: no unresolved IDs; provisional dimensions remain explicit blockers
- `proxy` / `VAL-PROXY` — compare 62 mm cage circle, upper 54 by 8.8 mm label plate, and six clip sectors against the official front-shell photographs and declared lower-duct keep-out Acceptance: no tab at 6 o'clock; label stays above intake; physical shell clearance remains explicitly gated
- `component` / `VAL-MESH` — deterministic voxel surface and edge-incidence audit Acceptance: positive volume, zero boundary edges, zero nonmanifold edges
- `integration` / `VAL-AIR` — projected occupancy inside 40 and 42 mm intake discs Acceptance: at least 60 percent open for the 40 mm proxy
- `manufacturing` / `VAL-3MF` — 3MF package/XML/reference/material check and final Anycubic Slicer Next preview Acceptance: one aligned assembly, four named bodies, no dropped regions, maximum 16 planned changes
- `physical` / `VAL-PHYSICAL` — fit coupon then complete prototype Acceptance: moderate insertion/removal force, no shell marks, no new fan noise/thermal issue, camera-readable branding

## Plan diagnostics

No errors or warnings.
