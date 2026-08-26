# Memory and performance

High-resolution AI meshes and dense volume methods can exhaust memory quickly. Plan memory before execution.

## Triangle mesh memory

Raw vertex and face arrays are only a fraction of peak use. A mesh with `V` float64 vertices and `F` int64 triangles needs approximately:

```text
vertices = V × 3 × 8 bytes
faces    = F × 3 × 8 bytes
```

Adjacency, normals, BVHs, Boolean acceleration structures, undo copies, evaluated modifier meshes, and Python copies can multiply this by roughly 5–20 depending on the tool and operation.

## Dense volume memory

For extents `(Lx, Ly, Lz)` and voxel size `s`:

```text
Nx = ceil(Lx / s) + padding
Ny = ceil(Ly / s) + padding
Nz = ceil(Lz / s) + padding
voxels = Nx × Ny × Nz
memory = voxels × bytes_per_value × simultaneous_buffers
```

A float32 field uses 4 bytes per voxel; float64 uses 8; bool is commonly 1 byte in NumPy. Marching cubes may create an additional float32 copy and large vertex/face arrays.

Run `scripts/estimate_voxel_memory.py` before allocating.

## Resolution selection

Choose voxel size from all of these:

- smallest ornament that must survive;
- minimum wall or gap;
- printer XY/Z capability and nozzle width;
- expected smoothing/remeshing error;
- available memory;
- size of ROI rather than whole-object bounds.

A useful operation usually needs several voxels across the smallest retained wall. Do not assume one voxel accurately represents a feature.

## Memory reduction hierarchy

1. Crop to ROI plus a seam/validation margin.
2. Use a decimated proxy for registration and previews.
3. Use float32 rather than float64 for fields.
4. Use bool masks when distance values are not required.
5. Use sparse OpenVDB or narrow-band level sets.
6. Process chunks with overlap, then stitch only if topology permits.
7. Increase voxel size for initial iterations.
8. Disable unnecessary viewport, undo, and duplicate evaluated meshes.
9. Union cutters before applying them to the production mesh.
10. Export intermediate results and release objects between stages.

## Sparse volumes

OpenVDB is advantageous when only a narrow band around a surface is active. It is less helpful when the entire bounding volume is densely populated. Preserve a narrow signed-distance band sufficient for the intended offset and Boolean blend.

## Local versus global remesh

A global voxel remesh costs memory based on the entire bounding box and can erase distant detail. Prefer:

- cropped ROI remesh;
- duplicate source, isolate patch, remesh patch;
- overlap band and seam union;
- final validation outside ROI.

## Blender-specific controls

- work headless for batch jobs;
- save a lightweight `.blend` before applying expensive modifiers;
- disable rendered viewport and high subdivision;
- use a low-res duplicate for cutter placement;
- avoid retaining many unapplied evaluated copies;
- decimate only a working copy, never the archive source;
- set voxel size in physical units after applying scale.

## CAD-kernel controls

B-Rep kernels are efficient for a modest number of analytic faces, not millions of triangular faces. Do not convert a dense mesh into one B-Rep face per triangle. Generate functional parts in CAD and combine in a mesh engine instead.
