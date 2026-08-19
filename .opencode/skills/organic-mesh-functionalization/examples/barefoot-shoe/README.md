# Barefoot shoe replacement example

The source mesh is used as a geometric reference. Do not assume the textile/sole boundary is a horizontal plane.

## Recommended sequence

1. Mark 20–50 seam landmarks around the shoe in Blender.
2. Extract footprint and seam sections.
3. Choose:
   - complete replacement;
   - skin-preserving core replacement;
   - reference-only sole rebuild.
4. Build the sole core and upper flange parametrically.
5. Create a replacement envelope and clearance cutter.
6. Combine in Blender/SDF, not by converting the full source mesh into CadQuery.
7. Check hidden voids, minimum sidewall, zero drop, toe box, and attachment tests.

`sole-parameters.json` is a requirements example, not a finished universal sole generator.
