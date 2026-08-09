# 02 — Image requirements and preprocessing

## Preferred master files

Retain the highest-quality original. For derived height maps prefer:

- lossless PNG;
- 16-bit grayscale when tonal steps matter;
- explicit alpha treatment;
- no JPEG ringing;
- no baked perspective unless the mapping requires it;
- no display-only sharpening halos;
- a known color-space/luminance policy.

The scripts preserve native 16-bit grayscale and convert color images through an explicit channel/luma rule.

## Image inspection checklist

Record:

- pixel width and height;
- data type and bit depth;
- min, max, mean, standard deviation, and percentile range;
- alpha presence and transparent fraction;
- aspect ratio;
- edge seam metrics;
- orientation;
- smallest important feature in pixels and millimetres;
- whether the texture has a preferred direction;
- whether highlights and shadows represent geometry or lighting.

Use:

```bash
python scripts/analyze_heightmap.py image.png \
  --physical-width-mm 100 --physical-height-mm 60 \
  --mesh-pitch-mm 0.3 --report image-analysis.json
```

## Grayscale conversion

Available policies include luma, average, max, min, red, green, blue, and alpha.

Luma is usually a starting point, but not an automatic truth. A red and green material with equal visual depth can produce different geometry. Use a channel or authored mask when color carries semantic regions.

`--luma-space linear` converts sRGB values before luma calculation. This changes mid-tones. Keep the policy in the report.

## Alpha

Transparent pixels need a base height:

- `base`: blend toward `--base-level`;
- `black`: transparent becomes zero;
- `white`: transparent becomes one;
- `multiply`: multiply gray by alpha;
- `ignore`: use RGB regardless of alpha;
- `grayscale alpha`: use alpha itself as the height source.

OpenSCAD’s native image `surface()` ignores alpha, so flatten alpha before that workflow.

## Fit modes

### Stretch

The source fills the target width and height independently. This changes aspect ratio.

Use for abstract textures where anisotropic scaling is acceptable or intentional. Do not stretch a unicorn, logo, face, or measured depth map without approval.

### Cover/crop

Aspect ratio is preserved and the source fills the target. Excess is cropped from the center.

Use when the mapped region must be completely filled and clipping is acceptable.

### Contain/pad

Aspect ratio is preserved and the whole image remains visible. Empty space receives `pad_level`.

Use for logos and the unicorn cylinder example. Put the seam in the padded background, not through the subject.

### Tile/repeat

The source repeats periodically. The sampler omits the duplicate endpoint so a periodic raster represents `[0, period)`.

Use for carbon weave, wood grain, fabric, stone, and other textures. The source must be periodic or edge-blended.

## Repeat, cut, or stretch decision

Ask in this order:

1. Is the image semantic artwork? Preserve aspect ratio; crop or pad.
2. Is it a material texture? Repeat at a physically plausible scale.
3. Is it a measured depth field? Neither stretch nor crop unless recalibrated.
4. Must opposite edges meet? Make the source periodic before mapping.
5. Is the target wider than one tile? Use a repeat count, not a gigantic upscaled tile.

Repeating a 50 mm wood tile four times and stretching one wood image to 200 mm produce visibly different grain.

## Tonal preprocessing

### Levels

Percentile levels suppress outliers:

```bash
--levels 1,99
```

Values below the low percentile become black and values above the high percentile become white. Do not over-normalize a calibrated depth map.

### Gamma

With this package, `output = input^gamma`:

- gamma above 1 darkens mid-tones and reduces shallow regions;
- gamma below 1 lifts mid-tones.

### Contrast

Contrast expands or compresses values around 0.5. It can clip extremes.

### Threshold

Threshold for binary art:

```bash
--threshold 0.52 --threshold-softness 0.08
```

A soft threshold creates a narrow bevel-like transition.

## Physical-scale filtering

Filters use millimetres, not arbitrary pixels.

### Blur

`--blur-mm 0.10` removes detail smaller than the intended physical radius. It also reduces steep relief walls and Boolean noise.

### Unsharp

Use cautiously after downsampling:

```bash
--unsharp-radius-mm 0.25 --unsharp-amount 0.5
```

Sharpening creates overshoot-like ridges even though values are clipped.

### High-pass

High-pass emphasizes texture and removes broad lighting variation:

```bash
--highpass-radius-mm 2.0 --highpass-amount 1.0
```

This is useful for material texture but destructive to true depth.

## Seam preparation

For a full wrap or repeated tile, compare the first/last rows and columns to normal neighboring-pixel variation. A nonzero edge difference is not automatically a bad seam in high-frequency texture. The analyzer reports both absolute seam RMS and seam-to-adjacent RMS ratio.

If the seam is exceptional:

- regenerate the texture procedurally as periodic;
- use offset-and-heal in an image editor;
- blend opposite strips with `--seam-blend-mm`;
- move the seam to a hidden area;
- avoid repeating that axis.

Do not blur a strong seam across the entire image.

## Preferred direction

Wood, brushed metal, fabric, and carbon weave have directional structure. Store the direction explicitly:

- source image X direction;
- mapped surface U direction;
- object/world axis;
- whether mapping swaps U/V;
- flips after swapping;
- repeat axes.

The common failure “wood changes direction on every face” comes from using each face’s local UV frame independently. Use one continuous perimeter coordinate or one global planar projection where appropriate.

## Photos and rendered materials

Before using luminance:

- remove cast shadows and specular highlights;
- remove perspective;
- isolate subject/background;
- flatten uneven illumination;
- decide whether dark means low or merely dark material;
- simplify tiny hair/noise;
- test silhouette recognizability.

For a photograph intended as a shallow portrait relief, a dedicated depth-estimation or manual sculpting process is usually better than raw grayscale.

## Normal-map and bump-map inputs

A bump map may already be a scalar height field, but verify its convention and neutral level. A normal map is directional RGB data. Ask for the displacement/height channel or reconstruct carefully; do not feed it to grayscale conversion without documenting the approximation.

## Preprocessing command examples

Artwork:

```bash
python scripts/prepare_heightmap.py unicorn.png unicorn-height.png \
  --physical-width-mm 251.33 --physical-height-mm 78 \
  --sample-pitch-mm 0.25 --fit contain --pad-level 0 \
  --levels 0,100 --bit-depth 16
```

Seamless material:

```bash
python scripts/prepare_heightmap.py carbon.png carbon-tile.png \
  --physical-width-mm 98.76 --physical-height-mm 83 \
  --sample-pitch-mm 0.20 --fit stretch \
  --levels 0.5,99.5 --blur-mm 0.08 --bit-depth 16
```

Tonal logo with transparent background:

```bash
python scripts/prepare_heightmap.py logo.png logo-height.png \
  --physical-width-mm 60 --physical-height-mm 30 \
  --sample-pitch-mm 0.20 --grayscale alpha \
  --fit contain --threshold 0.5 --threshold-softness 0.06
```

## Quality gate

Open the preview and a false-color or exaggerated-depth view. Confirm that recognizable regions are present *before* running CAD. If wood still looks like generic stripes in the height map, geometry cannot recover wood character.
