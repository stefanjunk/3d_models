# MM-ORG-025 PaletteGrid

Fully parametric digital print candidate for SKU-007, the vertical makeup-palette organizer. One 190 × 106 mm base provides sixteen 11.5 mm grid stations. Seven identical removable dividers form six default compartments with 20.6/20.6/20.6/20.6/32.1/43.6 mm clear widths.

## Build

```bash
python cad/build.py
python tools/photo_dimension_capture.py assets/photo-capture-example.json --output reports/photo-capture-example-output.json
pytest -q
python cad/render_preview.py
```

Primary outputs are STEP masters, four unique watertight STLs, and a ten-object 3MF containing one base, seven divider instances, and both coupons. All are draft artifacts pending the physical tests listed in `tests/physical-test-plan.md`.

No external geometry, fonts, logos, or purchased components are used. No G-code is retained and no printer action is part of this project.
