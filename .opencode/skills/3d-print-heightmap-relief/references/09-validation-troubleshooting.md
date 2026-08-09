# 09 — Validation and troubleshooting

## Validation layers

A relief project can pass one layer and fail another.

1. **Image validity:** correct content, range, seam, orientation, and physical scale.
2. **Mapping validity:** correct position, direction, repeat, crop, and normal.
3. **Patch validity:** closed, watertight, finite, correctly wound, expected body count.
4. **Boolean validity:** final object is a volume with expected bodies and no accidental holes.
5. **Slicer validity:** important ridges/recesses produce toolpaths.
6. **Print validity:** visible/tactile result survives extrusion, layers, material, and orientation.

Validate all six.

## Image checks

Use the generated reports and previews. Look for:

- clipped shadows/highlights;
- nearly flat range;
- unexpected transparent geometry;
- compression artifacts;
- one-axis stripes that are not in the intended material;
- nonperiodic edges;
- incorrect preferred direction;
- details that become sub-nozzle at final size.

The seam metric compares opposite-edge RMS with ordinary adjacent-pixel RMS. A periodic high-frequency texture may have nonzero first/last-pixel difference because the duplicate endpoint is omitted; the seam is suspicious when it is disproportionately large.

## Patch checks

```bash
python scripts/validate_mesh.py relief-patch.stl \
  --require-watertight --require-volume
```

Review:

- boundary edges = 0;
- non-manifold edges = 0;
- winding consistent;
- finite bounds;
- positive/meaningful volume;
- body count expected.

A front polygon ring intentionally contains one closed cutter per sector. Multiple bodies can be correct before the final Boolean.

## Boolean checks

Validate inputs separately first. Then confirm:

- cutter overlaps the base;
- result volume is plausible;
- expected opening/cavity remains;
- no small detached chips were created;
- final body count is correct;
- bounds did not change unexpectedly for engraving;
- emboss bounds changed only where intended.

Compare base and final volume. Engraving should reduce volume; embossing should increase it.

## Slicer checks

Use line/toolpath preview, not only model shading.

Check:

- minimum valleys receive paths;
- raised islands are not omitted;
- gap fill is reasonable;
- perimeters do not merge away the pattern;
- top-surface skin does not erase shallow emboss;
- thin wall warnings;
- overhang/support impact;
- layer seam placement;
- variable layer height behavior;
- final estimated time and file size.

## Coupon design

A useful coupon includes:

- relief depths, for example 0.2/0.4/0.6/0.8/1.0 mm;
- line widths from 0.2 to 1.2 mm;
- gaps of the same range;
- tonal ramps;
- a small region of the real texture;
- both emboss and engrave if undecided;
- intended surface orientation.

Use the same material, nozzle, layer height, wall count, speed, and orientation as the final object.

## Visibility engineering

The printed image is seen through geometry and lighting.

Improve recognition by:

- enlarging important features;
- reducing background noise;
- using more binary separation for small art;
- adding a controlled bevel;
- choosing depth that spans several layers;
- placing vertical texture where grazing light catches it;
- choosing matte material when specular reflections hide shallow relief;
- orienting layer lines to complement rather than mask the image;
- keeping support away from the visible surface;
- using a contrasting post-process wash only if permitted.

A textured CAD render can exaggerate detail because it has ideal normals, antialiasing, and lighting.

## Troubleshooting matrix

### “It only looks striped”

Likely causes:

- source texture is dominated by one frequency;
- fine structure was blurred/downsampled away;
- physical tile scale is too large;
- relief depth is too uniform;
- preferred direction is correct but cross-grain/knots are absent;
- slicer removes narrow secondary ridges.

Actions:

1. inspect the prepared height map at final physical scale;
2. add/retain secondary structure, not just resolution;
3. reduce tile size or increase repeats;
4. use a shallow multi-frequency height map;
5. compare toolpaths;
6. print a coupon.

For wood, recognizable knots and irregular band spacing matter more than raw pixels.

### “Wood grain rotates on different faces”

Cause: each face uses its own local UV orientation.

Fix:

- use one continuous polygon/rounded perimeter U coordinate for side walls;
- or use one world-space planar projection for coplanar face sectors;
- explicitly align face UV islands;
- record swap/flip/wrap after transformations.

The honeycomb example uses continuous wall mapping plus global planar mapping on front/back rings.

### “The texture stops at rounded corners”

Cause: only planar faces were textured, corner fillets were omitted, or independent cutters leave gaps.

Fix:

- use `rounded_rectangle_wall`;
- sample the true perimeter including arcs;
- match CadQuery radius exactly;
- use sufficient pitch around curvature;
- include the corner arc in the relief band.

### “The image is mirrored/upside down”

Use the asymmetric mapping test. Check:

- source rotation;
- image row direction;
- `swap_uv`;
- quarter turns;
- flips;
- object normal;
- camera viewpoint.

Do not solve a mirror with `invert`; invert changes height, not orientation.

### “White is shallow instead of deep”

Check mode and invert independently. For normal engraving, white is deepest. If the surface normal points inward instead of outward, the cutter can move into the wrong side.

### “The engraving appears on the inside”

Reverse `normal_sign` or correct the surface definition. Visualize a uniform white cutter and inspect bounds.

### “The Boolean does nothing”

- cutter is outside the body;
- no overlap/coplanar contact;
- wrong units;
- wrong coordinate origin;
- black map or zero range;
- wrong normal sign;
- base/cutter not closed.

Print bounds and use a constant-white test.

### “The Boolean removes the whole wall”

- depth is too large;
- normal reversed;
- wall thinner near fillets;
- cutter intersects an interior divider/cavity;
- units are wrong.

Measure remaining wall throughout curved regions.

### “Boolean fails or hangs”

- meshes too dense;
- self-intersections;
- coplanar adjacent patches;
- invalid inputs;
- excessive base tessellation;
- many tiny disconnected islands.

Actions:

1. validate each input;
2. use draft pitch;
3. increase overlap slightly;
4. split or gap adjacent surface families;
5. try Manifold/Blender/OpenSCAD;
6. simplify base facets;
7. remove sub-printable image detail.

### “Merged cutter is non-manifold”

Concatenating watertight cutters that share exact edges/faces creates edge incidence above two. Keep them as separate tool bodies and let the Boolean backend union them logically, or add a controlled gap/overlap.

### “Out of memory”

Estimate before generation. Increase pitch, crop, split surfaces, avoid B-rep conversion, process images at float32, and use low-resolution drafts. Keep final resolution parameterized rather than repeatedly loading a huge raster during design.

### “High-resolution source still looks like an uneven surface”

Resolution is not the same as material recognizability. Check image semantics, physical repeat scale, relief depth, noise filtering, mapping direction, and slicer path survival.

### “Fine detail is visible in STL but not print”

Inspect toolpaths. Enlarge features, reduce noise, use a smaller nozzle, adjust orientation, increase depth within wall limits, or convert tonal regions to simpler shapes.

### “Surface is too rough”

Reduce depth, blur at a physical radius, clip high-pass content, increase gamma, reduce output range, or use fewer repeats. Roughness may be source noise amplified by depth.

### “Terraces are obvious”

Use a smaller layer height, more relief depth steps, smoother slopes, a different orientation, or variable layer height. Do not only increase XY mesh resolution.

### “Seam is visible”

- make texture periodic;
- blend opposite edges;
- move seam to hidden side;
- place seam in blank artwork margin;
- align periodic sampler endpoint convention;
- avoid using clamp on a periodic axis.

### “Cylinder has a vertical ridge at seam”

Check both image seam and geometry seam. Periodic mesh topology should connect last sample to first without duplicate mismatched endpoints.

### “Sphere pinches at poles”

Latitude/longitude singularity. Avoid exact poles, use an atlas/cube map, or create local patches.

### “Carbon weave looks like parallel grooves”

The tile lacks over/under variation or its physical repeat is too large. Use alternating strand dominance and fine bundle ridges, then map continuously around the perimeter.

## Automated report

The package’s `tests/self-test-report.json` checks core topology implementations. `tests/validation-summary.json` records full draft example Boolean results.

Automated checks do not replace slicer and print validation.
