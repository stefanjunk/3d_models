# Alignment and fitting

## Coordinate contract

Define in millimetres:

- origin;
- up axis;
- forward axis;
- left/right handedness;
- functional centerline or rotation axis;
- datum plane for assembly or printing;
- at least three non-collinear landmarks when a measured transform is required.

Apply object transforms in Blender before using dimensions. Record every transform as a homogeneous 4×4 matrix.

## Methods and when to use them

### Explicit datum alignment

Best method. Align to known planes, axes, holes, or measured dimensions. Use for a dice-tower centerline, shoe heel-to-toe axis, or compartment door plane.

### Primitive fitting

Fit a cylinder, plane, sphere, capsule, or box to a selected ROI. Use robust statistics and exclude decorative protrusions. Validate the fit on multiple cross-sections.

For a tower interior, estimate a conservative permitted radius:

```text
r_permitted(z) = minimum radial distance to protected exterior at z
                 - required wall
                 - mesh/fit uncertainty
```

Use the minimum over the functional height, not the average.

### Landmark/Kabsch transform

Use corresponding source and target points to solve rigid rotation and translation. Uniform scale may be solved only when units or generation scale are uncertain and independent dimensional evidence permits it.

### PCA

Useful for a coarse guess on elongated, roughly symmetric objects. PCA axes can flip, swap on near-symmetry, and be dominated by a protruding courtyard or tail. Never treat PCA as a final datum without review.

### ICP

Use only after coarse alignment and only where source and target surfaces correspond. ICP can converge to the wrong symmetric location or deform the design intent if used as a substitute for landmarks.

### Shrinkwrap/conformal fitting

Use to conform a flange, patch, or bonding surface to an organic shell. Limit it with vertex groups and offsets. Check self-intersections and local thickness after application.

## Fitting a functional part into an organic envelope

1. Define the available-volume envelope and keep-outs.
2. Select the simplest primitive family that satisfies function.
3. Fit dimensions conservatively.
4. Add assembly clearance and Boolean overlap separately.
5. Generate the parametric part in its own local coordinate system.
6. apply the recorded transform at handoff.
7. inspect cross-sections at extrema and transition boundaries.

Do not conflate these values:

- functional clearance;
- print fit compensation;
- Boolean overlap epsilon;
- decorative preservation margin;
- minimum structural wall.
