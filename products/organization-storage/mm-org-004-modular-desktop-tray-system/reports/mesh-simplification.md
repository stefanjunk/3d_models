# Manufacturing mesh decision

Decision: `not-beneficial`.

The source is analytic CadQuery B-Rep and each tray manufacturing mesh has 8,284 triangles at 0.05 mm chordal and 0.15 rad angular tolerance. The connector has 620 triangles and the coupon 76. All parts are far below the 150,000-triangle and 12 MiB budgets, so global decimation would add dimensional risk at the dovetail interface without a meaningful workflow benefit.

STEP remains the native neutral master. STL is a manufacturing export only. No mesh was used as an editable master and no lossy simplification was applied.
