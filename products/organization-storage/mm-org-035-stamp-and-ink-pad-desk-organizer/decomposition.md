# Decomposition

| Component | Source of truth | Material | Interface |
|---|---|---|---|
| Square three-lane cassette | `cad/build.py` + parameters | PETG | 78 x 78 x 21 mm case envelope |
| Rectangular three-lane cassette | `cad/build.py` + parameters | PETG | 100 x 69 x 21 mm case envelope |
| Dual fit coupon | same lane/front/rear generator | PETG | one shallow mouth per envelope |
| Virtual cases | parameters | digital only | nominal maximum envelopes |
| Full and coupon plates | deterministic 3MF builder | PETG | separate first-fit/full jobs |

Functional X is case width, Y is insertion depth, and Z is vertical. Manufacturing rotates X onto printer Z so all lane sections grow as connected vertical webs.
