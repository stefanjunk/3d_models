# Practical website gap review

Review basis: repository `/workspace/Website/metrimade-store`, supplied `main` snapshot `1c75c8b0389d7aa7a57051bda8f11591906d9935` (2026-08-20). The locally checked-out branch was at `17fab9f` with uncommitted changes, so the review used Git objects for the supplied main commit and did not modify the website worktree.

Architecture update 2026-08-25: the business source of truth now defines two connected storefronts, `metriMade` and `metriCreate`, backed by one product/revision system. The original snapshot review remains valid for its inspected code, but implementation planning must now add domain/brand routing, shared product records, metriMade eligibility/content fields and exact-SKU cross-brand handoff. Do not clone the catalog into two independent databases.

## Verdict

The supplied main is technically staging-capable but not live-ready. The core page architecture is broad enough for the MVP. The blockers are real products, evidence, legal/operator data, CI, payment/tax configuration and operating processes—not a lack of marketing pages.

## What already exists

The repository already has shop, product detail, configurator, cart, checkout/success, authentication, account, orders, downloads, configurations, settings, wishlist, operator model publishing, privacy choices, imprint, privacy, terms, withdrawal, shipping/payment, digital license/content, product safety, accessibility, about and support surfaces. It also has Firestore/Storage/Auth/App Check-oriented architecture and a safe-core 3MF operator flow with publish/takedown approvals.

## Launch blockers confirmed

- Product images and catalog entries are placeholders, not product evidence.
- No real product release is linked to the catalog; the business review also found zero `P5+` products.
- Checkout, legal approval, printed fulfillment and configuration fulfillment gates are closed.
- The business-side legal profile is now populated with founder-provided operator, address, representative, register and VAT data but remains `WORKING_DRAFT_LAUNCH_BLOCKED`; verification, contact, responsibility/signature fields, legal approval and the production website mapping are incomplete.
- No GitHub Actions workflow/status checks were found for the supplied commit.
- The launch checklist has no signed/checked releases.
- The publisher supports one safe-core 3MF; demo copy sometimes promises 3MF, STL and PDF.

## Product/catalog corrections

Replace demo products only through approved release manifests. `GridFit`, `Arc Cable Dock`, `Planter`, `Laptop Stand`, `Wall Station`, `Orbit Tray`, `Label Rail`, and `Bench Tray` must remain visibly fictional/demo or be removed from production data. At most, map `GridFit` to `MM-ORG-001` after the exact drawer revision, files, tests, rights, copy, price and media are approved.

The shop needs only three initial product pages, but each needs stronger content: exact fit envelope and measurement method, printer volume, material/profile basis, included file, revision/change policy, tested scope, exclusions/warnings, license, support, real photos, labeled renders, price/tax presentation and delivery/access terms.

## Additional operational areas

Do not build these all as custom dashboards before launch; a secure, auditable manual tool can serve the MVP. The business must nevertheless own each function:

| Area | MVP implementation | Later UI |
|---|---|---|
| Release/evidence status | release manifest plus operator approvals | evidence dashboard with gate history |
| Order and entitlement operations | Stripe/Firebase consoles plus documented runbook/reconciler | searchable order detail and entitlement controls |
| Support/withdrawal/privacy cases | monitored inbox plus case register and templates | integrated service desk |
| Refund/fraud/chargeback | Stripe console plus case log | admin workflow |
| Rights/safety incidents and recalls | incident register, kill switch and order export | dedicated incident/recall panel |
| Printed batch/QC | disabled at launch | production queue, traveler, batch/QC and shipment status |

Useful customer-facing refinement after core readiness: a measurement guide linked from fit-dependent products and a clear printer-compatibility explainer. A full configurator is not required for the first fixed products.

## Engineering priorities

1. Add CI for lint, typecheck, unit tests, production build, Firebase rules/emulators and critical E2E; protect main.
2. Establish separate development/staging/production Firebase projects, least-privilege identities, App Check rollout, rules/index deployment, backups and alarms.
3. Publish one real release to staging and complete purchase/download/expiry/unauthorized/takedown tests.
4. Complete Stripe test/live configuration, verified webhook, idempotency/retries, refunds, country/tax decisions and accounting export.
5. Map and legally approve the populated real operator profile in the website; implement and test the electronic withdrawal flow and confirmation email.
6. Complete accessibility, browser/device, security, dependency/secret and rollback checks.

## Go-live rule

Do not turn on a feature flag because its page renders. Turn it on only when the product, legal, operational, negative-path, monitoring and rollback evidence for that delivery mode is signed.
