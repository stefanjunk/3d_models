# MM-ORG-018 drawer measurement gauge kit

Fully parametric metric measurement-aid kit derived from SKU-115. It coordinates six analytic corner-radius tiles, two identical multi-height ruler supports, a seven-width clearance comb and an independent calibration frame.

## Primary files

- Edit `config/model-parameters.json`.
- Regenerate STEP, STL, 3MF and source reports with `python cad/build.py`.
- Run the twelve deterministic geometry/semantic tests with `python -m pytest -q tests/test_parameters.py`.
- Render the current set with `python cad/render_preview.py`.
- Use `exports/3mf/DRAFT-MM-ORG-018-drawer-measurement-gauge-kit-0.1.0-draft.1.3mf` for the exact ten-object reference build.
- Measure the calibration frame and all used gauge surfaces with independent calipers before recording a drawer.

## Digital candidate status

- Radius tiles: R2/R4/R6/R8/R10/R12, 30 × 30 × 3 mm, identified by one through six holes.
- Height cards: 30 × 65 × 3 mm, ledge tops at 15/35/55 mm, two 3MF instances.
- Clearance comb: 100 × 40 × 3 mm, nominal fingers 0.8–2.0 mm in 0.2 mm steps.
- Calibration frame: 130 × 32 × 3 mm with 80 × 12 mm window and 10 mm round/square references.
- Nine unique meshes and ten-object 3MF: watertight single components and millimetre units.
- Exact Anycubic Slicer Next preflight: PASS, 15 layers, 4,641 s estimate, one tool and no native object warnings.

All outputs remain `DRAFT`. The kit is not calibrated, certified or metrology-grade. A 0.2 mm nominal step is not a 0.2 mm accuracy claim. Exact printed dimensions, radius seating, height-card stability, comb durability and ten-drawer user error remain deliberately deferred.
