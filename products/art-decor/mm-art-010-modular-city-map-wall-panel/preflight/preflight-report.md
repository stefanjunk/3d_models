# 3D-design preflight 0.5.0 — MM-ART-010 parameterized site marker

`MM-ART-010 | C3 (64.0/100) | R2 | K2 | Lane C | LOW_UNKNOWN`

## Decision

- Design release: `GO_WITH_CONTROLS`
- Palette selection: non-geometric product/slicer configuration
- Previous geometry authority: revision 0.4.0 `digital-candidate-r9`
- New visible geometry: parameterized raised site marker, concept approval pending
- Current production size: 600 × 400 mm only
- Map-extent selection: deferred

The official Berlin address point and both existing map transforms support a deterministic site-marker concept. The compact 16.5 mm metriCreate mark remains on the left half, more than 50 mm from the center seam, and is assigned to existing tool 4. Because it adds visible raised geometry, production CAD, mesh and 3MF generation is blocked until concept v05 receives human approval.

## Parameter boundary

| Axis | State | Geometry consequence |
|---|---|---|
| `palette_preset` | Implemented | None; maps existing tools 1–4 to filaments |
| `display_mode` | Implemented | Selects existing `boundary_crop` or `context_outline` geometry |
| `assembled_size_mm` | Reserved | Non-default value requires X/Y regeneration and renewed validation |
| `map_extent` | Deferred | Requires a new frozen source and full placement/mesh validation |
| `site_marker.location` | Concept-ready | Address/coordinate resolves to a frozen projected point |
| `site_marker.artwork` | Concept-ready | Rights-cleared logo/icon/monochrome mask is replaceable |
| `site_marker.size/relief/tool` | Concept-ready | Process dimensions and one existing tool are independently controlled |

Uniform production scaling in the slicer remains prohibited because it would also change connector clearance, relief height, wall gap, light keep-outs, aperture ligaments and printable color widths.

## Critical interfaces and open evidence

- Center connector and snap-in mounting interfaces remain E1/process-unqualified.
- Exact SUNLU batch, conditioning, compatible filament profiles, opacity and directed purge remain unresolved.
- Exact ACE slots are a job-local mapping that must be checked in the final slicer preview.
- As-built mass, substrate-specific wall anchors and physical proof load remain unresolved.
- Optional customer lighting remains outside the supplied product and requires a passive envelope/opacity coupon.
- The metriCreate logo asset is selected but brand-clearance approval remains open.
- Alternate marker artwork requires fresh rights, minimum-feature, placement, mesh and slicer checks.

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

1. Obtain human approval for `concepts/berlin-site-marker-concept-v05.png`.
2. Then integrate the marker into tool 4, rebuild both display modes and create/validate fresh Anycubic 3MF projects.
3. Print directed transition/opacity, logo-readability and existing connector/socket/light coupons.

Canonical machine-readable result: `preflight/preflight-result.json` (`PREFLIGHT-MM-ART-010-011`).
