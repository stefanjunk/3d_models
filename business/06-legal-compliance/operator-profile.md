# Legal operator profile

Document status: `WORKING_DRAFT_LAUNCH_BLOCKED`  
Profile owner: Stefan Junk, founder and managing director  
Last factual update: 2026-08-25  
Evidence basis: managing-director statements dated 2026-08-24 and 2026-08-25 and founder-provided screenshots of register and VAT data. The exact legal-form suffix, founding year, public email and VAT-ID assignment have been confirmed by the managing director. The first W-IdNr. is recorded as an expressly provisional planning assumption under the published BZSt assignment rule. A retained current register extract/representation wording, W-IdNr. verification and signed profile approval are still required.

This is the source of truth for `GOV-001`. Public legal texts, checkout, order confirmations, invoices, product information and manufacturer/economic-operator records must use the legal entity below. A brand or business designation must not replace the legal entity.

## Confirmed operator data

| Field | Recorded value | Evidence/status |
|---|---|---|
| Legal operator | `Stefan Junk Holding UG (haftungsbeschränkt)` | Exact firm and suffix confirmed by managing director on 2026-08-24; retain a current register extract in launch evidence |
| Legal form | Unternehmergesellschaft (`UG (haftungsbeschränkt)`) | Confirmed by managing director on 2026-08-24 |
| Year founded | `2019` | Confirmed by the founder/managing director on 2026-08-25; retain the exact incorporation/register date from the current register record if needed |
| Business/service address | `Sterkrader Straße 24, 13507 Berlin, Germany` | Founder-provided |
| Managing director / legal representative | `Stefan Junk` | Founder-provided |
| Managing-director address | `Sterkrader Straße 24, 13507 Berlin, Germany` | Internal operator record; do not duplicate as a separate public personal address where the company address is sufficient |
| Register | Handelsregister B (`HRB`) | Screenshot provided |
| Register court | Amtsgericht Charlottenburg | Screenshot provided |
| Register number | `HRB 205053 B` | Screenshot provided |
| VAT identification number | `DE328975027` | Screenshot provided and assignment confirmed by the managing director; retain the BZSt/tax record in launch evidence |
| Public contact email | `stefan@stefanjunk.com` | Supplied by the managing director on 2026-08-24; Stefan Junk is the mailbox owner and responsible responder |
| Internal workforce/governance model | One employee and one managing director: Stefan Junk | Confirmed by managing director on 2026-08-24; responsibilities are recorded in the linked matrix |
| Legal/operator country | Germany (`DE`) | Derived from the Berlin address and German register; confirm in signed profile |
| Initial transactional market | Germany only | Existing MVP decision; separate legal/tax approval remains open |

The screenshot also lists court contact addresses at Hardenbergstraße 31 and Amtsgerichtsplatz 1. These are addresses of the court/register services, not company addresses, and must not be used as the operator address.

## Trading and public names

| Layer | Name | Rule |
|---|---|---|
| Legal contracting party | `Stefan Junk Holding UG (haftungsbeschränkt)` | Required anywhere the seller, contracting party, invoice issuer, manufacturer or responsible economic operator is identified |
| Umbrella business designation | `JuSt Innovation` | Public-facing business designation only; show with a clear link to the legal operator, for example `JuSt Innovation ist eine geschäftliche Bezeichnung der Stefan Junk Holding UG (haftungsbeschränkt)` after legal review |
| Store / consumer brand | `metriMade` | Working public spelling supplied by the founder; brand clearance and final capitalization approval remain open |
| Store / creation-service brand | `metriCreate` | Working public spelling supplied by the founder; exact MVP storefront role, brand clearance and final capitalization approval remain open |

Recommended legal identity pattern for review, not yet approved website copy:

> Stefan Junk Holding UG (haftungsbeschränkt)  
> handelnd unter JuSt Innovation / metriMade [or metriCreate as applicable]  
> Sterkrader Straße 24, 13507 Berlin, Deutschland  
> Vertreten durch den Geschäftsführer Stefan Junk  
> Eingetragen im Handelsregister des Amtsgerichts Charlottenburg unter HRB 205053 B  
> E-Mail: stefan@stefanjunk.com  
> USt-IdNr.: DE328975027

Do not publish this block until the open fields below are closed and counsel/legal owner approves the exact wording.

## Open fields blocking `GOV-001`

| Required item | Current state | Acceptance evidence / owner |
|---|---|---|
| Current register extract, registered office and exact representation rule | `PARTIAL` | Firm/legal form confirmed by managing director; retain current official extract and record whether sole representation and any § 181 BGB exemption apply |
| Monitored legal/contact email for rapid electronic contact | `CLOSED` | `stefan@stefanjunk.com`; owner and responder Stefan Junk |
| Additional direct contact route, if required by the final legal review | `OPEN` | Approved contact method and tested website flow |
| Confirmation that the stated address is the current service/business address usable for legal notices | `CLOSED / legal wording review pending` | Managing-director statement dated 2026-08-24; reconcile with register/legal review |
| VAT ID assignment and current validity | `CLOSED / evidence retention pending` | `DE328975027` confirmed by managing director; retain BZSt/tax evidence with launch records |
| Economic identification number (`W-IdNr.`), if already assigned and required in the public profile | `ASSUMED / NOT VERIFIED`: `DE328975027-00001` | Founder authorized this planning assumption on 2026-08-25. It follows the BZSt rule for a USt-IdNr. assigned by 2024-11-30 plus first discriminator `-00001`; verify in BZSt/ELSTER before external publication or official use |
| Supervisory authority or regulated-profession information | `OPEN / likely N/A for the base webshop` | Written applicability decision; recheck for product-specific regulated activity |
| Liquidation status | `OPEN` | Current register extract; must be stated if applicable |
| Launch responsibility matrix | `CLOSED` | [Single-person responsibility and signing matrix](responsibility-and-signing-matrix.md), owner Stefan Junk |
| Authorized internal approver | `CLOSED` | Stefan Junk is the sole internal business approver and managing director; external representation wording remains subject to the register extract |
| Signed operator profile and legal approval/version | `OPEN` | Dated signature/approval by the legal operator and legal reviewer |

## Publication and consistency controls

- Keep the legal operator identical in the imprint, checkout seller disclosure, order confirmation, invoices/credits, terms, privacy notice, withdrawal flow, support messages and payment-provider profile.
- Use `JuSt Innovation`, `metriMade` or `metriCreate` only as additional business/brand identifiers; never make them appear to be a separate contracting entity unless one is created and documented.
- Where a product record identifies a manufacturer or economic operator, map the role explicitly to the legal operator and exact product revision.
- Do not publish tax numbers other than the approved VAT identification number; a domestic tax number is not collected in this profile.
- Review the operator profile after every register, address, representative, tax, contact, provider or market change and before each production launch approval.

## W-IdNr. note

The Wirtschafts-Identifikationsnummer identifies economically active persons/entities in tax and administrative procedures. It is assigned automatically by the BZSt and does not replace the USt-IdNr., domestic tax number or a natural person's IdNr. For businesses that already had a USt-IdNr. by 2024-11-30, the BZSt uses the same `DE` plus nine-digit base and adds the first activity discriminator `-00001`. On the founder's instruction, `DE328975027-00001` is used internally as the provisional planning value. It must remain labelled `ASSUMED / NOT VERIFIED` and must not be presented externally as a verified assignment until the BZSt/ELSTER record has been checked.

## Completion rule

`GOV-001` may move to `Complete` only when every applicable open field has evidence, non-applicable fields have a written reason, public/legal/payment profiles are reconciled, and the version is signed. The identity data currently recorded is sufficient to start implementation and legal drafting but not to enable production checkout.
