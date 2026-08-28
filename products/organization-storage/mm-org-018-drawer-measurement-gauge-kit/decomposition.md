# Product decomposition

| Component | Source of truth | Measurement interface | Manufacturing output |
| --- | --- | --- | --- |
| R2/R4/R6/R8/R10/R12 tiles | JSON radius series + analytic tangent arc | Protected lower-left external radius; one-to-six identity holes | six STEP + six STL |
| Height card | JSON 15/35/55 mm levels + analytic boxes | y = 0 floor datum and three ledge top faces; print quantity two | STEP + STL, two 3MF instances |
| Clearance comb | JSON finger widths/centers | seven left-to-right no-force gap probes | STEP + STL |
| Calibration frame | JSON external/internal references | caliper-accessible outer, window, circle, square and thickness surfaces | STEP + STL |
| Virtual kit | positioned component compound | visual/registration reference only | STEP |
| Print build set | unique meshes plus second height-card instance | ten independent millimetre objects | 3MF |
| Worksheet/test plan | Markdown records | raw readings, signed tool error, uncertainty and ten-drawer comparison | documentation |

No purchased parts, external fonts, logos, meshes, images-to-geometry or moving joints are required. JSON plus `cad/build.py` is authoritative; STEP is editable interchange and STL/3MF are manufacturing derivatives.
