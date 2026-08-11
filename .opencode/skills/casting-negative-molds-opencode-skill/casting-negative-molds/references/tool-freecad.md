# FreeCAD workflow

FreeCAD is useful when a visual desktop workflow and scripted OpenCascade operations are both required. It can combine STEP solids, Part booleans, meshes, drafting, and technical inspection.

## Best uses

- inspect and repair STEP/BREP geometry;
- create Part/Part Design blocks, shells, flanges, keys, ribs, and channels;
- perform boolean Cut/Common/Fuse operations;
- convert a moderate, repaired mesh into a shape/solid when no better source exists;
- export STEP and STL from a scripted or GUI workflow.

## Recommended GUI workflow

1. Create a new document and set units to millimetres.
2. Import the source STEP or mesh.
3. Inspect bounding box, orientation, and components.
4. For a STEP source, run geometry checks before booleans.
5. Create a simple outer block or frame as a Part solid.
6. Position and scale the master using exact datum transforms.
7. Cut the master from the outer solid.
8. Create split solids and use Part Common to produce each mold section.
9. Add/subtract keys, sprues, vents, and flanges.
10. Refine shape only after checking whether it removes needed seam edges.
11. Export the mold sections as STEP and STL with documented tessellation.

## Mesh-to-solid conversion

A common path is:

```text
Mesh import
→ repair/close mesh
→ Part: Create shape from mesh
→ convert shell to solid
→ refine shape
→ boolean operations
```

This can be extremely memory-intensive because a triangle mesh may become one BREP face per triangle. Use it only after decimation and repair, and only when the face count is manageable. Organic high-poly meshes are often better kept in Blender while FreeCAD builds a separate structural frame.

In Python, the core pattern is similar to:

```python
import Mesh, Part
m = Mesh.Mesh("master.stl")
shape = Part.Shape()
shape.makeShapeFromMesh(m.Topology, tolerance)
solid = Part.makeSolid(shape)
```

Whether `Part.makeSolid` succeeds depends on the shell being closed and valid. A successful object still needs `checkGeometry()` and visual inspection.

## STEP import

For production molds, prefer STEP:

```python
import Part
shape = Part.read("master.step")
errors = shape.check(True)
```

If the STEP contains a compound, inspect its solids and decide explicitly which belong to the article.

## Thickness and shelling

The Part Thickness tool can hollow a solid by offsetting faces, but complex concave detail may fail. For a mold case, an outer parametric frame or loft is often more robust than offsetting a dense organic master.

Use a hybrid strategy:

- cavity face from the organic master;
- structural walls/ribs from clean Part geometry;
- separate replaceable detail insert when necessary.

## Parting and booleans

Use a large box or custom parting solid and `common()` for each half. A non-planar parting surface must be converted into a closed cutting volume; a naked surface alone is not enough for a reliable solid Common.

```python
half_a = complete.common(clip_a)
half_b = complete.common(clip_b)
```

Save operands before large booleans so a failed result is diagnosable.

## Keys and channels

Create cylinders, cones, or boxes in Part and transform them to the seam normal. Fuse male keys to one section and cut enlarged sockets from the mate. Cut the sprue/vents from the complete mold before splitting when both halves should share them.

## Python baseline

Run under `FreeCADCmd`:

```bash
FreeCADCmd scripts/freecad/negative_mold.py \
  --input master.step \
  --output-dir build/freecad
```

Some FreeCAD builds pass script arguments differently. The included script also accepts arguments following `--` and explains its usage when run without an input/demo.

## Performance rules

- Do not convert the original full-resolution scan to BREP without a face-count budget.
- Use a decimated duplicate for split and architecture work.
- Hide or remove unused objects before recompute.
- Disable automatic recompute during batches and recompute at controlled checkpoints.
- Avoid long dependency chains where every parameter change repeats an expensive cavity boolean.
- Export intermediate cavity, structure, and split solids.
- Use mesh booleans in a mesh tool when a BREP conversion adds no value.

## Validation

Use `shape.check(True)` or GUI geometry checks. Export STL and run `mesh_preflight.py`. Confirm that refine/remove-splitter operations did not merge edges needed for assembly or erase tiny channels.
