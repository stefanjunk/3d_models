# Parametric four-color inlay nameplate

This example keeps three accent colors inside the top 0.6 mm of a 3 mm plate. The base is Boolean-cut by the exact same profiles used for the color inserts, so the four exported solids are aligned and non-overlapping.

Build through `scripts/build_examples.py`, or manually:

```bash
openscad -o base.stl -D 'part="base"' model.scad
openscad -o border.stl -D 'part="border"' model.scad
openscad -o lettering.stl -D 'part="lettering"' model.scad
openscad -o icon.stl -D 'part="icon"' model.scad
```

Design lesson: restrict colors to a narrow Z band whenever the visual concept allows it. This dramatically reduces color-active layers and purge compared with a through-body partition.
