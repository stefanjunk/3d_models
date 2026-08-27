# Product decomposition

| Component | Source of truth | Manufacturing role | Interface |
|---|---|---|---|
| Caddy chassis | `config/model-parameters.json` + `cad/build.py` | Upright PLA print | Base-connected wells, phone cradle and nameplate channel |
| Personalized nameplate | Embedded glyph map + name parameters | Flat PLA print | Slides from above into the front C-channel |
| Coupon holder | Production channel parameters | Small upright test print | Reproduces guide depth, overlap and clearances |
| Coupon plate | Production text/plate generator | Small flat test print | Confirms insertion and engraved-pixel legibility |

Datums: chassis bottom `Z=0`; front exterior backing `Y=0`; chassis left edge `X=0`. The assembly STEP owns registration. The manufacturing nameplate STL owns print orientation.
