# Design decomposition

| Component | Source of truth | Function | Interface |
|---|---|---|---|
| small holder | `config/model-parameters.json` + `cad/build.py` | 20 × 16.5 mm comfort sample | 82 mm span; 1-hole underside code |
| medium holder | same | 23 × 19 mm comfort sample | 92 mm span; 2-hole code |
| large holder | same | 26 × 21.5 mm comfort sample | 102 mm span; 3-hole code |
| sizing guide | same | compare all three openings before full sample | same opening geometry and 1/2/3 code |

All parts are independent analytic CadQuery solids. No purchased component, font, logo, external vector or mesh participates in the geometry.
