# MM-ORG-017 modular pocket-emptying tray

Fully parametric three-style tray family derived from SKU-173. Every module shares a shallow rear-to-front coin ramp, low rounded sweep mouth and integral planar connector. `Soft Arc`, `Clean Facet` and `Utility Rib` change only the exterior style; the functional interface is common.

## Primary files

- Edit `config/model-parameters.json`.
- Regenerate STEP, STL, 3MF and source reports with `python cad/build.py`.
- Run the eleven deterministic parameter/geometry tests with `python -m pytest -q tests/test_parameters.py`.
- Render the current candidate with `python cad/render_preview.py`.
- Print and qualify `connector-clearance-gauge` plus `connector-test-key` before connecting full modules.
- Use `exports/3mf/DRAFT-MM-ORG-017-modular-pocket-emptying-tray-0.1.0-draft.1.3mf` for the exact five-object reference build, or select individual STL files.

## Digital candidate status

- Three modules: each 60 × 76 × 22 mm including its right tab; connected pitch 56 mm and three-module envelope 172 × 76 × 22 mm.
- Coin path: 4.978° rear-to-front slope, 32 mm rounded mouth and 0.6 mm lip above the front floor.
- Connector: 4 mm depth, 6 mm neck, 10 mm head, 2.4 mm height and 0.25 mm default offset.
- Coupon: 0.15/0.25/0.35 mm sockets identified by one/two/three holes plus one nominal test key.
- Five independent watertight single-component meshes and five-object millimetre 3MF: PASS.
- Exact Anycubic Slicer Next preflight: PASS, 110 layers, 9,174 s estimate, one tool and no native object warnings.
- Aggregate draft validation and hash-bound approvals through print candidate: PASS.

All outputs remain `DRAFT`. Hard printed plastic is not qualified as scratch-safe for phones, watches, coated objects or furniture. Connector feel, coin-sweep ergonomics, lift retention, stability, abrasion and cycle life remain deliberately deferred to the user's physical validation. No G-code is retained and no printer action is part of this project.
