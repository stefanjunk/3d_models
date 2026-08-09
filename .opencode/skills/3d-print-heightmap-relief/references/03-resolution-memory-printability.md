# 03 — Resolution, memory, and printability

## Three resolutions, not one

### Source-image resolution

The master image’s pixel count. Keep a high-resolution source because future physical sizes and filters may change.

### Geometry sampling resolution

The spacing between sampled surface vertices, controlled here by `mesh_pitch_mm`. This determines mesh count and memory.

### Printable resolution

The machine/process limit. In FDM it differs by axis:

- XY detail is constrained by nozzle, extrusion/line width, path planning, material flow, and feature orientation;
- Z detail is quantized by layer height and affected by surface angle.

A 1254×1254 source does not require a 1254×1254 mesh, and neither guarantees 1254 distinguishable printed details.

## Convert pixels to millimetres

For physical width `W` and image width `Nx`:

```text
source pitch x = W / Nx
source pitch y = H / Ny
```

Example: 1254 pixels across a 100 mm texture is about 0.080 mm/pixel. That is valuable as a master and for filtering, but is much finer than the geometry pitch usually needed for a 0.4 mm FDM nozzle.

## Planning heuristics

These are starting values, not hard printer limits.

| Nozzle | Draft mesh pitch | Detailed mesh pitch | First coupon feature widths |
|---:|---:|---:|---:|
| 0.25 mm | 0.25–0.40 mm | 0.12–0.22 mm | 0.25–0.60 mm |
| 0.40 mm | 0.45–0.80 mm | 0.20–0.35 mm | 0.40–1.00 mm |
| 0.60 mm | 0.70–1.20 mm | 0.30–0.55 mm | 0.60–1.50 mm |

Use finer geometry than the target printed feature so curvature is represented, but avoid extreme oversampling. Curved-surface chord error may require a finer pitch than image detail alone.

A useful detailed default for a 0.4 mm nozzle is often 0.25–0.30 mm. Draft configurations in the examples deliberately use 0.9–1.5 mm to make iteration and Boolean testing fast.

## Z depth and layer height

Compute:

```text
relief steps = depth_mm / layer_height_mm
```

One layer of relief gives almost no tonal separation. Three to five steps are a more useful starting point; smooth bas-relief may need more. Vertical-side texture is not simply quantized as stacked horizontal terraces, but layer height still controls sloped Z changes.

Examples at 0.20 mm layer height:

| Depth | Nominal steps | Use |
|---:|---:|---|
| 0.20 mm | 1 | usually too subtle |
| 0.40 mm | 2 | shallow tactile texture |
| 0.60 mm | 3 | moderate texture |
| 0.80 mm | 4 | readable engraving |
| 1.20 mm | 6 | strong relief; check wall/overhang |

Top-surface embossing and vertical-wall engraving can behave differently. Print coupons in the intended orientation.

## Mesh size formulas

For a nonperiodic rectangular grid:

```text
Nu = ceil(width / pitch) + 1
Nv = ceil(height / pitch) + 1
```

A closed two-skin patch is approximately:

```text
vertices ≈ 2 · Nu · Nv
triangles ≈ 4 · (Nu-1) · (Nv-1) + side triangles
```

Raw NumPy-style storage estimated by the analyzer is:

```text
vertices: float64, 3 values each
faces:    int64, 3 indices each
field:    float32, 1 value per grid point
```

Boolean kernels, adjacency tables, spatial indices, temporary copies, and Python object overhead can require roughly 3–10 times the raw arrays.

## Why halving pitch is expensive

For a two-dimensional surface, halving pitch roughly quadruples samples, triangles, and raw memory. A Boolean may scale worse than linearly.

Do not respond to an unclear texture by blindly doubling resolution. First determine whether the problem is:

- wrong image content;
- wrong physical texture scale;
- inconsistent direction;
- excessive blur;
- insufficient relief depth;
- slicer suppression;
- lighting/viewing conditions;
- or actual sampling.

## Example estimates

### Unicorn cylinder

Radius 40 mm gives a circumference of about 251.3 mm. A 78 mm high band at 0.30 mm pitch is roughly:

```text
Nu ≈ 838 periodic samples
Nv ≈ 261 samples
surface grid ≈ 219,000 points
closed patch ≈ 438,000 vertices
triangles ≈ 870,000
```

This is reasonable as a mesh but inappropriate as hundreds of thousands of B-rep faces.

### Rounded organizer

A 90×65 mm rounded rectangle with 8 mm corner radius has a perimeter near 296.3 mm. An 83 mm band at 0.30 mm pitch is roughly 275,000 surface points and over one million closed-patch triangles.

### Honeycomb shelf

Split outer wall, inner wall, front ring, and back ring into separate closed cutters. This keeps each working set smaller and avoids merging adjacent relief families into a potentially non-manifold intermediate STL.

## Source downsampling strategy

1. Keep the original master.
2. Decide physical size.
3. Apply levels and filters while resolution is still sufficient.
4. Downsample to a target pitch at or finer than the geometry pitch.
5. Generate the mesh at the geometry pitch.
6. Let the slicer perform the final process discretization.

For a detailed 0.30 mm mesh, a prepared image pitch of 0.15–0.25 mm retains interpolation headroom without extreme memory use.

## Bit depth and memory

A 16-bit 4096×4096 grayscale image is about 32 MiB uncompressed. Converting it to float32 is about 64 MiB. Multiple filter buffers can multiply that. Image memory is often still smaller than the corresponding closed triangle mesh and Boolean workspace.

Use low-resolution previews for interaction, but keep final physical dimensions as parameters. The scripts separate preview size from final generated size.

## Curvature and aliasing

A flat image sampled on a tight curve needs enough geometric samples to represent both:

- the relief waveform;
- the base surface curvature.

For a cylinder, angular chord error decreases with more samples around the circumference. CadQuery/OpenSCAD base tessellation should be at least as fine as the relief’s useful scale; otherwise the Boolean result inherits a faceted base.

## Feature survival

A feature can disappear because:

- it is narrower than one viable extrusion path;
- slicer gap-fill rules omit it;
- an engraving valley is too narrow for the nozzle;
- tonal difference is less than a layer or path offset;
- neighboring peaks merge after nozzle convolution;
- the part orientation aligns the feature poorly with layers;
- pressure/flow variation overwhelms shallow texture.

Use the analyzer’s connected-component and slope diagnostics as warnings, then inspect actual toolpaths.

## Memory-control methods

In order of preference:

1. Increase mesh pitch to the finest useful value.
2. Crop/taper relief to only the visible region.
3. Split independent surface families.
4. Use one periodic texture tile and repeat coordinates rather than baking a huge image.
5. Reduce base STL tessellation only if it remains finer than visible curvature.
6. Use `float32` for image fields; reserve `float64` for geometry where needed.
7. Generate patches sequentially and Boolean together.
8. Use a dedicated mesh Boolean engine rather than converting dense relief to a B-rep.
9. Tile arbitrary meshes into overlapping patches only when the Boolean backend can reconcile them.

## Analyzer

```bash
python scripts/analyze_heightmap.py prepared.png \
  --physical-width-mm 296.3 --physical-height-mm 83 \
  --mesh-pitch-mm 0.30 \
  --nozzle-mm 0.4 --line-width-mm 0.44 \
  --layer-height-mm 0.2 --relief-depth-mm 0.38 \
  --repeat-x --report analysis.json
```

The high working-set estimate is deliberately conservative. Treat it as a reason to stage the workflow, not as an exact peak-RAM prediction.
