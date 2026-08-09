# 01 — Height-map fundamentals

## Height is a scalar field

A height map is a two-dimensional scalar field `h(u,v)`. In this package it is normalized to `[0,1]`:

- `0` normally comes from black;
- `1` normally comes from white;
- intermediate gray becomes intermediate height.

For a surface point `P(u,v)` with outward unit normal `N(u,v)`, a basic outward displacement is:

```text
P_relief(u,v) = P(u,v) + d · h(u,v) · N(u,v)
```

where `d` is relief depth in millimetres.

This equation is simple; the difficult parts are deciding what `h` means, calculating a stable `N`, sampling at a printable pitch, and closing the displaced surface into a Boolean-safe volume.

## Emboss

An emboss adds material outside the original surface. A robust patch has:

```text
outer = P + d · h · N
inner = P - overlap · N
```

The inner skin penetrates the base slightly. Union the closed patch with the base. At black pixels the outer skin remains at the original surface; at white pixels it reaches the full depth.

Use embossing when:

- tactile or decorative ridges are desired;
- the base wall is too thin for recesses;
- the object can tolerate a larger envelope;
- highlights from grazing light are important.

Risks include snagging, thin raised islands, support demand on downward-facing surfaces, and loss of sharp peaks due to nozzle width.

## Engraving

An engraving removes material. A robust cutter has:

```text
outside = P + overlap · N
inside  = P - d · h · N
```

Subtract the closed cutter from the base. Black pixels reach the surface but do not intentionally enter the part; white pixels cut to the full depth.

Use engraving when:

- the outer envelope must remain unchanged;
- the image should resist abrasion;
- recesses can be cleaned;
- wall thickness is sufficient.

Check that:

```text
remaining wall >= required structural wall
```

at every white area. On a 2.4 mm wall, a 0.8 mm engraving leaves at most 1.6 mm before considering curvature, tolerances, and interior features.

## Invert

`invert` changes `h` to `1-h`.

It is independent of emboss versus engrave:

- emboss + normal: white is highest;
- emboss + invert: black is highest;
- engrave + normal: white is deepest;
- engrave + invert: black is deepest.

Also distinguish image inversion from normal reversal. Reversing the surface normal changes which physical side is “outside”; inversion changes tonal ordering.

## Depth, overlap, and baseline

### Depth

`depth_mm` is the maximum displacement or cut depth. It is not image contrast. Increasing depth exaggerates every gradient and can turn small image noise into rough geometry.

### Overlap

`overlap_mm` crosses the nominal surface to avoid a coplanar Boolean. Typical mesh workflows use a small positive value such as 0.05–0.15 mm, adjusted to object scale and Boolean tolerance. It should be large enough for robust intersection but not so large that unrelated thin regions are touched.

### Input and output ranges

The config can remap height:

```json
"relief": {
  "depth_mm": 0.6,
  "overlap_mm": 0.08,
  "input_min": 0.1,
  "input_max": 0.9,
  "output_min": 0.0,
  "output_max": 1.0
}
```

This clips shadows/highlights without modifying the stored image. Prefer preprocessing for complex tonal edits and config remapping for deliberate design ranges.

## Centered and signed displacement

A centered displacement uses:

```text
z = d · (h - 0.5)
```

so middle gray is neutral, black moves inward, and white moves outward.

For a solid printable object this is best implemented as two operations:

1. emboss positive values above the neutral level;
2. engrave negative values below it.

A single zero-thickness displaced sheet is not a printable solid. Blender can directly displace a closed mesh around a midpoint, but wall thickness and self-intersection must be checked.

## Other relief types

### Binary engraving

Thresholded art has two levels. It is often more recognizable than tonal relief at small scale. Add a small bevel or blur if perfectly vertical pixel edges alias badly.

### Bas-relief

A tonal subject is compressed into shallow depth. Preserve large forms, suppress lighting gradients, and avoid using photographic shadows as literal cavities.

### Texture relief

Material texture such as carbon weave or wood grain usually needs:

- seamless repetition;
- a clear preferred direction;
- controlled high-pass content;
- shallow depth;
- removal of sub-nozzle noise.

Texture should create readable light modulation, not duplicate every source pixel.

### Lithophane

A lithophane maps image brightness to wall thickness rather than surface height. Its optical behavior, material, backlighting, and minimum/maximum thickness require a separate calibration. Do not use the shallow-relief defaults without reconsidering them.

### Through-cut or stencil

Threshold a binary image and subtract completely through the wall. Islands require bridges or retained connectors. This is a topology problem, not merely a deeper engraving.

## Height maps versus normal maps

A normal map stores surface direction, usually encoded in RGB, not absolute height. Raw luminance is not a valid conversion. Reconstructing height from normals is an integration problem and may be inconsistent. Prefer:

- the original height/displacement map;
- procedural regeneration;
- a dedicated normal-to-height integration step with boundary conditions;
- manual authoring for important parts.

## Tonal visibility

A relief can be geometrically present yet visually unreadable. Visibility depends on:

- enough lateral feature width;
- enough Z steps;
- meaningful contrast after smoothing;
- surface orientation and grazing light;
- material gloss and color;
- layer texture relative to image direction;
- absence of support scars;
- camera/viewing distance.

A high-resolution image cannot compensate for a 0.15 mm-wide line printed with a 0.4 mm nozzle.

## Coordinate and sign checklist

Before generating a final model, make a small asymmetric test with:

- a left/right marker;
- top/bottom labels;
- four unequal corner marks;
- a black-to-white ramp.

Use `scripts/generate_mapping_test_image.py`. It detects flips, quarter turns, seam placement, normal direction, and accidental inversion faster than a decorative image.
