# Per-product commercial evidence checklist

Complete this for the exact SKU/revision and delivery mode. Unknown answers are blockers.

## Identity and scope

- [ ] SKU, revision, product owner and release date are fixed.
- [ ] Intended user, intended use, countries, delivery mode and product claims are explicit.
- [ ] Excluded uses and foreseeable misuse are documented.
- [ ] Product/packaging/file identification supports traceability.
- [ ] For a physical metriMade item, the recessed mark reads `metriMade.com` plus the exact `<PRODUCT_ID> · v<VERSION>` from the release manifest.

## Source, rights and marks

- [ ] Editable source and deterministic build are identified.
- [ ] Every input/component/reference/font/library/AI contribution is in the source/component register.
- [ ] Commercial, modification and redistribution rights are evidenced.
- [ ] Required attribution and customer pass-through terms are included.
- [ ] Trademark, design-similarity and patent questions are resolved for the scope.
- [ ] No asset from an `external` folder is present, derived, embedded or used as a master.

## Digital artifact

- [ ] Correct units, scale, dimensions, bodies and orientation.
- [ ] Mesh/topology, walls, features, clearances and build volume pass.
- [ ] Exact customer 3MF opens in the target slicer with no unsupported feature.
- [ ] Files, sizes and SHA-256 hashes match the release manifest.
- [ ] Render geometry and exact customer geometry are compared.
- [ ] Generated watermark profile/cutter, integrated manufacturing mesh, placement, reading orientation and hashes are recorded; no live or manually edited trace text is used.

## Physical and safety evidence

- [ ] Production printer/material/profile and lot are recorded.
- [ ] Coupon and first prototype results are recorded.
- [ ] The exact watermark coupon passes with the intended nozzle, layer, material, first-layer settings and bed surface; domain, product ID and version are legible without guessing.
- [ ] Three final unchanged-revision prints pass reproducibility criteria.
- [ ] Critical dimensions and fit pass with measuring method/tolerance.
- [ ] Stability, load, cycles/wear, assembly and cleaning tests match claims.
- [ ] Foreseeable misuse and failure modes are evaluated.
- [ ] Risk decision is `PASS` or an approved customer-visible `WARN`, not unknown.
- [ ] Required warnings, instructions and manufacturer/safety information are approved.

## Customer and commercial package

- [ ] Actual included file/part list is accurate.
- [ ] License, update policy and support boundary are approved.
- [ ] Real photo of exact test print and labeled renders are approved.
- [ ] Description, dimensions, alt text and translations are accurate.
- [ ] Unit economics, price, tax class, country and delivery/access time are signed.
- [ ] Withdrawal/refund/returns treatment is approved for this delivery mode.

## Staging and release

- [ ] Rights, safety, render and commercial approvals are recorded.
- [ ] Catalog/search/filter/detail/sitemap show the same release.
- [ ] Positive purchase and exact-revision delivery test passes.
- [ ] Unauthorized/expired/duplicate/refund negative paths pass.
- [ ] Takedown, kill switch and rollback pass.
- [ ] Production decision is signed and monitoring/support owner assigned.

Final decision: `PASS` / `WARN` / `BLOCK`  
Decision owner:  
Date:  
Release manifest/hash:  
Open limitations:
