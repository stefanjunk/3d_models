# Portfolio field-completeness review

Review date: 2026-09-01. Scope: the 422-row `Portfolio` worksheet in `product-portfolio.xlsx` after regeneration from the version-controlled sources.

## Completed in this review

| Check | Before | After | Result |
|---|---:|---:|---|
| Research ideas without `Trend_Score_0_100` | 100 of 314 | 0 of 314 | All research ideas now have a numeric, reproducible directional score. |
| Product directories without the shared master classification/status fields | 9 of 108 | 0 of 108 | The nine previously unregistered rows now have category, origin, strategy, lifecycle, commercial state, offers, website state, priority and next gate. |
| Blank or duplicate `Working_SKU` | 0 of 422 | 0 of 422 | All 422 values remain populated and unique. |
| Missing `Next_Gate` | 9 product rows | 0 of 422 | Existing preflight/readiness evidence was used for the nine product rows. |

The SKU-101–200 trend score is the documented sum of primary-source strength (0–30), signal magnitude (0–30), metriMade strategy fit (0–25), and nonduplicate portfolio whitespace (0–15). Every row retains the four components, a readable basis, the assessment date/version, and `DIRECTIONAL PLANNING SCORE — NOT VALIDATED DEMAND`. The range is 48–99; low-evidence ideas were deliberately left low instead of being forced above a target.

The main directional evidence is the Germany-inclusive 31-market [IKEA Store & Organise Report 2026](https://www.ingka.com/newsroom/new-global-ikea-study-nearly-4-in-10-are-staging-a-silent-protest-over-household-mess/), the [Michaels 2026 Creativity Trend Report](https://www.prnewswire.com/news-releases/michaels-unveils-2026-creativity-trend-report-revealing-a-shift-towards-creative-living-in-the-analog-era-302709301.html), the nine-market [eBay Recommerce Report](https://www.ebayinc.com/recommerce-report/), the [RIAA 2025 year-end report](https://www.riaa.com/wp-content/uploads/2026/03/RIAA-Year-End-Revenue-2025.pdf), [Pinterest Predicts 2026](https://business.pinterest.com/pdf/pinterest-predicts/2026-trend-report/), and the [Etsy Spring/Summer 2026 trend report](https://www.etsy.com/seller-handbook/article/1473931456647). Compliance, material and printer sources do not increase a trend score.

## Deliberately not fabricated

- Seventy-one current product directories still have no product-level trend or priority score. Thirty-seven receive those values through an explicit implemented-research mapping. The remaining products have no equally strong product-specific or explicitly mapped source; copying a category average would look precise but would not be product evidence.
- Product-directory comparison fields for dimensions, material, mass, print time and unit economics remain blank in the canonical comparison block unless a controlled representative variant supplies them. A directory can contain several variants, so a convenient mesh bounding box is not automatically a commercial product dimension.
- Detailed research economics remain absent for 214 of 314 ideas. The newer rows retain the recorded price bands, dimensions, materials, support and difficulty, but COGS, mass, machine time and margin require a specific geometry and exact process.
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
python business/tools/build_product_workbook.py
python business/tools/validate_portfolio_preflight_overlay.py
```

The final validator requires exactly 422 rows, 422 unique populated working SKUs, 314 research ideas, 108 product directories, stable raw-source joins, 6 worksheets, and no shifted source-row pointers.
