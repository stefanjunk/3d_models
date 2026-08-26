# Changelog

## 2.4.0

- Added explicit triangle, peak-memory, file-size, and exact-slicer budgets to persistent relief jobs.
- Separated the unsimplified reference/master mesh from the optimized manufacturing mesh and their reports.
- Split geometric simplification acceptance from slicer/toolpath acceptance.
- Adopted the FDM automatic starting tolerance `min(0.10*nozzle, 0.20*layer, 0.125*depth, 0.05 mm)`.
- Added auditable starting gates for volume, relief correlation, robust contrast loss, and nozzle-relative RMS error.

## 2.3.0

- Added a mandatory pre-geometry relief triangle and file-size budget.
- Clarified that print pitch is a detail bound, not a uniform-triangulation mandate.
- Added adaptive generation, sequential memory processing, protected-region simplification, and exact-slicer gates.
- Added a process-aware physical tolerance sweep and measurable acceptance criteria.
- Added `relief_mesh_budget.py` plus regression coverage.

## 2.2.0

- Added physical-aspect invariant throughout generation, registration, preprocessing, and rebuild.
- `contain`, `cover`, and crop now fit in millimetres before rasterization.
- `stretch` is rejected by default under `aspect_policy=preserve`.
- Added explicit source/target/raster/physical-pixel aspect metadata and error tolerance.
- Added square-pixel human preview for anisotropic geometry rasters.
- Added metric mapping guidance for cylinders, rounded boxes, spheres, ellipsoids, and arbitrary UV meshes.
- Added no-accumulated-resizing rule.
- Added `validate_aspect_ratio.py` and `make_aspect_test_image.py`.
- Added regression tests proving a circle remains physically circular with 0.20×0.10 mm target sampling.

## 2.1.0

- Added generation-time source PPI, source registration, persistent rebuild job, and easy source replacement.

## 2.0.0

- Added 16-bit default and no-posterization guidance.
