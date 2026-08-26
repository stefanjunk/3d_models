# Layout and flow patterns

## Contents

1. [Choose by user job](#choose-by-user-job)
2. [Use shared composition rules](#use-shared-composition-rules)
3. [Build marketing and launch sites](#build-marketing-and-launch-sites)
4. [Build SaaS workspaces and dashboards](#build-saas-workspaces-and-dashboards)
5. [Build utilities and generators](#build-utilities-and-generators)
6. [Build commerce, affiliate, and marketplace products](#build-commerce-affiliate-and-marketplace-products)
7. [Build content, catalog, and research products](#build-content-catalog-and-research-products)
8. [Build communities and UGC products](#build-communities-and-ugc-products)
9. [Design onboarding, forms, and settings](#design-onboarding-forms-and-settings)
10. [Adapt across breakpoints](#adapt-across-breakpoints)
11. [Cover states and recovery](#cover-states-and-recovery)

## Choose by user job

Select the dominant archetype from the primary success action:

| Success action | Archetype | Dominant structure |
| --- | --- | --- |
| Understand and decide | Marketing/launch | Narrative sequence with evidence and objections |
| Monitor and act repeatedly | SaaS workspace/dashboard | Persistent navigation + task workspace |
| Enter, transform, receive | Utility/generator | Immediate input → progress → result |
| Discover and purchase | Commerce | Search/browse → compare → detail → checkout |
| Discover and leave via monetized link | Affiliate/recommendation | Decision guide → transparent ranking → retailer handoff |
| Match buyers and sellers | Marketplace | Discovery + trust + transaction + dispute/reporting |
| Find and learn | Content/catalog | Search/index + topic structure + reading/detail |
| Contribute and converse | Community/UGC | Feed/topic + composer + identity + moderation |
| Coordinate records | Portal/internal tool | Queue/list + detail + action history |

Combine archetypes only around a clear primary shell. A SaaS product may have a marketing shell, but the authenticated workspace should not inherit the landing page's composition.

## Use shared composition rules

### Page anatomy

Give each page:

- a clear landmark and unique title;
- a short orientation cue when context is not obvious;
- one dominant action or decision;
- visible system status when data can be stale or incomplete;
- a recovery route and support path;
- a meaningful final edge, not an accidental blank bottom.

### Width

- Use roughly 60–75ch for long prose.
- Use a 1100–1280px content cap for mixed marketing sections unless art direction calls for controlled full bleed.
- Let dense workspaces use available width with stable gutters; retain a readable detail pane.
- Use full bleed for media/background only when it contributes to narrative or comparison.

### Density

Offer density according to task frequency:

- occasional/consumer: generous controls, explanation, progressive disclosure;
- repeated/professional: compact rows, keyboard paths, saved views, visible batch actions;
- mixed: comfortable default plus an optional compact mode.

Never shrink text or targets merely to fit more. Remove, group, or defer information first.

## Build marketing and launch sites

Use a decision narrative rather than a standard section checklist:

1. **Promise:** identify audience, pain, outcome, and primary action above the fold.
2. **Immediate proof:** show the product, result, demo, credible evidence, or mechanism.
3. **How it changes the job:** explain the before/after workflow.
4. **Capability:** group features by user outcome, not internal architecture.
5. **Fit and limits:** state who it is for, who it is not for, requirements, and constraints.
6. **Risk resolution:** privacy, integration, support, returns, migration, or FAQ as appropriate.
7. **Decision:** pricing/plan or next action with full material terms.

Vary composition across the narrative. Use a product canvas, annotated demo, comparison table, timeline, evidence strip, case vignette, or interactive estimator when each conveys meaning better than another three-card row.

Required route candidates:

- `/`;
- `/features` or use-case routes only when search/content depth warrants them;
- `/pricing` when material terms cannot fit near conversion;
- `/about` or provenance when trust depends on operator story;
- `/contact` or support;
- privacy, terms, cookie/preferences, accessibility;
- sign-in/app entry for a product.

Keep global navigation concise. On mobile, keep the main conversion action visible without covering content or consent choices.

## Build SaaS workspaces and dashboards

Use persistent navigation for recurring, multi-route work:

- sidebar for stable modules and frequent desktop use;
- top navigation for few modules or document-like depth;
- sidebar + top utility bar only when account/global actions are truly distinct.

Organize the workspace:

1. Scope/context switcher: tenant, project, date range, saved view.
2. Status and anomalies: what needs attention now.
3. Primary work object: queue, table, canvas, editor, or detail—not decorative metrics.
4. Supporting analysis: trends, breakdowns, history.
5. Action and recovery: create, assign, resolve, export, undo.

Dashboard rules:

- Show a metric only when the user knows what decision it supports.
- Pair value with definition, comparison period, freshness, and drill-down.
- Use charts for patterns, not single values. Provide text/table alternatives.
- Put alert/anomaly items before broad summaries when urgency drives use.
- Keep filters reflected in the URL where sharing/back navigation matters.
- Preserve table sort/filter/page state across detail navigation.

Responsive workspace patterns:

- Collapse the sidebar to a sheet or focused module switcher.
- Convert master/detail to list → full-screen detail on narrow widths; preserve return position.
- Transform wide tables into prioritized rows with expandable secondary fields; do not turn every cell into a separate card.
- Keep batch operations accessible through explicit selection mode.

Include routes such as `/app`, object list/detail/create, activity/history, notifications, settings/profile, organization/team, billing only when active, support, and admin only for authorized roles.

## Build utilities and generators

Put the useful action above the fold. Avoid forcing users through a marketing page before a low-risk utility.

Recommended flow:

1. Minimal input with a useful example or prefilled demo.
2. Inline validation and constraints before submission.
3. Explicit progress when work is not immediate; preserve cancel/retry when feasible.
4. Result optimized for the next job: copy, download, edit, compare, save, share.
5. History/account upsell only after value, unless identity is technically required.

Use split view on wide screens when input and result benefit from comparison. Stack input then result on narrow screens and make the transition obvious.

For AI or uncertain output, include provenance/context, limitations, a way to refine, feedback/reporting, and safe handling of sensitive input. Never present fabricated certainty.

## Build commerce, affiliate, and marketplace products

### Commerce

Required journey:

1. Discover through categories/search/editorial entry.
2. Filter and compare without losing position or state.
3. Inspect a detail page with complete price, availability, delivery, return, variant, and seller information.
4. Add/edit cart with immediate totals.
5. Check out with clear steps, errors, final total, and unambiguous purchase action.
6. Receive durable confirmation and order management.

Do not hide mandatory fees until the final click. Do not preselect paid extras. Keep guest checkout unless identity is genuinely necessary.

### Affiliate/recommendation

Required journey:

1. State the decision question and intended audience.
2. Explain selection methodology, update date, testing/research basis, and conflicts.
3. Provide filters or a decision guide before rankings.
4. Show why each option fits, limitations, price/source date, and alternatives.
5. Place a clear affiliate disclosure near monetized recommendations and links.
6. Distinguish retailer data from independent analysis.

Never fabricate first-hand testing, ratings, prices, availability, reviews, or “best” claims. Link to a retailer with an accessible name that signals the destination.

### Marketplace

Add seller/trader identity, verification status, reporting, moderation, dispute/help, provenance, fulfillment responsibility, and review authenticity. Separate platform promises from seller claims.

Design seller onboarding, inventory management, buyer discovery, transaction, fulfillment, cancellation/refund, review, report, and appeal as connected journeys. A product-grid prototype is not a marketplace.

## Build content, catalog, and research products

Use information scent and stable addresses:

- global search with suggestions and useful zero-results recovery;
- topic/index navigation;
- result list with enough context to choose;
- canonical detail/reading route;
- related content based on meaning, not only recency;
- source, author, date, update status, and citations when factual trust matters.

For reading pages:

- keep prose width controlled;
- provide table of contents for long structured material;
- make headings linkable;
- put key summary and update date early;
- keep citations adjacent to supported claims;
- avoid interruptive ads inside a sentence or core interactive control.

For catalogs, use object-specific filters, comparison, saved lists, and metadata. Avoid generic card grids when a compact list, table, map, timeline, or gallery better matches the collection.

## Build communities and UGC products

Required system surfaces:

- public/private audience clarity before posting;
- composer with draft preservation, preview, limits, and upload status;
- feed/topic/thread with stable permalinks;
- identity/profile and privacy controls;
- report/block/mute near the affected content or user;
- moderation state and reason;
- appeal/contact route;
- notification preferences;
- deletion/deactivation and data export.

Design empty communities without fake engagement. Use prompts, starter topics, examples, or editorial seed content clearly owned by the operator.

Keep counts and ranking from becoming the only hierarchy. Offer chronological or user-controlled alternatives where required by product or regulation.

## Design onboarding, forms, and settings

### Onboarding

- Ask only what changes the initial experience.
- Show value before account creation when possible.
- Keep one coherent decision per step; show progress for multi-step flows.
- Explain why sensitive or surprising data is requested at the field.
- Permit skip/later for optional personalization.
- Make back navigation safe and preserve prior answers.
- End in the product with a meaningful first object or next action, not a congratulatory dead end.

### Forms

- Use persistent visible labels and concise field help.
- Group by user concept, not database schema.
- Validate format locally, business rules authoritatively on the server, and uniqueness without leaking other users.
- Show errors at the field and in an accessible summary for long forms.
- Preserve valid input after failure.
- Use appropriate input modes, autocomplete tokens, and password-manager-friendly markup.
- Confirm destructive actions by consequence; require typed confirmation only for rare, severe outcomes.

### Settings

Separate profile, security, notifications, privacy/data, appearance/language, organization, billing, and danger-zone concerns. Put current state beside each setting. Make save behavior explicit and avoid mixed automatic/manual persistence on one surface without clear feedback.

## Adapt across breakpoints

Do not design to device names. Test where content needs to reflow.

At narrow widths:

- prioritize the primary action and core status;
- change navigation into a concise sheet/tab/module switcher;
- stack only relationships that remain understandable;
- move secondary metadata behind disclosure;
- keep error/help text close to controls;
- avoid fixed-height content and viewport traps;
- account for safe areas and virtual keyboards;
- keep sticky controls from obscuring focus or consent choices.

At wide widths:

- add useful adjacency, not empty margins;
- use split views for compare/edit/detail when simultaneous context helps;
- cap prose even inside wide workspaces;
- keep actions near the object they affect;
- avoid stretching forms and buttons across the screen.

Test 200% zoom and content expansion. A “desktop” layout may receive a narrow effective viewport under zoom.

## Cover states and recovery

Specify these states for every data-dependent surface:

| State | Required behavior |
| --- | --- |
| Initial loading | Preserve layout, name what is loading when useful, avoid false progress |
| Empty first use | Explain value and provide the first action/example |
| Zero results | Keep query/filter context, explain why, offer clear recovery |
| Partial data | Render usable results and identify missing/stale portions |
| Slow work | Show progress/status, allow safe cancellation or background continuation |
| Validation error | Preserve input, focus/announce summary, identify exact correction |
| Dependency/network error | Explain impact, offer retry, prevent duplicate submission |
| Unauthorized | Distinguish signed-out, wrong role, expired session, and missing object |
| Offline | Identify offline state and what will sync or remain unavailable |
| Success | Confirm outcome near the action and expose the next likely job |
| Destructive pending | State object, scope, permanence, side effects, and alternative |

Use an error boundary and route-specific fallback, but also design local failures so one widget does not erase an otherwise usable page.
