# Decomposition review 0.5.3 — complete water openings and targeted bridges

Status: **human-approved by Stefan on 2026-09-04**

Machine-readable plan: `plan/hybrid-design-plan-v0.5.3.json`

## Approved ownership

- `SOURCE_SET_053` owns immutable Berlin/Brandenburg boundary, streets, water areas, water lines and S-/U-Bahn relations.
- `MAIN_RELIEF_SET_053` owns the two independently mounted halves and four positive color bodies.
- `WATER_APERTURE_TOOL_053` owns all-water negative geometry, protected keep-outs and the smallest required set of full-thickness topology bridges.

The visible design remains concept v07. The structural control does not reassign colors or redesign the map: it only prevents loose printed islands where a true water opening would otherwise disconnect land.

## Candidate rule

1. Candidate A: all retained waters open, no restoration.
2. Candidate B: Candidate A plus 2.0 mm full-thickness bridges only where disconnected printed land would otherwise result.
3. Candidate C: Candidate B plus local rear reinforcement only if exact analysis shows Candidate B cannot provide a viable handling span.

The build selects the least-material viable candidate. Candidate C is not automatically authorized: rear ribs conflict with the rear-datum-down print orientation and can obstruct halo-light lands. No rear grid or blanket rib network is permitted.

Every inserted bridge must record its panel half, coordinates, width, reason and restored area. Each half keeps its own upper wall support, so the permanent center seam is not the primary gravity load path.

## Gates that remain open

Source coverage, final topology, exact 3MF slicing, connector fit, light appearance, physical handling/proof load, watermark, rights and commercial release still require their own evidence. This approval does not authorize printer upload or print start.
