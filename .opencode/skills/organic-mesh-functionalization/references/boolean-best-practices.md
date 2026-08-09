# Boolean best practices and failure analysis

## Valid operands

For solid difference/union/intersection, target and tool should be:

- closed/watertight;
- consistently wound;
- non-self-intersecting to the practical tolerance of the engine;
- positive-volume;
- free of duplicate internal shells;
- expressed at sensible scale and units.

Manifold-style Boolean engines are strongest when inputs already satisfy oriented 2-manifold requirements. Blender Exact is more tolerant of difficult intersections but is not a substitute for inspecting invalid operands.

## Intersection quality

- Cutter must pass through the target; it should not terminate exactly on the target surface.
- Extend cutters beyond roofs, floors, and walls by a documented overshoot.
- Avoid tangent contact and zero-thickness remnants.
- Avoid coincident coplanar faces. Offset or extend one operand.
- Prefer rounded/chamfered transition geometry over knife-edge residual walls.
- Split complex work into semantic stages: core cavity, entry, exit, seat, insert.

## Operation ordering

Recommended:

```text
clean/validate source
-> union related cutters
-> subtract cavity/openings
-> validate intermediate
-> add/union insert only if integrated
-> validate final
```

For a removable component, do not union it. Export assembly parts separately.

## Diagnosing a failure

1. Check source and cutter independently.
2. Confirm bounding boxes overlap by a real volume.
3. Slice through the intended intersection.
4. Check component count and hidden duplicate shells.
5. inspect local triangle aspect ratios and nearly coincident surfaces.
6. simplify the cutter, not the preserved source.
7. retry with one cutter at a time.
8. compare engines on copies.
9. use local remesh/SDF fallback if exact intersections remain unstable.

Do not use arbitrary millimetre-scale tolerance inflation to make an operation pass; that may move the protected exterior.

## Detecting false success

A Boolean may return a valid mesh while:

- the cutter missed the source;
- an internal membrane remains;
- the wrong connected component was modified;
- the insert is trapped but not joined;
- the wall is perforated outside the intended opening;
- the result contains a tiny disconnected fragment;
- normals and volume are valid but topology no longer matches intent.

Therefore compare sections, volumes, bodies, protected-surface deviation, and intended pathway/clearances.
