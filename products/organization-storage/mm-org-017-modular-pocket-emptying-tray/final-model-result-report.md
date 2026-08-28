# MM-ORG-017 final digital model result

Revision `0.1.0-draft.1` is a fully parametric, regenerated and slicer-preflighted draft print candidate. The user-deferred physical gate remains open, so this is not a validated production release.

## Deliverables

| Artifact | Bounds (mm) | Topology | SHA-256 |
| --- | --- | --- | --- |
| Soft Arc module STL | 60 × 76 × 22 | 1 watertight positive-volume component; 1,236 triangles | `8ff8205629e39789d61caae14987899d25ad95cf5232057f69f4f0c7f321b1b6` |
| Clean Facet module STL | 60 × 76 × 22 | 1 watertight positive-volume component; 524 triangles | `75bb28c079fc69dd9c2faab850ad18a694f4f3e3a36429a0f0bab011237c1ef4` |
| Utility Rib module STL | 60 × 76 × 22 | 1 watertight positive-volume component; 1,236 triangles | `5a18f6568cb109005f8a7dc4e61ff52ac2a30f784d981642201f6b164b267aeb` |
| Connector gauge STL | 64 × 42 × 2.4 | 1 watertight positive-volume component; 2,612 triangles | `4b0681bfd76467414939b03462437beccc40f690d017377a6fa14d963f634ba6` |
| Connector key STL | 20 × 12 × 2.4 | 1 watertight positive-volume component; 28 triangles | `22abf13bf25fafda5ded5ec36164145d7eb3b30f800e7572be61813d67b78ee0` |
| Five-object 3MF | three modules plus gauge/key | 5 watertight objects; millimetre units | `d2ac4dea29019a45b42d3265d479b74df507bc5f7c7fac7688f964adc6cb3ff7` |

Editable STEP masters for every object and the connected virtual set are in `exports/master/`. `config/model-parameters.json` and `cad/build.py` are the authoritative source.

## Functional result

- Three exterior styles share one protected 56 mm pitch, coin path, mouth and connector system.
- The connected three-module envelope is 172 × 76 × 22 mm, below the 180 × 160 × 45 mm portfolio limit.
- The floor drops toward the front at 4.978° and reaches a 32 mm mouth with 4 mm lower radii and only 0.6 mm retaining lip above the floor.
- The integral connector is 4 mm deep, 6 mm wide at the neck, 10 mm at the head and 2.4 mm high; production offset is 0.25 mm.
- One/two/three-hole coupon sockets expose 0.15/0.25/0.35 mm offsets with a matching nominal key.
- Hollow tray geometry reduces three-module CAD volume 72.578% versus solid envelope blocks.

## Digital evidence

- Eleven parameter, envelope, slope, connector and single-solid tests: PASS.
- Parametric-source, mesh-generation and interface reports: PASS.
- Five independent mesh audits: watertight, positive volume, consistent winding, one component, zero boundary/nonmanifold/degenerate/duplicate faces and within bed/triangle/file budgets.
- 3MF structure: PASS with five build objects and millimetre units.
- Exact Anycubic Slicer Next 1.3.9.4 preflight using Kobra 3 Max / 0.4 mm / 0.20 mm Standard / Anycubic PLA: PASS, 110 layers, 9,174 s estimate, 55,138.09 mm³ extrusion volume, 22,923.75 mm positive extrusion, 15.458 mm³/s peak flow, one tool and no native object warnings.
- Hash-bound approvals through print candidate and aggregate draft project validation: PASS.
- The corrected open-edge coupon topology is recorded as project trace plus E0 candidate `EXP-00013`; the learning store validates with no promotion.

## Deferred gate

The coupon and modules still require dimensional fit, insertion/removal, 500 connector-cycle, mixed-euro-coin sweep, lift, rocking, abrasion, heat-load, drop and 1,000 use-cycle checks. Bare hard PLA has no scratch-safe claim. Final watermarking and commercial release remain blocked. Temporary G-code was deleted after analysis; no printer upload or print-start action was performed.
