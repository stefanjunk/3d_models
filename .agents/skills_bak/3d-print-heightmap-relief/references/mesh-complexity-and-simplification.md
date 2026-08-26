# Relief mesh complexity and simplification

## Contents

- [What the pitch means](#what-the-pitch-means)
- [Budget before geometry](#budget-before-geometry)
- [Reduce complexity in the right order](#reduce-complexity-in-the-right-order)
- [Choose a physical tolerance](#choose-a-physical-tolerance)
- [Protect geometry](#protect-geometry)
- [Tool routes](#tool-routes)
- [Acceptance gate](#acceptance-gate)
- [Failure modes](#failure-modes)

## What the pitch means

The X/Y print pitch is the smallest surface-sampling interval worth considering for the chosen nozzle, line width, layer height, orientation, and mapping. It does not require a regular two-triangle cell over the entire relief patch.

Keep three resolutions separate:

1. the immutable 16-bit source master;
2. the printer-specific build raster in physical coordinates;
3. the adaptive manufacturing mesh.

Also keep two mesh artifacts separate: the unsimplified `reference/master mesh` used for comparison and the selected optimized `manufacturing mesh`. They are not two names for one file. A candidate must never replace the only reference artifact.

A high-resolution image master prevents tonal loss during processing. It does not justify one mesh vertex per source pixel. Likewise, a 0.30 mm target pitch means that high-gradient printable regions may need samples at roughly that spacing; locally planar or slowly varying regions may use much larger triangles when a physical error bound is maintained.

## Budget before geometry

For a rectangular regular height field, use this conservative estimate:

```text
cells ~= displaced_surface_area_mm2 / (pitch_x_mm * pitch_y_mm)
relief_triangles ~= 2 * cells
binary_STL_bytes ~= 84 + 50 * total_triangles
```

The estimate omits boundaries, base/cutter closure, Boolean splits, and duplicate facets. It is a planning lower bound for a uniform mesh, not a final prediction.

Run:

```bash
python scripts/relief_mesh_budget.py \
  --area-mm2 72000 \
  --pitch-mm 0.30x0.30 \
  --process fdm \
  --nozzle-mm 0.60 \
  --depth-mm 0.32 \
  --layer-height-mm 0.30 \
  --memory-budget-gib 8 \
  --max-mesh-mib 100 \
  --max-slicer-seconds 120
```

Default portable policy per manufacturing part:

| Relief triangles | Gate | Required action |
|---:|---|---|
| at or below 1,000,000 | `PASS` | Continue, then measure the actual export and slicer. |
| above 1,000,000 through 5,000,000 | `REVIEW` | Generate adaptive/simplified variants and benchmark the exact slicer. |
| above 5,000,000 | `STOP` | Redesign the sampling/patch or document a measured override before the expensive Boolean/export. |

Treat these as conservative workflow and interchange defaults. Override them only with the actual workstation memory, geometry kernel, slicer/version, printer controller, and acceptance criteria recorded. A simple part may need far fewer triangles; a justified art master may need more.

Also budget the whole job. Record a peak-memory limit in GiB, a calibratable working-bytes-per-triangle coefficient for the selected kernel, a mesh-file limit, and a total exact-slicer import/slice-time limit. These are independent limits. Multiple individually acceptable parts can still exhaust memory when cutters and final meshes remain resident simultaneously. Build and serialize one part at a time; release intermediate arrays and meshes before starting the next part. Replace the planning memory coefficient with measured peak memory from representative jobs when available.

## Reduce complexity in the right order

Apply the earliest valid reduction:

1. Map only the visible/approved patch. Do not displace hidden backs, mating faces, internal walls, or areas behind another part.
2. Crop or mask flat background when it carries no intended surface information.
3. Preserve the build raster but generate geometry adaptively from local height error/curvature.
4. Split large independent surface families into sequential jobs while maintaining one shared physical coordinate system and seam values.
5. Simplify the closed relief cutter with a physical deviation tolerance and locked boundaries.
6. Boolean the simplified, validated cutter into the exact parametric base.
7. Apply a final manufacturing-mesh simplification only if the Boolean introduced redundant coplanar subdivisions.
8. Prefer indexed/compressed 3MF for delivery when the target toolchain supports it; retain a validated manufacturing STL when required.

Do not downsample the 16-bit master merely to make mesh generation fit memory. Change the build raster or mesh representation from the master and record the new pitch.

## Choose a physical tolerance

Do not select simplification only by a target percentage. A fixed percentage has no physical meaning across differently sized models or relief depths.

For FDM use this automatic starting candidate:

```text
t0 = min(
  0.10 * nozzle_diameter,
  0.20 * layer_height,
  0.125 * relief_depth,
  0.05 mm
)
```

Then evaluate approximately `0.5*t0`, `t0`, and `1.5*t0`. This is a candidate sweep, not automatic acceptance. For a 0.6 mm nozzle, 0.30 mm layer, and 0.32 mm relief, `t0=0.040 mm`. A shallower or appearance-critical relief may need a stricter candidate even when this formula permits more.

Use a stricter tolerance when:

- the image contains small text, eyes, sharp weave crossings, or a shallow low-contrast relief;
- the relief meets an exact border, tile seam, or masked transition;
- a functional fit, seal, rail, datum, or bed plane is nearby;
- the target process has substantially finer verified resolution.

Use a looser candidate only when the measured output still satisfies every acceptance criterion.

## Protect geometry

Exclude or lock these regions during simplification whenever the tool permits:

- mating, sliding, bearing, sealing, fastening, and alignment faces;
- calibrated holes, slots, pins, rails, and stops;
- print-bed contact planes and intentional support interfaces;
- relief patch boundaries, periodic tile seams, and cross-face mapping seams;
- intentional sharp creases and silhouette edges;
- minimum-wall and minimum-clearance regions;
- legible marks and other release-critical details.

When a simplifier cannot preserve named regions, simplify the relief cutter before the Boolean or split exact and reducible surface sets. Do not rely on a visual viewport to prove an interface stayed flat.

## Tool routes

### Generation first

Prefer adaptive height-field triangulation, quadtree subdivision, or curvature/error-based remeshing over generating a huge uniform grid and repairing it later. Preserve metric X/Y coordinates and periodic seam samples.

### Manifold

Use `simplify(tolerance)` when the mesh is already a valid manifold and the binding exposes it. Manifold documents the tolerance as a maximum movement of surfaces. Still compare the result independently, because preserved topology alone does not prove relief contrast, wall reserve, or interface quality.

### CGAL

Use surface-mesh simplification with constrained edges or a polyhedral-envelope filter when a guaranteed geometric envelope and boundary preservation are required. Record the policy and stop predicate; a target edge count alone is insufficient.

### Blender

Use Decimate Collapse for general reduction and Planar for redundant coplanar facets. Protect vertex groups/boundaries where possible. Blender's ratio is useful for exploration, but validate physical deviation independently before production.

### CAD tessellation

For analytic base bodies, adjust chordal and angular tessellation tolerances at export instead of decimating exact faces. Keep the native/STEP master. Apply dense sampling only to the relief surface family.

### Slicer simplification

Use PrusaSlicer/OrcaSlicer simplification as a visual and timing comparison, not the sole reproducible release pipeline. A slicer-level reduction can alter the bed plane or functional faces, and a percentage slider does not encode a millimetre error bound.

## Acceptance gate

Compare the unsimplified reference, every candidate, and the chosen final mesh. Require:

1. expected component/body count, watertightness, manifold edges, consistent orientation, and positive volume;
2. unchanged protected faces or deviations within their explicit dimensional tolerances;
3. bidirectional maximum surface distance within the selected physical tolerance and RMS distance no greater than 5% of nozzle diameter as an FDM starting limit;
4. absolute volume change below 0.1%; relief-height Pearson correlation at least 0.98; and robust contrast loss below 5% as starting limits;
5. preserved tile/cross-face seams, silhouettes, small text, and intentional sharp features;
6. safe remaining wall thickness and no new disconnected slivers;
7. unchanged or explicitly revalidated bed-contact area;
8. a meaningful improvement—normally at least 25% fewer triangles or a measured slicer/load/export benefit;
9. exact-slicer layer inspection and a process-matched relief coupon for borderline detail.

Compute correlation from aligned paired reference/candidate heights in the same physical surface coordinates after removing their means. Use the actual relief mask and exclude unrelated flat background, which could otherwise inflate correlation. Compute contrast from the same robust span in both meshes—prefer `P95-P5` unless the job records another percentile pair. Use `scripts/relief_mesh_acceptance.py` to gate these externally measured values. These numbers are starting points, not permission to relax a stricter project requirement.

The geometry gate and slicer gate are separate records. Geometry acceptance does not prove that the slicer retains walls or avoids harmful short segments; slicer acceptance does not prove that decimation preserved the continuous surface.

If a candidate passes geometry checks but produces nearly identical slice time and toolpaths, prefer the simpler pipeline and do not add a destructive production step merely to reduce a number in a report.

## Failure modes

- **Uniformly sampling a huge flat area:** millions of coplanar triangles with no printable benefit. Use adaptive geometry or a separate analytic cap.
- **Decimating after all Booleans without masks:** rounded holes, moving rails, damaged bed planes, and leaking seams. Simplify the cutter or reducible face set earlier.
- **Triangle-percentage optimization:** shallow relief and deep relief receive the same percentage despite different physical error budgets.
- **Simplifying only once:** no evidence that the selected point is on a useful fidelity/complexity trade-off curve. Run a small tolerance sweep.
- **Keeping all dense bodies in memory:** stable individual operations fail late during extraction/export. Process one part and one artifact at a time.
- **Checking only rendered shading:** smooth normals can hide geometric flattening, holes, or faceting. Measure the mesh and inspect sliced paths.
- **Using mesh count as print-time proxy:** dense facets can slow slicing and create short segments, but final print time depends on the generated toolpaths, acceleration, flow, and profile. Benchmark the slicer.
