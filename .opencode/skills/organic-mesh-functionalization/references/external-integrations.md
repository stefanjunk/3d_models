# External skills, MCPs, and libraries

Use integrations only when they add a needed execution capability.

## Complementary skill

- `functional-3d-design`: materials, nozzles/layers, print-vs-buy, fasteners, snap-fits, gears, slicer and physical test planning.

## Useful capability categories

- Blender MCP/add-on for interactive scene and mesh operations;
- CadQuery execution/MCP and CadQuery LLM guidance for precise functional parts;
- FreeCAD MCP for document, assembly, Python, and selected FEM workflows;
- OpenSCAD CLI or MCP for deterministic CSG generation;
- Trimesh/Manifold3D Python environment for validation and headless Booleans;
- slicer CLI for final manufacturing preflight.

## Security and reproducibility

- pin versions;
- review licenses;
- restrict tool filesystem access to the project;
- do not silently download arbitrary meshes or execute unreviewed scripts;
- separate read-only review agents from destructive agents;
- record engine/version in every Boolean and validation report.

OpenCode can load skills on demand, configure external references, define custom tools, and use MCP servers. Keep the core workflow usable through local scripts even when no MCP is installed.
