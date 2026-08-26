# Barefoot shoe freeform reference

This example builds a closed parametric sole/envelope from semantic stations rather than extruding one polygon.

The generator uses:

- asymmetric medial/lateral B-spline-like width profiles;
- a curved centerline;
- heel rise and toe spring;
- cross camber and a localized medial arch;
- registered closed sections and a deterministic loft.

It is a geometry reference, not a medical fit model or certified footwear design. A production shoe requires measured foot/last data, gait and flex-zone decisions, material/cycle testing, outsole traction, textile attachment, and physical fit trials.

```bash
python generate.py --parameters parameters.yaml --output build --quality print
```
