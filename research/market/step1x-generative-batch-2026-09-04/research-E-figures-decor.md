# Research E — Human figures / figurines / statues + trending FDM home decor
Brand: metriMade (DE, FDM/FFF, digital STL/3MF + printed goods)
Research date: 2026-09-04
Build envelope constraint for all concepts: 220 x 220 x 250 mm

> **Verification note (read first).** Several target domains blocked automated retrieval during this
> session: `etsy.com` (HTTP 403), `printables.com` HTML pages (403), `makerworld.com` HTML pages (403),
> `eur-lex.europa.eu` (empty/202 challenge), `grandviewresearch.com` (403), `heroforge.com` (403),
> `ebay.de` (403). Where a figure could not be read on a real page it is marked **UNVERIFIED** and no
> number is substituted. Two platform **APIs** did respond and were queried directly, which is the
> strongest primary evidence in this file: the Printables GraphQL API (`api.printables.com/graphql/`)
> and the MakerWorld design API (`makerworld.com/api/v1/design-service/design/{id}`). All figures in
> S86/S87 are raw API responses read on 2026-09-04.

---

## SECTION 1 — SOURCE RECORDS

**ID:** S86
**Category:** Platform primary data (API)
**Publisher:** Printables.com (Prusa Research) — public GraphQL API
**Title:** Printables GraphQL API — per-model download/like/view counters for decor and bust models
**Source Date:** live counters, queried 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** Queried `print(id:){name downloadCount likesCount displayCount datePublished makesCount}`. Verified: "Self Watering Pot/Planter (Parametric)" id 227702 = 4,744 downloads / 2,337 likes / 25,686 views / 41 makes, published 2025-02-16; "Self-Watering Planter (Small)" id 274589 = 2,479 downloads / 523 likes / 8,913 views / 74 makes, published 2022-09-11; "Self Watering Design Planter" id 932345 = 1,055 downloads / 394 likes / 7,338 views, published 2025-06-18; "self watering planter pot" id 1557962 = 495 downloads / 247 likes / 4,976 views, published 2026-01-16. Bust/statue tier is an order of magnitude lower: "Aphrodite Bust (Sculpture 3D Scan)" id 558045 = 837 downloads / 171 likes / 12 makes / rating 4.56 (9 ratings); "Dostoevsky bust" id 455940 = 602 downloads / 58 likes / 6 makes; "Elegant Female Bust Sculpture" id 1515424 = 343 downloads / 77 likes / 0 makes, published 2025-12-14; "Jesus Christ Bust Sculpture" id 859555 = 267 downloads / 34 likes / 1 make. Generic un-differentiated vessels perform very poorly: "Vase Planter V2" id 409036 = 44 downloads; "Planter or Vase" id 629506 = 55 downloads; "Is it a Vase, a planter or a little bin?" id 81033 = 49 downloads / 3 likes.
**URL:** https://api.printables.com/graphql/ (model pages: https://www.printables.com/model/227702 , /274589 , /558045 , /455940 , /1515424 , /859555 , /409036)
**Used For:** Functional-planter-beats-plain-vessel evidence; realistic download expectations per tier; bust demand is real but niche; anti-generic warning for concept design.

**ID:** S87
**Category:** Platform primary data (API)
**Publisher:** MakerWorld (Bambu Lab) — public design API
**Title:** MakerWorld design API — per-model like/print/download/collection counters for lamp shades
**Source Date:** live counters, queried 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** Queried `/api/v1/design-service/design/{id}` for `likeCount, printCount, downloadCount, rawModelFileDownloadCount, collectionCount, createTime, license`. Verified: "Lamp Shade 4.0 - Spiralvase" id 1025179 = 1,333 likes / 1,424 prints / 2,601 downloads / 4,647 collections, created 2025-01-22, "Standard Digital File License"; "Organic Lamp Shade (vase mode)" id 1206248 = 568 likes / 211 prints / 941 downloads / 1,697 collections, created 2025-03-13; "Lampenschirm 04 - Vasenmodus" id 1538820 = 74 likes / 139 prints / 213 downloads / 273 collections; "Diamond Lamp Shade" id 1040855 = 118 likes / 69 prints / 130 downloads; "Lampshade (vase mode)" id 210882 = 95 likes / 59 prints / 201 downloads, license "BY-NC"; "Parametric Lamp Shade -Vase Mode" id 162242 = 46 likes / 23 prints / 103 downloads; "Lamp Shade (vase mode)" id 1208224 = 86 likes / 4 prints / 144 downloads. Note `printCount` > `rawModelFileDownloadCount` on the top item, i.e. MakerWorld's cloud-print path dominates raw STL pulls.
**URL:** https://makerworld.com/api/v1/design-service/design/1025179 (model page: https://makerworld.com/en/models/1025179-lamp-shade-4-0-spiralvase)
**Used For:** Lamp-shade / vase-mode demand is the strongest verified decor niche; "collections" as a save-for-later demand signal; licence-model reality on MakerWorld.

**ID:** S88
**Category:** Platform ecosystem statistics (secondary, reporting Bambu Lab primary data)
**Publisher:** 3D Printing Industry
**Title:** Bambu Lab data highlights sustained 3D printing activity and creator growth on MakerWorld
**Source Date:** 2026-02-28
**Checked:** 2026-09-04
**Evidence Used:** Reports Bambu Lab's own 2025 figures: "83% of its users continue downloading models and printing one year after purchasing a machine"; combined annual print time 290 million hours; 30,000+ users printing 7+ hours daily and 130,000+ printing 6+ hours weekly; ~4,000 models with 1,000+ downloads each; MakerWorld China 280,000 creators averaging 5+ designs each; MakerLab 310,000 users generating 2.6 million models (~7,000/day) of which ~400,000 were lithophanes (~1 in 6). Fastest-growing categories in 2025: household models, then hobby/DIY, then tools; category list includes decorations and sculptures. Benchy held top global print volume for five consecutive years. Xiaohongshu searches: "3D printing" +119% YoY, "3D printer" +238%, "Bambu Lab" +323%.
**URL:** https://3dprintingindustry.com/news/bambu-lab-data-highlights-sustained-3d-printing-activity-and-creator-growth-on-makerworld-249474/
**Used For:** Household/decor is the fastest-growing MakerWorld category; only ~4,000 models cross 1,000 downloads (rarity of hits); lithophane/decor-light saturation warning; installed-base engagement.

**ID:** S89
**Category:** Consumer trend report (primary)
**Publisher:** Pinterest (Newsroom)
**Title:** Pinterest Predicts™: Nonconformity, self-preservation, and escapism drive 21 trends for 2026
**Source Date:** 2025-12-09
**Checked:** 2026-09-04
**Evidence Used:** 21 named 2026 trends with YoY search growth; methodology stated as YoY growth across 600 million monthly users with a claimed "88% accuracy" over six years. Decor-relevant: **Afrohemian Decor** — "afrobohemian home decor" +220%, "adire fabric" +130%, "motif berbere" +210%, "bamboo beaded curtains" +60%, "ethiopian art" +50%, "rattan accent chair" +50%. **Neo Deco** — "pendant lamp" +40%, "antique bar cart" +100%, "red marble bathroom" +80%, "brass aesthetic" +35%. **Extra Celestial** — "opalescent" +115%, "alien core aesthetic" +80%. **FunHaus** — "circus interior" +130%, "vintage circus aesthetic" +70%, "striped ceiling" +40%, "circus nursery" +50%. **Wilderkind** — "dragonfly nails" +145%, "bug jewellery" +60%, "deer aesthetic" +55%. **Gimme Gummy** — "jelly blush" +130%, "jelly candy aesthetic" +100%. **Opera Aesthetic** — "midnight masquerade" +95%, "masquerade decor" +40%. **Throwback Kid** — "nostalgia toys" +225%, "1970s childhood toys" +125%. **Brooched** — "maximalist accessories" +105%, "heirloom jewelry" +45%. **Vamp Romantic** — "dark romantic makeup" +160%. **Laced Up** — "lace doily" +105%.
**URL:** https://newsroom.pinterest.com/news/pinterest-predicts-nonconformity-self-preservation-and-escapism-drive-21-trends-for-2026/
**Used For:** Primary quantified aesthetic direction for 2026 decor concepts (geometric/Deco, iridescent, bohemian/textile-pattern relief, insect/nature motifs, masquerade/figurative, nostalgia). NOTE: no mushroom/cottagecore or brutalist trend appears in the 2026 list — see gap flag.

**ID:** S90
**Category:** Regional market report (secondary, paywalled research firm)
**Publisher:** IMARC Group
**Title:** Germany Home Decor Market — Size, Share, Trends and Forecast
**Source Date:** Report ID SR112026A23342; base year 2025; historical period 2020–2025 (page checked 2026-09-04)
**Checked:** 2026-09-04
**Evidence Used:** Germany home decor market size 2025 = USD 36.5 billion; forecast 2034 = USD 53.2 billion; CAGR 2026–2034 = 4.28%. Segmentation by product type covers home furniture, home textiles, flooring, **wall decor**, **lighting**, and others; distribution channels include home decor stores, supermarkets/hypermarkets, **online stores**, gift shops. Growth drivers named: rising disposable incomes, urbanization, preference for aesthetically pleasing interiors, "strong emphasis on sustainable and eco-friendly products", and social-media/home-improvement influence. Per-segment share percentages are NOT disclosed on the public page (UNVERIFIED).
**URL:** https://www.imarcgroup.com/germany-home-decor-market
**Used For:** German home-market sizing for decor; confirms wall decor and lighting as tracked segments; online channel relevance. Secondary, vendor-estimated — treat as directional only.

**ID:** S91
**Category:** Platform/consumer signal (search-result snippets only — degraded evidence)
**Publisher:** Printables.com / MakerWorld / Thingiverse (via search engine result snippets)
**Title:** Snippet-level popularity figures for decor and figurine models
**Source Date:** snippets undated; retrieved 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** These figures were returned in search-result snippets and could **not** be confirmed on the live page (both platforms returned HTTP 403 to direct retrieval), so they are recorded as **UNCONFIRMED SNIPPET VALUES, not verified counts**: Printables "Small Self-Watering Seed Starter" 17.5K downloads / 37.8K likes; "Hydroponic, Self-Watering, Seeds starter, Robert Planters" 10.4K downloads / 37.6K likes; "Geralt Of Rivia – The Witcher" 3.8K downloads / 14.7K likes; "Darth Vader Bust" 3.5K downloads / 15.2K likes. MakerWorld snippets: "Planter with legs" (SabreDesign) 35.1k downloads; "Crumbled Paper Plant Pot" (HpInvent) 20.4k; "Plant Pot smooth ribs curved" (HpInvent) 15.7k; "Happy Pot - Mini Succulent Planter" 11.2k; "Balloon Unicorn & Llama Figures" 12.8k; "Flexi Capybara - Articulated" 9.7k. Thingiverse snippets: "Curved Honeycomb Vase" 550,000+ downloads; "Self Watering Planter" 425,000+; "Spiral Vase" 188,000+.
**URL:** https://www.printables.com/model/227702 ; https://makerworld.com/en/models/396295-planter-with-legs ; https://makerworld.com/en/collections/1776679-planters
**Used For:** Direction only (planters and vases are the highest-volume decor category across all three platforms; character busts are IP-driven and therefore off-limits for us). **Do not quote these numbers as verified.**

**ID:** S92
**Category:** Digital-marketplace price observation (partially verified)
**Publisher:** Cults3D (Cults SAS, France)
**Title:** Cults3D bust/figurine tag listings and price points
**Source Date:** listings live; checked 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** Cults3D model pages are retrievable; the "Aphrodite Bust" art model page was retrieved and read (free model, 6 downloads, 2 likes, 0 collections at check time — i.e. long-tail free listings get near-zero traction). Tag-page counts and paid-model prices were only visible via search snippets and are therefore **UNCONFIRMED SNIPPET VALUES**: bust tag "30.2k models", figurine tag "8.6k models"; paid examples quoted as US$15.00 (Space Orc Bust STL, Space Bug Bust STL), US$5.79 (Terminator bust), ~US$5.83–5.84 (stone-sculpture busts/statues), US$3.84 (Sphynx Cat Flexi), US$4.41. Cults3D was NOT confirmed to display EUR to this session's client, so a EUR digital price band from Cults3D is **UNVERIFIED**.
**URL:** https://cults3d.com/en/3d-model/art/aphrodite-bust ; https://cults3d.com/en/tags/bust ; https://cults3d.com/en/tags/figurine
**Used For:** Order-of-magnitude digital price anchor for busts/figurines (single-digit USD typical, ~US$15 upper end for premium sculpts); evidence that free long-tail sculpts earn nothing.

**ID:** S93
**Category:** EU legislation (official Commission page — primary for identification, not for article text)
**Publisher:** European Commission, DG GROW (Internal Market, Industry, Entrepreneurship and SMEs)
**Title:** General product safety — harmonised standards page (Regulation (EU) 2023/988)
**Source Date:** page current at check; regulation adopted 2023-05-10, OJ L 135, 23.5.2023
**Checked:** 2026-09-04
**Evidence Used:** Confirms Regulation (EU) 2023/988 on general product safety, adopted 10 May 2023, published OJ L 135, 23.5.2023; repeals Directive 2001/95/EC (GPSD) and Council Directive 87/357/EEC; amends Regulation (EU) No 1025/2012 and Directive (EU) 2020/1828. Page states OJ publications supporting the regulation began 13 December 2024 and directs readers to the DG JUST product-safety pages for economic-operator obligations. Harmonised standards under GPSR are listed via Commission Implementing Decision (EU) 2026/901. The page itself does **not** enumerate Article 9/16/19 obligations (see S94).
**URL:** https://single-market-economy.ec.europa.eu/single-market/goods/european-standards/harmonised-standards/general-product-safety_en
**Used For:** Authoritative identification of the applicable EU product-safety instrument and its 13 Dec 2024 application date; existence of GPSR harmonised standards (Implementing Decision (EU) 2026/901).

**ID:** S94
**Category:** EU legislation — article-level detail (SECONDARY / snippet-level; primary text not retrievable this session)
**Publisher:** various compliance publishers (via search results); underlying instrument = Regulation (EU) 2023/988
**Title:** GPSR Articles 9(5)/(6), 16 and 19 — traceability, EU responsible person, distance-selling disclosure
**Source Date:** GPSR applies from 2024-12-13
**Checked:** 2026-09-04
**Evidence Used:** Read in search results, **not** confirmed against the EUR-Lex text (EUR-Lex returned an empty/202 challenge on every attempt): Article 16 — a product shall not be placed on the market unless there is an economic operator established in the Union responsible for it (EU manufacturer, EU importer, EU-established authorised representative, or EU fulfilment service provider); Article 16(3) with Articles 9(5) and 9(6) — products must carry identification elements (type, batch or serial number) plus the manufacturer's name/registered trade name/trademark and postal and electronic address, and the responsible person's name and contact details, on the product, its packaging, the parcel or an accompanying document; Article 19 — for distance selling the online offer must show the manufacturer's (or EU authorised representative's) name and contact details, product identification information including a product image, and any warnings or safety information. Online marketplaces must register on Safety Gate and provide a single contact point. **Article numbers and wording above are UNVERIFIED against the Official Journal text and must be re-checked on EUR-Lex before use in any published compliance statement.**
**URL:** https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32023R0988 (target primary text — not retrievable in this session)
**Used For:** Provisional shape of our GPSR duties: EU responsible person, product/packaging traceability marking, mandatory online-offer disclosures, DE-language warnings. Flagged for mandatory re-verification.

**ID:** S95
**Category:** Platform content rules — AI transparency (SECONDARY / snippet-level)
**Publisher:** MakerWorld (Bambu Lab) — policy pages read via search results only
**Title:** MakerWorld AI-assisted content disclosure rules and real-print image requirement
**Source Date:** policy pages undated on snippet; retrieved 2026-09-04
**Checked:** 2026-09-04
**Evidence Used:** Read in search results (the policy pages returned HTTP 403 to direct retrieval, so wording is **UNCONFIRMED**): projects using AI-assisted content must disclose the AI tools/technologies used, how AI-produced content is incorporated, and the extent of human involvement; AI-assisted work must include significant human creative input, and campaigns relying primarily on AI-generated models with minimal human involvement "will not be approved"; falsely claiming AI-generated work as fully human-made is prohibited; model images must include at least one **real printed photo** that matches the uploaded model file and model name, clearly and fully showing the final printed object. Existence of dedicated policy URLs `makerworld.com/en/crowdfunding-ai-policy`, `/community-guidelines`, `/user-agreement` and an `Aigenerated` community tag was confirmed in the result set.
**URL:** https://makerworld.com/en/crowdfunding-ai-policy ; https://makerworld.com/en/community-guidelines
**Used For:** Hard operational constraint on our imagegen → Step1X-3D → CAD pipeline: disclose AI use, document human CAD/finishing work, and photograph every real print before listing. Re-verify wording before relying on it.

**ID:** S96
**Category:** Market report — personalized gifts (SECONDARY / snippet-level, multiple vendors, conflicting)
**Publisher:** The Business Research Company / Technavio / Fortune Business Insights / others (via search results)
**Title:** Personalized gifts market size and Europe share
**Source Date:** 2025/2026 report vintages
**Checked:** 2026-09-04
**Evidence Used:** Read in search results only, **not** confirmed on the publisher pages: global personalized-gifts market growing from USD 30.79 bn (2025) to USD 33.49 bn (2026) at 8.7% CAGR (The Business Research Company); alternative estimate USD 33.70 bn (2025) → USD 69.20 bn (2033) at 9.40% CAGR; a third estimate USD 31,400.22 mn (2025) with ~5.49% CAGR 2026–2035; Technavio headline "grow by USD 10.76 billion". Europe stated as the largest region for personalized gifts in 2025, with one source citing a 51.30% share in 2024. European gift retailing quoted at USD 185.71 bn (2025) → USD 192.61 bn (2026). The wide spread (5.49%–9.40% CAGR) shows these are vendor estimates with incompatible definitions.
**URL:** https://www.thebusinessresearchcompany.com/report/personalized-gifts-global-market-report ; https://www.technavio.com/report/personalized-gifts-market-size-industry-analysis
**Used For:** Category-level justification for the personalization/keepsake half of the portfolio (custom figures, portrait-style busts, anniversary pieces), and for Europe being the leading region. Directional only; conflicting numbers, must not be quoted as fact.

**ID:** S97
**Category:** Custom-figurine service pricing (SECONDARY / snippet-level)
**Publisher:** Hero Forge (Sky Castle Studios) — product pages read via search results only
**Title:** Hero Forge custom miniature and statuette price points
**Source Date:** current pricing at retrieval
**Checked:** 2026-09-04
**Evidence Used:** heroforge.com returned HTTP 403 to direct retrieval; prices below are **UNCONFIRMED SNIPPET VALUES**: Custom Ultra High-Definition Color Plastic Miniatures from US$59.99; Custom Color Statuette from US$99.99 with price "based on overall size and complexity of the design"; Custom Steel Miniatures from US$49.99. Colour is printed directly onto the figure during printing. EUR equivalents and shipping to DE are **UNVERIFIED**.
**URL:** https://heroforge.com/content/product-information/about-products/custom-ultra-high-definition-color-plastic-miniatures/ ; https://heroforge.com/content/product-information/about-products/custom-color-statuette/
**Used For:** Upper price ceiling reference for the custom-figure category — a full-colour custom statuette clears the ~US$100 mark, which supports premium positioning for a personalised human-figure product. Re-verify before any competitive claim.

### Sources attempted and NOT obtained (do not cite)
- Etsy Seller Handbook "Seller Trend Report: Spring and Summer 2026" — https://www.etsy.com/seller-handbook/article/1473931456647 — HTTP 403. **Etsy trend figures: UNVERIFIED.**
- Etsy listing prices in EUR (figurines, busts, planters, lamps) — etsy.com and etsy.com/de-en both HTTP 403. **All EUR Etsy prices: UNVERIFIED.**
- EUR-Lex full text of Regulation (EU) 2023/988 (HTML and PDF, EN) — empty body / HTTP 202 challenge on every attempt.
- Commission GPSR Guidelines (Nov 2025) PDF — HTTP 403.
- Low Voltage Directive 2014/35/EU official page, EU AI Act Art. 50, EN 15493/EN 15494 candle standards, EN 60598 luminaires — **not retrieved. All electrical/candle/AI-Act specifics below are UNVERIFIED and must be checked before any product claim.**
- Printables contest pages and MakerWorld contest/year-in-review pages (HTML) — HTTP 403. **Contest results: UNVERIFIED.**
- Google Trends, Amazon best-seller ranks, Thangs statistics — not retrieved. **UNVERIFIED.**
- German/EU-specific consumer survey data (Destatis, GfK) — not retrieved. **UNVERIFIED.**

---

## SECTION 2 — PRICE OBSERVATIONS

**Honest headline: no EUR retail price was verified on a live page this session.** Etsy and eBay.de both refused
automated retrieval. Everything below is labelled by evidence strength. Do not build a published price list on
the UNVERIFIED lines without re-checking.

| Item | Observed / reported range | Currency as read | Evidence strength | Source |
|---|---|---|---|---|
| Custom full-colour statuette (service, ~portrait scale) | from 99.99 | USD | UNCONFIRMED snippet (403 on page) | S97 |
| Custom colour plastic miniature (service) | from 59.99 | USD | UNCONFIRMED snippet | S97 |
| Custom steel miniature (service) | from 49.99 | USD | UNCONFIRMED snippet | S97 |
| Printed custom bust / portrait figurine on Etsy | 30.99–142.24 (sale prices 50.05, 60.00, 88.06 seen in snippets) | USD | UNCONFIRMED snippet; **no EUR observed** | (Etsy — not obtained) |
| Printed planter / plant pot on Etsy | 16.50–25.00 | USD | UNCONFIRMED snippet; **no EUR observed** | (Etsy — not obtained) |
| Printed decor (watering-can pot) | 5.85 | GBP | UNCONFIRMED snippet | (Etsy — not obtained) |
| Printed lamp / light object, EUR retail | — | — | **UNVERIFIED** | — |
| Digital STL, premium bust/figurine sculpt | 5.79–15.00 | USD | UNCONFIRMED snippet; one Cults3D page read directly (free model) | S92 |
| Digital STL, flexi/character single file | 3.84–4.41 | USD | UNCONFIRMED snippet | S92 |
| Digital STL bundles (100s–1000s of files) | 3.13 (GBP) / 4.00 (USD) | GBP/USD | UNCONFIRMED snippet | (Etsy — not obtained) |
| MakerWorld digital licence terms | "Standard Digital File License" and "BY-NC" observed as the licence strings on 7 lamp-shade models | n/a (no price) | **VERIFIED via API** | S87 |
| Cults3D EUR display to this client | — | — | **UNVERIFIED** (currency shown could not be confirmed as EUR) | S92 |

**Derived pricing guidance (from verified structure, not from a verified EUR figure):**
- Digital files in this category are a **low-single-digit to ~15 unit** product, and free long-tail sculpts earn effectively nothing (Cults3D bust at 6 downloads — S92; Printables generic vases at 44–55 downloads — S86). Differentiation, not volume of uploads, is the lever.
- The **only** verified price-adjacent platform fact is that MakerWorld's top lamp shade drew 1,424 cloud prints vs 0 raw-file downloads (S87) — i.e. on MakerWorld the monetisable event is the *print*, not the file download. Model the revenue path accordingly.
- Personalised/custom human figures are the segment where a three-figure ticket is plausible (S97, category support S96), whereas planters/vases sit in the low-to-mid-two-figure band (snippet-level only).
- **Action before pricing sign-off: re-scrape 20–30 Etsy DE listings with a browser session to establish real EUR bands.**

---

## SECTION 3 — COMPLIANCE FLAGS

- **GPSR applies to every decor item we sell to EU consumers.** Regulation (EU) 2023/988 on general product safety was adopted 10 May 2023 (OJ L 135, 23.5.2023), repeals Directive 2001/95/EC and Council Directive 87/357/EEC, and its supporting OJ publications began 13 December 2024; harmonised standards are listed via Commission Implementing Decision (EU) 2026/901. [S93]
- **EU responsible person + traceability marking on the product itself.** Reported (article wording not yet verified against the OJ): no product may be placed on the market without an economic operator established in the Union responsible for it (Art. 16); products must carry a type/batch/serial identifier plus the manufacturer's name/trade name and postal **and** electronic address, and the responsible person's contact details, on the product, packaging, parcel or accompanying document (Arts. 9(5), 9(6), 16(3)). Practical consequence: every SKU needs an embossed/labelled ID and our DE address — which fits the existing metriMade release-marking step. **Re-verify on EUR-Lex before publishing.** [S94, S93]
- **Distance-selling disclosure in every online offer.** Reported for Art. 19: the online offer must show the manufacturer's (or EU authorised representative's) name and contact details, product identification information including a product image, and any warnings/safety information; marketplaces must register on Safety Gate and maintain a single contact point. Warnings must reach the German consumer in German. **UNVERIFIED wording.** [S94]
- **No food-contact claim, ever.** FDM parts are layered, porous and non-cleanable; we make **no** food, drink, oral, plant-edible or cosmetic-contact claim on any vase, planter, bowl, organizer or figurine, and we do not use food-contact symbols. **No EU food-contact regulation page (Reg. (EC) 1935/2004) was retrieved this session — the specific legal citation is UNVERIFIED**, but the commercial rule stands as a hard product constraint.
- **No electrical product, no flame product.** Lamp concepts ship as **passive shades/diffusers only**, with no bulb, socket, driver, wiring or battery included and no lumen/IP/insulation claim — that keeps us out of the Low Voltage Directive / EMC / RoHS / luminaire-standard perimeter. Candle-holder concepts are specified for **LED tea lights only**, explicitly labelled "not for open flame / not for real candles", because PLA/PETG soften well below flame temperature. **Official LVD 2014/35/EU, EN 60598 and EN 15493/15494 pages were NOT retrieved — these limits are self-imposed engineering policy, legal citations UNVERIFIED.**
- **AI-content transparency is a platform gate, not just an ethics point.** MakerWorld reportedly requires disclosure of AI tools used, how AI output was incorporated and the extent of human involvement; rejects work that is primarily AI-generated with minimal human input; forbids passing AI work off as fully human-made; and requires at least one **real printed photo** matching the uploaded file. Our imagegen → Step1X-3D → CAD chain must therefore be documented per SKU and every listing must carry a real print photo. **Wording UNCONFIRMED (403).** EU AI Act Art. 50 transparency duties were **not verified** this session. [S95]
- **Portfolio-level IP hygiene (evidence-driven).** The highest snippet-level figurine numbers on both platforms are licensed characters (Witcher, Star Wars, Pokémon, Minecraft) [S91], and Cults3D's front page is dominated by fan art [S92]. Those numbers are structurally unavailable to us: all 28 concepts below are original or public-domain-inspired, with no recognisable real person and no licensed IP.

---

## SECTION 4 — PRODUCT CONCEPTS (28)

Pipeline for all: single isolated AI product image → Step1X-3D image-to-3D → CAD finishing (hollowing, wall
thickness, flat base, interfaces, marking). All within 220 x 220 x 250 mm FFF. No licensed IP, no recognisable
real person, no food-contact claim, no electrical or open-flame claim.

### A. Human figures, figurines, busts, humanoid statues (14)

**A1 — Asana Bookend Pair**
- One-line description: Two abstracted yoga figures in mirrored forward-fold poses, each with a weighted flat foot forming a bookend.
- Customer job: Hold a small shelf of books upright while signalling a yoga/wellness identity.
- Trend signal sentence: Household/functional models were MakerWorld's fastest-growing 2025 category [S88]; functional vessels far outperform plain sculpture in verified download counts [S86].
- Target segment: Yoga and wellness practitioners, 25–45, self-gift and studio gifting.
- Approx. size: 110 x 90 x 180 mm (per figure)
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Needs a sand/ballast cavity plus a rubber foot pad to actually resist book load; thin extended limbs are the print-failure point — keep limbs merged to the torso.

**A2 — Climber Wall Hook**
- One-line description: A stylised climber figure reaching upward, its extended arm forming a coat or keys hook, mounted on a rock-texture backplate.
- Customer job: Hang keys or a jacket by the door with a hobby-signalling object instead of a plain hook.
- Trend signal sentence: Functional decor is the verified out-performer on Printables (parametric self-watering planter 4,744 downloads vs 44–55 for generic vases) [S86]; household models fastest-growing on MakerWorld [S88].
- Target segment: Climbers and boulderers, 20–40; hobby gifting.
- Approx. size: 120 x 60 x 200 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Cantilever load on the arm; needs a CAD-added internal rib and screw/keyhole mounts, with a stated max load and no adhesive-only mounting.

**A3 — Portrait Bust Blank (Personalisation Base)**
- One-line description: A neutral, non-identifiable stylised adult bust on a plinth, engineered as the CAD carrier into which a customer-supplied likeness can be substituted as a made-to-order variant.
- Customer job: Commission a keepsake portrait sculpture as a milestone gift.
- Trend signal sentence: Custom full-colour statuette services start at US$99.99 [S97, unconfirmed snippet] and Europe is reported as the largest personalized-gifts region [S96]; verified bust downloads stay modest (267–837) [S86], so this is a made-to-order margin play, not a volume file.
- Target segment: Milestone gift buyers (birthday, retirement, memorial), 35–65.
- Approx. size: 130 x 120 x 220 mm
- Type: SCULPTURE_ONLY
- Main risk/limit note: Any customer-supplied likeness makes it a portrait of a real person — requires written consent and a documented data/deletion policy; base concept must ship non-identifiable.

**A4 — Guitarist Silhouette Cable-and-Pick Dock**
- One-line description: Seated musician figure with a hollow body volume that holds picks, plus a slotted base that manages a cable or strap.
- Customer job: Keep guitar picks and a cable tidy on a desk or amp.
- Trend signal sentence: Only category-level evidence: decorations and sculptures are named MakerWorld categories and household/hobby models led 2025 growth [S88]; occupation/hobby figurines are not separately quantified — treat as inferred [S91].
- Target segment: Hobby guitarists, 18–50.
- Approx. size: 130 x 110 x 165 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: The instrument neck is the fragile overhang — merge it into the body or split as a keyed sub-part; no brand-shaped instrument silhouettes.

**A5 — Chef Figure Utensil Rest**
- One-line description: A rounded chef figure whose outstretched arms cradle a removable, wipe-clean rest tray for a spoon or spatula handle.
- Customer job: Park a cooking utensil beside the hob without messing the worktop.
- Trend signal sentence: Category-level only: household models were MakerWorld's fastest-growing 2025 category [S88] and functional models dominate verified counts [S86].
- Target segment: Home cooks, 25–60; kitchen gifting.
- Approx. size: 140 x 110 x 150 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: **Food-contact adjacency is the core risk** — the tray must be sold as a handle rest with an explicit "no food contact, not dishwasher safe, keep away from hob heat" statement, and PLA is unsuitable near heat (specify PETG). [S94 GPSR warnings duty]

**A6 — Gardener Figure Seed-Packet Holder**
- One-line description: A kneeling gardener figure with a slotted back panel that files upright seed packets or plant labels.
- Customer job: Keep seed packets and plant tags sorted on a potting bench or windowsill.
- Trend signal sentence: Planters and gardening decor are the highest-volume verified decor niche (self-watering planter 4,744 downloads, 41 makes) [S86]; snippet-level MakerWorld planters reach 5-figure downloads [S91, unconfirmed].
- Target segment: Balcony and allotment gardeners, 30–65.
- Approx. size: 150 x 90 x 160 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: No soil/water contact claim; if used outdoors, PLA will creep and yellow — specify indoor/PETG only.

**A7 — Caregiver Hands Ring & Watch Dish**
- One-line description: A pair of abstracted cupped human hands forming a shallow dish, on a low plinth.
- Customer job: Drop rings, a watch or a badge in one place at the end of a shift.
- Trend signal sentence: "Heirloom jewelry" +45% and "maximalist accessories" +105% in Pinterest Predicts 2026 [S89]; jewellery/trinket trays are a named decor use and functional forms out-download plain sculpture [S86].
- Target segment: Nurses, carers and shift workers, 22–55; thank-you gifting.
- Approx. size: 150 x 130 x 70 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Must not be framed as a medical or professional-association product; no occupational logos or uniform insignia.

**A8 — Gamer Headset Stand (Seated Figure)**
- One-line description: A seated, hooded abstract human figure whose raised knees and shoulders form a padded-contact headset cradle.
- Customer job: Store a gaming headset on the desk without it collapsing or scratching.
- Trend signal sentence: "Nostalgia toys" +225% and "1970s childhood toys" +125% in Pinterest Predicts 2026 [S89]; desk/organizer function aligns with the verified functional-model advantage [S86] and MakerWorld's fastest-growing household category [S88].
- Target segment: PC and console gamers, 16–35.
- Approx. size: 130 x 130 x 240 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Top-heavy; needs a wide ballasted base and a headband contact radius that will not dent foam. No game or console IP in the silhouette.

**A9 — Classical Draped Torso (Public-Domain-Inspired)**
- One-line description: An original headless draped torso in a classical antique idiom, on an integrated square plinth.
- Customer job: Add an art-history-coded focal object to a shelf or console.
- Trend signal sentence: Verified classical-sculpture demand exists but is modest (Aphrodite bust 837 downloads, rating 4.56/9 ratings; antique-style busts 267–602) [S86]; Pinterest 2026 "Neo Deco" and "Opera Aesthetic" support a formal-classical mood ("masquerade decor" +40%) [S89].
- Target segment: Interior-styling buyers, 28–55.
- Approx. size: 130 x 110 x 250 mm
- Type: SCULPTURE_ONLY
- Main risk/limit note: Must be an original sculpt in the classical *style* — do not scan or re-use a museum scan whose licence restricts commercial use; large smooth surfaces expose layer lines, so plan a surface texture.

**A10 — Abstract Ribbon Figure (Vase-Mode Human Form)**
- One-line description: A single continuous ribbon abstraction of a standing human body, printed as a thin spiralised shell.
- Customer job: Get a large, cheap-to-print sculptural statement piece for a shelf.
- Trend signal sentence: Vase-mode/spiralised decor is the strongest verified niche in this study — MakerWorld "Lamp Shade 4.0 - Spiralvase" logged 1,424 prints, 2,601 downloads and 4,647 collections [S87].
- Target segment: Design-led decor buyers, 25–45; also a low-cost print-farm SKU.
- Approx. size: 120 x 100 x 250 mm
- Type: SCULPTURE_ONLY
- Main risk/limit note: Single-wall shells are fragile and cannot overhang much; the form must be designed for a continuous, self-supporting spiral path with a widened foot.

**A11 — Two-Figure Anniversary Topper (Non-Identifiable)**
- One-line description: A pair of faceless, stylised embracing figures on a slim removable spike base, sized for a cake or a keepsake plinth.
- Customer job: Mark a wedding or anniversary with a keepsake that outlives the day.
- Trend signal sentence: Europe is reported as the largest personalized-gifts region and the category is growing at 8.7% into 2026 [S96, conflicting vendor estimates]; no platform-level cake-topper figure was verified [S91].
- Target segment: Couples and wedding gift buyers, 25–45.
- Approx. size: 90 x 70 x 150 mm
- Type: SCULPTURE_ONLY
- Main risk/limit note: **Cake use = food contact.** Ship with a separate keepsake plinth and require a food-safe barrier/wrap for any cake placement; label "decorative object, not food-safe, remove before serving". [S94]

**A12 — Runner's Medal Hanger Figure**
- One-line description: A forward-leaning sprinter figure on a wall plate whose trailing arm and back form a multi-medal rail.
- Customer job: Display race medals instead of leaving them in a drawer.
- Trend signal sentence: Category-level only: sports equipment and sculptures are named MakerWorld categories with household/hobby models leading 2025 growth [S88]; functional wall-mounted decor matches the verified functional advantage [S86].
- Target segment: Amateur runners and triathletes, 25–55.
- Approx. size: 200 x 60 x 190 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Cumulative medal weight and leverage — needs CAD-added steel-insert or through-screw mounting and a published max load; no race, club or brand marks.

**A13 — Reading Figure Book Weight**
- One-line description: A curled-up reading figure with a ballast chamber, shaped to sit in the gutter of an open book and hold pages flat.
- Customer job: Keep a cookbook or textbook open hands-free.
- Trend signal sentence: Category-level only: functional household objects both lead MakerWorld's 2025 growth [S88] and dominate verified Printables download counts versus decorative-only models [S86].
- Target segment: Readers, students, home cooks, 20–60.
- Approx. size: 130 x 80 x 90 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Requires a sealed, resealable ballast cavity with a documented non-loose fill; the page-contact face must be smooth and non-marking.

**A14 — Dancer Torso Jewellery Stand**
- One-line description: An armless, elongated dancing torso on a wide dish base, with shoulder and waist profiles that hold necklaces, bracelets and rings.
- Customer job: Store and display everyday jewellery on a dresser.
- Trend signal sentence: Pinterest Predicts 2026 shows "heirloom jewelry" +45%, "maximalist accessories" +105% and "brooch aesthetic" +110% [S89]; jewellery organizers are functional decor, the verified out-performing form [S86].
- Target segment: Jewellery wearers, 20–50; gifting.
- Approx. size: 140 x 140 x 240 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Tall and narrow — the base must be ballasted or widened for tip-over resistance; surfaces contacting metal jewellery need a low-friction finish to avoid scratching plated items.

### B. Trending home decor and viral consumer items (14)

**B1 — Spiral Diffuser Shade (E27 Passive)**
- One-line description: A tall spiralised single-wall lamp shade with an integrated CAD-cut standard socket ring, sold as a passive diffuser only.
- Customer job: Convert a bare bulb into a soft, designed light source.
- Trend signal sentence: Strongest verified decor datapoint in this study: MakerWorld's spiral-vase lamp shade logged 1,424 prints, 2,601 downloads and 4,647 collections; six further vase-mode shades all show live traction [S87]; "pendant lamp" +40% in Pinterest 2026 [S89].
- Target segment: Renters and design-led decor buyers, 22–45.
- Approx. size: 180 x 180 x 220 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: **No bulb, socket, wiring or lumen claim** — passive shade only, LED-only, stated maximum wattage/temperature and minimum bulb clearance; PLA is unsuitable, specify PETG/PCTG. [S94 warnings duty]

**B2 — Neo-Deco Fan-Arch Relief Panel**
- One-line description: A wall panel of stacked fan arches and chevrons in low relief, tileable into a larger field.
- Customer job: Add architectural texture to a bare wall without plaster or paint.
- Trend signal sentence: Pinterest Predicts 2026 "Neo Deco" reports "crisp chevrons, fan arches" with "antique bar cart" +100%, "red marble bathroom" +80%, "brass aesthetic" +35% [S89]; wall decor is a tracked segment of Germany's USD 36.5 bn (2025) home decor market [S90].
- Target segment: Interior decorators and renters, 25–50.
- Approx. size: 200 x 200 x 18 mm (tileable)
- Type: RELIEF_PANEL
- Main risk/limit note: Large flat panels warp and show seams between tiles — needs a ribbed back, a defined interlock, and a supplied alignment/mounting scheme; keep relief depth low to control print time.

**B3 — Adire-Pattern Planter Sleeve**
- One-line description: A slip-over decorative sleeve carrying an African-resist-dye-inspired geometric relief, sized to dress a standard nursery pot.
- Customer job: Make a cheap plastic nursery pot presentable without repotting the plant.
- Trend signal sentence: Pinterest Predicts 2026 "Afrohemian Decor": "afrobohemian home decor" +220%, "motif berbere" +210%, "adire fabric" +130%, "ethiopian art" +50% [S89]; planters are the highest-volume verified decor category [S86, S91].
- Target segment: Plant owners and bohemian-style decorators, 24–45.
- Approx. size: 150 x 150 x 160 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Pattern must be an original interpretation, not a traced textile artwork; needs a documented fit range for common nursery-pot diameters and drainage clearance (no water contact claim).

**B4 — Self-Watering Reservoir Planter (Wick Type)**
- One-line description: A two-part planter with an inner soil cup, a wick channel and a lower water reservoir with a level window.
- Customer job: Keep a houseplant watered through a week away.
- Trend signal sentence: The single best-performing verified decor model family in this study: Printables self-watering planters at 4,744 / 2,479 / 1,055 downloads with 41 and 74 recorded makes [S86], plus 5-figure snippet-level MakerWorld planters [S91, unconfirmed].
- Target segment: Houseplant owners, 22–50.
- Approx. size: 140 x 140 x 160 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Watertightness on FDM is the hard problem — needs validated wall count/material and a leak test in the release gate; explicitly not food-safe and not for edible crops.

**B5 — Iridescent Facet Bud Vase (Dry-Only)**
- One-line description: A faceted, opal-effect bud vase designed for iridescent/silk filament, supplied as a dry-stem or liner-insert vessel.
- Customer job: Show a single stem or dried arrangement as a colour-shifting accent object.
- Trend signal sentence: Pinterest Predicts 2026 "Extra Celestial" reports "opalescent" +115% and "alien core aesthetic" +80% [S89]; vase-mode/spiral vessels are the verified traction leader on MakerWorld [S87].
- Target segment: Design-led decor buyers and gift buyers, 20–40.
- Approx. size: 110 x 110 x 200 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Sell as dry-stem or with a glass/PET liner — do not claim water-tightness; facets must be angled above the self-supporting limit to avoid supports.

**B6 — LED Tea-Light Grotto Holder**
- One-line description: A pierced, layered holder that scatters light from a standard LED tea light through a lattice of organic apertures.
- Customer job: Get candle-like ambience safely in a rental or a child's room.
- Trend signal sentence: Verified lighting/diffuser demand is the strongest decor signal on MakerWorld [S87]; lighting is a tracked segment of the German home decor market (USD 36.5 bn in 2025) [S90].
- Target segment: Ambience and cosy-decor buyers, 20–50.
- Approx. size: 100 x 100 x 120 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: **LED tea lights only** — must carry "not for open flame / not for real candles" on product, packaging and listing, since PLA/PETG soften far below flame temperature. No electrical component supplied. [S94]

**B7 — Insect-Wing Wall Relief Trio**
- One-line description: Three mountable low-relief panels of dragonfly, beetle and moth wing venation, designed as a set.
- Customer job: Fill a wall gap with a nature-motif gallery set at low cost.
- Trend signal sentence: Pinterest Predicts 2026 "Wilderkind" reports "dragonfly nails" +145%, "flower outfit men" +105%, "animal inspired outfits" +90%, "bug jewellery" +60% [S89]; wall decor is a tracked German market segment [S90].
- Target segment: Nature-motif and cottagecore decorators, 25–50.
- Approx. size: 160 x 120 x 12 mm (each of 3)
- Type: RELIEF_PANEL
- Main risk/limit note: Fine venation risks under-extrusion at 0.4 mm nozzle — validate minimum rib width; supply a concealed hanging interface rather than adhesive.

**B8 — Modular Desk Trinket Trays (Stackable "Cute Clutter")**
- One-line description: A family of small nesting trays with rounded organic profiles that stack and interlock into a tower or spread flat.
- Customer job: Corral desk small-stuff (cables, clips, rings, dice) without buying a big organizer.
- Trend signal sentence: Household and tool/storage models led MakerWorld's 2025 category growth [S88]; functional organizers are the verified out-performer versus purely decorative prints [S86].
- Target segment: Desk workers, students, hobbyists, 18–45.
- Approx. size: 120 x 120 x 40 mm (single tray; stack ≤ 240 mm)
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Interlock tolerance must be validated across materials and shrinkage; commodity category — differentiation has to come from the sculpted profile, since generic vessels verifiably flatline [S86].

**B9 — Masquerade Mask Wall Sculpture**
- One-line description: An ornate, original masquerade-style face mask designed as a wall-hung sculpture with a concealed keyhole mount.
- Customer job: Add a dramatic, theatrical focal piece to a wall.
- Trend signal sentence: Pinterest Predicts 2026 "Opera Aesthetic" reports "midnight masquerade" +95%, "opera theatre" +35%, "masquerade decor" +40%, "opera outfits" +55% [S89].
- Target segment: Maximalist and theatrical-style decorators, 25–50.
- Approx. size: 180 x 40 x 230 mm
- Type: SCULPTURE_ONLY
- Main risk/limit note: Must be labelled decorative wall art, **not** PPE or wearable face protection, and not sized/strapped for wear; no carnival-brand or event-brand references.

**B10 — Ribbed Column Pillar Riser**
- One-line description: A heavy-looking fluted column riser that lifts a plant, a lamp or an object, with a load-spreading top plate.
- Customer job: Give a shelf display height and a solid architectural anchor.
- Trend signal sentence: Pinterest Predicts 2026 "Neo Deco" ("brass aesthetic" +35%, "pendant lamp" +40%) supports a heavy geometric idiom [S89]; German home decor market USD 36.5 bn in 2025, forecast USD 53.2 bn by 2034 at 4.28% CAGR [S90]. Brutalist/organic-modern was **not** found as a named 2026 trend — category-level inference only.
- Target segment: Interior stylists and plant owners, 25–50.
- Approx. size: 140 x 140 x 220 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: Must state a real tested vertical load; hollow FDM columns buckle at the top plate, so the CAD step needs internal ribbing rather than solid infill.

**B11 — Jelly-Gloss Fruit Bowl Sculpture (Non-Food)**
- One-line description: A soft, wobbling, translucent-gloss bowl form in the "jelly" idiom, sold as a decorative catch-all.
- Customer job: Have one sculptural bowl by the door for keys, masks and post.
- Trend signal sentence: Pinterest Predicts 2026 "Gimme Gummy" reports "jelly blush" +130%, "jelly candy aesthetic" +100%, "gummy bears aesthetic" +50%, "yokan" +60% [S89].
- Target segment: Trend-led young decor buyers, 18–35.
- Approx. size: 200 x 200 x 90 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: **Named "fruit bowl" reads as food contact — do not use that wording**; sell strictly as a decorative catch-all with a no-food-contact statement. Glossy translucency depends on material and print settings, so appearance must be validated, not promised.

**B12 — Striped Big-Top Pendant Diffuser (Passive)**
- One-line description: A scalloped, striped canopy shade in a circus/big-top idiom, printed in two colours or with a paintable stripe channel, passive only.
- Customer job: Give a child's room or a playful corner a statement light without rewiring.
- Trend signal sentence: Pinterest Predicts 2026 "FunHaus" reports "circus interior" +130%, "vintage circus aesthetic" +70%, "circus nursery" +50%, "striped ceiling" +40% [S89]; lamp shades are the verified traction leader on MakerWorld [S87].
- Target segment: Parents and playful-maximalist decorators, 28–45.
- Approx. size: 210 x 210 x 150 mm
- Type: HYBRID_FUNCTIONAL
- Main risk/limit note: No bulb/socket/wiring supplied, LED-only, stated wattage and clearance limits; a child's-room placement raises small-parts and heat scrutiny under GPSR warnings duties. [S94]

**B13 — Lace-Doily Light Panel**
- One-line description: A translucent panel whose thickness varies to reproduce a lace-doily pattern as a backlit or window-hung luminous relief.
- Customer job: Get a decorative privacy/light-play panel for a window or a niche.
- Trend signal sentence: Pinterest Predicts 2026 "Laced Up" reports "lace doily" +105%, "lace nails" +215%, "lace bandana" +150% [S89]; note Bambu Lab reported ~400,000 lithophanes generated in MakerLab in 2025 (~1 in 6 creations), i.e. the backlit-panel format is popular but crowded [S88].
- Target segment: Cottage/romantic-style decorators, 25–60.
- Approx. size: 200 x 200 x 6 mm
- Type: RELIEF_PANEL
- Main risk/limit note: Thin variable-thickness panels warp and need a frame; heavy competition from generic lithophane generators [S88], so the pattern design and framing are the only differentiators. No electrical parts supplied.

**B14 — Seasonal Ornament Frame System**
- One-line description: One reusable geometric frame plus swappable low-relief insert discs for different seasons and holidays, sold as a base plus insert packs.
- Customer job: Change seasonal decor without storing a box of single-use objects.
- Trend signal sentence: Pinterest Predicts 2026 shows nostalgia demand ("nostalgia toys" +225%, "1970s childhood toys" +125%) [S89]; Printables runs dedicated seasonal contests (Valentine's Classics 2026, Easter 2026) though results pages could not be retrieved [S91 — UNVERIFIED].
- Target segment: Seasonal decorators and gift buyers, 28–60.
- Approx. size: 180 x 180 x 25 mm (frame); inserts 150 x 150 x 8 mm
- Type: RELIEF_PANEL
- Main risk/limit note: Insert tolerance must survive material and colour changes; seasonal motifs must avoid licensed characters and any brand-associated holiday figures, and hanging hardware needs a stated load limit.

---

## Gaps to close before portfolio sign-off
1. **EUR retail prices — the biggest hole.** No Etsy/eBay.de price was read on a live page. Re-run with a real browser session (the `claude-in-chrome` skill) and record 20–30 DE listings per category.
2. **Etsy Seller Trend Report Spring/Summer 2026** — the specified primary source was never opened (403). Retrieve via browser.
3. **GPSR article text** — verify Arts. 9(5)/(6), 16, 19 and Art. 52 application date directly on EUR-Lex before any compliance copy is published.
4. **Electrical / candle / food-contact citations** — LVD 2014/35/EU, EN 60598, EN 15493/15494, Reg. (EC) 1935/2004 all unretrieved; the limits in Section 3 are currently self-imposed policy without legal citations.
5. **EU AI Act Art. 50** and confirmed MakerWorld/Printables AI-disclosure wording — needed because our whole pipeline is AI-assisted.
6. **Mushroom/cottagecore and brutalist motifs did not appear in Pinterest Predicts 2026** [S89]. If those motifs stay in the roadmap, they need their own evidence (Google Trends, platform tag counts) rather than an assumed trend.
7. **German/EU consumer survey data** — none obtained; Destatis/GfK still to do.
