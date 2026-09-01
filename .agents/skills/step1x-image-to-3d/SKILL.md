---
name: step1x-image-to-3d
description: Generate geometry and textured GLB drafts from a single isolated image with the local two-GPU Step1X-3D service, preserve reproducible run evidence, and route the mesh into functional CAD, organic-mesh post-processing, printable STL/3MF, or multicolor workflows. Use when an agent should create a whole appearance-led object, an organic component, or a sacrificial preform with imagegen and Step1X-3D before adding exact holes, channels, mounts, threads, backers, or interfaces.
license: MIT
metadata:
  audience: "functional 3D design agents"
  workflow: "imagegen to Step1X GLB to hybrid printable design"
  compatibility: "local Step1X Gradio service; Python client; optional Trimesh"
---

# Step1X Image to 3D

Use Step1X as a generative mesh provider inside the existing functional-design workflow. It proposes appearance-led 3D geometry from one image; it does not own dimensions, functional interfaces, safety, manufacturing acceptance, or commercial clearance.

Resolve every bundled path relative to this `SKILL.md`. Keep references unloaded until their decision point.

## Ownership and routing

| Decision/artifact | Owning skill |
|---|---|
| product/component decomposition, authority and interface skeleton | `decompose-printable-designs` |
| evidence, scale, camera and hidden-geometry interpretation | `reconstruct-printable-3d-from-images` |
| image generation and image editing | `imagegen` |
| Step1X service invocation, raw GLBs and run record | this skill |
| mesh repair, Boolean holes/channels, backers, mounts and inserts | `organic-mesh-functionalization` |
| exact solids, threads, fits, load paths and STEP authority | `functional-3d-design` |
| textured GLB to physical filament bodies/3MF | `multicolor-fdm-design` |
| rights graph, licenses and commercial release history | `commercialize-3d-models` |

Do not duplicate those authorities here. Load the sibling skill whose decision is active.

## Decide autonomously how Step1X helps

Choose the smallest Step1X scope that reduces design effort without surrendering functional control:

1. **Whole object** — only for appearance-dominant, low-risk objects whose functional features can be rebuilt or validated afterward. A raw Step1X output is never automatically a finished product.
2. **Component** — preferred for an ornament, grip skin, creature/head, decorative shell, ergonomic free-form insert, or other organic region bounded by a CAD-owned interface.
3. **Sacrificial preform** — preferred when Step1X supplies massing and surface character, then the agent trims a declared edit band and adds exact cavities, channels, holes, eyelets, fastener seats, threads, soles, flanges, or cores parametrically.
4. **Do not use Step1X** — when a profile, revolve, loft, primitive, height map, scan, or ordinary CAD feature is simpler and more controllable; or when generated uncertainty would enter a safety-critical surface or load path.

Read [examples/hybrid-recipes.md](examples/hybrid-recipes.md) only when selecting among these patterns.

## Non-negotiable rules

- A single-image output contains synthesized depth and hidden geometry. Label it `generated proposal`, not measured reconstruction.
- Keep the source image, image-generation prompt/record, geometry GLB, textured GLB, API schema and run manifest immutable.
- Do not ask Step1X to create exact dimensions, wall thickness, clearances, mating surfaces, seals, snaps, bearings, screw threads, text, logos, or certified load paths.
- Create sacrificial excess around future interfaces and protect the visible region from later Booleans/remeshing.
- Treat GLB as a scene/visual mesh, not a slicer-ready or CAD-native manufacturing authority.
- Establish physical scale and semantic orientation from the design contract after generation. Never trust the generated apparent size merely because glTF declares metres.
- Do not rename or directly convert a dense triangle GLB to STEP and call it editable CAD. Reconstruct exact surfaces/features or retain a mesh-plus-CAD hybrid.
- Queue one generation at a time. The two GPUs split one pipeline; they do not make concurrent jobs safe by default.
- A container or image may exist while the models are stopped or still loading. Before every submission, run the bundled `status` check and require `safe_to_submit_generation: true`; container state alone is insufficient.
- Expect a geometry-plus-texture request to take several minutes, including possible queue time. A quiet blocking client is not by itself a hang; inspect the service/container status before retrying or cancelling.
- Preserve failure records. A rendered preview or successful API response is not topology, printability, or license clearance.

## Workflow

### 1. Freeze the contract before generating

Complete the applicable functional requirements and concept gates first. For a component or preform, require:

- semantic component ID and intended role;
- target envelope and at least one authoritative physical datum;
- project front/up axes and symmetry policy;
- protected visible region, editable seam band and functional keep-outs;
- required silhouette/negative spaces and forbidden geometry;
- downstream route and acceptance checks.

If these are absent, load `decompose-printable-designs` and create them before invoking Step1X.

### 2. Create or prepare one generation plate

Load `imagegen` when generating or editing the raster input. Prefer one isolated, fully visible object on a transparent PNG, centered with margin, broad diffuse light and modest perspective. Exclude scenery, cast shadows, hands, stands, labels and nearby components.

Generate critical interfaces as simple sacrificial stock, not visual promises of precision. Read [references/image-input.md](references/image-input.md) for prompt templates, alpha/background handling and deterministic preprocessing.

### 3. Confirm loading, then freeze the runtime

Check model readiness before creating a run directory or submitting work:

```bash
python scripts/step1x_client.py status \
  --url http://127.0.0.1:7861 \
  --report reports/step1x-status.json
```

Proceed only on exit code `0`, `status: ready`, and `safe_to_submit_generation: true`. Exit code `1` means not ready or not confirmed: follow `recommended_action`, wait while loading, and rerun the check. Exit code `2` means the API answered but is incompatible. Do not start a second container merely because loading takes several minutes.

Probe the live contract before a run:

```bash
python scripts/step1x_client.py probe \
  --url http://127.0.0.1:7861 \
  --report reports/step1x-api.json
```

For work that may be commercialized, capture the actual source worktree, Docker image, Python/PyTorch/CUDA versions, GPU inventory and model snapshot revisions:

```bash
python scripts/capture_step1x_runtime.py \
  --repo /home/stefan/Projekte/Step1X-3D \
  --url http://127.0.0.1:7861 \
  --output evidence/step1x-runtime.json
```

Read [references/runtime-api.md](references/runtime-api.md) only for service startup, exact local pins, endpoint details, device placement or troubleshooting.

### 4. Generate an auditable pair of GLBs

Use a new run directory. Baseline settings are guidance `7.5`, `50` inference steps, `400000` maximum geometry faces, `x` symmetry and `sharp` edges; change them intentionally and record why.

```bash
python scripts/step1x_client.py generate input.png \
  --output-dir organic/raw/step1x/run-001 \
  --runtime-profile evidence/step1x-runtime.json \
  --image-prompt-file evidence/input-prompt.txt \
  --input-record evidence/imagegen-record.json \
  --guidance 7.5 --steps 50 --max-faces 400000 \
  --symmetry x --edge-type sharp
```

The command writes `geometry.raw.glb`, `textured.raw.glb`, an archived input, the exact API schema and `step1x-run.json` with hashes and parameters. The raw geometry GLB is the preferred shape master. In the current app, the textured path is made from a reduced working mesh and is primarily the appearance master.

Generate multiple candidates only when ambiguity warrants the compute. Select first by identity, massing, silhouette, negative spaces, seam reserve and keep-out compatibility; inspect texture last.

### 5. Normalize and hand off GLB explicitly

Inspect without changing the source:

```bash
python scripts/glb_to_print_mesh.py inspect \
  organic/raw/step1x/run-001/geometry.raw.glb \
  --report reports/step1x-geometry-intake.json
```

Then choose one of these routes:

- keep GLB for textured review or Blender mesh work;
- register and functionalize it with `organic-mesh-functionalization`;
- rebuild authoritative functional regions with `functional-3d-design` and retain STEP for those solids;
- derive a geometry-only STL after explicit scale/orientation/repair, then import it into the destination slicer and save a verified 3MF project;
- route the textured GLB through `multicolor-fdm-design` when visual texture must become physical filament regions.

Read [references/glb-handoff.md](references/glb-handoff.md) before any manufacturing export. It defines axis/unit handling, STL/3MF/STEP responsibilities and conversion acceptance.

### 6. Validate and record the derivation

Run the sibling mesh, geometry, slicer and physical gates appropriate to the product. Record every registration matrix, repair, remesh, Boolean, CAD replacement and export hash as a derivative of `step1x-run.json`.

For a commercial candidate, load `commercialize-3d-models`, read [references/commercial-and-research.md](references/commercial-and-research.md), and attach the run record to its provenance history. Step1X code and weights are Apache-2.0 in the verified configuration, but SDXL, background removal, input rights and downstream infringement/safety remain separate gates.

## Completion criteria

A Step1X handoff is complete only when:

- the selected use pattern and authority boundary are explicit;
- input image and prompt/edit history are retained and hashed;
- service schema, runtime profile, parameters and both raw GLBs are retained and hashed;
- hidden geometry, scale and orientation are labelled rather than assumed;
- the chosen GLB-to-CAD/mesh/3MF route is stated;
- topology, functional, slicer and physical checks are either passed or plainly blocked;
- commercial candidates link the Step1X run into the commercial evidence workspace.
