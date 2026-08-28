# Optimization plan

Baseline B0 is the selected smooth-carrier/cap batch at 0.20 mm. A process-only A candidate slices unchanged CAD at 0.28 mm; it is constrained by the requirement for at least three nominal engraving layers. Geometry-only B uses two large windows in each carrier at 0.20 mm; it is constrained by continuous sleeve-facing surfaces. Combined C slices the windowed geometry at 0.28 mm and inherits both constraints.

All four variants use the exact Kobra 3 Max 0.4 mm and Anycubic PETG profiles. Time/material are measured from temporary G-code, while support burden, warnings and layers remain gates. The 1.6 mm carrier has `NO_INFILL_CORE` under the path estimate, so infill percentage is not treated as an optimization lever.
