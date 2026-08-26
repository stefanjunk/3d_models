# Included examples

All examples are deterministic Python/NumPy generators. They demonstrate architecture and validation, not certified finished products.

## 1. Barefoot shoe

Path:

```text
examples/barefoot-shoe/
```

Pattern:

```text
semantic station parameters
→ smooth asymmetric half-width profiles
→ centerline + rocker/toe spring
→ closed cross-sections with arch/camber
→ seam-consistent loft
→ OBJ/STL + curve/mesh report
```

Key exposed parameters include length, heel/waist/ball/toe widths, toe spring, heel rise, arch height, sole thickness, lateral/medial asymmetry, and section resolution.

Build:

```bash
python3 examples/barefoot-shoe/generate.py \
  --parameters examples/barefoot-shoe/parameters.yaml \
  --output build/barefoot-shoe
```

## 2. Organic bowl

Path:

```text
examples/organic-bowl/
```

Pattern:

```text
smooth vertical radius profile
+ periodic Fourier lobe field
+ height-dependent amplitude and twist
→ outer and inner ring surfaces
→ rim and bottom closure
→ printable shell + report
```

Key parameters include height, base/belly/rim radius, wall, bottom thickness, lobe count, amplitude, twist, vertical profile tension, and mesh resolution.

## 3. RC car sporty envelope

Path:

```text
examples/rc-car-sporty-envelope/
```

Pattern:

```text
immutable axle/mount hardpoints
→ semantic longitudinal stations
→ smooth width/roof/shoulder profiles
→ body section loft
+ separate smooth chassis outline extrusion
→ hardpoint and mesh reports
```

The body and chassis are separate artifacts by design. Wheelbase and mounting coordinates are not inferred from the visual shell.

## Build all

From the skill directory:

```bash
python3 scripts/run_examples.py --output build/examples
```

Each output folder contains source parameters, OBJ/STL files, and `validation.json`.
