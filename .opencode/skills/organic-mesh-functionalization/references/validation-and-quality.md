# Validation and quality assessment

## Four levels of validation

### 1. File/topology

- file loads after export and re-import;
- expected vertices/faces and finite coordinates;
- watertightness and winding;
- positive volume;
- expected connected components;
- no unreferenced/degenerate/duplicate faces where detectable;
- no accidental zero-size bounds.

### 2. Geometric intent

- source/result overlay;
- protected-surface deviation outside ROI;
- cut depth/reach;
- opening dimensions;
- residual wall samples;
- clearances, interferences, and door/stair movement;
- sectional area and topology along the path;
- no hidden caps, duplicate shells, slivers, or trapped debris.

### 3. Manufacturing

- nozzle/layer-resolvable features;
- orientation and anisotropy;
- support accessibility and removal;
- bridge/overhang limits;
- drainage/air escape for closed cavities;
- bed fit and part separation;
- slicer preview confirms openings and bodies;
- material and interface process are compatible.

### 4. Function

- interface coupon;
- subassembly test;
- repeated cycle/drop/load test;
- fit on the actual mating object;
- inspection after conditioning, heat, moisture, or flexing as relevant.

## Protected-surface comparison

Use a mask representing `outside ROI + transition`. Compare source surface samples to the result and result samples to the source. Report:

- maximum;
- mean;
- median;
- 95th and 99th percentile;
- number/fraction above tolerance.

Symmetric comparison detects both accidental removal and accidental additions. Vertex-nearest-neighbour fallback is approximate; exact point-to-triangle proximity is preferred when dependencies permit.

## Volume accounting

Record source, cutter, insert, intermediate, and final volumes. Volume is a diagnostic, not an acceptance test by itself. A plausible total volume can hide a wrong-location cut.

## Cross-section review

Generate sections at:

- every functional opening;
- narrowest wall;
- start/end of transition band;
- extrema of fitted primitive;
- regular intervals through a long path.

For a dice tower, inspect the full dice route. For a shoe, inspect heel, midfoot, ball, and toe. For a compartment, inspect door rim, hinge side, latch side, and maximum cavity depth.

## Quality status

- **pass** — all measurable criteria and physical tests pass.
- **conditional** — topology and geometry pass but a physical/material test remains.
- **fail** — any protected-region breach, ambiguous topology, blocked function, insufficient wall, or unsupported safety claim.
