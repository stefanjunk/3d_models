# Single-person responsibility and signing matrix

Document status: `WORKING_DRAFT`  
Governance task: `GOV-001`  
Effective from: 2026-08-24  
Internal employee and managing director: Stefan Junk

## Operating model

`Stefan Junk Holding UG (haftungsbeschränkt)` currently has one employee and one managing director, Stefan Junk. Accordingly, Stefan Junk is both responsible (`R`) for execution and accountable (`A`) for every internal MVP workstream. This matrix documents ownership; it does not turn self-review into independent professional review and does not override the representation rule in the commercial register.

## RACI and approval matrix

| Workstream / decision | Responsible (`R`) | Accountable / internal signer (`A`) | External consultation or independent evidence | Retained approval evidence |
|---|---|---|---|---|
| Corporate/operator profile and launch authorization | Stefan Junk | Stefan Junk, managing director | Current register extract; legal review for public operator wording | Signed/versioned operator profile and launch decision |
| Brand, domains, names and IP risk | Stefan Junk | Stefan Junk | IP counsel when conflicts, filing strategy or material exposure require it | Search record, domain evidence and signed `BRD-001` risk decision |
| Consumer terms, digital licence, privacy and withdrawal | Stefan Junk | Stefan Junk | Qualified legal review before production checkout | Versioned legal package and implementation/E2E evidence |
| Tax, VAT, accounting and payments | Stefan Junk | Stefan Junk | Tax adviser or qualified tax confirmation for treatment/configuration | Tax memo, VAT/country allowlist and payment/accounting configuration |
| Product scope, intended use and claims | Stefan Junk | Stefan Junk | Product/category specialist when regulated or safety-critical | Approved requirements and claims/evidence mapping |
| CAD, source control and deterministic build | Stefan Junk | Stefan Junk | Automated validation and specialist review where risk warrants | Source/revision manifest, build log, validation report and hashes |
| Printing, inspection and physical testing | Stefan Junk | Stefan Junk | Repeatable measurements/tests; independent lab where required | Test plan, raw measurements, photos, material/printer/profile/lot records |
| Rights/provenance and commercial release | Stefan Junk | Stefan Junk | Legal/IP review for unresolved third-party or high-value issues | Source/component/rights registers and signed product release decision |
| Product safety, incidents, recall and takedown | Stefan Junk | Stefan Junk | Qualified safety/legal review for reportable or serious incidents | Risk assessment, incident register, corrective-action and notification record |
| Website, cloud, security and deployment | Stefan Junk | Stefan Junk | Automated CI/security checks; external specialist if risk or capacity warrants | Commit/configuration IDs, test results, backup/restore and deployment approval |
| Privacy operations and data-subject requests | Stefan Junk | Stefan Junk | DPO/adviser only if legally required or voluntarily appointed | Data map, request/breach register, decisions and response evidence |
| Customer support, refunds and complaints | Stefan Junk | Stefan Junk | Legal/payment-provider escalation where necessary | Case register, communications, refunds and resolution evidence |
| Finance, pricing and commercial viability | Stefan Junk | Stefan Junk | Tax/accounting input where applicable | Approved price sheet and unit-economics record |
| Final production launch, rollback and kill switch | Stefan Junk | Stefan Junk | All mandatory external reviews and evidence gates must already be complete | Signed `LAUNCH-001` record with exact legal/config/release versions |

## Signing authority

- Stefan Junk is the sole internal approver and managing director.
- Authority to represent the company externally, including whether Stefan Junk is individually authorized to represent it and whether a § 181 BGB exemption exists, must be copied exactly from the current commercial-register extract. Being the only employee or managing director does not by itself prove that wording.
- No document may name an adviser, counsel, test body or second approver unless that person/body actually performed and documented the review.
- External advisers are consulted reviewers, not internal employees or substitute managing directors. Their approval does not replace Stefan Junk's business decision; Stefan Junk's approval does not replace professional review where the applicable gate requires it.

## Single-person control measures

Because internal separation of duties is unavailable:

- use versioned checklists, immutable hashes and deterministic tests for every release;
- separate preparation and approval in time and record both timestamps;
- require all P0 evidence to be linked before signing rather than relying on memory;
- use external legal, tax, IP, safety or security review for matters needing independent competence;
- retain provider logs and automated negative-path test results for payment, access, deployment and takedown;
- never record `HUMAN_APPROVED` or an external review before the named person has actually approved the exact version.

## Change rule

Update this matrix when an employee, contractor, adviser, delegated signatory or data-protection officer is appointed, or when a workstream changes owner. A contractor or tool does not silently acquire approval authority.
