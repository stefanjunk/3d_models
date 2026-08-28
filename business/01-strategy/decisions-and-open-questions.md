# Decisions and open questions

## Decisions made in this restructuring

- Legal operator: `Stefan Junk Holding UG (haftungsbeschränkt)`; founded in `2019`; exact suffix and founding year confirmed by the managing director. Umbrella business designation: `JuSt Innovation`.
- Two connected storefronts are binding: `metriMade` is the premium guided consumer subset; `metriCreate` is the broader technical catalog, configuration environment and digital-download store.
- Every `metriMade` item maps to the same underlying `metriCreate` product ID/revision; not every `metriCreate` release is eligible for `metriMade`.
- `metriMade` promises personalized aesthetics plus practical home/office integration. `metriCreate` promises configurable, versioned and optionally self-printable 3D products across a thematically open but release-gated catalog.
- Owned catalog; no third-party marketplace in the MVP.
- Target initial products: DrawerFit Modular, NameForm Bookends and ShelfFit Mini Bins.
- MVP release threshold: at least one product must reach `P5` and pass staging/transaction gates. Three released products are preferred for the initial catalog but are optional for the MVP date.
- Market interviews, measurement-guide trials, waitlist and price experiments are recommended learning work, not a production-launch dependency. Lack of interest blocks expansion investment, not an otherwise complete one-product MVP.
- First transaction scope: fixed-revision safe-core 3MF on `metriCreate`, Germany only, after all gates pass.
- Printed products remain part of the offer strategy but launch after one SKU's fulfillment process qualifies.
- Self-service configuration follows a successful manual measurement/variant workflow.
- Every external-directory download is excluded.
- Product existence means `P5 Commercial release` or later; current count is zero.
- metriMade V10 concept `08` is selected as the new logo direction and redrawn as vector revision `MM-BRAND-001-R1`; legal/similarity clearance remains open.
- New physical metriMade product revisions use the generated `MM-WM-001-R1` recess containing `metriMade.com`, exact product ID and `v`-prefixed semantic version; historical releases are never overwritten.

## Decisions that require an accountable owner

| Decision | Needed by | Default planning assumption | Consequence if unresolved |
|---|---|---|---|
| Register representation wording, W-IdNr. verification and signed operator approval | before legal/payment production setup | exact firm, 2019 founding year, public email, VAT ID, provisional W-IdNr. `DE328975027-00001` and single-person responsibility matrix recorded | checkout blocked until verified, signed and reconciled |
| Shared catalog schema and cross-domain handoff | before implementing both storefronts | one product/revision record, brand-specific content and eligibility, preserved SKU/configuration context | duplicated catalog data and broken customer journey |
| Domain ownership and mark clearance | before public brand launch | user-stated domains | brand/publication blocked |
| Authoritative launch language | before final content | German | publication blocked |
| Printer envelope for digital catalog | before product requirements | 220 × 220 × 250 mm common printer | candidate can be excluded or segmented |
| Customer digital license and update entitlement | before P5 | personal-use license; exact purchased revision | file sale blocked |
| Support scope and remedy for measurement error | before P5 | guided measurement, transparent tolerance | claims/refund flow blocked |
| VAT/tax/accounting treatment | before Stripe live | Germany digital only | checkout blocked |
| Printed pilot SKU and capacity | after digital review | one standard SKU | print flag remains off |
| First `metriMade` transactional SKU and consumer presentation standard | before `metriMade` checkout | first qualified printed small-space SKU | `metriMade` remains preview/waitlist only |

## Questions to answer with evidence

- Which problem statement creates qualified interest: fit, recovered space, personalization or print confidence?
- Can typical customers measure reliably enough for the stated tolerance?
- Which personalization inputs can be supported without manual artwork/right issues?
- What support effort follows a digital sale?
- What printer sizes and materials dominate the initial audience?
- Does the printed preference justify fulfillment setup after the digital MVP?
- Which `metriCreate` categories create repeat demand without overwhelming one-person rights, safety and support capacity?
- Which objective aesthetic/content criteria distinguish `metriMade` eligibility from ordinary `metriCreate` availability?
