# Decomposition and representation routing

## Contents

1. [Start from a design claim](#1-start-from-a-design-claim)
2. [Interpret concept images](#2-interpret-concept-images)
3. [Interpret written concepts](#3-interpret-written-concepts)
4. [Build linked architectures](#4-build-linked-architectures)
5. [Choose component boundaries](#5-choose-component-boundaries)
6. [Allocate representation authority](#6-allocate-representation-authority)
7. [Choose granularity](#7-choose-granularity)
8. [Freeze a coarse assembly](#8-freeze-a-coarse-assembly)
9. [Failure patterns](#9-failure-patterns)

## 1. Start from a design claim

State which claim the project will make:

- **measured reconstruction:** dimensions and visible geometry are evidence-backed;
- **visual interpretation:** selected views and style are targets, hidden geometry is designed;
- **plausible completion:** incomplete evidence is completed with declared hypotheses;
- **functional redesign:** appearance is retained while function and interfaces are engineered;
- **new design:** text/images express intent rather than an object to recover.

Keep four acceptance axes separate: geometry, appearance, function, and manufacturability. A part can pass one and fail the others.

Record every requirement as `observed`, `measured`, `inferred`, `assumed`, or `requested`. Preserve conflicts. A concept render can be visually authoritative without being metrically or mechanically authoritative.

## 2. Interpret concept images

### 2.1 Preserve evidence and camera context

Keep the source unchanged. Record crop, perspective, likely projection, known scale, occlusion, reflections, depth of field, and whether the image itself is AI-generated. Create derivatives for masks, traces, edges, and color only.

Treat the following as separate layers:

1. primary mass and silhouette;
2. secondary volumes and negative spaces;
3. functional features and contact regions;
4. part/material/color boundaries;
5. geometric relief;
6. texture/roughness/albedo;
7. lighting, cast shadows, highlights, and compositing.

Do not turn every pixel boundary into a component boundary. A highlight may resemble a seam; a material transition may not imply a separate solid; a visible ornament may hide a continuous structural shell.

### 2.2 Produce two kinds of crops

- **Evidence crop:** retain 5–15% contextual halo so the part's relationship to neighbours remains visible. Mark occluded segments and confidence.
- **Generation plate:** isolate exactly the target organic component on a neutral or transparent background, with no neighbouring object that the model may fuse into the mesh.

The evidence crop explains context; the generation plate drives synthesis. Never substitute one for the other.

### 2.3 Cross-view identity

Give each component a stable semantic ID before creating masks. Use the same ID, color, handedness, and granularity across every view. Repeated components need indexed IDs such as `RIB_L_01`, `RIB_L_02`, not only the label `rib`.

For inconsistent concept views, decide whether to:

- preserve one hero view and design the rest;
- reconcile to the simplest manufacturable volume;
- create alternatives;
- request another view.

Do not average incompatible topology.

## 3. Interpret written concepts

Text usually mixes needs, functions, appearance, implementation guesses, and constraints. Separate them before geometry.

### 3.1 Extract scenarios

Write short operational sequences: install, load, use, refill, clean, repair, store, transport, dispose. Include off-nominal states such as a jam, drop, wet surface, depleted consumable, blocked vent, or wrong-way insertion.

### 3.2 Convert verbs into functions

Examples:

| Phrase | Function | Possible physical allocation |
|---|---|---|
| “hang on the wall” | transfer load to wall | parametric mounting spine plus purchased screws |
| “show how many remain” | expose or indicate state | window/negative space, index, light, or sensor |
| “feel like coral” | communicate organic identity | organic shell or replaceable ornament |
| “open without tools” | permit service access | parametric latch/hinge and access sweep |
| “different for every customer” | support variation | parameter set, replaceable panel, text/relief asset |

Do not preserve an implementation phrase when a simpler architecture satisfies the underlying function better.

### 3.3 Build a blockout before decorative generation

Create boxes, cylinders, planes, centerlines, and swept volumes for the functional arrangement. Validate size, user access, motion, load path, and print envelope. Use the blockout to derive target envelopes for organic work.

## 4. Build linked architectures

One decomposition is not enough. Maintain at least these linked views:

### 4.1 Functional architecture

Describe what happens, independent of shape: support, guide, retain, release, seal, diffuse, illuminate, sense, protect, adjust, clean, personalize.

### 4.2 Physical architecture

List printed bodies, purchased hardware, electronics, textiles/sheets, adhesives, fasteners, negative volumes, jigs, and test gauges.

### 4.3 Appearance architecture

Allocate silhouette, massing, relief, microtexture, color, translucency, gloss, and post-processing. Decide which appearance must be geometry and which can remain color/texture.

### 4.4 Manufacturing architecture

Allocate print orientation, material/color body, support strategy, split plane, bed-size module, post-processing, and assembly operation. A component split can be justified even if the final product has no visible seam.

### 4.5 Lifecycle architecture

Identify wear, contamination, repair, upgrades, customer-specific parts, and parts that should be reprinted without replacing the core.

Map requirements and interfaces across these views. A decorative shell may be one visual component, four printable modules, and no functional component.

## 5. Choose component boundaries

Create a boundary when it improves at least one of:

- dimensional authority or independent parameterization;
- generated-detail quality;
- material/color assignment;
- print orientation, support access, or bed fit;
- repair, cleaning, upgrade, or personalization;
- risk isolation and testing;
- standard-part reuse;
- assembly or inspection access.

Avoid a boundary when it creates:

- an inaccessible seam or adhesive joint;
- a new weak load path;
- ambiguous datum ownership;
- unnecessary part count and tolerance stack;
- a visible mismatch more costly than the benefit;
- an assembly order that becomes impossible.

### Boundary quality test

For each proposed component ask:

1. Does it have one coherent role or authority?
2. Can its inputs/outputs and interfaces be named?
3. Can it be generated and validated independently?
4. Can it be assembled, replaced, or fused without violating a protected region?
5. Does the boundary follow a natural seam, low-stress zone, material change, or manufacturing split?

If most answers are no, merge it with its neighbour or redefine the boundary.

## 6. Allocate representation authority

Score candidate components with `0 = not important`, `1 = relevant`, `2 = critical`:

| Criterion | Parametric tendency | Organic tendency |
|---|---:|---:|
| exact fit, datum, motion, seal, load | +2 | -2 |
| repeated/scalable/configurable | +2 | 0 |
| section/profile can be described | +1 | 0 |
| appearance dominates and back is hidden | 0 | +2 |
| free-form curvature or sculpted anatomy | -1 | +2 |
| high uncertainty but replaceable | +1 envelope | +1 detail |
| safety consequence | +2 | -2 |
| must preserve irregular captured surface | 0 | +2 |

Use the score as a discussion aid, not an automatic decision.

### Default authority patterns

- **Functional core + organic skin:** core owns envelope, load, mount, walls, keep-outs, and connection; skin owns visible surface inside a style envelope.
- **Parametric substrate + organic relief:** substrate owns back surface, thickness, edge frame, and placement; relief owns height field or sculpted foreground inside a no-detail seam margin.
- **Organic body + parametric insert:** insert owns all mating and moving geometry; organic body receives a pocket cut from the insert's master clearance body.
- **Organic appendage + parametric root:** appendage owns visible free-form shape; root/backer owns seat, key, screw/magnet/adhesive channel, and stress transition.

Never let two source models define the same nominal mating dimension. Derive the non-owner from the owner's exported interface body.

## 7. Choose granularity

Too coarse produces monolithic meshes, hard-to-edit interfaces, merged materials, and whole-object regeneration. Too fine produces style drift, identity swaps, many fragile seams, and unmanageable tolerance stacks.

Choose the largest component that has one authority and can still be generated, printed, and validated reliably.

Split an organic region further when:

- parts need different view evidence or topology;
- the generator repeatedly fuses holes or neighbours;
- different materials/colors or print orientations are required;
- one portion must remain replaceable;
- repeated elements can share one master plus transforms.

Keep organic parts together when continuous curvature and style coherence matter more than editability and the interface to CAD can remain simple.

Part-aware generators may accept masks and preserve context, but still need explicit semantic identities, envelopes, and print engineering. Do not assume their part boundaries are manufacturing boundaries.

## 8. Freeze a coarse assembly

Before detailed organic generation, deliver:

- global coordinate frame and master envelope;
- proxy solids for every component;
- interface graph and single owner per interface;
- functional keep-outs and swept volumes;
- assembly/exploded sequence;
- print/body/material allocation;
- target envelope and local frame for each organic component;
- open decisions and variants.

Use one structured decision log rather than scattering `TBD` through prompts and CAD notes. For each unresolved or provisional choice, record the current basis, the evidence needed to resolve it, and every downstream gate it blocks. A plan can be internally consistent while component generation, integration, manufacturing, physical validation, or release is still blocked.

Review the blockout from orthographic and intended-use views. Run simple collision and bed-fit checks. High-detail work is premature if the blockout cannot be assembled or used.

## 9. Failure patterns

| Failure | Cause | Corrective action |
|---|---|---|
| ornament merges with the whole product | generation plate contains contextual geometry | isolate component; keep context in a separate evidence crop |
| separately generated parts have inconsistent scale | no shared frame/envelope | use one master envelope and explicit local transforms |
| same feature changes identity between views | masks/IDs are not stable | index parts and use fixed mask colors/semantic tokens |
| functional core follows decorative surface noise | authority not allocated | fit datums/sections and make CAD the interface owner |
| many tiny components cannot be assembled | visual segmentation mistaken for manufacturing split | regroup by authority and assembly value |
| final seam blocks service access | assembly sequence not modeled | add access/swept volumes and sequence gates before detail |
| decorative part becomes structural by accident | load path crosses appearance body | route load through parametric core or engineer/test the ornament |
| text concept jumps straight to sculpting | functions and constraints were not extracted | create scenarios, functional blocks, and a coarse assembly first |
