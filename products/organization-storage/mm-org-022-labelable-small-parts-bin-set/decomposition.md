# Design decomposition

| Component | Source of truth | Function | Interface |
|---|---|---|---|
| narrow bin | `config/model-parameters.json` + `cad/build.py` | small lots; 45 mm row unit | common depth, height, paper slot and carrier datum |
| medium bin | same | sewing notions or medium electronic lots; 67.5 mm | 2-hole identity code |
| wide bin | same | long/mixed parts; 90 mm | 3-hole identity code |
| matrix frame | same | registers two 180 × 75 mm rows | 0.6 mm side and 1.2 mm inter-row clearance |
| label-slot gauge | same | chooses a printable paper-card clearance | 0.5 / 0.7 / 0.9 mm stations |
| paper labels | user-cut purchased stock | replaceable identification | max 0.4 mm nominal card thickness |

All generated solids are independent parametric parts. No imported mesh, logo, font, magnet, fastener or proprietary grid geometry is used.
