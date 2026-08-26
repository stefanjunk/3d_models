# Business model

## Revenue streams

| Stream | Launch status | Notes |
|---|---|---|
| `metriCreate` fixed digital 3MF revision | First commercial MVP | Lowest operational complexity; Germany-only initially |
| `metriMade` professionally printed `as-is` item | After fulfillment gate | Curated consumer SKU; controlled material/profile/QC and guided presentation |
| `metriCreate` configured digital revision | After configuration gate | Validated parameters, immutable generated revision and exact entitlement |
| `metriCreate` configured printed item | Later | Configuration validation plus manufacturing review, pricing and custom-goods terms |
| Bundles and room systems on `metriMade` | Later | Only after compatible interfaces, premium presentation and version policy exist |
| Technical/maker products on `metriCreate` | Incremental after MVP | Each category needs its own release, rights and safety evidence |

## Channel design

The two owned storefronts share one system of record for product IDs, released revisions, configuration schemas, licenses, entitlements, orders, support and takedowns. `metriMade` applies a consumer-curation flag and its own content layer; `metriCreate` exposes the broader technical catalog and advanced paths. Social platforms and marketplaces may acquire customers later, but must point to the same controlled release evidence and must not create unmanaged file versions.

Cross-brand attribution must survive the handoff: originating site, SKU/revision, selected configuration, price/fulfillment mode and customer entitlement are stored once, not recreated as loosely related products.

## Pricing logic

Digital price must cover design, testing, documentation, support, platform/payment costs, taxes, and expected refund/fraud cost—not only file delivery. Printed price must additionally cover material, machine time, setup, failure allowance, post-processing, inspection, packaging, shipping labor, payment costs, taxes, and warranty/returns reserve.

No research price is an approved shop price. Every SKU needs a signed price and margin sheet before `P5 Commercial release`.

## Geographic sequence

1. Germany, digital-only.
2. Germany, selected printed standard items after fulfillment qualification.
3. Additional EU digital countries from an explicit legal/tax/payment allowlist.
4. Additional physical countries only after shipping, packaging, returns, tax, product-safety, and language support are ready.

## Portfolio rule

Until repeat demand and operating capacity are proven, at least 70% of active development capacity should serve the initial low-risk release path. `metriMade` remains tightly curated even after `metriCreate` broadens. Technical or high-risk models may remain engineering evidence, internal tooling or gated future options without being presented as released products.
