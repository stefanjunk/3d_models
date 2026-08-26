# Physical aspect ratio and coordinate invariants

## The essential invariant

For recognizable artwork, preserve:

`source_physical_width / source_physical_height = placed_physical_width / placed_physical_height`

within a small tolerance.

Do **not** require:

`source_pixel_width / source_pixel_height = build_pixel_width / build_pixel_height`

because the build image may use different millimetres per pixel on X and Y.

## Example: correct non-square build sampling

A subject should occupy 80×40 mm, so its physical aspect is 2.0.

Target sampling:
- X pitch = 0.20 mm/px;
- Y pitch = 0.12 mm/px.

Approximate target raster:
- X = 80 / 0.20 = 400 px;
- Y = 40 / 0.12 ≈ 333 px.

The raw raster aspect is about 1.20, not 2.0. That is **correct** because the physical pixels are not square. Reconstruct physical aspect as:

`(400*0.20) / (333*0.12) ≈ 2.00`

A normal image viewer may show this heightmap compressed. Never re-stretch it based on appearance alone.

## Fit modes in physical space

Given source physical dimensions `Ws,Hs` and target patch `Wt,Ht`:

### contain

`scale = min(Wt/Ws, Ht/Hs)`

`Wp = Ws*scale`, `Hp = Hs*scale`

Center the remaining margin in millimetres. Then convert the placed rectangle independently to target pixels with `pitch_x` and `pitch_y`.

### cover

`scale = max(Wt/Ws, Ht/Hs)`

The placed image remains uniformly scaled and excess physical area is cropped. No axis is stretched independently.

### crop

Treat crop as controlled cover or a deliberately selected source region. Cropping changes composition, not physical scale ratio.

### repeat

Preserve the tile's physical width/height and repeat count. For a texture, change repeat count or crop the tile before using anisotropic stretch.

### stretch

Forbidden by default for recognizable art. Requires an explicit distortion opt-in and must record the percentage change in physical aspect.

## Aspect metadata to persist

Persist at least:
- source raster aspect;
- source physical aspect;
- target patch physical aspect;
- placed physical aspect;
- geometry raster aspect;
- pitch_x_mm and pitch_y_mm;
- physical pixel aspect = `pitch_x/pitch_y`;
- reconstructed placed physical aspect;
- aspect error percent;
- aspect tolerance percent;
- aspect policy and explicit distortion flag.

## Human preview versus geometry data

Keep two outputs when X/Y physical pixel pitch differs:

```text
current-heightmap.png          geometry data, may look visually stretched
current-heightmap.preview.png  square-pixel human preview, must look proportionally correct
```

Never feed the preview into OpenSCAD, Blender displacement, CadQuery, FreeCAD, or a mesh cutter.

## Avoid accumulated resampling

Always rebuild:

`source-master → final target heightmap`

not:

`source → resize A → resize B → resize C → target`.

Repeated interpolation degrades edges/detail and can obscure where aspect errors entered the pipeline.

## Distortion tolerances

Suggested default gates:
- people/portraits/animals/objects/text/logos/motifs: 0.75% physical aspect error;
- general non-repeating art: 1.0%;
- textures: 1.5% by default, while still preferring no distortion.

These are pipeline-error tolerances, not permission to intentionally deform the art.

## Diagnostic procedure

Before a long build, map a known 20 mm circle and 20×20 mm square through the production process. Measure the resulting geometry in CAD. If the circle is elliptical or the square becomes rectangular, locate the stage that changed physical coordinates before continuing.
