# Hybrid design architecture — Original reversible honeycomb printhead cover with Metrimade camera branding

- Project ID: `kobra3max-metrimade-fan-cage`
- Claim: `functional_redesign`
- Sources: product_photo, design_description, owner_supplied_vector
- Units: `mm`
- Master envelope: [-37.2, -52, 0] → [37.2, 36.2, 10.8] (74.4 × 88.2 × 10.8 mm)
- Plan integrity: PASS (0 errors, 0 warnings)
- Release readiness: BLOCKED
- Blocked gates: manufacturing, physical, release

## Requirements

| ID | Priority | Evidence | Statement | Verification |
|---|---|---|---|---|
| REQ-MOUNT | critical | requested | Mount the spatial full-front add-on cover reversibly on the raised circular bezel, with four secondary side stabilizers, without modifying factory screws or shell. | process-matched D50/D52/D54 full-envelope fit frame and physical installation test |
| REQ-COVER | important | requested | Cover the complete camera-facing printhead front with a lightweight honeycomb carrier while reserving the fan zone exclusively for the perforated M badge. | front render, envelope check, and physical interference review |
| REQ-AIR | critical | assumed | Retain at least 60 percent projected open area across an assumed 40 mm intake disc and avoid any inward fan-blade intrusion. | deterministic projected-area calculation followed by fan-noise and thermal observation |
| REQ-BRAND | important | requested | Use the supplied four-color M as an air-permeable grille and place its outlined wordmark on a closed plate above the fan intake. | front render and real camera test video |
| REQ-PRINT | critical | requested | Print support-free with a 0.4 mm nozzle and preserve explicit aligned color bodies in 3MF. | mesh/3MF checks and destination-slicer layer review |

## Decision and gate log

| ID | Status | Topic | Current basis | Evidence needed | Blocks |
|---|---|---|---|---|---|
| DEC-COVER-ENVELOPE | provisional | Approve full-front shell silhouette, side engagement, and lower air-nozzle clearance. | Official front photographs and the documented 50 mm fan were proportion-scaled and rounded to an independent 72 by 88 mm face with 10.8 mm side fingers; no manufacturer shell drawing is published. | Physical D50/D52/D54 fit-frame result plus measured front width, height, and side engagement on the cooled, powered-off printhead. | physical, release |
| DEC-BEZEL-D | provisional | Select exact raised-bezel target diameter. | Official uncalibrated photos suggest a range around 50-54 mm; D52 is the digital start candidate. | User caliper measurement and matching fit-coupon result. | physical, release |
| DEC-LOGO | resolved | Select authoritative camera-facing Metrimade artwork. | Project owner supplied metrimade-lockup-horizontal-color.svg with outlined wordmark and four colors. | Physical filament swatches remain a separate appearance gate. |  |
| DEC-SLICER | open | Approve exact Anycubic Slicer Next import, slot map, layer paths, and purge behavior. | Portable 3MF is generated, but the target slicer is unavailable in this environment. | Saved slicer project and reviewed preview. | manufacturing, physical, release |
| DEC-LABEL-CLEARANCE | provisional | Verify clearance of the closed upper wordmark plate against the printer front shell. | The 54 by 8.8 mm plate is inside the photo-scaled cover envelope and remains outside the assumed fan intake, but the stock shell surface is not dimensioned. | Physical D50/D52/D54 fit frame plus full-cover interference and camera check. | physical, release |

## Components

| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |
|---|---|---|---|---|---|---|
| CAGE_CORE | parametric | mesh | cover the complete camera-facing printhead front, stabilize around its side edges, protect the fan opening, carry branding, and provide reversible retention | [-37.2, -52, 0] → [37.2, 36.2, 10.8] (74.4 × 88.2 × 10.8 mm) | PETG / body_navy | IF-CAGE-BEZEL, IF-CAGE-INLAYS |
| COLOR_INLAYS | parametric | mesh | camera-facing brand identity only | [-28, -42.8, 0] → [28, 15, 0.6] (56 × 57.8 × 0.6 mm) | same-family PETG / body_navy, brand_teal, brand_aqua, brand_sand | IF-CAGE-INLAYS |
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

1. Measure the raised factory bezel and print the nearest full-envelope fit frame.
2. Print the matching cover visible face down with no supports.
3. Power off and cool the printer, then press the cover evenly onto the bezel while holding only the reinforced fan module.
4. Run staged fan, thermal, vibration, and camera checks before routine use.

## Validation gates

- `architecture` / `VAL-ARCH` — validate hybrid design plan and unique interface ownership Acceptance: no unresolved IDs; provisional dimensions remain explicit blockers
- `proxy` / `VAL-PROXY` — compare the independent 72 by 88 mm face, 10.8 mm side fingers, upper 54 by 8.8 mm label plate, and six fan-clip sectors against official front-shell photographs and the lower-duct keep-out Acceptance: full front is covered; honeycomb stays outside the fan module; label stays above intake; physical side-shell and duct clearance remain explicitly gated
- `component` / `VAL-MESH` — deterministic voxel surface and edge-incidence audit Acceptance: positive volume, zero boundary edges, zero nonmanifold edges
- `integration` / `VAL-AIR` — projected occupancy inside 40 and 42 mm intake discs Acceptance: at least 60 percent open for the 40 mm proxy
- `manufacturing` / `VAL-3MF` — 3MF package/XML/reference/material check and final Anycubic Slicer Next preview Acceptance: one aligned assembly, four named bodies, no dropped regions, maximum 16 planned changes
- `physical` / `VAL-PHYSICAL` — full-envelope fit frame then complete prototype Acceptance: moderate insertion/removal force, light side-finger contact, no shell marks or duct collision, no new fan noise/thermal issue, camera-readable branding

## Plan diagnostics

No errors or warnings.
