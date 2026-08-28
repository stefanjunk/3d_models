# Design decomposition

| Component | Source of truth | Function | Manufacturing state |
|---|---|---|---|
| Selected rack | `config/model-parameters.json` + `cad/build.py` | Eight aligned pair stations, base, collars and rounded posts | Selected STL/STEP |
| Spool-post gauge | Same source | 4.0/4.5/5.0/5.5 mm real-spool bore trial | Selected coupon STL/STEP |
| Bobbin-post gauge | Same source | 3.5/4.0/4.5/5.0 mm real-bobbin bore trial | Selected coupon STL/STEP |
| Light rack | Same source with base-only override | Structural/material experiment with unchanged fit pins | Rejected variant STL/STEP |
| Virtual loaded assembly | Parametric envelope proxies | Spacing review only | STEP, not manufacturing |

No downloaded mesh, machine-brand geometry or logo is embedded. Real spools and bobbins are purchased/user-owned test objects, not supplied components.
