# MARITA reinforced-run01 — digital DRAFT result

The approved 0.4.1 reinforcement has been applied parametrically to the
outline-balanced `MA | RITA` pair. The visible facade still consists of large,
separate glyphs with candidate-C wood relief; a glyph-shaped connector and
short local bridge bands sit behind the 12 mm-deep letters.

## Exact geometry

| Contract | v0.4.0 | v0.4.1 | Ratio |
|---|---:|---:|---:|
| Glyph depth | 6.0 mm | 12.0 mm | 2.00× |
| Connector thickness | 2.4 mm | 4.0 mm | 1.67× |
| Positive depth overlap | 0.1 mm | 2.0 mm | 20.00× |
| Local bridge width | 6.0 mm | 12.0 mm | 2.00× |
| Nominal gross bridge section | 14.4 mm² | 48.0 mm² | 3.33× |

The section ratios are deterministic geometry proxies, not measured stiffness
or strength. The connector occupies `y=10..14 mm`; glyphs occupy `y=0..12 mm`,
so the true overlap is 2 mm and the connector extends 2 mm behind the glyphs.

| Part | Envelope (mm) | Triangles | STL | Relief P95−P05 |
|---|---:|---:|---:|---:|
| MA left | 281.425 × 115 × 160 | 185,876 | 8.863 MiB | 0.331 mm |
| RITA right | 348.748 × 115 × 160 | 237,232 | 11.312 MiB | 0.327 mm |

Independent exact-coordinate audits pass for both STLs: one component,
watertight and consistently wound topology, positive volume, zero boundary and
nonmanifold edges, and declared bed/mesh budgets. Six and nine microscopic
Boolean sliver faces remain below the accepted numeric threshold; both exact
slicer runs accept the unchanged files.

## Wood appearance

- Registered 1254 × 1254 16-bit `wood-001` master.
- Direct bilinear sampling at about 0.45 × 0.45 mm; no reduced build raster.
- 120 × 45 mm physical repeat, 24 px periodic edge blend, 0.6 mm maximum depth.
- The robust relief span is byte-for-byte unchanged from v0.4.0: 0.331 mm on
  MA and 0.327 mm on RITA.
- Connector, counters, gaps, side blade, foot, bed datum, and book-contact
  surfaces remain protected.

## Exact Anycubic slice

Anycubic Slicer Next 1.3.9.4, Kobra 3 Max, 0.4 mm nozzle, explicit 0.12 mm
Standard process and Anycubic PETG profiles:

| Part | Status | Layers | Estimate | Filament | Change vs v0.4.0 | Native warning |
|---|---|---:|---:|---:|---:|---|
| MA | PASS | 1,333 | 11 h 52 min | 63.214 m | +13.2% time / +11.7% filament | none |
| RITA | PASS | 1,333 | 13 h 51 min | 72.389 m | +15.5% time / +15.1% filament | floating cantilever |

The exact G-code is retained as local evidence. It was not uploaded and no
print was started.

## Open gates

- Human layer/seam review, especially the RITA warning, crossbars, counters,
  connector bands, and first layer.
- Print and handling/deflection test of the reinforced FA coupon.
- Candidate-C appearance and complete 2.0 kg pair load/slide test.
- Watermark as the last solid change, standards-valid 3MF packaging, and final
  human release approval.
