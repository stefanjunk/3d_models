# Shower drain hair trap – funnel version with bed-contact swirl ribs

## Exact geometry
- Assembled outer size: **945.0 × 65.0 × 20.0 mm**
- 4 one-piece inverted-U segments
- Segment size: **236.25 × 65.0 × 20.0 mm**
- Shallow funnel catchers: 42 mm entry diameter, 2.2 mm depth
- Central sieve field: 2.6 mm holes, solid outer ring before the holes begin
- 5 spiral hair-guide ribs per funnel

## Change in this revision
The spiral ribs and center boss have been raised to the surrounding top-surface level for upside-down printing.
For robust CAD booleans the model uses a **0.02 mm relief**: the rib tips are 0.02 mm below the mathematical outer surface. With a normal 0.20 mm first layer, the slicer treats them as first-layer/bed-contact geometry in practice, while avoiding coplanar CAD failures.

This means the upside-down print has bed contact at:
- the broad outer top surface
- the spiral rib tips
- the center boss

Support is therefore mainly needed in the shallow funnel slopes between those contact regions.

## Recommended PETG support start profile (Anycubic Slicer Next / Orca-style)
For a 0.4 mm nozzle and 0.20 mm layer height:
- Support type: **Normal**
- Style: **Snug**
- On build plate only: **ON**
- Threshold angle: **~40°**
- Base density: **~10–15%** (or base-pattern spacing around 2.5–3.0 mm)
- Top Z distance: **0.30 mm**
- Support/Object XY distance: **0.45 mm**
- Support/Object first-layer gap: **0.50 mm**
- Top interface layers: **2**
- Interface pattern: **Rectilinear**
- Interface spacing: **0.40–0.50 mm**
- Support interface speed: **40–60 mm/s**

If the support is still difficult to remove:
1. increase Top Z distance to **0.35 mm**
2. increase XY distance to **0.55–0.60 mm**
3. use only **1 interface layer**

If the supported funnel surface becomes too rough:
1. reduce Top Z distance to **0.25 mm**
2. keep 2 interface layers
3. reduce interface spacing to **0.25–0.35 mm**

## Test first
Print `functional_test_tile_70mm.stl` before printing the four full segments. It includes the same funnel, sieve and full-height rib geometry.

## Main files
- `panel_left.stl`
- `panel_mid_left.stl`
- `panel_mid_right.stl`
- `panel_right.stl`
- `functional_test_tile_70mm.stl`
- `fit_coupon.stl`
- `joiner_key.stl`
- `joiner_keys_12x.stl`
- corresponding STEP files for the updated panels/test tile
- `build_shower_drain_hairtrap_945x65_funnel_flush.py`
