# Memory and performance

## Mesh memory

Raw array lower bounds are approximately:

```text
vertices float64: V * 3 * 8 bytes
faces int64:      F * 3 * 8 bytes
```

Real applications also hold normals, adjacency, BVHs, caches, colors, duplicate objects, Boolean intermediates, and Python overhead. Plan for roughly 2–8 times the raw arrays depending on operations.

Use binary STL/PLY/GLB rather than ASCII for storage efficiency. Storage size is not equal to peak RAM.

## Dense voxel memory

For extents `(X,Y,Z)` and voxel spacing `s`:

```text
Nx = ceil(X/s) + padding
Ny = ceil(Y/s) + padding
Nz = ceil(Z/s) + padding
N  = Nx * Ny * Nz
```

Approximate array memory:

- boolean mask: `N` bytes;
- float32 field: `4N` bytes;
- float64 field: `8N` bytes;
- three full float64 coordinate grids: `24N` bytes before fields/results.

Examples for a cube:

| Grid | Voxels | bool | float32 | 3×float64 coordinates |
|---|---:|---:|---:|---:|
| 300³ | 27 M | 26 MiB | 103 MiB | 618 MiB |
| 500³ | 125 M | 119 MiB | 477 MiB | 2.79 GiB |
| 700³ | 343 M | 327 MiB | 1.28 GiB | 7.67 GiB |

Additional temporary arrays can multiply peak memory.

## Rules

- Estimate before allocate.
- Use ROI cropping with padding.
- Use low-resolution preview and high-resolution final stages.
- Prefer `float32` for signed fields unless numerical evidence requires float64.
- Use broadcasting (`x[:,None,None]`) or chunked z-slabs, not full coordinate meshgrids.
- Use sparse/OpenVDB-style storage when available for narrow-band fields.
- Release large references and trigger process-level stage separation when necessary.
- Use `marching_cubes(mask=...)` or a local mask where appropriate; use larger `step_size` only for previews because it reduces detail.
- Keep final voxel size meaningfully smaller than the smallest feature to preserve, but not far below printable resolution.

## Local processing pattern

```text
full source on disk
-> proxy in memory for alignment
-> crop source faces intersecting ROI + safety margin
-> perform local Boolean/remesh
-> merge with untouched source or use exact global union once
-> validate seam and protected surface
```

Merging a local patch is itself a topology-sensitive operation. Prefer engine-supported local Boolean or a controlled boundary stitch over simply concatenating triangles.

## Supplied utilities

- `create_proxy.py` uses optional quadric decimation and reports sampled source-to-proxy deviation.
- `crop_roi.py` extracts an analysis patch; it is normally open and must not be confused with a printable solid.
- `validate_edit.py` avoids a large candidate-triangle fallback above 750,000 faces when no spatial-index dependency is available; the reported nearest-vertex fallback is only a screening metric.
