# Brand, name and domain clearance record

Document status: `WORKING_DRAFT_LAUNCH_BLOCKED`  
Task: `BRD-001`  
Business owner: Stefan Junk  
Last factual update: 2026-08-25

This record separates naming intent from evidence that a name can be used and, where desired, registered. Founder selection is recorded; clearance, ownership and approval remain open.

## Intended naming architecture

| Layer | Intended name/spelling | Intended role | Legal relationship |
|---|---|---|---|
| Legal operator | `Stefan Junk Holding UG (haftungsbeschränkt)` | Seller and contracting party | Exact firm confirmed by managing director; retain current register evidence |
| Umbrella business designation | `JuSt Innovation` | Business identity above the offers | Business designation of the legal operator; not a separate legal entity |
| Premium consumer storefront | `metriMade`; domain `metriMade.com` | Curated smart decor, space savers and practical personalized home/office products; guided `as-is` order path | Brand/business identifier used by the legal operator; domain acquired through Cloudflare |
| Maker/configuration storefront | `metriCreate`; domain `metriCreate.com` | Broad technical 3D-product catalog, parameterization, model downloads and optional printed orders | Brand/business identifier used by the legal operator; domain acquired through Cloudflare |
| Products | Descriptive German product title plus stable product ID/SKU | Product identification, not a planned product-mark portfolio | Internal labels such as `DrawerFit`, `NameForm` and `ShelfFit` are working labels only and must not silently become public brands |

The founder supplied the spellings `JuSt Innovation`, `metriMade` and `metriCreate` on 2026-08-24 and confirmed `metriMade.com` and `metriCreate.com` as the binding domains on 2026-08-25. Domain names are technically case-insensitive; the preferred display spellings are `metriMade.com` and `metriCreate.com`. Existing project files use variants such as `MetriMade` and `MetriCreate`; update them only through a controlled content revision.

## Domain-control record

| Domain | Registrar/DNS provider | Control statement | Retained proof | Renewal/recovery owner | Status |
|---|---|---|---|---|---|
| `metrimade.com` | Cloudflare | Acquired and controlled by Stefan Junk, confirmed 2026-08-25 | Cloudflare registrar/zone evidence still to be saved | Stefan Junk; account recovery/renewal settings to document | `PARTIAL` |
| `metricreate.com` | Cloudflare | Acquired and controlled by Stefan Junk, confirmed 2026-08-25 | Cloudflare registrar/zone evidence still to be saved | Stefan Junk; account recovery/renewal settings to document | `PARTIAL` |

Sufficient MVP evidence is a dated Cloudflare registrar screenshot or export showing each domain in the controlled account, plus a DNS-zone screenshot/export proving configuration control and a record of auto-renewal, account recovery and MFA ownership. Redact account IDs, API tokens, billing data and recovery secrets. Public WHOIS data is not required where registration privacy is enabled.

## Confirmed storefront architecture

The founder confirmed two connected storefronts on 2026-08-25:

- `metriMade` is the accessible premium consumer layer and displays a curated subset of the products controlled in the shared catalog.
- `metriCreate` is the broader maker/technical storefront, configuration environment and digital-model download route.
- A metriMade customer may order the qualified `as-is` printed item, follow an advanced link to the exact metriCreate configuration, or—after entering metriCreate—buy the released digital model.
- Both domains use the same legal operator, shared product ID/revision and approval evidence; customer-facing legal texts identify the actual brand/domain and fulfillment mode without implying different sellers.

## Clearance register

| Name/asset | Domain control | German/EU/international register search | Company/common-law/internet search | Goods/services scope | Rights owner | Risk decision | Status |
|---|---|---|---|---|---|---|---|
| `JuSt Innovation` | Not recorded | Not recorded | Not recorded | To define | Intended: legal operator; confirm | None | `OPEN` |
| `metriMade` | Cloudflare domain control founder-confirmed; retained proof pending | Directional research only; not clearance | Directional research only | [MVP goods/services scope](brand-goods-services-scope.md) | Proposed: legal operator; confirm in approval | None | `PARTIAL` |
| `metriCreate` | Cloudflare domain control founder-confirmed; retained proof pending | Directional research only; not clearance | Directional research only | [MVP goods/services scope](brand-goods-services-scope.md) | Proposed: legal operator; confirm in approval | None | `PARTIAL` |
| Descriptive product titles + stable product IDs | No separate domains planned | No product-mark registration planned | Basic pre-publication collision/misleading-term check only | Exact released product category | Legal operator owns SKU/catalog records; title is descriptive | Product-brand risk intentionally avoided | `POLICY SET` |
| Logos, icons and word/device marks | N/A | metriMade V10 `08` selected; device mark not yet searched | [`MM-BRAND-001-R1`](../01-strategy/brand-assets/metrimade/README.md) deterministic SVG redraw, concept/font/provenance records and hashes retained | Premium consumer store, packaging and product identification; approve exact scope | Proposed: legal operator; confirm | Selection fixed; similarity/risk decision open | `PARTIAL` |

## Evidence required to complete `BRD-001`

- retained proof of Cloudflare control for both launch domains, including renewal, recovery, MFA and organization/account ownership;
- final public capitalization and fallback names; binding domains and working brand spellings are recorded;
- documented searches for identical and similar names in DPMAregister, EUIPO/TMview and WIPO where relevant;
- searches beyond registers, including company names, business designations, products, domains, app stores and relevant market use;
- approve the dated [MVP goods/services scope](brand-goods-services-scope.md), including both storefront roles and the chosen protection breadth;
- source and commercial rights for every logo, icon, font and visual brand asset;
- decision whether to file `JuSt Innovation`, `metriMade`, `metriCreate` and/or logos as marks, naming the applicant/owner and any intra-group licence;
- similarity/risk assessment, conflicts found, mitigation/fallback decision and IP-counsel review appropriate to the exposure;
- approved public naming matrix for domain, website header, checkout, invoices, emails, packaging, files, metadata, support and social accounts;
- complete and sign the [brand risk approval](brand-risk-approval.md).

No separate fanciful product marks are planned. Descriptive titles still receive a lightweight check before publication because descriptive intent does not prevent collision with an existing mark or misleading use. The stable SKU/product ID remains the authoritative identifier.

## Completion rule

`BRD-001` may move to `Complete` only after the clearance register contains evidence links, dates, territories, goods/services, conflicts and a signed risk decision for every launch name and asset. Domain ownership or a successful registration alone is not sufficient clearance.
