# Requirements review 0.5.1 — enlarged metriMade site marker

Status: **approved from Stefan's explicit correction on 2026-09-03**.

This revision changes only the replaceable visible address artwork. The Berlin
map geometry, two display modes, 600 × 400 mm envelope, permanent split,
connectors, mounting, light preparation and four semantic color tools remain
unchanged. Revision 0.5.0 `digital-candidate-r7` remains the current geometry
authority until the new concept is approved and a new immutable candidate is
generated.

## Approved requirement and recommended implementation

| Item | Requirement | Source |
|---|---|---|
| Brand | Replace the visible metriCreate marker with the canonical `metriMade` logo | user-stated |
| Viewing intent | The logo should be recognizable from about 2 m | user-stated; physical human sight test remains required |
| Asset | `MM-BRAND-001-R1` stacked monochrome lockup | recommended; binding one-color production asset with outlined `metriMade` wordmark |
| Size | 54.0 × 57.18 mm, aspect ratio preserved | recommended; largest conservative size that retains the existing 50 mm center-seam clearance in both display modes |
| Location | Sterkrader Straße 24, 13507 Berlin | unchanged user-stated parameter; existing frozen EPSG:25833 point retained |
| Relief | 0.60 mm above the highest local face | unchanged; three nominal 0.20 mm layers |
| Color/tool | existing semantic tool 4 | unchanged; Sky Blue in the selected pilot palette and no fifth filament |
| Parameterization | address/coordinate, artwork asset/type, width, orientation, relief height and tool remain independent | unchanged user-stated product requirement |

At 54 mm width, the stacked lockup is approximately 3.27 times wider and 3.58
times taller than the former 16.5 × 15.97 mm compact marker. Its conservative
rectangular envelope remains inside both retained map bodies. The tightest
center-seam clearance is 50.37 mm in `context_outline`; the tightest perimeter
clearance is 20.36 mm in `boundary_crop`. A 0.05 mm raster inspection resolves
13 logo components and a smallest component bounding dimension of 1.20 mm.

These digital dimensions support the intended viewing distance but do not
prove human recognition. Acceptance requires a process-matched raised-logo
coupon, viewed on a wall at 2.0 m under ordinary indoor lighting, with the
intended Oak/Sky Blue contrast.

## Gates and exclusions

- The exact user correction is treated as requirements approval for revision
  0.5.1; no consequential requirement remains unresolved.
- Concept approval is reopened because logo identity and visible size change.
- Production source, mesh and 3MF generation remain blocked until concept v06
  is explicitly approved.
- The visible address logo remains separate from the required recessed rear
  `metriMade.com · MM-ART-010 · v0.5.1` release watermark.
- `MM-BRAND-001-R1` remains brand-clearance pending; no commercial-release
  claim is made.
- The official address source verifies the point, not company occupancy.
