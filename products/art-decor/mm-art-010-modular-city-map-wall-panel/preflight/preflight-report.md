# 3D-design preflight 0.5.1 — MM-ART-010 enlarged metriMade site marker

`MM-ART-010 | C3 (64.0/100) | R2 | K2 | Lane C | LOW_UNKNOWN`

## Decision

- Design release: `GO_WITH_CONTROLS`
- Palette selection: non-geometric product/slicer configuration
- Current DRAFT geometry authority: revision 0.5.0 `digital-candidate-r7` (unchanged map)
- Proposed visible change: canonical stacked metriMade lockup, 54.0 × 57.18 mm, concept v06 pending
- Current production size: 600 × 400 mm only
- Map-extent selection: deferred

The official Berlin address point and both existing map transforms locate the proposed 54.0 × 57.18 mm stacked metriMade lockup on the left half in existing tool 4. Its conservative envelope keeps 50.37 mm from the center seam in `context_outline` and 20.36 mm from the outer perimeter in `boundary_crop`. Revision 0.5.0 `digital-candidate-r7` remains evidence for the unchanged base-map pipeline only; it is not production proof of the new logo. The 2 m recognition target requires a process-matched physical sight test.

## Parameter boundary

| Axis | State | Geometry consequence |
|---|---|---|
| `palette_preset` | Implemented | None; maps existing tools 1–4 to filaments |
| `display_mode` | Implemented | Selects existing `boundary_crop` or `context_outline` geometry |
| `assembled_size_mm` | Reserved | Non-default value requires X/Y regeneration and renewed validation |
| `map_extent` | Deferred | Requires a new frozen source and full placement/mesh validation |
| `site_marker.location` | Retained from DRAFT r7 | Address/coordinate resolves to a frozen projected point |
| `site_marker.artwork` | Concept v06 pending | Canonical stacked metriMade SVG; logo/icon/monochrome mask remains replaceable by regeneration |
| `site_marker.size/relief/tool` | Concept v06 pending | Proposed 54.0 × 57.18 mm, 0.60 mm relief, existing tool 4 |

Uniform production scaling in the slicer remains prohibited because it would also change connector clearance, relief height, wall gap, light keep-outs, aperture ligaments and printable color widths.

## Critical interfaces and open evidence

- Center connector and snap-in mounting interfaces remain E1/process-unqualified.
- Exact SUNLU batch, conditioning, compatible filament profiles, opacity and directed purge remain unresolved.
- Exact ACE slots are a job-local mapping that must be checked in the final slicer preview.
- As-built mass, substrate-specific wall anchors and physical proof load remain unresolved.
- Optional customer lighting remains outside the supplied product and requires a passive envelope/opacity coupon.
- The canonical metriMade asset `MM-BRAND-001-R1` is selected but brand-clearance approval remains open.
- Recognition from 2 m is only a target until the Oak/Sky Blue raised-logo coupon passes human review.
- Alternate marker artwork requires fresh rights, minimum-feature, placement, mesh and slicer checks.
- The `context_outline` left project exceeded the nominal 600 second slice target but completed inside the controlled 900 second retry.

## Hard gates

| Gate | Status |
|---|---|
| G0 scope/variant | PASS |
| G1 entities/interfaces | PASS |
| G2 critical evidence | WARN |
| G3 manufacturing profile | WARN |
| G4 verification definition | PASS |
| G5 autonomy/criticality | PASS |
| G6 lifecycle | PASS |

## Next evidence

1. Explicitly approve concept v06 before revision 0.5.1 CAD, mesh or 3MF generation.
2. Build and validate a fresh revision 0.5.1 candidate, then print the Oak/Sky Blue 2 m recognition coupon.
3. Review profiles, ACE/purge and the rear metriMade.com watermark before permanent assembly and wall proof.

Canonical machine-readable result: `preflight/preflight-result.json` (`PREFLIGHT-MM-ART-010-013`).
