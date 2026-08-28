# Functional MVP webshop scope

## Launch slice within the two-brand architecture

The first transactional MVP is the German `metriCreate` storefront with at least one and preferably three fixed, commercially released 3MF products. It supports technical catalog discovery, product detail, checkout, order history, authorized exact-revision download, customer support, withdrawal/legal flows, operator publishing and takedown. Additional target products never block the first complete product from a controlled launch.

`metriMade` may expose a curated consumer-facing preview of eligible products and collect interest, but `as-is` printed orders remain non-transactional until printed fulfillment passes. The advanced link into `metriCreate` may be demonstrated, but parameterized purchase remains disabled until the configuration gate passes.

## Must work end to end

| Capability | MVP acceptance |
|---|---|
| Catalog | only approved Firestore releases; search/filter/detail/sitemap agree |
| Brand mapping | one product ID/revision source; explicit `metriMade` eligibility and brand-specific content; no copied divergent product records |
| Product truth | real media, exact revision, one actual 3MF, tested scope and exclusions |
| Identity | chosen guest/account model, login/reset/linking and account deletion tested |
| Checkout | Stripe test/live separation, country allowlist, tax and consent records, duplicate/retry safety |
| Digital delivery | exact immutable revision, signed URL, expiry and unauthorized-access tests |
| Legal | approved operator details and actual providers/processes; contract/withdrawal confirmation |
| Operator | least-privilege ingestion and independent approval/publish/takedown process |
| Support | contact route and logged refund, rights, safety and privacy handling |
| Operations | backups, restore test, monitoring, reconciliation, kill switch and rollback |
| Quality | lint, typecheck, unit, Firebase rules, production build and critical E2E in CI |

## Feature gates

- `CHECKOUT_ENABLED=false` until payment, tax, legal and E2E approvals pass.
- `LEGAL_CONTENT_APPROVED=false` until the real operator/profile and texts are signed.
- `PRINT_FULFILLMENT_READY=false` for the initial launch.
- `CONFIGURATION_FULFILLMENT_READY=false` for the initial launch.
- `METRIMADE_TRANSACTIONAL=false` until at least one curated SKU passes printed fulfillment.
- `METRICREATE_DIGITAL_TRANSACTIONAL=false` until the original checkout/legal/release E2E gates pass.
- Digital countries are an explicit allowlist; begin with Germany only after approval.

## Deliberately out of scope

- third-party marketplace/seller onboarding;
- public model upload;
- subscriptions, loyalty, reviews and social features;
- unlimited parameter combinations;
- multi-country physical shipping;
- multiple file formats or documentation bundles unsupported by the release manifest;
- automatic print-farm routing;
- broad analytics/advertising consent stack before it is needed.
- automatic publication of the broad `metriCreate` backlog or any product lacking a signed release.

## Launch definition

“MVP complete” means one real `metriCreate` customer can discover, lawfully buy, receive, use and obtain support for the exact approved digital revision—and the operator can reconcile, refund, block and trace it. Products two and three improve catalog credibility but are optional for this threshold. The later two-brand journey is complete only when a `metriMade` customer can order an `as-is` product and an advanced customer can cross into `metriCreate` without losing product/revision context.
