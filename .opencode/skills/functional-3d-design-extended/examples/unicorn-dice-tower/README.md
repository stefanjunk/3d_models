# Integrated unicorn dice tower

This OpenSCAD example demonstrates **part consolidation**: tower shell, alternating ramps, gussets, exit, and landing tray are one printable body. The unicorn artwork is original project SVG geometry and is shallowly engraved into the front wall.

## Build

```bash
openscad -o generated/unicorn-dice-tower.stl model.scad
```

## Critical review

- Inspect internal ramp layers in the slicer; the nominal 47° ramp is a starting point, not a universal printer limit.
- Test all intended dice sizes and shapes repeatedly.
- Do not use unreachable support inside the tower.
- Scale engraving depth/width with nozzle and layer height.
