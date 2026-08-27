# Product decomposition — MM-ORG-006

## Authority and parts

- JSON owns bar length, slot count/pitch, socket dimensions, clearances and cable bores.
- CadQuery owns one rigid bar, four TPU insert variants and the paired interface coupon.
- The PETG bar owns the 156 × 40 mm anti-tip footprint, 3 mm base skin and four local socket cells.
- Each TPU insert owns only its outer cartridge, retention ribs, cable bore and top entry slit.
- No purchased component, external mesh, logo, font or image-derived geometry is included.

## Interface contract

- Insert nominal envelope: 22 × 16 × 11 mm.
- Bar pocket: insert envelope plus 0.25 mm per side in X/Y and 0.20 mm vertical reserve.
- Two shallow insert side ribs add provisional 0.20 mm interference against matching pocket relief zones.
- Cable bore radius: nominal diameter/2 + 0.30 mm; slit width: 70% of nominal cable diameter.
- Inserts load vertically from +Z; all socket floors remain closed and all entries remain support-free.

The fit coupon pairs one socket cell with each insert cross-section. It must be printed in the intended PETG/TPU profiles before a full bar.
