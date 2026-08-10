---
name: 3d-print-heightmap-relief
description: Use when designing, generating, mapping, validating, or troubleshooting printable embossing or engraving from image height maps on flat, cylindrical, rounded, polygonal, spherical, toroidal, or arbitrary sampled surfaces.
license: MIT
compatibility: OpenCode; Python 3.10+; optional OpenSCAD, CadQuery, FreeCAD, or Blender
metadata:
  audience: 3d-print-designers
  workflow: heightmap-relief
  version: "1.0.0"
---

# 3D-print image height-map relief

Use this skill when an image must become visible, printable geometry: a raised emboss, a recessed engraving, a bas-relief, or a shallow texture. Do not treat “put the image on the object” as one operation. Separate image interpretation, physical sampling, surface mapping, closed geometry, Boolean application, and print validation.

## Load only what the task needs

Start with:

- `references/00-workflow.md` for the end-to-end decision process.
- `references/01-heightmap-fundamentals.md` for white/black, invert, depth, emboss, engraving, and signed relief.
- `references/02-image-requirements-preprocessing.md` for image checks and cleanup.
- `references/03-resolution-memory-printability.md` before choosing a raster or mesh resolution.
- `references/04-surface-mapping.md` for cylinders, rounded corners, cubes, polygon walls, spheres, toruses, and arbitrary meshes.
- One tool guide: `05-openscad.md`, `06-cadquery.md`, `07-freecad.md`, or `08-blender.md`.
- `references/09-validation-troubleshooting.md` before delivery.
- `references/10-examples.md` for the three complete reference designs.
- `references/11-relief-config-reference.md` when editing JSON.

## Default production workflow

1. Establish final physical width/height, target surface, outward normal, operation, depth, printer nozzle/line width/layer height, and whether the image must crop, fit, stretch, or repeat.
2. Inspect the image before modeling. Determine bit depth, alpha behavior, dynamic range, aspect ratio, orientation, noise, smallest physical feature, and seam quality.
3. Preserve the source image. Create a derived 16-bit grayscale height map at a deliberate *physical* sample pitch.
4. Choose representation:
   - native flat `surface()` or displacement for simple flat work;
   - UV displacement in Blender for an already UV-mapped dense mesh;
   - a closed relief patch plus mesh Boolean for curved, multi-face, or CAD-built objects;
   - coarse B-rep features only for sparse logos or intentionally low-resolution geometry.
5. Map continuously where continuity matters. A rounded organizer needs one arc-length perimeter coordinate; independently mapping four faces rotates or resets the texture.
6. Generate a closed patch with positive overlap:
   - emboss patch extends slightly into the body and outward by `depth × height`;
   - engraving cutter extends slightly outside and inward by `depth × height`.
7. Boolean, validate topology, inspect a slicer preview, and print a coupon before committing to a large object.

## Commands

From this skill directory:

```bash
python scripts/prepare_heightmap.py input.png prepared.png \
  --physical-width-mm 120 --physical-height-mm 60 \
  --sample-pitch-mm 0.25 --fit cover --bit-depth 16 \
  --preview prepared-preview.png --report prepared.report.json

python scripts/analyze_heightmap.py prepared.png \
  --physical-width-mm 120 --physical-height-mm 60 \
  --mesh-pitch-mm 0.30 --nozzle-mm 0.4 --layer-height-mm 0.2 \
  --relief-depth-mm 0.8 --report analysis.json

python scripts/relief_patch.py relief-config.json relief-patch.stl \
  --report relief-patch.report.json

python scripts/mesh_boolean.py difference base.stl relief-patch.stl \
  -o engraved.stl --engine auto --require-watertight \
  --require-single-body --report boolean.report.json

python ../mesh-validation/scripts/validate_mesh.py engraved.stl \
  --require-watertight --require-volume --require-single-body
```

Build the supplied examples:

```bash
python scripts/build_examples.py --quality draft --engine auto
python scripts/build_examples.py --quality print --skip-boolean
python scripts/self_test.py
```

## Non-negotiable checks

Do not declare success from a rendered preview alone. Confirm:

- the image is recognizable at final physical scale;
- the intended dark/light convention and normal direction are explicit;
- repeat seams are no stronger than ordinary local texture variation;
- mapping direction remains consistent across all intended faces;
- relief depth spans useful layer steps and does not destroy the base wall;
- the cutter or emboss patch is closed, watertight, and has no non-manifold edges;
- the final object is the expected number of bodies;
- the slicer produces real toolpaths for the relevant ridges and recesses.

## Selection rules

Prefer the mesh-patch workflow for dense textures, full-wrap cylinders, rounded corners, and honeycomb wall/face combinations. Keep the parametric base as STEP/CadQuery/FreeCAD geometry and the dense surface as a mesh until the final Boolean.

Do not increase image resolution merely because memory is available. Retain the high-resolution source, but sample the geometry at the finest pitch that the printer and mapping curvature can use. A 1254×1254 source can remain the master while a physically sampled derivative drives the mesh.

For a sharp cube, decide whether the image should be continuous in unfolded space, continuous in world space, or intentionally restarted on each face. These are different designs. For a rounded box, use a continuous perimeter parameter so relief transfers across the corner arcs.

When the user provides a normal map, color texture, photograph, or rendered material, do not assume luminance is valid depth. Explain or implement the conversion policy.

## Deliverables

A complete result includes the processed height map, physical-size and mesh-pitch assumptions, mapping configuration, base and relief scripts, a watertight patch/cutter, final validated mesh when the backend is available, and reports sufficient to reproduce the result.
