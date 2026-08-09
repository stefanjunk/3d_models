# Input triage, segmentation, and repair

## Establish what the mesh means

A visually closed object is not necessarily a solid. Determine:

- units and scale;
- outward normal orientation;
- whether internal shells are intentional;
- whether separate connected components represent decoration, debris, eyes, teeth, textile, or actual assembly parts;
- whether the bottom is open;
- whether the model contains coincident duplicate shells;
- whether its high face count represents useful detail or only oversampling.

Run a baseline report before processing. Preserve both the raw file and its SHA-256 hash.

## Repair hierarchy

Use the smallest repair that makes the next operation valid:

1. remove NaN/Inf and unreferenced vertices;
2. merge truly coincident vertices using a scale-aware tolerance;
3. remove duplicate and degenerate faces;
4. orient connected shells consistently;
5. fill only small, unambiguous planar/triangular holes;
6. remove tiny disconnected debris only when size and intent criteria are recorded;
7. repair self-intersections locally;
8. use local voxel remesh only when surface topology remains unusable.

Do not automatically close purposeful openings or delete small decorative components.

## Proxy meshes

Create a proxy for positioning and interactive planning when the source exceeds practical viewport or Boolean limits.

A proxy may be:

- decimated while preserving boundaries and sharp features;
- a hidden-interior crop;
- a convex/alpha-shape envelope;
- a voxel-remeshed low-resolution copy;
- a set of cross-sections and landmarks rather than a full mesh.

The proxy is not the final printable source unless deviation is measured and accepted.

## Segmentation methods

Use one or combine several:

- connected components;
- material/UV/object IDs when the source retained them;
- plane or height threshold;
- geodesic selection from seeds;
- curvature and normal direction;
- color/texture labels;
- spatial ROI primitives;
- manually painted vertex groups;
- fitted surface or signed distance to a reference curve/surface.

A shoe upper should not be removed only by `z > threshold` when the sole rim curves upward. A fitted interface surface or manually reviewed vertex group is safer.

## Destructive-operation checklist

Before remesh, decimate, smooth, or repair:

- duplicate the object/file;
- record face count, volume, area, bounds, and body count;
- record operation parameters;
- generate an overlay/deviation report;
- inspect protected high-frequency details;
- keep the original transform and units.
