# MM-ORG-001 P5 gap analysis

Status: `BLOCK` for P5 commercial release

Evidence check: 2026-08-28

Named internal owner: Stefan Junk

Scope: fixed-revision 3MF digital sale through `metriCreate`, Germany only. Printed `metriMade` fulfillment, self-service configuration and additional countries are outside this P5 decision.

## Current evidence

The active engineering project is `products/organization-storage/mm-org-001-drawerfit-modular/MM-ORG-001-metod-maximera-60`. Revision `0.1.0-draft.1` contains nine modules, the removable comb, connector/comb/drawer coupons and a ten-object 3MF.

A fresh deterministic validation on 2026-08-28 reconfirmed the recorded DRAFT result:

- 37 required digital checks `PASS`;
- exact slicer preflight `REVIEW_REQUIRED`;
- connector and comb physical fit `REVIEW_REQUIRED`;
- exact-drawer fit, 5 kg loaded use and 100 drawer cycles `REVIEW_REQUIRED`.

The 3MF is structurally valid and its ten meshes are watertight, but it is explicitly an assembly/reference package rather than proven customer manufacturing plates. No physical result, current commercial-clearance workspace or signed release package was found.

## Gate-by-gate gap

| Gate | Current state | Evidence still required for P5 |
|---|---|---|
| G0 Scope | `WARN` | Measure and identify the exact target drawer/revision; freeze the customer delivery mode, final release ID/version, intended use, load, supported tools, exclusions and exact compatibility wording. The published accessory envelope is not a real-drawer measurement. |
| G1 Source and rights | `BLOCK` | Create source, tool, component and human-contribution registers; trace the local R1.6 fork and every library/tool/AI contribution; retain applicable licenses/terms; decide design/patent/mark similarity and factual IKEA-system compatibility wording; approve outgoing digital-file rights. The current `THIRD-PARTY-NOTICES.md` calls itself incomplete. |
| G2 Digital manufacturing candidate | `BLOCK` | Slice every manufacturing object with the exact common-220 printer, PETG, nozzle and process profile; retain binary/profile/input/output hashes, material/time/support/bounds evidence and warnings. Freeze a final safe-core customer 3MF that opens and can actually be manufactured in the supported slicer workflow. If physical metriMade branding is enabled, integrate and coupon-test the exact product/version mark; otherwise record the mark as scoped `N/A` for this metriCreate-only release. |
| G3 Physical qualification | `BLOCK` | Record printer, firmware, nozzle, material/color/lot, drying, profile and measuring equipment. Measure the drawer; print the connector sweep, comb gauge/comb and drawer-corner coupon; select clearance without sanding/scaling; test a representative seam and one full prototype; after any correction, print three unchanged final sets and pass dimensions, fit, coplanarity/rocking, 5 kg distributed load, 100 drawer cycles, comb/tool range, appearance and defined misuse checks. |
| G4 Customer and commercial package | `BLOCK` | Complete product risk assessment and customer-visible limitations; final instructions, compatibility/measurement guide, supported printer/process envelope, digital license, update/support policy, notices and AI statement; real photo of the exact final print plus truthful renders/alt text; price/VAT/refund/withdrawal treatment and signed unit economics; Germany market and export/sanctions decision. |
| P5 freeze and approval | `BLOCK` | Create sanitized `provenance.json`, artifact `SHA256SUMS`, hashed technical validation summary and frozen evidence manifest. Record attributable engineering, rights/legal, safety/compliance and business decisions for the exact hashes. Any later geometry/profile/license/warning change creates a new revision or repeats affected gates. |

P5 ends with the signed commercial release package. Publishing it and passing purchase/download/takedown tests are the later P6 staging gate, not prerequisites for calling the package P5.

## Ordered critical path

1. Record the exact drawer measurements and the printer/nozzle/filament/measuring inventory used for evidence.
2. Run the exact slicer preflight and print connector, comb and drawer-corner coupons.
3. Select the process-matched clearance. If it changes from 0.45 mm, revise the source and rebuild every affected artifact and report.
4. Decide the digital-only watermark scope, freeze geometry and test any required marking coupon.
5. Print a representative seam and one full prototype; correct failures through a new revision.
6. Produce three unchanged final sets and execute the physical test matrix.
7. In parallel, build the commercial-clearance registers, legal/license package, safety file, catalog copy/media and economics.
8. Re-run release-profile validation, freeze hashes and obtain the named human approvals.

The immediate next physical action remains the connector sweep, not a full nine-module print.
