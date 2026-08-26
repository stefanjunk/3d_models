# Parametric color architecture

## Make color a semantic parameter

Define a color map beside geometric parameters:

```yaml
regions:
  body: body_orange
  muzzle: detail_white
  eyes: detail_black
  scarf: accent_blue
```

The CAD source owns named regions; a separate palette file owns filament appearance and polymer data; a separate machine map owns current slots.

## Preferred geometry patterns

### Top inlay

Subtract the same parameterized 2D profile from the base and extrude it as a separate color body from `top_z - inlay_depth` to `top_z`.

Advantages:

- exact shared boundary;
- all accent colors can be limited to the top few layers;
- easy to export one STL per color;
- readable in OpenSCAD, CadQuery, FreeCAD, and Blender.

Pitfalls:

- coincident overlapping solids if the base was not actually cut;
- too-shallow inlays disappearing after top-surface compensation;
- tiny counters or islands in text;
- seam gaps if separate bodies are independently offset.

### Through-body partition

Split a solid by semantic regions that extend through the full height. Use for stripes, handles, and side-by-side structural colors. It creates many color-active layers and can greatly increase changes.

### Colored shell

Create a surface shell of controlled physical depth around a base. Use for textured assets or skins. Avoid a purely offset duplicate that self-intersects in concave regions; use robust offset/SDF/voxel methods for organic geometry.

### Separate insert

Print an accent as a separate part and assemble it after printing. This often wins when the color region is small, repeated, or would otherwise cause thousands of changes. It also allows incompatible polymers because the interface is mechanical rather than co-extruded.

### Layer-band accent

Place logos, text, and graphics only in a narrow top or bottom Z band. This is one of the most effective ways to reduce purge while keeping a multicolor look.

## Boolean strategy

For each color region `Ci` and full product solid `P`:

```text
Ci := intended color volume clipped to P
Base := P minus union(C1...Cn)
```

Required properties:

- every `Ci` is manifold or a documented set of manifold components;
- pairwise interiors do not overlap;
- the union of all color parts reconstructs the intended product within tolerance;
- every part retains the same origin and transform;
- cutters extend through the target by a documented epsilon rather than ending exactly tangent.

## Parameter dependencies

Color features should regenerate from the same primary dimensions as the product. Examples:

- border width follows nozzle/line width and plate size;
- inlay depth follows layer height and top-shell strategy;
- text stroke has a minimum based on extrusion width;
- color island cleanup threshold follows physical area, not raster pixels;
- shell depth follows wall thickness and structural keep-out.

Do not hide color boundaries in manual face selections if a parameterized profile can generate them.

## Optimize color topology

A visually similar design may have very different change cost. Prefer:

- one contiguous island per color per layer;
- large regions rather than checkerboards;
- accents sharing the same Z band;
- color boundaries aligned with natural seams, ribs, panel lines, or part splits;
- a dominant base filament that can receive permitted purge into hidden infill.
