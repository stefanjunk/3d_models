# MM-ORG-001 — research on common drawer-system sizes

Research date: 2026-08-25  
Research status: primary-source review complete; sales-frequency evidence unavailable  
Selected first target: IKEA METOD/MAXIMERA, nominal 60 × 60 cm base cabinet

Design update 2026-08-25: requirements revision `0.2.0` keeps the dimensional conclusion but supersedes the earlier tool-specific/connector architecture. R1.6 is now a form reference only. The proposed implementation uses independent closed CadQuery trays with zero inter-module connectors by default and the minimum part count for the selected printer profile.

Design update 2026-08-26: requirements revision `0.3.0` retains the approved Kobra 3 Max profile and mixed four-tray layout, but reintroduces seam connectors. The minimum/largest-part result remains four approximately 256 × 245.5 mm rectangular trays: two halves cannot fit the assumed 416 × 416 mm usable bed because each straight half retains either the 512 mm width or the 491 mm depth. The R1.6 planar-jigsaw concept may be regenerated parametrically, but its documented physical non-fit prevents copying its dimensions without a new clearance coupon sweep.

**Active design rollback 2026-08-26:** at the user's explicit direction, revision `0.1.0-requirements` is active again. The implementation target is therefore the original common-220 nine-module tool organizer with one full-depth tool lane, removable comb, eighteen small-parts compartments and planar seam connectors. The 0.2.0/0.3.0 design updates above are retained as inactive history only.

## Executive conclusion

There is no current DIN or ISO standard that defines one interchangeable **usable internal drawer footprint** for a drop-in organizer. The standards found either coordinate kitchen-unit/appliance envelopes or define furniture safety and test methods. Drawer-side geometry, runners, backs, front clearances and usable bottom dimensions remain system-specific.

No audited public source was found that ranks installed drawer sizes by sales or household count. “Most common” therefore cannot be claimed as a measured market-share fact. The strongest evidence-backed first product target is the **600 mm nominal kitchen base-cabinet class**, implemented as one explicitly named system variant:

- IKEA sells METOD base cabinets and MAXIMERA drawers in 40, 60 and 80 cm nominal widths; its current German buying guide repeatedly uses those widths and includes 60 × 60 cm as the central cabinet class.
- IKEA publishes full-width UPPDATERA organizer combinations of 316 × 495 mm for a 40 cm drawer, 516 × 495 mm for a 60 cm drawer and 716 × 495 mm for an 80 cm drawer.
- Blum's professional AMBIA-LINE/ORGA-LINE documentation also treats 600 mm as a supported cabinet-width class, with drawer nominal lengths commonly spanning 450–650 mm. That corroborates the 600 mm class but does **not** make inserts interchangeable between Blum and IKEA.

The recommended first fixed variant is therefore a system-specific `MM-ORG-001 / METOD-MAXIMERA-60`, with a proposed organizer envelope of **512 × 491 × 50 mm**. This is 4 mm smaller in width and depth than IKEA's published 516 × 495 × 50 mm UPPDATERA combination, nominally leaving 2 mm clearance per side. Compatibility must still be proven in a real target drawer and must be limited to the tested system/revision.

## Evidence table

| Evidence | Published dimensions / scope | What it establishes | What it does not establish |
|---|---:|---|---|
| IKEA METOD German buying guide, July 2026 | base-cabinet families include 40 × 60, 60 × 60 and 80 × 60 cm | Current official system-width family | Unit sales or installed-base share |
| IKEA MAXIMERA low drawer, 40 × 60 | outer drawer assembly 364 × 542 × 78 mm; nominal cabinet 400 × 600 mm | Drawer family geometry and 60 cm depth class | Clear internal bottom footprint |
| IKEA MAXIMERA low drawer, 60 × 60 | outer drawer assembly 564 × 542 × 78 mm; nominal cabinet 600 × 600 mm | Selected nominal target system | Clear internal bottom footprint |
| IKEA MAXIMERA low drawer, 80 × 60 | outer drawer assembly 764 × 542 × 78 mm; nominal cabinet 800 × 600 mm | Wider family member | Clear internal bottom footprint |
| IKEA UPPDATERA, 40 cm drawer | 316 × 495 × 50 mm and explicitly stated to fit 40 cm MAXIMERA | Usable full-width accessory reference for 40 cm system | Universal 40 cm cabinet compatibility |
| IKEA UPPDATERA, 60 cm drawer | 516 × 495 × 50 mm; bamboo combination reaches 56 mm high | Usable full-width accessory reference for selected system | Exact clearance to every wall feature/revision |
| IKEA UPPDATERA, 80 cm drawer | 716 × 495 × 50 mm | Usable full-width accessory reference for 80 cm system | Universal 80 cm cabinet compatibility |
| Blum 2024/2025 catalogue | cabinet-width classes include 400, 450, 500, 550, 600, 800, 900, 1000, 1100, 1200 mm; drawer nominal lengths 270–650 mm depending on system | 600 mm is also a professional hardware-system class | A shared drop-in footprint with IKEA |
| DIN EN 1116:2018-03 | coordinating sizes for kitchen furniture and appliances | Kitchen modules are coordinated at cabinet/appliance level | Internal drawer dimensions |
| ISO 3055:2021 | height, width and depth coordination for non-custom domestic kitchens and appliance integration | International coordination scope | Internal drawer dimensions |
| DIN EN 14749:2022-07 | safety requirements and test methods for domestic/kitchen storage units and worktops | Relevant safety context | Organizer dimensions |
| ISO 7170:2021 | strength, durability and stability test methods for storage units | Relevant test-method context | Organizer dimensions or acceptance criteria |

## Size-family interpretation

The official IKEA organizer widths form a consistent family:

| Nominal drawer/cabinet width | Published full-width organizer | Proposed 2 mm-per-side product envelope | Portfolio decision |
|---:|---:|---:|---|
| 400 mm | 316 × 495 mm | 312 × 491 mm | future smaller fixed variant |
| 600 mm | 516 × 495 mm | **512 × 491 mm** | **first controlled variant** |
| 800 mm | 716 × 495 mm | 712 × 491 mm | future wide fixed variant; requires more modules |

This linear family is useful for later variants, but it is not a substitute for measurement. The 37 cm-deep MAXIMERA family is a separate shallow target and is outside this revision.

## Why 60 cm is selected first

The selection is an engineering/business inference, not a sales-frequency claim:

1. It sits between the supported 40 and 80 cm IKEA families and appears throughout the current METOD product architecture.
2. A complete official accessory envelope is published for the system, avoiding an unsafe inference from drawer exterior dimensions.
3. The 600 mm cabinet class also appears in a major non-IKEA hardware catalogue, so it is not an IKEA-only nominal convention.
4. It offers materially more personalization/storage value than the 40 cm target while requiring fewer modules and less print time than the 80 cm target.
5. A 3 × 3 segmentation keeps every proposed module below the business target of 220 × 220 × 250 mm.

Confidence:

- High: the published product dimensions and the absence of an internal-drawer dimension in the cited standard scopes.
- Medium: 600 mm is the best first nominal target.
- Low/unproven: 600 mm is the single most installed drawer width in Germany.

## Adaptation audit of the current R1.6 organizer

Source candidate:

`products/organization-storage/mm-org-001-drawerfit-modular/DRAFT-schubladen-organizer-R1.6-parametric-surfaces/schubladen-organizer`

Current envelope and architecture:

- drawer assumption: 230 × 360 × 80 mm;
- organizer envelope: 227 × 357 × 64 mm;
- four modules: driver-front, driver-back, hardware-front, hardware-back;
- one screwdriver lane plus a 2-column × 4-row hardware-bin field;
- 2.6 mm floor, 3.2 mm walls and planar jigsaw connectors;
- selectable plain, carbon, carbon-wave, micro-cast, walnut and steel surfaces.

The new envelope is approximately 2.26 times wider and 1.38 times deeper. Uniform geometric scaling is rejected because it would also scale wall thicknesses, fit clearances, connector clearance, finger geometry and texture feature sizes.

Required controlled changes after approval:

1. Fork R1.6 without overwriting it; rebuild the system-size envelope, functional grid and connector coordinates from parameters rather than uniformly scaling the legacy model.
2. Generate the fixed 3 × 3 / nine-module manufacturing grid for the common-220 profile.
3. Retain one full-depth screwdriver/hand-tool lane, one removable eight-slot comb and a 3 × 6 field of eighteen small-parts compartments.
4. Regenerate low-profile planar-jigsaw connectors from seam-relative parameters across the 3 × 3 topology.
5. Qualify connector and comb coupons before printing the nine full modules; never treat the R1.6 nominal `0.30 mm` connector clearance as proven fit.
6. Generate watermark placement per final tray rather than scaling legacy JuSt positions. The final physical metriMade revision must use `MM-WM-001-R1`: `metriMade.com` and `MM-ORG-001 · v<VERSION>`.
7. Validate plain connector fit, comb fit, drawer fit and joined-set stability first. Surface profiles can be reconsidered only after fit, flatness and protected-region checks pass.

## Fit and claim boundary

The release may say “designed and tested for [exact IKEA system/product revision]” only after an assembled print passes the real drawer. It must not say “DIN size”, “universal 60 cm”, “fits all METOD/MAXIMERA” or “fits all 600 mm cabinets” based on this desk research alone.

The measurement/fit coupon should verify:

- minimum clear flat floor width, depth and corner radius;
- front/back intrusions and side-wall taper at the intended organizer height;
- assembled maximum envelope;
- insertion/removal without tools or drawer damage;
- drawer closing, opening and loaded-cycle behaviour;
- connector flushness and no exposed snagging edges.

## Primary sources

- IKEA, [METOD buying guide, July 2026](https://www.ikea.com/de/de/files/pdf/cb/68/cb683dc0/bf_kaufhilfe_metod_07-2026_online.pdf)
- IKEA, [MAXIMERA low drawer 40 × 60 cm](https://www.ikea.com/de/de/p/maximera-schublade-niedrig-weiss-20319356/)
- IKEA, [MAXIMERA low drawer 60 × 60 cm](https://www.ikea.com/de/de/p/maximera-schublade-niedrig-weiss-70319354/)
- IKEA, [MAXIMERA low drawer 80 × 60 cm](https://www.ikea.com/de/de/p/maximera-schublade-niedrig-weiss-10319352/)
- IKEA, [UPPDATERA 316 × 495 × 50 mm for 40 cm MAXIMERA](https://www.ikea.com/de/de/p/uppdatera-besteckkasten-weiss-10460020/)
- IKEA, [UPPDATERA 516 × 495 × 50 mm combination](https://www.ikea.com/de/de/p/uppdatera-besteckkasten-gewuerzeinsatz-weiss-s79627353/)
- IKEA, [UPPDATERA 516 × 495 × 56 mm bamboo combination](https://www.ikea.com/de/de/p/uppdatera-besteckkasten-kasten-mit-messerfach-bambus-hell-s09611789/)
- IKEA, [UPPDATERA 716 × 495 × 50 mm combination](https://www.ikea.com/de/de/p/uppdatera-besteckkast-kast-kueutensil-gewueeins-weiss-s29626997/)
- Blum, [Catalogue and technical manual 2024/2025 — AMBIA-LINE](https://publications.blum.com/2024/catalogue/en/546/)
- DIN Media, [DIN EN 1116:2018-03](https://www.dinmedia.de/de/norm/din-en-1116/275325871)
- ISO, [ISO 3055:2021](https://www.iso.org/cms/%20render/live/en/sites/isoorg/contents/data/standard/07/38/73868.html)
- DIN Media, [DIN EN 14749:2022-07](https://www.dinmedia.de/de/norm/din-en-14749/347372014)
- ISO, [ISO 7170:2021](https://www.iso.org/standard/76864.html)
