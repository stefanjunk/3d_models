# Documentation and Release System

Use this record system for every commercial model. It creates a reproducible evidence chain from input to customer artifact.

## Contents

1. Design principles
2. Directory structure
3. Identifiers and versions
4. Mandatory registers
5. Evidence capture
6. Human-authorship trace
7. Engineering and product trace
8. Release manifest
9. Approval and change control
10. Retention and privacy
11. Customer-facing package
12. Incident and takedown trace

## 1. Design Principles

- Make every commercial claim traceable to a source, test, or signed decision.
- Preserve original evidence; never overwrite it with a later terms page or edited image.
- Use stable IDs and SHA-256 hashes to connect records.
- Separate internal confidential evidence from public/customer notices.
- Record UNKNOWN explicitly; absence is not permission.
- Version legal analysis and engineering artifacts together.
- Make approvals attributable to authorized humans.
- Prefer interoperable CSV, JSON, Markdown, PDF/A, and ordinary media/CAD formats over a proprietary compliance database.
- Add SPDX identifiers and relationships when practical.
- Keep machine-generated audit output distinct from legal/engineering approval.

## 2. Directory Structure

The project initializer creates:

    commercial-clearance/
      project.json
      01-sources/
        source-register.csv
        evidence/
      02-tools/
        tool-register.csv
        evidence/
      03-components/
        component-register.csv
        evidence/
      04-authorship/
        human-contribution-log.csv
        prompts/
        versions/
      05-clearance/
        RIGHTS-CLEARANCE.md
        market-matrix.csv
        searches/
        contracts/
      06-engineering/
        PRODUCT-TECHNICAL-FILE.md
        risk-assessment/
        test-reports/
        materials-and-batches/
      07-release/
        artifacts/
        COMMERCIAL-MODEL-LICENSE.md
        THIRD-PARTY-NOTICES.md
        AI-DISCLOSURE.md
        provenance.json
        SHA256SUMS
      08-approvals/
        EVIDENCE-SHA256SUMS
        release-approval.json
      09-incidents/
        complaints/
        corrections/
        recalls/
      reports/

Store proprietary source/native CAD in a controlled engineering repository if needed; put immutable hashes and repository commit/tag references in this workspace.

## 3. Identifiers and Versions

Use:

- project_id: immutable UUID for the product family;
- release_id: human-readable ID, for example ACME-HOOK-2026-001;
- semantic/file version: 1.0.0 for customer artifacts;
- design revision: controlled engineering revision, for example C;
- batch/lot ID: physical-production trace;
- source/tool/component IDs: SRC-0001, TOOL-0001, CMP-0001;
- evidence IDs: EVD-YYYYMMDD-####.

Put release_id in:

- project.json and provenance.json;
- native CAD custom properties and 3MF metadata;
- visible/tactile geometry mark where feasible;
- README/instructions and listing;
- license and notices;
- SKU/invoice;
- print batch and inspection record;
- support/incident records.

Do not reuse a release ID after changing geometry, material, required print process, safety warning, embedded component, license scope, or legal clearance. Cosmetic documentation corrections may use a patch version if traceability remains unambiguous.

## 4. Mandatory Registers

### Source Register

One row per input:

- source_id;
- design_stage;
- title and creator;
- source type;
- URL and original local path;
- SHA-256;
- acquired date;
- exact license expression or LicenseRef;
- license/terms evidence path and effective date;
- commercial_use;
- derivatives;
- ai_input;
- redistribute_digital;
- physical_sale;
- attribution_required and attribution text;
- patent_rights;
- trademark/privacy/publicity status;
- outputs/parts using source;
- reviewer, review date, status, notes.

### Tool Register

One row per application, cloud service, model, add-on, library, asset pack, slicer, or manufacturing service:

- tool_id;
- name, provider, version/build/hash;
- design stage and purpose;
- application/model/asset license;
- account plan;
- terms URL/evidence/effective date;
- commercial_use;
- input/confidentiality restrictions;
- output restrictions;
- plugins/assets/dependencies;
- distribution obligations;
- reviewer, date, status, notes.

### Component Register

One row per bought part, supplier model, imported model, standards-derived part, or open-hardware component:

- component_id;
- name/vendor/part number/revision;
- source URL/file/hash;
- license/evidence;
- embedded in which release artifact;
- redistribution rights;
- physical manufacture/use rights;
- patent/design/trademark review;
- supplier/datasheet/declaration/invoice proof;
- safety rating and change-control source;
- reviewer, date, status, notes.

### Human Contribution Log

One row per material human act:

- timestamp and contributor;
- artifact/commit/file;
- design problem;
- choice or change;
- constraints and alternatives;
- expressive or engineering contribution;
- AI/tool role;
- source IDs affected;
- evidence path;
- reviewer.

Avoid vague rows such as “edited model.” Record “replaced AI-proposed scallop pattern with a manually dimensioned 12-segment asymmetric pattern; selected radii and spacing after three fit tests.”

### Market Matrix

One row per target country/region and channel:

- market/channel;
- release type;
- product classification;
- AI actor/content classification;
- IP searches;
- product/safety framework;
- required conformity/label/representative;
- consumer/digital terms;
- tax/EPR/business registrations;
- privacy;
- export/sanctions;
- language;
- official source/effective date;
- local evidence snapshot path;
- owner/status/notes.

## 5. Evidence Capture

For terms, licenses, and product pages:

- save a PDF or standards-preserving web archive where lawful;
- record official URL, page title, retrieval timestamp, effective date, account/plan, and language;
- hash the saved evidence;
- preserve headers/receipt/order form if relevant;
- redact credentials and unrelated personal data from working copies;
- do not alter the original evidence;
- add a superseding record when terms change.

For files:

- retain the original archive/download;
- hash the archive and each used file;
- preserve internal LICENSE/README/metadata;
- record any repair/conversion and tool/version;
- keep before/after versions.

For verbal permission:

- obtain written confirmation from an authorized rights holder;
- describe exact files, versions, commercial uses, modification, digital redistribution, physical manufacture, sublicensing, territory, duration, attribution, and fees;
- verify signatory identity and authority.

Screenshots alone are weak where a full agreement, signed license, or page archive is available.

## 6. Human-Authorship Trace

Retain:

- dated sketches and requirements;
- prompt history and generated variants;
- reason for selecting/rejecting variants;
- original generated images with metadata;
- source code commits/diffs;
- CAD feature history, constraints, and parameters;
- manually authored profiles and ornament;
- decisions about fit, safety, material, orientation, and tolerances;
- test failures and redesigns;
- before/after comparison of AI output and final result;
- contributor identity and ownership agreement.

The trace serves copyright registration, design ownership, patent inventorship review, quality assurance, and truthful AI disclosure. It must not fabricate human contribution.

## 7. Engineering and Product Trace

For a physical product, record:

- intended use and reasonably foreseeable misuse;
- users and vulnerable users;
- product category and applicable laws/standards;
- design inputs, requirements, and acceptance criteria;
- dimensions, tolerances, interfaces, and material specifications;
- printer, firmware, slicer, profile, nozzle, layer, temperature, orientation, supports, infill/perimeters, post-processing;
- material manufacturer/type/color/lot, storage/drying/reuse;
- bought-part supplier/lot and assembly controls;
- hazards, risk estimates, controls, verification, residual risk, warnings;
- validation plan and test reports with calibrated equipment;
- inspection sampling and nonconformance handling;
- labeling, packaging, online-offer content, instructions and languages;
- declaration/certificates where applicable;
- batch release, complaints, incidents, corrective action, and recall capability.

For a digital file, record the expected production envelope. A customer’s printer variability does not excuse an unsafe or materially misleading file.

## 8. Release Manifest

provenance.json should include:

- schema_version;
- project_id and release_id;
- product name and release date;
- seller identity/contact;
- release types and target markets;
- intended use and prohibited uses;
- product classification;
- AI use: used, roles, providers, hashed generation-record paths, disclosure text, human reviewer;
- source/tool/component register paths and hashes;
- artifact list: path, media type, SHA-256, role, license;
- outgoing licenses by layer;
- attribution/notices path;
- watermark: geometry text/location, 3MF metadata, sidecar, signature;
- legal clearance summary: copyright/authorship, patent, design, trademark, privacy/publicity, export;
- compliance summary: risk assessment, tests, labels, consumer terms, traceability;
- approval record and signature reference;
- supersedes/superseded_by.

Do not place secrets, prompts containing confidential data, personal IDs, receipts, or privileged advice in a customer-facing manifest. Publish a sanitized manifest and retain a linked internal manifest if needed.

## 9. Approval and Change Control

Required approvers depend on risk:

| Role | Decision |
|---|---|
| Design/engineering | Artifact is correct, printable, versioned, and tested |
| IP/legal | Ownership, input licenses, outgoing terms, searches, AI disclosure |
| Safety/compliance | Classification, risk controls, testing, labels, technical file |
| Privacy | People/data/biometrics and releases |
| Export | Classification, end use/user/destination |
| Business owner | Markets, insurance, residual commercial risk, release authorization |

Each approval records:

- name, role, authority;
- release ID and artifact manifest hash;
- SHA-256 of the frozen pre-approval evidence manifest;
- decision PASS/WARN/BLOCK;
- assumptions/exceptions;
- unresolved risk owner/deadline;
- timestamp;
- signature mechanism and verification reference.

Approval is invalid if any artifact changes after the manifest hash. Create a new manifest and repeat affected reviews.

Before approval, generate EVIDENCE-SHA256SUMS over every project file except 08-approvals, 09-incidents, reports, and repository metadata. Record its own SHA-256 in release-approval.json. This binds source originals, terms snapshots, registers, clearance, engineering evidence, customer artifacts, and provenance without creating a circular hash over the approval itself. A later change to any covered file invalidates approval.

Use pull requests or equivalent four-eyes review for changes to:

- source/license rows;
- outgoing license;
- geometry or print parameters;
- product classification;
- warnings/labels;
- market list;
- AI disclosure;
- component supplier/revision;
- audit scripts/templates.

## 10. Retention and Privacy

Use a documented retention schedule by law and product category. Minimum internal policy recommendation:

- EU GPSR technical documentation and traceability: retain at least the statutory 10-year period after market placement, plus any longer sector/product-liability need;
- contracts, licenses, assignments, contributor and source evidence: product life plus limitation/enforcement tail set by counsel;
- patent/design records: through right expiry and dispute tail;
- production batches, tests, complaints, incidents, corrective actions: product life plus safety/liability tail;
- customer and personal data: only as long as a documented lawful purpose requires.

This is not one universal legal period. Product rules, tax law, marketplace rules, warranties, minors, medical products, and local limitation statutes can require different periods.

Protect:

- personal scans, model releases, identity documents;
- confidential CAD/prompts and unpublished inventions;
- supplier terms and legal advice;
- export-controlled technical data;
- customer lists and incident health data.

Apply access control, encryption, backup/restore testing, audit logs, deletion holds, and data minimization. Store public and internal manifests separately.

## 11. Customer-Facing Package

For a digital release, include:

- released model/source files;
- README/instructions with release ID, units, scale, compatibility, material/process envelope, tolerances, orientation/support, known limits, warnings, and contact;
- outgoing geometry/source/software/document licenses;
- THIRD-PARTY-NOTICES.md;
- AI-DISCLOSURE.md;
- sanitized provenance.json;
- SHA256SUMS and signature verification instructions;
- consumer terms/refund/withdrawal confirmation delivered through checkout;
- changelog and support/update policy.

For a physical product, include as applicable:

- product/release/batch identifier;
- manufacturer/importer/responsible-person contact;
- instructions, warnings, disposal, and languages;
- conformity mark and declaration only where lawfully required;
- third-party attribution if required;
- AI-assisted design statement where adopted;
- support/incident contact.

Do not ship the internal legal report, private contracts, or sensitive evidence by default.

## 12. Incident and Takedown Trace

Log:

- timestamp, reporter, channel, product/release/batch;
- complaint, defect, injury, IP allegation, privacy request, platform notice, or regulator contact;
- affected markets/customers/files;
- immediate containment: pause listing, quarantine stock, disable download, notify owner;
- evidence preservation;
- severity and reportability assessment;
- legal/insurer/regulator/marketplace notifications;
- root cause and corrective/preventive action;
- updated files/instructions/labels;
- customer communication and recall;
- closure approval.

Never silently replace a defective or allegedly infringing download. Preserve the old hash, mark it withdrawn, issue a new release ID/version, and notify affected customers when required.
