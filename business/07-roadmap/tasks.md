# Focused MVP task backlog

The detailed sortable backlog is `mvp-tasks.csv` and is also embedded in the Excel workbook. Estimates are active effort plus indicated print/adviser lead time, not delivery promises. Roles must be replaced with named owners when work starts.

## Critical path

`operator/name/legal decisions` → `three product requirements` → `CAD/digital candidates` → `coupons/prototypes` → `three unchanged final prints` → `P5 commercial packages` → `staging publication` → `payment/legal/entitlement E2E` → `signed launch`.

CI, Firebase/security setup, legal drafting, support runbooks and product work should run in parallel where dependencies allow. Printed fulfillment and configuration do not sit on the digital MVP critical path.

## Now — decisions and first evidence

- [ ] Finish `GOV-001`: exact firm, 2019 founding year, public email, VAT ID and single-person responsibility matrix are populated; retain register/representation evidence, verify the provisionally recorded W-IdNr., reconcile profiles and sign legal approval.
- [ ] Finish `BRD-001`: two connected storefront roles, names, Cloudflare domains and descriptive product-title policy are recorded; metriMade V10 `08` / `MM-BRAND-001-R1` is selected; retain domain proof, confirm rights owner/goods-services scope, select the metriCreate logo, complete name/device-mark searches and sign risk approval.
- [ ] Approve exactly `MM-ORG-001`, `MM-PER-001`, and `MM-ORG-002` as the fixed launch scope.
- [ ] Create release/source/component/decision templates, require the `metriMade.com · <PRODUCT_ID> · v<VERSION>` geometry-mark invariant for physical metriMade releases, and dry-run them.
- [x] Reactivate approved `MM-ORG-001` requirements `0.1.0-requirements`: common-220 nine-module tool organizer, full-depth tool lane, removable comb, 18 small-parts compartments and seam-relative planar connectors. The 0.2/0.3 branches remain historical. Reactivated by Stefan Junk and concept v1 approved at Gate 0B on 2026-08-26. Freeze the other two product requirements separately.
- [ ] Correct DrawerFit connector evidence and print coupons.
- [ ] Begin NameForm and ShelfFit controlled CAD.
- [ ] Interview target users and test the measurement guide.
- [ ] Reconcile the website development branch; add CI.
- [ ] Establish staging/prod environments, tax/payment decision, legal work and support/incident runbooks.

## Next — qualify and stage

- [ ] For each product: one prototype iteration, then three final unchanged-revision prints and claim-specific tests.
- [ ] Complete rights, safety, customer package, media, cost/price and signed `P5` decisions.
- [ ] Publish exact releases to staging; remove/segregate fictional demo data.
- [ ] Configure Stripe webhook/reconciliation, Firebase security/backups/alarms and withdrawal flow.
- [ ] Run positive and negative purchase/download/refund/takedown tests.
- [ ] Complete DE content, accessibility and browser/device review.

## Launch

- [ ] Record production commit, Firebase rules/config, Stripe config, legal versions and exact release hashes.
- [ ] Rehearse rollback and SKU/revision kill switch.
- [ ] Obtain written approval and enable only Germany digital checkout.
- [ ] Closely monitor the first 10 orders and run a two-week review before expanding.

## Later, deliberately off the MVP critical path

- [ ] Qualify one standard printed SKU and packaging/fulfillment process.
- [ ] Build server-side validated configuration and immutable generated-variant release flow.
- [ ] Add countries one by one through an evidence-backed allowlist.
- [ ] Revisit system-furniture inserts, DeskNest Mini, labyrinth boxes and other reserve products.
- [ ] Keep wall, structural, body-contact, toy, water, food and vehicle categories on hold until category-specific programs exist.

## Stop rules

- Do not add a fourth launch product while any of the three lacks an owner or a funded test path.
- Do not enable a sales flag with placeholder media or demo files.
- Do not compensate for missing physical evidence with stronger disclaimers.
- Do not turn unknown provenance into a license assumption.
- Do not build self-service configuration before the manual measurement workflow succeeds.
