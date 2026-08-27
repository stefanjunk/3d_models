# Shower drain hair trap – exact 945 × 65 × 20 mm, inverted U-profile, funnel catcher variant – edge-start swirl-rib revision

Generated parametrically from `build_shower_drain_hairtrap_945x65_funnel_edge.py`.

## Key geometry
- Exact assembled outer size: 945.0 × 65.0 × 21.0 mm
- Segments: 4
- Segment outer size: 236.250 × 65.0 × 21.0 mm
- Cross-section: inverted U-profile (open bottom)
- Top plate thickness: 4.2 mm
- Side wall thickness: 3.0 mm
- Side wall height below top plate: 16.8 mm

## Drainage / hair-catch concept
- 4 funnel catchers per segment, 1 row centered across the width
- Total funnel catchers: 16
- Funnel entry diameter: 46.0 mm
- Funnel floor diameter: 38.0 mm
- Funnel depth: 2.5 mm
- Hole-free outer rim inside each funnel: 3.0 mm radial margin before the sieve starts
- Holes per catcher: 55
- Total holes: 880
- Hole diameter: 2.8 mm
- Gross open hole area: ~5419 mm²
- Estimated effective open area after swirl ribs: ~4262 mm²
- 5 swirl ribs per catcher, beginning farther outward and curling inward for stronger hair guidance

## Joining strategy
- Exact outside dimensions are preserved by using loose internal joiner keys instead of protruding tabs.
- Each seam uses 3 keys.
- Included key part: `joiner_key.stl`
- Included 12-key batch: `joiner_keys_12x.stl`

## Files
- `panel_left.stl`, `panel_mid_left.stl`, `panel_mid_right.stl`, `panel_right.stl`
- `joiner_key.stl`, `joiner_keys_12x.stl`
- `fit_coupon.stl`
- `functional_test_tile_80mm.stl`
- STEP exports and `assembly_reference.step`

## Printing notes
- Recommended material: PETG
- User-requested print strategy: upside down with support
- Start with the `functional_test_tile_80mm.stl` to validate support scarring, funnel cleanup, and hair retention before printing all 4 segments
