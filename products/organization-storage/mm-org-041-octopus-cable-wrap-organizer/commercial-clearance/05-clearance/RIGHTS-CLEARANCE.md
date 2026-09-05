# Rights clearance — MM-ORG-041 Octopus cable wrap organizer

Status: **BLOCK for commercial release; TOOL-LICENCE WARN for the active geometry chain**. Release ID `MM-ORG-041-0.2.0`, seller/market scope DE, digital-first. Assessed 2026-09-05 by an agent session; no legal opinion or human release approval.

## Active v0.2.0 chain

- Own reference plate: `../../organic/reference/octopus-preform-plate-001.png`, recorded in `../../evidence/imagegen-record.json`.
- Geometry: `../../organic/raw/step1x/run-005/geometry.raw.glb`, generated with the clean owned fork at commit `4b6da92a56acb3a135b0493703470995c00c5e91`.
- Functional CAD: flat base plus six CAD-owned cable channels, recorded in `../../organic/work/run-005/functionalization-channels-parametric.json`.
- Candidate: `../../result/mm-org-041-octopus-cable-wrap-organizer-v0.2.0.stl`, hash-linked in `../../result/derivation-manifest-v0.2.0.json`.

## Gate decisions

| Gate | Decision | Basis |
|---|---|---|
| Own brief and concept IP | PASS for design | Own text brief and own prompt; no imported model, named character, logo, likeness or trade dress. |
| Step1X code/weights for run-005 | WARN | The run is after independent decoder commit `f00dd46`, after texture deletion `2433849`, and records clean commit `4b6da92`. Step1X code and published weights declare Apache-2.0. Residual warnings are documented in the repository audit. |
| Pre-cutoff / textured artifacts | BLOCK / historical only | Run-002 and any textured artifact remain outside the cleaned geometry-only chain and are not release inputs. |
| Image-generator output terms | BLOCK | Applicable commercial-output terms for the exact workspace route are not fixed in product-local evidence. |
| Functional source and geometry | WARN | CAD ownership and hashes are recorded; mesh and exact-profile slicer checks pass. No physical cable, edge, cycle or stability result exists. |
| Outgoing licence and notices | BLOCK | Customer licence, complete package notices and redistribution scope are not approved. |
| AI transparency and listing | BLOCK | Final disclosure wording, platform AI flags and a real-print photograph do not exist. |
| Seller/market/IP review | BLOCK | Seller identity, marketplace terms, trademark/design search and human/legal review remain open. |
| Human release approval | BLOCK | `../08-approvals/release-approval.json` remains BLOCK. |

## Step1X licence conclusion

The earlier product-specific tooling block is lifted only for run-005 and its derivatives. The active geometry path no longer executes the Hunyuan-derived decoder and the fork no longer contains or serves the texture stage. The exact run manifest records the clean fork commit, one geometry return and the pinned client. This is an engineering/tooling conclusion, not a freedom-to-operate opinion.

Remaining non-tooling warnings include the SKU-specific image-generator rights, upstream Objaverse/Objaverse-XL training provenance, an undeclared licence on the CLIP configuration repository (no CLIP weights are downloaded or redistributed), and disclosure obligations. See `business/06-legal-compliance/generative-tooling-licence-audit.md`.

## Physical and claim boundary

The nominal 4 mm and 6 mm channel families are declared design values, not measured compatibility claims. Commercial wording must not claim retention, jacket safety, edge comfort or stability until the exact-material prototype passes the planned cable-measurement, 2 N retention, 100-cycle jacket and 10-degree stability tests.

Overall decision: **BLOCK**. Continued digital engineering is permitted under the recorded controls; listing or sale is not.
