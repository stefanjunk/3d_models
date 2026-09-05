# Catalog and product-page requirements

## P2 development content

Before a product can be shown as a P2 development candidate, retain an English
product description, a whole-product concept image, a separately identified
render of the current digital model, and the complete oriented/support-planned
3MF print set for the exact revision. These are controlled development assets,
not evidence of a real print and not approved public listing content. Label the
concept and render truthfully, and do not infer physical finish, fit, safety,
rights clearance, or availability from them.

## Product record

Every public product maps to one approved SKU/revision and includes:

- public title, family, category and stable URL;
- concise customer problem and value;
- exact revision and release date;
- digital, printed or both delivery modes actually enabled;
- exact included file/part list and hashes in the internal manifest;
- physical dimensions and fit envelope with tolerance and measurement method;
- common-printer build-volume requirement and whether parts are segmented;
- tested material, nozzle, layer/profile assumptions, supports and estimated print information from the actual slicer;
- intended use, supported load/items, age/user limits if applicable, foreseeable misuse and exclusions;
- required purchased components and tools;
- instructions, assembly/use/care, warnings, disposal and support;
- digital license and update policy;
- price, VAT presentation, country availability, access/delivery time;
- real photos and labeled renders, meaningful alt text, no unsupported performance badge;
- manufacturer/operator/product identification and safety information required for the enabled delivery mode/market.
- for physical metriMade products, the exact visible geometry mark content (`metriMade.com`, product ID and version), placement and match to the release manifest.

## Customization data

For a future configured product, store both customer input and normalized manufacturing values:

- units, measurement schema/version and customer confirmation;
- allowed ranges, increments, dependent rules and rejected combinations;
- preview disclaimer and final dimensions;
- server-side validation result, generator/build version and output hash;
- price calculation version and manual/automatic approval;
- privacy/retention classification for names, images or personal measurements.

## Media evidence

Minimum per launch product:

- one truthful hero render labeled as a render when applicable;
- one real photo of the exact final-revision test print;
- fit/scale image with dimensions;
- included-parts view;
- one use image that does not imply an untested claim;
- alt text that describes the useful information, not decorative marketing prose.

Compare render and physical print before release. If texture, color, finish, part split or proportions materially differ, update the media or block the claim.

## Brand-specific presentation from one product record

Every released product has one authoritative ID/revision, safety record and fulfillment truth, with separate presentation fields:

- `metriMade`: benefit-first consumer title, premium lifestyle media, room/office context, concise guided options, `as-is` finished-product price and an optional advanced link;
- `metriCreate`: technical title/category, complete file/format/revision information, configurable parameter ranges, printer/process envelope, detailed exclusions and download/print-order choices;
- shared and never weakened: legal seller, exact product/revision identity, warnings, tested scope, rights/notices, support, withdrawal/remedy information and availability.

A `metriMade` page must not hide a material warning to look simpler. It may progressively disclose technical detail, but the customer must see what affects safe use, fit, care, price and the contract. The advanced link must carry the exact product ID/revision and must not land on a similar but different metriCreate product.

## Content states

- `concept`: may be shown only outside the sellable catalog with an honest label.
- `staged`: exact `P5` release, internal/test users only.
- `live`: exact `P7` release, country/delivery gates enabled.
- `withdrawn`: no new sale/download as the decision requires; support and historical order records remain.

## Translation

German is the authoritative launch language. English is published only after every safety, legal, measurement, support and product statement has a reviewed equivalent. No route may silently fall back to outdated demo copy.
