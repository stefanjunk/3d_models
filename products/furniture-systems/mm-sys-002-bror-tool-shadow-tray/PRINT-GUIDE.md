# Provisional print guide

- PETG or PLA prototype
- 0.4 mm nozzle, 0.20 mm layers, 0.45 mm nominal line width
- at least 3 perimeters; the 2.70 mm modeled perimeter permits six nominal lines
- tray recessed floor and gauge bases on the bed
- no supports intended

Measure the exact drawer at front/middle/rear and record its revision. Print the 215.30 mm gauge first, then nominal/high only if insertion remains free and does not mark the furniture or affect closure. Update the JSON envelope; never scale an STL to force furniture fit.

Before the full tray, measure the actual hammer, screwdriver, wrench and sockets. Tool recesses are conceptual. Add required process clearance to the JSON features and regenerate. Reject any layout with thin bridges, sharp exposed edges, tool interference or insufficient finger access.

Exact slicing, G-code inspection, point-load behavior, cleaning and removal-cycle evidence remain open.
