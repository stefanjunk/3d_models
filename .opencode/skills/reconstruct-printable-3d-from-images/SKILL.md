---
name: reconstruct-printable-3d-from-images
description: Design, reconstruct, validate, and prepare printable 3D models from one or more reference images. Use when an image, drawing, concept render, product photo, scan set, or turntable should become a measured or plausible 3D-printable object; when extracting design requirements, silhouettes, profiles, dimensions, shapes, relief, textures, colors, and uncertainty; when choosing parametric CAD, Blender, photogrammetry, single-image AI, or a hybrid workflow; when implementing in OpenSCAD, CadQuery, FreeCAD, or Blender; or when comparing matched renders with source images, planning image/mesh resolution and memory, auditing meshes, checking printability, and producing STL, 3MF, STEP, or GLB deliverables. Cover toys, utilities, household objects, image cleanup, camera and scale calibration, hidden-geometry assumptions, wall thickness, tolerances, slicer validation, and physical test prints.
---

# Reconstruct Printable 3D from Images

Turn reference imagery into an evidence-backed model, not an unlabelled guess. Separate visual fidelity, geometric correctness, functional requirements, and printability, then validate each independently.

Resolve every bundled `assets/`, `references/`, and `scripts/` path relative to the directory containing this `SKILL.md`. Command examples assume that directory is the current working directory; otherwise prefix each path with the resolved skill root.

## Non-negotiable rules

1. Treat a single image as incomplete evidence. Never claim that it determines scale, depth, hidden surfaces, wall thickness, material, or function.
2. Label every requirement as `observed`, `measured`, `inferred`, `assumed`, or `requested`; attach a source and confidence.
3. Preserve the original images. Create derivatives for masking, tracing, color sampling, and edges; never replace the evidence with an enhanced image.
4. Separate shape, surface relief, texture, color, material, lighting, and cast shadows. Do not convert every visible pixel variation into geometry.
5. Prefer measured parametric geometry for mating, load-bearing, ergonomic, or safety-critical features. Use generated or sculpted meshes for appearance-dominant organic regions.
6. Match camera projection and pose before judging a model against a photo. A similar render from an unmatched camera is not validation.
7. Validate at the intended physical size, process, material, nozzle/pixel size, layer height, orientation, and slicer settings. Avoid universal minimum-feature claims.
8. Keep units explicit and apply transforms before export. Retain an editable source, a print mesh, and a validation report.

## Workflow

### 1. Establish the evidence contract

Ask only for missing facts that materially change the route:

- target size or one known dimension;
- intended function, loads, contacts, moving or mating parts;
- print process, material, machine/nozzle or resin pixel size, and orientation constraints;
- available front/side/top/back views, turntable, video, or additional photos;
- required output: editable CAD, editable mesh, textured asset, print mesh, or all of them.

If answers are unavailable, continue with bounded hypotheses. Offer variants for materially different hidden geometry instead of silently selecting one.

Copy `assets/reconstruction-brief.yaml` into the project and fill it throughout the work. Read [references/core-method.md](references/core-method.md) for the evidence ledger, acquisition guidance, shape decomposition, and appearance extraction.

### 2. Audit and preprocess the images

Run the deterministic preprocessor on each image before tracing or generation:

```bash
python scripts/preprocess_image.py input.png --output-dir evidence/input \
  --background auto --target-width-mm 120 --effective-feature-mm 0.6
```

Inspect the normalized image, silhouette, edge image, palette, and JSON report. Correct EXIF orientation, lens distortion, white balance, perspective, background, occlusion, and scale only when justified. Keep hard-edged masks for measurement and soft masks for appearance work.

Reject or qualify evidence with motion blur, aggressive depth-of-field, clipped highlights, reflections, strong perspective, missing scale, or inconsistent views. Prefer obtaining better views over hallucinating geometry.

### 3. Extract a design specification

Create a canonical coordinate system and decompose the object into:

- bounding dimensions and proportions;
- primary primitives, profiles, cross-sections, symmetry, and repeated elements;
- openings, negative spaces, part boundaries, seams, and interfaces;
- edge character: sharp, chamfered, filleted, soft, faceted;
- surface detail split into geometry, relief, texture/color, or lighting;
- functional requirements, print requirements, and unresolved hidden regions.

Record landmarks in normalized image coordinates and physical dimensions where scale exists. Use multiple views to cross-check each dimension. Never measure depth from an uncalibrated perspective image as though it were orthographic.

### 4. Select the reconstruction route

| Evidence and goal | Primary route | Typical tools |
| --- | --- | --- |
| Dimensioned, symmetric, prismatic, revolved, or functional | Parametric reconstruction | CadQuery, FreeCAD, OpenSCAD |
| Organic or stylized appearance from one/few images | AI draft or sculpt, then engineering cleanup | Image-to-3D model, Blender, hybrid CAD |
| Real object with many overlapping photographs | Photogrammetry, then scale/repair | COLMAP or Meshroom, Blender, MeshLab |
| Flat logo, silhouette, cookie cutter, lithophane, or relief | Vector/height-map reconstruction | Inkscape/OpenCV, OpenSCAD, CadQuery, Blender |
| Functional core plus ornate or organic exterior | Hybrid BRep plus mesh | CadQuery/FreeCAD plus Blender or mesh Boolean tools |
| Color or material only, not printable geometry | UV/PBR or discrete material bodies | Blender/3MF-aware pipeline |

Read [references/ai-photogrammetry-hybrid.md](references/ai-photogrammetry-hybrid.md) before using generative reconstruction or photogrammetry. Read only the selected tool guide:

- [references/tools-openscad.md](references/tools-openscad.md)
- [references/tools-cadquery.md](references/tools-cadquery.md)
- [references/tools-freecad.md](references/tools-freecad.md)
- [references/tools-blender.md](references/tools-blender.md)

### 5. Plan detail and memory before high resolution

Base geometry sampling on the smallest physically meaningful feature, not on source-image pixel count. Keep texture resolution independent from mesh resolution.

```bash
python scripts/plan_resolution.py --width-mm 120 --height-mm 80 \
  --process fdm --nozzle-mm 0.4 --effective-feature-mm 0.6 \
  --memory-gb 8
```

Read [references/resolution-memory-printability.md](references/resolution-memory-printability.md) for formulas, height-map triangle growth, mesh tessellation, AI VRAM, decimation, and printer-aware defaults. Use a coarse blockout for camera and proportions, a medium mesh for iteration, and final detail only after silhouette approval.

### 6. Model in confidence order

1. Lock units, scale, axes, origin, and symmetry.
2. Match bounding proportions and primary silhouettes.
3. Match cross-sections, negative spaces, openings, and interfaces.
4. Add secondary forms, fillets, seams, and repeated features.
5. Engineer wall thickness, clearances, bases, joints, drainage, supports, and orientation.
6. Add printable relief; keep sub-resolution detail in texture or omit it.
7. Add colors/material assignments only after geometry stabilizes.

Checkpoint after each level. Do not let high-frequency texture conceal incorrect massing.

### 7. Compare matched views

Render the same source views with the same projection, focal length, camera pose, crop, lighting class, and transparent/neutral background. In Blender, use the bundled canonical renderer for initial views:

```bash
blender --background --python scripts/blender_render_views.py -- \
  --model model.glb --output-dir renders --views front,right,back,left,top,iso \
  --resolution 768 --projection orthographic
```

For a calibrated photo, replace the canonical camera with the recovered camera. Compare source and render without geometric alignment first; allow only a documented crop/scale alignment for diagnosis:

```bash
python scripts/compare_views.py source.png renders/front.png \
  --source-mask evidence/source/silhouette.png \
  --candidate-mask renders/front-mask.png --output-dir comparison/front
```

Use silhouette IoU, boundary distance, landmarks, masked color error, and SSIM as diagnostics, not as a single pass/fail score. Read [references/validation-comparison.md](references/validation-comparison.md) for the full checklist and acceptance gates.

### 8. Audit the mesh and the print

Run a structural audit when `trimesh` is available:

```bash
python scripts/mesh_audit.py model.stl --output report/mesh-audit.json
```

Then inspect in the modeling tool and slicer. Check watertightness, outward normals, components, self-intersections, degenerate faces, wall thickness, clearances, unsupported regions, trapped resin/support, bridges, first-layer contact, and units. Slice at the real profile and review every layer around thin walls, openings, fine details, and moving interfaces.

Print a coupon for relief, texture, fit, snap, or clearance uncertainty before a full-size print. Measure the prototype and update the requirement ledger with actual deviations.

### 9. Deliver an auditable package

Include:

- untouched source images and derivative evidence images;
- completed reconstruction brief with assumptions and confidence;
- editable master model and all linked profiles/textures;
- print-oriented export with units and orientation;
- matched renders, comparison reports, mesh audit, slicer profile/preview, and test results;
- a short list of unresolved or artistically invented regions.

Prefer STEP for editable solids, GLB for textured appearance, 3MF for print units/material assignments where the downstream tool supports them, and binary STL only for geometry-only compatibility. Verify the receiving slicer rather than assuming a file format preserves every color or material feature.

## Worked examples

Read [references/worked-examples.md](references/worked-examples.md) for end-to-end examples covering a stylized toy dinosaur, a wall-mounted cable clip, and a ceramic planter.

## Research basis

Read [references/research-sources.md](references/research-sources.md) when claims, versions, licenses, model hardware requirements, or tool capabilities need verification. Prefer linked official documentation and original papers; re-check rapidly changing AI tools before recommending or installing them.

For OpenCode placement, discovery, permission, and portability checks, read [references/opencode-installation.md](references/opencode-installation.md).

## Bundled scripts

- `preprocess_image.py`: preserve/normalize an image and derive silhouette, edges, palette, quality signals, and a resolution hint.
- `plan_resolution.py`: estimate image/height-map sampling, triangle count, serialized size, and working-memory range.
- `compare_views.py`: produce overlays, differences, silhouette metrics, boundary diagnostics, and optional SSIM.
- `mesh_audit.py`: inspect mesh scale, components, watertightness, winding, volume, and complexity.
- `blender_render_views.py`: render repeatable canonical views for comparison.

Install only dependencies required for the chosen scripts; see `scripts/requirements.txt`. Do not install packages or mutate the user's environment without authorization.
