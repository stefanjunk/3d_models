# Commercial 3D Model Research Report

Prepared: 2026-08-10
Scope: commercial sale of 3D model files and printed physical objects, with AI-assisted image/code/design inputs and worldwide-market ambitions.

## Contents

1. Executive conclusions
2. Responsibility by layer
3. Recommended commercial architecture
4. Recommended evidence stack
5. Recommended watermark
6. What requires a separate license
7. Highest-risk misconceptions
8. Implementation included in this skill
9. Limits

## Executive Conclusions

1. There is no single “commercial 3D license.” Permission must be cleared across inputs, contributors, tools/plans, embedded assets/components, output layers, IP rights, customer terms, and product/market law.
2. Contract ownership of an AI output is not the same as statutory copyright, exclusivity, or non-infringement. Preserve human design contribution and use designs/patents/trademarks/contracts strategically.
3. A supplier’s “official” CAD model is usually an engineering resource, not automatically redistributable content. Ship a simplified interface envelope and official link unless redistribution rights are explicit.
4. Open-source CAD application licenses normally do not “infect” ordinary model output. Copied code, plugins, fonts, textures, templates, libraries, and distributed modified software require separate review.
5. EU AI law does not currently create a blanket “AI-generated” label for every mesh or printed object. Article 50 is actor- and modality-specific. Preserve image provenance, disclose deceptive synthetic renders, and use a truthful voluntary AI-assisted statement for the sold design.
6. Watermarking must be layered: visible geometry release ID, 3MF/native metadata, signed sidecar/checksums, retained C2PA on source images, and optionally tested forensic geometry. No layer creates ownership or prevents removal.
7. Selling the physical product adds safety, conformity, labeling, traceability, insurance, incident, packaging, tax, and recall duties. Selling the file still creates digital-content and potentially product-liability exposure.
8. The recast EU Product Liability Directive expressly includes digital manufacturing files and applies to products placed on the market or put into service after 9 December 2026, following national transposition.
9. “Worldwide” launch must be represented as an approved country/channel matrix. No honest global clearance can be issued from one checklist.
10. Release automation should fail closed. Unknown licenses, missing evidence, NC/ND conflicts, restricted supplier CAD, unclassified safety products, and export red flags are BLOCK conditions.

## Responsibility by Layer

| Layer | Upstream party may provide | Commercial seller must still do |
|---|---|---|
| AI provider | Service access, output assignment/license, provenance signals | Input rights, review, similarity/IP clearance, disclosure role, safety |
| Image/asset licensor | Copyright permission under stated terms | Confirm AI/3D adaptation/merchandise scope and other depicted rights |
| CAD tool vendor | Right to run tool; output clause | Verify exact plan, plugins/assets, commercial use, dependencies |
| Community library | Item page/license | Verify uploader authority, exact version, compatibility, attribution |
| Supplier/manufacturer | CAD/datasheet/component | Confirm redistribution, genuine supply, ratings, IP/safety |
| Marketplace | Hosting/payment fields | Terms, consumer law, tax, safety, AI/IP truth, takedown response |
| Print service | Manufacturing service | Specifications, material/process qualification, inspection, traceability |
| Customer | Acceptance/payment | Nonwaivable consumer/product duties and accurate license grant |
| Seller | Final design/release | Complete chain of title, FTO decisions, compliance, records, incidents |

## Recommended Commercial Architecture

### Digital File

- proprietary geometry EULA by default when monetizing controlled access;
- optional distinct commercial print license tier;
- software license for scripts;
- documentation license;
- third-party notices and open-license exceptions;
- sanitized provenance manifest plus checksums/signature;
- customer assent and EU digital-content checkout evidence;
- versioned correction/withdrawal capability.

Do not promise that the customer receives exclusive copyright if AI-only or third-party elements exist.

### Physical Product

- retain IP; sell the particular object without transferring reproduction rights;
- qualify exact material/process/component chain;
- classify product and target market;
- create technical file/risk assessment/tests;
- label manufacturer/identifier/warnings and responsible operator;
- insure and maintain batch/customer incident/recall trace.

### Open Release

- choose CC BY 4.0 for open commercial expressive geometry when its scope is suitable;
- choose CC BY-SA 4.0 only if reciprocal licensing is desired and compatible;
- choose CERN-OHL v2 variant for open hardware source;
- use SPDX-compatible software licenses for code;
- state explicitly which assets/marks are excluded.

## Recommended Evidence Stack

### Internal

- source, tool, component, market, and authorship registers;
- terms/license snapshots and contracts;
- prompts/raw AI outputs/C2PA verification;
- CAD/source history and human design log;
- patent/design/trademark searches and counsel references;
- product classification, risk assessment, tests, batch controls;
- insurance/export/tax/EPR evidence;
- manifest hash and signed approvals;
- complaints, corrections, takedowns, incidents and recalls.

### Customer-Facing

- model/print and release ID;
- instructions/limitations/warnings;
- outgoing licenses;
- third-party notices;
- AI disclosure;
- sanitized provenance;
- hashes/signature verification;
- manufacturer/support/incident contact.

## Recommended Watermark

Use:

- owned seller ID or mark;
- compact release ID;
- placement on a low-stress/nonfunctional face;
- 0.4 mm-nozzle starting geometry of roughly 0.6–0.8 mm stroke and 0.4–0.6 mm relief/depth, validated by test print;
- the same release ID in 3MF metadata, provenance.json, SHA256SUMS, listing, invoice/SKU, and batch record.

Avoid a long “AI generated” engraving, OpenAI logo, unearned CE/certification icons, and marks on threads/seals/food-contact/safety surfaces.

## What Requires a Separate License

Likely separate clearance is needed for:

- external photos and underlying depicted subject;
- stock assets and extended merchandise/3D/AI rights;
- people/model/property releases;
- fonts and glyph outlines;
- textures, HDRIs, brushes, materials, SVGs, height maps;
- community/supplier CAD;
- OpenSCAD/CadQuery libraries and scripts;
- FreeCAD/Blender workbenches/add-ons/assets;
- slicer profiles/post-processors;
- AI model weights/services;
- bought-part CAD versus the bought physical part;
- trademarks/characters/brand names;
- standards content;
- contractor/employee contributions;
- marketplace and print-service terms.

The application license for OpenSCAD, CadQuery, FreeCAD, or Blender alone does not clear this list.

## Highest-Risk Misconceptions

- “I bought it, so I can scan/copy it.”
- “The manufacturer provided CAD, so I can include it.”
- “Free download means commercial use.”
- “Royalty-free means unrestricted.”
- “Open source means no obligations.”
- “OpenAI says I own output, so it is copyrightable and exclusive.”
- “Adding 20% makes it original.”
- “A patent search showed nothing, so there is no patent.”
- “A disclaimer eliminates product liability.”
- “CE is a general trust mark.”
- “A watermark proves copyright.”
- “STL metadata survives.”
- “A marketplace approved the listing, so it is legal.”
- “Worldwide shipping can use one country’s rules.”

## Implementation Included in This Skill

- a seven-gate release workflow;
- deep legal/tool/license/product references;
- source, tool, component, authorship, and market templates;
- rights, technical-file, notices, AI disclosure, and license templates;
- project initializer;
- fail-closed audit script;
- SHA-256 release manifest generator;
- 3MF metadata embedder;
- OpenSCAD geometry watermark module;
- unit tests and validation instructions.

## Limits

This work does not provide:

- a legal opinion or representation;
- a patent/design freedom-to-operate opinion;
- a CE/UKCA declaration or certificate;
- laboratory testing;
- product classification for an unspecified object;
- tax, customs, export, sanctions, insurance, or privacy advice for an unspecified transaction;
- a guarantee that a marketplace, court, regulator, or rights holder agrees.

Those outcomes require product facts, target countries, current law/terms, and competent signoff.
