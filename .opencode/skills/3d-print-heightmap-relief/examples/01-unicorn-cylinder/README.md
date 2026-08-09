# Example 1 — Unicorn cylindrical gift box

A 40 mm-radius, 90 mm-high open gift box with a separate lid. A stylized unicorn is engraved around a 78 mm-tall side band.

## Files

- `source/unicorn-source.png`: procedural 16-bit master.
- `prepared/unicorn-heightmap-{draft,print}.png`: physically sampled derivatives.
- `config/relief-{draft,print}.json`: cylindrical mapping.
- `cadquery/base_model.py`: body and lid.
- `openscad/apply_relief.scad`: direct Boolean wrapper.

## Build

From the skill root:

```bash
python scripts/build_examples.py --example 1 --quality draft --engine auto
```

The unicorn uses `contain`, not stretch. Blank background protects the full-wrap seam. The lid is not textured, so fit remains independent of the relief Boolean.

See `references/10-examples.md`.
