# Research sources and provenance

Retrieved 2026-08-09, with mesh/optimization sources added 2026-08-13. URLs are included so future maintainers can verify updates.

## OpenCode

- Agent skills: https://opencode.ai/docs/skills/
- Agents and subagents: https://opencode.ai/docs/agents/
- Custom commands: https://opencode.ai/docs/commands/
- References: https://opencode.ai/docs/references/
- Permissions: https://opencode.ai/docs/permissions/

## CAD and mesh tools

- CadQuery introduction: https://cadquery.readthedocs.io/en/latest/intro.html
- CadQuery import/export: https://cadquery.readthedocs.io/en/latest/importexport.html
- CadQuery LLM skill: https://github.com/jmwright/cadquery-llm-skill
- CadQuery contrib MCP: https://github.com/CadQuery/cadquery-contrib/tree/master/mcp-server
- OpenSCAD documentation: https://openscad.org/documentation.html
- FreeCAD FEM workbench: https://wiki.freecad.org/FEM_Workbench
- Blender Voxel Remesh: https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/tool_settings/remesh.html
- Blender 3D Print Toolbox: https://docs.blender.org/manual/en/latest/addons/mesh/3d_print_toolbox.html
- Trimesh: https://trimesh.org/
- Trimesh booleans: https://trimesh.org/trimesh.boolean.html
- Manifold simplify tolerance: https://manifoldcad.org/docs/jsuser/classes/Manifold.html#simplify
- CGAL triangulated surface mesh simplification: https://doc.cgal.org/latest/Surface_mesh_simplification/index.html
- Blender Decimate modifier: https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/decimate.html
- 3MF Core mesh requirements: https://github.com/3MFConsortium/spec_core/blob/master/3MF%20Core%20Specification.md#41-meshes
- Prusa Simplify mesh: https://help.prusa3d.com/article/simplify-mesh_238941
- OrcaSlicer Simplify model: https://github.com/OrcaSlicer/OrcaSlicer/wiki/prepare_stl_transformation

## Libraries

- cq_warehouse: https://cq-warehouse.readthedocs.io/
- bd_warehouse: https://github.com/gumyr/bd_warehouse
- cq_gears: https://github.com/meadiode/cq_gears
- build123d: https://github.com/gumyr/build123d
- BOSL2: https://github.com/BelfrySCAD/BOSL2
- NopSCADlib: https://github.com/nophead/NopSCADlib
- step.parts: https://github.com/earthtojake/step.parts
- text-to-cad skills: https://github.com/earthtojake/text-to-cad

## DfAM, printing, materials, and mechanics

- NIST, Design Rules for Additive Manufacturing: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=921515
- NIST, polymer AM material-testing standards: https://nvlpubs.nist.gov/nistpubs/ir/2015/NIST.IR.8059.pdf
- Prusa material guide: https://help.prusa3d.com/materials
- Prusa layers and perimeters: https://help.prusa3d.com/article/layers-and-perimeters_1748
- Prusa nozzle selection: https://help.prusa3d.com/article/different-nozzle-types_2193
- Prusa maximum volumetric speed: https://help.prusa3d.com/article/max-volumetric-speed_127176
- Prusa modifiers: https://help.prusa3d.com/article/modifiers_1767
- Prusa infill patterns: https://help.prusa3d.com/article/infill-patterns_177130
- Prusa watertight prints: https://help.prusa3d.com/article/watertight-prints_112324
- Prusa modeling for printing: https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
- Stratasys, FDM for End-Use Parts: https://www.stratasys.com/siteassets/3dlc/high-school/tag_fdm_enduseparts_en_1015_web.pdf
- Printing-ready topology optimization for material extrusion: https://pmc.ncbi.nlm.nih.gov/articles/PMC10133987/
- Effects of infill density, wall perimeter, and layer height: https://pmc.ncbi.nlm.nih.gov/articles/PMC9867140/
- Influence of CAD versus slicer-generated infill patterns: https://www.mdpi.com/2076-3417/11/16/7272
- Covestro snap-fit design guide: https://solutions.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1557218421.pdf
- KHK gear technical reference: https://khkgears.net/new/gear_knowledge/gear_technical_reference/
- SKF bearing selection: https://www.skf.com/group/products/rolling-bearings/principles-of-rolling-bearing-selection

## Source-use policy

- Exact supplier/component drawings override generic library geometry.
- Filament supplier profiles override broad temperature ranges.
- A generic plastics snap-fit guide supplies geometry principles, not printed-fatigue allowables.
- Upstream repositories should be pinned and license-reviewed before production use.
