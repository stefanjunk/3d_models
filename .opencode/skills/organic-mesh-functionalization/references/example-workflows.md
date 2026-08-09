# Example workflows

## Dice tower

### Inputs

- decorative tower shell with courtyard;
- maximum die size and required clearance;
- required minimum wall;
- entry and exit locations;
- print orientation and support constraints.

### Process

1. Fit tower axis from selected cylindrical body, excluding courtyard/decorations.
2. Generate radial clearance report at multiple z sections.
3. Choose inner cylinder/tapered loft radius below the minimum permitted radius.
4. Subtract core with roof/floor overshoot.
5. Cut top entry and courtyard exit independently.
6. Generate stair/baffle insert parametrically; prototype as separate captured insert.
7. Verify each die has a continuous path with clearance at rotations/corners.
8. Inspect sections for membranes and run repeated drop tests.

## Modern barefoot shoe

### Inputs

- external AI mesh;
- foot dimensions/scan or intended internal last;
- retained outsole/rand decision;
- zero-drop, sole thickness, flex, and upper attachment requirements.

### Process

1. Establish heel-to-toe axis, ground plane, left/right.
2. Segment decorative/textile upper with a reviewed interface boundary.
3. Keep source outsole skin/rand only if thickness and geometry are usable.
4. Remove the old interior/upper using split surface and ROI.
5. Generate parametric sole from foot/last data, not merely the external shell.
6. Add conformal bonding flange, stitch holes, capture lip, or separate outsole interface.
7. Validate internal volume, sole thickness, zero drop, flex, and protected outsole texture.
8. Print interface and flex coupons before a complete shoe.

## Unicorn belly compartment

### Inputs

- desired compartment volume;
- door size and opening direction;
- hinge/latch method;
- child-use/safety requirements;
- wall and decoration keep-outs.

### Process

1. Select low-curvature belly patch away from legs and thin decoration.
2. Fit a rounded box/capsule cavity and verify conservative wall clearance.
3. Cut door opening while retaining a seating rim.
4. Generate door, hinge, latch, stops, and clearance parametrically.
5. Prefer separate metal pin or robust printed hinge according to cycle target.
6. Validate sweep/collisions, small loose parts, edges, and retention physically.

For cylindrical shells, `radial_clearance.py` samples actual mesh cross-sections and reports a conservative permitted inner radius after wall and uncertainty allowances. Segment the intended tower body first so the courtyard and ornaments do not become false limits.
