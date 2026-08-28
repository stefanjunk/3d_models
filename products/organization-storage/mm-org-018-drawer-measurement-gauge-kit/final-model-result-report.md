# MM-ORG-018 final digital model result

Revision `0.1.0-draft.1` is a fully parametric and slicer-preflighted draft print candidate. Physical calibration and ten-drawer comparison remain open, so this is not a validated measurement instrument or production release.

## Deliverables

| Artifact | Bounds mm | Triangles | SHA-256 |
| --- | --- | ---: | --- |
| R2 tile | 30 × 30 × 3 | 544 | `dfa86ea6360675746beb36131d3644585eb62ae5e66057ec12fc4991e1e485b9` |
| R4 tile | 30 × 30 × 3 | 968 | `14ab7a444097d09e2bb169091eb53e2f74fafa77ee74ab59dc749b3042daea49` |
| R6 tile | 30 × 30 × 3 | 1,392 | `96fe11422dc13725dbacbed85cf042079c92644a43622a3f5946a7817c44c8aa` |
| R8 tile | 30 × 30 × 3 | 1,816 | `f2ae7745dec75342c6be41460cf99f82a58a464774f291580fc59887b02a251f` |
| R10 tile | 30 × 30 × 3 | 2,240 | `4519f7ad269c9de027f578c3ec833253d8bddc2ea69a7674246f239de7dffbf2` |
| R12 tile | 30 × 30 × 3 | 2,664 | `894bc17379e4629ffe779c46ed0b178b7c0eb5916b058a5f54715dbb1c6a485c` |
| Height card | 30 × 65 × 3 | 2,612 | `cd3218ddb09a7fd0070510674bf08f5d4d9e2e0f095e3b7cfabd6fc25272d00d` |
| Clearance comb | 100 × 40 × 3 | 3,524 | `0c9c2e513ae27a78efd55de7540da1f8d191df66d8a6b2bf860f0a82453eb220` |
| Calibration frame | 130 × 32 × 3 | 1,340 | `058176ab5bc15d610b7586421266e072a8d990ae586ee8b1fe0bd731224ac7b9` |
| Ten-object 3MF | six tiles, two cards, comb, frame | 10 watertight objects | `fc4d0838c5d62b976aecda529ccfa885651317c48014536d28070af1ef4d5d8f` |

All nine STL files are independently watertight positive-volume single components with consistent winding and zero boundary/nonmanifold/degenerate/duplicate faces. Editable STEP masters and a virtual kit STEP are in `exports/master/`.

## Digital evidence

- Twelve deterministic parameter, geometry and semantic tests: PASS.
- Radius, height, clearance and calibration interface contracts: PASS.
- 3MF: ten watertight millimetre objects, including two height-card instances: PASS.
- Exact Anycubic Slicer Next 1.3.9.4 / Kobra 3 Max / 0.4 mm / 0.20 mm Standard / Anycubic PLA: 15 layers, 4,641 s estimate, 26,511.16 mm³ extrusion, 11,022.06 mm positive extrusion, 17.283 mm³/s peak flow, one tool and no native object warnings.
- CAD volume reduction versus solid ten-object envelopes: 32.867%.
- Radius selection direction is parameter-bound and captured as E0 `EXP-00014`; no production learning rule was promoted.

## Deferred gate

The printed kit still needs frame and gauge calibration, radius seating, paired-card stability, comb cycle tests and independent measurement on ten real drawers. The draft target of ≤1.0 mm mean absolute user error is only a future acceptance criterion. No precision, calibrated, certified, exact-fit or remake-reduction claim is authorized. Temporary G-code was deleted and no printer action was performed.
