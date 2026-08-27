# Revision 0.2.0 DRAFT manufacturing-mesh review

## Reference

- Source authority: parametric CadQuery B-Rep and STEP
- Geometry revision: `r0.2.0-draft.2`
- DRAFT tessellation: chordal tolerance 0.10 mm, angular tolerance 0.15 rad
- STL set: `output/rev-0.2.0-draft/stl/`
- Geometry report: `output/rev-0.2.0-draft/reports/validation_report.json`
- Protected regions: all fits, holes, seams, drawer travel, floor/bed faces, shelf tops, text/relief, wall-restraint axes and final watermark region

## Measured burden

- Unique printable meshes: 42
- Total unique triangles: 113,692
- Total unique STL size: 5.425 MiB
- Maximum per-part triangles: 10,562
- Maximum per-part STL size: 0.504 MiB
- Assembly preview: 127,462 triangles / 6.078 MiB
- Every printable mesh: watertight, consistently wound, positive volume and within the 256 × 256 × 300 mm build volume
- Assembly-only M3 plate placement correction: all six plates report 0.0 mm boss-contact gap; printable part tessellation is unchanged
- Intentional coupon body counts are explicit: 9 bodies in the clearance coupon, 3 in the M3 seam coupon and 3 in the floor-foot/TPU-lock coupon; every product mesh must remain one body

These ordinary CAD-derived meshes are far below the recorded 1,000,000-triangle and 60 MiB dense-job planning limits. No part shows a triangle or file-size burden that justifies destructive decimation.

## Decision

**Geometry conclusion: lossy simplification is not beneficial for the current ordinary CAD meshes.** Preserve exact STEP/B-Rep authority and direct tessellation. No decimation candidate was generated because it would add interface and bed-plane risk without a material handling benefit.

**Workflow status remains pending**, not release-complete, because:

1. no exact slicer is available for the independent `slicer_resolution_check`;
2. immutable, separately named final `master_mesh` and `manufacturing_mesh` artifacts have not yet been packaged;
3. the later JuSt Innovation watermark must be protected and all affected checks repeated on the final export;
4. optional image relief requires its own adaptive/physical-error review even though the legacy demo was modest.

## Final-export policy candidate

- Keep STEP/B-Rep unchanged.
- Reuse direct STL tessellation at 0.10/0.15 only if the exact slicer shows no lost thin walls, harmful short paths or import burden.
- Do not apply global mesh decimation.
- For a selected image-relief insert, preserve the 16-bit master and assess that local mesh independently.
- After watermark integration, export to separate immutable master/manufacturing paths and rerun topology, bounds, volume, bed contact, protected dimensions, watermark readability and exact slicing.
