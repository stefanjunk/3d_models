# Manufacturing mesh decision

Decision: `not-beneficial`.

The analytic CadQuery source generates each clip at roughly 1,200 triangles and each coupon at the same order of magnitude, far below the 80,000-triangle / 8 MiB budgets. Global decimation could alter the cable bore, entry noses and tapered flexure while providing no relevant import or slicing benefit. STEP is the neutral master; STL is a direct process-scale tessellation at 0.04 mm chordal tolerance.
