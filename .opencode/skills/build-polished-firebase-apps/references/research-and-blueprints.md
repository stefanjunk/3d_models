# Research and blueprints

## Contents

1. [Convert a brief into build inputs](#convert-a-brief-into-build-inputs)
2. [Use the evidence ladder](#use-the-evidence-ladder)
3. [Research references without cloning](#research-references-without-cloning)
4. [Make and govern assumptions](#make-and-govern-assumptions)
5. [Choose direct build or planning depth](#choose-direct-build-or-planning-depth)
6. [Write the app blueprint](#write-the-app-blueprint)
7. [Plan vertical slices](#plan-vertical-slices)
8. [Turn requirements into acceptance tests](#turn-requirements-into-acceptance-tests)

## Convert a brief into build inputs

Expand every brief into these five inputs before implementation:

| Input | Question | Required output |
| --- | --- | --- |
| Product surface | What does the user see, understand, and manipulate? | Screens, components, records, actions |
| User | Who uses it and what is their capability/context? | Primary persona, secondary roles, accessibility needs |
| Moment | When, where, and on what device does use occur? | Frequency, urgency, environment, device priority |
| Outcome | What decision or completed job makes the visit successful? | Primary success action and measurable signal |
| Constraints and taste | What must be true or avoided? | Platform, data, brand, legal, visual, performance constraints |

For example, convert “make a meal-planning app” into:

- Product surface: weekly plan, recipe search, pantry exclusions, shared shopping list, recipe detail.
- User: busy household organizer with mixed dietary needs.
- Moment: ten-minute Sunday planning on desktop; list use on a phone in a store.
- Outcome: a complete week plus a consolidated, checkable shopping list.
- Constraints/taste: calm domestic editorial feel, low cognitive load, Firebase sharing, offline-tolerant list.

Do not treat the expanded inputs as user-verified facts. Record inferred items as assumptions.

## Use the evidence ladder

Gather only evidence that can change a decision:

1. **Repository evidence:** existing code, design tokens, content, analytics, rules, tests, environment examples, issue context.
2. **User evidence:** explicit brief, supplied files/screenshots, prior decisions, brand and business constraints.
3. **Domain evidence:** official product or regulatory sources, user vocabulary, expected workflows, content facts.
4. **Reference evidence:** analogous products, interaction patterns, art direction, asset precedents.
5. **Runtime evidence:** rendered output, logs, automated checks, device and assistive-technology behavior.

Label notes as `fact`, `user requirement`, `assumption`, `inference`, or `proposal`. Attach URL and retrieval date to web facts. Prefer primary sources for APIs, laws, prices, compatibility, and vendor requirements.

Stop research when new material no longer changes the blueprint. Do not postpone a reversible implementation decision merely to collect more inspiration.

## Research references without cloning

Choose a reference triad rather than one site to imitate:

| Lens | Look for | Extract |
| --- | --- | --- |
| Category convention | A mature product serving a similar job | Information hierarchy, expected terms, trust signals |
| Interaction model | A product with a similar task shape in another category | Flow mechanics, progressive disclosure, recovery |
| Visual/brand inspiration | Editorial, architecture, packaging, art, or a non-competing interface | Rhythm, material, imagery, type relationship, mood |

For every reference, record:

```text
Reference:
Purpose:
Abstract principle worth using:
Category convention users will expect:
Weakness/opportunity:
Elements forbidden to reproduce:
Decision changed:
Source and date:
```

Run a copy-avoidance check before visual sign-off:

- Compare hero composition, navigation, section order, typography, palette, signature illustrations, icons, copy, and motion.
- Replace any combination that would let a reasonable viewer name the source from the result.
- Never trace screenshots, remove watermarks, reproduce logos, or approximate proprietary illustrations.
- Use the functional convention when abandoning it would reduce usability; express it through the project's own visual grammar.

## Make and govern assumptions

Classify assumptions by reversibility and risk:

| Class | Examples | Action |
| --- | --- | --- |
| A: reversible presentation | Sample copy, route labels, initial ordering, illustration style | Decide, record, build |
| B: reversible product | Seed categories, notification defaults, optional onboarding step | Decide, expose in settings, record |
| C: costly architecture | SQL vs documents, SSR vs static, multi-tenancy, billing provider | Research and ask if evidence is insufficient |
| D: legal/security/irreversible | Data region, children, medical claims, operator identity, production deletion | Stop and obtain verified input/approval |

Use these safe defaults when the brief is thin:

- Select one primary persona and one primary success action.
- Prefer a familiar route model for the archetype.
- Create realistic fictional seed data and label it as demo data in development fixtures, not in the final interface.
- Design mobile-first unless a clearly desktop-dense job dominates; still make the core journey work on mobile.
- Use privacy-protective settings and disable optional telemetry/ads until configured.
- Prepare English source strings so they can be extracted for localization; do not assume every market uses English.
- Use a lightweight account model only if persistence or sharing actually needs identity.
- Keep destructive actions reversible or require confirmation plus a clear consequence.

Maintain the assumptions register inside `product/blueprint.json`:

```json
{
  "statement": "The primary user plans on desktop and executes on mobile",
  "basis": "Inferred from the task shape",
  "risk": "medium",
  "reversible": true,
  "validation": "Check device analytics after launch",
  "status": "assumed"
}
```

## Choose direct build or planning depth

Use a short internal blueprint and build immediately when all are true:

- one user role;
- one dominant journey;
- no payment, regulated data, UGC moderation, or destructive migration;
- a known framework and data model;
- fewer than roughly six routes.

Use an explicit reviewed plan when any are true:

- multiple roles or tenants;
- payment, subscriptions, marketplace, advertising, or affiliate monetization;
- children, health, finance, employment, education, identity, location, biometrics, or sensitive data;
- external API behavior drives the product;
- offline conflict resolution or realtime collaboration;
- migration of production data;
- more than one deployable service;
- unclear data residency or availability requirements.

Planning must remain executable. Resolve each requirement to a route, component, data field, permission, event, test, or launch gate.

## Write the app blueprint

Create `product/blueprint.json` before substantial code. Validate it against [app-blueprint.schema.json](../assets/app-blueprint.schema.json) when possible.

Required blueprint sections:

### Identity and outcome

- `name`, `slug`, `one_liner`, `archetype`, `status`.
- `primary_user`, `moment_of_use`, `job_to_be_done`, `success_action`, `success_metric`.
- `non_goals` to prevent feature drift.

### Information architecture

- Route, audience/role, purpose, primary action, data requirements, SEO/indexing intent.
- Navigation group and mobile behavior.
- Entry points and deep-link requirements.

### Flows and states

- Primary happy path as ordered steps.
- Recovery path for validation, network, authorization, and dependency failure.
- Loading, empty, zero-results, first-use, success, disabled, permission-denied, offline, and destructive-confirmation states.

### Data and permissions

- Entities, fields, ownership, retention, sensitivity, source of truth, indexes.
- Roles and an action matrix: create/read/list/update/delete/admin/export.
- Client versus server boundary for every privileged operation.

### Visual DNA

- Design thesis, desired and forbidden moods.
- Signature layout motif, type system, palette logic, surface/elevation language.
- Icon, illustration/photo, and motion treatment.
- Density and device strategy.

### Content and assets

- Page-level message hierarchy and evidence needed for claims.
- Asset inventory, gaps, provenance requirements, alt-text decision.
- Localization, currency, date/number, pluralization, and bidirectionality needs.

### Firebase/GCP

- Hosting profile and reason.
- Projects/environments, region, database, auth providers, storage, functions/services.
- Rules model, App Check, secrets, emulator fixtures, observability, budgets, backup/recovery.

### Compliance and release

- Target markets, legal entity facts still required, data categories, processors/vendors.
- Children/age, ads/affiliate, commerce/subscription, UGC, AI, health/finance flags.
- Consent categories, privacy controls, retention/deletion/export, accessibility target.
- `launch_blockers` with owner and resolution evidence.

### Acceptance

- Functional, visual, responsive, accessibility, performance, security, rules, content, and compliance criteria.
- Readiness label criteria: prototype, deploy, launch.

## Plan vertical slices

Prefer thin, demonstrable slices over isolated layers:

1. **Foundation:** route shell, tokens, navigation, metadata, environment validation, error boundary.
2. **Core slice:** entry → primary action → persisted result → confirmation/recovery.
3. **Identity and authorization:** only after the unauthenticated product model is clear.
4. **Secondary operations:** history, search/filter, settings, collaboration, export, admin.
5. **Launch layer:** consent, legal surfaces, observability, budgets, performance, asset set, deployment.

After each slice, render the app and perform the actual action. A compilation success is not a slice demo.

## Turn requirements into acceptance tests

Write acceptance criteria as observable behavior:

```text
Given a signed-out visitor on a 375px viewport
When they create a draft plan and choose Save
Then the app explains that an account is required, preserves the draft,
offers sign-in without a full-page context loss, and restores the draft after success.
```

Cover at least:

- the primary success path;
- invalid and partially complete input;
- empty/no-results data;
- slow and failed dependencies;
- unauthorized and cross-owner access;
- keyboard-only and reduced-motion use;
- phone and wide desktop composition;
- analytics/ads before and after consent decisions;
- deletion/export or cancellation when relevant.

Tie each acceptance criterion to an automated test where practical and a named manual check otherwise.
