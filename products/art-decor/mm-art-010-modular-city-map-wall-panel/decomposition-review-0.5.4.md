# Decomposition review 0.5.4 — four defects in the water pipeline

Status: **proposed, human approval required**

Generator: `source/v0.5.4/berlin/build_berlin_hydrography.py`
Parameters: `source/v0.5.4/berlin/hydrography-parameters.json`,
`source/v0.5.4/berlin/site-marker-parameters.json`
Independent checker: `source/v0.5.4/berlin/verify_candidate_water.py`

## Ownership

- `SOURCE_SET_054` owns the frozen multi-source hydrography: OpenStreetMap
  2026-08-30 unioned with the official Berlin Gewässerkarte, with BKG DLM250 as
  an independent named-water reference. Verified: Tegeler See and the Havel are
  100 % contained in the production union, so **the source was never the cause**.
- `WATER_APERTURE_TOOL_054` owns the aperture raster, every keep-out, the
  topology bridges and the fail-closed named-water gate.
- `MARKER_TOOL_054` owns marker placement, its anchor and its support ring.
- `MAIN_RELIEF_SET_054` is unchanged from 0.5.3.

## The four defects, each with its fix

### D1 — the gate measured the wrong array

`make_raster_masks` wrote the water accounting and raised the Tegeler See
regression, then `build_mode` ran `update_aperture_keepout` afterwards and
removed 821.4 mm² (`context_outline`) / 552.3 mm² (`boundary_crop`) more. The
report therefore recorded Tegeler See at 262.6 mm² open while the exported
`tool1-base` STL was 92.5 % solid across the lake.

**Fix:** `evaluate_final_water` runs inside a wrapper around
`update_aperture_keepout`, i.e. on the array that is converted to geometry, and
raises before any export when a fixture fails.

### D2 — the marker was centred on Tegeler See

The 54 mm logo silhouette covered 248 mm² of a 279 mm² lake, and a generic
12.0 mm aperture clearance was dilated around it.

**Fix:** anchor the artwork's west edge on the frozen address (+27.0 mm east),
and replace the 12.0 mm guard with the 2.0 mm functional support ring the raised
relief actually needs.

### D3 — keep-outs were bounding rectangles, not footprints

Each socket was protected by a 62 × 66 mm rectangle and each connector by
58 × 24 mm. Measured cost: 1 326.9 mm² of `boundary_crop` water and 287.6 mm² of
`context_outline` water, protecting no additional functional surface. The
5.0 mm outline ligament deleted a further 793.4 mm².

**Fix:** the keep-out is the exact rear-cutter footprint of the seam connector
and the socket anchor — the same geometry `BASE.rear_cutters` cuts — dilated by
the documented 12.0 mm functional margin. The outline ligament goes to 2.0 mm.
The centre-seam band and the two title bars stay as rectangles.

### D4 — the polygon rasteriser let one hole erase another lake

`draw_polygon_mask` filled every exterior and then punched every interior ring,
so a hole belonging to one water polygon deleted a *different* polygon lying
inside it. Schlachtensee and Groß-Glienicker See were 0.0 % open in revision
0.5.3 for this reason alone, although both are fully present in the source.

**Fix:** `polygon_mask` rasterises each polygon with its own holes into a local
tile and ORs the tiles together.

## Gates

Fail-closed inside the build, on the final aperture:

- Tegeler See and the Havel corridor ≥ 0.85 of their **mapped** area open, where
  mapped = official outline ∩ production water (the official outline includes
  islands the production union correctly excludes).
- All mapped water ≥ 0.80 open in `context_outline`, ≥ 0.70 in `boundary_crop`.
- Named water in aggregate ≥ 0.75 open.
- Every named body below 0.85 is listed with its area in the build report.

Independent, after the build: `verify_candidate_water.py` sections the exported
`tool1-base` STLs and remeasures. It never reads the build's own arrays.

Unchanged from 0.5.3: per-half open area ≤ 12 %, one connected watertight body
per half, disjoint tool bodies, no rear grid and no blanket ribs.

## Requires explicit approval

1. **Per-half open-area guard 0.12 → 0.15.** With correct hydrography the
   `boundary_crop` right half reaches 0.12966 — east Berlin genuinely carries
   Großer Müggelsee, Langer See, Seddinsee, Dämeritzsee, Spree and Dahme. The
   other three halves stay at 0.10681, 0.08954 and 0.11102. The 0.12 value is an
   undocumented digital heuristic with no measurement behind it, and the
   physical handling and installed proof-load gates are open. Candidate
   `digital-candidate-r1` is retained as the rejected evidence of that failure.
   The alternative — narrowing the water-line slots below 2.2 mm — would shrink
   rivers instead of lakes and was deliberately not taken without a decision.
2. Marker seam clearance 50.0 mm → 20.0 mm (achieved 23.37 / 41.94 mm).
3. Outline ligament 5.0 mm → 2.0 mm.
4. Marker aperture clearance 12.0 mm → 2.0 mm.
5. Accepting the wall-mount and title-bar water conflicts listed in
   `known_residual_conflicts`, or scheduling a mount-relocation phase.

## Gates that remain open

Exact 3MF slicing, connector fit, light appearance, physical handling and
installed proof load, watermark, rights and commercial release. This approval
does not authorize printer upload or print start.
