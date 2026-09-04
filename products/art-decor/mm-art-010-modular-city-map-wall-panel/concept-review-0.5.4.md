# Concept review 0.5.4 — visible changes of the hydrography correction

Status: **proposed, human approval required**

The map language of concept v07 is unchanged: Oak land, Mint Green middle
relief, Midnight streets, Sky Blue S-/U-Bahn plus context boundary and site
marker, and every mapped water cut through the panel. Revision 0.5.4 changes
what is actually *visible* in three places.

## 1. The waters that were missing are now open

| | revision 0.5.3, measured on the exported STL | revision 0.5.4, raster simulation |
| --- | ---: | ---: |
| `context_outline`, all mapped water open | 85.5 % | 84.5 % |
| `boundary_crop`, all mapped water open | **54.8 %** | **75.1 %** |
| Tegeler See, `context_outline` | **7.5 %** | 93.7 % |
| Tegeler See, `boundary_crop` | **18.3 %** | 95.4 % |
| Havel corridor, `context_outline` | — | 98.1 % |
| Havel corridor, `boundary_crop` | — | 89.6 % |

`context_outline` moves little in the aggregate because revision 0.5.4 also maps
more water (10 488 mm² instead of 9 445 mm², from the official Berlin
Gewässerkarte union). The named bodies improve throughout, most visibly Tegeler
See, Schlachtensee and Groß-Glienicker See, which were entirely closed before.

## 2. The metriMade marker moves 27 mm east

The marker keeps its approved 54.0 × 57.18 mm size, its 0.6 mm tool-4 relief and
the frozen address Sterkrader Straße 24. Only the **anchor** changes: the address
point is now the artwork's **west edge** instead of its centre.

Centred on the address, 248 mm² of the logo silhouette lay directly on Tegeler
See, whose whole mapped area is 279 mm² (`context_outline`) and 429 mm²
(`boundary_crop`) — no clearance value could have freed the lake. The address
lies 678 m east of the shore, so a west-edge anchor is the smallest displacement
that keeps size, address and an open lake at the same time.

Resulting marker centre: 231.06 / 283.52 mm in `boundary_crop`, 249.63 / 267.35 mm
in `context_outline`.

**This needs an explicit decision:** the east shift reduces the clearance to the
centre seam to 41.94 mm (`boundary_crop`) and 23.37 mm (`context_outline`). The
approved parameter is 50.0 mm. The marker still lies wholly inside the left half
and never touches the seam, so the functional requirement holds; the cosmetic
margin is proposed to drop to 20.0 mm.

## 3. The map reaches slightly closer to the panel edge

The protected outline ligament goes from 5.0 mm to 2.0 mm, so water that meets
the panel outline — above all the Havel along the western city border — is
visible again. The rim keeps a continuous 2.0 × 3.0 mm section.

## 4. The east half opens more area than the old guard allowed

The `boundary_crop` right half now opens 12.97 % of its body, against an
inherited 12 % guard. That guard is raised to 15 % — see the decomposition
review; it is a digital heuristic, not a measured strength limit, and the
physical handling and proof-load gates stay open and now explicitly cover it.

## What does not change

Format, both display modes, the four-tool palette and Z bands, street and
transit semantics, mount and connector positions, the marker artwork, and every
physical, appearance and release gate.

## Known residual, by design

Four `boundary_crop` wall-mount footprints and the right title bar sit on top of
water: Schlachtensee (0 %), Langer See (54 %), Große Krampe (46 %),
Nieder-Neuendorfer See (5 %), Tegeler Fließ (60 %), Zeuthener See (20 %). A
mount footprint legitimately keeps its water closed. Recovering roughly 630 mm²
would require relocating approved mount positions and is proposed as a separate
phase, not smuggled into this correction.
