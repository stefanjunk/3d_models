# Protected geometry map

| Geometry/data | Authority | Protected relation |
|---|---|---|
| Glyph pixels | `cad/gridfont.py` | `MM-GRID-5X7-v1`, same source for proof and CAD |
| Normalized strings | model parameters | proof and CAD must match exactly |
| Minimum feature | plate parameters | both lines ≥ 0.8 mm pixel width |
| Insert section | plate parameters | 3.0 mm thickness; 0.6 mm engraving; ≥2.4 mm backing |
| Production slot | stand parameters | 3.4 mm width at 70 degrees |
| Coupon slots | coupon parameters | 3.2/3.4/3.6 mm, same angle/cutter generator |
| Stand positions | stand parameters | symmetric centers −78/+78 mm |
| Installed envelope | workflow contract | ≤200 × 62 × 55 mm |

Do not decimate glyph faces, slot walls, key thickness, bottom datums, or the insert contact band. Regenerate every proof and manufacturing artifact after text or geometry changes.
