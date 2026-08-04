# Task Plan: German Filament Price Research

## Goal
Create a current, source-linked Markdown comparison of German-market filament prices for PLA, PLA+, high-speed PLA, PETG, high-speed PETG, and TPU 95A.

## Scope
- Geography: Sellers and marketplaces delivering to Germany
- Price basis: Item price including German VAT, excluding shipping
- Normalization: EUR per kilogram
- Offers: In-stock consumer listings; no account-only coupons, subscriptions, or bulk-only prices
- Color check: Record whether black is cheaper than other colors in the same product line

## Phases
- [x] Phase 1: Confirm scope and research plan
- [x] Phase 2: Research PLA, PLA+, and high-speed PLA
- [x] Phase 3: Research PETG, high-speed PETG, and TPU 95A
- [x] Phase 4: Validate prices, classifications, stock, and color effects
- [x] Phase 5: Build and review the Markdown deliverable

## Key Questions
1. What is the cheapest verified in-stock offer in each material class?
2. What price range represents comparable current offers in each class?
3. Is black cheaper than other colors in the cheapest product line?
4. Are any apparent bargains conditional, mislabeled, multipacks, refills, or different spool weights?

## Decisions Made
- Normalize all offers to EUR/kg so non-1 kg spools remain comparable.
- Include marketplaces, but reject unverifiable or condition-dependent prices.
- Treat "high speed" as a product classification that must be explicit in the listing.
- Treat TPU 95A as valid only when Shore 95A is stated.
- Use direct product pages as primary price evidence.
- Keep the six categories mutually exclusive: standard PLA and PETG exclude explicit high-speed products, and conventional PLA+ excludes explicit high-speed PLA+.
- Allow public, no-code limited-time sales but label them prominently.
- Treat ranges as the span of the directly validated sample, not an exhaustive market-wide interval.

## Errors Encountered
- A stale BerryBase PLA+ URL returned 404; replaced it with the live canonical product URL.
- One delegated PETG research run returned no findings; reran it successfully.
- Two Amazon ASINs were initially associated with the wrong colors: B0FCFL5VRX is YUANEANG white PLA and B0CR1CS3K8 is eSUN white PLA-Basic. Corrected before drafting.
- Amazon showed an inconsistent EUR/kg field for IEMAI high-speed PETG; used the explicit 1 kg weight and item price for conservative normalization.

## Status
**Complete** - Research, validation, deliverable drafting, and final review are finished.
