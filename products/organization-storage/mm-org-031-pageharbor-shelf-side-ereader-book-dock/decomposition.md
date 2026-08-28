# Design decomposition

| Component | Source of truth | Function | Manufacturing state |
|---|---|---|---|
| Selected dock | `config/model-parameters.json` + `cad/build.py` | Book pocket, device shoes/stops, four leaning contact rails and two gussets | Selected STL/STEP |
| Device fit gauge | Same parameter source | Five clearance-added U slots | Selected coupon STL/STEP |
| Device key comb | Same parameter source | Exact 8/10/12/14/16 mm reference tongues | Selected coupon STL/STEP |
| Book fit gauge | Same parameter source | Three clearance-added U slots | Selected coupon STL/STEP |
| Book key comb | Same parameter source | Exact 18/30/42 mm reference tongues | Selected coupon STL/STEP |
| Light dock | Same source with structural override | Quantified material experiment | Rejected variant STL/STEP |
| Virtual use assembly | Parametric proxy solids | Device/book envelope review only | STEP, not manufacturing |

No downloaded geometry, logo, electronic part or purchased fastener is embedded. Every printable solid is regenerated from repository-owned code and parameters.
