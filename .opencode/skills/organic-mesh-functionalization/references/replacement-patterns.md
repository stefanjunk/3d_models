# Replacement and integration patterns

## 1. Negative-volume cavity

Subtract a simple or compound cutter while retaining the organic exterior. Best for compartments, dice-tower cores, electronics, channels, and access openings.

Use a cutter with rounded corners when sharp corners would leave thin walls or stress concentrations.

## 2. Cavity plus separate insert

Subtract a seat and print the functional component separately. Benefits:

- different material/orientation;
- easier iteration and maintenance;
- less risk to the source shell;
- clean supports and better dimensional calibration.

Use a flange, ledge, rails, screws/inserts, snap features, magnets, adhesive land, or tongue-and-groove interface.

## 3. Window and patch/door

Cut an opening but retain a controlled rim. The replacement part covers or sits inside the rim. Best for doors, battery covers, belly compartments, service panels, and removable decorations.

## 4. Split-and-replace

Classify points/faces relative to a datum plane or fitted surface, remove one side, preserve a transition band, and replace it parametrically. Best for replacing a shoe sole or base.

A planar split is only valid when the actual interface is planar. Otherwise use a fitted spline surface, height field, offset shell, or manually authored boundary.

## 5. Conformal interface shell

Extract or duplicate a local patch, smooth only the low-frequency shape, offset it, and use it as a fitting/bonding surface. Best for curved flanges, pads, saddles, and shoe interfaces.

## 6. Embedded functional core

Keep the decorative shell and add an internal frame, rib cage, staircase, bearing seat, or electronics carrier. This can remain unfused if captured mechanically.

## 7. Decorative skin over parametric core

When function dominates, construct the entire core parametrically and use the organic model only as an outer skin/relief. This is often more robust than trying to derive structural geometry from an AI mesh.

## 8. Local SDF/voxel fusion

Crop the source around the transition, combine it with the functional part as a signed field, extract a local fused patch, and stitch/union it back to the untouched source. Use when triangle intersections are pathological or smooth blending is required.

## Shape selection

| Shape | Use when | Caution |
|---|---|---|
| Cylinder/tapered cylinder | axial tower, bore, cup, round core | check minimum radial wall at every height |
| Capsule | compartment/cavity with smooth ends | needs room beyond straight section |
| Rounded box | electronics, doors, storage | corner radius should exceed uncertainty and print limits |
| Sphere/ellipsoid | bulbous body, low stress cavity | may waste volume and create steep roofs |
| Loft | varying cross-section, organic transition | inspect every station and prevent twist |
| Extruded spline | side-defined opening/slot | ensure closed valid profile and overshoot |
| Offset surface | uniform fitted gap/bond land | offsets can self-intersect in tight concavities |
| Convex envelope | robust approximate volume | can remove too much in concave regions |
| Compound cutter | exact pathway/openings | union cutters first and inspect seams |

Choose the simplest shape that leaves adequate wall and fulfills the functional envelope. Decorative similarity is secondary to predictable manufacturing and validation.
