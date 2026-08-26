# Multicolor FDM Design Skill

A source-first OpenCode specialist for designing and converting multicolor FDM/FFF models. It complements the existing functional, organic-mesh, freeform-surfacing, and height-map skills instead of duplicating them.

The package supports:

- parametric color solids, inlays, shells, inserts, and layer-change architectures;
- actual-filament palette capture and perceptual texture quantization;
- textured OBJ/glTF/GLB inspection and conversion planning;
- a Bambu Studio texture-to-color handoff with explicit Anycubic verification;
- a headless voxel-to-solid fallback and standards-based multi-part 3MF writer;
- purge/change estimation, validation, and three built examples.

## Quick start

```bash
export MCFDM_SKILL=.opencode/skills/multicolor-fdm-design
python3 "$MCFDM_SKILL/scripts/validate_skill.py"
python3 "$MCFDM_SKILL/scripts/build_examples.py" --output-root build/examples
```

## Install

Project-local:

```bash
./install.sh --project /absolute/path/to/project
```

Global skill only:

```bash
./install.sh --global
```

See `SKILL.md`, `references/00-scope-and-routing.md`, and `VALIDATION.md` in the package root.
