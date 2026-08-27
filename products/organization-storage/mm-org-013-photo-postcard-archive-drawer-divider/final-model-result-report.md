# Final digital model result — MM-ORG-013

Revision `0.1.0-draft.1` is a complete parametric digital print candidate. Physical validation is intentionally deferred.

## Product

- Archive frame: 210 x 170 x 24 mm with a continuous base, ten selectable receiver positions, a 182 mm active-media width and a 19.2 mm lateral index gutter.
- Six interchangeable dividers: 209.2 x 68 x 2 mm with date labels 1900, 1980, 2000, 2010, 2020 and 2025.
- Three full-size open gauges: 10 x 15 cm, DIN A6 and 13 x 18 cm, each with 2.0 mm total allowance in both axes.
- Source of truth: `config/model-parameters.json`; deterministic builder: `cad/build.py`.
- Frame CAD-volume reduction versus the full 210 x 170 x 80 mm bounding block: 95.21 percent.

## Manufacturing outputs

- `exports/3mf/DRAFT-MM-ORG-013-frame-and-first-three-dividers-0.1.0-draft.1.3mf`
- `exports/3mf/DRAFT-MM-ORG-013-remaining-three-dividers-0.1.0-draft.1.3mf`
- `exports/3mf/DRAFT-MM-ORG-013-three-format-gauge-set-0.1.0-draft.1.3mf`
- Frame, six divider and three gauge STL files plus frame, divider, gauge-set and installed-assembly STEP masters.

## Digital evidence

- Parameter tests: 8 passed.
- Ten manufacturing meshes: each one watertight, consistently wound, positive-volume component with zero boundary, nonmanifold, degenerate or duplicate faces; frame 844 faces, dividers 1,024–1,168 faces, gauges 28 faces each.
- Three 3MF packages: millimetres, 4 + 3 + 3 watertight positive-volume objects.
- Exact local-profile slices: Anycubic Slicer Next 1.3.9.4, Kobra 3 Max 0.4 mm, 0.20 mm Standard, Anycubic PLA; all three passed with no native or G-code warnings.
- Aggregate slicer estimate: 34,179 s (9 h 29 min 39 s); extruded volume 221,225.6 mm3; positive extrusion 91,974.9 mm; peak flow 13.06 mm3/s.
- Aggregate digital validation: `PASS`; physical fit, snagging, visibility, cycle and drawer-closure checks remain optional `REVIEW_REQUIRED` by the user's direction.

## Release boundary

All artifacts remain `DRAFT`. No printer upload/start occurred. Actual drawer and sleeve measurement, all three gauge trials, paper-edge inspection, 250 divider insertions, 500 retrieval cycles, loaded drawer clearance, watermark qualification and commercial release remain open. Printed PLA is not claimed as an archival or photo-safe primary enclosure.
