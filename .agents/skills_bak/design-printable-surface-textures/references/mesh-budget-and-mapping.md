# Texture mesh budget, adaptive relief, and surface mapping

## Contents

1. Diagnose the slicer complaint
2. Estimate uniform heightfield cost
3. Reduce complexity in the right order
4. Simplify by physical error
5. Map in surface distance
6. Protect interfaces and wall reserve
7. Validate geometry and toolpaths separately

## 1. Diagnose the slicer complaint

Distinguish:

- **large/slow import or memory warning:** likely excessive facets or bodies;
- **repair/non-manifold warning:** open edges, duplicate/internal faces, self-intersections, inverted shells, or failed Booleans;
- **slow print/controller behavior:** excessive short generated segments, not necessarily excessive source triangles alone;
- **missing texture:** features removed by slicing, below path/layer scale, or on unsupported surfaces;
- **unexpected roughness:** aliasing, noise, crossings, flow, cooling, or seam behavior.

Reducing triangles does not repair every topology defect. Repair diagnosed faults, then re-measure.

## 2. Estimate uniform heightfield cost

For a rectangular uniform grid:

```text
cells ~= displaced_area_mm2 / (pitch_x_mm * pitch_y_mm)
relief_triangles ~= 2 * cells
binary_STL_bytes ~= 84 + 50 * total_triangles
```

Example: a `200 × 100 mm` patch at `0.10 mm` pitch is about four million relief triangles before closure and Boolean splits. At `0.20 mm`, it is about one million.

Use `scripts/plan_surface_texture.py` to expose the cost before geometry. Treat target sample pitch as a printable-detail bound for high-gradient areas, not a command to triangulate every flat region uniformly.

Portable workflow gates per manufacturing part:

| Relief/texture triangles | Gate |
|---:|---|
| at or below about 1,000,000 | continue and benchmark exact slicer |
| above 1,000,000 through 5,000,000 | review adaptive/vector/path alternatives |
| above 5,000,000 | redesign unless measured toolchain evidence justifies override |

Record whole-job RAM, file size, import time, slice time, and controller behavior separately.

## 3. Reduce complexity in the right order

1. Apply texture only to visible approved patches.
2. Exclude backs, internal walls, interfaces, bed planes, and hidden overlap.
3. Replace structured repeats with vector/procedural definitions.
4. Move sub-process detail into material/finish/toolpath.
5. Crop or mask flat background and illumination artifacts.
6. Low-pass/denoise below the physical detail budget.
7. Generate adaptive height-field geometry from local error/curvature.
8. Simplify the closed relief cutter with locked borders and a millimetre tolerance.
9. Boolean the simplified cutter into exact CAD.
10. Remove redundant coplanar Boolean facets only after verifying protected faces.

Do not decimate the final product globally merely because one texture patch is dense.

## 4. Simplify by physical error

Keep an immutable source/build master and unsimplified reference mesh. Write manufacturing candidates separately.

For FDM, use the heightmap skill's candidate starting tolerance:

```text
t0 = min(
  0.10 * nozzle_diameter,
  0.20 * layer_height,
  0.125 * relief_depth,
  0.05 mm
)
```

Sweep around `0.5*t0`, `t0`, and `1.5*t0`; do not accept automatically. Lock:

- patch/tile boundaries and mapping seams;
- silhouette and sharp intentional creases;
- text, weave crossings, petal tips, and knots that carry identity;
- fits, seals, rails, holes, sockets, and fastener interfaces;
- bed/contact planes and minimum-wall regions.

Compare bidirectional surface distance, volume, relief amplitude/contrast, boundary position, wall reserve, and exact slicer paths. A target triangle percentage has no physical meaning by itself.

## 5. Map in surface distance

### Plane

Use direct metric X/Y. Preserve aspect and motif scale.

### Cylinder

Use arc length `s = R * theta` for the wrap direction. Choose seam, repeat count, and phase explicitly. Keep an integer repeat only when it does not require unacceptable scaling.

### Rounded perimeter

Use accumulated perimeter distance across planes and corner arcs. Carry direction and phase across transitions. Avoid restarting a wood grain or weave independently on every face.

### Freeform patch

Use a low-distortion local parameterization, geodesic/surface projection, or a designed texture skin. Measure metric distortion and protect high-distortion seams/poles. For an important motif, map a known circle/square marker and verify its physical size after export.

Ordinary layer-space infill does not become a surface-conformal pattern on a curved exterior. Use mapped geometry, a separate insert, or a validated non-planar path route.

## 6. Protect interfaces and wall reserve

Define a no-texture margin around:

- mating and sealing surfaces;
- slide/bearing paths;
- threads, snaps, magnets, screws, and inserts;
- electrical connectors and cable interfaces;
- edge comfort and cleaning zones;
- split seams, registration datums, and adhesive lands.

For engraving, calculate remaining wall rather than applying a global depth. A conservative starting reserve from the heightmap workflow is:

```text
max_safe_depth = wall_thickness - max(1.2 mm, 3 * nozzle_mm)
```

Increase reserve for loaded, brittle, impact, wet, or safety-relevant parts. Emboss or thicken the substrate when engraving would violate the reserve.

## 7. Validate geometry and toolpaths separately

### Geometry gate

- expected body count and names;
- watertightness/manifoldness as required;
- no self-intersections, duplicate/internal faces, or disconnected slivers;
- physical dimensions, seam position, and mapping aspect;
- protected-face deviation and wall reserve;
- reference/candidate surface and relief metrics.

### Slicer gate

- import and slice time, warnings, and peak memory where available;
- missing thin lines, gap fill, short segments, seams, and retractions;
- actual top/perimeter/infill paths and line widths;
- material/tool changes and overlap at `CORE/TEXTURE_SKIN` boundaries;
- first-layer adhesion and crossing buildup;
- controller-appropriate segment count and estimated print time.

Neither gate substitutes for a process-matched physical coupon.
