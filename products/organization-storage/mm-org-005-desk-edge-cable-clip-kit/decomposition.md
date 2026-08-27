# Product decomposition — MM-ORG-005

## Authority

- `config/model-parameters.json` owns all dimensions and supported input ranges.
- `cad/build.py` owns clamp, flexure, hard stop, C-ring, slit, contact lips, labels and exports.
- The SVG is an approval image only and never drives geometry.
- No purchased part, external mesh, adhesive, magnet, font or image-derived surface is used.

## Printed parts

1. Thin: 12 mm target desk / 3.5 mm cable.
2. Standard: 15 mm target desk / 5.0 mm cable.
3. Thick: 18 mm target desk / 7.0 mm cable.
4. Fit coupons: the same three cross-sections at 4 mm width to test desk gap, cable slot and print behavior with little material.

## Interfaces

- Desk interface: fixed upper arm plus tapered lower leaf; a rounded 0.6 mm tip pad creates provisional interference.
- Cable interface: bore radius equals half the cable diameter plus 0.35 mm; the entry slit is 70% of nominal cable diameter.
- Print datum: full XZ side face; the clip width becomes the build direction so the flexure outline is continuous within each layer.

The one-piece body is authoritative. Optional TPU pads are deliberately deferred until the PETG-only contact pressure and marking tests are known.
