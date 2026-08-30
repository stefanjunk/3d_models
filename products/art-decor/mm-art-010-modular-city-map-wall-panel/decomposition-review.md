# Decomposition review — MM-ART-010 Berlin

Status: **superseded by requirements revision 0.3.0**. The historical planner result was `PASS` only against the now-rejected revision 0.2.0 rear-grid requirements. Production CAD remains blocked.

## Proposed product architecture

1. `REAR_GRID`: six interlocking PETG candidate segments. This is the sole owner of the 200 mm pitch, wall plane, 18 mm standoff, gravity shoulders, tile datums, magnet pockets, LED routes and cable exits.
2. `ART_TILE_SET`: six 3 mm PLA substrates. These own the printable rear plane, outer border, seam boundaries and minimum wall.
3. `BERLIN_VECTOR_FIELD`: one immutable OpenStreetMap-derived global vector master. It produces six registered tile regions and the four named Urban Signal color solids; it never owns a mounting feature.
4. `LIGHT_CUTTER_SET`: separate negative bodies derived from a few simplified paths. They cut the approved true openings only after seam, datum, attribution and mount keep-outs are applied.
5. `LIGHTING_ENVELOPES`: non-product volumes for the perimeter halo strip, selected straight front-light strip lands, diffuser lands and cable routes. Customer lighting remains removable and optional.
6. `TILE_RETENTION_HARDWARE`: recommended four captive 6 × 2 mm magnets plus steel counterparts per tile. Printed gravity shoulders carry vertical self-weight; magnets only hold the tile toward the wall.
7. `WALL_HARDWARE_REFERENCE`: a generic planning envelope only. Wall anchors remain customer-selected and outside the product claim.

## Key interface decisions

- Tile service: front placement onto three datum pads and a bottom shoulder, then magnetic seating. This avoids a fatigue-sensitive printed snap and permits individual reprinting; exact pockets and pull-off force remain coupon-controlled.
- Visible seam: 0.25 mm target, selected from the already defined 0.15 / 0.25 / 0.35 / 0.45 mm coupon.
- Color: separate, closed and non-overlapping semantic solids in one global frame. No slicer-only painting is authoritative.
- Lighting: 12 × 4 mm keep-out for 8/10 mm strips; dedicated straight lands sit behind selected aperture clusters while the perimeter route creates the halo.
- Apertures: at least 2 mm wide and 5 mm apart, no more than 12% open area per tile, with 8 mm seam and 12 mm datum/retention exclusion zones.

## Approval effect

Approval authorizes proxy and production-CAD generation for the shared rear-grid platform, Berlin vector pipeline, interface coupons, named color solids and light cutters. It does not approve printing, wall anchors, electrical components, physical appearance, safety or commercial release.

Authoritative machine-readable plan: `plan/hybrid-design-plan.json`; planner result: `reports/architecture.json`; readable generated matrix: `reports/architecture.md`.
