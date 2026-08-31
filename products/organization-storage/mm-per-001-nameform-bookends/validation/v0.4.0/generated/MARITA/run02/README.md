# MARITA run02 — digital DRAFT result

The parametric 0.4.0 generator selected `MA | RITA` from the real packed glyph
outlines. Both parts keep the approved 122 mm cap height, 1.8 mm visible outline
gap, recessed local connector, inward foot, and candidate-C wood relief.

## Geometry

| Part | Envelope (mm) | Triangles | STL | Relief P95-P05 |
|---|---:|---:|---:|---:|
| MA left | 281.425 × 115 × 160 | 185,836 | 8.861 MiB | 0.331 mm |
| RITA right | 348.748 × 115 × 160 | 237,192 | 11.310 MiB | 0.327 mm |

Independent exact-coordinate audits pass: one component per STL, watertight,
consistent winding, positive volume, no open/nonmanifold/duplicate faces, bed
fit, and all triangle/file budgets. Six and nine numerical Boolean sliver faces
remain below 2.7e-9 mm²; they are accepted only because topology stays closed
and both exact slicer runs succeed.

## Texture

- Source: registered 1254 × 1254, 16-bit `wood-001` master.
- Physical repeat: 120 × 45 mm with 24 px periodic edge blend.
- Mapping: direct bilinear sampling at approximately 0.45 × 0.45 mm; no reduced
  build raster.
- Maximum source relief: 0.6 mm with a 1.2 mm zero-relief outline taper.
- Protected: connector, gaps, counters, side blade, foot, bed datum, and book
  contact surfaces.

## Exact slice

Anycubic Slicer Next 1.3.9.4, Kobra 3 Max, 0.4 mm nozzle, explicit 0.12 mm
Standard process and Anycubic PETG profiles:

| Part | Native result | Layers | Estimate | Filament | Native warning |
|---|---|---:|---:|---:|---|
| MA | PASS | 1,333 | 10 h 29 min | 56.617 m | none |
| RITA | PASS | 1,333 | 11 h 59 min | 62.911 m | floating cantilever; human review required |

The G-code is preserved as exact local evidence only. No upload or print start
was performed.

## Open gates

- Human layer/seam review, especially `RITA` crossbars and local rear bridges.
- Physical appearance and connector-handling test using the exact profile.
- Complete-pair load/slide test.
- 0.4.0 watermark integration, 3MF package, and final release approval.
