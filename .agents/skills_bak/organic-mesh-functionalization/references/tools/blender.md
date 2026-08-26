# Blender guidance

## Best role

Blender is the default interactive and scriptable environment for organic STL/OBJ/GLB sources. Use it for inspection, segmentation, local remeshing, modifier-based Booleans, sculpted transitions, section views, and headless automation.

## Recommended stack

1. Import and establish units.
2. Duplicate and lock the archive object.
3. Apply rotation and scale on the working copy.
4. Split loose components and inspect internal shells.
5. Create a decimated proxy for placement.
6. Keep cutters in a dedicated collection.
7. Use Boolean Exact/Manifold where available.
8. Apply one stage at a time and export checkpoints.
9. Validate with Blender 3D Print Toolbox and external Trimesh scripts.

## Boolean modifier

- Use `Difference` for cavities/openings, `Union` for inserts that must fuse, and `Intersect` for retained envelopes.
- Exact is safer for overlapping/coplanar geometry than fast approximate methods but is not magic; invalid input can still fail.
- Extend cutters through the target and avoid tangent contact.
- Apply transforms before the operation.
- If a new Manifold solver is available in the installed Blender version, test it on a copy and record solver/version.

## Voxel remesh

Voxel remesh reconstructs a manifold mesh through a volume grid and can eliminate internal self-intersections. Use it when direct topology repair is insufficient. It changes surface detail according to voxel size; therefore:

- use the largest voxel resolution that preserves required detail;
- remesh only the ROI when possible;
- compare source/result outside ROI;
- account for memory using the physical bounding box;
- apply scale first.

## Solidify and hollowing

Use Solidify for open or relatively simple surfaces. Enable even-thickness/complex mode where needed and inspect concave regions for self-intersection. For complex closed organic objects and controlled constant thickness, prefer an SDF offset.

Never create the inner shell by uniformly scaling the outer mesh.

## Segmentation

For a shoe upper, toy belly, or decorated base, segment by a combination of:

- connected components/material slots if meaningful;
- manually marked seam landmarks;
- height and normal only as initial masks;
- curvature/ridge cues;
- section contours;
- face selection grown from known regions.

Automated Z-plane cuts are acceptable only when the project specification explicitly defines a planar seam.

## Headless execution

```bash
blender --background --python scripts/blender_functionalize.py -- path/to/config.json
```

The supplied script supports primitive and imported cutters, staged subtract/union/intersect operations, optional decimation, and checkpoint export. Blender APIs vary by version; test the import/export operators on a trivial file first.

## Geometry Nodes

Use Geometry Nodes for repeatable placement of tread, ribs, perforations, or fast preview masks. Realize instances before final mesh export and validate resulting topology. Do not use dense decorative nodes on the full production mesh until memory has been estimated.

## Validation

Use 3D Print Toolbox for non-manifold edges, intersections, wall thickness, overhang, and bounds. Treat it as one check, not the only check. Export and re-import the final STL/3MF, then run `inspect_mesh.py`.
