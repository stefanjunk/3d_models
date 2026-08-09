# Worked example strategy

## 1. Honeycomb wall shelf/display

### Recommended route

- CadQuery for exact hexagonal shell, back panel, rounded edges, and keyhole interfaces.
- Printed cell/frame.
- Purchased screws and wall-specific anchors.
- Optional printed connectors between cells.

### Why not print everything?

Wall anchors are substrate-specific and their performance cannot be inferred from the shelf model. Use a certified purchased anchor and verify the actual wall.

### Key tests

- body/mesh validity;
- keyhole fit coupon with the actual screw head;
- proof load using nonvaluable ballast;
- creep inspection after sustained load;
- wall-mount safety review.

## 2. Rounded desk organizer

### Recommended route

- CadQuery for rounded B-Rep body, drawer cavities, drawers, top pockets, and STEP outputs.
- Printed body and drawers.
- Optional purchased felt, magnets, or rubber feet.

### Key tests

- drawer clearance coupon;
- no-support print orientation;
- drawer travel and anti-tip behavior;
- edge comfort;
- profile/material choice based on heat and impact, not appearance alone.

## 3. Unicorn dice tower

### Recommended route

- OpenSCAD for shell, ramps, tray, parametric wall thickness, and SVG/2D engraving.
- Blender only if the unicorn becomes a sculpted organic relief.
- Printed tower/tray; optionally purchased felt liner to reduce noise.

### Key tests

- dice do not trap across intended sizes;
- self-supporting ramp angles and slicer preview;
- exit and tray retain dice;
- engraving survives nozzle/layer resolution;
- intended user/age safety review.

Each example folder includes a design specification, source, print notes, acceptance plan, and generated-output instructions.
