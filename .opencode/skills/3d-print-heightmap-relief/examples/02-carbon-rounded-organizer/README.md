# Example 2 — Carbon-fibre rounded desk organizer

A 90×65×95 mm organizer with 8 mm vertical corner radius, 2.4 mm walls, a bottom, and an internal divider. A periodic carbon weave is engraved continuously around front, left, back, right, and every rounded corner.

## Files

- `source/carbon-fiber-source.png`: seamless procedural twill-like source.
- `prepared/carbon-heightmap-{draft,print}.png`: one physical tile.
- `config/relief-{draft,print}.json`: three repeats around one rounded perimeter.
- `cadquery/base_model.py`: parametric organizer.
- `openscad/apply_relief.scad`: Boolean wrapper.

## Build

```bash
python scripts/build_examples.py --example 2 --quality draft --engine auto
```

The surface’s `depth_mm=65` is the organizer dimension. The engraving’s `relief.depth_mm=0.38` is separate by design.

See `references/10-examples.md`.
