# Local runtime and API contract

Read this reference only when starting, probing, invoking, reproducing, or troubleshooting the local Step1X service.

## Why this is a skill and CLI, not MCP

The working service exposes one local, long-running Gradio endpoint and serializes jobs at concurrency `1`. Agents already have skill and shell access, so a validated CLI provides typed parameters, file handling, hashes and failure records without another daemon or MCP schema in every context.

Add an MCP adapter later only if the service becomes remote or multi-host, needs authentication/authorization, or must be discovered by clients without filesystem access. The run-record schema and CLI can remain the stable implementation behind that adapter.

## Verified local configuration

Verified 2026-09-01:

| Layer | Pin/configuration |
|---|---|
| Step1X source base | `cb5ac944709c6c913109070c7b90c3447f57f3d4` plus a modified working tree captured by runtime hash/profile |
| model snapshot | `stepfun-ai/Step1X-3D@bf7084495b3a72222f36549b7942948aa4d9daa7` |
| container | `step1x3d:python310-cu124` |
| CUDA base | NVIDIA CUDA `12.4.1` with cuDNN development image, digest pinned in `Dockerfile` |
| Python | `3.10.12` |
| PyTorch | `2.5.1+cu124`; CUDA ABI `12.4` |
| Gradio/server client | `5.5.0` / `1.4.2` |
| Pydantic | `2.10.6` (newer boolean-schema output breaks this Gradio combination) |
| GPU architecture | two RTX 4060 Ti 16 GB, compute capability `8.9` |

The source worktree contains the operational fixes. A base commit alone does not reproduce it; `capture_step1x_runtime.py` records the dirty state, tracked-diff hash and relevant file hashes. For a frozen production deployment, commit/tag those runtime changes or archive the patch and all hashed runtime files.

## Device placement

| Work | Device | Reason |
|---|---|---|
| geometry diffusion, CLIP/DINO conditioning and extraction | `cuda:0` | persistent geometry pipeline |
| texture SDXL/multiview generation and baking | `cuda:1` | persistent texture pipeline |
| texture VAE/auxiliary CUDA work | `cuda:0` | uses otherwise released geometry capacity |
| BiRefNet fallback | `cuda:1` | only used by standalone texture calls that request background removal; the web app reuses geometry RGBA and disables this second removal |
| rembg/U2Net for an opaque input | CPU ONNX | `REMBG_PROVIDER=CPUExecutionProvider`; skipped when the input has useful alpha |
| orchestration, image I/O, mesh cleanup/decimation, UV/scene work and Gradio | CPU/RAM | these are host-side algorithms or control paths, not CPU offload of the main texture model |

`TEXTURE_CPU_OFFLOAD=0`, so the main texture model is not intentionally moved through system RAM. Both GPUs may show free VRAM because the model stages and kernels have different peak allocations; unused memory is not evidence that one job can be safely parallelized.

## Service control

```bash
docker compose -f /home/stefan/Projekte/Step1X-3D/docker-compose.yml up -d
docker compose -f /home/stefan/Projekte/Step1X-3D/docker-compose.yml ps
docker compose -f /home/stefan/Projekte/Step1X-3D/docker-compose.yml logs --tail 200 step1x3d
```

Do not rebuild or restart a healthy service during an active generation. A rebuild can be lengthy because native CUDA extensions target `sm_89`.

## Endpoint contract

Base URL: `http://127.0.0.1:7861`

Named endpoint: `/generate_func`

| Position | API name | Type/default | Meaning |
|---:|---|---|---|
| 1 | `input_image_path` | uploaded image, required | single input plate |
| 2 | `guidance_scale` | float, `7.5` | image-conditioning strength |
| 3 | `inference_steps` | integer, `50`, range 1–100 | geometry denoising steps |
| 4 | `max_facenum` | integer, `400000` | cap for raw geometry output |
| 5 | `symmetry` | `x` or `asymmetry`, default `x` | semantic shape control |
| 6 | `edge_type` | `sharp`, `normal`, or `smooth`, default `sharp` | edge/detail prior |

Returns, in order:

1. untextured geometry GLB;
2. textured GLB.

The current app exports the raw geometry before its texture-stage cleanup and default reduction to roughly 50,000 faces. Therefore use `geometry.raw.glb` for geometric fidelity and `textured.raw.glb` for UV/albedo appearance unless inspection proves a different choice.

No geometry seed is exposed by this endpoint. Identical parameters do not promise bitwise-identical output. Record every candidate separately.

## Probe and generate

```bash
python scripts/step1x_client.py probe --report reports/step1x-api.json

python scripts/step1x_client.py generate input.png \
  --output-dir organic/raw/step1x/run-001 \
  --runtime-profile evidence/step1x-runtime.json
```

The probe reads `/gradio_api/info`, verifies parameter names/enums and hashes canonical schema JSON. Generation refuses to overwrite a non-empty run directory.

## Parameter policy

- Start at `50` steps and `7.5` guidance. Lower steps are candidate-generation experiments, not equivalent-quality substitutions.
- Use `x` only when bilateral symmetry is intended; use `asymmetry` for deliberately chiral or irregular massing.
- Use `sharp` for hard-surface massing, `normal` for mixed forms and `smooth` for organic forms. None creates CAD-exact edges.
- Use a lower face cap for disposable candidates only after confirming that the silhouette and negative spaces remain useful. Keep the accepted high-detail geometry master.

## Common failures

- API schema `TypeError: argument of type 'bool' is not iterable`: the server environment drifted; restore Gradio `5.5.0`, gradio-client `1.4.2`, Pydantic `2.10.6` and rebuild.
- `localhost is not accessible`: the app must launch on `0.0.0.0`; do not enable a public share link for this local workflow.
- CUDA device mismatch in Voronoi/indexing: use the patched current Step1X worktree and capture its diff hash.
- OOM: confirm no competing jobs, inspect both GPUs, reduce candidate face/steps only as a diagnostic, then preserve quality settings for the accepted run.
- Opaque-input CPU delay: supply a reviewed RGBA/transparent plate so geometry preprocessing can use its alpha mask and skip rembg/U2Net.

## Primary sources

- [Step1X-3D official repository](https://github.com/stepfun-ai/Step1X-3D)
- [Step1X-3D official model repository](https://huggingface.co/stepfun-ai/Step1X-3D)
- [Gradio Python client](https://gradio.app/docs/python-client/introduction)
