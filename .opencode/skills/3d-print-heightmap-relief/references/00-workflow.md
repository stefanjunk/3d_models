# 00 — End-to-end workflow

## The six questions that define the job

Before creating geometry, record:

1. **What does the image mean?** Binary logo, tonal bas-relief, repeating material texture, photograph, true depth map, or normal map?
2. **Where does it go?** One plane, a full cylinder, selected faces, a rounded perimeter, every face of a shell, or an arbitrary UV-mapped mesh?
3. **What is the operation?** Emboss, engrave, centered displacement, through-cut, or lithophane-style variable wall thickness?
4. **What is the final physical size?** Image pixels have no useful meaning until width and height in millimetres are known.
5. **What can the process reproduce?** Nozzle, line width, layer height, material, orientation, and surface curvature matter.
6. **How must the image fit?** Stretch, aspect-preserving contain, crop/cover, or repeat/tile?

Do not let defaults answer these questions accidentally.

## Stage 1: classify the image

| Image class | Typical conversion |
|---|---|
| Binary logo or line art | Threshold or preserve alpha; optionally bevel the edge |
| Tonal bas-relief | Use grayscale after levels/gamma; verify shadows really mean depth |
| Repeating texture | Make/verify a seamless tile; preserve a preferred direction |
| Photograph | Segment subject/background and remove lighting gradients before using luminance |
| True depth map | Preserve numeric depth and calibration; avoid artistic contrast edits |
| Normal map | Reconstruct or author height; do not use raw RGB luminance |
| Color/material image | Define an explicit channel or conversion; visual albedo is not geometry |

A beautiful material render often makes a poor height map. Highlights, shadows, perspective, and color variations can become unwanted dents and ridges.

## Stage 2: define the physical mapping

Write down:

- physical image width and height;
- surface start point and seam position;
- which way image “up” points on the object;
- whether opposite edges must meet;
- whether the image repeats and how many times;
- whether the mapping is local to the surface or fixed in world coordinates;
- where relief should taper to zero;
- the outward normal of each target surface.

For a cylinder of radius `R`, a complete wrap width is `2πR`. For a rounded rectangular wall, use the true perimeter including corner arcs, not `2(width + depth)`.

## Stage 3: choose the representation

### Native height surface

Use when the target is flat and the tool already supports image displacement. Examples: OpenSCAD `surface()` for a plate, or Blender displacement on a prepared mesh.

Advantages: short pipeline and easy preview.  
Risks: implicit grayscale rules, weak control over watertight overlap, limited curved mapping, and large native feature trees.

### Direct displacement of the object mesh

Use in Blender when the object has a clean UV map, sufficient tessellation, applied scale, controlled normals, and a vertex group limiting the affected area.

Advantages: natural arbitrary-shape mapping and interactive preview.  
Risks: UV seams, displacement of thin walls, self-intersection, and accidental movement of hidden/back surfaces.

### Closed relief patch plus Boolean

This is the default for cylinders, rounded boxes, polygon walls, and CAD-built bases. Generate a watertight shell between an outer and inner sampled surface. Union it for embossing or subtract it for engraving.

Advantages: tool-neutral, explicit depth and overlap, inspectable, and compatible with parametric bases.  
Risks: mesh size and Boolean cost.

### Native B-rep features

Use only for sparse geometry such as a vector logo, engraved text, or a coarse cell pattern. Thousands of tiny faces and Boolean features overwhelm B-rep kernels long before a comparable triangle mesh becomes difficult.

## Stage 4: prepare the image

Keep the source untouched. Produce a derived image with:

- explicit grayscale/alpha policy;
- intended orientation;
- fit/crop/repeat decision;
- levels and gamma;
- physical-scale blur or sharpening;
- seam correction if repeating;
- 16-bit output when tonal depth matters;
- a report containing pixel dimensions and actual millimetres per pixel.

Example:

```bash
python scripts/prepare_heightmap.py source.png prepared.png \
  --physical-width-mm 150 --physical-height-mm 55 \
  --sample-pitch-mm 0.25 --fit tile \
  --levels 1,99 --blur-mm 0.10 --bit-depth 16 \
  --preview prepared-preview.png --report prepared.report.json
```

## Stage 5: estimate printability and memory

```bash
python scripts/analyze_heightmap.py prepared.png \
  --physical-width-mm 150 --physical-height-mm 55 \
  --mesh-pitch-mm 0.30 \
  --nozzle-mm 0.4 --line-width-mm 0.44 \
  --layer-height-mm 0.2 --relief-depth-mm 0.8 \
  --repeat-x --report analysis.json
```

Review:

- source pitch;
- mesh vertex and triangle estimates;
- likely working memory;
- seam-to-adjacent variation ratio;
- tiny connected components;
- relief slope;
- relief depth in layer steps.

A larger source image is harmless if geometry is sampled deliberately. A needlessly tiny mesh pitch is what creates excessive geometry and Boolean cost.

## Stage 6: generate a closed patch

Copy a JSON config from an example or `references/11-relief-config-reference.md`.

```bash
python scripts/relief_patch.py config.json cutter.stl \
  --report cutter.report.json
```

For engraving, the generated cutter reaches outward by `overlap_mm` and inward by `depth_mm × h`. For embossing, the patch reaches inward by the overlap and outward by the height.

The overlap is deliberate. Coplanar Boolean inputs are unreliable.

## Stage 7: Boolean with an explicit fallback path

```bash
python scripts/mesh_boolean.py difference base.stl cutter.stl \
  -o engraved.stl --engine auto \
  --require-watertight --require-single-body \
  --report boolean.report.json
```

`auto` tries available in-process engines and then OpenSCAD. Keep the original STEP/B-rep base and the separate cutter even after producing a final STL.

## Stage 8: validate geometry and toolpaths

Geometry:

```bash
python scripts/validate_mesh.py engraved.stl \
  --require-watertight --require-volume --require-single-body
```

Slicer:

- zoom into the toolpath, not just the shaded model;
- verify fine islands receive paths;
- check wall thickness below the deepest engraving;
- inspect vertical-surface stair stepping;
- inspect top/bottom relief for bridge and overhang behavior;
- confirm the chosen orientation does not bury the image in support scarring;
- print a small coupon containing the same feature widths and depth.

## Completion definition

The job is complete only when the following are reproducible:

- source and processed images;
- physical dimensions and printer assumptions;
- mapping and relief configuration;
- base model source;
- relief patch/cutter;
- final Boolean or a documented unavailable backend;
- topology report;
- slicer/coupon observations.

A screenshot that “looks textured” is not completion.
