# Research and commercial evidence for Step1X

Last verified: 2026-09-01. Re-open official sources and preserve dated evidence for every release; this reference is not a legal clearance.

## Practical research conclusions

Step1X is useful as an appearance-led proposal generator, not an engineering oracle:

- it conditions geometry on one image and therefore synthesizes unseen depth/backside;
- geometry is generated through a latent diffusion/TSDF/marching-cubes route;
- texture is generated separately through geometry-guided multi-view diffusion and baked as albedo;
- the authors explicitly describe the broader field and evaluated results as still short of production-ready quality;
- the reported texture limitation is albedo-only, not a complete physical/PBR material definition;
- training views are centered at about 90% occupancy, use background removal, and include orthographic or moderate 35–100 mm perspective equivalents.

Implication: select by massing and topology, then register, repair and engineer the result. Do not use visual similarity as proof of dimensional or functional correctness.

## Commercial-use conclusion

The official Step1X source repository and official Step1X weight repository identify Apache-2.0. That permissive license supports commercial use, modification and distribution subject to its conditions. This is strong evidence that the Step1X code/weights themselves are commercially usable.

It is not a blanket clearance of a sold model. Independently verify:

- rights to the input/reference image and permission to send it through imagegen/Step1X;
- imagegen provider terms and the exact account/plan;
- every model/runtime dependency actually executed;
- OpenRAIL use restrictions in the SDXL texture dependency;
- copied trademarks, designs, copyrighted characters/artwork, privacy/publicity and patents;
- human authorship and any claim of exclusive copyright;
- product safety, conformity and destination-market obligations;
- Apache notices if Step1X code/weights or a modified runtime are redistributed (ordinary generated mesh output is a separate rights analysis).

## Verified runtime dependency ledger

Record exact revisions from `capture_step1x_runtime.py`; the following are the current local snapshots:

| Component | Revision | License evidence | Commercial status |
|---|---|---|---|
| Step1X-3D source | base `cb5ac944709c6c913109070c7b90c3447f57f3d4` plus captured working-tree patch/hash | Apache-2.0 in official repo | permitted subject to Apache conditions; local modifications must be preserved |
| `stepfun-ai/Step1X-3D` weights | `bf7084495b3a72222f36549b7942948aa4d9daa7` | official HF repository: Apache-2.0 | permitted subject to Apache conditions |
| `stabilityai/stable-diffusion-xl-base-1.0` | `462165984030d82259a11f4367a4eed129e94a7b` | CreativeML Open RAIL++-M | commercial use is not categorically barred, but Attachment A/use restrictions must pass for the exact use |
| `openai/clip-vit-large-patch14` | `32bd64288804d66eefd0ccbe215aa642df71cc41` | official CLIP code license: MIT; capture exact HF model evidence | permissive, but retain exact model-page evidence |
| `facebook/dinov2-with-registers-large` | `e4c89a4e05589de9b3e188688a303d0f3c04d0f3` | official HF repository: Apache-2.0 | permitted subject to Apache conditions |
| `madebyollin/sdxl-vae-fp16-fix` | `207b116dae70ace3637169f1ddd2434b91b3a8cd` | official HF repository: MIT | permissive; retain notice/evidence |
| `ZhengPeng7/BiRefNet` fallback | `e2bf8e4460fc8fa32bba5ea4d94b3233d367b0e4` | official HF repository: MIT | conditional dependency; current web path disables second texture removal |
| `rembg` | `2.0.65` | official repository: MIT | code permissive |
| rembg `u2net.onnx` asset | record actual SHA-256 from container volume | rembg release download plus upstream U-2-Net Apache-2.0 repository; exact converted asset provenance/license link is not explicit enough for a high-confidence release | `WARN` until the exact ONNX artifact and license/provenance evidence are archived |

The current geometry preprocessor asks rembg for model name `bria`, which rembg `2.0.65` does not match to the registered `bria-rmbg` session and therefore falls back to U2Net. The observed cache file is `u2net.onnx`. A transparent RGBA input skips this runtime branch; record the alpha decision in each run rather than assuming the dependency executed.

## Evidence history per run

Every accepted or rejected Step1X attempt should have a `step1x-run.json` containing:

- stable run ID, UTC start/end and status;
- input path/archive, SHA-256, bytes, media type and useful-alpha diagnosis;
- imagegen prompt/record hashes when applicable;
- service URL, endpoint, canonical API-schema hash and client version;
- guidance, steps, face cap, symmetry and edge type;
- runtime-profile path/hash;
- geometry and textured GLB paths, SHA-256 and sizes;
- explicit notes that scale/orientation are unverified and geometry is generated;
- failure details without secrets when unsuccessful.

The runtime profile should contain:

- source origin/base commit, dirty paths, tracked-diff hash and relevant runtime-file hashes;
- Dockerfile/Compose hashes, container image ID/digest and selected device environment;
- Python, PyTorch, CUDA, Gradio and Pydantic versions;
- GPU names/UUIDs/memory/driver;
- exact Hugging Face model repository IDs and snapshot revisions;
- API schema hash and U2Net asset hash when available.

## Attach to the commercial release record

Load `commercialize-3d-models`. Place the runtime profile, license/terms snapshots and Step1X run record under `02-tools/evidence/`. Register Step1X and each executed model dependency as separate tool/model rows. Register the source/generated input image under `01-sources/` with its AI-input and commercial-use rights.

Use the commercial skill's attachment helper:

```bash
python /resolved/commercialize-3d-models/scripts/record_ai_generation.py \
  /path/to/commercial-clearance \
  /path/to/step1x-run.json \
  --provider stepfun-ai/Step1X-3D \
  --role geometry-generation \
  --role texture-generation
```

This copies the record into evidence, hashes it, appends a `generation_records` entry to `07-release/provenance.json`, and marks AI use without inventing a human reviewer or legal approval. The commercial audit remains blocked until the other required fields and licenses are resolved.

If an opaque input executed U2Net and its exact asset evidence remains unresolved, record `WARN` with an owner/deadline or use a reviewed alpha input and re-run. Do not silently claim the Step1X Apache license covers that dependency.

## Primary sources

- [Step1X-3D official repository and Apache-2.0 statement](https://github.com/stepfun-ai/Step1X-3D)
- [Step1X-3D official model repository, Apache-2.0](https://huggingface.co/stepfun-ai/Step1X-3D)
- [Step1X-3D technical report](https://arxiv.org/abs/2505.07747)
- [SDXL CreativeML Open RAIL++-M license](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/e4e60c65aa20ee60092c60ba197f541872cf9373/LICENSE.md)
- [DINOv2 registers model repository](https://huggingface.co/facebook/dinov2-with-registers-large)
- [SDXL VAE fp16 fix model repository](https://huggingface.co/madebyollin/sdxl-vae-fp16-fix)
- [BiRefNet model repository](https://huggingface.co/ZhengPeng7/BiRefNet)
- [OpenAI CLIP MIT license](https://github.com/openai/CLIP/blob/main/LICENSE)
- [rembg repository and MIT license](https://github.com/danielgatis/rembg)
- [U-2-Net upstream repository](https://github.com/xuebinqin/U-2-Net)
