# Commercial 3D Release Audit

- Project: /home/stefan/Projekte/3d_models/products/organization-storage/mm-org-041-octopus-cable-wrap-organizer/commercial-clearance
- Generated: 2026-09-05T10:39:34Z
- Decision: **BLOCK**

> Automated evidence check only. PASS is not legal advice, a freedom-to-operate opinion, a conformity certificate, or proof of product safety.

## Findings

| Severity | Code | Finding |
|---|---|---|
| BLOCK | PRJ-003 | project status must be ready_for_release |
| BLOCK | SRC-004 | source row 2 (SRC-0001) needs a 64-character SHA-256 |
| BLOCK | SRC-005 | source row 2 (SRC-0001) license evidence does not exist: business/02-portfolio/research-ideas-additions-3.csv |
| BLOCK | SRC-004 | source row 3 (SRC-0002) original source does not exist: organic/reference/octopus-preform-plate-001.png |
| BLOCK | SRC-005 | source row 3 (SRC-0002) license evidence does not exist: evidence/imagegen-record.json |
| BLOCK | SRC-006 | source row 3 (SRC-0002) status is not cleared: unknown |
| BLOCK | SRC-007 | source row 3 (SRC-0002) does not document commercial-use permission |
| BLOCK | SRC-008 | source row 3 (SRC-0002) has unresolved derivatives |
| BLOCK | SRC-009 | source row 3 (SRC-0002) lacks digital redistribution permission or documented not-applicable decision |
| BLOCK | SRC-004 | source row 4 (SRC-0003) original source does not exist: concept/concept-context-001.png |
| BLOCK | SRC-005 | source row 4 (SRC-0003) license evidence does not exist: evidence/concept-image-record.json |
| BLOCK | SRC-006 | source row 4 (SRC-0003) status is not cleared: unknown |
| BLOCK | SRC-007 | source row 4 (SRC-0003) does not document commercial-use permission |
| BLOCK | SRC-008 | source row 4 (SRC-0003) has unresolved derivatives |
| BLOCK | SRC-008 | source row 4 (SRC-0003) has unresolved ai_input |
| BLOCK | SRC-009 | source row 4 (SRC-0003) lacks digital redistribution permission or documented not-applicable decision |
| BLOCK | TOOL-004 | tool row 2 (TOOL-0001) terms evidence does not exist: business/06-legal-compliance/generative-tooling-licence-audit.md |
| WARN | TOOL-006 | tool row 2 (TOOL-0001) is marked WARN and needs documented acceptance |
| BLOCK | TOOL-004 | tool row 3 (TOOL-0002) terms evidence does not exist: UNVERIFIED - the current ChatGPT plan terms and the Codex CLI terms have not been read into this workspace |
| BLOCK | TOOL-005 | tool row 3 (TOOL-0002) does not document commercial use |
| BLOCK | TOOL-006 | tool row 3 (TOOL-0002) status is not cleared: unknown |
| BLOCK | TOOL-004 | tool row 4 (TOOL-0003) terms evidence does not exist: reports/run-005/ |
| WARN | TOOL-006 | tool row 4 (TOOL-0003) is marked WARN and needs documented acceptance |
| PASS | CMP-001 | No imported/bought components declared |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved market |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved ai_classification |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved channel |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved tax_epr |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved export_sanctions |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved language |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved conformity_and_label |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved owner |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved evidence_path |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved official_source |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved product_classification |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved ip_searches |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved effective_date |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved product_safety_framework |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved release_type |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved consumer_digital_terms |
| BLOCK | MKT-001 | market row 2 (REPLACE) has unresolved privacy |
| BLOCK | MKT-004 | market row 2 (REPLACE) evidence path is missing or unresolved |
| BLOCK | MKT-002 | market row 2 (REPLACE) status is not cleared: unknown |
| BLOCK | MKT-003 | Target market has no cleared country/channel row: DE |
| BLOCK | MAN-001 | provenance.json has unresolved intended_use |
| BLOCK | MAN-002 | project.json and provenance.json disagree on release_id |
| BLOCK | MAN-005 | seller.legal_name is unresolved |
| BLOCK | MAN-005 | seller.postal_address is unresolved |
| BLOCK | MAN-005 | seller.electronic_address is unresolved |
| BLOCK | MAN-006 | product classification status is not cleared: unknown |
| BLOCK | MAN-007 | product classification text is missing |
| BLOCK | MAN-008 | product classification evidence path is missing or unresolved |
| BLOCK | AI-001 | ai_use.used must be yes or no |
| BLOCK | ART-001 | provenance.json has no final artifacts |
| BLOCK | LIC-001 | Geometry outgoing license is unresolved |
| BLOCK | LIC-002 | Outgoing software license is unresolved |
| BLOCK | LIC-002 | Outgoing documentation license is unresolved |
| BLOCK | WM-001 | Watermark/provenance field geometry_mark is unresolved |
| BLOCK | WM-001 | Watermark/provenance field geometry_location is unresolved |
| BLOCK | WM-001 | Watermark/provenance field metadata is unresolved |
| BLOCK | CLR-001 | Clearance copyright_authorship is not PASS or not_applicable |
| BLOCK | CLR-001 | Clearance patent is not PASS or not_applicable |
| BLOCK | CLR-001 | Clearance design is not PASS or not_applicable |
| BLOCK | CLR-001 | Clearance trademark is not PASS or not_applicable |
| BLOCK | CLR-001 | Clearance privacy_publicity is not PASS or not_applicable |
| BLOCK | COM-001 | Compliance risk_assessment is not PASS or not_applicable |
| BLOCK | COM-001 | Compliance test_reports is not PASS or not_applicable |
| BLOCK | COM-001 | Compliance labels_and_instructions is not PASS or not_applicable |
| BLOCK | COM-001 | Compliance consumer_terms is not PASS or not_applicable |
| BLOCK | COM-001 | Compliance traceability is not PASS or not_applicable |
| BLOCK | COM-001 | Compliance technical_file is not PASS or not_applicable |
| BLOCK | EXP-001 | Export classification is unresolved |
| BLOCK | EXP-002 | Export/sanctions screening is unresolved |
| BLOCK | EXP-003 | export classification evidence path is missing or unresolved |
| BLOCK | DOC-002 | 06-engineering/PRODUCT-TECHNICAL-FILE.md still contains placeholder [DETAIL] |
| BLOCK | DOC-002 | 07-release/COMMERCIAL-MODEL-LICENSE.md still contains placeholder [VERSION] |
| BLOCK | DOC-002 | 07-release/THIRD-PARTY-NOTICES.md still contains placeholder [DATE] |
| BLOCK | DOC-002 | 07-release/AI-DISCLOSURE.md still contains placeholder [LEGAL NAME] |
| BLOCK | APP-004 | Approval manifest_sha256 does not match current provenance.json |
| BLOCK | APP-005 | Overall approval decision is not PASS |
| BLOCK | APP-006 | Approval timestamp is unresolved |
| BLOCK | APP-011 | pre-approval evidence manifest does not exist: 08-approvals/EVIDENCE-SHA256SUMS |
| BLOCK | APP-009 | Approver business_owner has unresolved name |
| BLOCK | APP-009 | Approver business_owner has unresolved authority |
| BLOCK | APP-009 | Approver business_owner has unresolved signed_at |
| BLOCK | APP-009 | Approver business_owner has unresolved signature_reference |
| BLOCK | APP-010 | Approver business_owner decision is not PASS |
| BLOCK | APP-009 | Approver engineering has unresolved name |
| BLOCK | APP-009 | Approver engineering has unresolved authority |
| BLOCK | APP-009 | Approver engineering has unresolved signed_at |
| BLOCK | APP-009 | Approver engineering has unresolved signature_reference |
| BLOCK | APP-010 | Approver engineering decision is not PASS |
| BLOCK | APP-009 | Approver ip_legal has unresolved name |
| BLOCK | APP-009 | Approver ip_legal has unresolved authority |
| BLOCK | APP-009 | Approver ip_legal has unresolved signed_at |
| BLOCK | APP-009 | Approver ip_legal has unresolved signature_reference |
| BLOCK | APP-010 | Approver ip_legal decision is not PASS |

## Release Rule

- PASS: automated checks found no required evidence omission; retain competent human approval.
- WARN: resolve or obtain written authorized risk acceptance before release.
- BLOCK: do not publish, upload, sell, manufacture for sale, or ship.
