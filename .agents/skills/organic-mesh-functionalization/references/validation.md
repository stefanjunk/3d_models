# Validation and acceptance testing

Validation must compare the result to both the source mesh and the functional specification.

## 1. Baseline and topology

Record before and after:

- vertices and faces;
- connected components;
- watertightness;
- winding consistency;
- boundary and over-connected edges;
- degenerate and duplicate faces;
- bounds and extents;
- volume, area, center of mass;
- optional self-intersection test;
- file size and estimated in-memory size.

A multi-part design may intentionally contain several components; encode the expected count.

## 2. Preservation outside ROI

Sample the original surface outside the permitted edit region and measure nearest-surface distance to the result. Report at least median, P95, P99, and maximum. Also sample the result outside ROI against the source to detect unexpected additions.

A high maximum with a low P95 may indicate one small breach; it still requires inspection.

Use `scripts/validate_edit.py` as a fast approximation. For critical work, use triangle-to-triangle distance or a signed-distance heat map rather than only vertex-nearest distance.

## 3. Removed and added volume

Compute:

- expected removed volume from cutter intersection;
- actual volume delta;
- expected insert volume;
- residual discrepancy.

Large disagreement can reveal missed cuts, internal duplicate shells, or unjoined inserts.

## 4. Wall thickness

Test critical regions using:

- ray casting along inward normals;
- maximal tangent sphere/thickness queries;
- section measurements;
- SDF distance to exterior;
- slicer thin-wall warnings.

Do not report a single global minimum without location. Exclude intentional sharp edges and openings using masks.

## 5. Interface and clearance

Measure:

- seam gap and overlap;
- insertion clearance;
- pin/hole and latch clearance;
- adhesive channel volume;
- lead-in length;
- anti-rotation engagement;
- minimum ligament around openings.

Print interface coupons before the full model.

## 6. Section and visual inspection

Generate:

- orthographic front/side/top views;
- transparent overlay of source and result;
- Boolean cutter overlay;
- section planes at critical stations;
- colored distance heat map;
- exploded view of inserts and clearances;
- slicer layer preview around openings and seams.

## 7. Use-case validation

### Dice tower

- simulate or physically test the largest supported die and several orientations;
- verify no trapped path or shelf;
- verify inlet/outlet dimensions and baffle spacing;
- perform repeated drop tests and inspect impact zones;
- verify tower stability and center of mass;
- check that supports can be removed or avoided.

### Barefoot sole

- verify outline, toe-box width, zero drop, local thickness, and flex line positions;
- bend and torsion coupons before the complete sole;
- test upper attachment peel/tear strength;
- inspect hidden cavities and water traps;
- use pressure data only as a comparative optimization input unless professionally measured.

### Toy compartment

- verify door sweep and access by intended fingers;
- cycle hinge/latch repeatedly;
- test pull-out and impact loads;
- remove sharp edges and pinch points;
- apply product-safety requirements appropriate to intended age and market.

## 8. Simulation policy

Use simulation to compare variants, not to create false certainty. Replace decorative geometry with a simplified surrogate containing the load paths, interfaces, minimum walls, and material regions. Calibrate printed-material properties with coupons when possible.

For FDM, account for orientation and anisotropy. For TPU or large deformation, use nonlinear/hyperelastic models if quantitative prediction is required.

## Acceptance report template

```yaml
geometry:
  watertight: true
  components: 1
  positive_volume: true
preservation:
  outside_roi_p95_mm: 0.12
  outside_roi_max_mm: 0.74
functional:
  minimum_wall_mm: 2.4
  opening_width_mm: 24.3
  clearance_mm: 0.45
manufacturing:
  fits_bed: true
  trapped_support: false
use_case:
  test: "100 dice drops"
  passed: true
```
