# Portfolio field-completeness review

Review date: 2026-09-04 (previous review 2026-09-01). Scope: the 580-row `Portfolio` worksheet in `product-portfolio.xlsx` after regeneration from the version-controlled sources. The row count rose from 423 on 2026-09-04, first when the 57 named-interface R3 variants SKU-501–557 were appended for the ten highest trend-score records, then when the 100 generative Step1X-3D concepts SKU-315–414 were added with their own modeled unit-economics block.

## Completed in the 2026-09-01 review

| Check | Before | After | Result |
|---|---:|---:|---|
| Research ideas without `Trend_Score_0_100` | 100 of 314 | 0 of 314 | All research ideas now have a numeric, reproducible directional score. |
| Product directories without the shared master classification/status fields | 9 of 108 | 0 of 108 | The nine previously unregistered rows now have category, origin, strategy, lifecycle, commercial state, offers, website state, priority and next gate. |
| Blank or duplicate `Working_SKU` | 0 of 422 | 0 of 422 | All 422 values remain populated and unique. |
| Missing `Next_Gate` | 9 product rows | 0 of 422 | Existing preflight/readiness evidence was used for the nine product rows. |

The SKU-101–200 trend score is the documented sum of primary-source strength (0–30), signal magnitude (0–30), metriMade strategy fit (0–25), and nonduplicate portfolio whitespace (0–15). Every row retains the four components, a readable basis, the assessment date/version, and `DIRECTIONAL PLANNING SCORE — NOT VALIDATED DEMAND`. The range is 48–99; low-evidence ideas were deliberately left low instead of being forced above a target.

The main directional evidence is the Germany-inclusive 31-market [IKEA Store & Organise Report 2026](https://www.ingka.com/newsroom/new-global-ikea-study-nearly-4-in-10-are-staging-a-silent-protest-over-household-mess/), the [Michaels 2026 Creativity Trend Report](https://www.prnewswire.com/news-releases/michaels-unveils-2026-creativity-trend-report-revealing-a-shift-towards-creative-living-in-the-analog-era-302709301.html), the nine-market [eBay Recommerce Report](https://www.ebayinc.com/recommerce-report/), the [RIAA 2025 year-end report](https://www.riaa.com/wp-content/uploads/2026/03/RIAA-Year-End-Revenue-2025.pdf), [Pinterest Predicts 2026](https://business.pinterest.com/pdf/pinterest-predicts/2026-trend-report/), and the [Etsy Spring/Summer 2026 trend report](https://www.etsy.com/seller-handbook/article/1473931456647). Compliance, material and printer sources do not increase a trend score.

## Completed in the 2026-09-04 review — one sortable planning scale

| Check | Before | After | Result |
|---|---:|---:|---|
| Product directories without `Trend_Score_0_100` / `Priority_Score_0_100` | 72 of 109 | 0 of 109 | Every product now carries the same two 0–100 planning scores as the research queue. |
| Product directories without `Opportunity_Score_0_100`, `Risk_Score_1_5` and the ten 1–5 components | 109 of 109 | 0 of 109 | The full 14-field comparison block is populated, numeric and sortable for all 423 rows. |
| Rows where the 14 fields carry no recorded basis | 109 of 109 | 0 of 109 | `Score_Basis`, `Trend_Score_Basis`, `Scoring_Rationale` and `Score_Status` now sit beside the scores for both record types. |

`business/tools/score_product_directories.py` produces `product-directory-scoring.csv`, and the workbook joins it as the product-row fallback for the 14 fields. Two routes exist and each row states which one it used:

- **37 inherited.** A product mapped to a research idea inherits that idea's recorded trend, priority, opportunity, risk and ten components unchanged. `Score_Basis` names the exact SKU.
- **72 derived.** Every other product is scored from its own documented repository evidence: the live `preflight/preflight-result.json` C/R/K scorecard and its eleven complexity dimensions, plus the product register's strategy fit, rights/provenance state, safety-risk note, model status, offer modes and product-family size.

The derived trend deliberately avoids a portfolio-wide category average. Each product category is mapped once, in a reviewable table, to the research family whose recorded primary sources cover the same customer job — the twenty named host-furniture inserts to `Named-system furniture organization`, the printer and workshop items to `3D-printer workshop organization`, the wall reliefs to `3D wall art, reliefs & gallery panels`, and so on. The family median then receives a strategy-fit adjustment that re-approximates the documented 0–25 metriMade-fit trend component. A category with no primary-source research family — generic decorative meshes, powered toys, RC/FPV vehicles, the mini ROV, wearables, the rainwater system, the diffuser concept — is stated as `NO PRIMARY-SOURCE RESEARCH FAMILY` and starts from a baseline of 35, below every scored research family. Those rows therefore sort to the bottom on trend instead of borrowing a signal they do not have.

`Priority_Score_0_100` uses the unmodified research weighting, so both record types remain directly comparable. Two limits are enforced in code for **derived** rows: `Market_Evidence_Confidence_1_5` can never exceed 3, because no product has validated sales or repository physical evidence; and `Economics_1_5` is labelled in every rationale as a complexity and purchased-content proxy, because no product COGS or price is recorded yet. An inherited row keeps the mapped research idea's own recorded confidence, which reaches 4 for six products. A derived score orders planning work only and never overrides current Lane E, `HOLD`, `CONCEPT_ONLY` or a release gate.

## Deliberately not fabricated

- Product trend and priority for the 72 derived rows remain **family-directional, not product-specific demand**. The score is reproducible from cited family sources and the product's own preflight, but no product row claims its own validated demand, and derived product evidence confidence stays capped at 3. Use trend for the market question and priority for the implementation question; do not average them with C/R/K.
- `Trend_Score_Basis` is empty for SKU-001–100. Those legacy research rows predate the four-component trend screen and their source register records no basis text; the workbook shows their actual score rather than a reconstructed justification.
- Product-directory comparison fields for dimensions, material, mass, print time and unit economics remain blank in the canonical comparison block unless a controlled representative variant supplies them. A directory can contain several variants, so a convenient mesh bounding box is not automatically a commercial product dimension.
- Detailed research economics remain absent for 271 of 471 ideas. The 100 generative Step1X rows SKU-315–414 now carry a modeled mass, print time, hands-on time, cost breakdown, price and contribution margin computed on the retained Unit Economics rates; those values are modeled planning figures, not a weighed part, a measured print or a quotation. The newer rows retain the recorded price bands, dimensions, materials, support and difficulty, but COGS, mass, machine time and margin require a specific geometry and exact process.
- Explicit R-component fields remain absent for SKU-001–200 because those older ideas have only preliminary or mapped-product preflight evidence. The workbook retains their actual C/R/K/lane result and evidence boundary rather than reverse-engineering R components.
- Lifecycle, commercial-existing and website fields are product-register concepts and are therefore intentionally empty for research-idea rows. Implementation and decision-tier fields are research-queue concepts and are intentionally empty for product-directory rows.

## Reproduction and checks

```bash
python business/tools/score_research_additions_trends.py
python business/tools/score_research_additions_trends.py --check
python business/tools/score_research_ideas.py
python business/tools/score_research_ideas.py --check
python business/tools/build_research_preflight_estimates.py
python business/tools/build_research_preflight_estimates.py --check
python business/tools/build_readiness_advancement_register.py
python business/tools/build_readiness_advancement_register.py --check
python business/tools/score_product_directories.py
python business/tools/score_product_directories.py --check
python business/tools/build_product_workbook.py
python business/tools/validate_portfolio_preflight_overlay.py
```

The final validator rebuilds the expected `Portfolio` tab from the sources and requires an exact match: 580 rows, 580 unique populated working SKUs, 471 research ideas, 109 product directories, complete product-scoring coverage, stable raw-source joins, and exactly 6 worksheets.
