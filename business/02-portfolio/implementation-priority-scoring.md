# Research-idea implementation priority

Status: planning model plus 3D-preflight and readiness-advancement overlay reviewed 2026-08-31. Priority-scoring version: `1.2`; preflight-estimate version: `1.2`.

This model orders all 314 research ideas for **what to finish, validate, or consider building next**. It does not approve a product for sale, replace the product lifecycle gates, or prove demand, price, margin, rights, safety, or German product-market fit.

The ordered source is `research-idea-priority.csv`; the generated workbook presents it as `Implementation Priority`. The workbook's leading `Portfolio` tab joins this queue with all product directories, idea sources, unit economics and readiness advancement in one 422-row filterable list. The source-prefixed columns are a complete audit copy; `Product Register` retains the prior 99-row curated product source.

## 3D-preflight planning overlay

The workbook keeps market potential and implementation feasibility separate. `Research Ideas 100`, `Research Ideas +100`, `Research Ideas +200`, `Research Variants R3`, and `Implementation Priority` therefore show a compact preflight field beside the opportunity, trend, and market-fit fields:

`C# · R# · K# · Lane X · CONFIDENCE`

- The 37 research rows mapped to a current product use that product's exact documented preflight scorecard and link its `preflight/preflight-result.json`.
- The 163 ideas without a mapped product are explicitly marked `PRELIMINARY IDEA ESTIMATE — NOT RELEASE APPROVAL`.
- For those preliminary rows, the C band is derived conservatively from the existing creation- and validation-effort estimates; the K band uses the existing research-risk value only as a broad proxy. It is not a safety qualification.
- An unstarted idea remains `R0–R1`, current `Lane E`, and `LOW_UNKNOWN` until scope, critical interfaces, manufacturing profile, acceptance criteria, and verification evidence exist. A research-risk proxy of 5 is shown as `K3` and `NOT_AUTONOMOUSLY_RELEASABLE`.
- SKU-201 through SKU-300 have an explicit purpose and a structured concept preflight. Every row passes `K1`, `C1–C2`, and `R2`; all remain current `Lane E`, `LOW_UNKNOWN`, and `CONCEPT_ONLY` because the exact printer, filament product/color/batch, nozzle, process profile, and customer variant evidence are still open. Their target is Lane B only after those gates close.
- SKU-301 through SKU-314 are new, separate children of retained generic ideas. Their scope names one exact device, product article, or published format; critical interface nominals come from cited primary sources; the research-only printer/material/nozzle/orientation/process baseline is exact and hash-pinned; and acceptance criteria plus a coupon method are defined. They therefore reach nominal `R3`, not R4. C1/C2 children use Lane B and C3 children Lane C; all remain `K1`, `CONDITIONAL`, and `GO_WITH_CONTROLS — NOT PRODUCT RELEASE APPROVAL`.
- A named child never raises its generic parent automatically. The parent remains at its current R until representative variants, parameter-domain limits, and boundary coupons justify broader evidence.
- `Preflight_Target_Lane_After_Evidence` is a planning aid for the likely design path after readiness and hard gates are sufficient. It never replaces the current lane, a `HOLD`/`CONCEPT_ONLY` decision, or product release gates.

The version-controlled row-level sources are `research-ideas-r3-variants.csv`, `research-idea-preflight-estimates.csv`, and `readiness-advancement-register.csv`. The last file covers all 314 ideas plus all 108 product directories and assigns a purpose, wave, bottleneck, evidence boundary, and next R-evidence action. Regenerate and verify them before rebuilding the workbook:

```bash
python business/tools/build_research_ideas_201_300.py
python business/tools/build_research_ideas_201_300.py --check
python business/tools/build_research_r3_variants.py
python business/tools/build_research_r3_variants.py --check
python business/tools/score_research_ideas.py
python business/tools/score_research_ideas.py --check
python business/tools/build_research_preflight_estimates.py
python business/tools/build_research_preflight_estimates.py --check
python business/tools/build_readiness_advancement_register.py
python business/tools/build_readiness_advancement_register.py --check
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

For SKU-201–300, `Trend_Score_0_100` is a transparent directional screen: primary-source strength (0–30) + signal magnitude (0–30) + metriMade strategy fit (0–25) + nonduplicate portfolio whitespace (0–15). All 100 score 87–94 and therefore exceed the requested `>70` gate. This is a prioritization judgment, not a statistically calibrated trend index or demand forecast.

No current source supplies German product-level search volume, listing competition, conversion, acquisition cost, return rate, or validated price. `Market_Evidence_Confidence_1_5` is therefore capped at `4`, and most ideas score `2` or `3`.

## Required gate before new CAD

For each tier-1 candidate:

1. Check German and English buyer terms, search volume, and listing competition using an authenticated marketplace-insights tool.
2. Collect at least five qualified problem signals from the intended segment; generic likes do not count.
3. Test the customer-input or measurement workflow when customization is part of the offer.
4. Define the smallest coupon or prototype that can disprove fit, usability, or willingness-to-pay assumptions.
5. Assign CAD capacity only after the evidence is recorded and the candidate remains ahead of the other tier-1 ideas.

The deterministic SKU-201–300 source generator is `business/tools/build_research_ideas_201_300.py`; the common queue generator is `business/tools/score_research_ideas.py`. Run both after changing the curated rows or implementation status, and use `--check` to detect stale outputs.
