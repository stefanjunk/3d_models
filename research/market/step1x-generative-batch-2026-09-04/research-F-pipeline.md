# Research F — AI image-to-3D production pipeline (technical + legal reality)

Scope: Step1X-3D based pipeline for metriMade (Germany/EU). Research date 2026-09-04.

**HONESTY NOTE / COVERAGE GAP.** This session verified, on real fetched pages, the
Step1X-3D primary sources, its dependency licences, and the mesh-printability evidence.
Research threads on (a) EU AI Act article text, (b) EU/DE and US copyright guidance,
(c) platform policies (MakerWorld / Printables / Cults3D / Thangs / MyMiniFactory / Etsy),
and (d) the competing-model licence comparison were dispatched but had **not returned before
wrap-up**. Everything in those four areas is therefore marked **UNVERIFIED** below, with no
invented article numbers, dates, quotes or verdicts. Do not put UNVERIFIED items into a
customer-facing document until confirmed on the primary page.

---

## SECTION 1 — SOURCE RECORDS

ID: S98
Category: Primary — official repository (code + licence)
Publisher: StepFun (stepfun-ai) via GitHub
Title: Step1X-3D: Towards High-Fidelity and Controllable Generation of Textured 3D Assets — repository README and LICENSE
Source Date: Latest news entries dated May 13 2025, May 14 2025, May 27 2025, June 9 2025, June 26 2025 (no entry later than June 26 2025)
Checked: 2026-09-04
Evidence Used: README section 8 states verbatim "Step1X-3D is licensed under the Apache License 2.0. You can find the license files in the respective github and HuggingFace repositories."; the repository's single LICENSE file is the complete, unmodified Apache License, Version 2.0, January 2004, with no appended restrictions or additional clauses; README resource table gives 27 GB GPU memory for Geometry-1300m + Texture and 29 GB for Geometry-Label-1300m + Texture, both at "152 seconds" for 50 steps; README abstract states the hybrid VAE-DiT component "produces watertight TSDF representations by employing perceiver-based latent encoding with sharp edge sampling for detail preservation" and the texture module is "SD-XL-based"; README section 7 acknowledgments name FLUX, DINOv2, MV-Adapter, CLAY, Michelangelo, CraftsMan3D, TripoSG, Dora, Hunyuan3D 2.0, FlashVDM, diffusers and HuggingFace, and state verbatim "part codes from Hunyuan 3D 2.0 for texture baker"; the README TODO list still shows "More controllable models" and "ComfyUI" as unchecked.
URL: https://github.com/stepfun-ai/Step1X-3D
Used For: Licence name for the project as a whole; capability claims; hardware/runtime budget; identification of upstream dependencies to audit.

ID: S99
Category: Primary — peer-reviewable preprint (author-stated limitations)
Publisher: arXiv (StepFun authors, 18 listed)
Title: Step1X-3D: Towards High-Fidelity and Controllable Generation of Textured 3D Assets (arXiv:2505.07747)
Source Date: Submitted 12 May 2025
Checked: 2026-09-04
Evidence Used: Section 7 states verbatim "Currently, we convert mesh to TSDF with grid resolution 256³. In future work, we will increase the grid resolution to achieve more accurate geometric details."; Section 7 also states verbatim "For the texture component, our current implementation is limited to albedo generation. We plan to extend this pipeline to support input image relighting and physically based rendering (PBR) material texture generation."; latent set sizes are 512 (first phase) and 2048 (second phase), conditioning uses a "pre-trained DINOv2 large image encoder" at 518×518 concatenated with "CLIP-ViT-L/14", and the texture backbone is "MV-Adapter" fine-tuned from SD-XL; the curated data comprises "320k valid samples from the original Objaverse dataset" plus "an additional 480k from Objaverse-XL" toward a ~2M asset set, with "30K 3D assets" for the multi-view texture model; quantitative evaluation used CLIP-Score, Uni3D-I and OpenShape (SparseConv and PointBERT) over 110 test images.
URL: https://arxiv.org/abs/2505.07747
Used For: The model's own stated limitations (geometry resolution ceiling, albedo-only texture); technical resolution figures; dataset provenance (Objaverse / Objaverse-XL) for IP audit; the fact that no printability or manifold guarantee is claimed.

ID: S100
Category: Primary — official model card and dataset card
Publisher: StepFun (stepfun-ai) via Hugging Face
Title: stepfun-ai/Step1X-3D model card; stepfun-ai/Step1X-3D-obj-data dataset card
Source Date: Model and dataset artefacts published 13–14 May 2025 per repository news
Checked: 2026-09-04
Evidence Used: The model card licence tag reads "apache-2.0"; no gated access, click-through agreement or usage restriction is presented on the card, and the card contains no explicit statement about commercial use either permitting or restricting it; variants listed are Step1X-3D-Geometry-1300m, Step1X-3D-Geometry-Label-1300m and Step1X-3D-Texture; the card repeats the "Watertight TSDF representations" and "Cross-view consistency through geometric conditioning" claims and states support for multiple aesthetic styles; the dataset card for Step1X-3D-obj-data states licence "Apache 2.0" and describes itself as "the training subdataset for Step1X-3D" but gives **no** statement about the per-asset licences of the underlying Objaverse / Objaverse-XL source assets — that gap is unresolved and is a live IP question.
URL: https://huggingface.co/stepfun-ai/Step1X-3D
Used For: Confirming the declared weights licence is Apache-2.0 and not a bespoke community licence; confirming no gate/EULA; documenting the unresolved training-data provenance gap.

ID: S101
Category: Primary — source-code evidence inside the Step1X-3D repository
Publisher: stepfun-ai / Step1X-3D repository (files inspected directly via raw.githubusercontent.com and GitHub code search)
Title: Step1X-3D source files carrying Tencent Hunyuan non-commercial licence headers
Source Date: Files present on branch `main` as fetched 2026-09-04
Checked: 2026-09-04
Evidence Used: GitHub code search for the exact string "TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT" restricted to repo stepfun-ai/Step1X-3D returns total_count 12; eleven of those files are under `step1x3d_texture/` (differentiable_renderer/{__init__,mesh_utils,setup,camera_utils,mesh_processor,mesh_render}.py and custom_rasterizer/{render,io_obj,io_glb,__init__}.py plus custom_rasterizer/lib/custom_rasterizer_kernel/__init__.py) and the twelfth is `step1x3d_geometry/models/autoencoders/volume_decoders.py`, i.e. in the **geometry** path, not only the texture path; each such file opens with the verbatim header "# Hunyuan 3D is licensed under the TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT" followed by "# For avoidance of doubts, Hunyuan 3D means the large language models and their software and algorithms, including trained model weights, parameters ... made publicly available by Tencent in accordance with TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT."; `step1x3d_geometry/models/autoencoders/michelangelo_autoencoder.py` line 23 reads `from .volume_decoders import HierarchicalVolumeDecoder, VanillaVolumeDecoder` and lines 581-584 instantiate `HierarchicalVolumeDecoder()` or `VanillaVolumeDecoder()`, so the geometry-only inference path executes the Hunyuan-headed file; the identical header appears in the upstream Tencent-Hunyuan/Hunyuan3D-2 file `hy3dgen/texgen/differentiable_renderer/mesh_render.py`, confirming the header travelled with copied code rather than being an error.
URL: https://github.com/stepfun-ai/Step1X-3D/blob/main/step1x3d_geometry/models/autoencoders/volume_decoders.py
Used For: Establishing that Step1X-3D's blanket Apache-2.0 claim conflicts with retained per-file Tencent headers, and that the conflict reaches the geometry pipeline as well as the texture pipeline. This is the single most commercially significant finding in this research.

ID: S102
Category: Primary — licence agreement text of an upstream dependency
Publisher: Tencent
Title: TENCENT HUNYUAN 3D 2.0 COMMUNITY LICENSE AGREEMENT (LICENSE file of Tencent-Hunyuan/Hunyuan3D-2)
Source Date: Header states "Tencent Hunyuan 3D 2.0 Release Date: January 21, 2025"; Exhibit A Acceptable Use Policy "Last modified: November 5, 2024"
Checked: 2026-09-04
Evidence Used: The agreement's third line states verbatim "THIS LICENSE AGREEMENT DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA AND IS EXPRESSLY LIMITED TO THE TERRITORY, AS DEFINED BELOW."; clause 1(l) defines verbatim "'Territory' shall mean the worldwide territory, excluding the territory of the European Union, United Kingdom and South Korea."; clause 5(c) states verbatim "You must not use, reproduce, modify, distribute, or display the Tencent Hunyuan 3D 2.0 Works, Output or results of the Tencent Hunyuan 3D 2.0 Works outside the Territory. Any such use outside the Territory is unlicensed and unauthorized under this Agreement."; clause 4 imposes a separate written licence requirement above "1 million monthly active users"; clause 6(d) states verbatim "Tencent claims no rights in Outputs You generate. You and Your users are solely responsible for Outputs and their subsequent uses."; clause 3(d) requires a Notice file reading "Tencent Hunyuan 3D 2.0 is licensed under the Tencent Hunyuan 3D 2.0 Community License Agreement, Copyright © 2025 Tencent. All Rights Reserved."; clause 9 sets governing law and exclusive jurisdiction as Hong Kong SAR.
URL: https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/main/LICENSE
Used For: Quantifying the EU-specific risk created by S101; also serves as the licence record for Hunyuan3D 2.0 as a *competing* model — it is expressly unusable by an EU business under its own terms.

ID: S103
Category: Primary — licence texts of further upstream base models
Publisher: Stability AI (via Hugging Face); Black Forest Labs (via Hugging Face)
Title: CreativeML Open RAIL++-M License (stable-diffusion-xl-base-1.0); FLUX.1 [dev] Non-Commercial License (FLUX.1-dev)
Source Date: SDXL licence self-dated "dated July 26, 2023"; FLUX.1-dev licence undated on the card as read
Checked: 2026-09-04
Evidence Used: The SDXL base 1.0 licence file is titled "CreativeML Open RAIL++-M License dated July 26, 2023" and grants "a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license" subject to Attachment A use-based restrictions (unlawful use, harming minors, disinformation, harassment/defamation, discrimination, medical advice, law-enforcement decisioning and similar); paragraph 5 states verbatim "You shall require all of Your users who use the Model or a Derivative of the Model to comply with the terms of this paragraph (paragraph 5)." and the use-based restrictions "MUST be included as an enforceable provision" in any downstream distribution agreement — this flows through to metriMade because Step1X-3D's texture module is SD-XL based (S99); the FLUX.1-dev model card names the licence "FLUX.1 [dev] Non-Commercial License" and states "Generated outputs can be used for personal, scientific, and commercial purposes as described in the FLUX.1 [dev] Non-Commercial License"; however Step1X-3D's `step1x3d_geometry/models/transformers/flux_transformer_1d.py` opens with "# Some parts of this file are adapted from Hugging Face Diffusers library." and imports only from `diffusers`, so FLUX appears in Step1X-3D as an architecture name and acknowledgement, not as loaded FLUX weights — the FLUX non-commercial licence therefore does **not** appear to attach.
URL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/LICENSE.md
Used For: Establishing the RAIL++-M use-restriction pass-through duty that must appear in metriMade's own terms; clearing FLUX as a false-positive risk.

ID: S104
Category: Primary — printer-manufacturer design guidance (platform guidance)
Publisher: Prusa Research
Title: Modeling with 3D printing in mind (Prusa Knowledge Base)
Source Date: No last-updated date displayed on the page as read
Checked: 2026-09-04
Evidence Used: For a standard 0.4 mm nozzle the page gives 1 perimeter = 0.45 mm, 2 perimeters = 0.9 mm, 3 perimeters = 1.35 mm and states verbatim "Walls thinner than one nozzle perimeter are not printable."; on topology it states models must be "solid or have 'manifold geometry'" and verbatim "If a model has holes on the surface or internal geometry, the part will not be able to be sliced."; on overhangs it states verbatim "A 3D printer can cleanly print overhanging structures with an angle between 45 and 60 degrees", with MK4S / CORE One / CORE One L using the Nextruder and 360° cooling reaching "overhangs of up to 75° without supports"; for moving assemblies it gives "An initial good measurement for movable parts is at least 0.3 mm"; it notes PC, ASA and PETG "may not print small details as well as PLA".
URL: https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
Used For: Hard, citable numeric thresholds for the mesh-quality gate (minimum wall, overhang, clearance) and the manifold/no-holes requirement as a slicing precondition.

ID: S105
Category: Primary — academic literature on printability and generated-mesh fabricability
Publisher: arXiv
Title: Evaluating the printability of stl files with ML (arXiv:2509.12392); related: From Prompts to Printable Models: Support-Effective 3D Generation via Offset Direct Preference Optimization (arXiv:2511.16434); As-exact-as-possible repair of unprintable STL files (arXiv:1605.07829)
Source Date: 2509.12392 submitted 15 September 2025 (Henn, Hauptmannl, Gardi); 2511.16434 v1 20 November 2025, v2 26 February 2026 (Wu, Li, Dai); 1605.07829 submitted 25 May 2016, published Rapid Prototyping Journal 2018 (Attene)
Checked: 2026-09-04
Evidence Used: arXiv:2509.12392 aims to "assist less experienced users by identifying features that are likely to cause print failures due to difficult to print geometries before printing even begins" and names as failure-causing features "severe overhangs", "inadequate bed adhesion", "warping", "structural fragility" and "fine structures" smaller than the nozzle diameter (typically 0.4 mm), with an overhang threshold around 45°; its dataset was only "approximately 150 3D models" from Printables.com with ~20 held for validation, and the authors concede the model "remains far from optimal" and that "full generalization remains unlikely" because severity depends on material, printer configuration and intended application — so automated printability scoring is not a substitute for a human gate; arXiv:2511.16434 states verbatim "Current text-to-3D models prioritize visual fidelity but often neglect physical fabricability, resulting in geometries requiring excessive support structures." (note: text-to-3D, not image-to-3D — treat as adjacent evidence, and the abstract gives no quantified failure rate); arXiv:1605.07829 addresses "all the possible triangle configurations" and distinguishes "triangles that bound solid parts and triangles that constitute zero-thickness sheets", i.e. the solid-vs-sheet (hollow/solid) ambiguity is a recognised, published defect class in STL repair.
URL: https://arxiv.org/abs/2509.12392
Used For: Academic backing that generative 3D output is optimised for appearance rather than fabricability; the named failure-feature list; the caveat that automated printability classifiers are immature, which justifies a mandatory human-reviewed gate rather than a purely automatic one.

ID: S106
Category: Vendor documentation (SECONDARY as general evidence; primary for that vendor's product)
Publisher: Meshy AI
Title: 3D Printing Workflow: From AI Model to Print (docs.meshy.ai)
Source Date: No date displayed on the page as read
Checked: 2026-09-04
Evidence Used: The page documents, as the standard problem set for AI-generated meshes, "Mesh has open edges/overlapping faces" causing the slicer to report non-manifold errors; it gives per-process minimum wall thickness of "FDM 1.2 mm", "SLA/DLP 0.5 mm" and "SLS 0.8 mm"; it names "Connection points too thin" as a breakage cause with the fix "Thicken connection areas in a DCC tool"; it names "Base too thin or poor bed adhesion" as a warping cause with a figurine base minimum of "~3mm thick"; it warns users to "Confirm model dimensions before export (Meshy uses cm as the unit)", i.e. generated assets arrive without trustworthy real-world scale; its built-in "Check & Repair" function is described as fixing "non-manifold edges, degenerate faces, holes and open boundaries".
URL: https://docs.meshy.ai/en/webapp/guides/use-cases/3d-printing
Used For: A commercial image-to-3D vendor's own admission of the defect classes and the unit/scale trap; corroborates the mesh-quality gate list from an industry side. Mark as vendor material, not independent.

### Sources NOT obtained in this session (declare as gaps, do not cite)
- EU AI Act Regulation (EU) 2024/1689 article text on EUR-Lex — **UNVERIFIED**, not fetched.
- US Copyright Office guidance and Part 2 Copyrightability report — **UNVERIFIED**, not fetched.
- German/EU copyright authority on AI output (UrhG, CJEU originality standard) — **UNVERIFIED**, not fetched.
- MakerWorld, Printables, Cults3D, Thangs, MyMiniFactory, Etsy policy pages — **UNVERIFIED**, not fetched.
- TRELLIS, TripoSR/Tripo, Rodin/Hyper3D, Meshy, Sparc3D, PartCrafter licences and 2026 state-of-the-art ranking — **UNVERIFIED**, not fetched (Hunyuan3D 2.0 is the one competitor whose licence *was* read: see S102).
- arXiv:2605.09606 "On the Generation and Mitigation of Harmful Geometry in Image-to-3D Models" appeared in a search result listing only; the page was **not fetched** — **UNVERIFIED**, do not cite.
- MV-Adapter licence reported as Apache-2.0 by a search-result summary only; the LICENSE file was **not read** — **UNVERIFIED**.

---

## SECTION 2 — STEP1X-3D FACTS

**Licence name (as declared)**
- Declared licence for code and weights is the **Apache License, Version 2.0** — README section 8 verbatim: "Step1X-3D is licensed under the Apache License 2.0." [S98]
- The repository LICENSE file is the complete, unmodified Apache-2.0 text with no appended clauses, no field-of-use limit and no non-commercial rider. [S98]
- The Hugging Face model card carries licence tag `apache-2.0`, with no gate, no click-through EULA and no commercial-use statement either way. [S100]
- The training subdataset `stepfun-ai/Step1X-3D-obj-data` also declares Apache 2.0. [S100]

**Commercial-use verdict**
- **On its face: YES, commercial use is permitted.** Apache-2.0 permits commercial use, modification and redistribution subject to notice/attribution and the NOTICE/state-changes conditions; there is no non-commercial clause anywhere in the top-level licence or model card. [S98][S100]
- **But: QUALIFIED — a real, documented licence conflict exists inside the repository.** Twelve source files retain the verbatim header "# Hunyuan 3D is licensed under the TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT". Eleven are in the texture pipeline; the twelfth, `step1x3d_geometry/models/autoencoders/volume_decoders.py`, is in the **geometry** pipeline and is imported and instantiated by `michelangelo_autoencoder.py` (line 23; instantiated at lines 581-584), so the geometry-only path also executes Hunyuan-derived code. [S101]
- **EU-specific aggravation.** The upstream Tencent licence for that code states verbatim "THIS LICENSE AGREEMENT DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA", defines "Territory" as "the worldwide territory, excluding the territory of the European Union, United Kingdom and South Korea", and in clause 5(c) prohibits use "or display [of] the Tencent Hunyuan 3D 2.0 Works, **Output or results**" outside that Territory, declaring such use "unlicensed and unauthorized". A German company is squarely outside the Territory. [S102]
- **Net verdict for metriMade: DO NOT treat Step1X-3D as clean Apache-2.0 for EU commercial use until this is resolved.** Concretely: (a) get written clarification from StepFun that the Hunyuan headers are stale and the files are theirs / relicensed, or (b) replace the twelve files with clean-room or independently licensed equivalents (the geometry blocker is one file — a volume decoder — which is replaceable), or (c) take legal advice on whether the copied portions are protectable expression at all. Not resolvable from public sources alone. [S101][S102]
- **Pass-through duty from SD-XL.** Because the texture module is SD-XL based [S99], the CreativeML Open RAIL++-M use-based restrictions apply and paragraph 5 obliges us to require our own users to comply and to include those restrictions "as an enforceable provision" in our downstream terms. This is a commercial-use *condition*, not a prohibition. [S103]
- **FLUX is a false alarm.** FLUX is only acknowledged; `flux_transformer_1d.py` is adapted from Hugging Face Diffusers and loads no FLUX weights, so the FLUX.1 [dev] Non-Commercial License does not appear to attach. [S103]
- **Unresolved: training-data provenance.** The data derives from Objaverse (320k) and Objaverse-XL (480k) [S99], whose assets carry heterogeneous per-asset licences; neither the dataset card nor the paper states how per-asset licence terms were handled. Treat as an open IP question, **UNVERIFIED**. [S99][S100]

**Documented capabilities**
- Two-stage architecture: hybrid VAE-DiT geometry generator plus an SD-XL-based texture synthesis module. [S98][S99]
- Geometry output is described as "watertight TSDF representations", produced with perceiver-based latent encoding and sharp-edge sampling for detail preservation. [S98][S99][S100]
- Three released variants: Step1X-3D-Geometry-1300m, Step1X-3D-Geometry-Label-1300m (accepts control labels such as `{"symmetry": "x", "edge_type": "sharp"}`), and Step1X-3D-Texture. [S100]
- Conditioning: DINOv2-large image encoder at 518×518 concatenated with CLIP-ViT-L/14. Latent set sizes 512 then 2048. [S99]
- Export format in the official `inference.py` is GLB. Mesh extraction is marching cubes via scikit-image `measure.marching_cubes(..., method="lewiner")`, with a dual-marching-cubes alternative available. [S98]
- Pipeline defaults read from `step1x3d_geometry/models/pipelines/pipeline.py`: `bounds = 1.05`, `mc_level = 0.0`, `octree_resolution = 384`. Note the signature default is 384 while the docstring says "defaults to 256" — an internal inconsistency; do not rely on the docstring. [S98]
- Official post-processing helpers ship with the repo: `remove_degenerate_face()` (pymeshlab round-trip) and `reduce_face(mesh, max_facenum=50000)` using pymeshlab `meshing_decimation_quadric_edge_collapse` with `preserveboundary=True`, `preservenormal=True`, `preservetopology=True`, `autoclean=True`. The label example calls the pipeline with `max_facenum=400000`. [S98]
- Runtime/hardware: 27 GB GPU memory for Geometry-1300m + Texture, 29 GB for Geometry-Label-1300m + Texture, both "152 seconds" at 50 steps; Python 3.10, CUDA 12.4, PyTorch 2.5.1, plus pytorch3d and kaolin 0.17.0. [S98]
- Texture generation supports cross-view consistency via geometric conditioning and latent-space synchronisation; 2D control techniques such as LoRA are claimed to transfer to 3D. [S98][S99]

**Documented limits**
- **Geometry resolution ceiling, author-stated:** "Currently, we convert mesh to TSDF with grid resolution 256³. In future work, we will increase the grid resolution to achieve more accurate geometric details." Fine detail and crisp functional edges are therefore resolution-bound by design. [S99]
- **Texture is albedo only, author-stated:** "For the texture component, our current implementation is limited to albedo generation. We plan to extend this pipeline to support input image relighting and physically based rendering (PBR) material texture generation." No PBR/roughness/metallic maps. [S99]
- **No metric scale.** The generator works inside a normalised cube with `bounds = 1.05`; nothing in the pipeline establishes real-world units. Every output must be scaled deliberately in CAD. [S98] Corroborated by the equivalent vendor warning "Confirm model dimensions before export". [S106]
- **Degenerate geometry is expected, by the authors' own workflow.** The official `inference.py` calls `remove_degenerate_face()` before texturing and offers `reduce_face()` decimation — i.e. the reference pipeline itself assumes degenerate faces and excessive face counts occur. [S98]
- **"Watertight" is a claim about the TSDF representation, not a printability guarantee.** Neither the README, the model card nor the paper claims manifoldness, absence of self-intersection, minimum wall thickness, freedom from floaters, or printability. No printability benchmark is reported; evaluation is image-alignment only (CLIP-Score, Uni3D-I, OpenShape) over 110 test images. [S98][S99][S100]
- **Training-data ceiling and heterogeneity** acknowledged in the paper's framing of data scarcity; curated set built from Objaverse/Objaverse-XL whose web-sourced provenance yields quality heterogeneity. [S99]
- **Project appears dormant.** No news entry, release or roadmap tick later than 26 June 2025 was found on the repository as checked 2026-09-04; the "More controllable models" and "ComfyUI" TODOs remain unchecked. Plan for no upstream fixes. [S98]
- **Typical failure modes specific to Step1X-3D (e.g. floaters, texture-sync artefacts):** the issue tracker contains items whose titles indicate such reports, but the issue bodies were **not** read in this session — **UNVERIFIED**, do not cite.

---

## SECTION 3 — LEGAL DUTIES CHECKLIST

Applicable-date column is only filled where a date was read on a real page. Anything else is UNVERIFIED and must be confirmed before it goes into terms of sale.

**A. Upstream licence duties — VERIFIED**

1. **Ship Apache-2.0 attribution with any redistributed Step1X-3D code or derivative.** Keep the LICENSE text, retain copyright/attribution notices, and mark modified files as changed. Applicable now, as a condition of using the software at all. [S98]
2. **Resolve the Tencent Hunyuan header conflict before the first EU commercial sale.** Twelve files in Step1X-3D carry a "TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT" header, including one in the geometry path that is actually imported and executed. Options: written clarification from StepFun, replacement of the affected files, or legal advice. Applicable now; blocking. [S101]
3. **Treat Hunyuan3D-2-derived code and its outputs as unlicensed in the EU.** Clause 5(c) prohibits use or display of the Works "Output or results" outside the Territory, and the Territory expressly excludes the European Union. Licence release date 21 January 2025; Acceptable Use Policy last modified 5 November 2024. Applicable now. [S102]
4. **Carry the CreativeML Open RAIL++-M use-based restrictions into metriMade's own customer terms as an enforceable provision, and require customers to comply.** Paragraph 5 of the licence dated 26 July 2023 makes this mandatory because Step1X-3D's texture module is SD-XL based. Applicable now. Practical wording: a short "Prohibited Uses" clause mirroring Attachment A (no unlawful use, no harming minors, no disinformation, no harassment/defamation, no discriminatory application, no medical advice, no law-enforcement decisioning) plus a flow-down obligation on resellers. [S103][S99]
5. **Do not rely on the image generator's own output-ownership terms without reading them.** If FLUX.1-dev or any non-commercial-licensed image model is used for step (1) of the pipeline, its own model licence governs; the FLUX.1-dev card states outputs may be used commercially "as described in the FLUX.1 [dev] Non-Commercial License", which is an output permission wrapped inside a non-commercial *model* licence — read the licence before relying on it. Applicable per-tool. [S103]
6. **Record provenance per SKU.** Because the training data derives from Objaverse (320k) and Objaverse-XL (480k) with heterogeneous per-asset licences and no published per-asset licence handling, keep a per-product record of input image, model version, seed, and the human CAD work performed. This is the evidence base for both an IP challenge and an authorship claim. Applicable now as internal practice. [S99][S100]

**B. EU AI Act transparency duty — UNVERIFIED, MUST BE CONFIRMED**

7. **UNVERIFIED.** Regulation (EU) 2024/1689 was not fetched in this session. The commonly cited provision for marking generative-AI output is Article 50, and the commonly cited application date for the transparency chapter is 2 August 2026 — **neither was read on EUR-Lex here, so neither is asserted as fact.** Also unconfirmed: whether metriMade is a "provider" or a "deployer" under Article 3, whether a seller of AI-derived 3D files falls inside Article 50 at all, whether the machine-readable-marking duty (commonly cited as Art. 50(2)) binds the model provider rather than us, and whether any 2025/2026 amendment or "Digital Omnibus" instrument has changed the timeline. **Action: fetch https://eur-lex.europa.eu/eli/reg/2024/1689/oj and the Commission AI Act pages and confirm article numbers, the exact duty text, and the applicable date before drafting any disclosure.** Do not publish a compliance statement citing an article number until this is done. [no source]
8. **Interim safe practice, independent of the unresolved article question:** disclose AI involvement plainly on the product page and in the file package (e.g. "Geometry initially generated with an AI image-to-3D model, then repaired, re-engineered and validated by a human designer"). This is defensible under consumer-information and unfair-commercial-practices principles regardless of how Article 50 resolves, and it also satisfies platform labelling expectations. Applicable now as prudence, not as a cited legal duty. [no source]

**C. Copyright and licensing of the files we sell — UNVERIFIED**

9. **UNVERIFIED.** No copyright-office or court source was fetched in this session. Not asserted here: the US Copyright Office position on purely AI-generated versus human-modified output, the 2023 registration guidance, the Part 2 Copyrightability report, Thaler v. Perlmutter, the German § 2(2) UrhG "persönliche geistige Schöpfung" threshold, or the CJEU "own intellectual creation" standard. **Action: fetch copyright.gov's AI guidance and the German UrhG text before writing any ownership clause.** [no source]
10. **Structurally safe drafting stance (reasoning, not a cited source):** do not build the offer on an assumed copyright in the raw AI mesh. Sell a **licence to use the delivered file package** grounded in (a) contract, (b) whatever copyright subsists in the *human* CAD work — the repair, the functional geometry, the tolerances, the assembly, the documentation, and (c) the compilation/database and know-how. State expressly that the human engineering work is the protected subject matter, keep the AI-origin disclosure consistent with clause 8, and avoid asserting exclusive rights over the underlying generated shape. Confirm with counsel once clause 9 is verified. [no source]

**D. Platform and marketplace labelling — UNVERIFIED**

11. **UNVERIFIED.** No platform policy page (MakerWorld, Printables, Cults3D, Thangs, MyMiniFactory, Etsy) was fetched in this session. Policies on AI-generated 3D models differ materially between these platforms and have changed repeatedly, and several run monetisation/boost programmes with separate eligibility rules for AI content. **Action: read each platform's own current terms and community guidelines and record the verbatim clause plus its last-updated date before the first upload. Assume per-platform divergence and assume an AI-origin label is required unless the platform's own text says otherwise.** [no source]

---

## SECTION 4 — MESH-QUALITY GATE

Each line is written to be reusable verbatim as a verification-plan sentence in a spreadsheet. Source ID in brackets; "[no source]" means the check is engineering practice justified by the adjacent cited items, not a quoted requirement.

1. **Manifold/topology check** — Verify the mesh is manifold with no holes or open boundaries, because a model with surface holes or stray internal geometry cannot be sliced at all. [S104]
2. **Degenerate-face check** — Verify zero degenerate (zero-area) faces remain, because the official Step1X-3D inference script itself runs `remove_degenerate_face()` before texturing, and vendor repair tooling lists degenerate faces as a standard defect class of AI-generated meshes. [S98][S106]
3. **Open-edge / overlapping-face check** — Verify there are no open edges or overlapping faces, because these are the specific conditions that make a slicer report non-manifold errors on AI-generated meshes. [S106]
4. **Self-intersection check** — Verify the mesh has no self-intersections before any boolean or hollowing operation, because self-intersection is a recognised defect class in the STL-repair literature and breaks downstream solid operations. [S105]
5. **Minimum wall thickness — FDM** — Verify every wall is at least 3 extrusion perimeters (1.35 mm at a 0.4 mm nozzle) for load-bearing surfaces and never below one perimeter (0.45 mm), because walls thinner than one nozzle perimeter are not printable. [S104] Cross-check against the vendor-stated per-process minima of FDM 1.2 mm, SLA/DLP 0.5 mm, SLS 0.8 mm. [S106]
6. **Thin-protrusion and connection-point check** — Verify no protrusion, spike, fin, antenna or joining neck is thinner than the nozzle diameter (typically 0.4 mm), and thicken every load-carrying connection point, because sub-nozzle "fine structures" and thin connection points are documented print-failure and breakage causes. [S105][S106]
7. **Overhang and support audit** — Verify every unsupported overhang is within 45–60° of vertical for a standard machine (up to 75° only on a Nextruder/360°-cooling machine), and record where supports are required, because generated geometry is optimised for visual fidelity rather than fabricability and tends to demand excessive support. [S104][S105]
8. **Floater / disconnected-shell check** — Verify the mesh contains exactly the intended number of connected components and no detached floating fragments, because marching-cubes extraction from a generated TSDF volume can leave isolated shells that print as loose debris. [no source — Step1X-3D issue bodies UNVERIFIED; keep the check, drop the citation]
9. **Solid-versus-sheet (hollow/solid) resolution** — Verify every region is unambiguously either a bounded solid or an intentional shelled volume with a stated wall thickness, and eliminate zero-thickness sheets, because STL repair literature treats the distinction between triangles bounding solid parts and triangles forming zero-thickness sheets as a core defect class. [S105]
10. **Real-world scale assignment** — Verify the model has been explicitly scaled to its target dimensions in millimetres against a dimensioned drawing, because Step1X-3D generates inside a normalised cube (`bounds = 1.05`) with no metric units and vendor tooling likewise warns to confirm dimensions before export. [S98][S106]
11. **Dimensional-accuracy and functional-fit check** — Verify every functional dimension, hole, thread, bore and mating interface has been re-created parametrically in CAD rather than inherited from the generated mesh, because the geometry is bounded by a 256³ TSDF grid resolution by the authors' own admission and cannot hold a tolerance. [S99]
12. **Assembly clearance check** — Verify at least 0.3 mm clearance at every intended moving or mating interface, as the baseline starting figure for movable parts. [S104]
13. **Base and adhesion check** — Verify the first-layer footprint is adequate and the base is thick enough (vendor guidance: roughly 3 mm for figurine-type parts), because thin bases and poor bed adhesion are documented warping causes and inadequate bed adhesion is a named print-failure feature. [S105][S106]
14. **Face-count / decimation sanity check** — Verify the final mesh face count is appropriate for the slicer and that any decimation was run topology-preserving, because the reference pipeline decimates with `preservetopology=True`, `preserveboundary=True`, `preservenormal=True` at `max_facenum` defaults of 50 000 (helper) / 400 000 (label example), and decimation can otherwise reintroduce defects. [S98]
15. **Human sign-off is mandatory, not optional** — Verify a named human designer has reviewed and signed off the gate, because published automated printability classifiers are trained on datasets as small as ~150 models, their authors state they remain "far from optimal" and that "full generalization remains unlikely" since severity depends on material, printer configuration and intended application. [S105]
16. **Test print before release** — Verify at least one physical test print of the final released geometry at the released scale and material, because none of Step1X-3D's documentation, model card or paper claims printability, and its published evaluation measures only image-geometry alignment (CLIP-Score, Uni3D-I, OpenShape) rather than any fabrication metric. [S98][S99][S100]
