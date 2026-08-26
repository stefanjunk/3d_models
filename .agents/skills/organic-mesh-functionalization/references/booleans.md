# Robust Boolean operations

## Preconditions

Before a Boolean, confirm both target and cutter:

- represent closed, consistently oriented solids;
- have positive volume;
- contain no unintended internal shells;
- use the same units and applied transforms;
- overlap by a finite, visible amount;
- avoid coincident/tangent faces and zero-thickness intersections;
- have no features far below solver tolerance.

A Boolean preview is not proof of a valid result.

## Epsilon policy

Use a project-level `boolean_epsilon_mm` tied to model size and process resolution. Typical print-scale work may use a small fraction of a millimeter, but do not hard-code a universal number. Extend through-cutters beyond both target surfaces by several epsilons.

Use epsilon to avoid exact adjacency, not to hide incorrect fit.

## Operation design

- Union overlapping removal cutters first, then subtract once.
- Break unrelated operations into named stages and validate each stage.
- Avoid subtracting hundreds of tiny bodies from the high-resolution source sequentially.
- Place fillets/chamfers in the parametric cutter or insert where possible.
- Keep a non-destructive modifier stack until validation screenshots and dimensions are captured.
- For a door, export body, door, pin, and clearance cutters separately.

## Common failure patterns

### Result disappears or volume becomes negative

Likely causes: inverted normals, open input, scale not applied, nested duplicate shell, or wrong object order.

### Spikes, flakes, or tiny disconnected pieces

Likely causes: near-coplanar faces, sliver intersections, self-intersections, degenerate triangles, or an excessively detailed cutter.

### Hole is not created

Likely causes: cutter does not fully cross the shell, operation not applied, target is only a surface, or solver sees tangent contact.

### Exterior detail changes far from the edit

Likely causes: global remesh, smoothing, voxel resolution too coarse, or unintended modifier ordering.

### Boolean succeeds visually but slicer reports holes

Likely causes: non-manifold intersection loops, internal faces, inconsistent winding, or multiple overlapping shells.

## Fallback ladder

1. Apply transforms and recalculate normals.
2. Remove duplicate/degenerate faces and isolate connected components.
3. Confirm target and cutter are positive-volume watertight solids.
4. Increase real overlap; remove coplanarity.
5. Union cutters before subtraction.
6. Try Blender Exact/Manifold or Manifold3D.
7. Crop and remesh only the ROI with an overlap seam.
8. Use a narrow-band SDF/OpenVDB CSG operation.
9. Redesign the seam or split the object.

## When to stop

Stop direct Boolean attempts when:

- each repair changes protected detail;
- the mesh remains non-manifold after controlled repair;
- solver time or memory grows without a stable result;
- the interface contains features smaller than process resolution;
- the source contains ambiguous overlapping surfaces that cannot be assigned inside/outside;
- validation cannot distinguish intended from unintended removal.

Switch to skin-preserving replacement, SDF, or reference-only reconstruction.
