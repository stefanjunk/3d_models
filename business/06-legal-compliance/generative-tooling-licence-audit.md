# Generative tooling licence audit — Step1X-3D pipeline

Audit date: 2026-09-04. Scope: every component that runs when metriMade generates geometry or
texture for the `SKU-315`–`SKU-414` generative research block.

**What was inspected, and how.** This audit reads the actual installation, not documentation:
the local checkout `/home/stefan/Projekte/Step1X-3D` at commit `cb5ac94`, the running container
`step1x-3d-step1x3d-1` (`step1x3d:python310-cu124`, 271 installed distributions read via
`importlib.metadata`), the model cache actually populated on disk
(`Step1X-3D/.cache/huggingface/hub`, 26 GB, six model repos), the Hugging Face model API for each
cached repo, and the GitHub licence API plus raw licence texts for each upstream project cited in
the source. Everything below is labelled with where it was read. Items that could not be
established are marked **UNVERIFIED** and carry no substitute assumption.

## 1. Current verdict — owned fork at `4b6da92` (2026-09-05)

The commercially considered runtime is the owned geometry-only fork
`github.com/stefanjunk/Step1X-3D@4b6da92`, not the historical upstream checkout described below.
The fork is clean and its `main` branch is synchronized with `origin/main` as of this audit.

- The texture pipeline and SDXL stack are absent (`2433849`), so their Hunyuan/RAIL restrictions do
  not execute and the service returns one untextured geometry GLB.
- The geometry-path Hunyuan-derived volume decoder was replaced independently at `f00dd46`.
  Geometry runs recorded at or after that commit inherit the portfolio's `TOOL-LICENCE WARN`
  position; older geometry and every historical textured artifact do not.
- The replacement decoder and mesh post-processing tests pass in the serving container (4 passed,
  7 passed respectively; the optional black-box upstream comparison was not enabled).
- Residual `WARN` items remain: image-generator rights per SKU, upstream training-data provenance,
  the undeclared-licence CLIP configuration file, and product/listing disclosure duties. This is
  evidence for an engineering go/no-go gate, not legal advice.

## 1A. Historical upstream verdict (superseded for new fork runs)

Before the owned-fork changes, two components imposed restrictions on the **output**, not merely
on redistribution of code, and both sat in the upstream live path:

1. **Tencent Hunyuan-derived code** — blocks EU commercial use today. Twelve files in Step1X-3D
   carry a verbatim Tencent Hunyuan licence header. One of them is in the geometry path and is
   executed on every geometry run. The upstream Hunyuan3D-2 licence excludes the European Union
   from its territory and forbids use of the works' output outside it.
2. **Stable Diffusion XL (CreativeML Open RAIL++-M)** — permitted commercially, but conditional:
   its use-based restrictions must be carried into metriMade's own customer terms as an
   enforceable provision and passed on to resellers. Applies only if the texture path is used.

Everything else in the stack is either permissive (Apache-2.0 / MIT / BSD) or copyleft that binds
only **distribution of the software**, which metriMade does not do. Two items need a decision
rather than a fix: the CC BY-NC provenance citations in the geometry encoders, and whether the
texture path is needed at all.

## 2. Component inventory

### Layer A — Step1X-3D itself

| Component | Licence as read | Where read | Commercial use |
| --- | --- | --- | --- |
| `stepfun-ai/Step1X-3D` code | Apache-2.0 (root `LICENSE`, unmodified, 11,357 bytes) | local checkout | Permitted, subject to attribution and modified-file notices |
| `stepfun-ai/Step1X-3D` weights | `apache-2.0`, not gated | HF model API | Permitted |
| Repository `NOTICE` / third-party notices file | **absent** | local checkout | Upstream attribution is incomplete; our own NOTICE must be assembled by hand |

### Layer B — Tencent Hunyuan-derived code (the blocker)

Header text, identical in all twelve files: *"Hunyuan 3D is licensed under the TENCENT HUNYUAN
NON-COMMERCIAL LICENSE AGREEMENT except for the third-party components listed below … made
publicly available by Tencent in accordance with TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT."*

**Geometry path (1 file — this is what makes it a blocker):**

- `step1x3d_geometry/models/autoencoders/volume_decoders.py` — imported at
  `michelangelo_autoencoder.py:23` and instantiated at lines 582 and 584. Both configuration
  branches (`hierarchical` and vanilla) construct a decoder from this file, so **no geometry run
  avoids it**.

**Texture path (11 files):**

- `step1x3d_texture/custom_rasterizer/custom_rasterizer/{__init__.py, io_glb.py, io_obj.py, render.py}`
- `step1x3d_texture/custom_rasterizer/lib/custom_rasterizer_kernel/__init__.py`
- `step1x3d_texture/differentiable_renderer/{__init__.py, camera_utils.py, mesh_processor.py, mesh_render.py, mesh_utils.py, setup.py}`

Both texture directories are compiled and installed into the runtime as `custom_rasterizer 0.1`
and `mesh_processor 0.0.0`, whose package metadata declares **no licence at all**.

Upstream: `Tencent-Hunyuan/Hunyuan3D-2` reports `NOASSERTION` on the GitHub licence API, i.e. a
custom agreement. Its licence text defines the territory as the world **excluding the European
Union, the United Kingdom and South Korea** and prohibits use or display of the works' *output or
results* outside that territory. Which of the two named Tencent agreements actually governs these
particular files — the non-commercial agreement or the 2.0 community agreement — is **UNVERIFIED**;
both outcomes block a German seller, one by the non-commercial restriction and one by the
territory exclusion.

### Layer B2 — Non-commercial provenance citations in the geometry encoders (new finding)

Two geometry files cite `facebookresearch/DiT` as their source of adaptation:

- `step1x3d_geometry/models/conditional_encoders/clip/modeling_conditional_clip.py`
- `step1x3d_geometry/models/conditional_encoders/dinov2/modeling_conditional_dinov2.py`

`facebookresearch/DiT` is licensed **Attribution-NonCommercial 4.0 International** (read from
`LICENSE.txt` on the upstream default branch). Whether these files contain copied DiT expression
or merely reference it is **UNVERIFIED** and must be resolved by diffing them against the upstream
source. Other provenance citations in the same modules resolve to permissive upstreams:
`PixArt-alpha/PixArt-alpha` Apache-2.0, `3DTopia/OpenLRM` Apache-2.0, `facebookresearch/dinov2`
Apache-2.0, `openai/CLIP` MIT, `huggingface/diffusers` Apache-2.0.

### Layer C — Model weights actually downloaded and used

| Weights | Licence as read (HF model API) | Path | Note |
| --- | --- | --- | --- |
| `stepfun-ai/Step1X-3D` | `apache-2.0` | geometry + texture | — |
| `facebook/dinov2-with-registers-large` | `apache-2.0` | geometry conditioning — configuration only | Cache holds `config.json` and `preprocessor_config.json` (20 KB); weights come from the Step1X-3D checkpoint |
| `openai/clip-vit-large-patch14` | **no licence declared on the model card** | geometry conditioning — **configuration only** | The local cache holds only `config.json` (16 KB). The encoder class is instantiated from that configuration and the trained weights come from the Apache-2.0 Step1X-3D checkpoint, so no OpenAI weight file is downloaded or redistributed |
| `stabilityai/stable-diffusion-xl-base-1.0` | `openrail++` | texture (`IG2MVSDXLPipeline` base model) | Use-based restrictions, mandatory flow-down |
| `madebyollin/sdxl-vae-fp16-fix` | `mit` | texture VAE | — |
| `ZhengPeng7/BiRefNet` | `mit` | background removal | — |
| `runwayml/stable-diffusion-v1-5` | repo no longer resolvable via the HF API | referenced at `step1x3d_texture/schedulers/scheduling_shift_snr.py:99` | **Not present in the cache.** Whether that line can execute is UNVERIFIED |

### Layer D — Python dependencies with licence consequences

| Package | Version | Licence as read | Where it runs | Consequence |
| --- | --- | --- | --- | --- |
| `pymeshlab` | 2023.12.post3 | **GPL-3.0** (installed metadata; upstream `cnr-isti-vclab/PyMeshLab` GPL-3.0) | live geometry path: `step1x3d_geometry/models/pipelines/pipeline_utils.py`, called from `app.py` via `remove_degenerate_face` / `reduce_face` | Internal use is unaffected; never bundle it into anything shipped to a customer |
| `plyfile` | 1.0.3 | **GPL-3.0-or-later** | `requirements.txt` | Same posture as pymeshlab |
| `easydict` | 1.13 | LGPL-3.0 | runtime | Distribution-only duty |
| `crc32c` | 2.8 | LGPL-2.1-or-later | transitive | Distribution-only duty |
| `paramiko` | 3.5.1 | LGPL | transitive | Distribution-only duty |
| `nvdiffrast` | 0.4.0 | Nvidia Source Code License (1-Way Commercial); package metadata declares none | imported only by `data/watertight_and_sampling.py` (training-data prep) | Commercial use permitted with redistribution conditions; it should not sit in a production image it is never used in |
| `kaolin` | 0.17.0 | Apache-2.0 | runtime | — |
| `pytorch3d` | 0.7.8 | metadata declares none | referenced in texture utils | Upstream licence **UNVERIFIED** |
| `nvidia-*` CUDA runtime | 12.4.x | NVIDIA Proprietary Software | runtime | Standard CUDA redistribution terms |
| `torch`, `diffusers`, `transformers`, `timm`, `accelerate`, `safetensors`, `trimesh`, `open3d`, `PyMCubes`, `scikit-image`, `rembg`, `gradio`, `spaces`, `sageattention`, `torch_cluster`, `onnxruntime` | — | BSD-3 / Apache-2.0 / MIT | runtime | No output restriction |

### Layer E — Training data behind the weights

Step1X-3D's curated training set derives from Objaverse (320k) and Objaverse-XL (480k), whose
assets carry heterogeneous per-asset licences. Neither the paper nor the dataset card states how
per-asset terms were handled. This is an upstream risk we cannot close; it is why per-SKU
provenance records and human-authored CAD as the protected subject matter matter.

### Layer F — The image generator (step 1 of our own pipeline)

Not part of Step1X-3D. Whichever image model produces the isolated reference image governs that
image and possibly its output; a non-commercial model licence there would poison the chain
independently. Currently **UNVERIFIED** because the generator choice is not yet fixed per SKU.

## 3. What actually attaches to the delivered file

- Apache-2.0, MIT, BSD, LGPL and GPL components impose duties on **distributing the software**.
  Running them to produce a mesh does not make the mesh a derivative work of the program, so they
  do not restrict the STL/3MF we sell — provided we never ship the tooling itself.
- **CreativeML Open RAIL++-M (SD-XL)** does reach the output: use-based restrictions apply to what
  is generated, and paragraph 5 obliges us to bind our own customers to those restrictions.
- **The Tencent agreement** reaches the output explicitly ("Output or results") and ties it to a
  territory that excludes the EU. This is the reason the whole block is gated.

## 4. Historical remediation plan

Ordered by what unblocks the most.

1. **Decide whether the texture path is needed at all.** Dropping textured GLB output removes 11 of
   the 12 Hunyuan files, both undeclared compiled extensions, the SD-XL RAIL++ flow-down duty, the
   SD-XL and `sdxl-vae-fp16-fix` weights and the dead `runwayml/stable-diffusion-v1-5` reference in
   one decision. Our products are printed in filament colours assigned in CAD, so texture is
   plausibly optional. Evidence to capture: a written scope decision plus a geometry-only run
   record proving the texture module is not imported.
2. **Establish which Tencent agreement governs `volume_decoders.py`, and get it in writing.** Ask
   StepFun whether the header is stale, whether the file is their own work, and under which licence
   they release it. Capture the request, the date and any answer verbatim.
3. **Prepare a clean-room replacement for `volume_decoders.py`.** It performs volume decoding ahead
   of surface extraction; `PyMCubes`, `scikit-image` and `open3d` are already installed, so a
   replacement written without reference to the Tencent code would make the geometry path
   Hunyuan-free regardless of StepFun's answer. Evidence: authorship record, a diff-free
   declaration, and a geometry regression comparison on fixed inputs.
4. **Diff the two conditional-encoder files against `facebookresearch/DiT`** (CC BY-NC 4.0) and
   record whether copied expression is present. If it is, that file needs the same treatment as
   item 3 before any commercial use.
5. **`openai/clip-vit-large-patch14` — resolved as far as it needs to be.** The model card declares no
   licence, but the repository supplies only `config.json` to this pipeline; the trained weights are
   the Apache-2.0 checkpoint's own. Record the finding; no further action unless a future
   configuration switches to `CLIPModel.from_pretrained`, which would download real weights.
6. **If texture stays: add the RAIL++-M use restrictions to the customer terms** as an enforceable
   clause with a flow-down obligation on resellers, and check whether
   `scheduling_shift_snr.py:99` can execute — the referenced Stable Diffusion 1.5 repository no
   longer resolves and carries its own RAIL-M terms.
7. **Confirm `nvdiffrast` is not imported in the serving path and remove it from the production
   image.** A component with custom NVIDIA terms should not be installed where it is never used.
8. **Fix the distribution posture for GPL components.** `pymeshlab` and `plyfile` are fine for
   internal use. Record explicitly that neither the container image nor any bundled tool goes to a
   customer, and if that ever changes, replace both before it does.
9. **Verify `pytorch3d`'s licence** and add it to the inventory; its installed metadata declares
   none.
10. **Assemble our own NOTICE / third-party-notices file.** Upstream has none, yet Apache-2.0
    requires attribution and modified-file notices for anything we redistribute internally or in a
    release package.
11. **Fix the image-generator licence per SKU** and record it in the product provenance, including
    the model, version and whether its licence permits commercial use of the output.
12. **Keep an alternative-model column open.** If StepFun does not clarify and item 3 is not
    completed, an image-to-3D model with a clean commercial licence is the fallback. The 2026
    landscape of alternatives was **UNVERIFIED** in the research pass and needs its own check
    before it can be relied on.

## 5. Implementation status — 2026-09-04

The pipeline now runs from an owned fork, `github.com/stefanjunk/Step1X-3D`, forked at upstream
commit `cb5ac94`. Five commits change what actually executes:

| Commit | Change |
| --- | --- |
| `f19046a` | Two-GPU device placement, validation and CUDA 12.4 container packaging |
| `39ffb6e` | `remove_floater`, `remove_degenerate_face` and `reduce_face` reimplemented on trimesh and Open3D (MIT); pymeshlab (GPL-3.0), plyfile (GPL-3.0-or-later) and easydict (LGPL-3.0) dropped |
| `f00dd46` | `volume_decoders.py` replaced by an independent implementation; the upstream module was only exercised as a black box |
| `2433849` | Texture pipeline deleted: `step1x3d_texture/`, its two vendored CUDA extensions, `configs/train-texture-ig2mv/`, `data/ig2mv/`, the SDXL dependency and the texture-only Python packages |
| `f5d4b91` | `NOTICE`, `FORK.md`, README banners |

### What that closes

| Check from section 4 | Status |
| --- | --- |
| 1. Decide whether texture is needed | **Closed** — removed, taking 11 of the 12 Hunyuan-headed files, both undeclared-licence extensions, the SD-XL RAIL++-M flow-down duty, two weight repositories and the withdrawn SD-1.5 reference with it |
| 3. Clean-room `volume_decoders.py` | **Closed** — the twelfth Hunyuan-headed file is gone from the geometry path. Verified against analytic fields: the dense grid matches upstream to 1e-6, the hierarchical decoder yields identical iso-surfaces at 192³ and 384³ including a thin antenna and a detached bead, and it needs 2.3M instead of 57M network evaluations at 384³ |
| 4. Diff the DiT-cited encoder files | **Closed, clean** — both carry the Hugging Face Apache-2.0 header and contain no adaLN-Zero, `modulate()`, `shift_msa` or `scale_msa` code; the CC BY-NC citation is architectural |
| 6. RAIL++-M clause; SD-1.5 reachability | **Moot** — both left with the texture path |
| 7. `nvdiffrast` out of the production image | **Closed** — moved to `requirements-dataprep.txt` |
| 8. GPL distribution posture | **Closed, stronger than required** — no copyleft component remains in the inference path |
| 9. Verify `pytorch3d` | **Moot** — removed |
| 10. Assemble a NOTICE file | **Closed** |

### What remains open

- **`openai/clip-vit-large-patch14` declares no licence** on its model card. Materially reduced on 2026-09-04: the
  local cache proves that repository contributes a 16 KB `config.json` and nothing else, because
  `dinov2_clip_encoder.py` instantiates the class from configuration and loads the trained weights from the
  Apache-2.0 Step1X-3D checkpoint's 2.8 GB `visual_encoder`. What remains is a dependency on an undeclared-licence
  *configuration file*, not on an undeclared-licence trained artifact — and it is not redistributed.
- **StepFun has not been asked** whether the Hunyuan headers were stale (check 2). This no longer blocks use; it decides whether upstream can be merged again.
- **Image-generator licence per SKU** (check 11) and the **alternative-model fallback** (check 12).
- **Training-data provenance** of the published weights (Objaverse / Objaverse-XL) — an upstream question we cannot close.
- **EU AI Act marking, GPSR article text and platform AI policies** remain UNVERIFIED from the research pass.

### Consequence applied to the portfolio

The 100 generative rows `SKU-315`–`SKU-414` were regenerated on 2026-09-04. Their `Hard_Gates` now
read `TOOL-LICENCE WARN (owned fork; weight-licence and disclosure items open)` instead of a failing
gate, `Idea__Generative_Tool_Licence_Gate` describes the fork and names the residual items, and
`Next_Gate` asks for the `openai/clip-vit-large-patch14` weight terms and the AI-disclosure duty
before release. Source record `S131` carries the fork and runtime-inventory evidence. The gate is
kept as a recorded `WARN` rather than removed, so that it returns to `FAIL` if a tool with a
non-commercial or territorially limited licence re-enters the pipeline; both the workbook validator
and the preflight-estimate builder now require it to be present as exactly one of `WARN` or `FAIL`.

### The cutoff: what the de-escalation does *not* cover

The `WARN` position describes the tooling as it stands, not every artifact ever produced with it.
The fork's own history makes the boundary exact:

| Commit | Effect |
| --- | --- |
| `f19046a` | Two-GPU packaging only. `volume_decoders.py` still opens with the verbatim Tencent Hunyuan header, and the geometry VAE executes it. |
| `f00dd46` | The geometry decoder is replaced. **This is the cutoff for geometry-only runs.** |
| `2433849` | The texture stage and its eleven Hunyuan-headed files are deleted. |

Therefore:

- a **geometry artifact** inherits the `WARN` position only if its recorded source commit is at or
  after `f00dd46`;
- a **textured artifact** never inherits it, whatever its commit, because the texture path itself was
  the Hunyuan-derived code — and it cannot simply be regenerated, since the fork no longer has that
  stage;
- anything derived from such an artifact — repaired meshes, released STL/3MF, G-code — carries the
  same status as its source.

Any existing product package whose Step1X run predates `f00dd46` keeps its pre-fork status until it
is regenerated, and regenerating changes the mesh, because `5a23ee7` also changed which mesh the
service exports. That is a per-product decision recorded in the product's own rights record, not
something this gate resolves.

A grep for the Hunyuan licence string still matches `volume_decoders.py`, `FORK.md` and `NOTICE` at
the fork's HEAD. In all three the match is prose describing what was removed, not a licence header.

#### Worked example: MM-ORG-041

The first product to be decided by this rule, verified against its own run records and derivation
manifests on 2026-09-05:

| Artifact | Source run | Fork commit recorded | Position |
| --- | --- | --- | --- |
| v0.1.0 STL | `run-002` (2026-09-04 18:50) | none recorded; predates the cleanup | Pre-fork status |
| v0.2.0 STL | `run-005` (2026-09-05 09:26) | `4b6da92`, worktree clean | `WARN`-covered |

Runs 003 to 005 all record `4b6da92`, which is past the `f00dd46` cutoff; runs 001 and 002 carry no
fork provenance at all. The distinction is only decidable because the run client now stamps a
`provider.served_by_fork` block with the commit and worktree state — that stamp is what makes the
cutoff auditable per artifact rather than arguable after the fact, and it should be treated as
required evidence for any future generative product.

## 6. Evidence pins

- Local checkout `/home/stefan/Projekte/Step1X-3D`, origin `github.com/stefanjunk/Step1X-3D`,
  upstream `github.com/stepfun-ai/Step1X-3D`, commit `4b6da92` (upstream base `cb5ac94`).
- Container `step1x-3d-step1x3d-1`, image `step1x3d:python310-cu124`, 271 installed distributions.
- Model cache `Step1X-3D/.cache/huggingface/hub` with exactly six model repos, listed in Layer C.
- Licence texts read on 2026-09-04: repository `LICENSE` files, installed package metadata, the
  Hugging Face model API per repo, the GitHub licence API per upstream project, and the raw
  `LICENSE.txt` of `facebookresearch/DiT` and `NVlabs/nvdiffrast`.
- Fork evidence: `github.com/stefanjunk/Step1X-3D` commits `f19046a`, `39ffb6e`, `f00dd46`,
  `2433849`, `f5d4b91`, `5a23ee7`, `4b6da92`; tests `tests/test_volume_decoders.py` and
  `tests/test_mesh_postprocess.py`.
- Related records: source records `S122`–`S130` in
  `business/02-portfolio/research-idea-sources-additions.csv`; raw research in
  `research/market/step1x-generative-batch-2026-09-04/research-F-pipeline.md`; the per-row gate text
  in `business/02-portfolio/research-ideas-additions-3.csv` (`Generative_Tool_Licence_Gate`) and the
  failing `TOOL-LICENCE` entry in every row's `Hard_Gates`.

This audit is an engineering and evidence record for a go/no-go decision. It is not legal advice,
and no item above may be treated as cleared until its evidence is captured.
