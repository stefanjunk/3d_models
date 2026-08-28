# metriCreate: business and website review

- Status: `CONCEPT_REVIEW / CONDITIONAL_GO`
- Review date: 2026-08-28
- Decision owner: Stefan Junk
- Scope: internal consistency, business-model strength, brand/experience direction and maintenance-oriented website architecture. This is not a legal, tax, trademark or production-readiness approval.

## Executive verdict

The new brief does not require a new business model. It largely restates the two-brand architecture already recorded in this folder:

- `metriCreate` is already defined as the broader technical catalog and configuration environment.
- `metriMade` is already defined as the curated consumer subset of the same controlled product/revision system.
- the first transactional MVP is already digital-first and belongs to `metriCreate`;
- configuration is already part of the target experience, but deliberately gated until its parameter and manufacturing pipeline is validated.

The business receives a **conditional go for a narrow digital beta**, not yet a scale verdict. Its defensible value is not “many STL files”; it is a controlled system of versioned models, truthful compatibility, validated parameter ranges, evidence-backed releases and durable entitlements. Demand, acquisition cost, conversion, support burden and willingness to pay remain unproven.

The website should therefore **not be forked into a second independent shop**. Use one application codebase, one product source of truth and shared commerce/account/operations services, then render two brand-specific storefronts from explicit brand profiles. A copied `metricreate-store` repository would contradict the stated maintenance goal and increase catalog, legal, security and checkout drift.

## Brief compared with the business folder

| New requirement | Existing business record | Assessment |
|---|---|---|
| Maker, hobbyist, tinkerer and tech audience | `brand-architecture.md`, `business-idea.md` and `customers-and-value-proposition.md` name hobby technologists, makers and tinkerers | Aligned. Add “future-facing builders” as a tone cue, not as a separate untested segment. |
| `metriCreate` is a superset of `metriMade` | The folder states that every `metriMade` product maps to a `metriCreate` product/revision, while the reverse is not required | Fully aligned. |
| Primary focus on selling 3D models | The first MVP is a fixed digital 3MF revision; printed items remain later revenue streams | Aligned for the MVP. The long-term model should state more clearly that digital is primary and printed fulfillment is secondary. |
| Models should become configurable | Configuration is a later gated flow; the first MVP uses fixed revisions | Product vision aligns, launch timing differs. Show an honest Studio preview, but do not imply that unrestricted configuration or purchase is live. |
| Possible later chatbot | No dedicated assistant strategy exists | Missing addition. Treat it as an advisory layer over deterministic validation, never as a bypass around parameter, safety or release gates. |
| Layout and functions should closely resemble `metriMade` | One shared product/revision system is binding, but each brand is meant to retain its own audience and journey | Reconcile as roughly 85% shared shell/behavior and 15% brand-specific hierarchy, content and visual treatment. “Same application” should not mean identical hero copy or product emphasis. |
| Dark, more aggressive technology palette | The current direction prefers deep blue/cyan/violet | Compatible extension, but it changes the documented color direction. The recommended system keeps midnight, petrol, teal and aqua, replaces violet with anthracite and adds controlled signal orange. |
| Separate domain `metricreate.com` | Domain control is already founder-confirmed; retained proof and brand clearance remain open | Aligned. Domain ownership is not trademark or launch clearance. |

## Business-model assessment

### What is strong

1. **Clear segment split.** `metriMade` sells an accessible outcome; `metriCreate` sells model control, technical transparency and self-print confidence.
2. **One controlled product graph.** Shared SKU, revision, evidence, warnings, entitlements and takedown state prevent the two stores from becoming inconsistent inventories.
3. **Good launch sequencing.** A fixed, single-format digital release is substantially simpler than simultaneous print fulfillment and arbitrary configuration.
4. **Useful moat.** Measurement rules, fit coupons, validated ranges, release history and customer support are harder to copy than a single mesh.
5. **Fail-closed release discipline.** The folder correctly separates “model exists” from “commercial product exists.”

### What remains weak or unproven

1. **No demonstrated demand.** The market folder contains hypotheses, not sales, conversion, interviews or acquisition economics.
2. **One product is a technical MVP, not necessarily a credible public catalog.** Keep the existing one-`P5` transaction threshold for a controlled beta. For a broader brand launch, test whether three to five related released models are needed to create trust, discovery depth and repeat purchase.
3. **Acquisition is underspecified.** The owned shops define transaction channels, but not a measurable customer-acquisition loop. Add hypotheses for problem-led SEO, technical build content, creator/maker community outreach, cross-brand referrals and carefully controlled marketplace previews.
4. **License packaging is unresolved.** A personal-use license is a planning default. Makers may also value a higher-priced commercial physical-print license. Test and legally review distinct license tiers rather than assuming one license fits the audience.
5. **Update entitlement is unresolved.** Decide whether a purchase includes only the exact revision, safety/defect fixes, minor revisions or a paid major upgrade. This affects price, support and lifetime cost.
6. **Configuration changes the cost model.** Generated variants add compute, storage, validation, support and possibly manual review. Add a separate contribution model for configured digital revisions.
7. **A broad catalog can overwhelm one-person operations.** Keep the current release-by-release gate and 70% core-capacity rule. Do not use empty categories or concept counts to simulate breadth.
8. **Two domains add overhead even with one codebase.** SEO, policies, consent, authentication state, support attribution, canonical URLs and cross-domain handoff still require explicit design.

### Recommended commercial priority

1. Fixed, versioned personal-use 3MF releases.
2. Bundles of compatible released models.
3. A legally reviewed commercial physical-print license tier, if interviews show demand.
4. Validated configured digital revisions.
5. Printed fulfillment only after measured demand and unit economics justify the operational burden.

Subscriptions, public uploads, third-party sellers, reviews and community features should remain outside the MVP.

## Recommended application architecture

### Decision

Use **one repository and one product/commerce backend**, with two explicit brand profiles and two domain-facing deployments from the same reviewed commit. Separate production frontends are preferable to a code fork because they keep domain metadata, caching, canonical URLs and rollback explicit while preserving a single implementation.

```text
one reviewed application commit
├── metriMade brand profile  -> metriMade.com frontend
└── metriCreate brand profile -> metriCreate.com frontend
             │
             └── shared catalog, SKU/revision records, Auth users,
                 orders, entitlements, downloads, support and takedowns
```

The exact App Hosting topology still needs implementation review. A single host-aware backend is acceptable only after host-specific caching, metadata, canonical URLs and failure isolation are verified.

### Shared application surface

- authentication, account, orders, downloads, wishlist and cart behavior;
- checkout, withdrawal, privacy choices, support and legal templates;
- catalog queries, search primitives and release-status enforcement;
- product detail, media gallery, entitlement and exact-revision delivery;
- operator ingestion, approval, publish and takedown tools;
- accessibility primitives, responsive shell, error/loading/empty states;
- Firebase rules, server authorization, Stripe integration, monitoring and CI.

### Brand-specific profile

| Concern | `metriMade` | `metriCreate` |
|---|---|---|
| Catalog policy | Curated eligible subset | All eligible released products |
| Default commercial mode | Printed `as-is`, when qualified | Digital 3MF |
| Primary promise | Beautiful, useful result | Model control and print confidence |
| Hero media | Lifestyle/product context | CAD/model viewport and revision state |
| Product-card density | Benefit, size, guided choice | Revision, format, build envelope, configurable state |
| Detail hierarchy | Use, fit, finish, delivery | File contents, compatibility, revision, license, exclusions |
| Configuration | Advanced handoff | Native Studio flow |
| Theme | Warm canvas, navy, teal, sand | Anthracite, midnight, teal/aqua, signal orange |

### Data invariants

- Shared fields are never rewritten by a brand layer: SKU, revision, release status, tested scope, warnings, rights/notices, file manifest, hashes, availability and seller.
- Brand fields may differ: benefit title, technical title, media ordering, editorial copy, navigation placement and eligibility.
- Search and sitemap generation must enforce both release status and brand eligibility.
- Old orders resolve the purchased revision, never “latest.”
- Cross-domain handoff uses the exact SKU/revision and a signed, expiring server-side state record for configuration/return context. Do not trust editable query parameters for price or entitlement.
- Account identity may use the same Firebase user population, but browser sessions do not silently transfer between origins. Design the sign-in and handoff recovery path explicitly.

## Maintenance-oriented page plan

| Route/surface | Reuse | `metriCreate` difference |
|---|---|---|
| Header/footer | Same component and behavior | Dark tokens, technical nav labels, digital-first utility message |
| Homepage | Same section skeleton | CAD viewport hero, model catalog before Studio, technical proof instead of lifestyle proof |
| Catalog | Same search/filter/result engine | Filters for printer envelope, configurable state, revision/format and supported process |
| Product detail | Same gallery and purchase-mode framework | Digital mode first; file/revision/license/compatibility visible before lifestyle story |
| Studio/configurator | Extend existing route | Three-column parameter/viewport/validation workspace; gated until `CONFIGURATION_FULFILLMENT_READY` |
| Cart/checkout | Same flow | Exact digital revision and license line item made prominent |
| Account/downloads | Same flow | Revision history, exact file hash/support boundary and update entitlement |
| Operator | Same workflow | Brand eligibility and both presentation layers previewed before publish |
| Legal/support | Shared templates with verified brand/domain variables | Seller stays the same legal operator |

Recommended `metriCreate` primary navigation:

1. Modelle
2. Kategorien
3. Studio
4. Downloads
5. Über uns
6. Support

Do not add “Community,” “Creators,” public uploads, ratings or a “free” section until those are actual approved product capabilities.

## Configuration and future assistant

The Studio should be deterministic first and conversational second:

1. Product/revision and configuration schema are fixed.
2. Inputs use allowed units, ranges, increments and dependent rules.
3. The server validates every change and creates an immutable configuration record.
4. The viewport explains the effect; it is not the manufacturing source of truth.
5. Only a passed configuration can reach price review, purchase or download.
6. The assistant may explain measurements, compare allowed options, focus a field and summarize errors.
7. The assistant may not invent parameters, remove warnings, widen validated ranges, declare printability or directly publish a generated file.

Add an `AI_ASSISTANT_ENABLED=false` gate and record provider, model, data retention, prompt/version, cost, user disclosure, escalation and evaluation before enabling it. Names, images and space/body measurements require explicit purpose and retention decisions.

## Visual directions

### Recommendation: Midnight Forge

Use a “technical studio plus archival catalog” thesis:

> A model moves visibly from parametric wireframe to a controlled, exact manufacturing revision.

Identity signals:

- split wireframe/solid viewport as the signature motif;
- condensed geometric display type, calm humanist body and monospace metadata;
- dark inset work surfaces with crisp rules and modest radii;
- orange only for the dominant action; teal/aqua for valid/configurable states;
- motion that connects parameter change to model change; a static split view under reduced motion.

Suggested semantic tokens:

| Role | Value | Use |
|---|---|---|
| Canvas | `#0B0F12` | Page background |
| Surface | `#111A20` | Header and low panels |
| Raised surface | `#17242C` | Cards and inspectors |
| Midnight | `#112431` | Shared family anchor |
| Petrol | `#0D4D53` | Deep brand surface |
| Teal | `#08777D` | Selected/technical state |
| Aqua | `#7FD5D3` | Focus and valid state |
| Text | `#F2F6F5` | Primary text |
| Muted text | `#A7B4B8` | Secondary copy |
| Action orange | `#F05A28` | One dominant CTA |
| On-action | `#0B0F12` | Text/icon on orange |
| Warning | `#F2B84B` | Warning only; never reuse the CTA hue |
| Danger | `#FF5A5F` | Destructive/error |

Calculated contrast checks for the implementation tokens:

- text on canvas: 17.66:1;
- muted text on canvas: 9.04:1;
- dark text on `#F05A28`: 5.68:1;
- aqua on canvas: 11.33:1;
- white on teal: 5.32:1.

The generated raster concepts are art-direction references, not accessibility evidence. In particular, production buttons must use the specified dark on-action token; white on a bright orange such as `#FF6B2C` does not reach normal-text AA contrast.

### Alternative: Teal Blueprint

Best family resemblance to `metriMade`. It feels inventive and approachable and can share more of the existing teal/aqua asset language. Risk: it can become calm enterprise software if the model imagery and typography are too restrained.

### Alternative: Carbon Pulse

Strongest maker-tool character and most aggressive contrast. It is memorable for workshop utilities and campaigns. Risk: the dense hard-edged language can narrow the perceived audience and become tiring across account, legal and support flows. Borrow its condensed headings and orange section markers rather than applying the full treatment everywhere.

## Concept images

- [Midnight Forge homepage](concepts/metricreate-website/metricreate-home-midnight-forge-v1.png) — recommended direction.
- [Teal Blueprint homepage](concepts/metricreate-website/metricreate-home-teal-blueprint-v1.png) — strongest shared-family direction.
- [Carbon Pulse homepage](concepts/metricreate-website/metricreate-home-carbon-pulse-v1.png) — most aggressive direction.
- [Midnight Forge Studio](concepts/metricreate-website/metricreate-studio-midnight-forge-v1.png) — future deterministic configurator with advisory assistant preview.

These images use concept models, a provisional wordmark and non-binding UI copy. They are not production product media, a selected logo, a released catalog, legal copy or proof that the depicted functions exist. Generation prompts, references and hashes are recorded in the [concept provenance README](concepts/metricreate-website/README.md).

## Contradictions and stale records found

1. `business/README.md` reports 91/91 portfolio records, while `02-portfolio/current-portfolio-review.md` still reports 58/58. The dated audit can remain historical, but the headline needs an explicit “superseded by” pointer or regeneration.
2. Step 4 in `04-operations/product-development-and-release-process.md` contains an accidental repository path inside the list of digital checks: `products/.../features`. Replace it with the intended generic term.
3. `05-webshop/environment-readiness.md` is an exact snapshot of a changing website worktree. Refresh it after the active website branch-reconciliation/hardening phase rather than treating its branch counts as permanent truth.
4. The `metriCreate` logo remains unselected and uncleared under `BRD-001`. The concepts therefore use a provisional wordmark and must not be treated as public brand masters.
5. The visual-direction record names violet, while the new preference introduces anthracite/orange. Record the selected palette semantically after choosing a direction.
6. Configuration is central to the new positioning but remains outside the transactional MVP. Marketing, navigation and feature flags must consistently label Studio as preview/development until its gate passes.
7. The new chatbot idea has no scope, risk or cost record.

## Recommended folder additions

Do not silently change the binding decisions from this concept review. Add or update them after owner selection:

| File/record | Recommended addition |
|---|---|
| `01-strategy/business-model.md` | State digital models as the primary offer; printed fulfillment as secondary. Add license-tier and update-entitlement decisions. |
| `01-strategy/brand-architecture.md` | Add the shared-shell/different-hierarchy rule, selected `metriCreate` visual direction and final semantic palette. |
| `01-strategy/customers-and-value-proposition.md` | Add printer-owner skill/compatibility segments and the “future-facing builder” tone hypothesis. |
| `03-market/validation-plan.md` | Test personal versus commercial print license, fixed versus configurable demand, Studio comprehension and support burden. |
| New `05-webshop/multi-brand-application-architecture.md` | Record brand resolution, deploy topology, shared data invariants, cross-domain state, Auth/session behavior, canonical/SEO and rollback. |
| New `05-webshop/metricreate-experience-blueprint.md` | Freeze route hierarchy, content priority, states, filters, product-card metadata and Studio preview behavior. |
| `05-webshop/mvp-scope.md` | Add brand-context acceptance tests and a non-transactional Studio-preview gate. |
| `07-roadmap/tasks.md` / `mvp-tasks.csv` | Add `BRD-002` visual selection/clearance, `WEB-002` multi-brand shell, `SEO-001` dual-domain indexing, `LIC-001` license/update decision and later `AI-001`. |
| `07-roadmap/risk-register.md` | Add dual-domain drift/SEO duplication, assistant hallucination/data cost, license ambiguity and configuration support load. |
| `08-finance/unit-economics.md` | Add configured-revision compute/storage/review cost and contribution by license tier. |

## Decision sequence

1. Select `Midnight Forge`, `Teal Blueprint` or `Carbon Pulse`.
2. Select and clear a compatible `metriCreate` logo/wordmark; do not derive a production logo from the raster concepts.
3. Approve the digital-primary offer hierarchy and decide which license/update hypotheses enter validation.
4. Write the multi-brand application blueprint before creating a second frontend deployment.
5. Build one shared-shell visual prototype with real release-gated data and compare both domains at desktop/mobile widths.
6. Keep Studio and assistant feature-gated until deterministic configuration, privacy, cost and evaluation evidence exists.

Recommended current decision: **Midnight Forge as the base system, with the stronger condensed section typography from Carbon Pulse and the teal/aqua continuity of Teal Blueprint.** Do not blend their layouts or use three competing accent systems.
