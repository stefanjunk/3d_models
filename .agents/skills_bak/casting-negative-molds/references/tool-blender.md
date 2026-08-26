# Blender workflow

Blender is the strongest of the four tools for organic, image-derived, scanned, and high-poly meshes. It supports local sculpting, displacement, remeshing, custom parting meshes, mesh booleans, shrinkwrap, and batch automation.

## Best uses

- repair and normalize organic meshes;
- remove floating components and internal shells;
- preserve or locally remesh fine ornament;
- create sculpted parting surfaces around undercuts;
- form conformal shells with Solidify or voxel/morphological methods;
- add texture relief with displacement or geometry nodes;
- combine an organic cavity with simpler structural meshes;
- export manifold mold parts.

For exact dimensions, keys, flanges, and channels, use numeric transforms and consider a hybrid CadQuery/FreeCAD frame.

## Import and normalization

1. Import STL/OBJ/PLY/3MF as supported by the installed Blender version.
2. Set scene units to millimetres or use a documented conversion factor.
3. Apply rotation and scale before remesh, Solidify, and booleans.
4. Join only components that form one article.
5. Remove loose fragments and internal shells intentionally.
6. Recalculate normals outside.
7. Inspect non-manifold edges and self-intersections.
8. Save a clean immutable master collection.

Never repair the only copy.

## Mesh cleanup

Useful operations include:

- Merge by Distance for duplicated vertices;
- Delete Loose for accidental fragments;
- Fill Holes only when the missing surface is understood;
- Recalculate Outside;
- Limited Dissolve on planar regions;
- Decimate in low-curvature areas;
- voxel remesh for globally broken topology;
- local remesh/sculpt for damaged detail.

A voxel remesh creates a 3D grid. Reducing voxel size by half can multiply voxel count roughly eightfold. Estimate the bounding volume first.

## Draft/undercut visualization

Create a material or Geometry Nodes setup driven by face-normal dot pull-direction to highlight draft sign. Treat it as a screening view, not a proof. Use duplicate mold-section meshes and move them incrementally along their pull vectors while checking intersections.

For complex objects, sculpt a parting ribbon along a visible ridge, extend it outward, solidify it into a cutting volume, and validate that both resulting sections can be removed.

## Block negative

1. Add a box around the compensated master.
2. Apply transforms to both.
3. Add Boolean Difference on the box using the master, Exact solver when suitable.
4. Apply and inspect the cavity.
5. Add the sprue/vents as cutter objects and subtract them.
6. Intersect with half-space boxes to create mold sections.
7. Add key solids and socket cutters.
8. run manifold checks and export selected sections.

Keep boolean cutters in a separate collection for reproducibility.

## Conformal shell

### Solidify

A duplicated master can be Solidified outward, then combined with a parting flange. This works best on a clean manifold mesh with thickness smaller than local concavity radius.

### Voxel shell

Voxel remesh or volume-based expansion can create a robust shell around problematic organic topology, but it smooths detail and uses cubic memory. Use a coarse structural shell plus a separate fine cavity skin where possible.

### Shrinkwrap structural shell

Create a low-poly outer cage, Shrinkwrap it toward the master with clearance, and add ribs. This separates structural resolution from cavity detail.

## Relief from images

Use a 16-bit height map where possible. Map one continuous coordinate system over the intended surface:

- planar UV for tiles;
- cylindrical UV for columns;
- carefully unwrapped UV for bowls and organic objects;
- object/world coordinates only when their seam and direction are intentional.

A common failure is projecting the same image separately onto each face, rotating the grain or engraving direction at every polygon island. Use one continuous UV layout and inspect seam continuity.

Apply subdivision only to the relief region. Keep the structural frame low-poly. Bake or apply displacement before the final cavity boolean, then preserve an undisturbed source copy.

## Parting and keys

For an arbitrary parting surface:

1. Create a clean closed cutter volume for side A.
2. Duplicate the complete mold.
3. Boolean Intersect A with cutter A.
4. Boolean Intersect B with the complementary cutter.
5. Add male keys to A.
6. subtract enlarged key cutters from B.
7. test assembly and pull motion.

Do not rely on coplanar boolean faces. Add a controlled overlap to cutters while keeping the actual parting datum shared.

## Batch script

```bash
blender --background --python scripts/blender/negative_mold.py -- \
  --input master.stl \
  --output-dir build/blender \
  --mode block \
  --split-axis X
```

The included script uses a conservative block workflow. Blender operator names can differ by major release, so validate it in the target version before production.

## Memory strategy

- Work with linked/duplicated instances until edits require real geometry.
- Keep proxy and high-detail collections separate.
- Apply modifiers only at checkpoints.
- Remesh only a local crop whenever possible.
- Avoid subdivision on hidden backs and structural walls.
- Disable or limit undo for very large batch operations.
- Save before exact booleans and voxel remesh.
- Split the 300 mm column into modules before high-resolution texture processing.
- Export and reopen mold sections to detect hidden dependency problems.

## Export and validation

Apply modifiers and transforms on export copies. Export each mold part separately, with millimetre scale verified in the slicer. Run `mesh_preflight.py` and inspect:

- manifoldness and winding;
- connected components;
- accidental internal shells;
- key/socket clearance;
- cavity detail after boolean;
- sprue and vent continuity;
- flatness of mating flanges;
- support and bridge behavior in the chosen print orientation.
