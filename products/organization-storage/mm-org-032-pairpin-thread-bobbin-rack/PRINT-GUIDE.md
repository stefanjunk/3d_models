# Print guide

1. Print both four-pin gauges first, base down and without supports. Test clean, empty spool and bobbin bores from smallest to largest pin; select the largest pin that inserts/removes repeatedly without force, whitening or spreading.
2. Confirm every stored spool is ≤45 mm diameter and ≤60 mm tall and every bobbin is ≤22 mm diameter and ≤12.5 mm tall. Confirm the bobbin type is correct for the sewing machine separately.
3. Set selected diameters in both `fit` and `rack`, rebuild, and rerun digital gates. Never scale the STL in the slicer.
4. Reference setup: Anycubic Kobra 3 Max, 0.4 mm nozzle, PLA and the layer height selected in `validation/optimization-report.json`; use at least three perimeters and four top/bottom layers, supports disabled.
5. After printing, inspect every post, tip, collar and adjacent base transition under bright raking light and with loose sacrificial thread. Deburr without cutting a notch; reject any surface that catches fibers.
6. Load by aligned X column: spool and matching bobbin share the same column centerline. Use only removable paper/adhesive labels on the four declared front datums.
7. Complete `tests/physical-test-plan.md` before relying on the rack. No G-code is supplied or retained.
