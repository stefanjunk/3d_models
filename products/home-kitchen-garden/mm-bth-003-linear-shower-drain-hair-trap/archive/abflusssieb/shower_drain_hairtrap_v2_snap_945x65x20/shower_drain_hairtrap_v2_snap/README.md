# Shower Drain Hair Trap V2 – printable plug-together version

## Exact installed envelope
- Length: **945.00 mm**
- Width: **65.00 mm**
- Height: **20.00 mm**

## FDM-oriented decomposition
The inverted U-profile is no longer printed as one difficult piece.

1. **Top/deck plates** print flat, underside on the build plate and visible surface upward.
2. **Side walls** print lying on their large outside face.
3. Side-wall joints are offset by half a deck length, so each 236.25 mm bridge wall spans one deck seam.
4. Small underside deck tabs prevent longitudinal drift while the side walls carry the seam mechanically.

This avoids large support structures, keeps all sieve holes vertical/circular and keeps build-plate texture off the visible top surface.

## Drainage
- Decks: 4 × 236.250 mm
- Hair catcher fields: 16 total (4 per deck)
- Catcher diameter: 46.0 mm
- Holes per catcher: 73
- Total sieve holes: 1168
- Hole diameter: 3.20 mm
- Gross open hole area: ~9394 mm² (15.3% of total top footprint)
- 5 recessed swirl ribs per field; rib tops remain below the surrounding walking surface.

## Side wall / rail system
- Visible wall height: 15.0 mm
- Wall thickness: 3.0 mm
- T-slot is open on the underside of the deck and only requires a ~5.2 mm bridge when printing.
- Male rails are discontinuous pads to reduce sliding friction and sensitivity to PETG warping.

### Required side-wall quantities
The same wall geometry is used on left and right; rotate it 180° around Z for the opposite side during assembly.
- `wall_half_print.stl`: **4 copies** total
- `wall_bridge_print.stl`: **6 copies** total

Per side the order is:
`118.125 + 236.25 + 236.25 + 236.25 + 118.125 = 945 mm`

Wall joints occur at the middle of deck plates, not at the deck seams.

## Deck quantities
- `deck_left.stl`: 1
- `deck_middle.stl`: 2
- `deck_right.stl`: 1

## Test parts
- `rail_fit_top.stl` + `rail_fit_wall_print.stl`: verify T-rail clearance before the full print.
- `functional_test_tile.stl`: one full 46 mm catcher field for water/hair testing.

## Recommended PETG starting settings
- 0.20 mm layer height
- 4–5 walls
- 5–6 top/bottom layers
- 25–35% infill for deck plates
- no supports intended
- print deck plates exactly as exported
- print wall STLs exactly as exported (`*_print` files already lie on their outer face)

## Parametric source
`build_v2.py` contains all main dimensions, clearances, hole/rib geometry and decomposition parameters at the top of the file.
