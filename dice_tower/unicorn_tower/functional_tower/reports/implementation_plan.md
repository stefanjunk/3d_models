# Functional Unicorn Dice Tower Implementation Plan

**Goal:** Preserve the imported unicorn exterior while producing one upright,
watertight FDM-printable dice tower with a closed base, open core, connected
rounded baffles, and through-openings for 22 mm dice.

**Architecture:** A preprocessing script reloads the source, welds coincident
vertices, applies +90 degrees about X, scales to millimetres, translates the
minimum Z to zero, and exports a derived upright input mesh. A parameter-driven
OpenSCAD model hollows and cuts that mesh, then unions wall-intersecting rounded
baffles. Reloaded final-STL validation, path sampling, printability checks, and
multi-angle/cutaway previews form the release gate.

**Tech stack:** Python 3, Trimesh, NumPy, OpenSCAD CLI, Matplotlib, shared
`mesh-validation`, and shared `fdm-printability` scripts.

## Execution tasks

1. Inspect principal axes and four radial projections; lock front/back axes.
2. Export a welded, oriented, millimetre-scaled exterior derivative.
3. Implement the parameterized hollow shell, rounded inlet/outlet, and five
   staggered rounded baffles with positive shell overlap.
4. Export a low-cost preview and inspect bounds, orientation, openings, and
   interior path before the final render.
5. Export the final STL and reload it from disk.
6. Validate watertightness, winding, component count, bounds, volume, floor
   closure, opening penetration, baffle fusion, and a conservative die path.
7. Run FDM checks and document slicer/physical-test limitations.
8. Render and inspect isometric, front, back, and cutaway/interior previews.
