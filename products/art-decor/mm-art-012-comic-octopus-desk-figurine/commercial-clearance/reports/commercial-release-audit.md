# Commercial 3D Release Audit

- Project: /home/stefan/orca/workspaces/3d_models/volute/products/art-decor/mm-art-012-comic-octopus-desk-figurine/commercial-clearance
- Generated: 2026-09-05T15:34:07Z
- Decision: **BLOCK**

> Automated evidence check only. PASS is not legal advice, a freedom-to-operate opinion, a conformity certificate, or proof of product safety.

## Findings

| Severity | Code | Finding |
|---|---|---|
| BLOCK | PRJ-002 | project.json has unresolved seller_country |
| BLOCK | PRJ-003 | project status must be ready_for_release |
| BLOCK | SRC-006 | source row 2 (SRC-0001) status is not cleared: block |
| BLOCK | SRC-007 | source row 2 (SRC-0001) does not document commercial-use permission |
| BLOCK | SRC-008 | source row 2 (SRC-0001) has unresolved derivatives |
| BLOCK | SRC-008 | source row 2 (SRC-0001) has unresolved ai_input |
| BLOCK | SRC-008 | source row 2 (SRC-0001) has unresolved patent_rights |
| BLOCK | SRC-008 | source row 2 (SRC-0001) has unresolved trademark_privacy_publicity |
| BLOCK | SRC-009 | source row 2 (SRC-0001) lacks digital redistribution permission or documented not-applicable decision |
| BLOCK | SRC-010 | source row 2 (SRC-0001) lacks physical-sale permission or documented not-applicable decision |
| BLOCK | TOOL-003 | tool row 2 (TOOL-0001) has unresolved plan |
| BLOCK | TOOL-003 | tool row 2 (TOOL-0001) has unresolved input_confidentiality |
| BLOCK | TOOL-003 | tool row 2 (TOOL-0001) has unresolved output_restrictions |
| BLOCK | TOOL-003 | tool row 2 (TOOL-0001) has unresolved distribution_obligations |
| BLOCK | TOOL-005 | tool row 2 (TOOL-0001) does not document commercial use |
| BLOCK | TOOL-006 | tool row 2 (TOOL-0001) status is not cleared: block |
| PASS | CMP-001 | No imported/bought components declared |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved tax_epr |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved official_source |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved product_safety_framework |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved privacy |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved channel |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved export_sanctions |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved conformity_and_label |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved language |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved consumer_digital_terms |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved effective_date |
| BLOCK | MKT-001 | market row 2 (UNKNOWN) has unresolved market |
| BLOCK | MKT-002 | market row 2 (UNKNOWN) status is not cleared: block |
| BLOCK | MKT-003 | Target market has no cleared country/channel row: UNKNOWN |
| BLOCK | MAN-005 | seller.legal_name is unresolved |
| BLOCK | MAN-005 | seller.country is unresolved |
| BLOCK | MAN-005 | seller.postal_address is unresolved |
| BLOCK | MAN-005 | seller.electronic_address is unresolved |
| BLOCK | MAN-006 | product classification status is not cleared: unknown |
| BLOCK | MAN-007 | product classification text is missing |
| BLOCK | MAN-008 | product classification evidence path is missing or unresolved |
| BLOCK | AI-003 | AI use needs disclosure_text |
| BLOCK | AI-003 | AI use needs human_reviewer |
| BLOCK | AI-004 | AI source-original retention is unresolved |
| BLOCK | AI-005 | AI use needs at least one hashed generation record |
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
| BLOCK | COM-004 | Physical release requires PASS for risk_assessment |
| BLOCK | COM-004 | Physical release requires PASS for test_reports |
| BLOCK | COM-004 | Physical release requires PASS for labels_and_instructions |
| BLOCK | COM-004 | Physical release requires PASS for traceability |
| BLOCK | COM-004 | Physical release requires PASS for technical_file |
| BLOCK | EXP-001 | Export classification is unresolved |
| BLOCK | EXP-002 | Export/sanctions screening is unresolved |
| BLOCK | EXP-003 | export classification evidence path is missing or unresolved |
| BLOCK | DOC-002 | 05-clearance/RIGHTS-CLEARANCE.md still contains placeholder [DETAIL] |
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
| BLOCK | APP-009 | Approver safety_compliance has unresolved name |
| BLOCK | APP-009 | Approver safety_compliance has unresolved authority |
| BLOCK | APP-009 | Approver safety_compliance has unresolved signed_at |
| BLOCK | APP-009 | Approver safety_compliance has unresolved signature_reference |
| BLOCK | APP-010 | Approver safety_compliance decision is not PASS |

## Release Rule

- PASS: automated checks found no required evidence omission; retain competent human approval.
- WARN: resolve or obtain written authorized risk acceptance before release.
- BLOCK: do not publish, upload, sell, manufacture for sale, or ship.
