# Manufacturing mesh decision

Decision: `not-beneficial`.

The generated production meshes contain about 1,000–2,700 triangles per part and remain below the 180,000-triangle and 15 MiB budgets. Global decimation would risk hinge-bore clearance, detent pockets, pin geometry and phone-contact edges without a meaningful workflow benefit. STEP remains the neutral master and STL is tessellated directly at 0.05 mm chordal tolerance.
