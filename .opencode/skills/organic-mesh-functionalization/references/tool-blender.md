# Blender-specific workflow

## Recommended object organization

Collections:

```text
00_SOURCE_LOCKED
10_PROXY
20_CUTTERS
30_FUNCTIONAL_PARTS
40_INTERMEDIATES
50_RESULT
90_REVIEW
```

Duplicate the source and disable selection on the archival object. Apply scale/rotation before dimensional work and keep a transform log.

## Operations

- **Decimate**: create proxy; inspect preservation and do not assume the ratio maps linearly to error.
- **Bisect / vertex groups / masks**: segment broad regions.
- **Shrinkwrap**: conform a flange or interface mesh to the organic surface; constrain with vertex groups and offset.
- **Boolean Exact**: default for difficult mesh intersections. Enable self-intersection handling only when required; hole-tolerant modes can be slower and should not excuse invalid operands.
- **Voxel Remesh**: reconstruct a manifold volume when topology is unusable. It discards original mesh topology and can remove detail; limit to a duplicate or ROI.
- **Solidify**: useful for open shells but can self-intersect in tight concavities and is not a universal uniform-wall solution.
- **3D Print Toolbox / Select Non-Manifold**: interactive checks, supplemented by re-import and external reports.

## Headless automation

Use Blender Python for:

- import/export;
- named object/collection management;
- modifiers with recorded settings;
- applying transforms;
- screenshots from fixed cameras;
- batch Boolean trials on copies;
- saving `.blend` intermediates.

Always check modifier result object count and mesh validity after applying. Save before destructive modifier application.

## Dense mesh tips

- Disable unnecessary modifiers and viewport overlays.
- Work on a proxy for placement.
- Use local vertex groups and separate ROI objects.
- Avoid duplicating the full source repeatedly.
- Do not voxel-remesh the full decorative exterior when only the belly, sole band, or tower interior transition needs reconstruction.
