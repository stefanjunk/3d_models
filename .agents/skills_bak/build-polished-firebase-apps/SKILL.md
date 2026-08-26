---
name: build-polished-firebase-apps
description: Create, redesign, complete, and production-harden distinctive full-stack web applications from short natural-language briefs with a Vercel-v0-like prompt-to-working-app experience, but target Google Cloud and Firebase. Use for UI/UX-first websites, SaaS products, dashboards, marketplaces, ecommerce or affiliate sites, content products, consumer utilities, portals, and prototypes that need polished visual identity, responsive layouts, functional flows, Firebase architecture, assets, accessibility, security, testing, deployment preparation, or global legal/compliance guardrails. Use with new or existing React, Next.js, TypeScript, Tailwind, shadcn/ui, Firebase Hosting, Firebase App Hosting, Firestore, Authentication, Storage, Functions, Cloud Run, or Data Connect projects.
---

# Build Polished Firebase Apps

Turn a brief into a coherent product, not a page mockup. Make reversible product and design assumptions, build the primary journey end to end, render and inspect it, connect real persistence when required, and leave the repository runnable and deployable to Firebase/GCP.

## Hold the delivery contract

Deliver all applicable layers:

1. A useful product model: audience, job, data, actions, routes, roles, and success signal.
2. A distinctive interface: intentional art direction, responsive hierarchy, complete interaction states, and credible content.
3. Working behavior: navigation, forms, validation, persistence, authorization, failure handling, and integrations.
4. Firebase/GCP readiness: environment separation, least-privilege rules, emulator coverage, secrets, budgets, and deploy configuration.
5. Launch safeguards: accessibility, performance, security, asset provenance, privacy, consumer protection, and conditional regulatory gates.

Do not equate a polished hero with a finished app. Do not claim production readiness while critical checks, legal facts, credentials, or live infrastructure remain unresolved.

## Work assumption-first

- Inspect the existing repository, instructions, assets, Firebase files, and user context before deciding anything.
- Infer low-risk, reversible details from the brief and record them in `product/blueprint.json`; keep moving.
- Ask only when an answer materially changes regulated scope, irreversible data location, external spend, account ownership, brand/IP permission, destructive migration, or a requested live deployment.
- Default to a privacy-protective global profile, mobile-first responsive behavior, English source copy prepared for localization, realistic demo data, and one primary user journey.
- Never invent a legal entity, contact, price, testimonial, certification, metric, partnership, license, or policy fact. Mark unresolved truth as a launch blocker rather than hiding it in copy.
- Prepare deployment files and commands by default. Create paid resources, domains, provider accounts, or live deployments only when the user explicitly authorizes them.

## Follow the build loop

### 1. Frame the product

Translate the brief into five inputs: product surface, user, moment of use, desired outcome, and constraints/taste. Read [research-and-blueprints.md](references/research-and-blueprints.md) for the research ladder and assumption rules. For a thin brief, run:

```bash
python3 <skill-dir>/scripts/create_blueprint.py \
  --name "Product name" --brief "User brief" --archetype utility \
  --out product/blueprint.json
```

Replace generated assumptions with known facts. Include routes, roles, core entities, permissions, primary and recovery flows, integrations, analytics events, asset needs, legal flags, and acceptance criteria.

### 2. Research without copying

- Research the domain when facts, conventions, competitors, laws, prices, APIs, or user expectations may be current.
- Sample three references with different purposes: category convention, interaction model, and visual/brand inspiration.
- Extract principles and gaps; never reproduce a competitor's composition, copy, trade dress, proprietary assets, or distinctive motion.
- Preserve source URLs, dates, facts, and asset rights in project notes. Separate sourced facts from design inferences.
- Stop research when it changes no remaining product, content, visual, architecture, or compliance decision.

### 3. Choose the Firebase shape

Read [firebase-gcp.md](references/firebase-gcp.md) before adding infrastructure.

| Need | Default |
| --- | --- |
| Next.js/Angular SSR, server actions, dynamic full-stack app | Firebase App Hosting |
| Static export or client-rendered SPA | Firebase Hosting |
| User-scoped realtime/document data | Firestore + Auth + Security Rules |
| Relational schema, joins, transactional SQL | Firebase SQL Connect (formerly Data Connect) |
| File uploads | Cloud Storage + content/type/size/ownership rules |
| Event/background work | Cloud Functions 2nd gen |
| Custom container, language, or runtime | Cloud Run |
| Privileged API or secret-bearing action | Server action/route, Function, or Cloud Run; never the browser |

For greenfield dynamic apps, prefer Next.js App Router + TypeScript + semantic CSS tokens + Tailwind + code-owned accessible primitives, deployed with App Hosting. Preserve an existing suitable stack instead of rewriting it for taste alone.

### 4. Establish an original design direction

Read [ui-ux-art-direction.md](references/ui-ux-art-direction.md) and [layout-and-flow-patterns.md](references/layout-and-flow-patterns.md). Before composing pages, write a compact visual thesis containing:

- one product metaphor or emotional promise;
- one signature spatial motif;
- one typography relationship;
- one controlled color strategy;
- one image/illustration treatment;
- one motion behavior and reduced-motion alternative.

Generate semantic tokens before components. If useful, run:

```bash
python3 <skill-dir>/scripts/generate_theme.py \
  --name "Product name" --archetype editorial --format css \
  --out src/app/theme.generated.css
```

Treat generated tokens as a considered starting point, then tune them against the product and rendered screens. Avoid unmodified library defaults, generic purple/blue glow, indiscriminate gradients, glass on every surface, card grids for all content, and decorative motion without meaning.

### 5. Build a complete vertical slice

Build in this order:

1. Route shell, metadata, navigation, global styles, skip link, and responsive container.
2. Primary journey from entry through success, using realistic copy and data.
3. Authentication, data model, authorization rules, and persistence where required.
4. Secondary routes required to make the product understandable and operable.
5. Loading, empty, no-results, validation, offline/retry, error, permission-denied, success, disabled, and destructive-confirmation states.
6. Settings, privacy controls, account export/deletion hooks, support/contact, and legal surfaces where applicable.

Make every visible action work or remove it. Do not substitute `localStorage` for requested multi-user or durable persistence. Use optimistic UI only with rollback and accessible status feedback.

### 6. Use assets as product structure

Read [content-and-assets.md](references/content-and-assets.md).

- Use a real visual when it explains the product, establishes identity, or improves trust; do not add random stock photography.
- Prefer user-provided assets, commissioned/generated originals, or assets with verified commercial rights.
- Create and maintain `product/asset-ledger.csv` from [asset-ledger.template.csv](assets/asset-ledger.template.csv).
- Record source, creator, license, retrieval date, modifications, model/tool when generated, intended route, and alt-text decision.
- Download and optimize approved assets instead of hotlinking, unless the provider explicitly requires hosted delivery.
- Produce the full launch set when applicable: favicon, app icon, Open Graph image, responsive hero/product media, empty-state illustration, and social preview.
- Reserve dimensions, serve suitable formats, keep the LCP asset discoverable, and avoid lazy-loading the initial LCP image.

### 7. Apply legal, privacy, accessibility, and security gates

Read [global-compliance.md](references/global-compliance.md) whenever the app is public, collects data, uses analytics/ads, sells or recommends products, accepts payments, hosts user content, targets children, or touches regulated decisions. Treat it as engineering guidance, not legal advice.

- Build to WCAG 2.2 AA as the technical baseline; test keyboard, focus, names/roles/values, contrast, zoom, target size, error recovery, accessible authentication, and reduced motion.
- Minimize collection and retention. Block optional analytics, advertising, pixels, and third-party embeds until the configured consent/opt-out state permits them.
- Make accept and reject choices comparably prominent where consent is used. Keep preferences reversible and honor supported browser privacy signals when applicable.
- Deny Firebase data access by default, authorize per operation and ownership/role, validate fields, test rules in the Emulator Suite, and add App Check without treating it as authorization.
- Keep secrets server-side and committed files free of credentials. Separate development, staging, and production projects.
- Add clear disclosures next to affiliate links, sponsored content, prices, recurring terms, material limitations, AI output, or user-generated content where applicable.
- Do not publish generated privacy policies or terms as legally approved. Populate only verified facts and expose unresolved operator/data/vendor/market details in `product/compliance.md` as launch blockers.

### 8. Render, test, and refine

Read [quality-gates.md](references/quality-gates.md). Use the available browser or preview tooling to inspect the actual app, not only source code.

- Test representative widths near 320, 375, 768, 1024, and 1440 CSS pixels; also test content expansion, keyboard-only use, 200% zoom, reduced motion, and light/dark modes when supported.
- Run formatter, lint, typecheck, unit/component tests, Firebase Rules tests, end-to-end smoke tests, and production build.
- Exercise fresh, returning, unauthenticated, unauthorized, empty, slow, offline, error, and success paths.
- Target field Core Web Vitals at the 75th percentile: LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1. Treat lab scores as diagnostics, not proof of field results.
- Run the bundled static audit as a backstop:

```bash
python3 <skill-dir>/scripts/audit_webapp.py . --profile global-strict
```

Fix critical findings. Manually verify areas static analysis cannot prove. Iterate on the weakest screen, not only the homepage.

## Enforce UI/UX non-negotiables

- Give each screen one dominant purpose and a clear primary action.
- Build hierarchy with proportion, spacing, alignment, type, and contrast before adding decoration.
- Keep reading width deliberate; let data-dense workspaces use more width than prose.
- Adapt information architecture across breakpoints instead of merely shrinking desktop.
- Use tables for comparison and scanning, lists for sequences, cards for bounded objects, and charts only when the visual encoding improves a decision.
- Keep labels visible; do not use placeholders as labels. Explain destructive or irreversible outcomes before confirmation.
- Preserve user input through recoverable errors. Announce async results without stealing focus.
- Use one icon family and meaningful icon semantics. Pair icons with text for unfamiliar actions.
- Write credible, specific product copy. Ban lorem ipsum, fake social proof, unsupported superlatives, and vague CTA labels.
- Require at least three unmistakable identity signals beyond logo/color. Score originality using the rubric in [ui-ux-art-direction.md](references/ui-ux-art-direction.md).

## Scaffold only when it helps

For an empty directory, copy the Firebase/Next.js foundation:

```bash
python3 <skill-dir>/scripts/scaffold_firebase_app.py \
  --name "Product name" --target ./product-app --archetype utility --install
```

Do not overwrite an existing project. The foundation is intentionally incomplete as a brand and business; replace its demo surface with the project blueprint rather than shipping the same shell repeatedly.

## Route supporting material

- Read [v0-observable-methods.md](references/v0-observable-methods.md) for the researched public v0 lifecycle, prompting, design systems, assets, testing, observable defaults, and Firebase translation.
- Read [research-and-blueprints.md](references/research-and-blueprints.md) for requirement inference, competitor research, assumptions, and blueprint schema.
- Read [ui-ux-art-direction.md](references/ui-ux-art-direction.md) for visual systems, style families, originality, typography, color, motion, and anti-generic review.
- Read [layout-and-flow-patterns.md](references/layout-and-flow-patterns.md) for app archetypes, route maps, responsive composition, onboarding, forms, dashboards, commerce, and content.
- Read [content-and-assets.md](references/content-and-assets.md) for copy, image strategy, generated media, licensing, provenance, SEO, and localization.
- Read [firebase-gcp.md](references/firebase-gcp.md) for hosting, data, auth, rules, App Check, environments, observability, cost, and deployment.
- Read [global-compliance.md](references/global-compliance.md) for privacy, consent, children, ads/affiliate, ecommerce, subscriptions, UGC, AI, accessibility, and jurisdiction gates.
- Read [quality-gates.md](references/quality-gates.md) for functional, visual, accessibility, performance, security, and launch checks.
- Read [examples.md](references/examples.md) for complete prompt-to-blueprint examples.
- Read [sources.md](references/sources.md) when verifying volatile product or regulatory claims; refresh any source relevant to a live launch.

## Declare done precisely

Finish with a compact handoff containing:

- what is operational and where;
- material assumptions made;
- validation actually run and its result;
- Firebase setup or deploy actions still requiring the user's account;
- launch blockers, especially unverified legal/business facts;
- the highest-value next iteration.

Use these readiness labels accurately:

- **Prototype-ready:** primary journey works with clearly identified demo boundaries.
- **Deploy-ready:** production build and required automated checks pass; infrastructure configuration exists.
- **Launch-ready:** deploy-ready plus verified business/legal content, production credentials, monitoring, consent configuration, security review, and owner approval.
