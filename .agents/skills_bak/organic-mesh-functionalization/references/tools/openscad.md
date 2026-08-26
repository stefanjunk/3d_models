# OpenSCAD guidance

## Best role

Use OpenSCAD when the imported mesh is already a clean 2-manifold solid and the modification is a simple, well-separated CSG operation. It is useful for quickly parameterizing primitive cutters and visible test geometry.

## Suitable operations

- subtract a cylindrical or box cavity from a clean STL;
- add a simple staircase or insert;
- create portal openings;
- generate alignment and clearance gauges;
- produce a reproducible proof of concept.

## Limitations

OpenSCAD is not an organic mesh repair environment. Full render operates on exact CSG/tessellated geometry and can become slow or fail on high-resolution invalid imports. Preview success does not guarantee F6 render success.

Do not use it as the first choice for:

- self-intersecting AI meshes;
- global hollowing with uniform wall thickness;
- local sculpted transitions;
- segmentation of textile versus sole;
- million-face mesh-to-CAD conversion;
- advanced moving assemblies.

## Boolean rules

- render with F6 before export;
- read console warnings;
- extend cutters beyond the target;
- use a small epsilon to avoid coplanar surfaces;
- keep imported mesh and generated insert in the same unit frame;
- validate exported STL externally.

See `examples/dice-tower/openscad_overlay.scad`.
