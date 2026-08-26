# Worked examples

The examples are intentionally source-first and backend-light. Each one contains a parameter YAML file, a deterministic generator, a focused README, and machine-checkable acceptance rules.

```bash
python3 ../scripts/run_examples.py --output ../../../build/examples --quality draft
python3 ../scripts/run_examples.py --output ../../../build/examples-print --quality print
```

- `barefoot-shoe` demonstrates anatomical station logic, asymmetric plan widths, rocker/toe spring, arch/camber, and a closed section loft.
- `organic-bowl` demonstrates a smooth vertical profile plus Fourier lobes and twist in a printable hollow shell.
- `rc-car-sporty-envelope` demonstrates immutable axle/mount hardpoints, a sporty body loft, and a separate smooth chassis.

The generated meshes are references, not medical, structural, food-contact, or vehicle-safety certifications.
