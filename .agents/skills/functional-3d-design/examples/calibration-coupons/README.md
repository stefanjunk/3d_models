# Calibration coupons

Generate only the uncertainty you need:

```bash
openscad -D 'coupon="fit"' -o fit.stl model.scad
openscad -D 'coupon="walls"' -o walls.stl model.scad
openscad -D 'coupon="engraving"' -o engraving.stl model.scad
openscad -D 'coupon="bridges"' -o bridges.stl model.scad
```

Record printer, exact filament product/batch/drying, nozzle, layer height, line width, orientation, cooling, speeds, and slicer/profile hash. A fit measured in PLA with a 0.4 mm nozzle should not be silently reused for PETG-CF with a 0.6 mm nozzle.
