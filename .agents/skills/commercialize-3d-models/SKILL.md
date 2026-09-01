---
name: commercialize-3d-models
description: Clear, document, license, watermark, and package AI-assisted or conventional 3D-printable designs for commercial distribution as CAD/mesh files, physical prints, or both. Use for STL, 3MF, STEP, OBJ, CAD source, OpenSCAD, CadQuery, FreeCAD, Blender, image-to-relief workflows, imported supplier or library parts, tool and asset license audits, IP/provenance records, EU AI transparency, product safety, consumer terms, export screening, or a commercial-release go/no-go review.
---

# Commercialize 3D Models

## Purpose

Build an evidence-backed commercial release package for a 3D model file, a printed product, or both. Separate contract permission, copyrightability, non-infringement, product compliance, and truthful AI disclosure; none substitutes for another.

Treat this as a structured compliance workflow, not legal advice or a promise of worldwide clearance. Use primary law and current official terms for the seller, target markets, product category, sales channel, and exact tool plan. Escalate regulated, safety-critical, patent-sensitive, disputed, or high-value releases to qualified counsel and testing bodies.

## Register a New Portfolio Product First

Inside the `3d_models` workspace, a new independently managed product must
already have one unique SKU, a correctly categorized
`products/<family>/<lowercase-sku>-<slug>` folder, one canonical
`business/02-portfolio/product-portfolio.csv` row, a regenerated
`product-portfolio.xlsx` row, and a current prospective preflight. Load
`3d-design-preflight` and read its `references/product-intake.md` when any of
those are absent. Do not allocate a separate SKU for a component or generated
preform that belongs to an existing product lifecycle.

Create this skill's evidence workspace inside that product folder at
`commercial-clearance/`. The portfolio `Rights_Provenance` field summarizes
the current state; the source, tool, component, authorship, evidence, and
provenance records here remain authoritative for the detailed license chain.
Explicit `UNKNOWN` keeps the chain truthful but blocks the affected release
gate; portfolio registration never means rights clearance.

## Establish Scope Before Clearance

Collect:

- seller legal entity and country;
- target countries and marketplaces;
- release types: editable/native source, STEP/CAD, mesh/3MF/STL, G-code, printed product, listing renders;
- intended use, users, age group, environment, loading, failure consequences, materials, and bought-in components;
- design history, prompts, generated images, external images/scans, code, assets, models, fonts, textures, plugins, and collaborators;
- desired outgoing rights: proprietary file license, print-selling license, open license, client assignment, or internal manufacture;
- planned release date and whether patent or design registration may matter.

Do not infer missing rights from “free,” “official,” “downloadable,” “royalty-free,” possession of a physical part, or an AI provider assigning output. Mark missing material facts UNKNOWN and block release where they affect a required right or safety duty.

## Create the Evidence Workspace

Run:

    python3 scripts/new_commercial_3d_project.py \
      --name "Product name" \
      --seller-country "DE" \
      --markets "EU,US" \
      --release-type both \
      --output /path/to/clearance

Keep release evidence under version control or an immutable document store with access logs and backups. Do not publish private prompts, receipts, personal data, confidential supplier terms, or legal advice; retain them in the internal evidence area and publish only the release-facing notices.

Use one project ID across:

- source, tool, component, and human-contribution registers;
- rights-clearance and safety records;
- model metadata and geometry mark;
- released files, listing, invoice/SKU, production batch, and customer license;
- checksum manifest and signed approval.

Read [documentation-and-release-system.md](references/documentation-and-release-system.md) for the exact directory, fields, change-control rules, retention periods, and release bundle.

## Build a Rights Graph

Trace every transformation:

    brief/prompt -> source image or scan -> derived height map or profile
    -> CAD code/native model -> imported components -> mesh/3MF/STL
    -> slicer/G-code/print -> render/listing/packaging

For every node, record creator, acquisition date, source URL or contract, immutable local evidence, SHA-256, applicable license or terms version, transformations, outputs containing it, and required permissions. Record rights separately for:

- commercial use;
- modification and derivative works;
- input to an AI service;
- redistribution inside an editable or mesh file;
- manufacture and sale of physical prints;
- sublicensing, attribution, notices, source disclosure, and share-alike;
- patents, registered/unregistered designs, trademarks/trade dress, privacy/publicity, moral rights, database rights, and confidential information.

Never collapse those fields into “licensed: yes.”

## Run the Release Gates

Assign PASS, WARN, BLOCK, or NOT APPLICABLE to every gate. A WARN requires a named owner and written risk acceptance. A BLOCK prevents publication or sale.

### Gate 1 — Input and Contributor Authority

- Verify that each creator, employee, contractor, client, photographer, scanner operator, and contributor assigned or licensed the necessary rights in writing.
- Verify that an external image or photo permits commercial use, adaptation, AI input, and the intended distribution. Clear depicted artwork, branded products, buildings where applicable, identifiable people, property access terms, and privacy/publicity rights separately.
- Preserve the original ChatGPT-generated image with its C2PA metadata and record the exact OpenAI terms/version, account type, prompt, date, human edits, and review. Treat OpenAI’s output assignment as contractual permission between the parties, not a warranty of exclusivity, copyrightability, or non-infringement.
- Do not use an unknown online image, search-result thumbnail, “inspiration” model, fan-art character, logo, or scan as production input without a documented permission or a reviewed legal exception.

Read [licensing-inputs-and-components.md](references/licensing-inputs-and-components.md).

### Gate 2 — Tool, Service, Model, Plugin, and Asset Terms

- Record the exact software version, license, plan/tier, terms effective date, and proof snapshot used at each step.
- Distinguish permission to run a tool commercially from rights in its output.
- Audit bundled sample files, templates, fonts, textures, materials, AI models, add-ons, macros, post-processors, cloud libraries, and render engines independently.
- When adding or upgrading a tool, create a register row and repeat this gate before using it on a release candidate.
- When Step1X-3D is used, register its code, weights and each executed model dependency separately; attach the hashed `step1x-run.json` and runtime profile rather than recording only the provider name.
- Treat personal, educational, trial, maker, community, non-commercial, and marketplace-restricted plans as BLOCK until their commercial rights are confirmed.

Open-source application licenses normally govern distribution or modification of the application, not the model output, but copied program code, libraries, and assets can create notice, source, patent, or reciprocal obligations. Read [toolchain-and-output-licenses.md](references/toolchain-and-output-licenses.md).

### Gate 3 — Imported and Bought-Part Models

- Treat a manufacturer, distributor, standards body, CAD portal, or “official library” model as third-party content.
- Confirm both engineering-reference use and redistribution in the delivered file. Permission to design around or buy a part does not automatically permit redistribution of the supplier’s detailed CAD.
- Prefer a self-made simplified interface envelope containing only dimensions needed for fit when redistribution rights are absent. Do not use simplification to evade design, patent, trade-secret, or database rights.
- For a physical product, confirm that use of the actual part is authorized, genuine, correctly sourced, and compliant for the target use. Retain supplier, part number, revision, datasheet, declarations, lot, invoice, and change notices.
- For a digital release, exclude restricted supplier geometry and provide a link/part number plus an assembly placeholder unless a written redistribution license says otherwise.

### Gate 4 — IP Ownership, Protectability, and Freedom to Operate

Evaluate independently:

- copyright in expressive geometry, source code, documentation, renders, and photos;
- human authorship, selection, arrangement, and modifications where AI contributed;
- patents or utility models covering function or manufacture;
- registered and unregistered designs/design patents covering appearance;
- trademarks, logos, trade dress, character rights, and false endorsement;
- privacy, publicity, portrait, moral, cultural-heritage, and location/property restrictions;
- trade secrets, NDAs, employer/client ownership, grants, and competition terms.

Document human decisions with dated sketches, commits, parameter choices, constraint reasoning, rejected variants, test failures, and manual edits. Do not claim exclusive copyright in purely machine-generated, public-domain, functional, or third-party elements.

Run design, patent, and trademark searches appropriate to each market, but label them “search,” never “freedom-to-operate opinion.” Stop public disclosure before filing if patent, utility-model, or registered-design protection might be valuable. Obtain professional clearance for crowded fields, close copies, safety products, or meaningful revenue exposure.

Read [legal-and-market-baseline.md](references/legal-and-market-baseline.md).

### Gate 5 — License Compatibility and Outgoing Terms

Select licenses per layer:

- geometry/native CAD and meshes;
- scripts and software;
- documentation;
- renders/photos;
- fonts/textures/assets;
- trademarks and product names.

Do not apply one blanket license to rights not owned.

Use a proprietary commercial model license when selling controlled file access or print rights. Have counsel localize the template for consumer law, warranty, liability, governing law, tax, and marketplace rules. Use CC BY 4.0 for open commercial reuse, CC BY-SA 4.0 only when its sharing conditions match the business model, and CERN-OHL v2 variants for open hardware source when appropriate. Reject CC NonCommercial input for a commercial release. Reject adapted CC NoDerivatives input. Evaluate ShareAlike and reciprocal hardware/software obligations before combination.

Generate complete attribution and third-party notices, including title, author, source, license/version/link, copyright notice if supplied, and modification statement. Keep notices with the digital file and physical-product documentation when the source license requires it.

### Gate 6 — AI Provenance, Disclosure, and Watermarking

Classify each AI use as ideation, source-image generation, geometry generation, code generation, editing, rendering, inspection, or documentation. State who performed the engineering review.

For every material AI generation, add a hashed run record to `ai_use.generation_records`. Use `scripts/record_ai_generation.py` to copy and link a Step1X or other provider record without silently filling human-review or clearance fields.

Do not assert that EU law requires a blanket “AI-generated” label on every AI-assisted CAD file or printed object. As of 10 August 2026, EU AI Act Article 50 provider marking addresses synthetic audio, image, video, and text; deployer disclosure is narrower, including deepfakes and certain public-interest text. A mesh is not expressly one of those listed output types. Nonetheless:

- preserve provider-applied provenance on generated source and listing images;
- visibly disclose deepfake or deceptively authentic synthetic imagery where required;
- avoid presenting AI output as wholly human-generated where provider terms prohibit that;
- use a conservative release statement such as “AI-assisted design; human reviewed and engineered” when AI materially influenced the sold design;
- re-check destination-country and marketplace rules at release time.

Apply layered provenance:

1. Add a visible or tactile geometry mark on a nonfunctional, low-stress surface: owned brand or maker ID plus short release/batch ID.
2. Add 3MF metadata for designer, copyright claim, license, release ID, AI role, and manifest URI. Do not rely on STL metadata.
3. Ship a sidecar manifest and SHA-256 checksums; sign the manifest where practicable.
4. Retain original generated images with C2PA/SynthID signals. Expect conversion, screenshots, and metadata stripping to break the link, so record hashes and derivation.
5. Optionally add a tested geometric fingerprint or Data Matrix, but do not call it tamper-proof.

A watermark does not create ownership, cure infringement, satisfy safety labeling, or guarantee provenance. Read [ai-provenance-and-watermarking.md](references/ai-provenance-and-watermarking.md).

### Gate 7 — Digital-Product, Physical-Product, and Market Compliance

For digital file sales, prepare:

- clear file formats, version, compatible tools/printers, units, scale, tolerances, materials, print orientation, supports, known limitations, and prohibited uses;
- customer license, price/tax/VAT treatment, privacy terms, support/update policy, conformity description, and refund/withdrawal flow;
- security review for scripts/macros and export/sanctions screening;
- complaint, takedown, defect-notice, update, and recall-capable customer records.

For physical sales, classify the product before choosing a conformity route. Perform intended-use and foreseeable-misuse risk assessment, verification tests, material/process qualification, inspection, traceability, warnings, manufacturer/importer/responsible-person labeling, online-offer disclosures, packaging/environmental duties, incident handling, and product-liability insurance.

Never add a CE mark “just in case.” Use it only where applicable EU harmonisation legislation requires it and after completing the correct conformity assessment, technical file, and declaration. Stop for product-specific review when the item can be a toy, child-care article, food-contact item, electrical/electronic product, radio device, machine/safety component, PPE, medical device, construction product, vehicle/aviation part, pressure item, load-bearing part, weapon, or other regulated/safety-critical product.

In the EU, treat a commercially supplied digital manufacturing/CAD file as a potentially liability-bearing product under the recast Product Liability Directive for products placed on the market or put into service after 9 December 2026. Treat consumer physical products as subject to the General Product Safety Regulation unless a sector rule displaces or supplements it.

Screen software, technical data, CAD files, destinations, customers, and end uses for export controls and sanctions. Block weapons, defense, aerospace, nuclear, surveillance, controlled dual-use, and sanctioned-market releases until a qualified classification is documented.

Read [product-safety-and-global-sales.md](references/product-safety-and-global-sales.md).

## Audit and Package the Release

Run:

    python3 scripts/audit_commercial_release.py /path/to/clearance \
      --report /path/to/clearance/reports/commercial-release-audit.md

Interpret:

- PASS: automated evidence checks found no blocking omission; this is not legal approval.
- WARN: complete the named review or accept risk through an authorized signatory.
- BLOCK: do not publish, upload, license, manufacture for sale, or ship.

Create hashes after final exports:

    python3 scripts/hash_release.py /path/to/release \
      --output /path/to/clearance/release/SHA256SUMS

Embed nonauthoritative metadata into a copy of a 3MF:

    python3 scripts/embed_3mf_provenance.py input.3mf output.3mf \
      --release-id PRODUCT-2026-001 \
      --designer "Seller legal name" \
      --license-terms "See COMMERCIAL-MODEL-LICENSE.md" \
      --ai-use "AI-assisted; human reviewed and engineered" \
      --manifest-uri "provenance.json"

Then hash and re-audit the final output. Never modify the release after approval without assigning a new release version, regenerating hashes, and repeating affected gates.

After every register, evidence item, final artifact, notice, license, manifest, and technical record is complete, freeze the pre-approval evidence set:

    python3 scripts/hash_release.py /path/to/clearance \
      --output /path/to/clearance/08-approvals/EVIDENCE-SHA256SUMS \
      --exclude 08-approvals \
      --exclude 09-incidents \
      --exclude reports

Record both the displayed evidence-manifest SHA-256 and the provenance.json SHA-256 in release-approval.json, then sign/approve. Approval and later incident/report folders are excluded to avoid circular hashes. Any pre-approval file change invalidates the evidence manifest and requires a new freeze and approval.

## Issue the Release Decision

Produce:

1. an executive decision: PASS, WARN, or BLOCK;
2. a rights graph and dependency/license table;
3. an unresolved-issues list with owner, deadline, and evidence required;
4. a target-market and product-category compliance matrix;
5. the internal evidence index;
6. the customer-facing package: license, notices, AI statement, instructions, warnings, version and contact;
7. a signed release approval naming engineering, IP/legal, safety/compliance, and business approvers as applicable.

State assumptions, source-check date, and limits. Do not say “copyright cleared,” “patent free,” “globally legal,” “safe,” or “compliant” without defining the scope and competent signoff.

## Route to Detailed References

- Read [commercial-3d-research-report.md](references/commercial-3d-research-report.md) for the researched executive conclusions and responsibility map.
- Read [scenario-playbooks.md](references/scenario-playbooks.md) for ChatGPT image-to-relief, external-photo, supplier-CAD, digital-file, and physical-print examples.
- Read [legal-source-register.md](references/legal-source-register.md) before making a current legal claim; open and verify the official source on the release date.
- When Step1X appears in the rights graph, load the sibling `step1x-image-to-3d` commercial/research reference and preserve its exact run/runtime evidence.
- Read [documentation-and-release-system.md](references/documentation-and-release-system.md) whenever creating or auditing records.
- Read only the topic-specific reference needed for the active gate, but always complete all seven gates before commercial release.

## Deterministic validation handoff

Use the sibling `validate-printable-3d-projects` skill to create a hashed technical validation summary for every released CAD, mesh, 3MF, G-code, profile, and inspection artifact. Apply `assets/validation-profile.json`, require fresh reports and named approvals, and include the resulting report hash in the evidence index. Technical `PASS` never replaces this skill's rights, licensing, product-safety, consumer-information, export, or market-specific legal gates; any required `NOT_RUN`, `REVIEW_REQUIRED`, unresolved legal item, or missing approval blocks commercial release.

At project start, read the project autonomy policy before changing artifacts. Record only `AUTO_APPROVED` or `BLOCKED` in the agent ledger and only for stages assigned to the agent. Never write `HUMAN_APPROVED`; IP/legal, safety/compliance, business approval, and commercial release remain in the separate human ledger. Workflow autonomy does not authorize dependency installation, external publication, upload, or printer start.
