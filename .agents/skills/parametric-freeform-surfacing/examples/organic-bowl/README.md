# Organic bowl freeform reference

This example creates a printable open vessel from a smooth vertical radius profile plus periodic Fourier lobes whose amplitude and phase vary over height.

It demonstrates a compact mathematical parameterization for bowls, vases, lamps, and decorative containers without relying on an opaque image-to-3D mesh.

The wall is a nominal radial offset, not an exact normal offset. Production food-contact, watertight, heat, cleaning, and material claims require process-specific validation.

```bash
python generate.py --parameters parameters.yaml --output build --quality print
```
