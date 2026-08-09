# 04 — Surface mapping

## General model

A parametric surface is:

```text
P = S(u,v)
N = normalized(∂S/∂u × ∂S/∂v)
```

The height map is sampled at image coordinates derived from `(u,v)` or from a world-space projection. Relief moves along `N`.

A successful mapping needs:

- a bijective or at least intentional correspondence;
- stable normals;
- controlled distortion;
- explicit seams;
- consistent orientation;
- enough sampling for curvature;
- a strategy for boundaries and adjacent patches.

No single UV map is distortion-free for every shape. “Every object and every image” therefore means choosing an appropriate parameterization or atlas, not applying one universal projection blindly.

## Mapping modes in this package

### `surface_uv`

Use the surface generator’s native coordinates.

Best for:

- full cylinders;
- cones/frustums;
- rounded rectangular perimeters;
- polygon walls;
- spheres and toruses;
- imported grids with known topology.

### `planar_axes`

Project positions onto two fixed world/object axes:

```text
u = dot(P - origin, axis_u) / tile_width
v = dot(P - origin, axis_v) / tile_height
```

Best for:

- preserving one wood-grain direction across several coplanar face sectors;
- stamping a world-aligned pattern onto multiple surfaces;
- avoiding independent face rotation.

It is not suitable where a single projection collapses edge-on surfaces.

## Coordinate transformations

The sampler applies, in order:

1. source/native UV or planar projection;
2. optional U/V swap;
3. quarter rotation;
4. U/V flips;
5. repeat and offset;
6. wrap or clamp;
7. image interpolation.

After `swap_uv`, explicitly revisit wrap flags. A periodic surface-U may have become image-V.

Use `scripts/generate_mapping_test_image.py` before decorative art.

## Plane

For origin `O` and axes `A` and `B`:

```text
P(u,v) = O + u·W·A + v·H·B
N = normalized(A × B)
```

Use `normal_sign=-1` to target the opposite side.

Common errors:

- axis order mirrors the image;
- image row zero is visually “top” while geometric V increases upward;
- exact coplanarity makes the Boolean fail;
- the relief reaches a panel edge and creates a knife edge.

Use edge taper or a border.

## Cylinder

For radius `R`, start angle `θ0`, and span `Δθ`:

```text
θ = θ0 + u·Δθ
P = (cx + R cos θ, cy + R sin θ, z0 + v·H)
N = (cos θ, sin θ, 0)
```

Full-wrap width:

```text
W = R · |Δθ| = 2πR for 360°
```

For a complete wrap, U is periodic and the duplicate endpoint is omitted. The height-map seam must also be periodic or intentionally placed in blank space.

### Cylinder design choices

- **One artwork around once:** prepare width `2πR`; `repeat_u=1`.
- **One texture tile repeated:** prepare one physical tile and set `repeat_u`.
- **Centered front graphic:** choose `start_angle_deg` so the subject faces the desired direction.
- **No seam through subject:** contain/pad artwork and put seam in the black margin.
- **Inside wall:** reverse `normal_sign`; verify cutter direction.

### Cylindrical caps

The side wall and top/bottom disks are different parameterizations. Use separate patches. A single rectangular image cannot pass continuously from side to cap without an atlas and distortion choice.

## Cone or frustum

Radius varies linearly:

```text
r(v) = r0 + v(r1-r0)
P = (r(v) cos θ, r(v) sin θ, z0 + vH)
```

A rectangular image mapped directly will compress toward the smaller radius. Options:

- accept physical compression;
- prewarp the image;
- use a sector-shaped unwrapped artwork;
- define repeats by angle rather than millimetres;
- split the frustum into bands.

The generator uses a normal containing the radial slope. Check very steep cones for self-intersection when relief depth is large relative to local radius.

## Rounded rectangular wall

This is the preferred map for a rounded cubic organizer.

Parameter U follows true arc length around:

1. front/bottom straight;
2. quarter corner arc;
3. side straight;
4. corner arc;
5. back straight;
6. corner arc;
7. other side;
8. final corner arc.

The perimeter is:

```text
L = 2(W + D - 4r) + 2πr
```

The image does not restart at a face boundary. Its local tangent turns continuously through rounded corners, so the texture wraps rather than rotating independently.

### Corner considerations

- Relief offset along normals slightly changes effective perimeter.
- Deep embossing on a tight convex corner can stretch and thin peaks.
- Deep engraving on a tight corner can make cutter skins intersect.
- Use a mesh pitch fine enough for the arc.
- Keep depth small relative to corner radius.
- Taper near top/bottom, not around U, when full continuity is desired.

## Sharp cube or rectangular prism

A sharp cube has no unique smooth normal at an edge. Choose one strategy.

### Separate faces

Map each face independently. Best for logos centered per face. Decide rotation and crop for each face. Add a small edge margin to avoid overlapping cutters.

### Unfolded strip

Treat front, side, back, side as a 2D strip with piecewise faces. The image is continuous in unfolded distance, but the relief normal jumps at edges. Generate one cutter per face with controlled overlaps/gaps, or bevel/round the object.

### Rounded-perimeter approximation

Add real corner radius and use the rounded rectangle wall map. This is usually the best option for a continuous material texture.

### World projection

Project one global image across selected faces. This preserves global direction but compresses surfaces that turn away from the projection. Good for wood grain across coplanar/ring sectors, not for a full cube side wrap.

## Polygon wall and honeycomb

For a closed polygon, U follows perimeter arc length and V follows depth/height. The outward normal is piecewise constant on sharp faces.

For an inner cavity wall, the normal into the cavity is the object’s outward normal. Set `normal_sign=-1` relative to the polygon’s exterior radial direction.

### Texture direction

To make wood grain run along shelf depth instead of around the hexagon:

1. use polygon-wall native `u=perimeter`, `v=depth`;
2. `swap_uv=true`;
3. map image X to depth;
4. set wrap flags *after* the swap;
5. repeat the cross-grain axis around the perimeter.

This avoids the alternating grain directions produced by six independent local face maps.

## Polygon ring plane

A honeycomb front/back rim is an annulus between outer and inner polygons. The generator creates one closed relief patch per side sector. `edge_gap_mm` retracts adjacent sectors slightly so their side walls do not become coincident in a merged STL.

Use a single global planar mapping for all sectors. The wood image then has one world-space direction across the entire front or back face.

Boolean the separate sector bodies together against the base. Multiple watertight cutter bodies are valid; the final object should still be validated as the expected body count.

## Sphere

Longitude/latitude mapping:

```text
P = C + R(cos φ cos θ, cos φ sin θ, sin φ)
```

Distortion increases toward the poles. A full rectangular image pinches into a point at ±90°. The provided generator is best for bands that avoid exact poles.

Strategies:

- use an equatorial band;
- split into an atlas;
- use cube-map or icosahedral mapping in Blender;
- accept polar distortion for nonsemantic texture;
- use geodesic/local decal patches.

Deep relief can self-intersect near tight curvature. Keep depth small relative to radius.

## Torus

Use major angle U and minor angle V. A full torus is periodic in both directions. The outer and inner closed skins form separate topological components of the patch; together they bound a solid shell.

Texture scale changes around the minor circumference if the same UV increments are interpreted visually at inner and outer regions. Use world-space or arc-length-aware remapping when uniform physical size is essential.

## Arbitrary sampled surface (`grid_npz`)

Store:

```python
np.savez(
    "surface.npz",
    positions=positions,   # shape (Nv, Nu, 3), millimetres
    normals=normals,       # optional, same shape
    periodic_u=False,
    periodic_v=False,
    u_length_mm=120.0,
    v_length_mm=60.0,
)
```

If normals are omitted, they are derived from neighboring positions. Supply normals for sharp, noisy, or irregular surfaces.

This works for surfaces sampled from:

- CAD evaluation grids;
- ray casts;
- height fields;
- Blender UV coordinates exported as a regular grid;
- mathematical patches.

It does not represent arbitrary branching topology in one rectangle. Split such an object into patches or use Blender UV displacement.

## Arbitrary triangle meshes

Common strategies outside this generator:

### UV displacement

Use an existing UV atlas and displace vertices. Best in Blender. Subdivide before displacement and restrict with vertex groups.

### Ray-projected decal

For each image sample, cast a ray onto the object, use the hit point and normal, then construct a local patch. Good for localized relief. Fails across occlusion/undercuts unless multiple projections are used.

### Closest-point projection

Project a prebuilt relief sheet to the nearest surface. Can jump between nearby object regions and distort around concavities.

### Shrinkwrap

Create a dense relief mesh, shrinkwrap its base to the target, then offset along normals. Useful interactively in Blender. Apply modifiers and inspect self-intersection.

### Surface parameter evaluation

For NURBS/B-rep faces, evaluate a regular `(u,v)` grid per face. Edges and trimmed regions need clipping/stitching. This is possible through CAD kernels but is more involved than a triangle-mesh UV path.

## Boundaries and taper

A relief ending abruptly at a patch edge creates a vertical wall. This may be intentional, but it often leaves a visible rectangle.

Use a smooth edge taper:

```text
factor = smoothstep(distance_to_edge / taper_width)
height = height · factor
```

Do not taper across a periodic seam. On a full cylinder, taper only V unless the artwork itself has a blank U margin.

## Adjacent patch strategy

When relief covers multiple surface families:

- keep each patch watertight;
- avoid exact coincident side walls;
- use small edge gaps for adjacent cutters;
- or intentionally overlap cutters and Boolean them as a union in the backend;
- never concatenate touching watertight shells and assume the resulting STL is manifold.

A mesh can contain individually valid bodies yet become non-manifold when they share exact edges/faces.

## Distortion checks

Measure or visualize:

- local U and V millimetres per UV unit;
- aspect ratio of mapped squares;
- Jacobian area scaling;
- normal change between adjacent samples;
- seam position;
- texture direction field.

A checkerboard or asymmetric mapping test should be run before detailed art.

## Normal quality

Normals determine relief direction. Problems arise from:

- reversed face winding;
- averaged normals across a sharp edge;
- non-unit normals;
- noisy imported meshes;
- normals pointing into the body on some patches.

For a cutter, “inward” is opposite the outward surface normal. Validate a constant white map first; it should create a uniform-depth band on the intended side.
