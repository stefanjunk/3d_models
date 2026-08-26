# SDF and implicit blending

## Role

Signed-distance and implicit fields are valuable for geometry that should merge like grown material rather than like Boolean solids with constant fillets.

Typical uses:

- rib-to-shell and branch junctions;
- ergonomic grip transitions;
- chassis braces and load-path webs;
- feet or handles growing from a vessel;
- soft unions between a mechanical core and an aesthetic envelope;
- local cleanup of awkward multi-solid intersections.

## Field model

An SDF represents a surface as the zero level set of a scalar field \(d(x,y,z)\). Union, subtraction, offset, and smooth blending operate on fields rather than explicit patch intersections.

## Localize the operation

Do not voxelize or smooth the entire product merely because one junction is difficult. Define:

- region of interest;
- protected region;
- transition band;
- target voxel/cell size;
- maximum allowed surface deviation;
- features to regenerate afterward.

## Resolution planning

Field resolution must be chosen from the smallest physical feature and acceptable deviation, not from an arbitrary grid dimension. Memory grows approximately with the number of voxels in the occupied volume. Sparse VDB systems reduce empty-space cost but do not remove the need for a resolution plan.

## Smoothing choices

Mean, Gaussian-like, Laplacian, and curvature-flow methods affect shrinkage and feature preservation differently. Record:

- operation type and iterations;
- voxel size;
- narrow-band width;
- mask/falloff;
- before/after hardpoint and wall measurements.

## Exact-feature rule

After an SDF or voxel operation:

- re-cut holes and slots;
- restore planar mating faces;
- regenerate threads/inserts/bearing seats;
- remeasure wall thickness;
- compare the protected surface;
- export with a mesh tolerance fine enough to preserve the field result.

Use Houdini/OpenVDB, nTop, Blender SDF/volume nodes, libfive, or a controlled Python field pipeline according to available tools. The core examples in this package do not require an SDF backend.
