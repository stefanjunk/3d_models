# Product lifecycle and release gates

## Status scale

The portfolio workbook uses one stage for progress and separate evidence columns for digital, physical, rights, safety, commercial, and shop status.

| Stage | Meaning | May appear in public shop? |
|---|---|---|
| `P0 Idea` | research concept only; no controlled product source | No |
| `P1 Model present` | a local source or mesh exists; provenance and quality may be unknown | No |
| `P2 Digital candidate` | controlled source/revision and automated geometry checks exist | Only as clearly labeled development content, never for sale |
| `P3 Physical prototype` | intended slicer/profile reviewed and at least one physical prototype or coupon tested | No |
| `P4 Product qualified` | reproducibility, fit/use tests, rights, safety, and claims evidence complete for scope | No; commercial package still open |
| `P5 Commercial release` | signed release manifest, customer package, price/cost, license, media, and support are approved | Yes in staging |
| `P6 Staged` | exact revision published and transaction/download or fulfillment flow passed | Staging only |
| `P7 Live` | production release approved and monitored | Yes |
| `HOLD` | deliberately deferred, off-strategy, or disproportionate risk | No |
| `EXCLUDED` | forbidden portfolio input, including every model under an `external` directory | No |

For planning, an **existing commercial product** means `P5` or later. A mesh, STEP file, 3MF, “FINAL” directory name, green geometry test, or successful one-off print does not by itself meet that definition.

## Evidence gates for each revision

### G0 — Scope

- product owner, stable SKU, revision, intended user/use, delivery modes, markets;
- explicit exclusions and reasonably foreseeable misuse;
- approved requirements and concept.

### G1 — Source and rights

- editable source of truth and deterministic build path;
- every model, reference image, font, icon, library part, AI-assisted input, and purchased component recorded;
- license, attribution, redistribution, trademark/design/patent review resolved for the commercial scope;
- unknown-source assets produce `BLOCK`, not “review later.”

### G2 — Digital manufacturing candidate

- correct units and dimensions;
- closed/manifold positive-volume bodies as applicable;
- build-volume, walls, clearances, minimum features, component count, orientation, and intended file format checked;
- exact checksums and file inventory recorded;
- supported core 3MF opens in the target slicer without unsupported extensions.
- for physical metriMade scope, the generated `metriMade.com` + product-ID/version engraving is integrated, orientation/remaining wall are checked, and the exact profile/cutter/manufacturing hashes are recorded.

### G3 — Physical qualification

- actual production slicer/profile recorded;
- fit coupons before full prints where appropriate;
- watermark coupon with intended material, first-layer settings and bed surface; domain, product ID and version legible without guessing where the mark is required;
- at least one prototype iteration followed by three reproducible final-revision prints for launch SKUs;
- dimensions, tolerances, stability, surface, assembly, wear/cycles, and misuse tested according to product claims;
- photos, measurements, printer/material lots, operator, date, failures, and corrective revisions retained.

### G4 — Commercial and customer package

- PASS/WARN/BLOCK risk decision and product-safety assessment;
- supported/unsupported uses, warnings, instructions, digital license, support scope;
- real product media and accessible alt text; renders labeled as renders;
- unit economics, price, tax class, countries, delivery time, refund/withdrawal treatment;
- release manifest ties the exact customer files, evidence, copy, and media to the revision.

### G5 — Staging and production

- second-person or explicitly independent review of rights, safety, render, and commercial data;
- staging publish, search/filter/detail/sitemap verification;
- successful and negative purchase/download tests or physical-order flow;
- takedown and entitlement revocation test;
- signed production decision and monitoring owner.

## Decision vocabulary

- `PASS`: the requirement has direct evidence for this exact revision and scope.
- `WARN`: usable only with an explicit limitation that is visible to the customer and accepted by the approver.
- `BLOCK`: sale or the affected delivery mode is prohibited until resolved.
- `N/A`: genuinely outside the approved product/delivery scope, with rationale.
- `UNKNOWN`: evidence was not found; treated as `BLOCK` at a release gate.

## Revision rule

Any geometry, material, profile, included-file, safety, claim, license, or instruction change receives a new revision and impact assessment. Evidence may be reused only when the manifest identifies it and the changed feature cannot invalidate it. Never replace a sold file in place.
