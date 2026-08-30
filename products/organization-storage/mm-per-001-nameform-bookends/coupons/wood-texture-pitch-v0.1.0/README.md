# NameForm wood-texture pitch coupon v0.1.0

This is an upright, one-piece comparison coupon for transferring the proven
`wood-001` Honeycomb-shelf engraving to the NameForm front. It is a digital
draft until the exact slicer review and physical appearance gate pass.

## What to print

Use:

`exports/DRAFT-nameform-wood-texture-pitch-coupon-v0.1.0.stl`

The three fields are read from the front, with the raised `E` facing the viewer:

| Position | Candidate | Mesh pitch | Purpose |
| --- | --- | ---: | --- |
| left | A | 0.45 mm | proven-reference pitch |
| center | B | 0.50 mm | low-loss candidate |
| right | C | 0.60 mm | reduced-compute candidate |

All fields use the same physical source coordinates, 0.6 mm maximum engraving,
3.2 mm wall, 1.2 mm edge/glyph fade, and 2.0 mm raised test glyph. Only the mesh
pitch and its printer-specific build raster change.

## Print contract

- Orientation: keep the supplied `z=0` foot on the build plate. Do not rotate
  the panels flat.
- Nozzle: 0.4 mm.
- Layer height: 0.12 mm.
- Nominal line width: 0.45 mm.
- Supports: off.
- Material: reproduce the exact successful shelf material if possible. The
  repository only records PETG family; exact product, color, batch, drying, and
  flow remain operator inputs.
- Do not scale the STL.

The current slice report uses the bundled `Anycubic PETG` profile only as an
explicit provisional slicer candidate. It does not identify or qualify the
operator's exact filament.

The verified headless slice used Anycubic Slicer Next 1.3.9.4 and produced 374
layers without support, brim, or tool changes. The slicer estimate is 21.80 g
and 1 h 34 min 37 s. The exact G-code is retained as evidence, but should only
be printed after confirming that the loaded PETG matches the intended profile.

## Evaluation

Keep exposure, white balance, light direction, distance, material, and slicer
profile fixed. Inspect each field at the intended NameForm viewing distance and
at three light/view angles. Record:

1. wood-family recognition and preferred scale;
2. missing or aliased grooves;
3. visible pitch faceting;
4. glyph bond, edge cleanliness, and legibility;
5. snagging, roughness, and dirt-trapping behavior;
6. selected candidate, or rejection of all three.

The physical-print and appearance decisions remain human-controlled. A digital
mesh or render cannot pass them.

Record the result in `physical-evaluation.md`. Candidate B is the intended
default only if it is visually indistinguishable from A. Candidate C should be
selected only if its coarser sampling is still unobjectionable at the intended
NameForm viewing distance.

## Rebuild

The committed output paths are write-once. Rebuild into a new empty directory:

```bash
python source/generate_coupon.py --output-root /new/empty/output-root
```

Render a generated STL:

```bash
blender --background --python source/render_coupon.py -- \
  --input exports/DRAFT-nameform-wood-texture-pitch-coupon-v0.1.0.stl \
  --output renders/DRAFT-nameform-wood-texture-pitch-coupon-v0.1.0.png
```

The immutable source is
`../../../../../libraries/surface-textures/wood-001/master/wood-001-tile-16bit.png`;
each candidate's 16-bit build raster is retained under `build/heightmaps/`.
