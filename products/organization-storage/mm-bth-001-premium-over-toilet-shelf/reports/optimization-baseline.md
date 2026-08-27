# Revision 0.2.0 DRAFT optimization baseline

## Status

**BLOCKED — no exact slicer is installed in the current environment.** No geometry or process candidate is selected and no print-time/material saving is claimed.

## Frozen digital baseline

- Specification/configuration revision: `0.2.0`
- Geometry revision: `r0.2.0-draft.2`
- DRAFT build: `output/rev-0.2.0-draft/`
- Build manifest: `output/rev-0.2.0-draft/reports/build_manifest.json`
- Validation report: `output/rev-0.2.0-draft/reports/validation_report.json`
- CAD/export tools: CadQuery 2.8.0, Trimesh 4.4.1, Python 3.11.15
- Provisional process: PETG, 0.6 mm nozzle, 0.68 mm line width, 0.30 mm structural layer
- Exact printer, filament product, drying state, slicer/version, profile hash, volumetric-flow limit and 3MF: **not available**
- Intended orientation: already encoded per part in the manifest/parts CSV

## Baseline geometry metrics

- 42 unique printable files / 69 configured instances, including three coupon files
- 63 named assembly bodies
- 113,692 triangles across the unique printable STL files
- 5.425 MiB total unique STL size
- Largest file: `personalized_header_insert_print`, 10,562 triangles / 0.504 MiB
- Assembly preview: 127,462 triangles / 6.078 MiB
- CAD enclosed volume proxy: 11,367.04 cm³ across configured instances; this is **not** deposited material mass because slicer wall/infill decisions are unavailable
- Digital geometry and integration validation: PASS
- All six M3 wide-module seam plates: 0.0 mm modeled boss-contact gap with open coaxial axes
- Manufacturing status: BLOCKED by absent exact-profile 3MF/slicer review

## Protected constraints

- Four M4-locked floor contacts, four-nub TPU retention and the complete side-frame load path
- Seven segment seams per side family, M4 locks and alignment features
- M5 frame/bracket grid, M4 shelf/bracket axes, shelf seams and joiners
- 620 mm shelf clear span, Z=1050/1400 mm top datums and 32 mm shelf section
- Real split-half drawer housing/drawer compounds, both M3 seam plates, guides, swept volume and front module stops
- Wall-restraint axes, bearing regions, wall gap and installer access
- Bed-contact faces, shelf top datums, module seats, decoration capture faces and localized image-relief boundary
- Toilet/service, baseboard and measured-site keep-outs

## Existing efficient patterns

- Open, diagonally braced side-frame segments instead of solid side walls
- Ribbed shelf skins with two continuous 14 × 32 mm edge beams
- Three printable shelf tiles with local seam reinforcement
- Thin open module shells and replaceable accent skins
- Purchased metal fasteners/anchors instead of printed primary threads or wall anchors

## Path-compatibility precheck

`plan_shell_ribs.py` with 0.6/0.68/0.30 mm, four shell paths, three rib paths and five floor layers reports:

- nominal four-path shell: 2.527 mm
- nominal three-path rib/web: 1.911 mm
- five-layer skin: 1.50 mm
- 2.8 mm plate with two wall paths per side: `SUB_LINE_WIDTH_CORE` (about 0.209 mm nominal remainder)
- requested flow at 45 mm/s: 9.18 mm³/s; not accepted because the exact hotend/filament flow limit is unknown

The thin module walls therefore do not have a reliable independent infill core. Changing infill percentage alone may not change those walls and must not be credited without exact slicing.

## Required candidate matrix

| Candidate | Geometry | Process | Current state |
|---|---|---|---|
| Baseline | current R0.2.0 DRAFT | provisional 0.6/0.30 PETG | geometry measured; exact slicing unavailable |
| A — process only | unchanged | exact-profile wall/infill/speed alternatives | blocked |
| B — geometry only | protected shell/rib/window alternative | baseline profile | blocked pending exact baseline and physical stiffness evidence |
| C — combined | selected B | selected A | blocked |

The `r0.2.0-draft.2` seam-seat correction is an integration repair, not an optimization candidate: it removes a modeled 1.5 mm air gap without changing printable part geometry or claiming time/material savings.

## Next acceptance action

Install or identify the exact target slicer and printer/material profile, create a revision-bound 3MF, then record model/support material, time, layer count, wall paths, infill, retractions, peak flow, supports, warnings, import time and slice time for Baseline/A/B/C. Do not lightweight the structural frame or shelves before the exact baseline and physical tests exist.
