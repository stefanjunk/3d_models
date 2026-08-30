# Image-to-3D component brief — HARZ_HEIGHTFIELD: Harz global 16-bit height field and six seam-locked relief bodies

## Identity and authority

- Role: Harz terrain geometry, aspect, global vertical scale and Z-band authority
- Authority: `hybrid`; representation: `heightmap`
- Source: `derived` — immutable Copernicus GLO-30 snapshot, DEC-HARZ-DATA-001, REQ-HEIGHT, REQ-COLOR
- Source confidence: `medium`
- Target project envelope: `[0, 0, 3] → [600, 400, 10] (600 × 400 × 7 mm)`
- Source-to-mm scale currently recorded: `1.0`
- Project frame: row-major 4x4 matrix maps source and component coordinates to project millimetres

The generated mesh does not own critical mating geometry. Preserve a thick sacrificial root/band and trim it with the parametric interface kit after registration.

## Generation plate

- Mode: `relief_heightmap`
- Required views: source/harz/copernicus-dem-master.tif, build/harz/harz-master-16bit.preview.png
- Positive prompt: Process the frozen official Harz DEM as one continuous 600 x 400 mm physical terrain field, preserve elevations and aspect, use one global vertical transform, keep seams exact, and retain major summits and valleys within a 7 mm relief budget.
- Exclude: invented terrain, per-tile normalization, anisotropic stretch, posterization, photographic land cover, texture noise, independent tile color thresholds
- Sacrificial interface band: `8 mm`
- Plate setup: full uncropped silhouette; isolated target; neutral/transparent background; broad diffuse light; matte clay; no ruler, labels, arrows, scenery, or neighbouring product body.
- Keep evidence crops with context separate from these generation plates.

## Shared style lock

- Summary: Abstract gallery-like terrain with continuous geometry, four broad elevation colors and sparse luminous terrain traces
- Motifs: continuous landform, large contour masses, quiet external border, few luminous valleys or benches, visible but controlled module grid
- Global exclusions: photographic realism, land-cover simulation, dither, tiny color islands, independent tile contrast, LED components in the sold print set
- Generation material: matte Anycubic PLA palette with a neutral PETG rear grid
- Detail hierarchy: whole-region relief first, seam-locked major landforms second, major contour or bench breaks third, printable local terrain last

## Protected visual geometry

- global outer extent
- all seam sample rows and columns
- major summit hierarchy
- continuous valleys
- rear datum plane

## Required negative spaces

- light apertures are separate derived cutter bodies and never holes in the 16-bit master

## Registration landmarks

| ID | Project point (mm) | Meaning |
|---|---|---|
| HARZ-BL | [0, 0, 3] | global lower-left relief datum |
| HARZ-BR | [600, 0, 3] | global lower-right relief datum |
| HARZ-TL | [0, 400, 3] | global upper-left relief datum |

## Interfaces and keep-outs

- `IF-TILE-HARZ`: TERRAIN_TILE_SET ↔ HARZ_HEIGHTFIELD
  - nominal owner: `TERRAIN_TILE_SET`; kind: `relief_substrate`
  - nominal geometry: `{"continuous_bits": 16, "maximum_relief_depth_mm": 7.0, "reference_pitch_mm": [0.3, 0.3], "type": "planar 3 mm substrate with globally mapped continuous height field"}`
  - local origin: `[0, 0, 3]`
  - assembly: watertight height-field body fused to parametric substrate with positive volume along +Z during model construction
  - modeled non-adhesive clearance per side: `0 mm`
  - adhesive gap per side: `0 mm`
  - Boolean overlap: `0.2 mm`
  - seam/edit band: `8 mm`
  - keep-outs: KEEP-SEAMS, KEEP-DATUMS, KEEP-ATTRIBUTION

## Candidate acceptance order

1. Correct semantic identity, handedness, and expected component count.
2. Target envelope, silhouette, and required negative spaces.
3. Sufficient sacrificial root and no protected detail in the seam band.
4. No functional keep-out collision after recorded placement.
5. Printable feature hierarchy and topology suitable for the selected integration route.
6. Surface detail and texture only after a clay render passes.

Expected mesh components: `6`
Require watertight at intake: `True`
Maximum project-bounds error after registration: `0.15 mm`

Checks:

- 16-bit master
- physical aspect
- global normalization
- seam height equality
- 7 mm relief cap
- mesh budget

## Return package

- raw model output with original nodes/materials and model/settings/seed where available;
- generation plates, masks, and named view convention;
- clay renders from required views;
- no destructive repair, scale bake, or fusion with the product core before intake;
- explicit note for invented backside/hidden regions.
