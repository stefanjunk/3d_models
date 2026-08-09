# Example 3 — Wood-textured honeycomb wall shelf

A 35 mm-deep regular hexagonal shelf with outer radius 60 mm and inner radius 51 mm. Wood texture appears on outer wall, inner wall, front rim, and back rim.

## Files

- `source/wood-source.png`: seamless directional wood grain with knots.
- `prepared/wood-heightmap-{draft,print}.png`.
- `config/*-{draft,print}.json`: four surface families.
- `cadquery/base_model.py`: parametric hexagonal shell.
- `openscad/apply_relief.scad`: one Boolean using all cutter bodies.

## Mapping

Wall configs swap native perimeter/depth coordinates so grain runs consistently along shelf depth. Front/back sectors use one global XY projection, avoiding per-face rotation. Ring sectors are slightly gapped to remain independent watertight cutter bodies.

## Build

```bash
python scripts/build_examples.py --example 3 --quality draft --engine auto
```

See `references/10-examples.md`.
