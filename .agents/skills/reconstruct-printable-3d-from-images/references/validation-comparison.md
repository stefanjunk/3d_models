# Validation and source-image comparison

## Contents

1. [Validation hierarchy](#1-validation-hierarchy)
2. [Make images comparable](#2-make-images-comparable)
3. [Visual comparison checklist](#3-visual-comparison-checklist)
4. [Metrics and interpretation](#4-metrics-and-interpretation)
5. [Geometry and mesh validation](#5-geometry-and-mesh-validation)
6. [Slicer and physical validation](#6-slicer-and-physical-validation)
7. [Acceptance plan](#7-acceptance-plan)
8. [Regression workflow](#8-regression-workflow)

## 1. Validation hierarchy

Validate from strongest evidence to weakest:

1. direct physical measurements;
2. calibrated multiview geometry/camera solution;
3. calibrated single-view dimensions on known planes;
4. silhouettes and landmarks from matched views;
5. shading/texture cues;
6. category priors and artistic assumptions.

A 2D image comparison validates reprojection from that camera. It does not prove the back, internal geometry, scale, wall thickness, or function. Add independent views and physical tests.

Use gates:

- **G0 Evidence:** sources preserved, scale/camera limits recorded.
- **G1 Specification:** requirement ledger and uncertainty map complete.
- **G2 Blockout:** dimensions, cameras, envelope, primary silhouettes accepted.
- **G3 Geometry:** sections, openings, interfaces, and secondary forms accepted.
- **G4 Appearance:** relief, color, and texture accepted separately.
- **G5 Print master:** mesh and slicer checks pass.
- **G6 Physical:** coupons/prototype meet measured acceptance.

Do not spend heavily on a later gate while an earlier critical gate fails.

## 2. Make images comparable

### Camera

Match:

- perspective versus orthographic projection;
- focal length and sensor fit/aspect;
- camera position and orientation;
- principal framing/lens shift;
- object pose and origin;
- source crop, resolution, and aspect ratio.

Keep a camera manifest. For photogrammetry, use recovered intrinsics/extrinsics. For an illustration, record that no physical camera may match exactly.

### Render conditions

For shape comparison:

- use a matte clay material;
- use neutral broad lighting that reveals form without dramatic cast shadows;
- render alpha or an object-ID mask;
- keep background uniform;
- disable depth-of-field and motion blur;
- use consistent color management across revisions.

For appearance comparison, approximate source illumination separately. Do not mix shape and material judgments into one render when a failure could be caused by either.

### Alignment policy

Use three modes:

1. **Locked:** no 2D alignment; preferred acceptance mode after camera calibration.
2. **Documented similarity:** translation and uniform scale only; diagnostic for crop/scale error.
3. **Prohibited for acceptance:** non-uniform scale, rotation, perspective warp, optical flow, or local deformation that could hide model/camera error.

Report any alignment transform. Compare the locked result first.

### Masks

Use reviewed hard masks for silhouette metrics. Exclude unrelated supports/ground shadows consistently. Keep holes and negative spaces as background. If a transparent or reflective part has ambiguous silhouette, annotate it rather than forcing a binary truth.

## 3. Visual comparison checklist

Review every source view at full frame and at critical crops.

### Evidence and camera

- [ ] Correct source revision and model revision are paired.
- [ ] Original aspect ratio and orientation are preserved.
- [ ] Projection type is correct.
- [ ] Focal length/camera distance or orthographic scale is plausible and locked.
- [ ] Object pose, ground plane, and crop match.
- [ ] Lens distortion or perspective correction is documented.
- [ ] Mask includes holes and excludes cast shadow/props as intended.

### Envelope and proportions

- [ ] Overall width, height, and visible depth match.
- [ ] Centerline, symmetry plane, and center of mass align.
- [ ] Primary masses have correct relative size and placement.
- [ ] Front/side/top silhouettes agree simultaneously.
- [ ] Three-quarter views show correct volume, not merely correct orthographic outlines.

### Shape identity

- [ ] Negative spaces, holes, handle interiors, and limb gaps match.
- [ ] Cross-section character is correct: flat, round, oval, faceted, tapered.
- [ ] Convex/concave transitions occur at the right landmarks.
- [ ] Edge character and fillet/chamfer size match.
- [ ] Repeated features share intended spacing and phase.
- [ ] Thin parts are neither fused nor exaggerated.
- [ ] Contact points and base footprint match.

### Surface detail

- [ ] Detail changes geometry only where intended.
- [ ] Relief direction, depth hierarchy, and frequency match.
- [ ] Texture grain orientation remains coherent over seams/corners.
- [ ] Text/logos are legible, correctly oriented, and not perspective-traced into distortion.
- [ ] Lighting and highlights are not baked into geometry accidentally.

### Color and material

- [ ] Base colors are sampled from diffuse midtones.
- [ ] White balance and display/render transform are controlled.
- [ ] Color boundaries align with geometry/UVs.
- [ ] Metallic/rough/translucent cues are represented as appearance, not false shape.
- [ ] Printed color method and file-format support are verified separately.

### Hidden and inferred regions

- [ ] Every unseen region is marked inferred/assumed.
- [ ] Symmetry breaking is supported by evidence or stated design intent.
- [ ] Alternate topology/function hypotheses were considered where material.
- [ ] The model remains plausible from withheld/novel views.

### Function and manufacturing

- [ ] Critical dimensions and tolerances are checked numerically.
- [ ] Wall thickness, clearance, holes, and fits match process evidence.
- [ ] Print orientation preserves important source-facing surfaces.
- [ ] Supports, seams, and layer lines do not destroy critical appearance.
- [ ] Slicer retains all intended small features.

## 4. Metrics and interpretation

Use metrics as a panel. Do not collapse them into one undocumented score.

### Silhouette intersection over union

```text
IoU = area(reference ∩ candidate) / area(reference ∪ candidate)
```

Strength: detects gross boundary/area disagreement. Weakness: a high value can hide localized thin-part or opening errors. Report full silhouette and critical-region IoU separately.

### Precision, recall, and F1

For binary masks:

- precision exposes extra candidate area;
- recall exposes missing candidate area;
- F1 balances them.

Inspect false-positive and false-negative overlays; the same F1 can represent different failures.

### Boundary distance

Compute nearest-boundary distances in both directions:

```text
mean symmetric distance = (mean d(A→B) + mean d(B→A)) / 2
Hausdorff-like p95 = high percentile of both directed distances
```

Report pixels and normalized image diagonal. Convert to millimeters only when projection and scale on that plane are valid. Use the 95th percentile rather than maximum alone to avoid one mask speck dominating, but inspect the maximum region.

### Landmark error

For landmarks `i`:

```text
normalized error = mean distance(reference_i, candidate_i) / image diagonal
```

Use landmarks for joint centers, hole centers, extrema, seams, and curve inflections. Weight critical functional landmarks separately.

### Pixel/color error

Compute masked RGB/luma MAE only after camera, lighting, and color management are controlled. Use Lab/Delta-E diagnostics for color when a color-managed pipeline is available. Do not interpret color error from a clay render.

### SSIM

SSIM assesses local structural/luminance/contrast similarity and is more perceptual than raw MSE in many image-quality tasks. In this workflow it is optional and diagnostic. It can reward matched texture/lighting while geometry is wrong, so pair it with silhouette and landmarks.

### 3D metrics

When ground-truth scan/CAD exists, compare aligned surfaces with sampled Chamfer distance, Hausdorff percentiles, signed distance, and section deviations. Report alignment method and scale. A globally aligned surface metric can underweight a small critical interface; evaluate regions of interest.

### Thresholds

Set thresholds per project from:

- physical tolerance and image scale;
- segmentation uncertainty;
- source resolution/blur;
- feature priority;
- a baseline model and human review.

Do not publish “IoU > 0.95 means correct” as a universal rule. A toy silhouette may tolerate a different error distribution than a cable-clip opening.

## 5. Geometry and mesh validation

### Parametric/BRep master

- verify units and datums;
- check solid validity;
- measure bounding box, volume, and critical dimensions;
- evaluate section curves at documented stations;
- check minimum radii/walls and interface clearances;
- verify each parameter range still produces valid geometry.

### Print mesh

- verify expected units and scale after export/re-import;
- check connected-component count;
- check watertightness, winding, outward normals, degenerate faces, and duplicated/internal geometry;
- check self-intersections using the modeling/slicer tool;
- compare mesh bounds/volume against the master;
- compare coarse and final tessellation renders;
- check that decimation/remesh did not close openings or shrink thin parts.

`scripts/mesh_audit.py` covers several structural properties but cannot certify minimum wall thickness or self-intersection for every format. Use tool-native checks and slicer views.

## 6. Slicer and physical validation

### Slicer review

Use the exact machine/material/nozzle or resin profile. Inspect:

- units and target dimensions;
- orientation and first-layer contact;
- perimeters through critical walls;
- omitted, fused, or auto-repaired features;
- overhang/bridge/support contact regions;
- trapped volume and drain/vent paths;
- seams and color/tool changes;
- layer transitions across relief;
- expected fit compensation.

Save the project/profile or record all non-default settings used for acceptance.

### Coupons

Print a small coupon whenever uncertainty is local:

- line/relief width and depth ladder;
- hole/pin/slot clearance ladder;
- snap/clip arm variants;
- surface texture band at several amplitudes;
- bridge/overhang region in intended orientation;
- material-color sample.

Build coupons from the same code/parameters as the part.

### Prototype measurement

Define measurement tools and conditions before printing. Measure several repeated features, not one. Record nominal, as-printed, deviation, and uncertainty. For fit/motion, record pass/fail plus qualitative failure mode.

Update compensation only after separating printer calibration error from model error.

## 7. Acceptance plan

For every critical requirement, specify:

| Field | Example |
| --- | --- |
| Requirement | Cable channel fits 5.0–5.5 mm cable |
| Evidence | User measurement and photo |
| Digital check | CAD channel 5.7 mm; insertion path clear |
| Image check | opening landmarks within 1% diagonal |
| Slicer check | two continuous perimeters around channel |
| Physical check | 5.0 and 5.5 mm gauges insert; 6.0 mm rejected |
| Pass condition | all three gauges behave as specified |

Separate critical, important, and cosmetic thresholds. A cosmetic render miss must not hide a failed load-bearing feature; a mechanically safe redesign must not be presented as an exact replica if its silhouette changed.

## 8. Regression workflow

1. Freeze source images, masks, cameras, landmarks, and thresholds.
2. Render the same named views for each model revision.
3. Run `scripts/compare_views.py` into revision-specific directories.
4. Store metrics and overlays with the model revision.
5. Compare changed regions, not just aggregate scores.
6. Re-run mesh audit and slicer checks after topology/export changes.
7. Reprint only the affected coupon where possible.

If a metric improves because the camera or mask changed, treat it as a new baseline, not a model improvement. Review camera/mask diffs explicitly.
