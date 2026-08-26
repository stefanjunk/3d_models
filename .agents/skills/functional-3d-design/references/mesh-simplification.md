# Manufacturing mesh simplification gate

## Contents

- [Purpose and timing](#purpose-and-timing)
- [What to simplify](#what-to-simplify)
- [Mandatory decision flow](#mandatory-decision-flow)
- [Physical tolerance selection](#physical-tolerance-selection)
- [Protected regions](#protected-regions)
- [Tool routes](#tool-routes)
- [Acceptance metrics](#acceptance-metrics)
- [Watermark and final export](#watermark-and-final-export)
- [Common failures](#common-failures)

## Purpose and timing

Check every manufacturing model for unnecessary mesh complexity after the production geometry and initial slicer baseline are stable, but before final release. The check is mandatory; applying simplification is conditional.

Record one outcome per manufacturing part:

- `applied` — a measured candidate passed every geometry/function/slicer constraint and provides a meaningful benefit;
- `not-beneficial` — candidates were measured but savings were insignificant or risks exceeded benefit;
- `not-applicable` — there is no triangle-mesh deliverable or the downstream manufacturing route consumes exact/native geometry without tessellation;
- `pending` — release-blocking until resolved.

Do not confuse:

- **design simplification** — remove redundant tiny fillets, unseen texture, excessive pattern cells, duplicate bodies, or needless CSG while preserving intent;
- **CAD tessellation** — convert analytic faces to a triangle mesh using chordal/angular tolerances;
- **mesh simplification/decimation** — reduce an existing mesh while bounding surface change;
- **slicer path simplification** — toolpath/controller behavior after slicing.

Each can reduce computation, but only exact slicing reveals manufacturing-path effects. Triangle reduction does not inherently reduce deposited material or print time.

## What to simplify

Prefer the earliest representation that can safely remove redundancy:

1. simplify repeated/unseen design features parametrically;
2. keep native CAD/STEP exact and choose sane export tessellation;
3. reduce dense relief/organic/cosmetic surface families separately from exact interfaces;
4. remove redundant coplanar subdivisions after robust Booleans only when needed;
5. use slicer simplification only as a comparison or last-resort downstream operation.

Preserve the editable native or high-fidelity `master_mesh`. Write the selected candidate to a separate `manufacturing_mesh` path. Never overwrite the only unsimplified source/export or alias both artifacts to one mutable filename.

Do not simplify a face-per-triangle B-Rep after converting a dense scan/relief to CAD; keep the functional interfaces exact and the dense surface as a mesh or hybrid representation.

## Mandatory decision flow

### 1. Measure the reference

Record per part:

- vertices, triangles, components/bodies, file bytes, bounds, volume, surface area, and topology;
- import, display, export, and exact-slicer computation time;
- planned and measured peak working memory;
- slicer warnings and short-segment/toolpath burden when available;
- process-sensitive detail: smallest radius/text/relief, layer height, line width, and dimensional tolerances.

If the mesh is modest, loads/slices promptly, and contains no redundant tessellation, record `not-beneficial` without destructive processing. The check remains complete.

For dense/relief work, define four independent budgets before expensive generation: triangle target/stop, peak-memory GiB, maximum mesh MiB, and maximum exact-slicer import/slice seconds. A pass on one does not waive the others.

### 2. Mark protected regions

Exclude exact interfaces, bed planes, seals, fits, relief boundaries, sharp features, and other regions listed below. If the simplifier cannot constrain them, split the exact and reducible sets or simplify before their Boolean union/difference.

### 3. Generate a small physical-tolerance sweep

Use at least a conservative and nominal candidate; add an aggressive candidate when useful. Control the maximum physical surface deviation in millimetres—not only a triangle-removal percentage.

### 4. Compare independently

Measure bidirectional surface distance, topology, bounds, volume, body count, protected dimensions, bed contact, minimum wall, relief/cosmetic detail, and assembly collisions. A simplifier's own success return is not acceptance evidence.

### 5. Slice exact candidates

Compare import/slice time, toolpaths, layer count, estimated time/material/support, missing walls, seams, and very short segments with the identical profile.

Record this as a separate `slicer_resolution_check`. Do not merge it into the geometric report: a slicer can accept a geometrically damaged mesh, and a geometrically accurate mesh can still produce missing walls or excessive short toolpaths.

### 6. Apply only with benefit

Normally require either:

- at least 25% fewer triangles/file-size burden with all checks passing; or
- a measured improvement in import/slice/controller handling that justifies a smaller reduction.

When no meaningful benefit exists, retain the reference and record `not-beneficial`. Do not add a lossy pipeline step to improve a report metric.

## Physical tolerance selection

For ordinary non-relief meshes, derive a candidate tolerance from the allowed deviation of the reducible surface, not from overall part size:

```text
t0 = min(
  0.25 * allowed_surface_deviation,
  0.10 * nominal_line_width,
  0.25 * layer_height,
  0.05 mm
)
```

Evaluate approximately `0.5*t0`, `t0`, and, when justified, `1.5*t0`. This formula creates candidates; it does not approve them.

If no allowed surface deviation exists, define it from the design acceptance criteria before production simplification. Values such as 0.01/0.025/0.04 mm may be used only as an explicitly exploratory sweep for an ordinary desktop-FDM cosmetic surface, never as universal tolerances.

Use a smaller tolerance for shallow relief, text, small holes/radii, seals, mating geometry, thin walls, and high-curvature silhouettes. Prefer zero movement by excluding critical interfaces entirely.

For FDM image relief, use the specialist starting candidate instead:

```text
t0 = min(
  0.10 * nozzle_diameter,
  0.20 * layer_height,
  0.125 * relief_depth,
  0.05 mm
)
```

This is a candidate, not automatic acceptance. For a 0.6 mm nozzle, 0.30 mm layer, and 0.32 mm relief, it gives `0.040 mm`. Evaluate a small sweep and protect seams, text, borders, and functional faces.

## Protected regions

Lock, exclude, or independently constrain:

- mating, sliding, alignment, bearing, sealing, and gasket faces;
- calibrated holes, pins, rails, stops, threads, gear teeth, flexures, and snap roots;
- bed-contact planes, datum surfaces, support interfaces, and assembly cut planes;
- minimum-wall/minimum-clearance zones and fluid barriers;
- relief/texture borders, tile and cross-face seams, text, logos, and approved sharp creases;
- visible silhouettes and locally critical curvature;
- generated `metriMade.com` watermark outlines, traceability text, gaps, recess floor/depth, host-wall reserve, and surrounding bed datum.

For a functional CAD part, the safest route is usually to simplify only the relief/organic cutter or export tessellation while keeping named CAD faces exact.

## Tool routes

### Native CAD

Keep STEP/B-Rep as the design master. Adjust chordal and angular export tolerances so analytic planes/cylinders are not over-tessellated. Preserve exact interface faces. Reimport the exported mesh and validate it.

### Manifold

Use `simplify(tolerance)` on a valid manifold mesh when available. Manifold documents that surfaces move by less than the supplied tolerance. Still measure protected features, bed contact, wall reserve, and slicer behavior independently.

### CGAL

Use constrained-edge surface simplification or a polyhedral-envelope filter when boundaries or a global error envelope must be preserved. Record cost/placement/stop policies.

### Blender

Use Decimate Collapse for general reduction and Planar for coplanar facets. Protect vertex groups/boundaries where possible. A ratio is suitable for exploration, but production acceptance requires a millimetre error bound and independent comparison.

### Relief and organic meshes

Use the respective specialist skill. Prefer adaptive generation, local surface sets, or a protected physical tolerance over global decimation. Preserve the 16-bit relief master or untouched organic source mesh.

### Slicer UI

PrusaSlicer/OrcaSlicer simplification is useful for visual and slice-time A/B tests. Do not make it the only reproducible production step: a global operation may alter bed contact, functional fits, or fine detail, and percentage-based controls do not state a physical error.

## Acceptance metrics

Require, as applicable:

1. expected body/component count, watertight/manifold topology, consistent orientation, nondegenerate faces, and positive volume;
2. unchanged protected faces/dimensions or error within their explicit tolerances;
3. bidirectional maximum and RMS surface error within the declared limit;
4. bounds, volume, center of mass, and assembly collisions within project limits;
5. retained bed-contact geometry and no first-layer overhang introduced;
6. retained minimum wall/clearance and no disconnected slivers;
7. retained relief amplitude, text gaps, curvature, silhouettes, and seams;
8. meaningful triangle/file/slicer/controller benefit;
9. exact-slicer layer inspection with no lost walls, new gaps, support changes, or harmful short paths;
10. physical coupon when the difference is close to process resolution or affects appearance/function.

When `relief_validation=true`, use these starting limits in `scripts/mesh_simplification_gate.py`:

- absolute volume change `< 0.1%`;
- registered relief-height correlation `>= 0.98`;
- robust relief-contrast loss `< 5%`;
- RMS surface error `<= 0.05 * nozzle_diameter`.

Measure correlation from paired heights in the same physical surface coordinates after mean removal. Mask to the actual relief and exclude unrelated flat background. Measure contrast with the same robust percentile span in both meshes, preferably `P95-P5`. Tighten limits when the project requires more.

Use `scripts/mesh_simplification_gate.py` to apply an auditable pass/fail gate to externally measured metrics. The script does not calculate surface distance; use the selected geometry tool to produce those measurements.

## Watermark and final export

Select and validate the simplification/tessellation policy on the stable unmarked production candidate before watermark integration. The watermark remains the last planned design-feature/solid-geometry change.

After watermark integration, create the final derived manufacturing export with the prevalidated policy. Protect the complete watermark and its bed datum, then rerun topology, surface-error, wall, bed-contact, mark readability, and exact-slicer checks. Any post-mark export that changes the watermark outside acceptance invalidates the watermark gate.

## Common failures

- Simplifying solely because a slicer warns about triangles, without measuring whether the candidate helps.
- Using one global ratio on relief, rails, bed plane, and holes together.
- Checking only rendered shading; smooth normals hide geometric damage.
- Sampling only candidate-to-reference distance and missing reference features erased by the candidate; measure bidirectionally.
- Ignoring bed-contact loss because the bottom still looks visually flat.
- Measuring triangle reduction but not slice/toolpath time.
- Keeping dense source, cutter, Boolean intermediate, and final mesh simultaneously until memory fails; process and serialize parts sequentially.
- Running automatic repair after simplification without comparing the repaired mesh to the reference.
