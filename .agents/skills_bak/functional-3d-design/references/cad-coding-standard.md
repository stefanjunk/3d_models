# CAD coding standard

## Common rules

- Millimetres are the default unit; document every exception.
- Put user-facing parameters together and separate them from derived values.
- Assert impossible combinations before expensive geometry begins.
- Use deterministic filenames and an explicit output directory.
- Preserve an editable source representation; do not treat STL as the only master for precise parts.
- Provide `preview` and `final` quality modes when tessellation or repeated features are expensive.
- Record tool version, library version/commit, parameter file, and export tolerances.
- Separate exact/protected interfaces from reducible cosmetic, relief, scan, and redundant tessellation regions.
- Expose manufacturing tessellation/simplification parameters without overwriting the native or high-fidelity master.
- Give dense jobs explicit triangle, peak-memory, mesh-file, and exact-slicer budgets; store the unsimplified master mesh and selected manufacturing mesh at separate paths.
- Never hide a required manual transform after export; manufacturing STLs should already be oriented or have orientation recorded.
- Generate small coupons for interfaces whose value depends on a real printer process.

## OpenSCAD

- Use modules/functions and centralized Customizer parameters.
- Prefer 2D profile operations plus extrusion for repeated planar geometry.
- Bound `$fn` and use lower preview quality for arrays/reliefs.
- Keep imported SVG/DXF art original or license-documented.
- Use `assert()` for wall, clearance, and envelope constraints.
- Test with CLI `openscad -o output.stl model.scad`.
- Avoid huge `minkowski()` and thousands of nested booleans when an offset, 2D pattern, or mesh/SDF route is more stable.
- Bound `$fn` by physical chordal need; do not use one high global facet count for every cylinder and fillet.

## CadQuery

- Build around workplanes and sketches rather than world-coordinate boolean piles.
- Export STEP as the neutral editable master and STL/3MF separately.
- Keep construction features named in functions and return valid solids/assemblies.
- Use stable geometric intent; brittle edge-number selection is a last resort.
- Catch optional fillet failures only when retaining a valid unfilleted model is explicitly acceptable.
- Test parameter boundaries because shells, fillets, and lofts can fail abruptly.
- Separate assembled coordinates from print-oriented tessellated exports.
- Record chordal/angular STL tolerances and compare candidate tessellations with the exact STEP/B-Rep master.
- Keep geometric comparison output separate from the exact-slicer resolution/toolpath report.

## FreeCAD Python

- Pin/test the FreeCAD version and workbench dependencies.
- Create deterministic document/object names.
- Recompute before export and verify solids after recompute.
- Keep FEM setup in a separate script/config from source geometry.
- Report mesh size, element type, solver, material model, contacts, loads, constraints, and convergence—not only a screenshot.

## Blender Python

- Set units to millimetres/metres consistently and apply object transforms before boolean/export.
- Preserve an untouched source copy before remesh/destructive modifiers.
- Use Voxel Remesh only at a documented resolution; estimate memory before high resolution.
- Use exact functional cutters generated from parameters where fit matters.
- Apply modifiers in a controlled order and validate the exported mesh with an independent tool.
- Do not confuse visual smooth shading with geometric smoothness or watertightness.
- Protect bed planes, fits, seals, sharp features, and relief boundaries before Decimate; a face ratio alone is not a production tolerance.

## Mesh/SDF pipeline

- Define the coordinate origin, voxel spacing, array bounds, and iso-level explicitly.
- Leave a nonzero empty margin around the object so marching cubes does not terminate at the array boundary.
- Memory grows with voxel count; use coarse preview grids, chunked/sparse fields, or narrow-band SDFs.
- Pass physical spacing to surface extraction.
- Re-load the exported STL/3MF and validate it independently.
- Keep precision interfaces in CAD or at a locally finer resolution.
- Prefer curvature/error-adaptive output and chunked/sequential processing over a uniform fine grid covering flat regions.
