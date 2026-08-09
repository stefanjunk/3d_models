# 08 — Blender workflow

## When Blender is the best tool

Use Blender when:

- the target is an organic or arbitrary mesh;
- a UV map already exists;
- visual texture placement needs interactive editing;
- shrinkwrap, projection, sculpting, or vertex groups are useful;
- the object must be locally retopologized/subdivided.

Use the external patch workflow when a CAD-accurate base and deterministic Boolean are more important than interactive UV editing.

## Modifier order

A common stack is:

1. apply object scale;
2. repair/confirm base topology;
3. UV unwrap;
4. Simple subdivision or remesh;
5. optional shrinkwrap to restore the nominal base;
6. Displace using image texture;
7. Solidify only if starting from a sheet;
8. Boolean or other finishing modifiers;
9. apply modifiers;
10. validate/export.

Order changes the result. Subdivision after displacement only smooths existing displaced geometry; subdivision before displacement creates samples for the image.

## Simple versus Catmull-Clark subdivision

Use **Simple** subdivision when preserving the exact base shape while adding vertices. Catmull-Clark changes the silhouette and rounds edges unless controlled by creases/support loops.

The bundled script uses Simple subdivision.

## Image settings

Set the height map to **Non-Color** data. Color-management transforms intended for display should not alter numeric displacement.

Use a 16-bit grayscale PNG when tonal smoothness matters. Confirm Blender loaded the intended channel; alpha is not automatically a height policy.

## UV map

A UV atlas defines image placement. Check:

- seam positions;
- island rotation;
- scale consistency;
- overlap;
- padding;
- mirrored islands;
- texture direction;
- distortion.

For a carbon texture around a rounded organizer, create one continuous side island. Four independently oriented islands produce visible direction changes.

For a honeycomb shell, separate side walls and front/back rings, but align each family intentionally.

## Displace modifier

The modifier moves vertices based on texture intensity.

For an outward emboss with neutral black:

```text
strength = +depth
midlevel = 0
direction = NORMAL
```

For inward engraving:

```text
strength = -depth
midlevel = 0
```

For centered displacement:

```text
strength = depth
midlevel = 0.5
```

Direct inward displacement changes the object itself rather than subtracting a closed cutter. Verify wall thickness, self-intersection, and manifold topology.

## Restricting the affected surface

Use a vertex group. Without it, UV-mapped hidden faces or shared vertices may move unexpectedly.

Feather the vertex weights at boundaries to avoid a hard rectangular wall. For periodic wraps, do not feather across the seam.

## Normals

Recalculate outside normals before displacement. Auto Smooth/custom split normals affect shading, but geometric displacement uses the actual mesh vertex normal context. Sharp edges can move diagonally if vertices are shared and normals are averaged.

Solutions:

- split vertices at intentional sharp boundaries;
- bevel/round edges;
- use separate patches;
- use shrinkwrap/normal-transfer techniques;
- displace a dedicated relief mesh and Boolean it.

## Density

An image does not create geometry unless vertices sample it. Estimate vertex spacing in millimetres after object scale. Adaptive subdivision through render-only displacement does not automatically become an STL mesh.

Apply the modifier and inspect final face count.

## UV seams

For a full cylinder:

- place seam in blank background or make texture periodic;
- align first/last UV columns;
- avoid duplicate mismatched vertices;
- inspect relief height on both sides of the seam.

For a torus, both U and V can be periodic.

## Sharp/rounded corners

A continuous UV strip across a rounded corner works naturally with sufficient subdivision. Across a mathematically sharp edge, decide whether to split normals/vertices or bevel the edge. A shared averaged normal can create diagonal relief that does not lie on either face.

## Shrinkwrap patch method

For local relief on an organic object:

1. create a dense planar grid matching image aspect;
2. displace it by the height map;
3. duplicate a base skin or maintain thickness;
4. shrinkwrap the base side to the object;
5. orient/offset along target normals;
6. close edges;
7. Boolean union/difference.

This is conceptually the same closed-patch method as the Python generator but uses Blender modifiers interactively.

## Export

Apply all intended modifiers. Export selected objects in millimetres with scale handled deliberately. Reimport the STL and compare bounds.

The bundled `templates/blender/displace_heightmap.py`:

- selects a mesh by name or active object;
- requires UVs;
- adds Simple subdivision;
- loads the image as Non-Color;
- applies emboss/engrave/centered displacement;
- optionally limits by vertex group;
- exports STL with Blender-version fallbacks.

Example:

```bash
blender object.blend --background \
  --python templates/blender/displace_heightmap.py -- \
  --image prepared.png --output displaced.stl \
  --object Organizer --mode engrave --depth-mm 0.4 \
  --subdivision-levels 3 --vertex-group ReliefBand
```

## Memory

Subdivision grows faces by roughly four per level for quads. Three levels can multiply quads by 64. Combine that with a high-resolution image only when the physical mesh density is useful.

Use:

- lower viewport subdivision;
- a cropped vertex group;
- multiresolution carefully;
- external patch generation for regular analytic surfaces;
- decimation only after checking loss of relief.

## Troubleshooting

### Image visible in material preview but absent from STL

Material/bump shading is not geometry. Use Displace, apply the modifier, and export the modified mesh.

### Surface explodes inward/outward

Object scale is unapplied, depth units are wrong, normals are reversed, or midlevel is incorrect.

### Texture changes direction on faces

UV islands are rotated or mirrored. Align them or use a continuous unwrap/global projection.

### Relief tears at seam

UV values or duplicated vertices disagree at the seam. Use a periodic image and matching boundary heights.

### Object is no longer watertight

Displacement caused self-intersection, moved open boundaries, or exposed zero-thickness regions. Reduce depth, increase wall, restrict the group, or use a Boolean cutter.

## Deliverables

- `.blend` with applied/clearly ordered modifiers;
- UV layout or mapping notes;
- prepared height map;
- script/command;
- applied exported mesh;
- external topology report.
