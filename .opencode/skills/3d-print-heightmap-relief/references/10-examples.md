# 10 — Three complete examples

Build all draft examples:

```bash
python scripts/build_examples.py --quality draft --engine auto
```

Generate detailed bases and cutters without the expensive final Boolean:

```bash
python scripts/build_examples.py --quality print --skip-boolean
```

## Example 1: unicorn engraving around a cylindrical gift box

Directory: `examples/01-unicorn-cylinder/`

### Design

- outer radius: 40 mm;
- body height: 90 mm;
- wall: 2.4 mm;
- bottom: 2.8 mm;
- engraving band: 78 mm high, from Z=6 to Z=84;
- complete wrap width: `2π·40 ≈ 251.33 mm`;
- engraving depth: 0.8 mm;
- Boolean overlap: 0.08 mm;
- top/bottom taper: 1.5 mm.

A separate CadQuery lid has an insertion skirt and knob. The side engraving is applied only to the body.

### Image strategy

The unicorn is semantic artwork, not a material tile:

- preserve aspect ratio;
- contain/pad with black;
- keep the subject away from the full-wrap seam;
- use white as deepest engraving;
- flip V so image “up” matches positive Z.

The source image is procedural and redistributable. Replace it with any user image after applying the same checks.

### Mapping

```json
"mapping": {
  "mode": "surface_uv",
  "wrap_u": true,
  "wrap_v": false,
  "flip_v": true
},
"surface": {
  "type": "cylinder",
  "radius_mm": 40,
  "height_mm": 78,
  "z_min_mm": 6,
  "start_angle_deg": -180,
  "angle_deg": 360
}
```

U follows angle and is periodic. V follows Z.

### Quality presets

- draft image pitch: about 0.60 mm; mesh pitch: 0.90 mm;
- print image pitch: about 0.25 mm; mesh pitch: 0.30 mm.

The detailed cutter is intentionally large. Use draft to confirm seam, orientation, and depth first.

### Build manually

```bash
python examples/01-unicorn-cylinder/cadquery/base_model.py \
  --output-dir build/unicorn --quality draft

python scripts/relief_patch.py \
  examples/01-unicorn-cylinder/config/relief-draft.json \
  build/unicorn/unicorn-cutter.stl

python scripts/mesh_boolean.py difference \
  build/unicorn/gift-box-body.stl \
  build/unicorn/unicorn-cutter.stl \
  -o build/unicorn/gift-box-engraved.stl \
  --engine auto --require-watertight --require-single-body
```

### Print checks

- remaining wall after deepest cut;
- cylinder facet smoothness;
- vertical seam placed away from the unicorn;
- thin horn/legs survive toolpath generation;
- lid clearance is independent of relief.

## Example 2: carbon-fibre texture around a rounded desk organizer

Directory: `examples/02-carbon-rounded-organizer/`

### Design

- width: 90 mm;
- depth: 65 mm;
- height: 95 mm;
- corner radius: 8 mm;
- wall: 2.4 mm;
- bottom: 3.0 mm;
- relief band: 83 mm high, Z=6 to Z=89;
- rounded perimeter: about 296.27 mm;
- engraving depth: 0.38 mm;
- overlap: 0.07 mm;
- repeat count around perimeter: 3.

### Why a continuous rounded wall

Mapping front, left, back, and right separately would reset or rotate the weave. The `rounded_rectangle_wall` surface uses one perimeter arc-length coordinate and carries the texture over each 8 mm corner arc.

The source tile includes diagonal bundle ridges and alternating over/under dominance. It is periodic in both axes.

### Image strategy

One physical tile is prepared at approximately:

```text
perimeter / 3 ≈ 98.76 mm wide
83 mm high
```

The config then repeats it three times around U. This keeps the material scale explicit.

### Mapping

```json
"mapping": {
  "mode": "surface_uv",
  "repeat_u": 3,
  "wrap_u": true,
  "wrap_v": false,
  "flip_v": true
},
"surface": {
  "type": "rounded_rectangle_wall",
  "width_mm": 90,
  "depth_mm": 65,
  "corner_radius_mm": 8,
  "height_mm": 83,
  "z_min_mm": 6
}
```

Note the two different “depths”:

- `surface.depth_mm = 65` is organizer front-to-back depth;
- `relief.depth_mm = 0.38` is engraving depth.

They are intentionally nested to prevent schema collisions.

### Quality presets

- draft image pitch: about 0.45 mm; mesh pitch: 0.90 mm;
- print image pitch: about 0.20 mm; mesh pitch: 0.30 mm.

### Print checks

- corner weave continuity;
- no wall puncture near inner corner fillets;
- weave scale looks like carbon, not broad diagonal stripes;
- relief remains subtle enough for handling;
- divider and cavity remain valid after Boolean.

## Example 3: wood texture on every surface of a honeycomb wall shelf

Directory: `examples/03-wood-honeycomb-shelf/`

### Design

- regular hexagon, six sides;
- outer circumradius: 60 mm;
- inner circumradius: 51 mm;
- depth: 35 mm;
- wall thickness by radial difference: 9 mm;
- side relief band: Z=1.2 to Z=33.8;
- front/back textured ring between radii 52.2 and 58.8 mm;
- engraving depth: 0.48 mm;
- overlap: 0.08 mm.

Four surface families are generated:

1. outer polygon wall;
2. inner polygon wall;
3. front polygon ring;
4. back polygon ring.

### Why four cutters

Outer and inner walls have different normal directions. Front/back rings use planar mapping and contain six separated sector cutters. Keeping families separate prevents exact shared-edge concatenation from creating a non-manifold intermediate STL.

All cutters are supplied to one final Boolean.

### Wall grain direction

The source wood grain runs along image X. The polygon wall’s native U goes around the hexagon and V goes along shelf depth. The config swaps U/V so image X aligns with depth:

```json
"mapping": {
  "mode": "surface_uv",
  "swap_uv": true,
  "repeat_u": 1,
  "repeat_v": 2,
  "wrap_u": false,
  "wrap_v": true,
  "flip_u": true
}
```

The wrap flags are explicit after the swap. Grain direction remains consistent instead of rotating on each face.

### Front/back grain direction

Each hexagonal rim sector uses one global XY projection:

```json
"mapping": {
  "mode": "planar_axes",
  "origin": [0,0,0],
  "axis_u": [1,0,0],
  "axis_v": [0,1,0],
  "tile_width_mm": 120,
  "tile_height_mm": 45,
  "wrap_u": true,
  "wrap_v": true
}
```

Every sector samples the same world-space wood field. Grain does not reset per side.

### Edge gap

`edge_gap_mm=0.08` slightly retracts adjacent front/back sector cutters. They remain separate watertight bodies and do not share exact side walls.

### Quality presets

- draft mesh pitch: 1.50 mm;
- print mesh pitch: 0.30 mm;
- prepared wood maps: 384² draft and 768² print.

The print configs point to `wood-heightmap-print.png`; this is tested to prevent accidentally running a fine mesh with the draft image.

### Manual build

```bash
python examples/03-wood-honeycomb-shelf/cadquery/base_model.py \
  --output-dir build/honeycomb --quality draft

for part in outer-wall inner-wall front-face back-face; do
  python scripts/relief_patch.py \
    "examples/03-wood-honeycomb-shelf/config/${part}-draft.json" \
    "build/honeycomb/${part}-cutter.stl"
done

python scripts/mesh_boolean.py difference \
  build/honeycomb/honeycomb-shelf.stl \
  build/honeycomb/outer-wall-cutter.stl \
  build/honeycomb/inner-wall-cutter.stl \
  build/honeycomb/front-face-cutter.stl \
  build/honeycomb/back-face-cutter.stl \
  -o build/honeycomb/honeycomb-shelf-engraved.stl \
  --engine auto --require-watertight --require-single-body
```

### Print checks

- wood remains recognizable rather than generic roughness;
- grain direction is consistent on all six wall faces;
- front and back share an intentional global direction;
- inner-wall cutter points into the shelf wall, not across the cavity;
- mounting/connection features added later keep adequate wall;
- front/back sector gaps are not visually distracting.

## Replacing example images

Use the same physical/mapping config when the replacement has the same intended scale. Re-run preprocessing and analysis. Do not simply copy a new image over the prepared file without checking aspect, alpha, range, seam, and preferred direction.
