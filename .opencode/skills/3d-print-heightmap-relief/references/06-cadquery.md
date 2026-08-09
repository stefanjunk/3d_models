# 06 — CadQuery workflow

## Use CadQuery for the base, not dense image pixels

CadQuery and OpenCascade are excellent for parametric solids, exact dimensions, fillets, shells, holes, lids, and STEP export. A dense image relief represented as thousands of B-rep faces and Boolean features is usually the wrong representation.

Recommended architecture:

```text
CadQuery B-rep base
        ↓
STEP archive + controlled STL tessellation
        ↓
closed mesh relief patch
        ↓
mesh Boolean
        ↓
validated printable STL
```

This preserves editability of the base and avoids forcing raster complexity into the feature tree.

## Export tolerances

CadQuery STL export accepts linear and angular tessellation tolerances. Smaller values produce more triangles and higher resource use.

Choose base tessellation so:

- visible base curvature is smoother than the desired print;
- base facets are not much coarser than relief sampling;
- tolerances are not orders of magnitude smaller than printer utility.

The examples use loose draft tolerances and finer print tolerances. Keep STEP as the authoritative base.

## Complete pattern

See `templates/cadquery/parametric_base_with_mesh_relief.py`.

```python
base = build_base()
cq.exporters.export(
    base,
    "base.stl",
    tolerance=0.08,
    angularTolerance=0.12,
)
cq.exporters.export(base, "base.step")
```

Then generate and apply the patch:

```bash
python scripts/relief_patch.py config.json relief-patch.stl
python scripts/mesh_boolean.py difference base.stl relief-patch.stl \
  -o final.stl --engine auto --require-watertight
```

## Why not import STL into CadQuery and cut?

CadQuery’s documented parametric import path is centered on CAD formats such as STEP/DXF/XCAF, while STL is primarily an export mesh format. Mesh-to-B-rep conversion can create one face per triangle and make the CAD kernel fragile and slow.

Use a mesh Boolean engine for the dense final operation. If an exact B-rep relief is mandatory, simplify/vectorize the image or build a small number of analytic features.

## When a native CadQuery relief is appropriate

- text using fonts;
- SVG/DXF line art;
- a logo with tens of regions;
- a coarse dot matrix;
- a repeated analytic groove;
- low-cell pixel art.

See `templates/cadquery/coarse_native_pixel_relief.py`. It deliberately defaults to a small grid and warns against photographic input.

## Parametric dimensions and relief configuration

Keep object dimensions in one source of truth. It is easy to create a collision between an object’s depth and relief depth. This package nests relief dimensions:

```json
"surface": {
  "type": "rounded_rectangle_wall",
  "width_mm": 90,
  "depth_mm": 65,
  "height_mm": 83
},
"relief": {
  "depth_mm": 0.38,
  "overlap_mm": 0.07
}
```

Do not flatten both into one `depth_mm` namespace.

## Rounded bases

The relief surface must match the same nominal dimensions as the CadQuery outer surface:

- width;
- depth;
- corner radius;
- center;
- Z band.

If CadQuery fillets only vertical edges, the side mapping is a rounded rectangle wall. If top/bottom edges are also filleted, stop the relief band before those transitions or sample the true CAD surface.

## Cylinders

Use the exact outer radius of the CadQuery base. Export tolerance must represent the cylinder smoothly. A mismatch between cutter radius and faceted base can leave scalloped artifacts.

## Honeycomb and polygon shells

Create the base as outer prism minus inner prism. Use separate patch configs for:

- outer wall;
- inner wall;
- front ring;
- back ring.

Do not fuse touching cutter STLs by concatenation. Give all cutters to one Boolean union/difference operation.

## STEP preservation

Deliver:

- the CadQuery Python script;
- STEP base before relief;
- base STL tessellation parameters;
- height-map/config files;
- final STL.

The final dense relief generally will not be conveniently editable as a STEP feature tree. That is an acceptable separation of concerns.

## Direct B-rep face sampling

Advanced users can evaluate OpenCascade faces on a UV grid and create offset/lofted faces. Trimmed faces, singularities, stitching, self-intersection, and Boolean cost make this substantially more complex than a mesh patch. Use it only when downstream exact-surface requirements justify the engineering.

## Debugging

### Base and relief do not align

Print bounds from `validate_mesh.py`; verify centers, origin, Z band, radius, and millimetre units.

### CadQuery export appears faceted

Lower linear/angular tolerance moderately. Do not change relief image resolution first.

### Export is enormous before relief

Tessellation tolerance is too strict or the base contains unnecessary small fillets/features.

### Boolean fails

Validate base and cutter independently. Increase overlap slightly, ensure cutter is a volume, use OpenSCAD fallback, and avoid coplanar adjacent cutters.

### Organizer wall is punctured

Reduce engraving depth or increase wall thickness. Check the inner fillet approaches the outer wall near corners.

## Example bases

- `examples/01-unicorn-cylinder/cadquery/base_model.py`
- `examples/02-carbon-rounded-organizer/cadquery/base_model.py`
- `examples/03-wood-honeycomb-shelf/cadquery/base_model.py`
