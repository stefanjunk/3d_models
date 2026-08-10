---
name: casting-negative-molds
description: Use when designing or validating printable negative molds, masters, cases, and plaster-working-mold workflows for porcelain, stoneware, gypsum, plaster, and related casting materials.
license: MIT
compatibility: OpenCode Agent Skills; Python 3.10+; optional OpenSCAD, CadQuery, FreeCAD, or Blender
metadata:
  domain: 3d-printing
  version: 1.0.0
  languages: de,en
---

# Casting Negative Molds

Create production-aware tooling for casts from arbitrary 3D objects. Treat geometry, casting material, demolding, shrinkage, surface transfer, and workshop process as one system.

## First principle: classify the process before modeling

Never use “negative mold” as a single undifferentiated concept.

1. **Gypsum/plaster as the final cast:** a sealed printed negative can often be the working mold. Select a compatible release system and prove it on a coupon.
2. **Conventional porcelain/stoneware slip casting:** ordinary FDM/SLA plastic is non-absorbent. Normally print a positive master or a reusable case, then cast an absorbent pottery-plaster working mold. Do not seal the slip-contact face of that plaster working mold.
3. **Solid ceramic press, ram, slump, or drain casting:** choose a process-specific positive/negative tool chain; do not assume the hollow slip-casting workflow.
4. **Experimental porous printed molds:** treat as R&D. Require measured permeability, water uptake, release, wear, and contamination tests before recommending production use.

Read [process-selection.md](references/process-selection.md) whenever the casting route is not explicit.

## Required intake

Resolve as much as possible from the request and source files. Record assumptions instead of blocking progress.

- Final cast material and exact body/product where known.
- Final dimensions after drying/firing; intended quantity and reuse count.
- Source type: STEP/BREP, manifold mesh, scan, height map, or image-derived mesh.
- Printer process, build volume, nozzle/pixel size, layer height, material, enclosure, and tolerance history.
- Desired transferred detail, surface finish, visible seam tolerance, and post-processing.
- Candidate pull directions, allowed parting lines, open faces, and sacrificial regions.
- Fill method, drain requirement, reservoir/spare, vents, clamp access, and cleaning access.
- For food-contact ceramics: country/market, food type, contact time/temperature, dishwasher expectation, body/glaze/decor system, and validation plan.

## Standard workflow

### 1. Preserve and inspect the source

Keep the original immutable. Work on a copy. Use `mesh-validation` for the
generic immutable baseline, then `scripts/common/mesh_preflight.py` for
casting-specific draft and pull-direction screening. Log:

- units and bounding box;
- vertex/face count and connected components;
- watertightness, winding, volume, boundary/non-manifold edges;
- degenerate/tiny triangles and edge-length distribution;
- likely thin regions, self-intersections, floating fragments, and open cavities.

Repair only what is understood. A remesh can erase ornament, sharpen seams, or close deliberate holes. Prefer local repair over global voxelization.

### 2. Define the final cast and compensate shrinkage

The user normally specifies the **final** dimensions. Derive tool dimensions from measured linear shrinkage for the exact body, preparation, drying, firing schedule, and orientation.

For shrinkage fraction `s`, use `tool_dimension = final_dimension / (1 - s)`. Use independent X/Y/Z values when tests show anisotropy. Run `scripts/common/shrinkage_calculator.py` and save the inputs in the manifest.

Never use a generic ceramic shrinkage value as production truth. Create and measure a representative coupon first.

### 3. Choose pull directions and parting topology

For every rigid mold part, prove that it can translate or rotate away without crossing the cast. Then:

- place seams on low-visibility, low-curvature, or naturally sharp boundaries;
- avoid undercuts relative to each pull vector;
- add draft as a starting heuristic, then increase it for deep or rough texture;
- split around re-entrant details, rims, capitals, handles, feet, and closed loops;
- use flexible inserts, sacrificial cores, soluble cores, or a silicone skin plus rigid mother mold when rigid segmentation becomes impractical.

Use [geometry-and-demolding.md](references/geometry-and-demolding.md) for pull tests, draft, keys, seam placement, and trapped-volume checks.

### 4. Choose a mold architecture

Select one or combine several:

- solid block negative;
- hollow conformal shell;
- thin shell with external ribs, flanges, and local bosses;
- thin precision insert in a reusable cottle/frame;
- modular panels or ring segments;
- flexible skin with a rigid mother mold;
- sacrificial/breakaway mold or core;
- printed master/case that produces an absorbent plaster working mold;
- casting-face-only insert backed by commodity boards, sand, plaster, or reusable fixtures;
- nested replaceable detail inserts in a durable structural mold.

Default to the least material that still controls distortion, clamping, hydrostatic load, handling, and seam registration. Read [mold-architectures.md](references/mold-architectures.md).

### 5. Design filling, draining, venting, and handling

Do not add a funnel blindly.

- **Open-face cast:** provide a level rim, overflow/screed ledge, and a way to vibrate or tap the mold.
- **Closed solid cast:** feed from a low-visibility high point; add vents at every local air trap; use a reservoir/spare above the casting to feed settlement or shrinkage.
- **Hollow slip cast:** use a removable pour spout/reservoir, a clean drain path, and a stable inverted draining position. The absorbent plaster working mold must remain exposed to the slip.
- **Complex cavity:** use multiple gated inlets only when flow and venting justify the extra seams.

Make channels printable, cleanable, and removable. Avoid blind pockets that trap casting material or wash water.

### 6. Add interfaces

Provide:

- registration keys that constrain all required degrees of freedom without over-constraining assembly;
- broad clamp flanges and defined clamp zones;
- pry tabs or jacking-screw pads that cannot damage the cast;
- replaceable sprue/funnel inserts where wear or cleanup is expected;
- labels, orientation marks, mold-part IDs, datum surfaces, and assembly order;
- drain stands, cradles, and drying racks when part of the real workflow.

Keep keys away from thin edges and delicate ornament. Use asymmetric key layouts so parts cannot be assembled incorrectly.

### 7. Allocate resolution deliberately

Detail transfer is limited by the complete chain: source, CAD tessellation, printer XY/Z capability, surface finishing, plaster reproduction, green-body shrinkage, firing, and glaze flow.

Use `scripts/common/memory_estimator.py` before voxel/remesh work. Delegate all
relief-image preparation and physical sampling to
`3d-print-heightmap-relief/scripts/prepare_heightmap.py`; do not maintain a
casting-specific image converter. Prototype with a detail-transfer coupon from
`scripts/cadquery/detail_coupon.py`.

Starting points, not guarantees:

- 0.4 mm FDM nozzle: 0.10–0.16 mm layers; favor relief widths around 0.5–0.8 mm or larger and depths around 0.2–0.5 mm or larger.
- 0.25 mm FDM nozzle: 0.06–0.12 mm layers; test features around 0.3–0.5 mm and above.
- SLA/MSLA: finer relief is possible, but support marks, resin inhibition/contamination, dimensional drift, and sealing/release remain process risks.

Use at least 2–3 samples across the smallest intended image feature. Do not convert an entire 300 mm object to 0.1 mm voxels merely to preserve a small ornament; isolate and process the detailed region.

Read [resolution-and-memory.md](references/resolution-and-memory.md).

### 8. Generate in the appropriate tool

- **OpenSCAD:** simple CSG, blocks, planar splits, fixtures, and parameterized demonstrations. Avoid 3D Minkowski on dense imported meshes unless the cost is proven acceptable. Read [tool-openscad.md](references/tool-openscad.md).
- **CadQuery:** dimensional BREP/STEP workflows, robust parametric mold frames, keys, flanges, ribs, channels, and export. Use STEP for imported solids; do not assume normal CadQuery import supports STL. Read [tool-cadquery.md](references/tool-cadquery.md).
- **FreeCAD:** GUI inspection plus Part/Part Design booleans; useful for hybrid STEP and mesh workflows. Dense mesh-to-shape-to-solid conversion can become extremely heavy. Read [tool-freecad.md](references/tool-freecad.md).
- **Blender:** organic/high-poly meshes, sculpted parting surfaces, local voxel remesh, shrinkwrap, solidify, displacement, and mesh booleans. Apply scale and validate manifoldness before export. Read [tool-blender.md](references/tool-blender.md).

Use tool scripts as baselines, not black boxes:

- `scripts/openscad/negative_mold.scad`
- `scripts/cadquery/block_mold.py`
- `scripts/freecad/negative_mold.py`
- `scripts/blender/negative_mold.py`

### 9. Validate before a full-size print

Run the checklist in [validation.md](references/validation.md). At minimum prove:

- correct units, final dimensions, compensation, and orientation;
- valid, closed cavity and separate manifold mold parts;
- mold-part removability and cast removability;
- no unreachable supports, trapped liquid, trapped air, or blind wash cavities;
- adequate walls, ribs, flanges, keys, clamp zones, and edge radii;
- continuous sprue/drain/vent paths with sufficient printable diameter;
- slicer preview has no missing walls, accidental bridges, or unsupported ceilings;
- a small-scale assembly test and full-scale detail/process coupon succeed.

### 10. Package the result

Return:

1. a process classification and why it was chosen;
2. assumptions and unresolved production variables;
3. mold architecture, pull vectors, parting strategy, and assembly order;
4. scale/shrinkage calculation;
5. resolution and memory budget;
6. source files plus neutral exports and a machine-readable manifest;
7. slicer/process recommendations;
8. inspection, casting, demolding, cleaning, drying, and storage instructions;
9. risks, test coupons, and explicit acceptance criteria.

## Material-specific safety gates

### Porcelain and stoneware

Do not call a normal sealed printed negative a conventional slip-casting working mold. Route to a porous plaster working mold unless an experimental porous process is explicitly requested and validated. Keep release agents and sealers off the working absorbent face.

### Gypsum/plaster final casts

Printed negatives may be used directly, but first verify print material, sealer, release chemistry, exotherm, water exposure, seam leakage, and demolding. Never cast plaster on body parts. Control dust and follow the selected product safety data.

### Food-contact ceramics

Do not claim “food safe” from filament, body, or glaze marketing alone. The final fired object—including body, glaze, decorations, firing, fit, defects, and intended use—must meet the current rules for the target market. Prefer a smooth, fully matured food-contact interior and place very fine/deep ornament on the exterior. Read [food-contact-ceramics.md](references/food-contact-ceramics.md).

## Three worked routes

- 300 mm Roman pillar with marble relief: [example-roman-pillar.md](references/example-roman-pillar.md)
- Marble-look floor tile with sunflower engraving: [example-sunflower-tile.md](references/example-sunflower-tile.md)
- Decorated food-serving bowl: [example-food-bowl.md](references/example-food-bowl.md)

Example manifests are in `assets/examples/`. Run:

```bash
python scripts/common/mold_planner.py assets/examples/roman-pillar.json
```

## Stop conditions

Stop and report the design risk instead of generating misleading production geometry when:

- the casting route is incompatible with the tool material;
- the source scale or final dimension is unknown and cannot be inferred;
- a rigid mold contains unresolved undercuts or a trapped core;
- shrinkage is guessed for a final-size ceramic production run;
- a high-resolution global operation exceeds the memory budget;
- a food-contact or dishwasher-safe claim lacks a final-body validation route.

## Reference map

Load only what is needed:

- Process choice: `references/process-selection.md`
- Demolding and geometry: `references/geometry-and-demolding.md`
- Material-saving architectures: `references/mold-architectures.md`
- Resolution/memory: `references/resolution-and-memory.md`
- Workshop/material handling: `references/materials-and-workshop.md`
- Tool implementation: `references/tool-*.md`
- Verification: `references/validation.md`
- Food-contact: `references/food-contact-ceramics.md`
- Research links: `references/sources.md`
