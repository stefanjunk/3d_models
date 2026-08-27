# Manufacturing mesh complexity decision

Decision: **not-beneficial**. The manufacturing files are direct tessellations of analytic CadQuery solids; no downstream decimation is applied.

| Part | Master triangles / MiB | Manufacturing triangles / MiB | Bounds | Decision |
|---|---:|---:|---|---|
| left rail | 1,004 / 0.048 | 716 / 0.034 | 210.0 × 20.8215 × 32.0 mm | retain direct manufacturing tessellation |
| right rail | 1,004 / 0.048 | 716 / 0.034 | 210.0 × 16.8358 × 32.0 mm | retain direct manufacturing tessellation |
| taper gauge | 5,080 / 0.242 | 2,576 / 0.123 | 107.0 × 30.0 × 3.2 mm | retain direct manufacturing tessellation |

All manufacturing meshes are below the per-part budgets of 20,000 triangles and 2 MiB. Master/manufacturing bounds match at reported precision; volume difference is below 0.001% for every part. The protected bed faces, linear taper datums, scallops and gauge notches make a further lossy step unjustified.

Exact slicer import/slice time and toolpath resolution remain `NOT_RUN`, independently of this geometric decision.
