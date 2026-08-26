---
name: design-freeform-surface
description: Design or refine a smooth parametric aesthetic envelope while preserving exact hardpoints and FDM printability. Use for freeform surfacing, curve fairness, lofts, SubD, NURBS, editable shells, or aesthetic product-envelope work.
---

# Design Freeform Surface

Load `parametric-freeform-surfacing`. Also load `functional-3d-design` when mechanical interfaces, material, or slicer decisions are involved. Also load `organic-mesh-functionalization` when an existing dense AI-generated or scanned mesh must be preserved.

Apply the user's request as follows:

1. Create or update `surfacing-spec.yaml`.
2. Select the simplest valid curve or surface representation.
3. Generate editable source and deterministic exports.
4. Run the required fairness, hardpoint, topology, tessellation, and printability checks.

Report validation evidence and unresolved uncertainty.
