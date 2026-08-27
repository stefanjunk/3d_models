# Shower drain hair trap – exact 945 × 65 × 20 mm, inverted U-profile

Generated parametrically from `build_shower_drain_hairtrap_945x65_uprofile.py`.

## Key geometry
- Exact assembled outer size: 945.0 × 65.0 × 20.0 mm
- Segments: 4
- Segment outer size: 236.250 × 65.0 × 20.0 mm
- Cross-section: inverted U-profile (open bottom)
- Top plate thickness: 4.2 mm
- Side wall thickness: 3.0 mm
- Side wall height below top plate: 15.8 mm

## Drainage concept
- 3 catcher zones per segment, 1 row centered across the width
- Total catcher zones: 12
- Catcher diameter: 44.0 mm
- Holes per catcher: 61
- Total holes: 732
- Hole diameter: 3.2 mm
- Gross open hole area: ~5887 mm²
- Estimated effective open area after swirl ribs: ~4881 mm²
- 5 spiral ribs per catcher to guide hair into the local catcher instead of letting a few hairs block the entire cover

## Joining strategy
- Exact outside dimensions are preserved by using loose internal joiner keys instead of protruding tabs.
- Each seam uses 3 keys.
- Included key part: `joiner_key.stl`
- Included 12-key batch: `joiner_keys_12x.stl`

## Files
- `panel_left.stl`, `panel_mid_left.stl`, `panel_mid_right.stl`, `panel_right.stl`
- `joiner_key.stl`, `joiner_keys_12x.stl`
- `fit_coupon.stl` (30 mm cross-section test)
- `functional_test_tile_70mm.stl`
- STEP exports and `assembly_reference.step`

## Printing notes
- Recommended material: PETG
- Suggested starting point: 0.20 mm layer height, 4-5 walls, 6 top/bottom layers, 25-35% infill
- Print the panels with the open side downward / top surface upward
- Print 9-12 keys and dry-fit the assembly before the full install
