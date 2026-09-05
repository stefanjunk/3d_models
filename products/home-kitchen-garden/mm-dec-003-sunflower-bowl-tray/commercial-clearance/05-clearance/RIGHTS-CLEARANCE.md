# Rights Clearance — MM-DEC-003 Sunflower Bowl / Tray

Project/release: `fcb2719d-7116-4ebb-9088-0b8f9f0d2a16` / `MM-DEC-003-0.2.0`

Seller: unresolved; country recorded as Germany

Target market: EU; channel unresolved

Review date and research cut-off: 2026-09-05

Overall decision: **BLOCK — no publication, sale, commercial manufacture, shipment, or release**

This document records engineering and licence issue spotting. It is not a freedom-to-operate opinion or legal advice.

## Release scope

The intended future scope is a digital STL/source package and physical prints of a one-piece adult decorative catchall tray for lightweight dry non-food items. The current scope is only an unreleased digital design candidate plus validation evidence. Food contact, watertightness, children, outdoor, structural and liquid-service claims are excluded.

## Legacy chain decision

The legacy `1.stl`, `2.stl`, `sunflower_bowl.3mf`, legacy procedural archive and external models are not release inputs. They lack a generator manifest and adequate author/licence evidence; the old 3MF also fails required structural validation. If the suspected generator was Tencent Hunyuan3D-2, its current public Community License excludes the EU from the licensed territory and states that output use outside that territory is unlicensed. Germany and the planned EU market therefore make that suspected route unacceptable without a separately verified version-specific written licence. Official source: <https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/main/LICENSE>.

The product-level record `../evidence/legacy-license-audit-v0.2.0.md` contains exact hashes and the 3MF findings. Exclusion prevents those files from contaminating the new derivative chain, but does not retrospectively clear them.

## New input and tool chain

The v0.2.0 geometry uses only:

1. two retained OpenAI-generated concept images as appearance direction;
2. one selected prompt-only OpenAI `gpt-image 2.0` input plate with C2PA credentials;
3. one selected untextured geometry run through the local owned Step1X-3D fork (`run-004`);
4. uniform metric registration to 200 mm longest XY;
5. an owner-confirmed parametric 80 × 6 mm disc-foot Boolean and exact-profile Anycubic slicing.

No prior mesh, supplier CAD, external model, font, logo, texture, person, property or bought component is included. The old Anycubic 3MF was consulted only to recover the factual disc dimensions and owner intent; no triangle or surface was copied. Registered copies and hashes are in `01-sources/source-register.csv`.

Step1X's upstream GitHub repository and Hugging Face model card declare Apache-2.0. Official sources: <https://github.com/stepfun-ai/Step1X-3D> and <https://huggingface.co/stepfun-ai/Step1X-3D>. The product used owned-fork commit `4b6da92a56acb3a135b0493703470995c00c5e91`, which passes the required cleanup commit gate. The exact run, container and model snapshots are archived under `02-tools/evidence/`.

The new chain remains WARN rather than PASS because:

- the operative OpenAI account plan and contract/terms snapshot are not established locally;
- the opaque image required rembg/U2Net preprocessing, whose exact model hash is captured but whose complete licence package is not archived;
- Step1X's model/dependency and training-data provenance have not received a competent commercial review;
- Apache-2.0 for code/weights is not a non-infringement warranty for generated output;
- generated forms may be similar to third-party works independently of tool licence.

OpenAI's current Service Terms were checked at <https://openai.com/policies/service-terms/> (page updated 2026-06-12), but the product cannot determine which customer agreement and plan governed this exact image-generation session. Owner verification and a retained snapshot are required.

## Human authorship and AI

The human owner identified the legacy risk, selected a clean Step1X recreation, prohibited repair or parametric reconstruction of the flower body, and authorized only the real-print disc foot as a parametric addition. AI generated the fresh reference and raw organic geometry. Codex authored requirements, uniform registration, the disc generator/Boolean, acceptance criteria, validation scripts and evidence. No person has yet supplied a signed final geometry, IP, safety or business release review. Copyright claims must therefore exclude AI-only expression and functional elements as required by the target jurisdiction.

## IP and market checks

No patent, registered design, trademark, trade-dress, image-similarity or marketplace search has been performed. No counsel freedom-to-operate opinion has been obtained. No people, biometric data, branded characters or third-party marks are visible in the selected design, but that observation is not a search clearance.

EU product classification, GPSR obligations, manufacturer identity and contact, warnings, traceability, online-offer data, consumer digital terms, tax/EPR and export screening remain unassigned. Physical safety evidence is limited to digital topology and slicer checks; rocking, loaded tilt, hand comfort, snagging, material batch and process capability are not tested.

## Outgoing licences and notices

No commercial outgoing licence has been approved. The draft commercial model licence is explicitly inactive. If product source scripts are distributed, third-party software notices and required licence texts must be included. The G-code is machine/profile-specific and must not be marketed as universally safe.

## Gate decision

| Gate | Decision | Evidence or blocker |
|---|---|---|
| Legacy input | BLOCK and excluded | missing chain; conditional Hunyuan EU incompatibility; invalid 3MF |
| New source images | WARN | C2PA and hashes present; governing account terms unresolved |
| Step1X geometry | WARN | Apache-labelled code/weights and exact runtime present; dependency/training-data review open |
| Engineering geometry | PASS for digital draft | one watertight body; 80 × 6 mm disc and protected-region comparison pass; sampled wall check passes |
| Exact slicer | PASS for digital draft | Anycubic 1.3.9.4 warning-free exact-profile supported G-code and parser pass; human layer preview remains open |
| IP/FTO | BLOCK | searches and competent review not performed |
| Physical/compliance | BLOCK | prototype and market qualification not performed |
| Marking | BLOCK | metriMade mark not placed or approved on final geometry |
| Human release approvals | BLOCK | engineering, IP/legal, safety/compliance and business signatures absent |

The overall commercial decision remains **BLOCK**. A later release audit must be based on a marked, physically qualified final geometry with current source/tool evidence, completed market documents and signed approvers.
