# Requirements review 0.5.4 — complete hydrography and an honest water gate

Status: **proposed, human approval required**

## Trigger

User inspection of revision 0.5.3 `digital-candidate-r4`: *"die letzte version hat
immer noch nicht alle gewässer korrekt abgebildet. der tegler see fehlt complett
und die havel fehlt zu einem nennenwerten teil. auf dem rechten stadtteil habe
ich gar nicht geschaut."*

## Measured state of revision 0.5.3 `digital-candidate-r4`

Measured on the exported `tool1-base` STLs, not on the build's own arrays. Water
is "open" where it is not inside the solid land cross-section.

| Mode | mapped water inside the panel | still solid | open |
| --- | ---: | ---: | ---: |
| `context_outline` | 8 516 mm² | 1 231 mm² | 85.5 % |
| `boundary_crop` | 5 838 mm² | 2 638 mm² | **54.8 %** |

Worst named bodies (`boundary_crop`, mm² still solid): Tegeler See 350.5,
Langer See 297.4, Großer Müggelsee 254.8, Seddinsee 238.5, Havel 205.9 + 121.0 +
77.1 + 32.5, Zeuthener See 129.1, Große Krampe 76.4 (0 % open),
Nieder Neuendorfer See 60.3 (0 %), Schlachtensee 45.3 (0 %),
Groß Glienicker See 34.3 (0 %), Heiligensee 34.8 (0 %), Jungfernsee 35.1 (0 %).

Tegeler See is open to **7.5 %** in `context_outline` and **18.3 %** in
`boundary_crop`, while the candidate's own `build-report.json` records
`tegeler_see_final_opening_area_mm2` 262.6 and 202.9 and status `PASS`.

The user's untested "right city half" is confirmed affected: Große Krampe,
Seddinsee, Langer See, Zeuthener See, Dämeritzsee and Großer Müggelsee all lose
water in `boundary_crop`.

## Requirements

- **R1** Every mapped water body must be cut through the panel. Only an exact
  functional support footprint or a logged topology bridge may interrupt water.
- **R2** The water regression gate must measure the aperture array that becomes
  geometry. A gate that runs before a later keep-out is a defect, not a report.
- **R3** A second, independent check must measure the **exported** artefact, so
  no future intermediate-array error can pass unseen.
- **R4** Named-water coverage must be verifiable against an authority
  independent of OpenStreetMap.
- **R5** The metriMade site marker must not be the reason a water body is
  missing.
- **R6** No change to the four-tool palette, the 600 × 400 mm format, the two
  display modes, the Z bands, the mount positions or the seam architecture.

## Out of scope

Panel size, city selection, palette, transit semantics, marker artwork, physical
print and every release gate.
