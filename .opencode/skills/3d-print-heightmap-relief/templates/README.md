# Tool templates

These are starting points, not opaque generators.

- **OpenSCAD**
  - `flat_surface_emboss.scad`: native `surface()` for a flat plate.
  - `imported_patch_boolean.scad`: recommended curved-surface path; import a closed patch made by `scripts/relief_patch.py`.
- **CadQuery**
  - `parametric_base_with_mesh_relief.py`: keep the base as a B-rep, tessellate once, then apply the dense relief as a mesh Boolean.
  - `coarse_native_pixel_relief.py`: B-rep-only method for sparse logos at low cell counts.
- **FreeCAD**
  - `part_to_mesh_relief.FCMacro`: controlled tessellation of a STEP/B-rep.
  - `mesh_relief_boolean.FCMacro`: mesh Boolean against a watertight relief cutter.
- **Blender**
  - `displace_heightmap.py`: UV-driven normal displacement with Simple subdivision and command-line STL export.

Read the matching `references/05-*.md` through `08-*.md` before adapting a template.
