# Legacy licence audit — MM-DEC-003 Sunflower Bowl / Tray

Date and research cut-off: 2026-09-05

Decision: **BLOCK all legacy manufacturing geometry**

This is an evidence-based issue-spotting record, not legal advice.

## Finding

The old manufacturing files do not contain an auditable generator run, prompt, model/version, account/plan, applicable terms snapshot, or licence grant. `1.stl` and `2.stl` are dense normalized AI-style meshes committed before the workspace's Step1X cleanup gate. `sunflower_bowl.3mf` records `2.stl` as its source and has blank designer/licence metadata. The legacy OpenSCAD source likewise has no author or licence record. None of their mesh geometry is used in the v0.2.0 Step1X derivative.

The owner later confirmed that a slicer-added `Generic-Disc` in the old 3MF was the intentional real-print foot. Its primitive bounds and transforms resolve to approximately 80 mm diameter × 6 mm thickness. Those numeric facts and the owner's intent are used to regenerate a new independent cylinder; no legacy vertex, face, surface or Boolean result is reused.

The owner's Hunyuan suspicion is materially relevant. If the old meshes were produced with Tencent Hunyuan3D-2 under its current public Community License, the licence defines its territory as worldwide **excluding the European Union, United Kingdom and South Korea**, limits its rights grant and distribution to that territory, and says use or display of outputs outside the territory is unlicensed. Official source: <https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/main/LICENSE>. The product owner and planned market are in Germany/EU. Because the exact Hunyuan product and licence snapshot cannot be established, this is a conditional legal concern rather than a proven model attribution; the missing chain of title alone is already release-blocking.

## Artifact findings

| Artifact | SHA-256 | Finding | v0.2.0 use |
|---|---|---|---|
| `sunflower_bowl/1.stl` | `2a0f66c549a7dbd2526abd9211c78ad9fecd8c6ae4fb656b7324987de5c0f2b8` | 1,328,566 triangles; no embedded provenance or run manifest | excluded |
| `sunflower_bowl/2.stl` | `f1437df2a9966cafcaba793db0cea10770e03cc339db110f57b5d95155a1fa4c` | 1,262,456 triangles; no embedded provenance or run manifest | excluded |
| `sunflower_bowl/sunflower_bowl.3mf` | `9deef6d518a4a612039eb5a29826970b82814122b634d507139db666d579d6af` | source metadata references `2.stl`; licence fields blank; standard 3MF validation fails; `Generic-Disc` dimensions remain factual evidence | geometry excluded; 80 × 6 mm dimension evidence only |
| `sunflower_bowl/sonnenblumen_ablageschale_idee1.scad` | `5e79b3fbb2685c05f81b12bdd6b95dbf64a04352c8914f44e56a50722106dc91` | author and licence unknown | excluded |
| packaged legacy STL | `f93d41cf6d11e5aff96ea9d075aca303a2b3aaa5af3fd146f62cc2b47d71bfdf` | provenance unknown | excluded |

The independent 3MF check is stored at `reports/legacy-3mf-validation-v0.2.0.json`. It reports three required structural failures: missing standard 3D model content declaration and two missing component-object references.

## New-chain replacement

The replacement flower body is derived only from a fresh prompt-bound OpenAI image and a local Step1X-3D run. The foot is a new parametric primitive generated from the owner-confirmed factual dimensions above. Step1X's upstream code repository and Hugging Face model card both declare Apache-2.0: <https://github.com/stepfun-ai/Step1X-3D> and <https://huggingface.co/stepfun-ai/Step1X-3D>. The exact owned-fork commit, container image, model snapshots, input hash, run manifest and raw GLB hash are recorded product-locally.

This improves the chain from **BLOCK/unknown legacy origin** to **WARN/auditable new generation**, not to commercial PASS. Open items include the operative OpenAI account terms, Step1X dependency/training-data review, IP/design searches, seller and market documents, marking, physical qualification and signed human approvals.
