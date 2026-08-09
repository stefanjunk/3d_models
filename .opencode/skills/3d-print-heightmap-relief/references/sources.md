# Sources and further reading

Checked 2026-08-09. Tool APIs and documentation can change; verify against the installed version.

## OpenCode skill format

- OpenCode, **Agent Skills**: https://opencode.ai/docs/skills/
  - on-demand skill discovery;
  - project path `.opencode/skills/<name>/SKILL.md`;
  - recognized frontmatter fields;
  - naming and troubleshooting rules.

## OpenSCAD

- OpenSCAD official cheat sheet: https://openscad.org/cheatsheet/
- OpenSCAD User Manual, **Surface Module**: https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Importing_Geometry/Surface_Module
  - PNG/data input;
  - image luminance and 0–100 height scaling;
  - `invert`, `center`, `convexity`;
  - alpha limitation and image orientation.

## CadQuery

- CadQuery documentation, **Importing and Exporting Files**: https://cadquery.readthedocs.io/en/latest/importexport.html
  - STEP/STL roles;
  - export formats;
  - tessellation tolerance and angular tolerance.

## FreeCAD

- FreeCAD Wiki, **Mesh Scripting**: https://wiki.freecad.org/Mesh_Scripting
- FreeCAD Wiki, **Mesh Difference**: https://wiki.freecad.org/Mesh_Difference
- FreeCAD Wiki, **Mesh Union**: https://wiki.freecad.org/Mesh_Union
- FreeCAD Wiki, **Mesh to Part**: https://wiki.freecad.org/Mesh_to_Part
  - mesh Boolean operations;
  - shape tessellation through `MeshPart.meshFromShape`;
  - mesh/Part conversion considerations.

The FreeCAD wiki may use an anti-bot interstitial in automated clients. Verify API spellings in the Python console for the installed release.

## Blender

- Blender Python API, **DisplaceModifier**: https://docs.blender.org/api/current/bpy.types.DisplaceModifier.html
- Blender Manual, **Displace Modifier**: https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/displace.html
- Blender Manual, **Subdivision Surface Modifier**: https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/subdivision_surface.html
- Blender Python API, **STL operators**: https://docs.blender.org/api/current/bpy.ops.wm.html
  - texture-driven displacement;
  - UV coordinate mode;
  - normal direction, strength, and midlevel;
  - subdivision and export.

## FDM process context

- Prusa Knowledge Base, **Layers and perimeters**: https://help.prusa3d.com/article/layers-and-perimeters_1748
- Prusa Knowledge Base, **Creating profiles for different nozzles**: https://help.prusa3d.com/article/creating-profiles-for-different-nozzles_127540

These sources support the distinction between XY extrusion/nozzle considerations and Z layer-height discretization. The numerical planning ranges in this skill are conservative engineering heuristics and must be verified with a coupon on the actual printer/material.

## Mathematical background

- Height field: https://en.wikipedia.org/wiki/Heightmap
- UV mapping: https://en.wikipedia.org/wiki/UV_mapping
- Normal mapping: https://en.wikipedia.org/wiki/Normal_mapping
- Parametric surface: https://en.wikipedia.org/wiki/Parametric_surface

## Included implementation references

The package is self-contained and uses:

- NumPy for arrays and geometry;
- Pillow for image I/O;
- SciPy for filtering/interpolation;
- trimesh for mesh I/O, topology checks, and Boolean dispatch;
- optional CadQuery for parametric bases;
- optional OpenSCAD/Blender/FreeCAD executables for backend operations.
