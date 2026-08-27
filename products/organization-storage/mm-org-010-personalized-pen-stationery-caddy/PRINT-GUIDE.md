# DRAFT print guide

This is a digital print candidate, not a validated release.

1. Edit only `config/model-parameters.json`; run `pytest -q tests/test_parameters.py` and then `python cad/build.py`.
2. Print the two coupon STLs first using the exact production filament, nozzle, layer height and orientation. Do not scale either part.
3. The retained local preflight uses Anycubic Slicer Next 1.3.9.4 with the bundled Kobra 3 Max 0.4 mm nozzle, 0.20 mm Standard and Anycubic PLA profiles. It generated 640 layers, one tool, a 7 h 06 min estimate and 191,527 mm3 extrusion volume. Treat these as reference-profile evidence, not as permission to print with an unconfirmed machine or filament batch. Apply first-layer/elephant-foot compensation in the calibrated slicer profile rather than changing the CAD interface.
4. Print the chassis with its continuous base on the bed. Print the nameplate flat with engraving upward. A brim is optional for the tall chassis if the exact printer needs it.
5. Inspect the coupon for free insertion, no rattle severe enough to escape the guides, readable `M8`, and intact retention lips. Adjust `channel_clearance` in 0.05 mm steps if required, rebuild, and keep the coupon paired with the exact process record.
6. Slide the final plate downward from the open top. Do not force a binding plate.

Before release, complete the physical plan for phone stability, asymmetric tall-item loading, edge feel and 250 plate cycles. The watermark is intentionally absent from DRAFT outputs. The retained G-code hash is evidence only; regenerate G-code after confirming the actual machine and material.
