# Research C — 3D-printable toys, fidgets, puzzles, kinetic desk objects
Brand: metriMade (Germany, FDM/FFF). Envelope 220 x 220 x 250 mm. All research checked 2026-09-04.

**Access note (honesty):** MakerWorld, Printables web UI, Thingiverse and Thangs all served Cloudflare/403 challenges to
automated fetches this session. Printables per-model counts below were read from Printables' **own public GraphQL API**
(`api.printables.com/graphql/`, query `searchPrints2`), which is primary platform data. **No MakerWorld per-model download
figure could be verified** — figures appearing in search snippets (e.g. "Fidget Cube Toy: Angled 172.1k downloads",
"My 10 star fidget design 116.4k") are **UNVERIFIED**. EUR-Lex itself returned HTTP 202/empty bodies repeatedly, so the
**article-level** text of the new Toy Safety Regulation was **not read**; regulatory facts below come from two official
European Commission pages instead.

---

## SECTION 1 — SOURCE RECORDS

ID: S70
Category: Platform popularity (primary)
Publisher: Printables / Prusa Research (public GraphQL API, api.printables.com)
Title: Printables `searchPrints2` API — live download and like counts for fidget models
Source Date: live data, queried 2026-09-04
Checked: 2026-09-04
Evidence Used: Query "fidget" returned, with exact live counts: "Yet Another Fidget Infinity Cube v2" (id 928) 155,845 downloads / 16,525 likes; "Spiral cone fidget toy" (927393) 122,166 / 6,279; "Print-In-Place Fidget Clicker" (922541) 118,213 / 12,117; "OTF Fidget Knife - only 3 Parts" (863424) 93,287 / 10,580; "fidget star" (161631) 59,521 / 5,458; "Dragon Egg Twist Fidget" (1616812) 56,665 / 3,772; "Joy Fidget" (276901) 46,019 / 7,855; "Fidget Clicking Wheel 2.0" (231691) 43,794 / 9,533; "Fidget: Squish Fidget" (866943) 43,562 / 3,553; "G26 Fidget Keychain - 3D-Printed Mini Slide-Action Toy" (1508863) 36,656 / 7,314; "Gear fidget" (550127) 29,670 / 5,583. Control query on a low-performing model ("focket toy" id 1237753) returned 11 downloads / 3 likes / 88 views, published 2025-03-21, confirming the API reports real per-model values and not rounded marketing numbers. Six of the eleven top hits are print-in-place mechanisms (clicker, slider, twist, infinity cube), i.e. exactly the mechanism class in scope.
URL: https://api.printables.com/graphql/  (models viewable at https://www.printables.com/model/928 , /927393 , /922541 , /863424 , /231691 , /1508863 , /550127)
Used For: Proving mechanism-level demand (click / slide / twist / gear / infinity-cube) with exact primary figures; ranking which fidget archetypes to build first.

ID: S71
Category: Platform popularity / catalogue scale (primary)
Publisher: Cults3D (Cults SAS)
Title: "Fidget best STL files for 3D printing" — tag page, default and downloads-sorted views
Source Date: live listing, retrieved 2026-09-04
Checked: 2026-09-04
Evidence Used: Page title and body read directly: "Fidget best STL files for 3D printing - 11.8k free models to download - Cults" and "11.8k model ideas to download with the keyword Fidget"; site-wide search field reads "Search 3.6M designs", giving platform catalogue scale. Sorted by Downloads, the top of the fidget tag is dominated by print-in-place articulated and clicker designs: "Grim Reaper, Slim Reaper - Articulated Snap-Flex Fidget" (Free), "Flexi Print-in-Place Imperial Dragon" (EUR 3.88), "Flexi Print-in-Place Fokobot 2.0 (robot)" (Free), "Cute Flexi Print-in-Place Frog" (EUR 2.54), "Bearded Dragon Articulated Toy, Print-In-Place Body, Snap-Fit Head" (EUR 3.44), "Leopard Gecko Articulated Toy ... Snap-Fit Head" (EUR 3.44). Observed paid price band for this class is roughly EUR 2.16-4.30, with "clicker" style items at EUR 2.58-3.44. Limitation: Cults3D does **not** print numeric download counts on the tag listing, so this source gives ranking order and price points, not counts.
URL: https://cults3d.com/en/tags/fidget and https://cults3d.com/en/tags/fidget?sort=downloads
Used For: Confirming commercial price band for print-in-place fidget STLs; showing "articulated flexi + snap-fit head" and "clicker" are the two best-selling shapes; category supply depth.

ID: S72
Category: Platform statistics (secondary, reporting primary Bambu Lab data)
Publisher: 3D Printing Industry
Title: "Bambu Lab data highlights sustained 3D printing activity and creator growth on MakerWorld"
Source Date: article reports Bambu Lab statistics published 2026-02-28
Checked: 2026-09-04
Evidence Used: Reports Bambu Lab's own figures: "83% of its users continue downloading models and printing one year after purchasing a machine"; combined user print time exceeded 290 million hours in the past year; over 30,000 users run printers 7+ hours daily and more than 130,000 users print 6+ hours weekly; "MakerWorld China recorded 280,000 creators uploading models" averaging over 5 designs each, with nearly 4,000 models downloaded or printed 1,000+ times each; MakerLab reached 310,000 users by end of 2025 and generated 2.6 million original models (7,000+ per day); Benchy held the top global print-volume position for five consecutive years; toys and games is a listed model category, with household models the fastest-growing category in 2025. SECONDARY source; underlying data was published by Bambu Lab on WeChat and covers Chinese users via the cloud system, so it is not a global figure.
URL: https://3dprintingindustry.com/news/bambu-lab-data-highlights-sustained-3d-printing-activity-and-creator-growth-on-makerworld-249474/
Used For: Sizing the installed printed-at-home audience for STL sales; showing only ~4,000 models cross 1,000 downloads (long-tail reality check for our file-sales forecast).

ID: S73
Category: Contest / platform programme (primary)
Publisher: Prusa Research (blog.prusa3d.com)
Title: "Printables Awards 2025: Celebrating the Best in 3D Printable Design!"
Source Date: 2026 (winners announced 2026-02-26)
Checked: 2026-09-04
Evidence Used: Awards structure read directly: prize pool of USD 10,000 each for Designer of the Year and Model of the Year, 3x Original Prusa XL (5-toolhead) for category winners, plus 1x Prusa CORE One L and 2x Prusa CORE One+ for randomly drawn voters. Timeline: nominations 2025-12-02 to 2025-12-15; voting 2025-12-17 to 2026-01-12; winners announced 2026-02-26; eligible models were those published 2024-11-01 to 2025-11-30. "Toys & Games" is one of only three model categories (alongside "Practical & Functional Objects" and "Decorations & Art"), i.e. toys are one third of the platform's top-level award taxonomy. Each user could nominate "up to five models and three designers". Community response described only as "thousands of nominations and votes" — no exact vote count published, and the winner names were not present in the retrieved content, so specific 2025 winners are UNVERIFIED.
URL: https://blog.prusa3d.com/printables-awards-2025-celebrating-the-best-in-3d-printable-design_126519/
Used For: Evidence that toys/games is a first-class, prize-backed platform category; award calendar for timing a launch to be eligible.

ID: S74
Category: EU regulation (primary — European Commission)
Publisher: European Commission (GROWTH newsroom)
Title: "New rules for safer toys"
Source Date: 2025/2026 (announcement of the new Toy Safety Regulation)
Checked: 2026-09-04
Evidence Used: States the Toy Safety Regulation entered into force on 1 January 2026 and starts applying on 1 August 2030 after a 4.5-year transition period. Introduces a mandatory Digital Product Passport: "all toys will be required to have a digital product passport, including compliance and other information on the toy, which will have to be immediately accessible via a data carrier". Confirms enforcement at the border and for e-commerce: "digital product passports will be submitted at the EU borders, including for toys sold online", and will be screened to stop non-compliant toys entering the market. The page carries no EU toy market size figure.
URL: https://ec.europa.eu/newsroom/growth/items/924293/en
Used For: Compliance timeline (2026 vs 2030), Digital Product Passport obligation, confirmation that online-sold toys are explicitly in scope of border screening.

ID: S75
Category: EU regulation (primary — European Commission)
Publisher: European Commission, DG GROW (Internal Market, Industry, Entrepreneurship and SMEs)
Title: "Legislation" — Toys / Toy safety
Source Date: page current as at check date
Checked: 2026-09-04
Evidence Used: Confirms Regulation (EU) 2025/2509 was adopted on 26 November 2025, replaces the Toy Safety Directive, "entered into force on 1 January 2026", and becomes applicable "on 1 August 2030" after a 4.5-year transition. Confirms that until then Directive 2009/48/EC is the framework that "establishes mandatory safety criteria for toys marketed in the EU", and that toys "must also comply with any other EU legislation applicable to them" — the page lists concurrently applicable acts including WEEE, RoHS, batteries, electromagnetic compatibility and food-contact materials. The page does **not** list the individual EN 71 harmonised standard parts and names no 3D-printing-specific guidance, so EN 71 part numbers and any 3D-printed-toy market-surveillance guidance remain UNVERIFIED from primary sources this session.
URL: https://single-market-economy.ec.europa.eu/sectors/toys/toy-safety/legislation_en
Used For: Establishing that a 2026 launch is governed by Directive 2009/48/EC, with 2025/2509 as the 2030 target state; identifying adjacent legislation to screen.

ID: S76
Category: Market data — toy industry (primary data owner)
Publisher: Circana
Title: "U.S. Toy Industry Returns to Growth in 2025, Circana Reports"
Source Date: 2026-02-03
Checked: 2026-09-04
Evidence Used: Total US toy dollar sales grew +6% in 2025, with average selling price +4% and units sold +3%; versus 2020 the market is +16% in total, a +3% 5-year CAGR. By supercategory, Games & Puzzles rose +37% in dollar sales, Building Sets +15% and Explorative & Other Toys +20%, and these "three supercategories contributed 92% of all toy industry growth in 2025". Pokemon was the top property at "$2.5 billion in U.S. sales, up 87% year over year". By price tier, the USD 30-69.99 band grew fastest at +18% year over year, while the under-USD-5 and USD 15-19.99 bands posted the steepest declines. Caveat to carry forward: the Games & Puzzles surge is explicitly attributed primarily to Pokemon trading cards, so it is **not** direct evidence for mechanical/dexterity puzzles. Also US-only data.
URL: https://www.circana.com/post/u-s-toy-industry-returns-to-growth-in-2025-circana-reports
Used For: Price-point strategy (the growing tier is EUR/USD 30-70, i.e. supports printed-goods pricing, not 5-euro trinkets); category growth context; honest caveat on puzzle evidence.

ID: S77
Category: Market sizing — fidget toys (secondary, commercial market-research vendor)
Publisher: Fortune Business Insights
Title: "Fidget Toys Market Size, Share, Trends" (Report ID FBI110591)
Source Date: page last updated 2026-08-17; study period 2021-2034, base year 2025
Checked: 2026-09-04
Evidence Used: Global fidget toys market valued at USD 9.01 billion in 2025, rising to USD 9.57 billion in 2026 and forecast at USD 17.65 billion by 2034, a "CAGR of 7.96% during the forecast period (2026-2034)". Regional split: North America 37.25% share (USD 3.36bn 2025 to USD 3.57bn 2026); Asia Pacific 31.81% (USD 2.87bn to USD 3.07bn); **Europe 20.17% share, USD 1.82bn in 2025 rising to USD 1.91bn in 2026** — the directly relevant addressable region. By product, "the fidget spinner segment is projected to lead the market with a 40.02% share in 2026". SECONDARY commercial vendor: methodology is paywalled and unverifiable, and vendor estimates for this market diverge widely (other vendors' 2025-26 figures range from ~USD 6.98bn to ~USD 9.07bn), so treat the level as indicative and the direction as the usable signal.
URL: https://www.fortunebusinessinsights.com/fidget-toy-market-110591
Used For: Europe-specific fidget TAM, growth direction, and the finding that spinner-type geometry still holds the largest product share.

### ADDITIONAL CHECKS — negative findings (no ID assigned, recorded for honesty)
- **Etsy** (https://community.etsy.com/forum/etsy-success-300/topic/etsy-insights-explore-the-trends-shaping-spring-and-summer-2026-165859/ , checked 2026-09-04): Etsy's official Spring/Summer 2026 seller trend report by Dayna Isom Johnson (Etsy Resident Trend Expert) publishes exact search-growth figures — embroidered straw bags +20,000%, polka dot phone cases +835%, journal charms +395%, petit cadeau +277%, beginner needlepoint kits +175%, wall art decor +110%, whimsical jewelry +84%, gallery prints +80% — and names five trends ("Soft Stitch Era", "World of Whimsy", "Treat Yourself", "Dear Diary", "Everyday Exhibits"). It contains **no** toy, puzzle, fidget, sensory or 3D-printing search data. Any "Etsy fidget search is up X%" claim is therefore UNVERIFIED.
- **Pinterest Predicts 2026** (https://business.pinterest.com/blog/pinterest-predicts-2026-turn-trends-into-unlimited-possibilities/ , published 2025-12-09, checked 2026-09-04): named 2026 trends read directly are Glamoratti, **Gimme Gummy**, Mystic Outlands, Cool Blue, Pen Pals, Glitchy Glam, Cabbage Crush, Brooched, Vamp Romantic. Verified platform claims: "Over the past six years, 88% of our trend predictions have come true"; Pinterest trends last nearly twice as long as trends elsewhere; checkouts on 2025 predictions up 68% year on year; Cool Blue +35%. **No** fidget/tactile/desk-toy search percentage is published on this page; the widely repeated "everything is going squishy and bendy" line is media interpretation, and the description and growth figure behind "Gimme Gummy" are UNVERIFIED.
- **Google Trends direction, TikTok view counts, and viral-print coverage**: not confirmed on any primary page this session — UNVERIFIED. Specifically the frequently quoted "3D-printed twisty strawberry fidget, 16.8M TikTok views" is UNVERIFIED.
- **Printables contest pages** (contest/77 "Fidget Toys", contest/420 "Finger toys", contest/499 "Balancing Games", contest/506 "Sensory Play") were 403-blocked; contest existence and winner lists are UNVERIFIED at page level. Partial corroboration only: the model named in snippets as the Fidget Toys contest winner, "Fidget Clicking Wheel 2.0", was independently confirmed to exist with 43,794 downloads / 9,533 likes via S70.

---

## SECTION 2 — TOY COMPLIANCE SUMMARY (German/EU seller)

- **The new Regulation is already law but does not yet bite.** Regulation (EU) 2025/2509 was adopted 26 November 2025 and **entered into force 1 January 2026**, but only **starts applying 1 August 2030** after a 4.5-year transition. A product launched in 2026 is therefore designed and certified against the **existing Toy Safety Directive 2009/48/EC**, which the Commission still describes as establishing the mandatory safety criteria for toys marketed in the EU. [S74][S75]
- **Design now for the 2030 end-state, because it is a Regulation.** 2025/2509 replaces the Directive rather than amending it, so the same text will bind a German seller directly. Do not build a compliance file that only satisfies 2009/48/EC and cannot be migrated. [S75]
- **Digital Product Passport is the big new build cost.** Under the new Regulation "all toys will be required to have a digital product passport, including compliance and other information on the toy, which will have to be immediately accessible via a data carrier". For metriMade this means per-SKU persistent identifiers plus an on-part data carrier (QR) designed into the geometry from the start — a marking and versioning problem, not just a paperwork problem. [S74]
- **Selling online does not reduce scope.** The Commission states digital product passports "will be submitted at the EU borders, including for toys sold online" and will be screened to block non-compliant toys. Marketplace/DTC channels are explicitly covered; there is no small-shop or online-only carve-out visible on the Commission pages. [S74]
- **Screen the adjacent legislation, not only toy law.** The Commission's own toys legislation page states toys "must also comply with any other EU legislation applicable to them" and lists concurrently applicable acts including WEEE, RoHS, batteries, EMC and food-contact materials. For our scope this matters if a concept gains a magnet, a battery, a light, or is marketed as usable with food/mouth contact — all of which we should avoid to keep the compliance file thin. [S75]
- **Printed physical toy vs. digital STL file — the distinction is NOT resolved by any source verified here.** Whether a downloadable STL/3MF design file is itself a "toy placed on the market" is **UNVERIFIED**; neither Commission page addressed design files or 3D printing. Working risk posture until legal review: for **printed goods** assume metriMade is the manufacturer and owes the full CE/DoC/technical-file/traceability/warning set; for **digital files** sell as design files for personal fabrication, make no age claim, do not apply a CE mark to a file, and state in the licence that whoever places printed copies on the market becomes the manufacturer. [S74][S75 for the framework only]
- **EN 71 detail and small-parts rules are UNVERIFIED at primary level.** The Commission legislation page does not enumerate the EN 71 harmonised standard parts, and no EN 71 clause text, small-parts-cylinder dimension, or "not suitable for children under 36 months" wording was read this session. Treat every concept in Section 3 as **14+ desk-toy positioned, explicitly not a children's toy**, and get EN 71-1 (mechanical/physical, small parts), EN 71-2 (flammability) and EN 71-3 (migration of elements) applicability confirmed by a test house before any 3+ claim. **UNVERIFIED**
- **No 3D-printing-specific market-surveillance guidance was found.** No Commission or member-state guidance addressing 3D-printed toys or toy design files surfaced on any primary page checked. Also flag: the commonly cited article-level details of 2025/2509 (that Articles 28-44 and 49-55 apply from 1 January 2026, and that EC type-examination certificates issued under 2009/48/EC stay valid until 1 February 2031) come only from commercial compliance-firm summaries and search snippets — EUR-Lex itself returned empty responses this session, so these remain **UNVERIFIED** and must be checked against the OJ text before they enter a compliance plan. [gap]

---

## SECTION 3 — PRODUCT CONCEPTS (18)

Workflow assumption for all: single isolated product image via AI image generation -> Step1X-3D image-to-3D mesh for the
organic/appearance shell -> functional geometry (joint clearances, gear teeth, detents, tolerances, split lines) finished in CAD.

### 1. Ridgeback Stag Beetle
- Description: Print-in-place articulated stag beetle; segmented abdomen flexes along its length and a snap-fit mandible head rotates.
- Customer job: An impressive, fiddle-able desk creature that proves the owner's printer can do "one-piece moving" prints.
- Trend signal: Cults3D's fidget tag sorted by downloads is led by print-in-place articulated animals with snap-fit heads, at EUR 2.16-4.30 [S71]; 6 of 11 top Printables fidget hits are print-in-place mechanisms [S70].
- Target segment: Adult FDM hobbyists, gift buyers, desk-toy collectors
- Size: 150 x 70 x 45 mm
- Mechanism type: PRINT_IN_PLACE_ARTICULATED
- Safety/limit: Detachable mandible head is a small part; pinch risk between abdomen segments; 14+, not for under-3.

### 2. Pangolin Curl
- Description: Armoured flexi pangolin whose overlapping scale plates let it roll into a closed ball and spring back open.
- Customer job: A tactile "fold it away" object that satisfies the urge to compress something without a squishy material.
- Trend signal: Articulated print-in-place animals dominate the downloads-sorted Cults3D fidget tag [S71]; "Fidget: Squish Fidget" reached 43,562 downloads on Printables, showing squeeze/compress interaction sells [S70].
- Target segment: Adults seeking stress-relief desk objects; animal-figure gift market
- Size: 165 x 75 x 60 mm
- Mechanism type: PRINT_IN_PLACE_ARTICULATED
- Safety/limit: Scale edges pinch fingers when curling; thin scale tips can snap off as small parts; 14+.

### 3. Dune Scorpion
- Description: Articulated scorpion whose segmented tail clicks through detents as it is raised, plus hinged pincers, so it doubles as a clicker.
- Customer job: Combines the collectible creature figure with an audible click fidget in one print.
- Trend signal: Click mechanisms are the strongest verified archetype: "Print-In-Place Fidget Clicker" 118,213 downloads and "Fidget Clicking Wheel 2.0" 43,794 downloads / 9,533 likes on Printables [S70].
- Target segment: Adult fidget users, desk-toy buyers, arachnid/creature figure niche
- Size: 190 x 90 x 55 mm
- Mechanism type: PRINT_IN_PLACE_ARTICULATED
- Safety/limit: Pointed tail tip must be radiused; pincer pinch points; small pincer tips; 14+.

### 4. Tidepool Hermit
- Description: Flexi hermit crab with articulated legs whose spiral shell unscrews on a printed thread into a tiny storage pod.
- Customer job: Desk object plus a hiding place for a ring, pill or SD card — utility raises perceived value over a pure figure.
- Trend signal: Twist interaction is proven at scale — "Dragon Egg Twist Fidget" 56,665 downloads and "Spiral cone fidget toy" 122,166 downloads on Printables [S70]; print-in-place flexi animals top Cults3D's fidget downloads ranking [S71].
- Target segment: Adults, gift and stocking-filler buyers, Etsy-style handmade shoppers
- Size: 130 x 100 x 65 mm
- Mechanism type: PRINT_IN_PLACE_ARTICULATED
- Safety/limit: Unscrewing shell separates into a swallowable part; not a container for food or medicine claims; 14+.

### 5. Mantis Fold
- Description: Print-in-place praying mantis whose raptorial forelegs fold and snap shut against the thorax on compliant hinges.
- Customer job: A poseable, repeatedly snappable creature for hands that need something to do during calls.
- Trend signal: Category-level evidence only for this specific creature; the mechanism class is proven, with print-in-place articulated and snap-fit designs leading Cults3D fidget downloads [S71] and clickers leading Printables [S70].
- Target segment: Adult hobbyists, insect/nature figure buyers, office desk gifts
- Size: 175 x 85 x 70 mm
- Mechanism type: PRINT_IN_PLACE_ARTICULATED
- Safety/limit: Foreleg snap action pinches fingertips; slender antennae are breakable small parts; 14+.

### 6. Orbit Bloom
- Description: Desk sculpture where turning a base knob drives a planetary gear set that opens and closes eight sculpted petals.
- Customer job: A "satisfying to operate" display piece that visibly demonstrates printed gearing to visitors.
- Trend signal: Geared fidgets are validated — "Gear fidget" has 29,670 downloads and 5,583 likes on Printables [S70]; the fidget category is sized at USD 9.57bn for 2026 with Europe USD 1.91bn [S77].
- Target segment: Design-led desk decor buyers, gift market, makers wanting a showpiece print
- Size: 140 x 140 x 110 mm
- Mechanism type: KINETIC_GEARED
- Safety/limit: Exposed gear mesh and closing petals are finger-pinch and hair-catch points; 14+, adult supervision only.

### 7. Trochoid Spinner
- Description: An epitrochoid rotor orbits inside a sculpted housing as it spins, giving an eccentric, non-obvious spin feel.
- Customer job: A spinner that looks and feels engineered rather than mass-produced plastic.
- Trend signal: Spinner-type product is still the largest share of the fidget market at a projected 40.02% in 2026 [S77]; rotary/spinner fidgets rank in Printables' top fidget results by downloads [S70].
- Target segment: Adult fidget buyers, engineering-minded gift recipients
- Size: 95 x 95 x 22 mm
- Mechanism type: KINETIC_GEARED
- Safety/limit: Rotating mass with a gap to the housing — pinch point; no bearing or magnet inserts, to stay out of ingestion-hazard territory; 14+.

### 8. Cog Reef
- Description: A coral-reef-shaped block of intermeshed gears where one knurled knob sets the whole reef turning at different rates.
- Customer job: An all-in-one-print kinetic ornament for a shelf or desk that rewards idle hands.
- Trend signal: Printed gear fidgets have verified demand (Printables "Gear fidget", 29,670 downloads / 5,583 likes) [S70]; toys and games is one of three top-level Printables award categories [S73].
- Target segment: Desk decor and interior-gift buyers; STL customers wanting a print showcase
- Size: 180 x 110 x 90 mm
- Mechanism type: KINETIC_GEARED
- Safety/limit: Many open gear meshes: significant pinch and entrapment risk for small fingers; 14+, keep away from children and pets.

### 9. Ripple Cam Wave
- Description: A hand crank rotates a phased cam shaft that lifts twelve sculpted pins in sequence, producing a travelling wave.
- Customer job: The classic "satisfying mechanism" purchase — bought to watch and to hand round the office.
- Trend signal: Only category-level evidence for kinetic sculpture specifically (UNVERIFIED at model level); adjacent proof is that the fastest-growing US toy price tier is USD 30-69.99 at +18%, which fits a mid-priced printed kinetic piece [S76].
- Target segment: Office gifting, design-object buyers, higher-priced printed-goods tier
- Size: 210 x 80 x 130 mm
- Mechanism type: KINETIC_GEARED
- Safety/limit: Crank and cam shaft create trap points between moving pins and frame; multi-part assembly with small pins; 14+.

### 10. Click Pebble
- Description: Palm-sized river-pebble form with a compliant bistable dome that snaps loudly under thumb pressure and resets.
- Customer job: A silent-to-carry, loud-to-press stress release that fits a pocket and does not look like a toy in a meeting.
- Trend signal: The single strongest verified archetype: "Print-In-Place Fidget Clicker" 118,213 downloads and "Fidget Clicking Wheel 2.0" 43,794 downloads / 9,533 likes on Printables [S70]; clickers sell at EUR 2.58-3.44 on Cults3D [S71].
- Target segment: Adults, ADHD/anxiety self-management buyers, office and commuter carry
- Size: 62 x 45 x 22 mm
- Mechanism type: COMPLIANT_SPRING
- Safety/limit: Whole object is below typical small-parts thresholds — must be sold 14+ and never age-graded 3+; sustained clicking noise nuisance.

### 11. Bolt Slide
- Description: A weighted sculpted slider runs in a channel and is thrown open or shut by thumb against a compliant detent that clicks at each end.
- Customer job: Reproduces the addictive slide-and-snap action of a mechanical switch in a legal, blade-free desk object.
- Trend signal: Slide-action fidgets are proven and near the top of Printables' fidget results: "OTF Fidget Knife - only 3 Parts" 93,287 downloads and "G26 Fidget Keychain - Mini Slide-Action Toy" 36,656 downloads / 7,314 likes [S70].
- Target segment: Adult EDC and pocket-fidget buyers
- Size: 105 x 32 x 18 mm
- Mechanism type: COMPLIANT_SPRING
- Safety/limit: Deliberately blunt and blade-free to avoid weapon-law and gravity-knife classification; slider pinches skin in the channel; small part; 14+.

### 12. Snap Blossom
- Description: Sculpted flower head whose petals sit on compliant living hinges; pressing the centre snaps all petals through to the open state at once.
- Customer job: A one-touch, visually rewarding reset action — decorative enough to leave on a desk permanently.
- Trend signal: Compliant snap and click mechanisms are the highest-download fidget class verified on Printables [S70]; snap-fit print-in-place designs also lead Cults3D's downloads-sorted fidget tag [S71].
- Target segment: Gift buyers, decor-led fidget buyers, teachers and desk workers
- Size: 90 x 90 x 40 mm
- Mechanism type: COMPLIANT_SPRING
- Safety/limit: Living hinges fatigue and can fracture into small parts; petal edges pinch; state a cycle-life expectation; 14+.

### 13. Ratchet Coin
- Description: A large sculpted coin with a captive inner disc that steps through a printed ratchet pawl, clicking once per index.
- Customer job: A worry-coin for continuous one-handed thumb rotation with tactile and audible feedback.
- Trend signal: Rotary click fidgets are validated at scale — "Fidget Clicking Wheel 2.0" 43,794 downloads / 9,533 likes, and "fidget star" 59,521 downloads on Printables [S70].
- Target segment: Adults, neurodivergent self-regulation buyers, pocket-carry gift market
- Size: 58 x 58 x 14 mm
- Mechanism type: COMPLIANT_SPRING
- Safety/limit: Small overall size plus a captive disc that can free itself — small-parts and choking risk; 14+ only, never marketed for children.

### 14. Basalt Burr
- Description: Six-piece interlocking burr puzzle whose exterior reads as a cluster of hexagonal basalt columns; only one assembly order works.
- Customer job: A giftable brain-teaser that looks like an ornament when solved and sits on a shelf.
- Trend signal: Honest limit: Circana's Games & Puzzles supercategory grew +37% in 2025 but that growth is attributed primarily to Pokemon trading cards, so this is category-adjacent, not mechanical-puzzle, evidence [S76].
- Target segment: Puzzle enthusiasts, adult gift market, corporate gifting
- Size: 110 x 110 x 110 mm
- Mechanism type: PUZZLE_INTERLOCK
- Safety/limit: Six loose rigid pieces, each a potential small part; needs tight tolerance control so pieces do not jam and get forced; 14+.

### 15. Nautilus Maze Sphere
- Description: Two-shell sphere with a shell-spiral exterior and an internal 3D maze; a captive printed ball is walked to the centre by tilting.
- Customer job: A single-object dexterity challenge with no loose parts to lose — good for travel and desks.
- Trend signal: Category-level only for maze puzzles (UNVERIFIED at model level); supporting context is the USD 30-69.99 price tier growing fastest at +18% in the US toy market, which suits a larger printed puzzle [S76].
- Target segment: Puzzle and dexterity-toy buyers, travel gift, printed-goods tier
- Size: 120 x 120 x 120 mm
- Mechanism type: PUZZLE_INTERLOCK
- Safety/limit: Captive ball must stay captive — verify the shell join cannot be split by hand, or the ball becomes a choking hazard; 14+.

### 16. Ammonite Packing Tray
- Description: A spiral ammonite relief dissected into nine tiles that pack into a tray exactly one way; the fossil pattern only aligns when solved.
- Customer job: A quiet, screen-free puzzle that finishes as a piece of wall or desk art.
- Trend signal: Category-adjacent only: Games & Puzzles was the largest US toy supercategory and grew +37% in 2025, though chiefly on trading cards [S76]; toys and games is one of three Printables award categories [S73].
- Target segment: Adult puzzle buyers, museum/nature-shop style gifting, decor buyers
- Size: 200 x 200 x 25 mm
- Mechanism type: PUZZLE_INTERLOCK
- Safety/limit: Nine loose tiles; thin tile edges chip; a solved-state image should be supplied; 14+, not for under-3.

### 17. Geode Worry Stone
- Description: Non-mechanical sculpted stone with a crystalline void on one face and a polished thumb dish on the other; purely surface-texture driven.
- Customer job: A calming, silent object to hold during calls where any clicking would be unacceptable.
- Trend signal: Squeeze/hold tactile fidgets are proven: "Fidget: Squish Fidget" has 43,562 downloads on Printables [S70]; the fidget category is put at USD 9.57bn for 2026, with Europe at USD 1.91bn [S77].
- Target segment: Adults, anxiety/stress-relief buyers, wellness and gift retail
- Size: 70 x 50 x 22 mm
- Mechanism type: SCULPTURAL_TACTILE
- Safety/limit: Small single-piece object — small-parts risk, 14+; must not be presented as a therapeutic or medical device.

### 18. Trefoil Knot Roller
- Description: A closed trefoil-knot torus with three captive rings that roll continuously around the knot path without ever coming off.
- Customer job: An endless-loop tactile motion object — the "keep hands busy forever" purchase, and a strong shelf piece.
- Trend signal: Endless-loop fidgets are the top verified performer on Printables: "Yet Another Fidget Infinity Cube v2" 155,845 downloads / 16,525 likes [S70]; spinner/rotary product holds a projected 40.02% fidget market share in 2026 [S77].
- Target segment: Adult fidget buyers, design-object and desk-decor market
- Size: 130 x 130 x 55 mm
- Mechanism type: SCULPTURAL_TACTILE
- Safety/limit: Captive rings create pinch points against the knot body; ring cross-section must be too large to be a choking hazard if a ring is forced off; 14+.

---
### Concept coverage check
PRINT_IN_PLACE_ARTICULATED 5 (1-5) / KINETIC_GEARED 4 (6-9) / COMPLIANT_SPRING 4 (10-13) / PUZZLE_INTERLOCK 3 (14-16) /
SCULPTURAL_TACTILE 2 (17-18) = 18 concepts. None duplicates the excluded list (articulated dragon, sea turtle, axolotl,
koi, chameleon, capybara, red panda, whale shark). All within 220 x 220 x 250 mm.
