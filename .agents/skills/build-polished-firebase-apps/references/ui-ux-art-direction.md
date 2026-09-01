# UI/UX art direction

## Contents

1. [Design from a thesis](#design-from-a-thesis)
2. [Generate and choose directions](#generate-and-choose-directions)
3. [Use style families deliberately](#use-style-families-deliberately)
4. [Build the token system](#build-the-token-system)
5. [Create hierarchy and rhythm](#create-hierarchy-and-rhythm)
6. [Treat type as interface](#treat-type-as-interface)
7. [Use color semantically](#use-color-semantically)
8. [Define surfaces, shapes, and icons](#define-surfaces-shapes-and-icons)
9. [Use motion for causality](#use-motion-for-causality)
10. [Score distinctiveness](#score-distinctiveness)
11. [Run the anti-generic review](#run-the-anti-generic-review)

## Design from a thesis

Write one sentence that connects the product's job to the desired feeling and visual behavior:

> “A planning workspace that turns a chaotic week into a calm, annotated field guide.”

Translate that sentence into a visual fingerprint:

| Axis | Decision | Example |
| --- | --- | --- |
| Metaphor | Product idea expressed visually | Field guide, control room, studio wall, ledger |
| Composition | Recognizable spatial behavior | Annotated rail, offset split, framed canvas, stacked timeline |
| Typography | Relationship, not merely font names | Expressive condensed headings + quiet humanist body |
| Color logic | What color means | Ink/paper neutral; one botanical action color; amber warnings |
| Material | Surface and edge language | Fine rules, paper grain, crisp inset panels |
| Imagery | Consistent treatment | Cropped documentary photos with caption strips |
| Motion | One recurring behavioral signature | Sections settle into alignment; results count in once |

Require at least three fingerprint decisions beyond logo and accent color to be visibly present.

## Generate and choose directions

Generate three directions privately before coding major surfaces. Make them structurally different, not palette swaps.

For each direction, specify:

```text
Name:
Product promise:
Desired adjectives:
Forbidden adjectives:
Composition:
Type relationship:
Color logic:
Surface/material:
Image/icon treatment:
Motion signature:
Memorable interaction:
Risk to usability:
```

Score each direction from 1–5 on:

- audience fit;
- task clarity;
- emotional fit;
- extensibility across all routes;
- accessibility feasibility;
- asset feasibility;
- category distinction without confusion.

Choose one dominant direction. Borrow at most one supporting device from another. Do not blend every interesting idea.

## Use style families deliberately

Use these as starting grammars, not ready-made themes:

| Family | Works for | Key moves | Common failure |
| --- | --- | --- | --- |
| Editorial clarity | Content, comparison, premium services | Strong type scale, captions, asymmetric whitespace, rules | Becoming a magazine that hides actions |
| Precision instrument | B2B, operations, analytics | Dense alignment, calibrated color, compact controls, explicit states | Coldness and tiny text |
| Warm tactile | Home, wellness, craft, food | Natural palette, rounded organic forms, texture, human imagery | Low contrast or childish softness |
| Quiet luxury | High-consideration products | Restrained palette, generous space, art-directed imagery, slow rhythm | Empty pages and vague copy |
| Civic trust | Finance-adjacent, public-interest, compliance | Plain language, stable grid, evidence, visible help | Bureaucratic visual weight |
| Playful modular | Learning, creator, family tools | Bold modular shapes, surprising grouping, responsive microcopy | Confetti everywhere and weak hierarchy |
| Technical studio | Developer and AI tools | Monospace accents, command surfaces, visible system state | Terminal cosplay and inaccessible density |
| Archival catalog | Collections, research, marketplaces | Indexing, labels, serials, filters, object-first imagery | Over-designed metadata |
| Cinematic narrative | Launch, travel, entertainment | Scene-based scroll, full-bleed media, dramatic contrast | Heavy assets and buried conversion |
| Neo-brutal utility | Youthful utility, events, cultural products | Direct type, hard borders, intentional rawness, obvious controls | Random ugliness or exhausting contrast |
| Organic systems | Climate, nature, community | Flowing dividers, maps, data + landscape, earthy accents | Decorative blobs unrelated to data |
| Data-forward calm | Health tracking, planning, progress | Layered summaries, quiet charts, trend annotations | Dashboard of interchangeable cards |

Express a family through type, layout, and content—not just color.

## Build the token system

Use semantic tokens so screens remain coherent and themes remain possible.

### Required token groups

- `surface`: canvas, raised, sunken, overlay, inverse.
- `text`: primary, secondary, muted, inverse, link.
- `action`: primary, secondary, destructive, focus.
- `status`: success, warning, danger, info, neutral.
- `border`: subtle, default, strong, focus.
- `space`: a compact scale with intentional large jumps.
- `size`: content widths, control heights, icon sizes, touch targets.
- `radius`: two or three related values plus pill only when semantically useful.
- `shadow`: none/subtle/raised/overlay; use borders or contrast before shadow.
- `motion`: duration, easing, distance, stagger; include reduced-motion behavior.
- `type`: display, title, body, label, caption, code/data.

Use a base spacing unit such as 4px, but choose rhythm optically. A useful scale is 4, 8, 12, 16, 24, 32, 48, 64, 96; do not force every relationship onto the same increment.

Keep controls at least 44×44 CSS pixels for important touch targets unless a denser pattern has a documented accessible alternative. Preserve visual focus at all densities.

## Create hierarchy and rhythm

Compose every screen at three reading distances:

1. **Glance:** purpose, status, and next action.
2. **Scan:** sections, objects, comparisons, priority.
3. **Read:** detailed copy, metadata, explanation, recovery.

Create hierarchy in this order:

1. Content priority and order.
2. Proportion and whitespace.
3. Alignment and grouping.
4. Typography.
5. Color and surface.
6. Decoration.

Use a layout grid, then break it once for emphasis. A signature offset is memorable; many arbitrary misalignments look broken.

Vary section rhythm intentionally. Alternate dense/quiet, text/media, explanation/proof, and exploration/decision. Repeating identical full-width card rows creates template fatigue.

## Treat type as interface

- Use one body family and optionally one display/data family. Add a third only for a specific functional script or code role.
- Choose families with the required language coverage before designing around them.
- Use local or self-hosted web fonts when licensing permits; subset responsibly and retain license notices.
- Use fluid display sizes with bounded `clamp()` values. Keep body text near 16px or larger on mobile.
- Keep prose around 45–75 characters per line; shorten instructions and form help further.
- Use weight, size, and whitespace before letter spacing. Avoid wide tracking on body copy.
- Use tabular numerals where values compare vertically or update in place.
- Do not put essential text inside raster images.
- Test long German-like labels, large translated expansion, mixed case, dates, currency, and RTL when relevant.

Typography must still work while the custom font loads or fails.

## Use color semantically

Define roles before hex values:

- one canvas family;
- one text family;
- one primary action color;
- one optional expressive accent;
- status colors that do not rely on hue alone.

Use the 60/30/10 idea only as a rough visual balance, not a rigid formula. Prefer large neutral fields with controlled emphasis for task interfaces; narrative products may invert that balance.

Check contrast in every state, including muted copy, placeholder text, disabled controls, charts, focus rings, selected rows, dark mode, image overlays, and visited links. Pair status color with text, icon, pattern, or position.

Avoid:

- a fashionable accent unrelated to the product;
- gradient text on important copy;
- low-opacity gray on white as a substitute for hierarchy;
- pure black/white everywhere when a softer contrast system fits;
- dark mode produced by mechanically inverting colors.

## Define surfaces, shapes, and icons

Choose one edge grammar:

- crisp rules and small radii;
- friendly medium radii;
- soft organic silhouettes;
- framed/inset objects;
- intentionally hard brutalist borders.

Do not mix all of them. Use pills for tags, compact filters, or binary state—not every button and heading.

Use surfaces to express nesting and interaction. A card is appropriate for an independently actionable or movable object; it is not the default wrapper for every paragraph.

Use one icon family with consistent stroke/fill, optical size, and corner character. Add text to novel or consequential icon actions. Treat brand logos as licensed assets, not generic icons.

## Use motion for causality

Define motion by user question:

| User question | Useful motion |
| --- | --- |
| What changed? | Highlight, count, or local state transition |
| Where did it go? | Shared-axis movement or expanding origin |
| Is work happening? | Progress, skeleton, or determinate status |
| What is related? | Coordinated reveal or spatial grouping |
| Did my action succeed? | Immediate state confirmation near the action |

Use 120–220ms for small state transitions and roughly 220–450ms for meaningful spatial changes; tune by distance and context. Prefer opacity and transform to layout-triggering animation.

Avoid entrance animation on every element, scroll-jacking, continuous ambient movement around reading/action areas, and motion that delays input. Under `prefers-reduced-motion`, remove nonessential travel/parallax and preserve immediate state changes.

## Score distinctiveness

Score the rendered app from 0–2 on each axis:

| Axis | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Product-specific metaphor | None | Mentioned | Visible and useful |
| Composition | Stock template | Some variation | Recognizable spatial signature |
| Typography | Default stack/scale | Tuned | Expressive and highly legible relationship |
| Color/material | Generic trend | Product-fit palette | Product-fit system with clear semantics |
| Assets | Placeholder/random stock | Consistent | Original/provenanced and structurally integrated |
| Interaction | CRUD defaults | One thoughtful detail | Memorable behavior that improves the job |
| Content voice | Generic | Specific | Distinct, credible, consistent |

Require at least 10/14, no zero in accessibility-critical execution, and at least three axes scoring 2. Re-score the weakest interior screen, not only the marketing hero.

## Run the anti-generic review

Search the rendered product for these symptoms:

- oversized gradient headline + centered badge + two buttons + floating dashboard image;
- blue/purple blur behind everything;
- three identical benefit cards with vague nouns;
- every section inside rounded cards;
- overuse of sparkles, rockets, shields, and lightning icons;
- fake logos, star ratings, testimonials, or “trusted by” rows;
- glassmorphism without a layered spatial reason;
- unnecessary dashboard stat cards before the primary action;
- a desktop layout merely squeezed into one mobile column;
- shadcn/ui defaults with only the primary color changed;
- animation library effects with no product meaning;
- generic names such as “Nexus”, “Elevate”, or “Transform” chosen without domain rationale.

For every symptom, change the underlying idea—not merely the border radius. Revisit content order, layout structure, visual thesis, and the user's moment of use.
