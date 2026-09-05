# Manufacturing-mesh optimization decision — MM-DEC-003 v0.2.0

Decision: **not applied to the selected Step1X body**.

The owner explicitly rejected model repair and parametric reconstruction. The selected run-004 body therefore remains at the full Step1X output resolution after uniform millimetre registration. The only generated parametric geometry is the 80 × 6 mm foot disc. Boolean union is necessary to make the confirmed foot part of the single printable solid; it is not an optimization of the flower body.

The final candidate has 396,316 triangles and is 18.898 MiB, both within the declared 500,000-triangle and 25 MiB budgets. Anycubic Slicer Next accepted it with exact profiles, so there is no demonstrated need to simplify it in this phase.

The run-001 tolerance study is retained solely as rejected historical evidence. Its 0.025 mm simplification had passed numeric and visual checks, while 0.05 mm showed visible faceting; however, run 001 used a planar body operation the owner later disallowed. Neither variant is the selected product.

Manufacturing tuning was confined to the slicer profile. Automatic build-plate-only tree support was enabled after the support-free slice reported floating regions, and support speed was reduced from 100 to 80 mm/s after the analyzer exceeded the existing 13.3 mm³/s limit. The selected slice then passed at 12.507 mm³/s without native warnings.

Physical print appearance and support removal have not been tested, so this decision does not authorize commercial release.
