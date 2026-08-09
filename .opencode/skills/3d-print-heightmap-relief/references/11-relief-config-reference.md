# 11 — Relief configuration reference

The JSON Schema is `schemas/relief-config.schema.json`.

## Root object

```json
{
  "$schema": "../../../schemas/relief-config.schema.json",
  "heightmap": "../prepared/image.png",
  "mode": "engrave",
  "mesh_pitch_mm": 0.30,
  "max_grid_vertices": 3000000,
  "relief": {
    "depth_mm": 0.6,
    "overlap_mm": 0.08
  },
  "mapping": {
    "mode": "surface_uv"
  },
  "edge_taper_mm": {"v": 1.5},
  "surface": {
    "type": "cylinder",
    "radius_mm": 40,
    "height_mm": 70
  }
}
```

Use either `surface` or `surfaces`.

Paths are resolved relative to the config file.

## Root fields

| Field | Meaning |
|---|---|
| `heightmap` | Default PNG or supported image for all surfaces |
| `mode` | `emboss` or `engrave` |
| `mesh_pitch_mm` | Default target surface sampling pitch |
| `max_grid_vertices` | Guard against accidental memory explosion |
| `relief` | Depth/range/invert controls |
| `mapping` | Default image mapping |
| `edge_taper_mm` | Optional boundary fade |
| `surface` | One surface spec |
| `surfaces` | List of surface specs |

A surface can override height map, mode, pitch, mapping, relief, and taper.

## Relief object

```json
"relief": {
  "depth_mm": 0.8,
  "overlap_mm": 0.08,
  "invert": false,
  "input_min": 0.0,
  "input_max": 1.0,
  "output_min": 0.0,
  "output_max": 1.0
}
```

- `depth_mm`: maximum displacement/cut.
- `overlap_mm`: penetration across nominal surface.
- `invert`: use `1-h`.
- `input_min/max`: clip/remap sampled values.
- `output_min/max`: restrict final normalized height.

For example, `output_min=0.2` creates a minimum relief level everywhere. Use cautiously for engraving because it cuts the full mapped rectangle.

## Mapping object

### Native surface UV

```json
"mapping": {
  "mode": "surface_uv",
  "swap_uv": false,
  "rotate_quarter_turns": 0,
  "flip_u": false,
  "flip_v": true,
  "repeat_u": 1,
  "repeat_v": 1,
  "offset_u": 0,
  "offset_v": 0,
  "wrap_u": true,
  "wrap_v": false,
  "interpolation_order": 1
}
```

Transform order is swap, quarter rotation, flip, repeat/offset, wrap/clamp.

### Planar axes

```json
"mapping": {
  "mode": "planar_axes",
  "origin": [0,0,0],
  "axis_u": [1,0,0],
  "axis_v": [0,1,0],
  "tile_width_mm": 100,
  "tile_height_mm": 50,
  "wrap_u": true,
  "wrap_v": true
}
```

Axes are normalized. Tile dimensions set the physical period.

### Interpolation

- `0`: nearest; binary/pixel art.
- `1`: linear; default and memory-efficient.
- `3`: cubic; smoother but may blur or overshoot before clipping.

## Edge taper

Number:

```json
"edge_taper_mm": 1.5
```

applies to nonperiodic U and V boundaries.

Per-axis:

```json
"edge_taper_mm": {"u": 0, "v": 1.5}
```

Periodic axes are not tapered.

## Surface types

### Plane

```json
{
  "type": "plane",
  "width_mm": 100,
  "height_mm": 60,
  "origin": [0,0,3],
  "axis_u": [1,0,0],
  "axis_v": [0,1,0],
  "normal_sign": 1
}
```

### Cylinder

```json
{
  "type": "cylinder",
  "radius_mm": 40,
  "height_mm": 78,
  "z_min_mm": 6,
  "center_xy": [0,0],
  "start_angle_deg": -180,
  "angle_deg": 360,
  "normal_sign": 1
}
```

A 360° span defaults to periodic U.

### Cone/frustum

```json
{
  "type": "cone",
  "radius_bottom_mm": 40,
  "radius_top_mm": 30,
  "height_mm": 70,
  "z_min_mm": 0,
  "angle_deg": 360
}
```

Aliases `radius0_mm` and `radius1_mm` are accepted.

### Rounded rectangular wall

```json
{
  "type": "rounded_rectangle_wall",
  "width_mm": 90,
  "depth_mm": 65,
  "corner_radius_mm": 8,
  "height_mm": 83,
  "z_min_mm": 6,
  "center_xy": [0,0],
  "start_offset_mm": 0
}
```

`depth_mm` here is object front-to-back dimension. Relief depth remains nested in `relief`.

### Polygon wall

Regular:

```json
{
  "type": "polygon_wall",
  "sides": 6,
  "radius_mm": 60,
  "start_angle_deg": 30,
  "height_mm": 35,
  "z_min_mm": 0,
  "normal_sign": 1
}
```

Custom:

```json
{
  "type": "polygon_wall",
  "points": [[-20,-10],[20,-10],[25,5],[0,20],[-25,5]],
  "height_mm": 30
}
```

Points are corrected to counterclockwise order internally.

### Sphere band

```json
{
  "type": "sphere",
  "radius_mm": 30,
  "center": [0,0,0],
  "longitude_start_deg": -180,
  "longitude_span_deg": 360,
  "latitude_min_deg": -70,
  "latitude_max_deg": 70
}
```

Avoid exact poles for this regular grid.

### Torus

```json
{
  "type": "torus",
  "major_radius_mm": 30,
  "minor_radius_mm": 8,
  "major_angle_deg": 360,
  "minor_angle_deg": 360,
  "center": [0,0,0]
}
```

Full spans are periodic.

### Polygon ring plane

```json
{
  "type": "polygon_ring_plane",
  "sides": 6,
  "outer_radius_mm": 58.8,
  "inner_radius_mm": 52.2,
  "start_angle_deg": 30,
  "z_mm": 0,
  "normal_sign": -1,
  "edge_gap_mm": 0.08
}
```

Custom `outer_points` and `inner_points` are supported and must have equal counts. Each side sector becomes a separate closed body.

### Arbitrary grid NPZ

```json
{
  "type": "grid_npz",
  "npz": "surface-grid.npz",
  "periodic_u": false,
  "periodic_v": false,
  "u_length_mm": 120,
  "v_length_mm": 60,
  "normal_sign": 1
}
```

NPZ:

- required `positions`: `(Nv,Nu,3)`;
- optional `normals`: same shape;
- optional scalar `periodic_u`, `periodic_v`, `u_length_mm`, `v_length_mm`.

Config values override NPZ metadata.

## Multiple surfaces

```json
{
  "heightmap": "texture.png",
  "mode": "engrave",
  "mesh_pitch_mm": 0.4,
  "relief": {"depth_mm": 0.5, "overlap_mm": 0.08},
  "surfaces": [
    {
      "type": "plane",
      "width_mm": 50,
      "height_mm": 30,
      "origin": [0,0,0]
    },
    {
      "type": "plane",
      "width_mm": 50,
      "height_mm": 30,
      "origin": [0,0,20],
      "normal_sign": -1,
      "mapping": {"mode": "planar_axes", "origin":[0,0,0],
                  "axis_u":[1,0,0], "axis_v":[0,1,0],
                  "tile_width_mm":50, "tile_height_mm":30}
    }
  ]
}
```

The output concatenates closed bodies. Touching/coincident bodies may not form one manifold shell; use them as separate Boolean tools.

## Memory guard

`max_grid_vertices` counts the sum of sampled *surface* points before top/bottom duplication. The final closed mesh has approximately twice that many vertices plus faces and temporary Boolean structures.

Raise the guard only after running `analyze_heightmap.py`.

## Normal sign

`normal_sign` multiplies the generated normal:

- `+1`: generator’s default outward direction;
- `-1`: opposite side.

For inner cavities and front/back faces, sign is often the most important field. Test with a constant white image.

## Schema limits

JSON Schema checks types, required keys, and common structure. Runtime validation additionally checks geometric relationships such as positive dimensions, corner radius, polygon edge lengths, input range order, and grid memory.
