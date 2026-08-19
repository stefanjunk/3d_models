---
name: decompose-printable-designs
description: Decompose printable product concepts into coordinated parametric, organic/image-to-3D, interface, purchased, and manufacturing components, then define how to generate, register, join, and validate them. Use for concept images, sketches, product photos, text briefs, or mixed design concepts that combine functional CAD with sculpted shells, ornaments, reliefs, AI-generated meshes, multiple materials/colors, or reusable modules; for planning component boundaries, source-of-truth ownership, keep-outs, datums, transforms, mating geometry, image-to-3D input plates, CAD counterparts, mesh/CAD integration, and interface coupons; and whenever a monolithic image-to-3D result would make a printable design hard to control, customize, repair, scale, or manufacture.
---

# Decompose Printable Designs

Turn a visual or written product concept into a controlled hybrid assembly. Treat decomposition and interfaces as design work, not as cleanup after independent parts have already been generated.

Resolve every bundled path relative to this `SKILL.md`. Keep the immutable evidence, parametric masters, organic masters, interface bodies, transforms, and manufacturing exports as distinct artifacts.

## Non-negotiable rules

1. Decompose by function, geometry, uncertainty, manufacturing, and appearance; never by color or visible seams alone.
2. Assign every dimension, datum, and interface to exactly one authoritative master. Default to parametric ownership for fits, loads, motion, seals, safety, and assembly access.
3. Freeze the global frame, envelopes, keep-outs, interface graph, and assembly sequence before generating detailed organic geometry.
4. Never ask an image-to-3D model to invent a critical mating surface. Generate sacrificial excess, then trim it with a parametric interface body or attach it to a parametric backer/core.
5. Keep nominal geometry, process compensation, motion clearance, adhesive gap, Boolean overlap, and registration uncertainty as separate values.
6. Preserve the raw AI/scan mesh. Register and repair a working copy. Do not globally remesh ornament merely to solve a local seam.
7. Validate the assembly with sections, collision/keep-out checks, surface-distance checks, slicer review, and a process-matched interface coupon. A convincing render is not acceptance.
8. Prefer reversible assemblies or replaceable decorative bodies when they improve material/color choice, repair, customization, support removal, or failure isolation.

## Route related work

- Use `reconstruct-printable-3d-from-images` for camera/evidence calibration, whole-object or component reconstruction, matched-view comparison, and image-derived requirements.
- Use `organic-mesh-functionalization` after an organic mesh exists and needs cutters, cavities, inserts, registration, local repair, or quantitative preservation checks.
- Use `optimize-fdm-design` after architecture and interfaces are stable to reduce print time/material without damaging protected geometry.
- Use `design-printable-surface-textures` when the appearance tree includes carbon, wood, fabric, stone, metal, leather, floral/lotus, procedural relief, slicer texture, or a distinct `TEXTURE_SKIN`. Keep component boundary, coordinate frame, interface owner, and fusion contract in this skill; let the texture skill choose geometry, toolpath, material/finish, or localized heightmap representation.
- Use `3d-print-heightmap-relief` when a surface is fundamentally a continuous-tone 2.5D relief rather than a free-standing 3D component.
- Use `reconstruct-printable-3d-from-images` as the primary route instead of this skill when the object is intentionally monolithic and has no meaningful hybrid architecture.

## Workflow

### 1. State the claim and evidence

Classify the goal as measured replica, visual interpretation, plausible completion, functional redesign, or new design. Record source images, text requirements, known dimensions, intended use, process/material, printer envelope, and unresolved choices.

Put every unresolved or provisional choice in `decision_log` with its current basis, evidence needed, and the validation gates it blocks. Treat planner `PASS` as structural plan integrity, not as production or release approval; read the reported blocked gates separately.

For a concept image, distinguish observed geometry from shading, texture, material, and invented hidden regions. For a text concept, convert scenarios and requirements into functions before choosing shapes. Read [references/decomposition-and-routing.md](references/decomposition-and-routing.md).

Copy [assets/hybrid-design-plan.template.json](assets/hybrid-design-plan.template.json) and keep it current. Validate it against [assets/hybrid-design-plan.schema.json](assets/hybrid-design-plan.schema.json) and the bundled planner.

### 2. Build three linked decompositions

Create:

- a functional tree: support, guide, contain, move, seal, mount, illuminate, customize, service;
- a physical/component tree: solids, shells, ornaments, fasteners, electronics, flexible parts, voids, and fixtures;
- an appearance tree: silhouette, secondary forms, relief, texture/color, material boundaries, and lighting-only cues.

Map the trees rather than forcing one hierarchy to serve all purposes. Draw an interface graph for every pair that exchanges load, motion, material, air/fluid, light, heat, or assembly constraint.

### 3. Allocate representation authority

Classify each component:

| Authority | Use for | Avoid |
|---|---|---|
| `parametric` | datums, load paths, walls, fits, motion, seals, repeated/scalable geometry | forcing high-frequency sculpture into fragile CAD |
| `organic` | sculpture, free-form ornament, appearance-dominant shells | critical holes, snaps, bearings, threads, clearances |
| `hybrid` | visible organic skin plus parametric backer/core/interface | ambiguous dual ownership of the seam |
| `purchased` | screws, magnets, LEDs, bearings, sheet goods, textiles | recreating standard hardware without reason |
| `negative/tooling` | keep-outs, swept volumes, cutters, gauges, molds, fixtures | exporting accidental helper bodies as product parts |

When uncertain, make a coarse parametric envelope first and retain the organic region as replaceable. Do not create detail until every component has a reason to exist and an acceptance test.

### 4. Freeze the interface skeleton

Define one right-handed project frame in millimetres, a master envelope, stable datums, local frames, at least three non-collinear registration landmarks where practical, functional keep-outs, contact/clearance volumes, and an assembly order.

For each interface record:

- component pair and single nominal owner;
- local origin/axes and saved 4×4 transform;
- nominal seat/patch/axis/profile and tolerance;
- joining strategy, load direction, anti-rotation, lead-in, access, and service plan;
- seam/edit band in which organic geometry may be trimmed or blended;
- minimum wall/ligament, protected surface, and keep-outs;
- separate allowance terms and verification method.

Read [references/interface-contracts.md](references/interface-contracts.md). Design the parametric counterpart and exported trim/backer/clearance bodies before requesting final organic meshes.

### 5. Specify organic components as generation jobs

Create a separate image-to-3D brief for every organic component unless a verified part-aware model accepts stable part masks/identities. Use:

```bash
python scripts/plan_hybrid_design.py project.json \
  --report reports/architecture.md --briefs-dir briefs
```

Provide a clean generation plate, evidence crop, mask, target envelope, semantic identity, view convention, style lock, protected features, sacrificial interface band, and explicit exclusions. Use multi-view inputs only when the selected model genuinely supports them.

Generate multiple low/medium-resolution candidates. Select massing, silhouette, negative space, and seam compatibility before texture. Read [references/component-image-briefs.md](references/component-image-briefs.md).

### 6. Register and normalize each returned mesh

Preserve the raw mesh and checksum. Record units, axes, components, watertightness, bounds, volume, and transform. Align first from datums/landmarks or fitted primitives; use ICP only as a local refinement after a credible initial placement.

Run an intake check when `trimesh` is available:

```bash
python scripts/inspect_component_mesh.py project.json ORNAMENT_ID raw.glb \
  --report reports/ORNAMENT_ID-intake.json
```

Reject identity swaps, merged parts, missing negative spaces, false symmetry, thin sheets, internal shells, uncontrolled backside invention, and detail below the manufacturing budget. Trim only inside the declared seam/edit band.

### 7. Integrate with a controlled method

Choose one primary route:

- cut-and-replace;
- separate keyed insert/inlay;
- organic shell over parametric core;
- organic body plus parametric backer/connector;
- relief/height map mapped to a controlled substrate;
- split multi-material assembly;
- final mesh Boolean with documented overlap;
- SDF/voxel union only where mesh condition requires it and detail loss is acceptable.

Prefer the detailed mesh in mesh-native tools and exact interfaces in CAD. Never convert a dense full mesh into one B-Rep face per triangle. Read [references/integration-and-validation.md](references/integration-and-validation.md).

### 8. Validate from proxies to production

Gate the work in this order:

1. architecture: requirements allocated, interface owners unique, assembly sequence feasible;
2. proxy: envelopes, keep-outs, swept volumes, access, and bed fit;
3. component: scale, axes, topology, bounds, landmarks, silhouette, and seam reserve;
4. integration: wall/ligament, overlap/gap, retention, surface preservation, no hidden islands;
5. manufacturing: orientation, toolpaths, material compatibility, supports, color-body separation;
6. physical: fit coupon, uncertain subassembly, then full prototype.

Generate an FDM XY fit series instead of guessing a universal clearance:

```bash
python scripts/generate_fit_coupon.py --output fit-coupon.scad \
  --clearances-mm 0.15,0.25,0.35,0.45
```

Use the same printer, nozzle, material, orientation, and profile as the real interface.

### 9. Deliver reproducibly

Include:

- source evidence and requirement/uncertainty ledger;
- decision log with unresolved items, blocked gates, and release status;
- completed hybrid design plan and interface matrix;
- coarse assembly/envelope and keep-out bodies;
- raw and registered organic meshes plus saved transforms;
- parametric masters, interface/backer/trim/cutter bodies, and purchased-part envelopes;
- separated manufacturing bodies and final 3MF/STL/STEP/GLB as appropriate;
- matched renders, section views, mesh/fit/slicer reports, coupon results, and unresolved risks.

Retain separate authorities. The fused STL/3MF is a derived manufacturing artifact, not the editable master.

## References and examples

- [references/decomposition-and-routing.md](references/decomposition-and-routing.md): source interpretation, dual decomposition, representation allocation, granularity.
- [references/component-image-briefs.md](references/component-image-briefs.md): component masks, generation plates, multi-view rules, sacrificial roots, relief and curved-surface cases.
- [references/interface-contracts.md](references/interface-contracts.md): coordinate frames, ownership, allowance stack, backers, sockets, seams, and CAD counterpart patterns.
- [references/integration-and-validation.md](references/integration-and-validation.md): registration, Boolean/SDF/assembly routes, validation gates, release structure.
- [references/research-and-pitfalls.md](references/research-and-pitfalls.md): primary research, official documentation, field failure patterns, and evidence limits.
- `examples/ornamented-wall-dispenser.json`: concept-image-led household product.
- `examples/barefoot-shoe-hybrid.json`: curved wearable interface and flexible material.
- `examples/decorative-enclosure.json`: description-led enclosure with electronics and service access.

## Safety boundary

Escalate to qualified engineering review for pressure vessels, lifting/climbing hardware, vehicle controls, mains/fire systems, medical devices, weapons, food-contact claims, or child-safety-critical products. Keep generated ornament outside safety-critical load paths unless separately engineered and tested.
