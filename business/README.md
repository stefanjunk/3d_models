# metriMade / metriCreate business workspace

Status: working business source of truth, reviewed 2026-08-28.

Legal operator: `Stefan Junk Holding UG (haftungsbeschränkt)`, founded in 2019; umbrella business designation: `JuSt Innovation`. The intended public names are `metriMade` and `metriCreate`. See the [operator profile](06-legal-compliance/operator-profile.md), [responsibility matrix](06-legal-compliance/responsibility-and-signing-matrix.md) and [brand/domain clearance record](06-legal-compliance/brand-and-domain-clearance.md); launch remains blocked pending the remaining verification and approvals.

This folder turns the material in `research/market/`, the local 3D-model workspace, and the webshop snapshot into one focused plan. It supersedes the scattered task lists for business prioritization; those files remain research inputs, not current commitments.

## Business in one paragraph

**metriMade** is the premium, non-technical consumer storefront for personalized products that combine aesthetics with useful integration: smart decor, attractive space savers and practical objects for living and office environments. It presents a deliberately curated subset of the wider catalog, with guided choices and an `as-is` printed-product path for customers who do not want to think about 3D printing. **metriCreate** is the broader, more technical maker storefront and parameterization environment for hobbyists, tinkerers and curious customers. It can offer many kinds of lawful, commercially released 3D products, exact model downloads and optional printed orders. A metriMade product links to the same underlying metriCreate product/revision when a customer chooses advanced parameterization or a digital model. Both brands are operated by the same legal entity and share one controlled product source of truth.

## Current decision

The controlled MVP may launch after **at least one** low-risk product has a complete `P5` commercial release package and the shop transaction gates pass. Three related releases remain the preferred first catalog, but products two and three are optional for the MVP date and may remain honestly labeled development/waitlist content:

1. `MM-ORG-001` DrawerFit Modular — `P2` digital candidate and preferred first P5 path; see the [P5 gap analysis](02-portfolio/mm-org-001-p5-gap.md).
2. `MM-PER-001` NameForm Bookends — `P2` parametric digital candidate; slicer, physical and commercial gates open.
3. `MM-ORG-002` ShelfFit Mini Bins — `P2` parametric digital candidate; slicer, physical and commercial gates open.

The versioned portfolio audit finds at least one local neutral/manufacturing 3D artifact for **91 of 91 records**; 76 also have detected parametric source and 59 have at least one 3MF. Uncommitted product work is deliberately excluded from those versioned totals. Model coverage is not release readiness: there are still **zero live or commercially release-ready products** under the stricter definition in [product lifecycle and release gates](02-portfolio/product-lifecycle-and-release-gates.md). `MM-MKR-001` CyberVault is the closest technical release-pipeline pilot, but it is not a launch hero for the small-space value proposition.

The first transactional release remains digital-only, Germany-only, with one safe-core 3MF per revision and therefore belongs to `metriCreate`. `metriMade` may present the curated consumer proposition honestly, but `as-is` printed checkout remains disabled until one SKU passes printed-fulfillment qualification. Advanced parameterization remains disabled until the `metriCreate` configuration pipeline passes its own gate. This staging implements the two-brand architecture without pretending that all three fulfillment modes are ready at once.

## Navigation

| Topic | Source of truth |
|---|---|
| Business idea and boundaries | [Business idea](01-strategy/business-idea.md) |
| Brands and names | [Brand architecture](01-strategy/brand-architecture.md) |
| Brand assets and logo history | [selected metriMade vector assets](01-strategy/brand-assets/metrimade/README.md), [concept/provenance sheets](01-strategy/logo-concepts/README.md) |
| Customer and offer | [Customers and value proposition](01-strategy/customers-and-value-proposition.md) |
| Revenue and channels | [Business model](01-strategy/business-model.md) |
| Decisions and risks | [Decisions/open questions](01-strategy/decisions-and-open-questions.md), [risk register](07-roadmap/risk-register.md) |
| Initial portfolio | [Initial portfolio](02-portfolio/initial-portfolio.md) |
| DrawerFit P5 critical path | [MM-ORG-001 P5 gap analysis](02-portfolio/mm-org-001-p5-gap.md) |
| Every local model reviewed | [Current portfolio review](02-portfolio/current-portfolio-review.md), [artifact audit](02-portfolio/model-artifact-audit.md) and `product-portfolio.xlsx` |
| Status meanings | [Product lifecycle](02-portfolio/product-lifecycle-and-release-gates.md) |
| Unknown downloads | [External-model exclusion](02-portfolio/external-model-exclusion.md) |
| Research findings | [Market synthesis](03-market/market-research-synthesis.md) |
| Assumptions to test | [Market validation plan](03-market/validation-plan.md) |
| Product-to-release workflow | [Product release process](04-operations/product-development-and-release-process.md) |
| Digital and printed operations | [Digital fulfillment](04-operations/digital-fulfillment.md), [printed fulfillment](04-operations/printed-fulfillment.md) |
| Customer operations | [Support and incidents](04-operations/customer-support-returns-incidents.md) |
| MVP shop | [MVP scope](05-webshop/mvp-scope.md), [website gap review](05-webshop/website-gap-review.md) |
| metriCreate business and website concept | [Business/website review and visual directions](05-webshop/metricreate-business-and-website-review.md) |
| Firebase environments and launch readiness | [Environment readiness](05-webshop/environment-readiness.md) |
| Required catalog content | [Catalog requirements](05-webshop/catalog-content-requirements.md) |
| Legal operator and public identity | [Operator profile](06-legal-compliance/operator-profile.md) |
| Responsibility and signing roles | [Single-person responsibility matrix](06-legal-compliance/responsibility-and-signing-matrix.md) |
| Brand/domain evidence | [Brand and domain clearance](06-legal-compliance/brand-and-domain-clearance.md) |
| Brand goods/services and signature | [Goods/services scope](06-legal-compliance/brand-goods-services-scope.md), [brand risk approval](06-legal-compliance/brand-risk-approval.md) |
| Legal/compliance workstream | [Launch legal topics](06-legal-compliance/launch-legal-topics.md) |
| Execution | [Now/next/later](07-roadmap/now-next-later.md), [tasks](07-roadmap/tasks.md), [90-day plan](07-roadmap/90-day-plan.md) |
| Unit economics | [Economics](08-finance/unit-economics.md) |
| Metrics and review rhythm | [Metrics](08-finance/metrics-and-review-cadence.md) |
| Inputs and review scope | [Source index](09-sources/source-index.md) |
| Production resources and stock | [Inventory](10-inventory/README.md) |

## Operating rule

No product reaches the public catalog because a mesh exists or automated tests pass. A sellable revision needs traceable source rights, deterministic files, slicer evidence, physical validation appropriate to its claims, product-safety review, customer documentation, price/cost approval, real media, and a signed release decision. Unknowns block the relevant gate rather than being recorded as assumptions.
