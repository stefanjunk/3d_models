# 3D-design preflight 0.5.0 — MM-ART-010 parameterized site marker

`MM-ART-010 | C3 (64.0/100) | R2 | K2 | Lane C | LOW_UNKNOWN`

## Decision

- Design release: `GO_WITH_CONTROLS`
- Palette selection: non-geometric product/slicer configuration
- Current DRAFT geometry authority: revision 0.5.0 `digital-candidate-r7`
- New visible geometry: parameterized raised site marker, concept v05 approved and digitally validated
- Current production size: 600 × 400 mm only
- Map-extent selection: deferred

The official Berlin address point and both existing map transforms locate the compact 16.5 mm metriCreate mark on the left half in existing tool 4. Revision 0.5.0 `digital-candidate-r7` passes the geometry build, four composite mesh audits, four vendor-aware Anycubic 3MF geometry checks and four native Anycubic slices. The 3MF checks resolve four non-empty bodies per project, including both right halves. The marker rises 0.6 mm and remains at least 12.25 mm from a retained light opening.

## Parameter boundary

| Axis | State | Geometry consequence |
|---|---|---|
| `palette_preset` | Implemented | None; maps existing tools 1–4 to filaments |
| `display_mode` | Implemented | Selects existing `boundary_crop` or `context_outline` geometry |
| `assembled_size_mm` | Reserved | Non-default value requires X/Y regeneration and renewed validation |
| `map_extent` | Deferred | Requires a new frozen source and full placement/mesh validation |
| `site_marker.location` | Implemented in DRAFT r7 | Address/coordinate resolves to a frozen projected point |
| `site_marker.artwork` | Implemented in DRAFT r7 | Rights-cleared logo/icon/monochrome mask remains replaceable by regeneration |
| `site_marker.size/relief/tool` | Implemented in DRAFT r7 | Process dimensions and one existing tool are independently controlled |

Uniform production scaling in the slicer remains prohibited because it would also change connector clearance, relief height, wall gap, light keep-outs, aperture ligaments and printable color widths.

## Critical interfaces and open evidence

- Center connector and snap-in mounting interfaces remain E1/process-unqualified.
- Exact SUNLU batch, conditioning, compatible filament profiles, opacity and directed purge remain unresolved.
- Exact ACE slots are a job-local mapping that must be checked in the final slicer preview.
- As-built mass, substrate-specific wall anchors and physical proof load remain unresolved.
- Optional customer lighting remains outside the supplied product and requires a passive envelope/opacity coupon.
- The metriCreate logo asset is selected but brand-clearance approval remains open.
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

1. Review physical profiles, four ACE slots, wipe tower, purge transitions and seams in the Anycubic GUI.
2. Print directed transition/opacity, logo-readability and existing connector/socket/light coupons.
3. Place and approve the rear metriMade.com watermark, then print, permanently assemble and proof the selected example.

Canonical machine-readable result: `preflight/preflight-result.json` (`PREFLIGHT-MM-ART-010-012`).
