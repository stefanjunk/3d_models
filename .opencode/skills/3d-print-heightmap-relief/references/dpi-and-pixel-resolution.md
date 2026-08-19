# DPI/PPI, pixel pitch, and resizing

## Two PPI stages

### Source authoring PPI

For newly generated art, request an isotropic square-pixel source master at a declared physical size and PPI. Persist requested physical size, PPI, requested pixels, prompt, actual pixels, and effective PPI.

### Surface-build PPI

The build heightmap is printer/surface-specific. Its X/Y PPI may differ because physical sampling directions differ.

`ppi = 25.4 / pitch_mm`

Example: 0.20 mm/px → 127 PPI; 0.12 mm/px → 211.67 PPI.

## FDM starting pitch

- axis mainly in printed XY: roughly 0.5× nozzle diameter per sample;
- axis mainly along model Z on a side wall: roughly one layer height per sample;
- top-facing relief: both image axes are XY, so start from nozzle/line-width scale;
- freeform/mixed orientation: use conservative isotropic sampling unless a metric-aware adaptive method exists.

These are model-sampling starting points, not guaranteed printable feature limits.

## Resizing quality rules

For recognizable subjects:
- never anisotropically stretch by default;
- warn above ~125% enlargement;
- strongly warn above ~150%;
- normally reject/seek a better source above ~200%.

For seamless textures:
- prefer crop and repeat;
- adjust tile repeat count rather than stretching;
- mild scale adjustment may be acceptable, but preserve tile aspect unless deliberately authorized.

Downscaling is acceptable when antialiased and when printable features survive.

## Do not confuse PPI with shape

PPI metadata alone does not preserve shape. Correct shape requires physical coordinates plus pixel pitch. Many CAD/image tools ignore embedded PPI, so the JSON sidecar is authoritative.
