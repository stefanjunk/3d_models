# Prompt-to-app examples

## Contents

1. [Affiliate decision product from one sentence](#affiliate-decision-product-from-one-sentence)
2. [Mobile-first operations dashboard](#mobile-first-operations-dashboard)
3. [Shared consumer planner](#shared-consumer-planner)
4. [Screenshot-led redesign without cloning](#screenshot-led-redesign-without-cloning)

## Affiliate decision product from one sentence

### Brief

> “Build a site that helps home-office users choose a standing desk and earns through Amazon affiliate links.”

### Assumptions to record and proceed with

- Primary user: remote worker comparing a first desk, unsure about size, stability, and total setup cost.
- Moment: research on desktop/phone; retailer handoff after a short decision guide.
- Product outcome: shortlist one of three fit categories and understand tradeoffs before leaving.
- Markets: unspecified; use `global-strict`, English source copy, no personalized ads, no live prices until a feed/API/source is configured.
- Evidence: no first-hand testing supplied; describe the methodology as researched comparison, never hands-on testing.

### Blueprint

```text
Routes:
/                    decision-first landing page and finder entry
/finder              room size, height, budget, equipment, priorities
/recommendations     transparent ranked matches + alternatives
/desks/[slug]        evidence, dimensions, strengths, limitations, price timestamp
/compare             accessible comparison table
/methodology         sources, scoring, update policy, conflicts
/privacy /terms /affiliate-disclosure /accessibility /contact

Entities:
Desk, MerchantOffer, SourceFact, Criterion, RecommendationRun

Primary flow:
answer five useful questions -> receive three explained matches
-> compare -> open retailer in a clearly named external link
```

### Art direction

Use “measured workshop”: off-white drafting canvas, graphite text, safety-orange action accent, measurement ticks, dimension diagrams, editorial product crops, condensed numeric labels. Avoid a generic tech gradient or fake lifestyle office stock.

### Firebase/GCP

- Static/editorial data with periodic updates: Firebase Hosting if statically generated.
- Firestore only if an editor/admin workflow or live offers are required.
- Scheduled Function for authorized data refresh; store source/time and handle unavailable values.
- Analytics and AdSense remain disabled until the legal profile and consent/CMP configuration are complete.

### Compliance gates

- Put affiliate disclosure beside monetized recommendations and links.
- Show methodology, source/update date, limitation, and retailer responsibility.
- Do not fabricate ratings, reviews, prices, stock, testing, discounts, urgency, or “best” claims.
- For AdSense traffic in EEA/UK/Switzerland, configure a currently Google-certified CMP/TCF path before serving personalized ads.
- Populate operator/privacy/terms from verified facts before launch.

### Acceptance tests

- A 375px user can complete the finder, revisit an answer, compare, and follow a disclosed retailer link using keyboard/touch.
- A missing/stale offer shows “check current price” with source date, not `0` or a fake sale.
- Rejecting optional tracking makes no Analytics/ads request.
- Every recommendation exposes why it fits and at least one limitation.

## Mobile-first operations dashboard

### Brief

> “Create a dashboard for support leads to keep tickets from breaching their SLA.”

### Assumptions to record

- User: non-technical lead managing 5–15 agents while walking the floor.
- Checks every 30 minutes on a phone; deeper reassignment happens on desktop.
- Core decision: which ticket/agent needs intervention now.
- Roles: agent, lead, admin. Do not expose all tickets to every authenticated user.

### Blueprint

```text
Routes:
/app                 attention queue, freshness, team status
/app/tickets         saved filters and bulk assignment
/app/tickets/[id]    thread, SLA, customer context, assignment/history
/app/team            workload and availability
/app/settings        notifications, privacy, accessibility, integrations

Entities:
Tenant, User, Membership, Ticket, Assignment, SLAEvent, AuditEntry

Primary flow:
see at-risk queue -> inspect ticket -> assign/reprioritize
-> accessible success status -> queue updates/undo
```

### Art direction

Use “calm incident room”: neutral high-contrast canvas, compact alignment, one vertical risk rail, clear age/priority labels, tabular numerals, restrained red/amber/green plus icon/text. Avoid a wall of metric cards; lead with the attention queue.

### Firebase/GCP

- Next.js on App Hosting for authenticated SSR/shell and server mutations.
- Firestore for realtime tickets/assignments if document workflows fit.
- Tenant/member/role Security Rules with positive and cross-tenant negative tests.
- Cloud Function for SLA events/notifications; idempotent and region-aligned.
- App Check staged after metrics; separate staging/production projects.

### Acceptance tests

- Wrong-tenant direct URLs and list queries are denied by Rules/server authorization.
- Reassignment is idempotent under a double tap and exposes undo/history.
- Phone view prioritizes at-risk queue; desktop adds adjacent detail without losing filter/scroll state.
- Empty, stale, offline, failed mutation, expired session, and notification failure are recoverable.

## Shared consumer planner

### Brief

> “Make a beautiful app where friends plan a weekend trip together.”

### Assumptions to record

- Primary user creates a two- or three-day plan and invites a small private group.
- Main devices: mobile during the trip, mixed devices during planning.
- Outcome: agreed itinerary with time/place, map link, notes, and shared status.
- Location data is entered as places; no continuous precise tracking.

### Blueprint

```text
Routes:
/                    value/demo entry
/trips/new           destination, dates, group setup
/trips/[id]          day timeline and shared state
/trips/[id]/ideas    proposals, votes, notes
/invite/[token]      preview and accept/decline
/settings/privacy    visibility, export, leave/delete

Entities:
Trip, Membership, Day, Activity, Proposal, Vote, Invite, AuditEntry
```

### Art direction

Use “annotated travel notebook”: layered timeline, ticket-stub date markers, place-caption imagery, warm paper neutral and a destination-derived accent. Keep handwriting to decorative marks; use accessible body type. Use one gentle “pin settles into itinerary” motion with a reduced-motion instant state.

### Firebase/GCP

- App Hosting + Next.js.
- Firestore realtime data with trip membership and invite Rules.
- Server-only invitation token creation/revocation.
- Storage only if the product includes shared photos; validate owner, size, type and retention.
- Do not enable persistent offline cache on shared devices without a product/privacy decision.

### Compliance and safety gates

- Private by default; show audience before posting.
- Avoid collecting precise background location.
- Provide leave trip, revoke invite, block/report if public discovery later exists, export/delete.
- Obtain rights/provenance for destination imagery; do not imply generated scenes are documentary facts.

### Acceptance tests

- A creator can invite, a guest can accept, both see updates, and a removed member loses direct/read/list access.
- A revoked/expired invite has a clear recovery path without leaking trip details.
- Timeline works at 320px, 200% zoom, keyboard, screen reader, reduced motion, and offline/reconnect.

## Screenshot-led redesign without cloning

### Brief

> “Use this competitor screenshot as inspiration and redesign my existing booking app.”

### Safe process

1. Inspect the repository and screenshot.
2. Ask only if the user cannot confirm they may use supplied assets or if it contains private/confidential material.
3. Extract abstract principles:
   - prominent availability search;
   - calendar + result adjacency;
   - clear price/constraint comparison;
   - trust details near booking.
4. List forbidden reproduction:
   - brand palette/logo;
   - exact hero/calendar composition;
   - copy, icons, photos, animation;
   - distinctive card silhouettes and section order.
5. Generate three product-specific compositions and choose one against the user's audience and flow.

### Alternative direction

Use “concierge ledger”: a vertical date rail on wide screens, a bottom-sheet date flow on phones, editorial property/appointment detail, transparent price/availability annotations, and a persistent summary that never hides terms. Use the user's verified brand and original/provenanced assets.

### Acceptance tests

- Side-by-side review cannot identify the source from composition, copy, trade dress, or assets.
- Search, availability, selection, errors, confirmation, cancellation, and back-navigation all work.
- Existing data/auth/analytics behavior remains intact or has explicit migration tests.
- Visual changes do not reduce accessibility, performance, or legal disclosures.
