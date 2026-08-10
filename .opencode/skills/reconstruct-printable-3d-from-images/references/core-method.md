# Core method: image evidence to design specification

## Contents

1. [Define the reconstruction claim](#1-define-the-reconstruction-claim)
2. [Acquire useful evidence](#2-acquire-useful-evidence)
3. [Preserve and preprocess](#3-preserve-and-preprocess)
4. [Calibrate scale and camera](#4-calibrate-scale-and-camera)
5. [Build the requirement ledger](#5-build-the-requirement-ledger)
6. [Extract shape](#6-extract-shape)
7. [Extract texture, color, and material cues](#7-extract-texture-color-and-material-cues)
8. [Choose geometry versus appearance](#8-choose-geometry-versus-appearance)
9. [Manage uncertainty](#9-manage-uncertainty)
10. [Define deliverables](#10-define-deliverables)

## 1. Define the reconstruction claim

State what the result is meant to be before modeling:

- **Measured replica:** Match known dimensions and visible geometry within declared tolerances.
- **Visual reconstruction:** Match selected views while accepting uncertainty elsewhere.
- **Plausible completion:** Create coherent hidden geometry based on explicit assumptions.
- **Functional redesign:** Preserve visual identity while replacing interfaces, walls, clearances, or internals with engineered geometry.
- **Relief interpretation:** Convert image intensity or drawn contours into a printable 2.5D surface.

Do not use “accurate” without naming the accuracy domain. A model can be visually accurate from the source view and dimensionally wrong, or dimensionally accurate in the envelope but visually wrong in curvature.

Define four independent acceptance axes:

| Axis | Typical evidence | Typical validation |
| --- | --- | --- |
| Geometry | dimensions, silhouettes, sections | calipers, landmarks, matched renders |
| Appearance | palette, texture, material cues | controlled render comparison |
| Function | load, fit, motion, grip, flow | calculation, coupon, assembly test |
| Manufacturability | process profile and orientation | mesh audit, slicer, test print |

## 2. Acquire useful evidence

### Preferred image set

Request, where possible:

1. front, rear, left, right, top, and bottom views;
2. three-quarter views to reveal curvature and transitions;
3. a close-up for every small feature that must become geometry;
4. a rigid ruler, calibration target, or known object in the same depth plane;
5. one image per view with a longer focal length and the camera farther away to reduce perspective;
6. a turntable sequence or overlapping orbit for organic real objects;
7. separate images under diffuse, consistent lighting for color and texture.

For photogrammetry, capture overlapping images around the object, include high and low camera rings, keep exposure and focus consistent, and avoid moving the object relative to the background unless the masking workflow expects it. Add removable random texture near weakly textured objects, but never alter a critical surface without documenting it.

### Poor evidence patterns

Flag:

- wide-angle close-ups with strong foreshortening;
- product composites that may combine different cameras or retouching;
- cast shadows touching the silhouette;
- reflective, transparent, translucent, furry, or moving surfaces;
- clipped highlights and crushed shadows;
- depth-of-field blur on required edges;
- occlusions, hands, stands, labels, or props hiding geometry;
- inconsistent versions of the object across views;
- AI-generated reference images with impossible or view-inconsistent details.

### Drawings and concept art

Treat orthographic drawings as stronger projection evidence only if they are internally consistent. Check that front/side/top views share landmarks and overall dimensions. Concept art often cheats perspective or changes details between views; preserve the design intent, but record the reconciled geometry as a design decision.

## 3. Preserve and preprocess

### Evidence preservation

- Keep the original byte-for-byte.
- Record filename, pixel dimensions, EXIF orientation, color profile, and any focal-length metadata.
- Create derivatives in a separate directory.
- Record every crop, rotation, undistortion, perspective correction, scale, mask, and enhancement.
- Never run repeated lossy JPEG saves on measurement images.

### Preprocessing order

1. Apply EXIF orientation.
2. Decode into a color-managed working space; preserve embedded profiles where the tool supports them.
3. Undistort with calibrated lens parameters when measurement matters.
4. Correct perspective only when a known planar surface justifies the transform.
5. Normalize white balance/exposure for appearance analysis, not for silhouette measurement.
6. Segment the object and repair only obvious mask defects.
7. Crop with context retained; keep a padded square derivative for AI tools when needed.
8. Generate grayscale, edge, silhouette, palette, and optional vector derivatives.
9. Downsample copies for iteration; preserve full resolution for later texture work.

Do not sharpen before measuring boundaries unless the resulting edge shift is checked. Denoising and super-resolution can invent edges; use them for visual assistance, never as stronger evidence than the original.

### Segmentation

Use, in increasing complexity:

- existing alpha channel;
- uniform-background threshold plus morphology;
- manual path/mask in GIMP, Krita, Photoshop, or Inkscape;
- interactive segmentation;
- a segmentation model with manual review.

Inspect holes, thin limbs, spokes, handles, transparent parts, hair/fur, and contact shadows at 100–400% zoom. Save a hard binary mask for metrics and a soft alpha mask for compositing.

### Vector tracing

Trace only boundaries that represent geometry. Simplify paths to the lowest control-point count that remains within the physical tolerance. Preserve deliberate corners. Remove bitmap noise, but do not smooth away asymmetry unless symmetry is a requirement.

## 4. Calibrate scale and camera

### Scale

Use evidence in this order:

1. supplied engineering dimension;
2. calibration target or ruler in the object's depth plane;
3. known mating part measured physically;
4. reliable manufacturer dimension;
5. category prior, explicitly marked low confidence.

One known dimension fixes uniform scale only. It does not remove perspective distortion or prove other dimensions.

### Projection

Identify whether each view is:

- orthographic or near-orthographic;
- perspective with known focal length/sensor;
- perspective with estimated camera;
- illustration with non-physical projection.

For perspective matching, solve or tune camera intrinsics and extrinsics before deforming the model. Use parallel edges and vanishing points, EXIF focal length, calibration targets, or photogrammetric camera recovery. Lock the camera after blockout approval.

For orthographic views, set the image scale from a known dimension and place view planes on canonical axes. Avoid using an orthographic camera merely because it makes an unmatched perspective photo easier to trace.

## 5. Build the requirement ledger

Use `assets/reconstruction-brief.yaml`. Give each requirement:

- stable ID;
- exact statement;
- category;
- evidence class: `observed`, `measured`, `inferred`, `assumed`, `requested`;
- source image and region or user statement;
- confidence;
- nominal value and tolerance, if dimensional;
- priority;
- validation method.

Examples:

| ID | Statement | Evidence | Confidence | Validation |
| --- | --- | --- | --- | --- |
| REQ-001 | Overall width is 68.0 mm | measured from caliper | high | CAD and printed caliper check |
| REQ-002 | Front silhouette follows traced curve P-01 | observed in IMG-001 | high | matched front render |
| REQ-003 | Back is mirror-symmetric | inferred from style | medium | rear variant review |
| REQ-004 | Cable channel fits 5.0–5.5 mm cable | requested | high | gauge/cable coupon |
| REQ-005 | Brown bands are printed color, not relief | assumed | medium | material assignment review |

Do not bury conflicts. If front and side sources disagree, record both and state which requirement wins and why.

## 6. Extract shape

### Establish axes and hierarchy

Define origin, up direction, front direction, symmetry planes, and primary datum surfaces. Then model from large to small:

1. envelope and center of mass;
2. primary masses;
3. cross-sections and transitions;
4. openings and negative spaces;
5. interfaces and part boundaries;
6. secondary forms;
7. high-frequency detail.

### Primitive decomposition

Identify boxes, cylinders, cones, spheres, tori, extrusions, revolutions, sweeps, lofts, shells, and freeform patches. Use a primitive only as a construction model; validate the resulting silhouette and sections rather than forcing the object to remain perfectly primitive.

### Silhouettes and profiles

- Trace each useful view independently.
- Mark occluded and uncertain segments.
- Align corresponding landmarks across views.
- Use silhouette intersections as bounds, not as proof of the exact interior surface.
- Check every view after editing one view; local matching can damage another silhouette.

For rotational objects, extract a centerline and a radius-versus-height profile, then revolve. For prismatic objects, extract a closed profile and depth. For varying sections, define stations and loft. For handles, wires, and limbs, use centerline paths plus section profiles.

### Curvature and edge character

Infer curvature from silhouette first, then from highlight flow and shading. Shading is ambiguous because light, material roughness, normals, and geometry interact. Use it as supporting evidence only.

Classify edges as sharp, chamfered, constant-radius fillet, variable fillet, or soft transition. Model important highlight-controlling bevels even when small; remove bevels that are below manufacturing resolution unless they affect fit.

### Negative space

Openings often carry stronger identity than surface texture. Measure holes, slots, gaps between limbs, handle interiors, undercuts, and clearance around moving parts. Validate their silhouettes from multiple views.

### Hidden geometry

Create a hypothesis set:

- symmetry completion;
- simplest manufacturable continuation;
- category-typical continuation;
- alternate user-selected design.

Prefer the simplest hypothesis consistent with all evidence and function. Keep hidden artistic invention separable so it can be replaced.

## 7. Extract texture, color, and material cues

### Separate causes of pixel variation

For each visible pattern, classify it as:

- base color/albedo;
- printed material boundary;
- geometric relief;
- fine normal/roughness variation;
- specular reflection;
- cast or self-shadow;
- dirt, wear, decal, or photographic background.

Sample color from several diffuse midtone regions, not a highlight or shadow. Report sRGB values as image observations, not as exact filament/resin matches. Physical print color depends on material, layer orientation, thickness, lighting, and device color management.

### Texture projection

Use UV or camera projection for appearance comparison. Avoid baking highlights and shadows into base color when the aim is a relightable asset. For multiview imagery, choose view assignments or blend after camera calibration; inspect seams and occlusion.

### PBR maps

Use base color, roughness, metallic, normal, opacity, and displacement only when the target asset or renderer needs them. For 3D printing, confirm which channels the slicer/printer uses. Most geometry-only print workflows ignore PBR appearance.

### Color manufacturing

Choose among:

- separate bodies by filament/material;
- per-face or texture color in a supported 3MF workflow;
- manual filament changes by height;
- paint/decal/post-processing;
- geometry relief when tactile or monochrome readability matters.

STL carries geometry only. Do not treat viewport color as a manufacturing instruction.

## 8. Choose geometry versus appearance

Promote a feature to geometry when it:

- changes silhouette;
- changes contact, fit, grip, fluid flow, or motion;
- remains visible/tactile at the intended print scale;
- must survive sanding, painting, or color loss;
- creates a deliberate shadow or edge important to identity.

Keep a feature as texture/color when it:

- is below measured printable feature size;
- is purely chromatic;
- would create millions of triangles without tactile benefit;
- is stochastic material grain;
- is lighting baked into the source.

Use a low-amplitude relief only after a printer-specific coupon confirms it. Preserve a higher-resolution texture asset separately even when geometry is downsampled.

## 9. Manage uncertainty

Maintain an uncertainty map by region. Use three levels:

- **Low:** constrained by several consistent views or direct measurement.
- **Medium:** constrained by one clear view plus symmetry/category evidence.
- **High:** hidden, occluded, reflective, blurred, inconsistent, or unscaled.

Spend modeling effort in proportion to priority and evidence. Do not add dense detail to a high-uncertainty back while a critical measured interface is unresolved.

When an uncertainty changes topology or function, create variants and ask for selection. When it changes only cosmetic micro-detail, choose a reversible default and document it.

## 10. Define deliverables

Retain distinct artifacts:

- **Evidence:** originals, masks, traces, palettes, camera data.
- **Specification:** completed requirement ledger and uncertainty map.
- **Master:** parametric CAD or editable mesh at working resolution.
- **Appearance asset:** UV/PBR model if needed.
- **Print master:** watertight, correctly scaled geometry with manufacturing splits.
- **Exports:** STEP/3MF/STL/GLB as appropriate.
- **Validation:** matched renders, metrics, mesh audit, slicer screenshots/profile, coupon and prototype measurements.

Name versions so geometry, cameras, and reports can be reproduced together. A render from revision B must not be compared against a mesh from revision C.
