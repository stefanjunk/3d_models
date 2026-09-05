# Product development and release process

## One SKU, one evidence chain

Each product has a stable folder/record keyed by SKU and revision. The same revision identifier appears in CAD parameters, exports, checksums, tests, catalog data, customer package, orders, support cases, and takedowns.

For every newly manufactured metriMade revision, the same identity also appears as a recessed geometry mark on the product: `metriMade.com` and `<PRODUCT_ID> · v<VERSION>`. Generate it with the versioned [metriMade watermark package](../../tools/metrimade-watermark/README.md); never type or edit the trace line independently.

## Workflow

1. **Select:** product owner records customer problem, fit envelope, intended use, excluded uses, markets, and delivery modes.
2. **Specify:** requirements, measurable acceptance criteria, printer/material constraints, safety questions, and configuration limits are approved.
3. **Design:** editable source of truth, components, datums, parameters, licenses, and deterministic build are established.
4. **Digitally validate and enter P2:** geometry, dimensions, interfaces,
   features, build volume, orientation, formats, and hashes are checked. Create
   the English product description, whole-product concept image, separate
   current-model render, and one complete product 3MF with intended part
   quantities, build orientation, and support decision; bind them in
   `p2-stage/p2-manifest.json` and require `validate-p2-stage` PASS.
5. **Prototype:** coupons first, then a complete intended-profile print. Failures become revisions, not undocumented sanding/scaling instructions.
6. **Qualify:** three reproducible final-revision prints; dimensional, fit, use, misuse, stability, wear/cycles, and appearance evidence appropriate to claims.
7. **Commercialize:** rights, product-safety decision, instructions, warnings, license, price/cost, media, alt text, translations, support and release manifest.
8. **Stage:** independent approvals, operator upload, automated 3MF checks, catalog review, transaction/download tests, negative access and takedown tests.
9. **Release:** signed production decision; retain exact files and evidence; monitor support, refunds, failures, and incidents.
10. **Revise/retire:** perform impact assessment, never overwrite customer history, and retain withdrawal/takedown capability.

## Minimal release record

- SKU, revision, status, owner, approvers, decision date;
- intended use, user, countries, digital/printed scope, claims and exclusions;
- source tree or build identifier and all input provenance;
- customer file names, formats, units, hashes, size and supported slicer profile;
- digital validation report and limitations;
- physical test matrix, results, photos, material/printer/profile/lot/operator;
- safety/risk decision and required warnings;
- license, instructions, support policy and change log;
- price, cost assumptions, tax class, media and catalog-copy versions;
- staging checks, production deployment reference and rollback/takedown route.
- generated watermark asset revision, visible domain/product/version, SVG/DXF/cutter hash, integrated manufacturing-file hash, placement/orientation and coupon evidence where a physical metriMade part is in scope.

## Product-mark invariant

Before a physical metriMade release can pass digital validation, compare four locations: authoritative product manifest, generated watermark metadata, integrated manufacturing mesh and public/package identification. Product ID and version must match exactly in all four. The mark must read normally from the finished product's viewing side, sit on a nonfunctional low-stress surface, leave at least 0.80 mm remaining wall, and pass the intended slicer plus a physical coupon.

Changing the logo geometry, domain, product ID, version, size, depth, orientation or placement changes product geometry. It therefore requires a new product revision and impact assessment. Existing JuSt Innovation or DingGenau-marked releases remain immutable; migrate only by releasing a new revision with new hashes and affected tests.

## Initial SKU test burden

Use a staged physical plan rather than immediately printing three full sets:

1. calibration/fit coupon;
2. one prototype of the chosen revision;
3. revise if any criterion fails;
4. three complete prints of the final unchanged revision with the intended profile;
5. repeat any claim-specific use and misuse tests on the defined sample count.

This keeps the reproducibility requirement meaningful while avoiding repeated production of a known-bad draft.

## Ownership

Even if one person holds several roles, the record must name the role responsible for product, CAD, test, rights, safety, commercial data, publishing, and release. The final four shop approvals should receive an independent review where practical. Self-approval must be visibly recorded as a temporary MVP exception, never implied.
