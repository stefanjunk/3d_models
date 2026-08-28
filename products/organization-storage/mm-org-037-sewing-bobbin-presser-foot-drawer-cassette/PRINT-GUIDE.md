# Print guide

1. Measure the usable drawer floor and closed height. The cassette needs a flat `210 x 150 mm` footprint, `28 mm` product height, and practical finger and drawer-motion clearance.
2. Print `exports/3mf/DRAFT-MM-ORG-037-fit-gauges-0.1.0-draft.1.3mf` first. It contains the two-diameter bobbin gauge, the 30 / 35 / 40 mm presser-foot width gauge, and the separate Full identity coupon.
3. Test the actual bobbins face-up in both shallow gauge pockets. Select the smallest pocket that accepts them without force and still permits removal. Do not assume that a machine brand identifies the bobbin geometry.
4. Place representative presser feet in the width gauge. They must enter and leave without forcing, snagging thread paths, or trapping protruding levers. The final cells are generic open storage, not retaining clips.
5. Check the Full identity coupon for complete, readable text and clean recesses. This is a physical process gate.
6. Choose one full kit: `exports/3mf/DRAFT-MM-ORG-037-stitchcell-cb-kit-0.1.0-draft.1.3mf` for the `20.5 mm` target or `exports/3mf/DRAFT-MM-ORG-037-stitchcell-horizontal-kit-0.1.0-draft.1.3mf` for the `21.6 mm` target.
7. Preview the chosen exact G-code for layers, first-layer placement, seam, tool assignment, and support state. The validated process prints the cassette and insert base-down with generated supports disabled.
8. After cooling, place the insert in the rear bay. It must seat without force, remain removable, and stay put through at least 100 normal drawer cycles. Stop if edges snag thread, any foot rocks into a neighboring cell, or the drawer contacts the cassette.

Exact PLA planning evidence:

- Gauge plate: `3,784 s` (`1 h 03 min 04 s`), approximately `28.8 g`, G-code SHA-256 `72733d2d19a844e24f409ebf9a7720af05b69a83f33a19b1e5115811d5335db1`.
- CB kit: `21,702 s` (`6 h 01 min 42 s`), approximately `189.5 g`, G-code SHA-256 `a2044afbacebc2dcb0c2f6cd6c5158fed0d1638a624d8489e82f780b62fc2e61`.
- Horizontal kit: `21,702 s` (`6 h 01 min 42 s`), approximately `189.4 g`, G-code SHA-256 `f9a8f504affa58333c9a7975ca99addb8f4a4a0871c30f1903dad52770a07965`.

The two full kits are alternatives; do not add their material totals. Supplied G-code is local validation evidence, not authorization to upload or start a printer.
