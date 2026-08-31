# NameForm 0.4.0 digital validation

Status: **DRAFT PRINT CANDIDATE — DIGITAL PASS WITH HUMAN REVIEW REQUIRED**

The approved letter-only architecture has been built with exact CadQuery
functional geometry and candidate-C wood relief on the glyph fronts. There is
no rectangular facade panel. Glyphs use a true 122 mm cap height, 1.8 mm actual
outline spacing, 6.0 mm body depth, and a 2.4 mm connector beginning nominally
6.0 mm behind the front. Only 6.0 mm wide local rear bridges join neighboring
outlines and the side blade.

## Main artifacts

- Left textured STL: `../../exports/v0.4.0/candidate/DRAFT-nameform-STE-left-wood-C-v0.4.0.stl`
- Right textured STL: `../../exports/v0.4.0/candidate/DRAFT-nameform-FAN-right-wood-C-v0.4.0.stl`
- Engineering STEP masters and assembly: `../../exports/v0.4.0/engineering/`
- Front evidence render: `renders/DRAFT-nameform-STE-FAN-front-v0.4.0.png`
- Three-quarter evidence render: `renders/DRAFT-nameform-STE-FAN-three-quarter-v0.4.0.png`
- Representative coupon: `../../coupons/nameform-letter-bridge-v0.4.0/`

## Deterministic geometry and texture results

| Artifact | Envelope mm | Triangles | File MiB | Topology | Active relief P95-P5 |
|---|---:|---:|---:|---|---:|
| FA coupon | 137.632 x 8.400 x 122.000 | 120,874 | 5.76 | watertight, 1 body | 0.320 mm |
| STE left | 268.382 x 115.000 x 160.000 | 158,212 | 7.54 | watertight, 1 body | 0.340 mm |
| FAN right | 300.315 x 115.000 x 160.000 | 211,348 | 10.08 | watertight, 1 body | 0.329 mm |

All meshes retain z=0, open counters, at least 1.8 mm front gaps, zero boundary
edges, zero nonmanifold edges, and remain well below the 1,000,000-triangle and
50 MiB stop budgets. The coupon and right STL contain 3 and 7 diagnostic
float32-scale micro-triangles respectively; they remain part of closed manifold
shells. A decimal-place weld was rejected because it opened the coupon shell.
Clean temporary rebuilds reproduced both pair STLs byte-for-byte.

## Exact Anycubic Slicer Next results

Machine: Anycubic Kobra 3 Max, 0.4 mm nozzle. Process: 0.12 mm Standard.
Filament profile: Anycubic PETG. Slicer: 1.3.9.4.

| Artifact | Layers | Slicer estimate | Filament | G-code SHA-256 |
|---|---:|---:|---:|---|
| FA coupon | 1,016 | 3 h 58 min | 18.50 m | `3cc5de7ff8767ba6c5bf83ee3ab9097a3e4dcb03c0fcdec27d680d4d6e9d03c6` |
| STE left | 1,333 | 9 h 42 min | 51.16 m | `9880163a88ca91dee2c47ed7c06dba5234a44f69a5d768ce5610b236c9094369` |
| FAN right | 1,333 | 11 h 09 min | 59.85 m | `1d713d2905f234e1851252d259992831bcd940da99153ce14a5230e648cbfd3e` |

All three runs returned native success and passed G-code analysis. The slicer
warns about floating regions/cantilevers. These correspond to the intended
letter crossbars and small rear bridges and are not silently waived: inspect the
layer preview and print the FA coupon without support before treating the pair as
physically qualified.

## Open gates

- Human layer, seam, bridge, and first-layer review.
- Physical FA coupon appearance and connector-handling acceptance.
- Exact filament manufacturer/product/color/batch/conditioning record.
- Complete-pair load, slide, handling, and appearance tests.
- 0.4.0 watermark placement and 3MF packaging.
- Final human model/release approval.

No printer upload or print start was performed.
