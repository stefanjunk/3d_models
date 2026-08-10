# OpenSCAD route

Use OpenSCAD for dimension-driven reconstruction from clean profiles, repeated primitives, revolved forms, simple relief, and robust parameter variation. Do not choose it as the primary tool for sculpting an organic single-image mesh or editing millions of scan triangles.

## Contents

1. [Route image evidence into OpenSCAD](#route-image-evidence-into-openscad)
2. [Parameter architecture](#parameter-architecture)
3. [Resolution and performance](#resolution-and-performance)
4. [Color and texture](#color-and-texture)
5. [Validation](#validation)

## Route image evidence into OpenSCAD

### Silhouette or section

1. Segment the object.
2. Trace the required contour in Inkscape or another vector tool.
3. Simplify the path within a declared physical error.
4. Export SVG/DXF with known units.
5. Import the 2D profile and extrude, revolve, offset, or Boolean it.

```scad
profile_file = "profile.svg";
depth_mm = 18;

linear_extrude(height = depth_mm, center = true, convexity = 10)
    import(profile_file, convexity = 10);
```

For a rotational object, trace only one side of the radius-versus-height profile and close it to the axis:

```scad
$fa = 3;
$fs = 0.35;

rotate_extrude(convexity = 10)
    import("half_profile.svg", convexity = 10);
```

Confirm the source profile orientation and distance from the rotation axis. Any profile crossing the axis can produce invalid or self-intersecting geometry.

### Height map or relief

Use `surface()` for a grayscale height field after preprocessing. Crop, linearize/invert intentionally, suppress noise, and downsample to printer-aware resolution first.

```scad
map_w_mm = 80;
map_h_mm = 60;
relief_mm = 1.2;
pixel_w = 401;
pixel_h = 301;

scale([
    map_w_mm / (pixel_w - 1),
    map_h_mm / (pixel_h - 1),
    relief_mm / 100
])
    surface(file = "heightmap.png", center = false, convexity = 10);
```

Verify the exact grayscale-to-height convention in the installed OpenSCAD version with a small ramp. Do not assume an 8-bit value becomes millimeters without scaling. Add a backing plate and union/intersect the relief intentionally.

### Multi-view blockout

OpenSCAD does not reconstruct depth from photos. Convert views into measured profiles and use them as constraints:

- front silhouette constrains X/Z;
- side silhouette constrains Y/Z;
- top silhouette constrains X/Y;
- sections constrain local shape.

Build a primitive/loft approximation or intersect extruded silhouettes as a visual hull. Treat a visual hull as an upper bound: concavities invisible in silhouettes will be missing.

## Parameter architecture

Keep evidence and design decisions separate:

```scad
// Measured/requested
overall_h = 120;
overall_w = 74;

// Inferred and easy to revise
back_depth = 36;
corner_r = 5;

// Printer/process
wall = 1.6;
clearance = 0.25;
```

Use modules for primary mass, openings, functional insert, relief, and manufacturing splits. Add `assert()` checks for invalid thickness, impossible clearances, and feature overlap.

## Resolution and performance

- Prefer `$fs` and `$fa` to a very high global `$fn`; they adapt segment count to physical size and angle.
- Use coarse values during preview and final values during render/export.
- Simplify traced polygons before Boolean operations.
- Downsample height maps with `scripts/plan_resolution.py`; a 2D grid grows to roughly two triangles per cell.
- Avoid Minkowski sums and deeply nested Booleans on high-resolution imported meshes unless necessary.
- Use a low-resolution proxy for imported organic geometry during positioning.
- Split color/material bodies and expensive relief into separately renderable modules.

Set curve sampling from physical error. For a 0.4 mm-nozzle FDM part, an extremely small `$fs` such as 0.01 mm normally adds computation without printable benefit; derive the value from the measured process capability and desired chord error.

## Color and texture

Treat `color()` as a preview instruction. STL does not preserve color. For material/color printing:

- export aligned bodies separately;
- use a downstream 3MF-capable assembly workflow;
- verify that the exact exporter and slicer preserve assignments;
- convert only selected color boundaries into physical relief.

OpenSCAD is not a UV/PBR texturing tool. Use Blender for photo textures and appearance comparison.

## Validation

1. Echo critical dimensions and parameter values.
2. Render with final `$fs/$fa` and inspect for non-manifold/self-intersecting output.
3. Export binary STL or 3MF where supported.
4. Audit the mesh and compare canonical renders.
5. Slice at the intended scale and profile.
6. Print interface/relief coupons before the complete part.

Prefer OpenSCAD when the editable parameter model is more valuable than exact organic surface matching. Switch to CadQuery/FreeCAD for complex fillets, constrained sketches, and BRep interfaces; switch to Blender for freeform organic reconstruction and texturing.
