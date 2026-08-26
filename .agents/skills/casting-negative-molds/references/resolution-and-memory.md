# Resolution, detail transfer, and memory planning

More polygons do not automatically create more printable or castable detail. Allocate resolution to the smallest feature that must survive the complete manufacturing chain.

## Resolution chain

The final feature passes through:

1. source image/scan/mesh;
2. relief or surface reconstruction;
3. CAD boolean/offset/tessellation;
4. printer XY sampling and layer height;
5. print surface finishing or sealing;
6. optional plaster mold reproduction;
7. ceramic drying/firing shrinkage or plaster setting;
8. glaze/decor application and firing;
9. inspection under real lighting and viewing distance.

The coarsest or most smoothing stage controls the result.

## FDM starting points

For a 0.4 mm nozzle:

- use 0.10–0.16 mm layers for high-detail mold faces;
- treat 0.5–0.8 mm relief width and 0.2–0.5 mm depth as practical initial coupon ranges;
- orient important grooves so stair-stepping and extrusion direction do not destroy them;
- use enough perimeters that sealing/sanding cannot open sparse infill.

For a 0.25 mm nozzle:

- use about 0.06–0.12 mm layers where the machine and material are stable;
- test widths around 0.3–0.5 mm and larger;
- expect longer print time and more sensitivity to contamination, flow, and minimum layer time.

These are conservative prototype starting points, not guaranteed printer limits. Printer dynamics, extrusion width, material, slicer, orientation, and finishing matter.

## SLA/MSLA starting points

SLA/MSLA can capture finer relief and smoother curves than normal FDM, but check:

- actual XY pixel/laser spot and optical blur, not only nominal layer height;
- support marks on mold faces;
- resin cure, wash residue, dimensional drift, water exposure, and compatibility with plaster, silicone, or release;
- whether a coating changes dimensions or obscures micro-detail;
- whether the resin becomes brittle over repeated demolding.

Use a test matrix rather than relying on nominal 25–50 µm Z layers.

## Relief design for visible images

A relief must create readable light and shadow after printing/casting.

- Preserve a coherent preferred direction for wood grain, marble veins, engraving hatching, or textile weave.
- Avoid very shallow high-frequency noise; it becomes roughness rather than an image.
- Separate macro-form, mid-scale motif, and microtexture into independent bands.
- Use a broad tonal curve: reserve full depth for a small fraction of pixels.
- Blur or close isolated one-pixel pits that become pinholes or fragile needles.
- Add edge falloff so a relief patch does not end as a vertical cliff.
- For glaze-covered ceramic, make important motifs broader and deeper because glaze can soften valleys and fill fine recesses.

Use `prepare_heightmap.py` to normalize, invert, gamma-correct, blur, crop, tile, and resize images.

## Height-map mesh size

For an image grid of width `W` and height `H`, a simple triangulated relief has approximately:

```text
vertices  ≈ W × H
triangles ≈ 2 × (W - 1) × (H - 1)
```

Examples:

| Height map | Approx. triangles |
|---:|---:|
| 512 × 512 | 0.52 million |
| 1024 × 1024 | 2.09 million |
| 2048 × 2048 | 8.38 million |
| 4096 × 4096 | 33.54 million |

A 4096² source image is not a reason to generate a 33-million-triangle mold if the printer cannot reproduce the corresponding physical pitch.

### Sampling from physical feature size

If the mold face is 200 mm wide and the smallest meaningful feature is 0.6 mm, use at least 2–3 samples across that feature:

```text
sample_pitch ≤ 0.6 / 3 = 0.2 mm
image_width  ≥ 200 / 0.2 = 1000 samples
```

Start near 1024 pixels, then verify the transfer coupon. Oversample modestly to support filtering, not by an order of magnitude.

## Voxel memory

For a dense voxel grid:

```text
Nx = ceil(Lx / pitch)
Ny = ceil(Ly / pitch)
Nz = ceil(Lz / pitch)
voxel_count = Nx × Ny × Nz
raw_memory = voxel_count × bytes_per_voxel
```

A 300 × 100 × 100 mm volume at 0.1 mm pitch contains 3,000 × 1,000 × 1,000 = 3 billion voxels. Even one byte per voxel is about 3 GB before distance fields, temporary arrays, meshes, undo, and application overhead. A 300 mm cube at 0.1 mm would be 27 billion voxels, about 27 GB at one byte per voxel and far more in a real operation.

Halving voxel pitch increases voxel count by about eight times. Use `memory_estimator.py` before enabling Blender Voxel Remesh or converting large textured meshes.

## Mesh-operation memory

Booleans, offsets, remeshes, and mesh-to-BREP conversion can require several simultaneous copies plus acceleration structures. Plan for more than the raw STL file size.

Reduce risk by:

- applying transforms and deleting hidden/internal meshes;
- merging only components that truly interact;
- decimating flat or low-curvature areas while preserving boundaries and relief;
- processing local detail patches separately;
- using BREP primitives for blocks, flanges, keys, ribs, funnels, and vents;
- splitting large tools before expensive booleans;
- using a coarse proxy to find parting and a high-detail mesh only for the final cavity operation;
- disabling excessive undo/history for batch processing;
- exporting intermediate checkpoints.

## Mesh-to-BREP warning

A dense triangulated STL converted into one BREP face per triangle produces a shape with enormous topological overhead. FreeCAD/OpenCascade operations can become much slower or fail. Prefer:

- keeping organic detail as a mesh in Blender;
- remodeling simple geometry parametrically;
- reducing the mesh before conversion;
- using STEP/BREP source whenever available;
- combining a parametric structural frame with a separate mesh detail insert.

## Tessellation settings

A STEP/BREP model still needs tessellation for printing. Set linear and angular deflection from the smallest printable curve deviation, not from an arbitrary “high quality” preset. Export a small curved coupon first.

A useful strategy:

- retain STEP as the design master;
- export one production STL/3MF with documented tolerances;
- compare its measured deviation or facet preview to the source;
- keep the slicer profile with the project.

## Multi-resolution workflow

1. **Proxy:** 1–5% of final polygon count for architecture, split, keys, and handling.
2. **Regional high detail:** retain original or height-map detail only on visible casting faces.
3. **Parametric structure:** build shells, ribs, flanges, and channels as CAD solids.
4. **Final boolean:** combine as late as possible.
5. **Print coupon:** include smallest grooves, ridges, curvature, seam, coating, plaster transfer, and glaze route.
6. **Full export:** only after the coupon passes.

## Acceptance criteria for visible detail

Define measurable tests, for example:

- all 0.6 mm sunflower petal grooves remain separate after casting;
- marble veins are recognizable at 500 mm viewing distance under diffuse side light;
- no pinhole/needle features smaller than the minimum greenware strength limit;
- seam cleanup removes less than 0.2 mm of relief height;
- glaze does not bridge the critical engraved valley in the chosen firing schedule.
