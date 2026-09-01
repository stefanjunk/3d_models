# Global compliance engineering

## Contents

1. [Set the boundary](#set-the-boundary)
2. [Create the legal profile](#create-the-legal-profile)
3. [Apply universally safer defaults](#apply-universally-safer-defaults)
4. [Design consent and tracking controls](#design-consent-and-tracking-controls)
5. [Provide privacy rights and lifecycle](#provide-privacy-rights-and-lifecycle)
6. [Apply market and feature gates](#apply-market-and-feature-gates)
7. [Handle advertising, affiliates, and claims](#handle-advertising-affiliates-and-claims)
8. [Handle commerce and subscriptions](#handle-commerce-and-subscriptions)
9. [Handle children and age assurance](#handle-children-and-age-assurance)
10. [Handle UGC, marketplaces, and AI](#handle-ugc-marketplaces-and-ai)
11. [Treat accessibility as a product requirement](#treat-accessibility-as-a-product-requirement)
12. [Map Firebase data flows and transfers](#map-firebase-data-flows-and-transfers)
13. [Block unsafe launch states](#block-unsafe-launch-states)

## Set the boundary

Treat this file as an implementation risk-control framework, not legal advice, a legal opinion, certification, or a complete map of world law. Applicability depends on operator establishment, markets targeted, monitoring, user location and age, scale, data, sector, and business model.

Use three separate claims:

- **Implemented safeguard:** the code/UI contains and tests a control.
- **Configured for a legal profile:** the operator supplied required facts and the control is configured for named markets/features.
- **Legally approved:** qualified counsel or the accountable owner approved the release. Never infer this from code.

Keep an app in prototype/staging or disable affected features until the legal profile is complete and required approvals exist.

## Create the legal profile

Copy [legal-profile.template.yaml](../assets/legal-profile.template.yaml) to `product/legal-profile.yaml`. Require verified values for:

- legal operator name, country, contact, privacy/support contacts, policy owner;
- enabled/blocked markets and languages;
- audience, minimum age, child-directed likelihood;
- collected/inferred data categories, sensitive/special data, purposes, lawful basis, retention;
- trackers, SDKs, storage, analytics, ads, sale/share, profiling, session replay;
- processors/recipients, Firebase/GCP products, regions, logs, subprocessors, transfers;
- subscriptions, physical goods, affiliate links, marketplace, UGC, user uploads;
- AI interaction, synthetic media, automated/consequential decisions;
- health, finance, insurance, employment, education, gambling, adult, safety/product regulation;
- legal, security, privacy, and accessibility approval owner/date/evidence.

Treat a blank profile as `global-strict` preview mode:

- essential-only storage and requests;
- no optional analytics, ads, personalization, replay, precise location, contacts, biometrics, health, government IDs, or open-ended uploads;
- no payment, subscription, marketplace, public UGC, child-directed, or consequential AI feature;
- no claim of global availability or compliance;
- visible launch blockers in `product/compliance.md`.

## Apply universally safer defaults

These are safer product defaults, not claims that every jurisdiction mandates each item.

| Default | UI/engineering behavior | Evidence/configuration |
| --- | --- | --- |
| Honest operator | Show verified business identity, contact/support, policy links, version/effective dates | Operator profile and policy owner |
| Privacy by default | Collect only data necessary for a declared purpose; optional features start off | Data inventory and purpose mapping |
| Essential-only initial state | No nonessential tag, pixel, storage, fingerprinting, replay, embed, or ad call before the applicable choice | Tag/SDK inventory and network tests |
| Fair choice | Equal-prominence accept/reject where consent applies; granular purposes; no preselection; easy withdrawal | Versioned preference schema and receipts |
| Broad privacy center | Access/export, correction, deletion, objection/restriction, sale/share/ads opt-outs, appeal/contact | Request workflow, verification and audit log |
| Defined lifecycle | Retention/deletion for data, files, logs, analytics, indexes, exports, backups | Retention schedule, TTL and deletion map |
| Accessible journey | WCAG 2.2 AA target across discovery, auth, purchase, support, policy and recovery | Automated + keyboard/screen-reader/zoom results |
| Fair commerce | Total price/material terms before commitment; no preselected paid extras; easy cancellation/refund paths | Offer snapshots and journey tests |
| Honest promotion | No fabricated social proof, review, urgency, endorsement, license, or performance claim | Claims and asset evidence |
| Secure baseline | Deny-first rules, least privilege, server authorization/validation, secrets, rate limits, backups, incident plan | Threat model, tests, access matrix |

Never use visual friction, repeated prompts, guilt language, confusing button hierarchy, obstruction, forced continuity, disguised ads, or hidden settings to defeat a user's choice.

## Design consent and tracking controls

Inventory technology, not only cookies. Include:

- cookies, local/session storage, IndexedDB;
- pixels, scripts, tags, SDKs, link decoration, fingerprinting;
- embeds, maps, video, chat, A/B testing, Remote Config experiments;
- Analytics, Performance, Crash/diagnostic, advertising, affiliate tracking;
- server-side events and conversion APIs.

Classify every item by purpose, vendor, data, retention, region, trigger, and whether it is strictly necessary for the requested service. A policy page does not replace a valid choice.

Implement a consent/choice state machine:

```text
unknown -> essential only
accepted(purposes/vendors) -> enable only granted categories
rejected -> remain essential only
changed/withdrawn -> stop future collection, update SDKs, clear what policy requires
expired/policy changed -> request a fresh decision without coercion
```

Requirements:

- Set defaults before optional SDK/tag initialization.
- Keep accept and reject comparably visible where consent is requested.
- Expose granular settings without making rejection harder.
- Persist the choice and notice/vendor version; avoid indefinite consent.
- Provide a persistent “Privacy choices” entry.
- Verify with browser storage and network inspection before/after each choice.
- Honor applicable recognized browser opt-out signals, including GPC for covered California sale/share requests, without requiring an account.
- Treat Google Consent Mode as a signal/control mechanism, not consent collection.

For Google AdSense/Ad Manager/AdMob publisher traffic in the EEA, UK, and Switzerland, current Google policy requires a Google-certified CMP integrated with the IAB TCF when serving personalized ads. Recheck the policy and certified list at launch. Do not hand-roll a banner and assume it satisfies Google or law.

## Provide privacy rights and lifecycle

Build one privacy center that can support jurisdiction-specific wording and deadlines:

- disclose categories, purposes, sources, recipients, retention, transfers, contact and complaint/appeal routes;
- provide authenticated access/export/correction/deletion without exposing another user;
- provide unauthenticated sale/share/targeted-ad opt-out where applicable;
- provide restriction/objection/consent withdrawal and direct-marketing controls;
- verify identity proportionately and do not collect more data than needed for the request;
- preserve request/decision/audit evidence while deleting operational data according to policy;
- propagate deletion to Auth, Firestore/SQL, Storage, derived records, queues, vendors, and scheduled deletion of eligible backups/logs;
- explain what cannot be deleted immediately and why, using verified policy facts.

Create a data map with:

```text
Data category -> collection point -> purpose/basis -> source of truth
-> recipients/processors -> region/transfer -> retention -> export format
-> correction/deletion path -> backup/log behavior -> owner
```

Add DPIA/risk-assessment and human review gates for systematic monitoring, sensitive data, profiling, children, biometrics/location, large-scale processing, or consequential decisions.

## Apply market and feature gates

Refresh volatile sources before a live launch. The table prioritizes common triggers; research additional enabled countries and sectors from their primary authorities.

| Trigger | Key risk/control | Required product surfaces/records |
| --- | --- | --- |
| EEA personal data/monitoring | GDPR lawful basis, transparency, rights, processor/security/accountability; ePrivacy prior consent for nonessential device storage/access | Layered notice, preferences, DSAR, ROPA, DPAs, retention, transfer map, DPIA where high risk |
| UK users/data | UK GDPR + PECR; 2025 Data (Use and Access) Act added limited conditional storage/access exceptions | Keep global essential-only default unless a UK-specific exception is verified; UK records/transfer analysis |
| California/covered US states | Rights and definitions vary; CA includes access/correct/delete, sale/share opt-out, sensitive-data limitation; honor GPC where covered | State applicability matrix, privacy choices, GPC test, appeal and request log |
| Other global markets | Brazil LGPD, Canada federal/provincial, Australia Privacy Act/APPs, and other laws use different scope, bases, localization and breach rules | Market-specific official research and counsel gate; do not infer equivalence from GDPR controls |
| International transfers | A region is not a transfer mechanism; EEA/UK may require adequacy/SCC/IDTA/Addendum and assessments | Full transfer/subprocessor map, agreements, review date, accurate notice |
| Data breach/incident | Notification thresholds and timeframes differ; GDPR authority notice can be within 72 hours where likely risk | Incident plan, detection, owner, breach register, notification decision workflow |
| Automated consequential decision | GDPR Article 22, sector rules, anti-discrimination and US state ADMT rules may require notice, reasons, opt-out/safeguards/human review | Feature off until assessed; input/reason disclosure, correction, human appeal, impact/bias testing |

Do not use geoblocking as sole proof that a law does not apply. Do not state that a consent banner legalizes an unnecessary purpose or invalid transfer.

## Handle advertising, affiliates, and claims

- Label ads so users can distinguish them from editorial/navigation/content.
- Place an affiliate or material-connection disclosure near the recommendation and relevant links, not only in the footer.
- Use clear language such as “We may earn a commission if you buy through this link” and adapt it to verified operator/country requirements.
- Explain ranking/selection methodology, update date, conflicts, retailer/source, and whether products were actually tested.
- Do not claim first-hand use, independence, expertise, or “best” without evidence.
- Keep price/stock/delivery timestamps and source; design for stale/unavailable values.
- Do not fabricate or buy reviews, testimonials, celebrity endorsements, ratings, trust badges, or customer logos.
- Do not present AI-generated text as an authentic consumer review or personal experience.
- Substantiate health, environmental, financial, safety, savings, and comparative claims before display.
- Show real sources for scarcity, countdown, inventory, or deadline messages.

Keep disclosures visually proximate, readable, persistent enough to understand, and accessible; a tooltip alone is insufficient for material information.

## Handle commerce and subscriptions

Before commitment, show:

- verified seller/operator;
- product/service identity and material limitations;
- total price, currency, mandatory fees, tax/shipping behavior;
- delivery/performance timing;
- refund/return/withdrawal/cancellation rules;
- subscription trial, renewal date/frequency, recurring amount or calculation;
- required compatibility, age, geographic or account constraints.

Use an unambiguous purchase/subscribe action. Preselect no paid add-on. Capture separate affirmative agreement to recurring terms and provide a durable confirmation.

Make cancellation at least as easy as signup and available without a retention chat as a condition. Support refunds/withdrawal where applicable. EU consumer law can require a 14-day withdrawal right for many distance contracts and, from national implementation around June 2026, an online withdrawal function. Resolve product/digital-content exceptions with counsel.

US caveat: the FTC's 2024 nationwide click-to-cancel amendment was vacated by the Eighth Circuit in July 2025. Do not cite it as effective federal law. ROSCA, the FTC Act, and state automatic-renewal rules remain relevant. Keep the fair easy-cancellation default and research each enabled market.

## Handle children and age assurance

Do not infer “not intended for children” from adult-looking design. Assess content, marketing, actual knowledge, likely audience, and platform context.

For a child-directed service or actual knowledge of US users under 13, COPPA can require notice, verifiable parental consent, parental access/deletion, security, and retention limits. Compliance with the amended COPPA rule began 22 April 2026; separate parental consent is generally required for targeted advertising/third-party disclosure under the amended framework. Recheck official FTC rules before launch.

Safer child/minor defaults:

- no targeted ads/profiling;
- high privacy and private visibility;
- minimum collection and retention;
- age-appropriate language and help;
- proportionate parental/guardian flow when required;
- no conditioning participation on excessive data;
- no persuasive streak, scarcity, or spend pressure;
- prevent contact/discovery/location exposure;
- delete raw ID/age-verification material promptly when a derived age attribute suffices;
- provide a challenge/review route for age assurance errors.

Use age assurance only after assessing accuracy, bias, accessibility, privacy, security, proportionality, and vendor processing. Never reuse age evidence for advertising.

## Handle UGC, marketplaces, and AI

### UGC/platforms

Provide report/block/mute, notice-and-action, moderation reason, status, appeal/contact, evidence preservation, emergency escalation, repeat-abuse controls, and transparent rules. Design moderator tools and audit logs, not only user-facing feeds.

EU DSA obligations vary by service category and size and can include ad/recommender transparency, trader traceability, statements of reasons, complaints/appeals, and minor protections. Small-business exemptions are partial; require a service classification.

### Marketplaces

Verify and display trader/seller information as required; distinguish platform and seller responsibility. Provide product/content reporting, dispute/return/help, review authenticity, fulfillment status, recall/safety communication, and seller appeal.

### AI

Inventory every AI feature, model/provider, input/output, training/retention setting, user disclosure, provenance, safety boundary, evaluation, and human escalation.

EU AI Act Article 50 transparency obligations apply from 2 August 2026. Where applicable:

- disclose AI interaction at first interaction unless obvious;
- mark relevant synthetic output in a machine-readable format;
- disclose deepfakes and specified public-interest AI text;
- provide meaningful human contact/review for consequential use.

A label is not enough for high-risk/consequential employment, credit, education, health, housing, insurance, or public-service decisions. Keep such automation disabled pending sector, AI Act, privacy, anti-discrimination, validation, explanation, and human-review approval.

## Treat accessibility as a product requirement

Target WCAG 2.2 AA, including full journeys and third-party embeds. Test:

- semantic structure, landmarks, headings, names/roles/values;
- keyboard access, visible and unobscured focus, skip link, logical order;
- contrast, reflow at 200%/400%, text spacing, color independence;
- images, audio/video alternatives, charts and canvas fallbacks;
- form labels/help/error identification and announcements;
- target size, dragging alternatives, motion and time limits;
- accessible authentication without memory/puzzle barriers;
- status, progress, dialogs, menus, toasts and route changes;
- support, policies, purchase, cancellation, privacy choices, and account deletion.

Automated scanners cannot certify conformance. Add manual keyboard, screen-reader, zoom/reflow, high-contrast, and reduced-motion tests.

The European Accessibility Act has applied since 28 June 2025 to covered services including ecommerce, banking, transport, e-books, and communications, with scope/exemptions implemented nationally. EN 301 549 also contains requirements beyond web content, and US/UK/public-sector/procurement laws differ. Generate an accessibility statement and issue/contact process from verified facts only.

## Map Firebase data flows and transfers

Firebase is not one homogeneous region. Record for every product:

- customer content and identifiers;
- configuration/control plane;
- primary resource region and replicas;
- logs, telemetry, support access, subprocessors;
- backups/exports;
- Auth, Analytics, advertising, extensions, AI and third-party APIs;
- deletion/export mechanism and retention;
- contract/transfer mechanism.

Require explicit location choice before immutable resources. Do not rely on a default Functions region. Hosting CDN reach or Analytics reporting location is not proof of residency.

Firebase documentation states Authentication processing occurs in US data centers; reassess Firebase Auth for hard non-US identity residency. Execute and retain applicable Google Cloud data-processing terms and separately resolve SCC/IDTA/transfer assessments where needed.

Deleting an installation identifier does not necessarily delete Analytics or other records. Orchestrate export/deletion across Auth, Firestore/SQL, Storage, Analytics/vendor systems, logs, derived data, queues, and eligible backups.

## Block unsafe launch states

Fail launch readiness when any applies:

- legal operator/contact, market, policy owner, or approval is blank;
- a nonessential tracker/request occurs before the applicable choice;
- personal-data purpose, basis, retention, region, recipient, or deletion path is undeclared;
- sale/share/targeted ads lack applicable opt-out and GPC handling;
- likely-minor experience enables public-by-default visibility, profiling, or targeted ads;
- subscription lacks total terms, confirmation, cancellation and withdrawal/refund tests;
- affiliate/sponsored/review/price/urgency claim lacks disclosure or evidence;
- marketplace/UGC lacks trader/moderation/report/appeal configuration;
- visible AI interaction/synthetic content lacks required disclosure/provenance;
- consequential automation lacks named legal approval and human review;
- a Firebase product lacks region/data-flow decision;
- critical journey fails keyboard/manual accessibility review;
- regulated-sector or product-safety flag exists without approval;
- generated privacy/terms text contains placeholders or unverified facts.

Report “legal review required” and the exact unresolved decisions. Never report “globally compliant.”
