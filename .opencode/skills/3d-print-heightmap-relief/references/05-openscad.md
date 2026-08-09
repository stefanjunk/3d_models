# 05 — OpenSCAD workflow

## Strengths

OpenSCAD is useful for:

- parametric constructive solid geometry;
- a native flat height-map `surface()` primitive;
- reproducible command-line rendering;
- robust fallback Booleans on imported watertight STL patches;
- simple packaging without a GUI dependency.

It is less suitable for dense curved image mapping written entirely in SCAD. Generate a curved relief patch externally and import it.

## Native `surface()`

The OpenSCAD surface module accepts a text data file or PNG image. For image input it interprets luminance and scales heights to a nominal 0–100 range. PNG alpha is ignored. The native extent follows image pixel dimensions, so scale X, Y, and Z explicitly.

Use:

```scad
scale([
    physical_width_mm / image_width_px,
    physical_height_mm / image_height_px,
    depth_mm / 100
])
surface(file="heightmap.png", center=false, invert=false, convexity=20);
```

See `templates/openscad/flat_surface_emboss.scad`.

### Important native behavior

- only PNG is supported for image height maps;
- RGB luminance is used;
- alpha is ignored;
- `invert` changes image height direction;
- data-file and image surfaces differ in base behavior;
- surface dimensions are tied to raster dimensions;
- high `convexity` helps preview but does not change final geometry.

Preprocess color and alpha yourself for predictable results.

## Flat emboss

Place the height solid so its base overlaps the top of the plate slightly, then union:

```scad
union() {
    base();
    translate([x0, y0, top_z - overlap])
        height_solid(depth + overlap);
}
```

## Flat engraving

Mirror the height solid downward from slightly above the surface, then subtract:

```scad
difference() {
    base();
    translate([x0, y0, top_z + overlap])
        mirror([0,0,1])
            height_solid(depth + overlap);
}
```

Do not rely on perfectly coplanar contact.

## Curved and multi-face relief

Recommended sequence:

```bash
python scripts/prepare_heightmap.py ...
python scripts/relief_patch.py config.json relief-patch.stl
openscad -o final.stl templates/openscad/imported_patch_boolean.scad
```

Or:

```bash
python scripts/mesh_boolean.py difference base.stl relief-patch.stl \
  -o final.stl --engine openscad
```

The external generator handles cylindrical normals, periodic topology, rounded corner arcs, edge taper, and closed skins. OpenSCAD only performs the final CSG operation.

## Mesh import and Boolean

```scad
render(convexity=20)
difference() {
    import("base.stl", convexity=20);
    union() {
        import("outer-wall-cutter.stl", convexity=20);
        import("inner-wall-cutter.stl", convexity=20);
    }
}
```

Use `render()` for final mesh output. Preview success does not prove manifold output.

## Resolution and memory

OpenSCAD’s Boolean workload depends on triangle count and intersections. Avoid:

- converting every source pixel into SCAD source code;
- excessive `$fn` on the base unrelated to visible curvature;
- a relief mesh pitch far below printer utility;
- many coplanar patches;
- repeated `render()` inside nested modules.

Use draft pitch for design iteration and a detailed pitch only after mapping and image content are correct.

The base cylinder tessellation must still be fine enough relative to relief pitch. If the base is much coarser, the final engraved side will remain visibly faceted.

## DAT versus PNG

Use DAT when:

- numeric height must be preserved outside image luminance rules;
- negative values or a custom range are needed;
- the grid is already generated numerically.

Use PNG when:

- the image workflow is convenient;
- normalized 0–100 mapping is acceptable;
- alpha has been flattened.

`prepare_heightmap.py` can emit `--dat-output` and `--scad-output` in addition to PNG.

## Direct cylindrical polyhedra

It is possible to create arrays of vertices and faces in SCAD, but large arrays are slow to parse and consume memory. The bundled Python patch generator is the preferred implementation. Keep SCAD for parametric base dimensions and Boolean composition.

## Troubleshooting

### Height is 100 times too large

Scale Z by `depth_mm / 100` for image `surface()`.

### Image is mirrored or upside down

Use the asymmetric mapping image. Check image row direction, `invert`, mirror, and placement independently.

### Alpha background becomes geometry

Flatten alpha during preprocessing; native `surface()` ignores it.

### Boolean produces no change

Confirm the cutter crosses the surface by `overlap_mm`, the normal points correctly, and both imported meshes occupy the same coordinate system.

### Export is empty or non-manifold

Validate inputs first. Remove coincident shells, increase overlap slightly, split independent cutters, and render to STL rather than judging only F5 preview.

### Process runs out of memory

Increase relief mesh pitch, reduce base facets, crop the patch, or Boolean surface families sequentially. Do not merely downscale the preview while leaving final geometry unchanged.

## Relevant files

- `templates/openscad/flat_surface_emboss.scad`
- `templates/openscad/imported_patch_boolean.scad`
- each example’s `openscad/apply_relief.scad`
- `scripts/mesh_boolean.py`
