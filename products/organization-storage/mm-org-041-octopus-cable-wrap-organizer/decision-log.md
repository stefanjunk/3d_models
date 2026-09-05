# MM-ORG-041 decision log

## 2026-09-04 — Product intake and generative design phase, revision 0.1.0

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 1 | Implement research SKU-331 as a new product MM-ORG-041 | Highest trend score (90) in the Step1X generative block with a genuine functional interface, K1 criticality and a clean IP basis from an own prompt | SKU-378/379 (C3, higher complexity); character and figurine rows (likeness and IP exposure) |
| 2 | Allocate MM-ORG-041 in `organization-storage` | Commercial purpose is desk cable organization; MM-ORG-040 was the highest used number in both the portfolio CSV and the live folders | A new family (untruthful); MM-DEC or MM-TOY (misstates the product's job) |
| 3 | Use Step1X as **sacrificial preform**, not whole-object | The octopus body supplies massing and surface character; the cable channels are functional and must stay CAD-owned | Whole-object (surrenders functional control); component-only (the body *is* the product envelope) |
| 4 | Cap readiness at R2 | Cable outer diameters are a declared design range carried from the research row. No cable was measured, so the retention contract is E1 and it is the weakest evidence link | Claiming R3 (would require measured or officially published cable nominals that do not exist here) |
| 5 | Set G2 to WARN rather than PASS | Honest: critical interface evidence is insufficient. The user auto-approved workflow gates, which is an approval of *proceeding*, not a substitute for absent measurement evidence | G2 PASS (fabricates evidence) |
| 6 | Lane C, GO_WITH_CONTROLS | C2 + K1 permits iterative engineering; controls are that the mesh is labelled a proposal, all functional dimensions are re-created parametrically, and no fit/retention/stability claim is published before the coupon passes | Lane B (needs R>=3); CONCEPT_ONLY (would block the requested build) |
| 7 | Approve requirements and concept in this phase | Explicitly instructed by the product owner ("auto approve alle gates") | Leaving them pending as MM-ORG-040 did |
| 8 | Keep commercial release BLOCKED | The Step1X-3D upstream licence conflict excludes the EU and is a third-party legal fact that no local approval can clear | Treating the owner's gate approval as licence clearance |

## 2026-09-04 — Generative step blocked

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 9 | Stop before generation and stage the prompt instead | No image-generation capability existed in this session: no `imagegen` skill in the repository, no image tool in the agent toolset, and no Stable Diffusion / SDXL checkpoint cached locally or in the Step1X container. The Step1X endpoint is strictly `input_image_path`-conditioned with no text-to-3D path. | Procedurally drawing an octopus silhouette (would yield a poor mesh and falsify "own imagegen prompt" in the IP basis); using a photograph or a third-party render (breaks the recorded IP basis); downloading an SDXL checkpoint (network and dependency install are `ask` under the autonomy policy, and it adds an unreviewed licence to the chain) |
| 10 | Set the autonomy ceiling to `autonomous-to-digital-candidate` | Confidence is LOW_UNKNOWN and G2 is WARN. Reaching a print candidate requires the measured-cable evidence in `next_actions` priority 1, which is human work. | `autonomous-to-print-candidate` as used by MM-ORG-040, whose readiness was R3 |

## 2026-09-04 — Image generation route authorized, autonomy policy widened

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 11 | Route A: generate the plate with Codex CLI's built-in `image_gen__imagegen` tool | Available now under existing ChatGPT auth, no new secret and no new dependency. The Step1X skill's own `references/image-input.md` already cites the OpenAI image guide as a primary source, so this is the intended generator. Owner-instructed 2026-09-04. | Route B, the OpenAI Images API with `gpt-image-1` — technically better (`size`, `background=transparent`, `output_format` are enforceable) but needs an API key that is not stored; deferred as the target route. Route C, a local SD/SDXL checkpoint — nothing cached and it adds an unreviewed licence. |
| 12 | `tool_policy.network` raised to `allow`; `external_upload` stays `ask` | The schema offers no `allow` for `external_upload`, and it should not: text-prompt generation is a network call that uploads no repository file, whereas an imagegen **edit** with `referenced_image_paths` does upload one. Encoding the permission as `network: allow` grants exactly the authorized capability and keeps edits gated. | Setting `external_upload: ask` to a permissive value (impossible in the schema) or inventing a custom `tool_policy` key (blocked by `additionalProperties: false`) |
| 13 | `mode` corrected to `custom`, `autonomy_ceiling` to `guided`, stage IDs reduced to the schema enum | The previous policy was schema-invalid: `autonomous-to-digital-candidate` is not a valid mode or ceiling, and `generative-mesh` / `cable-measurement` are not valid stage IDs. `guided` is the honest ceiling while G2 is WARN and confidence is LOW_UNKNOWN. | Keeping the invented values; claiming `autonomous-to-print-candidate` |
| 14 | `authorization.scope` left at `workflow-stages-only` | The schema pins that field to the literal string, so the delegation scope cannot be widened there. The image-gen authorization is expressed in `tool_policy` and recorded here and in `CLAUDE.md`. | Editing the schema to accept a wider scope |
| 15 | TOOL-0002 terms recorded as ChatGPT Pro, `commercial_use: unknown` | The owner stated a ChatGPT Pro subscription. Applicable terms are the plan terms plus the Codex CLI layer, not the API terms; whether they permit commercial use of the output for a sold product is unverified. Recording `unknown` rather than asserting clearance. | Recording `yes` on the assumption that a paid plan implies commercial output rights |

## 2026-09-04 — Mesh repair, orientation correction and channel geometry

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 16 | Voxel remesh rejected after trial | Produced watertight output but six separate blobs and lost the bottom (height 65 → 55.8 mm, z-min 8.1). OpenVDB needs closed input surfaces; the nine Step1X shells only touch, they do not overlap. Report kept at `reports/mesh-02-voxel-remesh.json`. | Accepting it; raising the voxel size to bridge gaps, which would have cost more silhouette |
| 17 | Screened Poisson depth 8 chosen | Reconstructs a closed surface from oriented normals — the standard fix for an open AI mesh. Depth 10 exceeded 900 s and was killed; the cost was the point-cloud normal estimate (`k=16`), not Poisson. `compute_normal_per_vertex()` does the same job in 2 s. Depth 8 finished in 168 s and preserved the dimensions to 0.03 mm. | Depth 10 (no measurable benefit for a smooth blob at this size) |
| 18 | Accept genus 0 after repair | Poisson closed the open tentacle-curl loops. This is brief-conformant, not a defect: the prompt asked for "generous solid stock inside every tentacle curl where cable channels will later be cut". The channels are CAD-owned. | Treating it as a reconstruction failure and regenerating |
| 19 | **Orientation error found and corrected** | The model was built head-down: glTF `+Y up` needs **+90°** about X to reach product `+Z up`, and I applied −90°. Detected only by rendering orthographic views — the numeric gates all passed on the inverted model. Corrected to net +90°. | Trusting the numeric gates alone; they cannot see orientation |
| 20 | Flat base cut at z = 4.0 mm, CAD-owned | `IF-EXT-MEC-SUP-PLN-001` names the flat underside as a CAD datum; the generator was never its authority. In correct orientation the cut yields 10 contact pads, 935 mm², tipping angle **64.6°** against the 10° in AC-STABILITY-001. In the inverted model the same cut gave only 30.3° — the error was costing real stability. | z=2 (224 mm², weak bed adhesion); z=0.5 (20 mm², unusable) |
| 21 | Channels as radial grooves, not tangential bores | A tangential 80 mm slot severed tentacle tips: component count rose 1 → 3 and the `--max-components 1` gate failed. A radial groove notches the arm without cutting it in two; component count stayed at 1 through all twelve Boolean steps. | Tangential through-channels |
| 22 | Six channels at the probed tentacle sites | An unconstrained probe put all six at r = 30 mm — the head dome, which is wrong per the design. Restricting the search to r 44–62 mm found the real tentacle arms with 27–32 mm of vertical material. Sites: 0°, 60°, 120°, 185°, 240°, 300°, alternating 4 mm and 6 mm nominal cable. | Head-dome placement; fewer channels |
| 23 | Boolean with per-operand healing | `manifold` rejects non-volume operands and only accepts two meshes per call. Healing every operand (`merge_vertices`, degenerate/duplicate removal, `fix_normals`, hole fill on failure) and subtracting one cutter at a time succeeded where a batch union failed. | Unioning the cutters first (`Not all meshes are volumes`); installing `mapbox_earcut` for `slice_plane(cap=True)`, which is a dependency install |

## 2026-09-04 — Slicing to a print candidate

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 24 | Absolute paths for the slicer adapter | The first run failed with exit 253 and the diagnostic `No such file`. AnycubicSlicerNext runs in an isolated `--datadir`, so relative source and profile paths do not resolve. With absolute paths the same command sliced successfully. | Assuming the exit code meant a bad mesh or profile |
| 25 | Keep the pinned baseline slice as a non-recommended record | The hashed R3 baseline has `enable_support = 0` and the slicer warned about floating regions. Measurement: 9003 mm² of overhang beyond 30°, 24.5 % of the surface, 2027 mm² of it above z = 10 mm. That would print unsupported at the tentacle undersides. | Deleting the run; silently editing the pinned baseline |
| 26 | Support variant as a product-local derived profile | `design-spec.yaml` states `supports: buildplate only`, which contradicts the baseline's `enable_support = 0`. Rather than modify a hashed R3 baseline, the four support keys were changed in a product-local copy. Result: adapter PASS, slicer warning cleared, 90.60 g and 5h 47m against 77.43 g and 4h 25m. | Editing `process-0p20-petg-tool-k3max.json` in place, which would break the pin every other product depends on |
| 27 | No printer upload, no print start | AGENTS.md section 3: the adapter may export local files only; upload and start need separate explicit human action. | Sending the G-code to the printer |

## 2026-09-04 — In-use concept image

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 28 | Context/in-use concept image generated (owner choice, variant 2) | Needed for catalogue and design communication; the registered concept asset is the Step1X input plate, which deliberately omits the cable channels and is not a product concept. | Variant 1, the isolated product-render style, which would have stayed closer to the built geometry |
| 29 | Text-only prompt, no reference-image upload | Sending `reports/render-08-iso.png` as `referenced_image_paths` would have raised fidelity, but it uploads a repository file and the product policy sets `external_upload: ask`. The geometry was instead described in text from measured values, keeping the run inside `network: allow`. | Uploading the render without asking |
| 30 | Filed as a communication asset, not as the concept-gate asset | The image was created *after* the geometry, so it cannot be the asset the concept gate was approved on. `workflow.concept_approval.asset` stays `organic/reference/octopus-preform-plate-001.png`. | Overwriting the concept asset with the nicer picture |
| 31 | Three geometry deviations recorded rather than retouched | The image shows grooves near the tentacle tips that read as almost severing them, rounded tips instead of the ten flat contact pads, and stubbier tentacles. Recording the gap is more useful than iterating the prompt until it merely looks right. | Regenerating until the picture matches; presenting it as accurate |

## 2026-09-05 — Existing product resumed and regenerated, revision 0.2.0

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 32 | Resume `MM-ORG-041` rather than allocate another Octopus SKU | The owner corrected that the Octopus already exists. `PORT-110` and the live product folder contain the complete earlier chain. | Creating a duplicate from research SKU-331 |
| 33 | Keep v0.1.0 historical and regenerate geometry as run-005 | The old run-002 records pre-cleanup commit `f19046a` and a textured output, so its licence block cannot be relabelled away. Run-005 records clean fork commit `4b6da92`, one geometry return and client 1.4.2. | Retroactively treating old artifacts as post-cleanup; deleting the historical evidence |
| 34 | Rebuild the base and channel Booleans on the new mesh | The new Step1X exporter produces a different organic surface; old cutter placement created two components and failed. Six new radial cutters were located against run-005 and retained one watertight component. | Reusing the old manufacturing STL or accepting the failed legacy placement |
| 35 | Select the 100k-face manufacturing candidate | It passes 60k-sample-per-direction exact-triangle regression at p95 0.0083 mm and max 0.0242 mm, reduces triangles by 73.87 percent, and changes exact-profile time/extrusion by less than 0.10 percent. | 200k variant, which adds no slicer benefit; 382744-face baseline, which needlessly retains mesh weight |
| 36 | Move the Step1X product gate from BLOCK to WARN, not PASS | The active chain no longer executes Hunyuan-derived code or a texture stage. Image-generator terms, upstream training provenance, CLIP-config licence, disclosure and human release gates remain open. | Keeping an obsolete run-specific block; declaring full commercial clearance |
| 37 | Keep commercial release blocked | Mesh and slicer checks are digital evidence only. Cable measurement, retention, jacket-cycle, edge, stability, marking, outgoing licence and human approval are absent. | Publishing v0.2.0 directly to metriCreate |

## 2026-09-05 — Mandatory whole-product concept image

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 38 | Add `concept-product-v0.2.0-r1.png` as the Gate 0B review asset | The owner requires a concept image for every product even when design gates are auto-approved. The image uses the current channel render and shows slack cables in the product. | Continuing to use the isolated Step1X preform plate as the product concept |
| 39 | Reopen concept approval as `pending` | The prior approval predates this exact image, while the current validated autonomy policy assigns the concept stage to a human. Creation does not imply approval. | Backdating approval or treating the owner's request to create the image as approval of its depiction |
| 40 | Record the reference upload, prompt, output and hashes | The image edit sent the own product-local render to the configured provider under the owner's explicit request; traceability and the unresolved output terms remain visible. | Treating the edit as text-only generation or silently clearing the commercial gate |
