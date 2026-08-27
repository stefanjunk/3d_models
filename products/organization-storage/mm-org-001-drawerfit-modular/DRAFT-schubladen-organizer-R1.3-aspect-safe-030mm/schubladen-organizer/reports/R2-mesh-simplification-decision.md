# R2 manufacturing mesh decision — DRAFT

Status: `not-beneficial` for additional lossy mesh simplification.

The selected R2 candidate removes the R1.3 image-heightfield at the parametric representation level and replaces it with sparse deterministic groove curves. The editable JavaScript/Manifold3D source and JSON parameters remain the master geometry.

Measured four-module manufacturing set:

| Metric | R1.3 baseline | R2 current | Change |
|---|---:|---:|---:|
| Triangles | 6,029,222 | 426,832 | −92.9206% |
| Binary-STL bytes | 301,461,436 | 21,341,936 | −92.9205% |
| Largest R2 module | — | 133,128 triangles / 6,656,484 bytes | below 750,000-triangle limit |
| Peak RSS budget | 2,083.953 MiB baseline worst case | every R2 module below 1,228.8 MiB | PASS |

All nine R2 STLs pass independent watertight/manifold/orientation/body/volume/degeneracy/duplicate-face checks. The exact assembly envelope remains 227 × 357 × 64 mm; minimum floor reserve is 2.40 mm and minimum double-grooved wall reserve is 2.88 mm.

Protected regions include the assembly envelope, split and connector faces, 0.30-mm connector fit, bed-contact undersides, future watermark regions, access-groove radii, wall-root and junction blends, grain/knot boundaries, top edges, visible silhouettes, and minimum wall/floor reserves.

An additional decimation stage is not justified: current meshes are modest and already far below the declared triangle/file/memory budgets, while any lossy global operation could damage protected interfaces or the shallow 0.16/0.20-mm grooves. The configured 0.0001-mm Manifold cleanup and deterministic cancellation of exact opposite internal Float32 face pairs are export hygiene, not a cosmetic decimation candidate; ambiguous duplicates fail the build.

Independent `slicer_resolution_check` remains `pending` because no exact slicer executable/profile was available. Final release still requires same-profile R1.3/R2 import-and-slice comparison, layer inspection, and physical coupons.

Evidence: `reports/R2-procedural-wood-digital-validation.json`, `reports/R2-procedural-wood-unmarked-mesh-validation.json`, and `reports/build-pipeline-R2-procedural-wood-unmarked.json`.
