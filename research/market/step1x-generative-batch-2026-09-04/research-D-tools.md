# Research D — 3D-printable hand tools, workshop aids, functional desk accessories
Compiled 2026-09-04 for metriMade (Germany, FDM/FFF). All figures below were read on a live page/API in this
session. Anything not confirmed is written UNVERIFIED with no substitute number.

> **Scope honesty note.** Two parallel research threads (German/EU DIY market data; official COTS
> manufacturer/standards dimension pages) did **not** return before this file was closed. Therefore
> **Section 2 contains almost no manufacturer-verified nominals** — the COTS numbers a CAD interface needs
> are marked UNVERIFIED and MUST be confirmed against a manufacturer or standards page before any
> dimension is cut in CAD. Likewise there is **no verified German/EU DIY market figure, no Etsy figure,
> no Google Trends observation and no Amazon best-seller observation** in this file. Do not treat the
> platform evidence below as a substitute for market sizing.

---

## SECTION 1 — SOURCE RECORDS

**ID:** S78
**Category:** Platform popularity — primary data (public API)
**Publisher:** Printables.com / Prusa Research (api.printables.com GraphQL endpoint)
**Title:** Printables public GraphQL API — platform model counter and per-model download/like/make statistics
**Source Date:** Live data, queried 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** Platform-wide counter `printsCount.printsCount` returned **1,385,663** published models. Wall/organization ecosystem models, exact values read: "Honeycomb storage wall" by RostaP (id 152592, published 2023-08-12) **280,480 downloads, 61,791 likes, 2,524 makes, 1,229,224 views**; "Skadis Mount Collection" by Printuin (id 147771, 2022-09-06) **40,207 downloads, 15,281 likes, 584 makes**; "Underware - The Ultimate Cable Management Solution" by Hands on Katie (id 941161, 2024-12-07) **25,762 downloads, 9,695 likes**; "openGrid - Wall/Desk mounting framework and ecosystem" by David D (id 1214361, 2025-10-20) **14,209 downloads, 1,129 likes**; "Gridfinity Rebuilt in OpenSCAD" by kennetek (id 274917) **11,968 downloads**; "Skadis Tool Mount Collection" by Jonas Pedrotti (id 57792) **11,571 downloads, 141 makes**; "Gridfinity OpenSCAD Model" by Jamie (id 174346) **10,601 downloads**; "GOEWS - Greatly Over Engineered Wall System" by MrExo3D (id 1090032, 2025-01-11) **3,542 downloads, 1,662 likes**. Desk accessories: "headphone stand · reDesk" by h3li0 (id 910680) **9,445 downloads, 2,588 likes**; "Hoodie Pen Holder – Sporty Desk Organizer" by Botany Chic (id 1538515, 2026-01-13) **15,864 downloads**; "Kumiko Pen Holder - Desk Organizer" by Meyui (id 1279939) **15,737 downloads**; "Desk Clamp Headphone Stand" by Siddharth S (id 1788319, 2026-07-22) **2,755 downloads, 945 likes**. Discrete hand-tool/bit items are an order of magnitude smaller: "Gridfinity 2x2 screwdriver hex bit holder stackable version" (id 403828) **4,421 downloads**; "Modular tool organizers - Mk2!" by Drew (id 297813) **2,326 downloads**; "Hex Bit Holder" by GUZ_prints (id 146076) **1,813 downloads**; "Deburring Tool" by Michal Fanta (id 414202) **1,598 downloads, 59 makes**; "Simple 1/4 in (6.35 mm) Hex Driver Bit Clip/Holder" (id 865058) **146 downloads**; "6.35mm Hex Bit Holder – Snap-Fit Organizer" (id 1710369, 2026-05-06) **11 downloads**.
**URL:** https://api.printables.com/graphql/ (queries `{print(id:"<id>"){name downloadCount likesCount makesCount displayCount datePublished}}` and `{printsCount{printsCount}}`); human-readable pages at https://www.printables.com/model/152592-honeycomb-storage-wall , https://www.printables.com/model/147771-skadis-mount-collection , https://www.printables.com/model/941161-underware-the-ultimate-cable-management-solution , https://www.printables.com/model/1214361-opengrid-walldesk-mounting-framework-and-ecosystem
**Used For:** Ranking wall/rail ecosystems far above standalone tools; sizing the desk-accessory opportunity; establishing that "6.35 mm" is the community-standard way to name the 1/4 in hex interface; all trend-signal sentences in Section 3.
**Note:** Primary. Website HTML at printables.com returns HTTP 403 to automated fetching; the public GraphQL API returns the same counters and was used instead. WebSearch snippets for several of these models quoted materially wrong figures (e.g. a snippet claimed 57k downloads for the Kumiko Pen Holder vs. the API's 15,737) — API values supersede.

---

**ID:** S79
**Category:** Platform popularity — primary data (public API)
**Publisher:** MakerWorld / Bambu Lab (makerworld.com design-service API)
**Title:** MakerWorld public design API — per-design download, print, like and collection counts
**Source Date:** Live data, queried 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** Cable management and wall systems dominate: "Underware – Ultimate Cable Management System (MB)" (id 545105, created 2024-07-17) **34,200 downloads, 11,910 prints, 15,731 likes, 54,797 collections**; "Underware 2.0 - Infinite Cable Management!" (id 783010, 2024-11-13) **29,621 downloads, 10,484 prints, 10,833 likes, 36,962 collections**; "openGrid - Wall/Desk mounting framework/ecosystem" (id 1179191, 2025-03-05) **20,698 downloads, 13,919 prints, 2,576 likes, 10,306 collections**. Tool holders and magnet-based aids: "Modular Wrench Holder" (id 44779, 2023-10-19) **9,604 downloads, 6,417 prints, 2,562 likes**; "Bambu MAGNETIC Tool Set Holder - Gridfinity" (id 696868, 2024-10-12) **5,668 downloads, 4,090 prints**; "Wall Mount Tool Organizer (with SKADIS variant)" (id 908825, 2024-12-24) **4,961 downloads, 3,446 prints, 9,305 collections**; "3D Printing Deburring Tool V2" (id 70149, 2023-11-21) **4,438 downloads, 3,690 prints, 1,375 likes**; "Magnet Insertion Tool v2" (id 647269, 2024-09-17) **3,410 downloads, 1,696 prints, 2,536 likes**; "6x3 mm Magnet Box" (id 230265) **87 downloads**. "Honeycomb Storage Wall (HSW), Wall-mounted Storage System" (id 1555114, 2025-06-27, licence **CC0**) **2,928 downloads, 1,238 prints, 2,199 collections**, and its own description states a single honeycomb panel consumes **approx. 77 g** of filament. Bit-specific holders are small: "1/4 Inch Hex Shank Bit Holder Wall Mountable" (id 455857) **588 downloads, 418 prints**; "Pocket Screwdriver Kit v2" (id 253704) **578 downloads, 330 prints**; "Screwdriver handle -1/4 hex bit holder" (id 252478) **152 downloads, 67 prints**; "Mini Screwdriver Handle for 1/4\" Hex Bits" (id 2115108, 2025-12-14) **76 downloads**.
**URL:** https://makerworld.com/api/v1/design-service/design/545105 (and /783010, /1179191, /44779, /696868, /908825, /70149, /647269, /1555114, /455857, /253704, /252478, /2115108); human-readable pages e.g. https://makerworld.com/en/models/545105-underware-ultimate-cable-management-system-mb , https://makerworld.com/en/models/1179191-opengrid-wall-desk-mounting-framework-ecosystem
**Used For:** Cross-platform confirmation that cable management + rail/wall ecosystems are the demand centre; evidence that magnet-retention aids print well; demonstrating that generic bit holders are a crowded low-traffic niche and need a differentiating ergonomic idea.
**Note:** Primary. `printCount` is MakerWorld's count of actual print jobs, a stronger intent signal than downloads.

---

**ID:** S80
**Category:** Platform / ecosystem behaviour data
**Publisher:** 3D Printing Industry (reporting Bambu Lab's own published statistics)
**Title:** Bambu Lab data highlights sustained 3D printing activity and creator growth on MakerWorld
**Source Date:** 2026-02-28
**Checked:** 2026-09-04
**Evidence Used:** Attributed to Bambu Lab's official WeChat channels for 2025: **83 %** of users continue downloading models and printing one year after buying a machine; combined print time exceeded **290 million hours** in the year; more than **30,000** users run printers over seven hours per day on average and more than **130,000** users print at least six hours per week. **280,000** creators uploaded models on MakerWorld China, averaging more than five designs per person, and **nearly 4,000 models have each been downloaded and printed more than 1,000 times**. Categories listed include storage tools, office items and printer accessories, with **household models the fastest-growing category during 2025, followed by hobby and DIY designs and then tool-related models**. Benchy held the top global print-volume position for five consecutive years. MakerLab reached **310,000** users generating **2.6 million** models (**>7,000/day**), of which the lithophane generator produced **~400,000** (roughly one in six).
**URL:** https://3dprintingindustry.com/news/bambu-lab-data-highlights-sustained-3d-printing-activity-and-creator-growth-on-makerworld-249474/
**Used For:** Demonstrating that DIY/tool categories are an explicitly named growth area on the largest FDM ecosystem, and that repeat printing behaviour (83 %, 290 M hours) supports a recurring-purchase digital-file business.
**Used For (limits):** SECONDARY (news article quoting a vendor's own marketing statistics). Figures describe **China-based users** of Bambu Lab's cloud; do not project onto Germany/EU.

---

**ID:** S81
**Category:** Platform contest / editorial signal
**Publisher:** Prusa Research (blog.prusa3d.com) — platform operator, primary
**Title:** Printables Awards 2025: Celebrating the Best in 3D Printable Design!
**Source Date:** 2026-02-26
**Checked:** 2026-09-04
**Evidence Used:** Printables' flagship annual awards run exactly three "Best Model" categories, of which the first is **"Practical & Functional Objects – Tools, holders, organizers, adapters, covers, etc."** (the others being Toys & Games and Decorations & Art). Prize pool read on the page: **2 × $10,000** (Designer of the Year, Model of the Year), **3 × Original Prusa XL (5-toolhead)** for category winners, **1 × Prusa CORE One L** and **2 × Prusa CORE One+** for randomly drawn voters. Nominations ran **2 December–15 December 2025**, voting **17 December 2025–12 January 2026**, winners announced **26 February 2026**; eligible models had to be published **1 November 2024–30 November 2025**, free and public; each user could nominate up to **5 models and 3 designers**. The page does **not** state total entry or vote counts — UNVERIFIED.
**URL:** https://blog.prusa3d.com/printables-awards-2025-celebrating-the-best-in-3d-printable-design_126519/
**Used For:** Evidence that "tools, holders, organizers" is a first-class, platform-promoted category rather than a niche — i.e. editorial as well as download support for this portfolio.

---

**ID:** S82
**Category:** Platform scale (operator statement)
**Publisher:** Prusa Research (blog.prusa3d.com) — primary
**Title:** The Great Recap of 2024 in Prusa Research
**Source Date:** 2025-02-12
**Checked:** 2026-09-04
**Evidence Used:** Prusa states of Printables.com: "We're pretty much hitting **one million uploaded models** now," and that the company "gave out **over 8000 vouchers** last year" as community rewards, while "running **dozens of community contests**." The post gives no download totals, no registered-user count and no per-category breakdown — UNVERIFIED.
**URL:** https://blog.prusa3d.com/the-great-recap-of-2024-in-prusa-research_110103/
**Used For:** Growth baseline for the platform: ~1 M models at the start of 2025 versus **1,385,663** measured on 2026-09-04 [S78] — i.e. roughly +385k models in ~19 months, which quantifies how fast the free-model supply side is expanding and therefore how much differentiation a paid file needs.
**Note:** Primary but the headline figure is approximate wording ("pretty much hitting"), not an exact audited count.

---

**ID:** S83
**Category:** Ecosystem interface specification (primary, ecosystem owner)
**Publisher:** MultiBuild (docs.multibuild.io) — the Multiboard/MultiBuild project's own documentation
**Title:** MultiBuild Core Parts — Complete Guide to Every Component
**Source Date:** Undated page, read 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** The system's unit grid is stated as **MU (Multi Unit) = based on 25 mm sizing** and **CU (Cell Unit) = based on 50 mm sizing**, with the conversion **2×2 MU = 1×1 CU**. Stacking MultiBin shells increases height by **50 mm (1 CU)**. Two connector thicknesses exist: a Regular Multipoint and a **Lite Multipoint, which is "1 mm thinner than a Regular Multipoint."** A worked example for an 8×8 tile reads **3 h 16 m print time, 80.55 g material, $1.6 cost** on a Bambu Lab X1C in Bambu PLA Basic. The page does **not** give tile thickness, the tile hole thread designation, snap dimensions, screw sizes or magnet sizes — all UNVERIFIED.
**URL:** https://docs.multibuild.io/beginner-section/core-parts-documentation
**Used For:** The only manufacturer/owner-verified rail-clip pitch in this file (25 mm MU / 50 mm CU) — used as the citable mounting nominal for every wall-mounted concept in Section 3.
**Note:** multiboard.io now 301-redirects to multibuild.io; multibuild.io root returns HTTP 403 to automated fetching, the docs subdomain does not.

---

**ID:** S84
**Category:** Developer-ecosystem traction (primary API)
**Publisher:** GitHub (api.github.com) — repository `kennetek/gridfinity-rebuilt-openscad`
**Title:** GitHub REST API repository metrics for the leading parametric Gridfinity generator
**Source Date:** Live data, queried 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** The repository reports **2,245 stars** and **326 forks**, created **2022-07-31**, with the most recent push **2025-08-31**. The same project's Printables listing carries **11,968 downloads** [S78]. The parallel "Gridfinity OpenSCAD Model" listing carries **10,601 downloads** [S78].
**URL:** https://api.github.com/repos/kennetek/gridfinity-rebuilt-openscad (page: https://github.com/kennetek/gridfinity-rebuilt-openscad)
**Used For:** Showing Gridfinity is sustained by *parametric generators*, not fixed STLs — i.e. a fixed-geometry Gridfinity bin has no commercial headroom, which is why Section 3 avoids plain bins and sells ergonomics instead.
**Note:** The 42 × 42 × 7 mm Gridfinity pitch and 41.5 mm bin footprint appeared only in WebSearch snippets this session; the official specification page was **not** fetched — see Section 2, UNVERIFIED.

---

**ID:** S85
**Category:** Community de-facto interface conventions (derived from primary platform data)
**Publisher:** Printables.com and MakerWorld (model titles/descriptions confirmed via the APIs in S78/S79)
**Title:** De-facto COTS sizes named in the titles of verified, live tool-model listings
**Source Date:** Listings dated 2023-03-06 to 2026-05-06; read 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** The 1/4 in hex bit interface is consistently expressed as **6.35 mm** in live listing titles verified via API: Printables id 865058 "Simple 1/4 in (**6.35 mm**) Hex Driver Bit Clip/Holder" and Printables id 1710369 "**6.35mm** Hex Bit Holder – Snap-Fit Organizer"; MakerWorld id 455857 "**1/4 Inch** Hex Shank Bit Holder Wall Mountable" and id 252478 "Screwdriver handle -**1/4 hex** bit holder". The de-facto default neodymium disc for printed pockets is **6 × 3 mm**: MakerWorld id 230265 is titled "**6x3 mm** Magnet Box" (87 downloads) and MakerWorld id 647269 "Magnet Insertion Tool v2" (3,410 downloads, 2,536 likes) is a dedicated magnet-seating aid. Search snippets (NOT confirmed on the primary listing pages) additionally indicated Printables id 297813 "Modular tool organizers - Mk2!" is built for **12 × 5 mm** discs, and that id 647269 covers **5×1, 6×2, 8×2 and 6×3 mm** — treat those two as snippet-derived.
**URL:** https://www.printables.com/model/865058-simple-14-in-635-mm-hex-driver-bit-clipholder , https://www.printables.com/model/1710369-635mm-hex-bit-holder-snap-fit-organizer , https://makerworld.com/en/models/230265-6x3-mm-magnet-box , https://makerworld.com/en/models/647269-magnet-insertion-tool-v2 (all counters re-verified via the S78/S79 API endpoints)
**Used For:** Choosing 6.35 mm and 6 × 3 mm as the portfolio's default interface targets, on the grounds that they are what the installed base already buys and prints.
**Note:** This is evidence of **community convention only**. It is **NOT** a manufacturer or standards figure. The DIN 3126 / ISO 1173 form E 6.3 designation, the official across-flats tolerance, the detent-groove position, and any magnet supplier's catalogue tolerance and holding force are **UNVERIFIED** in this session.

---

## SECTION 2 — CITABLE INTERFACE NOMINALS

**Verified in this session (safe to cite as read):**

| Interface | Exact figure read | Source | Confidence |
|---|---|---|---|
| MultiBuild / Multiboard grid unit | **MU = 25 mm**; **CU = 50 mm**; **2×2 MU = 1×1 CU** | S83 | Primary, ecosystem owner's own docs |
| MultiBuild bin stack increment | **+50 mm (1 CU)** per stacked shell | S83 | Primary |
| MultiBuild connector variant | Lite Multipoint is **1 mm thinner** than Regular Multipoint | S83 | Primary (absolute thickness UNVERIFIED) |
| HSW honeycomb panel material budget | **approx. 77 g** filament per panel | S79 | Primary (designer's own listing) |
| HSW licence | **CC0** (MakerWorld id 1555114) | S79 | Primary — commercially reusable |
| MultiBuild 8×8 tile print budget | **3 h 16 m, 80.55 g** (X1C, Bambu PLA Basic) | S83 | Primary |
| 1/4 in hex bit shank, community nominal | **6.35 mm** across flats | S85 | Community convention, NOT a spec |
| Default neodymium disc for printed pockets | **6 × 3 mm** (dia × height) | S85 | Community convention, NOT a supplier catalogue |
| Secondary magnet sizes seen in listings | **5 × 1, 6 × 2, 8 × 2, 12 × 5 mm** | S85 | Snippet-derived only — weakest tier |

**UNVERIFIED — no figure confirmed on a manufacturer or standards page in this session. Do NOT cut CAD to these without checking first:**

| Interface | Status |
|---|---|
| 1/4" hex bit shank official across-flats + tolerance; **DIN 3126 / ISO 1173 form E 6.3 and C 6.3** designations; standard bit lengths (25 / 50 mm); detent-groove position | **UNVERIFIED** — no Wera/Wiha/Bosch/ISO OBP page fetched |
| Neodymium disc magnets — supplier catalogue diameter/height tolerance and stated adhesive force (supermagnete.de, K&J) for 6×3, 10×2, 8×3, 5×2 mm | **UNVERIFIED** — no supplier page fetched |
| M3 / M4 heat-set insert outer diameter, length and **recommended installation hole diameter** (Ruthex, Böllhoff) | **UNVERIFIED** — this is the single most load-bearing missing number for Section 3 |
| Stanley-type trapezoid utility blade length × width × thickness | **UNVERIFIED** |
| Deburring-tool blade shaft diameter (3.2 mm appeared in a search snippet only) | **UNVERIFIED** |
| 608-2RS and 6001-2RS bore × OD × width (SKF/Schaeffler/NSK) | **UNVERIFIED** |
| Hex-key across-flats series; **ISO 2936 / DIN 911** | **UNVERIFIED** |
| Wood-pencil hex across-flats; carpenter pencil; Sharpie/edding marker barrel diameter | **UNVERIFIED** |
| Sandpaper sheet sizes (full / ¼ / ⅓ sheet) and 125 / 150 mm disc hole patterns (3M, Mirka, Klingspor) | **UNVERIFIED** |
| ISO metric coarse pitch for M3/M4/M5/M6/M8 (ISO 261 / ISO 262); M6 threaded-rod OD | **UNVERIFIED** |
| Steel-rule and combination-square blade widths | **UNVERIFIED** |
| **Gridfinity 42 × 42 × 7 mm pitch and 41.5 mm bin footprint** | **UNVERIFIED** — search snippets only; official spec page not fetched |
| **openGrid 28 mm grid, 6.8 mm full-board / ~4 mm lite-board thickness** | **UNVERIFIED** — search snippets only; opengrid.world page not fetched |
| German/EU DIY market size (BHB, Destatis, EDRA/GHIN); hand-tool market growth; home-office share; Etsy trend figures; Google Trends direction; Amazon best-seller ranks | **ALL UNVERIFIED** — not retrieved before close |

---

## SECTION 3 — PRODUCT CONCEPTS (16)

Workflow assumption for all 16: the **organic ergonomic shell** is generated as a single isolated product
image with AI imagegen and converted to a mesh with **Step1X-3D**; the **exact functional interface** (bit
socket, magnet pocket, blade slot, insert boss, rail clip) is then added parametrically in CAD and the
mesh is booleaned/registered to it. All stated sizes are **proposed design envelopes**, not measured
figures, and all fit inside 220 × 220 × 250 mm.

### 1. PalmDriver Stubby
- **Description:** Fist-filling organic stubby driver body that takes 1/4 in hex bits for confined-space, low-torque work.
- **Customer job:** Drive screws where a full-length screwdriver will not fit, without losing grip comfort.
- **Trend signal:** Bit-driver handles exist but are tiny listings — MakerWorld "Screwdriver handle -1/4 hex bit holder" 152 downloads, "Mini Screwdriver Handle for 1/4\" Hex Bits" 76 downloads [S79]; the interface is universally written 6.35 mm [S85], so the gap is ergonomics, not fit.
- **Target segment:** Hobby electronics, furniture assembly, bike/e-scooter owners.
- **COTS interface:** 1/4 in hex bit shank, community nominal **6.35 mm** across flats [S85]. Official DIN 3126 / ISO 1173 E 6.3 tolerance **UNVERIFIED**.
- **Size (L×W×H):** 70 × 58 × 52 mm
- **Risk/limit:** Hand tool only, low torque. Printed hex socket will round out under impact or breaker-bar loads; specify a steel bit-holder insert or a captive nut if torque claims are ever made. No power-tool use.

### 2. BitBloom Dock
- **Description:** Lobed, petal-like desktop bit dock whose organic pockets each hold a 1/4 in bit upright over a magnet.
- **Customer job:** Keep the ten bits you actually use visible and one-handed reachable on the bench.
- **Trend signal:** Magnet-retained bit storage outperforms plain racks — MakerWorld "Bambu MAGNETIC Tool Set Holder" 5,668 downloads / 4,090 prints [S79] vs. Printables "Hex Bit Holder" 1,813 downloads [S78]; 6×3 mm is the de-facto disc [S85].
- **Target segment:** Desk/bench makers, 3D-printer owners, repair hobbyists.
- **COTS interface:** 6.35 mm hex bit shank [S85] + **6 × 3 mm** neodymium disc pockets [S85]. Supplier tolerance and holding force **UNVERIFIED**.
- **Size (L×W×H):** 118 × 112 × 38 mm
- **Risk/limit:** Magnet pocket depth must be set from a verified supplier tolerance before release; press-fit-only (no adhesive claim). Not a child-safe product — loose small magnets are an ingestion hazard and need explicit warning.

### 3. TwinKnob Handscrew
- **Description:** Wooden-handscrew-style hand clamp with two sculpted organic palm knobs running on a metric threaded rod.
- **Customer job:** Apply gentle, controllable clamping pressure to glue-ups and repairs without marring the workpiece.
- **Trend signal:** Only category-level evidence — printed clamps and jigs sit in the platform-promoted "Practical & Functional Objects – Tools, holders, organizers" award category [S81]; no verified download figure for a printed handscrew clamp.
- **Target segment:** Woodworking hobbyists, model makers, repair cafés.
- **COTS interface:** M6 threaded rod + M6 hex nut captured in the knob. **Pitch UNVERIFIED** (ISO 261/262 not fetched); nut across-flats **UNVERIFIED**.
- **Size (L×W×H):** 190 × 60 × 45 mm
- **Risk/limit:** Hand tool only; low clamping force. Printed threads creep under sustained load — the load path must run through the steel rod and a metal nut, never printed thread. No structural or load-bearing claim.

### 4. EdgeGlide Deburr Grip
- **Description:** Teardrop palm grip that houses a standard rotating deburring blade for cleaning printed and machined edges.
- **Customer job:** Knock the sharp brim edge off a fresh print comfortably, without a pen-thin handle cramping the hand.
- **Trend signal:** Deburring is a proven printed-tool niche — MakerWorld "3D Printing Deburring Tool V2" 4,438 downloads / 3,690 prints / 1,375 likes [S79] and Printables "Deburring Tool" 1,598 downloads with 59 makes [S78].
- **Target segment:** FDM printer owners (self-referential, high-conversion audience), metalworking hobbyists.
- **COTS interface:** Standard deburring blade shaft bore. Nominal **UNVERIFIED** (a 3.2 mm shaft appeared in a search snippet only and was not confirmed).
- **Size (L×W×H):** 95 × 42 × 36 mm
- **Risk/limit:** Blade is a sharp COTS part — **no cutting-safety claim**; ship with a printed blade cap and a warning. Bore must be verified against a purchased blade before release.

### 5. OffsetSaddle Marking Guide
- **Description:** Organic hand-saddle that rides a board edge and holds a pencil at a repeatable parametric offset.
- **Customer job:** Scribe a parallel line down a board edge freehand-fast but repeatably.
- **Trend signal:** Category-level only — marking aids are thin on the platforms (Printables "Streichmaß / Making Gauge" 286 downloads, read 2026-09-04) [S78], so this is an underserved slot rather than a proven one.
- **Target segment:** Woodworking and DIY renovation, German Heimwerker.
- **COTS interface:** Standard hexagonal wood pencil across-flats and standard carpenter pencil. Both **UNVERIFIED** (no Faber-Castell/Staedtler page fetched).
- **Size (L×W×H):** 105 × 70 × 40 mm
- **Risk/limit:** Accuracy limited by print tolerance and hand pressure; **not a precision measuring instrument** — no accuracy specification. Pencil clamp must be a screw or insert, not a printed snap that relaxes.

### 6. SandShell Quarter-Block
- **Description:** Organic hand-conforming sanding block with a parametric cam that tensions a quarter sheet of abrasive.
- **Customer job:** Sand flat surfaces comfortably and change paper in seconds without adhesive.
- **Trend signal:** Category-level only — sanding/finishing aids fall inside the platform-promoted "Practical & Functional Objects" award category [S81]; no verified download figure for a printed sanding block.
- **Target segment:** Woodworking, model painting, filler/drywall DIY.
- **COTS interface:** Quarter-sheet abrasive paper. Sheet nominal **UNVERIFIED** (no 3M/Mirka/Klingspor page fetched) — this concept **cannot be dimensioned** until that is confirmed.
- **Size (L×W×H):** 120 × 75 × 55 mm
- **Risk/limit:** Whole product geometry is gated on the unverified sheet size; do not start CAD first. Hand sanding only, no power-tool mounting. PLA will soften under aggressive friction heat — specify PETG or ASA.

### 7. HexFan Key Rack
- **Description:** Fan-spread organic desk rack that presents a full metric hex-key set at a raked angle, each key in a sized slot.
- **Customer job:** Grab the right Allen key first time instead of fanning a folding set.
- **Trend signal:** Sorted-by-size tool presentation is a validated pattern — MakerWorld "Modular Wrench Holder" 9,604 downloads / 6,417 prints [S79] and Printables "Modular tool organizers - Mk2!" 2,326 downloads [S78].
- **Target segment:** Bike workshops, 3D-printer owners, IKEA-heavy households.
- **COTS interface:** Metric hex-key across-flats series (ISO 2936 / DIN 911). Series values **UNVERIFIED** — slot widths cannot be set until a dimension table is confirmed.
- **Size (L×W×H):** 150 × 90 × 65 mm
- **Risk/limit:** Fit is per-brand; publish as a parametric file with a printable test coupon rather than a fixed STL. Slot-width tolerance is the whole product — a 0.2 mm error makes it useless.

### 8. WallPebble Magnet Puck
- **Description:** River-pebble-shaped holder with a magnet face on one side and a parametric rail clip on the other, so it mounts to a printed tool wall or a steel surface.
- **Customer job:** Park a screwdriver, scissors or scraper on the wall without a bespoke holder per tool.
- **Trend signal:** Wall/rail systems are the strongest datapoint in this whole study — Printables "Honeycomb storage wall" **280,480 downloads, 61,791 likes, 2,524 makes** [S78]; magnet holders print well [S79].
- **Target segment:** Garage/workshop owners, printer-room organizers.
- **COTS interface:** MultiBuild/Multiboard rail pitch **MU = 25 mm, CU = 50 mm** [S83] + **6 × 3 mm** neodymium discs [S85].
- **Size (L×W×H):** 62 × 48 × 34 mm
- **Risk/limit:** Magnet holding force **UNVERIFIED** — publish a mass limit only after bench testing, never a calculated figure. Light hand tools only; not for anything that hurts when it falls.

### 9. CableWave Desk Spine
- **Description:** Organic wave-form under-desk cable raceway with parametric insert bosses and a snap lid.
- **Customer job:** Get the desk cable nest off the floor in one continuous run that looks intentional.
- **Trend signal:** The single most-downloaded functional family found on MakerWorld — "Underware – Ultimate Cable Management System (MB)" **34,200 downloads, 11,910 prints, 54,797 collections** and Underware 2.0 **29,621 downloads**; Printables Underware **25,762 downloads** [S78][S79].
- **Target segment:** Home-office and desk-setup buyers.
- **COTS interface:** M4 heat-set insert boss + wood screw. **M4 insert OD/length and recommended hole diameter UNVERIFIED** (no Ruthex/Böllhoff page fetched).
- **Size (L×W×H):** 210 × 60 × 45 mm per module, tiling
- **Risk/invalid:** **Direct competition with a free CC-licensed incumbent at 34k downloads** — this must sell on form and finish, not function, or not at all. No electrical-safety or fire-rating claim; state PLA is unsuitable near heat sources.

### 10. LedgeHook Headphone Perch
- **Description:** Organic cantilever perch that clamps a desk edge or monitor-shelf lip and cradles a headband on a broad saddle.
- **Customer job:** Store headphones without drilling the desk or deforming the headband pad.
- **Trend signal:** Desk headphone stands are a live paid-adjacent category — Printables "headphone stand · reDesk" **9,445 downloads, 2,588 likes** and "Desk Clamp Headphone Stand" **2,755 downloads, 945 likes** within weeks of a 2026-07-22 publish [S78].
- **Target segment:** Home-office, gaming and streaming desks.
- **COTS interface:** M4 heat-set insert + M4 thumbscrew for the clamp. **Insert and thumbscrew nominals UNVERIFIED.**
- **Size (L×W×H):** 150 × 95 × 130 mm
- **Risk/limit:** Clamp jaw must not mark a veneer or glass desk — needs a TPU or felt pad. Cantilever creep in PLA over months; specify PETG. Desk-thickness range must be published.

### 11. ScoreGrip Marking Knife
- **Description:** Organic finger-indexed grip that captures a standard trapezoid utility blade in a fixed, shallow-projection scoring slot.
- **Customer job:** Score a crisp knife line for joinery or cut card and veneer with full control.
- **Trend signal:** Category-level only — cutting and marking aids sit in the platform's promoted "Practical & Functional Objects" award category [S81]; no verified download figure for a printed blade holder was found.
- **Target segment:** Woodworkers, model makers, bookbinders.
- **COTS interface:** Stanley-type trapezoid utility blade. Length × width × **thickness all UNVERIFIED** — the blade slot cannot be dimensioned yet.
- **Size (L×W×H):** 130 × 32 × 26 mm
- **Risk/limit:** **Highest-liability concept in the set.** Sharp COTS blade in a printed body: make **no cutting-safety, no retention-strength and no guard claim**; blade must be mechanically screwed, never friction-held; ship a cap and a written warning. Consider dropping if EU product-safety review is not resourced.

### 12. SpinHub Tape Dispenser
- **Description:** Organic sculpted desk hub that runs a tape or filament-sample roll on a real ball bearing, with a parametric tear edge.
- **Customer job:** One-handed tape pull that does not skate across the desk.
- **Trend signal:** Category-level only — desk organizers convert well on Printables ("Hoodie Pen Holder – Sporty Desk Organizer" **15,864 downloads**; "Kumiko Pen Holder" **15,737**) [S78], but no verified figure for a printed bearing tape dispenser.
- **Target segment:** Home office, craft, small e-commerce packers.
- **COTS interface:** **608-2RS** ball bearing seat. Bore × OD × width **UNVERIFIED** (no SKF/Schaeffler/NSK page fetched).
- **Size (L×W×H):** 120 × 100 × 95 mm
- **Risk/limit:** Needs mass (infill or a ballast pocket) or it slides; bearing press-fit tolerance is the whole mechanism and is currently unspecified. No metal tear blade unless a sharp-edge warning is added.

### 13. LoopWrench Finger Turner
- **Description:** Closed organic finger-loop that grips a 1/4 in hex bit transversely for turning fasteners in tight, awkward spaces.
- **Customer job:** Turn a screw where there is no room to swing a handle, using finger strength through a comfortable loop.
- **Trend signal:** Bit-tool listings on MakerWorld are numerous but individually small (152–588 downloads across four verified 1/4 in bit-holder listings) [S79], while the 6.35 mm interface is universal [S85] — a differentiated form has room.
- **Target segment:** Automotive and appliance repair, electronics service.
- **COTS interface:** 1/4 in hex bit shank, community nominal **6.35 mm** [S85]; official tolerance **UNVERIFIED**.
- **Size (L×W×H):** 82 × 62 × 20 mm
- **Risk/limit:** Hand tool only; the loop is a leverage multiplier, so the printed hex socket is the failure point — steel insert strongly advised. No torque figure may be published without testing.

### 14. ShelfLedge Pen & Phone Ledge
- **Description:** Organic ledge that hooks over a monitor-riser or shelf edge, angling pens into sculpted wells with a magnet strip for steel tools.
- **Customer job:** Reclaim desk surface by moving pens and phone onto otherwise dead shelf-edge space.
- **Trend signal:** Desk-accessory demand is verified (Printables pen holders at **15,864** and **15,737 downloads**) [S78]; monitor-shelf-specific variants were not found with a verified count, so this is an adjacency bet.
- **Target segment:** Home-office and dual-monitor desk setups.
- **COTS interface:** **6 × 3 mm** neodymium discs [S85]; pen/marker barrel diameters **UNVERIFIED** (no Staedtler/edding page fetched).
- **Size (L×W×H):** 180 × 85 × 70 mm
- **Risk/limit:** Shelf-thickness range must be published; overhanging load can tip a light riser. Pen well diameters are unspecified until barrel nominals are confirmed. Explicitly not a phone charger or dock.

### 15. DepthThumb Drill Collar
- **Description:** Organic thumb-and-forefinger collar that clamps a drill bit as an adjustable depth stop.
- **Customer job:** Drill a repeatable depth without tape flags or a drill press.
- **Trend signal:** Category-level only — drilling jigs and aids fall inside the platform-promoted "Practical & Functional Objects – Tools, holders, organizers, adapters" award category [S81]; no verified download figure.
- **Target segment:** DIY renovation, furniture assembly, German Heimwerker.
- **COTS interface:** M3 heat-set insert + M3 grub/set screw clamping onto the bit shank. **M3 insert OD, length and recommended hole diameter UNVERIFIED**; ISO metric M3 pitch **UNVERIFIED**.
- **Size (L×W×H):** 34 × 34 × 26 mm
- **Risk/limit:** Rotating-tool accessory — **highest functional risk in the set.** A printed collar can slip or be thrown; it must clamp via a metal screw on a flat, must not be marketed for hammer drilling or high RPM, and needs spin-off testing. No accuracy claim.

### 16. PinchPour Parts Dish
- **Description:** Organic shell-shaped parts dish with a magnet base to sit on steel and a pinched pour spout to decant screws back into a bag.
- **Customer job:** Catch disassembly hardware where you are working, then pour it back without spilling.
- **Trend signal:** Bench organization is the top named growth area on the largest FDM ecosystem — DIY and tool-related models were the fastest growers after household in Bambu Lab's 2025 data [S80]; magnet-based bench holders print well [S79].
- **Target segment:** Automotive/appliance repair, electronics benches, e-bike service.
- **COTS interface:** **6 × 3 mm** neodymium discs in the base [S85]; larger 10 × 2 mm option **UNVERIFIED** (no supplier catalogue fetched).
- **Size (L×W×H):** 130 × 110 × 34 mm
- **Risk/limit:** Must be visibly distinct from a plain Gridfinity bin — the pour spout and magnet base are the whole differentiator. Magnets near a running engine bay or electronics are a hazard: warn about magnetic media and pacemakers. No holding-force claim until tested.

---

## OPEN ITEMS BEFORE ANY CAD WORK
1. **Blocking:** M3/M4 heat-set insert recommended hole diameters (gates concepts 9, 10, 15).
2. **Blocking:** abrasive sheet sizes (gates concept 6); trapezoid blade dimensions (gates concept 11); 608 bearing dimensions (gates concept 12); hex-key series (gates concept 7).
3. **Blocking:** 1/4 in hex official across-flats + tolerance per DIN 3126 / ISO 1173 E 6.3 (gates concepts 1, 2, 13) — 6.35 mm is currently only a community convention [S85].
4. **Blocking:** neodymium 6 × 3 mm supplier tolerance and holding force (gates concepts 2, 8, 14, 16).
5. **Commercial:** no German/EU DIY market figure, no Etsy figure, no Google Trends observation and no Amazon best-seller observation was verified — market sizing for this portfolio is **entirely unevidenced** in this file.
6. **Competitive:** concept 9 competes directly with a free 34,200-download incumbent [S79]; validate willingness-to-pay before investing.
