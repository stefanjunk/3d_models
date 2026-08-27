# Provisional print guide

## Starting process

- PLA or PETG prototype
- 0.4 mm nozzle
- 0.20 mm layers
- 0.45 mm nominal line width
- 3 perimeter paths minimum; the modeled 2.70 mm walls allow six nominal lines
- 4 top/bottom layers minimum
- 10–15% gyroid or equivalent where the slicer creates infill
- supports: none intended
- orientation: tray floor and gauge bases on the bed

## Measurement-first sequence

1. Record the furniture system, article number, country, purchase date/revision and drawer location.
2. Measure free width and depth at front, middle and rear, plus available height under every moving part.
3. Slice and print the three gauge bars. Start with 209.30 mm and stop if insertion needs force or marks the surface.
4. Choose the widest gauge that inserts/removes freely and permits the drawer to close without rubbing.
5. Convert that result into the tray envelope parameter; do not scale the STL in the slicer.
6. Rebuild and revalidate, then print the tray unchanged.

Reject the interface if a gauge bows, needs tool-assisted insertion, marks the furniture, interferes with stops/slides, or changes drawer closure. The 3MF is an inventory set, not a pre-arranged build plate.

The package contains no exact slicer metrics. Inspect first-layer coverage, perimeter allocation, islands and G-code before printing.
