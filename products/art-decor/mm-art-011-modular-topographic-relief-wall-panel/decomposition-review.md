# Decomposition review — MM-ART-011 Harz and Rheinisches Revier

Status: architecture planner `PASS`; human decomposition approval pending. Production CAD and terrain processing remain blocked.

## Proposed product architecture

1. `REAR_GRID`: reuse the same six-segment PETG candidate platform and interface skeleton as MM-ART-010.
2. `TERRAIN_TILE_SET`: six 3 mm PLA substrates per pilot. These own the printable rear plane, external border, seam boundaries and minimum wall.
3. `HARZ_HEIGHTFIELD`: one frozen Copernicus GLO-30-derived 16-bit master, one global elevation-to-Z transform and six seam-locked relief bodies.
4. `RHENISH_HEIGHTFIELD`: one frozen current GeoBasis NRW DGM1 acquisition state, one global elevation-to-Z transform and six seam-locked relief bodies.
5. `HARZ_LIGHT_CUTTERS`: separate negative bodies derived from a few simplified valley or contour paths.
6. `RHENISH_LIGHT_CUTTERS`: separate negative bodies derived from selected mine-bench or infrastructure traces.
7. `LIGHTING_ENVELOPES`, `TILE_RETENTION_HARDWARE` and `WALL_HARDWARE_REFERENCE`: same responsibilities and exclusions as the Berlin product.

## Key interface and manufacturing decisions

- Tile service: shared three-datum/gravity-shoulder/magnetic interface. Four captive 6 × 2 mm magnets plus steel counterparts per tile are the recommended provisional hardware.
- Terrain authority: geometry remains continuous 16-bit height information. Color bands never replace or posterize the terrain master.
- Color: exactly three common horizontal changes per pilot, applied at identical model-Z heights on all six tiles. Broad global elevation quantiles are the starting point; a threshold may move only to preserve a documented major summit or mine-bench break.
- Mesh: 0.30 × 0.30 mm reference sampling, adaptive manufacturing geometry, 900,000 triangle target and 5,000,000 hard stop per tile. The conservative per-tile planning estimate is 898,890 triangles, about 42.9 MiB binary STL and 0.86 GiB working memory: planning `PASS`.
- Lighting: same 18 mm halo, 12 × 4 mm LED keep-out, selected straight front-light lands, three cable exits and optional 6 mm diffuser lands as Berlin.
- Apertures: at least 2 mm wide and 5 mm apart, no more than 12% open area per tile, with all seams, datums, retention and terrain-critical vertices protected.

## Approval effect

Approval authorizes proxy and production-CAD generation, frozen source acquisition, 16-bit master preparation, reference/manufacturing relief generation, coupons and exact-slicer dry runs. It does not approve printing, wall anchors, electrical components, physical appearance, safety or commercial release.

Authoritative machine-readable plan: `plan/hybrid-design-plan.json`; planner result: `reports/architecture.json`; generated height-field briefs: `briefs/HARZ_HEIGHTFIELD.md` and `briefs/RHENISH_HEIGHTFIELD.md`.
