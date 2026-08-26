# Shower drain hair trap – exact 945 × 65 × 20 mm, inverted U-profile, funnel catcher variant

This is the revised variant requested after the T-slot / plug-in wall concept did not print cleanly enough.
It returns to the **one-piece inverted U-profile segment design** and is intended to be printed **upside down with support**.

## Main geometry
- Exact assembled outer size: **945.0 × 65.0 × 20.0 mm**
- Segment count: **4**
- Segment outer size: **236.25 × 65.0 × 20.0 mm** each
- Cross-section: **inverted U-profile** (open underside)
- Top plate thickness: **4.2 mm**
- Side wall thickness: **3.0 mm**
- Side wall height below top plate: **15.8 mm**

## Revised drain concept
- **4 catcher zones per segment** in one centered row → **16 total**
- Each catcher uses a **shallow funnel**:
  - funnel entry diameter: **42.0 mm**
  - funnel depth: **2.2 mm**
  - lower flat capture-floor diameter: **35.0 mm**
- The actual sieve starts only toward the middle:
  - hole-free outer rim inside each funnel: **3.5 mm radial margin**
  - hole field radius: **14.0 mm**
- Sieve hole diameter reduced to **2.6 mm** to better prevent hair from slipping through
- **43 holes per catcher**, **688 total**
- Gross open hole area: **~3653 mm²**
- **5 swirl ribs per catcher**, beginning farther outward and curling inward for stronger hair guidance

## Joining strategy
- Exact outside dimensions are preserved via **loose internal joiner keys**.
- Each seam uses **3 keys**.
- Included parts:
  - `joiner_key.stl`
  - `joiner_keys_12x.stl`

## Files
- `panel_left.stl`
- `panel_mid_left.stl`
- `panel_mid_right.stl`
- `panel_right.stl`
- `joiner_key.stl`
- `joiner_keys_12x.stl`
- `fit_coupon.stl`
- `functional_test_tile_70mm.stl`
- corresponding STEP files
- parametric source: `build_shower_drain_hairtrap_945x65_funnel.py`

## Recommended print/test flow
1. Print `functional_test_tile_70mm.stl` first.
2. Check support scarring on the visible funnel side.
3. Test whether wet hair stays reliably on the ribs / sieve and does not pass through.
4. If necessary, reduce support contact density or use support-interface layers for easier cleanup.
5. Only then print the 4 final segments.

## Notes
- The geometry was adapted specifically to your request:
  - no separate snap-in plates
  - shallow funnel-shaped drains
  - sieve located more toward the center
  - no holes near the outer funnel edge
  - swirl ribs begin farther outward for a stronger hair-guiding effect
