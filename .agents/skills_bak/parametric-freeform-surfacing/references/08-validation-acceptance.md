# Validation and acceptance

## Validation ladder

1. Specification/schema and parameter bounds.
2. Deterministic source execution.
3. Curve fairness and section correspondence.
4. Surface continuity/highlight review.
5. Hardpoint and protected-region comparison.
6. Topology, body count, normals, volume, and self-intersection screening.
7. Wall and feature measurements.
8. Tessellation deviation and silhouette review.
9. Slicer paths, layers, seams, supports, and bed fit.
10. Parameter-grid regression.
11. Representative print coupon and full physical acceptance test.

## Curve report

Record per dominant guide curve:

- point/control count;
- length;
- RMS and maximum discrete curvature;
- total curvature variation;
- curvature-extrema count;
- endpoint position/tangent constraints;
- before/after fairing displacement.

Thresholds depend on product scale. Use reports primarily to detect regressions and unexplained spikes.

## Section/loft report

Record:

- station order and coordinates;
- point count after resampling;
- original orientation and chosen seam shift;
- adjacent-section correspondence error;
- minimum local section area and width;
- self-intersection or inversion flags;
- cap strategy.

## Hardpoint report

Hardpoints can be points, axes, planes, faces, or protected volumes. Measure the right quantity:

- point displacement;
- axis angular and positional drift;
- plane offset and angle;
- face deviation/flatness;
- clearance or wall change around protected volumes.

After FFD, morph, SubD evaluation, smoothing, or SDF operations, regenerate late exact features and rerun the report.

## Mesh report

For a solid target, require:

- each undirected edge used exactly twice;
- non-degenerate triangles;
- expected connected components;
- consistent normal orientation;
- positive non-trivial signed volume;
- bounds inside the declared build envelope;
- no unexpected internal shells.

A watertight mesh can still have self-intersections or wrong geometry. Use a stronger backend such as Trimesh/Manifold, Blender, or a CAD kernel when consequences warrant it.

## Parameter sweep

Test nominal, every parameter bound, and selected combinations. At minimum detect:

- negative dimensions;
- section collapse or reversal;
- wall loss;
- hardpoint drift;
- self-intersection;
- abrupt curvature changes;
- body-count/topology changes;
- print-bed overflow.

## Acceptance evidence

Package machine-readable reports with visual evidence. Mark checks as:

- `PASS` — executed and within threshold;
- `FAIL` — executed and outside threshold;
- `NOT_RUN` — backend or input unavailable;
- `REVIEW_REQUIRED` — numerical check is insufficient, such as visual highlight quality or physical fit.
