# Decision log

- `2026-08-26` — MVP audit: DrawerFit, NameForm and ShelfFit already have controlled parametric 3MF candidates; their remaining gates are slicer/physical and were deferred by the user.
- `2026-08-26` — Selected PORT-004 as the next actual geometry-changing item: common-printer derivative of the Modern Carbon Desk Organizer.
- `2026-08-26` — Chose a 210 × 190 × 173 mm stack with two identical drawers and a removable six-bin sorter.
- `2026-08-26` — Replaced full-surface 16-bit image relief with physically scaled procedural grooves; texture remains cosmetic.
- `2026-08-26` — Chose CadQuery B-Rep/STEP masters with direct manufacturing tessellation and no global decimation.
- `2026-08-26` — Physical print, drawer-cycle, anti-tip and appearance evidence remain human-owned and deferred.
- `2026-08-26` — Reduced the thin drawer-front plate's plan fillet from an impossible 6.0 mm to 1.2 mm; the housing/sorter 10 mm product radius and every interface remain unchanged.
- `2026-08-26` — Localized housing/sorter twill to centered badge fields after the full-side Boolean exceeded the 2 GiB peak-memory budget; nominal pitch, depth and wall reserve remain unchanged.
- `2026-08-26` — Reconciled the 190 mm overall depth: drawer front now occupies y=0..3.2, body y=3.2..185.1 and the remaining 2.5 mm is the controlled rear clearance to the housing wall.
- `2026-08-26` — Selected the 9.6 mm product twill pitch after the 4.8 mm full drawer badge exceeded the bounded OCCT build budget; 4.8 mm remains a coupon-only fine candidate.
- `2026-08-26` — Replaced the redundant centers of all three housing decks with controlled 12 mm perimeter frames/guide rails after the first full digital build estimated 1.47 kg PLA-equivalent solid volume. Outer silhouette and protected paths stay fixed.
- `2026-08-26` — Reduced drawer bottom to 2.0 mm and sorter bottom/outer/divider walls to 2.0/2.4/1.8 mm; the divider remains four nominal 0.45 mm paths wide before slicer-specific allocation.
- `2026-09-05` — Owner rejected draft.1 for coarse non-carbon appearance, open housing/sorter corners, straight drawer fronts and unconvincing fit quality.
- `2026-09-05` — Root cause confirmed: rectangular cavity cutters broke through rounded outer corners; the drawer fascia occupied the housing cavity and overlapped it by 23.42 mm³ at the old 0.6 mm preview inset; the scoop cutter was on the wrong side of the fascia; the texture coupon was horizontal despite claiming a vertical-wall test.
- `2026-09-05` — Revision 2.0.0-draft.2 uses rear-rounded housing cavities, matched rounded drawer/sorter pockets, an 8 mm XZ fascia radius, a proud y=-3.2..0 fascia with 5.7 mm rear reserve, a working scoop cut, and a true vertical-wall texture coupon.
- `2026-09-05` — Replaced the coarse crossed pattern with a 3.2 mm single-family directional tow cue; physical selection remains gated by 2.4/3.2/4.0 mm coupon fields.
- `2026-09-05` — Nine exact drawer-travel intersections and the seated sorter intersection are all 0.0 mm³; nominal 0.45 mm side clearance remains unqualified until the exact-process fit coupon passes.
