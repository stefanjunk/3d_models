# Tool recipes

Choose by representation responsibility, not preference for one application.

## CadQuery / build123d / OpenCascade

Use for:

- exact hardpoints and B-Rep solids;
- spline wires, section lofts, shells, offsets, and STEP output;
- late holes, bores, interfaces, splits, and assemblies.

CadQuery supports spline interpolation/approximation and variational smoothing parameters. build123d exposes B-spline edges, lofts, and the OpenCascade kernel in a code-first API. Test installed versions because signatures evolve.

Pattern:

```text
parameters → guide wires/sections → loft/surface → shell/solid
→ exact feature regeneration → STEP → controlled mesh export
```

## Rhino / Grasshopper / Alias

Use for interactive high-quality surface development, curve combs, zebra/highlight analysis, surface matching, G2/G3 blends, and visual tuning. Grasshopper is strong for semantic parameters and repeatable surface networks. Alias is specialized for premium NURBS product surfacing.

Store:

- named inputs and data trees;
- section/rail landmarks;
- continuity targets/tolerances;
- screenshots or reports from zebra/curvature analysis;
- neutral exports plus native source.

## Blender

Use for:

- SubD cages;
- Lattice and Mesh Deform;
- shape keys/morph targets;
- Geometry Nodes procedural variation;
- retopology and reference fitting;
- local volume/SDF operations and presentation.

Keep object transforms applied before dimensional work. Export the evaluated mesh and compare hardpoints. Do not rely on smooth shading.

## FreeCAD and Curves workbenches

Use when open-source GUI handoff, STEP editing, sketches, drawings, or Python macros are important. Validate loft/network operations and file recompute in the exact installed version. Keep a fallback neutral export.

## Houdini / OpenVDB / nTop

Use for local implicit blends, field-driven thickness, graded structures, organic ribs, and high-complexity spatial variation. Record voxel/field resolution and protect exact regions. These tools are optional and not assumed by the core package.

## OpenSCAD / BOSL2

Use for mathematically generated vessels, sweeps, profiles, patterns, and print-first fixtures. It is effective for Fourier/superformula-like decoration and compact parameter sets. It is not the preferred platform for vehicle-style Class-A patch networks.

## Pure Python helpers in this skill

The core scripts provide a portable baseline:

- regularized and Fourier curve fairing, plus optional SciPy B-spline fitting;
- curvature screening;
- closed-section resampling and seam alignment;
- deterministic mesh loft/export and an optional CadQuery/OpenCascade STEP loft backend;
- Bernstein-lattice FFD with fixed-box falloff and hardpoint comparison;
- topology and mesh metrics;
- optional Trimesh reference-section extraction;
- three example generators.

Use them for reproducible prototypes, automated regression, and OpenCode execution. Move to a CAD/DCC backend when exact NURBS continuity, STEP solids, advanced offsets, or interactive art direction are required.
