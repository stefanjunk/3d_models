# Blender route

## Contents

1. [Choose Blender](#1-choose-blender)
2. [Scene and reference setup](#2-scene-and-reference-setup)
3. [Blockout and camera matching](#3-blockout-and-camera-matching)
4. [Organic and hard-surface reconstruction](#4-organic-and-hard-surface-reconstruction)
5. [AI/scan cleanup](#5-aiscan-cleanup)
6. [Engineering and print preparation](#6-engineering-and-print-preparation)
7. [Texture and color](#7-texture-and-color)
8. [Validation and export](#8-validation-and-export)
9. [Performance](#9-performance)

## 1. Choose Blender

Use Blender for organic meshes, sculpting, retopology, camera matching, photogrammetry cleanup, texture projection, PBR authoring, and matched-view rendering. Use a CAD tool for tight parametric interfaces when possible, then combine through a controlled hybrid workflow.

## 2. Scene and reference setup

1. Set scene units and unit scale deliberately; confirm that one model unit maps to the intended millimeters on export.
2. Define +Z up, front direction, origin, symmetry plane, and ground plane.
3. Add each image as an image Empty/reference, not as an editable replacement for the source.
4. Place near-orthographic front/side/top references on canonical axes.
5. Scale all references from the same known dimension and align shared landmarks.
6. Name sources, masks, cameras, and collections by view/revision.

Apply object scale before Solidify, bevel width, Boolean tolerances, thickness checks, and export. Unapplied non-uniform scale can make numeric settings misleading.

## 3. Blockout and camera matching

### Orthographic or concept-sheet views

- Use orthographic cameras for truly orthographic drawings.
- Block primary masses with boxes, cylinders, spheres, and low-resolution curves.
- Add Mirror early for evidence-backed symmetry.
- Match front, side, and top simultaneously.
- Lock accepted cameras and reference planes.

### Perspective photographs

Match the camera before refining the object:

- use EXIF focal length/sensor information where trustworthy;
- use parallel edges/vanishing points and known dimensions;
- adjust focal length and camera distance together;
- align horizon/verticals and principal framing;
- avoid scaling individual object regions to compensate for a wrong camera.

Use a camera-matching helper such as fSpy only when appropriate and verify the result with independent landmarks. For photogrammetry, import the recovered camera poses instead of hand matching each view.

### Milestone render

Create a flat clay material, neutral world, soft broad light, and transparent or plain background. Approve envelope and silhouettes before sculpt/detail. Texture and dramatic lighting can hide shape error.

## 4. Organic and hard-surface reconstruction

### Organic

- Start with a low-resolution symmetric base.
- Use subdivision or multiresolution for controlled refinement.
- Sculpt only after blockout and camera acceptance.
- Preserve thin appendages with explicit topology; voxel remesh can erase them.
- Break symmetry only where observed or deliberately designed.
- Retopologize when the generated/sculpt topology is unsuitable for edits, UVs, or print cleanup.

### Hard surface

- Use Mirror, Array, Solidify, Bevel, Boolean, and weighted-normal workflows non-destructively where possible.
- Use curve profiles for handles, seams, and pipes.
- Maintain datum objects for interface centers and axes.
- Keep Boolean cutters in a separate named collection.
- Apply modifiers only after preserving an editable version.

### Cross-sections

Use side/front silhouettes and section curves to constrain volume. A Shrinkwrap or surface built from sections can help, but validate other views continuously. A visual-hull intersection cannot recover concavity invisible to all silhouettes.

## 5. AI/scan cleanup

Preserve the raw mesh. Create a duplicate for cleanup.

### Diagnose first

Inspect:

- face/vertex count and object dimensions;
- connected components and loose fragments;
- open boundaries/non-manifold elements;
- duplicate/internal faces;
- normals and winding;
- self-intersections;
- paper-thin surfaces and fused openings;
- texture/UV quality.

### Choose the operation

| Condition | Operation | Main risk |
| --- | --- | --- |
| Sound surface, too many triangles | Decimate | silhouette/detail loss |
| Broken/noisy organic surface | Voxel Remesh | shrinkage, closed holes, lost thin parts |
| Need editable edge flow/UV | Retopology or quad remesh | projection error, labor |
| Need local repair | manual patch/sculpt | inconsistent curvature |
| Need a printable shell | Solidify or explicit inner surface | self-intersection at tight concavity |

Use Blender's remeshing controls from coarse to fine. The current manual describes remeshing as rebuilding uniform topology and Decimate as reducing face count with minimal shape change. Reproject color attributes only when supported and verify texture fidelity.

Compare before/after matched renders and physical dimensions. Never accept cleanup solely because the mesh looks smoother in perspective.

## 6. Engineering and print preparation

### Hybrid CAD insert

Import aligned STEP/mesh exports of functional solids. Check units immediately. Use keyed overlap and clearances rather than coincident boundaries. For critical interfaces, keep CAD as authority and modify the organic shell around it.

### Make volume

- close intentional holes while preserving functional openings;
- remove internal floating shells;
- add wall thickness that survives the chosen process;
- union touching printable bodies or keep explicit multi-part assemblies;
- add flat/keyed bases, drain/vent holes, and access for supports;
- avoid zero-thickness contacts and edge-only connections;
- re-check normals and manifold state after every Boolean/remesh.

### 3D Print Toolbox

Enable/install the official extension/add-on available for the Blender version. Use it to locate likely intersections, non-manifold geometry, thin regions, distorted faces, sharp areas, and overhangs. Interpret results: build-plate-facing surfaces may be intentionally overhanging, and numerical thickness checks depend on the correct scale and process limit.

Supplement with section views and slicer inspection. No toolbox check proves snap-fit behavior, watertight printing, or structural adequacy.

## 7. Texture and color

### Recover appearance

1. UV unwrap after topology stabilizes.
2. Project from calibrated views or create a texture atlas.
3. Separate base color from light/shadow/highlights.
4. Correct seams and occluded regions explicitly.
5. Use roughness/metallic/normal/displacement only for the target asset.
6. retain original high-resolution source textures separately from print geometry.

Use texture resolution based on rendered/painted appearance. Do not subdivide geometry to match every texture pixel.

### Convert selected texture to relief

Create a linear height map, remove lighting gradients, band-limit it to printer resolution, displace a sufficiently sampled surface, and apply/Boolean only after testing. Keep the relief amplitude a parameter. Inspect for self-intersection and impossible slopes.

### Printed color

Separate bodies/material regions as required by the slicer. Export GLB for appearance review and 3MF or aligned bodies for manufacturing where supported. Verify in the target slicer; a Blender material graph does not automatically become printed color.

## 8. Validation and export

### Matched rendering

Use `scripts/blender_render_views.py` for canonical clay views. For source-photo validation, create cameras that match the actual source views and render at the source aspect/resolution. Keep lighting neutral for shape comparison and separately approximate source lighting for appearance comparison.

Render:

- clay RGB;
- binary silhouette or object alpha;
- normal pass if diagnosing curvature;
- depth pass if comparing recovered depth;
- textured appearance pass.

Run `scripts/compare_views.py` and review overlays manually.

### Mesh validation

- apply transforms on the export duplicate;
- triangulate deterministically if the exporter/slicer will triangulate;
- check manifold/volume, components, normals, and bounding box;
- inspect minimum walls and gaps at critical regions;
- export binary STL for geometry compatibility, 3MF for supported print metadata, GLB for texture review;
- re-import/audit the exported file and slice it.

Do not export the high-resolution sculpt directly if a validated lower-resolution print mesh preserves all printable detail.

## 9. Performance

- Keep original, working, and print-resolution meshes in separate disabled collections.
- Use bounding-box/display simplification for dense references.
- Decimate a copy for camera matching and Boolean positioning.
- Use multiresolution/voxel remesh only as fine as the printer/detail budget requires.
- Disable heavy modifiers in viewport and enable them for final evaluation.
- Use linked duplicates for repeated parts.
- Save incremental files before remesh, Boolean, retopology, UV bake, and modifier application.
- Render low-resolution clay views during iteration.
- Close other GPU-heavy AI/photogrammetry processes before baking/rendering.

Switch to CadQuery/FreeCAD for dimensioned functional cores and OpenSCAD for compact parametric CSG families.
