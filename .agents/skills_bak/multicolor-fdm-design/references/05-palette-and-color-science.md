# Palette and color science

## Use a fixed physical palette

The printer cannot synthesize arbitrary RGB colors from four solid filaments. The default objective is therefore:

```text
for every source color, choose the perceptually closest available filament
```

Use actual filament IDs and record manufacturer, product name, batch/color, polymer family, opacity, and a swatch measurement.

## Why Lab and CIEDE2000

Euclidean distance in RGB does not correspond well to perceived difference. Convert sRGB samples to CIE Lab and use CIEDE2000 (`deltaE_ciede2000`) for fixed-palette matching. The included script uses scikit-image’s official color conversion and Delta-E implementation.

## Swatch acquisition

Preferred order:

1. spectrophotometer/colorimeter measurement of a printed swatch;
2. controlled RAW/photo with neutral target, fixed white balance, diffused D65-like light, and calibrated correction;
3. manufacturer RGB or website sample;
4. human-entered display hex as a rough fallback.

Print swatches with the same nozzle, layer height, wall thickness, and backing color as the final part. Translucent filaments can change apparent color with thickness.

## Critical semantic colors

Not every color should be chosen solely by nearest Delta-E. Protect semantic masks for:

- eyes, mouth, labels, warnings, logos;
- skin/fur boundaries;
- assembly indicators;
- transparent windows;
- functionally coded regions.

Map these manually or give them priority before general quantization.

## Dithering policy

Dithering is off by default because it creates alternating small regions and excessive filament changes. A deliberate FDM halftone process may be used only when:

- cells are larger than the proven minimum feature size;
- the pattern is optimized for contiguous runs;
- the change budget is acceptable;
- purge contamination and optical mixing are tested.

## Quantization report

Persist:

- source and palette hashes;
- palette colors in sRGB and Lab;
- mapping method;
- mean/median/p95/max Delta-E;
- pixel/area fraction per filament;
- removed and reassigned island statistics;
- preview images: original, quantized, difference heat map, and semantic-mask overlay.
