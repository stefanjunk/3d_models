# 3D-design preflight 0.4.2 — MM-ART-010 parameterized variants

`MM-ART-010 | C3 (62.0/100) | R2 | K2 | Lane C | LOW_UNKNOWN`

## Decision

- Design release: `GO_WITH_CONTROLS`
- Palette selection: non-geometric product/slicer configuration
- Geometry authority: revision 0.4.0 `digital-candidate-r9`
- Current production size: 600 × 400 mm only
- Map-extent selection: deferred

The approved geometry already contains four ordered semantic tools. Choosing Oak, Mint Green, Midnight and Sky Blue therefore does not require new CAD, meshes, body names or concept approval. It requires only the final Anycubic Slicer Next tool-to-filament assignment or matching ACE loading, plus supplier-specific profiles and physical color/purge evidence.

## Parameter boundary

| Axis | State | Geometry consequence |
|---|---|---|
| `palette_preset` | Implemented | None; maps existing tools 1–4 to filaments |
| `display_mode` | Implemented | Selects existing `boundary_crop` or `context_outline` geometry |
| `assembled_size_mm` | Reserved | Non-default value requires X/Y regeneration and renewed validation |
| `map_extent` | Deferred | Requires a new frozen source and full placement/mesh validation |

Uniform production scaling in the slicer remains prohibited because it would also change connector clearance, relief height, wall gap, light keep-outs, aperture ligaments and printable color widths.

## Critical interfaces and open evidence

- Center connector and snap-in mounting interfaces remain E1/process-unqualified.
- Exact SUNLU batch, conditioning, compatible filament profiles, opacity and directed purge remain unresolved.
- Exact ACE slots are a job-local mapping that must be checked in the final slicer preview.
- As-built mass, substrate-specific wall anchors and physical proof load remain unresolved.
- Optional customer lighting remains outside the supplied product and requires a passive envelope/opacity coupon.

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

1. Map tools 1/2/3/4 to Oak/Mint Green/Midnight/Sky Blue in Anycubic Slicer Next and confirm exact filament profiles and the GUI preview.
2. Print the directed transition/opacity and existing connector/socket/light coupons.
3. Keep non-default size and map-extent variants blocked until their dedicated parametric/data workflow is implemented and validated.

Canonical machine-readable result: `preflight/preflight-result.json` (`PREFLIGHT-MM-ART-010-010`).
