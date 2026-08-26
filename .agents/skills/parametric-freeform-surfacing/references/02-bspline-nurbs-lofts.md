# B-splines, NURBS, lofts, and surface networks

## B-spline/NURBS model

A rational B-spline curve is

\[
C(u)=\frac{\sum_i N_{i,p}(u) w_i P_i}{\sum_i N_{i,p}(u) w_i}.
\]

Its practical controls are:

- degree \(p\);
- control points \(P_i\);
- knot vector and multiplicities;
- optional rational weights \(w_i\);
- periodic/closed state;
- parameterization and end conditions.

Cubic curves are the default for broad product form. Higher degree can reduce patch count but may create global coupling and numerical fragility. Use weights deliberately for conics or controlled attraction, not as arbitrary shape knobs.

## Interpolation versus approximation

- **Interpolation** is appropriate for true hard landmarks and measured interfaces.
- **Approximation** is preferable for scans, AI meshes, sketches, and dense samples.
- Use a fit tolerance tied to physical scale and FDM visibility, not to source vertex spacing.
- Keep fitting error and fairness error as separate reported quantities.

## Section architecture

Choose stations with semantic meaning. Examples:

- shoe: heel end, heel seat, arch, midfoot, ball, toe box, toe tip;
- car: nose, front axle, hood, windshield, roof apex, rear axle, tail;
- vessel: foot, belly, shoulder, neck/rim.

Every closed section must share:

- orientation;
- a consistent seam landmark;
- corresponding feature indices or a common parameterization;
- comparable point density after resampling.

The supplied loft helper tests cyclic shifts and reversed orientation to minimize section-to-section mismatch. For production CAD, store semantic landmarks as well; a numerical minimum can select the wrong correspondence on symmetric shapes.

## Loft failure modes

- excessive section count transfers noise into the surface;
- inconsistent seams create a helical twist;
- sections with unrelated parameterization create diagonal ripples;
- abrupt section spacing causes local acceleration in shape change;
- a loft through near-degenerate end sections can pinch;
- ordinary end caps may create flat spots or curvature discontinuities;
- cross-sections alone may not control the side silhouette.

Use rails or a curve network when longitudinal shape is important. A Gordon/network surface combines section and rail families, but both families must be mutually compatible and fair.

## Patch strategy

Prefer a small number of meaningful patches. Patch boundaries should lie at:

- intentional creases;
- symmetry planes;
- natural feature lines;
- manufacturing splits;
- regions where continuity can be measured and controlled.

Avoid a patch boundary through the middle of a broad reflected highlight unless the backend can match it at the required continuity.

## B-Rep handoff

Use CadQuery, build123d, OpenCascade, Rhino, Alias, or another NURBS/B-Rep system when exact STEP exchange and later solid features matter. Use mesh/SubD when visual iteration or reference fitting dominates, then define a deliberate handoff.

Never convert a dense triangle mesh directly into a B-Rep with one face per triangle. Reconstruct a sparse surface model or keep the mesh representation.
