# Sources and further reading

Checked 2026-08-19. Tool documentation and research systems evolve; verify APIs against installed versions.

## OpenCode skill compatibility

- OpenCode Agent Skills: https://opencode.ai/docs/skills/
  - project path `.opencode/skills/<name>/SKILL.md`;
  - global path under the OpenCode configuration directory;
  - recognized frontmatter fields;
  - name/directory matching and description constraints.
- OpenCode Commands: https://opencode.ai/docs/commands/
  - project command path and `$ARGUMENTS` substitution.
- OpenCode References: https://opencode.ai/docs/config/#references

## B-splines, NURBS, and CAD kernels

- OpenCascade Modeling Data user guide: https://dev.opencascade.org/doc/overview/html/occt_user_guides__modeling_data.html
- OpenCascade B-spline continuity notes: https://dev.opencascade.org/doc/refman/html/class_geom___b_spline_curve.html
- CadQuery class reference (`spline`, `splineApprox`, surface approximation): https://cadquery.readthedocs.io/en/latest/classreference.html
- CadQuery examples (splines and lofts): https://cadquery.readthedocs.io/en/latest/examples.html
- build123d documentation: https://build123d.readthedocs.io/
- SciPy smoothing splines: https://docs.scipy.org/doc/scipy/tutorial/interpolate/smoothing_splines.html
- SciPy `make_smoothing_spline`: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.make_smoothing_spline.html

## Surface continuity and visual analysis

- Rhino Zebra analysis and G0/G1/G2 explanation: https://docs.mcneel.com/rhino/8/help/en-us/commands/zebra.htm
- Rhino Global Edge Continuity: https://docs.mcneel.com/rhino/9/help/en-us/commands/globaledgecontinuity.htm
- Autodesk Alias NURBS theory: https://help.autodesk.com/cloudhelp/2023/ENU/Alias-Getting-Started/files/theory-builders/GUID-366304CB-16FF-46F9-9F64-D7385358D855.html
- Autodesk Alias surface continuity: https://help.autodesk.com/cloudhelp/2020/CHS/Alias-Tutorials/files/GUID-2FCE06EB-8EF7-4507-92F7-82A73A0DF378.htm

## SubD, deformation, and morphs

- Blender Subdivision Surface: https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/subdivision_surface.html
- Blender Lattice Modifier: https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/lattice.html
- Blender Mesh Deform: https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/mesh_deform.html
- Blender Shape Keys: https://docs.blender.org/manual/en/latest/animation/shape_keys/introduction.html
- Blender Geometry Nodes Subdivision Surface: https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/mesh/operations/subdivision_surface.html
- Sederberg and Parry, Free-Form Deformation of Solid Geometric Models: https://www.cs.utah.edu/~ladislav/sederberg86freeform.pdf
- PyGeM FFD documentation: https://mathlab.github.io/PyGeM/ffd.html

## SDF / implicit workflows

- Houdini VDB Smooth SDF: https://www.sidefx.com/docs/houdini/nodes/sop/vdbsmoothsdf.html
- Houdini VDB from Polygons: https://www.sidefx.com/docs/houdini/nodes/sop/vdbfrompolygons.html
- libfive functional solid modeling: https://github.com/libfive/libfive

## FDM surface context

- Prusa, modeling with 3D printing in mind: https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
- Prusa, variable layer height: https://help.prusa3d.com/article/variable-layer-height-function_1750
- Autodesk Fusion mesh export controls: https://help.autodesk.com/view/fusion360/ENU/?guid=SLD-3D-PRINT

## AI and research directions

These are research references, not assumed production dependencies:

- NURBS-Diff: https://arxiv.org/abs/2104.14547
- Text2CAD: https://arxiv.org/abs/2409.17106
- NURBGen: https://arxiv.org/abs/2511.06194
- DreamCAD: https://arxiv.org/abs/2603.05607
- FutureCAD: https://arxiv.org/abs/2603.11831
- HistCAD: https://arxiv.org/abs/2602.19171
- Text2CAD-Bench: https://arxiv.org/abs/2605.18430
- Log-aesthetic curve fairing: https://link.springer.com/article/10.1007/s13160-023-00567-w
