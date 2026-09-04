# Requirements review 0.5.2 — complete water openings and blue S/U-Bahn network

Status: **approved from Stefan's explicit correction on 2026-09-04**.

Revision 0.5.2 corrects the map semantics; it is not a palette-only change.
The revision 0.5.1 meshes and 3MF projects remain preserved as historical
digital evidence, but they are rejected as product candidates because mapped
water areas are incomplete and tool 4 represents motorway/trunk routes.

## Approved requirement and recommended implementation

| Item | Requirement | Source |
|---|---|---|
| Water | Cut out all mapped water areas, including lakes such as Tegeler See, plus river/canal/stream paths | user-stated; manufacturing thresholds and protected structural keep-outs remain explicit |
| Water appearance | Water is negative through-geometry for optional front-through light, not a blue printed body | user-stated |
| Blue transit layer | Use Sky Blue for S-Bahn and U-Bahn route lines instead of motorways | user-stated |
| Motorways | Keep motorway/trunk routes inside the Midnight street network without a separate blue accent | inferred directly from the replacement instruction |
| Context boundary | Retain the already approved Sky Blue Berlin boundary in `context_outline` | unchanged approved feature |
| Site marker | Retain the raised metriMade site marker in semantic tool 4 | unchanged approved feature |
| Four-color ceiling | Keep exactly the existing four semantic tools and selected Oak/Mint Green/Midnight/Sky Blue loading | unchanged user-stated constraint |
| Source route | Add water multipolygons and S/U-Bahn route relations to a new immutable, context-complete OSM derivative | recommended fail-closed implementation |

The frozen Berlin snapshot proves that Tegeler See is present as OSM relation
`451908` (`natural=water`, `water=lake`). At the approved transforms its opening
would occupy approximately 429.13 mm² in `boundary_crop` and 279.09 mm² in
`context_outline`, wholly on the left print. It is therefore neither absent
from OSM nor too small to manufacture; the prior line-only extraction discarded
it.

S-Bahn and U-Bahn are selected from public-transport route geometries rather
than from undifferentiated railway tracks: S-Bahn uses `route=light_rail` plus
`network:metro=s-bahn`; U-Bahn uses `route=subway` plus
`network:metro=u-bahn`. Opposite-direction route duplicates will be dissolved
before rasterization so the artwork shows a readable network rather than every
individual track.

## Water completeness and printability contract

- Source scope includes mapped water polygons (`natural=water`, reservoirs,
  basins and riverbanks) and river/canal/stream lines.
- Every source water component is accounted for in a generated coverage report.
- Components below the physical aperture threshold or removed by perimeter,
  seam, connector, hanger, logo or watermark keep-outs are counted with removed
  area and reason; they are never silently dropped.
- Tegeler See is a named regression fixture and must have nonzero final opening
  area in both display modes.
- Each half must remain one connected positive body; necessary material bridges
  are reported with location, width and restored area.
- The existing maximum 12% open-area fraction per half and 5 mm outer ligament
  remain unchanged unless a later approved structural revision changes them.

## Gate effect

- The exact user correction is treated as requirements approval for revision
  0.5.2; no consequential semantic choice remains unresolved.
- Concept approval is reopened because the visible transport layer and the
  extent of negative water geometry change.
- Production extraction, CAD, mesh and 3MF generation remain blocked until the
  revision 0.5.2 concept is explicitly approved.
- The complete `context_outline` water/route derivative must be reacquired from
  the already recorded frozen Germany snapshot before production generation;
  the currently local Berlin PBF is sufficient for the diagnostic and concept,
  but not for context production coverage.

Diagnostic authority:
`validation/v0.5.2/berlin/requirements-diagnostic-r1/water-transit-layer-audit.json`.
