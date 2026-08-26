# Content and assets

## Contents

1. [Write product copy from evidence](#write-product-copy-from-evidence)
2. [Create a message hierarchy](#create-a-message-hierarchy)
3. [Choose the right visual asset](#choose-the-right-visual-asset)
4. [Source, generate, and clear assets](#source-generate-and-clear-assets)
5. [Maintain provenance](#maintain-provenance)
6. [Prepare images and media](#prepare-images-and-media)
7. [Create the launch asset set](#create-the-launch-asset-set)
8. [Handle icons, logos, and fonts](#handle-icons-logos-and-fonts)
9. [Prepare SEO and sharing](#prepare-seo-and-sharing)
10. [Prepare localization](#prepare-localization)

## Write product copy from evidence

Write copy in this order:

1. User's situation and vocabulary.
2. Specific outcome and mechanism.
3. Evidence or product behavior that supports the claim.
4. Limitation, requirement, or next action.

Use concrete nouns and verbs. Prefer “Compare three plans by total annual cost” to “Unlock smarter decisions.” Prefer “Save this filter” to “Get started.”

Create a claims ledger for public/commercial apps:

| Claim | Location | Evidence/source | Owner | Last verified | Status |
| --- | --- | --- | --- | --- | --- |

Block or soften claims without support. Do not invent:

- customer names, logos, quotes, ratings, or review counts;
- usage, savings, speed, conversion, market share, or performance metrics;
- “tested,” “expert,” “certified,” “secure,” “compliant,” or “best” assertions;
- current price, stock, delivery, law, compatibility, or API support without verification;
- first-person experience the operator did not have.

Keep example/demo records credible but fictional. Use neutral names and content that do not imitate real people. Mark fixtures in source/test data, not with distracting “demo” badges throughout the final UI unless users may mistake the environment for real production data.

## Create a message hierarchy

For each route, define:

```text
User question:
One-sentence answer:
Evidence/mechanism:
Primary action:
Likely objection:
Recovery/help:
```

Write interface copy for every state:

- labels and field help;
- empty and zero-results guidance;
- loading/progress status;
- validation and system errors;
- permission/session expiration;
- save/success/undo confirmation;
- destructive consequence and alternative;
- email/notification confirmation when the app sends one.

Use headings to orient, not decorate. Avoid repeating the same sentence in heading, subheading, card title, and button.

## Choose the right visual asset

Use an asset only when it serves one or more jobs:

| Job | Suitable asset |
| --- | --- |
| Demonstrate the product | Real screenshot, annotated UI, interactive preview, short task video |
| Explain a system | Diagram, process illustration, map, data visualization |
| Establish emotional context | Art-directed documentary/editorial photo, original illustration |
| Support object choice | Consistent product/item photography, floor plan, thumbnail set |
| Provide identity | Logo, signature shape, icon system, texture, character |
| Resolve emptiness or error | Small contextual illustration with helpful copy/action |
| Improve sharing | Route-specific Open Graph card |

Do not use generic stock imagery as visual filler. A strong type/layout composition is better than an irrelevant smiling-office photo.

Choose asset density by archetype:

- marketing/travel/commerce: media can carry narrative and comparison;
- SaaS/operations: product views, diagrams, data, and status dominate;
- utilities: keep media secondary to the input/result;
- content/catalog: media follows a documented editorial/catalog system.

## Source, generate, and clear assets

Use this preference order:

1. User-supplied assets with confirmed permission.
2. Original assets created for this project.
3. Official brand/product media under an applicable permission or press/partner program.
4. Commercially usable library assets with verified license and attribution terms.
5. Generated assets with a recorded tool/model, prompt/brief, date, edits, and human review.

Before using a third-party asset, verify:

- the actual license text, not a search snippet;
- commercial use, modification, distribution, and attribution conditions;
- whether people, property, trademarks, artwork, or products require releases/permissions;
- whether the license applies to the exact file and intended context;
- whether downstream redistribution in templates/source is permitted.

Do not assume “free,” “royalty-free,” a Creative Commons badge, or an image-search filter resolves all rights. Never remove watermarks or attribution metadata to hide provenance.

When generating imagery:

- write an art-direction brief tied to the visual thesis;
- generate a small coherent set, not unrelated one-offs;
- request space/orientation for the intended layout;
- inspect hands, text, logos, flags, product details, maps, medical/safety content, and cultural signals;
- do not depict a real person, endorsement, event, product performance, or documentary fact as authentic unless properly authorized and labeled;
- retain content credentials/provenance metadata when available;
- add an AI/synthetic disclosure when law, platform policy, or likely user interpretation requires it.

## Maintain provenance

Copy [asset-ledger.template.csv](../assets/asset-ledger.template.csv) to `product/asset-ledger.csv` and maintain it as assets enter the repository.

Required fields:

- repository path and route/use;
- asset kind and subject;
- origin URL or “project-generated”;
- creator/provider;
- exact license/permission and evidence location;
- acquisition/generation date;
- model/tool and prompt/brief reference when generated;
- modifications;
- attribution text/location;
- release/trademark review;
- alt-text decision;
- clearance status and owner.

Treat `unknown`, `search result`, and “found online” as uncleared. Do not ship an uncleared material asset.

For reference screenshots used only during design, keep them outside public assets and record “reference only—not for distribution.”

## Prepare images and media

### Raster images

- Start from an adequate master; avoid upscaling a small source to fake detail.
- Produce sizes around actual rendered widths and device density; do not send a 4000px master into a 320px card.
- Prefer AVIF/WebP for photographs when the toolchain and target support them; keep PNG for transparency/line detail and JPEG where compatibility or source requires it.
- Preserve the original master separately when future crops matter.
- Set intrinsic width/height or aspect ratio to prevent layout shift.
- Use responsive `sizes` and `srcset`/framework image behavior.
- Give the initial LCP image high priority and do not lazy-load it; lazy-load offscreen media.
- Use an image-processing pipeline compatible with Firebase App Hosting; do not assume Vercel image services.

### Video/audio

- Provide captions for speech and meaningful sound; provide transcript when useful.
- Include poster art and dimensions.
- Avoid autoplay with sound. Respect reduced motion and data-saving contexts.
- Use adaptive/streaming delivery for substantial media rather than bundling large files.
- Make controls keyboard and screen-reader operable.

### SVG and animation

- Sanitize untrusted SVG; avoid inserting arbitrary SVG markup from users.
- Keep text accessible or reproduce it in HTML.
- Use currentColor/tokens for system icons where appropriate.
- Provide a static/reduced-motion alternative for animated SVG, canvas, WebGL, shaders, or Rive content.

Decorative assets should use empty alt text. Informative assets need concise alt text conveying purpose, not visual trivia. Complex charts need a summary and data table or equivalent.

## Create the launch asset set

Create applicable assets before launch:

- favicon at multiple sizes;
- app/touch icon and mask-safe variant;
- manifest icons for installable apps;
- default and route-specific Open Graph/social images;
- logo lockups for light/dark backgrounds;
- responsive product/hero imagery;
- empty, error, offline, and success illustrations only when they add orientation;
- email/logo assets if transactional email is part of the flow;
- screenshot set for stores/directories only when distribution requires it.

Test images under dark mode, high contrast, browser zoom, and social crops. Do not place critical text near common crop edges.

## Handle icons, logos, and fonts

### Icons

- Use one coherent family and import only needed icons.
- Preserve the icon library's license/notice.
- Use icons as reinforcement; keep visible labels for unfamiliar, high-impact, or ambiguous actions.
- Give icon-only buttons accessible names and adequate targets.

### Logos and brands

- Use official supplied artwork and follow current brand rules.
- Do not imply partnership or endorsement through placement.
- Name third-party integration logos accurately and distinguish “works with” from sponsorship.
- Avoid recreating an unavailable brand mark from memory or generative output.

### Fonts

- Verify web embedding, commercial use, modification/subsetting, and redistribution rights.
- Prefer self-hosting when allowed for performance/privacy/control.
- Keep font files out of public source templates unless redistribution is permitted.
- Record family, source, version, license, subsets, and fallback stack.
- Test every required script and diacritic; a visually ideal Latin-only font is not a global system.

## Prepare SEO and sharing

For public/indexable routes:

- write a unique title and description matching actual content;
- set canonical URLs and explicit index/noindex intent;
- create sitemap and robots behavior appropriate to public versus private routes;
- add structured data only when the page visibly contains the matching, verified information;
- use semantic headings, links, lists, tables, and landmarks;
- create durable human-readable route slugs;
- return correct status codes for missing, redirected, private, and removed content;
- include Open Graph/social metadata and a tested share image;
- avoid indexing account, search-result, filter explosion, preview, staging, or sensitive routes.

Do not create doorway pages or mass-generated thin content. Factual programmatic pages require unique value, source freshness, canonical logic, and a correction/update process.

## Prepare localization

- Extract user-facing strings; avoid concatenating sentence fragments.
- Use locale-aware number, currency, relative time, date, plural, and list formatting.
- Store timestamps in a stable machine form and render in the user's chosen context.
- Do not infer permanent locale solely from IP or browser language; provide stable locale URLs or settings and a visible override.
- Allow 30–50% text expansion in navigation, buttons, and forms.
- Mirror directional layout intentionally for RTL while keeping media, charts, codes, and numbers semantically correct.
- Localize alt text, metadata, email, validation, legal content, and generated media text.
- Do not machine-translate legally material or safety-critical copy without qualified review.
