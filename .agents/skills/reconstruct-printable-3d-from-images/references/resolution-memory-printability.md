# Resolution, memory, and printability planning

## Contents

1. [Resolution is physical](#1-resolution-is-physical)
2. [Select image and height-map sampling](#2-select-image-and-height-map-sampling)
3. [Estimate mesh growth](#3-estimate-mesh-growth)
4. [Plan texture and color separately](#4-plan-texture-and-color-separately)
5. [Plan CAD tessellation](#5-plan-cad-tessellation)
6. [AI and photogrammetry memory](#6-ai-and-photogrammetry-memory)
7. [Printability checks](#7-printability-checks)
8. [Efficient staged workflow](#8-efficient-staged-workflow)
9. [Worked calculations](#9-worked-calculations)

## 1. Resolution is physical

Do not use source image pixel count as mesh resolution. Define:

- target physical dimensions;
- smallest feature that matters to function or appearance;
- measured process capability in XY and Z for the chosen material/orientation;
- desired samples per smallest feature;
- acceptable chord/surface error;
- available RAM/VRAM and runtime.

Distinguish:

- **image resolution:** input evidence and texture detail;
- **geometry sampling:** profile points, height-map cells, voxels, mesh edge length;
- **printer XY capability:** effective line/spot/pixel behavior and material spread;
- **Z resolution:** layer height plus process/material behavior;
- **dimensional accuracy:** deviation of printed dimensions, not pixel/voxel size;
- **minimum feature:** smallest reliable positive/negative feature in a defined orientation.

Nozzle diameter, resin pixel pitch, and layer height are useful inputs, not complete measures of output resolution. Measure a coupon with the actual printer, material, profile, and orientation when detail matters.

## 2. Select image and height-map sampling

Let:

- `L` = physical length in millimeters;
- `F` = smallest meaningful printable feature in millimeters;
- `S` = samples per feature, normally 2–4 for a band-limited map;
- `P = F / S` = target sample pitch in millimeters;
- `N = ceil(L / P) + 1` = samples along that length.

Use 3 samples per feature as a practical planning start, then test. Increase sampling when preserving sharp boundaries or doing repeated transformations. Decrease it when the source has no real detail, the process cannot reproduce it, or memory dominates.

For a two-dimensional height map:

```text
Nx = ceil(width_mm / pitch_mm) + 1
Ny = ceil(height_mm / pitch_mm) + 1
```

Keep the high-resolution source image. Create a filtered geometry map at `Nx × Ny`; do not permanently downsample the only texture source.

### Filtering

Before downsampling:

1. remove large lighting gradients not intended as relief;
2. linearize or define the intensity-to-height curve;
3. denoise only below the printable feature scale;
4. apply a low-pass filter appropriate to the target pitch;
5. downsample with an area/Lanczos method;
6. re-check edges and relief extrema.

Unfiltered subsampling aliases wood grain, fabric weave, and line art into random stripes or moiré. This is especially important for wrapped cylindrical textures.

### Height amplitude

Set emboss/engrave depth in millimeters independently of XY resolution. Features with height variation below one layer may quantize unpredictably in FDM; clearly visible relief often needs several layers, but exact visibility depends on slope, orientation, color, lighting, and material. Print a stepped relief coupon rather than hard-coding a universal depth.

For resin, distinguish nominal layer height from optical/material feature response. A fine Z layer does not imply the same XY accuracy or reliable unsupported microfeature.

## 3. Estimate mesh growth

### Height-map triangulation

For a regular `W × H` sample grid:

```text
triangles ≈ 2 × (W - 1) × (H - 1)
```

Examples:

| Grid | Approx. triangles |
| --- | ---: |
| 256 × 256 | 130,050 |
| 512 × 512 | 522,242 |
| 1024 × 1024 | 2,093,058 |
| 2048 × 2048 | 8,380,418 |
| 4096 × 4096 | 33,538,050 |

This excludes side walls, backing, duplicated seam vertices, modifiers, and temporary Boolean data.

### Serialized and working memory

Binary STL uses approximately:

```text
84 bytes + 50 bytes × triangle_count
```

Thus a two-million-triangle height map is roughly 100 MB as binary STL before filesystem compression. In-memory geometry is much larger because applications store vertex arrays, face indices, normals, attributes, acceleration structures, undo states, and modifier caches.

Use a planning range of roughly 80–240 bytes per triangle for a simple working mesh, then add application-specific copies. This is an estimate, not a guarantee. Sculpting, Boolean, remesh, UV, texture, or repair operations can multiply memory several times.

### Image buffers

Base buffer sizes:

```text
RGBA 8-bit:       W × H × 4 bytes
RGB float32:      W × H × 12 bytes
RGBA float32:     W × H × 16 bytes
```

Image pipelines often hold source, linearized, mask, edge, temporary, pyramid, and output buffers simultaneously. Budget 3–8 base-buffer equivalents for ordinary processing and more for feature pyramids or AI inference.

### Voxels

A dense cubic voxel grid grows as `N³`. Doubling linear resolution increases voxel count about eightfold. Prefer sparse/blocked representations when supported. For Blender voxel remesh, choose voxel size in physical units and estimate the bounding-box grid before applying it.

## 4. Plan texture and color separately

Texture resolution is governed by projected texel density and appearance requirements, not by nozzle diameter alone.

Keep separate targets:

- **Geometry map:** enough samples for printable relief/silhouette.
- **Base-color texture:** enough texels for viewing/painting or supported color printing.
- **Normal/roughness map:** for rendering only unless explicitly converted to geometry.

Example: a 1254-pixel wood image wrapped around a 300 mm circumference has about 0.239 mm per source pixel before tiling/cropping. That may be useful as a render or color texture. If the FDM process reliably reproduces only 0.6 mm relief features and the target is 3 samples per feature, a geometry map pitch of 0.2 mm is sufficient—about 1501 samples around the circumference. Tile the source seamlessly if its physical coverage is smaller; preserve grain direction across faces and rounded corners.

Do not interpret every dark wood line as an engraving valley. Remove illumination, decide which frequency bands become tactile relief, and print a coupon.

For multicolor printing, verify the entire 3MF/material pipeline. The 3MF specification supports color/material/texture extensions, but an individual CAD exporter or slicer may not implement them.

## 5. Plan CAD tessellation

Retain analytic BRep/parametric geometry as long as possible. Tessellate only for rendering/printing.

Choose linear/chord tolerance from:

- allowed surface deviation;
- smallest visible/functional curved feature;
- printer process capability;
- part size;
- slicer performance.

A useful starting principle is to make tessellation error materially smaller than the smallest reproducible feature, often around one-quarter to one-half of that feature, then inspect curves and file size. Do not treat this as a fixed standard.

Examples for experimentation, not universal defaults:

- ordinary 0.4 mm-nozzle FDM decorative/functional part: test 0.05–0.15 mm linear deflection;
- fine resin part: test 0.02–0.08 mm based on measured XY capability;
- very large gentle surfaces: allow larger absolute tolerance if no visible faceting;
- tiny gears/text: use project-specific tighter values only where necessary.

Use angular tolerance to control normals/segment direction on curvature. Compare silhouette and surface deviation across at least two tessellations. An export tolerance of 0.001 mm on a large model may generate a needlessly large mesh without improving the print.

## 6. AI and photogrammetry memory

### AI inference

Account separately for:

- model weights;
- activations and attention/sparse structures;
- input/background removal;
- mesh extraction;
- texture generation/baking;
- Blender or viewer memory after generation.

Official project figures at the time this guide was researched include about 6 GB VRAM for default TripoSR or Stable Fast 3D single-image inference, 10/21/29 GB for Hunyuan3D 2.1 shape/texture/combined, and at least 24 GB for TRELLIS.2. Re-check current repositories; quantization, low-VRAM modes, output resolution, and software versions change the result.

Use lower-resolution/shape-only inference first. Generate texture only for candidates that pass clay geometry review.

### Photogrammetry

Memory scales with image dimensions, image count, features/matches, source-view count, dense depth maps, and cache settings.

Reduce memory in this order when practical:

1. reconstruct a representative image subset;
2. cap feature/dense maximum image size while recording the factor;
3. reduce redundant images/source views;
4. lower cache sizes and accept more disk I/O;
5. split into overlapping clusters;
6. lower reconstruction/detail settings after identifying the bottleneck.

COLMAP documentation specifically exposes maximum image size, source-image count, feature/match limits, and dense cache controls. CPU fallback can consume substantial RAM and time.

## 7. Printability checks

Derive limits from the target process and verify with coupons.

### Geometry

- watertight, consistently wound closed volumes unless a supported special workflow is intentional;
- no accidental internal shells or self-intersections;
- walls and pins above measured reliable thickness/diameter;
- holes/channels compensated from measured results;
- clearances defined by assembly direction, material, size, and orientation;
- chamfers/fillets that survive tessellation and printing;
- stable base or designed supports;
- no trapped supports, powder, or uncured resin;
- drain/vent holes for hollow resin parts;
- bridging and overhangs checked in the chosen orientation;
- edges/tips safe for the intended handling context.

### Appearance

- important silhouette features survive at final scale;
- relief amplitude and line width pass a coupon;
- texture direction and seams remain coherent;
- color regions are large enough for the selected multicolor process;
- layer lines/support scars do not destroy the source-defining surface.

### Slicer

Review layer-by-layer:

- first occurrence and disappearance of every thin feature;
- number of perimeters through walls;
- gaps the slicer closes or omits;
- seam placement;
- bridge direction and support contact;
- small islands and fragile tips;
- color/tool transitions;
- estimated material/time only after geometry passes.

## 8. Efficient staged workflow

Use levels of detail:

| Stage | Geometry | Texture | Validation |
| --- | --- | --- | --- |
| L0 envelope | primitives, very low mesh | none | dimensions, camera, silhouettes |
| L1 primary | major sections/openings | flat colors | all source views |
| L2 secondary | fillets, seams, interfaces | medium | render metrics, functional checks |
| L3 print detail | printer-band-limited relief | final if needed | mesh/slicer/coupon |
| L4 archival/render | optional high mesh | high texture/PBR | appearance only |

Do not carry L4 geometry into the print workflow unless the printer and acceptance test justify it.

Use region-of-interest refinement: maintain fine sampling only around text, faces, interfaces, or sharp transitions. Keep flat/gentle surfaces coarse. Use adaptive tessellation, decimation with protected boundaries, or separate detail patches.

## 9. Worked calculations

### 120 × 80 mm FDM relief

Assume measured meaningful feature `F = 0.6 mm` and `S = 3`:

```text
P = 0.6 / 3 = 0.2 mm
Nx = ceil(120 / 0.2) + 1 = 601
Ny = ceil(80 / 0.2) + 1 = 401
T ≈ 2 × 600 × 400 = 480,000 triangles
binary STL ≈ 24 MB plus header/backing/sides
working mesh estimate ≈ 38–115 MB before modifier copies
```

This is a sensible starting map, not proof of print fidelity. Compare a 0.3 mm-pitch version and print a relief coupon.

### 100 × 100 mm source at 4096 pixels

The source sampling is about `0.0244 mm/pixel`. A 4096² height mesh would create about 33.5 million triangles, roughly 1.68 GB as binary STL and several gigabytes in memory. If the process resolves 0.5 mm features, a 0.167–0.25 mm geometry pitch is far more appropriate: roughly 401–601 samples per side. Preserve the 4096² image for texture/archive work.

### 50 × 50 mm fine resin relief

Assume a measured effective feature `F = 0.15 mm`, `S = 3`:

```text
P = 0.05 mm
N = ceil(50 / 0.05) + 1 = 1001
T ≈ 2,000,000 triangles
```

This already creates a heavy mesh. Use adaptive refinement or a CAD/displacement representation until final export. Test whether `F = 0.20 mm` is visually equivalent; that reduces the grid to about 751² and triangles to about 1.125 million.

Run `scripts/plan_resolution.py` for repeatable calculations and keep its JSON output with the project.
