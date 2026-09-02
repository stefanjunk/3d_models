# Requirements review 0.4.2 — parameterized MM-ART-010 variants

Status: **approved by Stefan's explicit corrections on 2026-09-02**.

This revision changes the configuration model, not the Berlin geometry. The existing revision 0.4.0 `digital-candidate-r9` meshes, relief topology, split, connectors, mounting and light preparation remain authoritative.

## Variant axes

| Axis | Current state | Geometry effect | Authority |
|---|---|---:|---|
| `palette_preset` | Implemented | None | `product-variants.json` and `palette-catalog.yaml` |
| `display_mode` | `boundary_crop` or `context_outline` implemented | Selects one existing geometry set | revision 0.4.0 production parameters |
| `assembled_size_mm` | Only 600 × 400 mm is currently production-supported | Non-default values require regeneration | reserved in `product-variants.json` |
| `map_extent` | Berlin frozen source only | A new extent requires new data and geometry | deferred |

## Selected colorway

`MM-ART-010-CW-OAK-MINT-MIDNIGHT-SKY` maps the existing tools without changing their bodies:

1. Tool/ACE 1 — Oak (`FIL-0005`) — `land_base`
2. Tool/ACE 2 — Mint Green (`FIL-0001`) — `medium_relief_and_areas`
3. Tool/ACE 3 — Midnight (`FIL-0003`) — `street_network`
4. Tool/ACE 4 — Sky Blue (`FIL-0002`) — `berlin_boundary_and_accents`

The ACE numbers are a recommended job-local loading order and must be confirmed in the final Anycubic Slicer Next preview. Exact supplier-specific filament profiles, opacity and directed purge remain process gates.

## Scaling rule

The product is not released for arbitrary uniform slicer scaling. A future size implementation will regenerate the map and outer envelope in X/Y while keeping connector/socket clearances, wall gap, relief heights, aperture ligaments, light keep-outs and minimum printable feature widths at qualified absolute dimensions. Until that implementation is validated, 600 × 400 mm is the only production value.

## Deferred map selection

Future selection of another city, boundary or rectangular context will be a separate `map_extent` parameter. It requires a newly frozen and rights-audited source plus renewed placement, split, interface, mesh and exact-slicer validation. No automatic substitution is currently allowed.

## Gate effect

- Concept v03 remains the approved design authority.
- Concept v04 is an informational palette preview and has no approval-gate function.
- Palette selection is a product/slicer configuration and must not regenerate, rename or rescale geometry.
- Physical print-candidate, purge/opacity, mounting, appearance, watermark, rights, safety and commercial gates remain unchanged.
