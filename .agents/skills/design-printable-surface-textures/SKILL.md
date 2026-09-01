---
name: design-printable-surface-textures
description: Design, select, generate, map, integrate, and validate efficient surface textures for printable FDM/FFF objects. Use for carbon-fiber weave looks, wood grain, stone, leather, fabric, hammered or brushed metal, knurling, floral or lotus motifs, image engraving that creates excessive mesh, vector or procedural relief, slicer Fuzzy Skin and top-surface patterns, distinct texture-skin parts, exposed infill used decoratively, custom extrusion paths or direct G-code, material/color/finish effects, and textures on flat, cylindrical, rounded, or freeform surfaces.
---

# Design Printable Surface Textures

Choose the lowest-complexity representation that creates the required physical or optical effect. Separate printable geometry from slicer state and material appearance; do not turn every reference image into a dense displacement mesh.

Resolve every bundled path relative to this `SKILL.md`. Keep the editable texture definition, exact product core, manufacturing parts, slicer project, and final fused print as distinct artifacts.

If the textured object is a new independently managed product, load
`3d-design-preflight` and complete its SKU, correct product-folder, portfolio
CSV/XLSX, license-chain, and prospective-preflight intake before generating
texture or geometry. A texture skin or finish for an existing product shares
the owning SKU and rights chain.

## Read only what the task needs

- Representation ladder and decision matrix: `references/representation-selection.md`
- Carbon, wood, stone, leather, metal, textile, knurl, and lotus patterns: `references/pattern-families.md`
- Slicer textures, multi-part objects, exposed infill, and direct toolpaths/G-code: `references/toolpaths-gcode-and-slicer-parts.md`
- Raster/mesh budgets, adaptive relief, mapping, seams, and simplification: `references/mesh-budget-and-mapping.md`
- Coupon design, measurements, slicer gates, and release criteria: `references/coupons-and-acceptance.md`
- Research basis, official documentation, and evidence limits: `references/evidence-and-sources.md`
- Worked plans: `examples/carbon-twill-flat.json`, `examples/wood-grain-curved.json`, and `examples/lotus-infill-panel.json`

## Route related work

- Use `3d-print-heightmap-relief` after this skill selects a localized continuous-tone heightmap route. Preserve its 16-bit master, physical scale, adaptive mesh, and relief acceptance workflow.
- Use `optimize-fdm-design` for structural lightweighting and for the complete framed exposed-infill contract. Surface appearance does not replace load-path design.
- Use `decompose-printable-designs` when the texture is one component in a larger parametric/organic/multi-material architecture.
- Use `organic-mesh-functionalization` when an existing dense organic mesh must receive exact interfaces or protected functional regions.

## Non-negotiable rules

1. **Name the intended effect.** Separate geometric silhouette, tactile relief, directed gloss, color/material, translucency, and porosity. One reference image may imply several effects that need different representations.
2. **Use physical resolution, not source pixels.** Define nozzle, measured line width, layer height, orientation, viewing distance, patch dimensions, smallest required feature, and relief height before generating detail.
3. **Do not rasterize a describable repeat by default.** Create carbon weave, grain centerlines, textile, knurl, ribs, rosettes, and other structured patterns as vectors, curves, procedural fields, or toolpaths before considering a heightmap.
4. **Do not model sub-process detail.** Move detail below a reliable extrusion/layer step into filament, color, sheen, bed-sheet imprint, coating, film, or another finish.
5. **Limit heightmaps to information that needs continuous local height.** Crop/mask flat background, denoise below process resolution, use adaptive meshing, and preserve the unsimplified reference separately.
6. **Protect functional geometry.** Exclude fits, seals, rails, bearings, fastener seats, datum faces, bed planes, thin walls, hand-contact edges, and load paths from uncontrolled texture displacement.
7. **Keep manufacturing identity when settings differ.** Retain `CORE`, `TEXTURE_SKIN`, `LATTICE_ENVELOPE`, modifier, and material bodies as named registered parts until slicing. Do not Boolean-union away the boundary required for per-part settings.
8. **Make one physical object deliberately.** For an in-place fused print, define positive capture/overlap or a keyed interface between generated texture paths and the core, inspect the connection in every affected layer, and print a joint coupon. Tangential CAD contact is not a bond.
9. **Treat slicer-defined texture as manufacturing data.** Preserve the exact 3MF/project, slicer/version, profile, part names, transforms, pattern, angles, line widths, flow, speed, and material. STL alone cannot carry these decisions.
10. **Treat direct G-code as machine-specific source code.** Generate paths parametrically, keep trusted machine start/end and safety routines, preview or simulate, check bounds/Z/extrusion modes/flow/acceleration/collisions, and prove the result on a small coupon before a product.
11. **Validate appearance and manufacturability separately.** A render does not prove toolpaths; a slicer preview does not prove tactile quality, gloss, adhesion, cleanability, wear, or acceptable visual scale.
12. **Do not imply structural properties from appearance.** A carbon-look surface is not a carbon laminate; a wood-look texture is not wood; an exposed decorative grid is not automatically a rated guard or load path.

## Mandatory workflow

### 1. Extract the texture intent

For a concept image, classify each cue as observed form, possible relief, lighting/shadow, reflection, color, material, or image noise. Do not reproduce highlights and shadows as geometry without independent shape evidence.

For a written design concept, record adjectives as measurable targets: directional or isotropic, regular or organic, smooth or tactile, matte or glossy, shallow or deep, cleanable or porous, unique or repeatable, and viewing/touch distance.

Record source provenance, target object/surface, process/material, printer/nozzle/profile, and whether the result must be one fused print, a multi-material print, or a replaceable skin.

### 2. Decompose the surface system

Allocate:

- `CORE`: exact envelope, wall reserve, loads, fits, seals, datums, and mounting;
- `MACRO_TEXTURE`: printable ribs, grooves, dimples, petals, knots, or relief above the path scale;
- `MESO_TOOLPATH`: nozzle-scale line direction, top pattern, Fuzzy Skin, exposed infill, or authored extrusion paths;
- `MATERIAL_FINISH`: color, sparkle, fill, translucency, gloss, coating, film, sanding, or paint;
- `TEXTURE_SKIN`: optional separately controlled body carrying one or more appearance layers;
- `KEEP_OUTS`: no-texture regions and seam/edit margins.

Give every dimension and interface one owner. Use a separate skin when it improves mapping, print orientation, material/color assignment, replacement, source-image swapping, or slicer control.

### 3. Select the representation ladder

Use `scripts/plan_surface_texture.py` before detailed geometry:

```bash
python scripts/plan_surface_texture.py \
  --pattern carbon-twill --source image \
  --surface horizontal-top --patch-mm 80x40 \
  --nozzle-mm 0.4 --line-width-mm 0.45 --layer-height-mm 0.20 \
  --smallest-feature-mm 1.8 --relief-mm 0.20
```

Treat its ratios and mesh gates as starting classifications, not printer guarantees. Normally choose:

1. material/finish for sub-path optical detail;
2. slicer or authored toolpaths for nozzle-scale direction and roughness;
3. vector/procedural CAD for repeatable macro relief;
4. localized adaptive heightmaps for irregular continuous-tone relief;
5. dense freeform mesh only when the visible result cannot be represented more compactly.

Read `references/representation-selection.md` before overriding this order.

### 4. Define physical pattern parameters

Specify millimetres, not image pixels:

- patch width/height and surface-distance coordinate system;
- motif/tile pitch, line/groove width, relief height/depth, duty cycle, and seed;
- direction field, grain/weave axis, phase, tile seam, fade/edit band, and protected margin;
- repeat strategy: integer repeat, controlled crop, or explicit small scale adjustment—never silent X/Y stretching;
- color/material/toolpath assignment and required part identity.

Generate editable vector source for structured patterns. For example:

```bash
python scripts/generate_surface_pattern_svg.py \
  --pattern carbon-twill --size-mm 80x40 \
  --pitch-mm 2.4 --stroke-mm 0.45 \
  --output build/carbon-twill.svg
```

Use the SVG as a curve/emboss/toolpath source; it is not machine-ready G-code.

### 5. Map to the target surface

Map in physical surface distance. Preserve scale and direction across seams. Use planar coordinates for flat patches, arc length for cylinders/rounded perimeters, and a measured low-distortion parameterization or surface projection for freeform patches.

Do not assume slicer infill or top-fill paths conform to a curved exterior. For a curved texture, prefer mapped vector/procedural geometry, a flat/formed insert, an organic skin with a parametric backer, or an explicitly validated non-planar path workflow.

### 6. Integrate without losing control

Choose one route:

- Boolean vector/procedural relief into `CORE` when one material/profile applies and the resulting mesh remains efficient;
- retain `TEXTURE_SKIN` as a keyed, bonded, snapped, or replaceable insert;
- retain aligned overlapping bodies in one multi-part 3MF when per-part material or slicer settings apply;
- retain `FRAME` plus `LATTICE_ENVELOPE` when wallless exposed infill forms a decorative/porous region;
- apply a localized relief cutter to an exact parametric substrate;
- create direct extrusion paths only for a controlled, machine-specific manufacturing job.

For a final one-piece print with distinguishable slicer parts, preserve a shared project origin, group the parts as one object, define a compatible capture band, and verify fused toolpaths. The editable master remains separated even when the manufactured result is physically continuous.

### 7. Control mesh and path complexity

Estimate a uniform heightmap worst case over only the displaced area:

```text
triangles ~= 2 * displaced_area_mm2 / (pitch_x_mm * pitch_y_mm)
```

Use about one million texture/relief triangles per manufacturing part as a portable workflow target, review one to five million in the exact toolchain, and redesign above five million unless measurements justify it. Reduce complexity in this order: shrink/mask patch, vectorize a structured motif, remove flat background, generate adaptively, simplify the relief cutter by physical error, then Boolean into exact CAD.

Inspect short toolpath segments separately. Fewer triangles do not guarantee faster G-code, and a vector pattern with hundreds of tiny cells can still print poorly.

### 8. Compare process-matched candidates

Create at least three candidates when the method is uncertain:

- `A — material/process`: no texture mesh; filament, finish, bed imprint, top paths, or Fuzzy Skin;
- `B — compact geometry`: vector/procedural relief;
- `C — localized image relief`: masked adaptive heightmap where needed;
- optional `D — custom path`: authored extrusion paths on a safe coupon.

Keep object, orientation, material, profile, lighting, and viewing distance fixed. Read `references/coupons-and-acceptance.md` and establish pass criteria before printing.

### 9. Release reproducibly

Deliver:

- texture intent and source/evidence classification;
- physical patch, resolution, motif, mapping, seam, and protected-region definitions;
- representation decision and rejected alternatives;
- editable vector/procedural/image master and seed/version;
- separate `CORE`, `TEXTURE_SKIN`, modifier, frame, and lattice bodies as applicable;
- mesh triangle/file metrics and exact-slicer import/slice warnings;
- exact 3MF/project/profile for slicer-defined behavior;
- direct-path source, machine assumptions, preview/simulation evidence, and safe test result when applicable;
- coupon matrix, measurements, chosen candidate, and remaining limitations;
- final manufacturing export plus unchanged editable masters.

## Safety boundary

Do not apply uncontrolled texture to sealing, bearing, electrical creepage, hygiene-critical, medical-contact, food-contact, child-safety, protective-guard, pressure, lifting, climbing, or vehicle-control surfaces. Escalate consequence-critical geometry and custom motion/G-code to qualified review and machine-specific testing.

## Deterministic validation handoff

Before release, load the sibling `validate-printable-3d-projects` skill and apply `assets/validation-profile.json`. Hash the editable texture master, mapping parameters, protected-region mask, core/skin bodies, manufacturing mesh, exact 3MF/profile, G-code, and coupon report. Run mesh, interface, G-code, 3MF, and parameter-sweep checks; retain motif scale, seam, pitch, triangle budget, surface deviation, and mapping diagnostics as fresh external reports. Appearance, tactility, adhesion, and cleaning behavior require a named physical coupon gate. Required `NOT_RUN`, `REVIEW_REQUIRED`, or stale evidence blocks release.

At project start, read the project autonomy policy before changing artifacts. Record only `AUTO_APPROVED` or `BLOCKED` in the agent ledger and only for stages assigned to the agent. Never write `HUMAN_APPROVED`; physical, appearance, safety, and commercial stages remain in the separate human ledger. Workflow autonomy does not authorize dependency installation, upload, or printer start.
