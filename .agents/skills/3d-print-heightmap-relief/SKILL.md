---
name: 3d-print-heightmap-relief
description: Plan, generate, preprocess, scale, place, rebuild, and validate continuous-tone image relief for 3D-printable engraving and embossing when an image genuinely carries local height. Preserve 16-bit grayscale masters, generation-time PPI, physical aspect ratio, and surface scale across flat and curved geometry. Use design-printable-surface-textures first for repeating carbon/wood/fabric patterns, primarily optical or material effects, slicer textures, vector/procedural relief, and custom surface toolpaths.
license: MIT
metadata:
  version: "2.4.0"
  domain: "3d-printing"
  units: "mm"
  master_format: "16-bit grayscale PNG"
  aspect_model: "physical-coordinate invariant"
---

# 3D print heightmap relief

Use this skill when an image, logo, writing, portrait, photograph, or authored depth map must become continuous-tone engraving or embossing on a 3D-printable object.

For carbon weave, wood grain, fabric, stone, metal, leather, floral patterns, or other repeating/optical surface appearance, use `design-printable-surface-textures` first. Enter this heightmap workflow only after the representation decision shows that localized continuous height is necessary; otherwise retain vector/procedural, slicer/toolpath, material, or finish authority.

The folder follows the standard `SKILL.md` plus relative-resource layout used by ChatGPT Work, OpenCode, and other Agent-Skills-compatible runtimes. Run bundled scripts with Python 3 from the skill directory or by absolute path.

## Read only what the task needs

- Physical aspect ratio and non-square target sampling: `references/aspect-ratio-and-physical-coordinates.md`
- Source generation and source-master PPI: `references/ai-generated-source-masters.md`
- DPI/PPI, nozzle/layer sampling, and resizing: `references/dpi-and-pixel-resolution.md`
- Continuous grayscale and 16-bit height resolution: `references/bit-depth-and-height-resolution.md`
- Texture versus single-subject placement: `references/image-types-and-placement.md`
- Plane/cube/cylinder/rounded box/sphere/ellipsoid/freeform mapping: `references/surface-mapping.md`
- Replaceable source images and one-command rebuilding: `references/rebuildable-jobs.md`
- Persistent job fields: `references/relief-job-format.md`
- Relief depth, visibility, and wall safety: `references/depth-visibility-and-structure.md`
- OpenSCAD/CadQuery/FreeCAD/Blender guidance: `references/tool-guidance.md`
- Triangle budgets, adaptive meshing, simplification, and slicer-load gates: `references/mesh-complexity-and-simplification.md`
- Agent checklist: `references/agent-checklist.md`
- Examples: `references/examples.md`

## Hard rules

1. **Preserve PHYSICAL aspect ratio by default.** For a recognizable image, the invariant is `placed_width_mm / placed_height_mm`, not raw PNG `pixel_width / pixel_height`.
2. **Never independently scale X and Y for a subject unless the user explicitly authorizes distortion.** `stretch` must fail under `aspect_policy=preserve`.
3. **Non-square build sampling is allowed and often correct.** A 0.20 mm X pitch and 0.12 mm Y pitch intentionally create a raster whose raw pixel aspect differs from the physical image aspect.
4. **Never "correct" a geometry heightmap merely because it looks stretched in a normal image viewer.** Generate a separate square-pixel preview for human inspection. Never use that preview as geometry input.
5. **Fit in millimetre space first, rasterize second.** `contain`, `cover`, and crop compute one uniform physical scale before converting X/Y distances to pixels.
6. **Use actual surface distance for curved mappings.** Cylinder horizontal distance is arc length `s = R*theta`; rounded-box horizontal distance is perimeter arc length; arbitrary UVs require distortion review.
7. **Do not reduce continuous relief to two or a few grayscale levels unless explicitly requested.** Processed source/build masters remain 16-bit grayscale by default.
8. **For AI-generated sources, request a physical authoring size, isotropic authoring PPI, and matching native pixel dimensions.** Persist requested and actual values.
9. **Keep the source master immutable and rebuild target images directly from it.** Never cascade resize from an old processed heightmap.
10. **Keep images replaceable.** Persist placement, printer, fit, aspect policy, and geometry command in a job JSON; rebuild a replacement with one command.
11. **Validate before geometry generation.** For non-texture subjects, default physical aspect tolerance is about 0.75%; stop if exceeded rather than generating a large wrong mesh.
12. **Protect wall thickness.** If adequate visual depth is unsafe as engraving, emboss or thicken the wall instead of sacrificing structure.
13. **Treat target pitch as a printable-detail bound, not a command to triangulate every square millimetre uniformly.** Estimate the uniform-grid worst case, set a triangle budget, then use adaptive sampling or error-bounded simplification wherever the height field is locally flat.
14. **Never simplify by triangle percentage alone for production.** Use a physical error tolerance, lock seams/boundaries/interfaces, compare against the unsimplified reference, and revalidate topology, relief amplitude, wall reserve, bed contact, and slicer paths.
15. **Do not release a relief mesh on image checks alone.** Record triangle/file-size metrics and run the exact target slicer. A smaller STL is useful only when printable detail and functional geometry remain within acceptance limits.
16. **Give every persistent relief job explicit triangle, working-memory, mesh-file, and exact-slicer budgets before geometry generation.** A triangle limit without a RAM and slicer limit is incomplete.
17. **Keep the unsimplified reference/master mesh and optimized manufacturing mesh as separate immutable paths.** Never overwrite the reference with a candidate.
18. **Run geometry and slicer gates separately.** Surface error, volume, correlation, and contrast validate the mesh; layer paths, missing walls, short segments, import/slice time, and print estimates validate the manufacturing interpretation.

## Required coordinate model

Always distinguish:

```text
SOURCE SPACE
  source master, usually square pixels
          ↓ uniform physical placement
SURFACE SPACE
  millimetres on the intended surface patch  ← aspect invariant lives here
          ↓ independent fabrication sampling per surface axis
RASTER SPACE
  target heightmap pixels; pixel aspect may be non-square physically
          ↓ metric-aware mapping
3D SURFACE
  actual printed geometry; must recover SURFACE SPACE dimensions
```

A 2:1 physical image can legitimately have a 400×333 build raster if X and Y use different mm/pixel. The physical result is correct when `400*pitch_x / (333*pitch_y) ≈ 2`.

## Mandatory workflow

### 1. Classify image and surface

Image: repeating texture, logo/motif, text, person/animal/object, photograph, authored height/depth map.

Surface: plane/cube face, cylinder, rounded perimeter, cone/frustum, sphere/ellipsoid patch, multiple faces, arbitrary UV/freeform mesh.

Decide whether the image repeats or is placed once.

### 2. Establish the source physical aspect

For AI generation, define physical authoring width/height and isotropic PPI before generation. For a supplied square-pixel image with no physical metadata, its pixel width/height defines the natural source aspect.

If a generator returns the wrong raster aspect, do not stretch it into compliance. Register it with `contain` or controlled `cover/crop`, then warn.

### 3. Select the final surface patch in millimetres

For a single subject, choose a bounded patch where the subject remains readable. For a texture, define either its physical tile size or global mapping scale.

### 4. Select target print pitch

FDM starting points:
- surface axis printed mainly in XY: about `0.5 * nozzle_mm` per sample;
- surface axis running mainly in model Z on a side wall: about `layer_height_mm` per sample.

Resin: use actual XY printer pixel size and layer height as starting references.

### 5. Set the mesh-complexity budget

Read `references/mesh-complexity-and-simplification.md` and estimate the worst-case uniform mesh over the actual displaced patch, not the full part bounding box:

```bash
python scripts/relief_mesh_budget.py \
  --area-mm2 72000 --pitch-mm 0.30x0.30 \
  --process fdm --nozzle-mm 0.60 \
  --depth-mm 0.32 --layer-height-mm 0.30 \
  --memory-budget-gib 8 --max-mesh-mib 100 \
  --max-slicer-seconds 120
```

Use the script defaults as a conservative portable workflow policy: target at most about one million relief triangles per manufacturing part, require an explicit review above that, and stop above five million unless a measured slicer/memory benchmark justifies an override. These are interchange and workflow limits, not printer-resolution laws.

Prefer, in order: limit the relief to visible/applied regions; remove flat background; generate an adaptive height-field mesh; simplify the relief cutter with a physical error tolerance; then Boolean it into the exact functional base. Keep the 16-bit source/build masters regardless of the final triangle count.

### 6. Prepare target heightmap in physical coordinates

Use:

```bash
python scripts/prepare_heightmap.py source/source-master.png build/current-heightmap.png \
  --source-manifest source/source-master.png.source.json \
  --size-mm 80x40 \
  --pitch-mm 0.20x0.12 \
  --fit contain \
  --aspect-policy preserve \
  --image-class person \
  --preview build/current-heightmap.preview.png
```

The geometry file may look squashed in a square-pixel viewer. The preview must look correct.

### 7. Validate physical aspect before mesh/CAD work

```bash
python scripts/validate_aspect_ratio.py build/current-heightmap.png.json
```

Do not proceed after a failed validation unless the user deliberately approved distortion.

### 8. Map using surface distance

Read `references/surface-mapping.md`. On a cylinder, map image X to physical arc length. On a rounded box, map X to accumulated perimeter length. On spheres/ellipsoids, keep recognizable subjects on bounded low-distortion patches. On arbitrary meshes, inspect UV metric distortion or use a local surface patch.

### 9. Choose depth independently of grayscale precision

Increase visual strength through physical depth, image size, contrast/gamma shaping, or embossing—not posterization.

### 10. Generate, simplify, and compare the relief geometry

Generate the unsimplified reference/master mesh at its persistent artifact path, then create manufacturing candidates at separate paths. For FDM, start the tolerance sweep from `min(0.10*nozzle, 0.20*layer_height, 0.125*relief_depth, 0.05 mm)` as reported by `relief_mesh_budget.py`; it is a candidate, not approval. Protect functional CAD faces, relief boundaries, tile seams, intentional sharp creases, and the print-bed plane.

As starting acceptance values, require absolute volume change below 0.1%, relief-height correlation at least 0.98, robust relief-contrast loss below 5%, and RMS surface error no greater than 5% of nozzle diameter. Measure correlation and contrast on paired heights inside the actual relief mask, excluding unrelated flat background. Tighten these values for safety-, fit-, text-, seam-, or appearance-critical work.

Use `scripts/relief_mesh_acceptance.py` to gate externally measured reference/candidate metrics. Accept a simplified manufacturing mesh only when it remains manifold and single-body as intended, preserves the physical dimensions and wall reserve, passes the mesh gate, and improves triangle count or measured slicer handling meaningfully. Then run a separate exact-slicer gate; otherwise ship the reference mesh or improve generation rather than hiding a failed candidate.

### 11. Rebuild only from the source master

```bash
python scripts/rebuild_relief_job.py jobs/my-job/relief-job.json \
  --source replacement.png --register-source --run-geometry
```

The command must regenerate the build heightmap from the canonical source master, validate aspect, then run the configured geometry command.

### 12. If mapping is suspect, use the diagnostic image

```bash
python scripts/make_aspect_test_image.py aspect-test.png \
  --size-mm 80x40 --ppi 200 --marker-mm 20
```

Map this through the exact production pipeline. A 20 mm circle must remain physically circular and a 20×20 mm square must remain square in the final CAD/mesh. Remove diagnostic artwork for production.

## Helper scripts

- `plan_ai_source.py` — generation-time physical size/PPI/pixel brief.
- `register_source_master.py` — registers raw/generated art without silent anisotropic stretching.
- `prepare_heightmap.py` — physical-coordinate fit, 16-bit geometry map, aspect validation, square-pixel preview.
- `validate_aspect_ratio.py` — early failure gate before expensive geometry.
- `make_aspect_test_image.py` — known-size circle/square diagnostic.
- `surface_patch_metrics.py` — cylinder arc-length, rounded-perimeter, sphere, and ellipsoid local metric calculations.
- `init_relief_job.py` — initializes a source-swappable job.
- `rebuild_relief_job.py` — source replacement → master → target map → validation → optional geometry command.
- `recommend_relief_plan.py` — print-pitch, fit, aspect, wall/depth starting plan.
- `relief_mesh_budget.py` — worst-case triangle/file-size estimate, portable complexity gates, and process-aware simplification tolerance sweep.
- `relief_mesh_acceptance.py` — starting volume/correlation/contrast/nozzle-relative-RMS gate for externally measured reference/manufacturing meshes.

## Deliverable contract

Always report:
- source image class and provenance;
- source physical size/aspect and authoring PPI;
- target surface patch in mm;
- target X/Y pitch and PPI;
- geometry raster pixel size and raw raster aspect;
- physical pixel aspect;
- fit and aspect policy;
- reconstructed physical aspect and percentage error;
- 16-bit/continuous-tone status;
- preview path when target X/Y pitches differ;
- mapping model and seam/patch location;
- depth and remaining-wall assumptions;
- actual displaced area, estimated/actual triangle count, file size, peak working memory, and each explicit budget/gate result;
- separate reference/master-mesh and manufacturing-mesh paths plus comparison, budget, and slicer reports;
- adaptive-meshing method, protected regions, simplification tolerance and before/after error/relief metrics, or the recorded decision not to simplify;
- volume delta, relief-mask correlation, robust contrast loss, and nozzle-relative RMS result when a relief mesh is simplified;
- exact slicer/version/profile and before/after slicing time, estimated print time, and material when simplification or resampling is applied;
- replacement/rebuild command;
- warnings about crop, upscaling, UV distortion, poles, corners, or intentional aspect distortion.

## Deterministic validation handoff

Before release, load the sibling `validate-printable-3d-projects` skill and apply `assets/validation-profile.json`. Register the source image, 16-bit master, reference mesh, manufacturing mesh, slicer profile, G-code, and reports in `validation-project.json` with SHA-256 hashes. Run the declared mesh, mesh-comparison, G-code, 3MF, and external-report freshness checks. Preserve this skill's relief-specific aspect, depth, correlation, contrast, memory, and PPI checks as hashed external reports. Accept only machine-readable statuses; a required `NOT_RUN`, `REVIEW_REQUIRED`, stale report, or missing physical coupon blocks release.

At project start, read the project autonomy policy before changing artifacts. Record only `AUTO_APPROVED` or `BLOCKED` in the agent ledger and only for stages assigned to the agent. Never write `HUMAN_APPROVED`; physical coupons, safety, appearance, and commercial release remain in the separate human ledger. Workflow autonomy does not authorize dependency installation, upload, or printer start.
