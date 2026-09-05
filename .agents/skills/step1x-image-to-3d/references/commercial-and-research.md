# Research and commercial evidence for Step1X

Last verified: 2026-09-05. Re-open official sources and preserve dated evidence for every release; this reference is not a legal clearance.

## Practical research conclusions

Step1X is useful as an appearance-led proposal generator, not an engineering oracle:

- it conditions geometry on one image and therefore synthesizes unseen depth/backside;
- geometry is generated through a latent diffusion/TSDF/marching-cubes route;
- the authors explicitly describe the broader field and evaluated results as still short of production-ready quality;
- training views are centered at about 90% occupancy, use background removal, and include orthographic or moderate 35–100 mm perspective equivalents.

Implication: select by massing and topology, then register, repair and engineer the result. Do not use visual similarity as proof of dimensional or functional correctness.

## Commercial-use conclusion

The official Step1X source repository and official Step1X weight repository identify Apache-2.0. The served owned fork is geometry-only: it replaced the Hunyuan-derived volume decoder independently at `f00dd46` and deleted the texture/SDXL path at `2433849`. This supports a recorded `WARN`, not blanket clearance: only geometry runs at or after the decoder cutoff qualify, and the remaining evidence items below stay open.

It is not a blanket clearance of a sold model. Independently verify:

- rights to the input/reference image and permission to send it through imagegen/Step1X;
- imagegen provider terms and the exact account/plan;
- every model/runtime dependency actually executed;
- the serving fork commit and whether it is at or after `f00dd46`;
- upstream training-data provenance and the undeclared-licence CLIP configuration file;
- copied trademarks, designs, copyrighted characters/artwork, privacy/publicity and patents;
- human authorship and any claim of exclusive copyright;
- product safety, conformity and destination-market obligations;
- Apache notices if Step1X code/weights or a modified runtime are redistributed (ordinary generated mesh output is a separate rights analysis).

## Verified runtime dependency ledger

Record exact revisions from `capture_step1x_runtime.py`; the following are the current local snapshots:

| Component | Revision | License evidence | Commercial status |
|---|---|---|---|
| Step1X-3D source | owned fork `4b6da92` from upstream base `cb5ac944709c6c913109070c7b90c3447f57f3d4` | Apache-2.0 plus fork `NOTICE`/`FORK.md`; independently replaced volume decoder | geometry-only runs at/after `f00dd46` are eligible for `WARN`; pre-cutoff runs remain blocked |
| `stepfun-ai/Step1X-3D` weights | `bf7084495b3a72222f36549b7942948aa4d9daa7` | official HF repository: Apache-2.0 | permitted subject to Apache conditions |
| `openai/clip-vit-large-patch14` | `32bd64288804d66eefd0ccbe215aa642df71cc41`; configuration only | official CLIP code license: MIT; HF model card declares no license | `WARN`; no trained CLIP artifact from this repository is downloaded or redistributed in the verified path |
| `facebook/dinov2-with-registers-large` | `e4c89a4e05589de9b3e188688a303d0f3c04d0f3` | official HF repository: Apache-2.0 | permitted subject to Apache conditions |
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
- geometry GLB path, SHA-256 and size;
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
  --role geometry-generation
```

This copies the record into evidence, hashes it, appends a `generation_records` entry to `07-release/provenance.json`, and marks AI use without inventing a human reviewer or legal approval. The commercial audit remains blocked until the other required fields and licenses are resolved.

If an opaque input executed U2Net and its exact asset evidence remains unresolved, record `WARN` with an owner/deadline or use a reviewed alpha input and re-run. Do not silently claim the Step1X Apache license covers that dependency.

## Primary sources

- [Step1X-3D official repository and Apache-2.0 statement](https://github.com/stepfun-ai/Step1X-3D)
- [Step1X-3D official model repository, Apache-2.0](https://huggingface.co/stepfun-ai/Step1X-3D)
- [Step1X-3D technical report](https://arxiv.org/abs/2505.07747)
- [DINOv2 registers model repository](https://huggingface.co/facebook/dinov2-with-registers-large)
- [OpenAI CLIP MIT license](https://github.com/openai/CLIP/blob/main/LICENSE)
- [rembg repository and MIT license](https://github.com/danielgatis/rembg)
- [U-2-Net upstream repository](https://github.com/xuebinqin/U-2-Net)
