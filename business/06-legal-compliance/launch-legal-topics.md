# Launch legal and compliance workstream

Status: issue-spotting checklist, not legal or tax advice. Obtain qualified review for the actual operator, products, countries, providers and contract flow. Sources checked 2026-08-24.

## Company, brand and mandatory information

- Reconcile and approve the populated [operator profile](operator-profile.md): legal entity, service address, representative, register and VAT ID are recorded; exact register spelling, current evidence, contact channel, responsibility matrix and signatures remain open.
- Complete the website legal profile and ensure imprint, order confirmation, invoices, product information and manufacturer contact are consistent.
- Complete the [brand/domain clearance record](brand-and-domain-clearance.md) for `JuSt Innovation`, `metriMade`, `metriCreate`, logos and launch product-family names through domain evidence, DPMA/EUIPO/WIPO and market searches, and appropriate counsel review.
- Record ownership and commercial rights for every CAD/reference/font/library/AI-assisted input and render.

Germany's [§ 5 DDG](https://www.gesetze-im-internet.de/ddg/__5.html) sets provider-information requirements including identity/address and, depending on the operator, legal form, representation, contact, register and VAT data. The operator identity is now populated, but missing verification, contact, responsibility and approval fields remain a launch blocker, not a copywriting task.

## Consumer contract and withdrawal

- Approve German terms, digital license, product conditions, payment, delivery and support scope against the actual flow.
- Distinguish digital content, standard printed goods, and individually made/configured goods; do not reuse one withdrawal rule for all three.
- Capture any required express request/consent and acknowledgment for digital performance and provide contract confirmation on a durable medium.
- Implement the continuously accessible electronic withdrawal function, required input/confirmation flow and confirmation email; test it end to end.
- Define refunds, defective digital content remedies, updates, complaints and dispute handling.

The current [German Civil Code](https://www.gesetze-im-internet.de/bgb/BJNR001950896.html) includes § 356a on the electronic withdrawal function and § 312f on contract confirmation/digital-content consent records. Legal review should map the exact UI and email evidence to the current provisions before enabling checkout.

## Product safety and online offers

- Create an intended-use and foreseeable-misuse risk assessment for every digital and printed release.
- Identify the manufacturer/economic operator and retain technical documentation, revision traceability, complaints and corrective actions.
- Put required product identification, manufacturer contact, warnings and safety information in the online offer and customer package.
- Establish Safety Business Gateway/authority escalation, incident, recall, customer notice and takedown procedures.
- Decide whether and how home-printed outcomes change instructions, warnings, process limits and claims; do not assume a file-only sale removes product-safety exposure.

The EU [General Product Safety Regulation 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj/eng) includes manufacturer documentation/traceability duties and Article 19 information for distance-sale offers. Apply it product by product with counsel, especially where a digital file enables a physical consumer product.

The recast [EU Product Liability Directive 2024/2853](https://eur-lex.europa.eu/eli/dir/2024/2853/oj/eng) expressly includes digital manufacturing files in the product definition and applies to products placed on the market or put into service after 9 December 2026 following national transposition. Recheck German implementation and insurance/contract implications before that date; it is directly relevant to the file business.

## Tax, payments and accounting

- Decide digital sales countries as an allowlist with tax advice; Germany only is the launch assumption, not an automatic legal conclusion.
- Configure VAT/tax treatment, Stripe Tax if used, invoices/credits, refunds/chargebacks and accounting exports.
- Assess OSS and registrations before adding EU countries; retain transaction/location evidence for the required period.
- Verify payment methods and Strong Customer Authentication behavior for actual devices/countries.

The European Commission's [VAT One Stop Shop overview](https://europa.eu/youreurope/business/finance-and-tax/vat/one-stop-shop/index_en.htm) explains destination-based EU reporting options for covered cross-border supplies and record obligations. Confirm the precise treatment of downloads, custom services and printed goods with tax counsel.

## Privacy, providers and security

- Map actual Firebase, Google Cloud, Stripe, SMTP, logging, support and analytics data flows; list controllers/processors, purposes, legal bases, transfers and contracts.
- Implement data minimization, role access, retention/deletion schedules, export/access/deletion requests and breach response.
- Treat names, customer images and body/space measurements as customer data with purpose and retention limits.
- Avoid non-essential analytics/advertising at launch unless consent and provider configuration are complete.
- Align account deletion with necessary tax, contract, fraud and product-safety retention rather than deleting audit evidence blindly.

## Accessibility

- Test keyboard, focus, screen reader, labels/errors, contrast, zoom/reflow, captions/alt text and checkout/legal flows.
- Determine applicability and any microenterprise service exemption from the real legal entity and service scope; document the decision rather than assuming exemption.

The [BFSG § 3](https://www.gesetze-im-internet.de/bfsg/__3.html) contains the accessibility obligation and a service microenterprise exemption. Even if an exemption is confirmed, accessible implementation reduces commercial and support risk.

## Packaging, physical goods and environment

- Before shipping, clarify LUCID registration, system participation, packaging data reporting, packaging minimization, labeling/information and supplier/brand-owner responsibilities under the now-applicable packaging framework.
- Keep supplier declarations/technical documentation and record packaging material/weight by SKU.
- Define material, care, disposal and recycling statements without unsupported environmental claims.

Germany's [Central Agency Packaging Register guidance for shipping and online retail](https://www.verpackungsregister.org/en/topics/shipping-and-online-retail) explains registration, system-participation and packaging responsibilities for ecommerce under the current framework.

## International expansion controls

For every new country, approve consumer law/language, tax, payment, sanctions/export, product safety/economic operator, file license enforcement, privacy/transfer, packaging/EPR, carrier/returns and support. Expansion is an evidence-backed country configuration, not a global checkout toggle.

## Required signed launch artifacts

- operator/legal profile and counsel approval/version;
- brand/IP search record;
- country/tax/payment allowlist;
- privacy data map, provider list, retention schedule and request runbook;
- terms, digital license, withdrawal texts/function/email evidence;
- per-SKU rights, risk, safety, claims and technical-documentation package;
- incident/recall/takedown runbook;
- accessibility decision and test report;
- physical fulfillment, packaging and insurance decision when enabled.
