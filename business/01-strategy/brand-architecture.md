# Brand architecture and naming

## Operator and naming hierarchy

| Layer | Recorded name | Function |
|---|---|---|
| Legal operator | `Stefan Junk Holding UG (haftungsbeschränkt)` | Contracting party, seller, invoice issuer and accountable operator |
| Umbrella business designation | `JuSt Innovation` | Business identity operated by the legal entity; not a separate company |
| Premium consumer storefront | `metriMade` | Curated, aesthetic, guided selection and `as-is` printed-product ordering |
| Maker/configuration storefront | `metriCreate` | Broad technical catalog, parameterization, digital-model downloads and optional printed orders |

The founder supplied the spellings above on 2026-08-24, confirmed the exact `UG (haftungsbeschränkt)` suffix, and confirmed control of `metriMade.com` and `metriCreate.com` through Cloudflare on 2026-08-25. Name/mark clearance and retained domain evidence remain subject to the [operator profile](../06-legal-compliance/operator-profile.md) and [brand clearance record](../06-legal-compliance/brand-and-domain-clearance.md).

## Binding roles

| Name | Role | Audience | Primary message |
|---|---|---|---|
| `metriMade` / `metriMade.com` | Premium curated consumer storefront | non-technical customers seeking personalized, attractive products for home or office | Beautifully made for your space |
| `metriCreate` / `metriCreate.com` | Technical maker catalog and parameterization storefront | hobby technologists, makers, tinkerers and advanced/customizing customers | Configure it. Print it. Make it yours. |

The architecture decision is two connected storefronts on one product/revision system. `metriMade` is not a separate inventory: it is a curated subset of eligible `metriCreate` releases. **metriMade — powered by metriCreate** may be used to explain the relationship, but each site retains its own audience, visual language and customer journey. Both must identify `Stefan Junk Holding UG (haftungsbeschränkt)` as the legal seller; neither brand is a separate contracting entity.

## Customer paths

| Entry point | Customer intent | Route | Commercial result |
|---|---|---|---|
| `metriMade` | “I want this attractive product without technical decisions.” | Select approved `as-is` variant and order a professionally printed item | Printed order after `PRINT_FULFILLMENT_READY` |
| `metriMade` | “I like this product but want to adapt dimensions/details.” | `Advanced anpassen` deep-links to the exact shared SKU/revision in `metriCreate` | Validated parameterized order after `CONFIGURATION_FULFILLMENT_READY` |
| `metriCreate` | “I want to configure, inspect or experiment.” | Browse the broad catalog and edit only allowed parameters | Frozen configured revision for print order or download |
| `metriCreate` | “I will print it myself.” | Buy/download the exact released 3D model and documentation | Licensed immutable digital release |

The handoff must preserve SKU, source revision, configuration schema, price context, locale and return URL. A configured output becomes its own immutable order/release record; it never silently overwrites the base product.

## Catalog relationship

- `metriCreate` is thematically broad rather than limited to storage or decor. It can include maker utilities, mechanisms, hobby-tech models, figures, drone-related concepts, fluid systems and other lawful 3D-printable products.
- `metriMade` includes only releases that meet its additional consumer curation criteria: premium appearance, understandable use, low cognitive load, guided choices, credible media and suitability for home/office presentation.
- Every `metriMade` item has a backing `metriCreate` product ID/revision. Not every `metriCreate` item is eligible for `metriMade`.
- “Broad catalog” never means automatic publication. Toys/figures, drones/aviation, drinking-water or filter systems, electrical, body-contact, structural, pressure, weapon/weapon-adjacent and other regulated or safety-critical categories remain blocked until category-specific rights, safety, test, insurance and market gates pass. Unlawful products are categorically excluded.

## Visual direction

| Brand | Visual character | Prefer | Avoid |
|---|---|---|---|
| `metriMade` | warm, premium, tactile, calm, interior-oriented and accessible | elegant negative space, sculptural/nested forms, balanced proportions, refined typography, warm neutral/earth/sage palette | CAD grids, dimension arrows, nodes, gears, printer imagery and overt maker-tech cues |
| `metriCreate` | precise, inventive, technical, configurable and playful | parametric curves, control points, modular geometry, layers, configuration states, deep blue/cyan/violet palette | cold enterprise-software sameness, generic gears, printers/nozzles, rockets and unsafe/weapon imagery |

## Selected metriMade identity

Stefan Junk selected V10 concept `08` on 2026-08-25. The reproducible vector candidate is [metriMade `MM-BRAND-001-R1`](brand-assets/metrimade/README.md): a spatial negative-space `M` with a navy left/top plane, teal right plane, warm beige fitted floor and restrained light-aqua inner edge. Its binding colors are navy `#112431`, teal `#08777D`, aqua `#7FD5D3`, sand/beige `#C7AB82`, and warm canvas `#FBFAF7`.

The compact mark, stacked logo, horizontal website lockup and monochrome versions share the same source geometry. The wordmark spelling is always `metriMade`. Selection is complete; name/device-mark searches, similarity review and the signed rights/risk decision remain open under `BRD-001`.

For physical product traceability, new metriMade product revisions use the [product-specific engraving standard](../../metrimade-watermark/README.md): `metriMade.com` plus the exact product ID and `v`-prefixed semantic version. This manufacturing mark is monochrome and deliberately omits the color-only aqua micro-edge at small size.

## Naming system

- Company/operator name: `Stefan Junk Holding UG (haftungsbeschränkt)`; exact suffix confirmed, current register/representation evidence to be retained.
- Umbrella business designation: `JuSt Innovation`.
- Premium consumer/store brand: `metriMade`.
- Maker/configuration/store brand: `metriCreate`.
- Product public naming: descriptive German title plus stable product ID/SKU; no separate product-mark portfolio is currently planned.
- Existing names such as `DrawerFit`, `ShelfFit`, and `NameForm` are internal working labels until deliberately approved for public use.
- Product identifier: stable SKU plus semantic revision, for example `MM-ORG-001 / 1.0.0`.
- Physical metriMade identifier: recessed `metriMade.com` plus `<PRODUCT_ID> · v<VERSION>` generated from the exact release record.
- Variant identifier: separate size/material/color or approved-configuration code, never silently encoded by overwriting a revision.

## Claims to avoid until proven

Do not claim “perfect fit,” “universal,” “food safe,” “child safe,” “load bearing,” “waterproof,” “medical,” “ergonomic,” “indestructible,” or “sustainable” without a defined test and evidence. Prefer measured claims such as “designed for a 360 × 230 mm drawer” and publish the tolerance and measurement method.

## Open name work

The local naming research is directional, not legal clearance. Before launch:

- retain Cloudflare control, renewal, recovery and MFA evidence for `metrimade.com` and `metricreate.com`;
- clear `JuSt Innovation` as a business designation as well as the store brands;
- search DPMA, EUIPO, and relevant international registers in the intended goods/services classes;
- review similar business, product, and domain names;
- decide whether both word marks, selected logos or neither are registered initially;
- introduce the new metriMade logo and product mark into existing product assets only through a controlled new revision; never overwrite released files.

Until that work is signed off, brand-rights status is `BLOCK` for public launch.
