# Research-idea implementation priority

Status: planning model plus 3D-preflight, readiness-advancement and product-directory scoring overlay reviewed 2026-09-04. Priority-scoring version: `1.2`; preflight-estimate version: `1.2`; SKU-101–200 trend-screen version: `1.0`; product-directory scoring version: `1.0`.

This model orders all 471 research ideas for **what to finish, validate, or consider building next**. It does not approve a product for sale, replace the product lifecycle gates, or prove demand, price, margin, rights, safety, or German product-market fit.

Since 2026-09-04 the same scale also covers all 109 product directories, so the leading `Portfolio` tab can be sorted and filtered on one column across both record types. See "Product-directory scores" below.

The ordered source is `research-idea-priority.csv`; the generated workbook joins it into the leading `Portfolio` tab together with all product directories, idea sources, unit economics and readiness advancement in one 580-row filterable list. Every row has one unique `Working_SKU`; redundant record/mapping identifiers and the duplicate `Product Register` worksheet are omitted. The prior 99-row curated product source remains version-controlled in `product-portfolio.csv`.

## 3D-preflight planning overlay

The workbook keeps market potential and implementation feasibility separate. `Research Ideas 100`, `Research Ideas +100`, `Research Ideas +200`, `Research Variants R3`, and `Implementation Priority` therefore show a compact preflight field beside the opportunity, trend, and market-fit fields:

`C# · R# · K# · Lane X · CONFIDENCE`

- The 37 research rows mapped to a current product use that product's exact documented preflight scorecard and link its `preflight/preflight-result.json`.
- The 163 ideas without a mapped product are explicitly marked `PRELIMINARY IDEA ESTIMATE — NOT RELEASE APPROVAL`.
- For those preliminary rows, the C band is derived conservatively from the existing creation- and validation-effort estimates; the K band uses the existing research-risk value only as a broad proxy. It is not a safety qualification.
- An unstarted idea remains `R0–R1`, current `Lane E`, and `LOW_UNKNOWN` until scope, critical interfaces, manufacturing profile, acceptance criteria, and verification evidence exist. A research-risk proxy of 5 is shown as `K3` and `NOT_AUTONOMOUSLY_RELEASABLE`.
- SKU-201 through SKU-300 have an explicit purpose and a structured concept preflight. Every row passes `K1`, `C1–C2`, and `R2`; all remain current `Lane E`, `LOW_UNKNOWN`, and `CONCEPT_ONLY` because the exact printer, filament product/color/batch, nozzle, process profile, and customer variant evidence are still open. Their target is Lane B only after those gates close.
- SKU-301 through SKU-314 and SKU-501 through SKU-557 are separate children of retained generic ideas. SKU-501–557 is the second wave: 57 named-interface children of the ten highest trend-score records (SKU-130, SKU-112, SKU-178, SKU-200, SKU-133, SKU-171, SKU-173, SKU-001, SKU-160, SKU-107). Their scope names one exact device, product article, or published format; critical interface nominals come from cited primary sources; the research-only printer/material/nozzle/orientation/process baseline is exact and hash-pinned; and acceptance criteria plus a coupon method are defined. They therefore reach nominal `R3`, not R4. C1/C2 children use Lane B and C3 children Lane C; all remain `K1`, `CONDITIONAL`, and `GO_WITH_CONTROLS — NOT PRODUCT RELEASE APPROVAL`.
- SKU-315 through SKU-414 are the generative Step1X-3D concepts: 100 appearance-led products for the requested popular-model groups (animals and creatures, cartoon and comic characters, toys and fidgets, tools and desktop utility, persons and figurines, trending decor). Each row records the image prompt, the Step1X-3D plus CAD route, a mandatory mesh-quality gate, an IP basis, an AI-transparency duty and a modeled unit-economics block on the retained cost basis. Every row passes a directional trend score above 70, `R2` on all five readiness components, `C1–C3` and `K1–K2`, and every row stays current `Lane E`, `LOW_UNKNOWN` and `CONCEPT_ONLY`. Two hard gates are deliberately left failing: `G3` for the exact manufacturing process and `TOOL-LICENCE` for the Step1X-3D licence conflict described below.
- The generative block carries a `TOOL-LICENCE` hard gate beside `G0`–`G6`, and it stands at `WARN`. The owned fork `github.com/stefanjunk/Step1X-3D` removed the Tencent Hunyuan-derived code that had excluded the European Union: eleven files left with the deleted texture stage and the twelfth, the volume decoder every geometry run executes, was replaced by an independent implementation verified to reproduce the same iso-surface. The Stable Diffusion XL RAIL++-M flow-down duty, pymeshlab, plyfile, easydict, pytorch3d, kaolin and nvdiffrast left the inference path with it. The gate stays at `WARN` rather than closing because the `openai/clip-vit-large-patch14` weights the visual encoder loads declare no licence, the published Step1X-3D weights derive from Objaverse and Objaverse-XL with heterogeneous per-asset terms, and the image generator used for step one is chosen per SKU. It returns to `FAIL` if a tool with a non-commercial or territorially limited licence re-enters the pipeline.
- A named child never raises its generic parent automatically. The parent remains at its current R until representative variants, parameter-domain limits, and boundary coupons justify broader evidence.
- `Preflight_Target_Lane_After_Evidence` is a planning aid for the likely design path after readiness and hard gates are sufficient. It never replaces the current lane, a `HOLD`/`CONCEPT_ONLY` decision, or product release gates.

The version-controlled row-level sources are `research-ideas-r3-variants.csv`, `research-idea-preflight-estimates.csv`, and `readiness-advancement-register.csv`. The last file covers all 471 ideas plus all 109 product directories and assigns a purpose, wave, bottleneck, evidence boundary, and next R-evidence action. Regenerate and verify them before rebuilding the workbook:

```bash
python business/tools/score_research_additions_trends.py
python business/tools/score_research_additions_trends.py --check
python business/tools/build_research_ideas_201_300.py
python business/tools/build_research_ideas_201_300.py --check
python business/tools/build_research_r3_variants.py
python business/tools/build_research_r3_variants.py --check
python business/tools/build_research_ideas_step1x_315_414.py
python business/tools/build_research_ideas_step1x_315_414.py --check
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

Do not combine C, R, K, lane, confidence, and market opportunity into one average. For later market-potential-versus-complexity analysis, compare `Opportunity_Score` or `Estimated_Market_Fit_1_5` beside `Preflight_Complexity_Band`, while retaining K and the current/target lane as separate gates.

## Readiness-advancement order

The `R Advancement` tab sequences the full estate without pretending every row deserves new CAD:

1. `W1 HIGH-TREND / LOW-COMPLEXITY`: trend at least 85, complexity no higher than C2, criticality no higher than K1, and current readiness below R3.
2. `W1 R3 NOMINAL — COUPON NEXT`: named variants whose nominal inputs are already R3; the next work is independent dimensional/physical evidence, not more market-score inflation.
3. `W2 LOW-COMPLEXITY`: C1–C2/K0–K1 rows without the W1 trend threshold.
4. `W3 CONTROLLED`: up to C3/K2, advanced only through the stated interface/process/test gate.
5. `W4 SPECIALIST / HOLD`: higher complexity or criticality; no autonomous readiness promotion.

The current purge catcher illustrates the fail-closed rule: own machine photos, the independently measured 17 mm screw pitch, abstracted third-party principles, and an exact process improve evidence, but do not supply a complete variant-confirmed clean-room envelope, screw hardware/tolerances, full-machine keep-outs, an approved storage architecture, an independent coupon, or low/mid/high-Z purge results. It therefore remains R2. Likewise, the ALEX tray's digital width gauges do not raise it above R1 without an exact article/revision, measured real drawer, pinned process, and recorded physical gauge result.

## Strategic rule before the score

Complete the current launch and validation critical path before opening another broad CAD workstream. Rows marked `0 FINISH CURRENT VALIDATION` already have mapped models; close their exact slicer, physical, rights, documentation, economics, and release evidence first. The `1 NEXT` rows are a candidate pool, not ten products to develop in parallel. Select at most one new candidate after its demand gate passes.

## Product-directory scores

`business/tools/score_product_directories.py` writes `product-directory-scoring.csv`, which the workbook joins as the product-row fallback for `Trend_Score_0_100`, `Priority_Score_0_100`, `Opportunity_Score_0_100`, `Risk_Score_1_5` and the ten 1–5 components. Products previously left all fourteen blank, so the unified list could not be ordered.

- **37 products inherit.** A product mapped to a research idea via `Mapped_Working_SKU` takes that idea's recorded values unchanged. `Score_Basis` names the SKU.
- **72 products are derived** from their own documented evidence, never from a portfolio-wide average:

| Component | Derived from |
|---|---|
| Strategy fit | The product register's `Strategy_Fit` text (`Core` 5, `Core adjacent` 4, `Adjacent` 3, `Off-strategy` 1) |
| Trend | Median trend of the research family covering the category, plus a strategy-fit adjustment; `NO PRIMARY-SOURCE RESEARCH FAMILY` uses a baseline of 35, below every scored family |
| Estimated market fit | Trend bands (>=90 → 5, >=80 → 4, >=65 → 3, >=45 → 2, else 1) |
| Market-evidence confidence | Exact family match 3, mapped family 2, no family 1; **capped at 3** for derived rows because no product has validated sales or repository physical evidence (an inherited row keeps the mapped idea's recorded value) |
| Creation effort | Preflight complexity class, reduced when a controlled parametric source already exists and raised when no model exists |
| Validation effort | Preflight criticality, raised at R0–R1 and when the `PHY` or `MOT` complexity dimension is >=3 |
| Commercial risk / risk score | The worst of criticality, the register's rights/provenance state, and the graded safety-risk note |
| AM differentiation | Exact-fit, named-format, measurement, defined-set, personalization and modularity wording in the strategy fit; capped at 3 when the `EXT` dimension is >=4 |
| Portfolio leverage | Controlled CAD source, a parametric generator, product-family size, and shared system/interface scope |
| Digital-first fit | Reduced by the `EXT`, `MOT` and `PHY` complexity dimensions and by K2–K3; forced to 1 when the digital offer is blocked from the digital-first scope |
| Economics | Complexity class adjusted for purchased content and premium exact-fit positioning; a **proxy**, since no product COGS or price is recorded |

`Priority_Score_0_100` then uses the unmodified weighting below, so a product row and a research row are directly comparable. `Opportunity_Score_0_100` follows the register convention of `min(99, trend + 2)`.

A derived product score orders planning work only. It is not product-specific demand, margin, safety or rights evidence, and it never overrides current Lane E, `HOLD`, `CONCEPT_ONLY` or a release gate. Adding a new product category fails the builder until that category receives an explicit research family or an explicit `None` in `CATEGORY_TREND_FAMILY`.

## Score meanings

All component scores use `1`–`5`:

| Component | Direction | Interpretation |
|---|---|---|
| Creation effort | Low is better | Estimated CAD, parameterization, documentation, and packaging effort |
| Validation effort | Low is better | Fit coupons, physical cycles, misuse, material, and workflow evidence expected |
| Commercial risk | Low is better | Safety, rights, compatibility, claims, support, and failure consequences |
| Estimated market fit | High is better | Directional problem and trend fit for the intended segment |
| Market-evidence confidence | High is better | Strength and geographic/product specificity of evidence; capped below validated sales |
| Strategy fit | High is better | Alignment with exact-fit, modular, personalized, small-space, digital-first products |
| Additive-manufacturing differentiation | High is better | Value created by exact dimensions, low-volume variants, modularity, or personalization |
| Portfolio leverage | High is better | Reuse of existing generators, interfaces, coupons, documentation, or customer workflows |
| Digital-first fit | High is better | Suitability for a common printer, support-free delivery, and a simple customer handoff |
| Economics | High is better | Directional price-to-complexity and material/fulfillment attractiveness |

## Priority formula

The `Priority_Score_0_100` is a weighted planning score:

| Component | Weight |
|---|---:|
| Estimated market fit | 20 |
| Strategy fit | 15 |
| Portfolio leverage | 15 |
| Additive-manufacturing differentiation | 10 |
| Low commercial risk | 9 |
| Low creation effort | 8 |
| Low validation effort | 8 |
| Digital-first fit | 5 |
| Economics | 5 |
| Market-evidence confidence | 5 |
| **Total** | **100** |

Effort, validation, and risk are inverted in the formula: a `1` receives the full component weight and a `5` receives zero. The score is only used within the tier gates below; a high score cannot override a risk or strategy hold.

## Decision tiers

| Tier | Meaning |
|---|---|
| `0 FINISH CURRENT VALIDATION` | A mapped model exists. Finish evidence instead of starting more geometry. |
| `1 NEXT — DEMAND TEST THEN CAD` | Top ten unstarted ideas meeting all gates: risk ≤2, creation effort ≤2, validation effort ≤3, strategy fit ≥4, market fit ≥4, and evidence confidence ≥3. |
| `2 VALIDATE NEXT` | Promising score, but demand, workflow, evidence, or risk must be resolved before CAD capacity is assigned. |
| `3 LATER` | Lower combined priority after the gated tiers. |
| `4 HOLD / SPECIALIST` | Risk ≥4 or strategy fit ≤2; specialist review or an explicit strategy exception is required before CAD. |

`Implementation_Order` sorts tier 0 first, then the gated tier-1 pool, followed by the other tiers. `New_Build_Rank` is the raw score order among unstarted ideas. `Next_Candidate_Rank` is the recommended order inside the gated tier-1 pool.

## Market-evidence limits

The current signals are directional:

- `S31` includes Germany in IKEA's 31-market storage survey and supports drawer, cable, countertop, sentimental-storage, and small-space problem hypotheses.
- `S01` provides Etsy 2026 search-direction evidence for mahjong, journaling, keepsakes, personalization, and related gift behavior.
- `S33` provides North American retailer search, sales, and survey evidence for sewing, needlepoint, yarn, journaling, and group crafts.
- `S34` supports collector and recommerce hypotheses across nine markets including Germany.
- `S35` is a US physical-media signal only.
- `S36` is Pinterest's 2026 platform-search forecast for correspondence, Poetcore, and fragrance rituals; it is not German product-level demand.
- `S29` supports the EU repair direction but does not prove demand for a specific printed replacement part.

For SKU-101–300, `Trend_Score_0_100` is a transparent directional screen: primary-source strength (0–30) + signal magnitude (0–30) + metriMade strategy fit (0–25) + nonduplicate portfolio whitespace (0–15). SKU-101–200 are now scored individually and reproducibly at 48–99; ten remain below 70 because maker-only, repair-policy-only, or missing direct market evidence was not promoted into demand proof. Their row-level components, basis, assessment date, version, and warning status are stored in `research-ideas-additions.csv`. SKU-201–300 retain their curated 87–94 scores. These are prioritization judgments, not statistically calibrated trend indices or demand forecasts.

No current source supplies German product-level search volume, listing competition, conversion, acquisition cost, return rate, or validated price. `Market_Evidence_Confidence_1_5` is therefore capped at `4`, and most ideas score `2` or `3`.

## Required gate before new CAD

For each tier-1 candidate:

1. Check German and English buyer terms, search volume, and listing competition using an authenticated marketplace-insights tool.
2. Collect at least five qualified problem signals from the intended segment; generic likes do not count.
3. Test the customer-input or measurement workflow when customization is part of the offer.
4. Define the smallest coupon or prototype that can disprove fit, usability, or willingness-to-pay assumptions.
5. Assign CAD capacity only after the evidence is recorded and the candidate remains ahead of the other tier-1 ideas.

The deterministic SKU-101–200 trend scorer is `business/tools/score_research_additions_trends.py`; the SKU-201–300 source generator is `business/tools/build_research_ideas_201_300.py`; the common queue generator is `business/tools/score_research_ideas.py`. Run the applicable source scorer/generator before the common queue after changing curated rows or implementation status, and use `--check` to detect stale outputs.
