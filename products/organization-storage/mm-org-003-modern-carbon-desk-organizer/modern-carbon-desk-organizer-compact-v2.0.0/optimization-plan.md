# Optimization plan

## Frozen baseline

The recoverable baseline is `modern-carbon-desk-organizer-v1.1.2`: 320 × 230 × 213.6 mm, Kobra-3-Max-specific, with about 1.47 M housing triangles, 1.01 M sorter triangles and 0.24 M triangles per drawer manufacturing mesh. Exact slicer time/material data was not found and is not invented.

## Candidate matrix

| Candidate | Geometry | Process | Status |
|---|---|---|---|
| A | unchanged v1.1.2 | generic 0.4/0.20 PLA | baseline only; does not fit 220 mm bed |
| B | 210 × 190 compact shell with 12 mm framed decks/guide rails | same generic process | geometry comparator |
| C | B plus procedural twill and process-sized tessellation | same generic process | selected digital development candidate |

Candidate C is selected because it satisfies the common-printer build-volume constraint and removes the dense raster-relief dependency. No print-time or material percentage is claimed until exact slicing is available.

The horizontal housing decks are open only in their redundant centers. Continuous 12 mm side rails carry the drawers; 12 mm front/rear beams close each frame and retain racking paths. The housing silhouette, back wall and top-interface pads are unchanged.

Protected regions are frozen in `protected-geometry-map.md`. Geometry comparisons will include envelope, volume, wall reserve, fit calculations, body count and mesh burden. The slicer and physical portions of the Pareto gate remain explicitly open.
