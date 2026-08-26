# Organic Mesh Functionalization Skill

A portable Agent Skill, optimized for OpenCode, for adding parametric and functional geometry to high-resolution organic meshes produced by image-to-3D systems.

## Install in OpenCode

Project-local:

```bash
mkdir -p .opencode/skills
cp -R organic-mesh-functionalization .opencode/skills/
```

Global:

```bash
mkdir -p ~/.config/opencode/skills
cp -R organic-mesh-functionalization ~/.config/opencode/skills/
```

OpenCode also discovers compatible `.agents/skills/` and `.claude/skills/` directories.

## Recommended runtime

- Python 3.10+
- NumPy, SciPy, Trimesh
- Manifold3D for robust valid-mesh Booleans
- Blender for organic mesh repair, local remesh, and Boolean execution
- CadQuery for precise cutters and inserts
- OpenSCAD for simple clean-mesh overlays
- FreeCAD for B-Rep workflows and simplified FEM

Install the Python core:

```bash
python -m pip install -r requirements-core.txt
```

Optional CAD dependencies are listed in `requirements-optional.txt`.

## Start

```bash
python scripts/inspect_mesh.py model.stl --json baseline.json
python scripts/estimate_voxel_memory.py --mesh model.stl --voxel 0.35 --buffers 5
```

Copy `assets/project-spec.template.yaml` and `assets/edit-roi.template.json` into the project and fill them before modifying geometry.
