# Manufacturing mesh decision

Decision: `not-beneficial`.

The analytic CadQuery bar has about 3,800 triangles; each TPU insert has roughly 650 and the coupon socket about 1,200. These are well below the 120,000-triangle and 10 MiB budgets. Global decimation would risk pocket clearances, retention ribs and cable-contact noses without a measurable workflow benefit. STEP remains the neutral master and STL is directly tessellated at 0.05 mm chordal tolerance.
