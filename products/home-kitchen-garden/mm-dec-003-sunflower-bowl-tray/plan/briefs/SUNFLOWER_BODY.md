# Image-to-3D component brief — SUNFLOWER_BODY: Step1X sunflower appearance preform

## Identity and authority

- Role: visible one-piece flower form and tray massing
- Authority: `organic`; representation: `mesh`
- Source: `concept_image` — organic/reference/sunflower-step1x-plate-003.png, design-spec.yaml
- Source confidence: `medium`
- Target project envelope: `[-100, -100, 0] → [100, 100, 65] (200 × 200 × 65 mm provisional)`
- Source-to-mm scale currently recorded: `105.43125475183143`
- Project frame: row-major 4x4 matrix maps Step1X source coordinates to project millimetres

The generated mesh owns the complete flower body and must not be repaired or parametrically reconstructed. Only uniform registration and the owner-confirmed 80 × 6 mm disc-foot union are permitted.

## Generation plate

- Mode: `single_view_whole_object`
- Required views: front-right three-quarter, slightly elevated
- Positive prompt: One coherent low shallow sunflower tray with twenty broad softly curved petals, a broad accessible central depression and sparse raised sunflower seed detail, shown as matte warm yellow clay.
- Exclude: text, logo, ruler, ground plane, cast shadow, hands, contents, separate seeds, floating fragments, thin sheets, open lattice, deep vase form
- Foot-only interface band: `6.1 mm`
- Plate setup: full uncropped silhouette; isolated target; neutral/transparent background; broad diffuse light; matte clay; no ruler, labels, arrows, scenery, or neighbouring product body.
- Keep evidence crops with context separate from these generation plates.

## Shared style lock

- Summary: one coherent soft sunflower tray with rounded petals and readable medium-scale seed detail
- Motifs: radial sunflower petals, broad shallow bowl, spiral-like seed disc
- Global exclusions: text, logo, floating fragments, thin lattice, detached seeds, cast shadow geometry, micro-noise
- Generation material: matte warm yellow clay with broad diffuse lighting
- Detail hierarchy: tray silhouette first, petals second, sparse printable seed relief last

## Protected visual geometry

- outer radial petal silhouette
- rounded petal ridges
- central seed-disc relief
- open central depression

## Required negative spaces

- the central depression remains open from above

## Registration landmarks

| ID | Project point (mm) | Meaning |
|---|---|---|
| LM-CENTRE | [0, 0, 0] | project centre on final bed plane |
| LM-X-PETAL | [100, 0, 20] | positive X silhouette extremum after registration |
| LM-Y-PETAL | [0, 100, 20] | positive Y silhouette extremum after registration |

## Interfaces and keep-outs

- `IF-BODY-BED-DATUM`: SUNFLOWER_BODY ↔ FOOT_DISC
  - nominal owner: `FOOT_DISC`; kind: `other`
  - nominal geometry: `{"nominal_support_diameter_mm": 80.0, "nominal_thickness_mm": 6.0, "target_min_z_mm": 0.0, "type": "disc_foot"}`
  - local origin: `[0, 0, 0]`
  - assembly: positive disc Boolean union with 5.9 mm overlap along +Z
  - modeled non-adhesive clearance per side: `0 mm`
  - adhesive gap per side: `0 mm`
  - Boolean overlap: `5.9 mm`
  - seam/edit band: `6.1 mm`
  - keep-outs: KEEP-TRAY-DEPRESSION, KEEP-VISIBLE-UPPER

## Candidate acceptance order

1. Correct semantic identity, handedness, and expected component count.
2. Target envelope, silhouette, and required negative spaces.
3. No body change outside the authorized cylindrical foot ROI.
4. No functional keep-out collision after recorded placement.
5. Printable feature hierarchy and topology suitable for the selected integration route.
6. Surface detail and texture only after a clay render passes.

Expected mesh components: `1`
Require watertight at intake: `True`
Maximum project-bounds error after registration: `0.2 mm`

Checks:

- 200 mm registered envelope
- provisional height at or below 65 mm
- open tray depression
- no thin or detached petal tips

## Return package

- raw model output with original nodes/materials and model/settings/seed where available;
- generation plates, masks, and named view convention;
- clay renders from required views;
- no destructive repair, scale bake, or fusion with the product core before intake;
- explicit note for invented backside/hidden regions.
