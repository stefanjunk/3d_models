# AI-assisted parametricization

## Current practical role

AI is most reliable as a source of targets and proposals, not as unverified design intent. Use it to:

- create visual concepts or reference meshes;
- identify semantic landmarks and feature lines;
- propose guide curves and section stations;
- initialize a SubD/FFD cage;
- generate style masters with common topology;
- provide a target for constrained curve/surface fitting.

Do not equate visual similarity with editable, dimensionally stable CAD.

## Reference roles

Declare exactly one role for each external artifact:

- `inspiration` — proportions/style only;
- `fit-target` — geometry is approximated within stated error;
- `deformable-master` — topology and shape are the basis of FFD/morph variants;
- `protected-source` — switch to the organic-mesh preservation workflow.

## Recommended reconstruction pipeline

1. Archive source, license/provenance, unit assumption, and checksum.
2. Normalize orientation and scale from known measurements.
3. Mark semantic landmarks, symmetry, seams, and hard interfaces.
4. Extract or draw a small set of centerlines, silhouettes, rails, and sections.
5. Fit B-splines/NURBS with regularization; do not interpolate every vertex.
6. Optimize control points against target distance plus fairness and hardpoint penalties.
7. Build the envelope and compare signed/unsigned deviations.
8. Add or regenerate exact functional features.
9. Test the exposed parameter range, not only the fitted nominal form.

## Experimental generative CAD

Recent research explores direct generation of NURBS parameters, editable B-Reps, executable CadQuery programs, and history-aware constraints. Treat these systems as experimental unless their outputs are available in the current environment and pass:

- source-code/build execution;
- topology and body-count checks;
- constraint and design-history inspection;
- parameter-edit regression;
- continuity and fairness review;
- manufacturing validation.

A generated STEP file without recoverable intent is a neutral artifact, not proof of a useful parametric model.

## Differentiable fitting

Differentiable NURBS or mesh distance losses can optimize control points and weights against a target. A useful objective combines:

- point-to-surface or silhouette error;
- curvature/fairness regularization;
- hardpoint and symmetry constraints;
- wall and self-intersection penalties;
- parameter-range robustness.

Report both target-fit error and deviation introduced by final print tessellation.

## Supplied operational helpers

- `extract_mesh_sections.py` uses an optional Trimesh backend to cut an immutable reference mesh at declared planes and exports the longest closed loop at each station. Review internal shells and semantic correspondence; longest-loop selection is only a heuristic.
- `fit_bspline.py` fits an actual SciPy parametric B-spline and records degree, knots, coefficients, residual error, and sampled fairness metrics.
- `compare_hardpoints.py` compares named points, axes, and planes before and after reconstruction/deformation.

These helpers create reproducible evidence but do not infer anatomy, vehicle packaging, or design intent automatically.
