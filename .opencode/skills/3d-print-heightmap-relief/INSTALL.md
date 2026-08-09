# Installation

## Project-local OpenCode installation

Copy this package’s `.opencode` directory into the root of the target Git worktree:

```text
your-project/
└── .opencode/
    └── skills/
        └── 3d-print-heightmap-relief/
            └── SKILL.md
```

OpenCode discovers project skills from `.opencode/skills/<name>/SKILL.md` while walking up to the Git worktree.

## Global installation

Copy the skill directory to:

```text
~/.config/opencode/skills/3d-print-heightmap-relief/
```

## Python environment

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -r \
  .opencode/skills/3d-print-heightmap-relief/requirements.txt
```

Core functionality requires NumPy, Pillow, SciPy, and trimesh. `jsonschema` validates configurations. CadQuery is optional and is only needed for the included parametric base examples.

## Optional applications

Install one or more of:

- OpenSCAD for a dependable command-line fallback for mesh Booleans.
- CadQuery for the three parametric example bases.
- FreeCAD for STEP/B-rep preparation and mesh workflows.
- Blender for UV-based displacement and mesh editing.
- `manifold3d` for faster in-process mesh Booleans through trimesh.

The Boolean helper tries Manifold, Blender, then OpenSCAD when `--engine auto` is selected.

## Verify

```bash
cd .opencode/skills/3d-print-heightmap-relief
python scripts/self_test.py
```

A machine without CadQuery or OpenSCAD still runs the core tests; unavailable optional backends are reported rather than silently assumed.

## Build examples

```bash
python scripts/build_examples.py --quality draft --engine auto
```

For high-resolution cutter generation without the expensive final Boolean:

```bash
python scripts/build_examples.py --quality print --skip-boolean
```

Build outputs go to `build/` unless `--output-root` is supplied.
