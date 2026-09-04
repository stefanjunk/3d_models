# Source index and review record

## Local business/research inputs

- Founder statement and screenshots supplied 2026-08-24 — legal-operator name, company/service address, managing director, register court/number, VAT ID and intended `JuSt Innovation` / `metriMade` / `metriCreate` naming. Extracted facts are recorded in `business/06-legal-compliance/operator-profile.md`; original chat attachments are not treated as a retained current register extract or tax-authority confirmation.
- Managing-director statement supplied 2026-08-25 — Cloudflare control of `metrimade.com` and `metricreate.com`, descriptive-product-title plus stable-ID policy, and single-person internal governance. Retained provider evidence and signed approvals remain separate gates.
- Founder brand/offer clarification supplied 2026-08-25 — `metriMade` is the premium guided non-technical consumer subset for aesthetic smart decor, space savers and practical home/office integration; `metriCreate` is the broader maker/technical catalog, parameterization and digital-download storefront. The connected-storefront and shared-product/revision architecture is now a binding strategy decision.
- OpenAI-generated `metriMade` and `metriCreate` logo concept sheets dated 2026-08-25 — source copies, hashes, prompts and selection/clearance limits are recorded in `business/01-strategy/logo-concepts/README.md`.

- `research/market/DingGenau_Global_Digital_EU_Print_Business_Report_2026.docx` and PDF — old-name business structure, dual delivery, curated/versioned portfolio and country sequencing.
- `research/market/JuSt_Innovation_3D_Print_Commercial_Product_Matrix_2026.xlsx` — 100 research concepts and preliminary commercial fields; concept selection is not product release evidence.
- `research/market/MetriMade_International_Naming_Report_2026.md` — MetriMade naming direction.
- `research/market/Namensrecherche_MetriCreate_Metreation_2026.md` — MetriCreate naming direction.
- `research/market/bericht-top20-alltags-organizer-kleine-wohnraeume.md` — small-space/everyday concept ranking.
- `research/market/bericht-top20-fdm-massanfertigung.md` — later mass-customization opportunities.
- `research/market/bericht-top20-systemmoebel-zubehoer-ikea.md` and `products/furniture-systems/` — system-furniture concepts and their self-contained product packages.
- legacy task/plan files throughout `research/market/` — reviewed as inputs; superseded for execution by `business/07-roadmap/`.

## Additional product-idea research checked 2026-08-27

- `S31` — Ingka Group / IKEA, [IKEA Store & Organise Report 2026](https://www.ingka.com/newsroom/new-global-ikea-study-nearly-4-in-10-are-staging-a-silent-protest-over-household-mess/): a 31-market survey of 31,488 people; directional problem evidence for catch-all drawers, charger search, countertop clutter, sentimental storage and smaller-space organization.
- `S32` — Etsy, [How to Spot Trends and Keywords With Marketplace Insights](https://www.etsy.com/seller-handbook/article/1404564905677): the official follow-up method for comparing current search demand and listing competition before selecting any research concept.
- `S33` — The Michaels Companies, [Michaels 2026 Creativity Trend Report](https://www.prnewswire.com/news-releases/michaels-unveils-2026-creativity-trend-report-revealing-a-shift-towards-creative-living-in-the-analog-era-302709301.html): directional retailer search, sales and survey signals for analog hobbies, sewing, needlepoint, journaling and group crafting.
- `S34` — eBay Inc., [2025 Recommerce Report](https://www.ebayinc.com/recommerce-report/): directional evidence for passion-led collecting, trading cards, antiques, recommerce and hobby reconnection across nine surveyed markets including Germany.
- `S35` — RIAA, [2025 Year-End Recorded Music Revenue Report](https://www.riaa.com/wp-content/uploads/2026/03/RIAA-Year-End-Revenue-2025.pdf): US physical-media signal reporting continued vinyl growth; not a Germany demand estimate.

The full row-level source records are in `business/02-portfolio/research-idea-sources-additions.csv`. Source IDs `S01`–`S30` remain defined in the `Sources` sheet of the retained legacy research workbook. All trend values are research hypotheses, not proof of German conversion, price or product-market fit. The common 200-idea ranking, evidence-confidence cap, weighting, and tier gates are documented in `business/02-portfolio/implementation-priority-scoring.md`.

## Generative Step1X-3D product research checked 2026-09-04

Source records `S84`–`S130` in `business/02-portfolio/research-idea-sources-additions.csv` back the
100 generative research concepts `SKU-315`–`SKU-414`. The raw research files, the raw Printables API
response and the provisional-to-registered source-ID remapping are archived in
`research/market/step1x-generative-batch-2026-09-04/`.

- Platform demand was read from the platforms' own public APIs, not from search results: `S84` and
  `S110` (Printables GraphQL: animals category, decor and bust models), `S94` and `S102` (Printables
  fidget and functional models plus the 1,385,663-model platform counter), `S85`, `S103` and `S111`
  (MakerWorld design API: dragons, tool and cable systems, lamp shades). Search-engine snippets were
  excluded after they were shown to overstate counts by more than an order of magnitude (`S85`).
- Category and market context: `S88` (Hasbro Q2 2026 filing), `S89` (Games Workshop FY2026 results),
  `S100` (Circana 2025 US toy sales), `S101` (fidget market sizing, secondary), `S114` (Germany home
  decor market, secondary), `S120` (personalized gifts, secondary and conflicting), `S90` (Etsy
  Spring/Summer 2026 trend report), `S113` (Pinterest Predicts 2026), `S96`/`S104` (Bambu Lab
  ecosystem statistics, secondary), `S97`/`S105` (Printables Awards 2025).
- Rights and platform rules: `S92` (MakerWorld community guidelines including the AI-flagging duty),
  `S87` (Cults3D NoAI policy and paid price points), `S93` (rightsholder enforcement precedent),
  `S119` (MakerWorld AI-disclosure and real-print-photo rules, snippet-level).
- Compliance: `S98`/`S99` (EU toy-safety framework and the 2026/2030 Regulation (EU) 2025/2509
  timeline), `S117` (GPSR identification), `S118` (GPSR article detail, snippet-level and flagged for
  re-verification).
- Generative tooling: `S122`–`S124` (Step1X-3D repository, paper and model card), `S125`/`S126` (the
  retained Tencent Hunyuan non-commercial headers and that licence's exclusion of the European
  Union), `S127` (CreativeML Open RAIL++-M pass-through duty), `S128`–`S130` (printability guidance
  and AI-mesh failure modes behind the mandatory mesh-quality gate).

Evidence limits are recorded per record. EUR-Lex article text, the EU AI Act transparency article and
its application date, US and EU copyright guidance on AI output, most platform AI policies, EUR retail
prices and German DIY or consumer survey data were **not** retrieved in this pass and are marked
UNVERIFIED; none of them may be cited in customer-facing or compliance copy until confirmed. The
Step1X-3D licence conflict recorded in `S125` and `S126` is treated as a blocking commercial gate for
the whole `SKU-315`–`SKU-414` block, not as a note.

## Model review scope

All workspace model-bearing top-level/product folders were classified at family level, with individual rows for all 20 system-furniture concepts. Stronger project evidence was reviewed for DrawerFit, Modern Carbon Desk Organizer, over-toilet shelf, toilet-paper system, CyberVault, system furniture, wall shelf, hair clip, barefoot shoe, printer enclosure, camera arm, toy popper, flapping submarine, rainwater filter, labyrinth box and dice tower.

The inventory pruned every product directory named `external`/`external_models` as required. Raw meshes and folders without direct provenance/status evidence remain `UNKNOWN`/blocked; the review did not infer ownership from filesystem location.

## Website input

- Repository: `/workspace/Website/metrimade-store`.
- Business review snapshot: supplied main commit `1c75c8b0389d7aa7a57051bda8f11591906d9935`.
- The local checkout was on `17fab9f` with uncommitted work; it was inspected read-only and not changed.
- Reviewed topics: README/runtime flags, catalog/operator/publishing model, routes, legal profile, launch checklist, package scripts and absence of CI workflow at the supplied main snapshot.
- User-provided launch-readiness findings were cross-checked and incorporated into the focused backlog.

## Current official legal/compliance sources

- Germany [DDG § 5](https://www.gesetze-im-internet.de/ddg/__5.html).
- BZSt [public W-IdNr. assignment notice](https://www.bzst.de/SharedDocs/Downloads/DE/WIdNr/oeffentliche_bekanntmachung_widnr.pdf?__blob=publicationFile&v=1).
- DPMA [goods/services classification guidance](https://www.dpma.de/marken/klassifikation/waren_dienstleistungen/index.html) and [Nice Classification 2026](https://www.dpma.de/marken/klassifikation/waren_dienstleistungen/nizza/).
- Germany [BGB](https://www.gesetze-im-internet.de/bgb/BJNR001950896.html), including current withdrawal/contract-confirmation provisions.
- Germany [BFSG § 3](https://www.gesetze-im-internet.de/bfsg/__3.html).
- EU [General Product Safety Regulation 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj/eng).
- EU [Product Liability Directive 2024/2853](https://eur-lex.europa.eu/eli/dir/2024/2853/oj/eng).
- European Commission [VAT One Stop Shop](https://europa.eu/youreurope/business/finance-and-tax/vat/one-stop-shop/index_en.htm).
- Germany ZSVR [Shipping and online retail](https://www.verpackungsregister.org/en/topics/shipping-and-online-retail).

These links support issue spotting only. Record counsel/adviser names, checked dates and approved document versions in the launch evidence.

## Evidence quality labels used

- **Direct:** project report/manifest/source or official primary source.
- **Reported:** a project document records a user/physical result but raw test evidence was not re-run.
- **Research hypothesis:** scored concept, price, trend or market assertion without local demand proof.
- **Unknown:** evidence not found in the reviewed repository; blocks the applicable release gate.
