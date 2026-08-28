# Decomposition

| Component | Source of truth | Quantity in build set | Interface |
|---|---|---:|---|
| PaletteGrid base | `config/model-parameters.json` + `cad/build.py` | 1 | 16 paired slots in front/rear rails |
| Removable divider | same parametric source | 7 identical instances | two 2.4 × 9.4 × 8.0 mm tongues |
| Slot gauge | same parametric source | 1 | 2.7/2.9/3.1 × 10 mm slots |
| Divider fit key | same parametric source | 1 | exact production tongue section |
| Photo capture | `tools/photo_dimension_capture.py` | digital tool | 100 mm reference + four palette corner points + caliper thickness |

No purchased components, embedded hardware, fonts, logos, external meshes, or image-to-3D geometry are used. Palettes are customer-owned context and are not modeled or distributed.

Assembly order: print coupon pair, choose acceptable slot station, regenerate `base.slot_width_mm` if needed, print base and seven dividers, insert dividers in chosen grid positions, then load closed palettes.
