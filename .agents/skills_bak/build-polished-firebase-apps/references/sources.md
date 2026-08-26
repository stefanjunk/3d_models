# Primary research sources

Checked 2026-08-13. Recheck volatile product compatibility, regions, prices, vendor policy, and law before live deployment. Public documentation supports observable workflows; it does not reveal v0's private model architecture or reasoning.

## Contents

1. [Vercel v0](#vercel-v0)
2. [Firebase and Google Cloud](#firebase-and-google-cloud)
3. [UI, accessibility, and performance](#ui-accessibility-and-performance)
4. [Privacy, tracking, and transfers](#privacy-tracking-and-transfers)
5. [Consumer, advertising, children, UGC, and AI](#consumer-advertising-children-ugc-and-ai)

## Vercel v0

### Product and lifecycle

- [What is v0?](https://v0.dev/docs) — current positioning as an agent for real code and full-stack applications.
- [Quickstart](https://v0.dev/docs/quickstart) — describe, generate a working application, iterate, publish.
- [Text Prompting](https://v0.dev/docs/text-prompting) — planning, requirements, context, prompt queueing.
- [How to prompt v0](https://vercel.com/blog/how-to-prompt-v0) — product surface, context of use, constraints/taste, and documented tests of specificity.
- [PRD design](https://v0.dev/docs/prd-design) — convert high-level product ideas into requirements and design direction.
- [Agentic features](https://v0.dev/docs/agentic-features) — web/browser and autonomous task behavior.
- [Sandbox](https://v0.dev/docs/sandbox) — code, runtime, preview, and tools in a shared isolated environment.
- [Terminal commands](https://v0.dev/docs/terminal-commands) — package, test, and CLI execution.
- [Code editing](https://v0.dev/docs/code-editing) — editor, search, diff, and split view.
- [Versions](https://v0.dev/docs/versions) — generated revision history and restoration.
- [Instructions](https://v0.dev/docs/instructions) — reusable behavior/context instructions.

### Full-stack, code, and integrations

- [Full-stack apps](https://v0.dev/docs/full-stack-apps) — Next.js default, server actions/API routes, staged full-stack development.
- [Projects](https://v0.dev/docs/projects) — shared app, deployment, environment, domains, integrations, and multiple chats.
- [GitHub](https://v0.dev/docs/github) — isolated working branches, commits, and pull requests.
- [Git import](https://v0.dev/docs/git-import) — existing repositories and project roots.
- [Deployments](https://v0.dev/docs/deployments) — Vercel deployment workflow; used only as comparison, not the Firebase target.
- [Databases](https://v0.dev/docs/databases) — documented provider integrations.
- [External APIs](https://v0.dev/docs/external-apis) — server-side environment variables and external service calls.
- [FAQs](https://v0.dev/docs/faqs) — scope, full-stack support, export, limitations, and user responsibility.
- [v0 Platform API](https://v0.dev/docs/api/v2) and [Vercel introduction](https://vercel.com/blog/build-your-own-ai-app-builder-with-the-v0-platform-api) — public prompt → project → files → live preview/deployment lifecycle.

### Design systems and assets

- [Design Mode](https://v0.dev/docs/design-mode) — selection-based visual editing and code revision.
- [Design Systems 2.0](https://v0.dev/docs/design-systems-2) — components, tokens, sources, starter-app review, and skill save gate.
- [Design Systems API guide](https://v0.dev/docs/api/v2/guides/design-systems) — verified components/props/tokens and working starter app.
- [Working with Figma and custom design systems](https://vercel.com/blog/working-with-figma-and-custom-design-systems-in-v0) — componentization, iterative fidelity, shadcn/ui, Tailwind, npm packages.
- [Figma](https://v0.dev/docs/figma) — file/frame-to-flow generation.
- [Screenshots and Files](https://v0.dev/docs/screenshots) — screenshot analysis and generation boundaries.
- [Images, videos, and file uploads](https://v0.dev/docs/images-and-videos) — supported media and high-resolution/web-optimization guidance.
- [shadcn/ui introduction](https://ui.shadcn.com/docs) — open-code accessible component foundation.
- [shadcn/ui theming](https://ui.shadcn.com/docs/theming) — semantic CSS-variable tokens.
- [shadcn/ui registry](https://ui.shadcn.com/docs/registry) — distributable design-system components, pages, styles, and assets.

## Firebase and Google Cloud

### Hosting and frameworks

- [Firebase App Hosting](https://firebase.google.com/docs/app-hosting) — framework-centered full-stack hosting over Cloud Build, Cloud Run, and Cloud CDN.
- [About App Hosting](https://firebase.google.com/docs/app-hosting/about-app-hosting) — architecture and rollout flow.
- [Frameworks and tooling](https://firebase.google.com/docs/app-hosting/frameworks-tooling) — current Next.js/Angular/Node support and adapters.
- [App Hosting product comparison](https://firebase.google.com/docs/app-hosting/product-comparison) — App Hosting versus other Firebase/Google solutions.
- [Configure App Hosting](https://firebase.google.com/docs/app-hosting/configure) — runtime, environment, secrets, build/run configuration.
- [Alternative/source deploy](https://firebase.google.com/docs/app-hosting/alt-deploy) — source deployment workflows.
- [Multiple environments](https://firebase.google.com/docs/app-hosting/multiple-environments) — environment/backend strategy.
- [Emulate App Hosting](https://firebase.google.com/docs/app-hosting/emulate) — local testing.
- [App Hosting caching](https://firebase.google.com/docs/app-hosting/optimize-cache) — Cloud CDN eligibility and headers.
- [Optimize image loading](https://firebase.google.com/docs/app-hosting/optimize-image-loading) — Firebase-compatible Next.js image strategy.
- [App Hosting route monitoring](https://firebase.google.com/docs/app-hosting/monitor-routes) and [logging](https://firebase.google.com/docs/app-hosting/logging) — requests, errors, latency, cache, logs.
- [App Hosting costs](https://firebase.google.com/docs/app-hosting/costs) — Blaze plan and component costs.
- [Firebase Hosting](https://firebase.google.com/docs/hosting) — static/SPA hosting, CDN, emulators, preview channels.
- [Hosting configuration](https://firebase.google.com/docs/hosting/full-config) — redirects, rewrites, headers, clean URLs, rule order.
- [Test, preview, deploy Hosting](https://firebase.google.com/docs/hosting/test-preview-deploy) — public preview-channel behavior and release.
- [Hosting GitHub integration](https://firebase.google.com/docs/hosting/github-integration) — PR previews for static Hosting.
- [Next.js on Firebase Hosting](https://firebase.google.com/docs/hosting/frameworks/nextjs) — experiment closed to new Next.js participants; migrate dynamic apps to App Hosting.

### Runtime and global architecture

- [Cloud Run multi-region services](https://cloud.google.com/run/docs/multiple-regions) — explicit multi-region deployment/load balancing.
- [Cloud Run domain mapping](https://cloud.google.com/run/docs/mapping-custom-domains) — domain topology and limitations.
- [Cloud Functions 2nd generation migration](https://firebase.google.com/docs/functions/2nd-gen-upgrade) — runtime/concurrency model.
- [Manage Functions](https://firebase.google.com/docs/functions/manage-functions) — scaling, concurrency, runtime versions, deployment.
- [Functions locations](https://firebase.google.com/docs/functions/locations) — explicit placement/co-location.
- [Functions environment and secrets](https://firebase.google.com/docs/functions/config-env) — Secret Manager and configuration.

### Data, Auth, Rules, App Check, Storage

- [Firestore locations](https://firebase.google.com/docs/firestore/locations) — regional/multi-region placement.
- [Firestore best practices](https://firebase.google.com/docs/firestore/best-practices) — IDs, hotspots, indexes, pagination, rollout.
- [Firestore offline data](https://firebase.google.com/docs/firestore/manage-data/enable-offline) — persistent web cache behavior.
- [Firestore backups](https://firebase.google.com/docs/firestore/backups) and [PITR](https://firebase.google.com/docs/firestore/pitr) — recovery controls.
- [Firebase SQL Connect](https://firebase.google.com/docs/sql-connect) — relational PostgreSQL-based data platform (renamed from Data Connect).
- [SQL Connect authorization and security](https://firebase.google.com/docs/sql-connect/authorization-and-security) — predefined operations and explicit auth.
- [Manage SQL Connect services/databases](https://firebase.google.com/docs/sql-connect/manage-services-and-databases) and [schemas/connectors](https://firebase.google.com/docs/sql-connect/manage-schemas-and-connectors) — regions, production instance, migrations.
- [Firebase Auth for web](https://firebase.google.com/docs/auth/web/start) — provider and web setup.
- [Redirect sign-in best practices](https://firebase.google.com/docs/auth/web/redirect-best-practices) — browser storage restrictions and custom domains.
- [Use Firebase with SSR](https://firebase.google.com/docs/web/ssr-apps) — `FirebaseServerApp` and user-context server rendering.
- [Firebase privacy and security](https://firebase.google.com/support/privacy) — product-specific processing, including Auth location caveat.
- [Firebase Security Rules](https://firebase.google.com/docs/rules), [Firestore rule conditions](https://firebase.google.com/docs/firestore/security/rules-conditions), and [Rules unit tests](https://firebase.google.com/docs/rules/unit-tests) — authorization, query behavior, Emulator tests.
- [Avoid insecure Rules](https://firebase.google.com/docs/rules/insecure-rules) — unsafe production patterns.
- [App Check with reCAPTCHA Enterprise](https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider) — recommended new web provider and staged enforcement.
- [Protect custom backends](https://firebase.google.com/docs/app-check/web/custom-resource) — token header/verification.
- [App Check debug provider](https://firebase.google.com/docs/app-check/web/debug-provider) — local/CI debug-token secrecy.
- [Cloud Storage Security](https://firebase.google.com/docs/storage/security), [rule conditions](https://firebase.google.com/docs/storage/security/rules-conditions), and [web uploads](https://firebase.google.com/docs/storage/web/upload-files) — ownership, validation, and upload behavior.

### Environments, consent, and operations

- [Firebase development workflow best practices](https://firebase.google.com/docs/projects/dev-workflows/general-best-practices) — separate projects/environments.
- [Firebase project locations](https://firebase.google.com/docs/projects/locations) — product-by-product location selection.
- [Firebase security checklist](https://firebase.google.com/support/guides/security-checklist) and [launch checklist](https://firebase.google.com/support/guides/launch-checklist) — production controls.
- [Firebase Analytics JavaScript API](https://firebase.google.com/docs/reference/js/analytics) — consent and collection controls.
- [Google Consent Mode](https://developers.google.com/tag-platform/security/guides/consent) and [consent debugging](https://developers.google.com/tag-platform/security/guides/consent-debugging) — defaults, updates, and verification.
- [Remote Config loading strategies](https://firebase.google.com/docs/remote-config/loading) — in-app defaults and safe activation.
- [Firebase data clear/export guidance](https://firebase.google.com/support/privacy/clear-export-data) and [identifier controls](https://firebase.google.com/support/privacy/manage-iids) — lifecycle boundaries.
- [Google Cloud Data Processing Addendum](https://cloud.google.com/terms/data-processing-addendum) — processor contract basis.

## UI, accessibility, and performance

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — current W3C accessibility recommendation and new 2.2 criteria.
- [How to Meet WCAG 2.2](https://www.w3.org/WAI/WCAG22/quickref/) — success criteria/technique mapping.
- [Core Web Vitals](https://web.dev/articles/vitals) — LCP, INP, CLS and good thresholds.
- [How Core Web Vitals thresholds were defined](https://web.dev/articles/defining-core-web-vitals-thresholds) — 75th percentile and bands.
- [High-impact Core Web Vitals improvements](https://web.dev/articles/top-cwv) — LCP discovery/priority, layout stability, long tasks, CDN.
- [Automated accessibility testing](https://web.dev/learn/accessibility/test-automated) and [assistive-technology testing](https://web.dev/learn/accessibility/test-assistive-technology) — automation limits and manual testing.
- [Next.js metadata and Open Graph images](https://nextjs.org/docs/app/getting-started/metadata-and-og-images) — route metadata/shareability.
- [Next.js image optimization](https://nextjs.org/docs/app/getting-started/images) and [font optimization](https://nextjs.org/docs/app/getting-started/fonts) — media and font behavior; verify Firebase compatibility.
- [Material responsive layout grid](https://m2.material.io/design/layout/responsive-layout-grid.html) — columns, gutters, margins as a general composition reference, not a mandated visual style.

## Privacy, tracking, and transfers

- [EU General Data Protection Regulation](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) — principles, transparency, rights, privacy by design, security, DPIA, accountability.
- [EDPB data protection by design/default](https://www.edpb.europa.eu/documents/guideline/guidelines-42019-on-article-25-data-protection-design-and-default_en) — engineering and default-setting guidance.
- [EDPB consent guidance](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en) — freely given, specific, informed, unambiguous, withdrawable consent.
- [EDPB deceptive design patterns](https://www.edpb.europa.eu/system/files/2023-02/edpb_03-2022_guidelines_on_deceptive_design_patterns_in_social_media_platform_interfaces_v2_en_0.pdf) — interface anti-patterns and rights.
- [EU ePrivacy Directive](https://eur-lex.europa.eu/eli/dir/2002/58/oj/eng) — device storage/access and communications privacy.
- [ICO storage/access technology guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/) — current UK PECR guidance, updated for 2026.
- [UK Data (Use and Access) Act 2025 changes](https://www.gov.uk/guidance/data-use-and-access-act-2025-data-protection-and-privacy-changes) — UK-specific conditional changes; do not transplant to EEA.
- [California CCPA/CPRA](https://oag.ca.gov/privacy/ccpa) and [Global Privacy Control](https://oag.ca.gov/privacy/ccpa/gpc) — rights and sale/share opt-out signal.
- [California Privacy Protection Agency regulations](https://cppa.ca.gov/regulations/ccpa_updates.html) — current rulemaking/regulations.
- [EU adequacy decisions](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en), [SCCs](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/standard-contractual-clauses-scc_en), and [ICO international transfers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/international-transfers/) — transfer mechanisms and assessments.
- [Australian Privacy Principles](https://www.oaic.gov.au/privacy/australian-privacy-principles) — Australia market research starting point.

## Consumer, advertising, children, UGC, and AI

- [European Accessibility Act](https://eur-lex.europa.eu/eli/dir/2019/882/oj/eng) and [Commission overview](https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/european-accessibility-act-eaa_en) — covered services/products and application since June 2025.
- [EN 301 549 v3.2.1](https://www.etsi.org/deliver/etsi_en/301500_301599/301549/03.02.01_60/en_301549v030201p.pdf) — ICT accessibility beyond web-only criteria.
- [EU Consumer Rights Directive](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A02011L0083-20220528) and [online withdrawal-function directive](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A32023L2673) — distance-sale information, withdrawal, online function implementation.
- [US Restore Online Shoppers' Confidence Act](https://www.ftc.gov/legal-library/browse/statutes/restore-online-shoppers-confidence-act) and [FTC 2026 Negative Option ANPRM](https://www.ftc.gov/system/files/ftc_gov/pdf/p064202negativeoptionruleanprm.pdf) — recurring terms and record of 2025 click-to-cancel vacatur.
- [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews) — material connections and endorsements.
- [FTC Consumer Reviews and Testimonials Rule Q&A](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers) — fake and AI-generated purported-experience reviews.
- [FTC dark-patterns report](https://www.ftc.gov/reports/bringing-dark-patterns-light) — deceptive interface patterns.
- [Google publisher CMP requirements](https://support.google.com/adsense/answer/13554116?hl=en) — certified CMP/TCF requirements for personalized ads in EEA, UK, Switzerland.
- [FTC COPPA Rule](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa) and [2025 amended final rule](https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule) — current children's privacy obligations and 2026 compliance date.
- [EDPB age-assurance principles](https://www.edpb.europa.eu/documents/statement/statement-12025-on-age-assurance_en) — proportionality, data minimization, accuracy, rights.
- [EU Digital Services Act](https://eur-lex.europa.eu/eli/reg/2022/2065/oj/eng) and [Commission DSA overview](https://digital-strategy.ec.europa.eu/en/policies/digital-services-act) — platform/UGC/marketplace classification, reporting, moderation, transparency, minors, dark patterns.
- [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng) and [Commission Article 50 transparency guidance](https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations) — AI interaction/synthetic-content duties applicable from 2026-08-02.
- [FTC Health Breach Notification Rule guidance](https://www.ftc.gov/business-guidance/resources/complying-ftcs-health-breach-notification-rule-0) and [HHS cloud/BAA guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html) — regulated health escalation.
- [EU General Product Safety Regulation overview](https://trade.ec.europa.eu/access-to-markets/en/news/eus-general-product-safety-regulation-gpsr-new-era-consumer-protection) — physical-product and marketplace escalation.
