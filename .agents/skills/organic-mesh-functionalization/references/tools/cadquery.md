# CadQuery guidance

## Best role

CadQuery is preferred for precise functional geometry:

- cylindrical cores and tubes;
- stairs and baffles;
- rounded compartments;
- doors, lips, hinges, pins, and latches;
- shoe sole cores, flanges, channels, and tread masters;
- test gauges and interface coupons;
- STEP deliverables.

Use CadQuery to build cutters and inserts, not to absorb a multi-million-triangle organic STL into B-Rep.

## Workflow

1. Establish the same coordinate frame and units as the organic mesh.
2. Encode all dimensions in a parameter structure.
3. Construct on named workplanes and datums.
4. Add assertions for minimum wall, clearance, and valid ranges.
5. Export each functional body as STEP and as a tessellated STL/3MF for mesh combination.
6. Combine with the organic mesh in Blender or Manifold3D.
7. Retain STEP as the authoritative functional source.

## Fitting to the organic mesh

Use measurements derived from the mesh:

- section outlines simplified to splines/polylines;
- fitted cylinder/cone parameters;
- seam plane and landmark transforms;
- clearance envelope;
- sampled boundary points.

Do not import every triangle as a CAD face. If a mesh-derived boundary is required, reduce it to a manageable section curve.

## Boolean robustness inside CadQuery

CadQuery/OpenCascade works best when the bodies are valid B-Reps with non-zero overlap. Avoid zero-thickness contacts and tiny sliver features. Apply fillets after the primary solid is stable; very large or topologically ambiguous fillets often fail.

## Dice tower

Generate the staircase/baffles and all cutter bodies parametrically. Export the cavity cutter, portal cutters, and staircase separately. The final fusion with the decorated shell should occur in a mesh-capable tool.

## Barefoot sole

Generate outline, thickness field approximation, zero-drop reference planes, flex grooves, tread, and upper attachment flange parametrically. For strongly organic top surfaces, use lofted sections or export a sole core that is blended to the retained mesh in Blender/SDF.

## Toy compartment

Generate the liner, door, lip, hinge barrels, pins, latch, and clearance bodies separately. Include test coupons for hinge and latch clearances.
