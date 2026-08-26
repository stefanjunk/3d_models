# FDM surface quality for freeform products

## Two discretizations

A smooth mathematical surface is discretized twice:

1. CAD/SubD/SDF to triangles or polygons;
2. triangles to sliced layers and extrusion paths.

A clean render can hide errors in either stage.

## Tessellation controls

Prefer exporters that expose:

- chord/surface deviation;
- angular/normal deviation;
- maximum edge length;
- aspect-ratio or adaptive refinement controls.

Use smaller triangles in high-curvature and silhouette-critical regions. Avoid uniformly tiny triangles on planar regions.

The template starts with conservative premium-surface values, but every product must validate them at actual scale. Compare the mesh to the authoritative surface when the backend supports it.

## File formats

- Keep native source and STEP/B-Rep when available.
- Use 3MF for manufacturing metadata and explicit units where the toolchain supports it.
- OBJ is useful for mesh/SubD/FFD handoff and semantic groups.
- STL is a geometry-only fallback with no reliable unit metadata.

## Layer stepping

Shallow roofs, domes, bowl shoulders, and shoe rockers can show large terraces even when the XY mesh is fine. Review:

- orientation alternatives;
- variable layer height;
- local layer-height modifiers;
- seam placement;
- support contact on visible surfaces;
- post-processing allowance.

## FDM-aware curvature

A mathematically circular underside can create a poor sequence of overhangs. Consider print-aware transition curves such as:

- chamfer-to-curve or ogee-like profiles;
- teardrop openings;
- progressively changing slopes;
- split orientation that moves critical curvature to XY.

Do not destroy the intended visual language merely to avoid every support. Compare printing, splitting, soluble support, and post-processing routes.

## Surface feature scale

Ensure visible ridges, grooves, dimples, and texture wavelengths survive nozzle width and layer height. Apply relief or patterns only after the base envelope is stable, and use the dedicated height-map/texture workflow for dense image-driven geometry.

## Required evidence

- exported mesh screenshots with flat shading or edge overlay;
- silhouette comparison against the source surface;
- slicer preview of shallow curves and seams;
- variable-layer-height map where used;
- print coupon for a representative curvature when premium finish is required.
