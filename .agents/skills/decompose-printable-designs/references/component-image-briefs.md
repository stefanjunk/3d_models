# Image-to-3D component briefs

## Contents

1. [Use two image sets](#1-use-two-image-sets)
2. [Define the component before generating](#2-define-the-component-before-generating)
3. [Prepare generation plates](#3-prepare-generation-plates)
4. [Use masks and part-aware models](#4-use-masks-and-part-aware-models)
5. [Use single-view and multi-view inputs](#5-use-single-view-and-multi-view-inputs)
6. [Protect the future interface](#6-protect-the-future-interface)
7. [Handle common component types](#7-handle-common-component-types)
8. [Lock style across components](#8-lock-style-across-components)
9. [Accept or reject candidates](#9-accept-or-reject-candidates)
10. [Brief example](#10-brief-example)

## 1. Use two image sets

Maintain separate sets with different purposes:

### Evidence images

Evidence images preserve the original concept, camera, neighbouring parts, scale cues, shadows, and ambiguity. Use them for interpretation, measurement qualification, and visual validation.

### Generation plates

Generation plates are deliberately simplified inputs for a specific image-to-3D job. They show one semantic component or a controlled set of masked parts. Use them to reduce fusion, background reconstruction, and identity ambiguity.

Do not edit the evidence image into the only surviving copy. Do not ask a generation plate to prove what the source actually showed.

## 2. Define the component before generating

Give every job a stable brief containing:

- component ID and human-readable name;
- intended role and whether it carries load;
- source references and confidence by region;
- project and local coordinate conventions;
- target bounding envelope in millimetres;
- intended front/up/left and any symmetry policy;
- required silhouettes and negative spaces;
- protected visible features;
- replaceable/sacrificial seam band;
- minimum printable feature budget tied to process;
- forbidden geometry and functional keep-outs;
- expected component count and topology policy;
- required output file and texture/material policy;
- acceptance views and numerical checks.

The image controls appearance. The brief controls identity, scale, interface intent, and acceptance.

## 3. Prepare generation plates

### 3.1 Default visual setup

Use:

- complete, uncropped silhouette with margin;
- transparent, white, or neutral mid-grey background;
- diffuse, broad lighting with recoverable shadows;
- matte clay or low-specular material for shape generation;
- moderate perspective or true orthographic views when supported;
- high contrast between object and background without clipped edges;
- one object, one pose, no labels, arrows, rulers, stands, hands, or scenery.

Store scale and annotations in metadata/briefs, not inside the generation image where the model may reconstruct them as geometry.

### 3.2 Keep geometry and texture tasks distinct

For shape generation, remove or suppress:

- strong metallic reflections;
- cast shadows crossing the silhouette;
- printed patterns that resemble grooves;
- depth-of-field blur;
- transparent overlays and glow;
- background objects touching the target.

Create a separate appearance plate when texture/PBR generation is needed. A clay render should pass before texture is considered.

### 3.3 Pixel budget

Make the component large enough in frame that the smallest required visible form spans several source pixels. Do not upscale a poor source and then describe invented edges as evidence.

Match the requested geometry detail to physical print capability. For FDM, derive minimum ridges, grooves, gaps, and wall features from the nozzle/line-width/layer/orientation and a coupon. Keep sub-resolution grain as color/texture or omit it.

## 4. Use masks and part-aware models

If the model supports part-aware input, provide stable part masks rather than relying on automatic semantic guesses.

Rules:

1. Use one integer identity per semantic part and keep it unchanged across views.
2. Use the same granularity across masks; do not mark a complete wing in one view and feathers as independent parts in another.
3. Mark occluded portions as unknown rather than painting invented boundaries with high confidence.
4. Separate repeated parts with indexed identities.
5. Preserve a mapping table from mask ID to component ID and intended representation.
6. Inspect masks at thin appendages, holes, contact shadows, and overlapping silhouettes.

Part-aware generation can improve editability and contextual cohesion, but it does not establish metric scale, printable walls, mechanical interfaces, or a valid assembly. Treat generated bounding boxes and part layouts as proposals to compare against the master architecture.

If the model does not reliably preserve identities, generate each organic component separately and re-establish context through explicit target envelopes and assembly transforms.

## 5. Use single-view and multi-view inputs

### 5.1 Single-view route

Use when the component is appearance-dominant and hidden geometry can be deliberately replaced. Expect synthesized depth and backside.

Provide:

- one clean hero image;
- a written symmetry/backside policy;
- target envelope and important depth stations;
- explicit statement that the interface/back will be trimmed or replaced.

Generate several candidates. A single output does not quantify ambiguity.

### 5.2 Multi-view route

Use only if the selected model accepts named views or a documented multi-view convention. Keep:

- identical scale and object center;
- fixed orientation and handedness;
- compatible focal length/projection;
- consistent lighting/material;
- consistent mask identities;
- no pose or design changes between views.

Prefer front, side, and back orthographic/near-orthographic views plus one three-quarter review view. Do not invent a back image and then treat the result as recovered evidence; label it as a design hypothesis.

### 5.3 Turntables and contact sheets

Do not send an unlabeled contact sheet to a model that expects one image. It may reconstruct the sheet or blend views. Use the model's documented multi-view API or process views separately.

## 6. Protect the future interface

The generator should create visible form plus disposable material, not a finished mating surface.

### 6.1 Sacrificial root/band

Add a simple thick root, collar, flange, or rear mass within the declared seam band. It must be large enough that the registered mesh can be cut back to the exact parametric seat without erasing visible detail.

Requirements:

- no high-value ornament inside the band;
- no narrow neck exactly at the cut plane;
- excess extends past the authoritative trim surface;
- visible curvature reaches the band smoothly;
- root remains one coherent component, not loose islands.

### 6.2 Do not encode precision in prompt prose alone

Phrases such as “exactly 40 mm”, “perfectly flat back”, or “0.3 mm clearance” are not metric constraints for an image-to-3D model. Enforce them later with scale, trim cutters, backers, pockets, and gauges.

### 6.3 Interface witness artifacts

Do not include rulers, datum arrows, or a CAD cage in the final generation plate unless the specific model supports conditioning channels for them. The model may fuse witnesses into the object. Keep witnesses as separate overlays for review.

## 7. Handle common component types

### 7.1 Free-standing ornament or appendage

Generate the visible body with a thick sacrificial root. Register to an envelope and three landmarks. Cut the root with the parametric seat plane/patch and add a parametric connector or backer.

Good for heads, creatures, leaves, knobs, handles, finials, and sculptural brackets. Do not let a decorative appendage carry critical load without a parametric load path through it.

### 7.2 Shallow relief on a flat substrate

Prefer a front-facing clay image or 16-bit height map when the design is genuinely 2.5D. Keep a no-detail border. Build the substrate and edge frame parametrically; apply the relief only inside the bounded field.

Avoid full image-to-3D for a relief when it invents an unnecessary backside and uneven thickness.

### 7.3 Relief on a curved substrate

Use one of:

- UV/parameter-space displacement from a controlled height map;
- a shallow organic patch with a sacrificial planar back, then controlled shrinkwrap/conform plus solidify;
- segmentation into several low-distortion patches;
- a separate rigid plaque/inlay seated on the curve.

The parametric substrate owns curvature and wall thickness. Validate distortion after conforming. A simple bend of a detailed mesh may stretch feature width and seam alignment.

### 7.4 Organic shell over a functional core

Generate the exterior silhouette with extra inward volume. Replace the interior with a parametric clearance/core offset. Keep ventilation, electronics, roll paths, user grips, and service access as negative keep-outs.

### 7.5 Repeated ornaments

Generate one high-quality master when repetition is intended. Pattern it parametrically with transforms. Generate separate variants only when controlled variation is a requirement; otherwise independent generation introduces accidental style and scale drift.

### 7.6 Mirrored components

Mirror a master only if chirality is not semantically important. Text, handed anatomy, twist direction, drain direction, and asymmetric attachment features require separate treatment.

## 8. Lock style across components

Create a compact style sheet shared by every brief:

- material/render style for input plates;
- motif vocabulary and forbidden motifs;
- edge softness, relief density, and detail hierarchy;
- symmetry/repetition policy;
- palette/material assignments for later review;
- reference component chosen as style anchor.

Reuse model version, resolution, preprocessing, and seed/settings when supported. Generate one calibration component first. Approve it before producing the full family.

Do not depend on identical prompt words alone for style consistency. Compare clay renders together at the same scale and lighting.

## 9. Accept or reject candidates

Review in this order:

1. semantic identity and component count;
2. target envelope and handedness;
3. silhouette from required views;
4. negative spaces and topology;
5. sacrificial root/seam reserve;
6. compatibility with functional keep-outs;
7. printable feature size and thickness potential;
8. surface detail and texture.

Reject candidates with:

- fused neighbours, duplicate parts, or missing holes;
- uncontrolled base/back geometry extending into keep-outs;
- thin sheets, self-intersections, internal shells, or disconnected ornament;
- critical visible detail inside the seam band;
- front-only success with implausible side depth;
- high polygon count that stores texture noise rather than physical form.

Use matched clay renders and masks. Do not select primarily from a textured hero view.

## 10. Brief example

```text
Component: ORN_WAVE_L — left wave ornament
Role: appearance-only replaceable insert; carries no wall load
Source: concept image IMG-001, left-front crop; hidden back is designed
Target envelope: 82 × 18 × 110 mm in local X/Y/Z
Front/up: crest points +Z; attachment direction -Y
Required form: one continuous breaking wave, open central negative space
Protected: outer crest silhouette and three foam curls
Sacrificial zone: rear 5 mm and 6 mm border along attachment edge
Interface: trim to CAD-owned curved backer IF-ORN-L; no generated key/socket
Process budget: 0.6 mm nozzle; ridges >= validated coupon result
Input plate: isolated matte-clay object, neutral grey, front + right + 3/4 views
Exclude: product body, wall, toilet roll, text, metallic highlights, floating droplets
Acceptance: one mesh component; envelope within declared registration budget;
            no collision with KEEP_ROLL_PATH; silhouette approved in three views
```

The brief is an engineering handoff. The exact numerical values must come from the current project plan and process tests, not from this example.
