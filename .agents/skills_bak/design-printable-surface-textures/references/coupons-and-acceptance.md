# Surface-texture coupons and acceptance

## Contents

1. Freeze the baseline
2. Build a compact candidate matrix
3. Design the coupon
4. Measure geometry and process
5. Evaluate appearance and use
6. Accept and release
7. Common experimental errors

## 1. Freeze the baseline

Record:

- object/source revision and units;
- printer, firmware, nozzle/hotend, build surface;
- filament product, batch/condition/drying;
- orientation, layer height, line widths, wall generator, flow, speed, acceleration, cooling, and supports;
- slicer/path generator and version, exact profile and 3MF/project;
- intended lighting, viewing distance, touch direction, and use environment.

Change one method family at a time. If material or nozzle changes, label it as a process candidate rather than attributing the result only to geometry.

## 2. Build a compact candidate matrix

Use at least:

| Candidate | Geometry | Process | Purpose |
|---|---|---|---|
| Baseline | plain surface | current | reference |
| A | none or simple envelope | material/top paths/Fuzzy Skin | isolate process effect |
| B | vector/procedural | current | isolate compact geometry |
| C | localized adaptive heightmap | current | test irreducible image relief |
| D optional | none | authored paths | test custom topology |

For a repeated pattern, test coarse, medium, and fine motif pitch. For a texture/core joint, test at least two capture/overlap values. Do not change depth, pitch, material, and speed simultaneously.

## 3. Design the coupon

Use the smallest coupon that reproduces:

- actual surface orientation and curvature;
- final wall/backer thickness and hidden reinforcement;
- pattern seam, edge frame, and protected margin;
- texture-to-core or lattice-to-frame joint;
- intended material/color/tool assignment;
- representative lighting and touch area.

A flat coupon does not validate a cylindrical seam. A top-surface coupon does not validate a vertical wall. Include a curved strip or corner when mapping or layer sampling is uncertain.

Suggested fields for a `50–80 mm` visual coupon:

- plain baseline;
- coarse/medium/fine pattern scale;
- one- versus two-layer shallow relief;
- material/process-only comparison;
- seam or capture-band section.

These dimensions are packaging guidance, not feature-size limits.

## 4. Measure geometry and process

Record:

- source and final triangle count/file size;
- slicer import/slice time and warnings;
- print time, material, path lengths, retractions, short segments, and tool changes where available;
- actual line/groove width, pitch, relief height/depth, aperture, and seam offset;
- continuity and pull/bend result at the core/frame connection;
- wall thickness and dimensional change near protected regions;
- crossing buildup, nozzle marks, stringing, warp, and first-layer behavior.

For simplified relief, preserve the reference mesh and measure physical surface error and contrast retention before slicer comparison.

## 5. Evaluate appearance and use

Define pass criteria before seeing the samples:

- recognition of intended family at target viewing distance;
- correct direction and scale under intended lighting;
- acceptable gloss/color variation across rotations;
- tactile strength, comfort, snagging, abrasion, and wear;
- cleanability, liquid/dirt trapping, and coating compatibility;
- no interference with fit, sealing, movement, or handling;
- acceptable joins, seams, and transitions to plain surface;
- required translucency, airflow, flexibility, or open-area ratio for porous textures.

Photograph every coupon with fixed camera, exposure, white balance, light direction, and scale marker. Rotate directional samples through at least three viewing/light angles. Record both dry and service-relevant conditions for grip or wet surfaces.

Do not use a beauty render as the acceptance reference. Use the actual concept/effect statement and measured coupon.

## 6. Accept and release

Accept only when:

1. the selected representation is the simplest candidate meeting the stated effect;
2. protected dimensions, walls, interfaces, and load paths pass;
3. mesh and exact-slicer gates pass;
4. the texture/core connection passes a process-matched coupon when fused in place;
5. direct paths pass complete-file preview/simulation and a machine-specific coupon;
6. appearance and service criteria pass under fixed evaluation conditions;
7. editable source, seed/tile/scale, named bodies, and exact manufacturing project are preserved.

Reject or revise when the result depends on an unrecorded slicer setting, a single lucky print, tangent contact, hidden mesh repair, uncontrolled image noise, or detail below reliable process scale.

## 7. Common experimental errors

- Comparing different colors/materials under automatic camera exposure.
- Using nominal infill density as though it guaranteed equal open area.
- Measuring pattern pitch in the SVG but not after curved mapping.
- Simplifying the entire part and damaging functional faces.
- Printing only the visually best scale rather than locating the failure boundary.
- Testing a lattice without its final frame joint.
- Evaluating carbon weave from one light angle only.
- Calling wood-like roughness successful without checking cleaning and hand feel.
- Keeping only G-code or only STL, so the chosen method cannot be reproduced.
